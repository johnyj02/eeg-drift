#!/usr/bin/env python3
"""D25 items E10 and E22 (notes/completeness-audit.md) on the D24 records. Post hoc and descriptive:
the D24 verdicts stay primary. CPU only, about a minute.

    .venv/bin/python scripts/analysis/stats_d25.py

E10, for every D24-A/B contrast and D17 (units: the 5 rotation means of D24-A, the 5 seeds of D24-B):
  (a) t-interval, df 4; (b) Nadeau-Bengio corrected interval, n_test/n_train from the test-index
  sizes; (c) the pre-registered D24-D bootstrap, recomputed with bootstrap_d24's RNG stream and
  checked against artifacts/tables/d24-bootstrap.md; (d) one-sided 95% bounds, TOST at +-1/2/3 and
  a test against the paper's gains (+36.2 BIOT, +29.5 CBraMod); (e) verdicts over thresholds 0-10 x
  k in {3, 4, 5}, flip points, leave-one-out; (f) power / false positives of the 3-point 4/5 rule
  under normal, t3 and centred-resample errors at each contrast's SD; (g) Holm within the families
  C1, Artifact 1, features, D17 with exact sign-flip p; (h) variance components (rotation, seed,
  subject; subject level from the npz scores, labels and pooled ROC checked against the records).
E22: CBraMod D24-A without the S_r seeds; P/P*/H/D tags; deviations; decision timestamps against
local file mtimes (aws s3 sync keeps S3 LastModified as the mtime; no AWS call is made).
Reads records only through scripts/read_d24.load. Writes artifacts/analysis/stats/.
"""

from __future__ import annotations

import itertools
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))
from bootstrap_d24 import CONTRASTS, SETS, cluster_ci  # noqa: E402
from read_d24 import ARMS, ROTS, load  # noqa: E402
from read_step1 import d17, paired  # noqa: E402

from eegdrift.data.chbmit import overlap_label  # noqa: E402

LOCAL = ROOT / "artifacts" / "s3-results"
OUT = ROOT / "artifacts" / "analysis" / "stats"
PT = ZoneInfo("America/Los_Angeles")
SETTING = {"S1E,S1M": "CHB-MIT", "S3E,S3M": "Siena", "S3FE,S3FM": "Siena filtered", "P1E": "paper split"}
UNIT_DIR = {
    "S1E,S1M": "arms-biot-chb-rot{r}-s1m",
    "S3E,S3M": "arms-biot-sie-rot{r}-s3m",
    "S3FE,S3FM": "arms-biot-sie-rot{r}-sfm",
}
FAMILY = {
    ("last", "lp"): "C1",
    ("last_randinit", "last"): "Artifact 1",
    ("lp", "lp_randinit"): "features",
    ("last_randinit", "lp_randinit"): "D17",
    ("all", "last"): "reference",
}
FAMS = ("C1", "Artifact 1", "features", "D17", "reference")
PAPER_GAIN = {"biot": 36.2, "cbramod": 29.5}  # paper Table 1 SA - LP, as E10(d) states them
S_R = (42, 123, 2021, 3407, 8888)
THRS = np.arange(0, 10.01, 0.5)
R_SIM = 200_000
ERRS = ("normal", "t3", "resample")
SIGNS = np.array(list(itertools.product((1, -1), repeat=5)))
INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"
C_T, C_NB, C_BOOT = "#2a78d6", "#eb6834", "#1baf7a"  # categorical slots 1-3 (dataviz reference palette)


# ---------- E10 statistics ----------


def rule(u, thr: float = 3.0, k: int | None = None, d17_row: bool = False) -> str:
    """D18 paired rule generalised to (thr, k): '+' first wins, '-' second wins, '.' none; 'E' = D17 equiv."""
    x = np.asarray(u, dtype=float)
    k = len(x) - 1 if k is None else k
    m = x.mean()
    if d17_row and abs(m) <= thr:
        return "E"
    if m > thr and (x > 0).sum() >= k:
        return "+"
    if m < -thr and (x < 0).sum() >= k:
        return "-"
    return "."


def rule_edges(E: np.ndarray, thr: float = 3.0, k: int = 4) -> tuple[np.ndarray, np.ndarray]:
    """Per replicate of errors E (R x n): 'first wins' iff the true effect > up, 'second wins' iff < down."""
    s = np.sort(E, axis=1)
    m = E.mean(axis=1)
    n = E.shape[1]
    return np.maximum(thr - m, -s[:, n - k]), np.minimum(-thr - m, -s[:, k - 1])


def errors(u, kind: str, rng: np.random.Generator, R: int = R_SIM) -> np.ndarray:
    u = np.asarray(u, dtype=float)
    n, sd = len(u), u.std(ddof=1)
    if kind == "normal":
        return rng.standard_normal((R, n)) * sd
    if kind == "t3":
        return rng.standard_t(3, (R, n)) * sd / np.sqrt(3)  # t3 variance is 3
    return rng.choice((u - u.mean()) * np.sqrt(n / (n - 1)), (R, n))  # centred, rescaled to variance sd^2


def holm(p) -> np.ndarray:
    p = np.asarray(p, dtype=float)
    o = np.argsort(p)
    adj = np.minimum(1.0, np.maximum.accumulate((len(p) - np.arange(len(p))) * p[o]))
    out = np.empty_like(adj)
    out[o] = adj
    return out


def signflip_p(u) -> float:
    """Exact two-sided sign-flip p over the 2^5 patterns (statistic: |mean|)."""
    u = np.asarray(u, dtype=float)
    return float(np.mean(np.abs(SIGNS @ u) / len(u) >= abs(u.mean()) - 1e-9))


def tost_p(m: float, se: float, d: float, T) -> float:
    if se == 0:
        return 0.0 if abs(m) < d else 1.0
    return float(max(T.sf((m + d) / se), T.cdf((m - d) / se)))


def vc_rot_seed(M) -> tuple[float, float]:
    """One-way random effects (rotation x seed, balanced): SD between rotations, SD between seeds."""
    M = np.asarray(M, dtype=float)
    k = M.shape[1]
    msw = M.var(axis=1, ddof=1).mean()
    msb = k * M.mean(axis=1).var(ddof=1)
    return float(np.sqrt(max(0.0, (msb - msw) / k))), float(np.sqrt(msw))


def vc_nested(cells: dict) -> tuple[float, float, float, int]:
    """{rot: {subject: [seed values]}} -> SD rotation (beyond its subjects), SD subject, SD seed, n subjects.
    ANOVA-type moments; subjects are unbalanced across rotations (harmonic mean)."""
    k = len(next(iter(next(iter(cells.values())).values())))
    s2_seed = float(np.mean([np.var(v, ddof=1) for subs in cells.values() for v in subs.values()]))
    cm = {r: np.array([np.mean(v) for v in subs.values()]) for r, subs in cells.items()}
    df = sum(len(v) - 1 for v in cm.values())
    s2_sub = max(0.0, sum(((v - v.mean()) ** 2).sum() for v in cm.values()) / df - s2_seed / k)
    nh = len(cm) / sum(1 / len(v) for v in cm.values())
    s2_rot = max(0.0, float(np.var([v.mean() for v in cm.values()], ddof=1)) - (s2_sub + s2_seed / k) / nh)
    return (
        float(np.sqrt(s2_rot)),
        float(np.sqrt(s2_sub)),
        float(np.sqrt(s2_seed)),
        sum(len(v) for v in cm.values()),
    )


def nb_ratio(tags: str) -> tuple[float, list[int]]:
    """Mean over rotations of n_test / n_train (grid windows; train = the 3 folds that are not test or val)."""
    W = []
    for r in range(5):
        f = sorted((LOCAL / UNIT_DIR[tags].format(r=r) / "results").glob("test-index-*.json"))[0]
        W.append(len(json.loads(f.read_text())))
    tot = sum(W)
    return float(np.mean([W[r] / (tot - W[r] - W[(r + 1) % 5]) for r in range(5)])), W


def build_rows() -> tuple[list[dict], dict]:
    """Every D24-A/B contrast in bootstrap_d24's loop order, so the same RNG stream reproduces its CIs."""
    rng = np.random.default_rng(20261101)
    rows, rocs = [], {}
    for dataset, tags, paper in SETS:
        roc = rocs[tags] = load(str(LOCAL), dataset, set(tags.split(",")))
        for model in ("biot", "cbramod"):
            for probe in sorted({c[3] for c in roc if c[0] == model}):
                for a, b in CONTRASTS:
                    if paper:
                        A, B = roc.get((model, a, "paper", probe), {}), roc.get((model, b, "paper", probe), {})
                        seeds = sorted(set(A) & set(B))
                        if len(seeds) < 5:
                            continue
                        runs = [[A[s] - B[s] for s in seeds]]
                        units = runs[0]
                    else:
                        cells = [
                            (roc.get((model, a, r, probe), {}), roc.get((model, b, r, probe), {})) for r in ROTS
                        ]
                        if not all(len(set(x) & set(y)) == 3 for x, y in cells):
                            continue
                        runs = [[x[s] - y[s] for s in sorted(set(x) & set(y))] for x, y in cells]
                        units = [float(np.mean(v)) for v in runs]
                    m, lo, hi = cluster_ci(runs, rng)
                    rows.append(
                        dict(
                            dataset=dataset,
                            tags=tags,
                            setting=SETTING[tags],
                            paper=paper,
                            model=model,
                            probe=probe,
                            a=a,
                            b=b,
                            family=FAMILY[(a, b)],
                            runs=runs,
                            units=[float(x) for x in units],
                            boot=(lo, hi),
                            boot_mean=m,
                        )
                    )
    return rows, rocs


def check_bootstrap_table(rows: list[dict]) -> None:
    logged = {
        ln.strip()
        for ln in (ROOT / "artifacts" / "tables" / "d24-bootstrap.md").read_text().splitlines()
        if ln.startswith("| chbmit") or ln.startswith("| siena")
    }
    mine = {
        f"| {r['dataset']} ({r['tags']}) | {r['model']} | {r['probe']} | {r['a']} - {r['b']} | "
        f"{r['boot_mean']:+.1f} | [{r['boot'][0]:+.1f}, {r['boot'][1]:+.1f}] |"
        for r in rows
    }
    if mine != logged:
        raise SystemExit(f"bootstrap does not reproduce d24-bootstrap.md: {sorted(mine ^ logged)[:4]}")


def verdict(r: dict) -> str:
    u = r["units"]
    if r["family"] == "reference":
        return "reference, no rule"
    if r["paper"] and r["family"] != "C1":
        return "descriptive (no rule on the paper split)"
    return d17(u, [0.0] * len(u)) if r["family"] == "D17" else paired(u)


def analyse(r: dict, ratio: float | None, rng: np.random.Generator) -> None:
    u = np.asarray(r["units"])
    n, m, sd = len(u), float(u.mean()), float(u.std(ddof=1))
    T = stats.t(n - 1)
    se = {"t": sd / np.sqrt(n), "nb": sd * np.sqrt(1 / n + ratio) if ratio is not None else None}
    r.update(n=n, mean=m, sd=sd, unit="seed" if r["paper"] else "rotation", nb_ratio=ratio, verdict=verdict(r))
    for key, s in se.items():
        if s is None:
            r[key] = None
            continue
        r[key] = dict(
            se=s,
            ci95=(m - T.ppf(0.975) * s, m + T.ppf(0.975) * s),
            ci90=(m - T.ppf(0.95) * s, m + T.ppf(0.95) * s),
            p=float(2 * T.sf(abs(m) / s)) if s > 0 else float(m == 0),
            tost={d: tost_p(m, s, d, T) for d in (1, 2, 3)},
            p_vs_paper=float(T.cdf((m - PAPER_GAIN[r["model"]]) / s)) if r["family"] == "C1" else None,
        )
    d17_row = r["family"] == "D17"
    r["sweep"] = {k: "".join(rule(u, t, k, d17_row) for t in THRS) for k in (3, 4, 5)}
    r["same_sign"] = int((u > 0).sum() if m >= 0 else (u < 0).sum())
    r["loo"] = "".join(rule(np.delete(u, i), 3.0, None, d17_row) for i in range(n))
    r["signflip_p"] = signflip_p(u)
    r["power"] = {}
    for kind in ERRS:
        E = errors(u, kind, rng)
        up, down = rule_edges(E)
        r["power"][kind] = dict(
            fpr0=float(np.mean((up < 0) | (down > 0))),
            at={d: float(np.mean(up < d)) for d in (3, 5, 10, 36)},
            d80=float(np.quantile(up, 0.8)),
            explain={d: float(np.mean(np.abs(E.mean(1) + d) <= 3)) for d in (0, 3, 5)} if d17_row else None,
        )


def boot_coverage(rng: np.random.Generator, n: int = 5, sims: int = 4000, B: int = 2000) -> tuple[float, float]:
    """Coverage of the 95% percentile bootstrap and t intervals for a mean of n iid normals."""
    hit_b = hit_t = 0
    q = stats.t(n - 1).ppf(0.975)
    for _ in range(sims):
        x = rng.standard_normal(n)
        lo, hi = np.quantile(x[rng.integers(0, n, (B, n))].mean(1), [0.025, 0.975])
        hit_b += lo <= 0 <= hi
        hit_t += abs(x.mean()) <= q * x.std(ddof=1) / np.sqrt(n)
    return hit_b / sims, hit_t / sims


def subject_rocs(dataset: str, tags: str) -> dict:
    """(model, arm, rot, seed) -> {subject: ROC x100} from the linear npz of the D24-A runs.
    Refuses a run whose labels (recomputed from the window keys, D18 overlap rule) or pooled ROC
    differ from the record."""
    table = json.loads((ROOT / "configs" / f"{dataset}_seizures.json").read_text())
    win = 10 * {"chbmit": 256, "siena": 512}[dataset]
    out, idx_cache = {}, {}
    for p in LOCAL.rglob("results/*.json"):
        if p.name.startswith(("diag-", "test-index-", "report-")):
            continue
        r = json.loads(p.read_text())
        if (
            r.get("smoke")
            or r["dataset"] != dataset
            or r.get("run_tag") not in tags.split(",")
            or r["split"] not in ROTS
            or r["arm"] not in ARMS
        ):
            continue
        ti = p.parent / r["test_index"]
        if ti not in idx_cache:
            idx = json.loads(ti.read_text())
            lab = [
                overlap_label(
                    {
                        "file": x["key"].rsplit("-grid-", 1)[0],
                        "start": int(x["key"].rsplit("-", 1)[1]),
                        "n_samples": win,
                    },
                    table,
                )
                for x in idx
            ]
            idx_cache[ti] = np.array([x["subject"] for x in idx]), np.array(lab)
        subj, lab = idx_cache[ti]
        z = np.load(p.with_name(p.stem + ".linear.npz"))
        y, s = z["y_test"], z["scores_best"]
        if not np.array_equal(y, lab):
            raise SystemExit(f"{p.name}: y_test differs from the overlap labels of its test index")
        if abs(roc_auc_score(y, s) - r["probes"]["linear"]["test_at_best"]["roc_auc"]) > 1e-6:
            raise SystemExit(f"{p.name}: pooled ROC from the npz differs from the record")
        out[(r["model"], r["arm"], r["split"], r["seed"])] = {
            g: 100 * roc_auc_score(y[subj == g], s[subj == g])
            for g in np.unique(subj)
            if 0 < y[subj == g].sum() < (subj == g).sum()
        }
    return out


# ---------- E22 ----------

ABSTRACT = (
    ("+36.2 ROC-AUC headline gain (BIOT)", "D", "paper value, quoted"),
    (
        "88.48 ± 0.19 (5 seeds), 88.51 ± 0.53, 88.49 ± 0.40: random-init BIOT last / last2 / all",
        "P*",
        "D12 'supported'; the rule's reference (wave-1 last_randinit, 88.5) was seen before D12 was written; "
        "the R1 rows are new screen data",
    ),
    ("88.67, 88.44, 88.60 (paper Table 2)", "D", "paper values"),
    ("51.99 ± 1.30: pretrained BIOT last (5 seeds)", "D", "wave 1; D5/D6 fix the protocol, no reading rule"),
    (
        "92.0 ± 0.0: frozen CBraMod on the paper split, fixed probe",
        "D",
        "D24-B arm mean; the probe fix (D23) is post hoc; the level was previewed by the CPU check "
        "(92.6, notes/cbramod-check.md section 4)",
    ),
    ("paper LP 54.14", "D", "paper value"),
    ("SSL adaptation adds 0.0 ± 0.0 (CBraMod, paper split)", "P", "D24-B SA-gain rule, fixed before any P1E run"),
    (
        "2 test patients; 206 of 252 test positives are duplicates; 70 of 114 ictal windows labelled negative",
        "D",
        "data counts (from the post-hoc re-scoring work); E1 re-checks them with the released scripts",
    ),
    ("16 papers in the census", "D", "agent-compiled, not verified by hand (E16)"),
    (
        "3 seeds per rotation",
        "P*",
        "D24 raised D18's 1 seed per rotation to 3 after the 1-seed results (deviation 2)",
    ),
    (
        "BIOT +1.9, CBraMod -0.0, 'no difference shown' (CHB-MIT, corrected protocol)",
        "P*",
        "D18 rule through D24-A; deviations 2, 6, 9",
    ),
    ("random-init result matches random features (within 3 points)", "H", "D17, a post-hoc control"),
    ("Siena: BIOT +9.2 / +4.1 'first term wins', not CBraMod", "P*", "D24-A; deviations 2, 6, 9"),
    ("C2 and C3 not supported with the fixed probe (1 seed)", "P", "D24-C applies D15's rules as written"),
    ("'not consistent with Table 1 as a whole'", "P", "D13 rule, fixed before the confirmation results"),
)

TABLE_TAG = {
    1: "P* (D12 reading; the reference value was seen before the rule)",
    2: "P (SA gain and verdict, D24-B) / D (arm means; probe fixed post hoc in D23)",
    3: "D (agent census, not verified by hand)",
    4: "H (post-hoc re-scoring of saved scores)",
    5: "D (per-rotation means behind the Table 6 verdicts)",
    6: "P* (last - lp, last_randinit - last, lp - lp_randinit) / H (D17) / D (all - last)",
    7: "P (D24-C, D15 rules as written, 1 seed)",
    8: "D (wave-1 means; no reading rule)",
}

DEVIATIONS = (
    (
        "D24-A: 'also mean +/- SEM over all 15 runs'",
        "the draft reports only the SEM over the 5 rotation means; read_d24.py prints the 15-run SEM labelled "
        "'seeds not independent' and the draft drops it (section 2.6)",
        "statistically right (seeds share a split), but the registered output is not reported; disclose",
    ),
    (
        "D18: one seed per rotation (S_r, per the D18 amendment)",
        "D24-A uses 3 seeds per rotation [S_r, 1000+r, 2000+r] and its verdicts are primary",
        "decided 2026-10-31 after every 1-seed result (S1, S3, S3F, S1E, S3E, S3FE) had been read; 3 verdicts "
        "changed (draft section 6); CBraMod reuses its S_r run, so 1/3 of its D24-A data was seen (part 1)",
    ),
    (
        "D24-D: bootstrap CIs, to be reported",
        "computed 2026-11-01 (artifacts/tables/d24-bootstrap.md), not cited in the draft; WORKLOG 2026-11-01 "
        "says 'CIs agree with every D24 verdict', which is wrong for: {disagree}",
        "cite as pre-registered D24-D with the under-coverage caveat (E10c)",
    ),
    (
        "D24-D: 'bootstrap CIs over (rotation, seed) runs'",
        "implemented as a two-stage bootstrap (rotations, then seeds inside each drawn rotation) after the "
        "D24 review",
        "a refinement; it still under-covers with 5 rotations (E10c coverage check)",
    ),
    (
        "D24-A: lp - lp_randinit rule 'new, fixed now'",
        "fixed 2026-10-31, after the D23 re-run had shown CBraMod lp above lp_randinit in 14 of 15 "
        "rotation-settings",
        "tag P*, not P (draft section 10 discloses it)",
    ),
    (
        "BIOT probe mode",
        "train mode in S1/S3/S3F; D24 moved BIOT to eval mode after all train-mode BIOT results were seen "
        "(registered in D24 before the runs)",
        "disclosed; two BIOT verdicts changed between the two",
    ),
    (
        "D17 lp_randinit control",
        "added after the D15 data; its rule was fixed before any lp_randinit run",
        "H wherever it appears (the draft says 'post hoc')",
    ),
    (
        "D23 CBraMod probe",
        "changed after every earlier CBraMod result; the eval-mode amendment came after the "
        "CPU check and a local 1-epoch smoke",
        "every fixed-probe CBraMod number rests on a post-hoc protocol change",
    ),
    (
        "D12 screen rule",
        "its reference value (wave-1 last_randinit 88.5) was seen before the rule; jobs logged as "
        "submitted ~18:05 local, rule timestamped 18:10 local",
        "rule precedes every screen result, not the submission: P*",
    ),
    (
        "D13 confirmation rule",
        "jobs logged as submitted ~14:15 local, rule timestamped 14:20 local",
        "matches its own wording ('BEFORE any result'); not 'before any run'",
    ),
    (
        "D25: 'BEFORE any D25 run or analysis'",
        "the adopted audit already quotes in-memory statistics by the stats "
        "reviewer ('t [-1.0, +4.8]', 'FPR 17%') computed before D25",
        "E10 and E11 are post hoc; cite script output only",
    ),
    (
        "E22: 'git init and commit; archived timestamp'",
        "D25 amendment: no git commits (not asked by the user)",
        "timing rests on file mtimes and the logs; get an archived timestamp before submission",
    ),
    (
        "E22: SageMaker CreationTime and S3 LastModified via AWS",
        "this run: local file mtimes only (no AWS calls); logged submission times stand in for CreationTime",
        "CreationTime unverified",
    ),
)

RE_WAVE1 = r"^(arms-(biot|cbra)-chb-(lp|last|last2|first|first2|lrand)|diag-(biot|cbra)-chb)$"
RE_SCREEN = r"^arms-(biot|cbra)-chb-r[1-4]$"
RE_CONFIRM = r"^arms-(biot|cbra)-chb-c[12]$"
RE_C23 = r"^arms-(biot|cbra)-chb-c(2n|3p)$"
RE_S1 = r"^arms-(biot|cbra)-chb-rot\d-s1$"
RE_S3 = r"^arms-(biot|cbra)-sie-rot\d-s3$"
RE_S3F = r"^arms-(biot|cbra)-sie-rot\d-s3f$"
RE_D23 = r"^arms-cbra-(chb-rot\d-s1e|sie-rot\d-s3e|sie-rot\d-sfe)$"
RE_D24 = r"^arms-(biot|cbra)-(chb-rot\d-s1m|sie-rot\d-s3m|sie-rot\d-sfm|chb-p1e\w+|chb-r3e|chb-c2e|chb-c3e)$"
RE_CBRA_OLD = r"^arms-cbra-(?!.*-(s1e|s3e|sfe|s1m|s3m|sfm|p1e\w+|r3e|c2e|c3e)$).*$"
# entry, stated time (decisions.md), claim, kind, run dirs, arm filter, jobs file, WORKLOG time (secondary)
DECISIONS = (
    ("D4-D11", "2026-10-15", "before any result", "result", RE_WAVE1, None, "wave1", None),
    ("D12", "2026-10-15 18:10", "BEFORE any result", "result", RE_SCREEN, None, "screen", None),
    ("D12 outcome", "2026-10-17", "after the results", "after", RE_SCREEN, None, None, None),
    ("D13", "2026-10-19 14:20", "BEFORE any result", "result", RE_CONFIRM, None, "confirm", None),
    ("D13 outcome", "2026-10-19 22:00", "AFTER the results", "after", RE_CONFIRM, None, None, None),
    ("D15", "2026-10-20", "BEFORE any run", "run", RE_C23, None, "c23", None),
    ("D15 outcome", "2026-10-20 13:30", "AFTER the results", "after", RE_C23, None, None, None),
    ("D17", "2026-10-20", "after the D15 data", "after", RE_C23, None, None, "2026-10-20 13:45"),
    (
        "D17 rule",
        "2026-10-20",
        "before any lp_randinit run",
        "run",
        f"{RE_S1}|{RE_S3}|{RE_S3F}",
        ("lp_randinit",),
        "s1",
        "2026-10-20 13:45",
    ),
    ("D18", "2026-10-20", "BEFORE any run", "run", RE_S1, None, "s1", None),
    ("D18 amendments", "2026-10-20 14:00", "BEFORE any Step 1 run", "run", RE_S1, None, "s1", None),
    (
        "D19",
        "2026-10-20",
        "BEFORE any run",
        "run",
        RE_S1,
        ("first_block", "embed_only", "first_noise"),
        "s1",
        None,
    ),
    ("D20", "2026-10-20 13:55", "BEFORE any Step 1 run (after the GPU smoke)", "run", RE_S1, None, "s1", None),
    (
        "D21",
        "2026-10-20",
        "BEFORE any Siena data is windowed or run",
        "run",
        f"{RE_S3}|{RE_S3F}",
        None,
        "s3",
        "2026-10-20 14:10",
    ),
    (
        "D22",
        "2026-10-20 15:30",
        "before any Step 1 adaptation arm was read; only rot0 lp/lp_randinit seen",
        "existing",
        RE_S1,
        None,
        None,
        None,
    ),
    (
        "D17/D18/D19 outcome",
        "2026-10-20 22:30",
        "AFTER the results",
        "after",
        f"{RE_S1}|{RE_S3}",
        None,
        None,
        None,
    ),
    ("D21 robustness outcome", "2026-10-20 22:55", "AFTER the results", "after", RE_S3F, None, None, None),
    ("D23", "2026-10-26", "AFTER seeing every earlier CBraMod result", "after", RE_CBRA_OLD, None, None, None),
    ("D23 amendment", "2026-10-26", "BEFORE any re-run result", "result", RE_D23, None, "d23", None),
    ("D23 re-run outcome", "2026-10-27 03:20", "AFTER the results", "after", RE_D23, None, None, None),
    ("D24", "2026-10-31", "BEFORE any of these runs", "run", RE_D24, None, "d24", "2026-10-31 13:15"),
    ("D24 outcome", "2026-10-31 17:45", "AFTER the results", "after", RE_D24, None, None, None),
    ("D25", "2026-11-01", "BEFORE any D25 run", "none-after", r".", None, None, None),
)


def pt(s: str) -> datetime:
    return datetime.fromisoformat(s if " " in s else s + " 00:00").replace(tzinfo=PT)


def fmt(t: datetime | None) -> str:
    return t.astimezone(PT).strftime("%m-%d %H:%M") if t else "-"


def objects() -> list[tuple[str, str | None, datetime, bool]]:
    """(run dir, arm or None, mtime, is_record) for every local results object."""
    out = []
    for p in LOCAL.rglob("results/*"):
        arm = None
        if p.suffix == ".json" and not p.name.startswith(("diag-", "test-index-", "report-")):
            arm = json.loads(p.read_text())["arm"]
        elif p.name.endswith(".npz"):
            arm = "?"
        out.append((p.parts[-3], arm, datetime.fromtimestamp(p.stat().st_mtime, PT), arm not in (None, "?")))
    return out


def job_logs() -> dict:
    out = {}
    for f in (ROOT / "notes").glob("jobs-*.txt"):
        lines = f.read_text().splitlines()
        m = re.search(r"submitted (\d{4}-\d{2}-\d{2}) ~(\d{2}:\d{2}) local", lines[0])
        name = re.search(r"-(\d{8})-", next(ln for ln in lines[1:] if ln.strip() and not ln.startswith("#")))
        if m:
            t = pt(f"{m.group(1)} {m.group(2)}")
            out[f.stem.removeprefix("jobs-")] = (t, name.group(1) if name else None)
    return out


def hm(td: timedelta) -> str:
    s = int(td.total_seconds())
    return f"{'-' if s < 0 else '+'}{abs(s) // 3600}:{abs(s) % 3600 // 60:02d}:{abs(s) % 60:02d}"


def check(kind: str, stated: datetime, date_only: bool, ref: datetime | None, sub: datetime | None) -> str:
    """kind 'after': stated must follow ref; otherwise stated must precede ref."""
    if ref is None:
        return "no local object"
    after = kind == "after"
    if date_only:
        end = stated + timedelta(days=1)
        if after:
            return (
                "consistent"
                if ref < stated
                else "INCONSISTENT"
                if ref >= end
                else f"same day: holds only if written after {fmt(ref)}"
            )
        return (
            "consistent"
            if ref >= end
            else "INCONSISTENT"
            if ref < stated
            else f"same day: holds only if written before {fmt(ref)}"
        )
    gap = stated - ref if after else ref - stated
    if gap > timedelta(0):
        return f"consistent (margin {hm(gap)})"
    if not after and ref == sub and -gap <= timedelta(minutes=10):
        return f"tie with the logged '~' submission ({hm(gap)})"
    return f"INCONSISTENT ({hm(gap)})"


def timestamps() -> tuple[list[dict], list[str], datetime]:
    objs, logs, rows = objects(), job_logs(), []
    existing = []
    for entry, stated_s, claim, kind, rx, arms, jobs, wl in DECISIONS:
        rgx = re.compile(rx)
        sel = [o for o in objs if rgx.search(o[0]) and (arms is None or o[1] in arms)]
        recs = [o[2] for o in sel if o[3]]
        stated, date_only = pt(stated_s), " " not in stated_s
        sub, jobdate = logs.get(jobs, (None, None)) if jobs else (None, None)
        first_obj = min((o[2] for o in sel), default=None)
        first_rec, last_rec = min(recs, default=None), max(recs, default=None)
        if kind == "existing":
            got = sorted(
                (o[2], o[0].split("-")[1], o[1], o[0].split("-")[3]) for o in sel if o[3] and o[2] < stated
            )
            existing = [f"{m} {a} {r} ({fmt(t)})" for t, m, a, r in got]
            adapted = [e for e, g in zip(existing, got, strict=True) if g[2] not in ("lp", "lp_randinit")]
            res = (
                f"{len(existing)} records had landed by {fmt(stated)}: "
                + ", ".join(existing)
                + (
                    f". Adaptation-arm records among them ({', '.join(adapted)}): that they were not read "
                    "cannot be confirmed from timestamps"
                    if adapted
                    else ""
                )
            )
        elif kind == "none-after":
            last_all = max(o[2] for o in objs)
            res = f"consistent: newest local object {fmt(last_all)}" if last_all < stated else "INCONSISTENT"
        else:
            ref = {
                "run": min([t for t in (sub, first_obj) if t], default=None),
                "result": first_rec,
                "after": last_rec,
            }[kind]
            res = check("after" if kind == "after" else "before", stated, date_only, ref, sub)
            if wl and date_only:
                second = check("after" if kind == "after" else "before", pt(wl), False, ref, sub)
                res += f"; WORKLOG time {wl[11:]} local -> {second}"
        utc_date = sub.astimezone(ZoneInfo("UTC")).strftime("%Y%m%d") if sub else None
        rows.append(
            dict(
                entry=entry,
                stated=stated_s,
                claim=claim,
                kind=kind,
                n_objects=len(sel),
                submitted=fmt(sub),
                job_name_date=jobdate,
                job_name_date_matches_utc=(jobdate == utc_date) if jobdate else None,
                first_object=fmt(first_obj),
                first_record=fmt(first_rec),
                last_record=fmt(last_rec),
                check=res,
            )
        )
    return rows, existing, max(o[2] for o in objs)


def without_sr(rocs: dict) -> list[dict]:
    """CBraMod D24-A read as D24 does, with all 3 seeds, without S_r (the reused D23 run), and S_r only."""
    out = []
    keep = {
        "3 seeds (D24 as logged)": lambda i, s: True,
        "2 new seeds (no S_r)": lambda i, s: s != S_R[i],
        "S_r only (D23 re-run)": lambda i, s: s == S_R[i],
    }
    for tags in ("S1E,S1M", "S3E,S3M", "S3FE,S3FM"):
        roc = rocs[tags]
        for a, b in CONTRASTS[:4]:
            row = dict(setting=SETTING[tags], contrast=f"{a} - {b}")
            for name, f in keep.items():
                per = {
                    arm: [
                        np.mean([v for s, v in roc[("cbramod", arm, f"rot{i}", "linear")].items() if f(i, s)])
                        for i in range(5)
                    ]
                    for arm in (a, b)
                }
                d = np.subtract(per[a], per[b])
                v = d17(per[a], per[b]) if (a, b) == ("last_randinit", "lp_randinit") else paired(list(d))
                row[name] = (float(d.mean()), v, [float(x) for x in d])
            row["holds"] = row["2 new seeds (no S_r)"][1] == row["3 seeds (D24 as logged)"][1]
            out.append(row)
    return out


def draft_rows() -> list[tuple[int, str]]:
    lines = (ROOT / "paper" / "reproducibility-note-draft.md").read_text().splitlines()
    cur, out = None, []
    for i, ln in enumerate(lines):
        m = re.match(r"\*Table (\d+)\.", ln)
        if m:
            cur = int(m.group(1))
        elif ln.startswith("## "):
            cur = None
        elif cur and ln.startswith("|") and not set(ln) <= set("|-: "):
            if i + 1 < len(lines) and set(lines[i + 1].strip()) <= set("|-: ") and lines[i + 1].strip():
                continue  # header row
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            out.append((cur, " | ".join(cells[: {4: 3, 5: 3, 8: 3, 7: 1}.get(cur, 2)])))
    return out


def row_tag(table: int, label: str) -> str:
    if table == 1 and label.startswith("last block"):
        return "P* (random init, D12) / D (pretrained init, wave 1) / paper"
    if table == 7 and "random" in label:
        return "D (D15 rules do not cover random init)"
    return TABLE_TAG[table]


# ---------- output ----------


def ci(x) -> str:
    return f"[{x[0]:+.1f}, {x[1]:+.1f}]" if x else "n/a"


def name(r: dict) -> str:
    return f"{r['setting']} | {r['model']} | {r['probe']} | {r['a']} - {r['b']}"


def excl0(x) -> str:
    return "-" if x is None else "y" if x[0] > 0 or x[1] < 0 else "n"


def e10_md(rows: list[dict], ratios: dict, cov: tuple, vc1: list, vc2: list, power_sds: dict) -> str:
    L = [
        "# E10: statistics on the D24 records (D25; post hoc and descriptive, D24 verdicts stay primary)",
        "",
        "Script: scripts/analysis/stats_d25.py. ROC-AUC x100. Units: D24-A = the 5 rotation means of the paired "
        "per-seed differences (3 seeds each); D24-B (paper split, P1E) = the 5 seeds on one split, so its "
        "intervals cover seed noise only, not test-set sampling. n = 5, df = 4 everywhere.",
        "Nadeau-Bengio: SE = SD * sqrt(1/5 + n_test/n_train), n_test/n_train = mean over rotations from the "
        "test-index sizes (grid windows; train = the 3 folds that are neither test nor val): "
        + "; ".join(f"{SETTING[t]} {v[0]:.3f} (fold sizes {v[1]})" for t, v in ratios.items())
        + ". Not defined for the paper split (one fixed split, no resampling of data): n/a.",
        f"Bootstrap (c) = pre-registered D24-D, under-covers at n=5; it reproduces "
        f"artifacts/tables/d24-bootstrap.md exactly (checked). Coverage check, 95% percentile bootstrap of a "
        f"mean of 5 iid normals: {cov[0]:.3f} (t-interval: {cov[1]:.3f}; 4,000 sims x 2,000 resamples).",
        "",
    ]
    ref = {(r["setting"], r["model"], r["a"], r["b"]): r for r in rows if r["probe"] == "linear"}
    fpr = [r["power"]["normal"]["fpr0"] for r in rows if not r["paper"] and r["family"] in FAMS[:3]]
    sie = ref[("Siena", "biot", "last", "lp")]
    L += [
        "The audit's in-memory numbers, checked here: 't [-1.0, +4.8]' is the t-interval of CHB-MIT BIOT "
        f"last - lp, {ci(ref[('CHB-MIT', 'biot', 'last', 'lp')]['t']['ci95'])} in this script; 'FPR 17%' names "
        f"no contrast: the FPR at true effect 0 (normal errors) of the D24-A rule contrasts runs from "
        f"{min(fpr):.3f} to {max(fpr):.3f}, e.g. Siena BIOT last - lp (SD "
        f"{sie['sd']:.1f}) {sie['power']['normal']['fpr0']:.3f}.",
        "",
    ]
    L += [
        "## (a)-(c) 95% intervals",
        "",
        "| setting | model | head | contrast | family | mean | per unit | t 95% | NB 95% | bootstrap 95% "
        "(D24-D, under-covers) | excludes 0 (t/NB/boot) | D24 verdict |",
        "|" + "---|" * 12,
    ]
    for r in rows:
        L.append(
            f"| {name(r)} | {r['family']} | {r['mean']:+.1f} | {', '.join(f'{x:+.1f}' for x in r['units'])} | "
            f"{ci(r['t']['ci95'])} | {ci(r['nb'] and r['nb']['ci95'])} | {ci(r['boot'])} | "
            f"{excl0(r['t']['ci95'])}/{excl0(r['nb'] and r['nb']['ci95'])}/{excl0(r['boot'])} | {r['verdict']} |"
        )
    L += [
        "",
        "## (d) One-sided bounds, equivalence (TOST) and the paper's gains",
        "",
        "One-sided 95% bounds = the 90% two-sided interval. TOST p at margin d: max of the two one-sided t "
        "tests; 'equivalent' at alpha 0.05 iff p < 0.05 (90% interval inside (-d, +d)). Paper gain test "
        "(C1 rows only): H0 effect >= paper gain (BIOT +36.2, CBraMod +29.5), one-sided t.",
        "",
        "| setting | model | head | contrast | 90% t | 90% NB | TOST p d=1/2/3 (t) | TOST p d=1/2/3 (NB) | "
        "p(effect >= paper gain) t / NB |",
        "|" + "---|" * 9,
    ]
    for r in rows:
        tt = "/".join(f"{r['t']['tost'][d]:.3f}" for d in (1, 2, 3))
        tn = "/".join(f"{r['nb']['tost'][d]:.3f}" for d in (1, 2, 3)) if r["nb"] else "n/a"
        pg = (
            (
                f"{r['t']['p_vs_paper']:.2g} / {r['nb']['p_vs_paper']:.2g}"
                if r["nb"]
                else f"{r['t']['p_vs_paper']:.2g} / n/a"
            )
            if r["family"] == "C1"
            else "-"
        )
        L.append(f"| {name(r)} | {ci(r['t']['ci90'])} | {ci(r['nb'] and r['nb']['ci90'])} | {tt} | {tn} | {pg} |")
    L += [
        "",
        "## (e) Threshold x k sweep, flip points, leave-one-out",
        "",
        "Each string has one symbol per threshold 0, 0.5, ..., 10 (21 symbols): '+' first term wins, '-' "
        "second term wins, '.' no difference shown; D17 rows: 'E' = |mean| <= threshold (random features "
        "explain it). Flip points: a win holds for threshold < |mean| and k <= the same-sign count. "
        "Leave-one-out (rotation or seed) uses the rule with k = n - 1 = 3 of 4, as read_step1.paired does; "
        "one symbol per left-out unit (rot0..rot4 or seeds in order).",
        "",
        "| setting | model | head | contrast | D18 verdict (3, 4/5) | abs(mean) | same-sign count | k=3 | k=4 | "
        "k=5 | leave-one-out | LOO stable |",
        "|" + "---|" * 12,
    ]
    for r in rows:
        full = rule(r["units"], 3.0, None, r["family"] == "D17")
        stable = "yes" if set(r["loo"]) == {full} else "NO"
        L.append(
            f"| {name(r)} | {full} | {abs(r['mean']):.1f} | {r['same_sign']}/5 | `{r['sweep'][3]}` | "
            f"`{r['sweep'][4]}` | `{r['sweep'][5]}` | `{r['loo']}` | {stable} |"
        )
    L += [
        "",
        "## (f) Power and false positives of the 3-point, 4/5 rule",
        "",
        f"Simulation: 5 units = true effect + errors with each contrast's SD (over its 5 units), {R_SIM:,} "
        "replicates per error model (normal; t3 scaled to the SD; centred resample of the contrast's own 5 "
        "values, rescaled to the SD). Computed exactly per replicate: the rule says 'first term wins' iff "
        "the true effect exceeds max(3 - mean(e), -e_(2)). Cells: normal / t3 / resample. FPR = P(any win) "
        "at true effect 0. Power = P(first term wins) at true effect 3, 5, 10, 36. Effect80 = smallest true "
        "effect with 80% power. D17 rows add P(|mean| <= 3) at true effect 0 / 3 / 5.",
        "",
        "| setting | model | head | contrast | SD | FPR at 0 | power at 3 | at 5 | at 10 | at 36 | effect80 | "
        "D17 P(explain) at 0/3/5 (normal) |",
        "|" + "---|" * 12,
    ]
    for r in rows:
        P = r["power"]
        fpr = " / ".join(f"{P[k]['fpr0']:.3f}" for k in ERRS)
        pw = " | ".join(" / ".join(f"{P[k]['at'][d]:.2f}" for k in ERRS) for d in (3, 5, 10, 36))
        d80 = " / ".join(f"{P[k]['d80']:.1f}" for k in ERRS)
        ex = "/".join(f"{P['normal']['explain'][d]:.2f}" for d in (0, 3, 5)) if P["normal"]["explain"] else "-"
        L.append(f"| {name(r)} | {r['sd']:.1f} | {fpr} | {pw} | {d80} | {ex} |")
    L += [
        "",
        "Generic power curves (normal and t3 errors, SD "
        + ", ".join(map(str, power_sds["sds"]))
        + "): power-rule.png. Observed contrast SDs: D24-A "
        + power_sds["a"]
        + "; paper split "
        + power_sds["b"]
        + ".",
        "",
    ]
    L += [
        "## (g) Multiplicity: exact sign-flip p and Holm within families",
        "",
        "Exact two-sided sign-flip p over the 32 sign patterns of the 5 units (statistic |mean|); the "
        "smallest possible p is 2/32 = 0.0625, so no contrast can reach 0.05 with 5 units, before or after "
        "Holm. Families: C1 = last - lp, Artifact 1 = last_randinit - last, features = lp - lp_randinit, "
        "D17 = last_randinit - lp_randinit; each family = its 6 D24-A rows + its 4 paper-split rows (10 "
        "tests). The t-test p (df 4) and its Holm adjustment are shown for comparison.",
        "",
        "| family | setting | model | head | contrast | sign-flip p | Holm | t p | Holm (t) |",
        "|" + "---|" * 9,
    ]
    for fam in FAMS[:4]:
        fr = [r for r in rows if r["family"] == fam]
        hs, ht = holm([r["signflip_p"] for r in fr]), holm([r["t"]["p"] for r in fr])
        for r, a, b in zip(fr, hs, ht, strict=True):
            L.append(f"| {fam} | {name(r)} | {r['signflip_p']:.4f} | {a:.4f} | {r['t']['p']:.2g} | {b:.2g} |")
    L += [
        "",
        "## (h) Variance components",
        "",
        "(h1) Rotation vs seed, from the run-level ROC (arms) or the paired per-seed differences (contrasts): "
        "one-way random effects, balanced (5 rotations x 3 seeds), method of moments. Paper split: seed SD "
        "only (one split).",
        "",
        "| setting | model | quantity | SD rotation | SD seed | rotation share of variance |",
        "|" + "---|" * 6,
    ]
    for v in vc1:
        rot = "n/a" if v["rot"] is None else f"{v['rot']:.2f}"
        tot = (v["rot"] or 0.0) ** 2 + v["seed"] ** 2
        share = "n/a" if v["rot"] is None or tot == 0 else f"{v['rot'] ** 2 / tot:.2f}"
        L.append(f"| {v['setting']} | {v['model']} | {v['q']} | {rot} | {v['seed']:.2f} | {share} |")
    L += [
        "",
        "(h2) Rotation / subject / seed, from per-subject ROC-AUC (npz scores, subjects with both classes "
        "in test), subjects nested in rotations, ANOVA-type moments with the harmonic mean subject count. The "
        "rules use the pooled-fold ROC, not per-subject ROC, so these SDs describe heterogeneity, not the "
        "rule's units. Every npz was checked: labels recomputed from the window keys equal y_test, and the "
        "pooled ROC equals the record.",
        "",
        "| setting | model | quantity | SD rotation (beyond its subjects) | SD subject | SD seed | subjects |",
        "|" + "---|" * 7,
    ]
    for v in vc2:
        L.append(
            f"| {v['setting']} | {v['model']} | {v['q']} | {v['rot']:.2f} | {v['sub']:.2f} | {v['seed']:.2f} "
            f"| {v['n']} |"
        )
    L += ["", "## Bounds for the abstract (input to E34)", ""]
    for r in rows:
        if r["family"] in ("C1", "D17") and r["probe"] == "linear":
            L.append(
                f"- {name(r)}: {r['mean']:+.1f}, t 95% {ci(r['t']['ci95'])}, NB 95% "
                f"{ci(r['nb'] and r['nb']['ci95'])}, bootstrap {ci(r['boot'])}; TOST +-3 p (t) "
                f"{r['t']['tost'][3]:.3f}; verdict: {r['verdict']}"
            )
    return "\n".join(L) + "\n"


def e22_md(sr: list, ts: list, existing: list, newest: datetime, disagree: str) -> str:
    keys = ("3 seeds (D24 as logged)", "2 new seeds (no S_r)", "S_r only (D23 re-run)")
    L = [
        "# E22: pre-registered vs post-hoc hygiene (D25)",
        "",
        "Script: scripts/analysis/stats_d25.py.",
        "",
        "## 1. D24-A CBraMod without the S_r seeds",
        "",
        "D24-A reuses CBraMod's S_r run (seed [42, 123, 2021, 3407, 8888][r]) from the D23 re-run, which "
        "had been read before D24 was written. Same reading as read_d24.py (per-rotation seed mean, D18 "
        "rule, D17), in memory, linear head. BIOT ran all 3 seeds inside D24 and is not affected.",
        "",
        "| setting | contrast | " + " | ".join(keys) + " | D24 verdict holds without S_r |",
        "|" + "---|" * 6,
    ]
    for r in sr:
        L.append(
            f"| {r['setting']} | {r['contrast']} | "
            + " | ".join(f"{r[k][0]:+.1f} ({', '.join(f'{x:+.1f}' for x in r[k][2])}): {r[k][1]}" for k in keys)
            + f" | {'yes' if r['holds'] else 'NO'} |"
        )
    L += [
        "",
        "## 2. Tags: P / P* / H / D",
        "",
        "- **P**: design and reading rule fixed before any data of the runs it reads, applied as written.",
        "- **P\\***: rule fixed before the runs, with a disclosed deviation: set after related data had been "
        "seen (same rotations at fewer seeds or another probe mode, a reused run, a reference value already "
        "seen), or its registered output changed.",
        "- **H**: post hoc: the control, rule or analysis was chosen after, or because of, the data it is "
        "read on.",
        "- **D**: descriptive: no reading rule (means, per-unit values, counts, references, quoted paper values).",
        "",
        "### Abstract numbers",
        "",
        "| number or claim | tag | basis |",
        "|---|---|---|",
    ]
    L += [f"| {a} | {t} | {b} |" for a, t, b in ABSTRACT]
    L += [
        "",
        "### Every row of the draft's Tables 1-8 (paper/reproducibility-note-draft.md)",
        "",
        "| table | row | tag |",
        "|---|---|---|",
    ]
    L += [f"| {t} | {lab} | {row_tag(t, lab)} |" for t, lab in draft_rows()]
    L += [
        "",
        "Untagged: the method tables of sections 2.4-2.5 (no results). E10/E11 outputs are H/D.",
        "",
        "## 3. Deviations from the registrations",
        "",
        "| registered | what was done | consequence |",
        "|---|---|---|",
    ]
    L += [f"| {a} | {b.format(disagree=disagree)} | {c} |" for a, b, c in DEVIATIONS]
    L += [
        "",
        "## 4. Decision timestamps against result-object times",
        "",
        "Object times are the local mtimes under artifacts/s3-results. aws s3 sync sets a downloaded file's "
        "mtime to the object's S3 LastModified; the cache was re-synced from S3 on 2026-10-26 (WORKLOG) yet "
        "wave-1 files still carry 2026-10-15, so the mtimes are upload times, not download times. Within a "
        "job they increase by about one arm's run time. Submission times are the '~HH:MM local' headers of "
        "notes/jobs-*.txt (logged by hand; they stand in for SageMaker CreationTime, which was not queried). "
        "All times US Pacific (local). 'first object' includes the test-index file a job writes at its "
        f"start. Newest local object: {fmt(newest)}.",
        "",
        "Check: a BEFORE claim must precede the first governed run (logged submission or first object) or "
        "result; an AFTER claim must follow the last governed record. Date-only entries can be checked only "
        "against the calendar day; a WORKLOG time is used as a secondary check when one exists.",
        "",
        "| entry | stated (decisions.md) | claim | objects | submitted (log) | job-name date = UTC date | "
        "first object | first record | last record | check |",
        "|" + "---|" * 10,
    ]
    for t in ts:
        jd = (
            "-"
            if t["job_name_date"] is None
            else f"{t['job_name_date']} {'yes' if t['job_name_date_matches_utc'] else 'NO'}"
        )
        L.append(
            f"| {t['entry']} | {t['stated']} | {t['claim']} | {t['n_objects']} | {t['submitted']} | {jd} | "
            f"{t['first_object']} | {t['first_record']} | {t['last_record']} | {t['check']} |"
        )
    L += [
        "",
        "Not verifiable here: SageMaker CreationTime and S3 LastModified as returned by AWS (no AWS call); "
        "the time of day of date-only entries; the content of decisions.md at a given time (no version "
        "history, no git).",
    ]
    return "\n".join(L) + "\n"


def forest(rows: list[dict], path: Path) -> None:
    plt.switch_backend("agg")
    order = [(s, m, "linear") for s in ("CHB-MIT", "Siena", "Siena filtered") for m in ("biot", "cbramod")]
    order += [("paper split", m, p) for m in ("biot", "cbramod") for p in ("linear", "mlp_fullft")]
    lab = {
        k: f"{k[0]}, {'BIOT' if k[1] == 'biot' else 'CBraMod'}" + (f", {k[2]}" if k[0] == "paper split" else "")
        for k in order
    }
    title = {
        "C1": "last − lp  (C1: SA helps)",
        "Artifact 1": "last_randinit − last  (Artifact 1)",
        "features": "lp − lp_randinit  (features)",
        "D17": "last_randinit − lp_randinit  (D17)",
        "reference": "all − last  (reference)",
    }
    short = {
        "first term wins": "1st wins",
        "second term wins": "2nd wins",
        "no difference shown": "none",
        "random features explain it": "explains",
        "reference, no rule": "",
        "neither rule met": "neither",
        "descriptive (no rule on the paper split)": "desc.",
    }
    fig, axes = plt.subplots(1, 5, figsize=(24, 7.2), sharey=True, facecolor="#fcfcfb")
    for ax, fam in zip(axes, FAMS, strict=True):
        ax.set_facecolor("#fcfcfb")
        for r in (r for r in rows if r["family"] == fam):
            y = order.index((r["setting"], r["model"], r["probe"]))
            ax.scatter(r["units"], [y + 0.27] * len(r["units"]), s=12, color="#a8a7a2", zorder=2, linewidths=0)
            for off, iv, col in (
                (-0.27, r["t"]["ci95"], C_T),
                (-0.09, r["nb"] and r["nb"]["ci95"], C_NB),
                (0.09, r["boot"], C_BOOT),
            ):
                if iv:
                    ax.plot(iv, [y + off] * 2, color=col, lw=2.2, solid_capstyle="round", zorder=3)
                    ax.plot(r["mean"], y + off, "o", color=col, ms=4.5, zorder=4, mec="#fcfcfb", mew=1)
            ax.annotate(
                short.get(r["verdict"], r["verdict"]),
                xy=(0.99, y - 0.42),
                xycoords=("axes fraction", "data"),
                ha="right",
                va="center",
                fontsize=7.5,
                color=INK2,
            )
        for x, ls in ((0, "-"), (-3, "--"), (3, "--")):
            ax.axvline(x, color="#b9b8b3", lw=0.9, ls=ls, zorder=1)
        ax.axhline(5.5, color=GRID, lw=0.8)
        ax.set_title(title[fam], fontsize=10.5, color=INK)
        ax.tick_params(colors=INK2, labelsize=8.5)
        ax.grid(axis="x", color=GRID, lw=0.5)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.set_xlabel("difference, ROC-AUC x100", fontsize=9, color=INK2)
    axes[0].set_yticks(range(len(order)), [lab[k] for k in order], fontsize=9, color=INK)
    axes[0].set_ylim(len(order) - 0.4, -0.7)
    handles = [
        plt.Line2D([], [], color=C_T, lw=2.2, marker="o", ms=4.5, label="t-interval, df 4"),
        plt.Line2D([], [], color=C_NB, lw=2.2, marker="o", ms=4.5, label="Nadeau-Bengio (rotations only)"),
        plt.Line2D(
            [],
            [],
            color=C_BOOT,
            lw=2.2,
            marker="o",
            ms=4.5,
            label="bootstrap, pre-registered D24-D (under-covers at n=5)",
        ),
        plt.Line2D(
            [], [], color="#a8a7a2", marker="o", ls="", ms=4, label="per rotation (D24-A) / per seed (paper split)"
        ),
    ]
    fig.legend(handles=handles, loc="upper center", ncol=4, frameon=False, fontsize=9, bbox_to_anchor=(0.5, 0.995))
    fig.suptitle(
        "D24 contrasts: 95% intervals over 5 units. Dashed lines: the rules' ±3 threshold. "
        "Right-hand labels: D24 verdict as logged. Paper split = 5 seeds on one split (seed noise only).",
        y=0.035,
        fontsize=9,
        color=INK2,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 0.95))
    fig.savefig(path, dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)


def power_fig(path: Path, rng: np.random.Generator, sds) -> None:
    plt.switch_backend("agg")
    grid = np.linspace(0, 60, 601)
    ramp = ("#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281", "#0d366b")
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4), sharey=True, facecolor="#fcfcfb")
    for ax, kind in zip(axes, ("normal", "t3"), strict=True):
        ax.set_facecolor("#fcfcfb")
        for sd, col in zip(sds, ramp, strict=True):
            Z = rng.standard_normal((R_SIM, 5)) if kind == "normal" else rng.standard_t(3, (R_SIM, 5)) / np.sqrt(3)
            up = np.sort(rule_edges(Z * sd)[0])
            ax.plot(grid, np.searchsorted(up, grid) / R_SIM, color=col, lw=2, label=f"SD {sd:g}")
        ax.axhline(0.8, color="#b9b8b3", lw=0.9, ls="--")
        ax.axvline(3, color="#b9b8b3", lw=0.9, ls="--")
        ax.set_title(f"{kind} errors", fontsize=10.5, color=INK)
        ax.set_xlabel("true effect, ROC-AUC x100", fontsize=9, color=INK2)
        ax.grid(color=GRID, lw=0.5)
        ax.tick_params(colors=INK2, labelsize=8.5)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    axes[0].set_ylabel("P(rule reads 'first term wins')", fontsize=9, color=INK2)
    axes[1].legend(frameon=False, fontsize=8.5, title="SD over 5 units", title_fontsize=8.5)
    fig.suptitle("Power of the D18 rule (mean > 3 and >= 4 of 5 positive) by unit SD", fontsize=11, color=INK)
    fig.tight_layout()
    fig.savefig(path, dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)


def selfcheck(rng: np.random.Generator) -> None:
    E = rng.standard_normal((2000, 5)) * 4
    up, down = rule_edges(E)
    for d in (-6.0, 0.0, 3.0, 7.5):
        direct = np.array([rule(e + d) for e in E])
        assert np.array_equal(direct == "+", up < d) and np.array_equal(direct == "-", down > d)
    assert signflip_p([1, 2, 3, 4, 5]) == 2 / 32 and signflip_p([1, -1, 1, -1, 0]) == 1.0
    assert np.allclose(holm([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06])
    assert vc_rot_seed([[1, 1, 1], [3, 3, 3]]) == (np.sqrt(2.0), 0.0)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20261101)
    selfcheck(rng)
    rows, rocs = build_rows()
    check_bootstrap_table(rows)
    ratios = {t: nb_ratio(t) for t in UNIT_DIR}
    for r in rows:
        analyse(r, None if r["paper"] else ratios[r["tags"]][0], rng)
        if r["family"] in ("C1", "Artifact 1", "features", "D17") and not (r["paper"] and r["family"] != "C1"):
            code = rule(r["units"], 3.0, None, r["family"] == "D17")  # generalised rule == logged rule
            want = {
                "+": ("first term wins", "SSL adds to random init"),
                "-": ("second term wins", "neither rule met"),
                ".": ("no difference shown", "neither rule met"),
                "E": ("random features explain it",),
            }[code]
            assert r["verdict"] in want, (name(r), code, r["verdict"])
    cov = boot_coverage(rng)
    # (h1) rotation x seed
    vc1 = []
    for tags in ("S1E,S1M", "S3E,S3M", "S3FE,S3FM", "P1E"):
        roc = rocs[tags]
        for model in ("biot", "cbramod"):
            for arm in ARMS:
                if tags == "P1E":
                    for probe in ("linear", "mlp_fullft"):
                        v = roc.get((model, arm, "paper", probe))
                        if v:
                            vc1.append(
                                dict(
                                    setting=SETTING[tags],
                                    model=model,
                                    q=f"{arm} ({probe})",
                                    rot=None,
                                    seed=float(np.std(list(v.values()), ddof=1)),
                                )
                            )
                    continue
                M = [
                    [roc[(model, arm, r, "linear")][s] for s in sorted(roc[(model, arm, r, "linear")])]
                    for r in ROTS
                ]
                vc1.append(
                    dict(
                        setting=SETTING[tags],
                        model=model,
                        q=arm,
                        **dict(zip(("rot", "seed"), vc_rot_seed(M), strict=True)),
                    )
                )
            for r in (r for r in rows if r["tags"] == tags and r["model"] == model):
                if r["paper"]:
                    vc1.append(
                        dict(
                            setting=r["setting"],
                            model=model,
                            q=f"{r['a']} - {r['b']} ({r['probe']})",
                            rot=None,
                            seed=r["sd"],
                        )
                    )
                else:
                    vc1.append(
                        dict(
                            setting=r["setting"],
                            model=model,
                            q=f"{r['a']} - {r['b']}",
                            **dict(zip(("rot", "seed"), vc_rot_seed(r["runs"]), strict=True)),
                        )
                    )
    # (h2) rotation / subject / seed
    vc2 = []
    for dataset, tags, paper in SETS:
        if paper:
            continue
        sub = subject_rocs(dataset, tags)
        for model in ("biot", "cbramod"):
            for a, b in [(arm, None) for arm in ARMS] + list(CONTRASTS):
                cells = {}
                for rot in ROTS:
                    seeds = sorted(s for (m_, a_, r_, s) in sub if (m_, a_, r_) == (model, "lp", rot))
                    cells[rot] = {
                        g: [sub[(model, a, rot, s)][g] - (sub[(model, b, rot, s)][g] if b else 0.0) for s in seeds]
                        for g in sub[(model, "lp", rot, seeds[0])]
                    }
                v = vc_nested(cells)
                vc2.append(
                    dict(
                        setting=SETTING[tags],
                        model=model,
                        q=a if b is None else f"{a} - {b}",
                        **dict(zip(("rot", "sub", "seed", "n"), v, strict=True)),
                    )
                )
    sds_a = [r["sd"] for r in rows if not r["paper"]]
    sds_b = [r["sd"] for r in rows if r["paper"]]
    power_sds = dict(
        sds=(0.5, 2, 5, 10, 15, 25),
        a=f"{min(sds_a):.1f} to {max(sds_a):.1f}",
        b=f"{min(sds_b):.2f} to {max(sds_b):.1f}",
    )
    (OUT / "e10-stats.md").write_text(e10_md(rows, ratios, cov, vc1, vc2, power_sds))
    forest(rows, OUT / "forest-d24.png")
    power_fig(OUT / "power-rule.png", rng, power_sds["sds"])
    # E22
    win = ("first term wins", "second term wins")
    dis = [
        f"{name(r)} ({r['verdict']}, bootstrap {ci(r['boot'])})"
        for r in rows
        if r["family"] in FAMS[:3]
        and not (r["paper"] and r["family"] != "C1")
        and ((r["verdict"] in win) != (r["boot"][0] > 0 or r["boot"][1] < 0))
    ]
    sr = without_sr(rocs)
    ts, existing, newest = timestamps()
    (OUT / "e22-hygiene.md").write_text(e22_md(sr, ts, existing, newest, "; ".join(dis)))
    (OUT / "stats.json").write_text(
        json.dumps(
            dict(
                e10=[{k: v for k, v in r.items()} for r in rows],
                nb_ratio=ratios,
                boot_coverage=cov,
                vc_rot_seed=vc1,
                vc_subject=vc2,
                e22_without_sr=sr,
                e22_timestamps=ts,
                e22_d22_existing=existing,
                e22_ci_verdict_disagreements=dis,
            ),
            indent=1,
            default=float,
        )
    )
    print(f"wrote {OUT}: e10-stats.md, e22-hygiene.md, stats.json, forest-d24.png, power-rule.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
