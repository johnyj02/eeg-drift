#!/usr/bin/env python3
"""D25-E1: compare the RELEASED CHB-MIT preprocessing outputs with our window stores.

Our own code; imports nothing from upstream (it only reads the files the released scripts wrote).
Runs on the desktop:

    python e1_compare_released.py --chb "$HOME/released/run/\\$WORK/datasets/physionet.org/files/chbmit" \
        --ours-eval ~/dxdata/lmdb/chbmit_eval10 --ours-ssl ~/dxdata/lmdb/chbmit_ssl30 \
        --raw ~/dxdata/chbmit/1.0.0 --lmdb-log ~/released/logs/e1_lmdb.log --out ~/released/e1

Released eval pickles hold the unfiltered 256 Hz window; its loader (src/datasets/chbmit.py)
applies scipy.signal.resample(X, 2000, axis=1) then /100. Our eval store holds the resampled
window in uV (scaling is applied by our reader), so we compare resample(X_released) with ours.
Released SSL values are pickled float32 [16, 30, 200] uV; ours are the same arrays as raw bytes.
Rule (D25-E1): counts must match exactly and per-window max|diff| / max|ref| <= 1e-5.
"""

import argparse
import json
import os
import pickle
import re
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import lmdb
import numpy as np
from scipy.signal import resample

GRID = re.compile(r"^(chb\d\d[a-z]?_\d+[a-z+]?)-(\d+)\.pkl$")
ADD = re.compile(r"^(chb\d\d[a-z]?_\d+[a-z+]?)-s-(\d+)-add-(\d+)\.pkl$")
REL_TOL = 1e-5
DRAFT = {"n_eval_windows": 326993, "test_pos": 252, "test_s_files": 206, "test_ictal_grid": 114,
         "test_ictal_grid_labelled_0": 70, "eval_cases_absent": ["chb12", "chb13", "chb17"],
         "n_ssl_windows": 81993}


def our_key(name: str) -> str:
    m = GRID.match(name)
    if m:
        return f"{m.group(1)}-grid-{m.group(2)}"
    m = ADD.match(name)
    if m:
        return f"{m.group(1)}-add{m.group(2)}-{m.group(3)}"
    raise ValueError(f"unexpected released file name {name}")


def read_label(path: str):
    with open(path, "rb") as f:
        d = pickle.load(f)
    return os.path.basename(path), int(d["y"]), int(d["X"].shape[1]), str(d["X"].dtype)


def open_ours(path: str):
    env = lmdb.open(path, readonly=True, lock=False, subdir=True)
    with env.begin() as txn:
        meta = json.loads(txn.get(b"__meta__"))
        index = json.loads(txn.get(b"__index__"))
    return env, meta, index


def rel_diff(ref: np.ndarray, got: np.ndarray) -> tuple[float, float]:
    d = float(np.max(np.abs(ref.astype(np.float64) - got.astype(np.float64))))
    return d, d / max(float(np.max(np.abs(ref))), 1e-12)


def true_seizures(raw: str) -> dict[str, list[tuple[int, int]]]:
    """file stem -> TRUE [onset, offset) in 256 Hz samples (seconds * 256), from the summaries."""
    out: dict[str, list[tuple[int, int]]] = {}
    for summ in sorted(Path(raw).glob("chb*/chb*-summary.txt")):
        cur, start = None, None
        for line in summ.read_text(errors="replace").splitlines():
            p = line.split()
            if len(p) == 3 and p[0] == "File" and p[1] == "Name:":
                cur = p[2].rsplit(".", 1)[0]
                out[cur] = []
            elif cur and p and p[0] == "Seizure" and "Start" in p:
                start = int(p[-2]) * 256
            elif cur and p and p[0] == "Seizure" and "End" in p:
                out[cur].append((start, int(p[-2]) * 256))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chb", required=True, help="released output root (holds processed*/ and the LMDB)")
    ap.add_argument("--ours-eval", required=True)
    ap.add_argument("--ours-ssl", required=True)
    ap.add_argument("--raw", required=True)
    ap.add_argument("--lmdb-log", default="")
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=2025)
    ap.add_argument("--workers", type=int, default=48)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    chb, out = Path(args.chb), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rep: dict = {"draft": DRAFT, "rel_tol": REL_TOL, "seed": args.seed}

    # --- process1 output: recordings per case
    proc = chb / "processed"
    rep["process1"] = {c.name: len(list(c.glob("*.pkl"))) for c in sorted(proc.iterdir()) if c.is_dir()}
    rep["process1_total_recordings"] = sum(rep["process1"].values())

    # --- process2 output: every pickle's label and length
    seg = chb / "processed_seg"
    paths = [str(p) for s in ("train", "val", "test") for p in sorted((seg / s).glob("*.pkl"))]
    with Pool(args.workers) as pool:
        rows = pool.map(read_label, paths, chunksize=256)
    rel = {}
    for path, (name, y, n, dt) in zip(paths, rows, strict=True):
        rel[our_key(name)] = {"split": Path(path).parent.name, "y": y, "n": n, "dtype": dt, "path": path,
                              "s": "-s-" in name}
    by = {}
    for s in ("train", "val", "test"):
        r = [v for v in rel.values() if v["split"] == s]
        by[s] = {"files": len(r), "pos": sum(v["y"] for v in r), "s_files": sum(v["s"] for v in r),
                 "short": sum(v["n"] != 2560 for v in r)}
    rep["released_eval"] = {"total": len(rel), "by_split": by,
                            "dtypes": dict(Counter(v["dtype"] for v in rel.values())),
                            "cases": sorted({k.split("_")[0] for k in rel})}

    # --- ours vs released, keys / splits / labels
    env, meta, index = open_ours(args.ours_eval)
    ours = {r["key"]: r for r in index}
    common = sorted(set(ours) & set(rel))
    rep["eval_keys"] = {
        "ours_total": len(ours), "released_total": len(rel), "common": len(common),
        "only_ours": sorted(set(ours) - set(rel))[:50], "n_only_ours": len(set(ours) - set(rel)),
        "only_released": sorted(set(rel) - set(ours))[:50], "n_only_released": len(set(rel) - set(ours)),
        "split_mismatch": sum(ours[k]["split"] != rel[k]["split"] for k in common),
        "label_mismatch": sum(ours[k]["label"] != rel[k]["y"] for k in common),
    }

    # --- draft numbers from the RELEASED output: 70 of 114 truly ictal test grid windows
    sz = true_seizures(args.raw)
    ictal = lab0 = 0
    for k, v in rel.items():
        if v["split"] != "test" or v["s"]:
            continue
        stem, i = k.rsplit("-grid-", 1)
        i = int(i)
        if any(i < off and i + 2560 > on for on, off in sz.get(stem, [])):
            ictal += 1
            lab0 += v["y"] == 0
    rep["released_test_ictal_grid"] = ictal
    rep["released_test_ictal_grid_labelled_0"] = lab0

    # --- values, eval: uniform seeded sample + every short (time-stretched) window
    rng = np.random.default_rng(args.seed)
    pick = sorted(rng.choice(len(common), min(args.n, len(common)), replace=False).tolist())
    keys = [common[i] for i in pick] + [k for k in common if rel[k]["n"] != 2560]
    diffs = []
    with env.begin() as txn:
        for k in keys:
            with open(rel[k]["path"], "rb") as f:
                x = pickle.load(f)["X"]
            ref = resample(x, 2000, axis=1)
            got = np.frombuffer(txn.get(k.encode()), dtype=meta["dtype"]).reshape(meta["shape"])
            diffs.append((k, *rel_diff(ref, got)))
    rep["eval_values"] = {"n": len(diffs), "max_abs": max(d[1] for d in diffs),
                          "max_rel": max(d[2] for d in diffs),
                          "n_rel_over_tol": sum(d[2] > REL_TOL for d in diffs),
                          "worst": sorted(diffs, key=lambda d: -d[2])[:5]}
    np.save(out / "eval_rel_diffs.npy", np.array([d[2] for d in diffs]))

    # --- released SSL LMDB
    renv = lmdb.open(str(chb / "chbmit_preprocessed_30S.lmdb"), readonly=True, lock=False)
    with renv.begin() as txn:
        rkeys = pickle.loads(txn.get(b"__keys__"))
        n_entries = renv.stat()["entries"]
    senv, smeta, sindex = open_ours(args.ours_ssl)
    skeys = [r["key"] for r in sindex]
    scommon = sorted(set(rkeys) & set(skeys))
    released_files = Counter(k.rsplit("_", 1)[0] for k in rkeys)
    our_files = Counter(k.rsplit("_", 1)[0] for k in skeys)
    rep["ssl"] = {
        "released_len_keys": len(rkeys), "released_lmdb_entries_minus_keys": n_entries - 1,
        "released_duplicate_keys": len(rkeys) - len(set(rkeys)), "ours_n": len(skeys),
        "common": len(scommon), "n_only_ours": len(set(skeys) - set(rkeys)),
        "n_only_released": len(set(rkeys) - set(skeys)),
        "only_ours": sorted(set(skeys) - set(rkeys))[:50], "only_released": sorted(set(rkeys) - set(skeys))[:50],
        "released_files": len(released_files), "our_files": len(our_files),
        "per_file_count_mismatch": sorted(f for f in set(released_files) | set(our_files)
                                          if released_files[f] != our_files[f])[:50],
    }
    if args.lmdb_log and os.path.exists(args.lmdb_log):
        log = Path(args.lmdb_log).read_text(errors="replace").splitlines()
        rep["ssl"]["released_log"] = {
            "skipping": [ln for ln in log if ln.startswith("Skipping")],
            "insufficient": [ln for ln in log if ln.startswith("Insufficient")],
            "failed": [ln for ln in log if ln.startswith("Failed") or ln.startswith("Error loading")],
            "stored_line": [ln for ln in log if ln.startswith("Stored ")],
        }
    pick = sorted(np.random.default_rng(args.seed).choice(len(scommon), min(args.n, len(scommon)),
                                                          replace=False).tolist())
    sd = []
    with renv.begin() as rt, senv.begin() as st:
        for i in pick:
            k = scommon[i]
            ref = pickle.loads(rt.get(k.encode()))
            got = np.frombuffer(st.get(k.encode()), dtype=smeta["dtype"]).reshape(smeta["shape"])
            if ref.shape != got.shape:
                raise SystemExit(f"{k}: shape {ref.shape} vs {got.shape}")
            sd.append((k, *rel_diff(ref, got)))
    rep["ssl_values"] = {"n": len(sd), "released_dtype": str(ref.dtype), "max_abs": max(d[1] for d in sd),
                         "max_rel": max(d[2] for d in sd), "n_rel_over_tol": sum(d[2] > REL_TOL for d in sd),
                         "worst": sorted(sd, key=lambda d: -d[2])[:5]}
    np.save(out / "ssl_rel_diffs.npy", np.array([d[2] for d in sd]))

    # --- verdict per draft number
    t = by["test"]
    checks = {
        "326,993 eval windows": (len(rel), DRAFT["n_eval_windows"]),
        "252 test positives": (t["pos"], DRAFT["test_pos"]),
        "206 test -s- files": (t["s_files"], DRAFT["test_s_files"]),
        "114 truly ictal test grid windows": (ictal, DRAFT["test_ictal_grid"]),
        "70 of them labelled 0": (lab0, DRAFT["test_ictal_grid_labelled_0"]),
        "chb12, chb13, chb17 absent from eval": (
            sorted({"chb12", "chb13", "chb17"} - set(rep["released_eval"]["cases"])), DRAFT["eval_cases_absent"]),
        "81,993 SSL windows": (len(rkeys), DRAFT["n_ssl_windows"]),
    }
    rep["checks"] = {k: {"released": a, "draft": b, "match": a == b} for k, (a, b) in checks.items()}
    exact = (all(c["match"] for c in rep["checks"].values())
             and rep["eval_keys"]["n_only_ours"] == rep["eval_keys"]["n_only_released"] == 0
             and rep["eval_keys"]["label_mismatch"] == rep["eval_keys"]["split_mismatch"] == 0
             and rep["ssl"]["n_only_ours"] == rep["ssl"]["n_only_released"] == 0)
    values_ok = rep["eval_values"]["max_rel"] <= REL_TOL and rep["ssl_values"]["max_rel"] <= REL_TOL
    rep["verdict"] = {"counts_exact": exact, "values_within_tol": values_ok,
                      "draft_reproduces_claims_stand": exact and values_ok}
    (out / "e1_compare.json").write_text(json.dumps(rep, indent=2, default=str))
    print(json.dumps({k: rep[k] for k in ("checks", "verdict", "eval_keys", "eval_values", "ssl_values")},
                     indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
