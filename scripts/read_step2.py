#!/usr/bin/env python3
"""Read Step 2 (does design C say where to adapt?) with the rule fixed in notes/decisions.md D22.

    .venv/bin/python scripts/read_step2.py --local artifacts/s3-results --dataset chbmit

Gains come from single-group arms minus `lp`, paired by rotation: embed_only, first_block and last
from Step 1 (run_tag S1/S3), single_bXX from Step 2 (S2/S4). Design C scores come from
artifacts/drift/diagC-<model>-<dataset>.json (scripts/diag_c_rotations.py).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
ROTS = tuple(f"rot{i}" for i in range(5))
# Step-1 tag per model: CBraMod Step 1 was re-run under D23 (encoder tap) as S1E/S3E
TAGS = {("chbmit", "biot"): ("S1", "S2"), ("chbmit", "cbramod"): ("S1E", "S2"),
        ("siena", "biot"): ("S3", "S4"), ("siena", "cbramod"): ("S3E", "S4")}
N_BLOCKS = {"biot": 4, "cbramod": 12}


def arm_of(model: str, group: str) -> str:
    last = f"block{N_BLOCKS[model] - 1:02d}"
    return {"embed": "embed_only", "block00": "first_block", last: "last"}.get(group, f"single_b{group[-2:]}")


def d22(rhos: list[float]) -> str:
    r = np.asarray(rhos, dtype=float)
    if r.mean() >= 0.5 and (r > 0).sum() >= len(r) - 1:
        return "design C predicts where to adapt"
    return "no predictive value shown"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--local", default="artifacts/s3-results")
    ap.add_argument("--dataset", default="chbmit")
    args = ap.parse_args()
    roc: dict = {}
    modes: dict = {}
    for p in Path(args.local).rglob("results/*.json"):
        if p.name.startswith(("diag-", "test-index-", "val-index-", "report-")):
            continue
        r = json.loads(p.read_text())
        if (r.get("smoke") or r["dataset"] != args.dataset or r["split"] not in ROTS
                or r.get("run_tag") not in TAGS[(args.dataset, r["model"])] or "linear" not in r["probes"]):
            continue
        cell = (r["model"], r["arm"], r["split"])
        if cell in roc:
            raise SystemExit(f"two records for {cell}; delete the stale one")
        roc[cell] = 100 * r["probes"]["linear"]["test_at_best"]["roc_auc"]
        modes.setdefault(r["model"], set()).add((json.dumps(r["versions"], sort_keys=True),
                                                 r["probes"]["linear"]["spec"].get("backbone_mode")))
    mixed = {m: v for m, v in modes.items() if len(v) > 1}
    if mixed:
        raise SystemExit(f"a model mixes code versions or probe modes: {mixed}")
    lines = [f"# Step 2 (D22), {args.dataset}: gain = single-group ROC - lp ROC, x100", ""]
    for model in ("biot", "cbramod"):
        f = ROOT / "artifacts" / "drift" / f"diagC-{model}-{args.dataset}.json"
        if not f.exists():
            lines.append(f"- {model}: no design-C file {f.name}")
            continue
        diag = json.loads(f.read_text())["splits"]
        groups = [g for g in diag[ROTS[0]]["rms_mean"] if g != "head"]
        rhos, hits, missing = [], 0, []
        for rot in ROTS:
            gain = {g: roc.get((model, arm_of(model, g), rot), np.nan) - roc.get((model, "lp", rot), np.nan)
                    for g in groups}
            missing += [f"{arm_of(model, g)}/{rot}" for g in groups if np.isnan(gain[g])]
            if any(np.isnan(v) for v in gain.values()):
                continue
            score = diag[rot]["rms_mean"]
            rhos.append(float(spearmanr([score[g] for g in groups], [gain[g] for g in groups]).statistic))
            hits += max(groups, key=score.get) == max(groups, key=gain.get)
            lines.append(f"- {model} {rot}: rho {rhos[-1]:+.2f}; C top-1 {max(groups, key=score.get)}, "
                         f"best {max(groups, key=gain.get)} ({max(gain.values()):+.1f})")
        if len(rhos) == len(ROTS):
            lines.append(f"- **{model}: mean rho {np.mean(rhos):+.2f}, top-1 hits {hits}/5 -> {d22(rhos)}**")
        else:
            lines.append(f"- {model}: incomplete, missing {missing}")
    text = "\n".join(lines) + "\n"
    (ROOT / "artifacts" / "tables").mkdir(parents=True, exist_ok=True)
    (ROOT / "artifacts" / "tables" / f"{args.dataset}-step2.md").write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
