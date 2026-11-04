#!/usr/bin/env python3
"""D25-E18: effect of training labels and split (P1F, S1U), and E13(d) finished with these cells.

    .venv/bin/python scripts/analysis/e18_labels_split.py [--reps 10000]

Cells (fixed probe: encoder tap, eval-mode backbone, probe v4; ROC-AUC x100 at the val-selected
epoch, test_at_best, as in D24):
                          upstream labels (dups in val/test)   overlap labels (grid val/test)
  paper split, 5 seeds    P1E                                  P1F (new)
  rotations, seed S_r     S1U (new)                            D24-A at S_r (BIOT S1M, CBraMod S1E)
Rule (E18, pre-registered in D25): a fix "removes the gain" for a contrast if the rule reads a win
before the fix and "no difference shown" after. The rule is D24-B on the paper split (paired by
seed: mean > 3 and same sign in >= 4/5) and D18 at 1 seed on rotations (same thresholds over the 5
rotations); both are read_step1.paired. A win is "first term wins" or "second term wins".
Reading choices fixed here before any P1F or S1U aggregate was computed (3 raw records seen):
- Fixes = the edges of the 2x2: labels on the paper split (P1E -> P1F, both heads); split under
  upstream labels (P1E -> S1U); labels on rotations (S1U -> D24-A@S_r); split under overlap labels
  (P1F -> D24-A@S_r); both (P1E -> D24-A@S_r). Off the paper split: linear head only.
- Contrasts: last - lp (the D24-B pre-registered SA gain), last_randinit - lp (the paper's SA - LP:
  the released-path SA gain of E13(d)), last_randinit - last, lp - lp_randinit, last_randinit -
  lp_randinit (paired rule; the D17 string is shown next to it).
- Other outcomes are named "win kept", "win reversed", "no win before" (rule not applicable).
Descriptive (E13(d) rule; post hoc):
- Waterfall: paper -> unreproduced residual -> released path -> init -> probe -> test scoring ->
  train labels (P1F) -> split (D24-A, 3 seeds per rotation = E13's endpoint). Released path, init,
  probe and scoring cells are E13(a)'s npz re-scorings (artifacts/analysis/decompose/
  posthoc-paper.json, checked against the records and against waterfall.json).
- Shapley, fixed probe: init x labels x split (linear; rotations at seed S_r; 8 cells) and init x
  labels (MLP head; paper split; 4 cells). E13's init x probe x protocol stays as computed there:
  the released-code probe has no overlap-label paper cell and no upstream-label rotation cell, so
  init x probe x labels x split cannot be filled.
- CIs: 95% percentile, resampling the 5 seeds (paper split) and the 5 rotations (seed means kept)
  jointly across cells, 10,000 reps; contrast CIs are bootstrap_d24.cluster_ci (D24-D). These are
  NOT E13's event/subject CIs (P1F and S1U have no npz here) and under-cover at n = 5.
Own loader: read_d24.load stops on the val-index-*.json files the 2026-11-01 runs added.
Writes artifacts/analysis/E18/e18.{md,json}, waterfall-{linear,mlp_fullft}.png, shapley.png.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "analysis"))
from bootstrap_d24 import cluster_ci  # noqa: E402
from decompose import DOWN, GRID, INK, INK2, MUTED, PAPER, SURF, TOTAL, UP, plt, shapley, style  # noqa: E402
from read_step1 import d17, paired  # noqa: E402

RES = ROOT / "artifacts" / "s3-results"
DEC = ROOT / "artifacts" / "analysis" / "decompose"
OUT = ROOT / "artifacts" / "analysis" / "E18"
SEEDS = (42, 123, 2021, 3407, 8888)
ROTS = tuple(f"rot{i}" for i in range(5))
ROT_SEEDS = {r: (SEEDS[i], 1000 + i, 2000 + i) for i, r in enumerate(ROTS)}
ARMS = ("lp", "last", "last_randinit", "lp_randinit")
HEADS = ("linear", "mlp_fullft")
TAGS = {"P1E": "upstream", "P1F": "overlap", "S1U": "upstream", "S1M": "overlap", "S1E": "overlap"}
# source -> (kind, label); DS = D24-A at seed S_r, D3 = D24-A seed means (3 per rotation)
SOURCES = {
    "P1E": ("paper", "upstream"),
    "P1F": ("paper", "overlap"),
    "S1U": ("rot", "upstream"),
    "DS": ("rot", "overlap"),
    "D3": ("rot", "overlap"),
}
CONTRASTS = (
    ("last", "lp"),
    ("last_randinit", "lp"),
    ("last_randinit", "last"),
    ("lp", "lp_randinit"),
    ("last_randinit", "lp_randinit"),
)
PREREG = {
    ("paper", "last", "lp"): "D24-B",
    ("rot", "last", "lp"): "D24-A",
    ("rot", "last_randinit", "last"): "D24-A",
    ("rot", "lp", "lp_randinit"): "D24-A",
    ("rot", "last_randinit", "lp_randinit"): "D17",
}
FIXES = (
    ("labels, paper split", "P1E", "P1F"),
    ("split, upstream labels", "P1E", "S1U"),
    ("labels, rotations", "S1U", "DS"),
    ("split, overlap labels", "P1F", "DS"),
    ("labels + split", "P1E", "DS"),
)
WIN = ("first term wins", "second term wins")
FCOL = {"init": "#2a78d6", "labels": "#eb6834", "split": "#1baf7a"}  # categorical slots 1-3


def e18(before: str, after: str) -> str:
    if before not in WIN:
        return "no win before" + (f" (after: {after})" if after in WIN else "")
    if after == "no difference shown":
        return "REMOVES THE GAIN"
    return "win kept" if after == before else "win reversed"


# ---------------------------------------------------------------- records and checks
def is_grid(key: str) -> bool:
    return key.rsplit("-", 2)[1] == "grid"


def load() -> tuple[dict, list[str]]:
    """-> roc[(source, model, head, arm)] = 5 parts (per seed / per rotation), and check lines."""
    raw: dict = {}
    meta: dict = defaultdict(set)
    recs: dict = {}
    for p in RES.rglob("results/*.json"):
        if p.name.startswith(("diag-", "test-index-", "val-index-", "report-")):
            continue
        r = json.loads(p.read_text())
        tag = r.get("run_tag") if isinstance(r, dict) else None
        if tag not in TAGS or r["dataset"] != "chbmit" or r.get("smoke") or r["arm"] not in ARMS:
            continue
        kind = "paper" if r["split"] == "paper" else "rot"
        if (tag[:2] == "P1") != (kind == "paper"):
            raise SystemExit(f"{p.name}: tag {tag} on split {r['split']}")
        if r.get("labels") != TAGS[tag]:
            raise SystemExit(f"{p.name}: labels {r.get('labels')} != {TAGS[tag]}")
        for head, res in r["probes"].items():
            sp = res["spec"]
            if (
                r["versions"]["probe"] != 4
                or sp.get("backbone_mode") != "eval"
                or sp.get("tap", "encoder") != "encoder"
            ):
                raise SystemExit(f"{p.name}: not a probe-v4 eval-mode encoder-tap record")
            k = (tag, r["model"], head, r["arm"], r["split"], r["seed"])
            if k in raw:
                raise SystemExit(f"two records for {k}")
            raw[k] = 100 * res["test_at_best"]["roc_auc"]
        recs[(tag, r["model"], r["arm"], r["split"], r["seed"])] = (p, r)
        grp = "D24A" if tag in ("S1M", "S1E") else tag
        meta[("eval", grp, r["split"])].add(r["eval_hash"])
        meta[("versions", "all", "")].add(json.dumps(r["versions"], sort_keys=True))
        meta[("test_index", grp, r["split"])].add(r["test_index"])
    lines = []

    def need(tag: str, model: str, head: str, arm: str, split: str, seed: int) -> float:
        k = (tag, model, head, arm, split, seed)
        if k not in raw:
            raise SystemExit(f"MISSING record {k}")
        return raw[k]

    roc: dict = {}
    for model in ("biot", "cbramod"):
        for arm in ARMS:
            for head in HEADS:
                for tag in ("P1E", "P1F"):
                    roc[(tag, model, head, arm)] = np.array(
                        [need(tag, model, head, arm, "paper", s) for s in SEEDS]
                    )
            roc[("S1U", model, "linear", arm)] = np.array(
                [need("S1U", model, "linear", arm, r, ROT_SEEDS[r][0]) for r in ROTS]
            )
            d3 = [
                [
                    need(
                        "S1E" if model == "cbramod" and s == ROT_SEEDS[r][0] else "S1M", model, "linear", arm, r, s
                    )
                    for s in ROT_SEEDS[r]
                ]
                for r in ROTS
            ]
            roc[("DS", model, "linear", arm)] = np.array([x[0] for x in d3])
            roc[("D3", model, "linear", arm)] = np.array([np.mean(x) for x in d3])
            roc[("D3seeds", model, "linear", arm)] = d3
    n = defaultdict(int)
    for tag, *_ in raw:
        n[tag] += 1
    lines.append(
        "- records (probe results) found: "
        + ", ".join(f"{t} {n[t]}" for t in TAGS)
        + "; expected and present: P1E/P1F 2 models x 4 arms x 5 seeds x 2 heads = 80 each, "
        "S1U 2 x 4 x 5 rotations at S_r x linear = 40, D24-A (S1M + S1E) 2 x 4 x 5 x 3 seeds = 120 used"
    )
    for k, v in sorted(meta.items()):
        if len(v) != 1:
            raise SystemExit(f"{k} not unique: {v}")
    lines.append(
        "- one eval_hash per (source, split): "
        + "; ".join(f"{g} {s} {next(iter(v))}" for (what, g, s), v in sorted(meta.items()) if what == "eval")
    )
    lines.append(
        f"- code versions identical in every record: {next(iter(meta[('versions', 'all', '')]))}; "
        "all eval-mode backbone, encoder tap (P1E/S1M/S1E predate the tap field; probe v4 = encoder)"
    )
    # SSL side identical between the before/after records of a fix (same seed and split family)
    diff_spec, pairs, extra = 0, 0, set()
    for (tag, model, arm, split, seed), (_, r) in recs.items():
        other = {"P1F": "P1E", "S1U": "S1E" if model == "cbramod" else "S1M"}.get(tag)
        if other and (other, model, arm, split, seed) in recs:
            pairs += 1
            o = recs[(other, model, arm, split, seed)][1]
            a, b = r["adapt_spec"], o["adapt_spec"]
            extra |= set(a) ^ set(b)
            diff_spec += any(a[k] != b[k] for k in set(a) & set(b))
    if diff_spec:
        raise SystemExit(
            f"{diff_spec} of {pairs} before/after pairs differ in adapt_spec (SSL data, ckpt, groups)"
        )
    lines.append(
        f"- adapt_spec (SSL data hash, checkpoint, groups, schedule) identical in all {pairs} "
        "P1E/P1F and D24-A/S1U pairs: only the probe's labels and split differ"
        + (f" (keys present on one side only, not compared: {sorted(extra)})" if extra else "")
    )
    # test and val windows: overlap = grid subset of upstream, same subjects
    for split in ("paper", *ROTS):
        up = "P1E" if split == "paper" else "S1U"
        ov = "P1F" if split == "paper" else "D24A"
        ti = {
            g: json.loads(next(RES.rglob(f"results/{next(iter(meta[('test_index', g, split)]))}")).read_text())
            for g in (up, ov)
        }
        grid_up = [t["key"] for t in ti[up] if is_grid(t["key"])]
        same = grid_up == [t["key"] for t in ti[ov]]
        subj = {t["subject"] for t in ti[up]} == {t["subject"] for t in ti[ov]}
        if not (same and subj):
            raise SystemExit(f"{split}: overlap test windows are not the grid subset of the upstream ones")
        msg = (
            f"- {split} test: {up} {len(ti[up])} windows ({len(ti[up]) - len(grid_up)} oversampled duplicates), "
            f"{ov} {len(ti[ov])} = its grid subset, same subjects"
        )
        vals = {}
        for g in (up, ov):
            h = next(iter(meta[("eval", g, split)]))
            f = next(RES.rglob(f"results/val-index-chbmit-{split}-{h}.json"), None)
            if f is not None:
                vals[g] = json.loads(f.read_text())
        if up in vals:
            msg += f"; val {up} {len(vals[up])} ({sum(not is_grid(t['key']) for t in vals[up])} duplicates)"
        if ov in vals:
            msg += f", {ov} {len(vals[ov])} ({sum(not is_grid(t['key']) for t in vals[ov])} duplicates)"
        elif split != "paper":
            msg += f", {ov} val index not saved (pre-2026-11-01 records)"
        lines.append(msg)
    return roc, lines


def e13_cells(roc: dict) -> tuple[dict, list[str]]:
    """Per-seed E13(a) cells (npz re-scorings) from posthoc-paper.json, checked against the records."""
    ph = json.loads((DEC / "posthoc-paper.json").read_text())["cells"]
    out = {}
    worst = 0.0
    for model in ("biot", "cbramod"):
        for head in HEADS:
            for arm in ("lp", "last", "last_randinit"):
                out[("W1", model, head, arm)] = np.array(
                    ph[f"W1/{model}/{head}/{arm}"]["upstream"]["roc"]["parts"]
                )
            for arm in ARMS:
                c = ph[f"P1E/{model}/{head}/{arm}"]
                out[("P1Efixed", model, head, arm)] = np.array(c["fixed"]["roc"]["parts"])
                worst = max(
                    worst,
                    float(np.abs(np.array(c["upstream"]["roc"]["parts"]) - roc[("P1E", model, head, arm)]).max()),
                )
    if worst > 1e-6:
        raise SystemExit(f"posthoc-paper.json P1E values differ from the records by {worst}")
    return out, [f"- E13(a) P1E per-seed ROC (upstream scoring) = records within {worst:.1e}"]


# ---------------------------------------------------------------- quantities with joint bootstrap reps
@dataclass
class Q:
    point: float
    reps: np.ndarray
    parts: np.ndarray | None = None  # per seed / rotation when the operands share units
    unit: str = ""

    def __sub__(self, o: Q) -> Q:
        same = self.parts is not None and o.parts is not None and self.unit == o.unit
        return Q(
            self.point - o.point,
            self.reps - o.reps,
            self.parts - o.parts if same else None,
            self.unit if same else "",
        )

    def ci(self) -> tuple[float, float]:
        lo, hi = np.quantile(self.reps, [0.025, 0.975])
        return float(lo), float(hi)

    def fmt(self, signed: bool = True) -> str:
        f = "+.1f" if signed else ".1f"
        lo, hi = self.ci()
        sem = f" ± {self.parts.std(ddof=1) / np.sqrt(len(self.parts)):.1f}" if self.parts is not None else ""
        return f"{self.point:{f}}{sem} [{lo:{f}}, {hi:{f}}]"

    def js(self) -> dict:
        return {
            "point": self.point,
            "ci95": list(self.ci()),
            "parts": None if self.parts is None else self.parts.tolist(),
            "unit": self.unit,
        }


class Boot:
    def __init__(self, R: int, rng: np.random.Generator):
        self.idx = {"paper": rng.integers(0, 5, (R, 5)), "rot": rng.integers(0, 5, (R, 5))}

    def q(self, parts, unit: str) -> Q:
        parts = np.asarray(parts, float)
        return Q(float(parts.mean()), parts[self.idx[unit]].mean(1), parts, unit)


# ---------------------------------------------------------------- report
def ms(v: np.ndarray, signed: bool = False) -> str:
    f = "+.1f" if signed else ".1f"
    return f"{v.mean():{f}} ± {v.std(ddof=1) / np.sqrt(len(v)):.1f} ({', '.join(f'{x:{f}}' for x in v)})"


def rule_part(roc: dict, rng: np.random.Generator, md: list, js: dict) -> list[tuple]:
    md += [
        "## Cells (ROC-AUC x100; mean ± SEM over 5 seeds (paper) or 5 rotations; per seed / rotation in brackets)",
        "",
        "| source | model | head | lp | last | last_randinit | lp_randinit |",
        "|---|---|---|---|---|---|---|",
    ]
    srcs = [(s, h) for s in SOURCES for h in HEADS if h == "linear" or SOURCES[s][0] == "paper"]
    for s, h in srcs:
        for model in ("biot", "cbramod"):
            md.append(f"| {s} | {model} | {h} | " + " | ".join(ms(roc[(s, model, h, a)]) for a in ARMS) + " |")
            js.setdefault("cells", {})[f"{s}/{model}/{h}"] = {a: roc[(s, model, h, a)].tolist() for a in ARMS}
    md += [
        "",
        "D3 = D24-A per-rotation means over its 3 seeds (reference; the pre-registered D24-A read). "
        "DS = D24-A at seed S_r only, the E18 comparator for S1U.",
        "",
        "## Contrasts and rule strings (paper split: D24-B; rotations: D18 paired rule at 1 seed; D3: D24-A)",
        "",
        "| source | model | head | contrast | pre-reg. | mean ± SEM (per unit) | 95% CI (D24-D) | rule | D17 |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    rules = {}
    for s, h in srcs:
        kind = SOURCES[s][0]
        for model in ("biot", "cbramod"):
            for a, b in CONTRASTS:
                d = roc[(s, model, h, a)] - roc[(s, model, h, b)]
                if s == "D3":
                    A, B = roc[("D3seeds", model, h, a)], roc[("D3seeds", model, h, b)]
                    diffs = [[x - y for x, y in zip(ra, rb, strict=True)] for ra, rb in zip(A, B, strict=True)]
                else:
                    diffs = [list(d)] if kind == "paper" else [[x] for x in d]
                m, lo, hi = cluster_ci(diffs, rng)
                rule = paired(list(d))
                dd = (
                    d17(roc[(s, model, h, a)], roc[(s, model, h, b)])
                    if (a, b) == ("last_randinit", "lp_randinit")
                    else ""
                )
                rules[(s, model, h, a, b)] = (rule, d)
                md.append(
                    f"| {s} | {model} | {h} | {a} - {b} | {PREREG.get((kind, a, b), '-')} | {ms(d, True)} | "
                    f"[{lo:+.1f}, {hi:+.1f}] | {rule} | {dd} |"
                )
                js.setdefault("contrasts", {})[f"{s}/{model}/{h}/{a}-{b}"] = {
                    "parts": d.tolist(),
                    "mean": float(d.mean()),
                    "ci95": [lo, hi],
                    "rule": rule,
                    "d17": dd or None,
                }
    md += [
        "",
        "## E18 verdict table: before -> after for each fix",
        "",
        "Last column (descriptive, post hoc): the same rule with the after-cell D24-A read at its 3-seed rotation "
        "means (D3) instead of seed S_r, because BIOT random-init arms vary by up to 19 ROC across seeds within a "
        "rotation (see Seed sensitivity).",
        "",
        "| fix | model | head | contrast | before: mean -> rule | after: mean -> rule | E18 rule output | "
        "after = D3 (descriptive) |",
        "|---|---|---|---|---|---|---|---|",
    ]
    out = []
    for name, s0, s1 in FIXES:
        for model in ("biot", "cbramod"):
            for h in HEADS:
                if h != "linear" and "paper" not in name:
                    continue
                for a, b in CONTRASTS:
                    (r0, d0), (r1, d1) = rules[(s0, model, h, a, b)], rules[(s1, model, h, a, b)]
                    o = e18(r0, r1)
                    alt = ""
                    if s1 == "DS":
                        r3, d3 = rules[("D3", model, h, a, b)]
                        alt = f"{d3.mean():+.1f} -> {r3}: {e18(r0, r3)}"
                    out.append((name, model, h, f"{a} - {b}", s0, d0, r0, s1, d1, r1, o))
                    md.append(
                        f"| {name} ({s0} -> {s1}) | {model} | {h} | {a} - {b} | {d0.mean():+.1f} -> {r0} | "
                        f"{d1.mean():+.1f} -> {r1} | **{o}** | {alt} |"
                    )
                    js.setdefault("e18", []).append(
                        {
                            "fix": name,
                            "before": s0,
                            "after": s1,
                            "model": model,
                            "head": h,
                            "contrast": f"{a}-{b}",
                            "before_rule": r0,
                            "after_rule": r1,
                            "before_parts": d0.tolist(),
                            "after_parts": d1.tolist(),
                            "output": o,
                            "descriptive_after_D3": alt or None,
                        }
                    )
    md += [
        "",
        "## Seed sensitivity (descriptive): SD over the 3 D24-A seeds within each rotation, linear head",
        "",
    ]
    for model in ("biot", "cbramod"):
        for arm in ARMS:
            sd = np.array(roc[("D3seeds", model, "linear", arm)]).std(1, ddof=1)
            md.append(
                f"- {model} {arm}: {', '.join(f'{x:.1f}' for x in sd)} (rotation SD of the seed means "
                f"{roc[('D3', model, 'linear', arm)].std(ddof=1):.1f})"
            )
            js.setdefault("seed_sd", {})[f"{model}/{arm}"] = sd.tolist()
    md.append("")
    return out


def value(roc: dict, e13: dict, B: Boot, model: str, head: str, arm: str, cell: str) -> Q:
    src = {"released": "W1", "init": "W1", "probe": "P1E", "scoring": "P1Efixed"}.get(cell, cell)
    if cell == "released":
        arm = "last_randinit" if arm == "last" else arm
    tab = e13 if src in ("W1", "P1Efixed") else roc
    return B.q(tab[(src, model, head, arm)], SOURCES.get(src, ("paper",))[0])


def waterfall_part(roc: dict, e13: dict, B: Boot, md: list, js: dict) -> None:
    md += [
        "## E13(d) waterfall, finished with P1F (descriptive)",
        "",
        "Steps: released path (W1 last_randinit, upstream scoring) -> init (W1 last) -> probe (P1E) -> test "
        "scoring (P1E re-scored: grid windows, overlap labels; E13(a)) -> train labels (P1F: probe trained and "
        "validated on overlap labels, same test windows and labels as the scoring step) -> split (D24-A "
        "rotations, 3-seed means; E13's endpoint). SA gain = SA arm - lp of the same cell. ROC x100; [95% CI: "
        "seeds / rotations resampled jointly, NO test-window resampling, so narrower than E13's event/subject "
        "CIs for the same cells (decompose/waterfall.md); P1F has no npz here].",
        "",
    ]
    w13 = json.loads((DEC / "waterfall.json").read_text())
    steps = [
        ("released path", "released"),
        ("+ init (pretrained)", "init"),
        ("+ probe (fixed)", "probe"),
        ("+ test scoring (post hoc)", "scoring"),
        ("+ train labels (P1F)", "P1F"),
        ("+ split (rotations, D24-A)", "D3"),
    ]
    fig_rows = []
    for head in HEADS:
        st = steps if head == "linear" else steps[:-1]
        for model in ("biot", "cbramod"):
            for kind in ("level", "gain"):
                vals = []
                for _, c in st:
                    v = value(roc, e13, B, model, head, "last", c)
                    if kind == "gain":
                        v = v - value(roc, e13, B, model, head, "lp", c)
                    vals.append(v)
                old = w13[f"{model}/{head}/{kind}"]["steps"]
                for i, o in enumerate(old):  # E13's cells must come out unchanged
                    j = i if i < 4 else 5
                    if j < len(vals) and abs(o["value"]["point"] - vals[j].point) > 1e-6:
                        raise SystemExit(
                            f"{model}/{head}/{kind} step {o['step']}: {vals[j].point} != E13 {o['value']['point']}"
                        )
                pv = PAPER[model]
                pval = pv["sa"] if kind == "level" else pv["sa"] - pv["lp"]
                psem = pv["sa_sem"] if kind == "level" else float(np.hypot(pv["sa_sem"], pv["lp_sem"]))
                resid = Q(pval - vals[0].point, pval - vals[0].reps)
                md += [
                    f"### {model}, {head} head, SA {kind}",
                    "",
                    f"- paper {pval:.2f} (± {psem:.2f}); unreproduced residual {resid.fmt()}",
                ]
                rec = {"paper": pval, "paper_sem": psem, "residual": resid.js(), "steps": []}
                for i, ((n, _), v) in enumerate(zip(st, vals, strict=True)):
                    step = (v - vals[i - 1]) if i else None
                    md.append(f"- {n}: {v.fmt(kind == 'gain')}" + (f"; step {step.fmt()}" if step else ""))
                    rec["steps"].append({"step": n, "value": v.js(), "delta": step.js() if step else None})
                if head == "linear":
                    alt = value(roc, e13, B, model, head, "last", "DS")
                    if kind == "gain":
                        alt = alt - value(roc, e13, B, model, head, "lp", "DS")
                    md.append(
                        f"- split step at seed S_r only (D24-A@S_r, the Shapley cell): {alt.fmt(kind == 'gain')}; "
                        f"step {(alt - vals[4]).fmt()}"
                    )
                    rec["split_at_Sr"] = alt.js()
                else:
                    md.append(
                        "- split: not run with the MLP head in E18 (E25's S1L carries mlp_fullft; not used here)"
                    )
                md.append("")
                js.setdefault("waterfall", {})[f"{model}/{head}/{kind}"] = rec
                fig_rows.append((model, head, kind, pval, psem, resid, st, vals))
    for head in HEADS:
        draw_waterfall([r for r in fig_rows if r[1] == head], head)


def draw_waterfall(rows: list, head: str) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(14, 7.5), facecolor=SURF)
    for ax, (model, _, kind, pval, psem, resid, steps, vals) in zip(axes.ravel(), rows, strict=True):
        style(ax, f"{model}, {head} head: SA {kind}", "ROC-AUC x100" if kind == "level" else "SA - LP, ROC x100")
        lo, hi = resid.ci()
        # (label, bottom, height, colour, hatched, error centre, CI low, CI high, text)
        bars = [
            ("paper", 0, pval, TOTAL, False, pval, pval - psem, pval + psem, f"{pval:.1f}"),
            (
                "unreproduced\nresidual",
                pval,
                -resid.point,
                SURF,
                True,
                vals[0].point,
                pval - hi,
                pval - lo,
                f"{resid.point:+.1f}",
            ),
            (
                "released\npath (ours)",
                0,
                vals[0].point,
                TOTAL,
                False,
                *[vals[0].point] * 3,
                f"{vals[0].point:.1f}",
            ),
        ]
        for i in range(1, len(vals)):
            d = vals[i] - vals[i - 1]
            dlo, dhi = d.ci()
            lab = steps[i][0].replace("+ ", "").replace(" (", "\n(")
            bars.append(
                (
                    lab,
                    vals[i - 1].point,
                    d.point,
                    UP if d.point >= 0 else DOWN,
                    False,
                    vals[i].point,
                    vals[i - 1].point + dlo,
                    vals[i - 1].point + dhi,
                    f"{d.point:+.1f}",
                )
            )
        flo, fhi = vals[-1].ci()
        bars.append(
            (
                "corrected\n(ours)" if head == "linear" else "paper split,\noverlap labels",
                0,
                vals[-1].point,
                TOTAL,
                False,
                vals[-1].point,
                flo,
                fhi,
                f"{vals[-1].point:.1f}",
            )
        )
        top = max(max(b[1], b[1] + b[2], b[7]) for b in bars)
        bot = min(0, *(min(b[1], b[1] + b[2], b[6]) for b in bars))
        pad = 0.03 * (top - bot)
        for x, (_, b0, h, col, hatch, c, elo, ehi, txt) in enumerate(bars):
            ax.bar(
                x,
                h,
                bottom=b0,
                color=col,
                width=0.6,
                edgecolor=MUTED if hatch else SURF,
                hatch="///" if hatch else None,
                lw=0.8 if hatch else 2,
            )
            if ehi > elo:
                ax.errorbar([x], [c], yerr=[[c - elo], [ehi - c]], color=INK, capsize=2, lw=1)
            ax.text(x, max(b0, b0 + h, ehi) + pad, txt, ha="center", fontsize=7, color=INK2)
        ax.set_ylim(bot - pad, top + 4 * pad)
        ax.set_xticks(range(len(bars)), [b[0] for b in bars], fontsize=6.5)
        ax.axhline(0, color="#c3c2b7", lw=0.8)
    fig.suptitle(
        f"E18 / E13(d) waterfall, {head} head: paper -> residual -> released path -> fixes in order "
        "(blue up, red down; 95% CI over seeds / rotations only, no test-window resampling)",
        fontsize=9,
        color=INK,
        x=0.01,
        ha="left",
    )
    fig.tight_layout()
    fig.savefig(OUT / f"waterfall-{head}.png", dpi=110)
    plt.close(fig)


def shapley_part(roc: dict, B: Boot, md: list, js: dict) -> None:
    md += [
        "## Shapley values, fixed probe (descriptive)",
        "",
        "Start cell = fixed probe, random init, upstream labels, paper split (P1E last_randinit). Factors "
        "switched to the fix: init (last_randinit -> last), labels "
        "(upstream -> overlap, in train, val and test), split (paper split, 5 seeds -> 5 rotations at seed S_r). "
        "SA gain = SA arm - lp. The MLP head has no rotation cells in E18 (init x labels only). [95% CI: seeds / "
        "rotations resampled jointly].",
        "",
    ]
    lv = {"labels": ("upstream", "overlap"), "split": ("paper", "rot")}
    src = {
        ("upstream", "paper"): "P1E",
        ("overlap", "paper"): "P1F",
        ("upstream", "rot"): "S1U",
        ("overlap", "rot"): "DS",
    }
    entries = []
    for head, factors in (("linear", ("init", "labels", "split")), ("mlp_fullft", ("init", "labels"))):
        for model in ("biot", "cbramod"):
            for kind in ("level", "gain"):
                cells = {}
                for k in range(len(factors) + 1):
                    for S in combinations(factors, k):
                        lab = lv["labels"]["labels" in S]
                        spl = lv["split"]["split" in S] if "split" in factors else "paper"
                        s = src[(lab, spl)]
                        v = B.q(roc[(s, model, head, "last" if "init" in S else "last_randinit")], SOURCES[s][0])
                        if kind == "gain":
                            v = v - B.q(roc[(s, model, head, "lp")], SOURCES[s][0])
                        cells[frozenset(S)] = v
                phi_p = shapley({k: c.point for k, c in cells.items()}, factors)
                phi_r = shapley({k: c.reps for k, c in cells.items()}, factors)
                total = cells[frozenset(factors)].point - cells[frozenset()].point
                assert abs(sum(phi_p.values()) - total) < 1e-9
                ci = {f: [float(x) for x in np.quantile(phi_r[f], [0.025, 0.975])] for f in factors}
                key = f"{model}/{head}/{kind}"
                md.append(
                    f"- {key} (total {total:+.1f}; start {cells[frozenset()].point:.1f} -> fixed "
                    f"{cells[frozenset(factors)].point:.1f}): "
                    + ", ".join(f"{f} {phi_p[f]:+.1f} [{ci[f][0]:+.1f}, {ci[f][1]:+.1f}]" for f in factors)
                )
                md.append(
                    "  - cells: "
                    + "; ".join(
                        f"{'+'.join(f for f in factors if f in k) or 'released'} {c.point:.1f}"
                        for k, c in sorted(cells.items(), key=lambda t: len(t[0]))
                    ).replace("released", "start")
                )
                js.setdefault("shapley", {})[key] = {
                    "factors": list(factors),
                    "total": total,
                    "cells": {"+".join(f for f in factors if f in k) or "start": c.js() for k, c in cells.items()},
                    "phi": {f: {"point": phi_p[f], "ci95": ci[f]} for f in factors},
                }
                entries.append((key, factors, phi_p, ci))
    md.append("")
    fig, ax = plt.subplots(
        figsize=(10, 0.3 * sum(len(e[1]) for e in entries) + 0.25 * len(entries) + 1.2), facecolor=SURF
    )
    style(
        ax,
        "E18 Shapley values, fixed probe (share of the start -> fixed change; 95% CI over seeds / rotations only)",
    )
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.grid(axis="y", visible=False)
    pos, labs, y = [], [], 0.0
    for key, factors, phi, ci in entries:
        for f in factors:
            ax.barh(y, phi[f], color=FCOL[f], height=0.7)
            ax.errorbar([phi[f]], [y], xerr=[[phi[f] - ci[f][0]], [ci[f][1] - phi[f]]], color=INK, capsize=2, lw=1)
            ax.text(max(ci[f][1], 0) + 0.5, y, f"{phi[f]:+.1f}", va="center", fontsize=6.5, color=INK2)
            pos.append(y)
            labs.append(f"{key}: {f}")
            y += 1
        y += 0.6
    ax.set_yticks(pos, labs, fontsize=7)
    ax.invert_yaxis()
    ax.axvline(0, color="#c3c2b7", lw=0.8)
    ax.set_xlabel("ROC-AUC x100", fontsize=8, color=INK2)
    fig.tight_layout()
    fig.savefig(OUT / "shapley.png", dpi=110)
    plt.close(fig)


def verdict_sentence(out: list) -> list[str]:
    lines = ["## Pre-registered verdict (E18 rule, applied as written)", ""]
    for name, *_ in FIXES:
        hit = [
            f"{m} {h} {c} ({r0} -> {r1})"
            for n, m, h, c, _, _, r0, _, _, r1, o in out
            if n == name and o == "REMOVES THE GAIN"
        ]
        wins = [f"{m} {h} {c}" for n, m, h, c, _, _, r0, *_ in out if n == name and r0 in WIN]
        lines.append(
            f"- The {name} fix removes the gain for: {'; '.join(hit) if hit else 'no contrast'}"
            f" (wins before the fix: {len(wins)}; {'; '.join(wins) if wins else 'none'})."
        )
    lines.append("")
    return lines


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=10_000)
    args = ap.parse_args()
    assert e18("first term wins", "no difference shown") == "REMOVES THE GAIN"
    assert e18("second term wins", "first term wins") == "win reversed"
    assert e18("no difference shown", "first term wins").startswith("no win before")
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20261101)
    roc, checks = load()
    e13, c2 = e13_cells(roc)
    B = Boot(args.reps, rng)
    md = [
        "# E18: training labels and split (P1F, S1U); E13(d) finished",
        "",
        f"<!-- generated by scripts/analysis/e18_labels_split.py --reps {args.reps}; D25-E18 -->",
        "",
        "## Checks",
        "",
        *checks,
        *c2,
        "",
    ]
    js: dict = {"reps": args.reps, "checks": checks + c2}
    out = rule_part(roc, rng, md, js)
    md[4:4] = verdict_sentence(out)
    js["verdict"] = verdict_sentence(out)[2:-1]
    waterfall_part(roc, e13, B, md, js)
    shapley_part(roc, B, md, js)
    (OUT / "e18.md").write_text("\n".join(md) + "\n")
    (OUT / "e18.json").write_text(json.dumps(js, indent=1, default=float))
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
