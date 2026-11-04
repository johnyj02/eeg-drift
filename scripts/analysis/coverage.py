#!/usr/bin/env python3
"""E9 (D25): coverage of the paper's CHB-MIT Tables 1-2 by our reimplementation runs.

    .venv/bin/python scripts/analysis/coverage.py [--local artifacts/s3-results]

Pre-registered (notes/completeness-audit.md E9, adopted by notes/decisions.md D25):
- D13 distance of a cell = worst of the bal/PR/ROC gaps in units of the paper's SEM, floor 1
  point; "consistent" <= 3 on all three metrics, "partial" on two of three, else "not".
- Closest run per paper cell, separately at test_at_best and test_last, with the failing metric.
- Rule D25-E9: a cell is "matched" only if D13-consistent at ONE epoch rule (best or last) fixed
  across all four Table 1 cells of a configuration; no mixing within a configuration.
Descriptive (no rule): Table 2 cells (one seed, no SEM: unit = 1 point), the P1E table, the AUCPR
panel. Released-code column left as "pending E4-E7". TUAB/TUEV: not tested (no TUH).
Writes artifacts/analysis/coverage/{coverage.md, coverage.json, *.png}.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.metrics import auc, precision_recall_curve

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from eegdrift.data.chbmit import overlap_label  # noqa: E402

OUT = ROOT / "artifacts" / "analysis" / "coverage"
METRICS = ("bal_acc", "pr_auc_trapz", "roc_auc")          # D13 order bal / PR / ROC
SHORT = {"bal_acc": "bal", "pr_auc_trapz": "PR", "roc_auc": "ROC"}
WHEN = ("test_at_best", "test_last")
WIN = 10 * 256

# Paper Table 1, CHB-MIT, mean ± SEM over 5 seeds (artifacts/paper/paper.txt l.155-175)
T1 = {("biot", "LP"): ((50.74, 0.21), (1.53, 0.03), (46.93, 0.30)),
      ("biot", "SA"): ((52.71, 0.72), (31.52, 1.21), (83.08, 1.89)),
      ("cbramod", "LP"): ((57.87, 0.20), (17.35, 0.24), (54.14, 1.39)),
      ("cbramod", "SA"): ((61.37, 3.50), (24.62, 2.31), (83.67, 1.36))}
# Paper Table 2, CHB-MIT, ONE seed, no dispersion (l.403-412): (params, bal, PR, ROC)
T2 = {("biot", "L"): ("0.92M", 60.62, 35.62, 88.67), ("biot", "L,L-1"): ("1.71M", 60.82, 35.05, 88.44),
      ("biot", "All"): ("3.19M", 62.18, 36.79, 88.60), ("cbramod", "L"): ("0.44M", 67.60, 31.25, 87.16),
      ("cbramod", "L,L-1"): ("0.84M", 58.69, 21.90, 86.62), ("cbramod", "All"): ("4.4M", 50.98, 29.41, 88.20)}
CELL_ARMS = {"LP": ("lp",), "SA": ("last", "last_randinit"), "L": ("last", "last_randinit"),
             "L,L-1": ("last2", "last2_randinit"), "All": ("all", "all_randinit")}
# reimplementation families on the paper split named in E9 (wave 1 incl. R1, R2-R4, C1/C2 = the D13
# confirmation seeds, P1E, R3E). R3E has lp only. R2 changes only the SSL pool, so its LP is wave 1's.
TAGS = {"": "wave1", "R2-fullN": "R2-fullN", "R3-b128": "R3-b128(+C1)", "R4-filt": "R4-filt",
        "C-filt-b128": "C2:C-filt-b128", "P1E": "P1E", "R3E-b128": "R3E-b128"}
LP_FROM = {"R2-fullN": ""}
# D13 outcome as published (decisions.md D13): R3-b128 / C-filt-b128, linear, last_randinit, best
D13_PUBLISHED = {("R3-b128", "biot", "LP"): (0.2, 2.7, 11.6), ("R3-b128", "biot", "SA"): (5.0, 6.2, 3.6),
                 ("R3-b128", "cbramod", "LP"): (0.3, 2.6, 10.6), ("R3-b128", "cbramod", "SA"): (0.5, 0.3, 1.2),
                 ("C-filt-b128", "biot", "LP"): (0.0, 2.4, 19.4), ("C-filt-b128", "biot", "SA"): (5.2, 4.0, 3.3),
                 ("C-filt-b128", "cbramod", "LP"): (0.2, 0.8, 4.1),
                 ("C-filt-b128", "cbramod", "SA"): (1.2, 0.6, 2.4)}
PREV_PAPER = 252 / 16964


def load(local: Path) -> dict:
    """(tag, split, model, arm, probe) -> {seed: (probe result, npz path, test-index path, record)}."""
    runs: dict = defaultdict(dict)
    seen: dict = defaultdict(set)
    for p in local.rglob("results/*.json"):
        if p.name.startswith(("diag-", "test-index-", "report-")):
            continue
        r = json.loads(p.read_text())
        if r.get("smoke") or r["dataset"] != "chbmit":
            continue
        tag = r.get("run_tag", "")
        split = r["split"] if r["split"] == "paper" else "rot"
        seen[(tag, split, r["model"])].add((r["eval_hash"] if split == "paper" else "-", r.get("labels"),
                                             r["versions"]["probe"]))
        for probe, res in r["probes"].items():
            cell = (tag, r["split"], r["model"], r["arm"], probe)
            if r["seed"] in runs[cell]:
                raise SystemExit(f"two records for {cell} seed {r['seed']}")
            runs[cell][r["seed"]] = (res, p.with_suffix(f".{probe}.npz"), p.parent / r["test_index"], r)
    mixed = {k: v for k, v in seen.items() if len(v) > 1}
    if mixed:
        raise SystemExit(f"a tag mixes eval data, labels or probe code: {mixed}")
    return runs


def m_s(v) -> tuple[float, float]:
    v = np.asarray(v, dtype=float)
    return float(v.mean()), float(v.std(ddof=1) / np.sqrt(len(v))) if len(v) > 1 else float("nan")


def fmt(t) -> str:
    return "-" if t is None else f"{t[0]:.2f} ± {t[1]:.2f}" if np.isfinite(t[1]) else f"{t[0]:.2f}"


def cell_mean(runs, tag, model, arm, probe, when) -> tuple[list[float], int] | None:
    src = LP_FROM.get(tag, tag) if arm == "lp" else tag
    seeds = runs.get((src, "paper", model, arm, probe), {})
    if not seeds:
        return None
    return [100 * float(np.mean([s[0][when][m] for s in seeds.values()])) for m in METRICS], len(seeds)


def d13(ours, paper) -> tuple[list[float], float, str, list[str]]:
    """Signed gaps in paper-SEM units (floor 1 point), distance, status, failing metrics."""
    g = [(o - v) / max(s, 1.0) for o, (v, s) in zip(ours, paper, strict=True)]
    k = sum(abs(x) <= 3 for x in g)
    status = "consistent" if k == 3 else "partial" if k == 2 else "not"
    return g, max(abs(x) for x in g), status, [SHORT[m] for m, x in zip(METRICS, g, strict=True) if abs(x) > 3]


def paper_cells():
    for (model, cell), p in T1.items():
        yield "T1", model, cell, p, "SEM, 5 seeds"
    for (model, cell), (_par, bal, pr, roc) in T2.items():
        yield "T2", model, cell, ((bal, 0.0), (pr, 0.0), (roc, 0.0)), "none (1 seed): unit = 1 point"


def coverage(runs) -> tuple[list[dict], list[dict]]:
    """All (paper cell, candidate) distances, and the closest candidate per cell and epoch rule."""
    probes = sorted({k[4] for k in runs})
    allrows = []
    for table, model, cell, paper, disp in paper_cells():
        for tag in TAGS:
            for probe in probes:
                for arm in CELL_ARMS[cell]:
                    for when in WHEN:
                        got = cell_mean(runs, tag, model, arm, probe, when)
                        if got is None:
                            continue
                        g, dist, status, fail = d13(got[0], paper)
                        allrows.append({"table": table, "model": model, "cell": cell, "dispersion": disp,
                                        "paper": [v for v, _ in paper], "paper_sem": [s for _, s in paper],
                                        "tag": tag, "probe": probe, "arm": arm, "when": when,
                                        "n_seeds": got[1], "ours": got[0], "gaps": g, "distance": dist,
                                        "status": status, "failing": fail})
    closest = []
    for table, model, cell, _p, _d in paper_cells():
        for when in WHEN:
            c = [r for r in allrows
                 if (r["table"], r["model"], r["cell"], r["when"]) == (table, model, cell, when)]
            closest.append(min(c, key=lambda r: r["distance"]))
    return allrows, closest


def configs(allrows) -> list[dict]:
    """Rule D25-E9 inputs: per (tag, probe, SA arm, epoch rule), the four Table 1 cells."""
    t1 = {(r["tag"], r["probe"], r["model"], r["cell"], r["arm"], r["when"]): r
          for r in allrows if r["table"] == "T1"}
    out = []
    for tag, probe, sa_arm in sorted({(k[0], k[1], k[4]) for k in t1 if k[3] == "SA"}):
        for when in WHEN:
            cells = {f"{m} {c}": t1.get((tag, probe, m, c, "lp" if c == "LP" else sa_arm, when))
                     for m in ("biot", "cbramod") for c in ("LP", "SA")}
            if any(v is None for v in cells.values()):
                continue
            n_cons = sum(v["status"] == "consistent" for v in cells.values())
            out.append({"tag": tag, "probe": probe, "sa_arm": sa_arm, "when": when, "n_consistent": n_cons,
                        "sum_distance": sum(v["distance"] for v in cells.values()),
                        "all_four_consistent": n_cons == 4,
                        "d13_all_at_least_partial": all(v["status"] != "not" for v in cells.values()),
                        "cells": {k: {"status": v["status"], "distance": v["distance"], "gaps": v["gaps"],
                                      "n_seeds": v["n_seeds"]} for k, v in cells.items()}})
    return out


def pr_trapz(y, s) -> float:
    p, r, _ = precision_recall_curve(y, s)
    return float(auc(r, p))


def aucpr_panel(runs) -> list[dict]:
    """PR-AUC (trapz) and PR/prevalence at the val-selected epoch for lp, last, last_randinit."""
    seizures = json.loads((ROOT / "configs" / "chbmit_seizures.json").read_text())
    masks: dict = {}
    rows = []
    for tag, proto in (("", "released path (wave 1)"), ("P1E", "fixed probe (P1E)")):
        for model in ("biot", "cbramod"):
            for probe in ("linear", "mlp_fullft"):
                for arm in ("lp", "last", "last_randinit"):
                    per: dict = defaultdict(list)    # scoring -> [(seed, pr, prevalence)]
                    for seed, (res, npz, idx, _r) in sorted(runs[(tag, "paper", model, arm, probe)].items()):
                        if idx not in masks:
                            tindex = json.loads(idx.read_text())
                            grid = np.array(["-grid-" in t["key"] for t in tindex])
                            fixed = np.array([overlap_label({"file": t["key"].rsplit("-", 2)[0], "n_samples": WIN,
                                                             "start": int(t["key"].rsplit("-", 2)[2])}, seizures)
                                              for t in tindex])
                            masks[idx] = (grid, fixed)
                        grid, fixed = masks[idx]
                        a = np.load(npz)
                        y, s = a["y_test"].astype(int), a["scores_best"]
                        up = pr_trapz(y, s)
                        if abs(up - res["test_at_best"]["pr_auc_trapz"]) > 1e-6:
                            raise SystemExit(f"{npz.name}: npz re-score {up} != record")
                        per["upstream"].append((seed, up, y.mean()))
                        per["dedup"].append((seed, pr_trapz(y[grid], s[grid]), y[grid].mean()))
                        per["fixed"].append((seed, pr_trapz(fixed[grid], s[grid]), fixed[grid].mean()))
                    for scoring, v in per.items():
                        rows.append({"protocol": proto, "scoring": scoring, "model": model, "head": probe,
                                     "arm": arm, "replicate": "seed",
                                     "by": {str(sd): (100 * pr, float(pv)) for sd, pr, pv in v}})
    # corrected protocol (D24-A tags S1M + CBraMod's S_r seed from S1E), linear head, 5 rotations
    for model in ("biot", "cbramod"):
        for arm in ("lp", "last", "last_randinit"):
            by = {}
            for rot in range(5):
                seeds = {**runs.get(("S1M", f"rot{rot}", model, arm, "linear"), {}),
                         **runs.get(("S1E", f"rot{rot}", model, arm, "linear"), {})}
                for res, *_ in seeds.values():
                    if res["spec"].get("backbone_mode") != "eval":
                        raise SystemExit(f"corrected protocol {model} {arm} rot{rot}: not eval mode")
                if len(seeds) != 3:
                    raise SystemExit(f"corrected protocol {model} {arm} rot{rot}: {len(seeds)} seeds, want 3")
                t = [s[0]["test_at_best"] for s in seeds.values()]
                # rotation = replicate: seed mean of PR and of PR/prevalence (prevalence is per fold)
                by[f"rot{rot}"] = (100 * float(np.mean([x["pr_auc_trapz"] for x in t])),
                                   float(np.mean([x["prevalence"] for x in t])))
            rows.append({"protocol": "corrected protocol (S1M+S1E)", "scoring": "overlap labels, grid only",
                         "model": model, "head": "linear", "arm": arm, "replicate": "rotation (3-seed mean)",
                         "by": by})
    lp = {(r["protocol"], r["scoring"], r["model"], r["head"]): r["by"] for r in rows if r["arm"] == "lp"}
    for r in rows:
        b = r["by"]
        r["pr"] = m_s([v[0] for v in b.values()])
        r["prevalence_pct"] = 100 * float(np.mean([v[1] for v in b.values()]))
        r["pr_over_prev"] = m_s([v[0] / (100 * v[1]) for v in b.values()])
        base = lp[(r["protocol"], r["scoring"], r["model"], r["head"])]
        # paired by seed or rotation; prevalence cancels within a replicate
        r["ratio_vs_lp"] = m_s([b[k][0] / base[k][0] for k in b])
        r["n"] = len(b)
    return rows


def check(allrows) -> None:
    """The distance code must reproduce the published D13 outcome (published to 0.1)."""
    for (tag, model, cell), want in D13_PUBLISHED.items():
        arm = "lp" if cell == "LP" else "last_randinit"
        r = next(x for x in allrows if (x["tag"], x["model"], x["cell"], x["arm"], x["probe"], x["when"])
                 == (tag, model, cell, arm, "linear", "test_at_best") and x["table"] == "T1")
        got = tuple(abs(g) for g in r["gaps"])
        assert all(abs(a - b) <= 0.06 for a, b in zip(got, want, strict=True)), (tag, model, cell, got, want)


def figures(allrows, panel) -> list[str]:
    import matplotlib  # noqa: PLC0415
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt  # noqa: PLC0415

    paths = []
    # 1. D13 distance heatmap: rows = paper cell x our arm, cols = family x head; best and last
    rowkeys = [(t, m, c, a) for t, m, c, _p, _d in paper_cells() for a in CELL_ARMS[c]]
    probes = ("linear", "mlp_fullft")
    colkeys = [(t, p) for t in TAGS for p in probes
               if any(r["tag"] == t and r["probe"] == p for r in allrows)]
    fig, axes = plt.subplots(1, 2, figsize=(17, 9), sharey=True, constrained_layout=True)
    for ax, when in zip(axes, WHEN, strict=True):
        z = np.full((len(rowkeys), len(colkeys)), np.nan)
        for r in allrows:
            if r["when"] != when:
                continue
            i = rowkeys.index((r["table"], r["model"], r["cell"], r["arm"]))
            z[i, colkeys.index((r["tag"], r["probe"]))] = r["distance"]
        im = ax.imshow(np.minimum(z, 20), cmap="Blues", vmin=0, vmax=20, aspect="auto")
        for i in range(z.shape[0]):
            for j in range(z.shape[1]):
                if np.isfinite(z[i, j]):
                    ax.text(j, i, f"{z[i, j]:.1f}", ha="center", va="center", fontsize=7,
                            color="white" if z[i, j] > 11 else "#0b0b0b",
                            fontweight="bold" if z[i, j] <= 3 else "normal")
                    if z[i, j] <= 3:
                        ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, ec="#eb6834", lw=2))
                else:
                    ax.text(j, i, "–", ha="center", va="center", fontsize=7, color="#8a8984")
        ax.axhline(5.5, color="#52514e", lw=1)
        ax.set_xticks(range(len(colkeys)), [f"{TAGS[t]}\n{p}" for t, p in colkeys], rotation=60,
                      ha="right", fontsize=8)
        ax.set_yticks(range(len(rowkeys)), [f"{t} {m} {c} · {a}" for t, m, c, a in rowkeys], fontsize=8)
        ax.set_title(f"{when}: D13 distance (worst of bal/PR/ROC, paper-SEM units, floor 1)\n"
                     "orange box = <= 3 on all three metrics (consistent)", fontsize=9)
    fig.colorbar(im, ax=axes, shrink=0.6, label="distance (clipped at 20)")
    fig.suptitle("E9 coverage: paper CHB-MIT Table 1 (SEM, 5 seeds) and Table 2 (1 seed, unit = 1 point; "
                 "descriptive) vs our runs (seed means)", fontsize=10)
    p = OUT / "coverage-d13-heatmap.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    paths.append(str(p))

    # 2. AUCPR panel: PR/prevalence (log) for lp / last / last_randinit across protocols and scorings
    colors = {"lp": "#2a78d6", "last": "#eb6834", "last_randinit": "#1baf7a"}
    groups = [("released path (wave 1)", "upstream"), ("released path (wave 1)", "dedup"),
              ("released path (wave 1)", "fixed"), ("fixed probe (P1E)", "upstream"),
              ("fixed probe (P1E)", "dedup"), ("fixed probe (P1E)", "fixed"),
              ("corrected protocol (S1M+S1E)", "overlap labels, grid only")]
    glabel = ["released\nupstream", "released\ndedup", "released\nfixed", "fixed probe\nupstream",
              "fixed probe\ndedup", "fixed probe\nfixed", "corrected\nprotocol\n(5 rot)"]
    idx = {(r["protocol"], r["scoring"], r["model"], r["head"], r["arm"]): r for r in panel}
    fig, axes = plt.subplots(2, 2, figsize=(14, 8), sharey=True, constrained_layout=True)
    for i, head in enumerate(("linear", "mlp_fullft")):
        for j, model in enumerate(("biot", "cbramod")):
            ax = axes[i, j]
            for k, arm in enumerate(colors):
                xs, ys, es = [], [], []
                for g, key in enumerate(groups):
                    r = idx.get((*key, model, head, arm))
                    if r:
                        xs.append(g + (k - 1) * 0.26)
                        ys.append(r["pr_over_prev"][0])
                        es.append(0 if not np.isfinite(r["pr_over_prev"][1]) else r["pr_over_prev"][1])
                ax.bar(xs, ys, width=0.24, yerr=es, color=colors[arm], label=arm, ec="white", lw=1,
                       error_kw={"lw": 1, "ecolor": "#52514e"})
            lp_p, sa_p = T1[(model, "LP")][1][0], T1[(model, "SA")][1][0]
            ax.scatter([-0.26, 0.0], [lp_p / (100 * PREV_PAPER), sa_p / (100 * PREV_PAPER)], marker="D", s=50,
                       color="#0b0b0b", zorder=5, label="paper Table 1 (LP, SA)")
            if head != "linear":
                ax.text(len(groups) - 1, 1.3, "not run\n(linear only)", ha="center", fontsize=8, color="#52514e")
            ax.axhline(1, color="#8a8984", ls="--", lw=1)
            ax.set_yscale("log")
            ax.set_xticks(range(len(groups)), glabel, fontsize=8)
            ax.set_title(f"{model}, {head} head", fontsize=10)
            ax.grid(axis="y", color="#e4e3df", lw=0.6)
            ax.set_axisbelow(True)
            if j == 0:
                ax.set_ylabel("PR-AUC / prevalence (1 = random)")
    axes[0, 0].legend(fontsize=8, loc="upper left")
    fig.suptitle("AUCPR panel for the paper's '20x AUCPR' claim: PR-AUC (trapz) / test prevalence, "
                 "val-selected epoch, mean ± SEM (seeds; corrected protocol: rotations). "
                 "Corrected protocol is linear-head only.", fontsize=9)
    p = OUT / "aucpr-panel.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    paths.append(str(p))
    return paths


def p1e_table(runs) -> list[dict]:
    rows = []
    for model in ("biot", "cbramod"):
        for probe in ("linear", "mlp_fullft"):
            for arm in ("lp", "last", "lp_randinit", "last_randinit"):
                seeds = runs[("P1E", "paper", model, arm, probe)]
                row = {"model": model, "head": probe, "arm": arm, "n": len(seeds)}
                for when in WHEN:
                    for m in ("bal_acc", "pr_auc_trapz", "avg_precision", "roc_auc"):
                        row[f"{when}.{m}"] = m_s([100 * s[0][when][m] for s in seeds.values()])
                rows.append(row)
    return rows


def write_md(allrows, closest, cfgs, p1e, panel, figs) -> str:
    L = ["# E9 coverage matrix: paper CHB-MIT Tables 1-2 vs our reimplementation (D25-E9)", "",
         "Generated by scripts/analysis/coverage.py from artifacts/s3-results (local records). x100.",
         "D13 distance = worst of the |ours - paper| gaps over bal / PR (trapz) / ROC in units of the paper's",
         "SEM with a floor of 1 point; consistent <= 3 on all three, partial on two of three, else not.",
         "Our value = mean over the run's seeds. Signed gaps (ours - paper, in units) are listed bal/PR/ROC.",
         "Candidate families (E9): wave 1 (incl. R1 random-init last2/all), R2-fullN (LP borrowed from wave 1: R2",
         "changes only the SSL pool), R3-b128 (+ C1 seeds 2021/3407/8888), R4-filt, C2 = C-filt-b128, P1E,",
         "R3E-b128 (lp only). Cell -> arms: LP: lp; SA and Table 2 L: last, last_randinit; L,L-1: last2,",
         "last2_randinit; All: all, all_randinit. The released-code column is filled after E4-E7.", "",
         "Self-check passed: the distance code reproduces the published D13 outcome (R3-b128 and C-filt-b128,",
         "linear, last_randinit, test_at_best) to 0.1 on all 24 gaps.", "",
         "## 1. Closest run per paper cell (Table 1 = rule-bearing; Table 2 = descriptive)", "",
         "| table | model | cell | paper bal/PR/ROC (dispersion) | epoch | closest run: family / head / arm (n) "
         "| ours bal/PR/ROC | gaps (units) | dist | status | failing | released-code run |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in closest:
        p = "/".join(f"{v:.2f}" for v in r["paper"])
        sem = "/".join(f"{s:.2f}" for s in r["paper_sem"]) if r["table"] == "T1" else "-"
        L.append(f"| {r['table']} | {r['model']} | {r['cell']} | {p} (± {sem}; {r['dispersion']}) | "
                 f"{r['when'].replace('test_', '')} | "
                 f"{TAGS[r['tag']]} / {r['probe']} / {r['arm']} ({r['n_seeds']}) | "
                 f"{'/'.join(f'{v:.2f}' for v in r['ours'])} | {'/'.join(f'{g:+.1f}' for g in r['gaps'])} | "
                 f"{r['distance']:.1f} | {r['status']} | {','.join(r['failing']) or '-'} | pending E4-E7 |")
    for ds in ("TUAB", "TUEV"):
        L.append(f"| T1 | biot, cbramod | {ds} LP, SA | (paper Table 1) | - | not tested (no TUH) | "
                 "- | - | - | - | - | - |")

    L += ["", "## 2. Rule D25-E9 on Table 1, per configuration (family, head, SA arm) and epoch rule", "",
          "Each row evaluates all four Table 1 cells at ONE epoch rule (no mixing). LP arm = lp.", "",
          "| family | head | SA arm | epoch | BIOT LP | BIOT SA | CBraMod LP | CBraMod SA | # consistent | "
          "all four consistent | D13 lenient (all >= partial) |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in cfgs:
        cells = " | ".join(f"{v['status']} {v['distance']:.1f} (n={v['n_seeds']})"
                           for v in (c["cells"][k] for k in ("biot LP", "biot SA", "cbramod LP", "cbramod SA")))
        L.append(f"| {TAGS[c['tag']]} | {c['probe']} | {c['sa_arm']} | {c['when'].replace('test_', '')} | "
                 f"{cells} | "
                 f"{c['n_consistent']}/4 | {'YES' if c['all_four_consistent'] else 'no'} | "
                 f"{'yes' if c['d13_all_at_least_partial'] else 'no'} |")
    matched = sorted({(k, c["tag"], c["probe"], c["sa_arm"], c["when"]) for c in cfgs
                      for k, v in c["cells"].items() if v["status"] == "consistent"})
    whole = [c for c in cfgs if c["all_four_consistent"]]
    L += ["", "### Verdict (D25-E9)", ""]
    L.append("- Table 1 as a whole (all four cells D13-consistent in one configuration at one epoch rule): "
             + ("**MATCHED** by "
                + "; ".join(f"{TAGS[c['tag']]}/{c['probe']}/{c['sa_arm']}/{c['when']}" for c in whole)
                if whole else "**NOT MATCHED** by any configuration at either epoch rule."))
    for k in ("biot LP", "biot SA", "cbramod LP", "cbramod SA"):
        hits = [f"{TAGS[t]}/{p}/{a}/{w.replace('test_', '')}" for kk, t, p, a, w in matched if kk == k]
        L.append(f"- {k}: " + (f"consistent within a configuration at one epoch rule in {len(hits)} case(s): "
                               + ", ".join(hits) if hits
                               else "consistent in NO configuration at either epoch rule"))
    L.append("- The E9 wording allows two readings. Strict: a cell is matched only if all four Table 1 cells are "
             "consistent in one configuration at one epoch rule (first bullet), so either every cell is matched "
             "or none is. Per cell: a cell is matched if it is consistent in a configuration whose four cells are "
             "all read at the same epoch rule (the per-cell bullets). Configurations with n=2 seeds (R2, R4, R3 "
             "mlp_fullft) are read the same way as the 5-seed ones.")
    better: dict = defaultdict(int)
    for tag, probe, arm in sorted({(c["tag"], c["probe"], c["sa_arm"]) for c in cfgs}):
        b, la = (next(c for c in cfgs if (c["tag"], c["probe"], c["sa_arm"], c["when"]) == (tag, probe, arm, w))
                 for w in WHEN)
        key = (b["n_consistent"], -b["sum_distance"]), (la["n_consistent"], -la["sum_distance"])
        better["best" if key[0] > key[1] else "last" if key[1] > key[0] else "tie"] += 1
    nb = sum(c["n_consistent"] for c in cfgs if c["when"] == "test_at_best")
    nl = sum(c["n_consistent"] for c in cfgs if c["when"] == "test_last")
    L.append(f"- Which epoch rule fits better: summed over configurations, {nb} consistent cells at best vs "
             f"{nl} at last. Per configuration (more consistent cells, ties broken by the smaller sum of the four "
             f"distances; this tie-break is our operationalisation, not in E9): best fits better in "
             f"{better['best']}, last in {better['last']}, tie in {better['tie']} of {len(cfgs) // 2}.")

    L += ["", "## 3. P1E (fixed probe, paper split): bal / PR / ROC, 4 arms x 2 heads, mean ± SEM over 5 seeds",
          "", "For draft Table 2. Paper Table 1 (bal/PR/ROC): BIOT LP 50.74/1.53/46.93, SA 52.71/31.52/83.08; "
          "CBraMod LP 57.87/17.35/54.14, SA 61.37/24.62/83.67.", "",
          "| model | head | arm | n | bal (best) | PR trapz (best) | AP (best) | ROC (best) | bal (last) | "
          "PR trapz (last) | ROC (last) |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in p1e:
        L.append(f"| {r['model']} | {r['head']} | {r['arm']} | {r['n']} | " + " | ".join(
            fmt(r[f"{w}.{m}"]) for w, m in (("test_at_best", "bal_acc"), ("test_at_best", "pr_auc_trapz"),
                                           ("test_at_best", "avg_precision"), ("test_at_best", "roc_auc"),
                                           ("test_last", "bal_acc"), ("test_last", "pr_auc_trapz"),
                                           ("test_last", "roc_auc"))) + " |")

    L += ["", "## 4. AUCPR panel for the '20x AUCPR' claim (descriptive)", "",
          f"PR-AUC = trapezoidal (upstream's), val-selected epoch. Paper: prevalence {100 * PREV_PAPER:.3f}% "
          f"(252/16,964); BIOT LP 1.53 -> SA 31.52 (PR/prev {1.53 / (100 * PREV_PAPER):.2f} -> "
          f"{31.52 / (100 * PREV_PAPER):.1f}, SA/LP {31.52 / 1.53:.1f}x); CBraMod 17.35 -> 24.62 "
          f"(PR/prev {17.35 / (100 * PREV_PAPER):.1f} -> {24.62 / (100 * PREV_PAPER):.1f}, {24.62 / 17.35:.2f}x).",
          "Scorings on the paper split: upstream = all 16,964 test windows, upstream labels; dedup = grid windows",
          "only, upstream labels; fixed = grid windows only, overlap labels (true bounds). Probes were trained on",
          "upstream labels. Released path = wave 1 (train-mode probe; CBraMod reads proj_out). Corrected protocol",
          "= D24-A runs (S1M, plus CBraMod's S_r seed from S1E), rotation = replicate (3-seed mean), linear head.",
          "ratio vs lp = mean of the paired (seed or rotation) PR(arm)/PR(lp).", "",
          "| protocol | scoring | model | head | arm | n | prevalence % | PR-AUC | PR / prevalence "
          "| ratio vs lp |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for r in panel:
        L.append(f"| {r['protocol']} | {r['scoring']} | {r['model']} | {r['head']} | {r['arm']} | {r['n']} | "
                 f"{r['prevalence_pct']:.3f} | {fmt(r['pr'])} | {fmt(r['pr_over_prev'])} | "
                 f"{fmt(r['ratio_vs_lp'])} |")
    L += ["", "## Figures", ""] + [f"- {Path(f).relative_to(ROOT)}" for f in figs]
    L += ["", "## Not covered here", "",
          "- Released-code runs (E4-E7): column left 'pending'.",
          "- TUAB / TUEV: not tested (no TUH access).",
          "- D15 fixed-compute runs (C2-N*/C3-P*, C2E/C3E) are not in E9's candidate list and are not searched."]
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--local", default=str(ROOT / "artifacts" / "s3-results"))
    args = ap.parse_args()
    runs = load(Path(args.local))
    allrows, closest = coverage(runs)
    check(allrows)
    cfgs = configs(allrows)
    p1e = p1e_table(runs)
    panel = aucpr_panel(runs)
    OUT.mkdir(parents=True, exist_ok=True)
    figs = figures(allrows, panel)
    (OUT / "coverage.json").write_text(json.dumps({"closest": closest, "all_candidates": allrows,
                                                   "configs": cfgs, "p1e": p1e, "aucpr_panel": panel}, indent=1))
    text = write_md(allrows, closest, cfgs, p1e, panel, figs)
    (OUT / "coverage.md").write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
