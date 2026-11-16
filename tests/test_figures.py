"""Smoke test: scripts/figures.py on a tiny synthetic record set writes every figure it can."""

import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from figures import effects_intervals, main

MODELS, ARMS = ("biot", "cbramod"), ("lp", "last", "last_randinit", "lp_randinit")


def write(root, tag, model, arm, split, seed, logged=False, heads=("linear",)):
    d = root / f"{model}-{tag or 'w1'}-{split}" / "results"
    d.mkdir(parents=True, exist_ok=True)
    key = f"{model}-chbmit-{arm}-s{seed}-{split}-{tag or 'w1'}"
    rng = np.random.default_rng(seed)
    y = (rng.random(300) < 0.1).astype(np.int8)
    m = {"bal_acc": 0.6, "roc_auc": 0.6 + 0.05 * ARMS.index(arm), "pr_auc_trapz": 0.3, "avg_precision": 0.3}
    probes = {}
    for h in heads:
        p = {"spec": {"backbone_mode": "eval"}, "best_epoch": seed % 10, "test_at_best": m,
             "val_curve": list(np.linspace(0.7, 0.8, 10))}
        if logged:
            p["history"] = [{"epoch": e, "train_loss": 0.7 - 0.02 * e, "val": m, "val_loss": 0.5,
                             "test_plot_only": m} for e in range(10)]
        probes[h] = p
        np.savez(d / f"{key}.{h}.npz", y_test=y, scores_best=(y + rng.normal(0, 1, 300)).astype(np.float32))
    rec = {"key": key, "model": model, "dataset": "chbmit", "arm": arm, "seed": seed, "split": split,
           "run_tag": tag, "eval_hash": "e", "labels": "overlap", "versions": {"adapt": 3, "probe": 4},
           "probes": probes}
    if arm in ("last", "last_randinit"):
        rec["adapt_spec"] = {"n_windows": 1000, "batch": 250}
        rec["adapt"] = {"epoch_losses": [0.9, 0.6, 0.5], "best_epoch": 2}
        if logged:
            rec["adapt"]["step_losses"] = list(np.linspace(1.0, 0.5, 12))
    (d / f"{key}.json").write_text(json.dumps(rec))


def test_figures_smoke(tmp_path):
    res = tmp_path / "results"
    for model in MODELS:
        for arm in ARMS:
            for seed in (42, 123):
                write(res, "P1E", model, arm, "paper", seed, heads=("linear", "mlp_fullft"))
                write(res, "P1L", model, arm, "paper", seed, logged=True)
                if arm != "lp_randinit":
                    write(res, "", model, arm, "paper", seed)
            for r in range(5):
                write(res, "S1M", model, arm, f"rot{r}", 42)
        for arm in ("last", "last_randinit"):
            for tag in ("C2-N896", "C2-N4174", "C2E-N896", "C2E-N4174", "C3-P3N2048", "C3E-P11N2048"):
                write(res, tag, model, arm, "paper", 42)
        write(res, "R3-b128", model, "lp", "paper", 42)
        write(res, "R3E-b128", model, "lp", "paper", 42)
    tables = tmp_path / "tables"
    tables.mkdir()
    (tables / "d24-bootstrap.md").write_text(
        "| dataset (tags) | model | head | contrast | mean | 95% CI |\n|---|---|---|---|---|---|\n"
        "| chbmit (P1E) | biot | linear | last - lp | -0.6 | [-2.6, +1.4] |\n"
        "| chbmit (P1E) | cbramod | mlp_fullft | lp - lp_randinit | +2.2 | [+1.2, +3.1] |\n")
    out = tmp_path / "figures"
    args = ["--results", str(res), "--out", str(out), "--tables", str(tables),
            "--store", str(tmp_path / "no-store"), "--analysis", str(tmp_path / "no-analysis"), "--dpi", "30"]
    assert main(args) == 0
    stems = ("f1_ssl_loss_epoch", "f1_ssl_loss_step", "f2_probe_curves_paper", "f2_probe_curves_chbmit_rot",
             "f3_table1_cells", "f4_d24_paired", "f5_roc_pr", "f6_chbmit_protocol_timeline", "f8_c2_c3",
             "f9_d24_forest")
    for stem in stems:
        assert (out / f"{stem}.png").stat().st_size > 0 and (out / f"{stem}.pdf").stat().st_size > 0
    captions = (out / "captions.md").read_text()
    assert all(f"`{s}`" in captions for s in stems)
    assert "- F7: skipped" in captions and "- F2 siena: skipped" in captions
    assert "\u2014" not in captions
    assert all(f"- {fid}: skipped" in captions for fid in ("F10", "F11", "F12"))
    assert main([*args, "--only", "F9"]) == 0   # --only keeps the captions of the other figures
    assert all(f"`{s}`" in (out / "captions.md").read_text() for s in stems)


def test_primary_effect_intervals_preserve_rotation_correction(tmp_path):
    """The ordinary Siena interval excludes zero; the primary corrected interval does not."""
    source = Path(__file__).parent / "fixtures" / "figure_intervals_d31.json"
    target = tmp_path / "D31" / "d31.json"
    target.parent.mkdir()
    target.write_bytes(source.read_bytes())
    data = effects_intervals(SimpleNamespace(analysis=tmp_path))
    corrected = data[("S3G", "biot", "raw", True)][("last", "lp")]
    fixed_recipe = data[("S3G", "biot", "raw", False)][("last", "lp")]
    seed_interval = data[("P1G", "biot", "raw", True)][("last", "lp")]
    assert corrected == pytest.approx((1.698963173062663, -0.9754950861593537, 4.373421432284679))
    assert fixed_recipe == pytest.approx((9.232413872446674, -2.2726999719686862, 20.737527716862033))
    assert seed_interval == pytest.approx((0.8615351956962798, -1.6817215748885619, 3.4047919662811212))
    saved = json.loads(source.read_text())
    assert saved["contrasts"]["S3W|biot|grid"]["contrasts"]["last - lp"]["t"]["ci95"][0] > 0
    assert corrected[1] < 0 < corrected[2]


def test_effect_figure_refuses_inconsistent_saved_interval(tmp_path):
    source = Path(__file__).parent / "fixtures" / "figure_intervals_d31.json"
    data = json.loads(source.read_text())
    data["contrasts"]["S3W|biot|grid"]["contrasts"]["last - lp"]["nb"]["ci95"][0] = 0.1
    target = tmp_path / "D31" / "d31.json"
    target.parent.mkdir()
    target.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="plotted interval differs"):
        effects_intervals(SimpleNamespace(analysis=tmp_path))
