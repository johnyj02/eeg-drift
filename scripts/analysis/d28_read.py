#!/usr/bin/env python3
"""D28 probe convergence: equally tuned, early-stopped linear probes on cached frozen features, read with the
protocol frozen in notes/decisions.md "## D28" (commit c0283f4, before any D28 run).

    .venv/bin/python scripts/analysis/d28_read.py

Run tags: P1G (DL's split, upstream labels, seeds 42/123/2021/3407/8888; lp, last, last_randinit, lp_randinit;
both models), P1QG (BIOT, input_norm q95, same split and seeds; lp, last, last_noise), S1G / S3G / S3FG
(CHB-MIT / Siena / Siena filtered, rotations rot0-4, overlap labels, seeds [S_r, 1000+r, 2000+r]; lp, last,
last_randinit, lp_randinit, last_noise; both models). Probe variants grid (raw features) and grid_z
(train-standardized), src/eegdrift/probe_grid.py.

Registered reading (D28), per setting x model x variant x contrast (last - lp, last_randinit - last,
lp - lp_randinit, last - last_noise): mean paired difference (ROC-AUC x100 at the selected configuration and
epoch), 95% t-interval over the 5 units (rotation means over the 3 seeds, df 4; on DL's split the 5 seeds,
i.e. seed uncertainty on one fixed split) and the Nadeau-Bengio corrected interval (rotations); label
"gain demonstrated" if the 95% t-interval excludes 0 and |mean| > 3 in that direction, "equivalent within +-3"
if TOST (margin 3, alpha 0.05) rejects, else "not resolved"; the D18 paired rule as a descriptive consistency
criterion. Q1-Q3 as in D28.

Reading choices (fixed after reading 3 raw records, before any D28 aggregate was computed):
- The label uses the t-interval and a TOST with the t standard error (as the D27-E TOST). The same label
  computed with the Nadeau-Bengio standard error is reported as a descriptive sensitivity. No NB interval on
  DL's split: its 5 seeds share one train/test split (there is no resampling to correct for).
- NB ratio n_test / n_train: stats_d25.nb_ratio on the D24-A unit directories (the D28 eval sets are asserted
  equal to the D24-A ones by eval_hash and test index).
- Q3 "direction": the sign of the mean difference, D28 grid against the fixed-recipe raw head (D24-A rotations,
  D24-B = P1E on DL's split), D28 grid_z against the fixed-recipe standardized head (D27-B; P1Z).
- Convergence fraction: the selected configuration's flag (record "converged"); the fraction over all 16
  configurations is also given. Epochs are 1-based (record best_epoch + 1). Grid edge: lr in {1e-4, 3e-3} or
  weight decay in {0, 1e-1} (12 of the 16 configurations touch an edge).
- Fixed-recipe references for the absolute ROC (same model, arm, split and seed): linear = S1E+S1M / S3E+S3M /
  S3FE+S3FM (last_noise: S1N, S3N, S3FN), P1E, P1QN; linear_z = S1Z / S3Z / S3FZ (last_noise: S3NM, S3FNM; none
  on CHB-MIT rotations), P1Z, P1QN.
Added AFTER the first aggregate output (descriptive only, no label or answer depends on them): the list of
single-seed differences beyond +-25 with each arm's selection, the "selected epoch <= 2" count, and the
per-model grouping of the Q3 text (the Q3 comparison itself is unchanged: sign of the mean).
Every expected record is checked first (counts, duplicates, smoke, versions, eval mode, encoder tap, labels,
input scaling, grid fields = the frozen protocol, selection/early-stopping consistency, eval_hash / test index /
adaptation / SSL-loss pairing with the fixed-recipe records). The fixed-recipe contrasts are re-derived and
asserted equal to the published D24-A, D27-B (artifacts/analysis/D27B/d27b.json), E27, A1 and A6 values.
Writes artifacts/analysis/D28/README.md, d28.json, artifacts/figures/f_d28_curves.{pdf,png},
artifacts/figures/fig_effects_d28.{pdf,png}.
"""

from __future__ import annotations

import itertools
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "analysis"))
from read_d24 import ROTS, load  # noqa: E402
from read_step1 import paired  # noqa: E402
from stats_d25 import C_NB, C_T, GRID, INK, INK2, nb_ratio, tost_p  # noqa: E402

LOCAL = ROOT / "artifacts" / "s3-results"
OUT = ROOT / "artifacts" / "analysis" / "D28"
FIG = ROOT / "artifacts" / "figures"
SR = (42, 123, 2021, 3407, 8888)
SEEDS3 = {r: (SR[i], 1000 + i, 2000 + i) for i, r in enumerate(ROTS)}
MODELS = ("biot", "cbramod")
NAME = {"biot": "BIOT", "cbramod": "CBraMod"}
A4 = ("lp", "last", "last_randinit", "lp_randinit")
A5 = A4 + ("last_noise",)
VARIANTS = ("grid", "grid_z")
FIXED = {"grid": "linear", "grid_z": "linear_z"}
CONTRASTS = (("last", "lp"), ("last_randinit", "last"), ("lp", "lp_randinit"), ("last", "last_noise"))
# frozen D28 search (decisions.md "## D28"), compared with every record's "grid" field
LRS, WDS = (1e-4, 3e-4, 1e-3, 3e-3), (0.0, 1e-4, 1e-2, 1e-1)
FROZEN = {
    "lr": list(LRS),
    "weight_decay": list(WDS),
    "batch": 256,
    "max_epochs": 200,
    "patience": 20,
    "min_delta": 1e-4,
    "schedule": "constant",
    "loss": "BCE on logits",
    "betas": [0.9, 0.999],
    "features": "float16",
    "version": 1,
}
# frozen D31 search (decisions.md "## D31"): the same coverage with a wider grid, a longer cap and
# GRID_CODE_VERSION 2. The 30 configurations contain all 16 of D28's, so the earlier optimum stays reachable.
LRS31, WDS31 = (3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2), (0.0, 1e-4, 1e-2, 1e-1, 1.0)
FROZEN31 = {**FROZEN, "lr": list(LRS31), "weight_decay": list(WDS31), "max_epochs": 500, "version": 2}
D31_TAG = {"P1G": "P1W", "P1QG": "P1QW", "S1G": "S1W", "S3G": "S3W", "S3FG": "S3FW"}
# TAG resolves a D28 tag literal to the active search's tag. use_d31() swaps it for D31_TAG, so code
# that names a setting by its D28 tag keeps working under --d31 instead of raising a KeyError.
TAG = {k: k for k in D31_TAG}
# Output names, so a --d31 run cannot overwrite the D28 outputs the paper and the supplement ship.
JSON_NAME, CURVES_FIG, EFFECTS_FIG = "d28.json", "f_d28_curves.pdf", "fig_effects_d28.pdf"
PROTOCOL = "D28"   # the decision-log entry whose search this run reads; use_d31() swaps it


def sci(x: float) -> str:
    """1e-4, 3e-3, 0, 1: the notation the frozen protocols are written in.

    Not "%g", which renders 1e-4 as 0.0001 and would silently rewrite the published D28 report.
    """
    if x == 0:
        return "0"
    if x == int(x):
        return str(int(x))
    m, e = f"{x:.0e}".split("e")
    return f"{m}e{int(e)}"
HEAD_PARAMS = {"biot": 257, "cbramod": 32001}
# tag, setting, dataset, labels, input_norm, models, arms, stats_d25.nb_ratio key, (linear tags, linear_z tags)
SETS = (
    ("P1G", "DL's split", "chbmit", "upstream", "", MODELS, A4, None, ("P1E", "P1Z")),
    (
        "P1QG",
        "DL's split, BIOT q95 input",
        "chbmit",
        "upstream",
        "q95",
        ("biot",),
        ("lp", "last", "last_noise"),
        None,
        ("P1QN", "P1QN"),
    ),
    ("S1G", "CHB-MIT rotations", "chbmit", "overlap", "", MODELS, A5, "S1E,S1M", ("S1E,S1M,S1N", "S1Z")),
    ("S3G", "Siena rotations", "siena", "overlap", "", MODELS, A5, "S3E,S3M", ("S3E,S3M,S3N", "S3Z,S3NM")),
    (
        "S3FG",
        "Siena filtered rotations",
        "siena",
        "overlap",
        "",
        MODELS,
        A5,
        "S3FE,S3FM",
        ("S3FE,S3FM,S3FN", "S3FZ,S3FNM"),
    ),
)
D27B_SET = {"P1G": "CHB-MIT paper split", "S1G": "CHB-MIT", "S3G": "Siena", "S3FG": "Siena filtered"}
# published last - last_noise means (artifacts/analysis/D27/noise.md: E27 linear, A6 linear_z, A1 both heads)
NOISE_PUB = {
    ("S1G", "biot", "linear"): 0.81,
    ("S3G", "biot", "linear"): 1.58,
    ("S3G", "cbramod", "linear"): -0.07,
    ("S3FG", "biot", "linear"): 1.26,
    ("S3FG", "cbramod", "linear"): -0.02,
    ("S3G", "biot", "linear_z"): 0.40,
    ("S3FG", "biot", "linear_z"): 1.13,
    ("P1QG", "biot", "linear"): 8.58,
    ("P1QG", "biot", "linear_z"): 0.46,
}
GAIN, EQUIV, UNRES = "gain demonstrated", "equivalent within +-3", "not resolved"
DEFAULTS = {"tap": "encoder", "input_norm": ""}  # fields older records do not store (their code's values)
ARM_C = {
    "lp": "#2a78d6",
    "last": "#eb6834",
    "last_randinit": "#1baf7a",
    "lp_randinit": "#eda100",
    "last_noise": "#e87ba4",
}  # dataviz reference categorical slots 1-5, fixed order
SURF = "#fcfcfb"


def cname(a: str, b: str) -> str:
    return f"{a} - {b}"


# ---------- statistics ----------


def label(m: float, ci, p: float) -> str:
    if (ci[0] > 0 and m > 3) or (ci[1] < 0 and m < -3):
        return GAIN
    return EQUIV if p < 0.05 else UNRES


def summarise(u, ratio: float | None) -> dict:
    u = np.asarray(u, dtype=float)
    n, m, sd = len(u), float(u.mean()), float(u.std(ddof=1))
    T = stats.t(n - 1)
    out = {
        "per_unit": u.tolist(),
        "mean": m,
        "sd": sd,
        "d18": paired(u),
        "same_sign": int(max((u > 0).sum(), (u < 0).sum())),
    }
    for key, se in (("t", sd / np.sqrt(n)), ("nb", None if ratio is None else sd * np.sqrt(1 / n + ratio))):
        if se is None:
            out[key] = None
            continue
        ci = [m - T.ppf(0.975) * se, m + T.ppf(0.975) * se]
        p = tost_p(m, se, 3, T)
        out[key] = {
            "se": float(se),
            "ci95": ci,
            "ci90": [m - T.ppf(0.95) * se, m + T.ppf(0.95) * se],
            "tost_p": p,
            "label": label(m, ci, p),
        }
    out["label"] = out["t"]["label"]
    return out


def stop_len(curve) -> int:
    """Replay of probe_grid's early stop on a logged val curve: epochs a head runs (max: len(curve))."""
    ref, wait = -np.inf, 0
    for i, x in enumerate(curve):
        if x > ref + FROZEN["min_delta"]:
            ref, wait = x, 0
        else:
            wait += 1
        if wait >= FROZEN["patience"]:
            return i + 1
    return len(curve)


def selfcheck() -> None:
    assert label(4.0, [1.0, 7.0], 0.9) == GAIN and label(-4.0, [-7.0, -1.0], 0.9) == GAIN
    assert label(2.9, [0.5, 5.3], 0.6) == UNRES and label(4.0, [-1.0, 9.0], 0.9) == UNRES
    assert label(0.1, [-0.5, 0.7], 1e-4) == EQUIV
    s = summarise([1.0, 1.2, 0.8, 1.1, 0.9], None)
    assert s["label"] == EQUIV and s["nb"] is None and s["d18"] == "no difference shown"
    assert summarise([5, 6, 7, 5, 6], 0.25)["label"] == GAIN
    flat = [0.5] + [0.5] * 30
    assert stop_len(flat) == 21 and stop_len([0.1 * i for i in range(8)]) == 8


# ---------- records ----------


def scan() -> list[dict]:
    tags = {s[0] for s in SETS} | {t for s in SETS for g in s[8] for t in g.split(",")}
    out = []
    for p in LOCAL.rglob("results/*.json"):
        if p.name.startswith(("diag-", "test-index-", "val-index-", "report-")):
            continue
        r = json.loads(p.read_text())
        if r.get("run_tag") in tags:
            out.append(r)
    return out


def cell(r: dict) -> tuple:
    return r["model"], r["arm"], r["split"], r["seed"]


def diff(new: dict, old: dict) -> set[str]:
    return {k for k in set(new) | set(old) if new.get(k, DEFAULTS.get(k)) != old.get(k, DEFAULTS.get(k))}


def want_cells(s) -> set[tuple]:
    tag, *_, models, arms, _nb, _ref = s
    if tag.startswith("P1"):
        return {(m, a, "paper", sd) for m in models for a in arms for sd in SR}
    return {(m, a, r, sd) for m in models for a in arms for r in ROTS for sd in SEEDS3[r]}


def check_fit(p: dict, v: str, r: dict, norm: str, acc: Counter) -> None:
    g = p["grid"]
    assert p["type"] == "GridProbeResult" and g["standardized"] == (v == "grid_z"), (r["key"], v)
    assert {k: g[k] for k in FROZEN} == FROZEN, (r["key"], v, g)
    spec = p["spec"]
    assert (
        spec["backbone_mode"],
        spec["tap"],
        spec["variant"],
        spec["seed"],
        spec["split"],
        spec["input_norm"],
        spec["n_classes"],
    ) == ("eval", "encoder", v, r["seed"], r["split"], norm, 2), (r["key"], v)
    assert p["head_params"] == HEAD_PARAMS[r["model"]], (r["key"], p["head_params"])
    cf = p["configs"]
    assert [(c["lr"], c["weight_decay"]) for c in cf] == list(itertools.product(LRS, WDS)), r["key"]
    for c in cf:
        cv, n = c["val_curve"], c["epochs_run"]
        assert len(cv) == len(c["train_loss"]) == n and 1 <= n <= FROZEN["max_epochs"], (r["key"], v)
        assert c["converged"] == (n < FROZEN["max_epochs"]), (r["key"], v)
        assert abs(max(cv) - c["best_val"]) <= 5.1e-7 and abs(cv[c["best_epoch"]] - c["best_val"]) <= 5.1e-7
        acc["configs"] += 1
        acc["replay_mismatch"] += stop_len(cv) != n
        acc["nonfinite_loss"] += not all(np.isfinite(c["train_loss"]))
    k = int(np.argmax([c["best_val"] for c in cf]))  # first max: smaller lr, then smaller wd (D28 tie rule)
    assert p["selected"] == {"index": k, "lr": cf[k]["lr"], "weight_decay": cf[k]["weight_decay"]}, r["key"]
    assert (p["best_val"], p["best_epoch"], p["converged"]) == (
        cf[k]["best_val"],
        cf[k]["best_epoch"],
        cf[k]["converged"],
    ), r["key"]
    assert p["epochs_run"] == max(c["epochs_run"] for c in cf), r["key"]
    acc["ties"] += sum(c["best_val"] == cf[k]["best_val"] for c in cf) > 1
    gap = abs(p["val_at_best"]["roc_auc"] - p["best_val"])
    acc["val_rescore_max_gap_e9"] = max(acc["val_rescore_max_gap_e9"], int(np.ceil(gap * 1e9)))
    assert gap < 1e-6, (r["key"], v, gap)


def verify(s, recs: list[dict], refs: dict) -> tuple[list[dict], list[str], dict]:
    tag, setting, ds, labels, norm, models, arms, _nb, (lt, zt) = s
    mine = [r for r in recs if r["run_tag"] == tag]
    cnt = Counter(cell(r) for r in mine)
    want = want_cells(s)
    assert set(cnt) == want, f"{tag}: missing {sorted(want - set(cnt))[:5]}, extra {sorted(set(cnt) - want)[:5]}"
    assert max(cnt.values()) == 1, f"{tag}: duplicates {[k for k, v in cnt.items() if v > 1]}"
    assert len({r["key"] for r in mine}) == len(mine), f"{tag}: duplicate keys"
    acc: Counter = Counter()
    pairs: Counter = Counter()
    for r in mine:
        k = cell(r)
        assert r["dataset"] == ds and not r.get("smoke") and r["labels"] == labels, (tag, k)
        assert r["versions"] == {"adapt": 3, "probe": 4} and set(r["probes"]) == set(VARIANTS), (tag, k)
        o = r["overrides"]
        assert (
            o.get("probes"),
            o.get("backbone_mode"),
            o.get("input_norm", ""),
            o.get("fold_seed"),
            o.get("protocol"),
            o.get("run_tag"),
        ) == ("grid,grid_z", "eval", norm, None, None, tag), (tag, k, o)
        assert set(o) - {"probes", "backbone_mode", "input_norm", "labels", "run_tag"} == set(), (tag, k, o)
        a = r["adapt_spec"]
        assert a["init"] == ("random" if r["arm"].endswith("randinit") else "pretrained"), (tag, k)
        assert a["input_norm"] == norm and a["protocol"] == "parity", (tag, k)
        assert r["arm_spec"]["ssl_input"] == ("noise" if r["arm"] == "last_noise" else "eeg"), (tag, k)
        assert ("adapt" in r) == r["arm_spec"]["adapt"] == (r["arm"] not in ("lp", "lp_randinit")), (tag, k)
        tn = {(p["test_at_best"]["n"], p["test_at_best"]["prevalence"]) for p in r["probes"].values()}
        assert len(tn) == 1, (tag, k)
        for v in VARIANTS:
            check_fit(r["probes"][v], v, r, norm, acc)
        for head, group in (("linear", lt), ("linear_z", zt)):
            ref = [refs[(t, *k)] for t in group.split(",") if (t, *k) in refs and head in refs[(t, *k)]["probes"]]
            assert len(ref) <= 1, (tag, k, head)
            if not ref:
                pairs[f"{head} missing"] += 1
                continue
            q = ref[0]
            assert (q["eval_hash"], q["test_index"], q["labels"]) == (r["eval_hash"], r["test_index"], labels), k
            assert q.get("val_index", r["val_index"]) == r["val_index"], (tag, k)
            assert not diff(a, q["adapt_spec"]) and not diff(r["arm_spec"], q["arm_spec"]), (tag, k, head)
            qs = q["probes"][head]["spec"]
            assert (qs["backbone_mode"], qs.get("tap", "encoder"), qs.get("input_norm", "")) == (
                "eval",
                "encoder",
                norm,
            )
            t = q["probes"][head]["test_at_best"]
            assert {(t["n"], t["prevalence"])} == tn, (tag, k, head)
            if "adapt" in r:
                what = "step_losses" if "step_losses" in q["adapt"] else "epoch_losses"
                assert r["adapt"][what] == q["adapt"][what], (tag, k, head, "SSL losses differ")
                pairs[f"{head} SSL {what.split('_')[0]} losses identical"] += 1
            pairs[f"{head} paired"] += 1
    hashes = defaultdict(set)
    for r in mine:
        hashes[r["split"]].add((r["eval_hash"], r["test_index"]))
    assert all(len(h) == 1 for h in hashes.values()), (tag, hashes)
    lines = [
        f"- {tag} ({setting}): {len(mine)} records = {len(models)} model(s) x {len(arms)} arms x "
        + ("5 seeds" if tag.startswith("P1") else "5 rotations x 3 seeds")
        + f"; 1 per cell, 0 missing, 0 duplicates, 0 smoke; versions adapt 3 / probe 4 / grid 1; probes "
        f'grid + grid_z; backbone eval, tap encoder, input_norm "{norm}", labels {labels}; '
        f"one eval set per split (both models)",
        f"  {acc['configs']} configuration fits checked: grid fields = the frozen {PROTOCOL} search; selected "
        f"configuration = first argmax of best val (ties among configurations: {acc['ties']} fits); "
        f"best_val = max of the logged curve; converged = stopped before epoch {FROZEN['max_epochs']}; "
        f"early-stop replay on the "
        f"logged (6-decimal) curves disagrees in {acc['replay_mismatch']} fits; non-finite train loss in "
        f"{acc['nonfinite_loss']}; val ROC re-scored at the selection = best_val within "
        f"{acc['val_rescore_max_gap_e9']}e-9",
        "  pairing with the fixed-recipe records of the same (model, arm, split, seed): "
        + "; ".join(f"{k}: {v}" for k, v in sorted(pairs.items()))
        + " (paired = same eval_hash, test index, val index, test n/prevalence, adapt_spec, arm_spec)",
    ]
    return mine, lines, dict(acc) | {"pairs": dict(pairs)}


# ---------- reading ----------


def units(roc: dict, model: str, arm: str, probe: str, paper: bool) -> list[float] | None:
    if paper:
        c = roc.get((model, arm, "paper", probe), {})
        return [c[s] for s in SR] if set(SR) <= set(c) else None
    cells = [roc.get((model, arm, r, probe), {}) for r in ROTS]
    if not all(set(SEEDS3[r]) <= set(c) for c, r in zip(cells, ROTS, strict=True)):
        return None
    return [float(np.mean([c[s] for s in SEEDS3[r]])) for c, r in zip(cells, ROTS, strict=True)]


def per_seed(roc, model, a, b, probe, paper) -> list:
    if paper:
        return [roc[(model, a, "paper", probe)][s] - roc[(model, b, "paper", probe)][s] for s in SR]
    return [[roc[(model, a, r, probe)][s] - roc[(model, b, r, probe)][s] for s in SEEDS3[r]] for r in ROTS]


def read_set(s, roc: dict, ref: dict, ratio: float | None) -> dict:
    tag, _setting, _ds, _lab, _norm, models, arms, _nb, _tags = s
    paper = tag.startswith("P1")
    out: dict = {}
    for m in models:
        for v in VARIANTS:
            fx = FIXED[v]
            arm_rows = {}
            for a in arms:
                u = units(roc, m, a, v, paper)
                assert u is not None, (tag, m, a, v)
                f = units(ref[fx], m, a, fx, paper)
                row = {"per_unit": u, "mean": float(np.mean(u)), "sem": float(np.std(u, ddof=1) / np.sqrt(5))}
                if f is not None:
                    d = np.subtract(u, f)
                    row.update(
                        fixed=f,
                        fixed_mean=float(np.mean(f)),
                        tuned_minus_fixed=d.tolist(),
                        tuned_minus_fixed_mean=float(d.mean()),
                    )
                arm_rows[a] = row
            con = {}
            for a, b in CONTRASTS:
                if a not in arms or b not in arms:
                    continue
                x = summarise(np.subtract(arm_rows[a]["per_unit"], arm_rows[b]["per_unit"]), ratio)
                x["per_seed"] = per_seed(roc, m, a, b, v, paper)
                fa, fb = units(ref[fx], m, a, fx, paper), units(ref[fx], m, b, fx, paper)
                if fa is not None and fb is not None:
                    x["fixed"] = summarise(np.subtract(fa, fb), ratio)
                con[cname(a, b)] = x
            out[(m, v)] = {"arms": arm_rows, "contrasts": con}
    return out


def check_published(res: dict) -> list[str]:
    """Fixed-recipe contrasts re-derived here = the published D24-A / D27-B / E27 / A1 / A6 values."""
    d27b = json.loads((ROOT / "artifacts" / "analysis" / "D27B" / "d27b.json").read_text())["sets"]
    n_b = n_n = 0
    for (tag, m, v), x in res.items():
        for name, c in x["contrasts"].items():
            if "fixed" not in c:
                continue
            if tag in D27B_SET and name != "last - last_noise":
                pub = d27b[D27B_SET[tag]]["models"][m]["raw" if v == "grid" else "z"]["contrasts"][name][
                    "per_unit"
                ]
                assert np.allclose(c["fixed"]["per_unit"], pub, atol=1e-9), (tag, m, v, name)
                n_b += 1
            if name == "last - last_noise":
                assert round(c["fixed"]["mean"], 2) == NOISE_PUB[(tag, m, FIXED[v])], (
                    tag,
                    m,
                    v,
                    c["fixed"]["mean"],
                )
                n_n += 1
    assert n_n == len(NOISE_PUB), n_n
    return [
        f"- Fixed-recipe contrasts re-derived from the records equal the published values: {n_b} D24-A/D24-B "
        f"(raw) and D27-B (standardized) unit vectors (artifacts/analysis/D27B/d27b.json), {n_n} "
        "last - last_noise means (E27, A1, A6; artifacts/analysis/D27/noise.md)."
    ]


def fit_stats(mine: list[dict], v: str) -> dict:
    ps = [r["probes"][v] for r in mine]
    sel = [p["configs"][p["selected"]["index"]] for p in ps]
    ep = np.array([p["best_epoch"] + 1 for p in ps])
    run = np.array([c["epochs_run"] for c in sel])
    lr_e = Counter(
        "lr 1e-4" if p["selected"]["lr"] == LRS[0] else "lr 3e-3"
        for p in ps
        if p["selected"]["lr"] in (LRS[0], LRS[-1])
    )
    wd_e = Counter(
        "wd 0" if p["selected"]["weight_decay"] == WDS[0] else f"wd {sci(WDS[-1])}"
        for p in ps
        if p["selected"]["weight_decay"] in (WDS[0], WDS[-1])
    )
    edge = sum(
        p["selected"]["lr"] in (LRS[0], LRS[-1]) or p["selected"]["weight_decay"] in (WDS[0], WDS[-1]) for p in ps
    )
    return {
        "n": len(ps),
        "converged_selected": int(sum(p["converged"] for p in ps)),
        "converged_all_configs": int(sum(c["converged"] for p in ps for c in p["configs"])),
        "n_configs": len(LRS) * len(WDS) * len(ps),
        "selected": Counter(f"{p['selected']['lr']:g}/{p['selected']['weight_decay']:g}" for p in ps),
        "epoch_median": float(np.median(ep)),
        "epoch_q": [float(np.quantile(ep, 0.25)), float(np.quantile(ep, 0.75))],
        "epoch_min": int(ep.min()),
        "epoch_max": int(ep.max()),
        "epoch_le2": int((ep <= 2).sum()),
        "run_median": float(np.median(run)),
        "run_max": int(run.max()),
        "edge": int(edge),
        "lr_edge": dict(lr_e),
        "wd_edge": dict(wd_e),
        "below_chance": sorted(
            (r["arm"], r["split"], r["seed"], round(100 * r["probes"][v]["test_at_best"]["roc_auc"], 1))
            for r in mine
            if r["probes"][v]["test_at_best"]["roc_auc"] < 0.5
        ),
    }


# ---------- figures ----------


def curves_fig(recs: dict, path: Path) -> None:
    plt.switch_backend("agg")
    cols = [(m, v) for m in MODELS for v in VARIANTS]
    fig, axes = plt.subplots(len(SETS), 4, figsize=(17, 17), facecolor=SURF)
    for i, s in enumerate(SETS):
        for j, (m, v) in enumerate(cols):
            ax = axes[i, j]
            ax.set_facecolor(SURF)
            rs = [r for r in recs[s[0]] if r["model"] == m]
            if not rs:
                ax.axis("off")
                ax.text(
                    0.5,
                    0.5,
                    f"{s[1]}: BIOT only",
                    ha="center",
                    va="center",
                    color=INK2,
                    fontsize=9,
                    transform=ax.transAxes,
                )
                continue
            for a in s[6]:
                for r in (r for r in rs if r["arm"] == a):
                    p = r["probes"][v]
                    cv = 100 * np.asarray(p["configs"][p["selected"]["index"]]["val_curve"])
                    x = np.arange(1, len(cv) + 1)
                    ax.plot(x, cv, color=ARM_C[a], lw=0.8, alpha=0.6, zorder=2)
                    ax.plot(
                        p["best_epoch"] + 1,
                        cv[p["best_epoch"]],
                        "o",
                        color=ARM_C[a],
                        ms=3,
                        mec=SURF,
                        mew=0.6,
                        zorder=3,
                    )
            ax.set_title(f"{s[1]}, {NAME[m]}, {v}", fontsize=9.5, color=INK)
            ax.grid(color=GRID, lw=0.5)
            ax.tick_params(colors=INK2, labelsize=8)
            for sp in ("top", "right"):
                ax.spines[sp].set_visible(False)
            if i == len(SETS) - 1:
                ax.set_xlabel("epoch", fontsize=9, color=INK2)
            if j == 0:
                ax.set_ylabel("val ROC-AUC x100", fontsize=9, color=INK2)
    handles = [plt.Line2D([], [], color=ARM_C[a], lw=2, label=a) for a in A5]
    handles.append(plt.Line2D([], [], color=INK2, marker="o", ls="", ms=4, label="selected epoch"))
    fig.legend(
        handles=handles, loc="upper center", ncol=6, frameon=False, fontsize=10, bbox_to_anchor=(0.5, 0.995)
    )
    fig.suptitle(
        "D28: validation ROC-AUC per epoch of the selected configuration (one line per run; early stop "
        "after 20 epochs without a 1e-4 gain, at most 200)",
        y=0.012,
        fontsize=10,
        color=INK2,
    )
    fig.tight_layout(rect=(0, 0.02, 1, 0.975))
    for suf in ("pdf", "png"):
        fig.savefig(path.with_suffix(f".{suf}"), dpi=130, facecolor=SURF)
    plt.close(fig)


def effects_fig(res: dict, path: Path) -> None:
    plt.switch_backend("agg")
    rows = [(s[0], m) for s in SETS for m in s[5]]
    lab = {(t, m): f"{next(s[1] for s in SETS if s[0] == t)}, {NAME[m]}" for t, m in rows}
    short = {GAIN: "gain", EQUIV: "equiv.", UNRES: "n.r."}
    vc = {"grid": C_T, "grid_z": C_NB}
    fig, axes = plt.subplots(1, 4, figsize=(21, 6.4), sharey=True, facecolor=SURF)
    for ax, (a, b) in zip(axes, CONTRASTS, strict=True):
        ax.set_facecolor(SURF)
        for y, (t, m) in enumerate(rows):
            for off, v in ((-0.17, "grid"), (0.17, "grid_z")):
                c = res[(t, m, v)]["contrasts"].get(cname(a, b))
                if c is None:
                    continue
                ax.scatter(c["per_unit"], [y + off] * 5, s=9, color="#a8a7a2", zorder=2, linewidths=0)
                if c["nb"]:
                    ax.plot(c["nb"]["ci95"], [y + off] * 2, color=vc[v], lw=1.0, zorder=3)
                ax.plot(c["t"]["ci95"], [y + off] * 2, color=vc[v], lw=2.6, solid_capstyle="round", zorder=3)
                ax.plot(c["mean"], y + off, "o", color=vc[v], ms=5, mec=SURF, mew=1, zorder=4)
                ax.annotate(
                    short[c["label"]],
                    xy=(1.0, y + off),
                    xycoords=("axes fraction", "data"),
                    ha="right",
                    va="center",
                    fontsize=7.5,
                    color=INK2,
                )
        for x, ls in ((0, "-"), (-3, "--"), (3, "--")):
            ax.axvline(x, color="#b9b8b3", lw=0.9, ls=ls, zorder=1)
        ax.axhline(2.5, color=GRID, lw=0.8)
        ax.set_title(cname(a, b), fontsize=11, color=INK)
        ax.tick_params(colors=INK2, labelsize=8.5)
        ax.grid(axis="x", color=GRID, lw=0.5)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        ax.set_xlabel("difference, ROC-AUC x100", fontsize=9, color=INK2)
    axes[0].set_yticks(range(len(rows)), [lab[k] for k in rows], fontsize=9, color=INK)
    axes[0].set_ylim(len(rows) - 0.5, -0.6)
    handles = [
        plt.Line2D([], [], color=C_T, lw=2.6, marker="o", ms=5, label="grid (raw), 95% t-interval df 4"),
        plt.Line2D([], [], color=C_NB, lw=2.6, marker="o", ms=5, label="grid_z (standardized), 95% t-interval"),
        plt.Line2D([], [], color=INK2, lw=1.0, label="thin: Nadeau-Bengio 95% (rotations)"),
        plt.Line2D([], [], color="#a8a7a2", marker="o", ls="", ms=4, label="rotation means / seeds"),
    ]
    fig.legend(handles=handles, loc="upper center", ncol=4, frameon=False, fontsize=9, bbox_to_anchor=(0.5, 0.995))
    fig.suptitle(
        "D28 contrasts with tuned, early-stopped probes. Dashed: +-3. Labels: gain = gain demonstrated, "
        "equiv. = equivalent within +-3 (TOST), n.r. = not resolved. DL's split: 5 seeds on one split "
        "(seed uncertainty only).",
        y=0.03,
        fontsize=9,
        color=INK2,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 0.95))
    for suf in ("pdf", "png"):
        fig.savefig(path.with_suffix(f".{suf}"), dpi=160, facecolor=SURF)
    plt.close(fig)


# ---------- report ----------


def f1(x: float) -> str:
    return f"{x:+.1f}"


def fixed_cols(r: dict) -> tuple[str, str]:
    return (f"{r['fixed_mean']:.1f}", f1(r["tuned_minus_fixed_mean"])) if "fixed" in r else ("-", "-")


def iv(c: dict | None) -> str:
    return "-" if c is None else f"[{f1(c['ci95'][0])}, {f1(c['ci95'][1])}]"


def pv(p: float) -> str:
    return f"{p:.2g}" if p < 1e-3 else f"{p:.3f}"


def report(res: dict, checks: list[str], fits: dict, ratios: dict, q: dict, outl: list[str]) -> str:
    L = [
        "# D28: probe convergence (tuned, early-stopped linear probes on cached frozen features)",
        "",
        f'Protocol: notes/decisions.md "## {PROTOCOL}", frozen in git (commit c0283f4) before any '
        f"{PROTOCOL} run; applied as written. Probes: grid (raw features), grid_z (train-standardized); "
        f"AdamW lr {{{', '.join(sci(x) for x in LRS)}}} x wd {{{', '.join(sci(x) for x in WDS)}}} "
        f"({len(LRS) * len(WDS)} configurations), batch {FROZEN['batch']}, constant lr, BCE, "
        f"<= {FROZEN['max_epochs']} epochs, early stop after {FROZEN['patience']} epochs without a val ROC "
        f"gain > {sci(FROZEN['min_delta'])}; configuration and epoch selected on val ROC-AUC; "
        "test read once there.",
        "Units: rotation means over seeds [S_r, 1000+r, 2000+r] (95% t-interval df 4; Nadeau-Bengio corrected "
        "interval with n_test/n_train " + ", ".join(f"{t} {r:.3f}" for t, r in ratios.items()) + "). DL's split: "
        "the 5 seeds 42/123/2021/3407/8888 on one fixed split (**seed uncertainty on one split**, no NB). "
        f"Labels: **{GAIN}** (95% t-interval excludes 0 and |mean| > 3 that way), **{EQUIV}** (TOST margin 3, "
        f"alpha 0.05 rejects), **{UNRES}**. D18 = the paired rule (|mean| > 3, same sign in >= 4/5), descriptive "
        "consistency criterion. Everything outside the labels and Q1-Q3 is descriptive. ROC-AUC x100.",
        "Reading choices (NB label as sensitivity, Q3 = sign of the mean against D24-A/D24-B and D27-B, edges, "
        "1-based epochs) were fixed before any aggregate; the outlier list, the epoch <= 2 count and the "
        "per-model Q3 grouping were added after the first output (descriptive). See the script docstring.",
        "",
        "Command: `.venv/bin/python scripts/analysis/d28_read.py`",
        "",
        "## Checks",
        "",
        *checks,
        "",
        "## Answers",
        "",
    ]
    L += [
        f'- **Q1** (any SA gain last - lp "{GAIN}" with tuned probes?): **{q["Q1"]["answer"]}**. '
        + q["Q1"]["text"],
        f'- **Q2** (BIOT q95, DL\'s split, last - last_noise "{GAIN}" with either variant?): '
        f"**{q['Q2']['answer']}**. " + q["Q2"]["text"],
        f"- **Q3** (pretrained-vs-random contrasts keep their direction vs D24-A / D27-B?): "
        f"**{q['Q3']['answer']}**. " + q["Q3"]["text"],
        "",
    ]
    L += [
        "## Contrasts (registered labels)",
        "",
        "| setting | model | variant | contrast | mean | 95% t | NB 95% | TOST p | **label** | label with NB SE | "
        "D18 | same sign | per unit (rotation means / seeds) | fixed recipe (mean, 95% t, D18) |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for (tag, m, v), x in res.items():
        st = next(s[1] for s in SETS if s[0] == tag)
        for name, c in x["contrasts"].items():
            fx = c.get("fixed")
            fxs = "-" if fx is None else f"{FIXED[v]} {f1(fx['mean'])} {iv(fx['t'])} {fx['d18']}"
            L.append(
                f"| {st} | {NAME[m]} | {v} | {name} | {f1(c['mean'])} | {iv(c['t'])} | {iv(c['nb'])} | "
                f"{pv(c['t']['tost_p'])} | **{c['label']}** | {c['nb']['label'] if c['nb'] else '-'} | "
                f"{c['d18']} | {c['same_sign']}/5 | {', '.join(f1(u) for u in c['per_unit'])} | {fxs} |"
            )
    L += ["", "## Per seed (rotations: S_r / 1000+r / 2000+r per rotation)", ""]
    for (tag, m, v), x in res.items():
        for name, c in x["contrasts"].items():
            ps = c["per_seed"]
            txt = (
                ", ".join(f1(d) for d in ps)
                if tag.startswith("P1")
                else "; ".join(f"{r} " + "/".join(f1(d) for d in sd) for r, sd in zip(ROTS, ps, strict=True))
            )
            L.append(f"- {tag} {NAME[m]} {v} {name}: {txt}")
    L += [
        "",
        "## Absolute test ROC-AUC per arm: tuned vs fixed recipe (same seeds)",
        "",
        "| setting | model | arm | grid | linear (fixed) | grid - linear | grid_z | linear_z (fixed) | "
        "grid_z - linear_z | grid per unit | grid_z per unit |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for s in SETS:
        for m in s[5]:
            for a in s[6]:
                g, z = res[(s[0], m, "grid")]["arms"][a], res[(s[0], m, "grid_z")]["arms"][a]
                (fg, dg), (fz, dz) = fixed_cols(g), fixed_cols(z)
                L.append(
                    f"| {s[1]} | {NAME[m]} | {a} | {g['mean']:.1f} ± {g['sem']:.1f} | {fg} | {dg} | "
                    f"{z['mean']:.1f} ± {z['sem']:.1f} | {fz} | {dz} | "
                    f"{', '.join(f'{u:.1f}' for u in g['per_unit'])} | "
                    f"{', '.join(f'{u:.1f}' for u in z['per_unit'])} |"
                )
    L += [
        "",
        "## Fits: convergence, selected configurations, epochs, grid edges (descriptive)",
        "",
        f"Converged = early stopping fired before epoch {FROZEN['max_epochs']}. Epochs 1-based. Edge: "
        f"lr {sci(LRS[0])} or {sci(LRS[-1])}, or wd {sci(WDS[0])} or {sci(WDS[-1])} "
        f"({len(LRS) * len(WDS) - (len(LRS) - 2) * (len(WDS) - 2)} of {len(LRS) * len(WDS)} configurations "
        f"touch an edge).",
        "",
        "| setting | model | variant | fits | converged (selected) | converged (all 16) | selected epoch median "
        "[IQR] (min-max; at epoch <= 2) | epochs run, selected (median, max) | at an edge | lr edge | wd edge | "
        "selected lr/wd (count) | test ROC < 50 |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for (tag, m, v), f in fits.items():
        st = next(s[1] for s in SETS if s[0] == tag)
        sel = ", ".join(f"{k} ({n})" for k, n in sorted(f["selected"].items(), key=lambda kv: -kv[1]))
        bc = "; ".join(f"{a} {sp} s{sd} {r}" for a, sp, sd, r in f["below_chance"]) or "-"
        L.append(
            f"| {st} | {NAME[m]} | {v} | {f['n']} | {f['converged_selected']}/{f['n']} | "
            f"{f['converged_all_configs']}/{f['n_configs']} | {f['epoch_median']:g} [{f['epoch_q'][0]:g}, "
            f"{f['epoch_q'][1]:g}] ({f['epoch_min']}-{f['epoch_max']}; {f['epoch_le2']}) | {f['run_median']:g}, "
            f"{f['run_max']} | {f['edge']}/{f['n']} | {json.dumps(f['lr_edge'])} | {json.dumps(f['wd_edge'])} | "
            f"{sel} | {bc} |"
        )
    L += [
        "",
        "## Single-seed differences beyond +-25 (descriptive)",
        "",
        "Each arm: selected lr / wd / epoch, val and test ROC-AUC x100 at the selection.",
        "",
        *outl,
    ]
    L += [
        "",
        "## Figures",
        "",
        "- artifacts/figures/f_d28_curves.pdf/png: selected configuration's val ROC-AUC per epoch, per arm, "
        "setting, model and variant (the D28 learning-curve figure).",
        "- artifacts/figures/fig_effects_d28.pdf/png: the D28 contrasts with 95% t and Nadeau-Bengio intervals.",
    ]
    return "\n".join(L) + "\n"


def answers(res: dict) -> dict:
    q1 = [
        (t, m, v, c["mean"])
        for (t, m, v), x in res.items()
        for n, c in x["contrasts"].items()
        if n == "last - lp" and c["label"] == GAIN and c["mean"] > 0
    ]
    sa = [(t, m, v, c) for (t, m, v), x in res.items() for n, c in x["contrasts"].items() if n == "last - lp"]
    q1t = (
        ("SA gain demonstrated in: " + "; ".join(f"{t} {NAME[m]} {v} {f1(mu)}" for t, m, v, mu in q1))
        if q1
        else f'0 of {len(sa)} last - lp readings read "{GAIN}" in the positive direction; labels: '
        + ", ".join(f"{lab} {n}" for lab, n in Counter(c["label"] for *_, c in sa).most_common())
        + "."
    )
    q2 = {v: res[(TAG["P1QG"], "biot", v)]["contrasts"]["last - last_noise"] for v in VARIANTS}
    q2a = "yes" if any(c["label"] == GAIN and c["mean"] > 0 for c in q2.values()) else "no"
    q2t = "; ".join(
        f"{v}: {f1(c['mean'])} {iv(c['t'])}, TOST p {pv(c['t']['tost_p'])}, {c['label']}, per seed "
        f"{', '.join(f1(u) for u in c['per_unit'])} (fixed recipe {FIXED[v]} {f1(c['fixed']['mean'])})"
        for v, c in q2.items()
    )
    rows, flips = [], []
    for (t, m, v), x in res.items():
        for n in ("last_randinit - last", "lp - lp_randinit"):
            c = x["contrasts"].get(n)
            if c is None or "fixed" not in c:
                continue
            keep = bool(np.sign(c["mean"]) == np.sign(c["fixed"]["mean"]))
            rows.append(
                {
                    "tag": t,
                    "model": m,
                    "variant": v,
                    "contrast": n,
                    "mean": c["mean"],
                    "label": c["label"],
                    "fixed_mean": c["fixed"]["mean"],
                    "fixed_d18": c["fixed"]["d18"],
                    "keeps_sign": keep,
                }
            )
            if not keep:
                flips.append(rows[-1])

    def one(r: dict) -> str:
        return (
            f"{r['tag']} {r['variant']} {r['contrast']} {f1(r['fixed_mean'])} ({r['fixed_d18']}) -> "
            f"{f1(r['mean'])} ({r['label']})"
        )

    q3t, per = [], {}
    for m in MODELS:
        rm = [r for r in rows if r["model"] == m]
        won = [r for r in rm if r["fixed_d18"] != "no difference shown"]
        per[m] = {
            "rows": len(rm),
            "sign_kept": sum(r["keeps_sign"] for r in rm),
            "gain_same_sign": sum(r["keeps_sign"] and r["label"] == GAIN for r in rm),
            "fixed_d18_wins": len(won),
            "fixed_wins_sign_kept": sum(r["keeps_sign"] for r in won),
            "fixed_wins_gain_same_sign": sum(r["keeps_sign"] and r["label"] == GAIN for r in won),
        }
        p = per[m]
        fl = [r for r in rm if not r["keeps_sign"]]
        q3t.append(
            f"{NAME[m]}: {p['sign_kept']} of {p['rows']} keep the sign of the mean ({p['gain_same_sign']} "
            f'"{GAIN}" that way); of the {p["fixed_d18_wins"]} fixed-recipe readings with a D18 win, '
            f'{p["fixed_wins_sign_kept"]} keep the sign and {p["fixed_wins_gain_same_sign"]} read "{GAIN}"'
            + (". Sign flips: " + "; ".join(one(r) for r in fl) if fl else "")
        )
    ans = "; ".join(
        f"{NAME[m]} "
        + (
            "yes (all signs kept)"
            if per[m]["sign_kept"] == per[m]["rows"]
            else f"{per[m]['rows'] - per[m]['sign_kept']} of {per[m]['rows']} signs flip"
        )
        for m in MODELS
    )
    return {
        "Q1": {"answer": "yes" if q1 else "no", "text": q1t, "hits": q1},
        "Q2": {"answer": q2a, "text": q2t},
        "Q3": {"answer": ans, "text": ". ".join(q3t) + ".", "per_model": per, "rows": rows, "flips": flips},
    }


def outliers(res: dict, mine_by: dict, thr: float = 25.0) -> list[str]:
    """Descriptive: single-seed contrast differences beyond +-thr, with each arm's selection, val and test ROC."""
    idx = {(t, *cell(r)): r for t, rs in mine_by.items() for r in rs}
    out = []
    for (t, m, v), x in res.items():
        for name, c in x["contrasts"].items():
            a, b = name.split(" - ")
            seeds = (
                [("paper", s, d) for s, d in zip(SR, c["per_seed"], strict=True)]
                if t.startswith("P1")
                else [
                    (r, s, d)
                    for r, ds in zip(ROTS, c["per_seed"], strict=True)
                    for s, d in zip(SEEDS3[r], ds, strict=True)
                ]
            )
            for sp, sd, d in seeds:
                if abs(d) <= thr:
                    continue
                arms = []
                for arm in (a, b):
                    p = idx[(t, m, arm, sp, sd)]["probes"][v]
                    arms.append(
                        f"{arm} lr {p['selected']['lr']:g} wd {p['selected']['weight_decay']:g} epoch "
                        f"{p['best_epoch'] + 1}: val {100 * p['val_at_best']['roc_auc']:.1f} test "
                        f"{100 * p['test_at_best']['roc_auc']:.1f}"
                    )
                out.append(f"- {t} {NAME[m]} {v} {name} {sp} s{sd}: {f1(d)} ({'; '.join(arms)})")
    return out


def use_d31() -> None:
    """Read the D31 tags (W) at FROZEN31 instead of the D28 tags (G), and write to artifacts/analysis/D31.

    Everything else is identical: the same settings, models, arms, partner tags and nb_ratio keys, so the
    two searches are read by one code path and stay comparable.
    """
    global OUT, SETS, FROZEN, LRS, WDS, D27B_SET, NOISE_PUB, TAG
    global JSON_NAME, CURVES_FIG, EFFECTS_FIG, PROTOCOL
    TAG = dict(D31_TAG)
    JSON_NAME, CURVES_FIG, EFFECTS_FIG = "d31.json", "f_d31_curves.pdf", "fig_effects_d31.pdf"
    PROTOCOL = "D31"
    OUT = ROOT / "artifacts" / "analysis" / "D31"
    SETS = tuple((D31_TAG[s[0]], *s[1:]) for s in SETS)
    D27B_SET = {D31_TAG[k]: v for k, v in D27B_SET.items()}
    NOISE_PUB = {(D31_TAG[tg], m, v): x for (tg, m, v), x in NOISE_PUB.items()}
    FROZEN, LRS, WDS = FROZEN31, LRS31, WDS31
    OUT.mkdir(parents=True, exist_ok=True)


def main() -> int:
    if "--d31" in sys.argv[1:]:
        use_d31()
    selfcheck()
    recs_all = scan()
    refs = {}
    d28_tags = {s[0] for s in SETS}
    for r in recs_all:
        if r["run_tag"] not in d28_tags and not r.get("smoke"):
            k = (r["run_tag"], *cell(r))
            assert k not in refs, f"two fixed-recipe records for {k}"
            refs[k] = r
    checks, res, fits, ratios, mine_by = [], {}, {}, {}, {}
    for s in SETS:
        mine, lines, _acc = verify(s, recs_all, refs)
        checks += lines
        mine_by[s[0]] = mine
        tag, _st, ds, *_x, nbk, (lt, zt) = s
        ratio = None
        if nbk:
            ratio, _w = nb_ratio(nbk)
            ratios[tag] = ratio
        roc = load(str(LOCAL), ds, {tag})
        ref = {
            "linear": load(str(LOCAL), ds, set(lt.split(","))),
            "linear_z": load(str(LOCAL), ds, set(zt.split(","))),
        }
        for (m, v), x in read_set(s, roc, ref, ratio).items():
            res[(tag, m, v)] = x
        for m in s[5]:
            for v in VARIANTS:
                fits[(tag, m, v)] = fit_stats([r for r in mine if r["model"] == m], v)
    checks += check_published(res)
    n_rec = sum(len(v) for v in mine_by.values())
    checks.insert(
        0,
        f"- {n_rec} D28 records ({', '.join(f'{t} {len(v)}' for t, v in mine_by.items())}), "
        f"{2 * n_rec} probe fits, {32 * n_rec} configuration fits; 0 smoke records among them.",
    )
    q = answers(res)
    outl = outliers(res, mine_by)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "README.md").write_text(report(res, checks, fits, ratios, q, outl))
    js = {
        "protocol": "notes/decisions.md ## D28 (commit c0283f4)",
        "checks": checks,
        "nb_ratio": ratios,
        "answers": q,
        "outliers": outl,
        "contrasts": {f"{t}|{m}|{v}": x for (t, m, v), x in res.items()},
        "fits": {f"{t}|{m}|{v}": f for (t, m, v), f in fits.items()},
    }
    (OUT / JSON_NAME).write_text(
        json.dumps(js, indent=1, default=lambda o: dict(o) if isinstance(o, Counter) else str(o))
    )
    curves_fig(mine_by, FIG / CURVES_FIG)
    effects_fig(res, FIG / EFFECTS_FIG)
    print((OUT / "README.md").read_text())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
