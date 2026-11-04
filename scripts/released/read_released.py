#!/usr/bin/env python3
"""D25 wave C: read the released-code runs (scripts/released/sm_released_entry.py outputs) into our
table format and apply the D25-E4/E5/E6/E7 rules (notes/completeness-audit.md, adopted by D25).

    .venv/bin/python scripts/released/read_released.py --root <dir of <cell>/s<seed>/ trees> \
        [--out artifacts/analysis/waveC] [--allow-smoke]

Reads only numbers (the released CSV rows) and counted log facts; no upstream text is copied.
Metrics x100 in D13 order bal / PR / ROC; "best" = the released best_* (val-selected test),
"last" = last_*; each rule is applied at best and at last separately, never mixed.
Reading choices (fixed 2026-11-01, before any released GPU result exists):
- D13 units = paper SEM with a 1-point floor (scripts/analysis/coverage.py d13, T1, T2).
- E4 "released = ours": ROC only; pooled SEM = sqrt(SEM_released^2 + SEM_ours^2); ours = wave 1
  (artifacts/tables/chbmit-paper.json) with the probe matching full_ft (True -> mlp_fullft).
- E5 noise floor = |e5noise-c - e4-c-sa| at seed 42, per metric and epoch rule (points); it widens
  every E5/E6/E7 unit threshold by delta / max(SEM, 1). Screen = seeds 42 and 123 only; a
  configuration screens in at either epoch rule; "reaches" needs >= 5 seeds.
- E6 fingerprint and E7 tap/mode effects use ROC; E7 effects use seeds 42 and 123 only.
- E31: SA(0) = E4 sa (fd0) / E5-SA fd1-ft1-b256-sR (fd1) / E6 all (layer), seeds 42 and 123.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "analysis"))
from coverage import T1, T2, d13  # noqa: E402

MET = ("acc", "pr_auc", "roc_auc")          # released names, D13 order bal / PR / ROC
WHEN = ("best", "last")
WAVE1 = {"best": "test_at_best", "last": "test_last"}
OURS_MET = ("bal_acc", "pr_auc_trapz", "roc_auc")
SCREEN = (42, 123)


def parse_seed(sd: Path) -> dict | None:
    st = json.loads((sd / "status.json").read_text())
    rec = {"rc": st["rc"], "seconds": st["seconds"], "smoke": st["smoke"]}
    rows = [r for p in sorted(sd.rglob("*.csv")) for r in csv.DictReader(p.open()) if "best_roc_auc" in r]
    if st["rc"] != 0 or len(rows) != 1:
        return {**rec, "ok": False}
    for w in WHEN:
        rec[w] = [100 * float(rows[0][f"{w}_{m}"]) for m in MET]
    text = (sd / "run.log").read_text(errors="replace") if (sd / "run.log").exists() else ""
    head = re.search(r"classifier structure: (.*?)(?:\n\S|\Z)", text, re.S)
    trainable = re.findall(r"Trainable parameters: ([\d,]+)", text)
    kept, cur = None, None
    for line in text.splitlines():   # SPT epoch whose weights were kept (last "Saved best" epoch)
        m = re.search(r"SPT Epoch (\d+)/\d+: Avg Loss", line) or re.search(r"\[SPT\] step (\d+)/", line)
        cur = int(m.group(1)) if m else cur
        kept = cur if "Saved best SPT model" in line else kept
    vals = [float(v) for v in re.findall(r"Epoch \d+ Loss: \S+ Val \w+: (\S+)", text)]
    return {**rec, "ok": True, "head_mlp": bool(head and "ELU" in head.group(1)),
            "probe_trainable": int(trainable[-1].replace(",", "")) if trainable else None,
            "nonfinite": text.count("non-finite SPT loss"),
            "foundation_loaded": bool(re.search(r"Loaded \w+ foundation weights", text)), "spt_kept": kept,
            "best_epoch": int(np.argmax(vals)) + 1 if vals else None}


def load(root: Path, allow_smoke: bool) -> dict:
    runs = {}
    for cj in sorted(root.glob("*/cell.json")):
        cell = json.loads(cj.read_text())
        if cell.get("smoke") and not allow_smoke:
            continue
        seeds = {}
        for sd in sorted(cj.parent.glob("s*/status.json")):
            r = parse_seed(sd.parent)
            if r and r["ok"]:
                seeds[int(sd.parent.name[1:])] = r
        runs[cell["id"]] = {"cell": cell, "seeds": seeds,
                            "failed": [sd.parent.name for sd in cj.parent.glob("s*/status.json")
                                       if not (sd.parent / "DONE").exists()]}
    return runs


def agg(run, w, seeds=None):
    """Mean and SEM over seeds of [bal, PR, ROC]; None when no seed is available."""
    if not run:
        return None
    v = [r[w] for s, r in run["seeds"].items() if seeds is None or s in seeds]
    if not v:
        return None
    a = np.asarray(v)
    sem = a.std(0, ddof=1) / np.sqrt(len(a)) if len(a) > 1 else np.full(3, np.nan)
    return a.mean(0), sem, len(a)


def fmt(t, i=None) -> str:
    if t is None:
        return "-"
    m, s, n = t
    idx = range(3) if i is None else [i]
    return " / ".join(f"{m[k]:.2f}" + (f" ± {s[k]:.2f}" if np.isfinite(s[k]) else "") for k in idx) + f" (n={n})"


def units(t, paper, delta, thr):
    """D13 gaps (paper SEM, floor 1); k = metrics within thr + delta/max(SEM, 1)."""
    gaps, _dist, _st, _fail = d13(list(t[0]), paper)
    k = sum(abs(g) <= thr + d / max(s, 1.0) for g, d, (_v, s) in zip(gaps, delta, paper, strict=True))
    return gaps, k


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", default=str(ROOT / "artifacts" / "analysis" / "waveC"))
    ap.add_argument("--allow-smoke", action="store_true", help="read smoke cells (harness check only)")
    args = ap.parse_args()
    runs = load(Path(args.root).expanduser(), args.allow_smoke)
    get = runs.get
    md, verdicts, warn = [], {}, []
    wave1 = {(r["model"], r["arm"], r["probe"]): r
             for r in json.loads((ROOT / "artifacts" / "tables" / "chbmit-paper.json").read_text())}
    M = {"b": "biot", "c": "cbramod"}

    md += ["# D25 wave C: released code (d056cdf), CHB-MIT paper split", "",
           "Values x100, mean ± SEM over seeds (n). bal / PR / ROC. Smoke cells included: "
           f"{args.allow_smoke}.", "", "## All cells", "",
           "| cell | seeds ok | failed | best bal/PR/ROC | last bal/PR/ROC | head MLP | probe trainable "
           "| non-finite SPT | SPT kept | foundation loaded |", "|---|---|---|---|---|---|---|---|---|---|"]
    for cid, r in runs.items():
        s = list(r["seeds"].values())
        md.append(f"| {cid} | {len(s)} | {','.join(r['failed']) or '-'} | {fmt(agg(r, 'best'))} | "
                  f"{fmt(agg(r, 'last'))} | {sorted({x['head_mlp'] for x in s})} | "
                  f"{sorted({x['probe_trainable'] for x in s}, key=str)} | {sum(x['nonfinite'] for x in s)} | "
                  f"{sorted({x['spt_kept'] for x in s}, key=str)} | "
                  f"{sorted({x['foundation_loaded'] for x in s})} |")
        fd = r["cell"]["levels"].get("fd") == "fd1" or any("foundation_dir" in o for o in r["cell"]["overrides"])
        if s and {x["foundation_loaded"] for x in s} != {fd}:
            warn.append(f"- WARNING {cid}: foundation_dir {'set' if fd else 'unset'} but the log says otherwise")
        if r["failed"]:
            warn.append(f"- WARNING {cid}: seeds {','.join(r['failed'])} not DONE; excluded from every number")

    md += [""] + warn
    # noise floor (E5): per epoch rule, per metric, points
    a, b = get("e5noise-c"), get("e4-c-sa")
    delta = {w: [0.0] * 3 for w in WHEN}
    noise_ok = bool(a and b and 42 in a["seeds"] and 42 in b["seeds"])
    if noise_ok:
        delta = {w: list(np.abs(np.subtract(a["seeds"][42][w], b["seeds"][42][w]))) for w in WHEN}
    md += ["", "Noise floor (E5, same-seed repeat, points bal/PR/ROC): "
           + (str(delta) if noise_ok else "NOT MEASURED (0 used)")]

    # ---- D25-E4
    md += ["", "## D25-E4", "", "| model | cell | rule | released | D13 gaps vs paper | wave-1 ours ROC | "
           "|released-ours| ROC | threshold | released = ours |", "|---|---|---|---|---|---|---|---|---|"]
    for mk, model in M.items():
        for arm, pcell, ours in (("lp", "LP", "lp"), ("sa", "SA", "last_randinit"), ("lprand", "LP", None)):
            for w in WHEN:
                t = agg(get(f"e4-{mk}-{arm}"), w)
                if t is None:
                    continue
                gaps, _d, st, _f = d13(list(t[0]), T1[(model, pcell)])
                row = f"| {model} | {arm} | {w} | {fmt(t)} | {' / '.join(f'{g:+.1f}' for g in gaps)} ({st}) |"
                o = wave1.get((model, ours, "mlp_fullft")) if ours else None
                if o:
                    om, osem = o[f"{WAVE1[w]}.roc_auc"]
                    diff = abs(t[0][2] - om)
                    thr = max(2.0, 2 * float(np.hypot(t[1][2] if np.isfinite(t[1][2]) else 0.0, osem)))
                    ok = bool(diff <= thr)
                    verdicts[f"E4 {model} {arm} {w}: released = ours"] = ok
                    row += f" {om:.2f} ± {osem:.2f} | {diff:.2f} | {thr:.2f} | {ok} |"
                else:
                    row += " - | - | - | - |"
                md.append(row)
            if arm == "lprand":
                for w in WHEN:
                    sa, rnd = agg(get(f"e4-{mk}-sa"), w), agg(get(f"e4-{mk}-lprand"), w)
                    if sa and rnd:
                        d = abs(sa[0][2] - rnd[0][2])
                        verdicts[f"E4 {model} {w}: random features explain released SA (|SA-LPrand| ROC "
                                 f"{d:.2f} <= 3)"] = d <= 3

    # ---- D25-E5 (screen at seeds 42/123; reaches with >= 5 seeds)
    configs = [(cid, r) for cid, r in runs.items() if r["cell"]["item"] in ("E5-LP", "E5-SA")]
    configs += [(cid, r) for cid in ("e4-b-lp", "e4-b-sa", "e4-c-lp", "e4-c-sa") if (r := get(cid))]
    md += ["", "## D25-E5", "", "| config | target | rule | screen mean (42,123) | units "
           "| screen pass (<=5 on >=2) | seeds | reaches (<=3 on 3, n>=5) | W&B mode tag vs head |",
           "|---|---|---|---|---|---|---|---|---|"]
    reach: dict = {}
    for cid, r in configs:
        model = M[r["cell"]["levels"]["model"]]
        target = "LP" if "fm_freeze" in " ".join(r["cell"]["overrides"]) else "SA"
        mode = "lp" if "training.full_ft=False" in r["cell"]["overrides"] else "full_ft"
        heads = {x["head_mlp"] for x in r["seeds"].values()}
        tag_ok = heads == {mode == "full_ft"} if heads else None
        # a configuration screens in at either epoch rule; one that fails both gets no follow-up
        # seeds, so it can never reach: False, not pending (re-check of 2026-11-01)
        screened_in = any(units(t, T1[(model, target)], delta[w], 5.0)[1] >= 2
                          for w in WHEN if (t := agg(r, w, SCREEN)) is not None)
        for w in WHEN:
            t = agg(r, w, SCREEN)
            if t is None:
                continue
            gaps, k = units(t, T1[(model, target)], delta[w], 5.0)
            full = agg(r, w)
            rc, g5 = None, None
            if full and full[2] >= 5:
                g5, k5 = units(full, T1[(model, target)], delta[w], 3.0)
                rc = bool(k5 == 3)   # python bool: the "is False" test below must see it (numpy bool is not False)
            elif not screened_in:
                rc = False
            reach.setdefault((model, target, w), []).append((rc, cid, g5))
            md.append(f"| {cid} | {model} {target} | {w} | {fmt(t)} | {' / '.join(f'{g:+.1f}' for g in gaps)} | "
                      f"{k >= 2} | {full[2] if full else 0} | {rc if rc is not None else 'pending'}"
                      f"{' (' + ' / '.join(f'{g:+.1f}' for g in g5) + ')' if g5 else ''} | {mode}: {tag_ok} |")
    md += ["", "E5 closest configuration per target (descriptive): smallest worst-metric excess of |5-seed gap| "
           "over its widened threshold 3 + noise/max(SEM, 1); negative = inside on every metric.", ""]
    for (model, target, w), rs in reach.items():
        flags = [x[0] for x in rs]
        txt = ("reaches" if any(flags) else "no released configuration reaches" if all(x is False for x in flags)
               else "pending (configurations without 5 seeds)")
        verdicts[f"E5 {model} {target} at {w}"] = txt
        thr = [3.0 + d / max(s, 1.0) for d, (_v, s) in zip(delta[w], T1[(model, target)], strict=True)]
        five = [(max(abs(g) - h for g, h in zip(g5, thr, strict=True)), cid, g5) for _rc, cid, g5 in rs if g5]
        if five:
            ex, cid, g5 = min(five)
            md.append(f"- {model} {target} {w}: {cid}, 5-seed gaps {' / '.join(f'{g:+.2f}' for g in g5)} units vs "
                      f"thresholds {' / '.join(f'{h:.2f}' for h in thr)}; worst excess {ex:+.2f}")

    # ---- D25-E6
    md += ["", "## D25-E6", ""]
    lay = {L: get(f"e6-b-{L}") for L in ("last1", "last2", "all")}
    e4 = get("e4-b-sa")
    if lay["last1"] and e4:
        common = sorted(set(lay["last1"]["seeds"]) & set(e4["seeds"]))
        agree = [all(abs(lay["last1"]["seeds"][s][w][i] - e4["seeds"][s][w][i]) <= delta[w][i] + 1e-9
                     for w in WHEN for i in range(3)) for s in common]
        verdicts[f"E6 entry points agree (main_layer last1 vs main.py step_up, seeds {common})"] = \
            bool(common) and all(agree)
        md.append(f"Per-seed agreement within the noise floor: {dict(zip(common, agree, strict=True))}")
    for w in WHEN:
        rows = []
        for L, key in (("last1", "L"), ("last2", "L,L-1"), ("all", "All")):
            t = agg(lay[L], w)
            if t is not None:
                rows.append(abs(t[0][2] - T2[("biot", key)][3]) <= 2)
                md.append(f"- {w} {L}: {fmt(t)}; paper ROC {T2[('biot', key)][3]}; "
                          f"set: {fmt(agg(get(f'e6fd-b-{L}'), w))}")
        verdicts[f"E6 fingerprint reproduced in released code at {w} (all 3 rows within 2 ROC)"] = \
            all(rows) if len(rows) == 3 else f"PENDING ({len(rows)} of 3 rows have finished seeds)"

    # ---- D25-E7 (CBraMod tap x mode x full_ft; BIOT mode x full_ft)
    def e7(mk, tap, mode, ft):
        if (tap, mode) == ("tproj", "mtrain"):
            return get(f"e4-{mk}-lp") if ft == "ft1" else get(f"e5lp-{mk}-ft0-b256")
        return get(f"e7{M[mk]}-{mk}-{tap}-{mode}-{ft}" if mk == "c" else f"e7biot-{mk}-{mode}-{ft}")

    md += ["", "## D25-E7", "", "| model | tap | mode | full_ft | rule | bal / PR / ROC | D13 vs CBraMod LP |",
           "|---|---|---|---|---|---|---|"]
    reachable: dict = {}
    for w in WHEN:
        for ft in ("ft1", "ft0"):
            roc = {}
            for tap in ("tproj", "tenc"):
                for mode in ("mtrain", "meval"):
                    r = e7("c", tap, mode, ft)
                    t = agg(r, w)
                    if t is None:
                        continue
                    gaps, k = units(t, T1[("cbramod", "LP")], delta[w], 3.0)
                    reachable.setdefault(w, []).append(k == 3)
                    md.append(f"| cbramod | {tap} | {mode} | {ft} | {w} | {fmt(t)} | "
                              f"{' / '.join(f'{g:+.1f}' for g in gaps)} |")
                    s2 = agg(r, w, SCREEN)
                    if s2:
                        roc[(tap, mode)] = s2[0][2]
            if len(roc) == 4:
                tap_eff = np.mean([roc[("tenc", m)] - roc[("tproj", m)] for m in ("mtrain", "meval")])
                mode_eff = np.mean([roc[(t, "meval")] - roc[(t, "mtrain")] for t in ("tproj", "tenc")])
                verdicts[f"E7 cbramod {ft} {w}: tap effect {tap_eff:+.2f}, mode effect {mode_eff:+.2f} ROC -> "
                         f"tap explains"] = bool(abs(tap_eff) > 3 >= abs(mode_eff))
                verdicts[f"E7 cbramod {ft} {w}: mode explains"] = bool(abs(mode_eff) > 3 >= abs(tap_eff))
            tr, ev = agg(e7("b", "tproj", "mtrain", ft), w, SCREEN), agg(e7("b", "tproj", "meval", ft), w, SCREEN)
            if tr and ev:
                md.append(f"| biot | - | eval - train | {ft} | {w} | ROC {ev[0][2] - tr[0][2]:+.2f} | - |")
    for w, rs in reachable.items():
        verdicts[f"E7 54.14 reachable in released code at {w} (any CBraMod LP config D13-consistent)"] = any(rs)

    # ---- E31 (lambda) and E30c (descriptive)
    md += ["", "## E31 (lambda matters if |SA(lambda) - SA(0)| > 3 ROC, 2-seed mean)", ""]
    for cid, r in runs.items():
        lv = r["cell"]["levels"]
        if r["cell"]["item"] not in ("E31", "E31-layer"):
            continue
        base = (get("e6-b-all") if r["cell"]["item"] == "E31-layer" else
                get(f"e4-{lv['model']}-sa") if lv["fd"] == "fd0" else get(f"e5sa-{lv['model']}-fd1-ft1-b256-sR"))
        for w in WHEN:
            t, z = agg(r, w, SCREEN), agg(base, w, SCREEN)
            if t and z:
                d = t[0][2] - z[0][2]
                verdicts[f"E31 {cid} {w}: lambda matters (dROC {d:+.2f})"] = bool(abs(d) > 3)
                md.append(f"- {cid} {w}: {fmt(t, 2)} vs lambda 0 {fmt(z, 2)}")
            else:
                verdicts[f"E31 {cid} {w}: lambda matters"] = "PENDING (cell or lambda-0 base: no finished seed)"
    md += ["", "## E30c (descriptive here; D15 rules on seed means are read separately)", ""]
    for cid, r in runs.items():
        if r["cell"]["item"].startswith("E30c"):
            md.append(f"- {cid}: best (bal-acc selected) {fmt(agg(r, 'best'))}; last {fmt(agg(r, 'last'))}")

    md += ["", "## Verdicts (pre-registered rules; n seeds as shown above)", ""]
    md += [f"- {k}: **{v}**" for k, v in verdicts.items()]
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "released.md").write_text("\n".join(md) + "\n")
    (out / "released.json").write_text(json.dumps({"verdicts": verdicts, "noise_floor": delta, "runs": {
        cid: {"cell": r["cell"], "seeds": r["seeds"], "failed": r["failed"]} for cid, r in runs.items()}},
        indent=1, default=float))
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
