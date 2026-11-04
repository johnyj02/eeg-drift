#!/usr/bin/env python3
"""Read Step 1 (corrected protocol) with the rules fixed in notes/decisions.md D17 and D18.

    aws s3 sync s3://<bucket>/<PREFIX>/checkpoints/ artifacts/s3-results \
        --exclude '*' --include '*/results/*.json'
    .venv/bin/python scripts/read_step1.py --local artifacts/s3-results [--run-tag S1]

ROC-AUC x100, paired by rotation, linear probe, val-selected epoch. Writes
artifacts/tables/<dataset>-<run-tag>.md.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ARMS = ("lp", "last", "first", "first_block", "embed_only", "first_noise", "all", "last_randinit",
        "lp_randinit")
# (a, b, label): verdict on a - b with the paired rule (D18, D19)
CONTRASTS = (("first", "last", "primary: first - last"),
             ("first_block", "last", "depth, equal params: first_block - last"),
             ("embed_only", "lp", "embedding alone: embed_only - lp"),
             ("first", "first_noise", "needs EEG data: first - first_noise"),
             ("last", "lp", "Paper A: last - lp"),
             ("last_randinit", "last", "Paper A: last_randinit - last"))
ROTS = tuple(f"rot{i}" for i in range(5))


def paired(d: list[float], thr: float = 3.0) -> str:
    """D18 rule for a paired difference a - b over rotations."""
    x = np.asarray(d, dtype=float)
    need = len(x) - 1   # 4 of 5
    if x.mean() > thr and (x > 0).sum() >= need:
        return "first term wins"
    if x.mean() < -thr and (x < 0).sum() >= need:
        return "second term wins"
    return "no difference shown"


def d19(d: list[float]) -> str:
    """D19 rule for first - first_noise (three outcomes, unlike the generic paired rule)."""
    if paired(d) == "first term wins":
        return "the gain needs EEG data"
    return "perturbation alone explains it" if abs(float(np.mean(d))) <= 3 else "unclear"


def d17(last_r: list[float], lp_r: list[float]) -> str:
    d = np.asarray(last_r) - np.asarray(lp_r)
    if abs(d.mean()) <= 3:
        return "random features explain it"
    if d.mean() > 3 and (d > 0).sum() >= len(d) - 1:
        return "SSL adds to random init"
    return "neither rule met"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--local", default="artifacts/s3-results")
    ap.add_argument("--run-tag", default="S1")
    ap.add_argument("--models", default="biot,cbramod")
    ap.add_argument("--dataset", default="chbmit", help="chbmit | siena")
    args = ap.parse_args()
    roc: dict = defaultdict(dict)
    pr: dict = defaultdict(dict)
    seen: dict = {}
    versions: dict = defaultdict(set)
    for p in Path(args.local).rglob("results/*.json"):
        if p.name.startswith(("diag-", "test-index-", "val-index-", "report-")):
            continue
        r = json.loads(p.read_text())
        if (r.get("smoke") or r.get("run_tag") != args.run_tag or r.get("labels") != "overlap"
                or r["dataset"] != args.dataset or r["split"] not in ROTS or "linear" not in r["probes"]):
            continue
        cell = (r["model"], r["arm"], r["split"])
        if seen.setdefault(cell, r["key"]) != r["key"]:
            raise SystemExit(f"two records for {cell}: {seen[cell]} and {r['key']}; delete the stale one")
        versions[(r["model"], r["split"])].add((r["eval_hash"], json.dumps(r["versions"], sort_keys=True)))
        versions[(r["model"], "all")].add((json.dumps(r["versions"], sort_keys=True),
                                          r["probes"]["linear"]["spec"].get("backbone_mode")))
        t = r["probes"]["linear"]["test_at_best"]
        roc[(r["model"], r["arm"])][r["split"]] = 100 * t["roc_auc"]
        pr[(r["model"], r["arm"])][r["split"]] = 100 * t["pr_auc_trapz"]
    lines = [f"# Step 1 ({args.run_tag}): corrected protocol, ROC-AUC x100 (PR-AUC in brackets)", "",
             "| model | arm | " + " | ".join(ROTS) + " | mean |", "|---|---|" + "---|" * 6]
    missing = []
    for model in args.models.split(","):
        for arm in ARMS:
            cell = roc.get((model, arm), {})
            missing += [f"{model}/{arm}/{k}" for k in ROTS if k not in cell]
            vals = [f"{cell[k]:.1f} ({pr[(model, arm)][k]:.1f})" if k in cell else "-" for k in ROTS]
            mean = f"{np.mean(list(cell.values())):.1f}" if cell else "-"
            lines.append(f"| {model} | {arm} | " + " | ".join(vals) + f" | {mean} |")
    lines += ["", "## Verdicts (D17, D18)"]
    for model in args.models.split(","):
        def d(a: str, b: str, model=model) -> list[float] | None:
            A, B = roc.get((model, a), {}), roc.get((model, b), {})
            return [A[k] - B[k] for k in ROTS] if all(k in A and k in B for k in ROTS) else None
        for a, b, name in CONTRASTS:
            v = d(a, b)
            rule = (d19 if b == "first_noise" else paired) if v else None
            lines.append(f"- {model} {name}: " + (f"mean {np.mean(v):+.1f}, per rotation "
                         f"{', '.join(f'{x:+.1f}' for x in v)} -> **{rule(v)}**" if v and rule else "incomplete"))
        v = d("all", "last")
        lines.append(f"- {model} all - last (reference): " + (f"mean {np.mean(v):+.1f}" if v else "incomplete"))
        lr, lp = roc.get((model, "last_randinit"), {}), roc.get((model, "lp_randinit"), {})
        ok = all(k in lr and k in lp for k in ROTS)
        lines.append(f"- {model} D17: " + (f"**{d17([lr[k] for k in ROTS], [lp[k] for k in ROTS])}**"
                                          if ok else "incomplete"))
    mixed = {k: v for k, v in versions.items() if len(v) > 1}
    if mixed:
        raise SystemExit(f"arms within a rotation disagree on eval hash or code versions: {mixed}")
    if missing:
        lines += ["", f"MISSING {len(missing)} cells: {', '.join(missing)}"]
    text = "\n".join(lines) + "\n"
    out = ROOT / "artifacts" / "tables"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{args.dataset}-{args.run_tag}.md").write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
