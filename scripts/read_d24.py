#!/usr/bin/env python3
"""Read the D24 runs (eval-mode probe, encoder tap) with the rules fixed in notes/decisions.md D24.

    # A: corrected protocol, 3 seeds per rotation (CBraMod's first seed comes from S1E)
    .venv/bin/python scripts/read_d24.py --dataset chbmit --tags S1E,S1M
    .venv/bin/python scripts/read_d24.py --dataset siena --tags S3E,S3M      # S3FE,S3FM for filtered
    # E26: standardized probe, seed S_r only
    .venv/bin/python scripts/read_d24.py --dataset chbmit --tags S1Z --seeds-per-rot 1
    # D27-B: the same tag at 3 seeds; --out keeps the E26 table in artifacts/tables untouched
    .venv/bin/python scripts/read_d24.py --dataset chbmit --tags S1Z --out artifacts/analysis/D27B/S1Z.md
    # B: the paper's split, 5 seeds, both heads
    .venv/bin/python scripts/read_d24.py --dataset chbmit --tags P1E --paper

Only probe-v4, eval-mode records are used. Writes artifacts/tables/d24-<dataset>-<tags>.md.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from read_step1 import d17, paired

ROOT = Path(__file__).resolve().parents[1]
ROTS = tuple(f"rot{i}" for i in range(5))
ARMS = ("lp", "lp_randinit", "last", "last_randinit", "all")
CONTRASTS = (("last", "lp", "SA helps? last - lp"),
             ("last_randinit", "last", "random init beats pretrained? last_randinit - last"),
             ("lp", "lp_randinit", "pretrained features beat random? lp - lp_randinit"))


def ms(v) -> str:
    v = np.asarray(v, dtype=float)
    sem = v.std(ddof=1) / np.sqrt(len(v)) if len(v) > 1 else float("nan")
    return f"{v.mean():.1f} ± {sem:.1f} (n={len(v)})"


def load(local: str, dataset: str, tags: set[str]) -> dict:
    """(model, arm, split, probe) -> {seed: roc x100}; refuses non-v4 or non-eval records."""
    out: dict = defaultdict(dict)
    same: dict = defaultdict(set)   # (model, split) -> eval data / labels / adapt code seen
    for p in Path(local).rglob("results/*.json"):
        if p.name.startswith(("diag-", "test-index-", "val-index-", "report-")):
            continue
        r = json.loads(p.read_text())
        if r.get("smoke") or r["dataset"] != dataset or r.get("run_tag") not in tags:
            continue
        same[(r["model"], r["split"])].add((r["eval_hash"], r.get("labels"), r["versions"]["adapt"]))
        for probe, res in r["probes"].items():
            if r["versions"]["probe"] != 4 or res["spec"].get("backbone_mode") != "eval":
                raise SystemExit(f"{p.name}: not a probe-v4 eval-mode record")
            cell = (r["model"], r["arm"], r["split"], probe)
            if r["seed"] in out[cell]:
                raise SystemExit(f"two records for {cell} seed {r['seed']}")
            out[cell][r["seed"]] = 100 * res["test_at_best"]["roc_auc"]
    mixed = {k: v for k, v in same.items() if len(v) > 1}
    if mixed:
        raise SystemExit(f"tags mix eval data, labels or adapt code within a rotation: {mixed}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--local", default="artifacts/s3-results")
    ap.add_argument("--dataset", default="chbmit")
    ap.add_argument("--tags", required=True)
    ap.add_argument("--paper", action="store_true", help="paper split, paired by seed")
    ap.add_argument("--seeds-per-rot", type=int, default=3, help="1 for S_r-only tags (E26 S1Z/S3Z/S3FZ)")
    ap.add_argument("--out", help="output .md (default artifacts/tables/d24-<dataset>-<tags>.md)")
    args = ap.parse_args()
    roc = load(args.local, args.dataset, set(args.tags.split(",")))
    lines = [f"# D24, {args.dataset}, tags {args.tags}: ROC-AUC x100, eval-mode probe, encoder tap", ""]
    for model in ("biot", "cbramod"):
        probes = sorted({c[3] for c in roc if c[0] == model})
        for probe in probes:
            lines.append(f"## {model}, {probe} head")
            if args.paper:
                for arm in ARMS:
                    v = roc.get((model, arm, "paper", probe), {})
                    if v:
                        lines.append(f"- {arm}: {ms(list(v.values()))}")
                for a, b, name in CONTRASTS:
                    A, B = roc.get((model, a, "paper", probe), {}), roc.get((model, b, "paper", probe), {})
                    seeds = sorted(set(A) & set(B))
                    if len(seeds) == 5:
                        d = [A[s] - B[s] for s in seeds]
                        # D24-B pre-registers only the SA gain; the others are descriptive
                        verdict = f"**{paired(d)}**" if a == "last" else "(descriptive, not pre-registered)"
                        lines.append(f"- {name}: {ms(d)}, per seed {', '.join(f'{x:+.1f}' for x in d)} "
                                     f"-> {verdict}")
                continue
            per_rot: dict = {}
            for arm in ARMS:
                cells = [roc.get((model, arm, r, probe), {}) for r in ROTS]
                if all(len(c) == args.seeds_per_rot for c in cells):
                    per_rot[arm] = [float(np.mean(list(c.values()))) for c in cells]
                    allruns = [x for c in cells for x in c.values()]
                    lines.append(f"- {arm}: per-rotation seed means "
                                 f"{', '.join(f'{x:.1f}' for x in per_rot[arm])}; over rotations "
                                 f"{ms(per_rot[arm])}; over runs (seeds not independent) {ms(allruns)}")
                else:
                    lines.append(f"- {arm}: INCOMPLETE, seeds per rotation {[len(c) for c in cells]}")
            for a, b, name in CONTRASTS:
                if a in per_rot and b in per_rot:
                    d = [x - y for x, y in zip(per_rot[a], per_rot[b], strict=True)]
                    lines.append(f"- {name}: mean {np.mean(d):+.1f}, per rotation "
                                 f"{', '.join(f'{x:+.1f}' for x in d)} -> **{paired(d)}**")
            if "last_randinit" in per_rot and "lp_randinit" in per_rot:
                lines.append(f"- D17: **{d17(per_rot['last_randinit'], per_rot['lp_randinit'])}**")
            if "all" in per_rot and "last" in per_rot:
                ref = np.mean(per_rot["all"]) - np.mean(per_rot["last"])
                lines.append(f"- all - last (reference): {ref:+.1f}")
    text = "\n".join(lines) + "\n"
    default = ROOT / "artifacts" / "tables" / f"d24-{args.dataset}-{args.tags.replace(',', '+')}.md"
    out = Path(args.out) if args.out else default
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
