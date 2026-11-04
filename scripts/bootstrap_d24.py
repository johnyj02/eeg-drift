#!/usr/bin/env python3
"""D24-D: cluster-bootstrap 95% CIs for the D24 contrasts (descriptive; verdicts stay the D24 rules).

    .venv/bin/python scripts/bootstrap_d24.py

Corrected protocol: resample the 5 rotations with replacement, then the 3 seeds inside each drawn
rotation (rotations are the independent units, D24 review). Paper split: resample the 5 seeds.
Writes artifacts/tables/d24-bootstrap.md.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from read_d24 import ROTS, load

ROOT = Path(__file__).resolve().parents[1]
CONTRASTS = (("last", "lp"), ("last_randinit", "last"), ("lp", "lp_randinit"),
             ("last_randinit", "lp_randinit"), ("all", "last"))
SETS = (("chbmit", "S1E,S1M", False), ("siena", "S3E,S3M", False), ("siena", "S3FE,S3FM", False),
        ("chbmit", "P1E", True))
B = 10_000


def cluster_ci(diffs: list[list[float]], rng: np.random.Generator) -> tuple[float, float, float]:
    """diffs[rotation][seed] -> (mean, lo, hi); two-stage resampling."""
    d = [np.asarray(x, dtype=float) for x in diffs]
    stats = np.empty(B)
    for b in range(B):
        rots = rng.integers(0, len(d), len(d))
        stats[b] = np.mean([rng.choice(d[r], len(d[r])).mean() for r in rots])
    point = float(np.mean([x.mean() for x in d]))
    return point, float(np.quantile(stats, 0.025)), float(np.quantile(stats, 0.975))


def main() -> int:
    rng = np.random.default_rng(20261101)
    lines = ["# D24-D: cluster-bootstrap 95% CIs (ROC-AUC x100, 10,000 resamples)", "",
             "| dataset (tags) | model | head | contrast | mean | 95% CI |", "|---|---|---|---|---|---|"]
    for dataset, tags, paper in SETS:
        roc = load(str(ROOT / "artifacts" / "s3-results"), dataset, set(tags.split(",")))
        for model in ("biot", "cbramod"):
            for probe in sorted({c[3] for c in roc if c[0] == model}):
                for a, b in CONTRASTS:
                    if paper:
                        A, Bv = roc.get((model, a, "paper", probe), {}), roc.get((model, b, "paper", probe), {})
                        seeds = sorted(set(A) & set(Bv))
                        if len(seeds) < 5:
                            continue
                        diffs = [[A[s] - Bv[s] for s in seeds]]   # one cluster: resample seeds only
                    else:
                        cells = [(roc.get((model, a, r, probe), {}), roc.get((model, b, r, probe), {}))
                                 for r in ROTS]
                        if not all(len(set(x) & set(y)) == 3 for x, y in cells):
                            continue
                        diffs = [[x[s] - y[s] for s in sorted(set(x) & set(y))] for x, y in cells]
                    m, lo, hi = cluster_ci(diffs, rng)
                    lines.append(f"| {dataset} ({tags}) | {model} | {probe} | {a} - {b} | {m:+.1f} | "
                                 f"[{lo:+.1f}, {hi:+.1f}] |")
    text = "\n".join(lines) + "\n"
    (ROOT / "artifacts" / "tables" / "d24-bootstrap.md").write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
