#!/usr/bin/env python3
"""D25-E13 (a)-(d): free part of the protocol-fix decomposition. DESCRIPTIVE (rule of E13).

    .venv/bin/python scripts/analysis/decompose.py [--reps 10000]

Reads only local records (artifacts/s3-results/**/results/: *.json, *.<head>.npz, test-index-*.json)
and writes artifacts/analysis/decompose/{posthoc-paper,rotations-upstream-rule,probe-mode-pairs,
waterfall}.{md,json} plus figures (*.png). scripts/posthoc_test.py is not used or changed.

(a) Paper split, wave 1 (run tag "", released-code probe) and P1E (fixed probe): saved per-window
    test scores (val-selected epoch) re-scored four ways. upstream = all 16,964 windows, upstream
    labels (as trained and reported); dedup = grid windows, upstream labels; fixed = grid windows,
    overlap labels; dupov = all windows (duplicates kept), overlap labels.
(b) D24-A rotations (S1M + S1E, fixed probe): grid test windows re-labelled with the upstream rule
    (positive iff a seizure start or end index, seconds * 256 - 1, lies strictly inside the window).
(c) Probe-mode pairs at seed S_r: BIOT S1 (train mode) vs S1M (eval mode); CBraMod S1 (proj_out
    tap, train mode = released-code probe) vs S1E (encoder tap, eval mode).
(d) Waterfall (paper -> unreproduced residual -> released path -> init -> probe -> test scoring ->
    training labels + split) and Shapley values over the 2^3 factorial cells.

CIs (E11 design): 95% percentile intervals. Paper split (2 test subjects): stratified cluster
bootstrap; seizure events (every test window within 10 s of a seizure, touching events merged) and
the per-file interictal remainders are resampled with replacement within their stratum, then the
5 seeds. Rotations: test subjects resampled within each rotation and the pooled ROC recomputed,
then seeds within the rotation; the 5 rotations are kept. ROC under resampling is exact:
AUC = w'Uw / ((w.P)(w.N)), U the cluster-pair concordance matrix (ties count 1/2).
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from itertools import combinations, permutations
from math import factorial
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from sklearn.metrics import auc, precision_recall_curve, roc_auc_score  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from read_step1 import d17, paired  # noqa: E402

RES = ROOT / "artifacts" / "s3-results"
OUT = ROOT / "artifacts" / "analysis" / "decompose"
WIN = 10 * 256
SEIZ = json.loads((ROOT / "configs" / "chbmit_seizures.json").read_text())   # true [on, off), 256 Hz
PAPER_SEEDS = (42, 123, 2021, 3407, 8888)
ROTS = tuple(f"rot{i}" for i in range(5))
ROT_SEEDS = {r: (PAPER_SEEDS[i], 1000 + i, 2000 + i) for i, r in enumerate(ROTS)}
D24_ARMS = ("lp", "lp_randinit", "last", "last_randinit", "all")
HEADS = ("linear", "mlp_fullft")
# scoring -> (window mask, label rule)
PAPER_SCORINGS = {"upstream": ("all", "up"), "dedup": ("grid", "up"), "fixed": ("grid", "ov"),
                  "dupov": ("all", "ov")}
ROT_SCORINGS = {"overlap": ("all", "ov"), "upstream_rule": ("all", "up")}   # rotation test = grid only
PAPER = {"biot": {"lp": 46.93, "sa": 83.08, "lp_sem": 0.30, "sa_sem": 1.89},     # Table 1, ROC, SEM
         "cbramod": {"lp": 54.14, "sa": 83.67, "lp_sem": 1.39, "sa_sem": 1.36}}
INK, INK2, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#fcfcfb"
ARM_COLOR = {"lp": "#2a78d6", "last": "#eb6834", "last_randinit": "#1baf7a", "lp_randinit": "#eda100",
             "all": "#e87ba4"}
UP, DOWN, TOTAL = "#2a78d6", "#e34948", "#52514e"


# ---------------------------------------------------------------- test sets, labels, clusters
class TestSet:
    def __init__(self, path: Path, split: str):
        idx = json.loads(path.read_text())
        parts = [t["key"].rsplit("-", 2) for t in idx]
        self.name, self.split, self.n = path.name, split, len(idx)
        self.file = np.array([p[0] for p in parts])
        self.grid = np.array([p[1] == "grid" for p in parts])
        self.start = np.array([int(p[2]) for p in parts])
        self.subject = np.array([t["subject"] for t in idx])
        self.up, self.ov = window_labels(self.file, self.start, self.grid)
        if split == "paper":
            self.cluster, self.strata = event_clusters(self.file, self.start)
        else:
            subs = sorted(set(self.subject))
            self.cluster = np.array([subs.index(s) for s in self.subject])
            self.strata = [list(range(len(subs)))]
        self.K = int(self.cluster.max()) + 1
        self.W = None

    def mask(self, which: str) -> np.ndarray:
        return self.grid if which == "grid" else np.ones(self.n, bool)


def window_labels(file: np.ndarray, start: np.ndarray, grid: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Upstream rule (grid: a seizure start/end index, seconds*256 - 1, strictly inside; duplicate
    windows: 1) and overlap rule (any overlap of [start, start + 10 s) with a true seizure)."""
    up = np.zeros(len(file), np.int8)
    ov = np.zeros(len(file), np.int8)
    for f in np.unique(file):
        m = file == f
        s = start[m]
        for on, off in SEIZ.get(f, []):
            ov[m] |= ((s < off) & (s + WIN > on)).astype(np.int8)
            a, b = on - 1, off - 1
            up[m] |= (((s < a) & (a < s + WIN)) | ((s < b) & (b < s + WIN))).astype(np.int8)
    up[~grid] = 1
    return up, ov


def event_clusters(file: np.ndarray, start: np.ndarray) -> tuple[np.ndarray, list[list[int]]]:
    """Event cluster = all windows overlapping [onset - 10 s, offset + 10 s) of a seizure (touching
    neighbourhoods merged); every other window goes to its file's interictal cluster."""
    cl = np.full(len(file), -1)
    k = 0
    for f in sorted(set(file)):
        hoods = []
        for on, off in sorted(SEIZ.get(f, [])):
            lo, hi = on - WIN, off + WIN
            if hoods and lo <= hoods[-1][1]:
                hoods[-1][1] = max(hoods[-1][1], hi)
            else:
                hoods.append([lo, hi])
        m = file == f
        for lo, hi in hoods:
            hit = m & (start < hi) & (start + WIN > lo)
            cl[hit] = k
            k += 1
    events = list(range(k))
    for f in sorted(set(file)):
        rest = (file == f) & (cl < 0)
        if rest.any():
            cl[rest] = k
            k += 1
    return cl, [events, list(range(len(events), k))]


def draw_weights(ts: TestSet, R: int, rng: np.random.Generator) -> np.ndarray:
    W = np.zeros((R, ts.K))
    for ids in ts.strata:
        ids = np.asarray(ids)
        d = ids[rng.integers(0, len(ids), (R, len(ids)))]
        np.add.at(W, (np.repeat(np.arange(R), len(ids)), d.ravel()), 1.0)
    return W


def pair_stats(s: np.ndarray, y: np.ndarray, c: np.ndarray, K: int):
    pos = y == 1
    sp, cp = s[pos], c[pos]
    U = np.zeros((K, K))
    for b in range(K):
        nb = np.sort(s[~pos & (c == b)])
        if len(nb):
            lo, hi = np.searchsorted(nb, sp, "left"), np.searchsorted(nb, sp, "right")
            U[:, b] = np.bincount(cp, weights=lo + 0.5 * (hi - lo), minlength=K)
    return U, np.bincount(cp, minlength=K).astype(float), np.bincount(c[~pos], minlength=K).astype(float)


def auc_w(U: np.ndarray, P: np.ndarray, N: np.ndarray, W: np.ndarray) -> np.ndarray:
    with np.errstate(invalid="ignore", divide="ignore"):
        return ((W @ U) * W).sum(1) / ((W @ P) * (W @ N))


def pr_trapz(y: np.ndarray, s: np.ndarray) -> float:
    p, r, _ = precision_recall_curve(y, s)
    return float(auc(r, p))


# ---------------------------------------------------------------- runs
@dataclass
class Run:
    rec: dict
    head: str
    ts: TestSet
    scores: np.ndarray
    point: dict = field(default_factory=dict)   # scoring -> (roc, pr)
    _reps: dict = field(default_factory=dict)

    def score(self, scoring: str) -> tuple[float, float]:
        if scoring not in self.point:
            m, lab = (PAPER_SCORINGS | ROT_SCORINGS)[scoring]
            mk = self.ts.mask(m)
            y = (self.ts.up if lab == "up" else self.ts.ov)[mk]
            self.point[scoring] = (100 * roc_auc_score(y, self.scores[mk]), 100 * pr_trapz(y, self.scores[mk]))
        return self.point[scoring]

    def reps(self, scoring: str) -> np.ndarray:
        if scoring not in self._reps:
            m, lab = (PAPER_SCORINGS | ROT_SCORINGS)[scoring]
            mk = self.ts.mask(m)
            y = (self.ts.up if lab == "up" else self.ts.ov)[mk]
            U, P, N = pair_stats(self.scores[mk], y, self.ts.cluster[mk], self.ts.K)
            exact = U.sum() / (P.sum() * N.sum())
            assert abs(100 * exact - self.score(scoring)[0]) < 1e-6, (self.rec["key"], scoring)
            self._reps[scoring] = 100 * auc_w(U, P, N, self.ts.W)
        return self._reps[scoring]


def load_runs(R: int, rng: np.random.Generator) -> dict:
    """(source, model, arm, head, split) -> {seed: Run}. Sources: W1 (wave 1), P1E, S1, S1M, S1E and
    D24A = S1M + S1E restricted to the D24 arms."""
    tests: dict[str, TestSet] = {}
    out: dict = {}
    want = {"": "W1", "P1E": "P1E", "S1": "S1", "S1M": "S1M", "S1E": "S1E"}
    for p in sorted(RES.rglob("results/*.json")):
        if p.name.startswith(("diag-", "test-index-", "val-index-", "report-")):
            continue
        r = json.loads(p.read_text())
        src = want.get(r.get("run_tag", ""))
        if r.get("smoke") or r["dataset"] != "chbmit" or src is None:
            continue
        if src == "W1" and not (r["split"] == "paper" and r["arm"] in ("lp", "last", "last_randinit")
                                and p.parent.parent.name.startswith("arms-")):
            continue
        ts = tests.get(r["split"])
        if ts is None:
            ts = tests[r["split"]] = TestSet(p.parent / r["test_index"], r["split"])
        if ts.name != r["test_index"]:
            raise SystemExit(f"{p.name}: test set {r['test_index']} != {ts.name} for {r['split']}")
        for head in r["probes"]:
            a = np.load(p.parent / f"{r['key']}.{head}.npz")
            y, s = a["y_test"].astype(np.int8), a["scores_best"].astype(np.float64)
            as_run = ts.up if r.get("labels", "upstream") in (None, "upstream") else ts.ov
            if len(y) != ts.n or not np.array_equal(y, as_run):
                raise SystemExit(f"{p.name}: saved labels differ from the recomputed {r.get('labels')} rule")
            run = Run(r, head, ts, s)
            got = run.score("upstream" if r["split"] == "paper" else "overlap")[0]
            if abs(got - 100 * r["probes"][head]["test_at_best"]["roc_auc"]) > 1e-6:
                raise SystemExit(f"{p.name}: npz ROC {got} != record")
            for s_ in ([src, "D24A"] if src in ("S1M", "S1E") and r["arm"] in D24_ARMS else [src]):
                cell = out.setdefault((s_, r["model"], r["arm"], head, r["split"]), {})
                if r["seed"] in cell:
                    raise SystemExit(f"two records for {(s_, r['model'], r['arm'], head, r['split'])} "
                                     f"seed {r['seed']}")
                cell[r["seed"]] = run
    for ts in tests.values():
        ts.W = draw_weights(ts, R, rng)
    return out, tests


# ---------------------------------------------------------------- cells
@dataclass
class Cell:
    point: float
    reps: np.ndarray
    parts: np.ndarray   # per seed (paper split) or per rotation (rotations)

    def __sub__(self, o: Cell) -> Cell:
        return Cell(self.point - o.point, self.reps - o.reps, self.parts - o.parts)

    def ci(self) -> tuple[float, float]:
        lo, hi = np.nanquantile(self.reps, [0.025, 0.975])
        return float(lo), float(hi)

    def sem(self) -> float:
        return float(self.parts.std(ddof=1) / np.sqrt(len(self.parts))) if len(self.parts) > 1 else float("nan")

    def fmt(self, signed: bool = False) -> str:
        lo, hi = self.ci()
        f = "+.1f" if signed else ".1f"
        return f"{self.point:{f}} ± {self.sem():.1f} [{lo:{f}}, {hi:{f}}]"

    def js(self) -> dict:
        lo, hi = self.ci()
        return {"point": self.point, "sem": self.sem(), "ci95": [lo, hi], "parts": self.parts.tolist()}


class Cells:
    def __init__(self, runs: dict, R: int, rng: np.random.Generator):
        self.runs, self.R = runs, R
        self.idx_paper = rng.integers(0, 5, (R, 5))
        self.idx_rot = {r: rng.integers(0, 3, (R, 3)) for r in ROTS}

    def _seedmean(self, by_seed: dict, seeds, idx, scoring: str) -> tuple[np.ndarray, np.ndarray]:
        missing = [s for s in seeds if s not in by_seed]
        if missing:
            raise KeyError(f"missing seeds {missing}")
        pts = np.array([by_seed[s].score(scoring)[0] for s in seeds])
        A = np.stack([by_seed[s].reps(scoring) for s in seeds])
        reps = A[0] if len(seeds) == 1 else np.take_along_axis(A, idx.T, axis=0).mean(0)
        return pts, reps

    def paper(self, src: str, model: str, arm: str, head: str, scoring: str) -> Cell:
        pts, reps = self._seedmean(self.runs[(src, model, arm, head, "paper")], PAPER_SEEDS,
                                   self.idx_paper, scoring)
        return Cell(float(pts.mean()), reps, pts)

    def rot(self, src: str, model: str, arm: str, scoring: str, seeds: str = "all") -> Cell:
        means, reps = [], []
        for r in ROTS:
            seeds_r = ROT_SEEDS[r] if src == "D24A" and seeds == "all" else ROT_SEEDS[r][:1]
            pts, rp = self._seedmean(self.runs[(src, model, arm, "linear", r)], seeds_r,
                                     self.idx_rot[r], scoring)
            means.append(pts.mean())
            reps.append(rp)
        return Cell(float(np.mean(means)), np.mean(reps, axis=0), np.array(means))

    def has(self, *key) -> bool:
        return key in self.runs


# ---------------------------------------------------------------- figures
def style(ax, title: str = "", ylabel: str = "") -> None:
    ax.set_facecolor(SURF)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    for k in ("top", "right"):
        ax.spines[k].set_visible(False)
    for k in ("left", "bottom"):
        ax.spines[k].set_color("#c3c2b7")
    ax.tick_params(colors=INK2, labelsize=8)
    if title:
        ax.set_title(title, fontsize=9, color=INK, loc="left")
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=8, color=INK2)


def errbar(ax, x, c: Cell, color: str, **kw) -> None:
    lo, hi = c.ci()
    ax.errorbar([x], [c.point], yerr=[[c.point - lo], [hi - c.point]], fmt="o", ms=5, color=color,
                ecolor=color, elinewidth=1.2, capsize=2, **kw)


# ---------------------------------------------------------------- (a)
def part_a(C: Cells, md: list, js: dict) -> None:
    md += ["## (a) Paper split re-scored four ways (val-selected epoch; ROC x100 mean ± SEM over 5 seeds "
           "[95% event-cluster + seed bootstrap CI]; PR-AUC trapezoid mean ± SEM)", "",
           "Probes were TRAINED on upstream labels (duplicates in train) in every row; only the test "
           "scoring changes. W1 = wave 1, released-code probe (train mode; CBraMod reads proj_out); "
           "P1E = fixed probe (eval mode, encoder output).", ""]
    ts = C.runs[("P1E", "biot", "lp", "linear", "paper")][42].ts
    counts = {k: (int((ts.up if lab == "up" else ts.ov)[ts.mask(m)].sum()), int(ts.mask(m).sum()))
              for k, (m, lab) in PAPER_SCORINGS.items()}
    md.append("positives / windows: " + ", ".join(f"{k} {p}/{n}" for k, (p, n) in counts.items())
              + f"; clusters: {len(ts.strata[0])} seizure events, {len(ts.strata[1])} interictal file blocks")
    md.append("")
    js["counts"] = counts
    md += ["| source | model | head | arm | " + " | ".join(f"ROC {k} | PR {k}" for k in PAPER_SCORINGS) + " |",
           "|---|---|---|---|" + "---|---|" * len(PAPER_SCORINGS)]
    rows = js.setdefault("cells", {})
    for src in ("W1", "P1E"):
        for model in ("biot", "cbramod"):
            for head in HEADS:
                for arm in ("lp", "last", "last_randinit", "lp_randinit"):
                    if not C.has(src, model, arm, head, "paper"):
                        continue
                    cells = {k: C.paper(src, model, arm, head, k) for k in PAPER_SCORINGS}
                    by_seed = C.runs[(src, model, arm, head, "paper")]
                    prs = {k: np.array([by_seed[s].score(k)[1] for s in PAPER_SEEDS]) for k in PAPER_SCORINGS}
                    md.append(f"| {src} | {model} | {head} | {arm} | " + " | ".join(
                        f"{cells[k].fmt()} | {prs[k].mean():.1f} ± {prs[k].std(ddof=1) / np.sqrt(5):.1f}"
                        for k in PAPER_SCORINGS) + " |")
                    rows[f"{src}/{model}/{head}/{arm}"] = {
                        k: {"roc": cells[k].js(), "pr_mean": float(prs[k].mean()), "pr_per_seed": prs[k].tolist()}
                        for k in PAPER_SCORINGS}
    md += ["", "### Contrasts per scoring (paired by seed; mean ± SEM [CI]; D24-B rule string, read "
           "descriptively here)", "",
           "| source | model | head | contrast | " + " | ".join(PAPER_SCORINGS) + " |",
           "|---|---|---|---|" + "---|" * len(PAPER_SCORINGS)]
    for src in ("W1", "P1E"):
        for model in ("biot", "cbramod"):
            for head in HEADS:
                for a, b in (("last", "lp"), ("last_randinit", "last"), ("lp", "lp_randinit"),
                             ("last_randinit", "lp_randinit")):
                    if not (C.has(src, model, a, head, "paper") and C.has(src, model, b, head, "paper")):
                        continue
                    ds = {k: C.paper(src, model, a, head, k) - C.paper(src, model, b, head, k)
                          for k in PAPER_SCORINGS}
                    md.append(f"| {src} | {model} | {head} | {a} - {b} | " + " | ".join(
                        f"{d.fmt(True)} {paired(list(d.parts))}" for d in ds.values()) + " |")
                    js.setdefault("contrasts", {})[f"{src}/{model}/{head}/{a}-{b}"] = {
                        k: {**d.js(), "rule": paired(list(d.parts))} for k, d in ds.items()}
    md.append("")
    # figure: ROC per arm across the four scorings
    fig, axes = plt.subplots(2, 4, figsize=(13, 6), sharey=True, facecolor=SURF)
    xs = np.arange(len(PAPER_SCORINGS))
    for i, model in enumerate(("biot", "cbramod")):
        for j, (src, head) in enumerate([(s, h) for s in ("W1", "P1E") for h in HEADS]):
            ax = axes[i, j]
            style(ax, f"{model} {src} {head}", "ROC-AUC x100" if j == 0 else "")
            for k, arm in enumerate(("lp", "last", "last_randinit", "lp_randinit")):
                if not C.has(src, model, arm, head, "paper"):
                    continue
                cs = [C.paper(src, model, arm, head, sc) for sc in PAPER_SCORINGS]
                off = (k - 1.5) * 0.08
                ax.plot(xs + off, [c.point for c in cs], color=ARM_COLOR[arm], lw=1.2, label=arm)
                for x, c in zip(xs + off, cs, strict=True):
                    errbar(ax, x, c, ARM_COLOR[arm])
            ax.set_xticks(xs, list(PAPER_SCORINGS), fontsize=8)
            ax.axhline(50, color=MUTED, lw=0.8, ls=":")
    axes[0, 0].legend(fontsize=7, frameon=False, loc="lower left")
    fig.suptitle("E13(a) paper split re-scored: upstream (as reported), dedup, fixed, duplicates kept + "
                 "overlap labels (95% CI)", fontsize=10, color=INK, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(OUT / "posthoc-paper.png", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------- (b)
def part_b(C: Cells, md: list, js: dict) -> None:
    md += ["## (b) D24-A rotations (S1M + S1E, fixed probe): grid test windows under the overlap labels "
           "(as run) vs the upstream start/end rule", "",
           "Per rotation: mean over its 3 seeds. ROC x100; mean ± SEM over 5 rotations [95% CI: test "
           "subjects within rotation, then seeds]. Rule strings use the D18/D24 paired rule and D17, "
           "applied descriptively. The probe was trained on overlap labels in both columns.", ""]
    ts = {r: C.runs[("D24A", "biot", "lp", "linear", r)][ROT_SEEDS[r][0]].ts for r in ROTS}
    md.append("test positives (overlap / upstream rule) / windows: " + ", ".join(
        f"{r} {int(ts[r].ov.sum())}/{int(ts[r].up.sum())}/{ts[r].n}" for r in ROTS))
    js["counts"] = {r: {"overlap": int(ts[r].ov.sum()), "upstream_rule": int(ts[r].up.sum()), "n": ts[r].n}
                    for r in ROTS}
    md += ["", "| model | arm | overlap: per rotation | overlap | upstream rule: per rotation | upstream rule |",
           "|---|---|---|---|---|---|"]
    for model in ("biot", "cbramod"):
        for arm in D24_ARMS:
            cs = {k: C.rot("D24A", model, arm, k) for k in ROT_SCORINGS}
            md.append(f"| {model} | {arm} | " + " | ".join(
                f"{', '.join(f'{x:.1f}' for x in c.parts)} | {c.fmt()}" for c in cs.values()) + " |")
            js.setdefault("arms", {})[f"{model}/{arm}"] = {k: c.js() for k, c in cs.items()}
    md += ["", "| model | contrast | overlap (per rotation; mean ± SEM [CI]) -> rule | upstream rule -> rule "
           "| upstream - overlap [CI] |", "|---|---|---|---|---|"]
    fig, axes = plt.subplots(2, 4, figsize=(13, 6), facecolor=SURF)
    for i, model in enumerate(("biot", "cbramod")):
        for j, (a, b) in enumerate((("last", "lp"), ("last_randinit", "last"), ("lp", "lp_randinit"),
                                    ("last_randinit", "lp_randinit"))):
            ds, rules = {}, {}
            for k in ROT_SCORINGS:
                A, B = C.rot("D24A", model, a, k), C.rot("D24A", model, b, k)
                ds[k] = A - B
                rules[k] = d17(A.parts, B.parts) if j == 3 else paired(list(ds[k].parts))
            shift = ds["upstream_rule"] - ds["overlap"]
            name = f"{a} - {b}" + (" (D17)" if j == 3 else "")
            md.append(f"| {model} | {name} | " + " | ".join(
                f"{', '.join(f'{x:+.1f}' for x in d.parts)}; {d.fmt(True)} -> **{rules[k]}**"
                for k, d in ds.items()) + f" | {shift.fmt(True)} |")
            js.setdefault("contrasts", {})[f"{model}/{a}-{b}"] = {
                **{k: {**d.js(), "rule": rules[k]} for k, d in ds.items()}, "upstream_minus_overlap": shift.js()}
            ax = axes[i, j]
            style(ax, f"{model}: {name}", "difference, ROC x100" if j == 0 else "")
            for r in range(5):
                ax.plot([0, 1], [ds["overlap"].parts[r], ds["upstream_rule"].parts[r]], color=GRID, lw=1)
                ax.scatter([0, 1], [ds["overlap"].parts[r], ds["upstream_rule"].parts[r]], s=14, color=MUTED,
                           zorder=3)
            for x, k in enumerate(ROT_SCORINGS):
                errbar(ax, x + 0.12, ds[k], INK)
            ax.axhline(0, color="#c3c2b7", lw=0.8)
            for h in (3, -3):
                ax.axhline(h, color=MUTED, lw=0.6, ls=":")
            ax.set_xticks([0, 1], ["overlap\n(as run)", "upstream\nrule"], fontsize=8)
            ax.set_xlim(-0.4, 1.5)
    fig.suptitle("E13(b) D24-A contrasts per rotation (grey) and mean with 95% CI (black); dotted = ±3 rule "
                 "threshold", fontsize=10, color=INK, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(OUT / "rotations-upstream-rule.png", dpi=150)
    plt.close(fig)
    md.append("")


# ---------------------------------------------------------------- (c)
def part_c(C: Cells, md: list, js: dict) -> None:
    md += ["## (c) Probe-mode pairs at seed S_r (1 seed per rotation; CHB-MIT rotations, overlap labels)", "",
           "released = S1 (backbone in train mode; CBraMod also reads proj_out). fixed = BIOT S1M / CBraMod "
           "S1E at seed S_r (eval mode, encoder output). BIOT pairs isolate the backbone mode; CBraMod pairs "
           "change tap and mode together. ROC x100; mean ± SEM over rotations [95% CI: test subjects within "
           "rotation]. Rules: D18 paired rule at 1 seed, descriptive.", "",
           "| model | arm | released per rotation | released | fixed per rotation | fixed | fixed - released |",
           "|---|---|---|---|---|---|---|"]
    fixed_src = {"biot": "S1M", "cbramod": "S1E"}
    fig, axes = plt.subplots(2, 2, figsize=(13, 6.5), facecolor=SURF, gridspec_kw={"width_ratios": [3, 2]})
    for i, model in enumerate(("biot", "cbramod")):
        arms = [a for a in ("lp", "last", "last_randinit", "lp_randinit", "all", "first", "first_block",
                            "embed_only", "first_noise")
                if all(C.has(s, model, a, "linear", r) for s in ("S1", fixed_src[model]) for r in ROTS)]
        cells = {a: (C.rot("S1", model, a, "overlap", "first"),
                     C.rot(fixed_src[model], model, a, "overlap", "first")) for a in arms}
        ax = axes[i, 0]
        style(ax, f"{model}: fixed - released probe, per arm (grey = rotation)", "ROC x100")
        for x, a in enumerate(arms):
            rel, fix = cells[a]
            d = fix - rel
            md.append(f"| {model} | {a} | {', '.join(f'{v:.1f}' for v in rel.parts)} | {rel.fmt()} | "
                      f"{', '.join(f'{v:.1f}' for v in fix.parts)} | {fix.fmt()} | {d.fmt(True)} |")
            js.setdefault("arms", {})[f"{model}/{a}"] = {"released": rel.js(), "fixed": fix.js(),
                                                         "fixed_minus_released": d.js()}
            ax.scatter([x] * 5, d.parts, s=12, color=MUTED, zorder=3)
            errbar(ax, x + 0.15, d, ARM_COLOR.get(a, INK))
        ax.set_xticks(range(len(arms)), arms, fontsize=7, rotation=20)
        ax.axhline(0, color="#c3c2b7", lw=0.8)
        ax = axes[i, 1]
        style(ax, f"{model}: contrasts under each probe", "difference, ROC x100")
        for j, (a, b) in enumerate((("last", "lp"), ("last_randinit", "last"), ("lp", "lp_randinit"),
                                    ("last_randinit", "lp_randinit"))):
            for k, (lab, col) in enumerate((("released", "#eb6834"), ("fixed", "#2a78d6"))):
                A, B = cells[a][k], cells[b][k]
                d = A - B
                rule = d17(A.parts, B.parts) if j == 3 else paired(list(d.parts))
                js.setdefault("contrasts", {}).setdefault(f"{model}/{a}-{b}", {})[lab] = {**d.js(), "rule": rule}
                errbar(ax, j + (k - 0.5) * 0.3, d, col, label=lab if j == 0 else None)
            ax.set_xticks(range(4), ["last-lp", "last_r-last", "lp-lp_r", "last_r-lp_r"], fontsize=7)
        ax.axhline(0, color="#c3c2b7", lw=0.8)
        for h in (3, -3):
            ax.axhline(h, color=MUTED, lw=0.6, ls=":")
        ax.legend(fontsize=7, frameon=False)
    md += ["", "| model | contrast | released: per rotation; mean ± SEM [CI] -> rule | fixed -> rule |",
           "|---|---|---|---|"]
    for key, v in js["contrasts"].items():
        model, name = key.split("/")
        md.append(f"| {model} | {name}{' (D17)' if name == 'last_randinit-lp_randinit' else ''} | " + " | ".join(
            f"{', '.join(f'{x:+.1f}' for x in v[k]['parts'])}; {v[k]['point']:+.1f} ± {v[k]['sem']:.1f} "
            f"[{v[k]['ci95'][0]:+.1f}, {v[k]['ci95'][1]:+.1f}] -> **{v[k]['rule']}**"
            for k in ("released", "fixed")) + " |")
    fig.suptitle("E13(c) probe-mode pairs at seed S_r (95% CI over test subjects within rotation)", fontsize=10,
                 color=INK, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(OUT / "probe-mode-pairs.png", dpi=150)
    plt.close(fig)
    md.append("")


# ---------------------------------------------------------------- (d)
def shapley(v: dict, factors: tuple[str, ...]) -> dict:
    n = len(factors)
    out = {}
    for f in factors:
        others = [g for g in factors if g != f]
        out[f] = sum(factorial(k) * factorial(n - k - 1) / factorial(n) * (v[frozenset(S) | {f}] - v[frozenset(S)])
                     for k in range(n) for S in combinations(others, k))
    return out


def part_d(C: Cells, md: list, js: dict) -> None:
    def value(model: str, head: str, arm: str, probe: str, proto: str) -> Cell:
        if proto in ("paper", "paper_fixed"):
            return C.paper("W1" if probe == "released" else "P1E", model, arm, head,
                           "upstream" if proto == "paper" else "fixed")
        return C.rot("S1" if probe == "released" else "D24A", model, arm, "overlap")

    def target(model, head, kind, init, probe, proto) -> Cell:
        arm = "last_randinit" if init == "random" else "last"
        v = value(model, head, arm, probe, proto)
        return v - value(model, head, "lp", probe, proto) if kind == "gain" else v

    md += ["## (d) Waterfall and Shapley decomposition (descriptive; re-run after E17 and E18)", "",
           "Target: SA level = ROC of the paper's SA arm; SA gain = SA arm - lp under the same probe and "
           "protocol. Factors switched from the released configuration to the fix: init (random = released "
           "path, `last_randinit` -> pretrained `last`); probe (W1/S1 released-code probe -> P1E/D24-A fixed "
           "probe); protocol (paper split, upstream labels and scoring -> corrected rotations, D24-A seeds; S1 "
           "has seed S_r only). 'scoring' = the post hoc test-scoring fix alone on the paper split (upstream -> "
           "fixed, P1E/W1 re-scored), the only protocol step that exists for the MLP head. Paper values: "
           "Table 1 ROC (mean ± SEM, 5 seeds). Unreproduced residual = paper - our released-path cell. "
           "ROC x100; [95% CI] from the E11 resampling (paper split: events/files then seeds; rotations: "
           "subjects then seeds), all cells resampled jointly.", ""]
    decomps = {"init x probe x protocol": ("init", "probe", "protocol"),
               "init x probe x scoring": ("init", "probe", "scoring")}
    fig_rows = []
    for head in HEADS:
        for model in ("biot", "cbramod"):
            for kind in ("level", "gain"):
                pv = PAPER[model]
                paper_val = pv["sa"] if kind == "level" else pv["sa"] - pv["lp"]
                paper_sem = pv["sa_sem"] if kind == "level" else float(np.hypot(pv["sa_sem"], pv["lp_sem"]))
                steps = [("released path", ("random", "released", "paper")),
                         ("+ init (pretrained)", ("pretrained", "released", "paper")),
                         ("+ probe (fixed)", ("pretrained", "fixed", "paper")),
                         ("+ test scoring (post hoc)", ("pretrained", "fixed", "paper_fixed"))]
                if head == "linear":
                    steps.append(("+ train labels & split", ("pretrained", "fixed", "corrected")))
                vals = [target(model, head, kind, *s) for _, s in steps]
                key = f"{model}/{head}/{kind}"
                res = js.setdefault(key, {})
                resid = Cell(paper_val - vals[0].point, paper_val - vals[0].reps, np.array([np.nan]))
                res["paper"] = {"value": paper_val, "sem_approx": paper_sem}
                res["residual"] = resid.js()
                res["steps"] = [{"step": n, "value": v.js(), **({"delta": (v - vals[i - 1]).js()} if i else {})}
                                for i, ((n, _), v) in enumerate(zip(steps, vals, strict=True))]
                md += [f"### {model}, {head} head, SA {kind}", "",
                       f"- paper: {paper_val:.2f} (± {paper_sem:.2f}"
                       f"{' approx., unpaired' if kind == 'gain' else ''})",
                       f"- unreproduced residual (paper - released path): {resid.point:+.1f} "
                       f"[{resid.ci()[0]:+.1f}, {resid.ci()[1]:+.1f}]"]
                for i, ((n, _), v) in enumerate(zip(steps, vals, strict=True)):
                    md.append(f"- {n}: {v.fmt(kind == 'gain')}"
                              + (f"; step {(v - vals[i - 1]).fmt(True)}" if i else ""))
                if head == "mlp_fullft":
                    md.append("- corrected protocol: not run with the MLP head (E25 adds it)")
                for dname, factors in decomps.items():
                    if "protocol" in factors and head != "linear":
                        continue
                    lv = {"init": ("random", "pretrained"), "probe": ("released", "fixed"),
                          "protocol": ("paper", "corrected"), "scoring": ("paper", "paper_fixed")}
                    cells = {}
                    for k in range(4):
                        for S in combinations(factors, k):
                            cfg = {f: lv[f][f in S] for f in factors}
                            proto = cfg.pop("protocol", None) or cfg.pop("scoring")
                            cells[frozenset(S)] = target(model, head, kind, cfg["init"], cfg["probe"], proto)
                    phi_p = shapley({k: c.point for k, c in cells.items()}, factors)
                    phi_r = shapley({k: c.reps for k, c in cells.items()}, factors)
                    total = cells[frozenset(factors)].point - cells[frozenset()].point
                    assert abs(sum(phi_p.values()) - total) < 1e-9
                    orders = {" > ".join(o): [cells[frozenset(o[:i + 1])].point - cells[frozenset(o[:i])].point
                                              for i in range(3)] for o in permutations(factors)}
                    res.setdefault("shapley", {})[dname] = {
                        "cells": {"+".join(sorted(k)) or "released": c.js() for k, c in cells.items()},
                        "phi": {f: {"point": phi_p[f],
                                    "ci95": [float(q) for q in np.nanquantile(phi_r[f], [.025, .975])]}
                                for f in factors},
                        "orders": orders}
                    md.append(f"- Shapley over {dname} (8 cells; total {total:+.1f}): " + ", ".join(
                        f"{f} {phi_p[f]:+.1f} [{np.nanquantile(phi_r[f], .025):+.1f}, "
                        f"{np.nanquantile(phi_r[f], .975):+.1f}]" for f in factors))
                    md.append("  - cells: " + "; ".join(
                        f"{'+'.join(sorted(k)) or 'released'} {c.point:.1f}"
                        for k, c in sorted(cells.items(), key=lambda t: len(t[0]))))
                    md.append("  - sequential steps by order: " + "; ".join(
                        f"{o}: {', '.join(f'{x:+.1f}' for x in v)}" for o, v in orders.items()))
                md.append("")
                fig_rows.append((model, head, kind, paper_val, paper_sem, resid, steps, vals))
    # waterfall figures, one per head
    for head in HEADS:
        rows = [r for r in fig_rows if r[1] == head]
        fig, axes = plt.subplots(2, 2, figsize=(13, 7.5), facecolor=SURF)
        for ax, (model, _, kind, pval, psem, resid, steps, vals) in zip(axes.ravel(), rows, strict=True):
            style(ax, f"{model}, {head} head: SA {kind}",
                  "ROC-AUC x100" if kind == "level" else "SA - LP, ROC x100")
            # (label, bottom, height, colour, hatched, error-bar centre, CI low, CI high, text)
            lo, hi = resid.ci()
            bars = [("paper", 0, pval, TOTAL, False, pval, pval - psem, pval + psem, f"{pval:.1f}"),
                    ("unreproduced\nresidual", pval, -resid.point, SURF, True, vals[0].point, pval - hi, pval - lo,
                     f"{resid.point:+.1f}"),
                    ("released\npath (ours)", 0, vals[0].point, TOTAL, False, vals[0].point, vals[0].point,
                     vals[0].point, f"{vals[0].point:.1f}")]
            for i in range(1, len(vals)):
                d = vals[i] - vals[i - 1]
                lo, hi = d.ci()
                bars.append((steps[i][0].replace("+ ", "").replace(" (", "\n(").replace(" & ", "\n& "),
                             vals[i - 1].point, d.point, UP if d.point >= 0 else DOWN, False, vals[i].point,
                             vals[i - 1].point + lo, vals[i - 1].point + hi, f"{d.point:+.1f}"))
            fin = vals[-1]
            lo, hi = fin.ci()
            bars.append(("corrected\n(ours)" if head == "linear" else "paper split,\nfixed scoring", 0, fin.point,
                         TOTAL, False, fin.point, lo, hi, f"{fin.point:.1f}"))
            top = max(max(b[1], b[1] + b[2], b[7]) for b in bars)
            bot = min(min(b[1], b[1] + b[2], b[6]) for b in bars + [("", 0, 0, "", False, 0, 0, 0, "")])
            pad = 0.03 * (top - bot)
            for x, (_, b0, h, col, hatch, c, elo, ehi, txt) in enumerate(bars):
                ax.bar(x, h, bottom=b0, color=col, width=0.6, edgecolor=MUTED if hatch else col,
                       hatch="///" if hatch else None, lw=0.8 if hatch else 0)
                if ehi > elo:
                    ax.errorbar([x], [c], yerr=[[c - elo], [ehi - c]], color=INK, capsize=2, lw=1)
                ax.text(x, max(b0, b0 + h, ehi) + pad, txt, ha="center", fontsize=7, color=INK2)
            ax.set_ylim(bot - pad, top + 4 * pad)
            ax.set_xticks(range(len(bars)), [b[0] for b in bars], fontsize=6.5)
            ax.axhline(0, color="#c3c2b7", lw=0.8)
        fig.suptitle(f"E13(d) waterfall, {head} head: paper -> residual -> released path -> fixes in the paper's "
                     "order (blue up, red down; 95% CI)", fontsize=10, color=INK, x=0.01, ha="left")
        fig.tight_layout()
        fig.savefig(OUT / f"waterfall-{head}.png", dpi=150)
        plt.close(fig)
    # Shapley figure
    entries = [(k, d, v) for k, r in js.items() if isinstance(r, dict) and "shapley" in r
               for d, v in r["shapley"].items()]
    fig, ax = plt.subplots(figsize=(11, 0.32 * len(entries) * 3 + 1.5), facecolor=SURF)
    style(ax, "E13(d) Shapley values (order-free share of the released -> fixed change; 95% CI)",
          "")
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.grid(axis="y", visible=False)
    fcol = {"init": "#2a78d6", "probe": "#eb6834", "protocol": "#1baf7a", "scoring": "#eda100"}
    pos, labs, y = [], [], 0.0
    for key, dname, v in entries:
        for f, phi in v["phi"].items():
            ax.barh(y, phi["point"], color=fcol[f], height=0.7)
            lo, hi = phi["ci95"]
            ax.errorbar([phi["point"]], [y], xerr=[[phi["point"] - lo], [hi - phi["point"]]], color=INK,
                        capsize=2, lw=1)
            ax.text(max(hi, 0) + 0.5, y, f"{phi['point']:+.1f}", va="center", fontsize=6.5, color=INK2)
            pos.append(y)
            labs.append(f"{key} [{dname.split(' x ')[-1]}]: {f}")
            y += 1
        y += 0.6
    ax.set_yticks(pos, labs, fontsize=7)
    ax.invert_yaxis()
    ax.axvline(0, color="#c3c2b7", lw=0.8)
    ax.set_xlabel("ROC-AUC x100", fontsize=8, color=INK2)
    fig.tight_layout()
    fig.savefig(OUT / "shapley.png", dpi=150)
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=10_000)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20261101)
    runs, tests = load_runs(args.reps, rng)
    C = Cells(runs, args.reps, rng)
    print(f"{sum(len(v) for v in runs.values())} (source, run, head) entries; test sets {sorted(tests)}")
    head = [f"<!-- generated by scripts/analysis/decompose.py --reps {args.reps}; D25-E13, descriptive -->", ""]
    for name, fn in (("posthoc-paper", part_a), ("rotations-upstream-rule", part_b),
                     ("probe-mode-pairs", part_c), ("waterfall", part_d)):
        md, js = [f"# E13 {name}", *head], {"reps": args.reps}
        fn(C, md, js)
        (OUT / f"{name}.md").write_text("\n".join(md) + "\n")
        (OUT / f"{name}.json").write_text(json.dumps(js, indent=1, default=float))
        print("\n".join(md))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
