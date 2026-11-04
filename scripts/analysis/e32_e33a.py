#!/usr/bin/env python3
"""D25-E32 (second subject partition) and D25-E33a (extended CHB-MIT store), read with the D24 rules.

    .venv/bin/python scripts/analysis/e32_e33a.py

E32 (notes/completeness-audit.md "E32"; decisions.md D25 "D25 parameters fixed"): fold_seed 20261101,
run tags S1R (CHB-MIT) / S3R (Siena), arms lp, lp_randinit, last, last_randinit, seeds per rotation
r [S_r, 1000 + r, 2000 + r], linear head, eval mode, overlap labels, both models.
Rule: "replicated" if the same verdict string holds AND the CI overlaps the original (D24-A: S1E+S1M,
S3E+S3M; CIs = artifacts/tables/d24-bootstrap.md).
E33a (decisions.md "D25 additions"): store chbmit_x, 23-subject rotations (seed 20261014), D24-A arms,
3 seeds, linear, eval mode, run tag S1X; D24 rules. Its comparison with D24-A CHB-MIT has no rule.

Reading (fixed before any aggregate was looked at, after reading 3 raw records):
- Verdicts: scripts/read_d24 rules: per rotation the mean over its 3 seeds, then read_step1.paired
  (|mean| > 3 and same sign in >= 4/5 rotations) on last - lp, last_randinit - last, lp - lp_randinit,
  and read_step1.d17 on last_randinit vs lp_randinit. ROC-AUC x100 at the val-selected epoch.
- CIs: bootstrap_d24.cluster_ci (rotations, then seeds inside each drawn rotation; 10,000 resamples),
  a fresh default_rng(20261101) per (dataset, tag) set. The D17 CI is that of last_randinit - lp_randinit.
- "CI overlaps the original" = the two 95% intervals intersect (lo_new <= hi_orig and lo_orig <= hi_new).
  Shown next to it, labelled post hoc: whether the new CI contains the original point mean.
- E33a vs D24-A (same verdict string, CI overlap) is descriptive: different subjects and folds.
Every expected record is checked (one per model x arm x rotation x seed, no smoke, one eval set per
rotation, specs equal to D24-A) before reading. Writes artifacts/analysis/{E32,E33A}/README.md + .json.
"""

from __future__ import annotations

import json
import re
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from bootstrap_d24 import cluster_ci  # noqa: E402
from read_d24 import ROTS, load  # noqa: E402
from read_step1 import d17, paired  # noqa: E402

LOCAL = ROOT / "artifacts" / "s3-results"
SR = (42, 123, 2021, 3407, 8888)
SEEDS = {r: (SR[i], 1000 + i, 2000 + i) for i, r in enumerate(ROTS)}
MODELS = ("biot", "cbramod")
A4 = ("lp", "lp_randinit", "last", "last_randinit")
CONTRASTS = (("last", "lp", "last - lp"), ("last_randinit", "last", "last_randinit - last"),
             ("lp", "lp_randinit", "lp - lp_randinit"), ("last_randinit", "lp_randinit", "D17"),
             ("all", "last", "all - last"))
# (item, dataset, tag, arms, fold_seed override, original dataset, original tags, label)
SETS = (("E32", "chbmit", "S1R", A4, "20261101", "chbmit", "S1E,S1M", "CHB-MIT"),
        ("E32", "siena", "S3R", A4, "20261101", "siena", "S3E,S3M", "Siena"),
        ("E33A", "chbmit_x", "S1X", (*A4, "all"), None, "chbmit", "S1E,S1M", "CHB-MIT extended"))
# published D24-A verdicts (decisions.md "D24 outcome"): last - lp, last_randinit - last, lp - lp_randinit, D17
NONE, FIRST, SECOND = "no difference shown", "first term wins", "second term wins"
RF = "random features explain it"
D24 = {("chbmit", "biot"): (NONE, NONE, NONE, RF), ("siena", "biot"): (FIRST, NONE, SECOND, RF),
       ("chbmit", "cbramod"): (NONE, SECOND, FIRST, RF), ("siena", "cbramod"): (NONE, SECOND, FIRST, RF)}


def scan() -> list[tuple[Path, dict]]:
    tags = {s[2] for s in SETS} | {t for s in SETS for t in s[6].split(",")}
    out = []
    for p in LOCAL.rglob("results/*.json"):
        if p.name.startswith(("diag-", "test-index-", "val-index-", "report-")):
            continue
        r = json.loads(p.read_text())
        if r.get("run_tag") in tags:
            out.append((p, r))
    return out


def farm_load(recs: list[tuple[Path, dict]], dataset: str, tags: set[str]) -> dict:
    """read_d24.load (v4 / eval / duplicate / mixed-eval guards) on a symlink farm of just these records."""
    with tempfile.TemporaryDirectory() as tmp:
        for p, r in recs:
            if r["dataset"] == dataset and r["run_tag"] in tags:
                d = Path(tmp) / p.parent.parent.name / "results"
                d.mkdir(parents=True, exist_ok=True)
                (d / p.name).symlink_to(p)
        return load(tmp, dataset, tags)


def index(name: str) -> list[dict]:
    copies = {p.read_bytes() for p in LOCAL.rglob(f"results/{name}")}
    assert len(copies) == 1, f"{len(copies)} different copies of {name}"
    return json.loads(copies.pop())


def verify(recs, ds, tag, arms, fold_seed, ods, otags) -> tuple[list[str], dict]:
    """Fail loudly on any gap; return report lines and per-rotation facts."""
    mine = [(p, r) for p, r in recs if r["dataset"] == ds and r["run_tag"] == tag]
    old = [(p, r) for p, r in recs if r["dataset"] == ods and r["run_tag"] in otags.split(",")]
    cnt = Counter((r["model"], r["arm"], r["split"], r["seed"]) for _, r in mine)
    want = {(m, a, s, x) for m in MODELS for a in arms for s in ROTS for x in SEEDS[s]}
    assert set(cnt) == want, f"{tag}: missing {sorted(want - set(cnt))}, extra {sorted(set(cnt) - want)}"
    dup = [k for k, v in cnt.items() if v > 1]
    assert not dup, f"{tag}: duplicates {dup}"
    lines = [f"- {tag}: {len(mine)} records = 2 models x {len(arms)} arms x 5 rotations x 3 seeds "
             f"[S_r, 1000+r, 2000+r]; exactly 1 per cell, 0 missing, 0 duplicates, 0 smoke"]
    skip = {"seed", "split", "data_hash", "n_total", "dataset"}
    for p, r in mine:
        assert not r.get("smoke") and set(r["probes"]) == {"linear"}, p.name
        assert r["labels"] == "overlap" and r["versions"] == {"adapt": 3, "probe": 4}, p.name
        assert r["overrides"].get("fold_seed") == fold_seed, (p.name, r["overrides"])
        spec = r["probes"]["linear"]["spec"]
        assert (spec["backbone_mode"], spec["tap"], spec["variant"], spec["split"]) == \
            ("eval", "encoder", "linear", r["split"]), p.name
        assert r["adapt_spec"]["init"] == ("random" if r["arm"].endswith("randinit") else "pretrained"), p.name
        ref = next(o for _, o in old if (o["model"], o["arm"]) == (r["model"], r["arm"]))
        for new, prev in ((spec, ref["probes"]["linear"]["spec"]), (r["adapt_spec"], ref["adapt_spec"]),
                          (r["arm_spec"], ref["arm_spec"])):
            bad = {k for k in set(new) & set(prev) - skip if new[k] != prev[k]}
            assert not bad, (tag, r["model"], r["arm"], bad)
    facts = {}
    for s in ROTS:
        rs = [r for _, r in mine if r["split"] == s]
        ev = {(r["eval_hash"], r["test_index"], r["val_index"]) for r in rs}
        assert len(ev) == 1, f"{tag} {s}: eval sets {ev}"
        eh, ti, vi = ev.pop()
        test, val = index(ti), index(vi)
        n = {r["probes"]["linear"]["test_at_best"]["n"] for r in rs}
        assert n == {len(test)}, (tag, s, n, len(test))
        tb = [r["probes"]["linear"]["test_at_best"] for r in rs]
        pos = {round(t["n"] * t["prevalence"]) for t in tb}
        assert len(pos) == 1, pos
        ot = {(r["eval_hash"], r["test_index"]) for _, r in old if r["split"] == s}
        assert len(ot) == 1, ot
        (oeh, oti), = ot
        facts[s] = {"eval_hash": eh, "orig_eval_hash": oeh, "test": sorted({x["subject"] for x in test}),
                    "val": sorted({x["subject"] for x in val}), "n_test": len(test), "pos": pos.pop(),
                    "orig_test": sorted({x["subject"] for x in index(oti)}),
                    "files": {x["key"].split("-")[0] for x in test},
                    "ssl_subjects": sorted({r["ssl_subjects"] for r in rs})}
        assert facts[s]["eval_hash"] != facts[s]["orig_eval_hash"], f"{tag} {s}: same eval set as {otags}"
    lines.append(f"  labels overlap, versions adapt 3 / probe 4, probe/adapt/arm specs = {otags} (except seed, "
                 f"split, data_hash, n_total, dataset), fold_seed override {fold_seed or 'none (config seed)'}; "
                 f"one eval set per rotation shared by both models, every rotation's eval_hash differs "
                 f"from {otags}")
    return lines, facts


def rotmeans(roc, model, arms) -> dict:
    out = {}
    for a in arms:
        cells = [roc[(model, a, s, "linear")] for s in ROTS]
        assert all(len(c) == 3 for c in cells), (model, a, [len(c) for c in cells])
        out[a] = [float(np.mean(list(c.values()))) for c in cells]
    return out


def contrasts(roc, model, arms, rng) -> dict:
    per = rotmeans(roc, model, arms)
    out = {}
    for a, b, name in CONTRASTS:
        if a not in per or b not in per:
            continue
        d = [x - y for x, y in zip(per[a], per[b], strict=True)]
        cl = [[roc[(model, a, s, "linear")][x] - roc[(model, b, s, "linear")][x] for x in SEEDS[s]] for s in ROTS]
        m, lo, hi = cluster_ci(cl, rng)
        assert abs(m - np.mean(d)) < 1e-9
        verdict = d17(per["last_randinit"], per["lp_randinit"]) if name == "D17" else \
            "reference only" if name == "all - last" else paired(d)
        out[name] = {"mean": float(np.mean(d)), "sem": float(np.std(d, ddof=1) / np.sqrt(5)),
                     "per_rot": d, "ci": [lo, hi], "verdict": verdict}
    return {"arms": {a: {"per_rot": v, "mean": float(np.mean(v)), "sem": float(np.std(v, ddof=1) / np.sqrt(5))}
                     for a, v in per.items()}, "contrasts": out}


def published_cis() -> dict:
    """(dataset, model, contrast name) -> [lo, hi] from artifacts/tables/d24-bootstrap.md."""
    names = {f"{a} - {b}": n for a, b, n in CONTRASTS}
    out = {}
    for line in (ROOT / "artifacts" / "tables" / "d24-bootstrap.md").read_text().splitlines():
        m = re.match(r"\| (\w+) \((S1E,S1M|S3E,S3M)\) \| (\w+) \| linear \| ([\w ]+ - [\w]+) \| ([+-][\d.]+) \| "
                     r"\[([+-][\d.]+), ([+-][\d.]+)\] \|", line)
        if m:
            out[(m[1], m[3], names[m[4]])] = {"mean": float(m[5]), "ci": [float(m[6]), float(m[7])]}
    assert len(out) == 20, len(out)
    return out


def overlap(a, b) -> bool:
    return a[0] <= b[1] and b[0] <= a[1]


def f(x) -> str:
    return f"{x:+.1f}"


def main() -> int:
    recs = scan()
    pub = published_cis()
    res: dict = {"E32": {}, "E33A": {}}
    checks: dict = {"E32": [], "E33A": []}
    mc = {"E32": 0.0, "E33A": 0.0}
    for item, ds, tag, arms, fold_seed, ods, otags, label in SETS:
        lines, facts = verify(recs, ds, tag, arms, fold_seed, ods, otags)
        checks[item] += lines
        new = farm_load(recs, ds, {tag})
        orig = farm_load(recs, ods, set(otags.split(",")))
        rng = np.random.default_rng(20261101)
        for model in MODELS:
            n = contrasts(new, model, arms, rng)
            # original: verdicts re-derived (must equal the published ones); CI = the published table,
            # re-bootstrapped with a fresh rng only to check the method (difference reported)
            o = contrasts(orig, model, (*A4, "all"), np.random.default_rng(20261101))
            got = tuple(o["contrasts"][k]["verdict"] for k in ("last - lp", "last_randinit - last",
                                                                "lp - lp_randinit", "D17"))
            assert got == D24[(ods, model)], (ods, model, got)
            for k, v in o["contrasts"].items():
                v["ci_recomputed"], v["ci"] = v["ci"], pub[(ods, model, k)]["ci"]
                assert abs(v["mean"] - pub[(ods, model, k)]["mean"]) < 0.051, (ods, model, k)
                drift = max(abs(a - b) for a, b in zip(v["ci"], v["ci_recomputed"], strict=True))
                mc[item] = max(mc[item], drift)
            for k, v in n["contrasts"].items():
                if k == "all - last":
                    continue
                ov = o["contrasts"][k]
                v["same_verdict"] = v["verdict"] == ov["verdict"]
                v["ci_overlap"] = overlap(v["ci"], ov["ci"])
                v["orig_mean_in_ci_posthoc"] = v["ci"][0] <= ov["mean"] <= v["ci"][1]
                v["replicated"] = v["same_verdict"] and v["ci_overlap"]
            res[item][f"{label}|{model}"] = {"new": n, "orig": o, "facts": facts, "tag": tag, "otags": otags}
    for item in mc:
        checks[item].append(f"- Method check: re-bootstrapping the D24-A records with a fresh rng(20261101) "
                            f"moves the published CI bounds by at most {mc[item]:.1f} ROC (Monte Carlo error; "
                            f"the published bounds are used)")
    write_e32(res["E32"], checks["E32"])
    write_e33a(res["E33A"], checks["E33A"], recs)
    return 0


def arm_lines(key, v) -> list[str]:
    out = []
    for a, x in v["new"]["arms"].items():
        o = v["orig"]["arms"][a]
        out.append(f"| {key} | {a} | {x['mean']:.1f} ± {x['sem']:.1f} | "
                   f"{', '.join(f'{y:.1f}' for y in x['per_rot'])} | "
                   f"{o['mean']:.1f} ± {o['sem']:.1f} | {', '.join(f'{y:.1f}' for y in o['per_rot'])} |")
    return out


def partition_lines(facts, tag, otags) -> list[str]:
    out = [f"| rotation | {tag} test subjects | n test windows | positive windows | {tag} val subjects | "
           f"{otags} test subjects | shared test subjects |", "|---|---|---|---|---|---|---|"]
    for s, x in facts.items():
        out.append(f"| {s} | {', '.join(x['test'])} | {x['n_test']:,} | {x['pos']} | {', '.join(x['val'])} | "
                   f"{', '.join(x['orig_test'])} | {len(set(x['test']) & set(x['orig_test']))} |")
    return out


def write_e32(res, checks) -> None:
    out = ROOT / "artifacts" / "analysis" / "E32"
    out.mkdir(parents=True, exist_ok=True)
    md = ["# D25-E32: second subject partition (fold_seed 20261101), read with the D24 rules", "",
          "Pre-registered rule (completeness-audit.md E32, adopted by D25): **replicated** if the same verdict "
          "string holds AND the CI overlaps the original (D24-A, S1E+S1M / S3E+S3M; CIs from "
          "artifacts/tables/d24-bootstrap.md). ROC-AUC x100, linear head, eval-mode probe, encoder tap.",
          "Verdicts: per-rotation 3-seed means, D18 paired rule (|mean| > 3, same sign >= 4/5) and D17. "
          "CIs: cluster bootstrap (rotations, then seeds), 10,000 resamples, rng 20261101 per set. "
          "\"CI overlaps\" = the two 95% intervals intersect. The column \"orig mean in new CI\" is post hoc "
          "(the other possible reading of \"overlaps the original\"). 3 seeds per rotation ran: no adaptation.",
          "", "Command: `.venv/bin/python scripts/analysis/e32_e33a.py`", "", "## Checks", "", *checks, "",
          "## Verdicts", "",
          "| dataset | model | contrast | E32 mean ± SEM (rot) | E32 per rotation | E32 95% CI | E32 verdict | "
          "D24-A mean | D24-A per rotation | D24-A 95% CI | D24-A verdict | same verdict | CI overlap | "
          "**replicated** | orig mean in new CI (post hoc) |", "|" + "---|" * 15]
    rows = [(key, k, x) for key, v in res.items() for k, x in v["new"]["contrasts"].items()]
    fails = [f"{key.replace('|', ' ')} {k}" for key, k, x in rows if not x["replicated"]]
    md[md.index("## Verdicts") + 2:md.index("## Verdicts") + 2] = [
        f"**Replicated (pre-registered rule): {len(rows) - len(fails)} of {len(rows)} verdicts.** Not replicated: "
        f"{'; '.join(fails) or 'none'}.", ""]
    for key, v in res.items():
        ds, model = key.split("|")
        for k, x in v["new"]["contrasts"].items():
            o = v["orig"]["contrasts"][k]
            md.append(f"| {ds} | {model} | {k} | {f(x['mean'])} ± {x['sem']:.1f} | "
                      f"{', '.join(f(y) for y in x['per_rot'])} | [{f(x['ci'][0])}, {f(x['ci'][1])}] | "
                      f"{x['verdict']} | {f(o['mean'])} | {', '.join(f(y) for y in o['per_rot'])} | "
                      f"[{f(o['ci'][0])}, {f(o['ci'][1])}] | {o['verdict']} | "
                      f"{'yes' if x['same_verdict'] else 'NO'} | "
                      f"{'yes' if x['ci_overlap'] else 'NO'} | **{'yes' if x['replicated'] else 'NO'}** | "
                      f"{'yes' if x['orig_mean_in_ci_posthoc'] else 'no'} |")
    md += ["", "For D17 the CI is that of last_randinit - lp_randinit (the D17 difference).", "",
           "## Arms (descriptive)", "",
           "| dataset, model | arm | E32 mean ± SEM (rot) | E32 per rotation | D24-A mean ± SEM | "
           "D24-A per rotation |",
           "|---|---|---|---|---|---|"]
    for key, v in res.items():
        md += arm_lines(key.replace("|", ", "), v)
    for ds in ("CHB-MIT", "Siena"):
        v = next(x for k, x in res.items() if k.startswith(ds + "|"))
        md += ["", f"## Partition, {ds} (descriptive)", "", *partition_lines(v["facts"], v["tag"], v["otags"])]
    (out / "README.md").write_text("\n".join(md) + "\n")
    (out / "e32.json").write_text(json.dumps({k: {"new": v["new"], "orig": v["orig"]} for k, v in res.items()},
                                             indent=1))
    print("\n".join(md))


def write_e33a(res, checks, recs) -> None:
    out = ROOT / "artifacts" / "analysis" / "E33A"
    out.mkdir(parents=True, exist_ok=True)
    v0 = next(iter(res.values()))
    facts = v0["facts"]
    # which EDFs the extended store adds: test windows over the 5 rotations cover every subject once
    files_x = set().union(*(x["files"] for x in facts.values()))
    old_ti = {r["test_index"] for _, r in recs if r["dataset"] == "chbmit" and r["run_tag"] in ("S1E", "S1M")}
    files_o = set().union(*({x["key"].split("-")[0] for x in index(t)} for t in old_ti))
    added = sorted(files_x - files_o)
    by_case = defaultdict(list)
    for a in added:
        by_case[a[:5]].append(a)   # chb17a_03 -> chb17
    same = [x["same_verdict"] for v in res.values() for k, x in v["new"]["contrasts"].items() if k != "all - last"]
    md = ["# D25-E33a: extended CHB-MIT store chbmit_x (23 subjects), read with the D24 rules", "",
          "Pre-registered (decisions.md \"D25 additions\"): chbmit_x store (chb12, chb13, chb17, chb02_16+ added; "
          "label-based channel selection), 23-subject rotations (seed 20261014), D24-A arms, 3 seeds, linear, "
          "eval mode, run tag S1X; D24 rules. ROC-AUC x100.",
          "Verdicts: per-rotation 3-seed means, D18 paired rule and D17 (as read_d24). CIs: the D24-D cluster "
          "bootstrap (rotations, then seeds; 10,000 resamples, rng 20261101). The comparison with D24-A CHB-MIT "
          "(S1E+S1M, 22 subjects, other folds) has no pre-registered rule: **descriptive/post hoc**.",
          "", "Command: `.venv/bin/python scripts/analysis/e32_e33a.py`", "", "## Checks", "", *checks,
          f"- Store content seen in the test indexes (5 rotations cover every subject once): {len(files_x)} EDFs "
          f"vs {len(files_o)} in chbmit_eval10; {len(added)} added: "
          + "; ".join(f"{c} x{len(v)}" if len(v) > 2 else f"{', '.join(v)}" for c, v in sorted(by_case.items())),
          f"- Nothing removed: {len(files_o - files_x)} chbmit_eval10 EDFs missing from chbmit_x.",
          "- n_present is not stored in the result records. The store report (chbmit_x_preprocess_report.json, "
          "desktop only) as logged in notes/WORKLOG.md 2026-11-01 10:55: all 78 added EDFs n_present 16/16; "
          "left out chb12_27/28/29 (0/16 by label, referential montage; 13 of chb12's 40 seizures).",
          "- Deviation from the pre-registered wording: the same label rule also added chb24_02 and chb24_22 "
          "(logged before the runs: WORKLOG 10:55, scripts/submit_d25.sh E33A comment).",
          "- The audit's \"also report on the old folds\" has no runs (no chbmit_x jobs on the 22-subject folds); "
          "D24-A (S1E+S1M) is the old-fold reference below.", "",
          "## Verdicts (pre-registered: D24 rules)", "",
          f"**Same verdict string as D24-A CHB-MIT (descriptive): {sum(same)} of {len(same)}.**", "",
          "| model | contrast | S1X mean ± SEM (rot) | S1X per rotation | S1X 95% CI | S1X verdict | D24-A mean | "
          "D24-A per rotation | D24-A 95% CI | D24-A verdict | same verdict (descr.) | CI overlap (descr.) |",
          "|" + "---|" * 12]
    for key, v in res.items():
        model = key.split("|")[1]
        for k, x in v["new"]["contrasts"].items():
            o = v["orig"]["contrasts"][k]
            sv = "" if k == "all - last" else "yes" if x["same_verdict"] else "NO"
            co = "yes" if overlap(x["ci"], o["ci"]) else "NO"
            md.append(f"| {model} | {k} | {f(x['mean'])} ± {x['sem']:.1f} | "
                      f"{', '.join(f(y) for y in x['per_rot'])} | "
                      f"[{f(x['ci'][0])}, {f(x['ci'][1])}] | {x['verdict']} | {f(o['mean'])} | "
                      f"{', '.join(f(y) for y in o['per_rot'])} | [{f(o['ci'][0])}, {f(o['ci'][1])}] | "
                      f"{o['verdict']} | {sv} | {co} |")
    md += ["", "D17 CI = last_randinit - lp_randinit. all - last is a reference (no rule), as in D24.", "",
           "## Arms (descriptive)", "",
           "| model | arm | S1X mean ± SEM (rot) | S1X per rotation | D24-A mean ± SEM | D24-A per rotation |",
           "|---|---|---|---|---|---|"]
    for key, v in res.items():
        md += arm_lines(key.split("|")[1], v)
    md += ["", "## Partition (descriptive; the D24-A rotations are over 22 subjects, so rotation r is NOT the "
           "same fold)", "", *partition_lines(facts, "S1X", "S1E,S1M")]
    (out / "README.md").write_text("\n".join(md) + "\n")
    (out / "e33a.json").write_text(json.dumps({k: {"new": v["new"], "orig": v["orig"]} for k, v in res.items()},
                                              indent=1))
    print("\n".join(md))


if __name__ == "__main__":
    raise SystemExit(main())
