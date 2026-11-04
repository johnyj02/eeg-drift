"""Pins the corrected protocol (notes/decisions.md D17, D18)."""

import json
from pathlib import Path

import pytest
import torch

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "data" / "lmdb" / "chbmit_eval10"


def test_overlap_label_rule():
    from eegdrift.data.chbmit import overlap_label

    sz = {"f": [[1000, 2000]]}
    rec = lambda start, n=2560: {"file": "f", "start": start, "n_samples": n}  # noqa: E731
    assert overlap_label(rec(0), sz) == 1             # contains the onset
    assert overlap_label(rec(1100, 500), sz) == 1     # inside the seizure, no start/end in it
    assert overlap_label(rec(2000), sz) == 0          # starts at the (exclusive) end
    assert overlap_label(rec(0, 1000), sz) == 0       # ends at the onset
    assert overlap_label({"file": "g", "start": 0, "n_samples": 2560}, sz) == 0


def test_seizure_table_matches_physionet():
    table = json.loads((ROOT / "configs" / "chbmit_seizures.json").read_text())
    assert sum(len(v) for v in table.values()) == 198            # CHB-MIT's documented total
    assert table["chb01_03"] == [[2996 * 256, 3036 * 256]]       # true [onset, offset) samples


def test_lp_randinit_is_an_unadapted_random_encoder(registry):
    import yaml

    from eegdrift.arms import resolve

    cfg = yaml.safe_load((ROOT / "configs" / "adapt.yaml").read_text())
    arm = resolve("lp_randinit", cfg, registry, "biot")
    assert (arm.groups, arm.adapt, arm.init) == ((), False, "random")
    noise = resolve("first_noise", cfg, registry, "biot")
    assert noise.ssl_input == "noise" and noise.groups == resolve("first", cfg, registry, "biot").groups


def test_noise_control_matches_channel_stats_only():
    from eegdrift.study import noise_like

    x = torch.randn(64, 16, 30, 200) * torch.arange(1, 17).view(1, 16, 1, 1) + 5
    n = noise_like(x, 42)
    assert n.shape == x.shape and torch.equal(n, noise_like(x, 42))
    assert torch.allclose(n.std(dim=(0, 2, 3)), x.std(dim=(0, 2, 3)), rtol=0.02)
    assert abs(float(torch.corrcoef(torch.stack([n.flatten(), x.flatten()]))[0, 1])) < 0.01


def test_jobspec_passes_labels():
    from jobspec import JobSpec

    spec = JobSpec.build("arms", "biot", "chbmit", arms=["lp"], seeds=[42], split="rot0",
                         labels="overlap")
    assert spec.hyperparameters["labels"] == "overlap" and "-rot0" in spec.name


@pytest.mark.skipif(not PILOT.exists(), reason="needs the pilot stores in data/lmdb")
def test_overlap_eval_drops_duplicates_outside_train(root, tmp_path):
    from eegdrift.data.chbmit import overlap_label
    from eegdrift.data.store import LocalStore
    from eegdrift.data.windows import WindowStore
    from eegdrift.study import Context, load_eval

    def ev(labels):
        ctx = Context(root=root, data_root=root / "data" / "lmdb", out=tmp_path,
                      artifacts=LocalStore(tmp_path / "a"), device=torch.device("cpu"), smoke=False,
                      log=lambda *_: None, overrides={"labels": labels} if labels else {})
        return load_eval(ctx, "chbmit", "rot1")

    up, ov = ev(""), ev("overlap")
    assert (up.labels, ov.labels) == ("upstream", "overlap") and up.hash != ov.hash
    assert all("-grid-" in t["key"] for t in ov.test_index)
    store = WindowStore(str(PILOT))
    table = json.loads((root / "configs" / "chbmit_seizures.json").read_text())
    by_key = {r["key"]: r for r in store.index}
    want = torch.tensor([overlap_label(by_key[t["key"]], table) for t in ov.test_index])
    assert torch.equal(ov.splits["test"][1], want)
    assert len(ov.splits["train"][1]) == len(up.splits["train"][1])   # train keeps every window


@pytest.mark.skipif(not PILOT.exists(), reason="needs the pilot stores in data/lmdb")
def test_smoke_eval_keeps_positives(root, tmp_path):
    from eegdrift.data.store import LocalStore
    from eegdrift.study import Context, load_eval

    ctx = Context(root=root, data_root=root / "data" / "lmdb", out=tmp_path,
                  artifacts=LocalStore(tmp_path / "a"), device=torch.device("cpu"), smoke=True,
                  log=lambda *_: None, overrides={"labels": "overlap"})
    ev = load_eval(ctx, "chbmit", "rot3")
    assert all(int(ev.splits[p][1].sum()) > 0 for p in ("train", "val", "test"))


def test_step1_reading_rules():
    from read_step1 import d17, paired

    assert paired([5, 4, 6, 3.5, -1]) == "first term wins"          # mean 3.5, 4/5 positive
    assert paired([5, 4, 6, -3.5, -1]) == "no difference shown"     # only 3/5 positive
    assert paired([-5, -4, -6, -4, 1]) == "second term wins"
    assert d17([90, 89], [88, 88]) == "random features explain it"
    assert d17([95, 94, 96, 93, 80], [88, 88, 88, 88, 88]) == "SSL adds to random init"


def test_logit_scores_match_sigmoid_metrics_without_saturation():
    import numpy as np

    from eegdrift.probe import LOGIT_T, metrics

    rng = np.random.default_rng(0)
    y = (rng.random(2000) < 0.05).astype(int)
    logit = rng.normal(size=2000) * 3 + 2 * y
    prob = 1 / (1 + np.exp(-logit))
    a, b = metrics(y, logit, 2, LOGIT_T), metrics(y, prob, 2)
    assert all(abs(a[k] - b[k]) < 1e-9 for k in ("bal_acc", "roc_auc", "avg_precision"))
    # the failure the change fixes: float32 sigmoid of large logits ties at exactly 0
    big = (logit * 60).astype(np.float32)
    sat = torch.sigmoid(torch.from_numpy(big - 200)).numpy()
    assert metrics(y, big - 200, 2, LOGIT_T)["roc_auc"] > metrics(y, sat, 2)["roc_auc"]


def test_step2_rule_and_arm_names():
    from read_step2 import arm_of, d22

    assert d22([0.6, 0.7, 0.5, 0.4, -0.1]) == "no predictive value shown"   # mean 0.42 < 0.5
    assert d22([0.9, 0.7, 0.5, 0.6, -0.1]) == "design C predicts where to adapt"
    assert d22([0.9, 0.7, 0.5, -0.6, -0.1]) == "no predictive value shown"
    assert [arm_of("biot", g) for g in ("embed", "block00", "block02", "block03")] == \
        ["embed_only", "first_block", "single_b02", "last"]
    assert arm_of("cbramod", "block03") == "single_b03" and arm_of("cbramod", "block11") == "last"


def test_d19_three_way_rule():
    from read_step1 import d19

    assert d19([5, 4, 6, 3.5, -1]) == "the gain needs EEG data"
    assert d19([-4.4, 1.2, 10.1, -2.8, 5.5]) == "perturbation alone explains it"   # mean 1.9
    assert d19([-3.9, 30.3, 12.2, -10.7, -6.1]) == "unclear"                       # mean 4.4, 2/5


def test_cbramod_probe_reads_encoder_not_reconstruction_head(registry):
    import copy

    from torch import nn

    m = registry.build("cbramod", "pretrained")
    ref = copy.deepcopy(m.module).eval()
    ref.proj_out = nn.Identity()          # official CBraMod downstream practice
    m.module.eval()
    x = torch.randn(2, 16, 10, 200) / 10
    with torch.no_grad():
        assert torch.equal(m.features(x), ref(x))
        assert not torch.allclose(m.features(x), m.module(x))   # proj_out is NOT what the probe sees


def test_probe_backbone_mode_per_model(registry, root, tmp_path):
    from eegdrift.data.store import LocalStore
    from eegdrift.study import Context, probe_template

    ctx = Context(root=root, data_root=tmp_path, out=tmp_path, artifacts=LocalStore(tmp_path),
                  device=torch.device("cpu"), log=lambda *_: None)
    assert probe_template(ctx, "cbramod", "chbmit", 42, "rot0").backbone_mode == "eval"
    assert probe_template(ctx, "biot", "chbmit", 42, "rot0").backbone_mode == "train"   # as run


def test_backbone_mode_override_reaches_probe_and_job(root, tmp_path):
    from jobspec import JobSpec

    from eegdrift.data.store import LocalStore
    from eegdrift.study import Context, probe_template

    ctx = Context(root=root, data_root=tmp_path, out=tmp_path, artifacts=LocalStore(tmp_path),
                  device=torch.device("cpu"), log=lambda *_: None, overrides={"backbone_mode": "eval"})
    assert probe_template(ctx, "biot", "chbmit", 42, "rot0").backbone_mode == "eval"
    spec = JobSpec.build("arms", "biot", "chbmit", arms=["lp"], seeds=[42], split="rot0", backbone_mode="eval")
    assert spec.hyperparameters["backbone_mode"] == "eval"


def test_d24_reader_refuses_old_probe_records(tmp_path):
    import json

    from read_d24 import load

    d = tmp_path / "x" / "results"
    d.mkdir(parents=True)
    rec = {"smoke": False, "dataset": "chbmit", "run_tag": "S1M", "model": "biot", "arm": "lp",
           "split": "rot0", "seed": 42, "versions": {"probe": 3, "adapt": 3}, "eval_hash": "e",
           "labels": "overlap",
           "probes": {"linear": {"spec": {"backbone_mode": "train"}, "test_at_best": {"roc_auc": 0.6}}}}
    (d / "a.json").write_text(json.dumps(rec))
    with pytest.raises(SystemExit):
        load(str(tmp_path), "chbmit", {"S1M"})
    rec["versions"]["probe"], rec["probes"]["linear"]["spec"]["backbone_mode"] = 4, "eval"
    (d / "a.json").write_text(json.dumps(rec))
    assert load(str(tmp_path), "chbmit", {"S1M"})[("biot", "lp", "rot0", "linear")] == {42: 60.0}


def test_cluster_bootstrap_ci_covers_mean_and_widens_with_rotation_spread():
    import numpy as np
    from bootstrap_d24 import cluster_ci

    rng = np.random.default_rng(0)
    tight = [[1.0, 1.1, 0.9]] * 5
    wide = [[-5.0, -5.1, -4.9], [5.0, 5.1, 4.9], [0.0, 0.1, -0.1], [3.0, 3.0, 3.0], [-3.0, -3.0, -3.0]]
    m, lo, hi = cluster_ci(tight, rng)
    assert lo <= m <= hi and hi - lo < 0.3
    m2, lo2, hi2 = cluster_ci(wide, rng)
    assert lo2 <= m2 <= hi2 and hi2 - lo2 > 4


def test_probe_logs_history_and_proj_out_tap(registry):
    from dataclasses import replace

    from eegdrift.probe import ProbeSpec, parity_probe

    m = registry.build("cbramod", "pretrained")
    m.module.eval()                        # no dropout, so two forwards are comparable
    x = torch.randn(4, 16, 10, 200) / 10
    with torch.no_grad():
        assert torch.equal(m.features(x, "proj_out"), m.module(x))
    with pytest.raises(ValueError):
        registry.build("biot", "pretrained").features(torch.randn(2, 16, 2000), "proj_out")
    g = torch.Generator().manual_seed(0)
    data = {k: (torch.randn(n, 16, 10, 200, generator=g) * 30, torch.tensor([0, 1] * (n // 2)))
            for k, n in (("train", 8), ("val", 6), ("test", 6))}
    spec = ProbeSpec(model="cbramod", dataset="chbmit", variant="linear", seed=1, n_classes=2, window_s=10,
                     epochs=2, batch=4, backbone_mode="eval")
    res, _ = parity_probe(m, spec, data, torch.device("cpu"), log=lambda *_: None)
    assert len(res.history) == 2 and {"train_loss", "val", "val_loss", "test_plot_only"} <= set(res.history[0])
    res2, _ = parity_probe(registry.build("cbramod", "pretrained"), replace(spec, tap="proj_out"), data,
                           torch.device("cpu"), log=lambda *_: None)
    assert res2.history[0]["train_loss"] != res.history[0]["train_loss"]


def test_d25_options(registry, root, tmp_path):
    import yaml

    from eegdrift.arms import resolve
    from eegdrift.models.protocols import scale_input
    from sm_entry import parse_sets

    x = torch.randn(3, 16, 10, 200) * 50
    q = scale_input(x, 100.0, "q95").abs().reshape(3, 16, -1).kthvalue(1900, dim=-1).values
    assert torch.allclose(q, torch.ones_like(q), atol=1e-3)
    assert torch.equal(scale_input(x, 100.0), x / 100.0)
    assert parse_sets("input_norm=q95,ssl_seed=7") == {"input_norm": "q95", "ssl_seed": "7"}
    with pytest.raises(ValueError):
        parse_sets("ssl_sed=7")
    cfg = yaml.safe_load((ROOT / "configs" / "adapt.yaml").read_text())
    assert resolve("last_noise", cfg, registry, "biot").ssl_input == "noise"


@pytest.mark.skipif(not PILOT.exists(), reason="needs the pilot stores in data/lmdb")
def test_fold_and_ssl_seed_overrides(root, tmp_path):
    from eegdrift.data.store import LocalStore
    from eegdrift.study import Context, case_splits, load_eval, load_ssl

    def ctx(o):
        return Context(root=root, data_root=root / "data" / "lmdb", out=tmp_path,
                       artifacts=LocalStore(tmp_path / "a"), device=torch.device("cpu"), smoke=True,
                       log=lambda *_: None, overrides=o)
    base, other = ctx({}), ctx({"fold_seed": "7"})
    assert case_splits(base, "chbmit", "rot0") != case_splits(other, "chbmit", "rot0")
    assert load_eval(base, "chbmit", "rot0").hash != load_eval(other, "chbmit", "rot0").hash
    a, b = load_ssl(base, "chbmit", "rot0"), load_ssl(ctx({"ssl_seed": "99"}), "chbmit", "rot0")
    assert a.hash != b.hash and len(a.x) == len(b.x)
    ev = load_eval(base, "chbmit", "rot0")
    assert ev.val_index and len(ev.val_index) == len(ev.splits["val"][1])


def test_linear_z_probe_standardizes_with_train_stats(registry):
    from eegdrift.probe import ProbeSpec, Standardize, build_head, parity_probe

    m = registry.build("biot", "pretrained")
    g = torch.Generator().manual_seed(0)
    data = {k: (torch.randn(n, 16, 10, 200, generator=g) * 30, torch.tensor([0, 1] * (n // 2)))
            for k, n in (("train", 16), ("val", 8), ("test", 8))}
    spec = ProbeSpec(model="biot", dataset="chbmit", variant="linear_z", seed=1, n_classes=2, window_s=10,
                     epochs=1, batch=8, backbone_mode="eval")
    res, arrays = parity_probe(m, spec, data, torch.device("cpu"), log=lambda *_: None)
    assert res.head_params == 257 and "scores_best" in arrays
    head = build_head("biot", "linear_z", 2, 10)
    assert isinstance(head[0], Standardize)


def test_ft_probe_trains_a_copy_of_the_encoder(registry):
    """D27 'ft': the encoder is fine-tuned on a copy; the caller's encoder and the linear path stay unchanged."""
    from dataclasses import replace

    from eegdrift.probe import ProbeSpec, parity_probe

    m = registry.build("biot", "pretrained")
    before = [p.detach().clone() for p in m.encoder().parameters()]
    g = torch.Generator().manual_seed(0)
    data = {k: (torch.randn(n, 16, 10, 200, generator=g) * 30, torch.tensor([0, 1] * (n // 2)))
            for k, n in (("train", 16), ("val", 8), ("test", 8))}
    spec = ProbeSpec(model="biot", dataset="chbmit", variant="linear", seed=1, n_classes=2, window_s=10,
                     epochs=1, batch=8, backbone_mode="eval")
    lin1, _ = parity_probe(m, spec, data, torch.device("cpu"), log=lambda *_: None)
    ft, _ = parity_probe(m, replace(spec, variant="ft"), data, torch.device("cpu"), log=lambda *_: None)
    lin2, _ = parity_probe(m, spec, data, torch.device("cpu"), log=lambda *_: None)
    assert all(torch.equal(a, b) for a, b in zip(before, m.encoder().parameters(), strict=True))
    assert lin1.test_at_best == lin2.test_at_best and ft.head_params == lin1.head_params == 257
    assert ft.history[0]["train_loss"] != lin1.history[0]["train_loss"]   # the encoder did train


def test_siena_pub_split(root, tmp_path):
    from eegdrift.data.store import LocalStore
    from eegdrift.study import Context

    ctx = Context(root=root, data_root=tmp_path, out=tmp_path, artifacts=LocalStore(tmp_path),
                  device=torch.device("cpu"), log=lambda *_: None)
    pub = ctx.data_cfg["siena"]["pub_split"]
    assert pub["test"] == ["PN13", "PN14", "PN16", "PN17"] and not set(pub["test"]) & set(pub["val"])
