"""Siena Scalp EEG pipeline (notes/siena-spec.md §9, decisions D21). No raw data needed."""

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
import torch

from eegdrift.data import siena

ROOT = Path(__file__).resolve().parents[1]
TABLE = json.loads((ROOT / "configs" / "siena_seizures.json").read_text())


def test_pairs_follow_biot_order_with_old_names():
    assert siena.PAIRS[1] == ("F7", "T3") and siena.PAIRS[6] == ("T4", "T6")
    assert len(siena.PAIRS) == 16 and len(siena.ELECTRODES) == 16


def test_electrodes_match_by_label():
    names = ["EEG Fp1", "EKG 1", *(f"EEG {e.title()}" for e in siena.ELECTRODES[1:])]
    idx = siena.electrode_indices(names)
    assert idx[0] == 0 and idx[1] == 2
    assert siena.norm("EEG FP2") == siena.norm("EEG Fp2  ") == "FP2"
    with pytest.raises(ValueError, match="FP1: 0"):
        siena.electrode_indices(names[1:])
    with pytest.raises(ValueError, match="2 matches"):
        siena.electrode_indices([*names, "EEG FP1"])


def test_time_and_name_parsing():
    assert siena.clock_s("1 6.49.25") == 16 * 3600 + 49 * 60 + 25
    assert siena.clock_s(" 16:13.23") == 16 * 3600 + 13 * 60 + 23
    assert siena.clock_s("11.41.04 opure 11.40.43") == 11 * 3600 + 41 * 60 + 4
    assert siena.file_stem(" PNO6-1.edf ") == "PN06-1" and siena.file_stem("PN01.edf") == "PN01-1"


def test_parse_list_carries_file_name_and_short_keys(tmp_path):
    txt = tmp_path / "Seizures-list-PN01.txt"
    txt.write_bytes(b"File name: PN01.edf\r\nRegistration start time: 19.00.44\r\n\r\nSeizure n 1\r\n"
                    b"Start time: 21:51:02\r\nEnd time: 21.51.56\r\n\r\nSeizure n 2 \r\n"
                    b"Start time: 07.53.17\r\nEnd time: 07.54.31")
    assert siena.parse_list(txt) == [("PN01-1", 78662, 78716), ("PN01-1", 28397, 28471)]


def test_committed_seizure_table():
    assert tuple(TABLE) == tuple(sorted(siena.RECORDS))
    assert sum(len(v) for v in TABLE.values()) == 47
    assert sum(b - a for v in TABLE.values() for a, b in v) == 2868 * 512
    s = {k: [[a // 512, b // 512] for a, b in v] for k, v in TABLE.items()}
    assert all(a % 512 == 0 and b % 512 == 0 for v in TABLE.values() for a, b in v)   # whole seconds
    assert s["PN14-3"] == [[6740, 6781]]      # EDF header origin, not the txt's 16.17.45
    assert s["PN00-3"] == [[765, 825]]        # TIME_FIX end 18.29.29
    assert s["PN10-2"] == [[7798, 7849]]      # later of the two ends
    assert s["PN10-3"] == [[7835, 7904]]      # earlier (clinical) onset
    assert s["PN01-1"][1][0] == 46353         # after midnight


def test_windows_grid_add_and_labels():
    table = {"PN99-1": [[100 * 512, 130 * 512]]}
    recs = siena.windows("PN99-1", 125 * 512 + 7, {"PN99-1": [[100 * 512, 120 * 512]]})
    grid = [r for r in recs if r["kind"] == "grid"]
    assert len(grid) == 12 and grid[-1]["start"] == 110 * 512          # last full window
    assert [r["start"] // 512 for r in recs if r["kind"] == "add0"] == [99, 104, 109, 114]
    assert [r["start"] // 512 for r in grid if r["label"]] == [100, 110]
    assert all(r["split"] is None and r["subject"] == "PN99" for r in recs)
    recs = siena.windows("PN99-1", 200 * 512, table)
    assert [r["start"] // 512 for r in recs if r["kind"] == "add0"] == [99, 104, 109, 114, 119, 124, 129]
    assert recs[-1]["label"] == 1 and len({r["key"] for r in recs}) == len(recs)


def test_cut_ssl_keeps_chbmit_output():
    """Pins chbmit.cut_ssl (moved out of ssl_windows for Siena) to the pre-refactor output:
    the hash was computed with the original inline block on this exact input."""
    from eegdrift.data.chbmit import cut_ssl

    x = np.random.default_rng(7).normal(0, 50, (16, 200 * 917)).astype(np.float32)
    x[2] = 0
    x[9, 200 * 300] = 701.0
    x[4, 200 * 500] = -699.0
    recs, segs, stats = cut_ssl(x, "chb21_05", "chb21")
    assert stats == {"status": "ok", "n_windows": 26, "n_kept": 25} and recs[0]["subject"] == "chb01"
    digest = hashlib.sha256(json.dumps(recs).encode() + segs.tobytes()).hexdigest()
    assert digest == "45e06fdb04bf25fdb7d6d8894d360d4637763956211e74f8b45be74769580461"
    assert cut_ssl(x[:, :200 * 299], "a", "chb01")[2]["status"] == "skipped: 299s < 300s"


def test_study_has_no_paper_split_and_overlap_only(root, tmp_path):
    from eegdrift.data.store import LocalStore
    from eegdrift.data.windows import WindowWriter
    from eegdrift.study import Context, case_splits, load_eval

    w = WindowWriter(tmp_path / "siena_eval10", "float32", (16, 2000), "test")
    w.put_many((r, np.zeros((16, 2000), np.float32)) for stem in ("PN00-1", "PN01-1")
               for r in siena.windows(stem, 30 * 512, TABLE))
    w.close()

    def ctx(**overrides):
        return Context(root=root, data_root=tmp_path, out=tmp_path / "o",
                       artifacts=LocalStore(tmp_path / "a"), device=torch.device("cpu"),
                       log=lambda *_: None, overrides=overrides)

    with pytest.raises(ValueError, match="no paper split"):
        case_splits(ctx(), "siena", "paper")
    with pytest.raises(ValueError, match="overlap only"):
        load_eval(ctx(labels="upstream"), "siena", "rot0")
    assert set(case_splits(ctx(), "siena", "rot0")) == {"PN00", "PN01"}


def test_jobspec_short_name():
    from jobspec import JobSpec

    spec = JobSpec.build("arms", "biot", "siena", arms=["lp"], seeds=[42], split="rot0",
                         labels="overlap")
    assert "-arms-biot-sie-rot0" in spec.name and spec.inputs["data"].endswith("/lmdb/siena/")


def test_full_run_builds_stores_into_fresh_out_and_flags_low_pass(tmp_path, monkeypatch):
    """main() end to end on one fake 400 s file: the store parents must be created (the first
    build() used to crash after all the processing), and a low-passed pair is in qc_flags."""
    import sys

    import preprocess_siena
    from scipy.signal import butter, sosfilt

    from eegdrift.data.windows import WindowStore

    rng = np.random.default_rng(0)
    sig = sosfilt(butter(4, 40, fs=512, output="sos"), rng.normal(0, 20, (16, 400 * 512))).astype(np.float32)
    sig[3] = sosfilt(butter(4, 10, fs=512, output="sos"), rng.normal(0, 20, 400 * 512))   # white noise
    # is flatter than EEG: 15 Hz order 4 gives lp_ratio ~1e-4 on PN00-1 but 1.0e-3 here

    class SerialPool:   # Pool workers would not see the monkeypatches
        def __init__(self, _n):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass

        def map(self, fn, items, chunksize=1):
            return [fn(i) for i in items]

    monkeypatch.setattr(siena, "RECORDS", ["PN00-1"])
    monkeypatch.setattr(siena, "seizure_table", lambda _root: TABLE)
    monkeypatch.setattr(siena, "read_bipolar", lambda _path: sig)
    monkeypatch.setattr(preprocess_siena, "Pool", SerialPool)
    out = tmp_path / "fresh" / "lmdb"
    monkeypatch.setattr(sys, "argv", ["x", "--root", str(tmp_path), "--out", str(out), "--skip-verify"])
    assert preprocess_siena.main() == 0

    ev, filt, ssl = (WindowStore(str(out / p)) for p in
                     ("siena/siena_eval10", "siena_filt/siena_eval10", "siena/siena_ssl30"))
    assert len(ssl.index) > 0 and [r["key"] for r in ev.index] == [r["key"] for r in filt.index] != []
    report = json.loads((out / "siena_preprocess_report.json").read_text())
    assert [f["pair"] for f in report["qc_flags"]] == [siena.BIOT_CHANNELS[3]]
    assert not list(out.glob("dx-siena-*"))
