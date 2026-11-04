"""D25-E21: differential test, our reimplementation vs the RELEASED modules, run in one process.

The released code (c3n-group/efficient-eeg-adapt @ d056cdf) is imported from a local clone at
test time ($EEA_CLONE, else ~/released/eea); the test skips if it is absent. Nothing is copied
from it. Its config comes from Hydra composed against the clone's own src/conf.

Per (model, probe head, start state): the same start state_dict, 2 SSL steps (2 epochs of one
16-window batch, so the lowest-loss-epoch restore runs too), transfer, 1 probe epoch on 512
windows (2 batches), then compare SSL losses, adapted weights, probe loss, head weights, test
logits and test metrics. Pairing: ours `linear` <-> released training.full_ft=False; ours
`mlp_fullft` <-> full_ft=True; ours backbone_mode="train" (released probes in train mode) and,
for CBraMod, tap="proj_out" (released reads proj_out, model_factory.py:29 commented out).

Harness interventions (test-side only, the released source is never edited):
* RNG alignment: the per-step randomness (CBraMod mask, BIOT perturbation, dropout) is reseeded
  identically at the start of each SSL loss call and each training-mode probe forward, in both
  pipelines. The SSL DataLoader is given our seeded generator so both shuffle identically, and
  the probe's train loader iterates the released CustomDataset in our permutation order.
* Same start state: the released setup_*_spt result is overwritten (strict) with our start
  state_dict, and the released classifier with our initial head.
* `visualization` (t-SNE/UMAP plots) is stubbed; `wandb` is stubbed only if not installed
  (training.wandb=False, so it is never called).
"""

from __future__ import annotations

import contextlib
import importlib
import json
import os
import pickle
import sys
import types
from functools import partial
from pathlib import Path

import numpy as np
import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("hydra")
pytest.importorskip("einops")
pytest.importorskip("linear_attention_transformer")

CLONE = Path(os.environ.get("EEA_CLONE", "~/released/eea")).expanduser().resolve()
if not (CLONE / "src" / "trainer.py").exists():
    pytest.skip(f"released clone not found at {CLONE} (set EEA_CLONE)", allow_module_level=True)

SEED = 42
TOL = 1e-5
N_SSL, N_TRAIN, N_VAL, N_TEST = 16, 512, 128, 128
_RELEASED_TOP = ("trainer", "model_factory", "refactor_datasets", "visualization", "models", "utils",
                 "datasets", "dataset_pretrain")


@pytest.fixture(scope="module")
def released():
    """Import the released modules; restore sys.path / sys.modules afterwards."""
    old_path, old_mods, old_bc = list(sys.path), set(sys.modules), sys.dont_write_bytecode
    sys.dont_write_bytecode = True                     # never write into the clone
    shadowed = {k: sys.modules.pop(k) for k in list(sys.modules)
                if k.split(".")[0] in _RELEASED_TOP}
    sys.path.insert(0, str(CLONE / "src"))
    viz = types.ModuleType("visualization")
    viz.generate_visualizations = lambda *a, **k: ""
    sys.modules["visualization"] = viz
    if importlib.util.find_spec("wandb") is None:
        sys.modules["wandb"] = types.ModuleType("wandb")
    try:
        ns = types.SimpleNamespace(trainer=importlib.import_module("trainer"),
                                   chbmit=importlib.import_module("datasets.chbmit"))
        yield ns
    finally:
        for k in set(sys.modules) - old_mods:
            sys.modules.pop(k, None)
        sys.modules.update(shadowed)
        sys.path[:] = old_path
        sys.dont_write_bytecode = old_bc


@pytest.fixture(scope="module")
def data(tmp_path_factory):
    """Synthetic uV windows, written in the released on-disk formats."""
    import lmdb
    from scipy.signal import resample

    root = tmp_path_factory.mktemp("e21")
    rng = np.random.default_rng(SEED)
    ssl = (rng.standard_normal((N_SSL, 16, 30, 200)) * 50).astype(np.float32)
    env = lmdb.open(str(root / "ssl.lmdb"), map_size=1 << 30)
    keys = [f"w{i:02d}" for i in range(N_SSL)]
    with env.begin(write=True) as txn:
        for k, x in zip(keys, ssl, strict=True):
            txn.put(k.encode(), pickle.dumps(x, protocol=pickle.HIGHEST_PROTOCOL))
        txn.put(b"__keys__", pickle.dumps(keys))
    env.close()
    t = np.arange(2560) / 256
    for split, n in (("train", N_TRAIN), ("val", N_VAL), ("test", N_TEST)):
        (root / "eval" / split).mkdir(parents=True)
        y = (rng.random(n) < 0.25).astype(int)
        y[:2] = (0, 1)
        for i in range(n):
            x = rng.standard_normal((16, 2560)) * 30 + y[i] * 6 * np.sin(2 * np.pi * 5 * t)
            with open(root / "eval" / split / f"chb99_{i:03d}-{i * 2560}.pkl", "wb") as f:
                pickle.dump({"X": x, "y": int(y[i])}, f)
    return {"root": root, "ssl": torch.from_numpy(ssl), "resample": resample}


def compose(model: str, full_ft: bool, root: Path, out: Path):
    from hydra import compose as hcompose
    from hydra import initialize_config_dir

    with initialize_config_dir(config_dir=str(CLONE / "src" / "conf"), version_base=None):
        return hcompose(config_name="config", overrides=[
            "~launchers", f"model={model}", "dataset=chbmit", "method=step_up", f"seed={SEED}",
            "+method.spt_anchor_l2sp_lambda=0", "+training.ft_only=true", "training.wandb=False",
            f"training.full_ft={full_ft}", "dataset.method.spt_epochs=2", "dataset.training.epochs=1",
            "model.use_pretrained_weights=False", f"output_dir={out}",
            f"dataset.datasets_dir={root / 'eval'}", f"dataset.pretrain_datasets_dir={root / 'ssl.lmdb'}"])


class Reseed:
    """Callable wrapper: reseed torch + numpy before each (training-mode) call."""

    def __init__(self, fn, base: int, when=lambda: True, record: list | None = None):
        self.fn, self.base, self.when, self.k, self.record = fn, base, when, 0, record

    def __call__(self, *a, **kw):
        if self.when():
            torch.manual_seed(self.base + self.k)
            np.random.seed(self.base + self.k)
            self.k += 1
        out = self.fn(*a, **kw)
        if self.record is not None:
            self.record.append(float(out.item()))
        return out


def maxdiff(a, b) -> float:
    return float((torch.as_tensor(a, dtype=torch.float64) - torch.as_tensor(b, dtype=torch.float64)).abs().max())


@pytest.mark.parametrize("init", ["random", "pretrained"])
@pytest.mark.parametrize("variant", ["linear", "mlp_fullft"])
@pytest.mark.parametrize("model_name", ["biot", "cbramod"])
def test_released_differential(released, data, registry, tmp_path, monkeypatch, model_name, variant, init):
    import eegdrift.probe as probe_mod
    from eegdrift.adapt import AdaptSpec, adapt, seed_everything
    from eegdrift.models.protocols import state_copy
    from eegdrift.objectives import objective_for

    if init == "pretrained" and not registry.checkpoint_path(model_name).exists():
        pytest.skip(f"no {model_name} checkpoint")
    torch.set_num_threads(min(16, os.cpu_count() or 1))
    dev = torch.device("cpu")
    n_blocks = registry.specs[model_name].n_blocks
    groups = (f"block{n_blocks - 1:02d}", "head")
    tap = "proj_out" if model_name == "cbramod" else "encoder"

    # ---------------- ours
    seed_everything(SEED)
    ours = registry.build(model_name, init=init)
    start = state_copy(ours.module)
    obj = objective_for(ours, 0.5)
    our_ssl_losses: list[float] = []
    obj.loss = Reseed(obj.loss, 1000, record=our_ssl_losses)
    spec = AdaptSpec(model=model_name, dataset="chbmit", arm="last" if init == "pretrained" else "last_randinit",
                     groups=groups, init=init, seed=SEED, protocol="parity", batch=256, epochs=2,
                     n_windows=N_SSL, n_total=N_SSL, scale=700.0, mask_ratio=0.5)
    res = adapt(ours, obj, spec, data["ssl"], dev, log=lambda s: None)

    rel_sets = {s: released.chbmit.CustomDataset(str(data["root"] / "eval"), mode=s)
                for s in ("train", "val", "test")}

    def load(split):
        xs, ys = [], []
        for f in rel_sets[split].files:   # the released dataset's own file order
            with open(f, "rb") as fh:
                d = pickle.load(fh)
            xs.append(data["resample"](d["X"], 2000, axis=1).reshape(16, 10, 200).astype(np.float32))
            ys.append(d["y"])
        return torch.from_numpy(np.stack(xs)), torch.tensor(ys)

    ev = {s: load(s) for s in ("train", "val", "test")}
    heads: list = []
    real_build = probe_mod.build_head

    def build_head(*a, **kw):
        h = real_build(*a, **kw)
        heads.append((h, {k: v.clone() for k, v in h.state_dict().items()}))
        return h

    monkeypatch.setattr(probe_mod, "build_head", build_head)
    probe_losses: list[float] = []
    ours.features = Reseed(ours.features, 2000, when=lambda: ours.encoder().training)
    pspec = probe_mod.ProbeSpec(model=model_name, dataset="chbmit", variant=variant, seed=SEED, n_classes=2,
                                window_s=10, epochs=1, scale=100.0, batch=256, backbone_mode="train", tap=tap)
    pres, arrays = probe_mod.parity_probe(ours, pspec, ev, dev, log=lambda s: None)
    our_head, head0 = heads[0]
    probe_losses.append(pres.history[0]["train_loss"])

    # ---------------- released
    cfg = compose(model_name, variant == "mlp_fullft", data["root"], tmp_path / "released")
    T = released.trainer.Trainer
    tr = T.__new__(T)
    tr.cfg, tr.device, tr.use_wandb, tr.wandb = cfg, dev, False, None
    torch.manual_seed(SEED)
    tr.model = released.trainer.get_model(cfg, dev)
    order = torch.randperm(N_TRAIN, generator=torch.Generator().manual_seed(SEED)).tolist()
    DL, Subset = torch.utils.data.DataLoader, torch.utils.data.Subset
    # the released loop gets exactly the float32 tensors our probe feeds the model (x / 100); the
    # released loader's own float64 transform is checked against ours separately ("input_rel")
    td = {s: torch.utils.data.TensorDataset(ev[s][0] / 100.0, ev[s][1]) for s in ev}
    tr.train_loader = DL(Subset(td["train"], order), batch_size=256)
    tr.val_loader = DL(td["val"], batch_size=256)
    tr.test_loader = DL(td["test"], batch_size=256)
    tr.setup_freezing(phase="spt")
    tr.setup_optimization()

    setup_name = f"setup_{model_name}_spt"
    real_setup = getattr(tr, setup_name)

    def setup_same_start():
        m = real_setup()
        m.load_state_dict(start, strict=True)
        return m

    setattr(tr, setup_name, setup_same_start)
    rel_ssl_losses: list[float] = []
    fwd = f"{model_name}_spt_forward"
    setattr(tr, fwd, Reseed(getattr(tr, fwd), 1000, record=rel_ssl_losses))
    with monkeypatch.context() as m:
        m.setattr(released.trainer, "DataLoader", partial(DL, generator=torch.Generator().manual_seed(SEED)))
        with contextlib.redirect_stdout(open(os.devnull, "w")):
            tr.train_step_up_pretraining()
    spt_files = list((tmp_path / "released" / "spt_checkpoints").glob("*_best.pth"))
    rel_spt = torch.load(spt_files[0], map_location="cpu", weights_only=True)

    tr.setup_freezing(phase="lp")
    tr.model.classifier.load_state_dict(head0, strict=True)
    tr.setup_optimization()
    rel_probe_batch_losses: list[float] = []
    tr.criterion = Reseed(tr.criterion, 0, when=lambda: False, record=rel_probe_batch_losses)
    tr.model.forward = Reseed(tr.model.forward, 2000, when=lambda: tr.model.training)
    with contextlib.redirect_stdout(open(os.devnull, "w")):
        last, best = tr.train()
    tr.model.eval()
    with torch.no_grad():
        rel_logits = torch.cat([tr.model(x) for x, _ in tr.test_loader])

    # ---------------- compare
    n_train_batches = len(tr.train_loader)
    input_rel = max(maxdiff(rel_sets[s][i][0], ev[s][0][i] / 100.0) / float(ev[s][0][i].abs().max() / 100.0)
                    for s in ev for i in range(0, len(ev[s][0]), 7))
    # released scoring: float32 sigmoid, threshold 0.5. Ours scores raw logits (PROBE_CODE_VERSION 3),
    # which can break float32-sigmoid ties: compared, but reported separately ("*_native")
    p_last = torch.sigmoid(torch.from_numpy(arrays["scores_last"])).numpy()
    as_released = probe_mod.metrics(arrays["y_test"], p_last, 2, 0.5)
    d = {
        "ssl_loss": maxdiff(our_ssl_losses, rel_ssl_losses),
        "ssl_weights": max(maxdiff(res.state[k], rel_spt[k]) for k in rel_spt),
        "ssl_moved": max(maxdiff(res.state[k], start[k]) for k in start),
        # AdamW at lr 3e-5 moves weights by ~1e-5 per step, the same order as TOL: so also
        # compare the UPDATES, relative to their size (kept out of the TOL assertion below)
        "ssl_update_rel": max(maxdiff(res.state[k] - start[k], rel_spt[k] - start[k]) for k in start)
        / max(maxdiff(res.state[k], start[k]) for k in start),
        "probe_loss": abs(probe_losses[0] - float(np.mean(rel_probe_batch_losses[:n_train_batches]))),
        "head_weights": max(maxdiff(v, tr.model.classifier.state_dict()[k])
                            for k, v in our_head.state_dict().items()),
        "logits_rel": max(maxdiff(arrays[k], rel_logits) for k in ("scores_best", "scores_last"))
        / max(1.0, float(rel_logits.abs().max())),
        "roc_auc": abs(as_released["roc_auc"] - last["roc_auc"]),
        "pr_auc": abs(as_released["pr_auc_trapz"] - last["pr_auc"]),
        "bal_acc": abs(as_released["bal_acc"] - last["acc"]),
        "best_vs_last_released": abs(best["roc_auc"] - last["roc_auc"]),
        "input_rel": input_rel,
    }
    native = {"roc_auc_native": abs(pres.test_last["roc_auc"] - last["roc_auc"]),
              "pr_auc_native": abs(pres.test_last["pr_auc_trapz"] - last["pr_auc"]),
              "bal_acc_native": abs(pres.test_last["bal_acc"] - last["acc"])}
    print("E21", json.dumps({"model": model_name, "variant": variant, "init": init,
                             "n_ssl_steps": len(rel_ssl_losses), "ssl_losses_ours": our_ssl_losses,
                             "ssl_losses_released": rel_ssl_losses, "roc_ours": pres.test_last["roc_auc"],
                             "roc_released": last["roc_auc"], "maxdiff": d, "descriptive": native}))
    assert len(our_ssl_losses) == len(rel_ssl_losses) == 2
    assert d["ssl_moved"] > 0, "adaptation did not move the weights; the comparison would be vacuous"
    assert d["ssl_update_rel"] <= 1e-3, d
    bad = {k: v for k, v in d.items() if k not in ("ssl_moved", "ssl_update_rel") and not v <= TOL}
    assert not bad, f"ours != released beyond {TOL}: {bad}"
