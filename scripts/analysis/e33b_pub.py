#!/usr/bin/env python3
"""D25-E33b (notes/completeness-audit.md; notes/decisions.md "D25 additions"): Siena published-style
split "pub" (test PN13/14/16/17 as CSBrain, val PN10/12, rest train), run tags S3P (Siena) and S3FP
(Siena filtered), arms lp / last / lp_randinit, seeds 42/1000/2000, BIOT and CBraMod, eval-mode
probe, encoder tap, linear head. Pre-registered as DESCRIPTIVE (one split): no verdict rule.

Reports mean +/- SEM over the 3 seeds per arm, last - lp and lp - lp_randinit paired by seed, next to
the 5-rotation D24-A numbers (S3E+S3M, S3FE+S3FM; per-rotation seed means, D24 verdict strings).
Primary metric: test_at_best ROC x100 (as read_d24). test_last ROC and the "|mean| > 3 and 3/3 same
sign" flag are post hoc. Verifies record counts, eval data, labels, versions and the split's subjects
before reading. CPU, seconds.

    .venv/bin/python scripts/analysis/e33b_pub.py

Writes artifacts/analysis/E33b/e33b_pub.{md,json}.
"""

from __future__ import annotations

import json
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from read_d24 import ROTS, load  # noqa: E402
from read_step1 import paired  # noqa: E402

LOCAL = ROOT / "artifacts" / "s3-results"
OUT = ROOT / "artifacts" / "analysis" / "E33b"
SETS = (("S3P", "S3E,S3M", "Siena"), ("S3FP", "S3FE,S3FM", "Siena filtered"))
MODELS = ("biot", "cbramod")
ARMS = ("lp", "last", "lp_randinit")
SEEDS = (42, 1000, 2000)
CONTRASTS = (("last", "lp"), ("lp", "lp_randinit"))
PUB = {"test": {"PN13", "PN14", "PN16", "PN17"}, "val": {"PN10", "PN12"}}


def ms(v) -> tuple[float, float]:
    v = np.asarray(v, dtype=float)
    return float(v.mean()), float(v.std(ddof=1) / np.sqrt(len(v)))


def records(tags: set[str]) -> list[tuple[Path, dict]]:
    out = []
    for p in LOCAL.rglob("results/*.json"):
        if p.name.startswith(("diag-", "test-index-", "val-index-", "report-")):
            continue
        r = json.loads(p.read_text())
        if r.get("dataset") == "siena" and r.get("run_tag") in tags:
            out.append((p, r))
    return out


def load_tags(tags: set[str]) -> dict:
    """read_d24.load on just these records. ponytail: load() skips test-index- but not the D25
    val-index-*.json files and crashes on them, so it gets a symlink farm instead of an edit."""
    with tempfile.TemporaryDirectory() as tmp:
        for p, _ in records(tags):
            d = Path(tmp) / p.parent.parent.name / "results"
            d.mkdir(parents=True, exist_ok=True)
            (d / p.name).symlink_to(p)
        return load(tmp, "siena", tags)


def verify(tag: str, d24_tags: str) -> tuple[list[str], dict, list[str]]:
    """Fail loudly on any gap; return report lines, {(model, arm, seed): {best, last, n, pos}}, test keys."""
    recs = records({tag})
    lines, vals = [], {}
    count = defaultdict(int)
    for _, r in recs:
        count[(r["model"], r["arm"], r["seed"])] += 1
    want = {(m, a, s) for m in MODELS for a in ARMS for s in SEEDS}
    assert set(count) == want and all(v == 1 for v in count.values()), \
        f"{tag}: cells {sorted(set(count) ^ want)}, duplicates {[k for k, v in count.items() if v > 1]}"
    lines.append(f"- {tag}: {len(recs)} records = 2 models x 3 arms x 3 seeds, exactly 1 per cell")
    same = {(r["eval_hash"], r["labels"], json.dumps(r["versions"], sort_keys=True), r["split"],
             r["test_index"], r["val_index"], r["adapt_spec"]["data_hash"], r["ssl_subjects"]) for _, r in recs}
    assert len(same) == 1, f"{tag}: mixed eval data / labels / versions / SSL pool: {same}"
    eh, labels, ver, split, ti, vi, dh, nsub = next(iter(same))
    assert split == "pub" and labels == "overlap", (split, labels)
    for p, r in recs:
        assert not r.get("smoke") and set(r["probes"]) == {"linear"}, p.name
        spec = r["probes"]["linear"]["spec"]
        got = (spec["backbone_mode"], spec["tap"], spec["variant"], spec["split"])
        assert got == ("eval", "encoder", "linear", "pub"), p.name
        assert r["adapt_spec"]["init"] == ("random" if r["arm"].endswith("randinit") else "pretrained"), p.name
        best, last = r["probes"]["linear"]["test_at_best"], r["probes"]["linear"]["test_last"]
        vals[(r["model"], r["arm"], r["seed"])] = {"best": 100 * best["roc_auc"], "last": 100 * last["roc_auc"],
                                                   "n": best["n"], "pos": round(best["n"] * best["prevalence"])}
    # split subjects, from the index files saved next to every record
    subj = {}
    for kind, name in (("test", ti), ("val", vi)):
        idx = {json.dumps(json.loads(p.read_text())) for p in LOCAL.rglob(f"results/{name}")}
        assert len(idx) == 1, f"{tag}: {len(idx)} different {name} copies"
        rows = json.loads(next(iter(idx)))
        subj[kind] = {x["subject"] for x in rows}
        assert subj[kind] == PUB[kind], (tag, kind, subj[kind])
        if kind == "test":
            assert {v["n"] for v in vals.values()} == {len(rows)}, "test n differs from the index"
            test_keys = [x["key"] for x in rows]
    pos = {v["pos"] for v in vals.values()}
    assert len(pos) == 1, pos
    # versions and hyperparameters match the D24 records this is compared with (keys the older
    # records lack, e.g. tap / input_norm, are compared only where both have them)
    old = records(set(d24_tags.split(",")))
    d24ver = {json.dumps(r["versions"], sort_keys=True) for _, r in old}
    assert d24ver == {ver}, (tag, d24ver, ver)
    skip = {"seed", "split", "data_hash", "n_total"}
    for _, r in recs:
        ref = next(o for _, o in old if (o["model"], o["arm"]) == (r["model"], r["arm"]))
        for new, prev in ((r["probes"]["linear"]["spec"], ref["probes"]["linear"]["spec"]),
                          (r["adapt_spec"], ref["adapt_spec"]), (r["arm_spec"], ref["arm_spec"])):
            bad = {k for k in set(new) & set(prev) - skip if new[k] != prev[k]}
            assert not bad, (tag, r["model"], r["arm"], bad)
    lines.append(f"  eval_hash {eh} (one for both models), labels {labels}, versions {ver} and "
                 f"probe/adapt/arm specs = {d24_tags}, SSL data_hash {dh} ({nsub} subjects), "
                 f"test {sorted(subj['test'])} n={len(test_keys)} pos={pos.pop()}, val {sorted(subj['val'])}")
    # load() is the D24 reader's guard (v4, eval mode, one record per seed, no mixed eval data)
    roc = load_tags({tag})
    for (m, a, s), v in vals.items():
        assert abs(roc[(m, a, "pub", "linear")][s] - v["best"]) < 1e-9
    return lines, vals, test_keys


def d24(tags: str) -> dict:
    """model -> {arm or contrast: per-rotation values} from the D24-A records (3 seeds per rotation)."""
    roc = load_tags(set(tags.split(",")))
    out = {}
    for m in MODELS:
        per = {}
        for a in ARMS:
            cells = [roc[(m, a, r, "linear")] for r in ROTS]
            assert all(len(c) == 3 for c in cells), (tags, m, a, [len(c) for c in cells])
            per[a] = [float(np.mean(list(c.values()))) for c in cells]
        for a, b in CONTRASTS:
            per[f"{a} - {b}"] = [x - y for x, y in zip(per[a], per[b], strict=True)]
        out[m] = per
    return out


def flag(d) -> str:
    """Post hoc: |mean| > 3 and the same sign in 3/3 seeds."""
    d = np.asarray(d)
    if d.mean() > 3 and (d > 0).all():
        return "3/3 +, >3"
    return "3/3 -, < -3" if d.mean() < -3 and (d < 0).all() else "-"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    md = ["# D25-E33b: Siena published-style split 'pub' (test PN13/14/16/17, val PN10/12)", "",
          "Pre-registered (decisions.md D25 additions): descriptive, one split; no verdict rule.",
          "ROC-AUC x100, linear head, eval-mode probe, encoder tap. pub = mean +/- SEM over 3 seeds "
          "(42/1000/2000; SEM is seed noise only, one fixed split). D24 = mean +/- SEM over 5 rotation "
          "seed-means (S3E+S3M / S3FE+S3FM). test_last and the 3/3 flag are post hoc.", "", "## Checks", ""]
    js: dict = {}
    keys = {}
    for tag, d24_tags, name in SETS:
        lines, vals, keys[tag] = verify(tag, d24_tags)
        md += lines
        ref = d24(d24_tags)
        for m in MODELS:
            row = js.setdefault(name, {}).setdefault(m, {})
            for a in ARMS:
                b = [vals[(m, a, s)]["best"] for s in SEEDS]
                last = [vals[(m, a, s)]["last"] for s in SEEDS]
                row[a] = {"pub_per_seed": b, "pub": ms(b), "pub_last": ms(last), "d24_per_rot": ref[m][a],
                          "d24": ms(ref[m][a])}
            for a, b in CONTRASTS:
                d = [vals[(m, a, s)]["best"] - vals[(m, b, s)]["best"] for s in SEEDS]
                dl = [vals[(m, a, s)]["last"] - vals[(m, b, s)]["last"] for s in SEEDS]
                k = f"{a} - {b}"
                row[k] = {"pub_per_seed": d, "pub": ms(d), "pub_last": ms(dl), "flag_posthoc": flag(d),
                          "d24_per_rot": ref[m][k], "d24": ms(ref[m][k]), "d24_verdict": paired(ref[m][k])}
    assert keys["S3P"] == keys["S3FP"], "S3P and S3FP test windows differ"
    md.append("- S3P and S3FP test on the same 14,083 window keys (filtered signal, different eval_hash)")
    md += ["", "## Results", "",
           "| setting | model | quantity | pub mean ± SEM (3 seeds) | pub per seed (42/1000/2000) | "
           "pub test_last (post hoc) | 3/3 flag (post hoc) | D24 5-rot mean ± SEM | D24 per rotation | "
           "D24 verdict | pub inside D24 range? |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, models in js.items():
        for m, row in models.items():
            for k, v in row.items():
                lo, hi = min(v["d24_per_rot"]), max(v["d24_per_rot"])
                sgn = "+" if " - " in k else ""
                md.append(f"| {name} | {m} | {k} | {v['pub'][0]:{sgn}.1f} ± {v['pub'][1]:.1f} | "
                          f"{', '.join(f'{x:{sgn}.1f}' for x in v['pub_per_seed'])} | "
                          f"{v['pub_last'][0]:{sgn}.1f} ± {v['pub_last'][1]:.1f} | {v.get('flag_posthoc', '')} | "
                          f"{v['d24'][0]:{sgn}.1f} ± {v['d24'][1]:.1f} | "
                          f"{', '.join(f'{x:{sgn}.1f}' for x in v['d24_per_rot'])} | {v.get('d24_verdict', '')} | "
                          f"{'yes' if lo <= v['pub'][0] <= hi else 'NO'} [{lo:{sgn}.1f}, {hi:{sgn}.1f}] |")
    md += ["", "Verdict (pre-registered): descriptive only (one split); no rule is applied to these numbers."]
    (OUT / "e33b_pub.md").write_text("\n".join(md) + "\n")
    (OUT / "e33b_pub.json").write_text(json.dumps(js, indent=1))
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
