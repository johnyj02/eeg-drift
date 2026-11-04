#!/usr/bin/env python3
"""D25-E28: other 4,174-window SSL draws (ssl_seed 11-14) against the base draw (seed 4174).

    .venv/bin/python scripts/analysis/e28_ssl_draws.py

Rule (notes/completeness-audit.md E28): "D4 robust" if every D24 verdict holds under each draw AND
BIOT last_randinit on the paper split stays within 2 ROC across draws.
Reading choices (the audit leaves them open; fixed in this script after reading 3 raw records,
before any aggregate; they are this analysis's choices, not pre-registered):
- Rotations (S1D11/12, S3D11/12) run seed S_r only, so each draw is read with the D24 rule on the
  5 per-rotation values at seed S_r. new last/last_randinit pair with the base lp/lp_randinit at S_r
  (lp does not use SSL data). "Holds" = the same verdict string as the published D24-A verdict
  (3-seed means, re-derived here and asserted against decisions.md). The base draw read at S_r
  alone is shown as the like-for-like reference. lp - lp_randinit uses no SSL data: holds by
  construction. Siena filtered was not run under other draws (not in the E28 design).
- Paper split (P1D11-14, seeds 42/123): the D24-B rule (gain if mean > 3 and positive in >= 4/5 of
  seeds) at 2 seeds = mean > 3 and both seeds positive; mirror for a loss. last - lp is the only
  pre-registered D24-B verdict; last_randinit - last and D17 are descriptive.
- "Within 2 ROC across draws" = max - min of the BIOT last_randinit seed-mean (42/123) over the 5
  draws (base + 4) <= 2. Per-seed ranges are reported next to it.
Records are read with scripts/read_d24.load (v4 / eval-mode / duplicate / mixed-eval checks) from a
symlink farm of the relevant records: load() crashes on the val-index-*.json lists newer jobs write.
Writes artifacts/analysis/E28/{e28.md, e28.json}.
"""

from __future__ import annotations

import json
import math
import shutil
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from read_d24 import ROTS, load  # noqa: E402
from read_step1 import d17, paired  # noqa: E402

LOCAL = ROOT / "artifacts" / "s3-results"
OUT = ROOT / "artifacts" / "analysis" / "E28"
SR = dict(zip(ROTS, (42, 123, 2021, 3407, 8888), strict=True))
MODELS = ("biot", "cbramod")
ARMS4 = ("lp", "lp_randinit", "last", "last_randinit")
BASE = {"chbmit": "S1E,S1M", "siena": "S3E,S3M"}
DRAWS = {"chbmit": ("S1D11", "S1D12"), "siena": ("S3D11", "S3D12")}
PBASE, PDRAWS, PSEEDS = "P1E", ("P1D11", "P1D12", "P1D13", "P1D14"), (42, 123)
SSL_DEP = (("last", "lp"), ("last_randinit", "last"), ("D17", ""))   # contrasts that see the draw
# published D24 verdicts (decisions.md "D24 outcome"); the 3-seed re-derivation must equal these
D24 = {("chbmit", "biot"): ("no difference shown", "no difference shown", "no difference shown"),
       ("siena", "biot"): ("first term wins", "no difference shown", "second term wins"),
       ("chbmit", "cbramod"): ("no difference shown", "second term wins", "first term wins"),
       ("siena", "cbramod"): ("no difference shown", "second term wins", "first term wins")}
D24_PAPER = "no difference shown"


def rule_k(d: list[float], thr: float = 3.0) -> str:
    """D24-B: mean beyond thr and the same sign in >= 4/5 of the seeds (ceil, so 2 of 2)."""
    x = np.asarray(d, dtype=float)
    need = math.ceil(0.8 * len(x))
    if x.mean() > thr and (x > 0).sum() >= need:
        return "first term wins"
    if x.mean() < -thr and (x < 0).sum() >= need:
        return "second term wins"
    return "no difference shown"


def scan() -> tuple[list[dict], Path]:
    """One pass over the records; returns metadata of the relevant ones and a symlink farm of them."""
    tags = {t for v in BASE.values() for t in v.split(",")} | {t for v in DRAWS.values() for t in v}
    tags |= {PBASE, *PDRAWS}
    farm = Path(tempfile.mkdtemp(prefix="e28-"))
    meta = []
    for p in LOCAL.rglob("results/*.json"):
        if p.name.startswith(("diag-", "test-index-", "val-index-", "report-")):
            continue
        r = json.loads(p.read_text())
        if not isinstance(r, dict) or r.get("smoke") or r.get("run_tag") not in tags:
            continue
        if r["arm"] not in ARMS4:
            continue
        link = farm / r["run_tag"] / p.parent.parent.name / "results" / p.name
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(p.resolve())
        spec = dict(r["probes"]["linear"]["spec"])
        spec.pop("seed")
        spec.setdefault("tap", "encoder")         # older records predate the field (S1L check, D25-E25)
        spec.setdefault("input_norm", "")
        ad = {k: v for k, v in r["adapt_spec"].items() if k not in ("seed", "data_hash")}
        ad.setdefault("input_norm", "")
        meta.append({"tag": r["run_tag"], "dataset": r["dataset"], "model": r["model"], "arm": r["arm"],
                     "split": r["split"], "seed": r["seed"], "eval_hash": r["eval_hash"],
                     "labels": r.get("labels"), "versions": json.dumps(r["versions"], sort_keys=True),
                     "probe": json.dumps(spec, sort_keys=True), "adapt": json.dumps(ad, sort_keys=True),
                     "data_hash": r["adapt_spec"].get("data_hash"), "n_windows": r["adapt_spec"].get("n_windows"),
                     "n_total": r["adapt_spec"].get("n_total"), "steps": (r.get("adapt") or {}).get("steps"),
                     "ssl_seed": r.get("overrides", {}).get("ssl_seed"), "path": str(p.relative_to(ROOT))})
    return meta, farm


def checks(meta: list[dict]) -> tuple[list[str], list[str]]:
    """Counts per cell, shared eval data / code within each comparison, distinct SSL draws."""
    gaps, lines = [], []
    seeds = defaultdict(set)
    for m in meta:
        grp = m["tag"] if "D1" in m["tag"] else ("base-" + m["dataset"] if m["split"] != "paper" else PBASE)
        seeds[(grp, m["dataset"], m["model"], m["arm"], m["split"])].add(m["seed"])
    expect = {}
    for ds in BASE:
        for model in MODELS:
            for r in ROTS:
                i = ROTS.index(r)
                for arm in ARMS4:
                    expect[("base-" + ds, ds, model, arm, r)] = {SR[r], 1000 + i, 2000 + i}
                for t in DRAWS[ds]:
                    for arm in ("last", "last_randinit"):
                        expect[(t, ds, model, arm, r)] = {SR[r]}
    for model in MODELS:
        for arm in ARMS4:
            expect[(PBASE, "chbmit", model, arm, "paper")] = {42, 123, 2021, 3407, 8888}
        for t in PDRAWS:
            for arm in ("last", "last_randinit"):
                expect[(t, "chbmit", model, arm, "paper")] = set(PSEEDS)
    for k, v in expect.items():
        if seeds.get(k) != v:
            gaps.append(f"cell {k}: seeds {sorted(seeds.get(k, set()))}, expected {sorted(v)}")
    extra = set(seeds) - set(expect)
    gaps += [f"unexpected cell {k}" for k in sorted(extra)]
    n_new = sum(len(v) for k, v in expect.items() if "D1" in k[0])
    lines.append(f"- Cells: {len(expect)} expected, {len(expect) - len([g for g in gaps if g.startswith('cell')])}"
                 f" complete; {n_new} new-draw records ({sum(1 for m in meta if 'D1' in m['tag'])} found).")
    by_cmp = defaultdict(list)
    for m in meta:
        by_cmp[(m["dataset"], m["model"], m["split"])].append(m)
    for key, ms in sorted(by_cmp.items()):
        for f in ("eval_hash", "labels", "versions", "probe"):
            vals = {m[f] for m in ms}
            if len(vals) > 1:
                gaps.append(f"{key}: {len(vals)} distinct {f}")
        for arm in ARMS4:
            vals = {m["adapt"] for m in ms if m["arm"] == arm}
            if len(vals) > 1:
                gaps.append(f"{key} {arm}: {len(vals)} distinct adapt_spec (minus seed, data_hash)")
    lines.append(f"- {len(by_cmp)} comparisons (dataset, model, split): eval_hash, labels, versions "
                 f"{sorted({m['versions'] for m in meta})}, linear probe spec (minus seed) and adapt_spec "
                 "(minus seed, data_hash) checked equal across base and draws.")
    # SSL draws: one data_hash per (dataset, split, draw), distinct across draws; the override matches
    dh = defaultdict(set)
    for m in meta:
        if m["arm"] in ("last", "last_randinit"):
            draw = m["ssl_seed"] or "4174"
            dh[(m["dataset"], m["split"], draw)].add(m["data_hash"])
            if "D1" in m["tag"] and m["ssl_seed"] != m["tag"][-2:]:
                gaps.append(f"{m['path']}: ssl_seed {m['ssl_seed']} vs tag {m['tag']}")
            if "D1" not in m["tag"] and m["ssl_seed"] is not None:
                gaps.append(f"{m['path']}: base record with ssl_seed {m['ssl_seed']}")
            if m["n_windows"] != 4174 or m["steps"] != 51:
                gaps.append(f"{m['path']}: n_windows {m['n_windows']}, steps {m['steps']}")
    for k, v in dh.items():
        if len(v) != 1:
            gaps.append(f"draw {k}: {len(v)} data hashes across models/arms/seeds")
    per_split = defaultdict(list)
    for (ds, split, _draw), v in dh.items():
        per_split[(ds, split)].append(next(iter(v)))
    for k, v in per_split.items():
        if len(set(v)) != len(v):
            gaps.append(f"{k}: two draws share a data hash")
    pools = sorted({(m["dataset"], m["split"], m["n_total"]) for m in meta if m["arm"] == "last"})
    lines.append(f"- SSL draws: {len(dh)} (dataset, split, draw) cells, one data hash each, all distinct "
                 "within a split; n_windows 4174 and 51 steps everywhere. Pool sizes (expected overlap of "
                 "two draws = 4174/pool): " + ", ".join(f"{d} {s} {n} ({4174 / n:.0%})" for d, s, n in pools))
    lines.append("- Gaps: " + ("none" if not gaps else "; ".join(gaps)))
    return lines, gaps


def contrasts(v: dict) -> dict:
    """v[arm] -> per-unit values; the 4 D24 contrasts as (diffs, verdict)."""
    out = {}
    for a, b in (("last", "lp"), ("last_randinit", "last"), ("lp", "lp_randinit")):
        d = [x - y for x, y in zip(v[a], v[b], strict=True)]
        out[f"{a} - {b}"] = (d, paired(d))
    d = [x - y for x, y in zip(v["last_randinit"], v["lp_randinit"], strict=True)]
    out["D17"] = (d, d17(v["last_randinit"], v["lp_randinit"]))
    return out


def fmt(d: list[float]) -> str:
    return f"{np.mean(d):+.1f} [{', '.join(f'{x:+.1f}' for x in d)}]"


def main() -> int:
    meta, farm = scan()
    lines = ["# D25-E28: other 4,174-window SSL draws vs the base draw (ROC-AUC x100, linear head, eval mode)",
             "", "Rule: \"D4 robust\" if every D24 verdict holds under each draw and BIOT last_randinit on "
             "the paper split stays within 2 ROC across draws. Reading choices: script docstring. "
             "Values: mean [per rotation r0..r4 or per seed 42, 123].", "", "## Checks"]
    chk, gaps = checks(meta)
    lines += chk
    res: dict = {"gaps": gaps, "rotations": {}, "paper": {}}
    fails, fails_base = [], []   # vs the published D24 verdict (primary) / vs base draw at S_r
    names = ("last - lp", "last_randinit - last", "D17")
    for ds in BASE:
        base = load(str(farm), ds, set(BASE[ds].split(",")))
        draws = {t: load(str(farm), ds, {t}) for t in DRAWS[ds]}
        lines += ["", f"## {ds} rotations (base {BASE[ds]}; draws {', '.join(DRAWS[ds])} at seed S_r)", "",
                  "| model | contrast | D24 (3 seeds) | base 4174 @S_r | " +
                  " | ".join(f"{t} @S_r" for t in DRAWS[ds]) + " | holds (vs D24) | vs base @S_r |",
                  "|---|---|---|---|" + "---|" * len(DRAWS[ds]) + "---|---|"]
        for model in MODELS:
            def cell(roc, arm, r, seed=None, m=model):
                c = roc[(m, arm, r, "linear")]
                return c[seed] if seed is not None else float(np.mean([c[s] for s in c]))
            ref = contrasts({a: [cell(base, a, r) for r in ROTS] for a in ARMS4})
            got = tuple(ref[k][1] for k in ("last - lp", "last_randinit - last", "lp - lp_randinit"))
            assert got == D24[(ds, model)], f"D24 re-derivation {ds} {model}: {got} != {D24[(ds, model)]}"
            assert ref["D17"][1] == "random features explain it", (ds, model, ref["D17"])
            lpv = {a: [cell(base, a, r, SR[r]) for r in ROTS] for a in ("lp", "lp_randinit")}
            rows = {"4174": contrasts({**lpv, **{a: [cell(base, a, r, SR[r]) for r in ROTS]
                                                 for a in ("last", "last_randinit")}})}
            for t in DRAWS[ds]:
                rows[t] = contrasts({**lpv, **{a: [cell(draws[t], a, r, SR[r]) for r in ROTS]
                                               for a in ("last", "last_randinit")}})
            for k in (*names, "lp - lp_randinit"):
                bad = [t for t in DRAWS[ds] if rows[t][k][1] != ref[k][1]]
                bad_b = [t for t in DRAWS[ds] if rows[t][k][1] != rows["4174"][k][1]]
                if k == "lp - lp_randinit":
                    flag = "by construction (no SSL) | same"
                else:
                    flag = (f"NO ({', '.join(bad)})" if bad else "yes") + " | " + \
                        (f"differs ({', '.join(bad_b)})" if bad_b else "same")
                    fails += [f"{ds} {model} {k} under {t}" for t in bad]
                    fails_base += [f"{ds} {model} {k} under {t}" for t in bad_b]
                lines.append(f"| {model} | {k} | {fmt(ref[k][0])} {ref[k][1]} | {fmt(rows['4174'][k][0])} "
                             f"{rows['4174'][k][1]} | " + " | ".join(f"{fmt(rows[t][k][0])} {rows[t][k][1]}"
                                                                    for t in DRAWS[ds]) + f" | {flag} |")
            res["rotations"][f"{ds}/{model}"] = {"D24": {k: v for k, v in ref.items()},
                                                 **{t: v for t, v in rows.items()}}
            # descriptive: spread across draws (S_r) vs across seeds (base draw)
            for arm in ("last", "last_randinit"):
                vals = [[cell(base, arm, r, SR[r])] + [cell(draws[t], arm, r, SR[r]) for t in DRAWS[ds]]
                        for r in ROTS]
                seedv = [list(base[(model, arm, r, "linear")].values()) for r in ROTS]
                res["rotations"][f"{ds}/{model}"][f"spread_{arm}"] = {
                    "per_rot_draw_values": vals,
                    "mean_range_draws": float(np.mean([np.ptp(v) for v in vals])),
                    "mean_range_seeds": float(np.mean([np.ptp(v) for v in seedv]))}
        lines += ["", "Descriptive spread (mean over rotations of max - min): across the 3 draws at S_r vs "
                  "across the 3 D24 seeds of the base draw:"]
        for model in MODELS:
            for arm in ("last", "last_randinit"):
                s = res["rotations"][f"{ds}/{model}"][f"spread_{arm}"]
                lines.append(f"- {model} {arm}: draws {s['mean_range_draws']:.1f}, "
                             f"seeds {s['mean_range_seeds']:.1f}")
    # paper split
    pb = load(str(farm), "chbmit", {PBASE})
    pd = {t: load(str(farm), "chbmit", {t}) for t in PDRAWS}
    lines += ["", f"## Paper split (base {PBASE}; draws {', '.join(PDRAWS)}; seeds 42, 123)", "",
              "| model | contrast | D24-B (5 seeds) | base 4174 | " + " | ".join(PDRAWS) + " | holds |",
              "|---|---|---|---|" + "---|" * len(PDRAWS) + "---|"]
    lri = {}
    for model in MODELS:
        g = {a: pb[(model, a, "paper", "linear")] for a in ARMS4}
        d5 = [g["last"][s] - g["lp"][s] for s in sorted(g["lp"])]
        assert paired(d5) == D24_PAPER, (model, d5)
        per = {"4174": {a: [g[a][s] for s in PSEEDS] for a in ARMS4}}
        for t in PDRAWS:
            per[t] = {**{a: per["4174"][a] for a in ("lp", "lp_randinit")},
                      **{a: [pd[t][(model, a, "paper", "linear")][s] for s in PSEEDS]
                         for a in ("last", "last_randinit")}}
        ref5 = contrasts({a: [g[a][s] for s in sorted(g[a])] for a in ARMS4})
        for k in names:
            row = {t: contrasts(per[t])[k] for t in per}
            if k == "last - lp":
                verd = {t: rule_k(v[0]) for t, v in row.items()}
                lit = {t: paired(v[0]) for t, v in row.items()}   # paired() needs n - 1 = 1 of 2
                holds = all(verd[t] == D24_PAPER for t in PDRAWS)
                if not holds:
                    fails.append(f"paper {model} last - lp")
                if lit != verd:
                    lines.append(f"<!-- {model}: paired() n-1 reading differs: {lit} -->")
                flag = "yes" if holds else "NO"
                refs = f"{fmt(ref5[k][0])} {D24_PAPER}"
            else:
                verd = {t: (d17(per[t]['last_randinit'], per[t]['lp_randinit']) if k == "D17"
                            else rule_k(v[0])) for t, v in row.items()}
                flag = "descriptive"
                refs = f"{fmt(ref5[k][0])} (descriptive)"
            lines.append(f"| {model} | {k} | {refs} | " +
                         " | ".join(f"{fmt(row[t][0])} {verd[t]}" for t in per) + f" | {flag} |")
            res["paper"].setdefault(model, {})[k] = {t: [row[t][0], verd[t]] for t in per}
        lri[model] = {t: per[t]["last_randinit"] for t in per}
    lines += ["", "last_randinit by draw (mean [seed 42, seed 123]):"]
    for model in MODELS:
        means = {t: float(np.mean(v)) for t, v in lri[model].items()}
        rng_mean = max(means.values()) - min(means.values())
        rng_seed = [float(np.ptp([v[i] for v in lri[model].values()])) for i in range(len(PSEEDS))]
        lines.append(f"- {model}: " + ", ".join(f"{t} {means[t]:.1f} [{v[0]:.1f}, {v[1]:.1f}]"
                                               for t, v in lri[model].items()) +
                     f"; range of draw means {rng_mean:.2f}, per-seed ranges "
                     f"{', '.join(f'{x:.2f}' for x in rng_seed)}")
        res["paper"][model]["last_randinit"] = {"by_draw": lri[model], "range_mean": rng_mean,
                                                "range_per_seed": rng_seed}
    biot_ok = res["paper"]["biot"]["last_randinit"]["range_mean"] <= 2
    if not biot_ok:
        fails.append("BIOT paper last_randinit range > 2")
    verdict = "D4 robust" if not fails and not gaps else "D4 NOT robust"
    verdict_b = "D4 robust" if not fails_base and biot_ok and not gaps else "D4 NOT robust"
    res["verdict"], res["fails"], res["verdict_vs_base_at_same_seeds"], res["fails_vs_base"] = \
        verdict, fails, verdict_b, fails_base
    lines += ["", "## Verdict", "",
              f"- BIOT last_randinit (paper split) range across the 5 draws: "
              f"{res['paper']['biot']['last_randinit']['range_mean']:.2f} ROC -> "
              f"{'within' if biot_ok else 'NOT within'} 2.",
              f"- Primary (draw verdict vs the published D24 verdict): changes {', '.join(fails) or 'none'}"
              f" -> **{verdict}**" + ("" if not gaps else " (record gaps, see Checks)") + ".",
              f"- Like-for-like (draw vs base draw read at the same seeds), descriptive: changes "
              f"{', '.join(fails_base) or 'none'} -> {verdict_b}."]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "e28.md").write_text("\n".join(lines) + "\n")
    (OUT / "e28.json").write_text(json.dumps(res, indent=1, default=str))
    print("\n".join(lines))
    shutil.rmtree(farm)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
