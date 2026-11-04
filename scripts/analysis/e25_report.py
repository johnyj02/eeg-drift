#!/usr/bin/env python3
"""D25-E25: the logged re-runs (S1L, S3L, S3FL rotations; P1L paper split), both heads.

    .venv/bin/python scripts/analysis/e25_report.py

Registered (notes/completeness-audit.md E25 + D24): the mlp_fullft head is read with the UNCHANGED D24
rules: D24-A (per-rotation mean over 3 seeds, D18 paired rule on last - lp, last_randinit - last,
lp - lp_randinit; D17) and D24-B (P1L: last - lp paired by seed, gain if mean > 3 and >= 4/5 seeds).
Test ROC at the validation-ROC-selected epoch (test_at_best), as in D24.
Descriptive / post hoc (labelled so in the output): the same rules on test ROC at the epoch chosen by
validation balanced accuracy (threshold logit 0, first max = strict ">" as the released
trainer_diversityN.py) and at the last epoch; cluster-bootstrap CIs (bootstrap_d24.cluster_ci);
per-epoch history summaries. Writes artifacts/analysis/E25/{E25.md, e25_runs.csv}.
"""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from bootstrap_d24 import cluster_ci  # noqa: E402
from read_d24 import ARMS, CONTRASTS, ROTS, ms  # noqa: E402
from read_step1 import d17, paired  # noqa: E402

# E25 tag -> (dataset, originals); rotation seeds [S_r, 1000 + r, 2000 + r] (D24-A)
SETS = {"S1L": ("chbmit", ("S1E", "S1M")), "S3L": ("siena", ("S3E", "S3M")),
        "S3FL": ("siena", ("S3FE", "S3FM")), "P1L": ("chbmit", ("P1E",))}
S_R = (42, 123, 2021, 3407, 8888)
PAPER_ARMS = ("lp", "last", "last_randinit", "lp_randinit")
HEADS = ("linear", "mlp_fullft")
SELS = ("roc", "bal", "last")          # roc = registered (test_at_best); bal, last = descriptive
NAMES = {("last", "lp"): ("SA helps", "SA hurts"),
         ("last_randinit", "last"): ("RANDOM init wins", "PRETRAINED wins"),
         ("lp", "lp_randinit"): ("pretrained features win", "RANDOM features win")}


def verdict(d, a, b) -> str:
    v = paired(d)
    return {"first term wins": NAMES[(a, b)][0], "second term wins": NAMES[(a, b)][1]}.get(v, "none")


def first_max(x) -> int:
    return int(np.argmax(np.asarray(x)))   # argmax returns the first max = strict ">" selection


def load(tags: set[str]) -> list[dict]:
    out = []
    for p in (ROOT / "artifacts" / "s3-results").rglob("results/*.json"):
        if not p.name.startswith(("biot-", "cbramod-")):     # skips diag/test-index/val-index/report
            continue
        r = json.loads(p.read_text())
        if isinstance(r, dict) and not r.get("smoke") and r.get("run_tag") in tags:
            r["_path"] = str(p.relative_to(ROOT))
            out.append(r)
    return out


def run_rows(recs: list[dict], problems: list[str]) -> list[dict]:
    rows = []
    for r in recs:
        for head in HEADS:
            res = r["probes"][head]
            h = res["history"]
            spec = res["spec"]
            if r["versions"]["probe"] != 4 or spec["backbone_mode"] != "eval" or spec["tap"] != "encoder":
                problems.append(f"{r['_path']} {head}: not v4/eval/encoder")
            if len(h) != spec["epochs"] or [e["val"]["roc_auc"] for e in h] != list(res["val_curve"]):
                problems.append(f"{r['_path']} {head}: history/val_curve mismatch")
            vroc = [e["val"]["roc_auc"] for e in h]
            troc = [e["test_plot_only"]["roc_auc"] for e in h]
            if res["best_epoch"] != first_max(vroc):
                problems.append(f"{r['_path']} {head}: best_epoch {res['best_epoch']} != first argmax val ROC")
            e_bal = first_max([e["val"]["bal_acc"] for e in h])
            vloss = [e["val_loss"] for e in h]
            tl = [e["train_loss"] for e in h]
            rows.append({
                "tag": r["run_tag"], "dataset": r["dataset"], "model": r["model"], "arm": r["arm"],
                "split": r["split"], "seed": r["seed"], "head": head, "eval_hash": r["eval_hash"],
                "n_epochs": len(h), "sel_roc": res["best_epoch"], "sel_bal": e_bal,
                "roc_roc": 100 * res["test_at_best"]["roc_auc"], "roc_bal": 100 * troc[e_bal],
                "roc_last": 100 * res["test_last"]["roc_auc"],
                "hist_best_diff": 100 * abs(troc[res["best_epoch"]] - res["test_at_best"]["roc_auc"]),
                "hist_last_diff": 100 * abs(troc[-1] - res["test_last"]["roc_auc"]),
                "bal_const": len({e["val"]["bal_acc"] for e in h}) == 1,
                "sel_vap": first_max([e["val"]["avg_precision"] for e in h]),
                "sel_vloss": int(np.argmin(vloss)), "sel_test_oracle": first_max(troc),
                "roc_oracle": 100 * max(troc), "train_loss_first": tl[0], "train_loss_last": tl[-1],
                "train_mono": all(b <= a for a, b in zip(tl, tl[1:], strict=False)), "val_loss_first": vloss[0],
                "val_loss_last": vloss[-1], "head_params": res["head_params"]})
    return rows


def inventory(tag: str, recs: list[dict], problems: list[str]) -> list[str]:
    paper = tag == "P1L"
    c = Counter((r["model"], r["arm"], r["split"], r["seed"]) for r in recs)
    dup = [k for k, n in c.items() if n > 1]
    if dup:
        problems.append(f"{tag}: duplicate records {dup[:5]}")
    want = set()
    for m in ("biot", "cbramod"):
        if paper:
            want |= {(m, a, "paper", s) for a in PAPER_ARMS for s in S_R}
        else:
            want |= {(m, a, f"rot{i}", s) for a in ARMS for i in range(5) for s in (S_R[i], 1000 + i, 2000 + i)}
    missing, extra = want - set(c), set(c) - want
    if missing or extra:
        problems.append(f"{tag}: missing {sorted(missing)[:5]} ({len(missing)}), extra {sorted(extra)[:5]}")
    # one eval data / labels / code version per split (both models, all arms); one probe spec per head
    per_split = defaultdict(set)
    spec_sets = defaultdict(set)
    for r in recs:
        per_split[r["split"]].add((r["eval_hash"], r.get("labels"), json.dumps(r["versions"], sort_keys=True),
                                   r.get("adapt_spec", {}).get("code_version") if r.get("adapt_spec") else None))
        for head in HEADS:
            s = {k: v for k, v in r["probes"][head]["spec"].items() if k not in ("seed", "model", "split")}
            spec_sets[(r["model"], head)].add(json.dumps(s, sort_keys=True))
    for split, v in per_split.items():
        hashes = {x[:3] for x in v}
        if len(hashes) > 1:
            problems.append(f"{tag} {split}: mixed eval_hash/labels/versions {hashes}")
    for k, v in spec_sets.items():
        if len(v) > 1:
            problems.append(f"{tag} {k}: {len(v)} different probe specs")
    cells = Counter((r["model"], r["arm"]) for r in recs)
    hashes = sorted({x[0] for v in per_split.values() for x in v})
    return [f"- {tag}: {len(recs)} records (expected {len(want)}); per (model, arm): "
            f"{sorted(set(cells.values()))} records; missing {len(missing)}, duplicates {len(dup)}; "
            f"eval_hash per split one value for both models and all arms "
            f"({'ok' if all(len({x[0] for x in v}) == 1 for v in per_split.values()) else 'MIXED'}; "
            f"{len(hashes)} hashes over {len(per_split)} splits); "
            f"labels {sorted({r.get('labels') for r in recs})}; "
            f"versions {sorted({json.dumps(r['versions'], sort_keys=True) for r in recs})}; adapt code_version "
            f"{sorted({str(r['adapt_spec'].get('code_version')) for r in recs if r.get('adapt_spec')})}"]


def originals_check(tag: str, recs: list[dict], problems: list[str]) -> str:
    dataset, otags = SETS[tag]
    orig = {}
    for r in load(set(otags)):
        if r["dataset"] != dataset:
            continue
        orig[(r["model"], r["arm"], r["split"], r["seed"])] = r
    diffs = defaultdict(list)
    hash_bad = 0
    for r in recs:
        o = orig.get((r["model"], r["arm"], r["split"], r["seed"]))
        if o is None:
            continue
        ident = ("eval_hash", "labels", "versions")
        hash_bad += any(o.get(k) != r.get(k) for k in ident)
        for head in HEADS:
            if head in o["probes"]:
                for key in ("test_at_best", "test_last"):
                    d = o["probes"][head][key]["roc_auc"] - r["probes"][head][key]["roc_auc"]
                    diffs[(head, key)].append(abs(d))
    if hash_bad:
        problems.append(f"{tag}: {hash_bad} records differ from originals in eval_hash/labels/versions")
    parts = [f"{h} {k}: {len(v)} pairs, max |diff| {100 * max(v):.2g} ROC x100, "
             f"{sum(x > 0.005 for x in v)} over 0.5" for (h, k), v in sorted(diffs.items())]
    return (f"- {tag} vs {'+'.join(otags)}: " + "; ".join(parts)
            + f"; eval_hash/labels/versions mismatches {hash_bad}")


def per_rot(rows, model, head, sel):
    """arm -> [rotation mean over its 3 seeds] (D24-A), plus arm -> [[seed values] per rotation]."""
    v = defaultdict(lambda: defaultdict(dict))
    for x in rows:
        if x["model"] == model and x["head"] == head:
            v[x["arm"]][x["split"]][x["seed"]] = x[f"roc_{sel}"]
    means = {a: [float(np.mean(list(v[a][r].values()))) for r in ROTS] for a in ARMS}
    return means, v


def rotation_block(tag, rows, rng, out_rows):
    lines = []
    for model in ("biot", "cbramod"):
        for head in HEADS:
            means, raw = per_rot(rows, model, head, "roc")
            for a in ARMS:
                allruns = [x for r in ROTS for x in raw[a][r].values()]
                lines.append(f"| {tag} | {model} | {head} | {a} | {', '.join(f'{x:.1f}' for x in means[a])} | "
                             f"{ms(means[a])} | {ms(allruns)} |")
    arm_lines = lines
    lines = []
    for model in ("biot", "cbramod"):
        res = {}
        for head in HEADS:
            for sel in SELS:
                means, raw = per_rot(rows, model, head, sel)
                for a, b, _ in CONTRASTS:
                    d = [x - y for x, y in zip(means[a], means[b], strict=True)]
                    res[(head, sel, a, b)] = (d, verdict(d, a, b))
                    if sel == "roc" and head == "mlp_fullft":
                        diffs = [[raw[a][r][s] - raw[b][r][s] for s in sorted(raw[a][r])] for r in ROTS]
                        res[(head, "ci", a, b)] = cluster_ci(diffs, rng)
                d = [x - y for x, y in zip(means["last_randinit"], means["lp_randinit"], strict=True)]
                res[(head, sel, "d17")] = (d, d17(means["last_randinit"], means["lp_randinit"]))
                res[(head, sel, "allref")] = float(np.mean(means["all"]) - np.mean(means["last"]))
        for a, b, _ in CONTRASTS:
            dl, vl = res[("linear", "roc", a, b)]
            dm, vm = res[("mlp_fullft", "roc", a, b)]
            m, lo, hi = res[("mlp_fullft", "ci", a, b)]
            alt = "; ".join(f"{h[:3]}/{s}: {res[(h, s, a, b)][1]}" for h in HEADS for s in ("bal", "last"))
            lines.append(f"| {tag} | {model} | {a} - {b} | {np.mean(dl):+.1f} {vl} | {np.mean(dm):+.1f} "
                         f"[{lo:+.1f}, {hi:+.1f}] | {', '.join(f'{x:+.1f}' for x in dm)} | **{vm}** | "
                         f"{'same' if vm == vl else 'CHANGED'} | {alt} |")
            out_rows.append({"tag": tag, "model": model, "contrast": f"{a} - {b}",
                             "linear": [np.mean(dl), vl], "mlp": [np.mean(dm), vm], "mlp_per_rot": dm,
                             **{f"{h}_{s}": res[(h, s, a, b)][1] for h in HEADS for s in ("bal", "last")}})
        dl, vl = res[("linear", "roc", "d17")]
        dm, vm = res[("mlp_fullft", "roc", "d17")]
        alt = "; ".join(f"{h[:3]}/{s}: {res[(h, s, 'd17')][1]}" for h in HEADS for s in ("bal", "last"))
        lines.append(f"| {tag} | {model} | D17 last_randinit vs lp_randinit | {np.mean(dl):+.1f} {vl} | "
                     f"{np.mean(dm):+.1f} | {', '.join(f'{x:+.1f}' for x in dm)} | **{vm}** | "
                     f"{'same' if vm == vl else 'CHANGED'} | {alt} |")
        out_rows.append({"tag": tag, "model": model, "contrast": "D17", "linear": [np.mean(dl), vl],
                         "mlp": [np.mean(dm), vm], "mlp_per_rot": dm,
                         **{f"{h}_{s}": res[(h, s, 'd17')][1] for h in HEADS for s in ("bal", "last")}})
        lines.append(f"| {tag} | {model} | all - last (reference, no verdict) | "
                     f"{res[('linear', 'roc', 'allref')]:+.1f} | "
                     f"{res[('mlp_fullft', 'roc', 'allref')]:+.1f} | | | | |")
    return arm_lines, lines


def paper_block(rows, rng, out_rows):
    lines, arm_lines = [], []
    for model in ("biot", "cbramod"):
        for head in HEADS:
            v = {(x["arm"], x["seed"], s): x[f"roc_{s}"] for x in rows
                 if x["model"] == model and x["head"] == head for s in SELS}
            for a in PAPER_ARMS:
                vals = [v[(a, s, "roc")] for s in S_R]
                arm_lines.append(f"| P1L | {model} | {head} | {a} | {', '.join(f'{x:.1f}' for x in vals)} | "
                                 f"{ms(vals)} |")
        res = {}
        for head in HEADS:
            v = {(x["arm"], x["seed"], s): x[f"roc_{s}"] for x in rows
                 if x["model"] == model and x["head"] == head for s in SELS}
            for sel in SELS:
                d = [v[("last", s, sel)] - v[("lp", s, sel)] for s in S_R]
                res[(head, sel)] = (d, {"first term wins": "GAIN",
                                        "second term wins": "loss"}.get(paired(d), "none"))
            res[(head, "ci")] = cluster_ci([[v[("last", s, "roc")] - v[("lp", s, "roc")] for s in S_R]], rng)
            res[(head, "rand")] = [v[("last_randinit", s, "roc")] - v[("lp", s, "roc")] for s in S_R]
        dl, vl = res[("linear", "roc")]
        dm, vm = res[("mlp_fullft", "roc")]
        m, lo, hi = res[("mlp_fullft", "ci")]
        alt = "; ".join(f"{h[:3]}/{s}: {res[(h, s)][1]}" for h in HEADS for s in ("bal", "last"))
        lines.append(f"| P1L | {model} | last - lp (D24-B SA gain) | {np.mean(dl):+.1f} {vl} | {np.mean(dm):+.1f} "
                     f"[{lo:+.1f}, {hi:+.1f}] | {', '.join(f'{x:+.1f}' for x in dm)} | **{vm}** | "
                     f"{'same' if vm == vl else 'CHANGED'} | {alt} |")
        lines.append(f"| P1L | {model} | last_randinit - lp (descriptive) | "
                     f"{np.mean(res[('linear', 'rand')]):+.1f} | "
                     f"{np.mean(res[('mlp_fullft', 'rand')]):+.1f} | "
                     f"{', '.join(f'{x:+.1f}' for x in res[('mlp_fullft', 'rand')])} | | | |")
        out_rows.append({"tag": "P1L", "model": model, "contrast": "last - lp", "linear": [np.mean(dl), vl],
                         "mlp": [np.mean(dm), vm], "mlp_per_seed": dm,
                         **{f"{h}_{s}": res[(h, s)][1] for h in HEADS for s in ("bal", "last")}})
    return arm_lines, lines


def hist_block(rows):
    g = defaultdict(list)
    for x in rows:
        g[(x["tag"], x["model"], x["head"])].append(x)
    sel = ["| tag | model | head | n | ROC-selected epoch (1-based) histogram 1..10 | median | % at last | "
           "mean test ROC last - best | max abs | % last != best | bal-sel epoch == ROC-sel % | "
           "% val bal_acc constant | mean test ROC bal-sel - ROC-sel | oracle max test ROC - ROC-sel |",
           "|" + "---|" * 14]
    cur = ["| tag | model | head | train loss ep1 -> ep10 (median) | % train loss monotone | val loss ep1 -> ep10 "
           "(median) | val-loss argmin epoch median (% at 10) | val-AP argmax epoch median (% == ROC-sel) | "
           "test-ROC (plot only) argmax epoch median |", "|" + "---|" * 9]
    for (tag, model, head), xs in sorted(g.items()):
        n = len(xs)
        e = np.array([x["sel_roc"] for x in xs]) + 1
        hist = " ".join(str(int((e == k).sum())) for k in range(1, 11))
        gap = np.array([x["roc_last"] - x["roc_roc"] for x in xs])
        bal = np.array([x["roc_bal"] - x["roc_roc"] for x in xs])
        sel.append(f"| {tag} | {model} | {head} | {n} | {hist} | {np.median(e):.0f} | "
                   f"{100 * np.mean(e == 10):.0f} | "
                   f"{gap.mean():+.2f} | {np.abs(gap).max():.1f} | {100 * np.mean(gap != 0):.0f} | "
                   f"{100 * np.mean([x['sel_bal'] == x['sel_roc'] for x in xs]):.0f} | "
                   f"{100 * np.mean([x['bal_const'] for x in xs]):.0f} | {bal.mean():+.2f} | "
                   f"{np.mean([x['roc_oracle'] - x['roc_roc'] for x in xs]):+.2f} |")
        vl = np.array([x["sel_vloss"] for x in xs]) + 1
        cur.append(f"| {tag} | {model} | {head} | {np.median([x['train_loss_first'] for x in xs]):.3f} -> "
                   f"{np.median([x['train_loss_last'] for x in xs]):.3f} | "
                   f"{100 * np.mean([x['train_mono'] for x in xs]):.0f} | "
                   f"{np.median([x['val_loss_first'] for x in xs]):.3f} -> "
                   f"{np.median([x['val_loss_last'] for x in xs]):.3f} | "
                   f"{np.median(vl):.0f} ({100 * np.mean(vl == 10):.0f}) | "
                   f"{np.median([x['sel_vap'] for x in xs]) + 1:.0f} "
                   f"({100 * np.mean([x['sel_vap'] == x['sel_roc'] for x in xs]):.0f}) | "
                   f"{np.median([x['sel_test_oracle'] for x in xs]) + 1:.0f} |")
    return sel, cur


def main() -> int:
    out = ROOT / "artifacts" / "analysis" / "E25"
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20261101)
    problems: list[str] = []
    inv, orig, rows = [], [], []
    for tag in SETS:
        recs = load({tag})
        inv += inventory(tag, recs, problems)
        orig.append(originals_check(tag, recs, problems))
        rows += run_rows(recs, problems)
    hist_max = max(max(x["hist_best_diff"], x["hist_last_diff"]) for x in rows)
    verdicts: list[dict] = []
    arm_tab = ["| tag | model | head | arm | per-rotation seed means | over rotations | over runs |",
               "|---|---|---|---|---|---|---|"]
    con_tab = ["| tag | model | contrast | linear (registered D24) | mlp_fullft mean "
               "[cluster-bootstrap 95% CI, descr.] | mlp per rotation (P1L: per seed) | mlp rule output "
               "| vs linear | descriptive: head/selection -> rule |",
               "|" + "---|" * 9]
    for tag in ("S1L", "S3L", "S3FL"):
        a, c = rotation_block(tag, [x for x in rows if x["tag"] == tag], rng, verdicts)
        arm_tab += a
        con_tab += c
    a, c = paper_block([x for x in rows if x["tag"] == "P1L"], rng, verdicts)
    paper_arm = ["| tag | model | head | arm | per seed 42/123/2021/3407/8888 | mean ± SEM |",
                 "|---|---|---|---|---|---|"] + a
    con_tab += c
    sel, cur = hist_block(rows)
    same = sum(v["linear"][1] == v["mlp"][1] for v in verdicts)
    changes = [f"- {v['tag']} {v['model']} {v['contrast']}: {k} -> {v[k]} (same head at ROC selection: "
               f"{v['linear' if k.startswith('linear') else 'mlp'][1]})"
               for v in verdicts for k in v if k.endswith(("_bal", "_last"))
               and v[k] != v["linear" if k.startswith("linear") else "mlp"][1]]
    lines = [
        "# D25-E25: logged re-runs with both heads (S1L CHB-MIT, S3L Siena, S3FL Siena filtered, P1L paper split)",
        "", "ROC-AUC x100 on test. Registered reading: mlp_fullft with the unchanged D24 rules at the "
        "validation-ROC-selected epoch (test_at_best). Everything marked descriptive is post hoc. "
        "BIOT's mlp_fullft head is ELU -> Linear (257 parameters, same count as linear); CBraMod's is the "
        "3-layer MLP (64.4M parameters on 10 s windows).", "",
        "## Integrity", *inv, *orig,
        f"- history test_plot_only at best_epoch / last epoch equals test_at_best / test_last: max |diff| "
        f"{hist_max:.2g} ROC x100 over {len(rows)} (run, head) pairs",
        f"- problems: {problems if problems else 'none'}", "",
        "## Verdicts: D24-A (rotations) and D24-B (P1L), mlp_fullft vs linear", *con_tab, "",
        "Rule outputs: D18 paired rule (|mean| > 3 and same sign in >= 4/5 rotations / seeds). bal = epoch of "
        "max validation balanced accuracy (logit threshold 0, first max); last = epoch 10. Linear/roc rows are "
        "the D24 outcome rows recomputed from the E25 records.", "",
        f"Registered: mlp_fullft rule output equals the linear one in {same} of {len(verdicts)} rule outputs.", "",
        f"Descriptive: rule outputs that change with the selection rule ({len(changes)} of {4 * len(verdicts)} "
        "head x {bal, last} x rule outputs):", *changes, "",
        "## Arm means, rotations (mean over 3 seeds per rotation; then over rotations; then over the 15 runs)",
        *arm_tab, "", "## Arm means, paper split (P1L)", *paper_arm, "",
        "## Histories (descriptive): epoch selection", *sel, "",
        "Histogram counts runs whose validation-ROC-selected epoch is 1..10. 'bal-sel - ROC-sel' is the test ROC "
        "change if the epoch were chosen by validation balanced accuracy; 'oracle' uses the plot-only test curve "
        "(never a selection rule).", "",
        "## Histories (descriptive): loss and curve shapes", *cur, ""]
    (out / "E25.md").write_text("\n".join(lines))
    with (out / "e25_runs.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    (out / "e25_verdicts.json").write_text(json.dumps(verdicts, indent=1, default=float))
    print("\n".join(lines))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
