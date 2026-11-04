from pathlib import Path

import numpy as np
import pytest

from eegdrift.data.edf import BIOT_CHANNELS, channel_indices, select_bipolar
from eegdrift.data.index import paper_split, rotations, subject_of

# Verbatim from github.com/ycq091044/BIOT README ("The 16 channels are ...").
README_ORDER = ('"FP1-F7", "F7-T7", "T7-P7", "P7-O1", "FP2-F8", "F8-T8", "T8-P8", "P8-O2", '
                '"FP1-F3", "F3-C3", "C3-P3", "P3-O1", "FP2-F4", "F4-C4", "C4-P4", "P4-O2"')


def test_channel_order_is_biot_readme_order():
    assert BIOT_CHANNELS == tuple(s.strip().strip('"') for s in README_ORDER.split(","))


def test_duplicate_labels_take_first_occurrence():
    names = ["FP1-F7", "T8-P8-0", "X", "T8-P8-1"]
    idx = channel_indices(names)
    assert idx[BIOT_CHANNELS.index("T8-P8")] == 1
    sig, n = select_bipolar(names, np.arange(8, dtype=float).reshape(4, 2))
    assert n == 2 and sig.shape == (16, 2) and sig[BIOT_CHANNELS.index("F7-T7")].sum() == 0


def test_identity_facts():
    assert subject_of("chb21") == "chb01" and subject_of("chb05") == "chb05"
    assert paper_split("chb21") == "val" and paper_split("chb24") == "test"
    assert paper_split("chb01") == "train"


def test_rotations_coassign_and_cover():
    cases = [f"chb{i:02d}" for i in range(1, 25) if i not in (12, 13, 17)]
    rots = rotations(cases)
    tested = set()
    for rot in rots:
        assert rot["chb01"] == rot["chb21"], "same subject split apart"
        tested |= {c for c, s in rot.items() if s == "test"}
        assert set(rot.values()) == {"train", "val", "test"}
    assert tested == set(cases), "every case is a test case in exactly one rotation"


SUMMARY = Path(__file__).resolve().parents[1] / "data/chbmit_probe/chb01/chb01-summary.txt"


@pytest.mark.skipif(not SUMMARY.exists(), reason="needs data/chbmit_probe (scripts download)")
def test_summary_parse_matches_upstream_index_convention():
    from eegdrift.data.chbmit import parse_summary

    s = parse_summary(str(SUMMARY))
    assert s["chb01_03.edf"][0].start == 2996 * 256 - 1
    assert s["chb01_03.edf"][0].end == 3036 * 256 - 1
    assert s["chb01_01.edf"] == []


def test_window_store_roundtrip(tmp_path):
    from eegdrift.data.windows import WindowStore, WindowWriter

    w = WindowWriter(tmp_path / "s", "float32", (2, 3), "test")
    w.put_many(({"key": f"k{i}", "split": "train", "label": i % 2}, np.full((2, 3), i, np.float32))
               for i in range(4))
    w.close()
    s = WindowStore(str(tmp_path / "s"))
    assert len(s) == 4 and s.get(3)[0, 0] == 3 and s.select(label=1) == [1, 3]
    with pytest.raises(FileExistsError):
        WindowWriter(tmp_path / "s", "float32", (2, 3), "again")
