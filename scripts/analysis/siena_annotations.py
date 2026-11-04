#!/usr/bin/env python3
"""E18-free (notes/completeness-audit.md, adopted by D25): Siena annotation alignment and
cross-check. Pre-registered rule: any UNEXPLAINED onset/offset difference larger than one window
(10 s) triggers relabelling and a re-score of Siena; every difference must be 0 or explained.

1. diff: epilepsy2bids 0.0.7 (MIT, PyPI; run from a throwaway venv, nothing vendored) loads
   onsets/offsets from the raw PhysioNet files; they are diffed against configs/siena_seizures.json
   (512 Hz samples) and configs/chbmit_seizures.json (256 Hz samples). A Siena difference is
   "explained" only if it equals, to the second, the sum of the two documented D21 choices:
   (a) clock origin = EDF header start, where epilepsy2bids uses the txt "Registration start time"
   (difference header - registration), and (b) a txt line holding two times (PN10): D21 takes the
   first (union of the alternatives), epilepsy2bids the last. Anything else is unexplained.
2. onset: for all 47 Siena seizures, per channel and 1 s bin from -120 to +120 s around the
   annotated onset (raw 512 Hz bipolar pairs): line length (mean |dx| after a 0.5-45 Hz band-pass)
   and 1-30 Hz power (mean square after a 1-30 Hz band-pass); zero-phase 4th-order Butterworth.
   Definitions fixed in this file before any output was seen: r = log(feature / channel median
   over the baseline [-120, -20) s); r_bar = channel mean of r; z = (mean r_bar over the ictal
   window [0, min(duration, 30)) s - baseline mean) / baseline SD (per-second values). "Rise" iff
   z >= 2 (primary); "any-channel rise" iff the per-channel z >= 2 on some channel (secondary).
   Signal-onset lag (descriptive): first t >= -60 s where the 5 s centred mean of r_bar exceeds
   the baseline mean + 3 SD.
3. Zero-parameter line-length ROC per rotation: score = channel mean of the line length of the
   eval window exactly as the probes see it (computed by handcrafted_baseline.py fit, same test
   windows and labels as the probes).

  # desktop. Throwaway venvs: ~/dxenv/bin/python -m venv /tmp/e2b-venv &&
  #   /tmp/e2b-venv/bin/pip install --only-binary=:all: epilepsy2bids   (0.0.7; source numpy needs GCC >= 10.3)
  # and /tmp/eegd-an-venv as in handcrafted_baseline.py (mne, scipy).
  /tmp/e2b-venv/bin/python scripts/analysis/siena_annotations.py diff --out /tmp/eegd-analysis/siena_annot
  /tmp/eegd-an-venv/bin/python scripts/analysis/siena_annotations.py onset --out /tmp/eegd-analysis/siena_annot
  # Mac, after copying the outputs to artifacts/analysis/siena_annot (and handcrafted fit)
  .venv/bin/python scripts/analysis/siena_annotations.py report
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from eegdrift.data import siena as S  # noqa: E402

OUT = ROOT / "artifacts" / "analysis" / "siena_annot"
WINDOW_S = 10
PRE, POST, PAD = 120, 120, 10  # s around onset; PAD absorbs filter edge effects
T = np.arange(-PRE, POST)  # left edge of each 1 s bin, s from annotated onset
BASE = (T >= -120) & (T < -20)
_CLK = re.compile(r"(\d\d)[.:](\d\d)[.:](\d\d)")


# ---------------------------------------------------------------- 1. annotation diff (e2b venv)
def _clock(val: str, last: bool) -> int:
    m = _CLK.findall(val.replace(" ", ""))
    h, mi, s = map(int, m[-1] if last else m[0])
    return h * 3600 + mi * 60 + s


def txt_seizures(path: Path) -> list[dict]:
    """Per seizure in txt order: stem, registration line (carried over, as epilepsy2bids does for
    PN12's second block), raw start and end values."""
    out, stem, reg, start = [], None, None, None
    with open(path, encoding="latin-1") as f:
        for line in f:
            key, _, val = line.partition(":")
            key = key.strip().lower()
            if key == "file name":
                stem = S.file_stem(val)
            elif key == "registration start time":
                reg = val
            elif key in ("seizure start time", "start time"):
                start = val
            elif key in ("seizure end time", "end time"):
                out.append({"stem": stem, "reg": reg, "start": start, "end": val})
    return out


def wrap(d: float) -> float:
    return (d + 43200) % 86400 - 43200


def diff(args) -> None:
    os.environ["TZ"] = "UTC"  # epilepsy2bids parses with time.mktime: keep it free of DST
    time.tzset()
    from importlib.metadata import version  # noqa: PLC0415

    from epilepsy2bids.load_annotations import chbmit as e2c  # noqa: PLC0415
    from epilepsy2bids.load_annotations import siena as e2s  # noqa: PLC0415

    out = {"epilepsy2bids": version("epilepsy2bids"), "siena": [], "chbmit": [], "errors": []}
    sroot, croot = Path(args.siena_root).expanduser(), Path(args.chbmit_root).expanduser()
    ours = json.loads((ROOT / "configs" / "siena_seizures.json").read_text())
    txt = {}
    for p in sorted(sroot.glob("PN*/Seizures-list-PN*.txt")):
        for sz in txt_seizures(p):
            txt.setdefault(sz["stem"], []).append(sz)
    for edf in sorted(sroot.glob("PN*/*.edf")):
        stem = edf.stem
        try:
            ev = sorted(e2s.loadAnnotationsFromEdf(str(edf)).getEvents())
        except Exception as e:  # noqa: BLE001  (recorded, counted as unexplained)
            out["errors"].append({"dataset": "siena", "stem": stem, "error": repr(e)})
            continue
        mine = sorted((a / S.FS_NATIVE, b / S.FS_NATIVE) for a, b in ours.get(stem, []))
        if len(ev) != len(mine):
            out["errors"].append({"dataset": "siena", "stem": stem, "error": f"{len(ev)} vs {len(mine)} seizures"})
        h0, rec_s = S.edf_header(edf)
        for k, ((ea, eb), (oa, ob)) in enumerate(zip(ev, mine, strict=False)):
            t = txt[stem][k]
            origin = wrap(h0 - _clock(t["reg"], last=False)) if t["reg"] else float("nan")
            fix = S.TIME_FIX.get(stem)
            alt_on = 0 if fix and fix[0] == "start" else wrap(_clock(t["start"], True) - _clock(t["start"], False))
            alt_off = 0 if fix and fix[0] == "end" else wrap(_clock(t["end"], True) - _clock(t["end"], False))
            d_on, d_off = wrap(ea - oa), wrap(eb - ob)
            why = []
            if origin:
                why.append(f"clock origin: EDF header start minus txt Registration start = {origin:+.0f} s (D21)")
            if eb > rec_s:
                why.append(f"the epilepsy2bids interval ends after the recording ({rec_s:.0f} s)")
            if alt_on or alt_off:
                why.append(
                    f"two times on the txt line (onset {alt_on:+.0f} s, offset {alt_off:+.0f} s): D21 takes "
                    "the first (union of the alternatives), epilepsy2bids the last"
                )
            explained = d_on == origin + alt_on and d_off == origin + alt_off
            out["siena"].append(
                {
                    "stem": stem,
                    "k": k,
                    "e2b_s": [ea, eb],
                    "ours_s": [oa, ob],
                    "d_on": d_on,
                    "d_off": d_off,
                    "header_minus_registration": origin,
                    "alt_on": alt_on,
                    "alt_off": alt_off,
                    "recording_s": rec_s,
                    "explained": bool(explained or (d_on == 0 and d_off == 0)),
                    "why": "; ".join(why) if (d_on or d_off) else "identical",
                    "txt": {k2: (v.strip() if v else v) for k2, v in t.items()},
                }
            )
    cours = json.loads((ROOT / "configs" / "chbmit_seizures.json").read_text())
    seen = set()
    for edf in sorted(croot.glob("chb*/*.edf")):
        stem = edf.stem
        seen.add(stem)
        try:
            ev = sorted(e2c.loadAnnotationsFromEdf(str(edf)).getEvents())
        except Exception as e:  # noqa: BLE001
            out["errors"].append({"dataset": "chbmit", "stem": stem, "error": repr(e)})
            continue
        mine = sorted((a / 256, b / 256) for a, b in cours.get(stem, []))
        if stem not in cours and not ev:  # benign: no seizure in either source
            out.setdefault("chbmit_edf_not_in_table_no_seizure", []).append(stem)
        elif stem not in cours:
            out["errors"].append(
                {"dataset": "chbmit", "stem": stem, "error": f"EDF not in table, {len(ev)} seizures"}
            )
        if len(ev) != len(mine):
            out["errors"].append(
                {"dataset": "chbmit", "stem": stem, "error": f"{len(ev)} vs {len(mine)} seizures"}
            )
        for k, ((ea, eb), (oa, ob)) in enumerate(zip(ev, mine, strict=False)):
            out["chbmit"].append(
                {"stem": stem, "k": k, "e2b_s": [ea, eb], "ours_s": [oa, ob], "d_on": ea - oa, "d_off": eb - ob}
            )
    out["chbmit_table_without_edf"] = sorted(set(cours) - seen)
    od = Path(args.out)
    od.mkdir(parents=True, exist_ok=True)
    (od / "diff.json").write_text(json.dumps(out, indent=1))
    n_s = sum(1 for r in out["siena"] if r["d_on"] or r["d_off"])
    n_c = sum(1 for r in out["chbmit"] if r["d_on"] or r["d_off"])
    print(
        f"[diff] siena {len(out['siena'])} seizures, {n_s} differ; chbmit {len(out['chbmit'])} seizures, "
        f"{n_c} differ; {len(out['errors'])} errors",
        flush=True,
    )


# ---------------------------------------------------------------- 2. onset-locked features (desktop)
def onset_one(job: tuple[str, str, int, int, int]) -> dict:
    import mne  # noqa: PLC0415
    from scipy.signal import butter, sosfiltfilt  # noqa: PLC0415

    root, stem, k, on, off = job
    fs = S.FS_NATIVE
    raw = mne.io.read_raw_edf(Path(root) / stem[:4] / f"{stem}.edf", preload=False, verbose="ERROR")
    a, b = on - (PRE + PAD) * fs, on + (POST + PAD) * fs
    a0, b0 = max(a, 0), min(b, raw.n_times)
    x = raw.get_data(picks=S.electrode_indices(raw.ch_names), start=a0, stop=b0, units="uV")
    ix = {e: i for i, e in enumerate(S.ELECTRODES)}
    bip = np.stack([x[ix[p]] - x[ix[q]] for p, q in S.PAIRS])
    xl = sosfiltfilt(butter(4, [0.5, 45], "bandpass", fs=fs, output="sos"), bip, axis=-1)
    xp = sosfiltfilt(butter(4, [1, 30], "bandpass", fs=fs, output="sos"), bip, axis=-1)
    ll, pw = np.full((16, len(T)), np.nan), np.full((16, len(T)), np.nan)
    for i in range(len(T)):
        s0 = (PAD + i) * fs - (a0 - a)
        if s0 >= 0 and s0 + fs <= xl.shape[1]:
            ll[:, i] = np.abs(np.diff(xl[:, s0 : s0 + fs], axis=1)).mean(1)
            pw[:, i] = np.mean(xp[:, s0 : s0 + fs] ** 2, axis=1)
    return {"stem": stem, "k": k, "on_s": on / fs, "dur_s": (off - on) / fs, "ll": ll, "pw": pw}


def onset(args) -> None:
    table = json.loads((ROOT / "configs" / "siena_seizures.json").read_text())
    root = str(Path(args.siena_root).expanduser())
    jobs = [(root, stem, k, on, off) for stem, sz in table.items() for k, (on, off) in enumerate(sz)]
    with Pool(args.workers) as pool:
        res = pool.map(onset_one, jobs)
    od = Path(args.out)
    od.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        od / "onset.npz",
        ll=np.stack([r["ll"] for r in res]),
        pw=np.stack([r["pw"] for r in res]),
        t=T,
        stem=np.array([r["stem"] for r in res]),
        k=np.array([r["k"] for r in res]),
        on_s=np.array([r["on_s"] for r in res]),
        dur_s=np.array([r["dur_s"] for r in res]),
    )
    print(f"[onset] {len(res)} seizures -> {od / 'onset.npz'}", flush=True)


def fmt_lag(v: float) -> str:
    return "-" if np.isnan(v) else f"{v:+.0f}"


def rise(F: np.ndarray, dur: float) -> dict:
    """F [16, len(T)] per-second feature of one seizure -> the pre-defined rise statistics."""
    lf = np.log(F)
    r = lf - np.nanmedian(lf[:, BASE], axis=1, keepdims=True)
    ictal = (T >= 0) & (T < min(dur, 30))
    rb = np.nanmean(r, 0)
    mb, sb = np.nanmean(rb[BASE]), np.nanstd(rb[BASE], ddof=1)
    z = (np.nanmean(rb[ictal]) - mb) / sb
    zc = (np.nanmean(r[:, ictal], 1) - np.nanmean(r[:, BASE], 1)) / np.nanstd(r[:, BASE], 1, ddof=1)
    sm = np.convolve(np.nan_to_num(rb, nan=mb), np.ones(5) / 5, mode="same")
    hit = np.flatnonzero((T >= -60) & (sm > mb + 3 * sb))
    return {
        "z": float(z),
        "z_any": float(np.max(zc)),
        "fold": float(np.exp(np.nanmean(rb[ictal]) - mb)),
        "lag_s": float(T[hit[0]]) if len(hit) else float("nan"),
        "r_bar": rb,
        "base_mean": mb,
        "base_sd": sb,
    }


# ---------------------------------------------------------------- report (Mac)
def report(args) -> None:
    import matplotlib  # noqa: PLC0415

    matplotlib.use("Agg")
    import handcrafted_baseline as hb  # noqa: PLC0415

    d = json.loads((OUT / "diff.json").read_text())
    same_siena = json.loads((ROOT / "artifacts/siena/siena_seizures.json").read_text())
    on = np.load(OUT / "onset.npz")
    L = [
        "# E18-free: Siena annotation alignment and cross-check (D25)",
        "",
        "Pre-registered rule (completeness-audit E18-free): every onset/offset difference against epilepsy2bids "
        "must be 0 or explained;",
        "any unexplained difference larger than 1 window (10 s) triggers relabelling and a re-score of Siena.",
        "",
    ]

    # 1. diff
    sd = d["siena"]
    nz = [r for r in sd if r["d_on"] or r["d_off"]]
    unexpl = [r for r in sd if not r["explained"]]
    big = [r for r in unexpl if max(abs(r["d_on"]), abs(r["d_off"])) > WINDOW_S]
    cd = d["chbmit"]
    cnz = [r for r in cd if r["d_on"] or r["d_off"]]
    s_err = [e for e in d["errors"] if e["dataset"] == "siena"]
    c_err = [e for e in d["errors"] if e["dataset"] == "chbmit"]
    trig = bool(big or s_err)
    L += [
        "## 1. Cross-check against epilepsy2bids " + d["epilepsy2bids"],
        "",
        f"- Siena: {len(sd)} seizures compared (table: 47); identical {len(sd) - len(nz)}; differ {len(nz)}; "
        f"explained {len(nz) - len(unexpl)}; unexplained {len(unexpl)} (of which > {WINDOW_S} s: {len(big)}); "
        f"loader errors / count mismatches {len(s_err)}.",
        f"- CHB-MIT: {len(cd)} seizures compared (table: {sum(len(v) for v in hb.seizures('chbmit').values())}); "
        f"identical {len(cd) - len(cnz)}; differ {len(cnz)}; loader errors / count mismatches / EDFs not in the "
        f"table {len(c_err)}; table entries without an EDF {len(d['chbmit_table_without_edf'])}.",
        f"- CHB-MIT EDFs absent from the table, with no seizure in epilepsy2bids either (not listed in their "
        f"summary file): {len(d.get('chbmit_edf_not_in_table_no_seizure', []))} "
        f"({', '.join(d.get('chbmit_edf_not_in_table_no_seizure', []))}).",
        "- configs/siena_seizures.json equals the preprocessing output artifacts/siena/siena_seizures.json: "
        f"{json.loads((ROOT / 'configs/siena_seizures.json').read_text()) == same_siena}.",
        f"- **Rule outcome: {'TRIGGERED: relabel and re-score Siena' if trig else 'not triggered'}** "
        f"({len(big)} unexplained Siena differences > {WINDOW_S} s; {len(s_err)} Siena loader problems).",
        "",
        "| stem | k | ours on-off (s) | epilepsy2bids on-off (s) | d on | d off | explained | why |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in nz:
        L.append(
            f"| {r['stem']} | {r['k']} | {r['ours_s'][0]:.0f}-{r['ours_s'][1]:.0f} | {r['e2b_s'][0]:.0f}-"
            f"{r['e2b_s'][1]:.0f} | {r['d_on']:+.0f} | {r['d_off']:+.0f} | {'yes' if r['explained'] else '**NO**'}"
            f" | {r['why']} |"
        )
    if cnz:
        L += ["", "CHB-MIT differences:", "", "| stem | k | ours (s) | epilepsy2bids (s) |", "|---|---|---|---|"]
        L += [f"| {r['stem']} | {r['k']} | {r['ours_s']} | {r['e2b_s']} |" for r in cnz]
    if d["errors"]:
        L += ["", "Loader errors, count mismatches and file-set differences:", ""]
        L += [f"- {e}" for e in d["errors"]]
    if d["chbmit_table_without_edf"]:
        L += ["", f"- chbmit_seizures.json entries without an EDF: {d['chbmit_table_without_edf']}"]
    L.append("")

    # 2. onset-locked features
    stats = {f: [rise(on[f][i], float(on["dur_s"][i])) for i in range(len(on["stem"]))] for f in ("ll", "pw")}
    names = {"ll": "line length (0.5-45 Hz)", "pw": "1-30 Hz power"}
    L += [
        "## 2. Onset-locked line length and 1-30 Hz power, all Siena seizures",
        "",
        "z = (ictal-window mean - baseline mean) / baseline SD of the channel-mean log ratio; rise iff z >= 2 "
        "(fixed before computing).",
        "",
    ]
    for f in ("ll", "pw"):
        z = np.array([s["z"] for s in stats[f]])
        za = np.array([s["z_any"] for s in stats[f]])
        lag = np.array([s["lag_s"] for s in stats[f]])
        L += [
            f"- {names[f]}: no rise (z < 2) in **{int((z < 2).sum())} / {len(z)}** seizures; no rise on any "
            f"channel in {int((za < 2).sum())}; median z {np.median(z):.1f} [IQR {np.quantile(z, 0.25):.1f}, "
            f"{np.quantile(z, 0.75):.1f}]; median fold change {np.median([s['fold'] for s in stats[f]]):.2f}; "
            f"signal onset found in {int(np.isfinite(lag).sum())} / {len(lag)}, median lag "
            f"{np.nanmedian(lag):+.0f} s, |lag| > {WINDOW_S} s in {int((np.abs(lag) > WINDOW_S).sum())} "
            "(descriptive)."
        ]
    both = [i for i in range(len(on["stem"])) if stats["ll"][i]["z"] < 2 and stats["pw"][i]["z"] < 2]
    L += [
        f"- No rise in either feature (channel mean): {len(both)} / {len(on['stem'])}",
        "",
        "| seizure | duration s | z LL | z LL any ch | z power | z power any ch | fold LL | lag LL s | lag pw s |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for i, (st, k) in enumerate(zip(on["stem"], on["k"], strict=True)):
        a, b = stats["ll"][i], stats["pw"][i]
        L.append(
            f"| {st}#{k} | {on['dur_s'][i]:.0f} | {a['z']:.1f} | {a['z_any']:.1f} | {b['z']:.1f} | "
            f"{b['z_any']:.1f} | {a['fold']:.2f} | {fmt_lag(a['lag_s'])} | {fmt_lag(b['lag_s'])} |"
        )
    L.append("")

    # 3. zero-parameter line-length ROC per rotation
    L += [
        "## 3. Zero-parameter line-length ROC per rotation (test ROC x100; probe test windows and labels)",
        "",
        "| setting | row | " + " | ".join(hb.ROTS) + " | mean ± SEM |",
        "|---|---|" + "---|" * 6,
    ]
    fits = {}
    for s in hb.SETTINGS:
        fits[s] = [json.loads((hb.OUT / "fit" / f"{s}-{r}-overlap.json").read_text()) for r in hb.ROTS]
        runs = hb.model_runs(hb.SETTINGS[s][0], set(hb.SETTINGS[s][2]))
        rows = {
            "line length, zero-parameter": [100 * f["line_length_zero_param"]["test"]["roc_auc"] for f in fits[s]],
            "line length, zero-parameter, >=50% labels": [
                100 * f["line_length_zero_param"]["test_label50"]["roc_auc"] for f in fits[s]
            ],
            "hand-crafted LR": [100 * f["test"]["roc_auc"] for f in fits[s]],
        }
        for m in hb.MODELS:
            rows[f"{m} lp (3-seed mean)"] = hb.rot_means(runs, m, "lp", "roc_best")
        for name, v in rows.items():
            L.append(f"| {s} | {name} | " + " | ".join(f"{x:.1f}" for x in v) + f" | {hb.ms(v)} |")
    L += ["", "Siena rows answer the item; the CHB-MIT row is descriptive.", ""]
    text = "\n".join(L) + "\n"
    (OUT / "siena_annot.md").write_text(text)
    (OUT / "siena_annot.json").write_text(
        json.dumps(
            {
                "rule_triggered": trig,
                "siena_differences": nz,
                "unexplained": unexpl,
                "chbmit_differences": cnz,
                "errors": d["errors"],
                "rise": {
                    f: [
                        {"seizure": f"{st}#{k}"} | {kk: vv for kk, vv in s.items() if kk != "r_bar"}
                        for st, k, s in zip(on["stem"], on["k"], stats[f], strict=True)
                    ]
                    for f in stats
                },
            },
            indent=1,
        )
    )
    figures(on, stats, sd, fits)
    print(text)


def figures(on, stats, sd, fits) -> None:
    import matplotlib.pyplot as plt  # noqa: PLC0415

    ink, muted, c1, c2, c3 = "#0b0b0b", "#52514e", "#2a78d6", "#eb6834", "#1baf7a"
    plt.rcParams.update(
        {
            "font.size": 7,
            "axes.edgecolor": muted,
            "xtick.color": muted,
            "ytick.color": muted,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "legend.frameon": False,
        }
    )
    n = len(on["stem"])
    for f, title in (("ll", "line length (0.5-45 Hz)"), ("pw", "1-30 Hz power")):
        fig, axes = plt.subplots(7, 7, figsize=(15, 13), sharex=True)
        for i, ax in enumerate(axes.flat):
            if i < n:
                s = stats[f][i]
                ax.axvspan(0, min(on["dur_s"][i], POST), color=c2, alpha=0.12, lw=0)
                ax.axhline(s["base_mean"] + 2 * s["base_sd"], color=muted, lw=0.6, ls=":")
                ax.plot(T + 0.5, s["r_bar"], color=c1 if s["z"] >= 2 else c2, lw=1)
                ax.set_title(
                    f"{on['stem'][i]}#{on['k'][i]}  z={s['z']:.1f}", fontsize=6.5, color=ink if s["z"] >= 2 else c2
                )
            elif i == n:
                rb = np.stack([s["r_bar"] for s in stats[f]])
                ax.fill_between(T + 0.5, *np.nanquantile(rb, [0.25, 0.75], axis=0), color=c1, alpha=0.25, lw=0)
                ax.plot(T + 0.5, np.nanmedian(rb, 0), color=c1, lw=1.5)
                ax.set_title(f"median, IQR over {n}", fontsize=6.5, color=ink)
            else:
                ax.set_visible(False)
            ax.axvline(0, color=ink, lw=0.6)
        fig.supxlabel("seconds from annotated onset (shaded: annotated seizure)", color=ink)
        fig.supylabel("channel-mean log ratio to baseline median", color=ink)
        fig.suptitle(
            f"Siena, {title}, onset-locked (orange title = no rise, z < 2; dotted = baseline mean + 2 SD)",
            color=ink,
        )
        fig.tight_layout(rect=(0.02, 0.02, 1, 0.97))
        fig.savefig(OUT / f"fig_onset_locked_{f}.png", dpi=130)
        plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(13, 3.6), sharey=True)
    x = np.arange(n)
    for ax, f, title in zip(axes, ("ll", "pw"), ("line length", "1-30 Hz power"), strict=True):
        z = np.array([s["z"] for s in stats[f]])
        ax.bar(x, np.clip(z, -5, None), color=[c1 if v >= 2 else c2 for v in z], width=0.8)
        ax.axhline(2, color=ink, lw=0.8, ls="--")
        ax.set_xticks(x, [f"{s}#{k}" for s, k in zip(on["stem"], on["k"], strict=True)], rotation=90, fontsize=5.5)
        ax.set_title(f"{title}: z per seizure (rise iff z >= 2; {int((z < 2).sum())} without)", color=ink)
    axes[0].set_ylabel("z (ictal vs baseline)")
    fig.tight_layout()
    fig.savefig(OUT / "fig_rise_z.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 3.4))
    lab = [f"{r['stem']}#{r['k']}" for r in sd]
    x = np.arange(len(sd))
    ax.scatter(x - 0.15, [r["d_on"] for r in sd], s=16, color=c1, label="onset: epilepsy2bids - ours")
    ax.scatter(
        x + 0.15, [r["d_off"] for r in sd], s=16, color=c2, marker="^", label="offset: epilepsy2bids - ours"
    )
    for i, r in enumerate(sd):
        if not r["explained"]:
            ax.annotate("unexplained", (i, max(r["d_on"], r["d_off"])), fontsize=6, color=ink)
    ax.axhspan(-WINDOW_S, WINDOW_S, color=c3, alpha=0.12, lw=0, label="within 1 window (10 s)")
    ax.set_yscale("symlog", linthresh=10)
    ax.set_xticks(x, lab, rotation=90, fontsize=5.5)
    ax.set_ylabel("difference (s)")
    ax.legend(loc="upper left", fontsize=6.5)
    ax.set_title("Siena annotation cross-check, per seizure", color=ink)
    fig.tight_layout()
    fig.savefig(OUT / "fig_annotation_diff.png", dpi=150)
    plt.close(fig)

    import handcrafted_baseline as hb  # noqa: PLC0415
    from sklearn.metrics import roc_curve  # noqa: PLC0415

    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6))
    pal = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4")
    for ax, s in zip(axes, hb.SETTINGS, strict=True):
        for k, r in enumerate(hb.ROTS):
            a = np.load(hb.OUT / "fit" / f"{s}-{r}-overlap.npz")
            fpr, tpr, _ = roc_curve(a["y_test"], a["ll_test"])
            ax.plot(
                fpr,
                tpr,
                color=pal[k],
                lw=1.5,
                label=f"{r} ({100 * fits[s][k]['line_length_zero_param']['test']['roc_auc']:.1f})",
            )
        ax.plot([0, 1], [0, 1], color=muted, lw=0.8, ls=":")
        ax.set_title(f"{s}: zero-parameter line length", color=ink)
        ax.set_xlabel("false positive rate")
        ax.legend(loc="lower right", fontsize=6.5)
    axes[0].set_ylabel("true positive rate")
    fig.tight_layout()
    fig.savefig(OUT / "fig_line_length_roc.png", dpi=150)
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("diff")
    a.add_argument("--siena-root", default="~/dxdata/siena/1.0.0")
    a.add_argument("--chbmit-root", default="~/dxdata/chbmit/1.0.0")
    a.add_argument("--out", required=True)
    o = sub.add_parser("onset")
    o.add_argument("--siena-root", default="~/dxdata/siena/1.0.0")
    o.add_argument("--out", required=True)
    o.add_argument("--workers", type=int, default=24)
    sub.add_parser("report")
    args = ap.parse_args()
    {"diff": diff, "onset": onset, "report": report}[args.cmd](args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
