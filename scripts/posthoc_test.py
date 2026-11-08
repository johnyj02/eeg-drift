#!/usr/bin/env python3
"""Re-score saved per-window test predictions under three test protocols. No GPU, no retraining.

    .venv/bin/python scripts/posthoc_test.py --dataset chbmit

  upstream   all 16,964 test windows, upstream labels (what the paper reports)
  dedup      grid windows only (drops the overlapping oversampled seizure windows)
  fixed      grid windows only, label = 1 if the window OVERLAPS any seizure (upstream labels a
             window 1 only if a seizure START or END index falls strictly inside it)

The probe itself was still TRAINED on upstream labels, so `fixed` corrects the test labels only.
Writes artifacts/tables/<dataset>-posthoc.md.
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.metrics import auc, precision_recall_curve, roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from eegdrift.data.chbmit import overlap_label  # noqa: E402

BUCKET, PREFIX = "<BUCKET>", "<PREFIX>/checkpoints/"
WIN = 10 * 256


def pr_trapz(y, s) -> float:
    p, r, _ = precision_recall_curve(y, s)
    return float(auc(r, p))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="chbmit")
    ap.add_argument("--run-tag", default="")
    args = ap.parse_args()
    if args.run_tag.startswith("S"):
        sys.exit("corrected-protocol runs are already overlap-labelled and grid-only: use read_step1.py")
    import boto3  # noqa: PLC0415

    s3 = boto3.Session(profile_name="<AWS_PROFILE>").client("s3")
    get = lambda k: s3.get_object(Bucket=BUCKET, Key=k)["Body"].read()  # noqa: E731
    keys = [o["Key"] for p in s3.get_paginator("list_objects_v2").paginate(Bucket=BUCKET, Prefix=PREFIX)
            for o in p.get("Contents", []) if "/results/" in o["Key"]]
    # true [onset, offset) bounds, the same table and rule as the corrected protocol (D18)
    seizures = json.loads((ROOT / "configs" / "chbmit_seizures.json").read_text())
    index_cache: dict = {}
    cells: dict = defaultdict(list)
    for k in keys:
        name = k.rsplit("/", 1)[1]
        if not name.endswith(".json") or name.startswith(("diag-", "test-index-", "val-index-", "report-")):
            continue
        rec = json.loads(get(k))
        if (rec.get("smoke") or rec["dataset"] != args.dataset or rec["split"] != "paper"
                or rec.get("run_tag", "") != args.run_tag):
            continue
        idx_key = k.rsplit("/", 1)[0] + "/" + rec["test_index"]
        if idx_key not in index_cache:
            index_cache[idx_key] = json.loads(get(idx_key))
        tindex = index_cache[idx_key]
        grid = np.array(["-grid-" in t["key"] for t in tindex])
        fixed = np.array([overlap_label({"file": t["key"].rsplit("-", 2)[0], "n_samples": WIN,
                                         "start": int(t["key"].rsplit("-", 2)[2])}, seizures)
                          for t in tindex])
        for variant in rec["probes"]:
            arr = np.load(io.BytesIO(get(k[:-5] + f".{variant}.npz")))
            y, s = arr["y_test"].astype(int), arr["scores_best"]
            row = {}
            for proto, mask, labels in (("upstream", np.ones_like(grid), y), ("dedup", grid, y),
                                        ("fixed", grid, fixed)):
                yy, ss = labels[mask], s[mask]
                row[proto] = (100 * roc_auc_score(yy, ss), 100 * pr_trapz(yy, ss), int(yy.sum()), len(yy))
            cells[(rec["model"], rec["arm"], variant)].append(row)
    lines = ["# CHB-MIT test set re-scored post hoc (val-selected epoch, x100, mean ± SEM over seeds)", "",
             "| model | arm | probe | n | ROC upstream | PR upstream | ROC dedup | PR dedup "
             "| ROC fixed | PR fixed |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for (model, arm, variant), rows in sorted(cells.items()):
        def ms(proto: str, i: int, rows=rows) -> str:
            v = np.array([r[proto][i] for r in rows])
            sem = v.std(ddof=1) / np.sqrt(len(v)) if len(v) > 1 else float("nan")
            return f"{v.mean():.1f} ± {sem:.1f}"
        lines.append(f"| {model} | {arm} | {variant} | {len(rows)} | {ms('upstream', 0)} | {ms('upstream', 1)} | "
                     f"{ms('dedup', 0)} | {ms('dedup', 1)} | {ms('fixed', 0)} | {ms('fixed', 1)} |")
    r0 = next(iter(cells.values()))[0]
    lines += ["", f"positives / windows: upstream {r0['upstream'][2]}/{r0['upstream'][3]}, "
              f"dedup {r0['dedup'][2]}/{r0['dedup'][3]}, fixed {r0['fixed'][2]}/{r0['fixed'][3]}"]
    text = "\n".join(lines) + "\n"
    out = ROOT / "artifacts" / "tables"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{args.dataset}-posthoc{'-' + args.run_tag if args.run_tag else ''}.md").write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
