#!/usr/bin/env python3
"""D26 (standardized head on the E32 partition) and D27-B (standardized head, 3 seeds), read with the D24 rules.

    .venv/bin/python scripts/analysis/d26_d27b.py

D26 (notes/decisions.md "## D26"): run tags S1RZ (CHB-MIT) / S3RZ (Siena), fold_seed 20261101, probe linear_z,
seeds per rotation r [S_r, 1000 + r, 2000 + r], arms lp, last, last_randinit, lp_randinit, both models.
Rule: D24 rules (3-seed means per rotation, D18 paired rule, D17) on the 3 contrasts. For each of the 3 E32
BIOT CHB-MIT non-replications: "raw-head effect" if the linear_z verdict is "no difference shown"; "partition
effect" if it equals the E32 raw-head verdict; anything else is reported as it is. Other cells descriptive
(E32 raw head S1R/S3R; E26 = S1Z/S3Z at seed S_r).
D27-B (notes/decisions.md "## D27", item B): S1Z / S3Z / S3FZ with seeds [S_r, 1000 + r, 2000 + r] (S_r = the
E26 runs), probe linear_z, same arms. Rule: D24 rules on 3-seed means (3 contrasts + D17); a conclusion holds
only if the raw head (D24-A: S1E+S1M, S3E+S3M, S3FE+S3FM, linear) and the standardized head agree, else it is
"head-dependent". P1Z (paper split, 5 seeds) for completeness: D24-B rule on last - lp (the only contrast D24-B
registers), same co-primary comparison with P1E linear; the other paper-split contrasts are descriptive.

Reading choices (fixed after reading 3 raw records, before any aggregate of these tags was looked at):
- "agree" = the same verdict string. ROC-AUC x100 at the val-selected epoch (test_at_best), as read_d24.
- CIs: bootstrap_d24.cluster_ci (rotations, then seeds inside each drawn rotation; paper split: seeds),
  a fresh default_rng(20261101) per (set, head), as E32. No rule here uses a CI: they are descriptive.
  The D17 CI is that of last_randinit - lp_randinit. t intervals: mean +/- t(0.975, 4) x SEM over units.
- Raw-head strings are re-derived from the records and asserted equal to the published D24-A, E32 and E26
  strings before anything is written. Every expected record is checked first (one per model x arm x rotation
  x seed, no smoke, probe v4 / adapt v3, eval mode, encoder tap, labels, eval_hash = the raw-head record's).
Writes artifacts/analysis/{D26,D27B}/README.md and d26.json / d27b.json.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "analysis"))
from bootstrap_d24 import cluster_ci  # noqa: E402
from e32_e33a import farm_load  # noqa: E402
from read_d24 import ROTS  # noqa: E402
from read_step1 import d17, paired  # noqa: E402

LOCAL = ROOT / "artifacts" / "s3-results"
SR = (42, 123, 2021, 3407, 8888)
SEEDS3 = {r: (SR[i], 1000 + i, 2000 + i) for i, r in enumerate(ROTS)}
SEEDS1 = {r: (SR[i],) for i, r in enumerate(ROTS)}
MODELS = ("biot", "cbramod")
ARMS = ("lp", "lp_randinit", "last", "last_randinit")
CONTRASTS = (("last", "lp", "last - lp"), ("last_randinit", "last", "last_randinit - last"),
             ("lp", "lp_randinit", "lp - lp_randinit"), ("last_randinit", "lp_randinit", "D17"))
NONE, FIRST, SECOND = "no difference shown", "first term wins", "second term wins"
RF = "random features explain it"
# published strings in CONTRASTS order (decisions.md D24 outcome; E32/README.md; E26/README.md)
D24A = {("CHB-MIT", "biot"): (NONE, NONE, NONE, RF), ("Siena", "biot"): (FIRST, NONE, SECOND, RF),
        ("Siena filtered", "biot"): (FIRST, SECOND, NONE, RF), ("CHB-MIT", "cbramod"): (NONE, SECOND, FIRST, RF),
        ("Siena", "cbramod"): (NONE, SECOND, FIRST, RF), ("Siena filtered", "cbramod"): (NONE, SECOND, FIRST, RF)}
E32 = {("CHB-MIT", "biot"): (FIRST, FIRST, SECOND, RF), ("CHB-MIT", "cbramod"): (NONE, SECOND, FIRST, RF),
       ("Siena", "biot"): (FIRST, NONE, SECOND, RF), ("Siena", "cbramod"): (NONE, SECOND, FIRST, RF)}
E26 = {("CHB-MIT", "biot"): (NONE, NONE, NONE, RF), ("Siena", "biot"): (NONE, NONE, NONE, RF),
       ("Siena filtered", "biot"): (NONE, NONE, NONE, RF), ("CHB-MIT", "cbramod"): (NONE, NONE, NONE, RF),
       ("Siena", "cbramod"): (NONE, SECOND, FIRST, RF), ("Siena filtered", "cbramod"): (NONE, SECOND, FIRST, RF)}
# (item, label, dataset, linear_z tag, raw-head tags, published raw strings, fold_seed override, labels)
SETS = (("D26", "CHB-MIT", "chbmit", "S1RZ", "S1R", E32, "20261101", "overlap"),
        ("D26", "Siena", "siena", "S3RZ", "S3R", E32, "20261101", "overlap"),
        ("D27B", "CHB-MIT", "chbmit", "S1Z", "S1E,S1M", D24A, None, "overlap"),
        ("D27B", "Siena", "siena", "S3Z", "S3E,S3M", D24A, None, "overlap"),
        ("D27B", "Siena filtered", "siena", "S3FZ", "S3FE,S3FM", D24A, None, "overlap"),
        ("D27B", "CHB-MIT paper split", "chbmit", "P1Z", "P1E", None, None, "upstream"))
T975 = float(stats.t(4).ppf(0.975))


def f(x) -> str:
    return f"{x:+.1f}"


DEFAULTS = {"tap": "encoder", "input_norm": ""}   # fields older records do not store (their code's values)


def diff(new: dict, old: dict) -> set[str]:
    return {k for k in set(new) | set(old) if new.get(k) != old.get(k, DEFAULTS.get(k))}


def scan() -> list[tuple[Path, dict]]:
    tags = {s[3] for s in SETS} | {t for s in SETS for t in s[4].split(",")}
    out = []
    for p in LOCAL.rglob("results/*.json"):
        if p.name.startswith(("diag-", "test-index-", "val-index-", "report-")):
            continue
        r = json.loads(p.read_text())
        if r.get("run_tag") in tags:
            out.append((p, r))
    return out


def verify(recs, ds, tag, raw_tags, fold_seed, labels) -> tuple[list[str], list[dict]]:
    """Fail loudly on any gap or mismatch with the raw-head record of the same cell; return report lines."""
    paper = tag == "P1Z"
    mine = [r for _, r in recs if r["run_tag"] == tag]
    raw: dict = {}
    for _, r in recs:
        if r["run_tag"] in raw_tags.split(",") and r["dataset"] == ds and not r.get("smoke"):
            k = (r["model"], r["arm"], r["split"], r["seed"])
            assert k not in raw, f"{raw_tags}: two raw records for {k}"
            raw[k] = r
    cnt = Counter((r["model"], r["arm"], r["split"], r["seed"]) for r in mine)
    want = ({(m, a, "paper", s) for m in MODELS for a in ARMS for s in SR} if paper else
            {(m, a, r, s) for m in MODELS for a in ARMS for r in ROTS for s in SEEDS3[r]})
    assert set(cnt) == want, f"{tag}: missing {sorted(want - set(cnt))}, extra {sorted(set(cnt) - want)}"
    assert max(cnt.values()) == 1, f"{tag}: duplicates {[k for k, v in cnt.items() if v > 1]}"
    assert len({r["key"] for r in mine}) == len(mine), f"{tag}: duplicate keys"
    same_loss = no_vi = 0
    n_loss: Counter = Counter()
    for r in mine:
        k = (r["model"], r["arm"], r["split"], r["seed"])
        assert r["dataset"] == ds and not r.get("smoke") and set(r["probes"]) == {"linear_z"}, (tag, k)
        assert r["labels"] == labels and r["versions"] == {"adapt": 3, "probe": 4}, (tag, k)
        assert r["overrides"].get("fold_seed") == fold_seed, (tag, k, r["overrides"])
        assert r["overrides"].get("probes") == "linear_z", (tag, k, r["overrides"])
        spec = r["probes"]["linear_z"]["spec"]
        assert (spec["backbone_mode"], spec["tap"], spec["variant"], spec["split"], spec["seed"],
                spec["input_norm"]) == ("eval", "encoder", "linear_z", r["split"], r["seed"], ""), (tag, k)
        assert r["adapt_spec"]["init"] == ("random" if r["arm"].endswith("randinit") else "pretrained"), (tag, k)
        o = raw[k]
        ospec = o["probes"]["linear"]["spec"]
        assert diff(spec, ospec) == {"variant"}, (tag, k, diff(spec, ospec))
        assert (r["eval_hash"], r["test_index"], r["labels"]) == (o["eval_hash"], o["test_index"], o["labels"])
        assert o.get("val_index", r["val_index"]) == r["val_index"], (tag, k)
        no_vi += "val_index" not in o
        assert not diff(r["adapt_spec"], o["adapt_spec"]) and not diff(r["arm_spec"], o["arm_spec"]), (tag, k)
        tz, to = r["probes"]["linear_z"]["test_at_best"], o["probes"]["linear"]["test_at_best"]
        assert (tz["n"], tz["prevalence"]) == (to["n"], to["prevalence"]), (tag, k)
        if "adapt" in r:
            what = "step" if "step_losses" in o["adapt"] else "epoch"   # pre-E25 records log epoch losses only
            n_loss[what] += 1
            same_loss += r["adapt"][f"{what}_losses"] == o["adapt"][f"{what}_losses"]
    hashes = {s: {r["eval_hash"] for r in mine if r["split"] == s} for s in {r["split"] for r in mine}}
    by_seed = Counter(r["seed"] for r in mine)
    lines = [f"- {tag}: {len(mine)} records = 2 models x 4 arms x "
             + ("5 seeds (42/123/2021/3407/8888), paper split" if paper else
                "5 rotations x 3 seeds [S_r, 1000+r, 2000+r]")
             + f"; exactly 1 per cell, 0 missing, 0 duplicates, 0 smoke (records per seed: "
             f"{', '.join(f'{s}: {n}' for s, n in sorted(by_seed.items()))})",
             f"  probe `linear_z` only, versions adapt 3 / probe 4, backbone eval, tap encoder, input_norm \"\", "
             f"labels {labels}, fold_seed override {fold_seed or 'none (config seed)'}",
             f"  every record pairs with the {raw_tags} raw-head record of the same (model, arm, split, seed): "
             f"same eval_hash, test index, test n and prevalence, adapt_spec and arm_spec, val index ({no_vi} raw "
             f"records predate the val_index field); probe spec differs only in `variant` (fields the raw records "
             f"predate: tap = encoder, input_norm = \"\"); SSL losses identical in {same_loss} of "
             f"{sum(n_loss.values())} adapted runs ({n_loss['step']} per step, {n_loss['epoch']} per epoch: "
             f"older raw records log epoch losses only)",
             "  eval sets per split (both models): "
             + ", ".join(f"{s} {len(h)}" for s, h in sorted(hashes.items()))]
    assert same_loss == sum(n_loss.values()), f"{tag}: SSL losses differ from {raw_tags}"
    return lines, mine


def summarise(roc, model, probe, seeds, rng) -> dict:
    """3 contrasts + D17 on per-rotation seed means (seeds = {rot: seeds}) or per paper-split seed."""
    paper = seeds is None
    per: dict = {}
    for a in ARMS:
        if paper:
            c = roc[(model, a, "paper", probe)]
            assert set(c) == set(SR), (model, a, sorted(c))
            per[a] = [c[s] for s in SR]
        else:
            cells = [roc[(model, a, r, probe)] for r in ROTS]
            assert all(set(seeds[r]) <= set(c) for c, r in zip(cells, ROTS, strict=True)), (model, a)
            per[a] = [float(np.mean([c[s] for s in seeds[r]])) for c, r in zip(cells, ROTS, strict=True)]
    out = {"arms": {a: {"per_unit": v, "mean": float(np.mean(v)), "sem": float(np.std(v, ddof=1) / np.sqrt(5))}
                    for a, v in per.items()}, "contrasts": {}}
    for a, b, name in CONTRASTS:
        d = [x - y for x, y in zip(per[a], per[b], strict=True)]
        m, sem = float(np.mean(d)), float(np.std(d, ddof=1) / np.sqrt(5))
        if paper:
            cl = [d]
            verdict = paired(d) if name == "last - lp" else "descriptive (D24-B registers last - lp only)"
        else:
            cl = [[roc[(model, a, r, probe)][s] - roc[(model, b, r, probe)][s] for s in seeds[r]] for r in ROTS]
            verdict = d17(per[a], per[b]) if name == "D17" else paired(d)
        x = {"mean": m, "sem": sem, "per_unit": d, "per_seed": cl, "verdict": verdict,
             "t95": [m - T975 * sem, m + T975 * sem], "same_sign": int(max((np.array(d) > 0).sum(),
                                                                             (np.array(d) < 0).sum()))}
        if rng is not None:
            cm, lo, hi = cluster_ci(cl, rng)
            assert abs(cm - m) < 1e-9
            x["ci"] = [lo, hi]
        out["contrasts"][name] = x
    return out


def anomalies(mine: list[dict]) -> list[str]:
    """Descriptive: below-chance test ROC and val-selected epoch = last epoch, per model x arm."""
    rows = []
    for m in MODELS:
        for a in ARMS:
            rs = [r for r in mine if (r["model"], r["arm"]) == (m, a)]
            p = [r["probes"]["linear_z"] for r in rs]
            low = sorted((r["split"], r["seed"], round(100 * x["test_at_best"]["roc_auc"], 1),
                          round(100 * x["best_val"], 1)) for r, x in zip(rs, p, strict=True)
                         if x["test_at_best"]["roc_auc"] < 0.5)
            last = sum(x["best_epoch"] == x["spec"]["epochs"] - 1 for x in p)
            rows.append(f"| {m} | {a} | {last} of {len(p)} | {len(low)} | "
                        + ("; ".join(f"{s} s{sd}: test {t} (val {v})" for s, sd, t, v in low) or "-") + " |")
    return ["| model | arm | best epoch = last epoch (10) | test ROC < 50 | which (test ROC, val ROC x100) |",
            "|---|---|---|---|---|", *rows]


def check_reader(path: Path, res: dict, paper: bool) -> None:
    """The verdict lines must equal what scripts/read_d24.py printed for the same tag (run first, --out)."""
    names = {"last - lp": "SA helps? last - lp",
             "last_randinit - last": "random init beats pretrained? last_randinit - last",
             "lp - lp_randinit": "pretrained features beat random? lp - lp_randinit"}
    text = path.read_text()
    for model, v in res.items():
        sec = text.split(f"## {model}, linear_z head")[1].split("## ")[0]
        for k, x in v["contrasts"].items():
            if paper:
                if k == "last - lp":
                    assert f"per seed {', '.join(f(y) for y in x['per_unit'])} -> **{x['verdict']}**" in sec
            elif k == "D17":
                assert f"- D17: **{x['verdict']}**" in sec, (path, model)
            else:
                assert (f"- {names[k]}: mean {f(x['mean'])}, per rotation "
                        f"{', '.join(f(y) for y in x['per_unit'])} -> **{x['verdict']}**") in sec, (path, model, k)


def d26_outcome(z: str, raw: str) -> str:
    """D26 rule for one E32 BIOT CHB-MIT non-replication (z = linear_z verdict, raw = E32 raw-head verdict)."""
    return "raw-head effect" if z == NONE else "partition effect" if z == raw else f"neither ({z})"


def main() -> int:
    assert (d26_outcome(NONE, FIRST), d26_outcome(FIRST, FIRST), d26_outcome(SECOND, FIRST)) == \
        ("raw-head effect", "partition effect", f"neither ({SECOND})")
    recs = scan()
    res: dict = {}
    checks: dict = {"D26": [], "D27B": []}
    for item, label, ds, tag, raw_tags, pub, fold_seed, labels in SETS:
        lines, mine = verify(recs, ds, tag, raw_tags, fold_seed, labels)
        z = farm_load(recs, ds, {tag})
        raw = farm_load(recs, ds, set(raw_tags.split(",")))
        paper = tag == "P1Z"
        seeds = None if paper else SEEDS3
        cell = {"tag": tag, "raw_tags": raw_tags, "item": item, "anomalies": anomalies(mine), "models": {}}
        rz, rr = np.random.default_rng(20261101), np.random.default_rng(20261101)
        # linear_z on the original partition: E26 (S_r only) and, for D26, D27-B at 3 seeds (descriptive)
        orig = None if paper else farm_load(recs, ds, {{"CHB-MIT": "S1Z", "Siena": "S3Z",
                                                         "Siena filtered": "S3FZ"}[label]})
        for model in MODELS:
            zs = summarise(z, model, "linear_z", seeds, rz)
            rs = summarise(raw, model, "linear", seeds, rr)
            got = tuple(rs["contrasts"][n]["verdict"] for _, _, n in CONTRASTS)
            if pub is not None:
                assert got == pub[(label, model)], (label, model, got)
            else:   # P1E: published D24-B last - lp string
                assert got[0] == NONE, got
            e26 = d27b = None
            if orig is not None:
                e26 = summarise(orig, model, "linear_z", SEEDS1, None)
                assert tuple(e26["contrasts"][n]["verdict"] for _, _, n in CONTRASTS) == E26[(label, model)]
            if item == "D26":
                d27b = summarise(orig, model, "linear_z", SEEDS3, None)
            cell["models"][model] = {"z": zs, "raw": rs, "e26_sr": e26, "d27b": d27b}
        reader = ROOT / "artifacts" / "analysis" / item / f"{tag}.md"
        if paper:
            reader = ROOT / "artifacts" / "analysis" / "E26" / "P1Z.md"
        check_reader(reader, {m: v["z"] for m, v in cell["models"].items()}, paper)
        lines.append(f"  verdict lines equal the scripts/read_d24.py output {reader.relative_to(ROOT)}")
        checks[item] += lines
        res[(item, label)] = cell
    write_d26({k[1]: v for k, v in res.items() if k[0] == "D26"}, checks["D26"])
    write_d27b({k[1]: v for k, v in res.items() if k[0] == "D27B"}, checks["D27B"])
    return 0


def cstr(x: dict) -> str:
    ci = f" [{f(x['ci'][0])}, {f(x['ci'][1])}]" if "ci" in x else ""
    return f"{f(x['mean'])}{ci}"


def arm_table(res: dict, unit: str) -> list[str]:
    md = [f"| setting | model | arm | linear_z mean ± SEM | linear_z per {unit} | raw head mean ± SEM | "
          f"raw head per {unit} |", "|---|---|---|---|---|---|---|"]
    for label, cell in res.items():
        for model, v in cell["models"].items():
            for a in ARMS:
                z, r = v["z"]["arms"][a], v["raw"]["arms"][a]
                md.append(f"| {label} | {model} | {a} | {z['mean']:.1f} ± {z['sem']:.1f} | "
                          f"{', '.join(f'{y:.1f}' for y in z['per_unit'])} | {r['mean']:.1f} ± {r['sem']:.1f} | "
                          f"{', '.join(f'{y:.1f}' for y in r['per_unit'])} |")
    return md


def seed_lines(x: dict) -> str:
    return "; ".join(f"{r} " + "/".join(f(y) for y in s) for r, s in zip(ROTS, x["per_seed"], strict=True))


def write_d26(res: dict, checks: list[str]) -> None:
    out = ROOT / "artifacts" / "analysis" / "D26"
    out.mkdir(parents=True, exist_ok=True)
    md = ["# D26: standardized head (`linear_z`) on the second partition (fold_seed 20261101)", "",
          "Rule (notes/decisions.md \"## D26\", written before the runs, post hoc to E32): D24 rules (3-seed "
          "means per rotation, D18 paired rule |mean| > 3 and same sign in >= 4/5 rotations, D17) on last - lp, "
          "last_randinit - last, lp - lp_randinit. For each of the 3 E32 BIOT CHB-MIT non-replications: "
          "**raw-head effect** if the linear_z verdict is \"no difference shown\"; **partition effect** if it "
          "equals the E32 raw-head verdict; anything else is reported as it is. Other cells are descriptive "
          "(compared with E32, raw head, and with E26 = linear_z at seed S_r on the original partition).",
          "ROC-AUC x100 at the val-selected epoch, eval-mode probe, encoder tap, overlap labels. CIs: cluster "
          "bootstrap (rotations, then seeds; 10,000 resamples; rng 20261101), descriptive. Run tags S1RZ / S3RZ; "
          "raw-head pairs S1R / S3R (E32).", "", "Command: `.venv/bin/python scripts/analysis/d26_d27b.py` "
          "(reader outputs: `scripts/read_d24.py --tags S1RZ|S3RZ --out artifacts/analysis/D26/<tag>.md`)", "",
          "## Checks", "", *checks,
          "- Raw-head verdicts re-derived from S1R / S3R equal the published E32 strings (16 of 16); E26 at S_r "
          "re-derived from S1Z / S3Z equals the published E26 strings.", ""]
    md += ["## D26 rule outputs (the 3 E32 BIOT CHB-MIT non-replications)", "",
           "| contrast | linear_z mean [95% CI] | linear_z per rotation | linear_z verdict | E32 raw mean [CI] | "
           "E32 raw verdict | **D26 outcome** |", "|---|---|---|---|---|---|---|"]
    v = res["CHB-MIT"]["models"]["biot"]
    outcomes = {}
    for _, _, n in CONTRASTS[:3]:
        z, r = v["z"]["contrasts"][n], v["raw"]["contrasts"][n]
        o = d26_outcome(z["verdict"], r["verdict"])
        outcomes[n] = o
        md.append(f"| {n} | {cstr(z)} | {', '.join(f(y) for y in z['per_unit'])} | {z['verdict']} | {cstr(r)} | "
                  f"{r['verdict']} | **{o}** |")
    md += ["", "Per seed (linear_z, BIOT CHB-MIT; rotation: S_r/1000+r/2000+r):"]
    md += [f"- {n}: {seed_lines(v['z']['contrasts'][n])}" for _, _, n in CONTRASTS[:3]]
    md += ["", "## All cells (D24 rules on linear_z; comparisons descriptive)", "",
           "| dataset | model | contrast | linear_z mean ± SEM | per rotation | 95% CI (bootstrap) | t95 | "
           "linear_z verdict | E32 raw mean [CI] | E32 raw verdict | E26 at S_r (1 seed) | D27-B 3 seeds, "
           "original partition (post hoc) |", "|" + "---|" * 12]
    for label, cell in res.items():
        for model, v in cell["models"].items():
            for _, _, n in CONTRASTS:
                z, r, e, b = (v[k]["contrasts"][n] for k in ("z", "raw", "e26_sr", "d27b"))
                md.append(f"| {label} | {model} | {n} | {f(z['mean'])} ± {z['sem']:.1f} | "
                          f"{', '.join(f(y) for y in z['per_unit'])} | [{f(z['ci'][0])}, {f(z['ci'][1])}] | "
                          f"[{f(z['t95'][0])}, {f(z['t95'][1])}] | {z['verdict']} | {cstr(r)} | {r['verdict']} | "
                          f"{f(e['mean'])} {e['verdict']} | {f(b['mean'])} {b['verdict']} |")
    same32 = sum(v["z"]["contrasts"][n]["verdict"] == v["raw"]["contrasts"][n]["verdict"]
                 for c in res.values() for v in c["models"].values() for _, _, n in CONTRASTS)
    same26 = sum(v["z"]["contrasts"][n]["verdict"] == v["e26_sr"]["contrasts"][n]["verdict"]
                 for c in res.values() for v in c["models"].values() for _, _, n in CONTRASTS)
    sameb = sum(v["z"]["contrasts"][n]["verdict"] == v["d27b"]["contrasts"][n]["verdict"]
                for c in res.values() for v in c["models"].values() for _, _, n in CONTRASTS)
    md += ["", f"Descriptive counts (16 cells): same string as E32 raw head {same32}; as E26 at S_r {same26}; "
           f"as D27-B (linear_z, 3 seeds, original partition; post hoc) {sameb}. D17 CI = last_randinit - "
           "lp_randinit.", "", "## Arms (descriptive; 3-seed means per rotation)", "", *arm_table(res, "rotation")]
    for label, cell in res.items():
        md += ["", f"## Anomalies, {label} (descriptive, linear_z)", "", *cell["anomalies"]]
    (out / "README.md").write_text("\n".join(md) + "\n")
    (out / "d26.json").write_text(json.dumps({"outcomes": outcomes, "sets": res}, indent=1))
    print("\n".join(md))


def write_d27b(res: dict, checks: list[str]) -> None:
    out = ROOT / "artifacts" / "analysis" / "D27B"
    out.mkdir(parents=True, exist_ok=True)
    md = ["# D27-B: standardized head (`linear_z`) at 3 seeds per rotation, co-primary with the raw head", "",
          "Rule (notes/decisions.md \"## D27\", item B, written before the runs): D24 rules on 3-seed means "
          "(per-rotation means over S_r / 1000+r / 2000+r; D18 paired rule |mean| > 3 and same sign in >= 4/5; "
          "D17) on last - lp, last_randinit - last, lp - lp_randinit. A conclusion **holds** only if the raw "
          "head (D24-A: S1E+S1M, S3E+S3M, S3FE+S3FM, linear) and the standardized head agree (same verdict "
          "string), else it is **head-dependent**. P1Z (paper split, 5 seeds) by D24-B on last - lp, against "
          "P1E linear; other paper-split contrasts descriptive.",
          "ROC-AUC x100 at the val-selected epoch, eval-mode probe, encoder tap. CIs: cluster bootstrap "
          "(rotations, then seeds; paper split: seeds; 10,000 resamples; rng 20261101), descriptive; raw-head CIs "
          "recomputed the same way (artifacts/tables/d24-bootstrap.md differs by Monte Carlo error only).", "",
          "Command: `.venv/bin/python scripts/analysis/d26_d27b.py` (reader outputs: `scripts/read_d24.py --tags "
          "S1Z|S3Z|S3FZ --out artifacts/analysis/D27B/<tag>.md`; P1Z: artifacts/analysis/E26/P1Z.md)", "",
          "## Checks", "", *checks,
          "- Raw-head verdicts re-derived from the D24-A records equal the published D24-A strings (24 of 24); "
          "the S_r-only linear_z reading equals the published E26 strings (24 of 24).", ""]
    rows, held, dep = [], [], []
    for label, cell in res.items():
        paper = cell["tag"] == "P1Z"
        for model, v in cell["models"].items():
            for _, _, n in CONTRASTS:
                z, r = v["z"]["contrasts"][n], v["raw"]["contrasts"][n]
                ruled = not paper or n == "last - lp"
                co = ("**holds**" if z["verdict"] == r["verdict"] else "**head-dependent**") if ruled else "-"
                if ruled:
                    (held if z["verdict"] == r["verdict"] else dep).append(f"{label} {model} {n}")
                e = v["e26_sr"]["contrasts"][n] if v["e26_sr"] else None
                rows.append(f"| {label} | {model} | {n} | {f(z['mean'])} ± {z['sem']:.1f} | "
                            f"{', '.join(f(y) for y in z['per_unit'])} | {cstr(z)} | {z['verdict']} | "
                            f"{f(r['mean'])} ± {r['sem']:.1f} | {', '.join(f(y) for y in r['per_unit'])} | "
                            f"{cstr(r)} | {r['verdict']} | {co} | "
                            + (f"{f(e['mean'])} {e['verdict']}" if e else "-") + " |")
    md += ["## Co-primary outcome", "",
           f"**{len(held)} of {len(held) + len(dep)} rule outputs hold (both heads agree); {len(dep)} are "
           f"head-dependent:** {'; '.join(dep) or 'none'}.", "",
           "| setting | model | contrast | linear_z mean ± SEM | linear_z per rotation (seed on paper split) | "
           "linear_z mean [95% CI] | linear_z verdict | raw mean ± SEM | raw per rotation | raw mean [95% CI] | "
           "raw verdict | **co-primary** | E26 at S_r (linear_z, 1 seed) |", "|" + "---|" * 13, *rows, "",
           "D17 CI = last_randinit - lp_randinit. Paper split: units are seeds 42/123/2021/3407/8888.", ""]
    md += ["## Per seed, linear_z (rotation: S_r/1000+r/2000+r)", ""]
    for label, cell in res.items():
        if cell["tag"] == "P1Z":
            continue
        for model, v in cell["models"].items():
            for _, _, n in CONTRASTS[:3]:
                md.append(f"- {label} {model} {n}: {seed_lines(v['z']['contrasts'][n])}")
    md += ["", "## Arms (descriptive)", "", *arm_table(res, "rotation (seed on paper split)")]
    for label, cell in res.items():
        md += ["", f"## Anomalies, {label} (descriptive, linear_z)", "", *cell["anomalies"]]
    (out / "README.md").write_text("\n".join(md) + "\n")
    (out / "d27b.json").write_text(json.dumps({"held": held, "head_dependent": dep, "sets": res}, indent=1))
    print("\n".join(md))


if __name__ == "__main__":
    raise SystemExit(main())
