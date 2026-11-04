#!/usr/bin/env python3
"""D27 items C and D (notes/decisions.md "## D27"). Post hoc controls; rules as written there.

    .venv/bin/python scripts/analysis/d27_cd.py

C. CBraMod LP at probe batch 128 on Siena / Siena filtered (S3CLPB, S3FCLPB; arm lp; 3 seeds per
   rotation). Rule: the E30 C2/C3 rules for the CBraMod control curve (S3CC / S3FCC, seed S_r)
   against LP at seed S_r, with the E30 reader choices recorded in decisions.md "D25 outcomes, wave
   B part 2" (mean over the 5 rotations; |v - LP| <= 3 = "within 3"; C3 "> 3 above LP" at every P).
   The verdict code and the control records come from scripts/analysis/e30_c2c3.py (imported).
D. Supervised fine-tuning reference, probe `ft` (P1FT paper split 5 seeds; S1FT, S3FT rotations 3
   seeds; arms lp = pretrained init, lp_randinit = random init; both models). Pre-stated contrast:
   "pretraining helps fine-tuning" if ft(lp) - ft(lp_randinit) wins by the D18 paired rule on the
   rotations (per-rotation 3-seed means, the D24-A reading) and by the D24-B rule on the paper split
   (paired by seed, read_d24's paired()). Everything else is descriptive.
ROC is read through scripts/read_d24.load; raw records are scanned once for the record checks.
Writes artifacts/analysis/D27CD/{README.md, d27cd.json}.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from bootstrap_d24 import cluster_ci  # noqa: E402
from e30_c2c3 import NC, PC, ROTS, SR, c2, c3, describe, num, seeds3  # noqa: E402
from e30_c2c3 import load as e30_load  # noqa: E402
from e30_c2c3 import selfcheck as e30_selfcheck  # noqa: E402
from read_d24 import load as d24_load  # noqa: E402
from read_step1 import paired  # noqa: E402

LOCAL = ROOT / "artifacts" / "s3-results"
OUT = ROOT / "artifacts" / "analysis" / "D27CD"
MODELS = ("biot", "cbramod")
FT_ARMS = ("lp", "lp_randinit")
HEAD = {"biot": 257, "cbramod": 32001}            # linear head on the encoder output
SHORT = {"first term wins": "1st wins", "second term wins": "2nd wins", "no difference shown": "none"}
# setting -> (dataset, ft tag, D24 reference tags, logged linear tag, eval-data group)
FT_SETS = {"CHB-MIT paper split": ("chbmit", "P1FT", ("P1E",), "P1L", "chb"),
           "CHB-MIT rotations": ("chbmit", "S1FT", ("S1E", "S1M"), "S1L", "chb"),
           "Siena rotations": ("siena", "S3FT", ("S3E", "S3M"), "S3L", "sie")}
LPB = {"Siena": ("S3", "S3CLPB", "sie"), "Siena filtered": ("S3F", "S3FCLPB", "sief")}
GROUP = {"P1E": "chb", "P1L": "chb", "S1E": "chb", "S1M": "chb", "S1L": "chb", "P1FT": "chb", "S1FT": "chb",
         "S3E": "sie", "S3M": "sie", "S3L": "sie", "S3FT": "sie", "S3CLPB": "sie",
         "S3FE": "sief", "S3FM": "sief", "S3FCLPB": "sief"}
# Published CHB-MIT fine-tuning rows (fractions), checked against the PDFs' extracted text.
BIOT_PUB = (("(Vanilla) BIOT", "random init", (0.6640, 0.0037), (0.2573, 0.0088), (0.8646, 0.0030)),
            ("Pretrained BIOT (PREST)", "", (0.6942, 0.0431), (0.3072, 0.1187), (0.8679, 0.0106)),
            ("Pretrained BIOT (PREST+SHHS)", "= our checkpoint", (0.6788, 0.0036), (0.3090, 0.0003),
             (0.8752, 0.0022)),
            ("Pretrained BIOT (6 EEG datasets)", "", (0.7068, 0.0457), (0.3277, 0.0460), (0.8761, 0.0284)))
CBRA_PUB = (("BIOT (as cited by CBraMod)", (0.7068, 0.0457), (0.3277, 0.0460), (0.8761, 0.0284)),
            ("LaBraM-Base", (0.7075, 0.0358), (0.3287, 0.0402), (0.8679, 0.0199)),
            ("CBraMod", (0.7398, 0.0284), (0.3689, 0.0382), (0.8892, 0.0154)))


def ft_verdict(d) -> tuple[str, str]:
    """D27-D: 'pretraining helps fine-tuning' iff ft(lp) - ft(lp_randinit) wins by the paired rule."""
    s = paired(d)
    return ("pretraining helps fine-tuning" if s == "first term wins"
            else "pretraining helps fine-tuning: not shown"), s


def selfcheck() -> None:
    e30_selfcheck()
    assert ft_verdict([5, 5, 5, 5, -1])[0] == "pretraining helps fine-tuning"
    assert ft_verdict([4, 4, 4, -1, -1])[0].endswith("not shown")
    assert ft_verdict([-4, -4, -4, -4, -4]) == ("pretraining helps fine-tuning: not shown", "second term wins")


def mse(v) -> tuple[float, float]:
    v = np.asarray(v, dtype=float)
    return float(v.mean()), float(v.std(ddof=1) / np.sqrt(len(v)))


def tci(v) -> tuple[float, float]:
    """t 95% interval over the units (as in stats_d25.analyse), descriptive."""
    m, se = mse(v)
    h = stats.t(len(v) - 1).ppf(0.975) * se
    return m - h, m + h


def f1(x: float) -> str:
    return f"{x:.1f}"


def pm(v) -> str:
    m, s = mse(v)
    return f"{m:.1f} ± {s:.1f}"


def scan() -> dict[str, list[dict]]:
    """run_tag -> non-smoke records, for the tags this reader checks."""
    tags = set(GROUP) | {"P1FT", "S1FT", "S3FT"}
    out: dict = defaultdict(list)
    for p in LOCAL.rglob("results/*.json"):
        if p.name.startswith(("diag-", "test-index-", "val-index-", "report-")):
            continue
        r = json.loads(p.read_text())
        if r.get("run_tag") in tags and not r.get("smoke"):
            out[r["run_tag"]].append(r)
    return out


def check_history(r: dict, probe: str) -> None:
    """best_epoch = first argmax of val_curve; test_at_best / test_last are the logged epochs' metrics."""
    pr = r["probes"][probe]
    vc, h = pr["val_curve"], pr["history"]
    assert len(vc) == len(h) == pr["spec"]["epochs"] == 10, r["key"]
    assert pr["best_epoch"] == int(np.argmax(vc)) and pr["best_val"] == max(vc), r["key"]
    assert [x["val"]["roc_auc"] for x in h] == vc, r["key"]
    assert h[pr["best_epoch"]]["test_plot_only"] == pr["test_at_best"], r["key"]
    assert h[-1]["test_plot_only"] == pr["test_last"], r["key"]


def checks(raw: dict, ctrl: dict) -> tuple[list[str], dict]:
    notes, eh, info = [], defaultdict(set), {}
    for tag, rs in raw.items():
        for r in rs:
            eh[(GROUP.get(tag, "chb" if r["dataset"] == "chbmit" else "sie"), r["split"])].add(r["eval_hash"])
    for (t, _m, _a, rot, _s), r in ctrl.items():   # every E30 Siena record (incl. the CBraMod control)
        if t.startswith("S3"):
            eh[("sief" if t.startswith("S3F") else "sie", rot)].add(r["eval_hash"])
    mixed = {k: v for k, v in eh.items() if len(v) > 1}
    assert not mixed, f"eval_hash differs within an eval-data group: {mixed}"
    assert all(eh[("sie", r)] != eh[("sief", r)] for r in ROTS), "filtered = unfiltered eval data"
    notes.append(f"- one eval_hash per (eval data, split) across the new records, the records they pair with "
                 f"(E30 S3CC/S3FCC, S3E/S3M, S3FE/S3FM, S1E/S1M, P1E, the logged linear P1L/S1L/S3L) and both "
                 f"models: {len(eh)} (data, split) cells; Siena filtered differs from unfiltered in all 5 "
                 "rotations (the records do not store the data variant: identified by run_tag and eval_hash)")
    pins = {m: {r["adapt_spec"]["ckpt_sha256"] for t in ("S1M", "S3M") for r in raw[t]
                if r["model"] == m and r["arm"] == "lp"} for m in MODELS}
    assert all(len(v) == 1 and "" not in v for v in pins.values()), pins

    # ---- C: CBraMod LP at probe batch 128 ----
    for name, (pre, tag, _) in LPB.items():
        rs = raw[tag]
        keys = Counter((r["split"], r["seed"]) for r in rs)
        want = {(rot, s) for i, rot in enumerate(ROTS) for s in seeds3(i)}
        assert set(keys) == want and max(keys.values()) == 1, (tag, keys)
        for r in rs:
            got = (r["model"], r["arm"], r["dataset"], r["labels"])
            assert got == ("cbramod", "lp", "siena", "overlap"), r["key"]
            assert r["versions"] == {"adapt": 3, "probe": 4} and set(r["probes"]) == {"linear"}, r["key"]
            a = r["adapt_spec"]
            assert a["groups"] == [] and a["init"] == "pretrained", r["key"]
            assert a["ckpt_sha256"] in pins["cbramod"], r["key"]
            spec = r["probes"]["linear"]["spec"]
            ref = ctrl[(f"{pre}CC-N896", "cbramod", "last", r["split"], SR[ROTS.index(r["split"])])]
            rspec = ref["probes"]["linear"]["spec"]
            bad = {k for k in set(spec) | set(rspec) if k != "seed" and spec.get(k) != rspec.get(k)}
            assert not bad and spec["batch"] == 128 and spec["backbone_mode"] == "eval" \
                and spec.get("tap", "encoder") == "encoder", (r["key"], bad)
            assert r["eval_hash"] == ref["eval_hash"], r["key"]
            assert r["probes"]["linear"]["head_params"] == HEAD["cbramod"], r["key"]
            check_history(r, "linear")
        be = Counter(r["probes"]["linear"]["best_epoch"] for r in rs)
        info[tag] = {"best_epoch": dict(sorted(be.items()))}
        notes.append(f"- {tag} ({name}): {len(rs)} records = 5 rotations x 3 seeds [S_r, 1000+r, 2000+r], 0 "
                     "duplicate, 0 smoke; CBraMod lp, pretrained checkpoint (sha pinned), probe v4 / adapt v3, "
                     "linear head 32,001 params, eval mode, encoder tap, probe batch 128, overlap labels; probe "
                     f"spec identical to the E30 control's ({pre}CC) apart from the seed; eval_hash = "
                     "the control's "
                     f"in every rotation; best epoch (0-based) counts {dict(sorted(be.items()))}")

    # ---- D: fine-tuning records ----
    for setting, (ds, tag, _refs, ltag, _g) in FT_SETS.items():
        rs = raw[tag]
        paper = setting.endswith("paper split")
        want = {(m, a, "paper", s) for m in MODELS for a in FT_ARMS for s in SR} if paper else \
            {(m, a, rot, s) for m in MODELS for a in FT_ARMS for i, rot in enumerate(ROTS) for s in seeds3(i)}
        keys = Counter((r["model"], r["arm"], r["split"], r["seed"]) for r in rs)
        assert set(keys) == want and max(keys.values()) == 1, (tag, set(want) ^ set(keys))
        lin = {(r["model"], r["arm"], r["split"], r["seed"]): r for r in raw[ltag] if r["arm"] in FT_ARMS}
        loss, be = [], Counter()
        for r in rs:
            k = (r["model"], r["arm"], r["split"], r["seed"])
            assert r["dataset"] == ds and r["labels"] == ("upstream" if paper else "overlap"), r["key"]
            assert r["versions"] == {"adapt": 3, "probe": 4} and set(r["probes"]) == {"ft"}, r["key"]
            a = r["adapt_spec"]
            assert a["groups"] == [] and not r["arm_spec"]["adapt"], r["key"]
            if r["arm"] == "lp":
                assert a["init"] == "pretrained" and a["ckpt_sha256"] in pins[r["model"]], r["key"]
            else:
                assert a["init"] == "random" and a["ckpt_sha256"] == "", r["key"]
            pr = r["probes"]["ft"]
            spec = pr["spec"]
            got = (spec["variant"], spec["backbone_mode"], spec.get("tap"), spec["batch"], spec["epochs"],
                   spec["lr"], spec["weight_decay"], spec["eta_min"], spec["scale"], spec.get("input_norm", ""))
            assert got == ("ft", "eval", "encoder", 256, 10, 4e-4, 0.05, 1e-5, 100.0, ""), (r["key"], got)
            assert pr["head_params"] == HEAD[r["model"]], r["key"]
            check_history(r, "ft")
            be[(r["model"], r["arm"], pr["best_epoch"])] += 1
            lr = lin[k]["probes"]["linear"]
            ls = lr["spec"]
            assert (ls["lr"], ls["batch"], ls["epochs"], ls["backbone_mode"]) == (4e-4, 256, 10, "eval"), ltag
            tf = [x["train_loss"] for x in pr["history"]]
            tl = [x["train_loss"] for x in lr["history"]]
            loss.append({"model": r["model"], "arm": r["arm"], "split": r["split"], "seed": r["seed"],
                         "ft0": tf[0], "lin0": tl[0], "ft9": tf[-1], "lin9": tl[-1],
                         "min_absdiff": float(np.min(np.abs(np.subtract(tf, tl)))),
                         "roc_ft": 100 * pr["test_at_best"]["roc_auc"],
                         "roc_lin": 100 * lr["test_at_best"]["roc_auc"], "sec": pr["seconds"]})
        info[tag] = {"loss": loss, "best_epoch": {f"{m}/{a}/{e}": n for (m, a, e), n in sorted(be.items())}}
        assert all(x["min_absdiff"] > 1e-6 for x in loss), f"{tag}: an ft train-loss curve equals the linear one"
        notes.append(f"- {tag} ({setting}): {len(rs)} records = 2 models x 2 arms x "
                     f"{'5 seeds' if paper else '5 rotations x 3 seeds'}, 0 duplicate, 0 smoke; probe `ft` only, "
                     "v4 / adapt v3, no SSL step (groups [], adapt False), lp = pinned pretrained checkpoint, "
                     "lp_randinit = random init (no checkpoint); spec ft / eval mode / encoder tap / batch 256 / "
                     "10 epochs / head lr 4e-4 (encoder 0.1x) / wd 0.05 / cosine to 1e-5; head params BIOT 257, "
                     f"CBraMod 32,001; labels {'upstream' if paper else 'overlap'}; 10-epoch history present, "
                     "best_epoch = argmax(val ROC), test_at_best and test_last equal the logged epochs' metrics; "
                     f"eval_hash = {'P1E/P1L' if paper else ltag[:2] + 'E/' + ltag[:2] + 'M/' + ltag} in "
                     "every split")
    return notes, info


def main() -> int:
    selfcheck()
    raw = scan()
    ctrl, _, _ = e30_load()
    notes, info = checks(raw, ctrl)
    js: dict = {"C": {}, "D": {}, "checks": info}
    summary: list[str] = []
    md = ["# D27-C and D27-D: CBraMod LP at probe batch 128 (E30 C2/C3 control) and the fine-tuning reference",
          "",
          "Post hoc controls (notes/decisions.md \"## D27\", designed after all D24-D26 data were seen, before "
          "any D27 run). ROC-AUC x100 at the val-selected epoch. Script: scripts/analysis/d27_cd.py. Anything not "
          "named a rule below is descriptive/post hoc.", "", "## Record checks", ""] + notes

    # ================= C =================
    md += ["", "## C. CBraMod LP at probe batch 128: the E30 C2/C3 reading for the CBraMod control", "",
           "Rule (D27-C): the E30 C2/C3 rules (D15 rules; decisions.md \"## D15\") for the CBraMod control curve "
           "(E30 run tags S3CC / S3FCC, arm `last`, fixed_c 132 SSL steps, N896 / N4174 / P2N2048 / "
           "P10N2048, seed "
           "S_r) against LP at seed S_r. E30 reader choices (decisions.md \"D25 outcomes, wave B part "
           "2\"): curve and "
           "LP = mean over the 5 rotations; \"within 3 of LP at every N\" = |v - LP| <= 3 for every N; C3 \"> 3 "
           "above LP\" = every P point; flat but not > 3 above LP = \"uninformative\". Verdict code imported from "
           "scripts/analysis/e30_c2c3.py (c2, c3, describe).", ""]
    for name, (pre, tag, _) in LPB.items():
        lpb = d24_load(str(LOCAL), "siena", {tag})
        lp128 = {rot: lpb[("cbramod", "lp", rot, "linear")] for rot in ROTS}
        assert all(set(lp128[rot]) == set(seeds3(i)) for i, rot in enumerate(ROTS)), tag
        cb = {rot: {sub: 100 * ctrl[(f"{pre}CC-{sub}", "cbramod", "last", rot, SR[i])]["probes"]["linear"]
                    ["test_at_best"]["roc_auc"] for sub in NC + PC} for i, rot in enumerate(ROTS)}
        curve = {sub: float(np.mean([cb[rot][sub] for rot in ROTS])) for sub in NC + PC}
        lp_sr = [lp128[rot][SR[i]] for i, rot in enumerate(ROTS)]
        lp_3 = [float(np.mean(list(lp128[rot].values()))) for rot in ROTS]
        LP, LP3 = float(np.mean(lp_sr)), float(np.mean(lp_3))
        cn, cp = {num(x): curve[x] for x in NC}, {num(x): curve[x] for x in PC}
        v = {"C2": c2(cn, LP), "C2_numbers": describe(cn, LP, "N"), "C3": c3(cp, LP),
             "C3_numbers": describe(cp, LP, "P")}
        v3 = {"C2": c2(cn, LP3), "C2_numbers": describe(cn, LP3, "N"), "C3": c3(cp, LP3),
              "C3_numbers": describe(cp, LP3, "P")}
        per_rot = {}
        for i, rot in enumerate(ROTS):
            pn, pp = {num(x): cb[rot][x] for x in NC}, {num(x): cb[rot][x] for x in PC}
            per_rot[rot] = {"C2": c2(pn, lp_sr[i]), "C2_numbers": describe(pn, lp_sr[i], "N"),
                            "C3": c3(pp, lp_sr[i]), "C3_numbers": describe(pp, lp_sr[i], "P")}
        # probe batch effect, CBraMod (descriptive): b128 - b256 at S_r (S3E / S3FE) and 3 seeds (+ S3M / S3FM)
        b256 = d24_load(str(LOCAL), "siena", {f"{pre}E", f"{pre}M"})
        b256_sr = [b256[("cbramod", "lp", rot, "linear")][SR[i]] for i, rot in enumerate(ROTS)]
        b256_3 = [float(np.mean([b256[("cbramod", "lp", rot, "linear")][s] for s in seeds3(i)]))
                  for i, rot in enumerate(ROTS)]
        d_sr = [a - b for a, b in zip(lp_sr, b256_sr, strict=True)]
        d_3 = [a - b for a, b in zip(lp_3, b256_3, strict=True)]
        # the rule-pinned numbers of E30 must come out of the same records
        e30 = json.loads((ROOT / "artifacts" / "analysis" / "E30" / "e30.json").read_text())["b"][name]
        assert all(abs(e30["cbramod_grand"][s][0] - curve[s]) < 1e-9 for s in NC + PC), name
        assert all(abs(e30["cbramod_lp_b256_S_r"][rot] - b256_sr[i]) < 1e-9 for i, rot in enumerate(ROTS)), name
        summary.append(f"- C, CBraMod control, {name}: C2 **{v['C2']}** ({v['C2_numbers']}); C3 **{v['C3']}** "
                       f"({v['C3_numbers']}); LP b128 at S_r {LP:.2f}, control {curve['N4174']:.2f} (N4174)")
        js["C"][name] = {"control_S_r": cb, "curve": curve, "lp_b128_S_r": dict(zip(ROTS, lp_sr, strict=True)),
                         "lp_b128_3seed_rot_means": dict(zip(ROTS, lp_3, strict=True)), "LP": LP, "LP_3seed": LP3,
                         "verdict": v, "verdict_3seed_LP": v3, "per_rotation": per_rot,
                         "lp_b256_S_r": b256_sr, "b128_minus_b256_S_r": d_sr, "b128_minus_b256_3seed": d_3}
        md += [f"### {name} ({pre}CC control vs {tag})", "",
               f"| rotation (S_r) | {' | '.join(NC + PC)} | LP b128 at S_r | LP b128 3-seed mean | LP b256 at S_r "
               f"({pre}E) |", "|---" * (5 + len(NC + PC)) + "|"]
        for i, rot in enumerate(ROTS):
            md.append(f"| {rot} ({SR[i]}) | " + " | ".join(f1(cb[rot][x]) for x in NC + PC)
                      + f" | {lp_sr[i]:.1f} | {lp_3[i]:.1f} | {b256_sr[i]:.1f} |")
        md.append("| **mean ± SEM** | " + " | ".join(f"**{pm([cb[r][x] for r in ROTS])}**" for x in NC + PC)
                  + f" | **{pm(lp_sr)}** | {pm(lp_3)} | {pm(b256_sr)} |")
        md += ["", "| reading | C2 verdict | numbers | C3 verdict | numbers |", "|---|---|---|---|---|",
               f"| control at S_r vs LP b128 at S_r, rotation means (D27-C RULE) | **{v['C2']}** | "
               f"{v['C2_numbers']} "
               f"| **{v['C3']}** | {v['C3_numbers']} |",
               f"| control at S_r vs LP b128 3-seed rotation means (descriptive/post hoc) | {v3['C2']} | "
               f"{v3['C2_numbers']} | {v3['C3']} | {v3['C3_numbers']} |", "",
               "Per rotation, control vs that rotation's LP at S_r (descriptive/post hoc): "
               f"C2 {dict(Counter(x['C2'] for x in per_rot.values()))}; "
               f"C3 {dict(Counter(x['C3'] for x in per_rot.values()))}.", ""]
        md += [f"- {rot}: C2 {x['C2']} ({x['C2_numbers']}); C3 {x['C3']} ({x['C3_numbers']})"
               for rot, x in per_rot.items()]
        md += ["", f"CBraMod probe batch (descriptive/post hoc): LP b128 - b256, per rotation at S_r "
                   f"{', '.join(f'{x:+.1f}' for x in d_sr)} (mean {np.mean(d_sr):+.1f}); 3-seed means "
                   f"{', '.join(f'{x:+.1f}' for x in d_3)} (mean {np.mean(d_3):+.1f}).", ""]

    md += ["Relation to E30 (decisions.md \"D25 outcomes, wave B part 2\"): the recorded CBraMod-control "
           "strings were C2 \"not supported or not testable\" and C3 \"flat, supported vs uninformative "
           "undetermined\" (no batch-128 LP). With S3CLPB / S3FCLPB they resolve to the strings above. The E30 "
           "descriptive reading against the batch-256 LP (Siena: C2 \"not supported\", C3 \"supported as "
           "written\", +3.76 above LP) does not hold against the batch-128 LP: part of that +3.76 was probe "
           "batch, not adaptation.", ""]

    # ================= D =================
    md += ["## D. Supervised fine-tuning reference (probe `ft`)", "",
           "Recipe (D27-D, from the records): linear head on the encoder output + the whole encoder "
           "trained on the "
           "labels; head lr 4e-4, encoder lr 0.1 x (4e-5); AdamW wd 0.05; cosine (both groups) to 1e-5; "
           "10 epochs; "
           "batch 256; BCE on logits; selection on val ROC; the encoder runs in EVAL mode during training and "
           "scoring (dropout off: `backbone_mode eval`); the caller's encoder is restored afterwards. Trained "
           "encoder parameters (from the code, models built at random init on CPU): BIOT 3,186,688 (all of "
           "`biot`); CBraMod 4,883,600 of 4,924,000 (`mask_encoding` and `proj_out` get no gradient on "
           "the encoder "
           "tap, so AdamW leaves them unchanged). The records store only the head size (BIOT 257, "
           "CBraMod 32,001).",
           "", "Rule (D27-D, pre-stated): \"pretraining helps fine-tuning\" if ft(lp) - ft(lp_randinit) wins: D18 "
           "paired rule on rotations (mean > 3 and > 0 in >= 4/5 rotations; per-rotation 3-seed means as "
           "in D24-A), "
           "D24-B on the paper split (mean > 3 and > 0 for >= 4/5 seeds). The rule output string of read_step1."
           "paired() is shown next to it (\"second term wins\" is not a pre-stated verdict; read it as "
           "descriptive). "
           "CIs are descriptive (cluster bootstrap of scripts/bootstrap_d24.py, 10,000 resamples, seed 20261101; "
           "t 95% over the 5 units).", ""]
    rng = np.random.default_rng(20261101)
    verdict_rows, ref_rows, arm_rows = [], [], []
    for setting, (ds, tag, refs, _ltag, _g) in FT_SETS.items():
        paper = setting.endswith("paper split")
        ft = d24_load(str(LOCAL), ds, {tag})
        ref = d24_load(str(LOCAL), ds, set(refs))
        js["D"][setting] = {}
        for model in MODELS:
            if paper:
                A = {a: ft[(model, a, "paper", "ft")] for a in FT_ARMS}
                units = {a: [A[a][s] for s in SR] for a in FT_ARMS}
                d = [x - y for x, y in zip(units["lp"], units["lp_randinit"], strict=True)]
                boot = cluster_ci([d], rng)
                unit_names = [f"s{s}" for s in SR]
            else:
                A = {a: {rot: ft[(model, a, rot, "ft")] for rot in ROTS} for a in FT_ARMS}
                units = {a: [float(np.mean([A[a][rot][s] for s in seeds3(i)])) for i, rot in enumerate(ROTS)]
                         for a in FT_ARMS}
                d = [x - y for x, y in zip(units["lp"], units["lp_randinit"], strict=True)]
                boot = cluster_ci([[A["lp"][rot][s] - A["lp_randinit"][rot][s] for s in seeds3(i)]
                                   for i, rot in enumerate(ROTS)], rng)
                unit_names = list(ROTS)
            v, s = ft_verdict(d)
            lo, hi = tci(d)
            npos = int((np.asarray(d) > 0).sum())
            # leave one unit out, paired() needs same sign in 3 of 4 (the D27-E reading), descriptive
            loo = [SHORT[paired(np.delete(d, i))] for i in range(len(d))]
            verdict_rows.append(f"| {setting} | {model} | {pm(units['lp'])} | {pm(units['lp_randinit'])} | "
                                f"**{np.mean(d):+.2f}** | {', '.join(f'{x:+.1f}' for x in d)} | {npos}/5 | "
                                f"[{boot[1]:+.1f}, {boot[2]:+.1f}] | [{lo:+.1f}, {hi:+.1f}] | **{v}** ({s}) | "
                                f"{', '.join(loo)} |")
            for a in FT_ARMS:
                runs = list(A[a].values()) if paper else [x for rot in ROTS for x in A[a][rot].values()]
                arm_rows.append(f"| {setting} | {model} | ft({a}) | "
                                + " | ".join(f"{x:.1f}" for x in units[a])
                                + f" | **{pm(units[a])}** | {pm(runs)} |")
            # descriptive: frozen probes (D24-A linear / D24-B linear + MLP) and SA next to ft
            heads = ("linear", "mlp_fullft") if paper else ("linear",)
            refrows = {}
            for head in heads:
                for arm in ("lp", "last", "lp_randinit", "last_randinit"):
                    if paper:
                        c = ref[(model, arm, "paper", head)]
                        assert set(c) == set(SR), (model, arm, head)
                        refrows[(head, arm)] = [c[s] for s in SR]
                    else:
                        cs = [ref[(model, arm, rot, head)] for rot in ROTS]
                        assert all(set(c) == set(seeds3(i)) for i, c in enumerate(cs)), (model, arm)
                        refrows[(head, arm)] = [float(np.mean([c[s] for s in seeds3(i)]))
                                                for i, c in enumerate(cs)]
            for (head, arm), u in refrows.items():
                ftu = units["lp_randinit" if arm.endswith("randinit") else "lp"]
                dd = [x - y for x, y in zip(ftu, u, strict=True)]
                ref_rows.append(f"| {setting} | {model} | {arm} ({head}) | {pm(u)} | "
                                f"ft({'lp_randinit' if arm.endswith('randinit') else 'lp'}) - {arm}: "
                                f"**{np.mean(dd):+.1f}** ({', '.join(f'{x:+.1f}' for x in dd)}; > 0 in "
                                f"{int((np.asarray(dd) > 0).sum())}/5) |")
            summary.append(f"- D, {setting}, {model}: ft(lp) {pm(units['lp'])} vs ft(lp_randinit) "
                           f"{pm(units['lp_randinit'])}, diff {np.mean(d):+.2f} ({npos}/5 > 0) -> **{v}** ({s})")
            js["D"][setting][model] = {"units": unit_names, "ft": units, "ft_runs": A, "diff": d, "verdict": v,
                                      "rule_output": s, "boot95": boot[1:], "t95": (lo, hi), "leave_one_out": loo,
                                      "references": {f"{a} ({h})": u for (h, a), u in refrows.items()}}
    md += ["### ft ROC per arm (units: rotations = 3-seed means; paper split = seeds)", "",
           "| setting | model | arm | unit 1 | unit 2 | unit 3 | unit 4 | unit 5 | mean ± SEM over units | "
           "mean ± SEM over runs (seeds not independent) |",
           "|---|---|---|---|---|---|---|---|---|---|"] + arm_rows
    md += ["",
           "Units: paper split seeds 42, 123, 2021, 3407, 8888; rotations rot0-rot4 (seeds S_r, 1000+r, 2000+r).",
           "", "### Pre-stated contrast: ft(lp) - ft(lp_randinit)", "",
           "| setting | model | ft(lp) | ft(lp_randinit) | mean diff | per unit | > 0 | cluster bootstrap 95% | "
           "t 95% | verdict (rule output) | without unit 1..5 (descriptive) |",
           "|---|---|---|---|---|---|---|---|---|---|---|"] + verdict_rows
    md += ["", "### Where LP and SA sit relative to ft (descriptive/post hoc)", "",
           "Frozen references: D24-A linear head (rotations; S1E+S1M, S3E+S3M) and D24-B linear and MLP heads "
           "(paper split; P1E); same seeds and eval data as ft, eval-mode probe. Pretrained arms (lp, "
           "last = SA) are "
           "compared with ft(lp), random-init arms with ft(lp_randinit); differences per unit.", "",
           "| setting | model | reference arm (head) | reference mean ± SEM | ft - reference |",
           "|---|---|---|---|---|"]
    md += ref_rows

    # ---- encoder trained? best epochs ----
    md += ["", "### ft records: was the encoder trained? best epochs", "",
           "Train loss of ft vs the logged linear probe of the same model / arm / split / seed (P1L, S1L, S3L: "
           "same head lr, batch, epochs, eval mode). An untrained encoder would give the linear curve.", "",
           "| setting | model | arm | n | epoch-0 train loss ft / linear (mean) | epoch-9 train loss ft / linear "
           "(mean) | ft ep9 < linear ep9 | min over epochs of abs(ft - linear) | ROC ft - linear (mean) | "
           "best epoch (0-based) counts | best = last epoch |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for setting, (_ds, tag, _r, _l, _g) in FT_SETS.items():
        loss, be = info[tag]["loss"], info[tag]["best_epoch"]
        for model in MODELS:
            for arm in FT_ARMS:
                x = [r for r in loss if r["model"] == model and r["arm"] == arm]
                cnt = {int(k.split("/")[2]): n for k, n in be.items() if k.startswith(f"{model}/{arm}/")}
                md.append(f"| {setting} | {model} | {arm} | {len(x)} | {np.mean([r['ft0'] for r in x]):.4f} / "
                          f"{np.mean([r['lin0'] for r in x]):.4f} | {np.mean([r['ft9'] for r in x]):.4f} / "
                          f"{np.mean([r['lin9'] for r in x]):.4f} | "
                          f"{sum(r['ft9'] < r['lin9'] for r in x)}/{len(x)} | "
                          f"{min(r['min_absdiff'] for r in x):.2e} | "
                          f"{np.mean([r['roc_ft'] - r['roc_lin'] for r in x]):+.1f} | "
                          f"{dict(sorted(cnt.items()))} | {cnt.get(9, 0)}/{len(x)} |")

    # ---- published CHB-MIT numbers ----
    p1 = {}
    for model in MODELS:
        for a in FT_ARMS:
            rs = sorted((r for r in raw["P1FT"] if r["model"] == model and r["arm"] == a), key=lambda r: r["seed"])
            p1[(model, a)] = {k: [r["probes"]["ft"]["test_at_best"][k] for r in rs]
                              for k in ("bal_acc", "avg_precision", "pr_auc_trapz", "roc_auc")}
    js["D"]["paper_split_metrics"] = {f"{m}/{a}": v for (m, a), v in p1.items()}

    def sd(v) -> str:
        v = np.asarray(v)
        return f"{v.mean():.4f} ± {v.std(ddof=1):.4f}"

    md += ["", "### Published CHB-MIT fine-tuning numbers (descriptive; different recipes)", "",
           "BIOT: Yang, Westover, Sun, arXiv 2305.10351v1 (10 May 2023), **Table 2** \"EEG "
           "classification tasks\", "
           "column group \"CHB-MIT (seizure detection)\", columns Balanced Acc. / AUC-PR / AUROC (mean ± "
           "std over 5 "
           "random seeds; the paper reports the average of two settings, val/test swapped). CBraMod: Wang et al., "
           "ICLR 2025 (text of arXiv 2412.07236v6, \"Published as a conference paper at ICLR 2025\"; the "
           "OpenReview "
           "PDF NPNUHgHF2w was behind a browser check), **Table 8** \"The results of different methods on seizure "
           "detection (CHB-MIT, 2-class)\", columns Balanced Accuracy / AUC-PR / AUROC (mean ± std, 5 seeds).", "",
           "| source | row | Balanced Acc. | AUC-PR | AUROC |", "|---|---|---|---|---|"]
    for row, note, b, p, r in BIOT_PUB:
        md.append(f"| BIOT Table 2 | {row}{' (' + note + ')' if note else ''} | {b[0]:.4f} ± {b[1]:.4f} | "
                  f"{p[0]:.4f} ± {p[1]:.4f} | {r[0]:.4f} ± {r[1]:.4f} |")
    for row, b, p, r in CBRA_PUB:
        md.append(f"| CBraMod Table 8 | {row} | {b[0]:.4f} ± {b[1]:.4f} | {p[0]:.4f} ± {p[1]:.4f} | "
                  f"{r[0]:.4f} ± {r[1]:.4f} |")
    for (model, a), v in p1.items():
        md.append(f"| ours P1FT (paper split, 5 seeds, mean ± SD) | {model} ft({a}) | {sd(v['bal_acc'])} | "
                  f"AP {sd(v['avg_precision'])}; trapz {sd(v['pr_auc_trapz'])} | {sd(v['roc_auc'])} |")
    md += ["", "Recipe differences (ours: P1FT records and src/eegdrift/probe.py; theirs: paper text and the MIT "
           "code clones in ../_upstream/BIOT and ../_upstream/CBraMod, read only):", "",
           "| | ours (ft) | BIOT paper / code | CBraMod paper / code |", "|---|---|---|---|",
           "| split | process2.py split: test chb23, chb24; val chb21, chb22; one setting | text: train 1-19, val "
           "20-21, test 22-23, then val/test swapped, average of the two; code process2.py: test chb23-24, val "
           "chb21-22 | text: train 1-19, val 20-21, test 22-23; code process2.py: test chb23-24, val chb21-22 |",
           "| windows / labels | upstream: 10 s grid + seizure windows re-cut at 5 s stride in every split "
           "(incl. test); start/end-in-window label | same pipeline (Appendix A.1: \"5 seconds as "
           "overlaps to split "
           "the seizure regions\"; ~0.6% positives in train) | \"consistent with BIOT\", 326,993 samples |",
           "| epochs / selection | 10, best val ROC | max 100 (Lightning), monitor val AUROC; code: EarlyStopping "
           "patience 5 | 50, val AUROC |",
           "| optimizer / lr | AdamW, head 4e-4, encoder 4e-5, wd 0.05, cosine to 1e-5, no clip | Adam lr 1e-3, "
           "L2 1e-5, no scheduler (code) | AdamW, backbone 1e-4, head 1e-3 x sqrt(64/256) = 5e-4 (multi_lr), wd "
           "5e-2, cosine to 1e-6, clip 1 |",
           "| batch | 256 | not stated for CHB-MIT; code default 512 (README TUAB runs 512) | 64 |",
           "| loss / sampling | BCE, shuffled, no class weighting or sampler | text: focal loss; code: BCE (focal "
           "commented out), shuffle, no sampler; supervised() in run_binary_supervised.py implements TUAB only | "
           "BCE, shuffle, no sampler |",
           "| head / dropout | one Linear on the encoder output; dropout OFF (eval mode) while training | BIOT "
           "classifier (ELU + Linear), train mode | 3-layer MLP on the flattened 16x10x200 output "
           "(`all_patch_reps`, "
           "dropout 0.1), proj_out = Identity, train mode |",
           "| checkpoint | EEG-SHHS+PREST-18-channels | PREST / PREST+SHHS / 6 datasets rows | CBraMod "
           "pretrained_weights.pth |",
           "| metrics | AP (= pyhealth pr_auc) and trapezoid PR; bal acc at logit 0 | pyhealth: pr_auc = average "
           "precision; bal acc at a val-derived threshold (top-k positives) | trapezoid PR-AUC (auc(recall, "
           "precision)); bal acc at 0.5 |", ""]
    md += ["## Commands", "", "```", ".venv/bin/python scripts/analysis/d27_cd.py",
           "# inputs: artifacts/s3-results (already synced); jobs notes/jobs-d27.txt (tags cb3/cbf, fz*, "
           "fn1/fn3); "
           "specs scripts/submit_d25.sh (want D27, items C and D)",
           ".venv/bin/python -m pytest -q && .venv/bin/python -m ruff check src tests scripts "
           "sm_entry.py", "```", ""]
    OUT.mkdir(parents=True, exist_ok=True)
    at = md.index("## Record checks")
    md[at:at] = ["## Verdicts (rule outputs; numbers and checks below)", ""] + summary + [""]
    (OUT / "README.md").write_text("\n".join(md) + "\n")
    (OUT / "d27cd.json").write_text(json.dumps(js, indent=1, default=str))
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
