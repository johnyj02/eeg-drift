#!/usr/bin/env python3
"""D25-E2: a seeded symlink farm of ~2K released CHB-MIT eval pickles, for CPU runs of main.py.

Our own script (reads the released outputs, imports nothing from upstream). Per split: N_POS
positives drawn from the '-s-' seizure windows (label 1 by construction, checked) and N_NEG
grid windows whose label is checked to be 0. Layout <farm>/{train,val,test}/<name>.pkl -> target.

    python e2_make_farm.py --seg "$HOME/released/run/\\$WORK/.../processed_seg" --farm ~/released/e2/farm
"""

import argparse
import json
import os
import pickle
from pathlib import Path

import numpy as np

PLAN = {"train": (100, 1400), "val": (50, 250), "test": (50, 250)}   # (positives, negatives)

ap = argparse.ArgumentParser()
ap.add_argument("--seg", required=True)
ap.add_argument("--farm", required=True)
ap.add_argument("--seed", type=int, default=2)
args = ap.parse_args()
rng = np.random.default_rng(args.seed)
farm = Path(args.farm)
summary = {}
for split, (n_pos, n_neg) in PLAN.items():
    names = sorted(os.listdir(Path(args.seg) / split))
    s_files = [n for n in names if "-s-" in n]
    grid = [n for n in names if "-s-" not in n]
    picked = {}
    for pool, want, label in ((s_files, n_pos, 1), (grid, n_neg, 0)):
        for n in rng.permutation(pool):
            if sum(v == label for v in picked.values()) >= want:
                break
            with open(Path(args.seg) / split / n, "rb") as f:
                y = int(pickle.load(f)["y"])
            if y == label:
                picked[n] = y
    (farm / split).mkdir(parents=True, exist_ok=True)
    for n in picked:
        os.symlink(Path(args.seg) / split / n, farm / split / n)
    summary[split] = {"n": len(picked), "pos": sum(picked.values())}
(farm / "farm.json").write_text(json.dumps({"seed": args.seed, "splits": summary}, indent=2))
print(json.dumps(summary))
