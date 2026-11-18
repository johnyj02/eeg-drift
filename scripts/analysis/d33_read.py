#!/usr/bin/env python3
"""Read the converged linear-probe analysis from its manifest and saved records.

python scripts/analysis/d33_read.py [--check-paper]

Reconstructs the eight ROC-AUC contrasts using the frozen rotation/seed units,
margin 3 and the saved Siena train/test ratio. Checks recorded diagnostics;
feature matrices are not included, so it does not recompute training gradients.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "artifacts/analysis/D33"
VARIANTS = ("logreg", "logreg_z")
CS = [1e-4, 1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0]


def summarize(values, ratio):
    values = np.asarray(values, dtype=float)
    assert len(values) == 5
    mean, sd = float(values.mean()), float(values.std(ddof=1))
    dist = stats.t(4)
    result = {"per_unit": values.tolist(), "mean": mean}
    for kind, se in (("t", sd / math.sqrt(5)), ("nb", None if ratio is None else sd * math.sqrt(0.2 + ratio))):
        if se is None:
            result[kind] = None
            continue
        p = max(float(dist.sf((mean + 3) / se)), float(dist.cdf((mean - 3) / se))) if se else float(abs(mean) >= 3)
        ci = [mean - float(dist.ppf(0.975)) * se, mean + float(dist.ppf(0.975)) * se]
        result[kind] = {"ci95": ci, "tost_p": p, "equivalent": p < 0.05, "improvement_demonstrated": ci[0] > 0}
    result["primary"] = "t" if ratio is None else "nb"
    return result


def read():
    manifest = json.loads((OUT / "manifest.json").read_text())
    levels, keys = {}, set()
    candidates, selected = [], []
    for entry in manifest["records"]:
        record = json.loads((ROOT / entry["path"]).read_text())
        assert record["key"] == entry["key"] and record["key"] not in keys
        keys.add(record["key"])
        assert not record["smoke"] and record["model"] == "biot"
        assert set(record["probes"]) == set(VARIANTS)
        assert record["arm"] in ("lp", "last", "last_noise")
        for variant, probe in record["probes"].items():
            assert probe["Cs"] == CS and probe["max_iter"] == 20000
            assert probe["tol"] == 1e-6 and probe["refit_tol"] == 1e-9
            assert probe["grad_tol"] == 1e-5 and probe["stable_tol"] == 0.001
            configs = probe["configs"]
            assert [c["C"] for c in configs] == CS
            for c in configs:
                numerical = (
                    c["n_iter"] < probe["max_iter"] and not c["warned"] and c["grad_inf_norm"] < probe["grad_tol"]
                )
                assert bool(numerical) == c["numerically_converged"]
            winner = max(range(len(configs)), key=lambda i: configs[i]["val_roc_auc"])
            assert probe["selected"]["index"] == winner
            assert probe["selected"]["C"] == CS[winner]
            assert probe["selected"]["at_grid_boundary"] == (winner in (0, len(CS) - 1))
            assert probe["numerically_converged"] == configs[winner]["numerically_converged"]
            assert probe["prediction_stable"] == (abs(probe["val_refit_delta"]) < 0.001)
            key = (record["dataset"], variant, record["split"], record["seed"], record["arm"])
            assert key not in levels
            levels[key] = probe["test_at_best"]["roc_auc"] * 100
            candidates.extend(configs)
            selected.append(probe)
    assert len(keys) == manifest["n_records"] == 60
    assert len(selected) == manifest["n_fits"] == 120 and len(candidates) == 840
    ratio = json.loads((ROOT / "artifacts/analysis/D31/d31.json").read_text())["nb_ratio"]["S3W"]
    contrasts = {}
    for dataset in ("chbmit", "siena"):
        for variant in VARIANTS:
            for comparator in ("lp", "last_noise"):
                units = defaultdict(list)
                for (ds, v, split, seed, arm), value in levels.items():
                    if (ds, v, arm) != (dataset, variant, "last"):
                        continue
                    unit = split if dataset == "siena" else seed
                    units[unit].append(value - levels[(ds, v, split, seed, comparator)])
                assert all(len(u) == (3 if dataset == "siena" else 1) for u in units.values())
                values = [float(np.mean(units[u])) for u in sorted(units)]
                contrasts[f"{dataset}|{variant}|last - {comparator}"] = summarize(
                    values, ratio if dataset == "siena" else None
                )
    diagnostics = {
        "records": len(keys),
        "candidate_fits": len(candidates),
        "selected_fits": len(selected),
        "nonconverged_candidates": sum(not c["numerically_converged"] for c in candidates),
        "nonconverged_selected": sum(not p["numerically_converged"] for p in selected),
        "validation_auc_unstable_selected": sum(not p["prediction_stable"] for p in selected),
        "boundary_selected": sum(p["selected"]["at_grid_boundary"] for p in selected),
        "selected_C_counts": dict(sorted(Counter(p["selected"]["C"] for p in selected).items())),
    }
    return {"analysis": "D33", "nb_ratio": ratio, "diagnostics": diagnostics, "contrasts": contrasts}


def check_paper(result):
    text = (ROOT / "paper/tmlr/sections/s7-main.tex").read_text()
    body = text.split(r"\label{tab:d33}", 1)[1].split(r"\end{tabular}", 1)[0]
    seen = set()
    for line in body.splitlines():
        if not line.startswith(("DL's split,", "Siena rotations")):
            continue
        cells = [c.strip() for c in line.removesuffix(r"\\").split("&")]
        ds = "chbmit" if cells[0].startswith("DL") else "siena"
        variant = "logreg" if cells[1] == "raw" else "logreg_z"
        comparator = "lp" if cells[2] == r"\lastarm$-$\lparm" else "last_noise"
        key = f"{ds}|{variant}|last - {comparator}"
        assert key not in seen
        seen.add(key)
        row = result["contrasts"][key]
        primary = row[row["primary"]]
        ci = primary["ci95"]
        expected = f"{row['mean']:+.2f} [{ci[0]:+.1f}, {ci[1]:+.1f}]".replace("[+", "[")
        assert cells[3].replace("$", "") == expected, (key, cells[3], expected)
        assert cells[4] == ("equivalent" if primary["equivalent"] else "not resolved"), key
    assert len(seen) == 8


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-paper", action="store_true")
    args = parser.parse_args()
    result = read()
    if args.check_paper:
        check_paper(result)
    primary = [r[r["primary"]] for r in result["contrasts"].values()]
    equivalents = sum(r["equivalent"] for r in primary)
    lines = [
        "# Converged linear probes",
        "",
        "Analysis identifier: D33. Selection: `manifest.json`.",
        "",
        "Results are reconstructed from saved ROC-AUC values; numerical diagnostics are checked "
        "against the reported criteria. Training gradients cannot be recomputed "
        "without the omitted features.",
        "",
        f"Primary inference supports equivalence within ±3 in {equivalents}/8 comparisons. "
        "Siena uses dependence-adjusted inference; DL uses seed intervals on one fixed split.",
        "",
        "| Setting | Features | Contrast | Mean | Primary 95% interval | TOST p | Outcome |",
        "|---|---|---|---:|---|---:|---|",
    ]
    for key, row in result["contrasts"].items():
        ds, variant, contrast = key.split("|")
        p = row[row["primary"]]
        ci = p["ci95"]
        lines.append(
            f"| {ds} | {variant} | {contrast} | {row['mean']:+.2f} | "
            f"[{ci[0]:+.2f}, {ci[1]:+.2f}] | {p['tost_p']:.6g} | "
            f"{'equivalent' if p['equivalent'] else 'unresolved'} |"
        )
    lines += [
        "",
        "Recorded diagnostics:",
        "",
        "```json",
        json.dumps(result["diagnostics"], indent=2),
        "```",
        "",
        "The raw records store the solver tolerance, iteration cap and gradient diagnostics. "
        "They do not separately store ftol and gtol. For the pinned scikit-learn 1.6.1 L-BFGS "
        "implementation, gtol equals the passed tol and ftol is 64 times float64 machine epsilon; "
        "these values follow from the implementation, not independent runtime capture.",
        "",
    ]
    (OUT / "d33.json").write_text(json.dumps(result, indent=1) + "\n")
    (OUT / "README.md").write_text("\n".join(lines))
    print(
        f"D33: 60 records, 840 candidate fits, 120 selected models; {equivalents}/8 equivalent "
        "under primary inference. Manifest and recorded diagnostics verified."
    )
    if args.check_paper:
        print("Paper table: 8/8 rows match.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
