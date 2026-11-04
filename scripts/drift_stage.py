#!/usr/bin/env python3
"""drift stage (Mac, no GPU): diag artifacts -> per-layer drift report -> drift_topk arms.

    python scripts/drift_stage.py --model biot --dataset chbmit --run-id drift-v1 \
        --diag s3://.../checkpoints/diag-biot-chb/results/diag-biot-chbmit.json

Streams one tap at a time from S3 (peak disk < 2 GB). Writes
artifacts/drift/<run_id>/<model>-<dataset>.json and configs/drift_arms/<model>-<dataset>.yaml.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from eegdrift.data.store import LocalStore, S3StreamingStore  # noqa: E402
from eegdrift.drift.metrics import (  # noqa: E402
    cka_from_grams,
    gram,
    half,
    per_seed_field,
    rank_stability,
    seed_mean,
    token_mean,
    top_k,
)
from eegdrift.models.registry import Registry  # noqa: E402

ARTIFACTS = "s3://<BUCKET>/<PREFIX>/artifacts/activations"


def _load_json(uri: str) -> dict:
    if uri.startswith("s3://"):
        import boto3  # noqa: PLC0415

        bucket, _, key = uri.removeprefix("s3://").partition("/")
        body = boto3.Session(profile_name="<AWS_PROFILE>").client("s3").get_object(Bucket=bucket, Key=key)
        return json.loads(body["Body"].read())
    return json.loads(Path(uri).read_text())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--run-id", default="drift-v1")
    ap.add_argument("--diag", required=True, help="diag summary JSON (s3:// or local path)")
    ap.add_argument("--local-store", default="", help="LocalStore root instead of S3 (pilot)")
    ap.add_argument("--k", type=int, default=2)
    ap.add_argument("--arms-dir", default=str(ROOT / "configs" / "drift_arms"))
    args = ap.parse_args()
    if args.run_id.endswith("-smoke") and Path(args.arms_dir) == ROOT / "configs" / "drift_arms":
        raise SystemExit("refusing to write smoke-derived arms into configs/drift_arms; pass --arms-dir")

    reg = Registry.load(ROOT)
    diag = _load_json(args.diag)
    store = (LocalStore(args.local_store) if args.local_store
             else S3StreamingStore(f"{ARTIFACTS}/{args.run_id}", profile="<AWS_PROFILE>"))
    # The store root already carries the run_id; cell ids never repeat it.
    frozen = f"{args.model}|{args.dataset}|frozen|target"
    adapted = f"{args.model}|{args.dataset}|adapted_all|target"

    # ---- activation view: CKA(frozen, adapted) per tap, streamed --------------------------------
    cka: dict[str, dict] = {}
    for tap in reg.taps(args.model):
        r0, a0 = store.open(frozen, tap.key)
        r1, a1 = store.open(adapted, tap.key)
        if r0["window_ids"] != r1["window_ids"]:
            raise SystemExit(f"{tap.key}: frozen/adapted windows differ; refusing to compare")
        row = {"depth_frac": tap.depth_frac, "kind": tap.kind,
               "token_mean": cka_from_grams(gram(token_mean(a0)), gram(token_mean(a1))),
               "flat": cka_from_grams(gram(a0), gram(a1))}
        if tap.kind == "post_attn":
            for h in ("spatial", "temporal"):
                row[f"{h}_token_mean"] = cka_from_grams(gram(token_mean(half(a0, h))),
                                                        gram(token_mean(half(a1, h))))
        cka[tap.key] = row
        del a0, a1
        print(f"{tap.key:12s} depth {tap.depth_frac:.3f}  CKA token_mean {row['token_mean']:.4f}  "
              f"flat {row['flat']:.4f}", flush=True)

    # ---- weight view (design A) and gradient view (design C), ranked on SCALE-FREE stats --------
    # D9: under AdamW the plan's relative displacement ranks partly by weight scale, so top-k ranks
    # on Adam coherence (A) and RMS gradient (C); the plan's ratios are reported beside them.
    keys = [g.key for g in reg.groups(args.model) if g.key != "head"]
    disp = [{k: v for k, v in d.items() if k in keys} for d in diag["displacement"].values() if d]
    grad = [{k: v for k, v in d.items() if k in keys} for d in diag["grad_pressure"].values() if d]
    coh, rel = seed_mean(disp, "coherence"), seed_mean(disp, "rel")
    rms, grel = seed_mean(grad, "rms"), seed_mean(grad, "rel")
    top_a, top_c = top_k(coh, args.k), top_k(rms, args.k)
    report = {
        "model": args.model, "dataset": args.dataset, "run_id": args.run_id, "k": args.k,
        "n_seeds_A": len(disp), "n_seeds_C": len(grad), "cka": cka,
        "A_coherence_mean": coh, "A_rel_mean": rel,
        "A_coherence_stability": rank_stability(per_seed_field(disp, "coherence"), keys),
        "A_rel_stability": rank_stability(per_seed_field(disp, "rel"), keys),
        "C_rms_mean": rms, "C_rel_mean": grel,
        "C_rms_stability": rank_stability(per_seed_field(grad, "rms"), keys),
        "top_k_A": top_a, "top_k_C": top_c, "A_C_agree": sorted(top_a) == sorted(top_c),
        "top_k_A_by_rel": top_k(rel, args.k), "top_k_C_by_rel": top_k(grel, args.k),
    }
    mean_disp = coh   # the statistic drift_topk is defined on
    out = ROOT / "artifacts" / "drift" / args.run_id / f"{args.model}-{args.dataset}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))

    # ---- arms the diagnostic defines -------------------------------------------------------------
    # Arm names are scoped to (model, dataset) and carry a `model` field that arms.resolve()
    # enforces: the same group keys exist in both models, so an unscoped name could silently run
    # one model's diagnosed mask on the other.
    scope = f"{args.model}_{args.dataset}"

    def arm(groups: list[str]) -> dict:
        return {"groups": [*groups, "head"], "init": "pretrained", "model": args.model}

    arms = {f"drift_top{j}_{scope}": arm(top_k(mean_disp, j)) for j in (1, args.k)}
    rng = np.random.default_rng(20261015)
    if args.model == "biot":   # 5 groups: enumerate every k-subset (a complete reference)
        for combo in itertools.combinations(keys, args.k):
            arms[f"enum_{'_'.join(combo)}_{scope}"] = arm(list(combo))
    else:                      # 13 groups: 5 distinct random k-subsets, drift_topk excluded
        drawn: set = set()
        while len(drawn) < 5:
            combo = tuple(sorted(rng.choice(keys, size=args.k, replace=False).tolist()))
            if sorted(combo) != sorted(top_a):
                drawn.add(combo)
        for i, combo in enumerate(sorted(drawn)):
            arms[f"random_k{args.k}_{i}_{scope}"] = arm(list(combo))
    arm_file = Path(args.arms_dir) / f"{args.model}-{args.dataset}.yaml"
    arm_file.parent.mkdir(parents=True, exist_ok=True)
    arm_file.write_text("# Written by scripts/drift_stage.py from the design-A diagnostic. Do not edit.\n"
                        + yaml.safe_dump({"arms": arms}, sort_keys=False))
    print(json.dumps({k: report[k] for k in ("A_coherence_stability", "C_rms_stability", "top_k_A",
                                              "top_k_C", "A_C_agree", "top_k_A_by_rel")}, indent=2))
    print(f"wrote {out}\nwrote {arm_file} ({len(arms)} arms)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
