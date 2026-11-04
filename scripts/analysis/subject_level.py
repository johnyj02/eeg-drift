#!/usr/bin/env python3
"""E11 (D25; post hoc): subject-level and test-set uncertainty for the D24 contrasts. CPU only.

    .venv/bin/python scripts/analysis/subject_level.py [--reps 10000]

Design: notes/completeness-audit.md E11, adopted by notes/decisions.md D25. Inputs: the records in
artifacts/s3-results/**/results/*.json, their <probe>.npz (y_test, scores_best = val-selected epoch)
and test-index-*.json (window key and subject). Outputs in artifacts/analysis/subject/.

A. D24-A rotations (CHB-MIT S1E+S1M, Siena S3E+S3M, Siena filtered S3FE+S3FM; linear head):
   per-subject ROC/AP per arm and seed; per-subject paired differences for last - lp,
   last_randinit - last, lp - lp_randinit and D17 (last_randinit - lp_randinit); Wilcoxon and exact
   sign-flip over subjects. statsmodels is NOT installed in .venv, so the mixed model
   diff ~ 1 + (1|rotation) is replaced by its permutation alternative: an exact rotation-block
   sign-flip (2^5 patterns) of the rotation means of the subject differences, with the t-interval
   over those 5 means (df 4). Macro-over-subjects next to the pooled-fold value. Two-stage
   bootstrap: subjects within each rotation (pooled ROC recomputed), then the 3 seeds; 10k reps.
B. Outlier folds: CHB-MIT rot3 and Siena-filtered rot1, BIOT last_randinit - last (+24.4, +37.1).
C. Paper split: P1E (D24-B) and the wave-1 runs of draft Table 4. chb23 vs chb24 separately, and a
   seizure-event cluster bootstrap under the upstream, dedup and fixed scorings (posthoc_test.py):
   positives clustered by seizure event, negatives by recording file, both resampled within
   patient; then the 5 seeds.
Reading rule (E11): post hoc. Equivalence = TOST at +/-3 ROC points: the 90% CI inside (-3, +3).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy import stats  # noqa: E402
from sklearn.metrics import auc, average_precision_score, precision_recall_curve, roc_auc_score  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "src")]
from bootstrap_d24 import cluster_ci  # noqa: E402
from read_d24 import CONTRASTS, ROTS  # noqa: E402

from eegdrift.data.chbmit import overlap_label  # noqa: E402

RES = ROOT / "artifacts" / "s3-results"
OUT = ROOT / "artifacts" / "analysis" / "subject"
ARMS = ("lp", "lp_randinit", "last", "last_randinit")
CON = tuple((a, b) for a, b, _ in CONTRASTS) + (("last_randinit", "lp_randinit"),)  # 3 D24 + D17
SETS = (("chbmit", ("S1E", "S1M"), "CHB-MIT"), ("siena", ("S3E", "S3M"), "Siena"),
        ("siena", ("S3FE", "S3FM"), "Siena filtered"))
OUTLIERS = (("CHB-MIT", "rot3"), ("Siena filtered", "rot1"))
SCORINGS = ("upstream", "dedup", "fixed")
WIN = 10 * 256
COLOR = {"lp": "#2a78d6", "lp_randinit": "#eb6834", "last": "#1baf7a", "last_randinit": "#eda100"}
C3 = ("#2a78d6", "#eb6834", "#1baf7a")   # first three categorical slots (all-pairs safe)
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#d9d8d4"
plt.rcParams.update({"font.size": 8, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
                     "savefig.dpi": 200, "axes.spines.top": False, "axes.spines.right": False})


def cname(a: str, b: str) -> str:
    return f"{a} - {b}"


# ---------------------------------------------------------------- loading ----------------------------------------
_INDEX: dict = {}


def index_arrays(path: Path) -> dict:
    """Window keys, subject, recording file, start sample and grid flag of one test index (cached by name)."""
    if path.name not in _INDEX:
        t = json.loads(path.read_text())
        parts = [x["key"].rsplit("-", 2) for x in t]
        _INDEX[path.name] = {"subj": np.array([x["subject"] for x in t]), "file": np.array([p[0] for p in parts]),
                             "grid": np.array([p[1] == "grid" for p in parts]),
                             "start": np.array([int(p[2]) for p in parts])}
    return _INDEX[path.name]


def load_runs(dataset: str, tags: set[str], split_prefix: str, arms: tuple, probe_version: int) -> list[dict]:
    """One dict per (record, probe head). Refuses duplicates, wrong versions and a pooled ROC != record."""
    runs, seen = [], set()
    for p in sorted(RES.rglob("results/*.json")):
        if p.name.startswith(("diag-", "test-index-", "report-")):
            continue
        r = json.loads(p.read_text())
        if (r.get("smoke") or r["dataset"] != dataset or r.get("run_tag", "") not in tags
                or not r["split"].startswith(split_prefix) or r["arm"] not in arms):
            continue
        if r["versions"]["probe"] != probe_version:
            raise SystemExit(f"{p.name}: probe version {r['versions']['probe']} != {probe_version}")
        idx = index_arrays(p.parent / r["test_index"])
        for probe, res in r["probes"].items():
            if probe_version == 4 and res["spec"].get("backbone_mode") != "eval":
                raise SystemExit(f"{p.name}: not an eval-mode record")
            cell = (r["model"], r["arm"], r["split"], probe, r["seed"])
            if cell in seen:
                raise SystemExit(f"two records for {cell}")
            seen.add(cell)
            z = np.load(p.parent / f"{p.name[:-5]}.{probe}.npz")
            y, s = z["y_test"].astype(int), z["scores_best"].astype(float)
            if len(y) != len(idx["subj"]):
                raise SystemExit(f"{p.name}: npz and test index lengths differ")
            if abs(roc_auc_score(y, s) - res["test_at_best"]["roc_auc"]) > 1e-9:
                raise SystemExit(f"{p.name} {probe}: npz ROC != record test_at_best")
            runs.append({"model": r["model"], "arm": r["arm"], "split": r["split"], "probe": probe,
                         "seed": r["seed"], "tag": r.get("run_tag", ""), "y": y, "s": s, "idx": idx,
                         "index": r["test_index"], "record": p.name})
    return runs


# ---------------------------------------------------------------- metrics ----------------------------------------
def roc_ap(y: np.ndarray, s: np.ndarray) -> tuple[float, float]:
    if 0 < y.sum() < len(y):
        return 100 * roc_auc_score(y, s), 100 * average_precision_score(y, s)
    return float("nan"), float("nan")


def pair_matrix(y, s, gpos, gneg, n_pos: int, n_neg: int):
    """C[a, b] = #(positive of group a scored above negative of group b) + 0.5 #ties; P, N group sizes.

    The pooled ROC of any resample that repeats group a u_a times and group b v_b times is
    u'Cv / ((u.P)(v.N)): exact, and the same as duplicating the windows."""
    pos = y == 1
    sp, gp = s[pos], gpos[pos]
    C = np.zeros((n_pos, n_neg))
    for b in range(n_neg):
        neg = np.sort(s[~pos & (gneg == b)])
        lo, hi = np.searchsorted(neg, sp, "left"), np.searchsorted(neg, sp, "right")
        C[:, b] = np.bincount(gp, weights=lo + 0.5 * (hi - lo), minlength=n_pos)
    P, N = np.bincount(gp, minlength=n_pos), np.bincount(gneg[~pos], minlength=n_neg)
    return C, P.astype(float), N.astype(float)


def wauc(C, P, N, U, V) -> np.ndarray:
    """Pooled ROC x100 for group multiplicities U (reps x positive groups) and V (reps x negative groups)."""
    with np.errstate(invalid="ignore", divide="ignore"):
        return 100 * np.einsum("ri,ij,rj->r", U, C, V) / ((U @ P) * (V @ N))


def pr_prep(y, s):
    order = np.argsort(-s, kind="stable")
    ss = s[order]
    return order, y[order].astype(float), np.r_[np.nonzero(np.diff(ss))[0], len(ss) - 1]


def wpr(prep, W) -> np.ndarray:
    """PR-AUC x100, trapezoid as sklearn auc(precision_recall_curve) (= the draft's Table 4 'PR'), for
    integer window weights W (reps x windows)."""
    order, ys, last = prep
    Ws = W[:, order]
    tp = np.cumsum(Ws * ys, axis=1)[:, last]
    al = np.cumsum(Ws, axis=1)[:, last]
    with np.errstate(invalid="ignore", divide="ignore"):
        prec = np.where(al > 0, tp / np.where(al > 0, al, 1), 1.0)   # leading zero-weight groups: start point
        rec = tp / tp[:, -1:]
    r = np.c_[np.zeros(len(W)), rec]
    p = np.c_[np.ones(len(W)), prec]
    return 100 * np.sum(np.diff(r, axis=1) * (p[:, 1:] + p[:, :-1]) / 2, axis=1)


def multinomial_draws(rng, groups: list[np.ndarray], n: int, reps: int) -> np.ndarray:
    """reps x n multiplicities: within each stratum (array of group ids), resample its groups with replacement."""
    U = np.zeros((reps, n))
    for g in groups:
        U[:, g] = rng.multinomial(len(g), np.full(len(g), 1 / len(g)), size=reps)
    return U


def signflip_p(d: np.ndarray) -> float:
    """Exact two-sided sign-flip p for mean(d) = 0 (all 2^n patterns, chunked)."""
    d = np.asarray(d, dtype=float)
    n, obs, hits = len(d), abs(d.sum()) - 1e-9, 0
    for lo in range(0, 2 ** n, 2 ** 16):
        k = np.arange(lo, min(lo + 2 ** 16, 2 ** n))[:, None]
        signs = 1 - 2 * ((k >> np.arange(n)) & 1)
        hits += int((np.abs(signs @ d) >= obs).sum())
    return hits / 2 ** n


def t_ci(v, level: float) -> tuple[float, float]:
    v = np.asarray(v, dtype=float)
    h = stats.t.ppf(0.5 + level / 2, len(v) - 1) * v.std(ddof=1) / np.sqrt(len(v))
    return v.mean() - h, v.mean() + h


def q(v, level: float) -> tuple[float, float]:
    v = np.asarray(v)[np.isfinite(v)]
    return float(np.quantile(v, 0.5 - level / 2)), float(np.quantile(v, 0.5 + level / 2))


def tost(ci90: tuple[float, float]) -> str:
    return "equivalent within +/-3" if -3 < ci90[0] and ci90[1] < 3 else "not shown equivalent"


def fmt_ci(ci) -> str:
    return f"[{ci[0]:+.1f}, {ci[1]:+.1f}]"


def self_check() -> None:
    """The exact resampling formulas must equal sklearn with integer sample weights (incl. 0 and ties)."""
    rng = np.random.default_rng(0)
    y = rng.integers(0, 2, 400)
    s = np.round(rng.normal(size=400) + y, 1)          # rounding forces ties
    g = rng.integers(0, 7, 400)
    C, P, N = pair_matrix(y, s, g, g, 7, 7)
    for _ in range(5):
        u = rng.integers(0, 3, 7).astype(float)
        u[0] = max(u[0], 1)
        w = u[g]
        assert abs(wauc(C, P, N, u[None], u[None])[0] - 100 * roc_auc_score(y, s, sample_weight=w)) < 1e-9
        pr, rc, _ = precision_recall_curve(y, s, sample_weight=w)
        assert abs(wpr(pr_prep(y, s), w[None])[0] - 100 * auc(rc, pr)) < 1e-9
    pr, rc, _ = precision_recall_curve(y, s)
    assert abs(wpr(pr_prep(y, s), np.ones((1, 400)))[0] - 100 * auc(rc, pr)) < 1e-9
    assert signflip_p(np.array([1.0, 2.0, 3.0])) == 0.25


# ---------------------------------------------------------------- A: rotations -----------------------------------
def rotation_analysis(rng, reps: int, rows_out: list, md: list, js: dict) -> dict:
    keep: dict = {}
    md += ["## A. D24-A rotations, linear head: per-subject differences and two-stage bootstrap", "",
           "Per-subject difference = mean over the rotation's 3 seeds of (ROC arm a - ROC arm b) within that "
           "subject. Pooled = the D24 estimand (per-rotation seed mean of the pooled-fold contrast, then mean "
           "over rotations). Wilcoxon and sign-flip: over subjects (independence across subjects assumed; "
           "subjects in one fold share a trained probe). Mixed-model alternative (statsmodels absent): exact "
           "rotation-block sign-flip on the 5 rotation means of the subject differences, and the t-interval "
           "over those means (df 4). Two-stage bootstrap: per rotation, resample its test subjects with "
           "replacement, recompute every run's pooled ROC, then resample the 3 seeds; mean over the 5 "
           f"rotations; {reps:,} reps. Rotation bootstrap = the D24-D algorithm (rotations, then seeds) rerun "
           "here for comparison. TOST +/-3 uses a 90% CI; it is read on two intervals because they answer "
           "different questions: the two-stage bootstrap holds the 5 trained folds fixed (test-set "
           "uncertainty of the D24 estimand), the t-interval over rotation means (the mixed-model "
           "alternative) also carries between-fold variation of the per-subject differences. The verdict "
           "column says which of them shows equivalence.", ""]
    for dataset, tags, label in SETS:
        runs = load_runs(dataset, set(tags), "rot", ARMS, 4)
        for model in ("biot", "cbramod"):
            R = [x for x in runs if x["model"] == model and x["probe"] == "linear"]
            per = {}   # rot -> dict
            for rot in ROTS:
                rr = [x for x in R if x["split"] == rot]
                subs = sorted(set(rr[0]["idx"]["subj"]))
                code = {s: i for i, s in enumerate(subs)}
                seeds = sorted({x["seed"] for x in rr})
                cell = {}
                for x in rr:
                    g = np.array([code[s] for s in x["idx"]["subj"]])
                    C, P, N = pair_matrix(x["y"], x["s"], g, g, len(subs), len(subs))
                    if (P == 0).any() or (N == 0).any():
                        raise SystemExit(f"{label} {rot}: a test subject lacks positives or negatives")
                    sub = {s: roc_ap(x["y"][g == i], x["s"][g == i]) for s, i in code.items()}
                    cell[(x["arm"], x["seed"])] = {"C": C, "P": P, "N": N, "sub": sub,
                                                   "pooled": wauc(C, P, N, np.ones((1, len(subs))),
                                                                  np.ones((1, len(subs))))[0],
                                                   "ap": 100 * average_precision_score(x["y"], x["s"])}
                    for s, i in code.items():
                        rows_out.append({"set": label, "tags": "+".join(tags), "model": model, "probe": "linear",
                                         "arm": x["arm"], "split": rot, "seed": x["seed"], "subject": s,
                                         "n": int((g == i).sum()), "n_pos": int(P[i]), "roc": sub[s][0],
                                         "ap": sub[s][1]})
                if sorted(cell) != sorted((a, sd) for a in ARMS for sd in seeds) or len(seeds) != 3:
                    raise SystemExit(f"{label} {model} {rot}: incomplete arms x 3 seeds")
                per[rot] = {"subs": subs, "seeds": seeds, "cell": cell}
            keep[(label, model)] = per
            # two-stage bootstrap: same subject and seed draws for every arm (paired)
            draws = {rot: (multinomial_draws(rng, [np.arange(len(per[rot]["subs"]))], len(per[rot]["subs"]), reps),
                           rng.integers(0, 3, (reps, 3))) for rot in ROTS}
            boot = {}
            for rot in ROTS:
                W, _ = draws[rot]
                boot[rot] = {k: wauc(v["C"], v["P"], v["N"], W, W) for k, v in per[rot]["cell"].items()}
            md += [f"### {label}, {model}", "",
                   "| contrast | pooled (D24) | two-stage 95% CI | two-stage 90% CI | TOST +/-3 (two-stage) "
                   "| rotation bootstrap 95% CI | macro over subjects (n) | subjects > 0 | Wilcoxon p "
                   "| sign-flip p | rotation-block flip p | t over rotation means 95% / 90% | TOST +/-3 (t) "
                   "| TOST +/-3 verdict |", "|---" * 14 + "|"]
            for a, b in CON:
                pooled_rot, stat = [], np.zeros(reps)
                d_sub, d_sub_seed, rot_of, names, seed_diffs = [], [], [], [], []
                for rot in ROTS:
                    pr = per[rot]
                    dseed = [pr["cell"][(a, sd)]["pooled"] - pr["cell"][(b, sd)]["pooled"] for sd in pr["seeds"]]
                    pooled_rot.append(np.mean(dseed))
                    seed_diffs.append(dseed)
                    _, SI = draws[rot]
                    D = np.stack([boot[rot][(a, sd)] - boot[rot][(b, sd)] for sd in pr["seeds"]], axis=1)
                    stat += np.take_along_axis(D, SI, 1).mean(1) / len(ROTS)
                    for s in pr["subs"]:
                        v = [pr["cell"][(a, sd)]["sub"][s][0] - pr["cell"][(b, sd)]["sub"][s][0]
                             for sd in pr["seeds"]]
                        d_sub.append(float(np.mean(v)))
                        d_sub_seed.append(v)
                        rot_of.append(rot)
                        names.append(f"{rot} {s}")
                d = np.array(d_sub)
                rmeans = np.array([d[np.array(rot_of) == r].mean() for r in ROTS])
                ci95, ci90 = q(stat, 0.95), q(stat, 0.90)
                rb = cluster_ci(seed_diffs, rng)
                tci95, tci90 = t_ci(rmeans, 0.95), t_ci(rmeans, 0.90)
                wil = stats.wilcoxon(d).pvalue
                res = {"pooled": float(np.mean(pooled_rot)), "pooled_per_rot": pooled_rot,
                       "two_stage_mean": float(stat.mean()), "two_stage_ci95": ci95, "two_stage_ci90": ci90,
                       "tost_two_stage": tost(ci90), "rotation_boot_ci95": rb[1:], "macro": float(d.mean()),
                       "n_subjects": len(d), "n_pos": int((d > 0).sum()), "wilcoxon_p": float(wil),
                       "signflip_p": signflip_p(d), "rotation_flip_p": signflip_p(rmeans),
                       "rot_means": rmeans.tolist(), "t_ci95": tci95, "t_ci90": tci90, "tost_t": tost(tci90),
                       "subjects": names, "d_subject": d_sub, "d_subject_seed": d_sub_seed}
                both = (res["tost_two_stage"], res["tost_t"])
                res["tost_verdict"] = {("e", "e"): "equivalent (both intervals)",
                                       ("e", "n"): "equivalent by two-stage only",
                                       ("n", "e"): "equivalent by t only"}.get(tuple(x[0] for x in both),
                                                                              "not shown equivalent")
                js[f"A|{label}|{model}|{cname(a, b)}"] = res
                md.append(f"| {cname(a, b)} | {res['pooled']:+.1f} | {fmt_ci(ci95)} | {fmt_ci(ci90)} | "
                          f"{res['tost_two_stage']} | {fmt_ci(rb[1:])} | {res['macro']:+.1f} ({len(d)}) | "
                          f"{res['n_pos']}/{len(d)} | {wil:.3f} | {res['signflip_p']:.4f} | "
                          f"{res['rotation_flip_p']:.4f} | {fmt_ci(tci95)} / {fmt_ci(tci90)} | {res['tost_t']} | "
                          f"**{res['tost_verdict']}** |")
            md.append("")
    return keep


def subject_tables(keep: dict, md: list, js: dict) -> None:
    md += ["## A2. Per-subject ROC (seed mean of 3) and macro vs pooled", "",
           "Pooled = mean over rotations of the fold's pooled ROC (the D24 number). Macro = mean over subjects "
           "of the per-subject ROC (every subject weighted equally). Pooled ROC = share x within-subject ROC + "
           "(1 - share) x between-subject ROC, where 'between' ranks positives of one subject against "
           "negatives of another (cross-subject score calibration). AP: pooled = the fold AP, macro = mean "
           "per-subject AP (prevalence differs by subject).", "",
           "| set | model | arm | pooled ROC | macro ROC | within-subject ROC | between-subject ROC | "
           "within share | pooled AP | macro AP |", "|---|---|---|---|---|---|---|---|---|---|"]
    for (label, model), per in keep.items():
        for arm in ARMS:
            pooled, macro, wi, be, sh, pap, mapv = [], [], [], [], [], [], []
            for rot in ROTS:
                pr = per[rot]
                cs = [pr["cell"][(arm, sd)] for sd in pr["seeds"]]
                pooled.append(np.mean([c["pooled"] for c in cs]))
                pap.append(np.mean([c["ap"] for c in cs]))
                for s in pr["subs"]:
                    macro.append(np.mean([c["sub"][s][0] for c in cs]))
                    mapv.append(np.mean([c["sub"][s][1] for c in cs]))
                for c in cs:
                    PN = np.outer(c["P"], c["N"])
                    diag = np.eye(len(c["P"]), dtype=bool)
                    wi.append(100 * c["C"][diag].sum() / PN[diag].sum())
                    be.append(100 * c["C"][~diag].sum() / PN[~diag].sum())
                    sh.append(PN[diag].sum() / PN.sum())
            row = {k: float(np.mean(v)) for k, v in (("pooled", pooled), ("macro", macro), ("within", wi),
                                                      ("between", be), ("share", sh), ("pooled_ap", pap),
                                                      ("macro_ap", mapv))}
            js[f"A2|{label}|{model}|{arm}"] = row
            md.append(f"| {label} | {model} | {arm} | {row['pooled']:.1f} | {row['macro']:.1f} | "
                      f"{row['within']:.1f} | {row['between']:.1f} | {row['share']:.2f} | "
                      f"{row['pooled_ap']:.1f} | {row['macro_ap']:.1f} |")
    md += ["", "### Per-subject ROC, seed mean (n windows / n positive)", ""]
    for (label, model), per in keep.items():
        md += [f"#### {label}, {model}", "", "| rotation | subject | n / pos | " + " | ".join(ARMS) + " | "
               + " | ".join(cname(a, b) for a, b in CON) + " |", "|---" * (3 + len(ARMS) + len(CON)) + "|"]
        for rot in ROTS:
            pr = per[rot]
            c0 = pr["cell"][(ARMS[0], pr["seeds"][0])]
            for i, s in enumerate(pr["subs"]):
                m = {a: np.mean([pr["cell"][(a, sd)]["sub"][s][0] for sd in pr["seeds"]]) for a in ARMS}
                n = int(round(c0["P"][i] + c0["N"][i]))
                md.append(f"| {rot} | {s} | {n} / {int(c0['P'][i])} | " + " | ".join(f"{m[a]:.1f}" for a in ARMS)
                          + " | " + " | ".join(f"{m[a] - m[b]:+.1f}" for a, b in CON) + " |")
        md.append("")


def forest_plots(js: dict) -> list[str]:
    files = []
    for _, _, label in SETS:
        for model in ("biot", "cbramod"):
            fig, axes = plt.subplots(1, len(CON), figsize=(11, 5.6), sharey=True)
            for ax, (a, b) in zip(axes, CON, strict=True):
                r = js[f"A|{label}|{model}|{cname(a, b)}"]
                n = len(r["d_subject"])
                ys = np.arange(n)[::-1] + 2   # subjects on top, macro at 1, pooled at 0
                for yv, dv, sv in zip(ys, r["d_subject"], r["d_subject_seed"], strict=True):
                    ax.plot([min(sv), max(sv)], [yv, yv], color=C3[0], lw=1.2, alpha=0.6)
                    ax.plot(dv, yv, "o", color=C3[0], ms=4)
                for yv, m, ci in ((1, r["macro"], r["t_ci95"]), (0, r["pooled"], r["two_stage_ci95"])):
                    ax.plot(ci, [yv, yv], color=INK, lw=1.6)
                    ax.plot(m, yv, "D", color=INK, ms=5)
                ax.axvline(0, color=MUTED, lw=0.8)
                ax.axhline(1.5, color=GRID, lw=0.8)
                for x in (-3, 3):
                    ax.axvline(x, color=MUTED, lw=0.6, ls="--")
                ax.set_title(cname(a, b), fontsize=8, color=INK)
                ax.set_xlabel("ROC-AUC difference (x100)")
                ax.grid(axis="x", color=GRID, lw=0.5)
                ax.set_yticks([*ys, 1, 0])
                ax.set_yticklabels([*r["subjects"], "macro, t 95% CI", "pooled, two-stage 95% CI"])
            fig.suptitle(f"{label}, {model}, linear head: per-subject paired differences (dot = mean of 3 "
                         "seeds, bar = seed range); dashed = +/-3 (post hoc, E11)", fontsize=9, color=INK)
            fig.tight_layout()
            f = OUT / f"forest_{label.lower().replace(' ', '_').replace('-', '')}_{model}.png"
            fig.savefig(f)
            plt.close(fig)
            files.append(f.name)
    return files


def macro_pooled_plot(js: dict) -> str:
    fig, axes = plt.subplots(1, len(SETS), figsize=(11, 3.2), sharex=True)
    for ax, (_, _, label) in zip(axes, SETS, strict=True):
        names = [(m, a) for m in ("biot", "cbramod") for a in ARMS]
        for i, (m, a) in enumerate(names):
            r = js[f"A2|{label}|{m}|{a}"]
            ax.plot([r["pooled"], r["macro"]], [i, i], color=GRID, lw=2)
            ax.plot(r["pooled"], i, "o", color=C3[0], ms=6, label="pooled fold (D24)" if i == 0 else None)
            ax.plot(r["macro"], i, "s", color=C3[1], ms=6, label="macro over subjects" if i == 0 else None)
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels([f"{m} {a}" for m, a in names])
        ax.invert_yaxis()
        ax.set_title(label, fontsize=9, color=INK)
        ax.set_xlabel("ROC-AUC (x100)")
        ax.grid(axis="x", color=GRID, lw=0.5)
    axes[0].legend(frameon=False, fontsize=7, loc="lower left")
    fig.tight_layout()
    fig.savefig(OUT / "macro_vs_pooled.png")
    plt.close(fig)
    return "macro_vs_pooled.png"


# ---------------------------------------------------------------- B: outlier folds -------------------------------
def outlier_folds(keep: dict, md: list, js: dict) -> str:
    a, b = "last_randinit", "last"
    md += ["## B. Outlier folds, BIOT, last_randinit - last (linear head, 3 seeds)", "",
           "LOSO = the fold's pooled contrast recomputed without that subject (seed mean). Within/between: "
           "pooled ROC split into within-subject and between-subject pairs (section A2).", ""]
    fig, axes = plt.subplots(1, len(OUTLIERS), figsize=(11, 3.6))
    for ax, (label, rot) in zip(axes, OUTLIERS, strict=True):
        pr = keep[(label, "biot")][rot]
        subs, seeds, cell = pr["subs"], pr["seeds"], pr["cell"]
        ones = np.ones((1, len(subs)))
        pooled = {arm: [cell[(arm, sd)]["pooled"] for sd in seeds] for arm in ARMS}
        md += [f"### {label} {rot}: pooled {cname(a, b)} = {np.mean(pooled[a]) - np.mean(pooled[b]):+.1f}", "",
               "| subject | n / pos | " + " | ".join(f"{arm} ROC (seeds)" for arm in ARMS) + " | "
               + " | ".join(f"{arm} AP" for arm in ARMS) + f" | {cname(a, b)} | LOSO pooled {cname(a, b)} |",
               "|---" * (4 + 2 * len(ARMS)) + "|"]
        out = {"pooled": {k: float(np.mean(v)) for k, v in pooled.items()}, "subjects": {}}
        for i, s in enumerate(subs):
            w = ones.copy()
            w[0, i] = 0
            loso = np.mean([wauc(cell[(a, sd)]["C"], cell[(a, sd)]["P"], cell[(a, sd)]["N"], w, w)[0]
                            - wauc(cell[(b, sd)]["C"], cell[(b, sd)]["P"], cell[(b, sd)]["N"], w, w)[0]
                            for sd in seeds])
            roc = {arm: [cell[(arm, sd)]["sub"][s][0] for sd in seeds] for arm in ARMS}
            ap = {arm: np.mean([cell[(arm, sd)]["sub"][s][1] for sd in seeds]) for arm in ARMS}
            c0 = cell[(ARMS[0], seeds[0])]
            out["subjects"][s] = {"roc": roc, "ap": ap, "loso": float(loso), "n_pos": int(c0["P"][i]),
                                  "n": int(c0["P"][i] + c0["N"][i])}
            md.append(f"| {s} | {int(c0['P'][i] + c0['N'][i])} / {int(c0['P'][i])} | "
                      + " | ".join(f"{np.mean(roc[arm]):.1f} ({', '.join(f'{x:.1f}' for x in roc[arm])})"
                                   for arm in ARMS)
                      + " | " + " | ".join(f"{ap[arm]:.2f}" for arm in ARMS)
                      + f" | {np.mean(roc[a]) - np.mean(roc[b]):+.1f} | {loso:+.1f} |")
        md += ["", "| arm | pooled ROC | within-subject ROC | between-subject ROC | within share |",
               "|---|---|---|---|---|"]
        for arm in ARMS:
            wi, be, sh = [], [], []
            for sd in seeds:
                c = cell[(arm, sd)]
                PN, diag = np.outer(c["P"], c["N"]), np.eye(len(subs), dtype=bool)
                wi.append(100 * c["C"][diag].sum() / PN[diag].sum())
                be.append(100 * c["C"][~diag].sum() / PN[~diag].sum())
                sh.append(PN[diag].sum() / PN.sum())
            out[f"decomp_{arm}"] = [float(np.mean(wi)), float(np.mean(be)), float(np.mean(sh))]
            md.append(f"| {arm} | {np.mean(pooled[arm]):.1f} | {np.mean(wi):.1f} | {np.mean(be):.1f} | "
                      f"{np.mean(sh):.2f} |")
        md.append("")
        js[f"B|{label}|{rot}"] = out
        groups = subs + ["pooled"]
        width = 0.2
        for j, arm in enumerate(ARMS):
            vals = [out["subjects"][s]["roc"][arm] for s in subs] + [pooled[arm]]
            xs = np.arange(len(groups)) + (j - 1.5) * width
            ax.bar(xs, [np.mean(v) for v in vals], width * 0.9, color=COLOR[arm], label=arm)
            for x, v in zip(xs, vals, strict=True):
                ax.plot([x] * len(v), v, ".", color=INK, ms=3)
        ax.set_xticks(range(len(groups)))
        ax.set_xticklabels([f"{s}\nLOSO {out['subjects'][s]['loso']:+.1f}" for s in subs]
                           + [f"pooled\n{np.mean(pooled[a]) - np.mean(pooled[b]):+.1f}"])
        ax.axhline(50, color=MUTED, lw=0.6, ls="--")
        ax.set_ylim(0, 100)
        ax.set_ylabel("ROC-AUC (x100)")
        ax.set_title(f"BIOT, {label} {rot} (bars = seed mean, dots = seeds)", fontsize=9, color=INK)
        ax.grid(axis="y", color=GRID, lw=0.5)
    fig.legend(*axes[0].get_legend_handles_labels(), frameon=False, fontsize=8, ncol=4, loc="upper center")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(OUT / "outlier_folds.png")
    plt.close(fig)
    return "outlier_folds.png"


# ---------------------------------------------------------------- C: paper split --------------------------------
def paper_clusters(idx: dict) -> dict:
    """Seizure events (positive clusters) and recording files (negative clusters) of the paper test set."""
    seizures = json.loads((ROOT / "configs" / "chbmit_seizures.json").read_text())
    files = sorted(set(idx["file"]))
    events = [(f, k) for f in files for k in range(len(seizures.get(f, [])))]
    ev_id = np.full(len(idx["file"]), -1)
    for i, (f, st) in enumerate(zip(idx["file"], idx["start"], strict=True)):
        iv = seizures.get(f, [])
        if iv:   # nearest event in the file (0 if the window overlaps it)
            dist = [max(on - (st + WIN), st - off, 0) for on, off in iv]
            ev_id[i] = events.index((f, int(np.argmin(dist))))
    fixed = np.array([overlap_label({"file": f, "n_samples": WIN, "start": int(st)}, seizures)
                      for f, st in zip(idx["file"], idx["start"], strict=True)])
    subj_of_file = {f: idx["subj"][idx["file"] == f][0] for f in files}
    subs = sorted(set(idx["subj"]))
    return {"ev": ev_id, "file": np.array([files.index(f) for f in idx["file"]]), "fixed": fixed,
            "n_ev": len(events), "n_file": len(files), "subs": subs, "events": events,
            "ev_strata": [np.array([i for i, (f, _) in enumerate(events) if subj_of_file[f] == s]) for s in subs],
            "file_strata": [np.array([i for i, f in enumerate(files) if subj_of_file[f] == s]) for s in subs]}


def scoring(run: dict, cl: dict, name: str):
    m = np.ones(len(run["y"]), bool) if name == "upstream" else run["idx"]["grid"]
    y = run["y"] if name != "fixed" else cl["fixed"]
    return m, y[m]


def paper_analysis(rng, reps: int, rows_out: list, md: list, js: dict) -> list[str]:
    sets = (("P1E", load_runs("chbmit", {"P1E"}, "paper", ARMS, 4)),
            ("Table 4 (wave 1)", load_runs("chbmit", {""}, "paper", ("lp", "last", "last_randinit"), 2)))
    idx_names = {x["index"] for _, rr in sets for x in rr}
    if len(idx_names) != 1:
        raise SystemExit(f"paper-split runs use several test indices: {idx_names}")
    idx = sets[0][1][0]["idx"]
    cl = paper_clusters(idx)
    y0 = sets[0][1][0]["y"]
    if any((x["y"] != y0).any() for _, rr in sets for x in rr):
        raise SystemExit("paper-split runs disagree on y_test")
    pos_up = y0 == 1
    if (cl["ev"][pos_up] < 0).any() or (cl["ev"][cl["fixed"] == 1] < 0).any():
        raise SystemExit("a positive window has no seizure event in its file")
    counts = {}
    for nm in SCORINGS:
        m, y = scoring({"y": y0, "idx": idx}, cl, nm)
        counts[nm] = (int(y.sum()), int(m.sum()))
    ev_per_sub = {str(s): len(e) for s, e in zip(cl["subs"], cl["ev_strata"], strict=True)}
    file_per_sub = {str(s): len(f) for s, f in zip(cl["subs"], cl["file_strata"], strict=True)}
    md += ["## C. Paper split (test chb23 + chb24): per patient, and seizure-event cluster bootstrap", "",
           f"Positives / windows: {', '.join(f'{k} {v[0]}/{v[1]}' for k, v in counts.items())}. Seizure events "
           f"per patient {ev_per_sub}; recording files per patient {file_per_sub}. Scorings as "
           "scripts/posthoc_test.py: upstream = all windows, upstream labels (as run); dedup = grid windows, "
           "upstream labels; fixed = grid windows, overlap labels (the probes were trained on upstream labels). "
           "P1E = D24-B (eval-mode probe, encoder tap); Table 4 = wave-1 records (run_tag '', probe v2, train "
           "mode, CBraMod via the released proj_out tap).", ""]
    # per patient
    md += ["### C1. chb23 vs chb24 (ROC / AP x100, mean over 5 seeds)", "",
           "| set | model | head | scoring | arm | chb23 ROC | chb24 ROC | pooled ROC | chb23 AP | chb24 AP | "
           "pooled AP | chb23 n/pos | chb24 n/pos |", "|---" * 13 + "|"]
    sub_res: dict = {}
    for set_name, rr in sets:
        for x in rr:
            for nm in SCORINGS:
                m, y = scoring(x, cl, nm)
                s, subj = x["s"][m], x["idx"]["subj"][m]
                vals = {sub: roc_ap(y[subj == sub], s[subj == sub]) + (int((subj == sub).sum()),
                                                                         int(y[subj == sub].sum()))
                        for sub in cl["subs"]}
                vals["pooled"] = roc_ap(y, s) + (len(y), int(y.sum()))
                sub_res[(set_name, x["model"], x["probe"], nm, x["arm"], x["seed"])] = vals
                for sub in cl["subs"]:
                    rows_out.append({"set": set_name, "tags": x["tag"], "model": x["model"], "probe": x["probe"],
                                     "arm": x["arm"], "split": "paper", "seed": x["seed"], "scoring": nm,
                                     "subject": sub, "n": vals[sub][2], "n_pos": vals[sub][3],
                                     "roc": vals[sub][0], "ap": vals[sub][1]})
    keys = sorted({k[:5] for k in sub_res})
    for set_name, model, probe, nm, arm in sorted(keys, key=lambda k: (k[0] != "P1E", k[1], k[2],
                                                                     SCORINGS.index(k[3]), ARMS.index(k[4]))):
        v = [sub_res[k] for k in sub_res if k[:5] == (set_name, model, probe, nm, arm)]
        mean = {g: (np.mean([r[g][0] for r in v]), np.mean([r[g][1] for r in v])) for g in v[0]}
        js[f"C1|{set_name}|{model}|{probe}|{nm}|{arm}"] = {g: {"roc": mean[g][0], "ap": mean[g][1],
                                                               "n": v[0][g][2], "n_pos": v[0][g][3],
                                                               "roc_seeds": [r[g][0] for r in v]} for g in v[0]}
        a23, a24 = (cl["subs"][0], cl["subs"][1])
        md.append(f"| {set_name} | {model} | {probe} | {nm} | {arm} | {mean[a23][0]:.1f} | {mean[a24][0]:.1f} | "
                  f"{mean['pooled'][0]:.1f} | {mean[a23][1]:.1f} | {mean[a24][1]:.1f} | {mean['pooled'][1]:.1f} | "
                  f"{v[0][a23][2]}/{v[0][a23][3]} | {v[0][a24][2]}/{v[0][a24][3]} |")
    md += ["", "### C2. Per-patient paired contrasts (seed-paired mean; seeds > 0 of 5)", "",
           "| set | model | head | scoring | contrast | chb23 | chb24 | pooled |", "|---" * 8 + "|"]
    for set_name, rr in sets:
        arms = sorted({x["arm"] for x in rr})
        for model in ("biot", "cbramod"):
            for probe in ("linear", "mlp_fullft"):
                seeds = sorted({x["seed"] for x in rr if x["model"] == model and x["probe"] == probe})
                for nm in SCORINGS:
                    for a, b in CON:
                        if a not in arms or b not in arms:
                            continue
                        cells = []
                        for g in [*cl["subs"], "pooled"]:
                            d = np.array([sub_res[(set_name, model, probe, nm, a, sd)][g][0]
                                          - sub_res[(set_name, model, probe, nm, b, sd)][g][0] for sd in seeds])
                            cells.append(f"{d.mean():+.1f} ({(d > 0).sum()}/5)")
                            js[f"C2|{set_name}|{model}|{probe}|{nm}|{cname(a, b)}|{g}"] = d.tolist()
                        md.append(f"| {set_name} | {model} | {probe} | {nm} | {cname(a, b)} | " + " | ".join(cells)
                                  + " |")
    # cluster bootstrap: one event/file draw per rep shared by every cell (paired), then seeds
    U = multinomial_draws(rng, cl["ev_strata"], cl["n_ev"], reps)
    V = multinomial_draws(rng, cl["file_strata"], cl["n_file"], reps)
    SI = rng.integers(0, 5, (reps, 5))
    md += ["", "### C3. Seizure-event cluster bootstrap (x100; point = 5-seed mean of the as-scored test set)", "",
           f"{reps:,} reps. Each rep resamples, within each patient, its seizure events (all positive windows "
           "of an event move together) and its recording files (all negative windows of a file move "
           "together), with replacement; 'events' CI keeps the 5 seeds fixed, 'events+seeds' then resamples "
           "the 5 seeds (paired across arms). ROC exact via the event x file pair matrix; PR = trapezoid "
           "PR-AUC as in Table 4.", "",
           "| set | model | head | scoring | arm / contrast | ROC | ROC 95% CI events | ROC 95% CI events+seeds "
           "| ROC 90% CI events+seeds | TOST +/-3 | PR | PR 95% CI events+seeds |", "|---" * 12 + "|"]
    cb: dict = {}
    for set_name, rr in sets:
        arms = [a for a in ARMS if any(x["arm"] == a for x in rr)]
        for model in ("biot", "cbramod"):
            for probe in ("linear", "mlp_fullft"):
                for nm in SCORINGS:
                    A, PRv = {}, {}
                    for arm in arms:
                        xs = sorted((x for x in rr if (x["model"], x["probe"], x["arm"]) == (model, probe, arm)),
                                    key=lambda x: x["seed"])
                        if len(xs) != 5:
                            raise SystemExit(f"{set_name} {model} {probe} {arm}: {len(xs)} seeds")
                        cols, pcols, pts, ppts = [], [], [], []
                        for x in xs:
                            m, y = scoring(x, cl, nm)
                            s, ev, fi = x["s"][m], cl["ev"][m], cl["file"][m]
                            C, P, N = pair_matrix(y, s, np.where(y == 1, ev, 0), fi, cl["n_ev"], cl["n_file"])
                            cols.append(wauc(C, P, N, U, V))
                            pts.append(100 * roc_auc_score(y, s))
                            point = wauc(C, P, N, np.ones((1, cl["n_ev"])), np.ones((1, cl["n_file"])))[0]
                            if abs(point - pts[-1]) > 1e-9:
                                raise SystemExit("pair-matrix ROC != sklearn on the paper split")
                            prep = pr_prep(y, s)
                            pcols.append(np.concatenate([wpr(prep, np.where(y == 1, U[i:i + 500][:, ev],
                                                                            V[i:i + 500][:, fi]))
                                                         for i in range(0, reps, 500)]))
                            pr, rc, _ = precision_recall_curve(y, s)
                            ppts.append(100 * auc(rc, pr))
                        A[arm] = (np.stack(cols, 1), pts)
                        PRv[arm] = (np.stack(pcols, 1), ppts)
                    items = [(arm, A[arm], PRv[arm]) for arm in arms]
                    items += [(cname(a, b), (A[a][0] - A[b][0], np.subtract(A[a][1], A[b][1])),
                               (PRv[a][0] - PRv[b][0], np.subtract(PRv[a][1], PRv[b][1])))
                              for a, b in CON if a in A and b in A]
                    for name, (Ab, pt), (Pb, ppt) in items:
                        ev_only = Ab.mean(1)
                        both = np.take_along_axis(Ab, SI, 1).mean(1)
                        pboth = np.take_along_axis(Pb, SI, 1).mean(1)
                        res = {"roc": float(np.mean(pt)), "roc_ci95_events": q(ev_only, 0.95),
                               "roc_ci95": q(both, 0.95), "roc_ci90": q(both, 0.90), "pr": float(np.mean(ppt)),
                               "pr_ci95": q(pboth, 0.95), "n_nan": int((~np.isfinite(both)).sum())}
                        is_con = " - " in name
                        res["tost"] = tost(res["roc_ci90"]) if is_con else ""
                        cb[(set_name, model, probe, nm, name)] = res
                        js[f"C3|{set_name}|{model}|{probe}|{nm}|{name}"] = res
                        sign = "+" if is_con else ""
                        md.append(f"| {set_name} | {model} | {probe} | {nm} | {name} | {res['roc']:{sign}.1f} | "
                                  f"{fmt_ci(res['roc_ci95_events'])} | {fmt_ci(res['roc_ci95'])} | "
                                  f"{fmt_ci(res['roc_ci90'])} | {res['tost']} | {res['pr']:{sign}.1f} | "
                                  f"{fmt_ci(res['pr_ci95'])} |")
    md.append("")
    return [p1e_plot(js, cl), cluster_plot(cb, sets)]


def p1e_plot(js: dict, cl: dict) -> str:
    fig, axes = plt.subplots(len(SCORINGS), 4, figsize=(11, 7), sharey=True)
    groups = [*cl["subs"], "pooled"]
    for i, nm in enumerate(SCORINGS):
        for j, (model, probe) in enumerate((m, p) for m in ("biot", "cbramod") for p in ("linear", "mlp_fullft")):
            ax = axes[i, j]
            for k, g in enumerate(groups):
                xs = np.arange(len(ARMS)) + (k - 1) * 0.27
                vals = [js[f"C1|P1E|{model}|{probe}|{nm}|{a}"][g] for a in ARMS]
                ax.bar(xs, [v["roc"] for v in vals], 0.25, color=C3[k], label=g)
                for x, v in zip(xs, vals, strict=True):
                    ax.plot([x] * len(v["roc_seeds"]), v["roc_seeds"], ".", color=INK, ms=2)
            ax.set_xticks(range(len(ARMS)))
            ax.set_xticklabels(["lp", "lp_rand", "last", "last_rand"], fontsize=7)
            ax.axhline(50, color=MUTED, lw=0.6, ls="--")
            ax.set_ylim(0, 100)
            ax.grid(axis="y", color=GRID, lw=0.5)
            ax.set_title(f"{model} {probe}, {nm}", fontsize=8, color=INK)
            if j == 0:
                ax.set_ylabel("ROC-AUC (x100)")
    fig.legend(*axes[0, 0].get_legend_handles_labels(), frameon=False, fontsize=8, ncol=3, loc="upper right")
    fig.suptitle("P1E (paper split, fixed probe): chb23 vs chb24 vs pooled; bars = 5-seed mean, dots = seeds",
                 fontsize=9, color=INK, x=0.4)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(OUT / "p1e_subjects.png")
    plt.close(fig)
    return "p1e_subjects.png"


def cluster_plot(cb: dict, sets) -> str:
    fig, axes = plt.subplots(1, len(sets), figsize=(11, 6.5))
    for ax, (set_name, _) in zip(axes, sets, strict=True):
        rows = sorted({k[1:3] + (k[4],) for k in cb if k[0] == set_name and " - " in k[4]},
                      key=lambda r: (r[0], r[1], [cname(a, b) for a, b in CON].index(r[2])))
        for i, (model, probe, con) in enumerate(rows):
            for k, nm in enumerate(SCORINGS):
                r = cb[(set_name, model, probe, nm, con)]
                yv = i + (k - 1) * 0.25
                ax.plot(r["roc_ci95"], [yv, yv], color=C3[k], lw=1.4)
                ax.plot(r["roc"], yv, "o", color=C3[k], ms=4, label=nm if i == 0 else None)
        ax.set_yticks(range(len(rows)))
        ax.set_yticklabels([f"{m} {p}: {c}" for m, p, c in rows], fontsize=7)
        ax.invert_yaxis()
        ax.axvline(0, color=MUTED, lw=0.8)
        for x in (-3, 3):
            ax.axvline(x, color=MUTED, lw=0.6, ls="--")
        ax.set_xlabel("ROC-AUC difference (x100), 95% CI events+seeds")
        ax.set_title(f"{set_name}: seizure-event cluster bootstrap", fontsize=9, color=INK)
        ax.grid(axis="x", color=GRID, lw=0.5)
        ax.legend(frameon=False, fontsize=7, loc="lower right")
    fig.tight_layout()
    fig.savefig(OUT / "cluster_bootstrap.png")
    plt.close(fig)
    return "cluster_bootstrap.png"


def ci_compare_plot(js: dict) -> str:
    rows = [(label, model, a, b) for _, _, label in SETS for model in ("biot", "cbramod") for a, b in CON]
    fig, ax = plt.subplots(figsize=(8, 9))
    kinds = (("two_stage_ci95", "two-stage (subjects, seeds)"), ("rotation_boot_ci95", "rotations, seeds (D24-D)"),
             ("t_ci95", "t over rotation means of subject diffs (dot = macro)"))
    for i, (label, model, a, b) in enumerate(rows):
        r = js[f"A|{label}|{model}|{cname(a, b)}"]
        for k, (key, name) in enumerate(kinds):
            yv = i + (k - 1) * 0.25
            ax.plot(r[key], [yv, yv], color=C3[k], lw=1.4, label=name if i == 0 else None)
            ax.plot(r["pooled"] if k < 2 else r["macro"], yv, "o", color=C3[k], ms=3)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([f"{lb}, {m}: {cname(a, b)}" for lb, m, a, b in rows], fontsize=7)
    ax.invert_yaxis()
    ax.axvline(0, color=MUTED, lw=0.8)
    for x in (-3, 3):
        ax.axvline(x, color=MUTED, lw=0.6, ls="--")
    ax.set_xlabel("ROC-AUC difference (x100), 95% intervals")
    ax.grid(axis="x", color=GRID, lw=0.5)
    ax.legend(frameon=False, fontsize=7, loc="lower right")
    ax.set_title("D24-A contrasts: three 95% intervals (post hoc, E11)", fontsize=9, color=INK)
    fig.tight_layout()
    fig.savefig(OUT / "ci_comparison.png")
    plt.close(fig)
    return "ci_comparison.png"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=10_000)
    args = ap.parse_args()
    self_check()
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20261101)
    md = ["# E11: subject-level and test-set uncertainty (D25; POST HOC, ROC-AUC x100, val-selected epoch)", "",
          "Generated by scripts/analysis/subject_level.py. Every number here is post hoc (E11 rule): the D24 "
          "verdicts stay primary. Equivalence statement = TOST at +/-3 with the 90% CI. statsmodels is not "
          "installed in .venv: the mixed model diff ~ 1 + (1|rotation) is replaced by the rotation-block "
          "sign-flip and the t-interval over rotation means (see section A).", ""]
    js: dict = {}
    rows: list = []
    keep = rotation_analysis(rng, args.reps, rows, md, js)
    subject_tables(keep, md, js)
    figs = forest_plots(js) + [macro_pooled_plot(js), ci_compare_plot(js), outlier_folds(keep, md, js)]
    figs += paper_analysis(rng, args.reps, rows, md, js)
    md += ["## Figures", "", *[f"- {f}" for f in figs], ""]
    (OUT / "subject_level.md").write_text("\n".join(md) + "\n")
    (OUT / "subject_level.json").write_text(json.dumps(js, indent=1, default=float))
    (OUT / "per_subject_runs.json").write_text(json.dumps(rows, indent=0, default=float))
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
