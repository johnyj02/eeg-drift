#!/usr/bin/env python3
"""D25-E17: CBraMod probe tap x backbone mode, 2x2 in our pipeline (notes/completeness-audit.md E17).

    .venv/bin/python scripts/analysis/e17_tap_mode.py

Cells (tap, mode):            paper split (5 seeds, both heads)   rotations (seed S_r, linear)
  encoder,  eval              P1E                                  S1E
  proj_out, eval              P1PE                                 S1PE
  encoder,  train             P1ET                                 S1ET
  proj_out, train             wave 1 (no run_tag, probe v2)        S1 (probe v3)
Rule (E17 = E7's decomposition): tap effect = encoder - proj_out averaged over mode; mode effect =
eval - train averaged over tap; a factor "explains" if |its effect| > 3 ROC while the other's is
<= 3. Applied to lp (E7's outcome) and to the SA gain last - lp; last / last_randinit descriptive.
Per cell, SA gain verdict: paper split D24-B (mean > 3, >= 4/5 seeds); rotations D18 at 1 seed
(descriptive). Bootstrap CIs (bootstrap_d24.cluster_ci over seeds / rotations) are descriptive.
ROC-AUC x100 at the val-selected epoch (test_at_best), as in D24. Own loader: read_d24.load refuses
train-mode records. Writes artifacts/analysis/E17/e17.{md,json}.
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
from read_step1 import paired  # noqa: E402

SEEDS = (42, 123, 2021, 3407, 8888)
ROTS = tuple(f"rot{i}" for i in range(5))
CELLS = (("encoder", "eval"), ("proj_out", "eval"), ("encoder", "train"), ("proj_out", "train"))
TAGS = {"paper": {"P1E": CELLS[0], "P1PE": CELLS[1], "P1ET": CELLS[2], None: CELLS[3]},
        "rot": {"S1E": CELLS[0], "S1PE": CELLS[1], "S1ET": CELLS[2], "S1": CELLS[3]}}
ARMS = {"paper": ("lp", "last", "last_randinit"), "rot": ("lp", "last")}
UNITS = {"paper": [("paper", s) for s in SEEDS], "rot": list(zip(ROTS, SEEDS, strict=True))}   # (split, seed)


def cell_of(r: dict, probe: dict) -> tuple[str, str] | None:
    """(tap, mode) the record claims, checked against its probe spec; None if not an E17 record."""
    kind = "paper" if r["split"] == "paper" else "rot"
    tag = r.get("run_tag") or None
    if tag not in TAGS[kind] or r["arm"] not in ARMS[kind]:
        return None
    v = r["versions"]["probe"]
    if v in (2, 3):   # pre-D23 records: proj_out tap, train mode, no spec fields
        if tag is not None and tag != "S1" or "backbone_mode" in probe["spec"]:
            return None
        return ("proj_out", "train")
    if v != 4 or tag is None:
        return None
    got = (probe["spec"].get("tap") or "encoder", probe["spec"].get("backbone_mode"))
    if got != TAGS[kind][tag]:
        raise SystemExit(f"{r['key']}: tag {tag} claims {TAGS[kind][tag]} but spec says {got}")
    return got


def load(local: Path):
    roc: dict = defaultdict(dict)        # (kind, head, cell, arm, split) -> {seed: roc}
    meta: dict = defaultdict(set)        # check sets
    for p in local.rglob("results/*.json"):
        if p.name.startswith(("diag-", "test-index-", "val-index-", "report-")):
            continue
        r = json.loads(p.read_text())
        if not isinstance(r, dict) or r.get("model") != "cbramod" or r.get("dataset") != "chbmit" \
                or r.get("smoke") or r["split"] not in ("paper", *ROTS):
            continue
        kind = "paper" if r["split"] == "paper" else "rot"
        for head, res in r["probes"].items():
            if kind == "rot" and head != "linear":
                continue
            c = cell_of(r, res)
            if c is None:
                continue
            k = (kind, head, c, r["arm"], r["split"])
            if r["seed"] in roc[k]:
                raise SystemExit(f"two records for {k} seed {r['seed']}")
            roc[k][r["seed"]] = 100 * res["test_at_best"]["roc_auc"]
            meta[("eval_hash", r["split"])].add(r["eval_hash"])
            meta[("labels", kind, c)].add(r.get("labels"))
            meta[("versions", kind, c)].add(json.dumps(r["versions"], sort_keys=True))
            meta[("ssl", r["split"], r["arm"], r["seed"])].add(
                (c, r["adapt_spec"].get("data_hash"), r["adapt_spec"]["ckpt_sha256"][:12]))
            if "adapt" in r:   # same SSL windows + seed => identical adaptation losses in every cell
                meta[("adapt", r["split"], r["arm"], r["seed"])].add(
                    tuple(round(x, 9) for x in r["adapt"]["epoch_losses"]))
            meta[("spec", kind, head, c)].add(json.dumps(   # input_norm "" is the absent default
                {k2: v for k2, v in res["spec"].items() if k2 not in ("seed", "split", "backbone_mode", "tap")
                 and not (k2 == "input_norm" and v == "")}, sort_keys=True))
    return roc, meta


def decompose(y: dict) -> dict:
    """y[(tap, mode)] -> tap / mode effects (E7 convention: encoder - proj_out, eval - train)."""
    tap = np.mean([y[("encoder", m)] - y[("proj_out", m)] for m in ("eval", "train")])
    mode = np.mean([y[(t, "eval")] - y[(t, "train")] for t in ("encoder", "proj_out")])
    inter = (y[CELLS[0]] - y[CELLS[1]]) - (y[CELLS[2]] - y[CELLS[3]])
    verdict = ("tap explains" if abs(tap) > 3 >= abs(mode) else "mode explains" if abs(mode) > 3 >= abs(tap)
               else "both > 3 (neither alone)" if abs(tap) > 3 else "neither > 3")
    return {"tap": float(tap), "mode": float(mode), "interaction": float(inter), "verdict": verdict}


assert decompose({CELLS[0]: 90, CELLS[1]: 80, CELLS[2]: 89, CELLS[3]: 79})["verdict"] == "tap explains"
assert decompose({CELLS[0]: 90, CELLS[1]: 89, CELLS[2]: 80, CELLS[3]: 79})["verdict"] == "mode explains"


def main() -> int:
    roc, meta = load(ROOT / "artifacts" / "s3-results")
    rng = np.random.default_rng(20261101)
    md = ["# D25-E17: CBraMod probe tap x backbone mode (ROC-AUC x100, test_at_best)", ""]
    out: dict = {"checks": {}, "paper": {}, "rot": {}}
    # ---- completeness and comparability
    gaps = []
    for kind, units in UNITS.items():
        for head in (("linear", "mlp_fullft") if kind == "paper" else ("linear",)):
            for c in CELLS:
                for arm in ARMS[kind]:
                    have = [(sp, s) for sp, s in units if s in roc.get((kind, head, c, arm, sp), {})]
                    n_all = sum(len(roc.get((kind, head, c, arm, sp), {})) for sp in {u[0] for u in units})
                    out["checks"][f"{kind}/{head}/{c[0]},{c[1]}/{arm}"] = f"{len(have)}/{len(units)}"
                    if len(have) != len(units) or n_all != len(have):
                        gaps.append(f"{kind}/{head}/{c}/{arm}: {len(have)}/{len(units)} units, {n_all} records")
    md.append("## Checks")
    md.append(f"- record counts: {'all cells complete' if not gaps else 'GAPS: ' + '; '.join(gaps)}")
    for k, v in sorted(meta.items(), key=str):
        if k[0] == "eval_hash" and len(v) != 1:
            gaps.append(f"eval_hash differs within {k[1]}: {v}")
    for name, what in (("eval_hash", "eval_hash per split"), ("labels", "labels per cell"),
                       ("versions", "code versions per cell")):
        md.append(f"- {what}: " + "; ".join(f"{' '.join(map(str, k[1:]))} {sorted(map(str, v))}"
                                            for k, v in sorted(meta.items(), key=str) if k[0] == name))
    specs = {k: v for k, v in meta.items() if k[0] == "spec"}
    for kind in ("paper", "rot"):
        for head in ("linear", "mlp_fullft"):
            s = set().union(*[v for k, v in specs.items() if k[1] == kind and k[2] == head] or [set()])
            if s:
                md.append(f"- probe spec (excl. seed/split/mode/tap) identical across cells, {kind}/{head}: "
                          f"{len(s) == 1}")
    ssl_diff = sorted({(k[1], k[2], tuple(sorted({(x[1], x[2]) for x in v})))
                       for k, v in meta.items() if k[0] == "ssl" and len({(x[1], x[2]) for x in v}) > 1})
    md.append(f"- SSL data_hash/ckpt that differ across cells for the same (split, arm, seed): "
              f"{[f'{a}/{b}: {h}' for a, b, h in ssl_diff] or 'none'}")
    adapt = {k: v for k, v in meta.items() if k[0] == "adapt"}
    bad = sorted(k[1:] for k, v in adapt.items() if len(v) > 1)
    gaps += [f"adaptation losses differ across cells: {k}" for k in bad]
    md.append(f"- adapted (split, arm, seed) units: {len(adapt)}; with identical SSL epoch losses in every "
              f"cell: {len(adapt) - len(bad)} (data_hash differs, losses identical: hash formula, not windows)")
    out["checks"]["gaps"] = gaps
    out["checks"]["ssl_diff"] = [list(map(str, x)) for x in ssl_diff]

    # ---- paper split
    for head in ("linear", "mlp_fullft"):
        md += ["", f"## Paper split, {head} head (5 seeds; cell values mean ± SEM)", "",
               "| tap, mode | lp | last | last_randinit | SA gain last - lp (per seed) | D24-B rule |",
               "|---|---|---|---|---|---|"]
        ps: dict = {}   # (cell, outcome) -> per-seed list
        res: dict = {"cells": {}}
        for c in CELLS:
            v = {arm: [roc[("paper", head, c, arm, "paper")][s] for s in SEEDS] for arm in ARMS["paper"]}
            v["gain"] = [a - b for a, b in zip(v["last"], v["lp"], strict=True)]
            for o, x in v.items():
                ps[(c, o)] = x
            rule = paired(v["gain"])
            res["cells"][f"{c[0]},{c[1]}"] = {o: x for o, x in v.items()} | {"gain_rule": rule}
            f = lambda x: f"{np.mean(x):.2f} ± {np.std(x, ddof=1) / np.sqrt(len(x)):.2f}"  # noqa: E731
            md.append(f"| {c[0]}, {c[1]} | {f(v['lp'])} | {f(v['last'])} | {f(v['last_randinit'])} | "
                      f"{f(v['gain'])} ({', '.join(f'{g:+.1f}' for g in v['gain'])}) | {rule} |")
        md += ["", "| outcome | tap effect (enc - proj) [95% CI] | mode effect (eval - train) [95% CI] | "
               "interaction | rule |", "|---|---|---|---|---|"]
        for o in ("lp", "gain", "last", "last_randinit"):
            d = decompose({c: float(np.mean(ps[(c, o)])) for c in CELLS})
            per = {e: [decompose({c: ps[(c, o)][i] for c in CELLS})[e] for i in range(5)] for e in ("tap", "mode")}
            ci = {e: cluster_ci([per[e]], rng) for e in per}
            d |= {"per_seed": per, "ci": ci}
            res[o] = d
            tag = "" if o in ("lp", "gain") else " (descriptive)"
            md.append(f"| {'SA gain' if o == 'gain' else o} | {d['tap']:+.2f} "
                      f"[{ci['tap'][1]:+.1f}, {ci['tap'][2]:+.1f}] | {d['mode']:+.2f} "
                      f"[{ci['mode'][1]:+.1f}, {ci['mode'][2]:+.1f}] | {d['interaction']:+.2f} | "
                      f"**{d['verdict']}**{tag} |")
        out["paper"][head] = res

    # ---- rotations (seed S_r, linear head)
    md += ["", "## Rotations rot0-4, seed S_r, linear head (1 seed per rotation: descriptive)", "",
           "| tap, mode | lp per rotation (mean) | last - lp per rotation (mean) | D18 rule |",
           "|---|---|---|---|"]
    pr: dict = {}
    res = {"cells": {}}
    for c in CELLS:
        v = {arm: [roc[("rot", "linear", c, arm, r)][s] for r, s in UNITS["rot"]] for arm in ARMS["rot"]}
        v["gain"] = [a - b for a, b in zip(v["last"], v["lp"], strict=True)]
        for o, x in v.items():
            pr[(c, o)] = x
        rule = paired(v["gain"])
        res["cells"][f"{c[0]},{c[1]}"] = v | {"gain_rule": rule}
        md.append(f"| {c[0]}, {c[1]} | {', '.join(f'{x:.1f}' for x in v['lp'])} ({np.mean(v['lp']):.2f}) | "
                  f"{', '.join(f'{x:+.1f}' for x in v['gain'])} ({np.mean(v['gain']):+.2f}) | {rule} |")
    md += ["", "| outcome | tap effect per rotation (mean) [95% CI] | mode effect per rotation (mean) [95% CI] | "
           "interaction | rule (descriptive) | D18 rule on effect |", "|---|---|---|---|---|---|"]
    for o in ("lp", "gain", "last"):
        d = decompose({c: float(np.mean(pr[(c, o)])) for c in CELLS})
        per = {e: [decompose({c: pr[(c, o)][i] for c in CELLS})[e] for i in range(5)] for e in ("tap", "mode")}
        ci = {e: cluster_ci([[x] for x in per[e]], rng) for e in per}
        d |= {"per_rotation": per, "ci": ci, "d18_on_effect": {e: paired(per[e]) for e in per}}
        res[o] = d
        md.append(f"| {'SA gain' if o == 'gain' else o} | {', '.join(f'{x:+.1f}' for x in per['tap'])} "
                  f"({d['tap']:+.2f}) [{ci['tap'][1]:+.1f}, {ci['tap'][2]:+.1f}] | "
                  f"{', '.join(f'{x:+.1f}' for x in per['mode'])} "
                  f"({d['mode']:+.2f}) [{ci['mode'][1]:+.1f}, {ci['mode'][2]:+.1f}] | {d['interaction']:+.2f} | "
                  f"**{d['verdict']}** | tap: {d['d18_on_effect']['tap']}; mode: {d['d18_on_effect']['mode']} |")
    out["rot"]["linear"] = res
    dest = ROOT / "artifacts" / "analysis" / "E17"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "e17.md").write_text("\n".join(md) + "\n")
    (dest / "e17.json").write_text(json.dumps(out, indent=1, default=float))
    print("\n".join(md))
    return 1 if gaps else 0


if __name__ == "__main__":
    raise SystemExit(main())
