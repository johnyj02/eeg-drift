#!/usr/bin/env python3
"""E17-free (D25): search for the origin of the paper's N_total = 4,174 CHB-MIT SSL windows.

Stages (the first two run on the desktop, the third anywhere):

    # (a) per-window peak |x| of our 81,993-window SSL store
    ~/dxenv/bin/python scripts/analysis/origin_4174.py peaks --store ~/dxdata/lmdb/chbmit_ssl30
    # (b) throwaway copies of the RELEASED LMDB script, one per variant, run outside the repo
    ~/dxenv/bin/python scripts/analysis/origin_4174.py released --clone ~/e17free/eea \
        --root ~/dxdata/chbmit/1.0.0 --work ~/e17free/runs --mne16-python ~/e17free/venv-mne16/bin/python
    # (a)+(b)+(c) tables, hit test and figures
    .venv/bin/python scripts/analysis/origin_4174.py report

Pre-registered (notes/completeness-audit.md E17-free, adopted as written by decisions.md D25):
- (a) counts of our SSL store windows with max|x| < T, T from 100 to 700 uV over the full 30 s
  window (non-zero channels, the released rule), per subject, as stored (uV, /700 normalisation)
  and with the "6x" scaling (6 * max|x| < T).
- (b) the released dataset_pretrain/make_CHBMIT_for_pretraining.py (d056cdf, sha256 pinned below)
  with variants: as released; x6 before the threshold; 100 uV; 800 uV; min_channels=16; chb01-24;
  10 s windows; MNE 1.6 (1.6.1 with the released numpy 1.26.4 / scipy 1.11.4 pins).
- (c) sums: single patient, val-only (process2.py val = chb21, chb22), first-k files in the
  released seed-1 shuffle order, seizure files only, cumulative per patient (sorted order).
- Targets 4,174, 86,592 and 86,592 / 0.4 = 216,480. Rule D25-E17: "match" = a rule giving the
  target exactly; within +-1 % of it = "near". A match feeds E23.
Fixed here before any count was computed (the audit gives the T range, not its step): a
threshold "rule" in (a) is a round T in {100, 150, ..., 700} uV. The full 1 uV curve (1-700) is drawn,
and the T at which it crosses a target is reported as "inverse T*", descriptive and NEVER a
match (a continuous threshold can always be tuned to any count). (b) variants are compared with
(a) and with our store (descriptive). (c) is applied to every (b) variant; the as-released row is
the primary one, the others descriptive; candidate counts are reported for multiplicity.

The released script is never copied into this repository: `released` copies it from a clone
OUTSIDE the repo into --work, verifies its sha256, replaces at most one line per variant by line
number (our own replacement text, below), and runs it with cwd = --work/<variant>, where a real
directory named '$WORK' holds a symlink to the raw data, so its hard-coded relative paths resolve
unmodified (storage shim: see KEYS_ONLY_SHIM). Writes artifacts/analysis/n4174/.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pickle
import re
import shutil
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "artifacts" / "analysis" / "n4174"
RELEASED = "dataset_pretrain/make_CHBMIT_for_pretraining.py"
RELEASED_SHA256 = "088d8c5db2d80cb3d95ff9d0ae0c92b3b541f4a6cbf8963d0c60c06af7170a05"
RELEASED_LINES = 231
TARGETS = {"4,174": 4174, "86,592": 86592, "86,592/0.4": 216480}
T_RULES = tuple(range(100, 701, 50))
T_CURVE = np.arange(1, 701)   # descriptive curve; rules are T_RULES
VAL = ("chb21", "chb22")
# Variant -> {1-based line of the released file: replacement line}. Lines are located by number
# only (the sha256 pins the file), so no released text lives here. 99 is a blank line.
VARIANTS: dict[str, dict[int, str]] = {
    "as_released": {},
    "x6": {99: "    signals = signals * 6"},
    "t100": {135: "        permissible_amplitude = 100.0"},
    "t800": {135: "        permissible_amplitude = 800.0"},
    "min16": {203: "            preprocessing_recording(file_path, db, file_key_list, min_channels=16)"},
    "chb01_24": {163: '    train_val_pats = [f"chb{i:02d}" for i in range(1, 25)]'},
    "win10": {69: "    window_len = 10"},
    "mne16": {},
}
LMDB_REL = "$WORK/datasets/physionet.org/files/chbmit/chbmit_preprocessed_30S.lmdb"
# Storage shim, put on PYTHONPATH (as sitecustomize) of the variant runs only. The released script
# commits one LMDB transaction per 384 KB window; on the shared desktop's EBS volume that ran at
# ~0.3 s per window with fsync, and still saturated the volume without it (8 variants x ~31 GB).
# The shim keeps lmdb.open/begin/commit and the __keys__ write, and turns every OTHER put into a
# no-op. The released code appends a key to its list before the put and never checks the put's
# return value, so which windows are kept, their keys, and len(__keys__) are unchanged; only the
# window arrays are not stored (the count is all this item needs).
KEYS_ONLY_SHIM = """import lmdb

_open = lmdb.open


class _Txn:
    def __init__(self, txn):
        self._txn = txn

    def put(self, key, value, *a, **kw):
        return self._txn.put(key, value, *a, **kw) if key == b"__keys__" else True

    def __getattr__(self, name):
        return getattr(self._txn, name)


class _Env:
    def __init__(self, env):
        self._env = env

    def begin(self, *a, **kw):
        return _Txn(self._env.begin(*a, **kw))

    def __getattr__(self, name):
        return getattr(self._env, name)


def _keys_only_open(path, **kw):
    kw.setdefault("sync", False)
    kw.setdefault("metasync", False)
    return _Env(_open(path, **kw))


lmdb.open = _keys_only_open
"""
RAW_REL = "$WORK/datasets/physionet.org/files/chbmit/1.0.0"


# ---------------------------------------------------------------- (a) our store, desktop
def peaks(args) -> int:
    """One sequential cursor pass (random per-window reads were I/O-bound on the shared desktop)."""
    import lmdb  # noqa: PLC0415

    path = os.path.expanduser(args.store)
    env = lmdb.open(path, readonly=True, lock=False, subdir=True, readahead=True)
    with env.begin() as txn:
        meta = json.loads(txn.get(b"__meta__"))
        index = json.loads(txn.get(b"__index__"))
        pos = {r["key"].encode(): i for i, r in enumerate(index)}
        pk = np.full((len(index), 2), np.nan, np.float32)
        for k, buf in txn.cursor():
            if k not in pos:
                continue
            x = np.frombuffer(buf, dtype=meta["dtype"]).reshape(meta["shape"])
            nz = np.any(x != 0, axis=(1, 2))
            if nz.any():
                pk[pos[k]] = np.max(np.abs(x[nz])), np.max(np.abs(x[nz] * 6))   # float32, as the x6 script
            else:
                pk[pos[k]] = 0.0, 0.0
    env.close()
    if np.isnan(pk).any():
        raise SystemExit(f"{int(np.isnan(pk[:, 0]).sum())} index keys not found in the store")
    OUT.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT / "ssl_peaks.npz", key=np.array([r["key"] for r in index]),
                        stem=np.array([r["file"] for r in index]),
                        case=np.array([r["case"] for r in index]), peak=pk[:, 0], peak6=pk[:, 1])
    print(f"{len(index)} windows, peak max {pk[:, 0].max():.2f} uV, min {pk[:, 0].min():.2f}")
    return 0


# ---------------------------------------------------------------- (b) released script, desktop
def _versions(py: str) -> dict:
    code = ("import mne, numpy, scipy, sys; "
            "print(mne.__version__, numpy.__version__, scipy.__version__, sys.version.split()[0])")
    v = subprocess.run([py, "-c", code], capture_output=True, text=True, check=True).stdout.split()
    return dict(zip(("mne", "numpy", "scipy", "python"), v, strict=True))


def _keys(db: Path) -> list[str]:
    import lmdb  # noqa: PLC0415

    env = lmdb.open(str(db), readonly=True, lock=False, subdir=True)
    with env.begin() as txn:
        raw = txn.get(b"__keys__")
    env.close()
    return [] if raw is None else pickle.loads(raw)   # our own run's output, trusted


def _log_rows(log: str) -> list[list]:
    """[file stem, accepted, status] in processing order, from the released script's prints."""
    rows = []
    for line in log.splitlines():
        if m := re.match(r"Processed (\S+): (\d+) accepted, (\d+) rejected", line):
            rows.append([m[1], int(m[2]), f"ok, {m[3]} rejected"])
        elif m := re.match(r"Skipping \S*/(\S+)\.edf: (.*)", line):
            rows.append([m[1], 0, m[2]])
        elif m := re.match(r"Insufficient data in (\S+): (.*)", line):
            rows.append([m[1], 0, m[2]])
    return rows


def released(args) -> int:
    clone, work = Path(os.path.expanduser(args.clone)), Path(os.path.expanduser(args.work))
    src = (clone / RELEASED).read_bytes()
    if hashlib.sha256(src).hexdigest() != RELEASED_SHA256:
        raise SystemExit(f"{clone / RELEASED}: sha256 differs from the pinned d056cdf file")
    lines = src.decode().split("\n")
    if len(lines) != RELEASED_LINES + 1:   # trailing newline
        raise SystemExit("unexpected line count")
    names = args.only.split(",") if args.only else list(VARIANTS)
    shim = work / "_shim"
    shim.mkdir(parents=True, exist_ok=True)
    (shim / "sitecustomize.py").write_text(KEYS_ONLY_SHIM)
    procs = {}
    for k, name in enumerate(names):
        d = work / name
        if d.exists():
            raise SystemExit(f"{d} exists; remove it first (throwaway runs are never reused)")
        (d / RAW_REL).parent.mkdir(parents=True)
        (d / RAW_REL).symlink_to(os.path.expanduser(args.root))
        patched = list(lines)
        for ln, text in VARIANTS[name].items():
            patched[ln - 1] = text
        script = d / "make_chbmit_variant.py"
        script.write_text("\n".join(patched))
        py = os.path.expanduser(args.mne16_python if name == "mne16" else args.python)
        cpus = f"{args.cpu0 + 4 * k}-{args.cpu0 + 4 * k + 3}"
        env = {**os.environ, "OMP_NUM_THREADS": "4", "MKL_NUM_THREADS": "4",
               "OPENBLAS_NUM_THREADS": "4", "PYTHONUNBUFFERED": "1", "PYTHONPATH": str(shim)}
        log = open(d / "run.log", "w")   # noqa: SIM115 - closed after wait()
        procs[name] = (subprocess.Popen(["taskset", "-c", cpus, py, str(script)], cwd=d, env=env,
                                        stdout=log, stderr=subprocess.STDOUT), log, time.time(), py)
        print(f"started {name} on cpus {cpus}", flush=True)
    (OUT / "released").mkdir(parents=True, exist_ok=True)
    for name, (p, log, t0, py) in procs.items():
        rc = p.wait()
        log.close()
        d = work / name
        keys = _keys(d / LMDB_REL) if rc == 0 else []
        per_file = Counter(k.rsplit("_", 1)[0] for k in keys)
        rows = _log_rows((d / "run.log").read_text(errors="replace"))
        bad = [r for r in rows if r[1] != per_file.get(r[0], 0)]
        rec = {"variant": name, "returncode": rc, "seconds": round(time.time() - t0),
               "patch": {str(k): v for k, v in VARIANTS[name].items()}, "python": py,
               "lmdb_shim": "keys-only: window puts are no-ops, __keys__ written; sync off",
               "versions": _versions(py), "released_sha256": RELEASED_SHA256,
               "n_keys": len(keys), "n_unique_keys": len(set(keys)), "files_in_order": rows,
               "log_vs_keys_mismatch": bad}
        (OUT / "released" / f"{name}.json").write_text(json.dumps(rec, indent=1))
        if name == "as_released":
            (OUT / "released" / "as_released_keys.json").write_text(json.dumps(keys))
        print(f"{name}: rc {rc}, {len(keys)} keys, {rec['seconds']} s, log/keys mismatches {len(bad)}",
              flush=True)
        if args.delete_lmdb and rc == 0 and name != "as_released":
            shutil.rmtree(d / LMDB_REL)
    return 0


# ---------------------------------------------------------------- report
def classify(v: float) -> list[tuple[str, str]]:
    """[(target, 'match' | 'near')] for one candidate count."""
    out = []
    for name, t in TARGETS.items():
        if v == t:
            out.append((name, "match"))
        elif abs(v - t) <= 0.01 * t:
            out.append((name, "near"))
    return out


def bracket(seq: list[int], t: int) -> str:
    """Closest cumulative values below/above t, with their k."""
    below = max(((v, k) for k, v in enumerate(seq, 1) if v <= t), default=None)
    above = min(((v, k) for k, v in enumerate(seq, 1) if v >= t), default=None)
    f = lambda x: "-" if x is None else f"{x[0]:,} (k={x[1]})"   # noqa: E731
    return f"{f(below)} / {f(above)}"


def report(_args) -> int:
    import matplotlib  # noqa: PLC0415

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt  # noqa: PLC0415

    z = np.load(OUT / "ssl_peaks.npz")
    case, peak, peak6 = z["case"], z["peak"].astype(np.float64), z["peak6"].astype(np.float64)
    cases = sorted(set(case.tolist()))
    seizures = json.loads((ROOT / "configs" / "chbmit_seizures.json").read_text())
    seizure_files = {f for f, v in seizures.items() if v}
    cand: list[dict] = []   # every candidate count tested against the targets

    def add(family: str, variant: str, rule: str, value: int, primary: bool) -> None:
        cand.append({"family": family, "variant": variant, "rule": rule, "value": int(value),
                     "primary": primary, "hits": classify(value)})

    # (a)
    curve = {"uV": [int((peak < t).sum()) for t in T_CURVE], "6x": [int((peak6 < t).sum()) for t in T_CURVE]}
    for t in T_RULES:
        add("a: total", "our store", f"max|x| < {t} uV", (peak < t).sum(), True)
        add("a: total", "our store", f"6 max|x| < {t} uV", (peak6 < t).sum(), True)
        for c in cases:
            m = case == c
            add("a: one subject", "our store", f"{c}, max|x| < {t} uV", (peak[m] < t).sum(), True)
            add("a: one subject", "our store", f"{c}, 6 max|x| < {t} uV", (peak6[m] < t).sum(), True)
    inverse = {}
    for scale, vals in curve.items():
        inverse[scale] = {}
        for name, t in TARGETS.items():
            v = np.asarray(vals)
            i = int(np.searchsorted(v, t))   # curve is non-decreasing in T
            inverse[scale][name] = None if i >= len(v) else {"T_uV": int(T_CURVE[i]), "count": int(v[i]),
                                                             "count_at_T-1": int(v[i - 1]) if i else None}
    # (b) + (c)
    variants = {}
    for name in VARIANTS:
        p = OUT / "released" / f"{name}.json"
        if p.exists():
            variants[name] = json.loads(p.read_text())
    store_files = Counter(z["stem"].tolist())
    cmp_rows = []
    for name, rec in variants.items():
        prim = name == "as_released"
        add("b: variant total", name, "len(__keys__)", rec["n_keys"], True)
        order = rec["files_in_order"]
        per_file = {f: n for f, n, _ in order}
        by_case = Counter()
        for f, n in per_file.items():
            by_case[re.match(r"chb\d\d", f)[0]] += n
        for c, n in sorted(by_case.items()):
            add("c: single patient", name, c, n, prim)
        add("c: val-only", name, "chb21 + chb22", sum(by_case[c] for c in VAL), prim)
        add("c: seizure files only", name, "files with >= 1 seizure", sum(n for f, n in per_file.items()
                                                                          if f in seizure_files), prim)
        cum_files = list(np.cumsum([n for _, n, _ in order]).astype(int))
        cum_cases = list(np.cumsum([by_case[c] for c in sorted(by_case)]).astype(int))
        for k, v in enumerate(cum_files, 1):
            add("c: first-k files (seed-1 order)", name, f"k={k}", v, prim)
        for k, v in enumerate(cum_cases, 1):
            add("c: first-k patients (sorted)", name, f"chb01..{sorted(by_case)[k - 1]}", v, prim)
        rec["_cum_files"], rec["_cum_cases"] = cum_files, cum_cases
        diff = sorted(f for f in set(per_file) | set(store_files) if per_file.get(f, 0) != store_files.get(f, 0))
        cmp_rows.append((name, rec["n_keys"], len(diff), diff[:6]))
    hits = [c for c in cand if c["hits"]]
    exact = [c for c in hits if any(h[1] == "match" for h in c["hits"])]

    L = ["# E17-free: origin of N_total = 4,174 (D25-E17)", "",
         "Rule (pre-registered): a rule giving 4,174 / 86,592 / 216,480 exactly is a **match**; within "
         "+-1 % is **near**. Threshold rules are round T in {100, 150, ..., 700} uV; inverse T* is "
         "descriptive. (c) on the as-released counts is primary; on other variants descriptive.", "",
         f"Candidates tested: {len(cand)} ({sum(c['primary'] for c in cand)} primary). "
         f"Exact matches: {len(exact)} ({sum(c['primary'] for c in exact)} primary). "
         f"Near: {len(hits) - len(exact)}.", "",
         "## Verdict", ""]
    pe = [c for c in exact if c["primary"]]
    if pe:
        L += [f"- **MATCH**: {c['family']} / {c['variant']} / {c['rule']} = {c['value']:,} -> {c['hits']}"
              for c in pe]
    else:
        L.append("- **No pre-registered rule reaches 4,174 (or 86,592, 216,480) exactly.**")
    L += [f"- descriptive exact: {c['family']} / {c['variant']} / {c['rule']} = {c['value']:,}"
          for c in exact if not c["primary"]]
    L += [f"- primary NEAR (+-1 %, a label, not a match): {c['family']} / {c['variant']} / {c['rule']} = "
          f"{c['value']:,} ({'; '.join(f'{a} {b}' for a, b in c['hits'])})"
          for c in hits if c["primary"] and c not in exact]
    # One row per run of consecutive first-k candidates with the same variant and hit (plateaus repeat).
    rows: list[dict] = []
    for c in hits:
        h = "; ".join(f"{a} {b}" for a, b in c["hits"])
        k = int(c["rule"][2:]) if c["family"].startswith("c: first-k files") else None
        last = rows[-1] if rows else None
        if k is not None and last and last["key"] == (c["family"], c["variant"], h) and last["k1"] == k - 1:
            last.update(k1=k, lo=min(last["lo"], c["value"]), hi=max(last["hi"], c["value"]))
            continue
        rows.append({"key": (c["family"], c["variant"], h), "k0": k, "k1": k, "lo": c["value"], "hi": c["value"],
                     "rule": c["rule"], "primary": c["primary"]})
    L += ["", "## All near / exact hits (consecutive first-k rows merged)", "",
          "| family | variant | rule | count | hit | primary |", "|---|---|---|---|---|---|"]
    for r in rows:
        rule = r["rule"] if r["k0"] == r["k1"] else f"k={r['k0']}..{r['k1']}"
        n = f"{r['lo']:,}" if r["lo"] == r["hi"] else f"{r['lo']:,}..{r['hi']:,}"
        fam, var, h = r["key"]
        L.append(f"| {fam} | {var} | {rule} | {n} | {h} | {'yes' if r['primary'] else 'no'} |")
    L += ["", "## (a) Our SSL store (81,993 windows, all max|x| < 700 uV by construction)", "",
          "| T (uV) | max|x| < T | 6 max|x| < T |", "|---|---|---|"]
    L += [f"| {t} | {int((peak < t).sum()):,} | {int((peak6 < t).sum()):,} |" for t in T_RULES]
    flat = Counter(case[peak < 1.0].tolist())
    L += ["", f"Flat windows (max|x| < 1 uV, descriptive): {sum(flat.values())}, "
          f"by case {dict(sorted(flat.items()))}."]
    L += ["", "Inverse T* (smallest integer T whose count >= target; descriptive, not a rule):", ""]
    for scale, d in inverse.items():
        for name, v in d.items():
            if v is None:
                L.append(f"- {scale}, {name}: above 700 uV (not reachable in this store)")
                continue
            prev = "n/a, already reached at the 100 uV start" if v["count_at_T-1"] is None else \
                f"{v['count_at_T-1']:,}"
            L.append(f"- {scale}, {name}: T* = {v['T_uV']} uV gives {v['count']:,} (T*-1 gives {prev})")
    L += ["", "Per subject, max|x| < T (uV):", "",
          "| case | " + " | ".join(str(t) for t in T_RULES) + " |", "|---" * (len(T_RULES) + 1) + "|"]
    for c in cases:
        m = case == c
        L.append(f"| {c} | " + " | ".join(f"{int((peak[m] < t).sum()):,}" for t in T_RULES) + " |")
    L += ["", "Per subject, 6 max|x| < T (uV):", "",
          "| case | " + " | ".join(str(t) for t in T_RULES) + " |", "|---" * (len(T_RULES) + 1) + "|"]
    for c in cases:
        m = case == c
        L.append(f"| {c} | " + " | ".join(f"{int((peak6[m] < t).sum()):,}" for t in T_RULES) + " |")
    L += ["", "## (b) Released script variants", "",
          "| variant | patch (line: our text) | mne / numpy / scipy | rc | len(__keys__) | "
          "files differing from our store | s |",
          "|---|---|---|---|---|---|---|"]
    for name, n, nd, ex in cmp_rows:
        rec = variants[name]
        v = rec["versions"]
        patch = "; ".join(f"L{k}: `{t.strip()}`" for k, t in rec["patch"].items()) or "none"
        L.append(f"| {name} | {patch} | {v['mne']} / {v['numpy']} / {v['scipy']} | {rec['returncode']} | "
                 f"{n:,} | {nd} {ex if nd else ''} | {rec['seconds']} |")
    kp = OUT / "released" / "as_released_keys.json"
    if kp.exists():
        rk, ok_ = set(json.loads(kp.read_text())), set(z["key"].tolist())
        L.append(f"\nas_released __keys__ vs our store index (descriptive, cf. E1): {len(rk & ok_):,} shared, "
                 f"{len(rk - ok_):,} only released, {len(ok_ - rk):,} only ours -> "
                 f"{'IDENTICAL key sets' if rk == ok_ else 'DIFFERENT key sets'}.")
    missing = [n for n in VARIANTS if n not in variants]
    if missing:
        L.append(f"\nNOT RUN / missing records: {missing}")
    L += ["", "## (c) Sums (closest cumulative value below / above each target)", "",
          "| variant | val-only | seizure files | first-k files (seed-1): 4,174 | first-k patients: 4,174 | "
          "first-k files: 86,592 | first-k files: 216,480 |", "|---|---|---|---|---|---|---|"]
    for name, rec in variants.items():
        val = next(c["value"] for c in cand if c["variant"] == name and c["family"] == "c: val-only")
        sz = next(c["value"] for c in cand if c["variant"] == name and c["family"] == "c: seizure files only")
        L.append(f"| {name} | {val:,} | {sz:,} | {bracket(rec['_cum_files'], 4174)} | "
                 f"{bracket(rec['_cum_cases'], 4174)} | {bracket(rec['_cum_files'], 86592)} | "
                 f"{bracket(rec['_cum_files'], 216480)} |")
    steps = [n for _, n, _ in variants["as_released"]["files_in_order"] if n] if "as_released" in variants else []
    if steps:
        m = float(np.mean(steps))
        L += ["", f"Chance yardstick (descriptive): as released, the mean non-zero per-file count is {m:.1f}, "
              f"so one cumulative file sequence passing a target hits it exactly with probability about "
              f"1/{m:.0f} and lands within +-1 % of 4,174 with probability about {min(1, 84 / m):.2f}."]
    # Post hoc (NOT a pre-registered target): every candidate against the paper's other two N_total
    # values (Fig. 1 caption, artifacts/paper/paper.txt l.306-307), with the number of candidates searched.
    paper_n = {"TUAB": 57614, "TUEV": 86587}
    post = [(c, ds) for c in cand for ds, v in paper_n.items() if c["value"] == v]
    L += ["", "## Post hoc: candidates equal to the paper's TUAB / TUEV N_total (not pre-registered)", ""]
    L += [f"- {c['family']} / {c['variant']} / {c['rule']} = {c['value']:,} = the paper's {ds} N_total"
          for c, ds in post] or ["- none"]
    L.append(f"- {len(cand)} candidate counts searched against these 2 numbers.")
    # Released conf_diversity/dataset/{chbmit,tuev}.yaml (d056cdf): chbmit compute_steps 2706, tuev 68, both
    # commented "S=N*E/B - N=4174, E=4, B=256 - we get 68 steps". main_diversityN.py:315-316 computes the
    # budget as spt_epochs * ceil(len(LMDB) / B) (spt_epochs 4) and never reads compute_steps.
    L += ["", "## Where the targets come from (descriptive arithmetic, no rule)", "",
          f"- 86,592 = 2706 x 128 / 4 (the CHB-MIT diversity config's unused compute_steps read as S = N E / B, "
          f"B = 128, E = 4). 86,587 x 4 / 128 = {86587 * 4 / 128:.2f}, which rounds to 2706. The code's own "
          "budget 4 x ceil(N / B) is a multiple of 4, which 2706 is not.",
          f"- The TUEV config's 68 = 4 x ceil(4,174 / 256) = {4 * -(-4174 // 256)}, and its comment derives 68 "
          "from N = 4174 (the CHB-MIT config carries the same comment next to 2706)."]
    text = "\n".join(L) + "\n"
    (OUT / "n4174.md").write_text(text)
    (OUT / "n4174.json").write_text(json.dumps({"candidates": cand, "inverse_T": inverse, "targets": TARGETS,
                                                "curve_T": T_CURVE.tolist(), "curve": curve}, indent=1))
    print(text)

    # figures
    ink, grid = "#52514e", "#e4e3df"
    blue, orange, aqua = "#2a78d6", "#eb6834", "#1baf7a"
    plt.rcParams.update({"axes.edgecolor": ink, "axes.labelcolor": ink, "xtick.color": ink, "ytick.color": ink,
                         "axes.spines.top": False, "axes.spines.right": False, "font.size": 9})

    def targets(ax, horizontal=True):
        for name, t in TARGETS.items():
            (ax.axhline if horizontal else ax.axvline)(t, color=ink, lw=0.8, ls="--")
            if horizontal:
                ax.text(ax.get_xlim()[0], t, f" {name}", va="bottom", ha="left", color=ink, fontsize=8)

    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    ax.plot(T_CURVE, curve["uV"], color=blue, lw=2, label="max|x| < T (as stored, /700)")
    ax.plot(T_CURVE, curve["6x"], color=orange, lw=2, label="6 x max|x| < T (the '6x' variant)")
    ax.set_yscale("log")
    ax.set_xlim(0, 700)
    ax.axvspan(0, 100, color=grid, zorder=0)
    ax.text(50, 300, "below the\npre-registered\nT range", ha="center", color=ink, fontsize=7)
    targets(ax)
    ax.set_xlabel("threshold T (uV)")
    ax.set_ylabel("windows kept (of 81,993)")
    ax.grid(color=grid, lw=0.6)
    ax.legend(frameon=False, loc="lower right")
    ax.set_title("E17-free (a): our SSL store vs amplitude threshold", color=ink, fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / "fig_a_threshold_curve.png", dpi=160)
    plt.close(fig)

    mat = np.array([[(peak[case == c] < t).sum() for t in T_RULES] for c in cases], dtype=float)
    fig, ax = plt.subplots(figsize=(7.2, 6.4))
    im = ax.imshow(np.log10(mat + 1), cmap="Blues", aspect="auto")
    for i in range(len(cases)):
        for j in range(len(T_RULES)):
            near = abs(mat[i, j] - 4174) <= 41.74
            ax.text(j, i, f"{int(mat[i, j])}", ha="center", va="center", fontsize=6,
                    color="#0b0b0b" if mat[i, j] < 10 ** (0.6 * np.log10(mat.max() + 1)) else "white",
                    fontweight="bold" if near else "normal")
    ax.set_xticks(range(len(T_RULES)), [str(t) for t in T_RULES])
    ax.set_yticks(range(len(cases)), cases)
    ax.set_xlabel("threshold T (uV), max|x| < T")
    fig.colorbar(im, ax=ax, label="log10(windows + 1)")
    ax.set_title("E17-free (a): windows per subject (bold = within 1 % of 4,174)", color=ink, fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / "fig_a_per_subject.png", dpi=160)
    plt.close(fig)

    if variants:
        fig, ax = plt.subplots(figsize=(6.4, 3.4))
        names = list(variants)
        ax.barh(names, [variants[n]["n_keys"] for n in names], color=blue, height=0.6)
        for i, n in enumerate(names):
            ax.text(variants[n]["n_keys"], i, f" {variants[n]['n_keys']:,}", va="center", color=ink, fontsize=8)
        ax.set_xscale("log")
        targets(ax, horizontal=False)
        ax.invert_yaxis()
        ax.set_xlabel("len(__keys__)  (dashed: 4,174 / 86,592 / 216,480)")
        ax.set_title("E17-free (b): released LMDB script variants", color=ink, fontsize=10)
        fig.tight_layout()
        fig.savefig(OUT / "fig_b_variants.png", dpi=160)
        plt.close(fig)
    if "as_released" in variants:
        rec = variants["as_released"]
        fig, axs = plt.subplots(1, 2, figsize=(9, 3.4))
        axs[0].plot(range(1, len(rec["_cum_files"]) + 1), rec["_cum_files"], color=blue, lw=2)
        axs[0].set_xlabel("first k files, released seed-1 shuffle order")
        axs[1].plot(range(1, len(rec["_cum_cases"]) + 1), rec["_cum_cases"], color=aqua, lw=2, marker="o", ms=4)
        axs[1].set_xlabel("first k patients (chb01..)")
        for ax in axs:
            ax.set_yscale("log")
            targets(ax)
            ax.grid(color=grid, lw=0.6)
            ax.set_ylabel("cumulative windows (as released)")
        fig.suptitle("E17-free (c): cumulative sums vs targets", color=ink, fontsize=10)
        fig.tight_layout()
        fig.savefig(OUT / "fig_c_cumulative.png", dpi=160)
        plt.close(fig)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="stage", required=True)
    a = sub.add_parser("peaks")
    a.add_argument("--store", required=True)
    b = sub.add_parser("released")
    b.add_argument("--clone", required=True)
    b.add_argument("--root", required=True)
    b.add_argument("--work", required=True)
    b.add_argument("--python", default=sys.executable)
    b.add_argument("--mne16-python", required=True)
    b.add_argument("--only", default="", help="comma list of variants (default: all)")
    b.add_argument("--cpu0", type=int, default=48, help="first CPU; variant k gets cpu0+4k .. +3")
    b.add_argument("--delete-lmdb", action="store_true")
    sub.add_parser("report")
    args = ap.parse_args()
    return {"peaks": peaks, "released": released, "report": report}[args.stage](args)


if __name__ == "__main__":
    raise SystemExit(main())
