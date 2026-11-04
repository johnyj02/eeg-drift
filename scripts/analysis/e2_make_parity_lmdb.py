#!/usr/bin/env python3
"""D25-E2/E5: write the 4,174-window CHB-MIT SSL store in the RELEASED LMDB format.

Our own script (imports nothing from upstream). Selection = exactly our parity subsample
(D4: np.sort(default_rng(4174).choice(len(store), 4174, replace=False)) over our chbmit_ssl30
index order, as scripts/subset_store.py and study.load_ssl draw it). Released format, as read by
its dataset_pretrain/pretraining_data_loader.py: value = pickle of a float32 [16, 30, 200] uV
array under the window key; key b"__keys__" = pickle of the key list.

    ~/released/eea-env/bin/python -I e2_make_parity_lmdb.py --src ~/dxdata/lmdb/chbmit_ssl30 \
        --dst ~/released/e2/ssl_4174.lmdb

Run it with numpy < 2 (the released env): numpy 2 pickles reference numpy._core, which the
released env (numpy 1.26.4) cannot unpickle (first attempt failed exactly so).
"""

import argparse
import json
import pickle
from pathlib import Path

import lmdb
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--src", required=True)
ap.add_argument("--dst", required=True)
ap.add_argument("--n", type=int, default=4174)
ap.add_argument("--seed", type=int, default=4174)
args = ap.parse_args()

src = lmdb.open(args.src, readonly=True, lock=False, subdir=True)
with src.begin() as txn:
    meta = json.loads(txn.get(b"__meta__"))
    index = json.loads(txn.get(b"__index__"))
dtype, shape = np.dtype(meta["dtype"]), tuple(meta["shape"])
idx = np.sort(np.random.default_rng(args.seed).choice(len(index), args.n, replace=False))
keys = [index[i]["key"] for i in idx]
if Path(args.dst).exists():
    raise SystemExit(f"refusing to overwrite {args.dst}")
dst = lmdb.open(args.dst, map_size=1 << 36)
with src.begin() as rt, dst.begin(write=True) as wt:
    for k in keys:
        x = np.frombuffer(rt.get(k.encode()), dtype=dtype).reshape(shape).astype(np.float32)
        wt.put(k.encode(), pickle.dumps(x, protocol=pickle.HIGHEST_PROTOCOL))
    wt.put(b"__keys__", pickle.dumps(keys, protocol=pickle.HIGHEST_PROTOCOL))
dst.sync()
dst.close()
subjects = sorted({index[i]["case"] for i in idx})
print(json.dumps({"dst": args.dst, "n": len(keys), "seed": args.seed, "src_n": len(index),
                  "cases": subjects, "first_keys": keys[:3]}))
