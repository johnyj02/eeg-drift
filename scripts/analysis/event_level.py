#!/usr/bin/env python3
"""E12 (D25): event-level seizure detection from the saved per-window test scores. CPU only.

    .venv/bin/python scripts/analysis/event_level.py --selftest   # fast sweep == brute force
    .venv/bin/python scripts/analysis/event_level.py [--jobs 12]  # writes artifacts/analysis/event/
    <venv with timescoring> scripts/analysis/event_level.py --xcheck   # vs timescoring (MIT), optional

Design: notes/completeness-audit.md E12, adopted by notes/decisions.md D25. Data: D24-A (S1E+S1M,
S3E+S3M, S3FE+S3FM; linear head; 5 rotations x 3 seeds), P1E (paper split, 5 seeds, both heads) and
wave 1 (paper split, run_tag None, probe v2, 5 seeds, both heads). Scores: `scores_best` (the
val-selected epoch, = test_at_best), grid windows only (oversampled `add` test windows dropped).

Scoring (SzCORE / timescoring EventScoring semantics, re-implemented here, nothing vendored):
- per recording (EDF), windows on the 10 s grid; score smoothed by a CAUSAL moving average of the
  last k windows (k in 1, 3, 5; shorter at the start of a recording); alarm = smoothed >= threshold;
- reference = true [onset, offset) from configs/<dataset>_seizures.json; both reference and alarm
  events: merged if < 90 s apart, then split into 5 min pieces; reference extended 30 s before /
  60 s after (clipped to the scored recording);
- TP = reference piece overlapped by any alarm (any overlap); FP = alarm piece overlapping no
  extended reference; sensitivity = TP / reference pieces; FA/h = FP / scored test hours, pooled
  over the fold's test subjects (one global threshold, like the pooled window ROC);
- curve: every distinct threshold. Sensitivity at f FA/h = max sensitivity over thresholds with
  FA/h <= f (step envelope; FP is not monotone in the threshold). pAUC = integral of that envelope
  over [0, 2] FA/h divided by 2 (1 = every seizure found at 0 FA/h). Thresholds that cannot reach
  FA/h <= 2 (or <= 1 on the other subjects, below) are skipped by a proven bound (`sweep`);
- non-oracle threshold, leave one test subject out inside the fold: for subject s, the threshold
  with the highest sensitivity on the fold's OTHER test subjects at FA/h <= 1 (ties: the higher
  threshold), applied to s; TP/FP summed over s;
- latency, at those thresholds, per detected seizure (merged, before splitting): end of the first
  raw alarm window overlapping [onset - 30 s, offset + 60 s) minus onset (a causal detector can
  only alarm when its window ends).
Reading rule (D25-E12): the D18 paired rule on pAUC with margin 0.05: mean difference > +0.05 and
> 0 in >= 4/5 units -> first term wins; < -0.05 and < 0 in >= 4/5 -> second term wins; else no
difference shown. Units: rotations (seed means) for D24-A; seeds for P1E and wave 1 (as D24-B).
The rule is applied at each k (D25 does not name one k). Everything else is descriptive.
"""

from __future__ import annotations

import argparse
import functools
import json
import math
import sys
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from read_step1 import paired  # noqa: E402

OUT = ROOT / "artifacts" / "analysis" / "event"
RES = ROOT / "artifacts" / "s3-results"
FS = {"chbmit": 256, "siena": 512}   # sample rate of the window keys and the seizure tables
WIN, MERGE, PRE, POST, MAXLEN = 10, 90, 30, 60, 300   # s
GAP_W = MERGE // WIN      # windows i < j are merged iff j - i <= 9 (gap 10 * (j - i - 1) < 90 s)
CH = MAXLEN // WIN        # 30 windows per 5 min piece
SEP = 40                  # empty grid slots between recordings (> GAP_W and > CH: nothing crosses)
KS = (1, 3, 5)
FA_AT = (0.5, 1.0, 2.0)
PAUC_MAX, LOSO_FA, MARGIN = 2.0, 1.0, 0.05
FA_GRID = np.round(np.arange(0, PAUC_MAX + 1e-9, 0.02), 2)
ROTS = tuple(f"rot{i}" for i in range(5))
ARMS = ("lp", "last", "lp_randinit", "last_randinit")
CONTRASTS = (("last", "lp"), ("lp", "lp_randinit"), ("last_randinit", "last"))
NAMES = {("last", "lp"): ("SA helps", "SA hurts"),
         ("lp", "lp_randinit"): ("pretrained features beat random", "random features win"),
         ("last_randinit", "last"): ("random init wins", "pretrained wins")}
# set -> (dataset, run tags, unit); D24-A sets are linear-only, P1E / W1 have both heads
SETS = {"A-chbmit": ("chbmit", {"S1E", "S1M"}, "rotation"),
        "A-siena": ("siena", {"S3E", "S3M"}, "rotation"),
        "A-siena_filt": ("siena", {"S3FE", "S3FM"}, "rotation"),
        "P1E": ("chbmit", {"P1E"}, "seed"),
        "W1": ("chbmit", {None}, "seed")}
assert MERGE % WIN == 0 and MAXLEN % WIN == 0 and SEP > max(GAP_W, CH)


@functools.cache
def seizure_table(dataset: str) -> dict:
    return json.loads((ROOT / "configs" / f"{dataset}_seizures.json").read_text())


def ref_events(sz: list[tuple[float, float]], dur: float) -> tuple[list, list, int]:
    """Seconds -> (merged seizures, 5 min pieces, n dropped as outside the scored [0, dur))."""
    merged: list = []
    for on, off in sorted(sz):
        if merged and on - merged[-1][1] < MERGE:
            merged[-1][1] = max(merged[-1][1], off)
        else:
            merged.append([on, off])
    kept = [(on, min(off, dur)) for on, off in merged if on < dur]
    pieces = []
    for on, off in kept:
        a = on
        while off - a > MAXLEN:
            pieces.append((a, a + MAXLEN))
            a += MAXLEN
        pieces.append((a, off))
    return kept, pieces, len(merged) - len(kept)


def wrange(a: float, b: float, n: int) -> tuple[int, int]:
    """Grid windows [10w, 10w + 10) overlapping [a, b) seconds, clipped to [0, n)."""
    return max(0, math.floor(a / WIN)), min(n, math.ceil(b / WIN))


@functools.cache
def timeline(index_path: str, dataset: str) -> dict:
    """Test grid windows of one test index on a global grid (recordings SEP slots apart)."""
    files: dict = defaultdict(list)
    for i, r in enumerate(json.loads(Path(index_path).read_text())):
        if "-grid-" in r["key"]:
            stem, start = r["key"].rsplit("-grid-", 1)
            files[stem].append((int(start), i, r["subject"]))
    return build(files, seizure_table(dataset), FS[dataset], index_path)


def build(files: dict, table: dict, fs: int, name: str = "") -> dict:
    """stem -> [(start sample, score index, subject)] + seizure table -> the scoring layout."""
    subjects = sorted({s for v in files.values() for _, _, s in v})
    sid = {s: j for j, s in enumerate(subjects)}
    idx, g, first, gsubj, lab, recs = [], [], [], [], [], {}
    ref, sz, dropped, off = [], [], 0, 0
    for stem in sorted(files):
        rows = sorted(files[stem])
        n = len(rows)
        if [s for s, _, _ in rows] != [w * fs * WIN for w in range(n)]:
            raise SystemExit(f"{name}: {stem} grid windows are not contiguous from 0")
        (s,) = {sid[x] for _, _, x in rows}
        raw = [(a / fs, b / fs) for a, b in table.get(stem, [])]
        merged, pieces, d = ref_events(raw, n * WIN)
        dropped += d
        y = np.zeros(n, np.int8)
        for a, b in raw:
            w0, w1 = wrange(a, b, n)
            y[w0:w1] = 1
        for a, b in merged:
            w0, w1 = wrange(a - PRE, b + POST, n)
            sz.append((off + w0, off + w1, s, a, off, stem))
        for a, b in pieces:
            w0, w1 = wrange(a - PRE, b + POST, n)
            ref.append((off + w0, off + w1, s))
        recs[stem] = (off, n, s)
        first += [len(idx)] * n
        idx += [i for _, i, _ in rows]
        g += range(off, off + n)
        gsubj += [s] * n + [-1] * SEP
        lab.append(y)
        off += n + SEP
    G, ns = off, len(subjects)
    gsubj = np.array(gsubj)
    ov = np.zeros(G, np.int64)
    near = np.zeros(G, bool)
    for r0, r1, _ in ref:
        ov[r0:r1] = 1
        near[max(0, r0 - CH):r1 + CH] = True   # any 5 min piece touching [r0, r1) lies in here
    r = np.array(ref, dtype=np.int64).reshape(-1, 3)
    n_win = np.bincount(gsubj[gsubj >= 0], minlength=ns)
    return {"idx": np.array(idx), "g": np.array(g), "first": np.array(first), "G": G,
            "gsubj": gsubj, "subjects": subjects, "ovc": np.r_[0, np.cumsum(ov)],
            "r0": r[:, 0], "r1": r[:, 1], "rs": r[:, 2], "sz": sz, "recs": recs,
            "hours": n_win * WIN / 3600, "n_ref": np.bincount(r[:, 2], minlength=ns),
            "near": np.bincount(gsubj[near & (gsubj >= 0)], minlength=ns),
            "lab": np.concatenate(lab), "dropped": dropped}


def smooth(x: np.ndarray, first: np.ndarray, k: int) -> np.ndarray:
    """Causal moving average of the last k windows inside each recording."""
    if k == 1:
        return x.astype(np.float64)
    c = np.r_[0.0, np.cumsum(x, dtype=np.float64)]
    j = np.arange(len(x))
    lo = np.maximum(first, j - k + 1)
    return (c[j + 1] - c[lo]) / (j + 1 - lo)


def events(pos: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Sorted alarm slots -> merged events [S, E) on the global grid."""
    cut = np.flatnonzero(np.diff(pos) > GAP_W)
    return pos[np.r_[0, cut + 1]], pos[np.r_[cut, len(pos) - 1]] + 1


def sweep(sm: np.ndarray, tl: dict) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """TP and FP per subject at every distinct threshold (row 0: no alarm, threshold +inf).

    Stops at the first threshold from which on FA/h > PAUC_MAX overall and > LOSO_FA on every
    leave-one-out subject set, so the envelope up to PAUC_MAX and every LOSO choice are exact.
    Bound: an alarm window more than CH slots from every extended reference sits in an FP piece,
    and a piece holds <= CH windows, so FP >= (P - near) / CH for P alarm windows."""
    grid = np.full(tl["G"], -np.inf)
    grid[tl["g"]] = sm
    thr = np.unique(sm)[::-1]
    ns, H, D = len(tl["subjects"]), tl["hours"], tl["near"]
    subj = tl["gsubj"][tl["g"]]
    P = len(sm) - np.searchsorted(np.sort(sm), thr, "left")
    stop = P > CH * PAUC_MAX * H.sum() + D.sum()
    for s in range(ns):
        Ps = (subj == s).sum() - np.searchsorted(np.sort(sm[subj == s]), thr, "left")
        stop &= P - Ps > CH * LOSO_FA * (H.sum() - H[s]) + D.sum() - D[s]
    m = int(np.argmax(stop)) + 1 if stop.any() else len(thr)
    thr = thr[:m]
    TP, FP = np.zeros((m + 1, ns), np.int64), np.zeros((m + 1, ns), np.int64)
    r0, r1, rs, ovc, gsubj = tl["r0"], tl["r1"], tl["rs"], tl["ovc"], tl["gsubj"]
    for i, t in enumerate(thr, 1):
        S, E = events(np.flatnonzero(grid >= t))
        n = -(-(E - S) // CH)
        cs = np.repeat(S, n) + CH * (np.arange(n.sum()) - np.repeat(np.cumsum(n) - n, n))
        ce = np.minimum(cs + CH, np.repeat(E, n))
        FP[i] = np.bincount(gsubj[cs[ovc[ce] == ovc[cs]]], minlength=ns)
        j = np.minimum(np.searchsorted(E, r0, "right"), len(E) - 1)
        TP[i] = np.bincount(rs[(E[j] > r0) & (S[j] < r1)], minlength=ns)
    return np.r_[np.inf, thr], TP, FP, grid


def summarise(thr, TP, FP, grid, tl) -> dict:
    H, R = tl["hours"].sum(), tl["n_ref"].sum()
    fa, se = FP.sum(1) / H, TP.sum(1) / max(R, 1)
    o = np.argsort(fa, kind="stable")
    fa_s, env = fa[o], np.maximum.accumulate(se[o])

    def at(f: float) -> float:
        return float(env[np.searchsorted(fa_s, f + 1e-12, "right") - 1])

    u = fa_s <= PAUC_MAX + 1e-12
    pauc = float(np.sum(env[u] * np.diff(np.r_[fa_s[u], PAUC_MAX])) / PAUC_MAX)
    # leave one test subject out: pick on the others, apply to s
    sel, ns = [], len(tl["subjects"])
    for s in range(ns):
        Ho, Ro = H - tl["hours"][s], R - tl["n_ref"][s]
        ok = (FP.sum(1) - FP[:, s]) <= LOSO_FA * Ho + 1e-9
        sens_o = (TP.sum(1) - TP[:, s]) / Ro if Ro else np.zeros(len(thr))
        sel.append(int(np.argmax(np.where(ok, sens_o, -1.0))))
    tp = sum(int(TP[i, s]) for s, i in enumerate(sel))
    fp = sum(int(FP[i, s]) for s, i in enumerate(sel))
    lat = []
    for s, i in enumerate(sel):
        if i == 0:
            continue
        pos = np.flatnonzero(grid >= thr[i])
        for z0, z1, zs, onset, g0, _ in tl["sz"]:
            p = np.searchsorted(pos, z0)
            if zs == s and p < len(pos) and pos[p] < z1:
                lat.append(float((pos[p] - g0 + 1) * WIN - onset))
    prec = tp / (tp + fp) if tp + fp else float("nan")
    sens = tp / max(R, 1)
    return {"pauc": pauc, **{f"sens@{f}": at(f) for f in FA_AT},
            "loso_sens": sens, "loso_fa": fp / H, "loso_prec": prec,
            "loso_f1": 2 * tp / (2 * tp + fp + (R - tp)) if R + fp else float("nan"),
            "loso_thr": {tl["subjects"][s]: float(thr[i]) for s, i in enumerate(sel)},
            "latency_median": float(np.median(lat)) if lat else float("nan"), "latencies": lat,
            "n_seizures": len(tl["sz"]), "n_ref": int(R), "hours": float(H), "n_thr": len(thr) - 1,
            "env": [at(f) for f in FA_GRID]}


def score_run(job: dict) -> dict:
    tl = timeline(job["index"], job["dataset"])
    z = np.load(job["npz"])
    if len(z["scores_best"]) != job["n_index"]:
        raise SystemExit(f"{job['npz']}: {len(z['scores_best'])} scores, index has {job['n_index']}")
    if job["labels"] == "overlap" and not np.array_equal(z["y_test"][tl["idx"]], tl["lab"]):
        raise SystemExit(f"{job['npz']}: saved labels disagree with the seizure table timeline")
    raw = z["scores_best"][tl["idx"]]
    out = {}
    for k in KS:
        thr, TP, FP, grid = sweep(smooth(raw, tl["first"], k), tl)
        out[k] = summarise(thr, TP, FP, grid, tl)
    return {**{key: job[key] for key in ("set", "model", "arm", "unit", "seed", "probe", "roc", "npz")},
            "dropped": tl["dropped"], "by_k": out}


def list_jobs() -> list[dict]:
    jobs, seen = [], set()
    for p in sorted(RES.rglob("results/*.json")):
        if p.name.startswith(("diag-", "test-index-", "val-index-", "report-")):
            continue
        r = json.loads(p.read_text())
        if r.get("smoke") or r["arm"] not in ARMS:
            continue
        for name, (dataset, tags, unit) in SETS.items():
            if r["dataset"] != dataset or r.get("run_tag") not in tags:
                continue
            if name == "W1":
                if r["versions"]["probe"] != 2 or r["split"] != "paper" or r["arm"] == "lp_randinit":
                    continue
            elif r["versions"]["probe"] != 4 or any(v["spec"].get("backbone_mode") != "eval"
                                                    for v in r["probes"].values()):
                raise SystemExit(f"{p.name}: not a probe-v4 eval-mode record")
            if (unit == "rotation") != (r["split"] in ROTS):
                raise SystemExit(f"{p.name}: split {r['split']} in set {name}")
            index = p.parent / r["test_index"]
            n_index = len(json.loads(index.read_text()))
            for probe, res in r["probes"].items():
                cell = (name, r["model"], r["arm"], r["split"], r["seed"], probe)
                if cell in seen:
                    raise SystemExit(f"two records for {cell}")
                seen.add(cell)
                jobs.append({"set": name, "dataset": dataset, "model": r["model"], "arm": r["arm"],
                             "unit": r["split"] if unit == "rotation" else r["seed"], "seed": r["seed"],
                             "probe": probe, "labels": r.get("labels"), "index": str(index),
                             "n_index": n_index, "npz": str(p.with_suffix(f".{probe}.npz")),
                             "roc": 100 * res["test_at_best"]["roc_auc"]})
    return jobs


# ---------------------------------------------------------------------------------------------
# aggregation, tables, figures

METRICS = ("pauc", "sens@0.5", "sens@1.0", "sens@2.0", "loso_sens", "loso_fa", "loso_f1",
           "latency_median")


def unit_means(runs: list[dict], metric: str, k: int) -> dict:
    """(set, model, probe, arm) -> {unit: mean over that unit's seeds}."""
    acc: dict = defaultdict(lambda: defaultdict(list))
    for r in runs:
        v = r["roc"] if metric == "roc" else r["by_k"][k][metric]
        acc[(r["set"], r["model"], r["probe"], r["arm"])][r["unit"]].append(v)
    mean = lambda v: float(np.mean(v)) if v else float("nan")  # noqa: E731
    return {c: {u: mean([x for x in v if x == x]) for u, v in d.items()} for c, d in acc.items()}


def fmt(v: list[float], nd: int = 3) -> str:
    v = np.asarray(v, float)
    v = v[~np.isnan(v)]
    if not len(v):
        return "n/a"
    sem = v.std(ddof=1) / np.sqrt(len(v)) if len(v) > 1 else float("nan")
    return f"{v.mean():.{nd}f} ± {sem:.{nd}f}"


def tables(runs: list[dict]) -> dict:
    cells = sorted({(r["set"], r["model"], r["probe"]) for r in runs},
                   key=lambda c: (list(SETS).index(c[0]),) + c[1:])
    means = {(m, k): unit_means(runs, m, k) for m in (*METRICS, "roc") for k in KS}
    arm_lines = ["# E12 event-level metrics per arm (descriptive)", "",
                 "Mean ± SEM over units (D24-A: 5 rotations, each the mean of its 3 seeds; P1E / W1: 5 "
                 "seeds). pAUC normalised to [0, 1] over 0-2 FA/h. LOSO = leave-one-test-subject-out "
                 "threshold at <= 1 FA/h on the other subjects. Latency in s (median per run, then mean "
                 "over units). Window ROC x100 for orientation.", "",
                 "| set | model | head | arm | k | pAUC | sens@0.5 | sens@1 | sens@2 | LOSO sens | LOSO FA/h "
                 "| LOSO F1 | latency s | window ROC |", "|" + "---|" * 14]
    con_lines = ["# E12 paired contrasts on event-level pAUC (D25-E12 rule)", "",
                 f"Rule: D18 paired rule on pAUC (0-{PAUC_MAX:g} FA/h, normalised), margin {MARGIN}. Units: "
                 "rotations (3-seed means) for D24-A, seeds for P1E / W1 (pairing as D24-B). The rule is "
                 "applied at each smoothing k; D25 names no single k. `alt` = the same rule if the margin "
                 "were meant on the un-normalised [0, 2] pAUC scale (0.025 normalised): a sensitivity "
                 "check, not a verdict. Other columns are descriptive.", "",
                 "| set | model | head | contrast | k | mean ΔpAUC | per unit | verdict | alt | Δsens@1 | "
                 "ΔLOSO sens | Δwindow ROC (D24 rule) |", "|" + "---|" * 12]
    verdicts = []
    for st, model, probe in cells:
        for arm in ARMS:
            for k in KS:
                row = [means[(m, k)].get((st, model, probe, arm)) for m in (*METRICS, "roc")]
                if row[0] is None:
                    continue
                vals = [fmt(list(d.values()), 1 if m in ("latency_median", "roc") else 3)
                        for m, d in zip((*METRICS, "roc"), row, strict=True)]
                arm_lines.append(f"| {st} | {model} | {probe} | {arm} | {k} | " + " | ".join(vals) + " |")
        for a, b in CONTRASTS:
            for k in KS:
                A, B = (means[("pauc", k)].get((st, model, probe, x)) for x in (a, b))
                if not A or not B:
                    continue
                units = sorted(set(A) & set(B), key=str)
                if len(units) != 5:
                    raise SystemExit(f"{st} {model} {probe} {a}-{b}: {len(units)} paired units")

                def diff(metric: str, k=k, c=(st, model, probe), ab=(a, b), units=units) -> list[float]:
                    X, Y = (means[(metric, k)][(*c, x)] for x in ab)
                    return [X[u] - Y[u] for u in units]

                d = diff("pauc")
                v, alt = paired(d, MARGIN), paired(d, MARGIN / 2)
                named = {"first term wins": NAMES[(a, b)][0], "second term wins": NAMES[(a, b)][1]}
                droc = diff("roc")
                verdicts.append({"set": st, "model": model, "probe": probe, "contrast": f"{a} - {b}",
                                 "k": k, "mean": float(np.mean(d)), "per_unit": d, "verdict": v,
                                 "verdict_name": named.get(v, v), "alt_verdict": alt,
                                 "d_sens@1": float(np.mean(diff("sens@1.0"))),
                                 "d_loso_sens": float(np.mean(diff("loso_sens"))),
                                 "d_roc": float(np.mean(droc)), "roc_verdict": paired(droc, 3.0)})
                con_lines.append(
                    f"| {st} | {model} | {probe} | {a} - {b} | {k} | {np.mean(d):+.3f} | "
                    f"{', '.join(f'{x:+.3f}' for x in d)} | **{named.get(v, v)}** | {named.get(alt, alt)} | "
                    f"{np.mean(diff('sens@1.0')):+.3f} | {np.mean(diff('loso_sens')):+.3f} | "
                    f"{np.mean(droc):+.1f} ({paired(droc, 3.0)}) |")
    n = defaultdict(set)
    for r in runs:
        n[r["set"]].add((r["by_k"][1]["n_seizures"], r["by_k"][1]["n_ref"], round(r["by_k"][1]["hours"], 1),
                         r["dropped"], r["unit"] if r["set"].startswith("A-") else "paper"))
    foot = ["", "## Test folds (merged seizures, 5 min reference pieces, scored hours, seizures outside "
            "the scored grid)", ""]
    foot += [f"- {s}: " + "; ".join(f"{u}: {a} seizures, {b} pieces, {h} h, {d} dropped"
                                     for a, b, h, d, u in sorted(v, key=lambda x: str(x[4])))
             for s, v in n.items()]
    (OUT / "event-arms.md").write_text("\n".join(arm_lines) + "\n")
    (OUT / "event-contrasts.md").write_text("\n".join(con_lines + foot) + "\n")
    return {"verdicts": verdicts, "means": {f"{m}|k{k}|{'|'.join(map(str, c))}": d
                                            for (m, k), cd in means.items() for c, d in cd.items()}}


COLORS = {"lp": "#2a78d6", "last": "#eb6834", "lp_randinit": "#1baf7a", "last_randinit": "#eda100"}
STYLE = {"lp": "-", "last": "-", "lp_randinit": "--", "last_randinit": "--"}
INK, MUTED, GRIDC = "#0b0b0b", "#52514e", "#e4e3df"


def _axes(ax) -> None:
    ax.grid(True, color=GRIDC, lw=0.6)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=8)


def _save(fig, name: str, top: float = 0.5) -> str:
    """Lay out below `top` inches reserved for the suptitle (and legend), write, close."""
    import matplotlib.pyplot as plt  # noqa: PLC0415

    fig.tight_layout(rect=(0, 0, 1, 1 - top / fig.get_figheight()))
    fig.savefig(OUT / name, dpi=130)
    plt.close(fig)
    return name


def figures(runs: list[dict], jobs: list[dict]) -> list[str]:
    import matplotlib  # noqa: PLC0415

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt  # noqa: PLC0415

    made = []
    groups = sorted({(r["set"], r["probe"]) for r in runs}, key=lambda c: (list(SETS).index(c[0]), c[1]))
    # 1. sensitivity vs FA/h envelopes, mean over all runs of a cell
    for st, probe in groups:
        fig, axs = plt.subplots(2, 3, figsize=(12, 7), sharex=True, sharey=True)
        for i, model in enumerate(("biot", "cbramod")):
            for j, k in enumerate(KS):
                ax = axs[i, j]
                _axes(ax)
                for arm in ARMS:
                    env = [r["by_k"][k]["env"] for r in runs if (r["set"], r["probe"], r["model"], r["arm"])
                           == (st, probe, model, arm)]
                    if env:
                        ax.step(FA_GRID, np.mean(env, 0), where="post", color=COLORS[arm], ls=STYLE[arm],
                                lw=2, label=f"{arm} (n={len(env)})")
                ax.set_title(f"{model}, k={k}", fontsize=10, color=INK)
                ax.set_ylim(0, 1)
                if i == 1:
                    ax.set_xlabel("false alarms per hour", color=MUTED)
                if j == 0:
                    ax.set_ylabel("event sensitivity", color=MUTED)
        fig.suptitle(f"E12 {st} ({probe} head): sensitivity at <= x FA/h, mean over runs", color=INK)
        fig.legend(*axs[0, 0].get_legend_handles_labels(), loc="upper center", ncol=4, frameon=False,
                   fontsize=8, bbox_to_anchor=(0.5, 1 - 0.4 / fig.get_figheight()))
        made.append(_save(fig, f"curves-{st}-{probe}.png", 0.6))
    # 2. paired pAUC differences per unit
    means = unit_means(runs, "pauc", 1), unit_means(runs, "pauc", 3), unit_means(runs, "pauc", 5)
    for tag, rows in (("A", [g for g in groups if g[0].startswith("A-")]),
                      ("paper", [g for g in groups if not g[0].startswith("A-")])):
        fig, axs = plt.subplots(len(rows), 6, figsize=(16, 2.6 * len(rows) + 0.6), sharey="row", squeeze=False)
        for i, (st, probe) in enumerate(rows):
            for j, (model, (a, b)) in enumerate((m, c) for m in ("biot", "cbramod") for c in CONTRASTS):
                ax = axs[i, j]
                _axes(ax)
                ax.axhline(0, color=MUTED, lw=1)
                for y in (MARGIN, -MARGIN):
                    ax.axhline(y, color=MUTED, lw=1, ls=":")
                for x, mk in enumerate(means):
                    A, B = mk.get((st, model, probe, a)), mk.get((st, model, probe, b))
                    if not A or not B:
                        continue
                    d = [A[u] - B[u] for u in sorted(set(A) & set(B), key=str)]
                    ax.scatter(x + np.linspace(-0.15, 0.15, len(d)), d, s=14, color=COLORS[a], alpha=0.7, lw=0)
                    ax.plot([x - 0.25, x + 0.25], [np.mean(d)] * 2, color=INK, lw=2)
                ax.set_xticks(range(3), [f"k={k}" for k in KS])
                ax.set_xlim(-0.5, 2.5)
                if i == 0:
                    ax.set_title(f"{model}: {a} - {b}", fontsize=9, color=INK)
                if j == 0:
                    ax.set_ylabel(f"{st} {probe}\nΔ pAUC", fontsize=8, color=MUTED)
        fig.suptitle(f"E12 paired Δ pAUC (0-2 FA/h) per {'rotation' if tag == 'A' else 'seed'}; bar = mean; "
                     f"dotted = ±{MARGIN} margin", color=INK)
        made.append(_save(fig, f"pauc-contrasts-{tag}.png"))
    # 3. LOSO operating points and latencies
    fig, axs = plt.subplots(len(groups), 2, figsize=(9, 2.8 * len(groups)), squeeze=False)
    for i, (st, probe) in enumerate(groups):
        for j, model in enumerate(("biot", "cbramod")):
            ax = axs[i, j]
            _axes(ax)
            for arm in ARMS:
                for k, mk in zip(KS, ("o", "s", "^"), strict=True):
                    se = unit_means(runs, "loso_sens", k).get((st, model, probe, arm), {})
                    fa = unit_means(runs, "loso_fa", k).get((st, model, probe, arm), {})
                    if se:
                        ax.scatter([fa[u] for u in se], list(se.values()), marker=mk, s=18, color=COLORS[arm],
                                   alpha=0.75, lw=0, label=f"{arm} k={k}")
            ax.axvline(LOSO_FA, color=MUTED, lw=1, ls=":")
            ax.set_title(f"{st} {probe}, {model}", fontsize=9, color=INK)
            ax.set_ylim(-0.02, 1.02)
            ax.set_xlabel("held-out FA/h", fontsize=8, color=MUTED)
            ax.set_ylabel("held-out sensitivity", fontsize=8, color=MUTED)
    fig.suptitle("E12 non-oracle (leave-one-test-subject-out) operating points, one point per unit", color=INK)
    fig.legend(*axs[0, 0].get_legend_handles_labels(), loc="upper center", ncol=4, frameon=False,
               fontsize=7, bbox_to_anchor=(0.5, 1 - 0.55 / fig.get_figheight()))
    made.append(_save(fig, "loso-points.png", 1.3))
    fig, axs = plt.subplots(len(groups), 2, figsize=(10, 2.6 * len(groups)), squeeze=False, sharey=True)
    for i, (st, probe) in enumerate(groups):
        for j, model in enumerate(("biot", "cbramod")):
            ax = axs[i, j]
            _axes(ax)
            data, pos, cols = [], [], []
            for a_i, arm in enumerate(ARMS):
                for k_i, k in enumerate(KS):
                    lat = [x for r in runs
                           if (r["set"], r["probe"], r["model"], r["arm"]) == (st, probe, model, arm)
                           for x in r["by_k"][k]["latencies"]]
                    data.append(lat or [np.nan])
                    pos.append(a_i * 4 + k_i)
                    cols.append(COLORS[arm])
            bp = ax.boxplot(data, positions=pos, widths=0.7, showfliers=False, patch_artist=True)
            for patch, c in zip(bp["boxes"], cols, strict=True):
                patch.set(facecolor=c, alpha=0.6, edgecolor=MUTED)
            for med in bp["medians"]:
                med.set(color=INK)
            ax.set_xticks([a_i * 4 + 1 for a_i in range(len(ARMS))], ARMS, fontsize=7)
            ax.axhline(0, color=MUTED, lw=1)
            ax.set_title(f"{st} {probe}, {model} (boxes k=1,3,5 per arm)", fontsize=9, color=INK)
            if j == 0:
                ax.set_ylabel("latency, s", fontsize=8, color=MUTED)
    fig.suptitle("E12 detection latency at the LOSO threshold (all detected seizures, pooled over runs)",
                 color=INK)
    made.append(_save(fig, "latency.png"))
    # 4. example score traces with seizure shading (rotation rot0, seed 42, k = 3)
    k = 3
    byid = {(r["set"], r["model"], r["arm"], r["unit"], r["seed"], r["probe"]): r for r in runs}
    for st in ("A-chbmit", "A-siena"):
        for model in ("biot", "cbramod"):
            js = {j["arm"]: j for j in jobs
                  if (j["set"], j["model"], j["unit"], j["seed"], j["probe"]) == (st, model, "rot0", 42, "linear")}
            if len(js) != len(ARMS):
                continue
            tl = timeline(js["lp"]["index"], js["lp"]["dataset"])
            ex, seen_s = [], set()
            for z in sorted(tl["sz"], key=lambda z: z[5]):
                if z[2] not in seen_s:
                    seen_s.add(z[2])
                    ex.append(z)
            ex = ex[:3]
            fig, axs = plt.subplots(len(ARMS), len(ex), figsize=(5 * len(ex), 9), squeeze=False)
            for c, (_, _, zs, onset, g0, stem) in enumerate(ex):
                n = tl["recs"][stem][1]
                lo, hi = max(0, int(onset // WIN) - 120), min(n, int(onset // WIN) + 180)
                t = (np.arange(lo, hi) * WIN + WIN) / 60   # window end, minutes from recording start
                c0 = int(np.searchsorted(tl["g"], g0 + lo))
                compact = slice(c0, c0 + hi - lo)
                for rr, arm in enumerate(ARMS):
                    ax = axs[rr, c]
                    _axes(ax)
                    raw = np.load(js[arm]["npz"])["scores_best"][tl["idx"]].astype(np.float64)
                    sm = smooth(raw, tl["first"], k)
                    th = byid[(st, model, arm, "rot0", 42, "linear")]["by_k"][k]["loso_thr"][tl["subjects"][zs]]
                    for on, off in seizure_table(js[arm]["dataset"]).get(stem, []):
                        a, b = on / FS[js[arm]["dataset"]] / 60, off / FS[js[arm]["dataset"]] / 60
                        ax.axvspan(a - PRE / 60, b + POST / 60, color="#efefec", lw=0)
                        ax.axvspan(a, b, color="#c9c8c2", lw=0)
                    ax.plot(t, raw[compact], color=MUTED, lw=0.6, alpha=0.5)
                    ax.plot(t, sm[compact], color=COLORS[arm], lw=1.6)
                    if np.isfinite(th):
                        ax.axhline(th, color=INK, lw=1, ls="--")
                        al = t[sm[compact] >= th]
                        ax.plot(al, np.full(len(al), ax.get_ylim()[0]), "|", color=INK, ms=8)
                    ax.set_title(f"{stem} ({tl['subjects'][zs]}): {arm}", fontsize=9, color=INK)
                    if rr == len(ARMS) - 1:
                        ax.set_xlabel("minutes from recording start (window end)", fontsize=8, color=MUTED)
                    if c == 0:
                        ax.set_ylabel("probe logit", fontsize=8, color=MUTED)
            fig.suptitle(f"E12 example traces, {st} rot0 seed 42, {model}: raw (grey) and k={k} causal mean; "
                         "dark band seizure, light band tolerance; dashed = LOSO threshold; ticks = alarms",
                         fontsize=10, color=INK)
            made.append(_save(fig, f"traces-{st}-{model}.png"))
    return made


# ---------------------------------------------------------------------------------------------
# checks

def brute(files: list[tuple[np.ndarray, list, int]], t: float) -> tuple[np.ndarray, np.ndarray]:
    """Independent slow scorer in seconds: (scores, seizures s, subject) per recording -> TP, FP."""
    ns = max(s for _, _, s in files) + 1
    tp, fp = np.zeros(ns, int), np.zeros(ns, int)

    def merge_split(ev: list) -> list:
        out: list = []
        for a, b in ev:
            if out and a - out[-1][1] < MERGE:
                out[-1][1] = b
            else:
                out.append([a, b])
        res = []
        for a, b in out:
            while b - a > MAXLEN:
                res.append((a, a + MAXLEN))
                a += MAXLEN
            res.append((a, b))
        return res

    for x, sz, s in files:
        dur = len(x) * WIN
        hyp = merge_split([(WIN * w, WIN * w + WIN) for w in np.flatnonzero(x >= t)])
        ref = [(max(0, a - PRE), min(dur, b + POST)) for a, b in merge_split(sorted(sz))]
        hit = [any(a < d and b > c for a, b in hyp) for c, d in ref]
        tp[s] += sum(hit)
        fp[s] += sum(not any(a < d and b > c for (c, d), h in zip(ref, hit, strict=True) if h) for a, b in hyp)
    return tp, fp


def selftest() -> int:
    rng = np.random.default_rng(0)
    for trial in range(40):
        files, xs, table = {}, [], {}
        for f in range(int(rng.integers(2, 5))):
            n, sz, a = int(rng.integers(60, 400)), [], 0.0
            while True:
                a += float(rng.uniform(20, 1500))
                b = a + float(rng.choice([15, 45, 200, 299, 301, 420, 900]))
                if b >= n * WIN:
                    break
                sz.append((a, b))
                a = b
            x = rng.normal(size=n)
            for a, b in sz:
                x[int(a // WIN):int(b // WIN) + 1] += rng.uniform(0, 3)
            base = sum(len(v) for v in xs)
            files[f"r{f}"] = [(w * 256 * WIN, base + w, f"s{f % 2}") for w in range(n)]
            table[f"r{f}"] = [[a * 256, b * 256] for a, b in sz]
            xs.append((x, sz, f % 2))
        tl = build(files, table, 256)
        for k in KS:
            sm = smooth(np.concatenate([x for x, _, _ in xs]), tl["first"], k)
            x0 = xs[0][0]
            assert np.allclose(sm[:len(x0)], [x0[max(0, w - k + 1):w + 1].mean() for w in range(len(x0))])
            thr, TP, FP, grid = sweep(sm, tl)
            cuts = np.cumsum([0] + [len(x) for x, _, _ in xs])
            fk = [(sm[cuts[i]:cuts[i + 1]], sz, s) for i, (_, sz, s) in enumerate(xs)]
            for i in range(1, len(thr), max(1, len(thr) // 25)):
                btp, bfp = brute(fk, thr[i])
                assert np.array_equal(btp, TP[i]) and np.array_equal(bfp, FP[i]), (trial, k, i)
            # every skipped threshold: FA/h > PAUC_MAX overall and > LOSO_FA on each leave-one-out set
            H = tl["hours"]
            for t in np.unique(sm)[::-1][len(thr) - 1:][::5]:
                _, bfp = brute(fk, t)
                assert bfp.sum() / H.sum() > PAUC_MAX, (trial, k, t)
                assert all((bfp.sum() - bfp[s]) / (H.sum() - H[s]) > LOSO_FA for s in range(len(H)))
            summarise(thr, TP, FP, grid, tl)
    # hand-checked: seizure [600, 1200) s = 2 pieces, extended [570, 960) and [870, 1260).
    # 56 = [560, 570) misses 570 -> FP; 100-101 hit piece 2 only; 200 + 208 merge (70 s gap) -> 1 FP;
    # 220 (110 s later) -> FP; 300 -> FP; 320-351 = 320 s -> split into 2 FPs. TP 1, FP 6. Two
    # identical 11.1 h recordings (subjects a, b): the LOSO pick on the other one is threshold 1
    # (6 FP / 11.1 h <= 1 FA/h); latency = end of window 100 (1010 s) ... 1020 s - 600 s = 410 s.
    x = np.zeros(4000)
    x[[56, 100, 101, 200, 208, 220, 300, *range(320, 352)]] = 1.0
    files = {r: [(w * 256 * WIN, i * 4000 + w, r) for w in range(4000)] for i, r in enumerate("ab")}
    tl = build(files, {r: [[600 * 256, 1200 * 256]] for r in "ab"}, 256)
    thr, TP, FP, grid = sweep(np.r_[x, x], tl)
    assert (TP[1].tolist(), FP[1].tolist(), tl["n_ref"].tolist()) == ([1, 1], [6, 6], [2, 2]), (TP, FP)
    assert [v.tolist() for v in brute([(x, [(600.0, 1200.0)], 0)], 0.5)] == [[1], [6]]
    res = summarise(thr, TP, FP, grid, tl)
    assert res["latencies"] == [410.0, 410.0] and res["loso_sens"] == 0.5, res
    print("selftest ok: fast sweep == brute force (40 random timelines x 3 k), stop bound holds, "
          "hand case TP 1 / FP 6 / latency 410 s")
    return 0


def xcheck(jobs: list[dict]) -> int:
    """Cross-check TP / FP against timescoring.EventScoring (MIT licence, external, not vendored)."""
    from timescoring import scoring  # noqa: PLC0415
    from timescoring.annotations import Annotation  # noqa: PLC0415

    rng = np.random.default_rng(1)
    picks = [jobs[i] for i in rng.choice(len(jobs), 6, replace=False)]
    par = scoring.EventScoring.Parameters(toleranceStart=PRE, toleranceEnd=POST, minOverlap=0,
                                          maxEventDuration=MAXLEN, minDurationBetweenEvents=MERGE)
    for job in picks:
        tl = timeline(job["index"], job["dataset"])
        raw = np.load(job["npz"])["scores_best"][tl["idx"]]
        sm = smooth(raw, tl["first"], 3)
        thr, TP, FP, _ = sweep(sm, tl)
        fs = FS[job["dataset"]]
        for i in sorted(set(np.linspace(1, len(thr) - 1, 8).astype(int))):
            tp = fp = 0
            for stem, (g0, n, _s) in tl["recs"].items():
                c = np.flatnonzero((tl["g"] >= g0) & (tl["g"] < g0 + n))
                ref = Annotation([(a / fs, b / fs) for a, b in seizure_table(job["dataset"]).get(stem, [])],
                                 1, n * WIN)
                hyp = Annotation(np.repeat(sm[c] >= thr[i], WIN), 1)
                sc = scoring.EventScoring(ref, hyp, par)
                tp, fp = tp + sc.tp, fp + sc.fp
            assert (tp, fp) == (TP[i].sum(), FP[i].sum()), (job["npz"], i, tp, fp, TP[i].sum(), FP[i].sum())
        print(f"xcheck ok: {Path(job['npz']).name}, k=3, {len(thr) - 1} thresholds, 8 compared")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=12)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--xcheck", action="store_true")
    ap.add_argument("--figures-only", action="store_true", help="reuse artifacts/analysis/event/runs.json")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    jobs = list_jobs()
    if args.xcheck:
        return xcheck(jobs)
    OUT.mkdir(parents=True, exist_ok=True)
    count = defaultdict(int)
    for j in jobs:
        count[(j["set"], j["probe"])] += 1
    print("runs:", dict(count))
    if args.figures_only:
        runs = json.loads((OUT / "runs.json").read_text())
        for r in runs:
            r["by_k"] = {int(k): v for k, v in r["by_k"].items()}
    else:
        with Pool(args.jobs) as pool:
            runs = pool.map(score_run, jobs, chunksize=1)
        (OUT / "runs.json").write_text(json.dumps(runs))
    summary = tables(runs)
    (OUT / "event-summary.json").write_text(json.dumps(summary, indent=1))
    made = figures(runs, jobs)
    print((OUT / "event-contrasts.md").read_text())
    print("figures:", ", ".join(made))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
