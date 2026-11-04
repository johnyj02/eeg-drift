"""Pins the fixes from the 2026-10-15 pre-submission code review."""

from pathlib import Path

import numpy as np
import pytest
import torch

from eegdrift.adapt import seed_everything
from eegdrift.models._ckpt import checkpointing
from eegdrift.models.protocols import set_trainable
from eegdrift.objectives import objective_for

ROOT = Path(__file__).resolve().parents[1]


def _grads(registry, name: str, ckpt: bool) -> dict[str, torch.Tensor]:
    seed_everything(0)
    m = registry.build(name)
    set_trainable(m, list(m.groups))
    m.module.train()                       # dropout ON: the RNG replay is what is under test
    x = torch.randn(3, 16, 30, 200) / 100
    seed_everything(1)
    with checkpointing(m.checkpoint_units() if ckpt else []):
        objective_for(m).loss(m, x).backward()
    return {n: p.grad.clone() for n, p in m.module.named_parameters() if p.grad is not None}


@pytest.mark.parametrize("name", ["biot", "cbramod"])
def test_checkpointing_leaves_gradients_unchanged(registry, name):
    plain, ckpt = _grads(registry, name, False), _grads(registry, name, True)
    assert plain.keys() == ckpt.keys() and len(plain) > 10
    worst = max(float((plain[k] - ckpt[k]).abs().max()) for k in plain)
    assert worst < 1e-6, f"checkpointed gradients differ by {worst}"


def test_checkpointing_restores_forward_on_error(registry):
    m = registry.build("cbramod")
    units = m.checkpoint_units()
    with pytest.raises(RuntimeError), checkpointing(units):
        raise RuntimeError("boom")
    assert all("forward" not in u.__dict__ for u in units)


def test_all_arm_trains_mask_encoding_like_upstream(registry):
    m = registry.build("cbramod")
    assert set_trainable(m, list(m.groups), include_fixed=True) == 4_924_000
    b = registry.build("biot")
    assert set_trainable(b, list(b.groups), include_fixed=True) == 3_318_272  # index is integer


def test_displacement_reports_scale_free_coherence(registry):
    from eegdrift.drift.metrics import displacement
    from eegdrift.models.protocols import state_copy

    m = registry.build("cbramod")
    s0 = state_copy(m.module)
    s1 = {k: v + 1e-3 if v.is_floating_point() else v for k, v in s0.items()}
    d = displacement(s0, s1, m, lr_sum=1e-3)
    assert abs(d["block00"]["coherence"] - 1.0) < 1e-6      # every element moved the full lr
    assert d["block00"]["rel"] > 0 and d["block00"]["n"] == 402_600


PILOT = ROOT / "data" / "lmdb" / "chbmit_ssl30"


@pytest.mark.skipif(not PILOT.exists(), reason="needs the pilot stores in data/lmdb")
def test_rotated_ssl_pool_excludes_test_subjects(root, tmp_path):
    from eegdrift.data.index import subject_of
    from eegdrift.data.store import LocalStore
    from eegdrift.study import Context, case_splits, load_ssl

    ctx = Context(root=root, data_root=root / "data" / "lmdb", out=tmp_path,
                  artifacts=LocalStore(tmp_path / "a"), device=torch.device("cpu"), smoke=True,
                  log=lambda *_: None)
    for split in ("rot0", "rot3"):
        test = {subject_of(c) for c, s in case_splits(ctx, "chbmit", split).items() if s == "test"}
        ssl = load_ssl(ctx, "chbmit", split)
        assert test and not {r["subject"] for r in ssl.records} & test
    assert load_ssl(ctx, "chbmit", "rot0").hash != load_ssl(ctx, "chbmit", "paper").hash


def test_result_key_covers_probe_and_eval(registry, root, tmp_path):
    from eegdrift.arms import resolve
    from eegdrift.data.store import LocalStore
    from eegdrift.study import Context, EvalData, SSLData, adapt_spec, probe_template, result_key

    ctx = Context(root=root, data_root=tmp_path, out=tmp_path, artifacts=LocalStore(tmp_path),
                  device=torch.device("cpu"), log=lambda *_: None)
    arm = resolve("last", ctx.adapt_cfg, ctx.registry, "biot")
    ssl = SSLData(torch.zeros(4174, 1), [], "h", 81993, "paper")
    spec = adapt_spec(ctx, "biot", "chbmit", arm, 42, ssl)
    tpl = probe_template(ctx, "biot", "chbmit", 42, "paper")
    ev = EvalData({}, "e1", [], "paper")
    k = result_key(spec, arm, tpl, ("mlp_fullft", "linear"), ev)
    assert k != result_key(spec, arm, tpl, ("linear",), ev)
    assert k != result_key(spec, arm, tpl, ("mlp_fullft", "linear"), EvalData({}, "e2", [], "paper"))
    from dataclasses import replace
    assert k != result_key(spec, arm, replace(tpl, epochs=9), ("mlp_fullft", "linear"), ev)
    assert np.isfinite(len(k))


def test_run_tag_and_batch_change_the_result_key(registry, root, tmp_path):
    from eegdrift.arms import resolve
    from eegdrift.data.store import LocalStore
    from eegdrift.study import Context, EvalData, SSLData, adapt_spec, probe_template, result_key

    def key(overrides, tag=""):
        ctx = Context(root=root, data_root=tmp_path, out=tmp_path, artifacts=LocalStore(tmp_path),
                      device=torch.device("cpu"), log=lambda *_: None, overrides=overrides)
        arm = resolve("last", ctx.adapt_cfg, ctx.registry, "biot")
        ssl = SSLData(torch.zeros(4174, 1), [], "h", 81993, "paper")
        return result_key(adapt_spec(ctx, "biot", "chbmit", arm, 42, ssl), arm,
                          probe_template(ctx, "biot", "chbmit", 42, "paper"), ("linear",),
                          EvalData({}, "e", [], "paper"), tag)

    base = key({})
    assert key({"batch": "128"}) != base and key({}, "R3") != base


def test_fixed_c_restores_lowest_loss_pass(registry):
    """D16: like upstream's diversity trainer, fixed_c restores the lowest mean-loss pass."""
    from eegdrift.adapt import AdaptSpec, adapt
    from eegdrift.objectives import objective_for

    torch.manual_seed(0)
    m = registry.build("cbramod")
    spec = AdaptSpec("cbramod", "chbmit", "last", ("block11", "head"), "pretrained", 0, "fixed_c",
                     batch=2, epochs=3, n_windows=4, n_total=4, scale=700.0, lr=1e-2)
    res = adapt(m, objective_for(m), spec, torch.randn(4, 16, 2, 200) * 50, torch.device("cpu"),
                log=lambda *_: None)
    assert res.steps_done == spec.steps() == 6
    assert res.best_epoch == int(np.argmin(res.epoch_losses))


def test_ssl_subsets_follow_upstream_rules():
    from eegdrift.study import _subset_indices

    class _Store:   # minimal stand-in: 6 subjects x 50 windows
        index = [{"subject": f"chb{s:02d}"} for s in range(6) for _ in range(50)]

    pool = list(range(300))
    parity = list(range(0, 300, 2))
    a = _subset_indices("N60", parity, pool, _Store())
    assert len(a) == 60 and set(a) <= set(parity) and a == _subset_indices("N60", parity, pool, _Store())
    b = _subset_indices("P3N100", parity, pool, _Store())
    assert len(b) == 100 and len({_Store.index[i]["subject"] for i in b}) == 3
    with pytest.raises(ValueError):
        _subset_indices("P6N306", parity, pool, _Store())   # needs 52 per subject, only 50 exist


def test_fixed_c_budget_is_upstream_132_steps(registry, root, tmp_path):
    from eegdrift.arms import resolve
    from eegdrift.data.store import LocalStore
    from eegdrift.study import Context, SSLData, adapt_spec

    ctx = Context(root=root, data_root=tmp_path, out=tmp_path, artifacts=LocalStore(tmp_path),
                  device=torch.device("cpu"), log=lambda *_: None, overrides={"protocol": "fixed_c"})
    arm = resolve("last", ctx.adapt_cfg, ctx.registry, "biot")
    ssl = SSLData(torch.zeros(896, 1), [], "h", 81993, "paper", "N896")
    spec = adapt_spec(ctx, "biot", "chbmit", arm, 42, ssl)
    assert (spec.protocol, spec.batch, spec.n_total, spec.steps()) == ("fixed_c", 128, 4174, 132)
