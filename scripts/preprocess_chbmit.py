#!/usr/bin/env python3
"""preprocess-chbmit: raw CHB-MIT EDF -> two window stores. Runs on the desktop (CPU).

    python scripts/preprocess_chbmit.py --root ~/dxdata/chbmit/1.0.0 --out ~/dxdata/lmdb --workers 64

Writes <out>/chbmit_ssl30/ and <out>/chbmit_eval10/ (LMDB, see data/windows.py) and
<out>/chbmit_preprocess_report.json. Verifies every raw file against PhysioNet's SHA256SUMS.txt
first and refuses to continue on a mismatch.

--extended (D25-E33a) writes <out>/chbmit_x_eval10/ and <out>/chbmit_x_preprocess_report.json
instead: the upstream file list plus every other chb01-chb24 EDF with all 16 channels by label
(chbmit.eval_files(extended=True)), same windows/labels/oversampling; the report adds n_present
per file, per-case counts and the EDFs left out.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from eegdrift.data import chbmit  # noqa: E402
from eegdrift.data.windows import WindowWriter  # noqa: E402


def _sha256(path: str) -> tuple[str, str]:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return path, h.hexdigest()


def verify(root: str, workers: int) -> dict:
    expected = {}
    for line in Path(root, "SHA256SUMS.txt").read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        expected[name.strip()] = digest
    edfs = {k: v for k, v in expected.items() if k.endswith(".edf")}
    with Pool(workers) as pool:
        got = dict(pool.map(_sha256, [os.path.join(root, k) for k in edfs]))
    bad = [k for k, v in edfs.items() if got[os.path.join(root, k)] != v]
    if bad:
        raise SystemExit(f"SHA256 MISMATCH on {len(bad)} files, e.g. {bad[:3]}")
    return {"verified_edf_files": len(edfs)}


def _ssl_job(args):
    path, stage = args
    records, x, stats = chbmit.ssl_windows(path)
    out = os.path.join(stage, os.path.basename(path) + ".ssl.npy")
    np.save(out, x)
    return records, out, stats


def _eval_job(args):
    path, seizures, stage, filtered = args
    records, x, stats = chbmit.eval_windows(path, seizures, filtered=filtered)
    out = os.path.join(stage, os.path.basename(path) + ".eval.npy")
    np.save(out, x)
    return records, out, stats


def build(store_path: Path, shape, results, description: str, extra: dict) -> int:
    writer = WindowWriter(store_path, "float32", shape, description)
    n = 0
    for records, npy, _stats in sorted(results, key=lambda r: r[1]):
        x = np.load(npy)
        n += writer.put_many(zip(records, x, strict=True))
        os.remove(npy)
    writer.close(extra)
    return n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=32)
    ap.add_argument("--skip-verify", action="store_true")
    ap.add_argument("--eval-only", action="store_true", help="build only the eval store")
    ap.add_argument("--filtered", action="store_true",
                    help="eval windows with the preprocessing the PAPER describes (R4)")
    ap.add_argument("--extended", action="store_true",
                    help="D25-E33a: also every other chb01-chb24 EDF with all 16 channels by label")
    args = ap.parse_args()
    root, out = os.path.expanduser(args.root), Path(os.path.expanduser(args.out))
    out.mkdir(parents=True, exist_ok=True)
    report: dict = {"root": root, "started": time.strftime("%Y-%m-%dT%H:%M:%S")}
    if not args.skip_verify:
        report.update(verify(root, args.workers))
        print("sha256 OK:", report["verified_edf_files"], "files", flush=True)

    stage = tempfile.mkdtemp(prefix="dx-chbmit-", dir=str(out))
    with Pool(args.workers) as pool:
        ssl = ([] if args.eval_only else
               pool.map(_ssl_job, [(p, stage) for p in chbmit.ssl_files(root)], chunksize=1))
        summaries = {}
        jobs = []
        for p in chbmit.eval_files(root, extended=args.extended):
            case = chbmit.case_of(p)
            if case not in summaries:
                summaries[case] = chbmit.parse_summary(os.path.join(root, case, f"{case}-summary.txt"))
            jobs.append((p, summaries[case].get(os.path.basename(p), []), stage, args.filtered))
        ev = pool.map(_eval_job, jobs, chunksize=1)

    n_ssl = 0 if args.eval_only else build(
        out / "chbmit_ssl30", (16, 30, 200), ssl,
        "CHB-MIT SSL windows, upstream make_CHBMIT_for_pretraining behaviour, uV",
        {"scale_parity": 700.0, "fs": 200, "window_s": 30})
    desc = ("CHB-MIT eval windows, upstream windows+labels, PAPER-DESCRIBED preprocessing "
            "(MNE resample 200 Hz, 0.3-75 Hz band-pass, 60 Hz notch), uV" if args.filtered else
            "CHB-MIT eval windows, upstream process1+process2+loader behaviour, uV, "
            "FFT-resampled 2560->2000")
    extra = {"scale_parity": 100.0, "fs": 200, "window_s": 10, "filtered": args.filtered}
    if args.extended:
        desc += "; EXTENDED (D25-E33a): + every other chb01-chb24 EDF with all 16 channels by label"
        extra["file_list"] = "upstream+label16"
    n_eval = build(out / ("chbmit_x_eval10" if args.extended else "chbmit_eval10"), (16, 2000), ev,
                   desc, extra)
    os.rmdir(stage)

    eval_records = [r for recs, _, _ in ev for r in recs]
    by_split: dict = {}
    by_case: dict = {}
    for r in eval_records:
        for d in (by_split.setdefault(r["split"], {"n": 0, "pos": 0, "add": 0}),
                  by_case.setdefault(r["case"], {"n": 0, "pos": 0, "add": 0})):
            d["n"] += 1
            d["pos"] += r["label"]
            d["add"] += r["kind"] != "grid"
    report.update({
        "n_ssl_windows": n_ssl, "paper_Ntotal_chbmit": 4174,
        "ssl_files": len(ssl), "ssl_skipped": [s for *_, s in ssl if s["status"] != "ok"],
        "n_eval_windows": n_eval, "eval_files": len(ev), "eval_by_split": by_split,
        "eval_short_stretched": sum(s["n_short_stretched"] for *_, s in ev),
        "eval_skipped": [s for *_, s in ev if s["status"] != "ok"],
        "finished": time.strftime("%Y-%m-%dT%H:%M:%S"),
    })
    if args.extended:
        upstream = {os.path.basename(p) for p in chbmit.eval_files(root)}
        used = {os.path.basename(j[0]) for j in jobs}
        report.update({
            "eval_by_case": dict(sorted(by_case.items())),
            "eval_file_stats": [dict(s, added=s["file"] + ".edf" not in upstream) for *_, s in ev],
            "eval_left_out": [{"file": os.path.basename(p), "n_present": chbmit.n_present_by_label(p)}
                              for p in chbmit.all_edfs(root) if os.path.basename(p) not in used],
        })
    name = "chbmit_x_preprocess_report.json" if args.extended else "chbmit_preprocess_report.json"
    (out / name).write_text(json.dumps(report, indent=2))
    print(json.dumps({k: v for k, v in report.items() if not k.endswith(("skipped", "stats"))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
