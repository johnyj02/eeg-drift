#!/usr/bin/env python3
"""D25-E27: `last_noise` control (notes/completeness-audit.md E27; rule = D19 on last - last_noise).

    .venv/bin/python scripts/analysis/e27_last_noise.py

Records: S1N (BIOT, CHB-MIT), S3N / S3FN (both models, Siena / Siena filtered), paired with the
D24-A last and lp records of the same rotations and seeds (S1E+S1M, S3E+S3M, S3FE+S3FM).
Reading (pre-registered): per rotation, mean over its 3 D24 seeds; D19 on last - last_noise:
"the gain needs EEG data" if it wins by the D18 paired rule, "perturbation alone explains it" if
|mean| <= 3, else "unclear". Descriptive only: last - lp (re-reads D24-A, a pairing check),
last_noise - lp, the D24-D cluster bootstrap CI, SSL loss and LAST-block displacement.
Reads ROC only through scripts/read_d24.load. Writes artifacts/analysis/E27/ (e27.md, e27.json).
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from bootstrap_d24 import cluster_ci  # noqa: E402
from read_d24 import ROTS, load  # noqa: E402
from read_step1 import d19, paired  # noqa: E402

RES = ROOT / "artifacts" / "s3-results"
OUT = ROOT / "artifacts" / "analysis" / "E27"
S_R = (42, 123, 2021, 3407, 8888)
SEEDS = {r: {S_R[i], 1000 + i, 2000 + i} for i, r in enumerate(ROTS)}
ARMS = ("lp", "last", "last_noise")
# keys added after D24 (probe-tap / E19 code, same versions adapt 3 / probe 4); D24 records lack them
DEFAULTS = {"input_norm": "", "tap": "encoder"}
# (label, dataset, D24 tags, noise tag, models)
SETTINGS = (("CHB-MIT", "chbmit", ("S1E", "S1M"), "S1N", ("biot",)),
            ("Siena", "siena", ("S3E", "S3M"), "S3N", ("biot", "cbramod")),
            ("Siena filtered", "siena", ("S3FE", "S3FM"), "S3FN", ("biot", "cbramod")))


def _hash(*parts) -> str:   # copy of eegdrift.study._hash (noise data_hash = _hash(ssl.hash, "noise"))
    import hashlib
    return hashlib.sha256(json.dumps(parts, sort_keys=True, default=str).encode()).hexdigest()[:16]


def scan(tags: set[str]) -> list[tuple[Path, dict]]:
    out = []
    for p in RES.rglob("results/*.json"):
        if p.name.startswith(("diag-", "test-index-", "val-index-", "report-")):
            continue
        r = json.loads(p.read_text())
        if not r.get("smoke") and r.get("run_tag") in tags:
            out.append((p, r))
    return out


def load_via_links(recs: list[tuple[Path, dict]], dataset: str, tags: set[str], tmp: Path) -> dict:
    """read_d24.load on a symlink mirror: it crashes on the val-index-*.json lists E25 added to results/."""
    d = tmp / dataset / "_".join(sorted(tags))
    for p, _ in recs:
        link = d / p.parent.parent.name / "results" / p.name
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(p.resolve())
    return load(str(d), dataset, tags)


def check(recs: list[dict], models: tuple[str, ...], noise_tag: str) -> list[str]:
    """Completeness and pairing checks; returns a list of gaps (empty = all good)."""
    gaps = []
    by = defaultdict(list)
    for r in recs:
        if r["arm"] in ARMS and r["model"] in models:
            by[(r["model"], r["split"])].append(r)
    for m in models:
        for rot in ROTS:
            rs = by[(m, rot)]
            for arm in ARMS:
                seeds = sorted(r["seed"] for r in rs if r["arm"] == arm)
                if sorted(SEEDS[rot]) != seeds:
                    gaps.append(f"{m}/{rot}/{arm}: seeds {seeds}, expected {sorted(SEEDS[rot])}")
            noise_tags = {r["run_tag"] for r in rs if r["arm"] == "last_noise"}
            if noise_tags != {noise_tag}:
                gaps.append(f"{m}/{rot}: last_noise run tags {noise_tags}")
            for name, f in (("eval_hash", lambda r: r["eval_hash"]), ("labels", lambda r: r["labels"]),
                            ("versions", lambda r: json.dumps(r["versions"], sort_keys=True)),
                            ("test n/prevalence", lambda r: (r["probes"]["linear"]["test_at_best"]["n"],
                                                             r["probes"]["linear"]["test_at_best"]["prevalence"])),
                            ("probe spec minus seed", lambda r: json.dumps(
                                {**DEFAULTS, **{k: v for k, v in r["probes"]["linear"]["spec"].items()
                                                if k != "seed"}}, sort_keys=True))):
                vals = {f(r) for r in rs}
                if len(vals) != 1:
                    gaps.append(f"{m}/{rot}: {name} differs across arms: {vals}")
            ad = [r for r in rs if r["arm"] in ("last", "last_noise")]
            keep = {"model", "dataset", "groups", "init", "protocol", "batch", "epochs", "n_windows", "n_total",
                    "lr", "weight_decay", "betas", "eta_min", "clip", "scale", "mask_ratio", "ckpt_sha256",
                    "include_fixed", "input_norm", "code_version"}
            specs = {json.dumps({k: r["adapt_spec"].get(k, DEFAULTS.get(k)) for k in keep}, sort_keys=True)
                     for r in ad}
            if len(specs) != 1:
                gaps.append(f"{m}/{rot}: last vs last_noise adapt_spec differs beyond arm/seed/data_hash")
            eeg = {r["adapt_spec"]["data_hash"] for r in ad if r["arm"] == "last"}
            noi = {r["adapt_spec"]["data_hash"] for r in ad if r["arm"] == "last_noise"}
            if len(eeg) != 1 or noi != {_hash(h, "noise") for h in eeg}:
                gaps.append(f"{m}/{rot}: noise SSL sample not derived from last's sample ({eeg} -> {noi})")
            if any(r["arm_spec"].get("ssl_input") != "noise" for r in ad if r["arm"] == "last_noise"):
                gaps.append(f"{m}/{rot}: a last_noise record without ssl_input noise")
    return gaps


def descr(recs: list[dict], model: str) -> dict:
    """Mean final-epoch SSL loss and LAST-block relative displacement, last vs last_noise (descriptive)."""
    out = {}
    for arm in ("last", "last_noise"):
        rs = [r for r in recs if r["model"] == model and r["arm"] == arm]
        last_block = rs[0]["adapt_spec"]["groups"][0]
        out[arm] = {"ssl_loss_final": float(np.mean([r["adapt"]["epoch_losses"][-1] for r in rs])),
                    "ssl_loss_first": float(np.mean([r["adapt"]["epoch_losses"][0] for r in rs])),
                    f"rel_disp_{last_block}": float(np.mean([r["displacement"][last_block]["rel"] for r in rs])),
                    "n": len(rs)}
    return out


def main() -> int:
    rng = np.random.default_rng(20261101)
    rows, js, all_gaps = [], [], []
    lines = ["# D25-E27: last_noise control, ROC-AUC x100 (linear head, eval-mode probe, encoder tap)", "",
             "Per-rotation values are means over the 3 D24 seeds [S_r, 1000+r, 2000+r]. Rule (pre-registered, "
             "D19 on last - last_noise): wins by the D18 paired rule -> \"the gain needs EEG data\"; "
             "|mean| <= 3 -> \"perturbation alone explains it\"; else \"unclear\". Everything else is "
             "descriptive.",
             ""]
    every = scan({t for s in SETTINGS for t in (*s[2], s[3])})
    tmp = Path(tempfile.mkdtemp(prefix="e27-"))
    for label, dataset, d24_tags, ntag, models in SETTINGS:
        tags = set(d24_tags) | {ntag}
        sel = [(p, r) for p, r in every if r["dataset"] == dataset and r["run_tag"] in tags]
        recs = [r for _, r in sel]
        gaps = check(recs, models, ntag)
        all_gaps += [f"{label}: {g}" for g in gaps]
        roc = load_via_links(sel, dataset, tags, tmp)   # raises if eval data/labels/adapt code mix in a rotation
        for m in models:
            per = {a: [float(np.mean([roc[(m, a, r, "linear")][s] for s in sorted(SEEDS[r])])) for r in ROTS]
                   for a in ARMS}
            res = {"setting": label, "model": m, "tags": sorted(tags), "per_rotation": per,
                   "arm_means": {a: float(np.mean(v)) for a, v in per.items()}}
            for a, b, rule, primary in (("last", "last_noise", d19, True), ("last", "lp", paired, False),
                                        ("last_noise", "lp", paired, False)):
                d = [x - y for x, y in zip(per[a], per[b], strict=True)]
                diffs = [[roc[(m, a, r, "linear")][s] - roc[(m, b, r, "linear")][s] for s in sorted(SEEDS[r])]
                         for r in ROTS]
                _, lo, hi = cluster_ci(diffs, rng)
                out = rule(d)
                res[f"{a} - {b}"] = {"mean": float(np.mean(d)), "per_rotation": d, "rule": out,
                                     "n_pos": int(sum(x > 0 for x in d)), "boot95": [lo, hi], "primary": primary}
                rows.append((label, m, f"{a} - {b}", np.mean(d), d, out if primary else f"({out}; descriptive)",
                             lo, hi))
            res["adapt_descriptive"] = descr(recs, m)
            js.append(res)
    shutil.rmtree(tmp)
    lines += ["## Verdict table", "",
              "| setting | model | contrast | mean | per rotation (rot0..rot4) | rule output "
              "| bootstrap 95% CI (descr.) |",
              "|---|---|---|---|---|---|---|"]
    for label, m, c, mean, d, out, lo, hi in rows:
        lines.append(f"| {label} | {m} | {c} | {mean:+.1f} | {', '.join(f'{x:+.1f}' for x in d)} | {out} | "
                     f"[{lo:+.1f}, {hi:+.1f}] |")
    lines += ["", "## Arm means over rotations (descriptive)", "",
              "| setting | model | lp | last | last_noise |", "|---|---|---|---|---|"]
    for r in js:
        a = r["arm_means"]
        lines.append(f"| {r['setting']} | {r['model']} | {a['lp']:.1f} | {a['last']:.1f} | "
                     f"{a['last_noise']:.1f} |")
    lines += ["", "## SSL adaptation, last vs last_noise (descriptive, mean over 15 runs)", "",
              "| setting | model | arm | SSL loss epoch 1 | SSL loss epoch 3 | rel. displacement of LAST block |",
              "|---|---|---|---|---|---|"]
    for r in js:
        for arm, v in r["adapt_descriptive"].items():
            disp = next(x for k, x in v.items() if k.startswith("rel_disp_"))
            lines.append(f"| {r['setting']} | {r['model']} | {arm} | {v['ssl_loss_first']:.4f} | "
                         f"{v['ssl_loss_final']:.4f} | {disp:.4f} |")
    lines += ["", "## Checks", "",
              "Per setting and model: lp, last, last_noise each have exactly the 3 D24 seeds in every rotation; "
              "within a rotation all arms share eval_hash, labels, code versions, test n/prevalence and the probe "
              "spec (except seed); last and last_noise share the adapt spec (except arm, seed, data_hash) and the "
              "noise data_hash equals _hash(last data_hash, 'noise') (same SSL sample). D24 records lack the "
              f"later spec keys {sorted(DEFAULTS)}; compared at their defaults {DEFAULTS}.",
              "", "GAPS: " + ("; ".join(all_gaps) if all_gaps else "none")]
    OUT.mkdir(parents=True, exist_ok=True)
    text = "\n".join(lines) + "\n"
    (OUT / "e27.md").write_text(text)
    (OUT / "e27.json").write_text(json.dumps({"gaps": all_gaps, "results": js}, indent=1))
    print(text)
    return 1 if all_gaps else 0


if __name__ == "__main__":
    raise SystemExit(main())
