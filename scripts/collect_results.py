#!/usr/bin/env python3
"""Pull every (arm, seed) result from the S3 checkpoint prefixes and print the arms table.

    .venv/bin/python scripts/collect_results.py --dataset chbmit [--split paper] [--local DIR]

One row per (model, arm, probe variant): mean ± SEM over seeds of the test metrics at the
validation-selected epoch ("best", what upstream reports) and at the last epoch. Parity and
strong probes are different result types and never share a table (D6). Writes
artifacts/tables/<dataset>-<split>.json and .md.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BUCKET, PREFIX = "<BUCKET>", "<PREFIX>/checkpoints/"

# The paper's Table 1 (LP vs SA), for the comparability column. SA = their `last` arm.
PAPER = {
    ("biot", "lp"): {"bal_acc": 50.74, "pr_auc": 1.53, "roc_auc": 46.93},
    ("biot", "last"): {"bal_acc": 52.71, "pr_auc": 31.52, "roc_auc": 83.08},
    ("cbramod", "lp"): {"bal_acc": 57.87, "pr_auc": 17.35, "roc_auc": 54.14},
    ("cbramod", "last"): {"bal_acc": 61.37, "pr_auc": 24.62, "roc_auc": 83.67},
}


def records(local: str | None) -> list[dict]:
    if local:
        return [json.loads(p.read_text()) for p in Path(local).rglob("results/*.json")
                if not p.name.startswith(("diag-", "test-index-"))]
    import boto3  # noqa: PLC0415

    s3 = boto3.Session(profile_name="<AWS_PROFILE>").client("s3")
    out = []
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=BUCKET, Prefix=PREFIX):
        for o in page.get("Contents", []):
            name = o["Key"].rsplit("/", 1)[1]
            skip = name.startswith(("diag-", "test-index-"))
            if "/results/" in o["Key"] and name.endswith(".json") and not skip:
                out.append(json.loads(s3.get_object(Bucket=BUCKET, Key=o["Key"])["Body"].read()))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="chbmit")
    ap.add_argument("--split", default="paper")
    ap.add_argument("--local", default="")
    ap.add_argument("--run-tag", default="", help="'' = wave 1; one table per tag, never mixed")
    args = ap.parse_args()
    recs = [r for r in records(args.local or None)
            if r["dataset"] == args.dataset and r["split"] == args.split and not r.get("smoke")
            and r.get("run_tag", "") == args.run_tag]
    if not recs:
        print("no results yet", file=sys.stderr)
        return 1
    seen: dict = {}
    for r in recs:   # one record per (model, arm, seed); identical reruns collapse by key
        seen[(r["model"], r["arm"], r["seed"], r["key"])] = r
    cells: dict = defaultdict(list)
    for (model, arm, _seed, _k), r in seen.items():
        for variant, p in r["probes"].items():
            cells[(model, arm, variant)].append(p)
    rows = []
    for (model, arm, variant), ps in sorted(cells.items()):
        row = {"model": model, "arm": arm, "probe": variant, "n_seeds": len(ps)}
        for when in ("test_at_best", "test_last"):
            for m in ("bal_acc", "roc_auc", "pr_auc_trapz", "avg_precision"):
                v = np.array([p[when][m] for p in ps if m in p[when]]) * 100
                if len(v):
                    sem = v.std(ddof=1) / np.sqrt(len(v)) if len(v) > 1 else float("nan")
                    row[f"{when}.{m}"] = (round(float(v.mean()), 2), round(float(sem), 2))
        row["paper"] = PAPER.get((model, arm)) if variant == "mlp_fullft" else None
        rows.append(row)
    out = ROOT / "artifacts" / "tables"
    out.mkdir(parents=True, exist_ok=True)
    stem = f"{args.dataset}-{args.split}" + (f"-{args.run_tag}" if args.run_tag else "")
    (out / f"{stem}.json").write_text(json.dumps(rows, indent=2))
    lines = [f"# {args.dataset} / {args.split}: test metrics x100, mean ± SEM over seeds", "",
             "| model | arm | probe | seeds | bal_acc | ROC-AUC | PR-AUC (trapz) | AP | paper bal/PR/ROC |",
             "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        def f(k: str, row=r) -> str:
            v = row.get(f"test_at_best.{k}")
            return f"{v[0]:.2f} ± {v[1]:.2f}" if v else "-"
        paper = r["paper"]
        ptxt = f"{paper['bal_acc']}/{paper['pr_auc']}/{paper['roc_auc']}" if paper else ""
        lines.append(f"| {r['model']} | {r['arm']} | {r['probe']} | {r['n_seeds']} | {f('bal_acc')} | "
                     f"{f('roc_auc')} | {f('pr_auc_trapz')} | {f('avg_precision')} | {ptxt} |")
    text = "\n".join(lines) + "\n"
    (out / f"{stem}.md").write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
