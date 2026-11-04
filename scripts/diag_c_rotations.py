#!/usr/bin/env python3
"""Design C (gradient pressure of the frozen pretrained model, label-free) per rotation.

    SM_CHANNEL_DATA=~/dxdata/lmdb python scripts/diag_c_rotations.py --model cbramod --dataset chbmit

Each split uses its OWN adaptation pool (load_ssl drops the rotation's test subjects), so the
ranking is leak-free per rotation. No adaptation, no probe, CPU is enough. Writes
artifacts/drift/diagC-<model>-<dataset>.json with per-seed RMS gradients, the seed-mean ranking
per split and Kendall tau of every split's ranking against the first split's.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import torch
from scipy.stats import kendalltau

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from eegdrift.adapt import seed_everything  # noqa: E402
from eegdrift.data.store import LocalStore  # noqa: E402
from eegdrift.drift.metrics import grad_pressure  # noqa: E402
from eegdrift.objectives import objective_for  # noqa: E402
from eegdrift.study import Context, drift_sample, load_ssl  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--dataset", default="chbmit")
    ap.add_argument("--splits", default="", help="default: paper,rot0..rot4 (chbmit); rot0..rot4 (siena)")
    ap.add_argument("--seeds", default="42,123,2021,3407,8888")
    args = ap.parse_args()
    splits = args.splits.split(",") if args.splits else (
        ["paper"] * (args.dataset == "chbmit") + [f"rot{i}" for i in range(5)])
    data_root = Path(os.path.expanduser(os.environ.get("SM_CHANNEL_DATA", ROOT / "data" / "lmdb")))
    out_dir = ROOT / "artifacts" / "drift"
    ctx = Context(root=ROOT, data_root=data_root, out=out_dir / "diagC-scratch",
                  artifacts=LocalStore(out_dir / "diagC-scratch"), device=torch.device("cpu"),
                  log=print)
    scale = ctx.adapt_cfg["scale"][args.dataset]
    res: dict = {"model": args.model, "dataset": args.dataset, "splits": {}}
    for split in splits:
        xs, _, _ = drift_sample(ctx, args.dataset, load_ssl(ctx, args.dataset, split))
        per_seed = {}
        for seed in map(int, args.seeds.split(",")):
            seed_everything(seed)
            m = ctx.registry.build(args.model, "pretrained")
            gp = grad_pressure(m, objective_for(m, ctx.adapt_cfg["mask_ratio"]), xs, scale, ctx.device)
            per_seed[seed] = {g: v["rms"] for g, v in gp.items()}
            print(f"[diagC] {args.model} {split} s{seed}: top3 "
                  f"{sorted(per_seed[seed], key=per_seed[seed].get, reverse=True)[:3]}", flush=True)
        groups = [g for g in next(iter(per_seed.values())) if g != "head"]   # head: not an arm group
        mean = {g: float(np.mean([s[g] for s in per_seed.values()])) for g in groups}
        res["splits"][split] = {"rms_per_seed": per_seed, "rms_mean": mean,
                                "ranking": sorted(groups, key=mean.get, reverse=True)}
    ref = res["splits"][splits[0]]["rms_mean"]
    for r in res["splits"].values():
        groups = list(ref)
        r["tau_vs_" + splits[0]] = float(kendalltau([ref[g] for g in groups],
                                                    [r["rms_mean"][g] for g in groups]).statistic)
    path = out_dir / f"diagC-{args.model}-{args.dataset}.json"
    path.write_text(json.dumps(res, indent=1))
    print(json.dumps({s: (r["ranking"][:3], round(r[f"tau_vs_{splits[0]}"], 3))
                      for s, r in res["splits"].items()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
