#!/usr/bin/env python3
"""preprocess-siena: raw Siena Scalp EEG EDF -> three window stores. Runs on the desktop (CPU).

    python scripts/preprocess_siena.py --root ~/dxdata/siena/1.0.0 --out ~/dxdata/lmdb --dry-run
    python scripts/preprocess_siena.py --root ~/dxdata/siena/1.0.0 --out ~/dxdata/lmdb --workers 8

Writes <out>/siena/{siena_ssl30, siena_eval10}, <out>/siena_filt/siena_eval10 (same keys as the
unfiltered eval store), <out>/siena_seizures.json and <out>/siena_preprocess_report.json.
Verifies every EDF against SHA256SUMS.txt and refuses to continue if the recomputed seizure
table differs from configs/siena_seizures.json. --dry-run reads only EDF headers and the
Seizures-list files and prints the window counts the full run must reproduce.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from preprocess_chbmit import build, verify  # noqa: E402

from eegdrift.data import siena  # noqa: E402

# notes/siena-spec.md §6, from header durations and the parsed table (no signal read)
EXPECTED = {"files": 41, "seizures": 47, "grid": 50749, "grid_pos": 329, "add": 613}


def edf_path(root: str, stem: str) -> str:
    return os.path.join(root, stem[:4], f"{stem}.edf")


def counts(records: list[dict]) -> dict:
    grid = [r for r in records if r["kind"] == "grid"]
    add = [r for r in records if r["kind"] != "grid"]
    return {"grid": len(grid), "grid_pos": sum(r["label"] for r in grid),
            "add": len(add), "add_pos": sum(r["label"] for r in add)}


def by_subject(rows: list[tuple[str, list[dict], dict]], table: dict) -> dict:
    """rows: (stem, eval records, extra per-file counts) -> per-subject sums plus "total"."""
    out: dict = {}
    for stem, recs, extra in rows:
        for d in (out.setdefault(stem[:4], {}), out.setdefault("total", {})):
            for k, v in {"files": 1, "seizures": len(table[stem]), **counts(recs), **extra}.items():
                d[k] = d.get(k, 0) + v
    return dict(sorted(out.items()))


def dry_run(root: str, table: dict) -> dict:
    """Header-only: channel matching, sfreq, windows and labels, SSL windows before rejection."""
    import mne  # noqa: PLC0415

    rows = []
    for stem in siena.RECORDS:
        raw = mne.io.read_raw_edf(edf_path(root, stem), preload=False, verbose="ERROR")
        if raw.info["sfreq"] != siena.FS_NATIVE:
            raise SystemExit(f"{stem}: sfreq {raw.info['sfreq']}")
        siena.electrode_indices(raw.ch_names)   # raises on a missing or duplicate electrode
        seconds = raw.n_times // siena.FS_NATIVE
        ssl_max = seconds // 30 - 4 if seconds >= 300 else 0   # cut_ssl before the 700 uV rejection
        rows.append((stem, siena.windows(stem, raw.n_times, table), {"ssl_max": ssl_max, "hours": seconds / 3600}))
    return by_subject(rows, table)


def _job(args):
    path, table, stage = args
    ssl_recs, ssl_x, recs, ev, filt, stats = siena.process(path, table)
    base = os.path.join(stage, os.path.basename(path))
    for suffix, x in ((".ssl.npy", ssl_x), (".eval.npy", ev), (".filt.npy", filt)):
        np.save(base + suffix, x)
    return ssl_recs, recs, base, stats


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="the directory holding SHA256SUMS.txt")
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--skip-verify", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="headers + annotations only; print counts")
    args = ap.parse_args()
    root, out = os.path.expanduser(args.root), Path(os.path.expanduser(args.out))
    out.mkdir(parents=True, exist_ok=True)
    report: dict = {"root": root, "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "expected": EXPECTED}

    table = siena.seizure_table(root)
    (out / "siena_seizures.json").write_text(json.dumps(table, indent=0))
    committed = REPO / "configs" / "siena_seizures.json"
    same = committed.exists() and json.loads(committed.read_text()) == table
    print(f"seizure table: {sum(len(v) for v in table.values())} seizures in {len(table)} files, "
          f"wrote {out / 'siena_seizures.json'}; matches {committed.name}: {same}", flush=True)
    if args.dry_run:
        subj = dry_run(root, table)
        cols = list(subj["total"])
        print("subject " + " ".join(f"{c:>8}" for c in cols))
        for name, d in subj.items():
            print(f"{name:7} " + " ".join(f"{d[c]:8.2f}" if c == "hours" else f"{d[c]:8d}" for c in cols))
        print("expected", EXPECTED)
        return 0
    if not same:
        raise SystemExit(f"seizure table differs from {committed}; review and commit "
                         f"{out / 'siena_seizures.json'} first")
    if not args.skip_verify:
        report.update(verify(root, args.workers))
        print("sha256 OK:", report["verified_edf_files"], "files", flush=True)

    stage = tempfile.mkdtemp(prefix="dx-siena-", dir=str(out))
    with Pool(args.workers) as pool:   # ~PN01-1 (13.5 h) peaks at several GB per worker
        res = pool.map(_job, [(edf_path(root, s), table, stage) for s in siena.RECORDS], chunksize=1)
    for d in ("siena", "siena_filt"):   # WindowWriter's lmdb.open makes only the last level
        (out / d).mkdir(exist_ok=True)
    meta = {"fs_native": siena.FS_NATIVE, "fs": siena.FS, "notch": siena.NOTCH}
    n_ssl = build(out / "siena" / "siena_ssl30", (16, 30, 200),
                  [(ssl, base + ".ssl.npy", st) for ssl, _, base, st in res],
                  "Siena SSL windows: bipolar, MNE resample 200 Hz, 0.3-75 Hz, 50 Hz notch, "
                  "chbmit.cut_ssl, uV",
                  {**meta, "scale_parity": 700.0, "window_s": 30, "filtered": True})
    n_eval = build(out / "siena" / "siena_eval10", (16, 2000),
                   [(recs, base + ".eval.npy", st) for _, recs, base, st in res],
                   "Siena eval windows: bipolar, unfiltered 512 Hz, FFT-resampled 5120->2000 per "
                   "window, overlap labels, uV",
                   {**meta, "scale_parity": 100.0, "window_s": 10, "filtered": False})
    n_filt = build(out / "siena_filt" / "siena_eval10", (16, 2000),
                   [(recs, base + ".filt.npy", st) for _, recs, base, st in res],
                   "Siena eval windows: bipolar, MNE resample 200 Hz, 0.3-75 Hz, 50 Hz notch, "
                   "same keys as siena/siena_eval10, overlap labels, uV",
                   {**meta, "scale_parity": 100.0, "window_s": 10, "filtered": True})
    os.rmdir(stage)

    subj = by_subject([(st["file"], recs, {"ssl_windows": st["ssl"].get("n_windows", 0),
                                           "ssl_kept": len(ssl)}) for ssl, recs, _, st in res], table)
    flags = [{"file": st["file"], "pair": siena.BIOT_CHANNELS[i], "rms_uv": rms, "hf_share": hf,
              "lp_ratio": lp}
             for *_, st in res for i, (rms, hf, lp) in enumerate(zip(
                 st["qc"]["rms_uv"], st["qc"]["hf_share"], st["qc"]["lp_ratio"], strict=True))
             if hf > 0.5 or rms < 1.0 or lp < 1e-3]   # ponytail: fixed thresholds, a human reads the full QC
    report.update({"n_ssl_windows": n_ssl, "n_eval_windows": n_eval, "n_eval_filt_windows": n_filt,
                   "got": subj["total"], "by_subject": subj, "qc_flags": flags,
                   "per_file": [st for *_, st in res], "finished": time.strftime("%Y-%m-%dT%H:%M:%S")})
    (out / "siena_preprocess_report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps({k: report[k] for k in ("expected", "got", "n_ssl_windows", "n_eval_windows",
                                             "n_eval_filt_windows", "qc_flags")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
