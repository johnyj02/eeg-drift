#!/usr/bin/env python3
"""Every Paper A figure (F1-F11) as PNG (300 dpi) and PDF, plus artifacts/figures/captions.md.

    .venv/bin/python scripts/figures.py [--results artifacts/s3-results] [--out artifacts/figures] [--only F10 F11]

Inputs: result records (results/*.json and the per-window *.npz next to them; smoke records are
ignored), artifacts/tables/d24-bootstrap.md (F9), configs/chbmit_seizures.json (F6), for F7
the CBraMod checkpoint and the local pilot store data/lmdb/chbmit_eval10, and for F10/F11 the
analyses under artifacts/analysis (E17, D28, D27B, D27, stats). A figure whose inputs do not exist yet
is skipped with the reason printed and listed in captions.md. --only remakes the named figures and
keeps the other captions. The exit code is 1 only if a figure fails for another reason (for
example read_d24 refusing a record, or a cross-check against an analysis file failing).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from functools import partial
from pathlib import Path
from typing import NamedTuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, MaxNLocator, MultipleLocator, NullFormatter
from matplotlib.transforms import blended_transform_factory
from read_d24 import CONTRASTS, ROTS
from read_d24 import load as load_d24
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
MODELS = ("biot", "cbramod")
NAME = {"biot": "BIOT", "cbramod": "CBraMod"}
ARMS = ("lp", "last", "last_randinit", "lp_randinit")
# Categorical slots 1-4 of the validated default palette (adjacent CVD and normal-vision checks
# pass); every multi-series plot also varies the marker or line style.
COLOR = {"lp": "#2a78d6", "last": "#eb6834", "last_randinit": "#1baf7a", "lp_randinit": "#eda100",
         "last_noise": "#e87ba4"}   # slot 5 of the same palette (also ROT_COLORS[4])
MARK = {"lp": "o", "last": "s", "last_randinit": "^", "lp_randinit": "D", "last_noise": "v"}
STYLE = {"lp": "-", "last": "--", "last_randinit": "-.", "lp_randinit": ":"}
ROT_COLORS = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4")
RELEASED_C, FIXED_C, PAPER_C = "#2a78d6", "#eb6834", "#8a8983"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e6e5e0"
RCPARAMS = {
    "font.size": 8, "axes.titlesize": 8, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "axes.edgecolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED, "lines.linewidth": 1.5,
    "legend.frameon": False, "legend.fontsize": 7, "pdf.fonttype": 42, "ps.fonttype": 42,
}


class Setting(NamedTuple):
    label: str
    dataset: str
    paper: bool                              # paper split (else the 5 rotations)
    fixed: tuple[tuple[str, ...], ...]       # fixed-probe tag sets, first one with records wins
    released: tuple[tuple[str, tuple[str, ...]], ...]   # (condition, tags) of released-code probes


SETTINGS = {
    "paper": Setting("CHB-MIT, DL's split", "chbmit", True, (("P1L",), ("P1E",)),
                     (("released-code probe", ("",)), ("proj_out tap, eval mode", ("P1PE",)),
                      ("encoder tap, train mode", ("P1ET",)))),
    "chbmit_rot": Setting("CHB-MIT, 5 rotations", "chbmit", False, (("S1L",), ("S1E", "S1M")),
                          (("released-code probe", ("S1",)), ("proj_out tap, eval mode", ("S1PE",)),
                           ("encoder tap, train mode", ("S1ET",)))),
    "siena": Setting("Siena, 5 rotations", "siena", False, (("S3L",), ("S3E", "S3M")),
                     (("released-code probe", ("S3",)),)),
    "siena_filt": Setting("Siena filtered, 5 rotations", "siena", False, (("S3FL",), ("S3FE", "S3FM")),
                          (("released-code probe", ("S3F",)),)),
}
FIXED_LABEL = "encoder-level probe (encoder tap, eval mode)"


class Skip(Exception):
    """The inputs of a figure do not exist yet."""


# ---- records ---------------------------------------------------------------------------------
def load_records(results: Path) -> list[dict]:
    out = []
    for p in sorted(results.rglob("results/*.json")):
        if p.name.startswith(("diag-", "test-index-", "val-index-", "report-")):
            continue
        r = json.loads(p.read_text())
        if "probes" in r and not r.get("smoke"):
            r["_path"] = p
            out.append(r)
    return out


def select(recs, tags, model=None, arm=None, setting=None, split=None, seed=None) -> list[dict]:
    s = SETTINGS.get(setting)
    return [r for r in recs if r.get("run_tag", "") in tags
            and (model is None or r["model"] == model) and (arm is None or r["arm"] == arm)
            and (s is None or (r["dataset"] == s.dataset and (r["split"] == "paper") == s.paper))
            and (split is None or r["split"] == split) and (seed is None or r["seed"] == seed)]


def first_present(recs, options, **kw) -> tuple[tuple[str, ...], list[dict]]:
    for tags in options:
        got = select(recs, tags, **kw)
        if got:
            return tags, got
    return (), []


def tagtxt(tags) -> str:
    return "+".join(t or "replication runs" for t in tags)


def metric(r: dict, head: str, key: str) -> float:
    return 100 * r["probes"][head]["test_at_best"][key]


def mean_sem(v) -> tuple[float, float]:
    v = np.asarray(v, dtype=float)
    return float(v.mean()), float(v.std(ddof=1) / np.sqrt(len(v))) if len(v) > 1 else 0.0


# ---- drawing helpers -------------------------------------------------------------------------
def band(ax, curves, color, marker, label, ls="-", fill=True):
    """Median line and min-max band over runs; runs of a non-modal length are dropped."""
    n = Counter(len(c) for c in curves).most_common(1)[0][0]
    a = np.array([c for c in curves if len(c) == n], dtype=float)
    x = np.arange(1, n + 1)
    if fill and len(a) > 1:
        ax.fill_between(x, np.nanmin(a, 0), np.nanmax(a, 0), color=color, alpha=0.15, lw=0)
    ax.plot(x, np.nanmedian(a, 0), color=color, marker=marker, ms=3.5, ls=ls, label=label,
            lw=1.5 if fill else 1.0)


def note(ax, text):
    ax.text(0.5, 0.5, text, ha="center", va="center", transform=ax.transAxes, color=MUTED, fontsize=7)


def logy(ax):
    """Log y axis with plain-number labels; minor ticks are labelled only on a narrow axis."""
    ax.set_yscale("log")
    lo, hi = ax.get_ylim()
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    some = FuncFormatter(lambda v, _: f"{v:g}" if round(v / 10 ** np.floor(np.log10(v))) in (2, 3, 5) else "")
    ax.yaxis.set_minor_formatter(some if np.log10(hi / lo) < 1.5 else NullFormatter())


def arm_handles():
    return [Line2D([], [], color=COLOR[a], marker=MARK[a], ms=4, label=a) for a in ARMS]


def save(fig, a, stem: str) -> None:
    for ext in ("png", "pdf"):
        fig.savefig(a.out / f"{stem}.{ext}", dpi=a.dpi, bbox_inches="tight")
    plt.close(fig)


# ---- F1: SSL adaptation loss -----------------------------------------------------------------
def f1(a, per_step: bool):
    kind = "step_losses" if per_step else "epoch_losses"
    rows = []
    for key, s in SETTINGS.items():
        cells = {}
        for m in MODELS:
            tags, rs = first_present(a.recs, s.fixed, model=m, setting=key)
            rs = [r for r in rs if r["arm"] in ("last", "last_randinit") and (r.get("adapt") or {}).get(kind)]
            if rs:
                cells[m] = (tags, rs)
        if cells:
            rows.append((s, cells))
    if not rows:
        raise Skip(f"no last/last_randinit record carries adapt.{kind} yet"
                   + (" (the D25 logged runs S1L, S3L, S3FL, P1L add it)" if per_step else ""))
    fig, axes = plt.subplots(len(rows), 2, figsize=(7.5, 2.4 * len(rows)), squeeze=False)
    used = []
    for i, (s, cells) in enumerate(rows):
        for j, m in enumerate(MODELS):
            ax = axes[i, j]
            ax.set_title(f"{NAME[m]}, {s.label}")
            if m not in cells:
                note(ax, "no records yet")
                continue
            tags, rs = cells[m]
            used.append(f"{NAME[m]} {s.label} {tagtxt(tags)}")
            n = Counter(r["arm"] for r in rs)
            ax.set_title(f"{NAME[m]}, {s.label}\n({tagtxt(tags)}; runs: {n['last']} pretrained, "
                         f"{n['last_randinit']} random init)")
            for arm, lab in (("last", "pretrained init"), ("last_randinit", "random init")):
                ad = [r["adapt"] for r in rs if r["arm"] == arm]
                if not ad:
                    continue
                band(ax, [d[kind] for d in ad], COLOR[arm], None if per_step else MARK[arm], lab)
                if per_step:   # shade the pass most runs restored
                    best, k = Counter(d["best_epoch"] for d in ad).most_common(1)[0]
                    spec = next(r["adapt_spec"] for r in rs if r["arm"] == arm)
                    # ponytail: assumes no skipped non-finite batch (adapt.skipped_nonfinite is 0 in every
                    # record so far); log per-pass step counts in adapt if that ever changes.
                    per = -(-spec["n_windows"] // spec["batch"])
                    ax.axvspan(best * per + 0.5, (best + 1) * per + 0.5, color=COLOR[arm], alpha=0.1, lw=0,
                               label=f"restored pass, {lab} ({k} of {len(ad)} runs)")
                else:
                    ax.scatter([d["best_epoch"] + 1 for d in ad], [d[kind][d["best_epoch"]] for d in ad],
                               s=45, facecolors="none", edgecolors=INK, lw=0.8, zorder=3,
                               label="_nolegend_")
            logy(ax)
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
            ax.set_xlabel("optimizer step" if per_step else "SSL pass (epoch)")
            ax.set_ylabel("SSL loss (log scale)")
            if per_step:   # the restored pass differs per panel
                ax.legend(handles=[h for h in ax.get_legend_handles_labels()[0] if isinstance(h, Patch)],
                          fontsize=6)
    handles = [Line2D([], [], color=COLOR[arm], marker=None if per_step else MARK[arm], label=lab)
               for arm, lab in (("last", "pretrained init"), ("last_randinit", "random init"))]
    if not per_step:
        handles.append(Line2D([], [], color=INK, marker="o", mfc="none", ls="none", ms=7,
                              label="restored (lowest-loss) pass of each run"))
    fig.legend(handles=handles, loc="lower center", ncol=3, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout()
    stem = "f1_ssl_loss_step" if per_step else "f1_ssl_loss_epoch"
    save(fig, a, stem)
    what = ("every optimizer step, with the restored pass shaded" if per_step else
            "each pass, with open circles at the pass each run restored (lowest mean loss)")
    return stem, (f"SSL adaptation loss (log scale) of the last block from the pretrained checkpoint and "
                  f"from random init, at {what}; median line and min-max band over seeds and rotations. "
                  f"Runs: {'; '.join(used)}.")


# ---- F2: probe learning curves ---------------------------------------------------------------
ROWS2 = (("train_loss", "train loss (BCE)"), ("val_loss", "val loss (BCE)"),
         ("val_roc", "val ROC-AUC x100"), ("val_pr", "val PR-AUC x100"))


def per_epoch(pr: dict) -> dict:
    h = pr.get("history")
    if not h:   # older records: only the validation ROC-AUC per epoch
        return {"val_roc": [100 * v for v in pr["val_curve"]]}
    return {"train_loss": [e["train_loss"] for e in h],
            "val_loss": [np.nan if e["val_loss"] is None else e["val_loss"] for e in h],
            "val_roc": [100 * e["val"]["roc_auc"] for e in h],
            "val_pr": [100 * e["val"]["pr_auc_trapz"] for e in h],
            "test_roc": [100 * e["test_plot_only"]["roc_auc"] for e in h]}


def f2(a, key: str):
    s = SETTINGS[key]
    cols = []
    for m in MODELS:
        for lab, tags in s.released:
            rs = select(a.recs, tags, model=m, setting=key)
            if rs:
                cols.append((m, lab, tags, rs))
        tags, rs = first_present(a.recs, s.fixed, model=m, setting=key)
        if rs:
            cols.append((m, FIXED_LABEL, tags, rs))
    if not cols:
        raise Skip(f"no probe records for {s.label}")
    data = [{arm: [r["probes"]["linear"] for r in rs if r["arm"] == arm and "linear" in r["probes"]]
             for arm in ARMS} for _, _, _, rs in cols]
    curves = [{arm: [per_epoch(p) for p in runs] for arm, runs in d.items() if runs} for d in data]
    rows = [row for row in ROWS2 if any(row[0] in c for cur in curves for cs in cur.values() for c in cs)]
    roc = [row for row, _ in rows].index("val_roc")
    fig, axes = plt.subplots(len(rows), len(cols), figsize=(2.7 * len(cols), 0.4 + 2.05 * len(rows)),
                             squeeze=False, sharex=True)
    jitter = np.random.default_rng(0)
    for j, (m, lab, tags, _) in enumerate(cols):
        for arm, cs in curves[j].items():
            for i, (row, _) in enumerate(rows):
                got = [c[row] for c in cs if row in c]
                if got:
                    band(axes[i, j], got, COLOR[arm], MARK[arm], arm)
            got = [c["test_roc"] for c in cs if "test_roc" in c]
            if got:
                band(axes[roc, j], got, COLOR[arm], None, "_nolegend_", ls="--", fill=False)
        ax = axes[roc, j]
        lo, hi = ax.get_ylim()
        ax.set_ylim(lo - 0.3 * (hi - lo), hi)   # a strip at the bottom for the selected-epoch ticks
        for k, arm in enumerate(ARMS):
            best = np.array([p["best_epoch"] + 1 for p in data[j][arm]], dtype=float)
            ax.plot(best + jitter.uniform(-0.15, 0.15, len(best)), np.full(len(best), 0.03 + 0.045 * k), "|",
                    color=COLOR[arm], ms=6, transform=ax.get_xaxis_transform())
        n_runs = max(len(v) for v in data[j].values())
        axes[0, j].set_title(f"{NAME[m]}, {lab}\n({tagtxt(tags)}, up to {n_runs} runs per arm)")
        for i in range(len(rows)):
            if not axes[i, j].lines:
                note(axes[i, j], "not logged in these records")
        axes[-1, j].set_xlabel("probe epoch")
        axes[-1, j].xaxis.set_major_locator(MaxNLocator(integer=True))
    for i, (_, ylab) in enumerate(rows):
        axes[i, 0].set_ylabel(ylab)
    extra = [Line2D([], [], color=MUTED, ls="--", lw=1, label="test ROC-AUC (plot only, not used for selection)"),
             Line2D([], [], color=MUTED, marker="|", ls="none", ms=7, label="selected epoch of each run")]
    has_test = any("test_roc" in c for cur in curves for cs in cur.values() for c in cs)
    if not has_test:
        extra = extra[1:]
    fig.legend(handles=arm_handles() + extra, loc="lower center", ncol=6, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout()
    stem = f"f2_probe_curves_{key}"
    save(fig, a, stem)
    cond = "; ".join(f"{NAME[m]} {lab}, {tagtxt(t)}" for m, lab, t, _ in cols)
    shown = [lab.replace(" x100", "").replace(" (BCE)", "") for _, lab in rows]
    shown = shown[0] if len(shown) == 1 else ", ".join(shown[:-1]) + " and " + shown[-1]
    test = (", and the dashed test ROC-AUC is plot only, not used for selection"
            if has_test else "")
    partial_log = (". Records without per-epoch history show the logged val ROC-AUC only"
                   if any("val_loss" not in c for cur in curves for cs in cur.values() for c in cs)
                   and len(rows) > 1 else "")
    return stem, (f"Linear-probe learning curves per epoch on {s.label}: {shown}, median line and min-max band "
                  f"over seeds and rotations per arm; ticks at the bottom of the ROC panels mark each run's "
                  f"selected epoch (best val ROC-AUC){test}{partial_log}. The released-code probe runs the frozen "
                  f"backbone in train mode and, for CBraMod, reads proj_out. Columns: {cond}.")


# ---- F3: the paper's Table 1 cells ------------------------------------------------------------
PAPER_T1 = {   # Dani and Liebe, Table 1, CHB-MIT: (mean, SEM over 5 seeds), x100
    ("biot", "lp"): {"bal_acc": (50.74, 0.21), "pr_auc_trapz": (1.53, 0.03), "roc_auc": (46.93, 0.30)},
    ("biot", "last"): {"bal_acc": (52.71, 0.72), "pr_auc_trapz": (31.52, 1.21), "roc_auc": (83.08, 1.89)},
    ("cbramod", "lp"): {"bal_acc": (57.87, 0.20), "pr_auc_trapz": (17.35, 0.24), "roc_auc": (54.14, 1.39)},
    ("cbramod", "last"): {"bal_acc": (61.37, 3.50), "pr_auc_trapz": (24.62, 2.31), "roc_auc": (83.67, 1.36)},
}
CELLS3 = (("biot", "lp", "BIOT LP"), ("biot", "last", "BIOT SA"),
          ("cbramod", "lp", "CBraMod LP"), ("cbramod", "last", "CBraMod SA"))
METRICS3 = (("bal_acc", "balanced accuracy"), ("pr_auc_trapz", "AUCPR"), ("roc_auc", "AUROC"))
SERIES3 = (   # label, run tag (None = paper), arm behind the paper's LP / SA cell, colour, hatched
    ("DL Table 1", None, {}, PAPER_C, False),
    ("released-code probe, pretrained init (replication runs)", "", {"lp": "lp", "last": "last"},
     RELEASED_C, False),
    ("released-code probe, random init: the released SA path (replication runs)", "", {"last": "last_randinit"},
     RELEASED_C, True),
    ("encoder-level probe (P1E), pretrained init", "P1E", {"lp": "lp", "last": "last"}, FIXED_C, False),
    ("encoder-level probe (P1E), random init", "P1E", {"lp": "lp_randinit", "last": "last_randinit"},
     FIXED_C, True),
)


def f3(a):
    if not select(a.recs, ("", "P1E"), setting="paper"):
        raise Skip("no replication-run or P1E records on the paper split")
    fig, axes = plt.subplots(2, 3, figsize=(11, 6), squeeze=False)
    w, seeds = 0.8 / len(SERIES3), set()
    for i, head in enumerate(("linear", "mlp_fullft")):
        for j, (met, mlab) in enumerate(METRICS3):
            ax = axes[i, j]
            for k, (_lab, tag, arms, col, hatched) in enumerate(SERIES3):
                xs, ys, es = [], [], []
                for c, (m, cell, _) in enumerate(CELLS3):
                    if tag is None:
                        y, e = PAPER_T1[(m, cell)][met]
                    else:
                        rs = (select(a.recs, (tag,), model=m, arm=arms[cell], setting="paper")
                              if cell in arms else [])
                        v = [metric(r, head, met) for r in rs if head in r["probes"]]
                        if not v:
                            continue
                        seeds.add(len(v))
                        y, e = mean_sem(v)
                    xs.append(c + (k - (len(SERIES3) - 1) / 2) * w)
                    ys.append(y)
                    es.append(e)
                ax.bar(xs, ys, w * 0.9, yerr=es, color="white" if hatched else col, edgecolor=col,
                       hatch="////" if hatched else None, lw=0.8, ecolor=INK, capsize=1.5,
                       error_kw={"elinewidth": 0.8})
            ax.set_xticks(range(len(CELLS3)), [c[2] for c in CELLS3])
            ax.set_ylim(0, 100)
            ax.grid(axis="x", visible=False)
            ax.set_title(f"{mlab}, our runs with the {head} head")
            ax.set_ylabel("x100")
    handles = [Patch(facecolor="white" if h else c, edgecolor=c, hatch="////" if h else None, label=lab)
               for lab, _, _, c, h in SERIES3]
    fig.legend(handles=handles, loc="lower center", ncol=3, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout()
    save(fig, a, "f3_table1_cells")
    n = "/".join(str(x) for x in sorted(seeds)) or "0"
    return "f3_table1_cells", (
        f"The paper's Table 1 CHB-MIT cells (mean and SEM over 5 seeds) next to our runs on the paper split "
        f"(mean and SEM over {n} seeds; top row linear head, bottom row the shipped MLP head): the "
        f"released-code probe from the pretrained checkpoint and along the released SA path (random init), "
        f"and the encoder-level probe (P1E) from pretrained and random init. The replication runs have no "
        f"random-init LP run.")


# ---- F4: per-rotation paired D24 contrasts ----------------------------------------------------
SETS4 = (("CHB-MIT", "chbmit", "S1E,S1M"), ("Siena", "siena", "S3E,S3M"),
         ("Siena filtered", "siena", "S3FE,S3FM"))


def f4(a):
    data = {lab: load_d24(str(a.results), ds, set(tags.split(","))) for lab, ds, tags in SETS4}
    if not any(data.values()):
        raise Skip("no D24-A records (S1E/S1M, S3E/S3M, S3FE/S3FM)")
    rows = [(lab, m) for lab, _, _ in SETS4 for m in MODELS]
    fig, axes = plt.subplots(len(rows), len(CONTRASTS), figsize=(8, 2.0 * len(rows)), squeeze=False)
    nseeds = Counter()
    for i, (lab, m) in enumerate(rows):
        roc = data[lab]
        for j, (x, y, _) in enumerate(CONTRASTS):
            ax, diffs = axes[i, j], []
            for r, rot in enumerate(ROTS):
                pa = list(roc.get((m, x, rot, "linear"), {}).values())
                pb = list(roc.get((m, y, rot, "linear"), {}).values())
                if not pa or not pb:
                    continue
                nseeds.update((len(pa), len(pb)))
                ma, mb = float(np.mean(pa)), float(np.mean(pb))
                diffs.append(ma - mb)
                ax.plot([0, 1], [mb, ma], color=ROT_COLORS[r], marker="o", ms=4, lw=1.2)
                ax.errorbar([0, 1], [mb, ma], yerr=[[mb - min(pb), ma - min(pa)], [max(pb) - mb, max(pa) - ma]],
                            fmt="none", ecolor=ROT_COLORS[r], elinewidth=0.8, capsize=2)
            ax.set_xticks([0, 1], [y, x])
            ax.set_xlim(-0.35, 1.35)
            ax.grid(axis="x", visible=False)
            ax.set_title(f"{x} minus {y}" + (f": mean {np.mean(diffs):+.1f}" if diffs else ""))
            if not diffs:
                note(ax, "no records yet")
        axes[i, 0].set_ylabel(f"{lab}, {NAME[m]}\nROC-AUC x100")
    handles = [Line2D([], [], color=c, marker="o", ms=4, label=r) for c, r in zip(ROT_COLORS, ROTS, strict=True)]
    fig.legend(handles=handles, loc="lower center", ncol=5, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout()
    save(fig, a, "f4_d24_paired")
    n = "/".join(str(k) for k in sorted(nseeds))
    return "f4_d24_paired", (
        f"D24-A contrasts per rotation (linear head, eval-mode probe on the encoder output; CHB-MIT S1E+S1M, "
        f"Siena S3E+S3M, Siena filtered S3FE+S3FM): each line joins the two arms' seed means in one rotation, "
        f"error bars show the min-max over its {n} seeds, and the title gives the mean of the per-rotation "
        f"differences.")


# ---- F5: test ROC and PR curves --------------------------------------------------------------
ROT5 = "rot0"


def f5(a):
    from sklearn.metrics import precision_recall_curve, roc_curve  # noqa: PLC0415

    rows = (("CHB-MIT DL's split (P1E)", ("P1E",), "paper"), (f"CHB-MIT {ROT5} (S1E, S1M)", ("S1E", "S1M"), ROT5))
    fig, axes = plt.subplots(len(rows), 4, figsize=(11, 5.4), squeeze=False)
    drawn = 0
    for i, (lab, tags, split) in enumerate(rows):
        for jm, m in enumerate(MODELS):
            axr, axp = axes[i, 2 * jm], axes[i, 2 * jm + 1]
            prev = None
            for arm in ARMS:
                rs = [r for r in select(a.recs, tags, model=m, arm=arm, split=split, seed=42)
                      if "linear" in r["probes"]]
                npz = rs[0]["_path"].with_name(rs[0]["_path"].stem + ".linear.npz") if rs else None
                if npz is None or not npz.exists():
                    continue
                z = np.load(npz)
                y, sc = z["y_test"], z["scores_best"]
                fpr, tpr, _ = roc_curve(y, sc)
                prec, rec, _ = precision_recall_curve(y, sc)
                kw = {"color": COLOR[arm], "ls": STYLE[arm], "lw": 1.2, "rasterized": True}
                axr.plot(fpr, tpr, label=f"{arm} ({metric(rs[0], 'linear', 'roc_auc'):.1f})", **kw)
                axp.plot(rec, prec, label=f"{arm} ({metric(rs[0], 'linear', 'pr_auc_trapz'):.1f})",
                         drawstyle="steps-post", **kw)
                prev, drawn = float(y.mean()), drawn + 1
            axr.plot([0, 1], [0, 1], color=MUTED, lw=0.6)
            if prev is not None:
                axp.axhline(prev, color=MUTED, lw=0.6)
            axr.set(title=f"{NAME[m]}, {lab}: ROC", xlabel="false positive rate", ylabel="true positive rate")
            axp.set(title=f"{NAME[m]}, {lab}: PR", xlabel="recall", ylabel="precision", ylim=(0, 1.02))
            for ax in (axr, axp):
                if ax.get_legend_handles_labels()[0]:
                    ax.legend(fontsize=6, title="arm (AUC x100)", title_fontsize=6)
                else:
                    note(ax, "no score file yet")
    if not drawn:
        raise Skip("no P1E or S1E/S1M score files (*.linear.npz) for seed 42")
    fig.tight_layout()
    save(fig, a, "f5_roc_pr")
    return "f5_roc_pr", (
        f"Test ROC and precision-recall curves at the validation-selected epoch (seed 42, linear head, "
        f"encoder-level probe) for lp, last, last_randinit and lp_randinit, on the paper split (P1E) and on "
        f"CHB-MIT {ROT5} of the revised protocol; legend values are ROC-AUC or PR-AUC x100, the grey line in the "
        f"PR panels is the test prevalence.")


# ---- F6: CHB-MIT protocol timeline -----------------------------------------------------------
def f6(a):
    from unittest import mock  # noqa: PLC0415

    from eegdrift.data import chbmit  # noqa: PLC0415

    path = Path(a.seizures)
    if not path.exists():
        raise Skip(f"{path} not found")
    seizures = json.loads(path.read_text())
    if not seizures.get("chb01_03"):
        raise Skip("chb01_03 has no seizure in the seizure table")
    on, off = seizures["chb01_03"][0]   # true [onset, offset) in 256 Hz samples
    fs = chbmit.FS_NATIVE
    zeros = np.zeros((16, 3600 * fs), np.float32)   # chb01_03 is a one-hour record
    # Run the real window code on a silent signal of the record's length: only starts and labels are used.
    with mock.patch.multiple(chbmit, read_edf_uv=lambda p: ([], None, float(fs)),
                             select_bipolar=lambda c, d: (zeros, 16)):
        recs, _, _ = chbmit.eval_windows("chb01_03.edf", [chbmit.Seizure(on - 1, off - 1)])  # upstream: s*256-1
    t_on, t_off = on / fs, off / fs
    lo, hi = t_on - 30, t_off + 30
    grid = [r for r in recs if r["kind"] == "grid" and lo - 10 < r["start"] / fs < hi]
    extra = [r for r in recs if r["kind"] != "grid"]
    pos, neg = "#eb6834", GRID
    fig, ax = plt.subplots(figsize=(8, 2.8))
    ax.broken_barh([(t_on, t_off - t_on)], (2.75, 0.4), facecolors=MUTED)
    ax.text((t_on + t_off) / 2, 2.95, f"{t_on:.0f} to {t_off:.0f} s", ha="center", va="center", color="white",
            fontsize=7)
    for t in (t_on, t_off):
        ax.axvline(t, color=MUTED, lw=0.6)
    rows = (("grid windows,\ninherited start/end rule", 2, [r["label"] for r in grid]),
            ("grid windows,\noverlap rule", 1, [chbmit.overlap_label(r, seizures) for r in grid]))
    ictal = sum(chbmit.overlap_label(r, seizures) for r in grid)
    for _lab, y, labels in rows:
        for r, lbl in zip(grid, labels, strict=True):
            ax.broken_barh([(r["start"] / fs, r["n_samples"] / fs)], (y - 0.3, 0.6),
                           facecolors=pos if lbl else neg, edgecolor="white", lw=1.5)
        ax.text(hi + 2, y, f"{sum(labels)} of {ictal} ictal windows positive", va="center", fontsize=7)
    for k, r in enumerate(extra):
        ax.broken_barh([(r["start"] / fs, r["n_samples"] / fs)], (0.05 - 0.38 * (k % 2), 0.3),
                       facecolors=pos, edgecolor="white", lw=1.5)
    ax.text(hi + 2, -0.1, f"{len(extra)} extra windows, all positive, kept in test", va="center", fontsize=7)
    ax.set_yticks([2.95, 2, 1, -0.1], ["seizure (summary file)", rows[0][0], rows[1][0],
                                      "extra windows at a\n5 s stride (inherited)"])
    ax.set_xlim(lo - 10, hi)
    ax.set_ylim(-0.6, 3.3)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("time in record chb01_03 (s)")
    ax.legend(handles=[Patch(color=pos, label="labelled seizure"), Patch(color=neg, label="labelled non-seizure")],
              loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2)
    save(fig, a, "f6_chbmit_protocol_timeline")
    return "f6_chbmit_protocol_timeline", (
        f"CHB-MIT protocol on record chb01_03 (seizure {t_on:.0f} to {t_off:.0f} s): 10 s grid windows labelled "
        f"by the inherited start/end rule (positive only if a seizure start or end falls inside the window) and "
        f"by the overlap rule, and the extra 10 s windows at a 5 s stride that the inherited preprocessing adds "
        f"around every seizure in every split, test included; computed with eval_windows and overlap_label in "
        f"src/eegdrift/data/chbmit.py.")


# ---- F7: CBraMod proj_out mechanism ----------------------------------------------------------
def f7(a):
    store = Path(a.store)
    if not (store / "data.mdb").exists():
        raise Skip(f"local pilot store {store} not found")
    import torch  # noqa: PLC0415

    from eegdrift.data.windows import WindowStore  # noqa: PLC0415
    from eegdrift.models.registry import Registry  # noqa: PLC0415

    reg = Registry.load(ROOT)
    if not reg.checkpoint_path("cbramod").exists():
        raise Skip(f"CBraMod checkpoint {reg.checkpoint_path('cbramod')} not found")
    ws = WindowStore(str(store))
    idx = np.sort(np.random.default_rng(0).choice(len(ws), 512, replace=False))
    s = ws.shape[1] // 200
    x = torch.from_numpy(np.stack([ws.get(int(i)).reshape(16, s, 200) for i in idx])) / 100.0
    sv, stats = {}, {}
    for init in ("pretrained", "random"):
        torch.manual_seed(42)
        m = reg.build("cbramod", init)
        m.module.eval()
        with torch.no_grad():
            feats = {tap: torch.cat([m.features(m.prepare(xb), tap) for xb in x.split(64)])
                     for tap in ("encoder", "proj_out")}
        sv[init] = torch.linalg.svdvals(m.module.proj_out[0].weight.detach().double()).numpy()
        stats[init] = {tap: (f.std().item(), f.reshape(len(f), -1).std(0).mean().item())
                       for tap, f in feats.items()}
    col = {"pretrained": COLOR["last"], "random": COLOR["last_randinit"]}
    mk = {"pretrained": MARK["last"], "random": MARK["last_randinit"]}
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 3.2))
    for init, v in sv.items():
        rel = v / v.max()
        a1.plot(np.arange(1, len(v) + 1), rel, color=col[init], marker=mk[init], ms=2.5, markevery=10,
                label=f"{init} init: condition number {v.max() / v.min():.1e}, {int((rel < 0.01).sum())} below 1%")
    a1.axhline(0.01, color=MUTED, lw=0.8)
    a1.set(yscale="log", xlabel="singular value index", ylabel="singular value / largest",
           title="(a) proj_out weight spectrum")
    a1.legend(fontsize=6)
    groups = [("encoder", 0, "encoder,\noverall"), ("encoder", 1, "encoder,\nacross windows"),
              ("proj_out", 0, "proj_out,\noverall"), ("proj_out", 1, "proj_out,\nacross windows")]
    for k, init in enumerate(("pretrained", "random")):
        xs = np.arange(len(groups)) + (k - 0.5) * 0.3
        ys = [stats[init][tap][q] for tap, q, _ in groups]
        a2.plot(xs, ys, ls="none", marker=mk[init], ms=7, color=col[init], label=f"{init} init")
        for xx, yy in zip(xs, ys, strict=True):
            a2.text(xx, yy * 1.35, f"{yy:.3g}", ha="center", fontsize=6)
    a2.set_xticks(range(len(groups)), [g[2] for g in groups])
    a2.set_xlim(-0.6, len(groups) - 0.4)
    a2.set_yscale("log")
    a2.set_ylim(top=a2.get_ylim()[1] * 2.5)   # room for the value labels
    a2.set(yscale="log", ylabel="feature standard deviation (log scale)", title="(b) feature scale, eval mode")
    a2.grid(axis="x", visible=False)
    a2.legend(fontsize=6, loc="center right")
    fig.tight_layout()
    save(fig, a, "f7_cbramod_proj_out")
    p, r = stats["pretrained"], stats["random"]
    return "f7_cbramod_proj_out", (
        f"Why the released CBraMod probe under-fits: (a) singular values of the proj_out weight relative to the "
        f"largest, pretrained checkpoint against random init (seed 42); (b) standard deviation of the encoder "
        f"output and of the proj_out output on 512 windows of the local CHB-MIT pilot store (divided by 100, "
        f"eval mode), overall and across windows (mean over dimensions). Pretrained proj_out output "
        f"{p['proj_out'][0]:.3g} against {r['proj_out'][0]:.3g} for random init.")


# ---- F8: C2/C3 ---------------------------------------------------------------------------------
def tagnum(tag: str, key: str) -> int:
    """'C2E-N896' -> 896 for key N; 'C3-P11N2048' -> 11 for key P."""
    return int(tag.split("-", 1)[1][1:].split("N")[0]) if key == "P" else int(tag.rsplit("N", 1)[1])


def f8(a):
    probes = (("released-code probe", "C2-N", "C3-P", "R3-b128", RELEASED_C),
              ("encoder-level probe", "C2E-N", "C3E-P", "R3E-b128", FIXED_C))
    fig, axes = plt.subplots(2, 2, figsize=(9, 6), squeeze=False)
    seeds, drawn = set(), False
    for i, m in enumerate(MODELS):
        axis_specs = (("N", "SSL windows N (all patients)"), ("P", "patients P (N = 2,048)"))
        for j, (key, xlabel) in enumerate(axis_specs):
            ax = axes[i, j]
            for lab, c2, c3, lp_tag, col in probes:
                prefix = c2 if key == "N" else c3
                for arm, ls, mk, init in (("last", "-", "o", "pretrained"),
                                          ("last_randinit", "--", "^", "random init")):
                    pts = defaultdict(list)
                    for r in a.recs:
                        if (r.get("run_tag", "").startswith(prefix) and r["model"] == m and r["arm"] == arm
                                and "linear" in r["probes"]):
                            pts[tagnum(r["run_tag"], key)].append(metric(r, "linear", "roc_auc"))
                    if pts:
                        xs = sorted(pts)
                        seeds.update(len(v) for v in pts.values())
                        ax.plot(xs, [np.mean(pts[x]) for x in xs], color=col, ls=ls, marker=mk, ms=4,
                                label=f"{lab}, {init}")
                        ax.set_xticks(xs)
                        drawn = True
                v = [metric(r, "linear", "roc_auc") for r in select(a.recs, (lp_tag,), model=m, arm="lp")
                     if "linear" in r["probes"]]
                if v:
                    mu, se = mean_sem(v)
                    ax.axhline(mu, color=col, ls=":", lw=1.2,
                               label=f"LP baseline, {lab} ({lp_tag}, {len(v)} seeds)")
                    ax.axhspan(mu - se, mu + se, color=col, alpha=0.12, lw=0)
            ax.set(title=f"{NAME[m]}: ROC-AUC against {key}", xlabel=xlabel, ylabel="test ROC-AUC x100")
            if not ax.get_legend_handles_labels()[0]:
                note(ax, "no records yet")
    if not drawn:
        raise Skip("no C2/C3 records (C2-*, C3-*, C2E-*, C3E-*)")
    legend = {lab: h for ax in axes.flat for h, lab in zip(*ax.get_legend_handles_labels(), strict=True)}
    fig.legend(legend.values(), legend.keys(), loc="lower center", ncol=3, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout()
    save(fig, a, "f8_c2_c3")
    n = "/".join(str(k) for k in sorted(seeds))
    return "f8_c2_c3", (
        f"Data-amount (C2, ROC-AUC against the number of SSL windows N) and patient-count (C3, against the number "
        f"of patients P at N = 2,048) tests on the paper split, linear head at batch 128, fixed-compute SSL "
        f"({n} seed per point): released-code probe (C2-*, C3-*) against the encoder-level probe (C2E-*, C3E-*), "
        f"pretrained and random init, with the LP baselines (R3-b128, R3E-b128; mean, band = SEM over seeds) "
        f"as dotted lines.")


# ---- F9: forest plot of the D24 bootstrap ----------------------------------------------------
SETLAB = {"chbmit (S1E,S1M)": "CHB-MIT rot.", "siena (S3E,S3M)": "Siena rot.",
          "siena (S3FE,S3FM)": "Siena filt. rot.", "chbmit (P1E)": "CHB-MIT DL's split"}
MODEL_C = {"biot": "#2a78d6", "cbramod": "#eb6834"}


def f9(a):
    path = Path(a.tables) / "d24-bootstrap.md"
    if not path.exists():
        raise Skip(f"{path} not found (run scripts/bootstrap_d24.py)")
    rows = []
    for line in path.read_text().splitlines():
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) < 6:
            continue
        try:
            lo, hi = (float(v) for v in c[5].strip("[]").split(","))
            rows.append((c[0], c[1], c[2], c[3], float(c[4]), lo, hi))
        except ValueError:   # header and separator rows
            continue
    if not rows:
        raise Skip(f"no contrast rows parsed from {path}")
    order = list(dict.fromkeys((r[0], r[1], r[2]) for r in rows))
    contrasts = list(dict.fromkeys(r[3] for r in rows))
    fig, axes = plt.subplots(1, len(contrasts), figsize=(2.6 * len(contrasts) + 1.5, 0.22 * len(order) + 1.4),
                             sharey=True, squeeze=False)
    for ax, con in zip(axes[0], contrasts, strict=True):
        for ds, model, head, c, mu, lo, hi in rows:
            if c != con:
                continue
            y = order.index((ds, model, head))
            ax.errorbar(mu, y, xerr=[[mu - lo], [hi - mu]], fmt="o" if head == "linear" else "s", ms=3.5,
                        color=MODEL_C.get(model, MUTED), elinewidth=1, capsize=0)
        for x0 in (-3, 3):
            ax.axvline(x0, color=MUTED, lw=0.5, alpha=0.5)
        ax.axvline(0, color=MUTED, lw=0.9)
        ax.set_title(con.replace(" - ", " minus "))
        ax.set_xlabel("ROC-AUC x100")
        ax.grid(axis="y", visible=False)
    axes[0, 0].set_yticks(range(len(order)), [f"{SETLAB.get(d, d)}, {NAME.get(m, m)}, {h}" for d, m, h in order])
    axes[0, 0].invert_yaxis()
    handles = [Line2D([], [], color=MODEL_C[m], marker="o", ls="none", label=NAME[m]) for m in MODELS]
    handles += [Line2D([], [], color=MUTED, marker=k, ls="none", label=f"{h} head")
                for k, h in (("o", "linear"), ("s", "mlp_fullft"))]
    fig.legend(handles=handles, loc="lower center", ncol=4, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout()
    save(fig, a, "f9_d24_forest")
    return "f9_d24_forest", (
        "Cluster-bootstrap 95% intervals for every D24 contrast (ROC-AUC x100, from "
        "artifacts/tables/d24-bootstrap.md: rotations then seeds under the revised protocol, seeds on the "
        "paper split); the thin lines at minus and plus 3 mark the D24 decision margin. Descriptive only, the "
        "verdicts stay those of the D24 rules.")


# ---- F10: initialisation x probe setting on DL's split ------------------------------------------
# Probe settings on DL's split, linear head: (label, run tag, E17 cell); BIOT's released probe reads its encoder.
SETTINGS10 = {
    "biot": (("released-code\nprobe\n(train mode)", "", None), ("encoder-level\nprobe\n(eval mode)", "P1E", None)),
    "cbramod": (("released-code\nprobe (proj_out\ntap, train mode)", "", "proj_out,train"),
                ("encoder tap only\n(train mode)", "P1ET", "encoder,train"),
                ("eval mode only\n(proj_out tap)", "P1PE", "proj_out,eval"),
                ("encoder-level\nprobe (encoder\ntap, eval mode)", "P1E", "encoder,eval")),
}
ARMS10 = (("lp", "frozen pretrained encoder (lp)"), ("last", "SA from the pretrained weights (last)"),
          ("last_randinit", "SA from random init, as shipped (last_randinit)"))


def f10(a):
    path = Path(a.analysis) / "E17" / "e17.json"
    if not path.exists():
        raise Skip(f"{path} not found (scripts/analysis/e17_tap_mode.py)")
    e17 = json.loads(path.read_text())["paper"]["linear"]["cells"]
    vals = {}
    for m, sets in SETTINGS10.items():
        for _, tag, cell in sets:
            for arm, _ in ARMS10:
                rs = sorted(select(a.recs, (tag,), model=m, arm=arm, setting="paper"), key=lambda r: r["seed"])
                v = [metric(r, "linear", "roc_auc") for r in rs if "linear" in r["probes"]]
                if not v:
                    raise Skip(f"no {NAME[m]} {arm} records ({tagtxt((tag,))}) on DL's split")
                if cell and not np.allclose(v, e17[cell][arm], atol=1e-6):   # the paper cites E17 for these
                    raise ValueError(f"CBraMod {cell} {arm}: records {v} differ from {path}")
                vals[(m, tag, arm)] = np.array(v)
    fig, axes = plt.subplots(1, 2, figsize=(6.5, 2.9), sharey=True,
                             gridspec_kw={"width_ratios": [len(s) + 0.4 for s in SETTINGS10.values()]})
    dx = (-0.25, 0.0, 0.25)
    for ax, (m, sets) in zip(axes, SETTINGS10.items(), strict=True):
        for g, (_, tag, _) in enumerate(sets):
            mu = {arm: vals[(m, tag, arm)].mean() for arm, _ in ARMS10}
            ax.plot([g + dx[0], g + dx[1]], [mu["lp"], mu["last"]], color=MUTED, lw=0.8, zorder=2)
            for (arm, _), d in zip(ARMS10, dx, strict=True):
                v = vals[(m, tag, arm)]
                ax.errorbar(g + d, mu[arm], yerr=[[mu[arm] - v.min()], [v.max() - mu[arm]]], fmt=MARK[arm], ms=5,
                            color=COLOR[arm], mec="white", mew=0.5, elinewidth=1, capsize=2, zorder=3)
            gain = f"{mu['last'] - mu['lp']:+.1f}".replace("-", "−")
            ax.text(g, 98.5, f"last − lp: {gain}", ha="center", va="top", fontsize=6.5)
        for k, ls in (("lp", "--"), ("last", "-.")):
            y = PAPER_T1[(m, k)]["roc_auc"][0]
            ax.axhline(y, color=PAPER_C, ls=ls, lw=0.9, zorder=1)
            ax.text(-0.47, y + (0.5 if k == "last" else -0.5), f"DL {'LP' if k == 'lp' else 'SA'} {y:.1f}",
                    va="bottom" if k == "last" else "top", fontsize=6, color=PAPER_C)   # LP label below its line
        ax.set_xticks(range(len(sets)), [s[0] for s in sets], fontsize=6.5)
        ax.set_xlim(-0.5, len(sets) - 0.5)
        ax.grid(axis="x", visible=False)
        ax.set_title(NAME[m])
    axes[0].set_ylim(40, 100)
    axes[0].set_ylabel("test ROC-AUC x100")
    handles = [Line2D([], [], color=COLOR[arm], marker=MARK[arm], ls="none", ms=5, label=lab)
               for arm, lab in ARMS10]
    handles += [Line2D([], [], color=PAPER_C, ls=ls, lw=0.9, label=f"DL's reported {k} (their Table 1)")
                for k, ls in (("LP", "--"), ("SA", "-."))]
    fig.legend(handles=handles, loc="lower center", ncol=3, bbox_to_anchor=(0.5, 1.0), fontsize=6.5)
    fig.tight_layout()
    save(fig, a, "fig_ablation")
    gain = {t: float(np.mean(vals[("cbramod", t, "last")] - vals[("cbramod", t, "lp")]))
            for _, t, _ in SETTINGS10["cbramod"]}
    return "fig_ablation", (
        "Initialisation and probe setting on DL's split (upstream labels, DL's SSL protocol, linear head): test "
        "ROC-AUC of the frozen pretrained encoder (lp), of SSL adaptation of the last block from the pretrained "
        "weights (last) and from random init, the path the release runs as shipped (last_randinit); marker = "
        "mean over 5 seeds, whisker = range over the seeds; the grey segment and the number above each group "
        "are the SA gain last - lp. Dashed and dash-dotted lines: DL's reported LP and SA (their Table 1). "
        "Probe settings: DL's released-code probe (CBraMod: reads proj_out, the reconstruction head, with the "
        "frozen backbone in train mode, dropout on; BIOT: train mode, it already reads its encoder), each change "
        "alone, and both changed, the encoder-level probe (for BIOT only the mode changes). "
        "CBraMod SA gain per setting: "
        + ", ".join(f"{gain[t]:+.2f}" for _, t, _ in SETTINGS10["cbramod"])
        + " (released-code probe, encoder tap only, eval mode only, both). Sources: wave-1 replication records "
        "(released-code probe), P1ET, P1PE, P1E records; the CBraMod cells equal artifacts/analysis/E17/e17.json "
        "seed by seed (checked); BIOT means as in artifacts/tables/chbmit-paper.md and d24-chbmit-P1E.md.")


# ---- F11: adaptation effects with the fixed-recipe and the tuned probes, with the noise control ----------
SETS11 = (   # D28 tag, fixed-recipe set in d27b.json / cpu.json, header
    ("S1G", "CHB-MIT", "CHB-MIT (5 rotations)"), ("S3G", "Siena", "Siena (5 rotations)"),
    ("S3FG", "Siena filtered", "Siena filtered (5 rotations)"),
    ("P1G", "CHB-MIT paper split", "CHB-MIT, DL's split (5 seeds)"),
    ("P1QG", "CHB-MIT paper split, q95", "CHB-MIT, DL's split, q95 input (5 seeds)"))
PROBES11 = (   # D28 variant, head, tuned, row label
    ("grid", "raw", False, "fixed, raw"), ("grid", "raw", True, "tuned, raw"),
    ("grid_z", "z", False, "fixed, standardized"), ("grid_z", "z", True, "tuned, standardized"))
CON11 = (("last", "lp"), ("last", "last_noise"))
ARMS11 = ("lp", "last", "last_noise")
NOISE11 = {("E27", "linear"): "raw", ("A1", "linear"): "raw", ("A1", "linear_z"): "z", ("A6", "linear_z"): "z"}
SHADE = "#f1f0eb"


def t95(d) -> tuple[float, float, float]:
    """Mean and 95% t-interval over units (df = n - 1)."""
    d = np.asarray(d, dtype=float)
    h = stats.t.ppf(0.975, len(d) - 1) * d.std(ddof=1) / np.sqrt(len(d))
    return float(d.mean()), float(d.mean() - h), float(d.mean() + h)


def effects_data(a) -> dict:
    """Per-unit arm means (rotation means of 3 seeds; on DL's split the 5 seeds) per (D28 tag, model, head,
    tuned) from d28.json; the fixed-recipe partners are checked against the files the paper cites for them."""
    base = Path(a.analysis)
    paths = [base / p for p in ("D28/d28.json", "D27B/d27b.json", "D27/cpu.json", "stats/stats.json")]
    if missing := [str(p) for p in paths if not p.exists()]:
        raise Skip(f"{', '.join(missing)} not found")
    d28, d27b, cpu, st = (json.loads(p.read_text()) for p in paths)
    ref = {(s, m, h): {k: np.array(v["per_unit"]) for k, v in cell[h]["arms"].items() if k in ARMS11}
           for s, sv in d27b["sets"].items() for m, cell in sv["models"].items() for h in ("raw", "z")}
    for t in cpu["tost"]:   # noise control: E27 (raw), A6 (standardized), A1 (q95 input, both)
        if h := NOISE11.get((t["item"], t["probe"])):
            u = ref.setdefault((t["setting"], t["model"], h), {k: np.array(t[k]) for k in ("lp", "last")})
            if not np.allclose(t["last"], u["last"]):
                raise ValueError(f"{t['setting']} {t['model']} {h}: noise-control 'last' differs from d27b.json")
            u["last_noise"] = np.array(t["last_noise"])
    for r in st["e10"]:   # the raw head on the rotations is Table d24a (stats.json, D24-A)
        if not r["paper"] and r["probe"] == "linear" and (r["a"], r["b"]) == ("last", "lp"):
            u = ref[(r["setting"], r["model"], "raw")]
            if not np.allclose(t95(u["last"] - u["lp"]), (r["mean"], *r["t"]["ci95"])):
                raise ValueError(f"{r['setting']} {r['model']} last - lp: d27b.json differs from stats.json")
    out = {}
    for tag, s, _ in SETS11:
        for m in MODELS:
            for v, h, *_ in PROBES11[::2]:
                cell = d28["contrasts"].get(f"{tag}|{m}|{v}")
                if cell is None:   # q95 input: BIOT only
                    continue
                arms = {k: x for k, x in cell["arms"].items() if k in ARMS11}
                tuned = {k: np.array(x["per_unit"]) for k, x in arms.items()}
                fixed = {k: np.array(x["fixed"]) for k, x in arms.items() if "fixed" in x}
                r = ref.get((s, m, h), {})
                if set(fixed) != set(r) or not all(np.allclose(fixed[k], r[k]) for k in r):
                    raise ValueError(f"{tag} {m} {v}: fixed-recipe arms in d28.json differ from d27b/cpu.json")
                for name, c in cell["contrasts"].items():
                    con = tuple(name.split(" - "))
                    for u, rec in ((tuned, c), (fixed, c.get("fixed"))):
                        if con in CON11 and rec and not np.allclose(t95(u[con[0]] - u[con[1]]),
                                                                    (rec["mean"], *rec["t"]["ci95"])):
                            raise ValueError(f"{tag} {m} {v} {name}: arm means do not give d28.json's interval")
                out[(tag, m, h, False)], out[(tag, m, h, True)] = fixed, tuned
    return out


def f11(a):
    data = effects_data(a)
    fig, axes = plt.subplots(1, 4, figsize=(6.5, 3.4), sharey=True, gridspec_kw={"width_ratios": [5, 4, 5, 4]})
    rows, labels, pitch = [], [], len(PROBES11) + 1.4
    for g, (tag, _, head) in enumerate(SETS11):
        y0 = g * pitch
        axes[0].text(0.004, y0, head, transform=blended_transform_factory(fig.transFigure, axes[0].transData),
                     va="center", fontsize=6.5, fontweight="bold", zorder=5,
                     bbox={"fc": "white", "ec": "none", "pad": 0.4})
        for ax in axes if g else ():
            ax.axhline(y0 - 0.7, color=GRID, lw=0.8)
        for k, (_, h, tuned, lab) in enumerate(PROBES11):
            y = y0 + 1 + k
            rows.append(y)
            labels.append(lab)
            for (ax, al), m in zip((axes[:2], axes[2:]), MODELS, strict=True):
                if (u := data.get((tag, m, h, tuned))) is None:
                    continue
                if tuned:
                    for axx in (ax, al):
                        axx.axhspan(y - 0.5, y + 0.5, color=SHADE, lw=0, zorder=0)
                for j, (x, b) in enumerate(CON11):
                    if b in u:
                        mu, lo, hi = t95(u[x] - u[b])
                        c = INK if b == "lp" else COLOR[b]
                        ax.errorbar(mu, y + (j - 0.5) * 0.42, xerr=[[mu - lo], [hi - mu]], fmt=MARK[b], ms=3,
                                    mfc=c if tuned else "white", mec=c, mew=0.8, color=c, elinewidth=0.9,
                                    capsize=1.2)
                for q, arm in enumerate(ARMS11):
                    if arm in u:
                        al.plot(u[arm].mean(), y + (q - 1) * 0.28, MARK[arm], ms=3, mfc=COLOR[arm] if tuned else
                                "white", mec=COLOR[arm], mew=0.8)
        if not any((tag, "cbramod", h, t) in data for _, h, t, _ in PROBES11):
            for ax, x in zip(axes[2:], (0.5, 0.7), strict=True):   # arm panel: clear of the chance line
                ax.text(x, y0 + 2.5, "BIOT only", transform=ax.get_yaxis_transform(), ha="center", va="center",
                        fontsize=6.5, color=MUTED, zorder=5, bbox={"fc": "white", "ec": "none", "pad": 0.4})
    for (ax, al), m in zip((axes[:2], axes[2:]), MODELS, strict=True):
        ax.axvline(0, color=MUTED, lw=0.9, zorder=1)
        for x0 in (-3, 3):
            ax.axvline(x0, color=MUTED, lw=0.5, ls=":", zorder=1)
        ax.xaxis.set_major_locator(MultipleLocator(5))
        ax.set_title(f"{NAME[m]}: differences")
        ax.set_xlabel("difference, ROC-AUC x100", fontsize=7)
        al.axvline(50, color=MUTED, lw=0.6, ls=":", zorder=1)
        al.set_xlim(28, 97)
        al.set_xticks(range(30, 100, 20))
        al.set_title(f"{NAME[m]}: arm means")
        al.set_xlabel("test ROC-AUC x100", fontsize=7)
    axes[0].set_yticks(rows, labels, fontsize=6.5)
    axes[0].set_ylim(rows[-1] + 0.7, -0.7)
    for ax in axes:
        ax.grid(axis="y", visible=False)
        ax.tick_params(axis="y", length=0)
        ax.spines["left"].set_visible(False)
    handles = [Line2D([], [], color=INK if b == "lp" else COLOR[b], marker=MARK[b], ms=3.5, lw=0.9,
                      label=f"{x} − {b}") for x, b in CON11]
    handles += [Line2D([], [], color=COLOR[arm], marker=MARK[arm], ls="none", ms=3.5, label=arm) for arm in ARMS11]
    handles += [Line2D([], [], color=MUTED, marker="o", mfc=fc, ls="none", ms=3.5, label=lab)
                for fc, lab in (("white", "open: fixed recipe"), (MUTED, "filled, shaded: tuned"))]
    fig.legend(handles=handles, loc="lower center", ncol=7, bbox_to_anchor=(0.5, 1.0), fontsize=6.5,
               handlelength=1.6, columnspacing=1.2)
    fig.tight_layout(w_pad=0.6)
    save(fig, a, "fig_effects")
    q = {k: data[("P1QG", "biot", "raw", k)] for k in (False, True)}
    return "fig_effects", (
        "SA gain and noise control with the fixed probe recipe and with tuned probes (encoder-level linear probe, "
        "raw or standardized features; ROC-AUC x100). Rows per setting: fixed recipe, raw; tuned, raw; fixed "
        "recipe, standardized; tuned, standardized (open markers = fixed recipe, filled markers on shaded rows = "
        "tuned). Settings: CHB-MIT, Siena and Siena filtered under the revised protocol (5 subject rotations, 3 "
        "seeds each, overlap labels; unit = rotation mean), and DL's split (upstream labels; unit = seed, 5 seeds "
        "on one split, seed uncertainty only) with standard input for both models and with BIOT's q95 input "
        "(BIOT only). Left panel per model: last - lp (black circle) and last - last_noise (pink triangle), mean "
        "and 95% t-interval over the 5 units (df 4); dotted lines at -3 and +3 mark the decision margin; no "
        "triangle = no noise arm "
        "(fixed recipe: BIOT CHB-MIT standardized; CBraMod CHB-MIT both heads, Siena and Siena filtered "
        "standardized; DL's split with standard input: neither probe). Right panel per model: arm means (mean "
        "over the 5 units) of lp (blue circle), last (orange square) and last_noise (pink triangle); dotted line "
        "at 50 = chance. "
        "Example, BIOT q95 input, raw features, lp / last / last_noise: fixed recipe "
        + " / ".join(f"{q[False][k].mean():.1f}" for k in ARMS11) + ", tuned "
        + " / ".join(f"{q[True][k].mean():.1f}" for k in ARMS11) + ". Sources: artifacts/analysis/D28/d28.json "
        "(tuned probes and their fixed-recipe partners, same seeds); the fixed-recipe values equal "
        "artifacts/analysis/D27B/d27b.json (arm means, both heads, rotations and DL's split), "
        "artifacts/analysis/D27/cpu.json (last_noise: E27 raw, A6 standardized, A1 q95 input) and, for the raw "
        "head on the rotations, artifacts/analysis/stats/stats.json (Table d24a) (checked).")


FIGURES = (
    [("F1 per epoch", partial(f1, per_step=False)), ("F1 per step", partial(f1, per_step=True))]
    + [(f"F2 {k}", partial(f2, key=k)) for k in SETTINGS]
    + [("F3", f3), ("F4", f4), ("F5", f5), ("F6", f6), ("F7", f7), ("F8", f8), ("F9", f9),
       ("F10", f10), ("F11", f11)]
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Paper A figures")
    ap.add_argument("--results", default=str(ROOT / "artifacts" / "s3-results"))
    ap.add_argument("--out", default=str(ROOT / "artifacts" / "figures"))
    ap.add_argument("--tables", default=str(ROOT / "artifacts" / "tables"))
    ap.add_argument("--seizures", default=str(ROOT / "configs" / "chbmit_seizures.json"))
    ap.add_argument("--store", default=str(ROOT / "data" / "lmdb" / "chbmit_eval10"))
    ap.add_argument("--analysis", default=str(ROOT / "artifacts" / "analysis"))
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--only", nargs="+", metavar="ID", help="figure ids (e.g. F10 F11); other captions are kept")
    a = ap.parse_args(argv)
    plt.switch_backend("Agg")
    plt.rcParams.update(RCPARAMS)
    a.out = Path(a.out)
    a.out.mkdir(parents=True, exist_ok=True)
    a.recs = load_records(Path(a.results))
    cap = a.out / "captions.md"
    made = ({ln.split("**")[1]: ln for ln in cap.read_text().splitlines() if ln.startswith("- **")}
            if a.only and cap.exists() else {})
    missing, failed = [], False
    for fid, fn in FIGURES:
        if a.only and fid not in a.only:
            continue
        made.pop(fid, None)
        try:
            stem, caption = fn(a)
            made[fid] = f"- **{fid}** `{stem}`: {caption}"
            print(f"[{fid}] wrote {a.out / stem}.png and .pdf")
        except Skip as e:
            missing.append(f"- {fid}: skipped, {e}")
            print(f"[{fid}] skipped: {e}")
        except (Exception, SystemExit) as e:   # one broken figure must not stop the others
            plt.close("all")
            failed = True
            missing.append(f"- {fid}: FAILED, {type(e).__name__}: {e}")
            print(f"[{fid}] FAILED: {type(e).__name__}: {e}", file=sys.stderr)
    res = Path(a.results).resolve()
    src = res.relative_to(ROOT) if res.is_relative_to(ROOT) else res
    lines = ["# Paper A figure captions", "",
             f"Generated by scripts/figures.py from {src}; PNG ({a.dpi} dpi) and PDF next to this file.", "",
             *(made[fid] for fid, _ in FIGURES if fid in made)]
    if missing:
        lines += ["", "## Not produced in the last run", "", *missing]
    cap.write_text("\n".join(lines) + "\n")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
