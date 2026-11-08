#!/usr/bin/env python3
"""E19-free (D25): montage/QC sensitivity of the D24-A contrasts, and the CHB-MIT seizure census
(142 of 198 seizures tested; chb12/13/17 and chb02_16+ dropped, and why).

    # per-EDF montage (n_present) and QC on the raw CHB-MIT files: desktop
    PYTHONPATH=src ~/dxenv/bin/python scripts/analysis/qc_sensitivity.py files --root ~/dxdata/chbmit/1.0.0
    # re-score + census + figures: anywhere with artifacts/s3-results
    .venv/bin/python scripts/analysis/qc_sensitivity.py rescore

Pre-registered (notes/completeness-audit.md E19-free, adopted as written by decisions.md D25):
- files with n_present < 16 or a QC flag, and the affected test windows per fold;
- re-score the D24-A contrasts without those windows; rule: report the contrast change, a
  verdict flip is flagged as a limitation;
- the seizure census for the paper text.
Fixed here before any of it was computed:
- "QC flag" = the D21 rule (scripts/preprocess_siena.py: a bipolar pair with hf_share > 0.5,
  RMS < 1 uV or lp_ratio < 1e-3). Siena: the flags in its preprocess report. CHB-MIT: its report
  carries no QC, so this script computes the same three numbers per present pair on the raw
  256 Hz recording (Welch, 2 s segments, as for Siena). n_present comes from the same
  channel_indices() the preprocessing used (the report lists only the three 0/16 files).
- The PRIMARY exclusion set is the union (n_present < 16 OR any QC flag) at file level; the two
  components are also reported (descriptive). Excluding a file drops all its test windows.
- Re-score = test_at_best ROC-AUC recomputed from the saved per-window scores (scores_best) on the
  kept windows, then exactly the D24-A reading (scripts/read_d24.py): per-rotation mean over the
  3 seeds, D18 paired rule on last - lp, last_randinit - last, lp - lp_randinit, and D17.
  The full-set recomputation must equal the stored ROC (checked; abort otherwise).
Writes artifacts/analysis/qc/.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
OUT = ROOT / "artifacts" / "analysis" / "qc"
ROTS = tuple(f"rot{i}" for i in range(5))
ARMS = ("lp", "lp_randinit", "last", "last_randinit", "all")
CONTRASTS = (("last", "lp"), ("last_randinit", "last"), ("lp", "lp_randinit"))
SETTINGS = (("chbmit", "CHB-MIT", ("S1E", "S1M")), ("siena", "Siena", ("S3E", "S3M")),
            ("siena", "Siena filtered", ("S3FE", "S3FM")))
FS = 256


def qc_flags(rms: float, hf: float, lp: float) -> bool:
    """D21 rule, same thresholds as scripts/preprocess_siena.py (NaN ratios: flat pair, RMS flags it)."""
    return hf > 0.5 or rms < 1.0 or lp < 1e-3


# ---------------------------------------------------------------- files stage (desktop)
def _file(args):
    path, in_eval = args
    import mne  # noqa: PLC0415
    from scipy.signal import welch  # noqa: PLC0415

    from eegdrift.data.edf import BIOT_CHANNELS, channel_indices  # noqa: PLC0415

    raw = mne.io.read_raw_edf(path, preload=False, verbose="ERROR")
    idx = channel_indices(list(raw.ch_names))
    rec = {"file": os.path.basename(path)[:-4], "case": re.match(r"chb\d\d", os.path.basename(path))[0],
           "sfreq": float(raw.info["sfreq"]), "duration_s": raw.n_times / raw.info["sfreq"],
           "n_present": sum(i is not None for i in idx), "in_eval": in_eval,
           "missing": [c for c, i in zip(BIOT_CHANNELS, idx, strict=True) if i is None]}
    if in_eval:
        rows = []
        for ch, i in zip(BIOT_CHANNELS, idx, strict=True):
            if i is None:
                continue
            x = raw.get_data(picks=[i], units="uV")[0]
            f, p = welch(x, fs=raw.info["sfreq"], nperseg=2 * int(raw.info["sfreq"]))
            with np.errstate(invalid="ignore", divide="ignore"):
                hf = float(p[f > 45].sum() / p.sum())
                lp = float(p[(f >= 30) & (f < 45)].sum() / p[(f >= 1) & (f < 30)].sum())
            rms = float(np.sqrt(np.mean(np.square(x, dtype=np.float64))))
            rows.append({"pair": ch, "rms_uv": round(rms, 3), "hf_share": round(hf, 4), "lp_ratio": round(lp, 6),
                         "flag": qc_flags(rms, hf, lp)})
        rec["qc"] = rows
    return rec


def files(args) -> int:
    from eegdrift.data.chbmit import eval_files  # noqa: PLC0415

    root = os.path.expanduser(args.root)
    ev = set(eval_files(root))
    paths = sorted(os.path.join(root, c, f) for c in sorted(os.listdir(root)) if c.startswith("chb")
                   and os.path.isdir(os.path.join(root, c)) for f in os.listdir(os.path.join(root, c))
                   if f.endswith(".edf"))
    with Pool(args.workers) as pool:
        recs = pool.map(_file, [(p, p in ev) for p in paths], chunksize=1)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "chbmit_files.json").write_text(json.dumps(recs, indent=1))
    changes = {c: sum(line.startswith("Channels changed") for line in (Path(root) / c / f"{c}-summary.txt")
                      .read_text(errors="replace").splitlines())
               for c in sorted(os.listdir(root)) if (Path(root) / c / f"{c}-summary.txt").exists()}
    (OUT / "chbmit_montage_changes.json").write_text(json.dumps(changes, indent=1))
    print(f"{len(recs)} EDFs, {sum(r['in_eval'] for r in recs)} eval files, "
          f"n_present < 16: {sum(r['n_present'] < 16 for r in recs)}, "
          f"eval files with a QC flag: {sum(any(q['flag'] for q in r.get('qc', [])) for r in recs)}")
    return 0


# ---------------------------------------------------------------- rescore stage
def stem(key: str) -> str:
    return key.rsplit("-", 2)[0]


def contrast(x, y, is_d17: bool, paired, d17) -> dict | None:
    """D18 paired rule (or D17) over the rotations whose re-scored ROC exists."""
    if x is None or y is None:
        return None
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    ok = ~np.isnan(x - y)
    if ok.sum() < 3:
        return None
    d = (x - y)[ok]
    verdict = d17(list(x[ok]), list(y[ok])) if is_d17 else paired(list(d))
    return {"mean": float(d.mean()), "per_rot": [float(v) for v in x - y], "verdict": verdict,
            "rotations": int(ok.sum())}


def exclusion_sets() -> tuple[dict, dict]:
    """dataset -> {set name: {file stem: reason}}; and the CHB-MIT per-file records."""
    ch = json.loads((OUT / "chbmit_files.json").read_text())
    ev = [r for r in ch if r["in_eval"]]
    mont = {r["file"]: f"n_present {r['n_present']}/16, missing {','.join(r['missing'])}"
            for r in ev if r["n_present"] < 16}
    qc = {r["file"]: "QC " + ", ".join(f"{q['pair']} (rms {q['rms_uv']}, hf {q['hf_share']}, lp {q['lp_ratio']})"
                                       for q in r["qc"] if q["flag"])
          for r in ev if any(q["flag"] for q in r["qc"])}
    sie = json.loads((ROOT / "artifacts" / "siena" / "siena_preprocess_report.json").read_text())
    sq: dict = defaultdict(list)
    for f in sie["qc_flags"]:
        sq[f["file"]].append(f"{f['pair']} (rms {f['rms_uv']}, hf {f['hf_share']}, lp {f['lp_ratio']})")
    sqc = {k: "QC " + ", ".join(v) for k, v in sq.items()}
    union = {**qc, **mont}
    for k in set(qc) & set(mont):
        union[k] = mont[k] + "; " + qc[k]
    return {"chbmit": {"primary": union, "n_present<16": mont, "qc_flag": qc},
            "siena": {"primary": sqc, "n_present<16": {}, "qc_flag": sqc}}, {r["file"]: r for r in ch}


def load_runs(dataset: str, tags: tuple[str, ...]) -> list[dict]:
    runs, seen = [], set()
    for p in sorted((ROOT / "artifacts" / "s3-results").rglob("results/*.json")):
        if p.name.startswith(("diag-", "test-index-", "val-index-", "report-")):
            continue
        r = json.loads(p.read_text())
        if r.get("smoke") or r["dataset"] != dataset or r.get("run_tag") not in tags or r["arm"] not in ARMS \
                or r["split"] not in ROTS or "linear" not in r["probes"]:
            continue
        res = r["probes"]["linear"]
        if r["versions"]["probe"] != 4 or res["spec"].get("backbone_mode") != "eval":
            raise SystemExit(f"{p.name}: not a probe-v4 eval-mode record")
        cell = (r["model"], r["arm"], r["split"], r["seed"])
        if cell in seen:
            raise SystemExit(f"two records for {cell}")
        seen.add(cell)
        runs.append({"cell": cell, "roc": res["test_at_best"]["roc_auc"], "npz": p.with_suffix(".linear.npz"),
                     "index": p.parent / r["test_index"], "tag": r["run_tag"]})
    return runs


def rescore(_args) -> int:
    import matplotlib  # noqa: PLC0415

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt  # noqa: PLC0415
    from read_step1 import d17, paired  # noqa: PLC0415
    from sklearn.metrics import roc_auc_score  # noqa: PLC0415

    sets, chfiles = exclusion_sets()
    idx_cache: dict = {}
    L = ["# E19-free: montage/QC sensitivity of the D24-A contrasts (D25)", "",
         "Primary exclusion = files with n_present < 16 OR a D21 QC flag (CHB-MIT QC computed here on the raw "
         "256 Hz files; Siena QC from its preprocess report). Rule: report the contrast change; a verdict "
         "flip is flagged as a limitation. ROC-AUC x100, linear head, test_at_best, per-rotation means of "
         "3 seeds, D18 paired rule, D17.", ""]
    # excluded files
    for ds, s in sets.items():
        L += [f"## Excluded files, {ds} (primary: {len(s['primary'])}; n_present<16: {len(s['n_present<16'])}; "
              f"QC: {len(s['qc_flag'])})", ""]
        L += [f"- {f}: {why}" for f, why in sorted(s["primary"].items())] or ["- none"]
        L.append("")
    # affected test windows per fold + re-score
    affected_rows, results, flips = [], [], []
    fold_plot: dict = {}
    for ds, label, tags in SETTINGS:
        runs = load_runs(ds, tags)
        roc: dict = defaultdict(lambda: defaultdict(dict))   # set -> (model, arm, rot) -> seed -> roc
        for run in runs:
            if run["index"] not in idx_cache:
                idx_cache[run["index"]] = np.array([stem(k["key"]) for k in json.loads(run["index"].read_text())])
            fst = idx_cache[run["index"]]
            z = np.load(run["npz"])
            y, s = z["y_test"].astype(int), z["scores_best"].astype(np.float64)
            if len(y) != len(fst):
                raise SystemExit(f"{run['npz'].name}: {len(y)} scores vs {len(fst)} index rows")
            full = roc_auc_score(y, s)
            if abs(full - run["roc"]) > 1e-6:
                raise SystemExit(f"{run['npz'].name}: recomputed ROC {full} != stored {run['roc']}")
            model, arm, rot, seed = run["cell"]
            roc["none"][(model, arm, rot)][seed] = 100 * full
            for name, ex in sets[ds].items():
                keep = ~np.isin(fst, list(ex))
                ok = 0 < y[keep].sum() < keep.sum()
                roc[name][(model, arm, rot)][seed] = 100 * roc_auc_score(y[keep], s[keep]) if ok else float("nan")
                if name == "primary" and (label, rot) not in fold_plot:   # same index + labels per fold
                    ex_mask = ~keep
                    fold_plot[(label, rot)] = {"n": int(len(y)), "pos": int(y.sum()), "ex_n": int(ex_mask.sum()),
                                               "ex_pos": int(y[ex_mask].sum()),
                                               "files": sorted(set(fst[ex_mask].tolist()))}
        for rot in ROTS:
            f = fold_plot[(label, rot)]
            affected_rows.append((label, rot, f))
        for model in ("biot", "cbramod"):
            per: dict = {}
            for name in roc:
                per[name] = {}
                for arm in ARMS:
                    cells = [roc[name].get((model, arm, r), {}) for r in ROTS]
                    if all(len(c) == 3 for c in cells):
                        per[name][arm] = [float(np.mean(list(c.values()))) for c in cells]
            for a, b in (*CONTRASTS, ("D17", "")):
                row = {"setting": label, "model": model,
                       "contrast": f"{a} - {b}" if b else "D17 (last_randinit vs lp_randinit)"}
                xa, xb = ("last_randinit", "lp_randinit") if a == "D17" else (a, b)
                for name in per:
                    row[name] = contrast(per[name].get(xa), per[name].get(xb), a == "D17", paired, d17)
                    if row[name] and row[name]["rotations"] < 5 and row.get("none"):
                        ok = ~np.isnan(row[name]["per_rot"])   # the full test set on the same rotations
                        row[name]["full_same_rot"] = contrast(list(np.asarray(per["none"][xa])[ok]),
                                                              list(np.asarray(per["none"][xb])[ok]), a == "D17",
                                                              paired, d17)
                if row.get("none") and row.get("primary") and row["none"]["verdict"] != row["primary"]["verdict"]:
                    flips.append(row)
                results.append(row)
    # CHB-MIT paper split (descriptive)
    paper_idx = next((ROOT / "artifacts" / "s3-results").glob("arms-biot-chb-p1elp/results/test-index-*.json"))
    pst = np.array([stem(k["key"]) for k in json.loads(paper_idx.read_text())])
    pex = np.isin(pst, list(sets["chbmit"]["primary"]))

    L += ["## Affected test windows per fold (primary set)", "",
          "| setting | fold | test windows | positives | excluded windows | excluded positives | excluded files |",
          "|---|---|---|---|---|---|---|"]
    for label, rot, f in affected_rows:
        L.append(f"| {label} | {rot} | {f['n']:,} | {f['pos']:,} | {f['ex_n']:,} "
                 f"({100 * f['ex_n'] / f['n']:.1f} %) | {f['ex_pos']:,} | {', '.join(f['files']) or '-'} |")
    L.append(f"| CHB-MIT | paper split (P1E, descriptive) | {len(pst):,} | - | {int(pex.sum()):,} | - | "
             f"{', '.join(sorted(set(pst[pex].tolist()))) or '-'} |")
    def fmt(v):
        if v is None:
            return "n/a"
        per_rot = ", ".join("n/a" if np.isnan(x) else f"{x:+.1f}" for x in v["per_rot"])
        n = v["rotations"]
        k = "" if n == 5 else f" ({n}/5 rotations, rule needs {n - 1}: DESCRIPTIVE)"
        return f"{v['mean']:+.1f} [{per_rot}] {v['verdict']}{k}"

    def change(r):
        if not (r.get("none") and r.get("primary")):
            return "n/a", "n/a"
        ref = r["primary"].get("full_same_rot") or r["none"]
        ch = f"{r['primary']['mean'] - ref['mean']:+.2f}"
        if r["primary"]["rotations"] < 5:
            return ch + " (vs full set on the same rotations)", (
                "not computable as pre-registered; same-rotation verdict "
                + ("**changes** (descriptive)" if ref["verdict"] != r["primary"]["verdict"] else "unchanged"))
        return ch, "**FLIP**" if r["none"]["verdict"] != r["primary"]["verdict"] else "no"

    L += ["", "## D24-A contrasts: full test set vs without the excluded files", "",
          "Per-rotation values in brackets. If the exclusion leaves a rotation with no test windows (or no "
          "positives), the 5-rotation D24-A reading cannot be applied; the same D18/D17 functions are then run "
          "on the remaining rotations (k-1 of k same sign) and labelled DESCRIPTIVE.", "",
          "| setting | model | contrast | full test set (recomputed = D24) | primary exclusion | change in mean | "
          "verdict flip | n_present<16 only | QC only |", "|---|---|---|---|---|---|---|---|---|"]
    for r in results:
        ch, flip = change(r)
        L.append(f"| {r['setting']} | {r['model']} | {r['contrast']} | {fmt(r.get('none'))} | "
                 f"{fmt(r.get('primary'))} | {ch} | {flip} | {fmt(r.get('n_present<16'))} | "
                 f"{fmt(r.get('qc_flag'))} |")
    L += ["", "## Verdict (D25 E19-free rule)", ""]
    pre = [r for r in results if r.get("primary") and r["primary"]["rotations"] == 5]
    desc = [r for r in results if r.get("primary") and r["primary"]["rotations"] < 5]
    nocomp = sorted({r["setting"] for r in results if r.get("none") and not r.get("primary")} |
                    {r["setting"] for r in desc})
    L += ([f"- **LIMITATION: verdict flip** {r['setting']} / {r['model']} / {r['contrast']}: "
           f"{r['none']['verdict']} -> {r['primary']['verdict']}" for r in flips if r in pre] or
          [f"- Where the pre-registered 5-rotation reading is computable ({sorted({r['setting'] for r in pre})}), "
           "no D24-A verdict string changes when the excluded files' test windows are dropped."])
    if pre:
        big = max(abs(r["primary"]["mean"] - r["none"]["mean"]) for r in pre)
        L.append(f"- Largest change in a contrast mean there: {big:.2f} ROC points.")
    if nocomp:
        L.append(f"- **LIMITATION (not computable as pre-registered): {nocomp}**: the QC exclusion removes every "
                 "test window of at least one rotation, so the D24-A verdicts cannot be re-read without the "
                 "flagged files under the 5-rotation rule; the same-rotation descriptive readings are in the "
                 "table.")
        for r in desc:
            ref = r["primary"].get("full_same_rot")
            if ref and ref["verdict"] != r["primary"]["verdict"]:
                L.append(f"  - descriptive change: {r['setting']} / {r['model']} / {r['contrast']}: "
                         f"{ref['verdict']} -> {r['primary']['verdict']} on {r['primary']['rotations']} rotations")

    # seizure census (CHB-MIT)
    seizures = json.loads((ROOT / "configs" / "chbmit_seizures.json").read_text())
    total = sum(len(v) for v in seizures.values())
    ev_files = {f for f, r in chfiles.items() if r["in_eval"]}
    in_eval = {f: v for f, v in seizures.items() if f in ev_files and v}
    n_eval = sum(len(v) for v in in_eval.values())
    tested, pos_windows = set(), Counter()
    for rot in ROTS:
        res = ROOT / "artifacts" / "s3-results" / f"arms-biot-chb-{rot}-s1m" / "results"
        p = sorted(res.glob("biot-chbmit-lp-s*.json"))[0]
        rec = json.loads(p.read_text())
        y = np.load(p.with_suffix(".linear.npz"))["y_test"].astype(int)
        keys = [k["key"] for k in json.loads((p.parent / rec["test_index"]).read_text())]
        for k, lab in zip(keys, y, strict=True):
            f, kind, start = k.rsplit("-", 2)
            if not lab or kind != "grid":
                continue
            for j, (on, off) in enumerate(seizures.get(f, [])):
                if int(start) < off and int(start) + 10 * FS > on:
                    tested.add((f, j))
                    pos_windows[(f, j)] += 1
    by_case = Counter()
    for f, v in seizures.items():
        by_case[re.match(r"chb\d\d", f)[0]] += len(v)
    dropped = {f: len(v) for f, v in seizures.items() if v and f not in ev_files}
    L += ["", "## CHB-MIT seizure census (for §2.2 / §5.1)", "",
          f"- Seizures in the summary files (configs/chbmit_seizures.json): **{total}** in {len(by_case)} cases.",
          f"- In files the upstream eval pipeline processes (= our eval store): **{n_eval}**.",
          f"- With >= 1 positive (overlap-label) TEST window in the rotation where their case is test: "
          f"**{len(tested)} of {total}** (each case is test in exactly one of rot0-4).",
          f"- Dropped: {total - n_eval} seizures in {len(dropped)} files:", ""]
    dcase = Counter(re.match(r"chb\d\d", f)[0] for f in dropped for _ in range(dropped[f]))
    mpath = OUT / "chbmit_montage_changes.json"
    changes = json.loads(mpath.read_text()) if mpath.exists() else {}
    for c, n in sorted(dcase.items()):
        fl = [r for r in chfiles.values() if r["case"] == c]
        np_ = Counter(r["n_present"] for r in fl)
        names = sorted({re.sub(r"_\d+.*", "", r["file"]) for r in fl})
        why = ("case absent from the upstream process1.py file table (UPSTREAM_EVAL_FILES; a commented-out "
               "entry for patient 12 with an empty reference file follows that table)" if c in
               ("chb12", "chb13", "chb17") else
               "file name has a '+' suffix, which the table's chbNN_MM.edf pattern never matches")
        L.append(f"- {c}: {n} seizures dropped ({by_case[c]} in the case); {why}. Case has {len(fl)} EDFs "
                 f"(name stems {names}), {sum(r['duration_s'] for r in fl) / 3600:.1f} h; "
                 f"n_present over its EDFs {dict(sorted(np_.items()))}; montage changes in its summary: "
                 f"{changes.get(c, 'n/a')}"
                 + ("; its file names would not match the table's chbNN_MM.edf pattern either" if names != [c]
                    else "") + ".")
    plus = [f for f in dropped if "+" in f]
    L.append(f"- Files with '+' in the name that hold seizures: {plus}.")
    from eegdrift.data.chbmit import UPSTREAM_EVAL_FILES  # noqa: PLC0415

    block = {f"chb{p}": blk for p, _ref, _a, _b, blk in UPSTREAM_EVAL_FILES}
    L.append("- Montage changes per case ('Channels changed' blocks in chbXX-summary.txt) and the table's "
             "summary_index (which channel block of the summary is the reference), for every case with a "
             "change: "
             + ", ".join(f"{c} {n} ({'dropped' if c not in block else f'summary_index {block[c]}'})"
                         for c, n in sorted(changes.items()) if n) + ".")
    eval_np = Counter(r["n_present"] for r in chfiles.values() if r["in_eval"])
    L += [f"- n_present over the {len(ev_files)} eval files: {dict(sorted(eval_np.items()))}."]
    text = "\n".join(L) + "\n"
    (OUT / "qc_sensitivity.md").write_text(text)
    (OUT / "qc_sensitivity.json").write_text(json.dumps(
        {"exclusions": sets, "affected": [{"setting": a, "fold": b, **c} for a, b, c in affected_rows],
         "paper_split_excluded_windows": int(pex.sum()), "contrasts": results, "flips": flips,
         "census": {"total": total, "in_eval": n_eval, "tested_rotations": len(tested), "dropped_files": dropped,
                    "by_case": dict(sorted(by_case.items()))}}, indent=1, default=float))
    print(text)

    # figures
    ink, grid = "#52514e", "#e4e3df"
    blue, orange = "#2a78d6", "#eb6834"
    plt.rcParams.update({"axes.edgecolor": ink, "axes.labelcolor": ink, "xtick.color": ink, "ytick.color": ink,
                         "axes.spines.top": False, "axes.spines.right": False, "font.size": 9})
    fig, ax = plt.subplots(figsize=(9, 3.4))
    short = {"CHB-MIT": "CHB", "Siena": "Siena", "Siena filtered": "Siena-F"}
    lab = [f"{short[a]}\n{b}" for a, b, _ in affected_rows]
    xs = np.arange(len(affected_rows))
    ax.bar(xs - 0.2, [100 * f["ex_n"] / f["n"] for *_, f in affected_rows], 0.38, color=blue, label="test windows")
    ax.bar(xs + 0.2, [100 * f["ex_pos"] / max(f["pos"], 1) for *_, f in affected_rows], 0.38, color=orange,
           label="positive test windows")
    ax.set_xticks(xs, lab, fontsize=7)
    ax.set_ylabel("% excluded (primary set)")
    ax.grid(axis="y", color=grid, lw=0.6)
    ax.legend(frameon=False)
    ax.set_title("E19-free: test windows removed by the montage/QC exclusion, per fold", color=ink, fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / "fig_affected_windows.png", dpi=160)
    plt.close(fig)

    fig, axs = plt.subplots(2, 3, figsize=(11, 6.2), sharey=False)
    for j, (_, label, _) in enumerate(SETTINGS):
        for i, model in enumerate(("biot", "cbramod")):
            ax = axs[i, j]
            rows = [r for r in results if r["setting"] == label and r["model"] == model and r.get("none")]
            for k, r in enumerate(rows):
                for name, col, dx, mk in (("none", blue, -0.12, "o"), ("primary", orange, 0.12, "^")):
                    if r.get(name):
                        ax.scatter([k + dx] * 5, r[name]["per_rot"], color=col, s=14, marker=mk,
                                   label=("full test set" if name == "none" else "without excluded files")
                                   if k == 0 else None, zorder=3)
                        ax.plot([k + dx - 0.1, k + dx + 0.1], [r[name]["mean"]] * 2, color=col, lw=2)
            ax.axhspan(-3, 3, color=grid, zorder=0)
            ax.axhline(0, color=ink, lw=0.6)
            ax.set_xticks(range(len(rows)), [r["contrast"].split(" (")[0] for r in rows], fontsize=7, rotation=15)
            ax.set_title(f"{label}, {model}", color=ink, fontsize=9)
            ax.set_ylabel("per-rotation difference (ROC x100)")
            ax.grid(axis="y", color=grid, lw=0.6)
    axs[0, 0].legend(frameon=False, fontsize=7)
    fig.suptitle("E19-free: D24-A contrasts per rotation, full vs QC-excluded test set (band = +-3)", color=ink,
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / "fig_rescore_contrasts.png", dpi=160)
    plt.close(fig)

    cases = sorted(by_case)
    t_case = Counter(re.match(r"chb\d\d", f)[0] for f, _ in tested)
    fig, ax = plt.subplots(figsize=(8, 3.2))
    ax.bar(cases, [t_case[c] for c in cases], color=blue, label="tested (positive test window)")
    ax.bar(cases, [by_case[c] - t_case[c] for c in cases], bottom=[t_case[c] for c in cases], color=orange,
           label="not tested (dropped)")
    ax.set_ylabel("seizures")
    ax.tick_params(axis="x", rotation=60, labelsize=7)
    ax.grid(axis="y", color=grid, lw=0.6)
    ax.legend(frameon=False)
    ax.set_title(f"CHB-MIT seizures: {len(tested)} of {total} tested across rot0-4", color=ink, fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / "fig_seizure_census.png", dpi=160)
    plt.close(fig)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="stage", required=True)
    f = sub.add_parser("files")
    f.add_argument("--root", required=True)
    f.add_argument("--workers", type=int, default=16)
    sub.add_parser("rescore")
    args = ap.parse_args()
    return {"files": files, "rescore": rescore}[args.stage](args)


if __name__ == "__main__":
    raise SystemExit(main())
