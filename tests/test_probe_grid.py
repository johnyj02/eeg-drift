"""D28 grid probes (src/eegdrift/probe_grid.py) on tiny synthetic features, plus the guarantee that the
existing probe variants and result keys are untouched."""

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
import torch

from eegdrift.probe_grid import CONFIGS, fit_grid, grid_probe, train_stats

CPU = torch.device("cpu")
PILOT = Path(__file__).resolve().parents[1] / "data" / "lmdb" / "chbmit_eval10"


def _quiet(*_):
    pass


def _feats(seed=0, n=(400, 200, 200), d=8, signal=0.6):
    g = torch.Generator().manual_seed(seed)
    out = {}
    for split, m in zip(("train", "val", "test"), n, strict=True):
        y = (torch.rand(m, generator=g) < 0.3).long()
        x = torch.randn(m, d, generator=g) + signal * y[:, None] * torch.linspace(1, 0, d)
        out[split] = ((3 * x + 5).half(), y)   # off-centre, scaled: standardizing matters
    return out


def _fit(feats, variants=("grid", "grid_z"), seed=1, max_epochs=30):
    return fit_grid(feats, variants, seed, CPU, _quiet, max_epochs)


def _strip(rec):
    return {k: v for k, v in rec.items() if k != "seconds"}


def test_selection_uses_validation_only():
    a = _feats()
    # test = val with flipped labels: test ROC = 1 - val ROC, so the config best on test is the worst on val
    b = {**a, "test": (a["val"][0], 1 - a["val"][1])}
    ra, rb = _fit(a), _fit(b)
    for v in ("grid", "grid_z"):
        rec = rb[v][0]
        best = [c["best_val"] for c in rec["configs"]]
        assert len(set(best)) > 1 and rec["selected"]["index"] == int(np.argmax(best))   # first max
        assert rec["selected"]["index"] != int(np.argmin(best))   # the config best on test is not taken
        assert rec["test_at_best"]["roc_auc"] == pytest.approx(1 - rec["val_at_best"]["roc_auc"])
        assert rec["val_at_best"]["roc_auc"] == rec["best_val"]   # snapshot reproduces the chosen epoch
        # a different test set changes nothing but the test metrics and scores
        drop = ("test_at_best", "seconds")
        assert {k: x for k, x in rec.items() if k not in drop} == \
            {k: x for k, x in ra[v][0].items() if k not in drop}
        assert np.array_equal(rb[v][1]["scores_val_best"], ra[v][1]["scores_val_best"])
    lr, wd = CONFIGS[rb["grid"][0]["selected"]["index"]]
    assert (lr, wd) == (rb["grid"][0]["selected"]["lr"], rb["grid"][0]["selected"]["weight_decay"])


def test_tie_rule_prefers_smaller_lr_then_wd():
    assert CONFIGS == tuple(sorted(CONFIGS)) and len(CONFIGS) == 16   # np.argmax takes the first max


def test_early_stopping_fires():
    g = torch.Generator().manual_seed(0)
    feats = {}
    for split, m in (("train", 300), ("val", 100), ("test", 100)):
        y = torch.tensor([0, 1] * (m // 2))
        feats[split] = ((torch.randn(m, 4, generator=g) * 0.1 + 4 * y[:, None]).half(), y)   # separable
    out = _fit(feats, max_epochs=200)
    for v in ("grid", "grid_z"):
        rec = out[v][0]
        assert rec["epochs_run"] < 200 and rec["converged"]
        for c in rec["configs"]:
            curve = c["val_curve"]
            assert c["converged"] and c["epochs_run"] == len(curve) == len(c["train_loss"]) < 200
            assert max(curve[-20:]) <= max(curve[:-20]) + 1e-4   # 20 epochs without a real gain
            assert c["best_epoch"] == int(np.argmax(curve))


def test_stopped_heads_frozen_stop_epoch_exact(monkeypatch):
    """Every epoch's val scoring sees the live weights: a stopped head must never move again, it must
    stop at the first epoch where the D28 rule (ref + 1e-4, patience 20) says so, and the selected
    snapshot must be the weights of its best epoch."""
    import eegdrift.probe_grid as pg

    g = torch.Generator().manual_seed(0)
    feats = {}
    for split, m in (("train", 300), ("val", 100), ("test", 100)):
        y = torch.tensor([0, 1] * (m // 2))
        feats[split] = ((torch.randn(m, 4, generator=g) * 1.5 + y[:, None]).half(), y)   # noisy: mixed stops
    seen, score = [], pg._score

    def spy(x, params, view, move):
        seen.append({v: (w.detach().clone(), b.detach().clone()) for v, (w, b) in params.items()})
        return score(x, params, view, move)

    monkeypatch.setattr(pg, "_score", spy)
    out = _fit(feats, max_epochs=200)
    for v in ("grid", "grid_z"):
        cfgs = out[v][0]["configs"]
        assert len({c["epochs_run"] for c in cfgs}) > 1   # some heads stop while others train on
        for k, c in enumerate(cfgs):
            e, last = c["epochs_run"], max(x["epochs_run"] for x in cfgs)
            assert all(torch.equal(seen[t][v][i][k], seen[e - 1][v][i][k]) for t in range(e, last) for i in (0, 1))
            ref, wait, stop = -np.inf, 0, None
            for i, r in enumerate(c["val_curve"]):
                ref, wait = (r, 0) if r > ref + 1e-4 else (ref, wait + 1)
                if wait >= 20:
                    stop = i
                    break
            assert (stop is None and e == 200) or stop == e - 1
            assert torch.equal(seen[last][v][0][k], seen[c["best_epoch"]][v][0][k])   # snapshot = best epoch


def test_collect_results_reads_grid_records(tmp_path, monkeypatch):
    import collect_results as cr

    (tmp_path / "results").mkdir()
    rec = {"key": "k", "model": "biot", "dataset": "chbmit", "arm": "lp", "seed": 1, "split": "paper",
           "run_tag": "P1G",
           "probes": {"grid": {"type": "GridProbeResult", "test_at_best": {"roc_auc": 0.7, "bal_acc": 0.6}}}}
    (tmp_path / "results" / "k.json").write_text(json.dumps(rec))
    (tmp_path / "results" / "val-index-chbmit-paper-h.json").write_text("[]")
    monkeypatch.setattr(cr, "ROOT", tmp_path)
    monkeypatch.setattr("sys.argv", ["x", "--dataset", "chbmit", "--local", str(tmp_path), "--run-tag", "P1G"])
    assert cr.main() == 0
    row = json.loads((tmp_path / "artifacts" / "tables" / "chbmit-paper-P1G.json").read_text())[0]
    assert row["test_at_best.roc_auc"][0] == 70.0 and "test_last.roc_auc" not in row


def test_deterministic_and_variants_independent():
    feats = _feats()
    a, b, other = _fit(feats), _fit(feats), _fit(feats, seed=2)
    alone = _fit(feats, ("grid",))
    for v in ("grid", "grid_z"):
        assert _strip(a[v][0]) == _strip(b[v][0])
        assert all(np.array_equal(a[v][1][k], b[v][1][k]) for k in a[v][1])
        assert _strip(other[v][0])["configs"] != _strip(a[v][0])["configs"]
    assert _strip(alone["grid"][0]) == _strip(a["grid"][0])   # one shared pass changes no head


def test_standardization_uses_train_statistics_only():
    feats = _feats()
    x = feats["train"][0].double()

    def move(t, idx):
        return t[idx].float()

    mean, std = train_stats(feats["train"][0], move)
    assert torch.allclose(mean.double(), x.mean(0), atol=1e-4)
    assert torch.allclose(std.double(), x.std(0, unbiased=False), atol=1e-4)
    shifted = {**feats, **{s: ((feats[s][0].float() * 10 - 7).half(), feats[s][1]) for s in ("val", "test")}}
    a, b = _fit(feats, max_epochs=5), _fit(shifted, max_epochs=5)
    for ca, cb in zip(a["grid_z"][0]["configs"], b["grid_z"][0]["configs"], strict=True):
        assert ca["train_loss"] == cb["train_loss"]   # train-side z is blind to val/test


def test_existing_probes_unchanged_and_grid_runs_on_models(registry, root, tmp_path):
    from eegdrift.arms import resolve
    from eegdrift.data.store import LocalStore
    from eegdrift.models.protocols import scale_input
    from eegdrift.probe import DEFAULT_VARIANTS, PROBE_CODE_VERSION, ProbeSpec, parity_probe
    from eegdrift.probe_grid import cache_features
    from eegdrift.study import Context, EvalData, SSLData, adapt_spec, probe_template, result_key

    assert DEFAULT_VARIANTS == ("mlp_fullft", "linear", "linear_z") and PROBE_CODE_VERSION == 4
    # result keys of existing variant lists, pinned before the grid code existed
    ctx = Context(root=root, data_root=tmp_path, out=tmp_path, artifacts=LocalStore(tmp_path),
                  device=CPU, log=_quiet)
    arm = resolve("last", ctx.adapt_cfg, ctx.registry, "biot")
    spec = adapt_spec(ctx, "biot", "chbmit", arm, 42, SSLData(torch.zeros(4174, 1), [], "h", 81993, "paper"))
    tpl, ev = probe_template(ctx, "biot", "chbmit", 42, "paper"), EvalData({}, "e1", [], "paper")
    assert result_key(spec, arm, tpl, ("linear",), ev) == "biot-chbmit-last-s42-paper-e4c0d7c1779cc56c"
    assert result_key(spec, arm, tpl, ("mlp_fullft", "linear", "linear_z"), ev, "S1M") == \
        "biot-chbmit-last-s42-paper-e0db8e68e35795bb"
    assert result_key(spec, arm, tpl, ("grid", "grid_z"), ev) != result_key(spec, arm, tpl, ("linear",), ev)

    # an existing probe gives bit-identical results before and after a grid probe on the same model
    m = registry.build("biot", "pretrained")
    g = torch.Generator().manual_seed(0)
    data = {k: (torch.randn(n, 16, 10, 200, generator=g) * 30, torch.tensor([0, 1] * (n // 2)))
            for k, n in (("train", 16), ("val", 8), ("test", 8))}
    pspec = ProbeSpec(model="biot", dataset="chbmit", variant="linear", seed=1, n_classes=2, window_s=10,
                      epochs=2, batch=8, backbone_mode="eval")
    before, arr_before = parity_probe(m, pspec, data, CPU, log=_quiet)
    out = grid_probe(m, replace(pspec, variant="*"), data, CPU, log=_quiet, max_epochs=2)
    after, arr_after = parity_probe(m, pspec, data, CPU, log=_quiet)
    assert _strip(before.to_record()) == _strip(after.to_record())
    assert all(np.array_equal(arr_before[k], arr_after[k]) for k in arr_before)
    rec = out["grid_z"][0]
    assert rec["spec"]["variant"] == "grid_z" and rec["head_params"] == 257 and len(rec["configs"]) == 16
    assert set(out["grid"][1]) == {"y_test", "scores_best", "y_val", "scores_val_best"}
    with pytest.raises(ValueError):
        grid_probe(m, replace(pspec, backbone_mode="train"), data, CPU, log=_quiet)

    # the cache is exactly the parity probe's eval-mode feature path, in float16
    feats = cache_features(m, pspec, data, CPU)
    m.encoder().eval()
    with torch.no_grad():
        ref = m.features(m.prepare(scale_input(data["val"][0], pspec.scale, pspec.input_norm)))
    assert torch.equal(feats["val"][0], ref.half()) and feats["val"][0].dtype == torch.float16
    cb = registry.build("cbramod", "pretrained")
    small = {k: (v[0][:2], v[1][:2]) for k, v in data.items()}
    assert cache_features(cb, replace(pspec, model="cbramod"), small, CPU)["train"][0].shape == (2, 32000)


@pytest.mark.skipif(not PILOT.exists(), reason="needs the pilot stores in data/lmdb")
def test_study_runs_grid_variants_from_one_cache(root, tmp_path):
    from eegdrift.data.store import LocalStore
    from eegdrift.study import Context, load_eval, load_ssl, run_arm_seed

    ctx = Context(root=root, data_root=root / "data" / "lmdb", out=tmp_path, artifacts=LocalStore(tmp_path / "a"),
                  device=CPU, smoke=True, log=_quiet,
                  overrides={"probes": "grid_z,linear,grid", "backbone_mode": "eval", "labels": "overlap"})
    rec = run_arm_seed(ctx, "biot", "chbmit", "lp", 42, load_ssl(ctx, "chbmit", "rot0"),
                       load_eval(ctx, "chbmit", "rot0"))
    assert list(rec["probes"]) == ["grid_z", "linear", "grid"]
    assert rec["probes"]["grid"]["cache_seconds"] == rec["probes"]["grid_z"]["cache_seconds"]   # one cache
    assert rec["probes"]["linear"]["type"] == "ParityProbeResult"
    assert all((tmp_path / "results" / f"{rec['key']}.{v}.npz").exists() for v in rec["probes"])
    ctx.overrides["probes"] = "grid,nope"
    with pytest.raises(ValueError):
        run_arm_seed(ctx, "biot", "chbmit", "lp", 42, load_ssl(ctx, "chbmit", "rot0"),
                     load_eval(ctx, "chbmit", "rot0"))
