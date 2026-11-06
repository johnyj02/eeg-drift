#!/usr/bin/env python3
"""D29 (notes/decisions.md "## D29", frozen in git at c0283f4 before any D29 run): C2/C3 controls at the
fixed-compute budget on Siena / Siena filtered, and the PR-AUC readings.

    .venv/bin/python scripts/analysis/d29_read.py

Records: S3C2D-<N> / S3FC2D-<N> (N896, N1664, N2048, N4174) and S3C3D-<P>N2048 / S3FC3D-<P>N2048 (P2, P5,
P10): BIOT arms last and last_noise; S3LPBD / S3FLPBD: BIOT lp at probe batch 128; probes linear and
linear_z; 5 rotations x 3 seeds [S_r, 1000+r, 2000+r]. Paired with E30b (S3C2 / S3C3 / S3LPB and the S3F
tags), whose linear values the D29 last / lp linear values must reproduce exactly.
Rules (as frozen): (1) the E30 C2/C3 rules (scripts/analysis/e30_c2c3.py: c2, c3, with the E30 reader
choices) for each head separately: curve and LP = mean over the 5 rotations of 3-seed means. (2) Noise
control: "the plateau needs EEG data" only if at EVERY N (every P) the 95% t-interval (df 4) of
last - last_noise over the 5 rotation means excludes 0 with mean > 3; else "no difference demonstrated";
TOST (margin 3, alpha 0.05) reported per N and P.
Descriptive (no rule): the E30 rules on the last_noise curve; per-rotation verdicts; Nadeau-Bengio
intervals; the PR-AUC readings (average precision, and the trapezoid PR-AUC the release reports) of C1
(last - lp; D24-A/B, P1Z / S*Z linear_z, D28 grid / grid_z) and C2/C3 (E30a DL's split, D24-C CBraMod,
D29 rotations, the CBraMod control vs its batch-128 LP of D27-C).
PR-AUC re-read (2026-11-05, AFTER the results, in answer to an external review): no ROC-derived
threshold is applied to a PR-AUC contrast any more. The frozen D29 PR-AUC item only asks for C1/C2/C3
"read again with average precision"; it defines no PR margin. The earlier version of this reader reused
the ROC rule strings and the margin-3 TOST, which compared a 3-point margin against AP baselines of 1.5
to 44 points and hid measured changes (Siena BIOT raw head: AP 1.65 -> 2.20, +0.55 [+0.14, +0.96], +33%
relative, labelled "no difference shown" because 0.55 < 3). Every PR-AUC contrast now reports both arm
means, the absolute difference with its 95% t-interval over the stated units, the relative change in
percent of the baseline arm, and whether the interval excludes 0 (the only inference claim); no
practical-importance label and no margin-3 TOST (see pr_read). The ROC readings are unchanged.
Writes artifacts/analysis/D29/{README.md, pr_auc.md, d29.json}.
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from e30_c2c3 import NA, NB, NC, PA, PB, PC, ROTS, SR, c2, c3, describe, num, seeds3  # noqa: E402
from e30_c2c3 import selfcheck as e30_selfcheck  # noqa: E402
from read_step1 import d19, paired  # noqa: E402
from stats_d25 import nb_ratio, tost_p  # noqa: E402

LOCAL = ROOT / "artifacts" / "s3-results"
OUT = ROOT / "artifacts" / "analysis" / "D29"
E30_JSON = ROOT / "artifacts" / "analysis" / "E30" / "e30.json"
SKIP = ("diag-", "test-index-", "val-index-", "report-")
SETTINGS = (("S3", "Siena", "S3E,S3M"), ("S3F", "Siena filtered", "S3FE,S3FM"))
HEADS = ("linear", "linear_z")
MET = {"avg_precision": "AP", "pr_auc_trapz": "PR-AUC trapz", "roc_auc": "ROC"}
PR = {k: v for k, v in MET.items() if k != "roc_auc"}  # the PR metrics: no ROC threshold applies to them
SUBS = NB + PB
C1_PAPER = (
    ("linear", ("P1E",)),
    ("mlp_fullft", ("P1E",)),
    ("linear_z", ("P1Z",)),
    ("grid", ("P1G",)),
    ("grid_z", ("P1G",)),
)
C1_ROT = {
    "CHB-MIT": (
        "S1E,S1M",
        (("linear", ("S1E", "S1M")), ("linear_z", ("S1Z",)), ("grid", ("S1G",)), ("grid_z", ("S1G",))),
    ),
    "Siena": (
        "S3E,S3M",
        (("linear", ("S3E", "S3M")), ("linear_z", ("S3Z",)), ("grid", ("S3G",)), ("grid_z", ("S3G",))),
    ),
    "Siena filtered": (
        "S3FE,S3FM",
        (("linear", ("S3FE", "S3FM")), ("linear_z", ("S3FZ",)), ("grid", ("S3FG",)), ("grid_z", ("S3FG",))),
    ),
}
# published C1 ROC means (decisions.md D24 outcome A/B, D27-B / P1Z), re-derived as a loader check
C1_PUBLISHED = {
    ("CHB-MIT", "biot", "linear"): 1.9,
    ("Siena", "biot", "linear"): 9.2,
    ("Siena filtered", "biot", "linear"): 4.1,
    ("CHB-MIT", "cbramod", "linear"): -0.0,
    ("Siena", "cbramod", "linear"): 0.3,
    ("Siena filtered", "cbramod", "linear"): 0.1,
    ("Siena", "biot", "linear_z"): 1.7,
    ("Siena filtered", "biot", "linear_z"): 1.9,
    ("DL's split", "biot", "linear"): -0.6,
    ("DL's split", "biot", "mlp_fullft"): -1.2,
    ("DL's split", "cbramod", "linear"): 0.0,
    ("DL's split", "cbramod", "mlp_fullft"): 0.0,
    ("DL's split", "biot", "linear_z"): 0.2,
    ("DL's split", "cbramod", "linear_z"): 0.2,
}
PRCOLS = "base mean | arm mean | difference | 95% t | relative | excludes 0"
PR_READING = (
    "No ROC-derived threshold is applied to a PR-AUC contrast, and no practical-importance label is attached to "
    "one. The frozen D29 text asks only for C1, C2 and C3 \"read again with average precision (and the trapezoid "
    "PR-AUC the release reports)\" and defines no PR-AUC margin; the first version of this reader reused the ROC "
    "rule strings (D18 |mean| > 3 with 4 of 5 units agreeing; the E30 C2/C3 \"within 3\" / \"> 3 above LP\" cuts; "
    "the D29 noise rule's \"mean > 3\") and the margin-3 TOST. That compared one fixed 3-point margin against AP "
    "baselines from 1.5 to 44 points and hid measured differences: Siena BIOT raw head AP 1.65 -> 2.20, +0.55 "
    "[+0.14, +0.96], about +33% relative, was labelled \"no difference shown\" because 0.55 < 3. Those labels and "
    "the margin-3 TOST are withdrawn here (change made 2026-11-05, AFTER the results, in answer to an external "
    "review; post hoc). Each PR-AUC contrast now reports the two arm means, the absolute difference with its 95% "
    "t-interval over the stated units, the relative change in percent of the baseline arm, and whether the "
    "interval excludes 0 - which is the only inference claim made. A relative change on a near-zero baseline is "
    "unstable, so the baseline is printed next to every percentage and should be read with it. No PR-AUC margin "
    "is defined in its place: defining one now, after seeing the data, would be a post hoc threshold, and the "
    "prevalence-scaled alternatives already in the artifacts (AP / prevalence, scripts/analysis/coverage.py and "
    "handcrafted_baseline.py) are reported there rather than turned into a cut here. Every ROC reading in these "
    "files is unchanged."
)
BASES = (
    {f"{t}{x}" for t, _, _ in SETTINGS for x in ("C2D", "C3D", "LPBD", "C2", "C3", "LPB", "CC", "CLPB")}
    | {"C2E", "C3E", "C2X", "C3X", "R3E"}
    | {t for _, ts in C1_PAPER for t in ts}
    | {t for _, hs in C1_ROT.values() for _, ts in hs for t in ts}
)


def _hash(*parts) -> str:  # copy of eegdrift.study._hash (noise data_hash = _hash(ssl.hash, "noise"))
    return hashlib.sha256(json.dumps(parts, sort_keys=True, default=str).encode()).hexdigest()[:16]


def group(tag: str, split: str) -> str:
    """Eval-data group (records do not store the Siena data variant: run_tag tells it)."""
    if split == "paper":
        return "chbmit paper"
    return "siena filtered" if tag.startswith("S3F") else "siena" if tag.startswith("S3") else "chbmit"


# ---- records -------------------------------------------------------------------------------------
def scan() -> tuple[dict, list[str]]:
    """(run_tag, model, arm, split, seed) -> record, for every tag this reader uses; generic checks."""
    got: dict = defaultdict(list)
    for p in sorted(LOCAL.rglob("results/*.json")):
        if p.name.startswith(SKIP):
            continue
        r = json.loads(p.read_text())
        tag = r.get("run_tag") or ""
        if r.get("smoke") or tag.split("-")[0] not in BASES:
            continue
        for res in r["probes"].values():  # keep memory small; nothing below reads these
            res.pop("history", None)
            res.pop("configs", None)
        got[(tag, r["model"], r["arm"], r["split"], r["seed"])].append(r)
    dups = [k for k, v in got.items() if len(v) > 1]
    assert not dups, f"duplicate records: {dups[:5]} ({len(dups)})"
    rec = {k: v[0] for k, v in got.items()}
    eh: dict = defaultdict(set)
    for k, r in rec.items():
        assert r["versions"]["probe"] == 4, k
        assert r["labels"] == ("upstream" if r["split"] == "paper" else "overlap"), (k, r["labels"])
        for name, res in r["probes"].items():
            s = res["spec"]
            assert (s["variant"], s["backbone_mode"], s.get("tap", "encoder")) == (name, "eval", "encoder"), k
        eh[(group(k[0], k[3]), k[3])].add(r["eval_hash"])
    mixed = {k: v for k, v in eh.items() if len(v) > 1}
    assert not mixed, f"eval_hash differs within an eval-data group: {mixed}"
    assert all(eh[("siena", r)] != eh[("siena filtered", r)] for r in ROTS), "filtered = unfiltered eval data"
    n_tag = Counter(k[0].split("-")[0] for k in rec)
    return rec, [
        f"- {len(rec)} records read (0 duplicate, 0 smoke used); per tag: "
        + ", ".join(f"{t} {n}" for t, n in sorted(n_tag.items())),
        "- every record: probe v4, eval mode, encoder tap, probe variant = probe name; labels upstream "
        "on DL's split, overlap on rotations; one eval_hash per (eval data, split) over ALL these "
        f"records and both models ({len(eh)} cells); Siena filtered differs from Siena in every "
        "rotation",
    ]


def d29_checks(rec: dict) -> tuple[list[str], dict]:
    """D29 cell set, specs, pairing with E30b and the exact-reproduction check."""
    want = set()
    for t, _, _ in SETTINGS:
        for r, rot in enumerate(ROTS):
            for s in seeds3(r):
                want |= {
                    (f"{t}C{2 if sub in NB else 3}D-{sub}", "biot", arm, rot, s)
                    for sub in SUBS
                    for arm in ("last", "last_noise")
                }
                want.add((f"{t}LPBD", "biot", "lp", rot, s))
    d29_tags = {f"{t}{x}" for t, _, _ in SETTINGS for x in ("C2D", "C3D", "LPBD")}
    have = {k for k in rec if k[0].split("-")[0] in d29_tags}
    assert have == want, f"missing {sorted(want - have)[:5]}, extra {sorted(have - want)[:5]}"
    n_exact = Counter()
    best_ep: dict = defaultdict(Counter)
    for k in sorted(want):
        tag, _, arm, rot, s = k
        r = rec[k]
        old_tag = tag.replace("C2D", "C2").replace("C3D", "C3").replace("LPBD", "LPB")
        old = rec[(old_tag, "biot", "last" if arm == "last_noise" else arm, rot, s)]
        assert r["versions"] == {"adapt": 3, "probe": 4}, k
        assert set(r["probes"]) == set(HEADS), k
        sl, sz = r["probes"]["linear"]["spec"], r["probes"]["linear_z"]["spec"]
        assert {q for q in sl if sl[q] != sz[q]} == {"variant"} and sl["batch"] == 128, k
        assert sl == old["probes"]["linear"]["spec"], k
        assert r["eval_hash"] == old["eval_hash"], k
        for h in HEADS:
            best_ep[(arm, h)][r["probes"][h]["best_epoch"]] += 1
        if arm == "lp":
            assert r["adapt_spec"]["groups"] == [] and not r.get("ssl_subset") and "adapt" not in r, k
            assert r["adapt_spec"] == old["adapt_spec"], k
        else:
            sub = tag.split("-", 1)[1]
            a, ad = r["adapt_spec"], r["adapt"]
            assert (
                a["protocol"],
                a["batch"],
                a["n_total"],
                a["init"],
                a["groups"],
                a["lr"],
                ad["steps"],
                ad["skipped_nonfinite"],
            ) == ("fixed_c", 128, 4174, "pretrained", ["block03", "head"], 3e-5, 132, 0), k
            assert r["ssl_subset"] == sub and a["n_windows"] == int(sub.rsplit("N", 1)[1]), k
            if sub.startswith("P"):
                assert r["ssl_subjects"] == num(sub), (k, r["ssl_subjects"])
            assert r["ssl_subjects"] == old["ssl_subjects"], k
            assert r["arm_spec"]["ssl_input"] == ("noise" if arm == "last_noise" else "eeg"), k
            if arm == "last":
                assert a == old["adapt_spec"] and r["arm_spec"] == old["arm_spec"], k
                assert ad["epoch_losses"] == old["adapt"]["epoch_losses"], k
                assert ad["best_epoch"] == old["adapt"]["best_epoch"], k
            else:
                assert a["data_hash"] == _hash(old["adapt_spec"]["data_hash"], "noise"), k
                assert {q for q in a if a[q] != old["adapt_spec"][q]} == {"arm", "data_hash"}, k
        if arm != "last_noise":
            o, n = old["probes"]["linear"], r["probes"]["linear"]
            same = all(o[q] == n[q] for q in ("test_at_best", "test_last", "val_curve", "best_epoch", "best_val"))
            n_exact[(arm, same)] += 1
    reps = sum(v for (a, ok), v in n_exact.items() if ok)
    total = sum(n_exact.values())
    assert reps == total, f"D29 linear does not reproduce E30b: {dict(n_exact)}"
    notes = [
        f"- D29: {len(want)} records = 2 settings x 5 rotations x 3 seeds x (7 subsets x 2 arms + lp), "
        "exactly the expected cells (0 missing, 0 extra, 0 duplicate)",
        "- every D29 record: probe v4 / adapt v3, probes linear and linear_z with specs identical apart from "
        "the variant (batch 128, 10 epochs, lr 4e-4, wd 0.05, eval mode, encoder tap), linear spec = the "
        "E30b record's; eval_hash = the E30b record's in every rotation",
        "- adapted cells: fixed_c, SSL batch 128, lr 3e-5, n_total 4174, pretrained init, groups block03 + head, "
        "132 steps, 0 non-finite steps, n_windows = N, ssl_subjects = P (C3) and = E30b's; `last` adapt_spec, "
        "arm_spec, per-pass SSL losses and restored pass identical to E30b; `last_noise` adapt_spec differs "
        "from E30b `last` only in arm and data_hash, data_hash = _hash(EEG subset hash, 'noise') "
        "(same window subset, noise input), arm ssl_input noise",
        f"- reproduction: D29 last and lp linear = E30b linear EXACTLY (test_at_best, test_last, val_curve, "
        f"best_epoch, best_val equal as floats) in {reps} of {total} records "
        f"(last {n_exact[('last', True)]}, lp {n_exact[('lp', True)]})",
        "- selected probe epoch (0-based; 9 = the last of 10) counts: "
        + "; ".join(f"{a} {h} {dict(sorted(c.items()))}" for (a, h), c in sorted(best_ep.items())),
    ]
    return notes, {f"{a} {h}": dict(sorted(c.items())) for (a, h), c in best_ep.items()}


def m(rec: dict, key: tuple, probe: str, metric: str) -> float:
    return 100 * rec[key]["probes"][probe]["test_at_best"][metric]


def get(rec: dict, tags, model: str, arm: str, split: str, seed: int, probe: str, metric: str) -> float:
    """One value from exactly one of `tags`."""
    hits = [k for t in tags if (k := (t, model, arm, split, seed)) in rec and probe in rec[k]["probes"]]
    assert len(hits) == 1, (tags, model, arm, split, seed, probe, hits)
    return m(rec, hits[0], probe, metric)


# ---- statistics ------------------------------------------------------------------------------------
def tint(u, ratio: float | None = None) -> dict:
    """Mean, 95% t-interval (df n-1), TOST p at margin 3; Nadeau-Bengio variants if ratio is given."""
    u = np.asarray(u, dtype=float)
    n, mu, sd = len(u), float(u.mean()), float(u.std(ddof=1))
    T, out = stats.t(n - 1), {"units": [float(x) for x in u], "mean": float(u.mean()), "sd": sd}
    for name, se in (("t", sd / np.sqrt(n)), ("nb", sd * np.sqrt(1 / n + ratio) if ratio else None)):
        if se is None:
            continue
        q = T.ppf(0.975) * se
        out[name] = {"ci95": [mu - q, mu + q], "tost3_p": tost_p(mu, se, 3.0, T)}
    out["n_pos"] = int((u > 0).sum())
    return out


def pr_read(d, base: float, arm: float, arms: str, unit: str, ratio: float | None = None) -> dict:
    """One PR-AUC contrast: both arm means, the absolute difference with its 95% t-interval over
    `unit`s, the relative change in percent of the baseline arm, and whether the interval excludes 0.

    No practical-importance label and no margin-3 TOST. 3 points is the ROC margin of the D15 / D18 /
    D29 rules; the frozen D29 PR-AUC item defines no PR margin, and the AP baselines here run from 1.5
    to 44 points, so one fixed 3-point margin is not a statement about PR-AUC at all. "Interval
    excludes 0" is the only inference claim made here. A relative change on a near-zero baseline is
    unstable, so `base` is reported next to `rel_pct` everywhere. With a single unit (CBraMod on DL's
    split: one seed) there is no interval; `t` is None and `excludes_0` is None, never False.
    """
    d = [float(x) for x in d]
    if len(d) < 2:
        out = {"units": d, "mean": d[0], "sd": None, "t": None, "n_pos": int(d[0] > 0)}
    else:
        out = tint(d, ratio)
        for k in ("t", "nb"):
            if k in out:
                out[k].pop("tost3_p", None)  # margin 3 is the ROC margin; no PR margin is defined
    lo, hi = out["t"]["ci95"] if out["t"] else (None, None)
    return out | {
        "arms": arms,
        "unit": unit,
        "base": base,
        "arm": arm,
        "rel_pct": 100 * out["mean"] / base if base else None,
        "excludes_0": None if out["t"] is None else bool(lo > 0 or hi < 0),
    }


def passes(t: dict) -> bool:
    """D29: the 95% t-interval excludes 0 with mean > 3 (the ROC noise rule; ROC metrics only)."""
    return t["mean"] > 3 and t["t"]["ci95"][0] > 0


def noise_verdict(rows: list[dict]) -> str:
    return "the plateau needs EEG data" if all(passes(t) for t in rows) else "no difference demonstrated"


def verdicts(curve: dict, lp: float | None, nn, pp) -> dict:
    cn, cp = {num(x): curve[x] for x in nn}, {num(x): curve[x] for x in pp}
    return {
        "C2": c2(cn, lp),
        "C2_numbers": describe(cn, lp, "N"),
        "C3": c3(cp, lp),
        "C3_numbers": describe(cp, lp, "P"),
    }


def selfcheck() -> None:
    e30_selfcheck()
    ok, no = tint([4, 5, 6, 5, 4]), tint([4, 9, -1, 5, 4])
    assert passes(ok) and not passes(no) and not passes(tint([2.9, 3, 3.1, 3, 2.9]))
    assert noise_verdict([ok, ok]) == "the plateau needs EEG data"
    assert noise_verdict([ok, no]) == "no difference demonstrated"
    assert (
        tint([0.1, -0.2, 0.0, 0.1, -0.1])["t"]["tost3_p"] < 0.05 and tint([5, -5, 4, -4, 0])["t"]["tost3_p"] > 0.05
    )
    # the PR-AUC reading: no threshold, no margin TOST, the review's example read as a real difference
    x = pr_read([0.07, 0.50, 0.55, 0.64, 0.99], 1.65, 2.20, "LP -> last", "rotation mean")
    assert x["excludes_0"] and 0.54 < x["mean"] < 0.56 and 32 < x["rel_pct"] < 34
    assert "tost3_p" not in x["t"] and not {"rule", "passes", "label"} & set(x)
    assert not pr_read([0.5, -0.5, 0.4, -0.4, 0.0], 10.0, 10.0, "a -> b", "seed")["excludes_0"]
    one = pr_read([0.3], 1.0, 1.3, "a -> b", "none (1 seed)")
    assert one["t"] is None and one["excludes_0"] is None and one["rel_pct"] == 30
    assert pr_read([1.0, 1.0], 0.0, 1.0, "a -> b", "seed")["rel_pct"] is None  # zero baseline, no percent


# ---- formatting --------------------------------------------------------------------------------------
def ci(t: dict, key: str = "t") -> str:
    lo, hi = t[key]["ci95"]
    return f"[{lo:+.2f}, {hi:+.2f}]"


def tp(p: float) -> str:
    return f"{p:.2g}" if p < 0.001 else f"{p:.3f}"


def units(t: dict, nd: int = 2) -> str:
    return ", ".join(f"{x:+.{nd}f}" for x in t["units"])


def pci(t: dict, key: str = "t") -> str:
    """95% interval of a PR-AUC contrast; one unit gives no interval."""
    return ci(t, key) if t.get(key) else "n/a (1 unit)"


def pct(t: dict) -> str:
    return "n/a (baseline 0)" if t["rel_pct"] is None else f"{t['rel_pct']:+.1f}%"


def exc(t: dict) -> str:
    return "n/a" if t["excludes_0"] is None else ("yes" if t["excludes_0"] else "no")


def pr_row(t: dict, nd: int = 2) -> str:
    """The shared PR-AUC cells: base, arm, difference, 95% t, relative change, excludes 0."""
    return (
        f"{t['base']:.{nd}f} | {t['arm']:.{nd}f} | {t['mean']:+.{nd}f} | {pci(t)} | {pct(t)} | {exc(t)}"
    )


# ---- LaTeX for the appendix (ready to paste; no paper file is written by this script) -------------
TEXHEAD = {"linear": "raw", "mlp_fullft": "MLP", "linear_z": "std", "grid": "tuned raw", "grid_z": "tuned std"}
LETTER = {"first term wins": "F", "second term wins": "S", "no difference shown": "N"}
DAG = "$^{\\dagger}$"


def tn(v: float, nd: int = 2, sign: bool = True) -> str:
    """A number for LaTeX text mode: ASCII minus becomes the math minus the paper uses."""
    return (f"{v:+.{nd}f}" if sign else f"{v:.{nd}f}").replace("-", "$-$")


def tci(t: dict) -> str:
    if not t["t"]:
        return "no interval (1 seed)"
    lo, hi = t["t"]["ci95"]
    return f"[{tn(lo)}, {tn(hi)}]"


def tpct(t: dict, nd: int = 1) -> str:
    return "--" if t["rel_pct"] is None else tn(t["rel_pct"], nd) + "\\%"


def tspan(xs: list[dict], key: str = "mean", nd: int = 2) -> str:
    v = [x[key] for x in xs]
    return f"{tn(min(v), nd)} to {tn(max(v), nd)}" if min(v) != max(v) else tn(min(v), nd)


def tex_tables(c1: list[dict], pc: dict, rot_pr: dict, rots: dict) -> list[str]:
    """The two appendix tables, the appendix paragraph and the main-text sentence, as LaTeX."""
    def pairs(d: dict) -> list[tuple[dict, dict]]:
        return [(d["avg_precision"][w][sub], d["pr_auc_trapz"][w][sub])
                for w in ("vs_lp", "vs_noise") if w in d["avg_precision"]
                for sub in d["avg_precision"][w]]

    ap_tz = (
        [(r["avg_precision"], r["pr_auc_trapz"]) for r in c1]
        + [x for d in pc.values() for x in pairs(d)]
        + [x for (name, h, k), b in rot_pr.items() if k == "avg_precision"
           for x in pairs({"avg_precision": b, "pr_auc_trapz": rot_pr[(name, h, "pr_auc_trapz")]})]
        + [x for name, d in rots.items() for x in pairs(d["cbramod"])]
    )
    gap = max(abs(a["mean"] - z["mean"]) for a, z in ap_tz)
    bases = [x["base"] for r in c1 for x in (r["avg_precision"], r["pr_auc_trapz"])]
    rows_b = (
        [("DL's split", f"{mo}, raw", pc[mo]["avg_precision"]["lp"], pc[mo]["avg_precision"]["vs_lp"], None)
         for mo in ("biot", "cbramod")]
        + [
            x
            for name in ("Siena", "Siena filtered")
            for x in (
                [
                    (
                        name.replace("filtered", "filt."),
                        f"BIOT, {TEXHEAD[h]}",
                        rot_pr[(name, h, "avg_precision")]["lp"],
                        rot_pr[(name, h, "avg_precision")]["vs_lp"],
                        rot_pr[(name, h, "avg_precision")]["vs_noise"],
                    )
                    for h in HEADS
                ]
                + [
                    (
                        name.replace("filtered", "filt."),
                        "CBraMod, raw",
                        rots[name]["cbramod"]["avg_precision"]["lp"],
                        rots[name]["cbramod"]["avg_precision"]["vs_lp"],
                        None,
                    )
                ]
            )
        ]
    )
    L = [
        "% D29 PR-AUC re-reading, generated by scripts/analysis/d29_read.py (do not hand-edit the numbers;",
        "% re-run the reader instead). Drop-in replacement for Table tab:d29pr and Table tab:d29prc of",
        "% sections/app-c-robust.tex, plus the appendix paragraph and the main-text sentence below.",
        "% Columns are sized for the TMLR text width at \\scriptsize; booktabs, as the rest of the appendix.",
        "",
        "% ===== Table 1 of 2: C1 =====",
        "\\begin{table}[!htbp]",
        "\\caption{D29 PR-AUC readings of C1 (descriptive; existing records, test split at the ROC-selected",
        "epoch): \\lastarm$-$\\lparm{} in average precision (AP) and in the trapezoid PR-AUC of the release",
        "($\\times100$). No practical-importance threshold is applied to a PR metric: the $\\pm3$-point margin of",
        "our rules is a ROC margin, no PR-AUC margin was pre-registered, and the PR baselines here span",
        f"{min(bases):.2f} to {max(bases):.2f} points. Each row gives the two arm means, the difference with its",
        "95\\% $t$-interval over the units (5",
        "seeds on DL's split, 5 rotation means of 3 seeds elsewhere) and the change relative to the \\lparm{}",
        "baseline, which should be read together with that baseline: a percentage on a near-prevalence",
        "baseline is",
        "unstable. A dagger ($\\dagger$) marks the",
        f"{len([1 for r in c1 for k in PR if r[k]['excludes_0']])} intervals that exclude 0, the only inference",
        "claim made here. The ROC column is the unchanged ROC reading with its consistency",
        "label (F, S, N: Table~\\ref{tab:vocab}). Heads: raw = linear head, MLP = shipped MLP head (fixed",
        "recipe),",
        "std = \\texttt{linear\\_z}, tuned raw / tuned std = the D28 probes; run tags as in",
        "Table~\\ref{tab:glossary}.}",
        "\\label{tab:d29pr}",
        "\\centering\\scriptsize",
        "\\setlength{\\tabcolsep}{2.5pt}",
        "\\begin{tabular}{llllllll}",
        "\\toprule",
        "model & head (tags) & ROC & AP \\lparm{} / \\lastarm{} & AP difference [95\\% $t$] & AP rel. & "
        "trapezoid & rel.\\\\",
        "\\midrule",
    ]
    last = None
    for r in c1:
        if r["setting"] != last:
            L.append("\\multicolumn{8}{l}{\\emph{" + r["setting"].replace("'", "'") + "}}\\\\")
            last = r["setting"]
        a, z = r["avg_precision"], r["pr_auc_trapz"]
        L.append(
            f"{r['model'].replace('biot', 'BIOT').replace('cbramod', 'CBraMod')} & {TEXHEAD[r['head']]} "
            f"({r['tags'].replace('_', chr(92) + '_')}) & {tn(r['roc_auc']['mean'])} "
            f"{LETTER[r['roc_auc']['rule']]} & {tn(a['base'], sign=False)} / {tn(a['arm'], sign=False)} & "
            f"{tn(a['mean'])}{DAG if a['excludes_0'] else ''} {tci(a)} & {tpct(a)} & "
            f"{tn(z['mean'])}{DAG if z['excludes_0'] else ''} & {tpct(z)}\\\\"
        )
    L += [
        "\\bottomrule",
        "\\end{tabular}",
        "\\end{table}",
        "% src: artifacts/analysis/D29/pr_auc.md section 1 (AP and trapezoid rows) and 1b (ROC reference);",
        "% artifacts/analysis/D29/d29.json \"pr\".\"C1\"; the reading itself: d29.json \"pr\".\"reading\"",
        "",
        "% ===== Table 2 of 2: C2/C3 and the noise arm =====",
        "\\begin{table}[!htbp]",
        "\\caption{D29 PR-AUC readings of C2/C3 and of the noise arm (descriptive), in average precision",
        "($\\times100$), with no threshold applied: spans over the curve points ($N$ 896--4174 and $P$ 2/5/10 at",
        "$N$ 2048; 4 points for the CBraMod control). \\emph{curve $-$ LP} and \\emph{vs \\lastnoise} give the",
        "range of the per-point differences and, in the next column, of the changes relative to the baseline arm;",
        "\\emph{excl.} counts the points whose 95\\% $t$-interval excludes 0 (the only inference claim), and the",
        "number in brackets the points whose wider Nadeau-Bengio interval also does (that interval is defined for",
        "the rotation settings only). Units: 5 rotation means of 3",
        "seeds on Siena, 5 seeds on DL's split for BIOT; CBraMod on DL's split has a single curve seed, so no",
        "interval exists for that row. DL's split: as in Table~\\ref{tab:c2c3}; Siena: BIOT the D29 runs, CBraMod",
        "the fixed-compute control at seed $S_r$ (linear head only, no noise arm). The trapezoid PR-AUC gives the",
        f"same picture throughout (it differs from AP by at most {gap:.2f} points in any contrast); per-point",
        "numbers and intervals for both metrics are in \\texttt{artifacts/analysis/D29/pr\\_auc.md}.}",
        "\\label{tab:d29prc}",
        "\\centering\\scriptsize",
        "\\setlength{\\tabcolsep}{2pt}",
        "\\begin{tabular}{llllllll}",
        "\\toprule",
        "setting & model, head & LP & curve & curve $-$ LP & rel. & vs \\lastnoise & rel.\\\\",
        "\\midrule",
    ]
    for setting, mh, lp, vs, nz in rows_b:
        xs = list(vs.values())
        cv = [x["arm"] for x in xs]
        nex = f"{sum(1 for x in xs if x['excludes_0'])}/{len(xs)}" if xs[0]["t"] else "--"
        nbx = (
            f" [{sum(1 for x in xs if x['nb']['ci95'][0] > 0 or x['nb']['ci95'][1] < 0)}]"
            if "nb" in xs[0]
            else ""
        )
        if nz is None:
            ncell, nrel = "--", "--"
        else:
            ns = list(nz.values())
            ncell = (
                f"{tspan(ns)} ({sum(1 for x in ns if x['excludes_0'])}/{len(ns)}"
                f" [{sum(1 for x in ns if x['nb']['ci95'][0] > 0 or x['nb']['ci95'][1] < 0)}])"
            )
            nrel = f"{tn(min(x['rel_pct'] for x in ns), 1)} to {tn(max(x['rel_pct'] for x in ns), 1)}\\%"
        L.append(
            f"{setting} & {mh.replace('biot', 'BIOT').replace('cbramod', 'CBraMod')} & "
            f"{tn(lp, sign=False)} & {tn(min(cv), sign=False)}--{tn(max(cv), sign=False)} & "
            f"{tspan(xs)} ({nex}{nbx}) & {tn(min(x['rel_pct'] for x in xs), 1)} to "
            f"{tn(max(x['rel_pct'] for x in xs), 1)}\\% & {ncell} & {nrel}\\\\"
        )
    sl = rot_pr[("Siena", "linear", "avg_precision")]
    ex = next(r for r in c1 if (r["setting"], r["model"], r["head"]) == ("Siena", "biot", "linear"))
    exa, nexc = ex["avg_precision"], len([1 for r in c1 for k in PR if r[k]["excludes_0"]])
    nsl = list(sl["vs_noise"].values())
    arm = "\\lastnoise{}"
    L += [
        "\\bottomrule",
        "\\end{tabular}",
        "\\end{table}",
        "% src: artifacts/analysis/D29/pr_auc.md sections 2 (DL's split), 3 (vs LP), 4 (noise arm) and 5",
        "% (CBraMod control); artifacts/analysis/D29/d29.json \"pr\".\"C2C3_dl_split\" / \"C2C3_rotations\"",
        "",
        "% ===== Appendix paragraph (replaces the \"PR-AUC (descriptive)\" paragraph of app-c-robust.tex) =====",
        "\\emph{PR-AUC (descriptive).} We read C1, C2 and C3 again in average precision (AP) and in the trapezoid",
        "PR-AUC of the release, and we do not carry the $\\pm3$-point margin of our ROC rules over to them: that",
        "margin was fixed for ROC-AUC, no PR-AUC margin was pre-registered, and AP sits near the test prevalence",
        "(1.49\\% on DL's split, 0.16--0.66\\% on the CHB-MIT rotations, 0.43--0.99\\% on Siena), so one fixed",
        "margin would mean very different things across these settings. We therefore report, for each contrast,",
        "the two arm means, the difference with its 95\\% $t$-interval over the units, the change relative to the",
        "baseline arm, and whether the interval excludes 0; we attach no practical-importance label, and a",
        "relative change should always be read next to the baseline printed beside it, since a percentage on a",
        f"near-prevalence baseline is unstable. In Table~\\ref{{tab:d29pr}}, {nexc} of {2 * len(c1)} C1 contrasts",
        "have an interval that excludes 0, all of them positive; the largest relative change is Siena BIOT with",
        f"the raw head, where AP moves from {exa['base']:.2f} to {exa['arm']:.2f} ({tn(exa['mean'])}",
        f"{tci(exa)}, about {tn(exa['rel_pct'], 0)}\\% of that {exa['base']:.2f}-point baseline) --- the same",
        f"comparison that reads a consistent difference of {tn(ex['roc_auc']['mean'])} ROC points. On C2/C3",
        f"(Table~\\ref{{tab:d29prc}}) the Siena BIOT raw-head curve sits {tspan(list(sl['vs_lp'].values()))} AP",
        f"points above LP at every subset and {tspan(nsl)} above its own {arm} arm; the EEG-versus-noise",
        "difference is the one that also survives the wider Nadeau-Bengio interval at every subset, while the",
        f"gain over LP does not, and {arm} itself reaches {min(sl['curve']['last_noise'].values()):.2f} to",
        f"{max(sl['curve']['last_noise'].values()):.2f} AP against LP {sl['lp']:.2f}, so most of the gain over LP",
        "is reproduced by perturbing with noise rather than by the EEG data. In every other row of that table",
        "the intervals include 0 on both PR metrics, or (CBraMod on DL's split, one curve seed) no interval",
        "exists. None of this changes a ROC reading: the D29 noise rule",
        "still reads ``no difference demonstrated'' on ROC-AUC, where the same contrast has means of about $+3$",
        "to $+4$ points with intervals that include 0.",
        "% src: artifacts/analysis/D29/README.md \"PR-AUC readings\" (the reading, prevalence, the C1 rows whose",
        "% interval excludes 0, the rotation span table and its reading paragraph); pr_auc.md sections 1-6",
        "",
        "% ===== Main-text sentence (one sentence; place where the PR-AUC aside is made) =====",
        "We also read precision-recall performance without the $\\pm3$-point margin of our ROC rules, which was",
        "never defined for it: the adaptation differences that ROC-AUC resolves are small in absolute average",
        f"precision but large next to a near-prevalence baseline (Siena BIOT, raw head: {exa['base']:.2f} to",
        f"{exa['arm']:.2f} AP, {tn(exa['mean'])} {tci(exa)}, about {tn(exa['rel_pct'], 0)}\\% of the",
        "\\lparm{} baseline), and we report them as measured differences with intervals rather than labelling",
        "them against a ROC-scale threshold (Appendix~\\ref{app:d29}).",
        "% src: artifacts/analysis/D29/README.md \"PR-AUC readings\"; the ROC readings are unchanged",
    ]
    return L


# ---- readings ----------------------------------------------------------------------------------------
def rot_curves(rec, t: str, head: str, metric: str) -> dict:
    """arm -> sub -> rot -> [3 seed values]; 'LP' under arm 'lp'."""
    out: dict = {"last": {}, "last_noise": {}, "lp": {}}
    for arm in ("last", "last_noise"):
        for sub in SUBS:
            out[arm][sub] = {
                rot: [
                    m(rec, (f"{t}C{2 if sub in NB else 3}D-{sub}", "biot", arm, rot, s), head, metric)
                    for s in seeds3(r)
                ]
                for r, rot in enumerate(ROTS)
            }
    out["lp"]["LP"] = {
        rot: [m(rec, (f"{t}LPBD", "biot", "lp", rot, s), head, metric) for s in seeds3(r)]
        for r, rot in enumerate(ROTS)
    }
    return out


def grand(cell: dict) -> float:
    return float(np.mean([np.mean(v) for v in cell.values()]))


def rule_block(rec, t: str, name: str, head: str, metric: str, ratio: float) -> dict:
    cv = rot_curves(rec, t, head, metric)
    lp = grand(cv["lp"]["LP"])
    out = {
        "lp": lp,
        "lp_rot": {rot: float(np.mean(v)) for rot, v in cv["lp"]["LP"].items()},
        "curve": {arm: {sub: grand(cv[arm][sub]) for sub in SUBS} for arm in ("last", "last_noise")},
        "rot_means": {
            arm: {sub: {rot: float(np.mean(v)) for rot, v in cv[arm][sub].items()} for sub in SUBS}
            for arm in ("last", "last_noise")
        },
        "seed_values": cv,
    }
    out["verdicts"] = {
        "last (PRIMARY)": verdicts(out["curve"]["last"], lp, NB, PB),
        "last_noise (descriptive)": verdicts(out["curve"]["last_noise"], lp, NB, PB),
    }
    out["per_rotation"] = {
        rot: verdicts({s: out["rot_means"]["last"][s][rot] for s in SUBS}, out["lp_rot"][rot], NB, PB)
        for rot in ROTS
    }
    noise = {}
    for sub in SUBS:
        per_seed = {
            rot: [a - b for a, b in zip(cv["last"][sub][rot], cv["last_noise"][sub][rot], strict=True)]
            for rot in ROTS
        }
        t_ = tint([np.mean(v) for v in per_seed.values()], ratio)
        t_["per_seed"] = per_seed
        t_["passes"] = passes(t_)
        t_["d19"] = d19(t_["units"])  # the older D19 three-way string, descriptive only
        noise[sub] = t_
    out["noise"] = noise
    out["noise_verdict"] = {
        "C2": noise_verdict([noise[s] for s in NB]),
        "C3": noise_verdict([noise[s] for s in PB]),
    }
    return out


def c1_cell(d, last: float, lp: float, metric: str, unit: str, ratio: float | None = None) -> dict:
    """One C1 cell: the ROC rule string on ROC, the threshold-free PR reading on AP and trapz."""
    if metric == "roc_auc":
        return {**tint(d, ratio), "rule": paired(d), "last": last, "lp": lp}
    return pr_read(d, lp, last, "lp -> last", unit, ratio)


def c1_rows(rec, ratios: dict) -> list[dict]:
    rows = []
    for head, tags in C1_PAPER:
        for model in ("biot", "cbramod"):
            row = {"setting": "DL's split", "model": model, "head": head, "tags": "+".join(tags), "unit": "seed"}
            for k in MET:
                a = [get(rec, tags, model, "last", "paper", s, head, k) for s in SR]
                b = [get(rec, tags, model, "lp", "paper", s, head, k) for s in SR]
                d = [x - y for x, y in zip(a, b, strict=True)]
                row[k] = c1_cell(d, float(np.mean(a)), float(np.mean(b)), k, "seed (one split)")
            rows.append(row)
    for setting, (rk, heads) in C1_ROT.items():
        for head, tags in heads:
            for model in ("biot", "cbramod"):
                row = {
                    "setting": setting,
                    "model": model,
                    "head": head,
                    "tags": "+".join(tags),
                    "unit": "rotation",
                }
                for k in MET:
                    a = [
                        float(np.mean([get(rec, tags, model, "last", rot, s, head, k) for s in seeds3(r)]))
                        for r, rot in enumerate(ROTS)
                    ]
                    b = [
                        float(np.mean([get(rec, tags, model, "lp", rot, s, head, k) for s in seeds3(r)]))
                        for r, rot in enumerate(ROTS)
                    ]
                    d = [x - y for x, y in zip(a, b, strict=True)]
                    row[k] = c1_cell(
                        d, float(np.mean(a)), float(np.mean(b)), k, "rotation mean of 3 seeds", ratios[rk]
                    )
                rows.append(row)
    for r in rows:  # loader check: the published ROC means
        pub = C1_PUBLISHED.get((r["setting"], r["model"], r["head"]))
        if pub is not None:
            assert abs(r["roc_auc"]["mean"] - pub) <= 0.05 + 1e-9, (
                r["setting"],
                r["model"],
                r["head"],
                r["roc_auc"]["mean"],
                pub,
            )
    return rows


def pr_rot_block(rec, t: str, head: str, metric: str, ratio: float) -> dict:
    """C2/C3 on the rotations, PR-AUC reading: every curve point against LP and against its own noise
    arm, threshold-free. Units = the 5 rotation means of 3 seeds (paired seeds for the noise arm)."""
    cv = rot_curves(rec, t, head, metric)
    lp_rot = {rot: float(np.mean(v)) for rot, v in cv["lp"]["LP"].items()}
    curve = {arm: {sub: grand(cv[arm][sub]) for sub in SUBS} for arm in ("last", "last_noise")}
    out = {"lp": grand(cv["lp"]["LP"]), "lp_rot": lp_rot, "curve": curve, "vs_lp": {}, "vs_noise": {}}
    for sub in SUBS:
        last_rot = {rot: float(np.mean(v)) for rot, v in cv["last"][sub].items()}
        ls, ns = cv["last"][sub], cv["last_noise"][sub]
        out["vs_lp"][sub] = pr_read(
            [last_rot[rot] - lp_rot[rot] for rot in ROTS],
            out["lp"],
            curve["last"][sub],
            f"LP -> last at {sub}",
            "rotation mean of 3 seeds",
            ratio,
        )
        out["vs_noise"][sub] = pr_read(
            [
                float(np.mean([a - b for a, b in zip(ls[rot], ns[rot], strict=True)]))
                for rot in ROTS
            ],
            curve["last_noise"][sub],
            curve["last"][sub],
            f"last_noise -> last at {sub}",
            "rotation mean of 3 paired seeds",
            ratio,
        )
    return out


def paper_c2c3(rec) -> dict:
    """DL's split: BIOT 5-seed mean at data_seed 1 (E30a primary), CBraMod seed 42 (D24-C) vs R3E-b128.

    ROC keeps the E30 verdicts. AP and trapz get the threshold-free reading of every curve point
    against LP, paired by seed (CBraMod has one curve seed, so there is no interval for it)."""
    out = {}
    for model, seeds in (("biot", SR), ("cbramod", (42,))):
        out[model] = {}
        for k in MET:
            vals = {
                sub: {
                    s: m(
                        rec,
                        (f"{'C2' if sub in NA else 'C3'}{'E' if s == 42 else 'X'}-{sub}", model, "last", "paper",
                         s),
                        "linear",
                        k,
                    )
                    for s in seeds
                }
                for sub in NA + PA
            }
            cur = {sub: float(np.mean(list(v.values()))) for sub, v in vals.items()}
            lp_s = {s: m(rec, ("R3E-b128", model, "lp", "paper", s), "linear", k) for s in SR}
            lp = float(np.mean(list(lp_s.values())))
            out[model][k] = {"curve": cur, "lp": lp}
            if k == "roc_auc":
                out[model][k]["verdicts"] = verdicts(cur, lp, NA, PA)
            else:
                out[model][k]["vs_lp"] = {
                    sub: pr_read(
                        [vals[sub][s] - lp_s[s] for s in seeds] if len(seeds) > 1 else [cur[sub] - lp],
                        lp,
                        cur[sub],
                        f"LP -> last at {sub}",
                        "seed (one split)" if len(seeds) > 1 else "1 seed (no interval)",
                    )
                    for sub in NA + PA
                }
    return out


def cbramod_rot(rec, t: str) -> dict:
    """CBraMod control S3CC / S3FCC at S_r vs S3CLPB / S3FCLPB at S_r (the D27-C reading).

    ROC keeps the E30 verdicts; AP and trapz get the threshold-free reading, units = the 5 rotations."""
    out = {}
    for k in MET:
        vals = {
            sub: {
                rot: m(rec, (f"{t}CC-{sub}", "cbramod", "last", rot, SR[r]), "linear", k)
                for r, rot in enumerate(ROTS)
            }
            for sub in NC + PC
        }
        cur = {sub: float(np.mean(list(v.values()))) for sub, v in vals.items()}
        lp_rot = {
            rot: m(rec, (f"{t}CLPB", "cbramod", "lp", rot, SR[r]), "linear", k) for r, rot in enumerate(ROTS)
        }
        lp = float(np.mean(list(lp_rot.values())))
        out[k] = {"curve": cur, "lp": lp}
        if k == "roc_auc":
            out[k]["verdicts"] = verdicts(cur, lp, NC, PC)
        else:
            out[k]["vs_lp"] = {
                sub: pr_read(
                    [vals[sub][rot] - lp_rot[rot] for rot in ROTS],
                    lp,
                    cur[sub],
                    f"LP -> last at {sub}",
                    "rotation (1 seed S_r each)",
                )
                for sub in NC + PC
            }
    return out


def prevalence(rec) -> dict:
    out = {}
    for name, key in (
        ("DL's split", ("P1E", "biot", "lp", "paper", 42)),
        ("CHB-MIT rotations", None),
        ("Siena", None),
        ("Siena filtered", None),
    ):
        if key:
            out[name] = 100 * rec[key]["probes"]["linear"]["test_at_best"]["prevalence"]
            continue
        tag = {"CHB-MIT rotations": "S1M", "Siena": "S3M", "Siena filtered": "S3FM"}[name]
        out[name] = [
            100 * rec[(tag, "biot", "lp", rot, SR[r])]["probes"]["linear"]["test_at_best"]["prevalence"]
            for r, rot in enumerate(ROTS)
        ]
    return out


# ---- main ----------------------------------------------------------------------------------------
def main() -> int:
    selfcheck()
    rec, notes = scan()
    n2, best_ep = d29_checks(rec)
    notes += n2
    ratios = {}
    for k in ("S1E,S1M", "S3E,S3M", "S3FE,S3FM"):
        ratios[k], _ = nb_ratio(k)
    for t, _, _ in SETTINGS:  # the NB ratio comes from the D24 unit dirs: same eval data as the D29 records
        d = "s3m" if t == "S3" else "sfm"
        for r, rot in enumerate(ROTS):
            idx = sorted((LOCAL / f"arms-biot-sie-{rot}-{d}" / "results").glob("test-index-*.json"))
            assert len(idx) == 1 and rec[(f"{t}LPBD", "biot", "lp", rot, SR[r])]["eval_hash"] in idx[0].name, rot
    notes.append(
        "- Nadeau-Bengio ratio n_test/n_train (mean over rotations, from the D24 test-index files, same "
        "eval_hash as the D29 records): " + ", ".join(f"{k} {v:.3f}" for k, v in ratios.items())
    )

    e30 = json.loads(E30_JSON.read_text())["b"]
    js: dict = {"notes": notes, "best_epoch_counts": best_ep, "nb_ratio": ratios, "rules": {}, "pr": {}}
    md = [
        "# D29: C2/C3 controls at the fixed-compute budget (Siena) and PR-AUC readings",
        "",
        'Protocol: notes/decisions.md "## D29" (frozen in git, commit c0283f4, before any D29 run). Script '
        "scripts/analysis/d29_read.py. ROC-AUC x100 at the val-selected epoch unless stated. BIOT, fixed_c "
        "(132 SSL steps, batch 128, constant lr 3e-5, lowest-loss pass restored), probes linear and linear_z at "
        "batch 128, eval mode, encoder tap; 5 rotations x 3 seeds [S_r, 1000+r, 2000+r]. Anything not called a "
        "rule is descriptive/post hoc.",
        "",
        "Rules applied: (1) the E30 C2/C3 rules (D15 text, E30 reader choices: curve and LP = mean over the 5 "
        'rotations of 3-seed means; "within 3" = |v - LP| <= 3 at every N; C3 "> 3 above LP" at every P), '
        'each head separately, LP = S3LPBD / S3FLPBD with the same head. (2) Noise control: "the plateau needs '
        'EEG data" only if at every N (every P) the 95% t-interval (df 4) of last - last_noise over the 5 '
        'rotation means excludes 0 with mean > 3; else "no difference demonstrated"; TOST margin 3 per N and '
        "P.",
        "",
    ]
    summary = ["## Verdicts (rule outputs)", ""]
    body = []
    for t, name, rk in SETTINGS:
        js["rules"][name] = {}
        for head in HEADS:
            b = rule_block(rec, t, name, head, "roc_auc", ratios[rk])
            js["rules"][name][head] = b
            v = b["verdicts"]["last (PRIMARY)"]
            if head == "linear":  # E30b reproduction at the aggregate level
                ref = e30[name]
                prim = ref["verdicts"]["BIOT, mean over 5 rotations of 3-seed means (PRIMARY)"]
                assert v == prim, (name, v, prim)
                for rot in ROTS:
                    for sub in SUBS:
                        assert b["seed_values"]["last"][sub][rot] == ref["biot_per_rotation_seed_values"][rot][sub]
                    assert b["seed_values"]["lp"]["LP"][rot] == ref["biot_per_rotation_seed_values"][rot]["LP"]
            nv = b["noise_verdict"]
            summary += [
                f"- {name}, {head}: E30 C2 **{v['C2']}** ({v['C2_numbers']}); C3 **{v['C3']}** "
                f"({v['C3_numbers']}); LP {b['lp']:.2f}",
                f"- {name}, {head}: noise control C2 **{nv['C2']}**, C3 **{nv['C3']}**; last - last_noise "
                + ", ".join(
                    f"{s} {b['noise'][s]['mean']:+.2f} {ci(b['noise'][s])} TOST p "
                    f"{tp(b['noise'][s]['t']['tost3_p'])}"
                    for s in SUBS
                ),
            ]
            cols = SUBS + ("LP",)
            body += [
                "",
                f"### {name}, head {head}",
                "",
                f"3-seed mean per rotation; LP = {t}LPBD {head} (batch 128).",
                "",
                "| arm | rotation | " + " | ".join(cols) + " |",
                "|---" * (2 + len(cols)) + "|",
            ]
            for arm in ("last", "last_noise"):
                for rot in ROTS:
                    body.append(
                        f"| {arm} | {rot} | "
                        + " | ".join(f"{b['rot_means'][arm][s][rot]:.1f}" for s in SUBS)
                        + f" | {b['lp_rot'][rot]:.1f} |"
                    )
                body.append(
                    f"| **{arm}** | **mean** | "
                    + " | ".join(f"**{b['curve'][arm][s]:.2f}**" for s in SUBS)
                    + f" | **{b['lp']:.2f}** |"
                )
            body += ["", "| reading | C2 | numbers | C3 | numbers |", "|---|---|---|---|---|"]
            for k, vv in b["verdicts"].items():
                body.append(f"| {k} | **{vv['C2']}** | {vv['C2_numbers']} | **{vv['C3']}** | {vv['C3_numbers']} |")
            c2n = Counter(x["C2"] for x in b["per_rotation"].values())
            c3n = Counter(x["C3"] for x in b["per_rotation"].values())
            body += [
                "",
                f"Per-rotation `last` verdicts vs the rotation's own LP (descriptive): C2 {dict(c2n)}; "
                f"C3 {dict(c3n)}.",
                "",
                "Noise control (rule), last - last_noise, units = 5 rotation means of 3 paired seeds:",
                "",
                "| subset | mean | sd | 95% t-interval | passes (lo > 0, mean > 3) | TOST p (margin 3) | "
                "NB 95% | TOST p NB | per rotation | > 0 | D19 string (descriptive) |",
                "|---" * 11 + "|",
            ]
            for s in SUBS:
                x = b["noise"][s]
                body.append(
                    f"| {s} | {x['mean']:+.2f} | {x['sd']:.2f} | {ci(x)} | {'yes' if x['passes'] else 'no'} | "
                    f"{tp(x['t']['tost3_p'])} | {ci(x, 'nb')} | {tp(x['nb']['tost3_p'])} | {units(x)} | "
                    f"{x['n_pos']}/5 | {x['d19']} |"
                )
            body += [
                "",
                f"Noise rule: C2 (every N) **{nv['C2']}**; C3 (every P) **{nv['C3']}**.",
                "",
                "Per-seed last - last_noise (seeds S_r / 1000+r / 2000+r):",
                "",
            ]
            body += [
                f"- {s}: "
                + "; ".join(
                    f"{rot} " + ", ".join(f"{d:+.2f}" for d in b["noise"][s]["per_seed"][rot]) for rot in ROTS
                )
                for s in SUBS
            ]

    # ---- PR-AUC readings (no ROC-derived threshold anywhere; see pr_read) ----
    prev = prevalence(rec)
    c1 = c1_rows(rec, ratios)
    pc = paper_c2c3(rec)
    js["pr"] = {
        "reading": PR_READING,
        "prevalence_test_pct": prev,
        "C1": c1,
        "C2C3_dl_split": pc,
        "C2C3_rotations": {},
    }
    prev_txt = "; ".join(
        f"{k} {v:.2f}" if isinstance(v, float) else f"{k} " + "/".join(f"{x:.2f}" for x in v)
        for k, v in prev.items()
    )
    assert pc["biot"]["roc_auc"]["verdicts"]["C2"].startswith("not testable")  # E30a primary
    assert pc["biot"]["roc_auc"]["verdicts"]["C3"] == "uninformative"
    assert pc["cbramod"]["roc_auc"]["verdicts"]["C2"].startswith("not testable")  # D24-C
    assert pc["cbramod"]["roc_auc"]["verdicts"]["C3"] == "uninformative"

    # full tables -> pr_auc.md; the C1 contrasts
    full = [
        "# D29 PR-AUC readings: full tables (no ROC-derived threshold)",
        "",
        PR_READING,
        "",
        f"Test prevalence x100 (the scale AP lives on): {prev_txt}.",
        "",
        "Script scripts/analysis/d29_read.py (one run writes README.md, this file and d29.json). Every number "
        "below is x100 at the ROC-selected probe epoch (probe selection unchanged, so these are the same fitted "
        "probes the ROC readings use). AP = average precision (sklearn), trapz = the trapezoid PR-AUC the release "
        "reports. ROC columns are shown for reference only and are unchanged from the ROC readings.",
        "",
        "## 1. C1 (SA - LP = `last` - `lp`)",
        "",
        "Units: 5 seeds on DL's split (seed uncertainty on one split), 5 rotation means of 3 seeds elsewhere. "
        "NB 95% = Nadeau-Bengio interval (rotation settings only, ratio n_test/n_train). ROC column: the D18 / "
        "D24-B rule string, which does apply to ROC (F = first term wins, S = second, N = no difference shown).",
        "",
        f"| setting | model | head (tags) | metric | unit | {PRCOLS} | NB 95% | > 0 | per unit | ROC |",
        "|---" * 15 + "|",
    ]
    for r in c1:
        for k, lab in PR.items():
            x = r[k]
            roc = f"{r['roc_auc']['mean']:+.2f} {r['roc_auc']['rule']}"
            full.append(
                f"| {r['setting']} | {r['model']} | {r['head']} ({r['tags']}) | {lab} | {x['unit']} | "
                f"{pr_row(x)} | {ci(x, 'nb') if 'nb' in x else '-'} | {x['n_pos']}/5 | {units(x)} | {roc} |"
            )
    exc_c1 = [(r, k) for r in c1 for k in PR if r[k]["excludes_0"]]
    big = sorted(exc_c1, key=lambda rk: -abs(rk[0][rk[1]]["rel_pct"]))
    full += [
        "",
        f"{len(exc_c1)} of {2 * len(c1)} C1 PR-AUC intervals exclude 0 "
        f"({sum(1 for r, k in exc_c1 if r[k]['mean'] > 0)} positive, "
        f"{sum(1 for r, k in exc_c1 if r[k]['mean'] < 0)} negative). Largest relative changes among them: "
        + "; ".join(
            f"{r['setting']} {r['model']} {r['head']} {PR[k]} {r[k]['base']:.2f} -> {r[k]['arm']:.2f} "
            f"({r[k]['mean']:+.2f}, {pct(r[k])})"
            for r, k in big[:6]
        )
        + ".",
        "",
        "### 1b. ROC reference for the same 34 rows (unchanged; the 3-point margin is a ROC margin)",
        "",
        "| setting | model | head (tags) | lp | last | last - lp | 95% t | NB 95% | TOST p (margin 3) | > 0 | "
        "rule | per unit |",
        "|---" * 12 + "|",
    ]
    for r in c1:
        x = r["roc_auc"]
        full.append(
            f"| {r['setting']} | {r['model']} | {r['head']} ({r['tags']}) | {x['lp']:.2f} | {x['last']:.2f} | "
            f"{x['mean']:+.2f} | {ci(x)} | {ci(x, 'nb') if 'nb' in x else '-'} | {tp(x['t']['tost3_p'])} | "
            f"{x['n_pos']}/5 | {x['rule']} | {units(x)} |"
        )

    # C2/C3 on DL's split
    full += [
        "",
        "## 2. C2/C3 on DL's split (CHB-MIT paper split; E30a / D24-C records)",
        "",
        "Every curve point against LP. BIOT: 5 seeds at data_seed 1 (C2E seed 42 + C2X/C3X), paired by seed "
        "with the R3E-b128 LP. CBraMod: one curve seed (42, as D24-C) against the 5-seed LP mean, so there is "
        "no interval and no inference claim at all for CBraMod here.",
        "",
        f"| model | metric | point | unit | {PRCOLS} | per unit |",
        "|---" * 11 + "|",
    ]
    for model, d in pc.items():
        for k, lab in PR.items():
            for sub in NA + PA:
                x = d[k]["vs_lp"][sub]
                full.append(f"| {model} | {lab} | {sub} | {x['unit']} | {pr_row(x)} | {units(x)} |")
    full += [
        "",
        "ROC reference for the same curves (unchanged; the E30 rules do apply to ROC):",
        "",
        "| model | " + " | ".join(NA + PA) + " | LP | C2 | numbers | C3 | numbers |",
        "|---" * (6 + len(NA + PA)) + "|",
    ]
    for model, d in pc.items():
        x = d["roc_auc"]
        v = x["verdicts"]
        full.append(
            f"| {model} | "
            + " | ".join(f"{x['curve'][s]:.2f}" for s in NA + PA)
            + f" | {x['lp']:.2f} | {v['C2']} | {v['C2_numbers']} | {v['C3']} | {v['C3_numbers']} |"
        )

    # C2/C3 on the rotations: vs LP, and the noise arm
    rot_pr: dict = {}
    for t, name, rk in SETTINGS:
        js["pr"]["C2C3_rotations"][name] = {"biot": {}, "cbramod": cbramod_rot(rec, t)}
        for head in HEADS:
            js["pr"]["C2C3_rotations"][name]["biot"][head] = {}
            for k in MET:
                b = rule_block(rec, t, name, head, k, ratios[rk]) if k == "roc_auc" else pr_rot_block(
                    rec, t, head, k, ratios[rk]
                )
                b.pop("seed_values", None)
                js["pr"]["C2C3_rotations"][name]["biot"][head][k] = b
                rot_pr[(name, head, k)] = b
        cb = js["pr"]["C2C3_rotations"][name]["cbramod"]
        assert cb["roc_auc"]["verdicts"]["C2"].startswith("not testable"), cb["roc_auc"]  # D27-C
        assert cb["roc_auc"]["verdicts"]["C3"] == "uninformative", cb["roc_auc"]
    full += [
        "",
        "## 3. C2/C3 on the Siena rotations, BIOT: every curve point against LP",
        "",
        "The D29 records (`last`; LP = S3LPBD / S3FLPBD, same head). Units = the 5 rotation means of 3 seeds. "
        "N896-N4174 are the C2 ladder, P2-P10 the C3 points at N2048.",
        "",
        f"| setting | head | metric | point | {PRCOLS} | NB 95% | > 0 |",
        "|---" * 12 + "|",
    ]
    for (name, head, k), b in rot_pr.items():
        if k == "roc_auc":
            continue
        for sub in SUBS:
            x = b["vs_lp"][sub]
            full.append(
                f"| {name} | {head} | {PR[k]} | {sub} | {pr_row(x)} | {ci(x, 'nb')} | {x['n_pos']}/5 |"
            )
    full += [
        "",
        "## 4. The noise arm on the rotations, BIOT: `last` against `last_noise`",
        "",
        "Same subset, SSL input replaced by noise. Units = the 5 rotation means of 3 paired seeds. The D29 "
        'noise rule ("mean > 3 and the interval excludes 0") is a ROC rule and is NOT applied here; the '
        "columns below are the measurement.",
        "",
        f"| setting | head | metric | point | {PRCOLS} | NB 95% | > 0 |",
        "|---" * 12 + "|",
    ]
    for (name, head, k), b in rot_pr.items():
        if k == "roc_auc":
            continue
        for sub in SUBS:
            x = b["vs_noise"][sub]
            full.append(
                f"| {name} | {head} | {PR[k]} | {sub} | {pr_row(x)} | {ci(x, 'nb')} | {x['n_pos']}/5 |"
            )
    full += [
        "",
        "## 5. The CBraMod fixed-compute control on the rotations (D27-C reading)",
        "",
        "S3CC / S3FCC `last` at seed S_r against its batch-128 LP S3CLPB / S3FCLPB at S_r; linear head only "
        "(no CBraMod linear_z or noise run at fixed compute). Units = the 5 rotations, 1 seed each.",
        "",
        f"| setting | metric | point | {PRCOLS} | > 0 |",
        "|---" * 10 + "|",
    ]
    for name, d in js["pr"]["C2C3_rotations"].items():
        for k, lab in PR.items():
            for sub in NC + PC:
                x = d["cbramod"][k]["vs_lp"][sub]
                full.append(f"| {name} | {lab} | {sub} | {pr_row(x)} | {x['n_pos']}/5 |")
    full += [
        "",
        "ROC reference for the same control (unchanged):",
        "",
        "| setting | " + " | ".join(NC + PC) + " | LP | C2 | numbers | C3 | numbers |",
        "|---" * (6 + len(NC + PC)) + "|",
    ]
    for name, d in js["pr"]["C2C3_rotations"].items():
        x = d["cbramod"]["roc_auc"]
        v = x["verdicts"]
        full.append(
            f"| {name} | "
            + " | ".join(f"{x['curve'][s]:.2f}" for s in NC + PC)
            + f" | {x['lp']:.2f} | {v['C2']} | {v['C2_numbers']} | {v['C3']} | {v['C3_numbers']} |"
        )

    rot_rows = [
        (f"{name} biot {head}", PR[k], sub, which, b[which][sub])
        for (name, head, k), b in rot_pr.items()
        if k != "roc_auc"
        for which in ("vs_lp", "vs_noise")
        for sub in SUBS
    ] + [
        (f"{name} cbramod linear", PR[k], sub, "vs_lp", d["cbramod"][k]["vs_lp"][sub])
        for name, d in js["pr"]["C2C3_rotations"].items()
        for k in PR
        for sub in NC + PC
    ]
    dl_rows = [
        (f"DL's split {model}", PR[k], sub, "vs_lp", d[k]["vs_lp"][sub])
        for model, d in pc.items()
        for k in PR
        for sub in NA + PA
    ]
    allp = [x for *_, x in rot_rows + dl_rows]
    cnt = Counter(
        "no interval (1 unit)"
        if x["excludes_0"] is None
        else "excludes 0, positive"
        if x["excludes_0"] and x["mean"] > 0
        else "excludes 0, negative"
        if x["excludes_0"]
        else "includes 0"
        for x in allp
    )
    js["pr"]["counts"] = {
        "C1_contrasts": 2 * len(c1),
        "C1_excludes_0": len(exc_c1),
        "C1_excludes_0_positive": sum(1 for r, k in exc_c1 if r[k]["mean"] > 0),
        "C2C3_contrasts": dict(sorted(cnt.items())),
    }
    js["pr"]["C1_excludes_0"] = [
        {
            "setting": r["setting"],
            "model": r["model"],
            "head": r["head"],
            "tags": r["tags"],
            "metric": PR[k],
            **{q: r[k][q] for q in ("unit", "base", "arm", "mean", "rel_pct")},
            "ci95": r[k]["t"]["ci95"],
            "roc_mean": r["roc_auc"]["mean"],
            "roc_rule": r["roc_auc"]["rule"],
        }
        for r, k in exc_c1
    ]
    full += [
        "",
        "## 6. Counts",
        "",
        f"- C1: {len(exc_c1)} of {2 * len(c1)} PR-AUC intervals exclude 0.",
        f"- C2/C3 and noise contrasts ({len(allp)} PR-AUC readings): "
        + ", ".join(f"{k} {v}" for k, v in sorted(cnt.items())),
        "- No practical-importance label is attached to any of them: no PR-AUC margin is defined (see the "
        "statement at the top of this file).",
        "",
        "## Commands",
        "",
        "```",
        ".venv/bin/python scripts/analysis/d29_read.py",
        "```",
    ]

    # README section: the new reading, the decisive rows, and a pointer to the full tables
    pr = [
        "",
        "## PR-AUC readings (descriptive; D29 PR-AUC item; re-read 2026-11-05 without any ROC threshold)",
        "",
        PR_READING,
        "",
        f"Test prevalence x100 (the scale AP lives on): {prev_txt}.",
        "",
        "**Full tables for every contrast (C1, C2/C3 on DL's split and on the rotations, the noise arm, both "
        "PR metrics): artifacts/analysis/D29/pr_auc.md.** The rows below are the ones whose interval excludes 0.",
        "",
        "### C1 (SA - LP = last - lp): the intervals that exclude 0",
        "",
        f"{len(exc_c1)} of {2 * len(c1)} C1 PR-AUC contrasts ({len(c1)} rows x 2 metrics) have an interval that "
        f"excludes 0: {sum(1 for r, k in exc_c1 if r[k]['mean'] > 0)} positive, "
        f"{sum(1 for r, k in exc_c1 if r[k]['mean'] < 0)} negative. Units: 5 seeds on DL's split, 5 rotation "
        "means of 3 seeds elsewhere. ROC column for reference (unchanged, with its D18 rule string).",
        "",
        f"| setting | model | head (tags) | metric | unit | {PRCOLS} | per unit | ROC |",
        "|---" * 13 + "|",
    ]
    for r, k in exc_c1:
        x = r[k]
        pr.append(
            f"| {r['setting']} | {r['model']} | {r['head']} ({r['tags']}) | {PR[k]} | {x['unit']} | "
            f"{pr_row(x)} | {units(x)} | {r['roc_auc']['mean']:+.2f} {r['roc_auc']['rule']} |"
        )
    ex = next(r for r in c1 if (r["setting"], r["model"], r["head"]) == ("Siena", "biot", "linear"))
    pr += [
        "",
        "The review's example, re-read: Siena BIOT raw head (S3E+S3M, linear). AP "
        f"{ex['avg_precision']['base']:.2f} -> {ex['avg_precision']['arm']:.2f}, "
        f"{ex['avg_precision']['mean']:+.2f} {ci(ex['avg_precision'])}, {pct(ex['avg_precision'])} relative on a "
        f"baseline of {ex['avg_precision']['base']:.2f} AP points; trapz {ex['pr_auc_trapz']['base']:.2f} -> "
        f"{ex['pr_auc_trapz']['arm']:.2f}, {ex['pr_auc_trapz']['mean']:+.2f} {ci(ex['pr_auc_trapz'])}, "
        f"{pct(ex['pr_auc_trapz'])}. Both intervals exclude 0; the AP baseline sits near the test prevalence "
        "(0.43 to 0.99 per rotation), which is why the relative change is large and why it is also unstable. The "
        'earlier reading labelled this "no difference shown" because 0.55 < 3, the ROC margin; that label is '
        "withdrawn.",
        "",
        "### C2/C3 (DL's split and the rotations) and the noise arm",
        "",
        f"{len(allp)} PR-AUC readings (every curve point against LP, and `last` against `last_noise` on the "
        "rotations): " + ", ".join(f"{k} {v}" for k, v in sorted(cnt.items())) + ". Full numbers in pr_auc.md "
        "sections 2-5. Spans over the 7 subsets (N896-N4174 and P2/P5/P10 at N2048) of the rotation contrasts, "
        "BIOT, units = 5 rotation means; `excl 0` counts the subsets whose t-interval excludes 0, `NB` the same "
        "with the Nadeau-Bengio interval:",
        "",
        "| setting | head | metric | vs LP: LP; curve | difference | relative | excl 0 | NB | "
        "vs last_noise: difference | relative | excl 0 | NB |",
        "|---" * 12 + "|",
    ]
    for (name, head, k), b in rot_pr.items():
        if k == "roc_auc":
            continue
        cells = []
        for which in ("vs_lp", "vs_noise"):
            xs = [b[which][sub] for sub in SUBS]
            cells.append(
                f"{min(x['mean'] for x in xs):+.2f} to {max(x['mean'] for x in xs):+.2f} | "
                f"{min(x['rel_pct'] for x in xs):+.1f}% to {max(x['rel_pct'] for x in xs):+.1f}% | "
                f"{sum(x['excludes_0'] for x in xs)}/7 | "
                f"{sum(1 for x in xs if x['nb']['ci95'][0] > 0 or x['nb']['ci95'][1] < 0)}/7"
            )
        cv = [b["curve"]["last"][sub] for sub in SUBS]
        pr.append(
            f"| {name} | {head} | {PR[k]} | {b['lp']:.2f}; {min(cv):.2f}-{max(cv):.2f} | {cells[0]} | {cells[1]} |"
        )
    sl = rot_pr[("Siena", "linear", "avg_precision")]
    nsl = [js["rules"]["Siena"]["linear"]["noise"][sub]["mean"] for sub in SUBS]
    pr += [
        "",
        "Reading of that table: on Siena with the raw head the `last` curve sits about "
        f"{min(x['mean'] for x in sl['vs_lp'].values()):+.2f} to "
        f"{max(x['mean'] for x in sl['vs_lp'].values()):+.2f} AP points above LP "
        f"({min(x['rel_pct'] for x in sl['vs_lp'].values()):.0f}% to "
        f"{max(x['rel_pct'] for x in sl['vs_lp'].values()):.0f}% of a {sl['lp']:.2f}-point baseline) and "
        f"{min(x['mean'] for x in sl['vs_noise'].values()):+.2f} to "
        f"{max(x['mean'] for x in sl['vs_noise'].values()):+.2f} above its own noise arm "
        f"({min(x['rel_pct'] for x in sl['vs_noise'].values()):.0f}% to "
        f"{max(x['rel_pct'] for x in sl['vs_noise'].values()):.0f}%). The EEG-vs-noise difference is the one "
        "that also survives the Nadeau-Bengio interval (7 of 7 subsets); the gain over LP does not (0 of 7). "
        f"`last_noise` itself sits above LP ({min(sl['curve']['last_noise'].values()):.2f} to "
        f"{max(sl['curve']['last_noise'].values()):.2f} against {sl['lp']:.2f} AP), so most of the gain over LP "
        "is reproduced by perturbing with noise. With the standardized head, and on filtered Siena, every "
        "interval includes 0. The ROC reading of the same noise contrast does not resolve it either way (means "
        f"{min(nsl):+.2f} to {max(nsl):+.2f} ROC points, intervals include 0, so the D29 noise rule reads "
        '"no difference demonstrated"); that ROC verdict stands and is not a PR-AUC claim.',
        "",
        "DL's split C2/C3 (pr_auc.md section 2): BIOT every point vs LP "
        + "; ".join(
            f"{PR[k]} {min(x['mean'] for x in pc['biot'][k]['vs_lp'].values()):+.2f} to "
            f"{max(x['mean'] for x in pc['biot'][k]['vs_lp'].values()):+.2f} "
            f"(LP {pc['biot'][k]['lp']:.2f}, {sum(x['excludes_0'] for x in pc['biot'][k]['vs_lp'].values())}/7 "
            "exclude 0)"
            for k in PR
        )
        + "; CBraMod has one curve seed, so no interval. CBraMod fixed-compute control on the rotations "
        "(section 5): "
        + "; ".join(
            f"{name} {PR[k]} {min(x['mean'] for x in d['cbramod'][k]['vs_lp'].values()):+.2f} to "
            f"{max(x['mean'] for x in d['cbramod'][k]['vs_lp'].values()):+.2f} "
            f"(LP {d['cbramod'][k]['lp']:.2f}, "
            f"{sum(x['excludes_0'] for x in d['cbramod'][k]['vs_lp'].values())}/4 exclude 0)"
            for name, d in js["pr"]["C2C3_rotations"].items()
            for k in PR
        )
        + ".",
    ]
    summary += [
        "",
        "Descriptive (no rule):",
        "",
        "- older D19 three-way string on last - last_noise (the E27 / D27-A rule): "
        + "; ".join(
            f"{name} {h}: " + ", ".join(f"{s} {js['rules'][name][h]['noise'][s]['d19']}" for s in SUBS)
            for _, name, _ in SETTINGS
            for h in HEADS
        ),
        "- PR-AUC (re-read 2026-11-05): no ROC-derived threshold and no practical-importance label is applied "
        f"to a PR-AUC contrast. C1: {len(exc_c1)} of {2 * len(c1)} intervals exclude 0; C2/C3 and noise: "
        + ", ".join(f"{k} {v}" for k, v in sorted(cnt.items()))
        + ". Full tables: artifacts/analysis/D29/pr_auc.md.",
    ]

    md += summary + ["", "## Record checks", ""] + notes + ["", "## Rule readings (ROC)"] + body + pr
    md += [
        "",
        "## Commands",
        "",
        "```",
        ".venv/bin/python scripts/analysis/d29_read.py",
        "# inputs: artifacts/s3-results (synced); specs: scripts/submit_d25.sh (want D29; E30 for the pairs)",
        ".venv/bin/python -m pytest -q && .venv/bin/python -m ruff check src tests scripts sm_entry.py",
        "```",
        "",
    ]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "README.md").write_text("\n".join(md) + "\n")
    (OUT / "pr_auc.md").write_text("\n".join(full) + "\n")
    (OUT / "pr_auc_table.tex").write_text(
        "\n".join(tex_tables(c1, pc, rot_pr, js["pr"]["C2C3_rotations"])) + "\n"
    )
    (OUT / "d29.json").write_text(json.dumps(js, indent=1, default=str))
    print("\n".join(summary + [""] + notes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
