"""D25-E15: BIOT probe strength, feature scale and input-scaling precheck (CPU, desktop).

Item design and reading rule: notes/completeness-audit.md E15, adopted by notes/decisions.md D25.
Everything not named in the rule below is DESCRIPTIVE.

Stages, run in this order (--work holds every intermediate; features stay there, they are GBs):
  selfcheck  parity_cached() on cached eval-mode features == probe.parity_probe (tiny random BIOT).
  adapt      Siena only: re-adapt `last` on CPU at seed S_r for rotation r (51 steps), exactly the
             run_arm_seed path; saves the state and the full SSL log (per-step losses).
  extract    eval-mode BIOT encoder features [N, 256] for EVERY window of one eval store: lp
             (pretrained), lp_randinit (seed_everything(S_r) + random build, as run_arm_seed), at
             inputs /100 (as run) and per-channel per-window q95 (protocols.scale_input, D25-E19);
             Siena stores also `last` (the adapt states, /100). Writes feature stats and the
             load_eval split indices/labels for rot0-4 (+ the CHB-MIT paper split).
  probe      per (dataset, split, seed, arm, input): the parity linear head (ProbeSpec defaults:
             AdamW 4e-4 / wd 5e-2, cosine to 1e-5, 10 epochs, batch 256, BCE, best epoch by val
             ROC) on raw features (= the D24 records' probe) and on z-scored features (train-split
             statistics), and standardized logistic regression with C chosen on validation ROC.
             Every epoch / every C is logged; val and test scores at the selected point saved.
  report     fidelity vs the D24 records, the D25-E15 verdicts, tables and figures (run on the
             desktop: it reads the split npz files, ~90 MB, which must not go to the Mac).

Pre-registered rule (D25-E15), applied per dataset (CHB-MIT, Siena, Siena filtered) at seed S_r:
  "BIOT conclusions are probe-limited" if z-scoring or LR moves lp - lp_randinit by > 3 ROC points
  in >= 4/5 rotations: delta_P,r = (lp - lp_randinit)[P] - (lp - lp_randinit)[parity raw], for
  P in {parity_z, lr}, /100 inputs, |delta| > 3 counted (literal reading; the same-sign count is
  reported next to it). Gates E26.
  "Input scale matters" if lp(q95) - lp(/100) > 3 in >= 4/5 rotations, read with the pipeline's own
  probe (parity raw), i.e. the probe E19 will use; z / LR versions descriptive. E19 runs either way.

Desktop, as run 2026-11-01 (repo copy in ~/e15/EEGDrift; D24 record JSONs copied to ~/e15/s3-results):
  ~/e15/venv/bin/python scripts/analysis/biot_probe_strength.py queue --work ~/e15/work  # adapt + extract
  OMP_NUM_THREADS=1 ~/e15/venv/bin/python scripts/analysis/biot_probe_strength.py probe --work ~/e15/work \
      --threads 1 --procs 96
  ~/released/eea-env/bin/python scripts/analysis/biot_probe_strength.py report --runs ~/e15/work \
      --results ~/e15/s3-results --dest ~/e15/report   # this env has matplotlib; ~/e15/venv does not
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
import warnings
from dataclasses import asdict
from pathlib import Path

import numpy as np
import torch
from torch import nn

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from eegdrift.adapt import adapt, seed_everything  # noqa: E402
from eegdrift.arms import resolve  # noqa: E402
from eegdrift.data.chbmit import overlap_label  # noqa: E402
from eegdrift.data.store import LocalStore  # noqa: E402
from eegdrift.data.windows import WindowStore  # noqa: E402
from eegdrift.drift.metrics import displacement  # noqa: E402
from eegdrift.models.protocols import scale_input, state_copy  # noqa: E402
from eegdrift.objectives import objective_for  # noqa: E402
from eegdrift.probe import LOGIT_T, ProbeSpec, _batches, _bce, build_head, metrics, parity_probe  # noqa: E402
from eegdrift.study import Context, _Windows, adapt_spec, case_splits, load_ssl  # noqa: E402

SEEDS = [42, 123, 2021, 3407, 8888]  # S_r for rot r (D24)
NORMS = {"d100": "", "q95": "q95"}  # input: /100 as run, BIOT-native q95
# dataset tag -> (config dataset, store dir under --lmdb, D24 run tag, D24 results dir pattern)
DATASETS = {
    "chbmit": ("chbmit", ".", "S1M", "arms-biot-chb-rot{r}-s1m"),
    "siena": ("siena", "siena", "S3M", "arms-biot-sie-rot{r}-s3m"),
    "siena_filt": ("siena", "siena_filt", "S3FM", "arms-biot-sie-rot{r}-sfm"),
}
PAPER = ("P1E", {"lp": "arms-biot-chb-p1elp", "lp_randinit": "arms-biot-chb-p1epr"})  # p1elr = last_randinit
LR_GRID = (1e-4, 1e-3, 1e-2, 1e-1, 1.0, 10.0)  # strong_probe's grid + 1e-4 (h5 used 1e-3)
THRESH, K = 3.0, 4
CPU = torch.device("cpu")


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def ctx_for(data_root: Path, work: Path) -> Context:
    return Context(
        root=REPO,
        data_root=data_root,
        out=work / "ctx",
        artifacts=LocalStore(work / "ctx/act"),
        device=CPU,
        log=log,
    )


def splits_of(ds: str) -> list[str]:
    return [f"rot{r}" for r in range(5)] + (["paper"] if ds == "chbmit" else [])


def seeds_of(split: str) -> list[int]:
    return SEEDS if split == "paper" else [SEEDS[int(split[3:])]]


# ---- the probes ----------------------------------------------------------------------------
def parity_cached(F: dict, Y: dict, seed: int, epochs: int = 10) -> dict:
    """probe.parity_probe (binary, linear head, backbone eval) on cached features: same seed rule,
    same head init, same batch order, same schedule and selection. selfcheck asserts equality."""
    spec = ProbeSpec(
        model="biot", dataset="-", variant="linear", seed=seed, n_classes=2, window_s=10, epochs=epochs
    )
    torch.manual_seed(spec.seed)
    head = build_head("biot", "linear", 2, 10)
    opt = torch.optim.AdamW(head.parameters(), lr=spec.lr, weight_decay=spec.weight_decay, betas=spec.betas)
    xtr, ytr = torch.from_numpy(F["train"]), torch.from_numpy(Y["train"])
    n_batches = -(-len(xtr) // spec.batch)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=spec.epochs * n_batches, eta_min=spec.eta_min)
    crit = nn.BCEWithLogitsLoss()
    gen = torch.Generator().manual_seed(spec.seed)

    def score(f: np.ndarray) -> np.ndarray:
        head.eval()
        with torch.no_grad():
            return np.concatenate(
                [head(torch.from_numpy(f[i : i + 4096])).squeeze(-1).numpy() for i in range(0, len(f), 4096)]
            )

    best_val, best_epoch, history, best = 0.0, -1, [], {}
    for epoch in range(spec.epochs):
        head.train()
        losses = []
        for xb, yb in _batches(xtr, ytr, spec.batch, True, gen):
            loss = crit(head(xb).reshape(-1, 1), yb.float().reshape(-1, 1))
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            sched.step()
            losses.append(loss.item())
        sv, st = score(F["val"]), score(F["test"])
        val = metrics(Y["val"], sv, 2, LOGIT_T)
        history.append(
            {
                "epoch": epoch,
                "train_loss": float(np.mean(losses)),
                "val_loss": _bce(Y["val"], sv),
                "val": val,
                "test_plot_only": metrics(Y["test"], st, 2, LOGIT_T),
            }
        )
        if val["roc_auc"] > best_val:
            best_val, best_epoch = val["roc_auc"], epoch
            best = {"test_at_best": metrics(Y["test"], st, 2, LOGIT_T), "scores_val": sv, "scores_test": st}
    w = head.weight.detach().numpy().ravel()
    return {
        "best_epoch": best_epoch,
        "best_val": best_val,
        "val_curve": [h["val"]["roc_auc"] for h in history],
        "history": history,
        "test_last": history[-1]["test_plot_only"],
        "head_weight_norm": float(np.linalg.norm(w)),
        "head_bias": float(head.bias.item()),
        **best,
    }


def lr_probe(F: dict, Y: dict) -> dict:
    """Standardized logistic regression (train statistics), C on validation ROC (strong_probe rule)."""
    from sklearn.exceptions import ConvergenceWarning  # noqa: PLC0415
    from sklearn.linear_model import LogisticRegression  # noqa: PLC0415
    from sklearn.preprocessing import StandardScaler  # noqa: PLC0415

    sc = StandardScaler().fit(F["train"])
    Z = {k: sc.transform(v) for k, v in F.items()}
    sweep, best = [], None
    for c in LR_GRID:
        t0 = time.time()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", ConvergenceWarning)
            clf = LogisticRegression(C=c, max_iter=3000).fit(Z["train"], Y["train"])
        sv, st = clf.decision_function(Z["val"]), clf.decision_function(Z["test"])
        row = {
            "C": c,
            "val": metrics(Y["val"], sv, 2, LOGIT_T),
            "test_plot_only": metrics(Y["test"], st, 2, LOGIT_T),
            "train_loss": _bce(Y["train"], clf.decision_function(Z["train"])),
            "val_loss": _bce(Y["val"], sv),
            "n_iter": int(clf.n_iter_[0]),
            "converged": not any(issubclass(w.category, ConvergenceWarning) for w in caught),
            "seconds": time.time() - t0,
        }
        sweep.append(row)
        if best is None or row["val"]["roc_auc"] > best[0]["val"]["roc_auc"]:
            best = (row, sv, st)
    row, sv, st = best
    return {
        "C": row["C"],
        "best_val": row["val"]["roc_auc"],
        "test_at_best": row["test_plot_only"],
        "sweep": sweep,
        "C_at_grid_edge": row["C"] in (LR_GRID[0], LR_GRID[-1]),
        "scores_val": sv,
        "scores_test": st,
    }


# ---- stages --------------------------------------------------------------------------------
def selfcheck(_args) -> None:
    ctx = ctx_for(REPO / "data/lmdb", Path("/tmp/e15-selfcheck"))
    seed_everything(0)
    m = ctx.registry.build("biot", "random")
    g = torch.Generator().manual_seed(1)
    data = {}
    for part, n in (("train", 600), ("val", 300), ("test", 300)):
        x = torch.randn(n, 16, 10, 200, generator=g) * 40
        y = (torch.rand(n, generator=g) < 0.15).long()
        x[y == 1] *= 1.02  # weak signal: ROC strictly inside (0, 1), so selection is exercised
        data[part] = (x, y)
    spec = ProbeSpec(
        model="biot",
        dataset="-",
        variant="linear",
        seed=7,
        n_classes=2,
        window_s=10,
        epochs=3,
        backbone_mode="eval",
    )
    res, arr = parity_probe(m, spec, data, CPU, log=lambda *_: None)
    F = {k: feats(m, v[0], "") for k, v in data.items()}
    Y = {k: v[1].numpy() for k, v in data.items()}
    mine = parity_cached(F, Y, seed=7, epochs=3)
    log(
        f"selfcheck: repo best_epoch {res.best_epoch} roc {res.test_at_best['roc_auc']:.6f} | cached "
        f"{mine['best_epoch']} {mine['test_at_best']['roc_auc']:.6f}"
    )
    assert mine["best_epoch"] == res.best_epoch
    assert np.allclose(mine["val_curve"], res.val_curve, atol=1e-6)
    assert abs(mine["test_at_best"]["roc_auc"] - res.test_at_best["roc_auc"]) < 1e-6
    assert np.allclose(mine["scores_test"], arr["scores_best"], atol=1e-4)
    log("selfcheck OK: parity_cached reproduces parity_probe (eval mode)")


@torch.no_grad()
def feats(model, x: torch.Tensor, norm: str, scale: float = 100.0, batch: int = 512) -> np.ndarray:
    model.module.eval()
    return np.concatenate(
        [
            model.features(model.prepare(scale_input(x[i : i + batch], scale, norm))).numpy()
            for i in range(0, len(x), batch)
        ]
    )


def stage_adapt(args) -> None:
    """Same steps as study.run_arm_seed for arm `last` (seed, build, state0, adapt, displacement)."""
    work = Path(args.work)
    ctx = ctx_for(Path(args.lmdb) / "siena", work)
    (work / "states").mkdir(parents=True, exist_ok=True)
    for r in args.rot:
        seed, split = SEEDS[r], f"rot{r}"
        ssl = load_ssl(ctx, "siena", split)
        arm = resolve("last", ctx.adapt_cfg, ctx.registry, "biot")
        spec = adapt_spec(ctx, "biot", "siena", arm, seed, ssl)
        seed_everything(seed)
        model = ctx.registry.build("biot", init=arm.init)
        state0 = state_copy(model.module)
        res = adapt(model, objective_for(model, spec.mask_ratio), spec, _Windows(ssl.x), CPU, log)
        torch.save(res.state, work / "states" / f"last-s{seed}-{split}.pt")
        (work / "states" / f"last-s{seed}-{split}.json").write_text(
            json.dumps(
                {
                    "split": split,
                    "seed": seed,
                    "adapt_spec": asdict(spec),
                    "trainable": res.trainable,
                    "steps": res.steps_done,
                    "epoch_losses": res.epoch_losses,
                    "best_epoch": res.best_epoch,
                    "skipped_nonfinite": res.skipped_nonfinite,
                    "seconds": res.seconds,
                    "lr_sum": res.lr_sum,
                    "lr_sum_by_epoch": res.lr_sum_by_epoch,
                    "step_losses": res.step_losses,
                    "displacement": displacement(state0, res.state, model, lr_sum=res.lr_sum),
                    "torch_threads": torch.get_num_threads(),
                },
                default=str,
            )
        )
        log(f"[adapt] {split} s{seed}: losses {res.epoch_losses} in {res.seconds:.0f}s")


def eval_splits(ctx: Context, cfg_ds: str, store: WindowStore, split: str) -> dict:
    """study.load_eval's window selection and labels, as index arrays (rotations: overlap labels,
    grid-only val/test, as S1M/S3M/S3FM; paper: upstream labels, as P1E)."""
    case_split = case_splits(ctx, cfg_ds, split)
    seizures = None if split == "paper" else json.loads((REPO / "configs" / f"{cfg_ds}_seizures.json").read_text())
    out = {}
    for part in ("train", "val", "test"):
        idx = [
            i
            for i, r in enumerate(store.index)
            if case_split.get(r["case"]) == part and (seizures is None or part == "train" or r["kind"] == "grid")
        ]
        y = [store.index[i]["label"] if seizures is None else overlap_label(store.index[i], seizures) for i in idx]
        out[f"idx_{part}"], out[f"y_{part}"] = np.array(idx, dtype=np.int64), np.array(y, dtype=np.int64)
    out["test_keys"] = np.array([store.index[i]["key"] for i in out["idx_test"]])
    out["test_subjects"] = np.array([store.index[i]["subject"] for i in out["idx_test"]])
    return out


def stage_extract(args) -> None:
    ds = args.dataset
    cfg_ds, sub, _, _ = DATASETS[ds]
    work = Path(args.work)
    out = work / ds
    out.mkdir(parents=True, exist_ok=True)
    ctx = ctx_for(Path(args.lmdb) / sub, work)
    store = WindowStore(str(ctx.data_root / ctx.data_cfg[cfg_ds]["eval_store"]))
    want = args.models.split(",") if args.models else None
    norms = {k: v for k, v in NORMS.items() if not args.norms or k in args.norms.split(",")}
    if (want is None or "pre" in want) and "d100" in norms:  # this process also writes the split indices
        for split in splits_of(ds):
            np.savez(out / f"split-{split}.npz", **eval_splits(ctx, cfg_ds, store, split))
            log(f"[split] {ds} {split} written")
    builders = {"pre": (SEEDS[0], "pretrained", None)}
    builders.update({f"rnd{s}": (s, "random", None) for s in SEEDS})
    if cfg_ds == "siena":
        builders.update(
            {f"last{s}": (s, "pretrained", work / "states" / f"last-s{s}-rot{r}.pt") for r, s in enumerate(SEEDS)}
        )
    models = {}
    for name, (seed, init, state) in builders.items():
        if want is None or name in want:
            while state and not state.with_suffix(".json").exists():  # adapt writes .pt, then .json
                log(f"[extract] waiting for {state.name}")
                time.sleep(60)
            seed_everything(seed)  # as run_arm_seed: seed, then build
            sd = torch.load(state, weights_only=True) if state else None
            models[name] = ctx.registry.build("biot", init, state_dict=sd)
    jobs = [(m, nk) for m in models for nk in norms if not (m.startswith("last") and nk != "d100")]
    n, s_ = len(store), ctx.data_cfg[cfg_ds]["window_s"]
    mm = {j: np.lib.format.open_memmap(out / f"feat-{j[0]}-{j[1]}.npy", "w+", np.float32, (n, 256)) for j in jobs}
    t0 = time.time()
    for a in range(0, n, args.chunk):
        b = min(n, a + args.chunk)
        x = torch.from_numpy(
            np.stack([store.get(i) for i in range(a, b)]).reshape(-1, 16, s_, 200).astype(np.float32)
        )
        xs = {nk: scale_input(x, 100.0, norm) for nk, norm in norms.items()}  # eval_scale 100
        for m, nk in jobs:
            mm[(m, nk)][a:b] = feats(models[m], xs[nk], "", scale=1.0, batch=64)  # 64: fastest on CPU
        el = time.time() - t0
        log(f"[extract] {ds} {b}/{n} windows, {b / el:.0f} win/s, eta {(n - b) * el / b / 60:.1f} min")
    grid = np.array([r["kind"] == "grid" for r in store.index])
    stats = {}
    for j, f in mm.items():
        f.flush()
        (out / f"feat-{j[0]}-{j[1]}.done").touch()
        g = np.asarray(f[grid], dtype=np.float64)
        sd = g.std(0)
        stats[f"{j[0]}-{j[1]}"] = {
            "n": int(len(g)),
            "std": float(g.std()),
            "mean_abs": float(np.abs(g).mean()),
            "row_norm_mean": float(np.linalg.norm(g, axis=1).mean()),
            "per_dim_std_median": float(np.median(sd)),
            "per_dim_std_min": float(sd.min()),
            "per_dim_std_max": float(sd.max()),
            "finite": bool(np.isfinite(g).all()),
        }
    (out / f"stats-{'_'.join(models)}-{'_'.join(norms)}.json").write_text(json.dumps(stats, indent=1))
    log(f"[extract] {ds} done in {(time.time() - t0) / 60:.1f} min")


def stage_queue(args) -> None:
    """Every adapt and extract task as its own --threads process, --procs at a time (the measured
    optimum on the shared desktop is 2 threads/process; extract `last` tasks wait for their state)."""
    import subprocess  # noqa: PLC0415
    from concurrent.futures import ThreadPoolExecutor  # noqa: PLC0415

    tasks = [["adapt", "--rot", str(r)] for r in range(5)]
    for ds in DATASETS:
        for m in ["pre"] + [f"rnd{s}" for s in SEEDS]:
            tasks += [["extract", "--dataset", ds, "--models", m, "--norms", nk] for nk in NORMS]
    for ds in ("siena", "siena_filt"):
        tasks += [["extract", "--dataset", ds, "--models", f"last{s}", "--norms", "d100"] for s in SEEDS]
    logs = Path(args.work) / "logs"
    logs.mkdir(parents=True, exist_ok=True)

    def run(t: list[str]) -> str:
        name = "-".join(x for x in t if not x.startswith("--"))
        cmd = [
            sys.executable,
            "-u",
            __file__,
            *t,
            "--work",
            args.work,
            "--lmdb",
            args.lmdb,
            "--threads",
            str(args.threads),
        ]
        with open(logs / f"{name}.log", "w") as f:
            rc = subprocess.call(cmd, stdout=f, stderr=subprocess.STDOUT)
        log(f"[queue] {name} exit {rc}")
        return name if rc else ""

    with ThreadPoolExecutor(args.procs) as ex:
        failed = [x for x in ex.map(run, tasks) if x]
    log(f"[queue] {len(tasks)} tasks, failed: {failed or 'none'}")


def probe_jobs(work: Path) -> list[tuple]:
    jobs = []
    for ds, (cfg_ds, *_rest) in DATASETS.items():
        for split in splits_of(ds):
            for seed in seeds_of(split):
                arms = {"lp": "pre", "lp_randinit": f"rnd{seed}"}
                if cfg_ds == "siena":
                    arms["last"] = f"last{seed}"
                for arm, m in arms.items():
                    for nk in NORMS:
                        if arm == "last" and nk != "d100":
                            continue
                        jobs.append(("parity", ds, split, seed, arm, m, nk))
                        if not (arm == "lp" and split == "paper" and seed != SEEDS[0]):  # LR is seed-free
                            jobs.append(("lr", ds, split, seed, arm, m, nk))
    return [j for j in jobs if (work / j[1] / f"feat-{j[5]}-{j[6]}.done").exists()]


def job_name(job: tuple) -> str:
    kind, ds, split, seed, arm, _m, nk = job
    return f"{kind}-{ds}-{split}-s{seed}-{arm}-{nk}"


def run_job(args_job) -> str:
    work, job = args_job
    torch.set_num_threads(1)
    kind, ds, split, seed, arm, m, nk = job
    dest = work / "probe" / f"{job_name(job)}.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        return f"skip {dest.name}"
    t0 = time.time()
    feat = np.load(work / ds / f"feat-{m}-{nk}.npy", mmap_mode="r")
    sp = np.load(work / ds / f"split-{split}.npz")
    F = {p: np.ascontiguousarray(feat[sp[f"idx_{p}"]]) for p in ("train", "val", "test")}
    Y = {p: sp[f"y_{p}"] for p in ("train", "val", "test")}
    meta = {
        "kind": kind,
        "dataset": ds,
        "split": split,
        "seed": seed,
        "arm": arm,
        "features": m,
        "input": nk,
        "n": {p: int(len(Y[p])) for p in Y},
        "pos": {p: int(Y[p].sum()) for p in Y},
    }
    res = {}
    if kind == "parity":
        res["parity_raw"] = parity_cached(F, Y, seed)
        mu, sd = F["train"].astype(np.float64).mean(0), F["train"].astype(np.float64).std(0)
        sd[sd == 0] = 1.0  # StandardScaler's rule
        Fz = {p: ((v - mu) / sd).astype(np.float32) for p, v in F.items()}
        res["parity_z"] = parity_cached(Fz, Y, seed)
    else:
        res["lr"] = lr_probe(F, Y)
    np.savez_compressed(
        dest.with_suffix(".npz"),
        y_val=Y["val"].astype(np.int8),
        y_test=Y["test"].astype(np.int8),
        **{f"{p}_{k}": r.pop(k).astype(np.float32) for p, r in res.items() for k in ("scores_val", "scores_test")},
    )
    dest.write_text(json.dumps({**meta, "probes": res, "seconds": time.time() - t0}, default=float))
    return f"done {dest.name} in {time.time() - t0:.0f}s: " + ", ".join(
        f"{p} {100 * r['test_at_best']['roc_auc']:.2f}" for p, r in res.items()
    )


def stage_probe(args) -> None:
    import multiprocessing as mp  # noqa: PLC0415

    work = Path(args.work)
    (work / "probe").mkdir(parents=True, exist_ok=True)
    jobs = probe_jobs(work)
    jobs.sort(key=lambda j: (j[0] != "lr", j[1] != "chbmit"))  # long LR fits first
    log(f"[probe] {len(jobs)} jobs on {args.procs} processes")
    with mp.get_context("fork").Pool(args.procs) as pool:
        for msg in pool.imap_unordered(run_job, [(work, j) for j in jobs]):
            log(f"[probe] {msg}")


# ---- report (Mac) --------------------------------------------------------------------------
def record_roc(results: Path, pattern: str, arm: str, seed: int) -> tuple[float, dict]:
    hits = sorted(results.glob(f"{pattern}/results/biot-*-{arm}-s{seed}-*.json"))
    if len(hits) != 1:
        raise RuntimeError(f"{pattern} {arm} s{seed}: {len(hits)} records")
    r = json.loads(hits[0].read_text())
    return 100 * r["probes"]["linear"]["test_at_best"]["roc_auc"], r


def rule_count(deltas: list[float], gt_only: bool = False) -> dict:
    d = np.array(deltas)
    absn = int((d > THRESH).sum()) if gt_only else int((np.abs(d) > THRESH).sum())
    same = max(int((d > THRESH).sum()), int((d < -THRESH).sum()))
    return {
        "deltas": [round(float(x), 2) for x in d],
        "count": absn,
        "same_sign_count": same,
        "fires": absn >= K,
        "fires_same_sign": same >= K,
    }


def stage_report(args) -> None:
    import matplotlib  # noqa: PLC0415

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt  # noqa: PLC0415

    runs, results, dest = Path(args.runs), Path(args.results), Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)
    R = {}
    for f in (runs / "probe").glob("*.json"):
        j = json.loads(f.read_text())
        for p, r in j["probes"].items():
            R[(j["dataset"], j["split"], j["seed"], j["arm"], j["input"], p)] = r
    # LR on pretrained features is seed-free: paper-split lp LR fitted once, reused for every seed
    for (ds, sp, _s, a, nk, p), r in list(R.items()):
        if sp == "paper" and a == "lp" and p == "lr":
            for s2 in SEEDS:
                R.setdefault((ds, sp, s2, a, nk, p), r)

    def roc(ds, sp, s, a, nk, p):
        return 100 * R[(ds, sp, s, a, nk, p)]["test_at_best"]["roc_auc"]

    probes = ("parity_raw", "parity_z", "lr")
    md, out = (
        [
            "# D25-E15 BIOT probe strength, feature scale and input-scaling precheck",
            "",
            f"Generated by `scripts/analysis/biot_probe_strength.py report` on {time.strftime('%Y-%m-%d %H:%M')}. "
            "Test ROC x100 at the validation-selected epoch (parity heads) or C (LR). Seed S_r per rotation "
            "(42/123/2021/3407/8888). Eval-mode encoder features, all windows (no subsampling).",
            "",
        ],
        {},
    )

    # 1. fidelity: test windows and the raw parity head vs the D24 records ------------------------
    fid, md_f = (
        [],
        [
            "## 1. Fidelity against the D24 records (raw parity head, /100 = the records' probe)",
            "",
            "| dataset | split | seed | arm | record | ours (CPU, cached) | diff | test keys identical |",
            "|---|---|---|---|---|---|---|---|",
        ],
    )
    for ds, (_c, _s, _tag, pat) in DATASETS.items():
        for sp in splits_of(ds):
            for s in seeds_of(sp):
                arms = ("lp", "lp_randinit") + (("last",) if _c == "siena" else ())
                for a in arms:
                    p_ = PAPER[1][a] if sp == "paper" else pat.format(r=sp[3:])
                    rec, r = record_roc(results, p_, a, s)
                    keys = json.loads((results / p_ / "results" / r["test_index"]).read_text())
                    mine = np.load(runs / ds / f"split-{sp}.npz")["test_keys"] if (runs / ds).exists() else None
                    same = None if mine is None else [k["key"] for k in keys] == mine.tolist()
                    ours = roc(ds, sp, s, a, "d100", "parity_raw")
                    fid.append(
                        {
                            "dataset": ds,
                            "split": sp,
                            "seed": s,
                            "arm": a,
                            "record": rec,
                            "ours": ours,
                            "diff": ours - rec,
                            "test_keys_identical": same,
                        }
                    )
                    md_f.append(
                        f"| {ds} | {sp} | {s} | {a} | {rec:.2f} | {ours:.2f} | {ours - rec:+.2f} | {same} |"
                    )
    maxdiff = max(abs(f["diff"]) for f in fid)
    md += md_f + ["", f"Max |ours - record| = {maxdiff:.2f} ROC points over {len(fid)} runs.", ""]
    out["fidelity"] = fid

    # 1b. CPU re-adaptation of `last` vs the GPU records (Siena) ---------------------------------
    md += [
        "### CPU re-adaptation of `last` (Siena, seed S_r) vs the GPU record (S3M; S3FM shares the SSL run)",
        "",
        "| rot | seed | GPU epoch losses | CPU epoch losses | max abs diff | best epoch GPU/CPU | CPU seconds |"
        " rel. displacement block03 GPU / CPU |",
        "|---|---|---|---|---|---|---|---|",
    ]
    adapt_rows = []
    for r_, s in enumerate(SEEDS):
        cpu = json.loads((runs / "states" / f"last-s{s}-rot{r_}.json").read_text())
        _, rec = record_roc(results, DATASETS["siena"][3].format(r=r_), "last", s)
        g, c = rec["adapt"]["epoch_losses"], cpu["epoch_losses"]
        spec_diff = {
            k: (rec["adapt_spec"][k], v)
            for k, v in cpu["adapt_spec"].items()
            if k in rec["adapt_spec"] and json.dumps(rec["adapt_spec"][k]) != json.dumps(v)
        }
        dg = rec["displacement"]["block03"]["rel"]
        dc = cpu["displacement"]["block03"]["rel"]
        adapt_rows.append(
            {
                "rot": r_,
                "seed": s,
                "gpu": g,
                "cpu": c,
                "max_abs_diff": float(np.max(np.abs(np.subtract(g, c)))),
                "spec_mismatch": spec_diff,
                "seconds": cpu["seconds"],
                "disp_rel_block03": [dg, dc],
            }
        )
        md.append(
            f"| rot{r_} | {s} | {', '.join(f'{x:.4f}' for x in g)} | {', '.join(f'{x:.4f}' for x in c)} | "
            f"{adapt_rows[-1]['max_abs_diff']:.4f} | {rec['adapt']['best_epoch']}/{cpu['best_epoch']} | "
            f"{cpu['seconds']:.0f} | {dg:.2e} / {dc:.2e} |"
        )
    md += [
        "",
        "AdaptSpec fields that differ from the record (beyond fields the record predates): "
        + (", ".join(f"rot{a['rot']}: {a['spec_mismatch']}" for a in adapt_rows if a["spec_mismatch"]) or "none"),
        "",
    ]
    out["readapt"] = adapt_rows

    # 2. feature scale ------------------------------------------------------------------------
    md += [
        "## 2. Feature scale (eval-mode encoder output, 256-d, grid windows of the whole store)",
        "",
        "| dataset | features | input | std | mean abs | row norm | per-dim std median [min, max] |",
        "|---|---|---|---|---|---|---|",
    ]
    out["feature_stats"] = {}
    for ds in DATASETS:
        st = {k: v for f in sorted((runs / ds).glob("stats-*.json")) for k, v in json.loads(f.read_text()).items()}
        out["feature_stats"][ds] = st
        for k, v in st.items():
            md.append(
                f"| {ds} | {k.rsplit('-', 1)[0]} | {k.rsplit('-', 1)[1]} | {v['std']:.4g} | {v['mean_abs']:.4g} | "
                f"{v['row_norm_mean']:.4g} | {v['per_dim_std_median']:.4g} [{v['per_dim_std_min']:.3g}, "
                f"{v['per_dim_std_max']:.3g}] |"
            )
    md.append("")

    # 3. the pre-registered rules ---------------------------------------------------------------
    verdicts, contrast = {}, {}
    md += [
        "## 3. D25-E15 rule 1: does z-scoring or LR move lp - lp_randinit by > 3 in >= 4/5 rotations?",
        "",
        "Contrast c = lp - lp_randinit at /100, seed S_r. delta = c[probe] - c[parity raw]. Record column: the "
        "D24 record at S_r and the D24-A 3-seed rotation mean.",
        "",
        "| dataset | rot | lp raw / z / LR | lp_randinit raw / z / LR | c raw | c z | c LR | delta z | delta LR |"
        " c record S_r | c record 3-seed |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for ds, (_c, _s, _tag, pat) in DATASETS.items():
        rows = []
        for r_ in range(5):
            sp, s = f"rot{r_}", SEEDS[r_]
            c = {p: roc(ds, sp, s, "lp", "d100", p) - roc(ds, sp, s, "lp_randinit", "d100", p) for p in probes}
            seeds3 = [s, 1000 + r_, 2000 + r_]
            rec3 = np.mean(
                [
                    record_roc(results, pat.format(r=r_), "lp", x)[0]
                    - record_roc(results, pat.format(r=r_), "lp_randinit", x)[0]
                    for x in seeds3
                ]
            )
            recS = (
                record_roc(results, pat.format(r=r_), "lp", s)[0]
                - record_roc(results, pat.format(r=r_), "lp_randinit", s)[0]
            )
            rows.append(
                {
                    "rot": r_,
                    **{f"c_{p}": c[p] for p in probes},
                    "delta_z": c["parity_z"] - c["parity_raw"],
                    "delta_lr": c["lr"] - c["parity_raw"],
                    "c_record_Sr": recS,
                    "c_record_3seed": rec3,
                    **{f"lp_{p}": roc(ds, sp, s, "lp", "d100", p) for p in probes},
                    **{f"lpr_{p}": roc(ds, sp, s, "lp_randinit", "d100", p) for p in probes},
                }
            )
            q = rows[-1]
            md.append(
                f"| {ds} | {r_} | {q['lp_parity_raw']:.1f} / {q['lp_parity_z']:.1f} / {q['lp_lr']:.1f} | "
                f"{q['lpr_parity_raw']:.1f} / {q['lpr_parity_z']:.1f} / {q['lpr_lr']:.1f} | "
                f"{c['parity_raw']:+.1f} | "
                f"{c['parity_z']:+.1f} | {c['lr']:+.1f} | {q['delta_z']:+.1f} | {q['delta_lr']:+.1f} | "
                f"{recS:+.1f} | {rec3:+.1f} |"
            )
        contrast[ds] = rows
        rz, rl = rule_count([q["delta_z"] for q in rows]), rule_count([q["delta_lr"] for q in rows])
        # sensitivity: deltas against the record baselines instead of our CPU raw head
        sens = {
            b: {p: rule_count([q[f"c_{p}"] - q[f"c_record_{b}"] for q in rows]) for p in ("parity_z", "lr")}
            for b in ("Sr", "3seed")
        }
        verdicts[ds] = {
            "probe_limited": rz["fires"] or rl["fires"],
            "z": rz,
            "lr": rl,
            "probe_limited_same_sign": rz["fires_same_sign"] or rl["fires_same_sign"],
            "sensitivity_record_baseline": sens,
        }
    md.append("")
    md += [
        "| dataset | rotations |delta z| > 3 (same sign) | rotations |delta LR| > 3 (same sign) | VERDICT |",
        "|---|---|---|---|",
    ]
    for ds, v in verdicts.items():
        word = (
            "BIOT conclusions are probe-limited"
            if v["probe_limited"]
            else "not probe-limited (rule does not fire)"
        )
        md.append(
            f"| {ds} | {v['z']['count']}/5 ({v['z']['same_sign_count']}) | {v['lr']['count']}/5 "
            f"({v['lr']['same_sign_count']}) | **{word}** |"
        )
    any_pl = any(v["probe_limited"] for v in verdicts.values())
    md += [
        "",
        f"E26 (strong/standardized probe on GPU) is **{'TRIGGERED' if any_pl else 'NOT triggered'}** by E15.",
        "Sensitivity (descriptive): the same counts with the D24 record contrast as the baseline: "
        + "; ".join(
            f"{ds}: "
            + ", ".join(
                f"{b} {p} {v['sensitivity_record_baseline'][b][p]['count']}/5"
                for b in ("Sr", "3seed")
                for p in ("parity_z", "lr")
            )
            for ds, v in verdicts.items()
        ),
        "",
    ]

    md += [
        "## 4. D25-E15 rule 2: is lp(q95) - lp(/100) > 3 in >= 4/5 rotations?",
        "",
        "Primary probe: parity raw (the pipeline's head, as E19 will run it). z / LR descriptive.",
        "",
        "| dataset | rot | lp /100 raw / z / LR | lp q95 raw / z / LR | q95 - /100 raw | z | LR |"
        " lp_randinit q95 - /100 raw |",
        "|---|---|---|---|---|---|---|---|",
    ]
    qrows = {}
    for ds in DATASETS:
        qrows[ds] = []
        for r_ in range(5):
            sp, s = f"rot{r_}", SEEDS[r_]
            d = {p: roc(ds, sp, s, "lp", "q95", p) - roc(ds, sp, s, "lp", "d100", p) for p in probes}
            dr = roc(ds, sp, s, "lp_randinit", "q95", "parity_raw") - roc(
                ds, sp, s, "lp_randinit", "d100", "parity_raw"
            )
            qrows[ds].append({"rot": r_, **{f"d_{p}": d[p] for p in probes}, "d_randinit_raw": dr})
            md.append(
                f"| {ds} | {r_} | "
                + " / ".join(f"{roc(ds, sp, s, 'lp', 'd100', p):.1f}" for p in probes)
                + " | "
                + " / ".join(f"{roc(ds, sp, s, 'lp', 'q95', p):.1f}" for p in probes)
                + f" | {d['parity_raw']:+.1f} | {d['parity_z']:+.1f} | {d['lr']:+.1f} | {dr:+.1f} |"
            )
        verdicts[ds]["input_scale"] = {
            p: rule_count([q[f"d_{p}"] for q in qrows[ds]], gt_only=True) for p in probes
        }
        verdicts[ds]["input_scale_matters"] = verdicts[ds]["input_scale"]["parity_raw"]["fires"]
    md += [
        "",
        "| dataset | rotations > +3 (parity raw, PRIMARY) | z (descr.) | LR (descr.) | VERDICT |",
        "|---|---|---|---|---|",
    ]
    for ds, v in verdicts.items():
        word = "input scale matters" if v["input_scale_matters"] else "input scale: rule does not fire"
        md.append(
            f"| {ds} | {v['input_scale']['parity_raw']['count']}/5 | {v['input_scale']['parity_z']['count']}/5 | "
            f"{v['input_scale']['lr']['count']}/5 | **{word}** |"
        )
    md += ["", "E19 runs either way (must).", ""]

    # 5. descriptive: Siena last - lp; paper split ---------------------------------------------
    md += [
        "## 5. Descriptive: Siena `last` - lp under each probe (CPU re-adapted `last`, seed S_r, /100)",
        "",
        "| dataset | rot | last raw / z / LR | last - lp raw | z | LR | record last - lp (S_r) |",
        "|---|---|---|---|---|---|---|",
    ]
    sa = {}
    for ds in ("siena", "siena_filt"):
        sa[ds] = []
        for r_ in range(5):
            sp, s = f"rot{r_}", SEEDS[r_]
            d = {p: roc(ds, sp, s, "last", "d100", p) - roc(ds, sp, s, "lp", "d100", p) for p in probes}
            pat = DATASETS[ds][3].format(r=r_)
            rec = record_roc(results, pat, "last", s)[0] - record_roc(results, pat, "lp", s)[0]
            sa[ds].append({"rot": r_, **{f"d_{p}": d[p] for p in probes}, "record_Sr": rec})
            md.append(
                f"| {ds} | {r_} | "
                + " / ".join(f"{roc(ds, sp, s, 'last', 'd100', p):.1f}" for p in probes)
                + f" | {d['parity_raw']:+.1f} | {d['parity_z']:+.1f} | {d['lr']:+.1f} | {rec:+.1f} |"
            )
        md.append(
            f"| {ds} | mean | | "
            + " | ".join(f"{np.mean([q[f'd_{p}'] for q in sa[ds]]):+.1f}" for p in probes)
            + f" | {np.mean([q['record_Sr'] for q in sa[ds]]):+.1f} |"
        )
    md += [
        "",
        "## 6. Descriptive: CHB-MIT paper split (upstream labels, as P1E), 5 seeds, /100 and q95",
        "",
        "| arm | input | parity raw | parity z | LR |",
        "|---|---|---|---|---|",
    ]
    paper = {}
    for a in ("lp", "lp_randinit"):
        for nk in NORMS:
            vals = {p: [roc("chbmit", "paper", s, a, nk, p) for s in SEEDS] for p in probes}
            paper[f"{a}-{nk}"] = vals
            md.append(
                f"| {a} | {nk} | "
                + " | ".join(f"{np.mean(v):.1f} ± {np.std(v, ddof=1) / math.sqrt(5):.1f}" for v in vals.values())
                + " |"
            )
    md += ["", "(mean ± SEM over 5 seeds; LR on pretrained features is seed-free, so its SEM is 0.)", ""]
    out.update(
        {"verdicts": verdicts, "contrast": contrast, "q95": qrows, "siena_last_minus_lp": sa, "paper": paper}
    )

    # LR grid-edge and convergence audit
    edge = [k for k, r in R.items() if k[5] == "lr" and r["C_at_grid_edge"]]
    nonconv = [k for k, r in R.items() if k[5] == "lr" and not all(x["converged"] for x in r["sweep"])]
    md += [
        "## 7. Probe audit",
        "",
        f"- LR fits whose selected C sits on the grid edge {LR_GRID[0]} / {LR_GRID[-1]}: {len(edge)} of "
        f"{sum(k[5] == 'lr' for k in R)}: "
        + ", ".join("/".join(map(str, k[:5])) + f" C={R[k]['C']}" for k in edge),
        f"- LR fits with a ConvergenceWarning at any C: {len(nonconv)}",
        "- Parity heads whose best epoch is the last one (val ROC still rising, head under-trained): "
        + ", ".join(
            f"{p} {sum(R[k]['best_epoch'] == 9 for k in R if k[5] == p)}/{sum(k[5] == p for k in R)}"
            for p in ("parity_raw", "parity_z")
        ),
        "",
    ]
    out["audit"] = {"lr_grid_edge": ["/".join(map(str, k)) for k in edge], "lr_nonconverged": len(nonconv)}

    # ---- figures ----
    C_BLUE, C_ORANGE, C_AQUA, INK, MUTED = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#8a8984"
    PC = {"parity_raw": C_BLUE, "parity_z": C_ORANGE, "lr": C_AQUA}
    PL = {
        "parity_raw": "parity head, raw (as run)",
        "parity_z": "parity head, z-scored",
        "lr": "std. LR (C on val)",
    }
    plt.rcParams.update(
        {
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.color": "#e6e5e0",
            "grid.linewidth": 0.6,
            "axes.edgecolor": MUTED,
            "axes.labelcolor": INK,
            "xtick.color": INK,
            "ytick.color": INK,
            "font.size": 9,
            "legend.frameon": False,
            "figure.dpi": 150,
        }
    )
    names = {"chbmit": "CHB-MIT", "siena": "Siena", "siena_filt": "Siena filtered"}
    figs = []

    def save(fig, name):
        fig.savefig(dest / name, bbox_inches="tight")
        plt.close(fig)
        figs.append(name)

    # F1 feature scale
    fig, axs = plt.subplots(1, 3, figsize=(11, 3.2), sharey=True)
    for ax, ds in zip(axs, DATASETS, strict=True):
        st = out["feature_stats"][ds]
        for xi, nk in enumerate(NORMS):
            ax.scatter(
                [xi - 0.12],
                [st[f"pre-{nk}"]["std"]],
                color=C_BLUE,
                s=40,
                zorder=3,
                label="pretrained (lp)" if xi == 0 else None,
            )
            ax.scatter(
                [xi + 0.12] * 5,
                [st[f"rnd{s}-{nk}"]["std"] for s in SEEDS],
                color=C_ORANGE,
                s=22,
                zorder=3,
                label="random init, 5 seeds (lp_randinit)" if xi == 0 else None,
            )
            if ds != "chbmit" and nk == "d100":
                ax.scatter(
                    [xi] * 5,
                    [st[f"last{s}-d100"]["std"] for s in SEEDS],
                    color=C_AQUA,
                    s=22,
                    marker="D",
                    zorder=3,
                    label="last (CPU re-adapted), 5 seeds",
                )
        ax.set_xticks([0, 1], ["/100 (as run)", "per-channel q95"])
        ax.set_yscale("log")
        ax.set_title(names[ds])
    axs[0].set_ylabel("feature std (all dims, all grid windows)")
    axs[2].legend(loc="center left", bbox_to_anchor=(1, 0.5))
    save(fig, "fig1_feature_scale.png")

    # F2 contrast by probe; F3 deltas vs the rule band
    for name, key, ylabel, band in (
        ("fig2_lp_minus_randinit_by_probe.png", None, "lp - lp_randinit (test ROC points)", None),
        ("fig3_rule1_deltas.png", "delta", "change in lp - lp_randinit vs raw parity head", THRESH),
    ):
        fig, axs = plt.subplots(1, 3, figsize=(11, 3.2), sharey=True)
        for ax, ds in zip(axs, DATASETS, strict=True):
            rows, x = contrast[ds], np.arange(5)
            if key is None:
                for p in probes:
                    ax.plot(x, [q[f"c_{p}"] for q in rows], "-o", color=PC[p], lw=1.5, ms=5, label=PL[p])
                ax.plot(
                    x, [q["c_record_3seed"] for q in rows], "x", color=MUTED, ms=6, label="D24 record, 3-seed mean"
                )
            else:
                ax.plot(
                    x,
                    [q["delta_z"] for q in rows],
                    "-o",
                    color=PC["parity_z"],
                    lw=1.5,
                    ms=5,
                    label="z-scored - raw",
                )
                ax.plot(x, [q["delta_lr"] for q in rows], "-o", color=PC["lr"], lw=1.5, ms=5, label="LR - raw")
                for b in (band, -band):
                    ax.axhline(b, color=MUTED, ls="--", lw=0.8)
                v = verdicts[ds]
                ax.text(
                    0.02,
                    0.97,
                    f"|d|>3: z {v['z']['count']}/5, LR {v['lr']['count']}/5",
                    transform=ax.transAxes,
                    va="top",
                    color=INK,
                )
            ax.axhline(0, color=INK, lw=0.6)
            ax.set_xticks(x, [f"rot{i}" for i in x])
            ax.set_title(names[ds])
        axs[0].set_ylabel(ylabel)
        axs[2].legend(loc="center left", bbox_to_anchor=(1, 0.5))
        save(fig, name)

    # F4 q95 - /100
    fig, axs = plt.subplots(1, 3, figsize=(11, 3.2), sharey=True)
    for ax, ds in zip(axs, DATASETS, strict=True):
        x = np.arange(5)
        for p in probes:
            ax.plot(x, [q[f"d_{p}"] for q in qrows[ds]], "-o", color=PC[p], lw=1.5, ms=5, label=PL[p])
        ax.axhline(THRESH, color=MUTED, ls="--", lw=0.8)
        ax.axhline(0, color=INK, lw=0.6)
        ax.text(
            0.02,
            0.97,
            f">+3 (raw, primary): {verdicts[ds]['input_scale']['parity_raw']['count']}/5",
            transform=ax.transAxes,
            va="top",
            color=INK,
        )
        ax.set_xticks(x, [f"rot{i}" for i in x])
        ax.set_title(names[ds])
    axs[0].set_ylabel("lp(q95) - lp(/100), test ROC points")
    axs[2].legend(loc="center left", bbox_to_anchor=(1, 0.5))
    save(fig, "fig4_rule2_q95_minus_d100.png")

    # F5 training curves per dataset (+ paper split): arm = colour, probe = line style
    cols = (
        ("train_loss", "train BCE"),
        ("val_loss", "val BCE"),
        ("val", "val ROC (selection)"),
        ("test_plot_only", "test ROC (plot only)"),
    )
    arm_c = {"lp": C_BLUE, "lp_randinit": C_ORANGE, "last": C_AQUA}
    for ds in list(DATASETS) + ["paper"]:
        dsr, splits = ("chbmit", ["paper"]) if ds == "paper" else (ds, [f"rot{r}" for r in range(5)])
        arms = ("lp", "lp_randinit") + (("last",) if dsr != "chbmit" else ())
        for nk in NORMS:
            fig, axs = plt.subplots(len(splits), 4, figsize=(12, 2.1 * len(splits) + 0.6), squeeze=False)
            for i, sp in enumerate(splits):
                s = seeds_of(sp)[0]
                for a in arms:
                    if a == "last" and nk != "d100":
                        continue
                    for p, ls in (("parity_raw", "-"), ("parity_z", "--")):
                        h = R[(dsr, sp, s, a, nk, p)]["history"]
                        for j, (k, _t) in enumerate(cols):
                            yv = [e[k]["roc_auc"] if isinstance(e[k], dict) else e[k] for e in h]
                            axs[i, j].plot(
                                range(1, 11),
                                yv,
                                ls,
                                color=arm_c[a],
                                lw=1.3,
                                label=f"{a}, {'raw' if p == 'parity_raw' else 'z-scored'}",
                            )
                axs[i, 0].set_ylabel(f"{sp} (s{s})")
                for j, (_k, t) in enumerate(cols):
                    if i == 0:
                        axs[i, j].set_title(t)
                    if i == len(splits) - 1:
                        axs[i, j].set_xlabel("probe epoch")
            axs[0, 3].legend(loc="center left", bbox_to_anchor=(1, 0.5))
            fig.suptitle(
                f"{names.get(ds, 'CHB-MIT paper split')}: parity linear head per epoch, input {nk}", y=1.0
            )
            save(fig, f"fig5_curves_{ds}_{nk}.png")

    # F6 LR C sweeps
    fig, axs = plt.subplots(2, 3, figsize=(11, 5.6), sharex=True)
    for col, ds in enumerate(DATASETS):
        for row, a in enumerate(("lp", "lp_randinit")):
            ax = axs[row, col]
            for r_ in range(5):
                sw = R[(ds, f"rot{r_}", SEEDS[r_], a, "d100", "lr")]["sweep"]
                cs = [w["C"] for w in sw]
                ax.plot(
                    cs,
                    [100 * w["val"]["roc_auc"] for w in sw],
                    "-o",
                    color=arm_c[a],
                    lw=1,
                    ms=3,
                    alpha=0.4 + 0.12 * r_,
                )
                ax.plot(cs, [100 * w["test_plot_only"]["roc_auc"] for w in sw], ":", color=MUTED, lw=1)
            ax.set_xscale("log")
            ax.set_title(f"{names[ds]}, {a}")
            if col == 0:
                ax.set_ylabel("ROC (solid: val, dotted: test plot only)")
            if row == 1:
                ax.set_xlabel("C")
    save(fig, "fig6_lr_C_sweep.png")

    # F7 SSL re-adaptation losses
    fig, ax = plt.subplots(figsize=(6.5, 3.4))
    for r_, a in enumerate(adapt_rows):
        cpu = json.loads((runs / "states" / f"last-s{a['seed']}-rot{r_}.json").read_text())
        steps = np.arange(1, len(cpu["step_losses"]) + 1)
        ax.plot(
            steps,
            cpu["step_losses"],
            color=C_BLUE,
            lw=1,
            alpha=0.35 + 0.13 * r_,
            label="CPU per step" if r_ == 0 else None,
        )
        per = len(steps) // len(a["gpu"])
        ax.plot(
            [per * (e + 1) for e in range(len(a["gpu"]))],
            a["gpu"],
            "x",
            color=C_ORANGE,
            ms=7,
            label="GPU record, epoch mean" if r_ == 0 else None,
        )
        ax.plot(
            [per * (e + 1) for e in range(len(a["cpu"]))],
            a["cpu"],
            "o",
            mfc="none",
            color=C_BLUE,
            ms=7,
            label="CPU epoch mean" if r_ == 0 else None,
        )
    ax.set_xlabel("optimizer step")
    ax.set_ylabel("BIOT contrastive SSL loss")
    ax.set_title("Siena `last` re-adaptation, rot0-4 at seed S_r")
    ax.legend()
    save(fig, "fig7_readapt_ssl_loss.png")

    # F8 Siena last - lp
    fig, axs = plt.subplots(1, 2, figsize=(8.5, 3.2), sharey=True)
    for ax, ds in zip(axs, ("siena", "siena_filt"), strict=True):
        x = np.arange(5)
        for p in probes:
            ax.plot(x, [q[f"d_{p}"] for q in sa[ds]], "-o", color=PC[p], lw=1.5, ms=5, label=PL[p])
        ax.plot(x, [q["record_Sr"] for q in sa[ds]], "x", color=MUTED, ms=6, label="D24 record (S_r)")
        ax.axhline(0, color=INK, lw=0.6)
        ax.set_xticks(x, [f"rot{i}" for i in x])
        ax.set_title(names[ds])
    axs[0].set_ylabel("last - lp (test ROC points)")
    axs[1].legend(loc="center left", bbox_to_anchor=(1, 0.5))
    save(fig, "fig8_siena_last_minus_lp.png")

    # F9 paper split per seed
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.2), sharey=True)
    for ax, nk in zip(axs, NORMS, strict=True):
        for xi, p in enumerate(probes):
            for a, off in (("lp", -0.12), ("lp_randinit", 0.12)):
                ax.scatter(
                    [xi + off] * 5,
                    paper[f"{a}-{nk}"][p],
                    color=arm_c[a],
                    s=18,
                    zorder=3,
                    label=a if xi == 0 else None,
                )
        ax.set_xticks(range(3), [PL[p] for p in probes], rotation=12)
        ax.set_title(f"CHB-MIT paper split, input {nk}")
    axs[0].set_ylabel("test ROC (5 seeds)")
    axs[1].legend(loc="center left", bbox_to_anchor=(1, 0.5))
    save(fig, "fig9_paper_split.png")

    md += ["## Figures", ""] + [f"- `{f}`" for f in figs] + [""]
    (dest / "biot_probe.md").write_text("\n".join(md))
    (dest / "biot_probe.json").write_text(json.dumps(out, indent=1, default=float))
    log(f"[report] wrote {dest / 'biot_probe.md'} and {len(figs)} figures")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=("selfcheck", "queue", "adapt", "extract", "probe", "report"))
    ap.add_argument("--work", default=str(Path.home() / "e15/work"))
    ap.add_argument("--lmdb", default=str(Path.home() / "dxdata/lmdb"))
    ap.add_argument("--dataset", choices=tuple(DATASETS), default="chbmit")
    ap.add_argument("--models", default="", help="extract: comma list of pre,rnd<seed>,last<seed> (default all)")
    ap.add_argument("--norms", default="", help="extract: comma list of d100,q95 (default both)")
    ap.add_argument("--rot", type=int, nargs="+", default=list(range(5)))
    ap.add_argument("--chunk", type=int, default=4096)
    ap.add_argument("--threads", type=int, default=48)
    ap.add_argument("--procs", type=int, default=24)
    ap.add_argument("--runs", default=str(REPO / "artifacts/analysis/biot_probe/runs"))
    ap.add_argument("--results", default=str(REPO / "artifacts/s3-results"))
    ap.add_argument("--dest", default=str(REPO / "artifacts/analysis/biot_probe"))
    args = ap.parse_args()
    torch.set_num_threads(args.threads)
    {
        "selfcheck": selfcheck,
        "queue": stage_queue,
        "adapt": stage_adapt,
        "extract": stage_extract,
        "probe": stage_probe,
        "report": stage_report,
    }[args.stage](args)


if __name__ == "__main__":
    main()
