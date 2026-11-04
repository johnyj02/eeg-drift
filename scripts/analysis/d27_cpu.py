#!/usr/bin/env python3
"""D27 item E (CPU part) and the TOST part of D27 item A (notes/decisions.md D27). Post hoc, descriptive.

    .venv/bin/python scripts/analysis/d27_cpu.py

1. Leave-one-rotation-out (LORO) for every primary verdict (3 contrasts + D17, both models): D24-A
   (S1E+S1M, S3E+S3M, S3FE+S3FM, linear), E32 (S1R, S3R, linear), E26 / D27-B (S1Z, S3Z, S3FZ,
   linear_z: S_r only until every cell has the 3 D24 seeds, then 3-seed means) and D26 (S1RZ, S3RZ).
   Before any row is written, the 5-rotation lines are re-derived and asserted equal to the published
   artifacts/tables/d24-*.md (and E32's e32.json, E10's leave-one-out strings for D24-A).
2. TOST (margin 3, alpha 0.05, t over the 5 rotation means or 5 paper-split seeds, df 4) on last -
   last_noise for E27 (S1N, S3N, S3FN with the D24 seeds) and the D27-A tags P1QN, S3FQN, S1RN/S3RN
   (paired with S1R/S3R linear and S1RZ/S3RZ linear_z), A6 S3NM/S3FNM (paired with S3L/S3FL
   mlp_fullft and S3Z/S3FZ linear_z). 1 seed, descriptive (TOST p shown, not read): A4 S1LRN<i>,
   A5 S3LRN<i> and A7 S3DN11/S3DN12 (last from E28 S3D11/S3D12). The D19 three-way verdict is shown
   next to it, with last - lp and last_noise - lp (descriptive; lp from the same tags, or from
   S1E/S1M/S1Z, S3M/S3Z at S_r). Checks: every last / last_noise / lp triple is one record each with
   the same eval data, labels, versions, test index, probe spec (eval mode, encoder tap) and adapt
   spec, and the noise SSL sample is derived from last's; lp pairings equal E25 / E28 / E29 (asserted);
   P1QN and S3FQN lp/last equal P1Q and S3FQ, and S1LRN<i>/S3LRN<i> last linear equals E29 (reported).
3. Step-0 SSL loss (adapt.step_losses[0], the first batch before any update) and epoch-1 mean loss,
   pretrained vs random init, from the logged records S1L, S3L, S3FL, P1L.
Rerunnable: inputs not yet in artifacts/s3-results are skipped with a printed note. ROC is read only
through scripts/read_d24.load. Writes artifacts/analysis/D27/cpu.md, cpu.json and noise.md.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from e27_last_noise import DEFAULTS, _hash, scan  # noqa: E402
from read_d24 import CONTRASTS, ROTS, load  # noqa: E402
from read_step1 import d17, d19, paired  # noqa: E402
from stats_d25 import tost_p  # noqa: E402

LOCAL = ROOT / "artifacts" / "s3-results"
OUT = ROOT / "artifacts" / "analysis" / "D27"
MODELS = ("biot", "cbramod")
S_R = (42, 123, 2021, 3407, 8888)
SEEDS3 = {r: (S_R[i], 1000 + i, 2000 + i) for i, r in enumerate(ROTS)}
SEEDS1 = {r: (S_R[i],) for i, r in enumerate(ROTS)}
VERDICTS = (*CONTRASTS, ("last_randinit", "lp_randinit", "D17"))
SHORT = {"first term wins": "1st wins", "second term wins": "2nd wins", "no difference shown": "none",
         "random features explain it": "explains", "SSL adds to random init": "SSL adds",
         "neither rule met": "neither"}
# (item, setting, dataset, tags, head, 1-seed S_r reading allowed while D27-B is incomplete)
LORO_SETS = (("D24-A", "CHB-MIT", "chbmit", "S1E,S1M", "linear", False),
             ("D24-A", "Siena", "siena", "S3E,S3M", "linear", False),
             ("D24-A", "Siena filtered", "siena", "S3FE,S3FM", "linear", False),
             ("E32", "CHB-MIT", "chbmit", "S1R", "linear", False),
             ("E32", "Siena", "siena", "S3R", "linear", False),
             ("E26/D27-B", "CHB-MIT", "chbmit", "S1Z", "linear_z", True),
             ("E26/D27-B", "Siena", "siena", "S3Z", "linear_z", True),
             ("E26/D27-B", "Siena filtered", "siena", "S3FZ", "linear_z", True),
             ("D26", "CHB-MIT", "chbmit", "S1RZ", "linear_z", False),
             ("D26", "Siena", "siena", "S3RZ", "linear_z", False))
# (item, setting, dataset, tags holding last and last_noise (noise tag last), heads, seeds per unit or
#  None = paper split, registered (False = 1 seed: descriptive), tags holding lp if not the first tags)
TOST_SETS = (("E27", "CHB-MIT", "chbmit", "S1E,S1M,S1N", ("linear",), SEEDS3, True, None),
             ("E27", "Siena", "siena", "S3E,S3M,S3N", ("linear",), SEEDS3, True, None),
             ("E27", "Siena filtered", "siena", "S3FE,S3FM,S3FN", ("linear",), SEEDS3, True, None),
             ("A1", "CHB-MIT paper split, q95", "chbmit", "P1QN", ("linear", "mlp_fullft", "linear_z"), None,
              True, None),
             ("A2", "Siena filtered, q95", "siena", "S3FQN", ("linear", "linear_z"), SEEDS3, True, None),
             ("A3", "CHB-MIT, E32 partition", "chbmit", "S1R,S1RN", ("linear",), SEEDS3, True, None),
             ("A3", "CHB-MIT, E32 partition", "chbmit", "S1RZ,S1RN", ("linear_z",), SEEDS3, True, None),
             ("A3", "Siena, E32 partition", "siena", "S3R,S3RN", ("linear",), SEEDS3, True, None),
             ("A3", "Siena, E32 partition", "siena", "S3RZ,S3RN", ("linear_z",), SEEDS3, True, None),
             *(("A4", f"CHB-MIT, E29 cell S1LR{i}", "chbmit", f"S1LRN{i}", ("linear", "linear_z"), SEEDS1, False,
                "S1E,S1M,S1Z") for i in (1, 3, 4, 5)),
             *(("A5", f"Siena, E29 cell S3LR{i}", "siena", f"S3LRN{i}", ("linear", "linear_z"), SEEDS1, False,
                "S3M,S3Z") for i in range(1, 6)),
             ("A6", "Siena", "siena", "S3L,S3NM", ("mlp_fullft",), SEEDS3, True, None),
             ("A6", "Siena", "siena", "S3Z,S3NM", ("linear_z",), SEEDS3, True, None),
             ("A6", "Siena filtered", "siena", "S3FL,S3FNM", ("mlp_fullft",), SEEDS3, True, None),
             ("A6", "Siena filtered", "siena", "S3FZ,S3FNM", ("linear_z",), SEEDS3, True, None),
             *(("A7", f"Siena, ssl_seed {k}", "siena", f"S3D{k},S3DN{k}", ("linear",), SEEDS1, False, "S3M")
               for k in (11, 12)))
# D27 bit-reproducibility: (new tag, earlier tag, dataset, arms, heads) must give identical ROC
REPRO = (("P1QN", "P1Q", "chbmit", ("lp", "last"), ("linear", "mlp_fullft")),
         ("S3FQN", "S3FQ", "siena", ("lp", "last"), ("linear",)))
# adapt_spec fields last and last_noise must share (as e27_last_noise.check)
KEEP = {"model", "dataset", "groups", "init", "protocol", "batch", "epochs", "n_windows", "n_total", "lr",
        "weight_decay", "betas", "eta_min", "clip", "scale", "mask_ratio", "ckpt_sha256", "include_fixed",
        "input_norm", "code_version"}
STEP0_SETS = (("CHB-MIT rotations", "S1L"), ("Siena", "S3L"), ("Siena filtered", "S3FL"),
              ("CHB-MIT paper split", "P1L"))


def note(notes: list[str], msg: str) -> None:
    print(f"NOTE: {msg}")
    notes.append(msg)


def get(dataset: str, tags: str, notes: list[str]) -> dict:
    try:
        return load(str(LOCAL), dataset, set(tags.split(",")))
    except SystemExit as e:   # read_d24.load's guards (non-v4/eval record, duplicates, mixed eval data)
        note(notes, f"{dataset} {tags}: read_d24.load refused the records ({e}); skipped")
        return {}


def rot_means(roc: dict, model: str, arm: str, probe: str, seeds: dict) -> list[float] | None:
    cells = [roc.get((model, arm, r, probe), {}) for r in ROTS]
    if not all(all(s in c for s in seeds[r]) for c, r in zip(cells, ROTS, strict=True)):
        return None
    return [float(np.mean([c[s] for s in seeds[r]])) for c, r in zip(cells, ROTS, strict=True)]


def verdict(a: str, b: str, A, B) -> str:
    A, B = np.asarray(A), np.asarray(B)
    return d17(A, B) if (a, b) == ("last_randinit", "lp_randinit") else paired(list(A - B))


# ---------- 1. LORO ----------


def loro(notes: list[str]) -> list[dict]:
    rows = []
    arms = ("lp", "lp_randinit", "last", "last_randinit")
    for item, setting, dataset, tags, probe, allow1 in LORO_SETS:
        roc = get(dataset, tags, notes)
        if not roc:
            note(notes, f"LORO {item} {setting} ({tags}): no records yet, skipped")
            continue
        seeds = SEEDS3
        if allow1:
            done = sum(rot_means(roc, m, a, probe, SEEDS3) is not None for m in MODELS for a in arms)
            if done < len(MODELS) * len(arms):
                seeds = SEEDS1
                note(notes, f"LORO {item} {setting} ({tags}): {done} of {len(MODELS) * len(arms)} model x arm "
                     "cells have the 3 D24 seeds in every rotation; reading S_r only (E26)")
        for model in MODELS:
            per = {a: rot_means(roc, model, a, probe, seeds) for a in arms}
            if any(v is None for v in per.values()):
                note(notes, f"LORO {item} {setting} ({tags}) {model}: incomplete arms "
                     f"{[a for a, v in per.items() if v is None]}, skipped")
                continue
            for a, b, name in VERDICTS:
                A, B = np.array(per[a]), np.array(per[b])
                d = A - B
                full = verdict(a, b, A, B)
                drop = []
                for i, r in enumerate(ROTS):
                    v = verdict(a, b, np.delete(A, i), np.delete(B, i))
                    drop.append(dict(rot=r, mean=float(np.delete(d, i).mean()), verdict=v, changed=v != full))
                rows.append(dict(item=item, setting=setting, dataset=dataset, tags=tags, model=model, probe=probe,
                                 seeds_per_rot=len(seeds["rot0"]), a=a, b=b, name=name,
                                 per_rot=[float(x) for x in d], mean=float(d.mean()), verdict=full, drop=drop,
                                 n_changed=sum(x["changed"] for x in drop)))
    return rows


def check_published(rows: list[dict]) -> list[str]:
    """Assert the 5-rotation lines equal the published tables; returns what was checked."""
    done = []
    by_set = defaultdict(list)
    for r in rows:
        by_set[(r["item"], r["setting"], r["dataset"], r["tags"], r["probe"], r["seeds_per_rot"])].append(r)
    d24a = [k for k in by_set if k[0] == "D24-A"]
    assert len(d24a) == 3 and all(len(by_set[k]) == 8 for k in d24a), "D24-A rows incomplete"
    for (item, setting, dataset, tags, probe, k), rs in by_set.items():
        path = ROOT / "artifacts" / "tables" / f"d24-{dataset}-{tags.replace(',', '+')}.md"
        if item == "D26" or (item == "E26/D27-B" and k == 3):   # 3-seed tables (read_d24.py --out), if written
            path = ROOT / "artifacts" / "analysis" / ("D26" if item == "D26" else "D27B") / f"{tags}.md"
        # E26 tables in artifacts/tables are the S_r-only reading
        if item == "D24-A" or (item in ("E26/D27-B", "D26") and path.exists()):
            sections = {s.split("\n", 1)[0]: s for s in path.read_text().split("## ")[1:]}
            for r in rs:
                want = (f"- D17: **{r['verdict']}**" if r["name"] == "D17" else
                        f"- {r['name']}: mean {r['mean']:+.1f}, per rotation "
                        f"{', '.join(f'{x:+.1f}' for x in r['per_rot'])} -> **{r['verdict']}**")
                assert want in sections[f"{r['model']}, {probe} head"], (path.name, r["model"], want)
            done.append(f"{path.relative_to(ROOT)}: {len(rs)} verdict lines (means, per-rotation values, verdict)")
        if item == "E32":
            e32 = json.loads((ROOT / "artifacts" / "analysis" / "E32" / "e32.json").read_text())
            for r in rs:
                c = e32[f"{setting}|{r['model']}"]["new"]["contrasts"]["D17" if r["name"] == "D17" else
                                                                      f"{r['a']} - {r['b']}"]
                assert c["verdict"] == r["verdict"] and abs(c["mean"] - r["mean"]) < 1e-9, (tags, r["name"])
            done.append(f"artifacts/analysis/E32/e32.json {tags}: {len(rs)} verdicts and means")
    sym = {"first term wins": "+", "second term wins": "-", "no difference shown": ".",
           "random features explain it": "E", "SSL adds to random init": "+", "neither rule met": "-."}
    e10 = {(r["setting"], r["model"], r["a"], r["b"]): r["loo"] for r in
           json.loads((ROOT / "artifacts" / "analysis" / "stats" / "stats.json").read_text())["e10"]
           if not r["paper"]}
    n = 0
    for r in rows:
        if r["item"] == "D24-A":
            loo = e10[(r["setting"], r["model"], r["a"], r["b"])]
            assert all(c in sym[x["verdict"]] for c, x in zip(loo, r["drop"], strict=True)), (r["setting"], loo)
            n += 1
    done.append(f"artifacts/analysis/stats/stats.json E10(e) leave-one-out strings: {n} D24-A verdicts agree")
    return done


# ---------- 2. TOST on last - last_noise ----------


def per_unit(roc: dict, model: str, arm: str, probe: str, seeds: dict | None) -> list[float] | None:
    """The 5 units: rotation means over `seeds`, or the 5 paper-split seeds (seeds None, D24-B)."""
    if seeds is None:
        c = roc.get((model, arm, "paper", probe), {})
        return [c[s] for s in S_R] if all(s in c for s in S_R) else None
    return rot_means(roc, model, arm, probe, seeds)


def diff(A, B) -> list[float] | None:
    return None if A is None or B is None else [float(x - y) for x, y in zip(A, B, strict=True)]


def tost(notes: list[str]) -> list[dict]:
    rows, T = [], stats.t(4)
    for item, setting, dataset, tags, probes, seeds, registered, lp_tags in TOST_SETS:
        roc = get(dataset, tags, notes)
        if not any(k[1] == "last_noise" for k in roc):
            note(notes, f"TOST {item} {setting} ({tags}, {'/'.join(probes)}): no last_noise records under "
                 f"{tags.split(',')[-1]} yet, skipped")
            continue
        lp_roc = get(dataset, lp_tags, notes) if lp_tags else roc
        for model in MODELS:
            for probe in probes:
                L, N, P = (per_unit(r, model, a, probe, seeds) for r, a in
                           ((roc, "last"), (roc, "last_noise"), (lp_roc, "lp")))
                d = diff(L, N)
                if d is None:
                    if any(k[:2] == (model, "last_noise") and k[3] == probe for k in roc):
                        note(notes, f"TOST {item} {setting} {model} {probe}: last or last_noise incomplete, "
                             "skipped")
                    continue
                if P is None:
                    note(notes, f"TOST {item} {setting} {model} {probe}: no lp under {lp_tags or tags}; "
                         "last - lp not shown")
                x = np.asarray(d)
                m, se = float(x.mean()), float(x.std(ddof=1) / np.sqrt(len(x)))
                q = T.ppf(0.95) * se
                p = tost_p(m, se, 3, T)
                rows.append(dict(item=item, setting=setting, tags=tags, lp_tags=lp_tags or tags, model=model,
                                 probe=probe, unit="seed" if seeds is None else "rotation",
                                 n_seeds=None if seeds is None else len(seeds["rot0"]), registered=registered,
                                 per_unit=d, mean=m, sd=float(x.std(ddof=1)), ci90=(m - q, m + q), tost_p=p,
                                 equivalent=p < 0.05 if registered else None, d19=d19(d),
                                 last=L, last_noise=N, lp=P, last_lp=diff(L, P), noise_lp=diff(N, P)))
    check_lp(rows)
    return rows


def check_lp(rows: list[dict]) -> None:
    """Assert the pairings equal the published readings that used the same records."""
    A = ROOT / "artifacts" / "analysis"
    e27 = json.loads((A / "E27" / "e27.json").read_text())["results"]
    e29 = json.loads((A / "E29" / "e29.json").read_text())["rows"]
    e28 = json.loads((A / "E28" / "e28.json").read_text())["rotations"]
    e25 = {(v["tag"], v["model"]): v for v in json.loads((A / "E25" / "e25_verdicts.json").read_text())
           if v["contrast"] == "last - lp"}

    def same(a, b):
        return a is not None and b is not None and np.allclose(a, b, rtol=0, atol=1e-9)

    for r in rows:
        key = (r["item"], r["model"], r["probe"])
        if r["item"] == "E27":   # last - last_noise and last - lp of the published E27 reading
            e = next(e for e in e27 if (e["setting"], e["model"]) == (r["setting"], r["model"]))
            ref = e["last - last_noise"]
            assert ref["rule"] == r["d19"] and abs(ref["mean"] - r["mean"]) < 1e-9, key
            assert same(e["last - lp"]["per_rotation"], r["last_lp"]), key
        elif r["item"] in ("A4", "A5") and r["probe"] == "linear":   # the E29 lp at S_r
            cell = int(r["tags"][-1])
            e = next(e for e in e29 if (e["dataset"], e["model"], e["cell"]) ==
                     ("chbmit" if r["item"] == "A4" else "siena", r["model"], cell))
            assert same(e["lp"], r["lp"]), key
        elif r["item"] == "A6" and r["probe"] == "mlp_fullft":   # E25 MLP head, same S3L/S3FL records
            assert same(e25[(r["tags"].split(",")[0], r["model"])]["mlp_per_rot"], r["last_lp"]), key
        elif r["item"] == "A7":   # E28 last - lp at S_r, same S3D11/S3D12 last records
            assert same(e28[f"siena/{r['model']}"][r["tags"].split(",")[0]]["last - lp"][0], r["last_lp"]), key


def repro(notes: list[str]) -> list[dict]:
    """D27 design: lp/last under the new tags must reproduce the earlier runs exactly (reported, not asserted)."""
    out = []

    def add(check: str, pairs: list[tuple[float, float]], n_new: int) -> None:
        dd = [abs(a - b) for a, b in pairs]
        out.append(dict(check=check, n_records=n_new, n_paired=len(pairs), n_identical=sum(x == 0 for x in dd),
                        max_abs_diff=max(dd) if dd else None))

    for new, old, dataset, arms, probes in REPRO:
        a, b = get(dataset, new, notes), get(dataset, old, notes)
        cells = [k for k in a if k[1] in arms and k[3] in probes]
        add(f"{new} vs {old} ({'/'.join(arms)}; {'/'.join(probes)})",
            [(a[k][s], b[k][s]) for k in cells for s in a[k] if s in b.get(k, {})], sum(len(a[k]) for k in cells))
    e29 = json.loads((ROOT / "artifacts" / "analysis" / "E29" / "e29.json").read_text())["rows"]
    for dataset, pfx in (("chbmit", "S1"), ("siena", "S3")):
        for e in (e for e in e29 if e["dataset"] == dataset and e["model"] == "biot" and e["cell"]):
            roc = get(dataset, f"{pfx}LRN{e['cell']}", notes)
            if not roc:
                continue
            c = [roc.get(("biot", "last", r, "linear"), {}) for r in ROTS]
            add(f"{pfx}LRN{e['cell']} last linear vs E29 cell {e['cell']} (S_r)",
                [(x[S_R[i]], y) for i, (x, y) in enumerate(zip(c, e["last"], strict=True)) if S_R[i] in x],
                sum(len(x) for x in c))
    return out


def triple_gaps(L: dict, N: dict, P: dict, probe: str, split: str) -> list[str]:
    g = [f"{name} differs" for name, f in (
        ("eval_hash", lambda r: r["eval_hash"]), ("labels", lambda r: r["labels"]),
        ("versions", lambda r: json.dumps(r["versions"], sort_keys=True)),
        ("test_index", lambda r: r.get("test_index")),
        ("test n/prevalence", lambda r: (r["probes"][probe]["test_at_best"]["n"],
                                         r["probes"][probe]["test_at_best"]["prevalence"])),
        ("probe spec", lambda r: json.dumps({**DEFAULTS, **r["probes"][probe]["spec"]}, sort_keys=True)))
        if len({f(r) for r in (L, N, P)}) != 1]
    spec = {**DEFAULTS, **L["probes"][probe]["spec"]}
    if spec.get("backbone_mode") != "eval" or spec["tap"] != "encoder":
        g.append("not eval mode / encoder tap")
    if L["labels"] != ("upstream" if split == "paper" else "overlap"):
        g.append(f"labels {L['labels']}")
    if L["versions"] != {"adapt": 3, "probe": 4}:
        g.append(f"versions {L['versions']}")
    ka = [json.dumps({k: r["adapt_spec"].get(k, DEFAULTS.get(k)) for k in KEEP}, sort_keys=True) for r in (L, N)]
    if ka[0] != ka[1]:
        g.append("last vs last_noise adapt_spec differs")
    if N["adapt_spec"]["data_hash"] != _hash(L["adapt_spec"]["data_hash"], "noise"):
        g.append("noise SSL sample not derived from last's sample")
    if N["arm_spec"].get("ssl_input") != "noise" or L["arm_spec"].get("ssl_input", "eeg") != "eeg":
        g.append("ssl_input")
    return g


def provenance() -> list[dict]:
    """Per TOST set: record counts by tag and arm, and the checks above on every last / last_noise / lp triple."""
    out = []
    for item, setting, dataset, tags, probes, seeds, _, lp_tags in TOST_SETS:
        own = set(tags.split(","))
        lpt = set(lp_tags.split(",")) if lp_tags else own
        recs = [r for _, r in scan(own | lpt) if r["dataset"] == dataset]
        models = {r["model"] for r in recs if r["arm"] == "last_noise"}
        by, counts = defaultdict(list), defaultdict(int)
        for r in recs:
            if r["model"] in models and (r["arm"] in ("last", "last_noise") and r["run_tag"] in own
                                         or r["arm"] == "lp" and r["run_tag"] in lpt):
                counts[f"{r['run_tag']} {r['model']} {r['arm']}"] += 1
                for probe in set(probes) & set(r["probes"]):
                    by[(r["model"], r["split"], r["seed"], probe, r["arm"])].append(r)
        gaps, n, cfg = [], 0, set()
        for model, split in sorted({k[:2] for k in by if k[4] == "last_noise"}):
            for seed in S_R if seeds is None else seeds[split]:
                for probe in probes:
                    t = {a: by.get((model, split, seed, probe, a), []) for a in ("last", "last_noise", "lp")}
                    bad = {a: len(v) for a, v in t.items() if len(v) != 1}
                    if bad:
                        gaps.append(f"{model}/{split}/s{seed}/{probe}: record counts {bad}")
                        continue
                    n += 1
                    L, N, P = t["last"][0], t["last_noise"][0], t["lp"][0]
                    cfg.add((L["adapt_spec"]["lr"], L["adapt_spec"]["n_windows"] == L["adapt_spec"]["n_total"],
                             L["adapt_spec"]["epochs"], L["overrides"].get("ssl_seed", "")))
                    gaps += [f"{model}/{split}/s{seed}/{probe}: {x}" for x in triple_gaps(L, N, P, probe, split)]
        out.append(dict(item=item, setting=setting, tags=tags, lp_tags=lp_tags or tags, probes=list(probes),
                        n_triples=n, counts=dict(sorted(counts.items())), gaps=gaps,
                        ssl=sorted(f"lr {a:g}, {'whole pool' if b else 'N sample'}, {c} ep"
                                   + (f", ssl_seed {s}" if s else "") for a, b, c, s in cfg)))
    return out


# ---------- 3. Step-0 SSL loss ----------


def step0(notes: list[str]) -> list[dict]:
    recs = scan({t for _, t in STEP0_SETS})
    rows = []
    for setting, tag in STEP0_SETS:
        g = defaultdict(list)
        for _, r in recs:
            if r["run_tag"] == tag and r["arm_spec"]["adapt"]:
                if not r["adapt"].get("step_losses"):
                    note(notes, f"step-0 {tag}: {r['key']} has no step_losses, skipped")
                    continue
                g[(r["model"], r["arm"], r["adapt_spec"]["init"])].append(
                    (r["adapt"]["step_losses"][0], r["adapt"]["epoch_losses"][0]))
        if not g:
            note(notes, f"step-0 {tag}: no logged records, skipped")
        for (model, arm, init), v in sorted(g.items()):
            s0, e0 = np.array(v).T
            rows.append(dict(setting=setting, tag=tag, model=model, arm=arm, init=init, n=len(v),
                             step0=dict(mean=float(s0.mean()), min=float(s0.min()), max=float(s0.max())),
                             epoch1=dict(mean=float(e0.mean()), min=float(e0.min()), max=float(e0.max()))))
    return rows


# ---------- output ----------


def md(lo: list[dict], checks: list[str], to: list[dict], rep: list[dict], prov: list[dict], s0: list[dict],
       notes: list[str]) -> str:
    changed = [r for r in lo if r["n_changed"]]
    L = ["# D27 CPU items: LORO (D27-E), TOST on last - last_noise (D27-A), step-0 SSL loss (D27-E)", "",
         "Script: scripts/analysis/d27_cpu.py. ROC-AUC x100, eval-mode probe, encoder tap. Post hoc and "
         "descriptive; the registered verdicts stay primary.", "",
         "## 1. Leave-one-rotation-out", "",
         "Per rotation: mean over its seeds ([S_r, 1000+r, 2000+r]; S_r only where marked 1), as read_d24.py. "
         "All 5 rotations: the D18 paired rule (|mean| > 3 and same sign in >= 4 of 5) and D17 (|mean| <= 3: "
         "random features explain it; mean > 3 and >= 4 of 5 positive: SSL adds to random init; else neither). "
         "**Adaptation for 4 rotations (post hoc choice, made before looking at any LORO output of this "
         "script): the same rules with 'same sign in at least 3 of 4' and the same |mean| > 3 (D17: |mean| <= "
         "3; mean > 3 and >= 3 of 4 positive).** This is read_step1.paired / d17 applied to 4 values (their "
         "n - 1 sign count). Disclosure: stats_d25.py E10(e) had already printed leave-one-out strings with this "
         "rule for the 24 D24-A verdicts (artifacts/analysis/stats/e10-stats.md); they are checked equal below.",
         "", "Self-checks passed before any row was written:", *[f"- {c}" for c in checks], "",
         f"**{len(changed)} of {len(lo)} verdicts change when one rotation is dropped** "
         f"({sum(r['n_changed'] for r in lo)} of {5 * len(lo)} drops; "
         + ", ".join(f"{i} {sum(r['n_changed'] > 0 for r in lo if r['item'] == i)} of "
                     f"{sum(r['item'] == i for r in lo)}" for i in dict.fromkeys(r["item"] for r in lo)) + "):"]
    L += [f"- {r['item']} {r['setting']} {r['model']} {r['probe']} {r['name']}: {r['verdict']} -> "
          + "; ".join(f"without {x['rot']}: {x['verdict']} ({x['mean']:+.1f})" for x in r["drop"] if x["changed"])
          for r in changed]
    L += ["", "| item | setting | model | head | seeds/rot | contrast | per rotation (rot0..rot4) | 5 rotations "
          "| " + " | ".join(f"without {r}" for r in ROTS) + " | changes |", "|" + "---|" * 13]
    for r in lo:
        cells = [f"**{x['mean']:+.1f} {SHORT[x['verdict']]}**" if x["changed"] else
                 f"{x['mean']:+.1f} {SHORT[x['verdict']]}" for x in r["drop"]]
        L.append(f"| {r['item']} | {r['setting']} | {r['model']} | {r['probe']} | {r['seeds_per_rot']} | "
                 f"{r['name']} | "
                 f"{', '.join(f'{x:+.1f}' for x in r['per_rot'])} | {r['mean']:+.1f} {SHORT[r['verdict']]} | "
                 + " | ".join(cells) + f" | {r['n_changed']} |")
    L += ["", "## 2. TOST on last - last_noise (margin 3, alpha 0.05)", "",
          "Units: 5 rotation means (seeds paired within rotation) or the 5 paper-split seeds; t with df 4; "
          "TOST p = max of the two one-sided t tests (stats_d25.tost_p); 'equivalent' only if p < 0.05 (90% "
          "t-interval inside (-3, +3)). D19 (registered): 'the gain needs EEG data' if last wins by the paired "
          "rule; 'perturbation alone explains it' if |mean| <= 3; else 'unclear'. A4 (S1LRN<i>), A5 (S3LRN<i>) "
          "and A7 (S3DN11/12) have 1 seed per rotation: D19 and TOST p are descriptive. last - lp and "
          "last_noise - lp are descriptive (lp from the tags in the 'lp from' column, same seeds). Asserted "
          "before writing: E27 rows equal artifacts/analysis/E27/e27.json (last - last_noise mean and rule, "
          "last - lp); A4/A5 linear lp equals the E29 lp (e29.json); A6 mlp_fullft last - lp equals E25 "
          "(e25_verdicts.json); A7 last - lp equals E28 (e28.json).", "",
          "| item | setting | model | head | last / noise tags | lp from | units | per unit (last - last_noise) | "
          "mean | SD | 90% t | TOST p | equivalent | D19 | last - lp | last_noise - lp |", "|" + "---|" * 16]
    for r in to:
        units = f"5 {r['unit']}s" + (f" x {r['n_seeds']} seeds" if r["n_seeds"] and r["n_seeds"] > 1 else "")
        p = f"{r['tost_p']:.4f}" if r["tost_p"] >= 1e-4 else f"{r['tost_p']:.1e}"
        eq = "yes" if r["equivalent"] else "no" if r["registered"] else "- (descriptive)"
        dl = " (descriptive)" if not r["registered"] else ""
        lpm = [f"{np.mean(r[k]):+.2f}" if r[k] else "-" for k in ("last_lp", "noise_lp")]
        L.append(f"| {r['item']} | {r['setting']} | {r['model']} | {r['probe']} | {r['tags']} | {r['lp_tags']} | "
                 f"{units} | {', '.join(f'{x:+.2f}' for x in r['per_unit'])} | {r['mean']:+.2f} | {r['sd']:.2f} | "
                 f"[{r['ci90'][0]:+.2f}, {r['ci90'][1]:+.2f}] | {p}{dl} | {eq} | {r['d19']}{dl} | {lpm[0]} | "
                 f"{lpm[1]} |")
    L += ["", "### Reproduction checks (D27 design: lp/last under the new tags reproduce the earlier runs)", "",
          "ROC x100 at the val-selected epoch, paired by (model, arm, split, head, seed); 'identical' = "
          "difference exactly 0.", "", "| check | records | paired | identical | max abs diff |",
          "|---|---|---|---|---|"]
    for c in rep:
        mx = "-" if c["max_abs_diff"] is None else f"{c['max_abs_diff']:.3g}"
        L.append(f"| {c['check']} | {c['n_records']} | {c['n_paired']} | {c['n_identical']} | {mx} |")
    L += ["", "### Pairing checks and record counts", "",
          "Per row: one record each for last, last_noise and lp per (model, split, seed, head); same eval_hash, "
          "labels (overlap on rotations, upstream on the paper split), versions (adapt 3, probe 4), test index, "
          "test n/prevalence and probe spec (eval mode, encoder tap); last and last_noise share the adapt spec "
          "(lr, epochs, N, ...) and the noise SSL sample is _hash(last data_hash, 'noise'). No record is used "
          "twice within a row (read_d24.load refuses duplicates).", "",
          "| item | setting | heads | triples | SSL config | records used (tag model arm: n) | gaps |",
          "|---|---|---|---|---|---|---|"]
    for x in prov:
        gaps = "; ".join(x["gaps"][:5]) + (f" (+{len(x['gaps']) - 5} more)" if len(x["gaps"]) > 5 else "")
        L.append(f"| {x['item']} | {x['setting']} | {'/'.join(x['probes'])} | {x['n_triples']} | "
                 f"{'; '.join(x['ssl'])} | {', '.join(f'{k}: {v}' for k, v in x['counts'].items())} | "
                 f"{gaps or 'none'} |")
    L += ["", "## 3. Step-0 SSL loss, pretrained vs random init", "",
          "step_losses[0] = SSL loss on the first batch, before the first optimizer step (src/eegdrift/adapt.py); "
          "epoch 1 = mean loss over the first pass. Over every adapted run of the tag (rotations x seeds, or "
          "the 5 paper-split seeds).", "",
          "| setting | tag | model | arm | init | n | step 0 mean [min, max] | epoch 1 mean [min, max] |",
          "|" + "---|" * 8]
    for r in s0:
        a, b = r["step0"], r["epoch1"]
        L.append(f"| {r['setting']} | {r['tag']} | {r['model']} | {r['arm']} | {r['init']} | {r['n']} | "
                 f"{a['mean']:.4f} [{a['min']:.4f}, {a['max']:.4f}] | "
                 f"{b['mean']:.4f} [{b['min']:.4f}, {b['max']:.4f}] |")
    key = {(r["tag"], r["model"], r["arm"]): [round(v, 9) for x in (r["step0"], r["epoch1"]) for v in x.values()]
           for r in s0}
    same = [k for k in key if k[0] == "S3L" and key.get(("S3FL", *k[1:])) == key[k]]
    if same:
        L += ["", f"S3FL equals S3L in {len(same)} of {sum(k[0] == 'S3L' for k in key)} rows: Siena filtered "
              "changes only the eval preprocessing; the SSL sample (adapt_spec.data_hash) is the same."]
    L += ["", "## Skipped or partial inputs", ""] + ([f"- {n}" for n in notes] or ["- none"])
    return "\n".join(L) + "\n"


def noise_md(to: list[dict], rep: list[dict], prov: list[dict], lo: list[dict], notes: list[str]) -> str:
    """Readable summary of the noise controls (E27 + D27-A A1-A7); every number comes from cpu.json."""
    def row(r):
        p = f"{r['tost_p']:.4f}" if r["tost_p"] >= 1e-4 else f"{r['tost_p']:.1e}"
        lp = " / ".join(f"{np.mean(r[k]):+.1f}" if r[k] else "-" for k in ("last_lp", "noise_lp"))
        arms = " / ".join(f"{np.mean(r[k]):.1f}" if r[k] else "-" for k in ("lp", "last", "last_noise"))
        return (f"| {r['item']} | {r['setting']} | {r['model']} | {r['probe']} | {r['mean']:+.2f} "
                f"[{r['ci90'][0]:+.2f}, {r['ci90'][1]:+.2f}] | {', '.join(f'{x:+.1f}' for x in r['per_unit'])} | "
                f"{r['d19']} | {p} | {'yes' if r['equivalent'] else 'no' if r['registered'] else '-'} | {lp} | "
                f"{arms} |")
    head = ["| item | setting | model | head | last - last_noise, mean [90% t] | per unit | D19 | TOST p | "
            "equivalent | last - lp / last_noise - lp | lp / last / last_noise |", "|" + "---|" * 11]
    reg = [r for r in to if r["registered"]]
    des = [r for r in to if not r["registered"]]
    L = ["# D27-A noise controls: last - last_noise (summary of cpu.md section 2)", "",
         "Script: scripts/analysis/d27_cpu.py (same run as cpu.md / cpu.json). ROC-AUC x100, val-selected epoch, "
         "eval-mode probe, encoder tap. Rule (notes/decisions.md D27-A and 'D27 addition'): D19 three-way on "
         "last - last_noise per head ('the gain needs EEG data' if last wins by the D18 paired rule, |mean| > 3 "
         "and >= 4 of 5 units positive; 'perturbation alone explains it' if |mean| <= 3; else 'unclear'); units "
         "= 5 rotation means over the seeds S_r/1000+r/2000+r, or the 5 paper-split seeds (A1); TOST margin 3, "
         "alpha 0.05, t df 4, 'equivalent' only if TOST rejects. A4, A5 and A7 have 1 seed per rotation and are "
         "descriptive. last - lp and last_noise - lp are descriptive.", "",
         f"## Registered readings ({len(reg)} rows)", "", *head, *map(row, reg), "",
         f"## Descriptive, 1 seed per rotation ({len(des)} rows)", "", *head, *map(row, des), ""]
    L.append("## Counts")
    L.append("")
    for name, rs in (("registered", reg), ("descriptive", des)):
        for v in ("the gain needs EEG data", "unclear", "perturbation alone explains it"):
            hit = [r for r in rs if r["d19"] == v]
            eq = f"; TOST equivalent in {sum(bool(r['equivalent']) for r in hit)}" if name == "registered" else ""
            L.append(f"- {name}, '{v}': {len(hit)} of {len(rs)}{eq}"
                     + (": " + "; ".join(f"{r['item']} {r['setting']} {r['model']} {r['probe']} {r['mean']:+.2f}"
                                         for r in hit) if hit and v != "perturbation alone explains it" else ""))
    by = defaultdict(set)
    for r in to:
        by[(r["item"], r["setting"], r["model"])].add((r["probe"], r["d19"]))
    split = [f"{k[0]} {k[1]} {k[2]}: " + ", ".join(f"{p} {v}" for p, v in sorted(s))
             for k, s in by.items() if len({v for _, v in s}) > 1]
    low = [f"{r['item']} {r['setting']} {r['model']} {r['probe']}" for r in to
           if r["lp"] and max(np.mean(r[k]) for k in ("lp", "last", "last_noise")) < 50]
    L += ["", "Head-dependent D19 readings (raw head and linear_z disagree): "
          + ("; ".join(split) if split else "none"), "",
          "Rows where lp, last and last_noise all average below ROC 50 (the difference is between below-chance "
          "scores): " + ("; ".join(low) if low else "none"), "", "## Checks", ""]
    L += [f"- {c['check']}: {c['n_identical']} of {c['n_paired']} paired values identical"
          + ("" if c["max_abs_diff"] is None else f" (max |diff| {c['max_abs_diff']:.3g})") for c in rep]
    bad = [x for x in prov if x["gaps"]]
    L.append(f"- Pairing and provenance (one record per last / last_noise / lp, same eval data, labels, versions, "
             f"test index, probe spec, adapt spec, derived noise sample): {len(prov) - len(bad)} of {len(prov)} "
             f"rows with no gap ({sum(x['n_triples'] for x in prov)} triples)"
             + ("" if not bad else "; gaps in " + ", ".join(f"{x['item']} {x['setting']}" for x in bad)))
    L += ["- Lp pairings asserted equal to E25 (A6 mlp_fullft), E28 (A7) and E29 (A4/A5 linear lp); E27 rows "
          "equal artifacts/analysis/E27/e27.json.", "",
          f"Leave-one-rotation-out (cpu.md section 1): {sum(r['n_changed'] > 0 for r in lo)} of {len(lo)} "
          "verdicts change when one rotation is dropped.", "", "## Skipped or partial inputs", ""]
    L += [f"- {n}" for n in notes] or ["- none"]
    return "\n".join(L) + "\n"


def main() -> int:
    notes: list[str] = []
    lo = loro(notes)
    checks = check_published(lo)
    to = tost(notes)
    rep = repro(notes)
    prov = provenance()
    s0 = step0(notes)
    OUT.mkdir(parents=True, exist_ok=True)
    text = md(lo, checks, to, rep, prov, s0, notes)
    (OUT / "cpu.md").write_text(text)
    js = dict(notes=notes, checks=checks, loro=lo, tost=to, repro=rep, provenance=prov, step0=s0)
    (OUT / "cpu.json").write_text(json.dumps(js, indent=1))
    (OUT / "noise.md").write_text(noise_md(to, rep, prov, lo, notes))
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
