#!/usr/bin/env python3
"""D25-E19 (notes/completeness-audit.md): native input scaling, read with the rules fixed in D25.

    .venv/bin/python scripts/analysis/e19_input_scaling.py

BIOT q95 (S1Q, S3Q, S3FQ, P1Q) vs the D24 /100 runs (S1E+S1M, S3E+S3M, S3FE+S3FM, P1E);
CBraMod SSL at /100 (S1C, S3C, S3FC; arms last, all) vs the D24 /700 runs. ROC x100, test_at_best,
linear head, per-rotation means over the 3 D24-A seeds, as read_d24.py.
Rules (D25-E19):
  R1 "input scaling changes the BIOT conclusion" if any D24-A BIOT verdict string changes
     (last - lp, last_randinit - last, lp - lp_randinit by the D18 paired rule; D17);
  R2 "frozen BIOT input-limited" if lp(q95) - lp(/100) > 3 in >= 4/5 rotations (per dataset);
  R3 CBraMod "SSL scale matters" if last(/100) - last(/700) wins by the D18 rule (per dataset).
Everything else (P1Q, all arm, last - lp at /100, bootstrap CIs) is descriptive.
read_d24.load is not used: it crashes on the val-index-*.json lists that E25 added to results/.
Writes artifacts/analysis/E19/e19.md and e19.json.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from bootstrap_d24 import cluster_ci  # noqa: E402
from read_d24 import ARMS, ROTS, ms  # noqa: E402
from read_step1 import d17, paired  # noqa: E402

LOCAL = ROOT / "artifacts" / "s3-results"
OUT = ROOT / "artifacts" / "analysis" / "E19"
S_R = (42, 123, 2021, 3407, 8888)
SEEDS = {f"rot{r}": {S_R[r], 1000 + r, 2000 + r} for r in range(5)} | {"paper": set(S_R)}
BIOT_SETS = (("CHB-MIT", "chbmit", "S1Q", "S1E,S1M"), ("Siena", "siena", "S3Q", "S3E,S3M"),
             ("Siena filtered", "siena", "S3FQ", "S3FE,S3FM"))
CBRA_SETS = (("CHB-MIT", "chbmit", "S1C", "S1E,S1M"), ("Siena", "siena", "S3C", "S3E,S3M"),
             ("Siena filtered", "siena", "S3FC", "S3FE,S3FM"))
CONTRASTS = (("last", "lp"), ("last_randinit", "last"), ("lp", "lp_randinit"))
# the only fields allowed to differ between the two sides of a comparison
EXPECTED = {"biot": {"adapt": {"input_norm"}, "probe": {"input_norm"}},
            "cbramod": {"adapt": {"scale"}, "probe": set()}}


def load(dataset: str, tags: str, model: str, arms=ARMS) -> tuple[dict, dict]:
    """(arm, split, probe) -> {seed: roc x100}, (arm, split, seed) -> record. Same refusals as
    read_d24.load (probe v4, eval mode, one record per seed, one eval hash/labels/adapt code)."""
    roc, rec, same = defaultdict(dict), {}, defaultdict(set)
    for p in LOCAL.rglob("results/*.json"):
        if p.name.startswith(("diag-", "test-index-", "val-index-", "report-")):
            continue
        r = json.loads(p.read_text())
        if (r.get("smoke") or r["dataset"] != dataset or r.get("run_tag") not in tags.split(",")
                or r["model"] != model or r["arm"] not in arms):
            continue
        same[r["split"]].add((r["eval_hash"], r.get("labels"), r["versions"]["adapt"]))
        if (r["arm"], r["split"], r["seed"]) in rec:
            raise SystemExit(f"two records for {model} {r['arm']} {r['split']} seed {r['seed']}")
        rec[(r["arm"], r["split"], r["seed"])] = r
        for probe, res in r["probes"].items():
            if r["versions"]["probe"] != 4 or res["spec"].get("backbone_mode") != "eval":
                raise SystemExit(f"{p.name}: not a probe-v4 eval-mode record")
            roc[(r["arm"], r["split"], probe)][r["seed"]] = 100 * res["test_at_best"]["roc_auc"]
    if any(len(v) > 1 for v in same.values()):
        raise SystemExit(f"{tags}: eval data, labels or adapt code mixed within a split: {dict(same)}")
    return roc, rec


def norm(d: dict) -> dict:
    """Spec with the defaults of fields added after D24 (tap, input_norm) filled in."""
    return {"tap": "encoder", **d, "input_norm": d.get("input_norm") or ""}


def check(model: str, new: dict, base: dict, splits, arms, probes) -> list[str]:
    """Counts per cell and field-by-field equality of every new record with its baseline twin."""
    gaps = []
    for split in splits:
        for arm in arms:
            for probe in probes:
                for side, roc in (("new", new[0]), ("base", base[0])):
                    got = set(roc.get((arm, split, probe), {}))
                    if got != SEEDS[split]:
                        gaps.append(f"{side} {arm}/{split}/{probe}: seeds {sorted(got)}")
            for seed in SEEDS[split]:
                a, b = new[1].get((arm, split, seed)), base[1].get((arm, split, seed))
                if not (a and b):
                    continue
                for f in ("eval_hash", "labels", "versions", "ssl_subjects", "test_index"):
                    if a.get(f) != b.get(f):
                        gaps.append(f"{arm}/{split}/s{seed}: {f} {a.get(f)} vs {b.get(f)}")
                ad = {k for k in set(a["adapt_spec"]) | set(b["adapt_spec"])
                      if norm(a["adapt_spec"]).get(k) != norm(b["adapt_spec"]).get(k)}
                if ad - EXPECTED[model]["adapt"]:
                    gaps.append(f"{arm}/{split}/s{seed}: adapt_spec differs in {sorted(ad)}")
                for probe in probes:
                    pa, pb = norm(a["probes"][probe]["spec"]), norm(b["probes"][probe]["spec"])
                    pd = {k for k in set(pa) | set(pb) if pa.get(k) != pb.get(k)}
                    if pd - EXPECTED[model]["probe"]:
                        gaps.append(f"{arm}/{split}/s{seed}/{probe}: probe spec differs in {sorted(pd)}")
    return gaps


def rot_means(roc: dict, arm: str, probe: str = "linear") -> list[float]:
    return [float(np.mean(list(roc[(arm, r, probe)].values()))) for r in ROTS]


def fmt(v) -> str:
    return ", ".join(f"{x:+.1f}" for x in v)


def ci(new: dict, base: dict, arm_a: str, arm_b: str, rng) -> str:
    """Cluster bootstrap (bootstrap_d24) of new[arm_a] - base[arm_b], paired by seed in a rotation."""
    diffs = [[new[(arm_a, r, "linear")][s] - base[(arm_b, r, "linear")][s] for s in sorted(SEEDS[r])]
             for r in ROTS]
    m, lo, hi = cluster_ci(diffs, rng)
    return f"{m:+.1f} [{lo:+.1f}, {hi:+.1f}]"


def main() -> int:
    rng = np.random.default_rng(20261101)
    L = ["# D25-E19: native input scaling (ROC-AUC x100, test_at_best, linear head unless stated)", "",
         "Per-rotation values are means over the 3 D24-A seeds [S_r, 1000+r, 2000+r]. Rules D25-E19.", ""]
    J: dict = {"biot": {}, "cbramod": {}, "gaps": []}
    gaps = J["gaps"]

    # ---- BIOT, rotations: R1 and R2
    L += ["## BIOT q95 vs /100 (D24-A arms, 5 rotations x 3 seeds)", ""]
    changed = []
    for name, ds, qt, bt in BIOT_SETS:
        q, b = load(ds, qt, "biot"), load(ds, bt, "biot")
        gaps += [f"BIOT {name}: {g}" for g in check("biot", q, b, ROTS, ARMS, ["linear"])]
        Q = {a: rot_means(q[0], a) for a in ARMS}
        B = {a: rot_means(b[0], a) for a in ARMS}
        L += [f"### {name} ({qt} vs {bt})", "",
              "| arm | q95 mean ± SEM | /100 mean ± SEM | q95 - /100 per rotation |", "|---|---|---|---|"]
        L += [f"| {a} | {ms(Q[a])} | {ms(B[a])} | {fmt(np.subtract(Q[a], B[a]))} |" for a in ARMS]
        L += ["", "| D24-A contrast | q95 mean; per rotation -> verdict | /100 mean; per rotation -> verdict "
              "| changed? |", "|---|---|---|---|"]
        J["biot"][name] = {"q95": Q, "d100": B, "verdicts": {}}
        for x, y in CONTRASTS + (("D17", ""),):
            if x == "D17":
                vq, vb = d17(Q["last_randinit"], Q["lp_randinit"]), d17(B["last_randinit"], B["lp_randinit"])
                dq = np.subtract(Q["last_randinit"], Q["lp_randinit"])
                db = np.subtract(B["last_randinit"], B["lp_randinit"])
                label = "D17 (last_randinit vs lp_randinit)"
            else:
                dq, db = np.subtract(Q[x], Q[y]), np.subtract(B[x], B[y])
                vq, vb = paired(dq), paired(db)
                label = f"{x} - {y}"
            ch = vq != vb
            if ch:
                changed.append(f"{name} {label}: '{vb}' -> '{vq}'")
            J["biot"][name]["verdicts"][label] = {"q95": vq, "d100": vb, "q95_diff": list(dq),
                                                  "d100_diff": list(db)}
            L.append(f"| {label} | {dq.mean():+.1f}; {fmt(dq)} -> **{vq}** | {db.mean():+.1f}; {fmt(db)} -> {vb} "
                     f"| {'**CHANGED**' if ch else 'no'} |")
        d = np.subtract(Q["lp"], B["lp"])
        n = int((d > 3).sum())
        J["biot"][name]["R2"] = {"diff": list(d), "n_gt3": n, "fires": n >= 4}
        L += ["", f"- R2 lp(q95) - lp(/100): mean {d.mean():+.1f}, per rotation {fmt(d)}; > +3 in {n}/5 -> "
              f"**{'frozen BIOT input-limited' if n >= 4 else 'does not fire'}**",
              f"- descriptive: cluster-bootstrap 95% CI of lp(q95) - lp(/100) {ci(q[0], b[0], 'lp', 'lp', rng)}; "
              f"all - last q95 {np.mean(Q['all']) - np.mean(Q['last']):+.1f}, /100 "
              f"{np.mean(B['all']) - np.mean(B['last']):+.1f}", ""]
    J["biot"]["R1_changed"] = changed
    r2 = {n: J["biot"][n]["R2"]["fires"] for n, *_ in BIOT_SETS}

    # ---- BIOT paper split (descriptive w.r.t. E19; D24-B rule applied)
    L += ["## BIOT paper split: P1Q vs P1E (5 seeds; descriptive for E19, D24-B rule on the SA gain)", ""]
    q, b = load("chbmit", "P1Q", "biot"), load("chbmit", "P1E", "biot")
    parms = ("lp", "last", "last_randinit", "lp_randinit")
    gaps += [f"BIOT paper: {g}" for g in check("biot", q, b, ["paper"], parms, ["linear", "mlp_fullft"])]
    J["biot"]["paper"] = {}
    for probe in ("linear", "mlp_fullft"):
        L += [f"### {probe}", "", "| arm | q95 | /100 | q95 - /100 per seed |", "|---|---|---|---|"]
        for a in parms:
            vq = [q[0][(a, "paper", probe)][s] for s in S_R]
            vb = [b[0][(a, "paper", probe)][s] for s in S_R]
            J["biot"]["paper"][f"{probe}/{a}"] = {"q95": vq, "d100": vb}
            L.append(f"| {a} | {ms(vq)} | {ms(vb)} | {fmt(np.subtract(vq, vb))} |")
        for side, src in (("q95", q[0]), ("/100", b[0])):
            g = [src[("last", "paper", probe)][s] - src[("lp", "paper", probe)][s] for s in S_R]
            L.append(f"- SA gain last - lp, {side}: {ms(g)}, per seed {fmt(g)} -> {paired(g)} (D24-B rule)")
        L.append("")

    # ---- CBraMod: R3
    L += ["## CBraMod SSL /100 vs /700 (arms last, all; 5 rotations x 3 seeds)", "",
          "| setting | last /100 mean ± SEM | last /700 mean ± SEM | last(/100) - last(/700) per rotation "
          "| D18 rule | R3 | bootstrap CI (descr.) | all(/100) - all(/700) (descr.) | last(/100) - lp (descr.) |",
          "|---|---|---|---|---|---|---|---|---|"]
    r3 = {}
    for name, ds, ct, bt in CBRA_SETS:
        c, b = load(ds, ct, "cbramod", ("last", "all")), load(ds, bt, "cbramod")
        gaps += [f"CBraMod {name}: {g}" for g in check("cbramod", c, b, ROTS, ("last", "all"), ["linear"])]
        steps = {r["adapt"]["steps"] for r in c[1].values()}
        moved = min(r["displacement"]["block11"]["rel"] for r in c[1].values())
        if steps != {51} or moved <= 0:
            gaps.append(f"CBraMod {name}: adapt steps {steps}, min block11 rel displacement {moved}")
        C = {a: rot_means(c[0], a) for a in ("last", "all")}
        B = {a: rot_means(b[0], a) for a in ("last", "all", "lp")}
        d = np.subtract(C["last"], B["last"])
        v = paired(d)
        r3[name] = v != "no difference shown"
        da, dl = np.subtract(C["all"], B["all"]), np.subtract(C["last"], B["lp"])
        J["cbramod"][name] = {"s100": C, "s700": B, "diff": list(d), "verdict": v, "fires": r3[name]}
        L.append(f"| {name} | {ms(C['last'])} | {ms(B['last'])} | {fmt(d)} (mean {d.mean():+.1f}) | {v} | "
                 f"**{'SSL scale matters' if r3[name] else 'does not fire'}** "
                 f"| {ci(c[0], b[0], 'last', 'last', rng)} "
                 f"| {da.mean():+.1f} ({fmt(da)}) | {dl.mean():+.1f} ({fmt(dl)}) -> {paired(dl)} |")

    # ---- verdicts
    v1 = ("**input scaling changes the BIOT conclusion**: " + "; ".join(changed) if changed
          else "no D24-A BIOT verdict string changes -> **input scaling does not change the BIOT conclusion**")
    on2, on3 = [k for k, f in r2.items() if f], [k for k, f in r3.items() if f]
    v2 = f"frozen BIOT input-limited on {', '.join(on2)}" if on2 else "frozen BIOT not shown input-limited"
    v3 = f"SSL scale matters on {', '.join(on3)}" if on3 else "SSL scale does not matter (no difference shown)"
    L += ["", "## Pre-registered verdicts (D25-E19)", "", f"- R1: {v1}",
          "- R2: " + ", ".join(f"{k} {J['biot'][k]['R2']['n_gt3']}/5" for k in r2) + f" -> **{v2}**",
          "- R3: " + ", ".join(f"{k} {J['cbramod'][k]['verdict']}" for k in r3) + f" -> **{v3}**",
          "", "## Integrity", ""]
    L += [f"- GAP: {g}" for g in gaps] or [
        "- all cells complete (15 runs per rotation arm, 5 per paper arm); every new record matches its "
        "baseline twin in eval_hash, labels, code versions, ssl_subjects, test_index and every spec field "
        "except the manipulated one"]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "e19.md").write_text("\n".join(L) + "\n")
    (OUT / "e19.json").write_text(json.dumps(J, indent=1, default=float))
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
