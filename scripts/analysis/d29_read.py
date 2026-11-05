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
D29 rotations, the CBraMod control vs its batch-128 LP of D27-C), read with the same strings and the
same 3-point threshold as the ROC readings (a ROC-scale threshold; on AP it is only a label).
Writes artifacts/analysis/D29/{README.md, d29.json}.
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


def passes(t: dict) -> bool:
    """D29: the 95% t-interval excludes 0 with mean > 3."""
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


# ---- formatting --------------------------------------------------------------------------------------
def ci(t: dict, key: str = "t") -> str:
    lo, hi = t[key]["ci95"]
    return f"[{lo:+.2f}, {hi:+.2f}]"


def tp(p: float) -> str:
    return f"{p:.2g}" if p < 0.001 else f"{p:.3f}"


def units(t: dict, nd: int = 2) -> str:
    return ", ".join(f"{x:+.{nd}f}" for x in t["units"])


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


def c1_rows(rec, ratios: dict) -> list[dict]:
    rows = []
    for head, tags in C1_PAPER:
        for model in ("biot", "cbramod"):
            row = {"setting": "DL's split", "model": model, "head": head, "tags": "+".join(tags), "unit": "seed"}
            for k in MET:
                a = [get(rec, tags, model, "last", "paper", s, head, k) for s in SR]
                b = [get(rec, tags, model, "lp", "paper", s, head, k) for s in SR]
                d = [x - y for x, y in zip(a, b, strict=True)]
                row[k] = {**tint(d), "rule": paired(d), "last": float(np.mean(a)), "lp": float(np.mean(b))}
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
                    row[k] = {
                        **tint(d, ratios[rk]),
                        "rule": paired(d),
                        "last": float(np.mean(a)),
                        "lp": float(np.mean(b)),
                    }
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


def paper_c2c3(rec) -> dict:
    """DL's split: BIOT 5-seed mean at data_seed 1 (E30a primary), CBraMod seed 42 (D24-C) vs R3E-b128."""
    out = {}
    for model, seeds in (("biot", SR), ("cbramod", (42,))):
        out[model] = {}
        for k in MET:
            cur = {
                sub: float(
                    np.mean(
                        [
                            m(
                                rec,
                                (
                                    f"{'C2' if sub in NA else 'C3'}{'E' if s == 42 else 'X'}-{sub}",
                                    model,
                                    "last",
                                    "paper",
                                    s,
                                ),
                                "linear",
                                k,
                            )
                            for s in seeds
                        ]
                    )
                )
                for sub in NA + PA
            }
            lp = float(np.mean([m(rec, ("R3E-b128", model, "lp", "paper", s), "linear", k) for s in SR]))
            out[model][k] = {"curve": cur, "lp": lp, "verdicts": verdicts(cur, lp, NA, PA)}
    return out


def cbramod_rot(rec, t: str) -> dict:
    """CBraMod control S3CC / S3FCC at S_r vs S3CLPB / S3FCLPB at S_r (the D27-C reading)."""
    out = {}
    for k in MET:
        cur = {
            sub: float(
                np.mean(
                    [
                        m(rec, (f"{t}CC-{sub}", "cbramod", "last", rot, SR[r]), "linear", k)
                        for r, rot in enumerate(ROTS)
                    ]
                )
            )
            for sub in NC + PC
        }
        lp = float(
            np.mean([m(rec, (f"{t}CLPB", "cbramod", "lp", rot, SR[r]), "linear", k) for r, rot in enumerate(ROTS)])
        )
        out[k] = {"curve": cur, "lp": lp, "verdicts": verdicts(cur, lp, NC, PC)}
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

    # ---- PR-AUC readings ----
    prev = prevalence(rec)
    c1 = c1_rows(rec, ratios)
    pc = paper_c2c3(rec)
    js["pr"] = {"prevalence_test_pct": prev, "C1": c1, "C2C3_dl_split": pc, "C2C3_rotations": {}}
    pr = [
        "",
        "## PR-AUC readings (descriptive; D29 PR-AUC item)",
        "",
        "AP = average precision (sklearn), trapz = trapezoid area under the PR curve (the released metric), "
        "x100, test split at the ROC-selected probe epoch (selection unchanged). The rule strings and the "
        "3-point threshold are the ROC rules applied unchanged; AP sits near the prevalence, so 3 AP points are "
        "a much larger relative change on Siena than on DL's split. Test prevalence x100: "
        + "; ".join(
            f"{k} {v:.2f}" if isinstance(v, float) else f"{k} " + "/".join(f"{x:.2f}" for x in v)
            for k, v in prev.items()
        ),
        "",
        "### C1 (SA - LP = last - lp)",
        "",
        "Units: 5 seeds on DL's split (seed uncertainty on one split), 5 rotation means of 3 seeds otherwise. "
        "Rule string = the D18 / D24-B paired rule (|mean| > 3, 4 of 5 same sign), descriptive here. ROC "
        "means re-derive the published D24-A/B, D27-B and P1Z numbers (asserted).",
        "",
        "| setting | model | head (tags) | metric | lp | last | last - lp | 95% t | NB 95% | TOST p | > 0 | "
        "string | per unit |",
        "|---" * 13 + "|",
    ]
    for r in c1:
        for k, lab in MET.items():
            x = r[k]
            nb = ci(x, "nb") if "nb" in x else "-"
            pr.append(
                f"| {r['setting']} | {r['model']} | {r['head']} ({r['tags']}) | {lab} | {x['lp']:.2f} | "
                f"{x['last']:.2f} | {x['mean']:+.2f} | {ci(x)} | {nb} | {tp(x['t']['tost3_p'])} | "
                f"{x['n_pos']}/5 | {x['rule']} | {units(x)} |"
            )
    agree = Counter(
        (r["roc_auc"]["rule"] == r["avg_precision"]["rule"], r["roc_auc"]["rule"] == r["pr_auc_trapz"]["rule"])
        for r in c1
    )
    flips = [
        f"{r['setting']} {r['model']} {r['head']}: ROC {r['roc_auc']['rule']} ({r['roc_auc']['mean']:+.2f}), "
        f"AP {r['avg_precision']['rule']} ({r['avg_precision']['mean']:+.2f}), trapz {r['pr_auc_trapz']['rule']} "
        f"({r['pr_auc_trapz']['mean']:+.2f})"
        for r in c1
        if len({r[k]["rule"] for k in MET}) > 1
    ]
    js["pr"]["C1_string_changes"] = flips
    pr += [
        "",
        f"C1 rows where the AP or trapz string differs from the ROC string: {len(flips)} of {len(c1)} "
        f"(AP/trapz agreement with ROC counts {dict(agree)}):",
        "",
    ] + [f"- {f}" for f in flips or ["none"]]

    pr += [
        "",
        "### C2/C3 on DL's split (CHB-MIT paper split; E30a / D24-C records)",
        "",
        "BIOT: 5-seed mean at data_seed 1 (C2E seed 42 + C2X/C3X), CBraMod: seed 42 (C2E/C3E, as D24-C); LP = "
        "R3E-b128 5-seed mean, linear head batch 128.",
        "",
        "| model | metric | " + " | ".join(NA + PA) + " | LP | C2 | numbers | C3 | numbers |",
        "|---" * (6 + len(NA + PA)) + "|",
    ]
    for model, d in pc.items():
        for k, lab in MET.items():
            x = d[k]
            v = x["verdicts"]
            pr.append(
                f"| {model} | {lab} | "
                + " | ".join(f"{x['curve'][s]:.2f}" for s in NA + PA)
                + f" | {x['lp']:.2f} | {v['C2']} | {v['C2_numbers']} | {v['C3']} | {v['C3_numbers']} |"
            )
    assert pc["biot"]["roc_auc"]["verdicts"]["C2"].startswith("not testable")  # E30a primary
    assert pc["biot"]["roc_auc"]["verdicts"]["C3"] == "uninformative"
    assert pc["cbramod"]["roc_auc"]["verdicts"]["C2"].startswith("not testable")  # D24-C
    assert pc["cbramod"]["roc_auc"]["verdicts"]["C3"] == "uninformative"

    pr += [
        "",
        "### C2/C3 on the Siena rotations",
        "",
        "BIOT: the D29 records (last, last_noise; LP S3LPBD / S3FLPBD), the E30 reading (mean over rotations of "
        "3-seed means) and the D29 noise rule, each head and metric. CBraMod: the E30 control S3CC / S3FCC "
        "(seed S_r) vs its batch-128 LP S3CLPB / S3FCLPB at S_r (the D27-C reading); linear head only (no CBraMod "
        "linear_z or noise run at fixed compute).",
        "",
        "| setting | model | head | metric | " + " | ".join(SUBS) + " | LP | C2 | C3 | noise C2 | noise C3 | "
        "last - last_noise per subset [95% t] |",
        "|---" * (10 + len(SUBS)) + "|",
    ]
    for t, name, rk in SETTINGS:
        js["pr"]["C2C3_rotations"][name] = {"biot": {}, "cbramod": cbramod_rot(rec, t)}
        for head in HEADS:
            js["pr"]["C2C3_rotations"][name]["biot"][head] = {}
            for k, lab in MET.items():
                b = rule_block(rec, t, name, head, k, ratios[rk])
                b.pop("seed_values")
                js["pr"]["C2C3_rotations"][name]["biot"][head][k] = b
                v, nv = b["verdicts"]["last (PRIMARY)"], b["noise_verdict"]
                pr.append(
                    f"| {name} | biot | {head} | {lab} | "
                    + " | ".join(f"{b['curve']['last'][s]:.2f}" for s in SUBS)
                    + f" | {b['lp']:.2f} | {v['C2']} | {v['C3']} | {nv['C2']} | {nv['C3']} | "
                    + "; ".join(f"{b['noise'][s]['mean']:+.2f} {ci(b['noise'][s])}" for s in SUBS)
                    + " |"
                )
        cb = js["pr"]["C2C3_rotations"][name]["cbramod"]
        for k, lab in MET.items():
            x = cb[k]
            cells = " | ".join(f"{x['curve'][s]:.2f}" if s in x["curve"] else "-" for s in SUBS)
            pr.append(
                f"| {name} | cbramod | linear | {lab} | {cells} | {x['lp']:.2f} | {x['verdicts']['C2']} | "
                f"{x['verdicts']['C3']} | - | - | - |"
            )
        assert cb["roc_auc"]["verdicts"]["C2"].startswith("not testable"), cb["roc_auc"]  # D27-C
        assert cb["roc_auc"]["verdicts"]["C3"] == "uninformative", cb["roc_auc"]
    c23 = []
    for model, d in pc.items():
        c23 += [
            f"DL's split {model} linear {MET[k]}: C2 {d[k]['verdicts']['C2']}, C3 {d[k]['verdicts']['C3']} "
            f"(ROC: C2 {d['roc_auc']['verdicts']['C2']}, C3 {d['roc_auc']['verdicts']['C3']})"
            for k in MET
            if k != "roc_auc"
            and (d[k]["verdicts"]["C2"], d[k]["verdicts"]["C3"])
            != (d["roc_auc"]["verdicts"]["C2"], d["roc_auc"]["verdicts"]["C3"])
        ]
    for name, d in js["pr"]["C2C3_rotations"].items():
        heads = [
            (
                f"biot {h}",
                {
                    k: {
                        **x["verdicts"]["last (PRIMARY)"],
                        **{f"noise {c}": x["noise_verdict"][c] for c in ("C2", "C3")},
                    }
                    for k, x in dd.items()
                },
            )
            for h, dd in d["biot"].items()
        ]
        heads.append(("cbramod linear", {k: x["verdicts"] for k, x in d["cbramod"].items()}))
        for lab, vs in heads:
            for k in MET:
                diff = [
                    f"{q} {vs[k][q]} (ROC: {vs['roc_auc'][q]})"
                    for q in ("C2", "C3", "noise C2", "noise C3")
                    if q in vs[k] and vs[k][q] != vs["roc_auc"][q]
                ]
                if k != "roc_auc" and diff:
                    c23.append(f"{name} {lab} {MET[k]}: " + "; ".join(diff))
    js["pr"]["C2C3_string_changes"] = c23
    pr += ["", f"C2/C3 readings where the AP or trapz string differs from the ROC string ({len(c23)}):", ""]
    pr += [f"- {x}" for x in c23 or ["none"]]
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
        f"- PR-AUC: C1 rows whose AP / trapz string differs from ROC: {len(flips)} of {len(c1)}: "
        + "; ".join(flips or ["none"]),
        f"- PR-AUC: C2/C3 readings whose AP / trapz string differs from ROC: {len(c23)}: "
        + "; ".join(c23 or ["none"]),
    ]
    pr += ["", "Numbers behind the PR rows (C2 / C3 describe strings):", ""]
    for name, d in js["pr"]["C2C3_rotations"].items():
        for head, dd in d["biot"].items():
            for k, b in dd.items():
                v = b["verdicts"]["last (PRIMARY)"]
                pr.append(
                    f"- {name} biot {head} {MET[k]}: C2 {v['C2_numbers']}; C3 {v['C3_numbers']}; noise TOST p "
                    + ", ".join(f"{s} {tp(b['noise'][s]['t']['tost3_p'])}" for s in SUBS)
                )
        for k, x in d["cbramod"].items():
            pr.append(
                f"- {name} cbramod linear {MET[k]}: C2 {x['verdicts']['C2_numbers']}; C3 "
                f"{x['verdicts']['C3_numbers']}"
            )

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
    (OUT / "d29.json").write_text(json.dumps(js, indent=1, default=str))
    print("\n".join(summary + [""] + notes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
