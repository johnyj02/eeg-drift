#!/usr/bin/env python3
"""Write a smaller window store from a big one (pilot data for the Mac, §6.0).

    # the exact parity SSL subsample study.load_ssl would draw
    python scripts/subset_store.py --src chbmit_ssl30 --dst pilot/chbmit_ssl30 --parity 4174 --seed 4174
    # eval: every positive per split + seeded negatives up to a per-split cap
    python scripts/subset_store.py --src chbmit_eval10 --dst pilot/chbmit_eval10 --caps 6000,1500,2000
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from eegdrift.data.windows import WindowStore, WindowWriter  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--dst", required=True)
    ap.add_argument("--parity", type=int, default=0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--caps", default="")
    args = ap.parse_args()
    src = WindowStore(args.src)
    if args.parity:
        idx = np.sort(np.random.default_rng(args.seed).choice(len(src), args.parity, replace=False))
    else:
        caps = dict(zip(("train", "val", "test"), map(int, args.caps.split(",")), strict=True))
        rng = np.random.default_rng(args.seed)
        idx = []
        for part, cap in caps.items():
            pos = [i for i, r in enumerate(src.index) if r["split"] == part and r["label"] == 1]
            neg = [i for i, r in enumerate(src.index) if r["split"] == part and r["label"] == 0]
            idx += pos + rng.choice(neg, size=max(0, min(len(neg), cap - len(pos))), replace=False).tolist()
        idx = sorted(idx)
    Path(args.dst).parent.mkdir(parents=True, exist_ok=True)
    w = WindowWriter(args.dst, src.meta["dtype"], src.shape, src.meta["description"] + " [PILOT SUBSET]")
    w.put_many((src.index[i], src.get(int(i))) for i in idx)
    w.close({k: v for k, v in src.meta.items() if k not in ("n", "description")}
            | {"subset_of": args.src, "pilot": True})
    print(f"{args.dst}: {len(idx)} windows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
