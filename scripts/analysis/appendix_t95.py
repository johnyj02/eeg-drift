#!/usr/bin/env python3
"""95% t-intervals (df 4) for the appendix contrasts whose reading outputs print none. Post hoc, descriptive.

    .venv/bin/python scripts/analysis/appendix_t95.py

Reads saved reading outputs only (no result records): D27/cpu.json (per-rotation differences of D24-A,
E32, D27-B and D26; per-unit last - last_noise of E27 and D27-A), E19/e19.json, E25/e25_verdicts.json,
E28/e28.json and E33A/e33a.json. Units: the 5 rotation means (3 seeds each; 1 seed, S_r, for E28, A4,
A5 and A7) or, for A1 and E19 on DL's split, the 5 seeds on that split (seed uncertainty on one split,
not test-set sampling).
Checks, asserted before writing: the recomputed D24-A, D27-B and D26 intervals equal those written by
stats_d25.py and d26_d27b.py; the recomputed 90% intervals equal cpu.json's TOST intervals; E19's /100
differences equal D24-A (and, on DL's split, E10's units); every mean equals the mean its reading output
printed. The E19 DL's-split rule output is the D24-B rule (mean > 3 and 4 of 5 seeds, as e19.md prints it).
Writes artifacts/analysis/stats/appendix-t95.md and .json (full precision).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy import stats

A = Path(__file__).resolve().parents[2] / "artifacts" / "analysis"
OUT = A / "stats" / "appendix-t95.md"


def tci(x, level=0.95):
    x = np.asarray(x, float)
    h = stats.t(len(x) - 1).ppf(0.5 + level / 2) * x.std(ddof=1) / np.sqrt(len(x))
    return x.mean(), x.mean() - h, x.mean() + h


def close(a, b, tol=1e-9):
    return all(abs(u - v) < tol for u, v in zip(a, b, strict=True))


def main() -> None:
    files = {"cpu": "D27/cpu.json", "e10": "stats/stats.json", "d27b": "D27B/d27b.json", "d26": "D26/d26.json",
             "e19": "E19/e19.json", "e25": "E25/e25_verdicts.json", "e28": "E28/e28.json",
             "e33a": "E33A/e33a.json"}
    j = {k: json.loads((A / p).read_text()) for k, p in files.items()}
    rows = []

    # checks against intervals already written by other scripts
    e10 = {(r["setting"], r["model"], r["a"], r["b"]): r for r in j["e10"]["e10"] if r["probe"] == "linear"}
    loro = j["cpu"]["loro"]
    for r in loro:
        key = (r["setting"], r["model"], r["a"], r["b"])
        _, lo, hi = tci(r["per_rot"])
        if r["item"] == "D24-A":
            assert close((lo, hi), e10[key]["t"]["ci95"]), key
        if r["item"] in ("E26/D27-B", "D26"):
            src = j["d27b"] if r["item"] != "D26" else j["d26"]
            c = "D17" if r["b"] == "lp_randinit" and r["a"] == "last_randinit" else f"{r['a']} - {r['b']}"
            sets = src["sets"][r["setting"]]["models"][r["model"]]["z"]["contrasts"]
            assert close((lo, hi), sets[c]["t95"]), (r["item"], key)
        if r["item"] == "E32":
            c = f"{r['a']} - {r['b']}"
            rows.append(("E32", r["setting"], r["model"], "linear", c, r["per_rot"], r["verdict"]))
    for r in j["cpu"]["tost"]:
        _, lo, hi = tci(r["per_unit"], 0.90)
        assert close((lo, hi), r["ci90"]), (r["item"], r["setting"])
        c = "last - last_noise"
        rows.append((r["item"], r["setting"], r["model"], r["probe"], c, r["per_unit"], r["d19"]))

    d24 = {(r["setting"], r["model"], f"{r['a']} - {r['b']}"): r["per_rot"] for r in loro if r["item"] == "D24-A"}
    for setting in ("CHB-MIT", "Siena", "Siena filtered"):
        for c, v in j["e19"]["biot"][setting]["verdicts"].items():
            name = "last_randinit - lp_randinit" if c.startswith("D17") else c
            assert close(v["d100_diff"], d24[(setting, "biot", name)]), (setting, c)
            rows.append(("E19 q95", setting, "biot", "linear", name, v["q95_diff"], v["q95"]))
    p1 = j["e19"]["biot"]["paper"]
    for head in ("linear", "mlp_fullft"):
        d100 = np.subtract(p1[f"{head}/last"]["d100"], p1[f"{head}/lp"]["d100"])
        ref = next(r for r in j["e10"]["e10"] if r["paper"] and r["model"] == "biot" and r["probe"] == head
                   and (r["a"], r["b"]) == ("last", "lp"))
        assert close(d100, ref["units"]), head
        q = np.subtract(p1[f"{head}/last"]["q95"], p1[f"{head}/lp"]["q95"])
        win = abs(q.mean()) > 3 and (np.sign(q) == np.sign(q.mean())).sum() >= 4  # D24-B rule
        verdict = ("first term wins" if q.mean() > 0 else "second term wins") if win else "no difference shown"
        rows.append(("E19 q95", "DL's split (seeds)", "biot", head, "last - lp", q, verdict))
    tagset = {"S1L": "CHB-MIT", "S3L": "Siena", "S3FL": "Siena filtered"}
    for r in j["e25"]:
        if r["tag"] in tagset:
            assert abs(np.mean(r["mlp_per_rot"]) - r["mlp"][0]) < 1e-9, r["tag"]
            pu, verdict = r["mlp_per_rot"], r["mlp"][1]
            rows.append(("E25", tagset[r["tag"]], r["model"], "mlp_fullft", r["contrast"], pu, verdict))
    for key, v in j["e28"]["rotations"].items():
        setting = {"chbmit": "CHB-MIT", "siena": "Siena"}[key.split("/")[0]]
        for draw, cs in v.items():
            if draw.startswith("spread"):
                continue
            for c, (pu, verdict) in cs.items():
                rows.append((f"E28 {draw}", setting, key.split("/")[1], "linear", c, pu, verdict))
    for key, v in j["e33a"].items():
        for c, r in v["new"]["contrasts"].items():
            assert abs(np.mean(r["per_rot"]) - r["mean"]) < 1e-9, (key, c)
            rows.append(("E33a", "CHB-MIT extended", key.split("|")[1], "linear", c, r["per_rot"], r["verdict"]))

    lines = ["# 95% t-intervals for appendix contrasts (post hoc, descriptive)", "",
             "Script: scripts/analysis/appendix_t95.py (see its docstring for inputs and checks; all asserted).",
             "t with df 4 over the 5 units; ROC-AUC x100. A1 and E19 DL's-split units are seeds on that split",
             "(seed uncertainty on one split). Rule output = the string printed by the item's reading script.", "",
             "| item | setting | model | head | contrast | mean | t 95% | t 90% | rule output |",
             "|---|---|---|---|---|---|---|---|---|"]
    for item, setting, model, head, c, pu, verdict in rows:
        m, lo, hi = tci(pu)
        _, lo9, hi9 = tci(pu, 0.90)
        lines.append(f"| {item} | {setting} | {model} | {head} | {c} | {m:+.2f} | [{lo:+.2f}, {hi:+.2f}] "
                     f"| [{lo9:+.2f}, {hi9:+.2f}] | {verdict} |")
    OUT.write_text("\n".join(lines) + "\n")
    full = [dict(zip(("item", "setting", "model", "head", "contrast", "mean", "lo95", "hi95", "rule"),
                     (item, setting, model, head, c, *tci(pu), verdict), strict=True))
            for item, setting, model, head, c, pu, verdict in rows]
    OUT.with_suffix(".json").write_text(json.dumps(full, indent=1) + "\n")
    print(f"wrote {OUT} and .json ({len(rows)} rows)")


if __name__ == "__main__":
    main()
