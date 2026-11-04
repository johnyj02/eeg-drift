"""D25-E33a: the extended CHB-MIT eval file list leaves the default (upstream) list untouched."""

import hashlib
import os

from eegdrift.data import chbmit

EXTRA = ["chb02/chb02_16+.edf", "chb17/chb17a_03.edf", "chb17/chb17c_13.edf"]


def _tree(tmp_path):
    for c in range(1, 25):
        (tmp_path / f"chb{c:02d}").mkdir()
        for n in range(1, 100):
            (tmp_path / f"chb{c:02d}" / f"chb{c:02d}_{n:02d}.edf").touch()
    for rel in EXTRA:
        (tmp_path / rel).touch()
    return str(tmp_path)


def _digest(files, root):
    return hashlib.sha256("\n".join(os.path.relpath(p, root) for p in files).encode()).hexdigest()


def test_default_list_unchanged(tmp_path, monkeypatch):
    monkeypatch.setattr(chbmit, "n_present_by_label", lambda p: 1 / 0)   # default never reads headers
    root = _tree(tmp_path)
    files = chbmit.eval_files(root)
    assert len(files) == 882
    assert _digest(files, root) == "fe5dbe125377ab33888f993e3e4e033ada9a7add91843513f5008b33f557b640"


def test_extended_is_superset(tmp_path, monkeypatch):
    root = _tree(tmp_path)
    missing = {"chb12_27.edf", "chb12_28.edf", "chb12_29.edf"}   # referential montage: 0/16
    monkeypatch.setattr(chbmit, "n_present_by_label", lambda p: 0 if os.path.basename(p) in missing else 16)
    default, ext = chbmit.eval_files(root), chbmit.eval_files(root, extended=True)
    assert ext[:len(default)] == default and len(set(ext)) == len(ext)
    names = {os.path.basename(p) for p in ext}
    assert {"chb02_16+.edf", "chb12_01.edf", "chb13_01.edf", "chb17a_03.edf", "chb24_02.edf"} <= names
    assert not names & missing
    assert len(ext) == 24 * 99 + len(EXTRA) - len(missing)


def test_chbmit_x_config(root):
    import yaml

    cfg = yaml.safe_load((root / "configs/data.yaml").read_text())
    x, base = cfg["chbmit_x"], cfg["chbmit"]
    assert x["eval_store"] == "chbmit_x_eval10" and base["eval_store"] == "chbmit_eval10"
    x.pop("eval_store"), base.pop("eval_store")
    assert x == base
    # labels=overlap reads configs/<dataset>_seizures.json; the CHB-MIT table already covers chb01-chb24
    cfgs = root / "configs"
    assert (cfgs / "chbmit_x_seizures.json").read_bytes() == (cfgs / "chbmit_seizures.json").read_bytes()
