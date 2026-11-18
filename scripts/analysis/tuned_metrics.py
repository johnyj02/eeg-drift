#!/usr/bin/env python3
"""Recompute D31 ROC/AP and D32 dose controls from saved selected metrics.

CPU only. D31 is checked against d28_read.py --d31, using its saved train/test
ratios for the rotation correction. D32 uses that same Siena ratio. No ROC
margin or gain classification is applied to either precision-recall metric.
Pass --paper to synchronize generated manuscript tables after reading records.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
TAGS31 = ("P1W", "P1QW", "S1W", "S3W", "S3FW")
TAGS32 = ("S3LRW2", "S3LRW5")
METRICS = ("roc_auc", "avg_precision", "pr_auc_trapz")
VARIANTS = ("grid", "grid_z")
SEEDS = (42, 123, 2021, 3407, 8888)
NAMES = {
    "P1W": "DL's split",
    "P1QW": "DL's split, q95",
    "S1W": "CHB-MIT",
    "S3W": "Siena",
    "S3FW": "Filtered Siena",
    "S3LRW2": "Cell 2",
    "S3LRW5": "Cell 5",
}
CONTRASTS = ("last - lp", "last - last_noise", "last_randinit - last", "lp - lp_randinit")


def summarize(values, ratio, roc):
    u = np.asarray(values, dtype=float)
    mean, sd = float(u.mean()), float(u.std(ddof=1))
    result = {"per_unit": u.tolist(), "mean": mean}
    for kind, se in [("t", sd / math.sqrt(5)), ("nb", None if ratio is None else sd * math.sqrt(0.2 + ratio))]:
        if se is None:
            result[kind] = None
            continue
        dist = stats.t(4)
        ci = [mean - dist.ppf(0.975) * se, mean + dist.ppf(0.975) * se]
        row = {"se": se, "ci95": ci}
        if roc:
            p = (
                max(float(dist.sf((mean + 3) / se)), float(dist.cdf((mean - 3) / se)))
                if se
                else float(abs(mean) >= 3)
            )
            row.update(
                ci90=[mean - dist.ppf(0.95) * se, mean + dist.ppf(0.95) * se],
                tost_p=p,
                label="gain demonstrated"
                if (mean > 3 and ci[0] > 0) or (mean < -3 and ci[1] < 0)
                else "equivalent within +-3"
                if p < 0.05
                else "not resolved",
            )
        result[kind] = row
    return result


def load_records():
    records = {}
    for path in sorted((ROOT / "artifacts/s3-results").glob("*/results/*.json")):
        if path.name.startswith(("diag-", "test-index-", "val-index-", "report-")):
            continue
        r = json.loads(path.read_text())
        if r.get("run_tag") not in TAGS31 + TAGS32 or r.get("smoke"):
            continue
        key = (r["run_tag"], r["model"], r["arm"], r["split"], r["seed"])
        assert key not in records, ("duplicate", key)
        for variant in VARIANTS:
            p = r["probes"][variant]
            g = p["grid"]
            assert (g["version"], g["max_epochs"], len(p["configs"])) == (2, 500, 30), key
            assert g["lr"] == [3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2] and g["weight_decay"] == [
                0,
                1e-4,
                1e-2,
                0.1,
                1,
            ], key
            selected = p["configs"][p["selected"]["index"]]
            assert p["best_val"] == max(c["best_val"] for c in p["configs"]), key
            assert selected["best_val"] == p["best_val"], key
            assert (p["spec"]["backbone_mode"], p["spec"]["tap"]) == ("eval", "encoder"), key
        records[key] = r
    for tag in TAGS31 + TAGS32:
        models = ("biot",) if tag in ("P1QW", *TAGS32) else ("biot", "cbramod")
        arms = (
            ("lp", "last", "last_noise")
            if tag in ("P1QW", *TAGS32)
            else (
                ("lp", "last", "last_randinit", "lp_randinit")
                if tag == "P1W"
                else ("lp", "last", "last_randinit", "lp_randinit", "last_noise")
            )
        )
        expected = {
            (tag, m, a, split, seed)
            for m in models
            for a in arms
            for split in (("paper",) if tag.startswith("P1") else tuple(f"rot{i}" for i in range(5)))
            for seed in (
                SEEDS
                if split == "paper"
                else (SEEDS[int(split[-1])], 1000 + int(split[-1]), 2000 + int(split[-1]))
            )
        }
        assert {k for k in records if k[0] == tag} == expected, ("coverage", tag)
    return records


def read(records, d31):
    grouped = defaultdict(list)
    for (tag, model, arm, split, seed), r in records.items():
        unit = str(seed) if tag.startswith("P1") else split
        for variant in VARIANTS:
            for metric in METRICS:
                grouped[(tag, model, variant, arm, unit, metric)].append(
                    100 * r["probes"][variant]["test_at_best"][metric]
                )
    means = {k: float(np.mean(v)) for k, v in grouped.items()}
    results = {}
    for tag in TAGS31 + TAGS32:
        for model in ("biot", "cbramod"):
            for variant in VARIANTS:
                arms = sorted({k[3] for k in means if k[:3] == (tag, model, variant)})
                if not arms:
                    continue
                units = [str(seed) for seed in SEEDS] if tag.startswith("P1") else [f"rot{i}" for i in range(5)]
                ratio = None if tag.startswith("P1") else d31["nb_ratio"]["S3W" if tag in TAGS32 else tag]
                cell = {}
                for metric in METRICS:
                    levels = {arm: [means[(tag, model, variant, arm, u, metric)] for u in units] for arm in arms}
                    contrasts = {}
                    for name in CONTRASTS:
                        a, b = name.split(" - ")
                        if a in arms and b in arms:
                            contrasts[name] = summarize(
                                np.array(levels[a]) - np.array(levels[b]), ratio, metric == "roc_auc"
                            )
                            if tag in TAGS31 and metric == "roc_auc":
                                saved = d31["contrasts"][f"{tag}|{model}|{variant}"]["contrasts"][name]
                                assert np.allclose(
                                    contrasts[name]["per_unit"], saved["per_unit"], atol=1e-10, rtol=0
                                ), (
                                    tag,
                                    name,
                                )
                                assert np.allclose(
                                    contrasts[name]["t"]["ci95"], saved["t"]["ci95"], atol=1e-10, rtol=0
                                ), (
                                    tag,
                                    name,
                                )
                    cell[metric] = {
                        "arms": {
                            a: {
                                "mean": float(np.mean(v)),
                                "sem": float(np.std(v, ddof=1) / math.sqrt(5)),
                                "per_unit": v,
                            }
                            for a, v in levels.items()
                        },
                        "contrasts": contrasts,
                    }
                results[f"{tag}|{model}|{variant}"] = cell
    return results


def diagnostics(records, tags):
    ps = [p for k, r in records.items() if k[0] in tags for p in r["probes"].values()]
    selected = [p["configs"][p["selected"]["index"]] for p in ps]
    return {
        "records": sum(k[0] in tags for k in records),
        "selected_fits": len(ps),
        "selected_capped": sum(c["epochs_run"] >= 500 for c in selected),
        "any_candidate_capped": sum(any(c["epochs_run"] >= 500 for c in p["configs"]) for p in ps),
        "candidate_capped": sum(c["epochs_run"] >= 500 for p in ps for c in p["configs"]),
        "candidate_fits": sum(len(p["configs"]) for p in ps),
        "selected_max_epochs": max(c["epochs_run"] for c in selected),
    }


def signed(x):
    return f"{x:+.1f}"


def interval(c):
    if c is None:
        return "--"
    endpoints = [f"{x:+.3f}" if 0 < abs(x) < 0.05 else signed(x) for x in c["ci95"]]
    return "[" + ", ".join(endpoints) + "]"


def table(caption, label, columns, rows, spec):
    return "\n".join(
        [
            r"\begin{table}[!htbp]",
            r"\caption{" + caption + "}",
            r"\label{" + label + "}",
            r"\centering\footnotesize",
            r"\setlength{\tabcolsep}{3pt}",
            r"\begin{tabular}{" + spec + "}",
            r"\toprule",
            " & ".join(columns) + r"\\",
            r"\midrule",
            *(" & ".join(row) + r"\\" for row in rows),
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{table}",
            "",
        ]
    )


def render31(d31, metrics, name):
    rows = []
    for key, cell in d31["contrasts"].items():
        if name not in cell["contrasts"]:
            continue
        tag, model, variant = key.split("|")
        c = cell["contrasts"][name]
        adj = c["nb"] or c["t"]
        rows.append(
            [
                NAMES[tag],
                "BIOT" if model == "biot" else "CBraMod",
                "raw" if variant == "grid" else "std",
                signed(c["mean"]),
                interval(c["t"]),
                interval(c["nb"]),
                f"{adj['tost_p']:.3g}",
                "eq."
                if adj["label"] == "equivalent within +-3"
                else "n.r."
                if adj["label"] == "not resolved"
                else "gain",
            ]
        )
    return table(
        "Expanded-search "
        + (r"\lastarm$-$\lparm" if name == "last - lp" else r"\lastarm$-$\lastnoise")
        + r" contrasts in ROC-AUC points. Units are five seeds on DL\textquotesingle s fixed split "
        r"or five rotation means of three seeds. "
        r"NB corrects the rotation intervals for overlapping training folds; it does not apply "
        r"on the fixed split. "
        r"TOST uses $\pm3$ and $\alpha=0.05$; its $p$ and classification use NB where applicable "
        r"(eq. = equivalent; n.r. = unresolved). "
        r"These are per-comparison results, not simultaneous equivalence.",
        "tab:d28" if name == "last - lp" else "tab:d28b",
        ["Setting", "Model", "Features", "Mean", r"95\% $t$", r"95\% NB", "TOST $p$", "Class"],
        rows,
        "lllrrrrl",
    )


def render32(data, metric, compact=False):
    rows = []
    for key, cell in data.items():
        tag, _model, variant = key.split("|")
        if compact:
            lp = cell[metric]["contrasts"]["last - lp"]
            noise = cell[metric]["contrasts"]["last - last_noise"]
            rows.append(
                [
                    NAMES[tag],
                    "raw" if variant == "grid" else "std",
                    signed(lp["mean"]),
                    interval(lp["nb"]),
                    signed(noise["mean"]),
                    interval(noise["nb"]),
                ]
            )
        else:
            for name, c in cell[metric]["contrasts"].items():
                row = [
                    NAMES[tag],
                    "raw" if variant == "grid" else "std",
                    r"EEG$-$LP" if name == "last - lp" else r"EEG$-$noise",
                    signed(c["mean"]),
                    interval(c["t"]),
                    interval(c["nb"]),
                ]
                if metric == "roc_auc":
                    row.append("eq." if c["nb"]["label"] == "equivalent within +-3" else "n.r.")
                rows.append(row)
    metric_name = {
        "roc_auc": "ROC-AUC",
        "avg_precision": "average precision",
        "pr_auc_trapz": "trapezoidal PR-AUC",
    }[metric]
    caption = (
        "BIOT on Siena with two larger-dose SSL recipes (learning rate $10^{-3}$, "
        "4,174 windows in cell 2; full SSL pool in cell 5), "
    )
    caption += (
        "the same 30-configuration probe search for LP, EEG and matched noise adaptation, "
        "and five rotation means of three seeds. "
    )
    caption += metric_name + r" $\times100$; NB = dependence-adjusted interval. "
    if metric == "roc_auc":
        caption += (
            r"Only cell 5 with standardized features, EEG-minus-LP, supports corrected "
            r"equivalence within $\pm3$; the other seven contrasts are unresolved."
        )
    else:
        caption += "No equivalence margin or practical-importance classification is applied."
    columns = (
        ["Cell", "Features", r"EEG$-$LP", r"95\% NB", r"EEG$-$noise", r"95\% NB"]
        if compact
        else ["Cell", "Features", "Contrast", "Mean", r"95\% $t$", r"95\% NB"]
        + (["Class"] if metric == "roc_auc" else [])
    )
    return table(
        caption,
        "tab:d32" if compact else "tab:d32-" + metric,
        columns,
        rows,
        "llrrrr" if compact else "lllrrr" + ("l" if metric == "roc_auc" else ""),
    )


def report32(data, diag, records):
    lines = [
        "# Matched probe tuning for two larger-dose Siena BIOT recipes",
        "",
        "Protocol: notes/decisions.md D32, frozen at 222d090 before its runs. Additional "
        "analysis motivated by E29; not an external replication.",
        "Command: `.venv/bin/python scripts/analysis/tuned_metrics.py`",
        "",
        "Selection uses validation ROC-AUC only. Unit: mean of three seeds within each of five "
        "rotations. The correction uses the saved D31 Siena train/test ratio. ROC TOST margin "
        "is 3; no ROC margin is applied to AP or trapezoidal PR-AUC.",
        "",
        "## Record and optimization checks",
        "",
        json.dumps(diag, sort_keys=True),
        "",
        "A capped candidate is distinct from a capped selected configuration. Early stopping "
        "does not establish optimization convergence.",
        "",
    ]
    for tag in TAGS32:
        steps = sorted(
            {r["adapt"]["steps"] for k, r in records.items() if k[0] == tag and k[2] in ("last", "last_noise")}
        )
        lines.append(f"- {NAMES[tag]}: matched EEG/noise adaptation steps across rotations: {steps}.")
    for metric in METRICS:
        lines += [
            "",
            "## " + metric,
            "",
            "| cell | features | contrast | mean | 95% t | 95% NB |",
            "|---|---|---|---|---|---|",
        ]
        for key, cell in data.items():
            tag, _, variant = key.split("|")
            for name, c in cell[metric]["contrasts"].items():
                lines.append(
                    f"| {NAMES[tag]} | {variant} | {name} | {signed(c['mean'])} | "
                    f"{interval(c['t'])} | {interval(c['nb'])} |"
                )
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper", action="store_true")
    args = parser.parse_args()
    d31 = json.loads((ROOT / "artifacts/analysis/D31/d31.json").read_text())
    records = load_records()
    results = read(records, d31)
    data31 = {k: v for k, v in results.items() if k.split("|")[0] in TAGS31}
    data32 = {k: v for k, v in results.items() if k.split("|")[0] in TAGS32}
    for tag in TAGS32:
        for rot in range(5):
            for seed in (SEEDS[rot], 1000 + rot, 2000 + rot):
                eeg = records[(tag, "biot", "last", f"rot{rot}", seed)]
                noise = records[(tag, "biot", "last_noise", f"rot{rot}", seed)]
                ignored = {"arm", "data_hash"}
                assert {k: v for k, v in eeg["adapt_spec"].items() if k not in ignored} == {
                    k: v for k, v in noise["adapt_spec"].items() if k not in ignored
                }
                assert eeg["adapt_spec"]["lr"] == 0.001 and eeg["adapt"]["steps"] == noise["adapt"]["steps"]
                assert eeg["eval_hash"] == noise["eval_hash"] and eeg["test_index"] == noise["test_index"]
                assert noise["arm_spec"]["ssl_input"] == "noise"
    diag31 = diagnostics(records, TAGS31)
    diag32 = diagnostics(records, TAGS32)
    out31 = ROOT / "artifacts/analysis/D31"
    out32 = ROOT / "artifacts/analysis/D32"
    out32.mkdir(parents=True, exist_ok=True)
    (out31 / "metrics.json").write_text(
        json.dumps({"protocol": "D31 at 222d090", "diagnostics": diag31, "cells": data31}, indent=1) + "\n"
    )
    (out32 / "d32.json").write_text(
        json.dumps({"protocol": "D32 at 222d090", "diagnostics": diag32, "cells": data32}, indent=1) + "\n"
    )
    (out32 / "README.md").write_text(report32(data32, diag32, records))
    tables = {
        "d31-primary.tex": render31(d31, data31, "last - lp"),
        "d31-noise.tex": render31(d31, data31, "last - last_noise"),
        "d32-primary.tex": render32(data32, "roc_auc", True),
    }
    for name, text in tables.items():
        out = (out32 if name.startswith("d32") else out31) / name
        out.write_text(text)
        if args.paper:
            dst = ROOT / "paper/tmlr/sections/generated" / name
            dst.parent.mkdir(exist_ok=True)
            dst.write_text(text)
    for metric in METRICS:
        (out32 / f"d32-{metric}.tex").write_text(render32(data32, metric))
    print(
        "D31: 505 records; all 64 ROC contrasts match the primary reader. D32: 90 records; "
        "matched noise settings verified."
    )
    print("D31 stopping:", diag31)
    print("D32 stopping:", diag32)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
