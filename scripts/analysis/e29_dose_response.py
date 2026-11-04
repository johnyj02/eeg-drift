#!/usr/bin/env python3
"""D25-E29 SSL dose-response (notes/completeness-audit.md E29; tags in decisions.md "D25 parameters fixed").

    .venv/bin/python scripts/analysis/e29_dose_response.py

Cells (run tags S1LR<i> CHB-MIT, S3LR<i> Siena; arms last, all; seed S_r; both models; eval mode, linear):
  1 lr 3e-4, N 4,174 x 3 ep | 2 lr 1e-3, N 4,174 | 3 lr 3e-5, whole pool | 4 lr 3e-4, pool | 5 lr 1e-3, pool.
  Cell 0 = the existing D24 cell (lr 3e-5, N 4,174) at S_r, reference only, not counted.
Pair: base lp at seed S_r from the D24 records (S1E/S1M, S3E/S3M). ROC x100 at the val-selected epoch.
Rule (exploratory, as written): "more SSL helps" if any cell gives last - lp > 3 in >= 4/5 rotations;
report the number of cells tested. D18 paired output, all - lp, test_last and last - cell 0 are descriptive.
read_d24.load is not reused: it crashes on the val-index-*.json lists the D25 runs added.
Writes artifacts/analysis/E29/e29.md and e29.json.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from read_step1 import paired  # noqa: E402

LOCAL = ROOT / "artifacts" / "s3-results"
OUT = ROOT / "artifacts" / "analysis" / "E29"
S_R = (42, 123, 2021, 3407, 8888)
ROTS = tuple(f"rot{i}" for i in range(5))
MODELS = ("biot", "cbramod")
CELLS = {1: (3e-4, "4174"), 2: (1e-3, "4174"), 3: (3e-5, "pool"), 4: (3e-4, "pool"), 5: (1e-3, "pool")}
PFX = {"chbmit": "S1", "siena": "S3"}
BASE = {"chbmit": {"S1E", "S1M"}, "siena": {"S3E", "S3M"}}
REPRO = {"chbmit": "S1L", "siena": "S3L"}   # bit-identical logged re-runs (D25-E25), cross-check only
SPEC_DEFAULT = {"tap": "encoder", "input_norm": ""}   # ProbeSpec defaults; older records omit them
DOSE_KEYS = {"lr", "n_windows", "data_hash"}   # the only adapt_spec fields allowed to differ between cells


def fires(d) -> bool:
    return int((np.asarray(d) > 3).sum()) >= 4


def spec(r: dict) -> str:
    return json.dumps({**SPEC_DEFAULT, **r["probes"]["linear"]["spec"]}, sort_keys=True)


def adapt_fixed(r: dict) -> str:
    a = {"input_norm": "", **r["adapt_spec"]}   # field added for E19; older records omit the "" default
    return json.dumps({k: v for k, v in a.items() if k not in DOSE_KEYS}, sort_keys=True)


CHECKS = (("eval_hash", lambda r: r["eval_hash"]), ("test_index", lambda r: r["test_index"]),
          ("versions", lambda r: json.dumps(r["versions"], sort_keys=True)),
          ("ckpt", lambda r: r["adapt_spec"]["ckpt_sha256"]), ("probe spec", spec))


def records():
    tags = {f"{PFX[ds]}LR{i}" for ds in PFX for i in CELLS} | set().union(*BASE.values()) | set(REPRO.values())
    for p in LOCAL.rglob("results/*.json"):
        if p.name.startswith(("diag-", "test-index-", "val-index-", "report-")):
            continue
        r = json.loads(p.read_text())
        if isinstance(r, dict) and not r.get("smoke") and r.get("run_tag") in tags and r["dataset"] in PFX:
            yield p, r


def collect() -> dict:
    """(dataset, model, cell, arm, rot) -> (path, record); cell 0 = D24 last, 'lp' = base, 'lpL' = re-run."""
    rec: dict = {}
    for p, r in records():
        ds, tag, rot = r["dataset"], r["run_tag"], r["split"]
        if rot not in ROTS or "linear" not in r["probes"] or r["seed"] != S_R[ROTS.index(rot)]:
            continue
        if tag in BASE[ds]:
            cell = {"lp": "lp", "last": 0}.get(r["arm"])
        elif tag == REPRO[ds]:
            cell = "lpL" if r["arm"] == "lp" else None
        else:
            cell = int(tag[-1]) if r["arm"] in ("last", "all") else None
        if cell is None:
            continue
        k = (ds, r["model"], cell, r["arm"], rot)
        if k in rec:
            raise SystemExit(f"two records for {k}: {rec[k][0].name}, {p.name}")
        rec[k] = (p, r)
    return rec


def check(rec: dict) -> tuple[list[str], list[str]]:
    gaps, notes = [], []
    counts: dict = defaultdict(int)
    for (ds, m, cell, arm, _), (p, r) in rec.items():
        counts[(ds, m, cell, arm)] += 1
        s = json.loads(spec(r))
        if (r["versions"] != {"adapt": 3, "probe": 4} or s["backbone_mode"] != "eval" or r["labels"] != "overlap"
                or s["tap"] != "encoder" or s["input_norm"]):
            gaps.append(f"{p.name}: versions/mode/labels/tap off: {r['versions']} {s}")
        if isinstance(cell, int) and cell > 0:
            lr, n = CELLS[cell]
            a, ad = r["adapt_spec"], r["adapt"]
            want_n = 4174 if n == "4174" else a["n_total"]
            if abs(a["lr"] - lr) > 1e-12 or a["epochs"] != 3 or a["n_windows"] != want_n:
                gaps.append(f"{p.name}: adapt lr {a['lr']} ep {a['epochs']} n {a['n_windows']}/{a['n_total']}")
            if ad["skipped_nonfinite"] or not np.all(np.isfinite(ad["epoch_losses"])):
                notes.append(f"{p.name}: nonfinite SSL steps {ad['skipped_nonfinite']}, {ad['epoch_losses']}")
    for ds in PFX:
        for m in MODELS:
            expected = [("lp", "lp"), ("lpL", "lp"), (0, "last")]
            expected += [(c, a) for c in CELLS for a in ("last", "all")]
            for cell, arm in expected:
                if counts[(ds, m, cell, arm)] != 5:
                    gaps.append(f"{ds} {m} cell {cell} {arm}: {counts[(ds, m, cell, arm)]} of 5")
            for rot in ROTS:
                group = [(k, r) for k, (_, r) in rec.items() if k[:2] == (ds, m) and k[4] == rot]
                for name, f in CHECKS:
                    if len(vals := {f(r) for _, r in group}) > 1:
                        gaps.append(f"{ds} {m} {rot}: {name} differs: {sorted(vals)[:3]}")
                for arm in ("last", "all"):   # cells may differ only in lr / N (and the SSL data hash)
                    same = {(adapt_fixed(r), json.dumps(r["arm_spec"], sort_keys=True))
                            for k, r in group if k[3] == arm and k[2] not in ("lp", "lpL")}
                    if len(same) > 1:
                        gaps.append(f"{ds} {m} {rot} {arm}: adapt/arm spec differs beyond lr/N")
    return gaps, notes


def main() -> int:
    assert fires([4, 4, 4, 4, -9]) and not fires([4, 4, 4, 3, 3]) and not fires([9, 9, 9, 2, 2])
    rec = collect()
    gaps, notes = check(rec)
    if gaps:
        print("\n".join(["GAPS:", *gaps]))
        return 1
    roc = {k: 100 * r["probes"]["linear"]["test_at_best"]["roc_auc"] for k, (_, r) in rec.items()}
    rocl = {k: 100 * r["probes"]["linear"]["test_last"]["roc_auc"] for k, (_, r) in rec.items()}
    off = [k for k in roc if k[2] == "lp" and abs(roc[k] - roc[(*k[:2], "lpL", *k[3:])]) > 1e-6]
    notes.append(f"base lp vs S1L/S3L logged re-runs: {20 - len(off)} of 20 identical (|diff| < 1e-6)")

    def d(ds, m, cell, arm, src=roc):
        return [src[(ds, m, cell, arm, r)] - src[(ds, m, "lp", "lp", r)] for r in ROTS]

    md = ["# D25-E29 SSL dose-response: last - lp (ROC x100, val-selected epoch, linear, eval, S_r)", "",
          'Rule (exploratory): "more SSL helps" if any cell gives last - lp > 3 in >= 4/5 rotations.',
          "Cell 0 = existing D24 cell at S_r (reference, not counted). n>3 = rotations with last - lp > 3.",
          "D18 paired rule, all - lp, the test_last version and last - cell 0 are descriptive / post hoc.", "",
          "| dataset | model | cell | lr | SSL N | lp mean | last mean | last - lp mean | per rotation | n>3 "
          "| rule | D18 (descr.) | all - lp mean (descr.) | last - lp at test_last, n>3 (descr.) "
          "| last - last(cell 0) mean, n>3 (post hoc) |",
          "|" + "---|" * 15]
    rows = []
    for ds in PFX:
        for m in MODELS:
            lp = [roc[(ds, m, "lp", "lp", r)] for r in ROTS]
            for cell in (0, *CELLS):
                lr, n = (3e-5, "4174") if cell == 0 else CELLS[cell]
                x, xl = d(ds, m, cell, "last"), d(ds, m, cell, "last", rocl)
                x0 = [v - w for v, w in zip(x, d(ds, m, 0, "last"), strict=True)]
                last = [roc[(ds, m, cell, "last", r)] for r in ROTS]
                allv = float(np.mean(d(ds, m, cell, "all"))) if cell else None
                row = {"dataset": ds, "model": m, "cell": cell, "lr": lr, "n": n, "lp": lp, "last": last, "d": x,
                       "n_gt3": int((np.asarray(x) > 3).sum()), "fires": fires(x), "d18": paired(x),
                       "all_minus_lp_mean": allv, "d_test_last": xl, "last_minus_cell0": x0}
                rows.append(row)
                ref = cell == 0
                md.append(" | ".join([
                    f"| {ds}", m, f"{cell}{' (ref)' if ref else ''}", f"{lr:g}", n, f"{np.mean(lp):.1f}",
                    f"{np.mean(last):.1f}", f"{np.mean(x):+.1f}", ", ".join(f"{v:+.1f}" for v in x),
                    f"{row['n_gt3']}/5", "FIRES" if row["fires"] else "no", row["d18"],
                    "" if ref else f"{allv:+.1f}", f"{np.mean(xl):+.1f}, {sum(v > 3 for v in xl)}/5",
                    "" if ref else f"{np.mean(x0):+.1f}, {sum(v > 3 for v in x0)}/5"]) + " |")
    tested = [r for r in rows if r["cell"] != 0]
    hit = [r for r in tested if r["fires"]]
    md += ["", f"Cells tested: {len(tested)} (2 datasets x 2 models x 5 cells). Cells that fire: "
           + (", ".join(f"{r['dataset']} {r['model']} cell {r['cell']}" for r in hit) or "none") + ".", ""]
    for ds in PFX:
        for m in MODELS:
            h = [r["cell"] for r in hit if r["dataset"] == ds and r["model"] == m]
            md.append(f"- {ds} {m}: **{'more SSL helps' if h else 'more SSL helps NOT shown'}**"
                      + (f" (cells {h})" if h else ""))
    md += ["", "Notes:"] + [f"- {s}" for s in notes]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "e29.md").write_text("\n".join(md) + "\n")
    out = {"cells_tested": len(tested), "rows": rows, "notes": notes}
    (OUT / "e29.json").write_text(json.dumps(out, indent=1))
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
