"""Study driver: the code path shared by the Mac pilot and every SageMaker stage.

Resume discipline: every (arm, seed, split) result is one JSON file whose name carries a hash of
EVERYTHING that determines it: the AdaptSpec, the probe template, the probe variants, both code
versions and the eval store's content hash. It is written the moment it completes; a restarted
job skips keys already present, and any change to any input produces a new key and a rerun.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path

import numpy as np
import torch
import yaml
from torch.utils.data import Dataset

from eegdrift.adapt import ADAPT_CODE_VERSION, AdaptSpec, adapt, seed_everything
from eegdrift.arms import Arm, resolve
from eegdrift.data.chbmit import OVERLAP_RULE_VERSION, overlap_label
from eegdrift.data.index import rotations, subject_of
from eegdrift.data.store import ArtifactStore
from eegdrift.data.windows import WindowStore
from eegdrift.drift.extract import extract_cell
from eegdrift.drift.metrics import decay_baseline, displacement, grad_pressure
from eegdrift.models.protocols import state_copy
from eegdrift.models.registry import Registry
from eegdrift.objectives import objective_for
from eegdrift.probe import DEFAULT_VARIANTS, PROBE_CODE_VERSION, VARIANTS, ProbeSpec, parity_probe


@dataclass
class Context:
    root: Path                      # repo root (configs/, weights/)
    data_root: Path                 # directory holding the LMDB stores
    out: Path                       # results dir (the job's checkpoint dir)
    artifacts: ArtifactStore
    device: torch.device
    smoke: bool = False
    log: object = print
    # Job-level reproduction knobs (NEXT-STEPS.md screen): batch (SSL AND probe, as upstream's
    # single training.batch_size), ssl_n ("parity" = the paper's N, "all" = the whole pool),
    # run_tag (a label carried into every record and the resume key).
    overrides: dict = field(default_factory=dict)
    registry: Registry = field(init=False)
    adapt_cfg: dict = field(init=False)
    data_cfg: dict = field(init=False)

    def __post_init__(self) -> None:
        self.registry = Registry.load(self.root)
        self.adapt_cfg = yaml.safe_load((self.root / "configs/adapt.yaml").read_text())
        # Arms the drift stage defines (drift_topK, enum_*, random_k*) live in their own files;
        # a name clash with a base arm is an error, never a silent override.
        for f in sorted((self.root / "configs/drift_arms").glob("*.yaml")):
            extra = yaml.safe_load(f.read_text())["arms"]
            clash = set(extra) & set(self.adapt_cfg["arms"])
            if clash and any(extra[k] != self.adapt_cfg["arms"][k] for k in clash):
                raise ValueError(f"{f.name} redefines arms {sorted(clash)}")
            self.adapt_cfg["arms"].update(extra)
        self.data_cfg = yaml.safe_load((self.root / "configs/data.yaml").read_text())
        self.out.mkdir(parents=True, exist_ok=True)


@dataclass
class SSLData:
    x: torch.Tensor          # [N, 16, 30, 200] unscaled
    records: list[dict]
    hash: str
    n_total: int             # pool size the subsample was drawn from
    split: str
    subset: str = ""         # "" | "N<n>" (from the parity sample) | "P<p>N<n>" (p subjects)


@dataclass
class EvalData:
    splits: dict[str, tuple[torch.Tensor, torch.Tensor]]
    hash: str
    test_index: list[dict]   # key, case, subject per test window, in tensor order
    split: str
    labels: str = "upstream"  # "upstream" | "overlap" (corrected protocol, D18)
    val_index: list = field(default_factory=list)   # key, case, subject per val window (D25-E25)


class _Windows(Dataset):
    def __init__(self, x: torch.Tensor):
        self.x = x

    def __len__(self) -> int:
        return len(self.x)

    def __getitem__(self, i: int) -> torch.Tensor:
        return self.x[i]


def noise_like(x: torch.Tensor, seed: int) -> torch.Tensor:
    """D19 control input: Gaussian noise with the SSL sample's per-channel mean and std."""
    g = torch.Generator().manual_seed(seed)
    mean, std = x.mean(dim=(0, 2, 3), keepdim=True), x.std(dim=(0, 2, 3), keepdim=True)
    return mean + std * torch.randn(x.shape, generator=g)


def _hash(*parts) -> str:
    return hashlib.sha256(json.dumps(parts, sort_keys=True, default=str).encode()).hexdigest()[:16]


def case_splits(ctx: Context, dataset: str, split: str) -> dict[str, str]:
    """case -> train/val/test for the paper split or a leak-free rotation (`rot0`..`rot4`)."""
    store = WindowStore(str(ctx.data_root / ctx.data_cfg[dataset]["eval_store"]))
    cases = sorted({r["case"] for r in store.index})
    if split == "paper":
        if any(r["split"] is None for r in store.index):   # Siena: rotations only
            raise ValueError(f"{dataset} has no paper split; use rot0..rot4")
        return {r["case"]: r["split"] for r in store.index}
    if split == "pub":   # D25-E33b: Siena published-style split (test as CSBrain), pre-registered
        pub = ctx.data_cfg[dataset].get("pub_split")
        if not pub:
            raise ValueError(f"{dataset} has no 'pub' split")
        return {c: "test" if subject_of(c) in pub["test"] else "val" if subject_of(c) in pub["val"] else "train"
                for c in cases}
    rot = ctx.data_cfg[dataset]["rotations"]
    fold_seed = int(ctx.overrides.get("fold_seed") or rot["seed"])   # D25-E32: second partition
    return rotations(cases, rot["n_folds"], fold_seed)[int(split.removeprefix("rot"))]


def _subset_indices(subset: str, parity_idx: list[int], pool: list[int], store: WindowStore,
                    data_seed: int = 1) -> list[int]:
    """Upstream ablation subsets (D15). N<n>: n windows from the parity sample, upstream's seed rule
    rng(data_seed * 1_000_003 + N_total). P<p>N<n>: p subjects drawn from the adaptation pool, about
    n/p windows each (the first n % p subjects take one extra), subjects with fewer than n // p
    windows ineligible, as in upstream compute_P."""
    m = re.fullmatch(r"N(\d+)", subset)
    if m:
        n = min(int(m.group(1)), len(parity_idx))
        rng = np.random.default_rng(data_seed * 1_000_003 + len(parity_idx))
        return sorted(parity_idx[i] for i in rng.choice(len(parity_idx), size=n, replace=False))
    m = re.fullmatch(r"P(\d+)N(\d+)", subset)
    if not m:
        raise ValueError(f"bad ssl subset {subset!r}; expected N<n> or P<p>N<n>")
    p, n = int(m.group(1)), int(m.group(2))
    by_subject: dict[str, list[int]] = {}
    for i in pool:
        by_subject.setdefault(store.index[i]["subject"], []).append(i)
    w = n // p
    eligible = sorted(s for s, v in by_subject.items() if len(v) >= w + 1)
    if len(eligible) < p:
        raise ValueError(f"only {len(eligible)} subjects have >= {w + 1} windows; need {p}")
    rng = np.random.default_rng(data_seed * 1_000_003 + p)
    chosen = sorted(rng.choice(eligible, size=p, replace=False).tolist())
    out: list[int] = []
    for k, subj in enumerate(chosen):
        take = w + (1 if k < n % p else 0)
        out += rng.choice(by_subject[subj], size=take, replace=False).tolist()
    return sorted(int(i) for i in out)


def load_ssl(ctx: Context, dataset: str, split: str = "paper", subset: str = "") -> SSLData:
    """Seeded parity subsample of the SSL store, drawn from the split's ADAPTATION pool.

    Upstream adapts on train+val subjects only (their SSL store excludes the test patients). For
    the paper split the store already does that. For a rotation, windows of the rotation's TEST
    subjects are removed before subsampling, or rotated runs would be transductive.
    """
    dcfg = ctx.data_cfg[dataset]
    store = WindowStore(str(ctx.data_root / dcfg["ssl_store"]))
    pool = list(range(len(store)))
    if split != "paper":
        test_subjects = {subject_of(c) for c, s in case_splits(ctx, dataset, split).items() if s == "test"}
        pool = [i for i in pool if store.index[i]["subject"] not in test_subjects]
    n = min(dcfg["parity_n"], len(pool)) if not ctx.smoke else min(256, len(pool))
    if ctx.overrides.get("ssl_n") == "all" and not ctx.smoke:
        n = len(pool)
    rng = np.random.default_rng(int(ctx.overrides.get("ssl_seed") or dcfg["parity_subsample_seed"]))
    idx = sorted(rng.choice(pool, size=n, replace=False).tolist())
    if subset:
        # smoke: same rules, N capped at 256 so a rehearsal stays seconds long
        eff = re.sub(r"N(\d+)$", lambda m: f"N{min(int(m.group(1)), 256)}", subset) if ctx.smoke else subset
        idx = _subset_indices(eff, idx, pool, store, int(ctx.overrides.get("data_seed") or 1))
        n = len(idx)
    x = np.empty((n, *store.shape), dtype=np.float32)
    for j, i in enumerate(idx):
        x[j] = store.get(int(i))
    recs = [store.index[int(i)] for i in idx]
    h = _hash(store.meta, split, subset, [r["key"] for r in recs])
    n_subj = len({r["subject"] for r in recs})
    ctx.log(f"[data] {dataset} SSL/{split}{'/' + subset if subset else ''}: {n} windows from {n_subj} "
            f"subjects (pool {len(pool)}, store {len(store)}), hash {h}")
    return SSLData(torch.from_numpy(x), recs, h, len(pool), split, subset)


def load_eval(ctx: Context, dataset: str, split: str = "paper") -> EvalData:
    dcfg = ctx.data_cfg[dataset]
    store = WindowStore(str(ctx.data_root / dcfg["eval_store"]))
    case_split = case_splits(ctx, dataset, split)
    s = dcfg["window_s"]
    labels = str(ctx.overrides.get("labels") or dcfg.get("labels", "upstream"))
    if labels not in ("upstream", "overlap"):
        raise ValueError(f"unknown labels {labels!r}; expected upstream | overlap")
    if dcfg.get("labels") == "overlap" and labels != "overlap":   # Siena: no upstream rule exists
        raise ValueError(f"{dataset} supports labels=overlap only")
    # overlap (D18): label = any overlap with a seizure; oversampled windows stay in train only
    seizures = (json.loads((ctx.root / "configs" / f"{dataset}_seizures.json").read_text())
                if labels == "overlap" else None)
    def label(i: int) -> int:
        return store.index[i]["label"] if seizures is None else overlap_label(store.index[i], seizures)

    splits, test_index, val_index = {}, [], []
    for part in ("train", "val", "test"):
        pos = [i for i, r in enumerate(store.index) if case_split.get(r["case"]) == part
               and (seizures is None or part == "train" or r["kind"] == "grid")]
        if ctx.smoke:   # up to 25 positives first, so the smoke exercises val selection
            rng = np.random.default_rng(0)
            size = min(len(pos), 1500 if part == "train" else 500)
            ones = [i for i in pos if label(i)]
            ones = rng.choice(ones, size=min(25, len(ones)), replace=False).tolist() if ones else []
            rest = sorted(set(pos) - set(ones))
            pos = sorted(ones + rng.choice(rest, size=size - len(ones), replace=False).tolist())
        x = np.empty((len(pos), 16, s, 200), dtype=np.float32)
        y = np.empty(len(pos), dtype=np.int64)
        for j, i in enumerate(pos):
            x[j] = store.get(i).reshape(16, s, 200)
            y[j] = label(i)
        splits[part] = (torch.from_numpy(x), torch.from_numpy(y))
        if part == "test":
            test_index = [{k: store.index[i][k] for k in ("key", "case", "subject")} for i in pos]
        if part == "val":
            val_index = [{k: store.index[i][k] for k in ("key", "case", "subject")} for i in pos]
        ctx.log(f"[data] {dataset} eval/{split}/{part}: {len(pos)} windows, prevalence {y.mean():.4f}")
    h = _hash(store.meta, split, ctx.smoke, len(store.index), [r["key"] for r in store.index[::997]],
              *([labels, _hash(seizures), OVERLAP_RULE_VERSION] if seizures is not None else []),
              *([("fold_seed", ctx.overrides["fold_seed"])] if ctx.overrides.get("fold_seed") else []))
    return EvalData(splits, h, test_index, split, labels, val_index)


def adapt_spec(ctx: Context, model: str, dataset: str, arm: Arm, seed: int, ssl: SSLData) -> AdaptSpec:
    protocol = ctx.overrides.get("protocol", "parity")
    p = ctx.adapt_cfg["protocols"][protocol]
    if protocol == "fixed_c":
        # Upstream Fig. 1 / Fig. 2 path: S = E_ref * ceil(N_total / B), anchored on the PAPER's
        # N_total (4,174) whatever subset is trained on.
        epochs = 1 if ctx.smoke else p["epochs_ref"]
        n_total = len(ssl.x) if ctx.smoke else ctx.data_cfg[dataset]["parity_n"]
        eta_min, clip = 0.0, ctx.adapt_cfg["protocols"]["parity"]["clip"]
    else:
        epochs = 1 if ctx.smoke else int(ctx.overrides.get("ssl_epochs") or p["epochs"][dataset])
        n_total, eta_min, clip = ssl.n_total, p["eta_min"], p["clip"]
    return AdaptSpec(
        model=model, dataset=dataset, arm=arm.name, groups=arm.groups, init=arm.init, seed=seed,
        protocol=protocol, batch=int(ctx.overrides.get("batch") or p["batch"]), epochs=epochs,
        n_windows=len(ssl.x), n_total=n_total, lr=float(ctx.overrides.get("ssl_lr") or p["lr"]),
        weight_decay=p["weight_decay"], eta_min=eta_min, clip=clip,
        scale=float(ctx.overrides.get("ssl_scale") or ctx.adapt_cfg["scale"][dataset]),
        input_norm=ctx.overrides.get("input_norm", ""),
        mask_ratio=ctx.adapt_cfg["mask_ratio"], include_fixed=arm.include_fixed,
        data_hash=ssl.hash if arm.ssl_input == "eeg" else _hash(ssl.hash, arm.ssl_input),
        ckpt_sha256=ctx.registry.specs[model].checkpoint["sha256"] if arm.init == "pretrained" else "")


def probe_template(ctx: Context, model: str, dataset: str, seed: int, split: str) -> ProbeSpec:
    dcfg = ctx.data_cfg[dataset]
    return ProbeSpec(model=model, dataset=dataset, variant="*", seed=seed,
                     n_classes=dcfg["n_classes"], window_s=dcfg["window_s"], split=split,
                     epochs=1 if ctx.smoke else 10, scale=dcfg["eval_scale"],
                     batch=int(ctx.overrides.get("batch") or 256),
                     # D23: dropout in the frozen backbone corrupts pretrained CBraMod features
                     backbone_mode=ctx.overrides.get("backbone_mode")
                     or ("eval" if model == "cbramod" else "train"),
                     tap=ctx.overrides.get("probe_tap") or "encoder",
                     input_norm=ctx.overrides.get("input_norm", ""))


def result_key(spec: AdaptSpec, arm: Arm, template: ProbeSpec, variants, ev: EvalData,
               run_tag: str = "") -> str:
    h = _hash(spec.key(), asdict(arm), asdict(template), sorted(variants), PROBE_CODE_VERSION,
              ADAPT_CODE_VERSION, ev.hash, run_tag)
    return f"{spec.model}-{spec.dataset}-{arm.name}-s{spec.seed}-{ev.split}-{h}"


def run_arm_seed(ctx: Context, model_name: str, dataset: str, arm_name: str, seed: int,
                 ssl: SSLData, ev: EvalData, keep_state: bool = False, variants=DEFAULT_VARIANTS) -> dict:
    if ssl.split != ev.split:
        raise ValueError(f"SSL split {ssl.split} != eval split {ev.split}")
    if ctx.overrides.get("probes"):   # e.g. "linear": run only the listed probe variants
        variants = tuple(ctx.overrides["probes"].split(","))
        unknown = set(variants) - set(VARIANTS)
        if unknown:
            raise ValueError(f"unknown probe variants {sorted(unknown)}; expected {VARIANTS}")
    arm = resolve(arm_name, ctx.adapt_cfg, ctx.registry, model_name)
    spec = adapt_spec(ctx, model_name, dataset, arm, seed, ssl)
    template = probe_template(ctx, model_name, dataset, seed, ev.split)
    run_tag = str(ctx.overrides.get("run_tag", ""))
    key = result_key(spec, arm, template, variants, ev, run_tag)
    res_dir = ctx.out / "results"
    path = res_dir / f"{key}.json"
    if path.exists():
        ctx.log(f"[resume] skip {key}")
        return {**json.loads(path.read_text()), "resumed": True}
    res_dir.mkdir(parents=True, exist_ok=True)
    seed_everything(seed)
    model = ctx.registry.build(model_name, init=arm.init)
    record: dict = {"key": key, "model": model_name, "dataset": dataset, "arm": arm_name,
                    "seed": seed, "split": ev.split, "adapt_spec": asdict(spec), "arm_spec": asdict(arm),
                    "eval_hash": ev.hash, "labels": ev.labels, "smoke": ctx.smoke, "run_tag": run_tag,
                    "ssl_subset": ssl.subset, "ssl_subjects": len({r["subject"] for r in ssl.records}),
                    "overrides": dict(ctx.overrides),
                    "versions": {"adapt": ADAPT_CODE_VERSION, "probe": PROBE_CODE_VERSION}}
    if arm.adapt:
        state0 = state_copy(model.module)
        x = ssl.x if arm.ssl_input == "eeg" else noise_like(ssl.x, seed)
        res = adapt(model, objective_for(model, spec.mask_ratio), spec, _Windows(x), ctx.device, ctx.log)
        record["adapt"] = {"trainable": res.trainable, "steps": res.steps_done,
                           "epoch_losses": res.epoch_losses, "best_epoch": res.best_epoch,
                           "skipped_nonfinite": res.skipped_nonfinite, "seconds": res.seconds,
                           "lr_sum": res.lr_sum, "lr_sum_by_epoch": res.lr_sum_by_epoch,
                           "step_losses": res.step_losses}
        record["displacement"] = displacement(state0, res.state, model, lr_sum=res.lr_sum)
        # Under the cosine schedule the decoupled-decay shrinkage is 1 - prod(1 - lr_t*wd)
        # ~ 1 - exp(-wd * sum lr_t), NOT the constant-peak-lr formula (code review MINOR).
        record["decay_baseline"] = float(1 - np.exp(-spec.weight_decay * res.lr_sum))
        record["decay_baseline_constant_lr"] = decay_baseline(spec.lr, spec.weight_decay, res.steps_done)
        if keep_state:
            (ctx.out / "states").mkdir(parents=True, exist_ok=True)
            torch.save(res.state, ctx.out / "states" / f"{key}.pt")
    test_index_path = res_dir / f"test-index-{dataset}-{ev.split}-{ev.hash}.json"
    if not test_index_path.exists():
        test_index_path.write_text(json.dumps(ev.test_index))
    record["test_index"] = test_index_path.name
    val_index_path = res_dir / f"val-index-{dataset}-{ev.split}-{ev.hash}.json"
    if ev.val_index and not val_index_path.exists():
        val_index_path.write_text(json.dumps(ev.val_index))
    record["val_index"] = val_index_path.name
    record["probes"] = {}
    for variant in variants:
        result, arrays = parity_probe(model, replace(template, variant=variant), ev.splits,
                                      ctx.device, ctx.log)
        np.savez_compressed(res_dir / f"{key}.{variant}.npz", **arrays)
        record["probes"][variant] = result.to_record()
    _save(path, record)   # atomic: a kill mid-write must never leave a truncated, resumable file
    ctx.log(f"[done] {key}: " + ", ".join(
        f"{v}: test_at_best auroc={record['probes'][v]['test_at_best'].get('roc_auc', float('nan')):.4f}"
        for v in variants))
    return record


def drift_sample(ctx: Context, dataset: str, ssl: SSLData) -> tuple[torch.Tensor, list[str], list[str]]:
    cfg = ctx.data_cfg[dataset]["drift_sample"]
    n = min(cfg["n"] if not ctx.smoke else 64, len(ssl.x))
    idx = np.sort(np.random.default_rng(cfg["seed"]).choice(len(ssl.x), size=n, replace=False))
    return ssl.x[idx], [ssl.records[i]["key"] for i in idx], [ssl.records[i]["subject"] for i in idx]


def run_diag(ctx: Context, model_name: str, dataset: str, seeds: list[int], run_id: str) -> dict:
    """Design A + C for one (model, dataset) on the paper split.

    Design C is computed PER SEED: BIOT's SSL loss runs through the `prediction` head, which is
    randomly initialised per seed (the checkpoint holds the encoder only), so a single-seed
    gradient vector would be one arbitrary head's view (code review 2026-10-15).
    """
    ssl = load_ssl(ctx, dataset, "paper")
    ev = load_eval(ctx, dataset, "paper")
    xs, wids, sids = drift_sample(ctx, dataset, ssl)
    reg = ctx.registry
    dkey = _hash(ctx.data_cfg[dataset]["drift_sample"], [t.to_record() for t in reg.taps(model_name)],
                 reg.specs[model_name].checkpoint["sha256"], ssl.hash, ADAPT_CODE_VERSION, ctx.smoke)
    summary_path = ctx.out / "results" / f"diag-{model_name}-{dataset}-{dkey}.json"
    summary = json.loads(summary_path.read_text()) if summary_path.exists() else {"key": dkey}
    scale = ctx.adapt_cfg["scale"][dataset]
    # "ssl_pool": the paper split's adaptation pool (train AND val subjects, chb01-chb22), not "train"
    base = {"run_id": run_id, "dataset": dataset, "split": "ssl_pool", "domain": "target"}
    if "frozen_taps" not in summary:
        seed_everything(seeds[0])
        frozen = reg.build(model_name, "pretrained")
        meta = {**base, "cell_id": f"{model_name}|{dataset}|frozen|target", "model_state": "frozen",
                "ckpt_sha256": reg.specs[model_name].checkpoint["sha256"]}
        summary["frozen_taps"] = extract_cell(frozen, xs, scale=scale, meta=meta, window_ids=wids,
                                              subject_ids=sids, store=ctx.artifacts, device=ctx.device)
        _save(summary_path, summary)
    for i, seed in enumerate(seeds):
        if str(seed) not in summary.setdefault("grad_pressure", {}):
            seed_everything(seed)
            m = reg.build(model_name, "pretrained")
            summary["grad_pressure"][str(seed)] = grad_pressure(
                m, objective_for(m, ctx.adapt_cfg["mask_ratio"]), xs, scale, ctx.device)
            _save(summary_path, summary)
        rec = run_arm_seed(ctx, model_name, dataset, "all", seed, ssl, ev, keep_state=True)
        summary.setdefault("displacement", {})[str(seed)] = rec.get("displacement")
        summary.setdefault("all_keys", {})[str(seed)] = rec["key"]
        if i == 0 and "adapted_taps" not in summary:
            state = torch.load(ctx.out / "states" / f"{rec['key']}.pt", weights_only=True)
            adapted = reg.build(model_name, "pretrained", state_dict=state)
            meta = {**base, "cell_id": f"{model_name}|{dataset}|adapted_all|target",
                    "model_state": "adapted_all", "adapt_seed": seed, "adapt_key": rec["key"],
                    "ckpt_sha256": reg.specs[model_name].checkpoint["sha256"]}
            summary["adapted_taps"] = extract_cell(adapted, xs, scale=scale, meta=meta, window_ids=wids,
                                                   subject_ids=sids, store=ctx.artifacts, device=ctx.device)
        _save(summary_path, summary)
    return summary


def run_arms(ctx: Context, model_name: str, dataset: str, arms: list[str], seeds: list[int],
             split: str = "paper") -> list[dict]:
    """With overrides["ssl_subsets"] (e.g. "N896,N2048"), runs every arm on every subset in turn;
    each subset gets run_tag "<run_tag>-<subset>" so tables never mix subsets."""
    ev = load_eval(ctx, dataset, split)
    subsets = [s for s in str(ctx.overrides.get("ssl_subsets", "")).split(",") if s] or [""]
    base_tag = str(ctx.overrides.get("run_tag", ""))
    out = []
    for subset in subsets:
        if subset:
            ctx.overrides["run_tag"] = f"{base_tag}-{subset}" if base_tag else subset
        ssl = load_ssl(ctx, dataset, split, subset)
        for arm in arms:
            for seed in seeds:
                t0 = time.time()
                out.append(run_arm_seed(ctx, model_name, dataset, arm, seed, ssl, ev))
                ctx.log(f"[timing] {subset or 'parity'} {arm} s{seed}: {time.time() - t0:.0f}s")
    ctx.overrides["run_tag"] = base_tag
    return out


def _save(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, default=str))
    tmp.replace(path)
