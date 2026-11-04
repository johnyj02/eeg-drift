#!/usr/bin/env python3
"""D25-E30 (a) and (b): C2/C3 re-tested in our pipeline (notes/completeness-audit.md E30;
notes/decisions.md D15, "D15 outcome", "D24 outcome" C, D25 "D25 parameters fixed"). Part (c), the
released code, is read by scripts/released/read_released.py, not here.

    .venv/bin/python scripts/analysis/e30_c2c3.py

(a) CHB-MIT paper split, BIOT `last`, fixed_c 132 steps, linear head at batch 128, eval mode:
    seed 42 = D24 C2E/C3E, seeds 123/2021/3407/8888 = C2X/C3X (data_seed 1); seed 42 at data_seed
    2 and 3 = C2X2/C3X2 and C2X3/C3X3. LP baseline = R3E-b128, 5-seed BIOT lp (as D24-C).
(b) Siena and Siena filtered rotations, BIOT `last` fixed_c, N ladder (S3C2 / S3FC2) and P2/P5/P10
    at N2048 (S3C3 / S3FC3), seeds [S_r, 1000+r, 2000+r]; LP at batch 128 = S3LPB / S3FLPB (same
    seeds); CBraMod control S3CC / S3FCC (N896, N4174, P2N2048, P10N2048) at seed S_r.

Rule (pre-registered): D15 rules on seed means; ROC-AUC x100 at the val-selected epoch.
Reader choices (the rule text leaves them open; fixed here after reading raw records, before any
E30 aggregate was computed; they are this reader's choices, not pre-registered):
1. (a) primary curve = mean over the 5 model seeds at data_seed 1. Each data_seed draw at seed 42
   is a 1-seed curve read with D15 as D15 itself was (1 seed). 3-draw mean, per-seed verdicts:
   descriptive.
2. (b) primary curve = mean over the 5 rotations of the 3-seed means (= mean over 15 runs), LP the
   same over S3LPB / S3FLPB. Per-rotation verdicts: descriptive.
3. "within 3 of LP at every N" = |v - LP| <= 3 for every N. C3 "> 3 above LP" = every P point
   > LP + 3. Flat but not > 3 above LP = "uninformative" (the D24-C reading of BIOT, 2.6-3.2 below
   LP). Range > 3 across P = "not flat: not supported".
4. The CBraMod control has no batch-128 CBraMod LP (none was run), so LP-dependent parts are
   "undetermined"; a batch-256 LP (S3E / S3FE lp at S_r) comparison is descriptive.
Writes artifacts/analysis/E30/{README.md, e30.json}.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
LOCAL = ROOT / "artifacts" / "s3-results"
OUT = ROOT / "artifacts" / "analysis" / "E30"
SR = (42, 123, 2021, 3407, 8888)
ROTS = tuple(f"rot{r}" for r in range(5))
NA, PA = ("N896", "N1664", "N2048", "N4174"), ("P3N2048", "P11N2048", "P21N2048")
NB, PB = NA, ("P2N2048", "P5N2048", "P10N2048")
NC, PC = ("N896", "N4174"), ("P2N2048", "P10N2048")
DIRS = re.compile(r"^arms-(biot-chb-(c2e|c3e|c2x\d?|c3x\d?|r3e)|(biot|cbra)-sie-rot\d-x[23bc][3f]"
                  r"|cbra-sie-rot\d-(s3e|sfe)|biot-sie-rot\d-(s3m|sfm))$")
SETTINGS = (("S3", "Siena"), ("S3F", "Siena filtered"))


def seeds3(r: int) -> tuple[int, int, int]:
    return SR[r], 1000 + r, 2000 + r


def num(sub: str) -> int:
    """'N1664' -> 1664 (C2 x axis); 'P11N2048' -> 11 (C3 x axis)."""
    return int(sub[1:].split("N")[0]) if sub.startswith("P") else int(sub[1:])


# ---- D15 (decisions.md "## D15"; verdict strings as in "### D15 outcome") -----------------------
def c2(curve: dict[int, float], lp: float | None) -> str:
    best, top = max(curve, key=curve.get), max(curve)
    peak = best <= 2048 and curve[best] - curve[top] > 3
    if lp is None:
        return ("undetermined: peak condition met, no batch-128 LP" if peak else
                "not supported or not testable (no batch-128 LP; no N <= 2048 beats N4174 by > 3)")
    if all(abs(v - lp) <= 3 for v in curve.values()):
        return "not testable: adaptation adds nothing at any N"
    return "supported for the pretrained FM" if peak and curve[best] - lp > 3 else "not supported"


def c3(curve: dict[int, float], lp: float | None) -> str:
    if max(curve.values()) - min(curve.values()) > 3:
        return "not flat: not supported"
    if lp is None:
        return "flat; supported vs uninformative undetermined (no batch-128 LP)"
    return "supported as written" if min(curve.values()) - lp > 3 else "uninformative"


def selfcheck() -> None:
    """The verdict code reproduces the published D15 outcome (decisions.md, seed 42 table)."""
    assert c2({896: 59.2, 1664: 58.9, 2048: 59.1, 4174: 59.2}, 58.6).startswith("not testable")
    assert c2({896: 76.2, 1664: 76.5, 2048: 76.3, 4174: 76.6}, 68.9) == "not supported"
    assert c3({3: 58.1, 11: 59.3, 21: 59.2}, 58.6) == "uninformative"
    assert c3({3: 76.7, 11: 76.4, 21: 76.4}, 68.9) == "supported as written"
    assert c2({896: 70.0, 1664: 66.0, 2048: 65.0, 4174: 65.0}, 60.0).startswith("supported")
    assert c3({3: 60.0, 11: 64.0, 21: 62.0}, 50.0).startswith("not flat")


def describe(curve: dict[int, float], lp: float | None, key: str) -> str:
    """The numbers behind a verdict."""
    v = np.array(list(curve.values()))
    s = f"range {v.max() - v.min():.2f}"
    if key == "N":
        best = max(curve, key=curve.get)
        s = f"best N {best} ({curve[best]:.2f}), best - N4174 {curve[best] - curve[max(curve)]:+.2f}, " + s
    if lp is not None:
        s += f", v - LP {(v - lp).min():+.2f} to {(v - lp).max():+.2f}"
    return s


# ---- records -------------------------------------------------------------------------------------
def wanted() -> dict[tuple, dict]:
    """(run_tag, model, arm, split, seed) -> expected attributes for every record E30 reads."""
    w: dict = {}
    for sub in NA + PA:
        c = "C2" if sub in NA else "C3"
        w[(f"{c}E-{sub}", "biot", "last", "paper", 42)] = {"data_seed": None, "sub": sub, "ds": "chbmit"}
        for s in SR[1:]:
            w[(f"{c}X-{sub}", "biot", "last", "paper", s)] = {"data_seed": None, "sub": sub, "ds": "chbmit"}
        for k in ("2", "3"):
            w[(f"{c}X{k}-{sub}", "biot", "last", "paper", 42)] = {"data_seed": k, "sub": sub, "ds": "chbmit"}
    for s in SR:
        w[("R3E-b128", "biot", "lp", "paper", s)] = {"sub": "", "ds": "chbmit"}
    for t, _ in SETTINGS:
        ds = "siena_filt" if t == "S3F" else "siena"
        for r, rot in enumerate(ROTS):
            for s in seeds3(r):
                for sub in NB + PB:
                    w[(f"{t}C{2 if sub in NB else 3}-{sub}", "biot", "last", rot, s)] = {"sub": sub, "ds": ds}
                w[(f"{t}LPB", "biot", "lp", rot, s)] = {"sub": "", "ds": ds}
                w[(f"{t}M", "biot", "lp", rot, s)] = {"sub": "", "ds": ds, "b256": True}
            for sub in NC + PC:
                w[(f"{t}CC-{sub}", "cbramod", "last", rot, SR[r])] = {"sub": sub, "ds": ds}
            w[(f"{t}E", "cbramod", "lp", rot, SR[r])] = {"sub": "", "ds": ds, "b256": True}
    return w


def load() -> tuple[dict, list[str], list[str]]:
    """key -> record for every wanted key; fails on a missing or duplicate record or a wrong spec."""
    want, got, extra = wanted(), defaultdict(list), Counter()
    for d in sorted(p for p in LOCAL.iterdir() if DIRS.match(p.name)):
        for p in sorted((d / "results").glob("*.json")):
            if p.name.startswith(("diag-", "test-index-", "val-index-", "report-")):
                continue
            r = json.loads(p.read_text())
            if r.get("smoke"):
                continue
            k = (r.get("run_tag"), r["model"], r["arm"], r["split"], r["seed"])
            if k in want:
                got[k].append(r)
            else:
                extra[r.get("run_tag", "").split("-")[0]] += 1
    missing = sorted(set(want) - set(got), key=str)
    dups = sorted((k for k, v in got.items() if len(v) > 1), key=str)
    assert not missing and not dups, \
        f"missing {missing[:10]} ({len(missing)}), duplicate {dups[:10]} ({len(dups)})"
    rec = {k: v[0] for k, v in got.items()}
    eval_hash: dict = defaultdict(set)
    data_hash: dict = defaultdict(set)
    for k, r in rec.items():
        tag, model, arm, split, _ = k
        w = want[k]
        eval_hash[(w["ds"], split)].add(r["eval_hash"])
        assert r["versions"] == {"adapt": 3, "probe": 4}, (k, r["versions"])
        assert set(r["probes"]) == {"linear"}, k
        spec = r["probes"]["linear"]["spec"]
        got_spec = (spec["variant"], spec["backbone_mode"], spec.get("tap", "encoder"))
        assert got_spec == ("linear", "eval", "encoder"), k
        assert spec["batch"] == (256 if w.get("b256") else 128), (k, spec["batch"])
        assert r["labels"] == ("upstream" if w["ds"] == "chbmit" else "overlap"), (k, r["labels"])
        assert r["dataset"] == ("chbmit" if w["ds"] == "chbmit" else "siena"), k
        if arm == "lp":
            assert r["adapt_spec"]["groups"] == [] and not r.get("ssl_subset"), k
            continue
        a, ad = r["adapt_spec"], r["adapt"]
        assert (a["protocol"], a["batch"], a["n_total"], a["init"], ad["steps"], ad["skipped_nonfinite"]) == \
            ("fixed_c", 128, 4174, "pretrained", 132, 0), (k, a["protocol"], ad["steps"])
        assert r["ssl_subset"] == w["sub"] and a["n_windows"] == int(w["sub"].rsplit("N", 1)[1]), k
        if w["sub"].startswith("P"):
            assert r["ssl_subjects"] == num(w["sub"]), (k, r["ssl_subjects"])
        assert r["overrides"].get("data_seed") == w.get("data_seed"), k
        data_hash[(w["ds"], split, w["sub"], w.get("data_seed"), model)].add(a["data_hash"])
    mixed = {k: v for k, v in eval_hash.items() if len(v) > 1}
    assert not mixed, f"mixed eval data within a (dataset, split): {mixed}"
    assert all(eval_hash[("siena", r)] != eval_hash[("siena_filt", r)] for r in ROTS), "filtered = unfiltered data"
    split_dh = {k: v for k, v in data_hash.items() if len(v) > 1}
    assert not split_dh, f"seeds of one cell saw different SSL data: {split_dh}"
    # the pooled seed-42 D24 record must have the same specs as the new seeds (all keys both have)
    for sub in NA + PA:
        c = "C2" if sub in NA else "C3"
        ref = rec[(f"{c}E-{sub}", "biot", "last", "paper", 42)]
        for s in SR[1:]:
            new = rec[(f"{c}X-{sub}", "biot", "last", "paper", s)]
            for x, y in ((new["probes"]["linear"]["spec"], ref["probes"]["linear"]["spec"]),
                         (new["adapt_spec"], ref["adapt_spec"]), (new["arm_spec"], ref["arm_spec"])):
                bad = {q for q in set(x) & set(y) - {"seed"} if x[q] != y[q]}
                assert not bad, (sub, s, bad)
    notes = [f"- {len(rec)} records read, exactly 1 per expected cell (0 missing, 0 duplicate); "
             f"other records in the same directories, not used: "
             f"{', '.join(f'{t} x{n}' for t, n in sorted(extra.items())) or 'none'} (other arms / last_randinit)",
             "- every record: probe v4, adapt code v3, linear head, eval mode, encoder tap, one eval_hash "
             "per (dataset, split); adapted cells: fixed_c, SSL batch 128, 132 steps, 0 non-finite steps, "
             "n_windows = N, ssl_subjects = P; probe batch 128 (the descriptive lp b256 records "
             "S3E/S3FE CBraMod, S3M/S3FM BIOT: 256)",
             "- every seed of a cell saw the same SSL subset (one data_hash per cell); the seed-42 D24 "
             "records (C2E/C3E) have the same probe, adapt and arm specs as C2X/C3X apart from the seed"]
    # data_seed draws: which subsets changed
    same = []
    for sub in NA + PA:
        h = [data_hash[("chbmit", "paper", sub, k, "biot")] for k in (None, "2", "3")]
        n = len(set().union(*h))
        same.append(f"{sub} {'same' if n == 1 else 'different' if n == 3 else 'PARTLY same'}")
    notes.append("- SSL subset across data_seed 1/2/3 (data_hash): " + ", ".join(same)
                 + " (N4174 is the whole 4,174-window sample, so it cannot change with data_seed)")
    cross = []
    for t, name in SETTINGS:
        ds = "siena_filt" if t == "S3F" else "siena"
        n = sum(data_hash[(ds, rot, sub, None, "biot")] == data_hash[(ds, rot, sub, None, "cbramod")]
                for rot in ROTS for sub in NC + PC)
        cross.append(f"{name} {n}/{len(ROTS) * len(NC + PC)}")
    notes.append("- CBraMod control and BIOT saw the same SSL subset (data_hash equal) in: " + ", ".join(cross))
    return rec, notes, sorted(f"{k}" for k in extra)


def roc(r: dict) -> float:
    return 100 * r["probes"]["linear"]["test_at_best"]["roc_auc"]


def ms(v) -> tuple[float, float]:
    v = np.asarray(v, dtype=float)
    return float(v.mean()), float(v.std(ddof=1) / np.sqrt(len(v))) if len(v) > 1 else float("nan")


def fmt(v: float) -> str:
    return f"{v:.1f}"


# ---- main ----------------------------------------------------------------------------------------
def main() -> int:
    selfcheck()
    rec, notes, _ = load()
    js: dict = {"a": {}, "b": {}}
    md = ["# D25-E30 (a) and (b): C2/C3 re-tested, our pipeline", "",
          "Rule (pre-registered, notes/completeness-audit.md E30): D15 rules on seed means "
          "(notes/decisions.md \"## D15\"; verdict strings as in \"### D15 outcome\"). ROC-AUC x100 at the "
          "val-selected epoch, linear head at batch 128, eval mode, encoder tap, fixed_c 132 SSL steps "
          "(batch 128, lr 3e-5), BIOT arm `last` (block03 + head). Only differences > 3 are interpreted.",
          "",
          "D15: C2 is \"supported for the pretrained FM\" only if the best N is <= 2048 AND beats both "
          "N4174 and LP by > 3; \"not testable: adaptation adds nothing at any N\" if within 3 of LP at "
          "every N; else \"not supported\". C3 \"flat\" if max - min across P <= 3; flat supports C3 only "
          "if > 3 above LP; flat at the LP level = \"uninformative\".", "",
          "Reader choices (not in the rule text; fixed before any E30 aggregate, after reading raw "
          "records; see the script docstring): (a) primary = 5-seed mean at data_seed 1, each data_seed "
          "draw at seed 42 read as a 1-seed D15 curve; (b) primary = mean over 5 rotations of 3-seed "
          "means, LP = S3LPB / S3FLPB the same way; |v - LP| <= 3 = \"within 3\"; C3 \"> 3 above LP\" "
          "= every P point; flat but not above LP = \"uninformative\" (D24-C precedent). Everything "
          "else below is labelled descriptive/post hoc.", "", "## Record checks", ""] + notes

    # ---- (a) ----
    lp_a = {s: roc(rec[("R3E-b128", "biot", "lp", "paper", s)]) for s in SR}
    LPA = float(np.mean(list(lp_a.values())))
    rows: dict = {}
    def curve_a(tag: str, s: int) -> dict[str, float]:
        return {sub: roc(rec[(f"{'C2' if sub in NA else 'C3'}{tag}-{sub}", "biot", "last", "paper", s)])
                for sub in NA + PA}

    for s in SR:
        rows[f"seed {s}"] = curve_a("E" if s == 42 else "X", s)
    for k in ("2", "3"):
        rows[f"seed 42, data_seed {k}"] = curve_a(f"X{k}", 42)
    mean5 = {sub: ms([rows[f"seed {s}"][sub] for s in SR]) for sub in NA + PA}
    draws = {1: rows["seed 42"], 2: rows["seed 42, data_seed 2"], 3: rows["seed 42, data_seed 3"]}
    mean3 = {sub: ms([draws[k][sub] for k in draws]) for sub in NA + PA}

    def verdicts(curve: dict[str, float], lp: float | None, nn, pp) -> dict:
        cn = {num(x): curve[x] for x in nn}
        cp = {num(x): curve[x] for x in pp}
        return {"C2": c2(cn, lp), "C2_numbers": describe(cn, lp, "N"),
                "C3": c3(cp, lp), "C3_numbers": describe(cp, lp, "P")}

    va = {"5-seed mean, data_seed 1 (PRIMARY)": verdicts({k: v[0] for k, v in mean5.items()}, LPA, NA, PA)}
    for k in draws:
        va[f"seed 42, data_seed {k} (1 seed, D15 as written)"] = verdicts(draws[k], LPA, NA, PA)
    va["3-draw mean at seed 42 (descriptive/post hoc)"] = verdicts({k: v[0] for k, v in mean3.items()},
                                                                    LPA, NA, PA)
    for s in SR[1:]:
        va[f"seed {s} alone (descriptive/post hoc)"] = verdicts(rows[f"seed {s}"], LPA, NA, PA)
    d24 = va["seed 42, data_seed 1 (1 seed, D15 as written)"]
    js["a"] = {"lp_r3e_b128": lp_a, "lp_mean": LPA, "rows": rows, "mean5": mean5, "mean3draws": mean3,
               "verdicts": va}
    md += ["", "## (a) CHB-MIT paper split, BIOT pretrained `last`", "",
           f"LP baseline (D15/D24-C): R3E-b128, BIOT lp, linear, batch 128, eval mode, 5 seeds: "
           f"**{LPA:.2f}** (per seed {', '.join(f'{s}: {v:.2f}' for s, v in lp_a.items())}).", "",
           "| curve | " + " | ".join(NA + PA) + " |", "|---" * (1 + len(NA + PA)) + "|"]
    for name, row in rows.items():
        label = name + (" (= D24 C2E/C3E)" if name == "seed 42" else "")
        md.append(f"| {label} | " + " | ".join(fmt(row[x]) for x in NA + PA) + " |")
    md.append("| **5-seed mean ± SEM, data_seed 1** | " + " | ".join(f"**{m:.1f}** ± {e:.1f}" for m, e in
                                                                   (mean5[x] for x in NA + PA)) + " |")
    md.append("| 3-draw mean ± SEM at seed 42 (descriptive) | " + " | ".join(f"{m:.1f} ± {e:.1f}" for m, e in
                                                                           (mean3[x] for x in NA + PA)) + " |")
    md.append(f"| LP baseline R3E-b128 | {LPA:.1f} | | | | | | |")
    md += ["", "| reading | C2 verdict | numbers | C3 verdict | numbers |", "|---|---|---|---|---|"]
    for name, v in va.items():
        md.append(f"| {name} | **{v['C2']}** | {v['C2_numbers']} | **{v['C3']}** | {v['C3_numbers']} |")
    pre = {k: v for k, v in va.items() if "descriptive" not in k}
    hold_c2 = all(v["C2"] == "not supported" for v in pre.values())
    hold_c3 = all(v["C3"] == "uninformative" for v in pre.values())
    md += ["", f"D24-C (seed 42, published): C2 \"not supported\", C3 \"uninformative\". Re-derived here "
               f"from the C2E/C3E records: C2 \"{d24['C2']}\", C3 \"{d24['C3']}\". Same string in every "
               f"pre-registered reading (5-seed mean, data_seed 2, data_seed 3): "
               f"C2 **{'yes' if hold_c2 else 'NO'}** "
               f"({'; '.join(k.split(' (')[0] + ': ' + v['C2'] for k, v in pre.items())}), "
               f"C3 **{'yes' if hold_c3 else 'NO'}**. C2 is supported in no reading: best N - N4174 <= +0.2."]
    js["a"]["d24_holds"] = {"C2": hold_c2, "C3": hold_c3}

    # ---- (b) ----
    for t, name in SETTINGS:
        biot: dict = {}
        for r, rot in enumerate(ROTS):
            row = {sub: [roc(rec[(f"{t}C{2 if sub in NB else 3}-{sub}", "biot", "last", rot, s)])
                         for s in seeds3(r)] for sub in NB + PB}
            row["LP"] = [roc(rec[(f"{t}LPB", "biot", "lp", rot, s)]) for s in seeds3(r)]
            biot[rot] = row
        cols = NB + PB + ("LP",)
        rotmean = {rot: {c: float(np.mean(biot[rot][c])) for c in cols} for rot in ROTS}
        grand = {c: ms([rotmean[rot][c] for rot in ROTS]) for c in cols}
        LPB = grand["LP"][0]
        vb = {"BIOT, mean over 5 rotations of 3-seed means (PRIMARY)":
              verdicts({c: grand[c][0] for c in cols}, LPB, NB, PB)}
        per_rot = {rot: verdicts(rotmean[rot], rotmean[rot]["LP"], NB, PB) for rot in ROTS}
        cb = {rot: {sub: roc(rec[(f"{t}CC-{sub}", "cbramod", "last", rot, SR[r])]) for sub in NC + PC}
              for r, rot in enumerate(ROTS)}
        cb_lp256 = {rot: roc(rec[(f"{t}E", "cbramod", "lp", rot, SR[r])]) for r, rot in enumerate(ROTS)}
        cgrand = {c: ms([cb[rot][c] for rot in ROTS]) for c in NC + PC}
        b256 = [float(np.mean([roc(rec[(f"{t}M", "biot", "lp", rot, s)]) for s in seeds3(r)]))
                for r, rot in enumerate(ROTS)]
        dbatch = [rotmean[rot]["LP"] - b for rot, b in zip(ROTS, b256, strict=True)]
        lp256 = ms(list(cb_lp256.values()))
        vb["CBraMod control, mean over 5 rotations at S_r (pre-registered rule, no batch-128 LP)"] = \
            verdicts({c: cgrand[c][0] for c in NC + PC}, None, NC, PC)
        vb["CBraMod control vs batch-256 lp S3E/S3FE at S_r (descriptive/post hoc)"] = \
            verdicts({c: cgrand[c][0] for c in NC + PC}, lp256[0], NC, PC)
        js["b"][name] = {"biot_per_rotation_seed_values": biot, "biot_rotation_means": rotmean,
                         "biot_grand": grand,
                         "biot_per_rotation_verdicts": per_rot, "cbramod_S_r": cb, "cbramod_lp_b256_S_r": cb_lp256,
                         "cbramod_grand": cgrand, "verdicts": vb, "biot_lp_b256_rotation_means": b256,
                         "biot_lp_b128_minus_b256": dbatch}
        md += ["", f"## (b) {name}, 5 rotations", "",
               f"LP baseline: {t}LPB, BIOT lp, linear, batch 128, eval mode, 3 seeds per rotation (the same "
               f"seeds as the curves): **{LPB:.2f}** ± {grand['LP'][1]:.2f} (SEM over rotation means).", "",
               "BIOT pretrained `last`, 3-seed mean per rotation:", "",
               "| rotation (seeds) | " + " | ".join(cols) + " |", "|---" * (1 + len(cols)) + "|"]
        for r, rot in enumerate(ROTS):
            md.append(f"| {rot} ({'/'.join(map(str, seeds3(r)))}) | "
                      + " | ".join(fmt(rotmean[rot][c]) for c in cols) + " |")
        md.append("| **mean ± SEM over rotations** | " + " | ".join(f"**{grand[c][0]:.1f}** ± {grand[c][1]:.1f}"
                                                                   for c in cols) + " |")
        md += ["", f"CBraMod control `last` at seed S_r (one run per rotation; lp b256 = {t}E lp at S_r, "
                   "descriptive only):", "",
               "| rotation (seed) | " + " | ".join(NC + PC) + " | lp b256 |", "|---" * (2 + len(NC + PC)) + "|"]
        for r, rot in enumerate(ROTS):
            md.append(f"| {rot} ({SR[r]}) | " + " | ".join(fmt(cb[rot][c]) for c in NC + PC)
                      + f" | {cb_lp256[rot]:.1f} |")
        md.append("| **mean ± SEM** | "
                  + " | ".join(f"**{cgrand[c][0]:.1f}** ± {cgrand[c][1]:.1f}" for c in NC + PC)
                  + f" | {lp256[0]:.1f} ± {lp256[1]:.1f} |")
        md += ["", f"Probe batch matters (descriptive/post hoc): BIOT lp b128 ({t}LPB) - lp b256 ({t}M), same "
                   f"seeds, per rotation {', '.join(f'{x:+.1f}' for x in dbatch)} (mean {np.mean(dbatch):+.1f}). "
                   "So the CBraMod row against the b256 lp mixes probe batch with adaptation and is not a C2/C3 "
                   "reading.", "",
               "| reading | C2 verdict | numbers | C3 verdict | numbers |", "|---|---|---|---|---|"]
        for k, v in vb.items():
            md.append(f"| {k} | **{v['C2']}** | {v['C2_numbers']} | **{v['C3']}** | {v['C3_numbers']} |")
        c2n = Counter(v["C2"] for v in per_rot.values())
        c3n = Counter(v["C3"] for v in per_rot.values())
        md += ["", "Per-rotation verdicts, BIOT, 3-seed mean vs the rotation's own LP (descriptive/post hoc): "
                   f"C2 {dict(c2n)}; C3 {dict(c3n)}.", ""]
        md += [f"- {rot}: C2 {v['C2']} ({v['C2_numbers']}); C3 {v['C3']} ({v['C3_numbers']})"
               for rot, v in per_rot.items()]
    md += ["", "## Commands", "", "```",
           ".venv/bin/python scripts/analysis/e30_c2c3.py",
           "# inputs: artifacts/s3-results (already synced); jobs: notes/jobs-d25b.txt after '# E30';",
           "# specs: scripts/submit_d25.sh (want E30), D24 C2E/C3E/R3E: scripts/submit_d24.sh",
           ".venv/bin/python -m pytest -q && .venv/bin/python -m ruff check src tests scripts sm_entry.py",
           "```", ""]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "README.md").write_text("\n".join(md) + "\n")
    (OUT / "e30.json").write_text(json.dumps(js, indent=1, default=str))
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
