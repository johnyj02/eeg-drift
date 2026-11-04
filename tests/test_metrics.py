import numpy as np
import torch

from eegdrift.drift.metrics import (
    decay_baseline,
    half,
    linear_cka,
    rank_stability,
    token_mean,
    top_k,
)


def test_cka_identities():
    rng = np.random.default_rng(0)
    x = rng.normal(size=(200, 30))
    q, _ = np.linalg.qr(rng.normal(size=(30, 30)))
    assert abs(linear_cka(x, x) - 1) < 1e-10
    assert abs(linear_cka(x, x @ q) - 1) < 1e-10          # orthogonal invariance
    assert abs(linear_cka(x, 3.7 * x + 5) - 1) < 1e-10    # isotropic scale + shift invariance
    assert linear_cka(x, rng.normal(size=(200, 30))) < 0.25  # independent noise is far from 1


def test_cka_accepts_token_tensors_and_pools():
    rng = np.random.default_rng(1)
    a = rng.normal(size=(50, 16, 30, 8))
    assert token_mean(a).shape == (50, 8)
    assert abs(linear_cka(a, a) - 1) < 1e-10
    assert half(a, "spatial").shape[-1] == 4 and half(a, "temporal").shape[-1] == 4


def test_decay_baseline_matches_plan_numbers():
    assert abs(decay_baseline(3e-5, 5e-2, 4059) - 0.0061) < 2e-4
    assert decay_baseline(3e-5, 5e-2, 0) == 0


def test_rank_stability_and_topk():
    a = {"embed": 3.0, "block00": 2.0, "block01": 1.0, "head": 9.0}
    assert rank_stability([a, dict(a)], ["embed", "block00", "block01"])["mean_tau"] == 1.0
    assert top_k(a, 2) == ["embed", "block00"]   # head excluded by default


def test_displacement_zero_on_identical_states(registry):
    from eegdrift.drift.metrics import displacement
    from eegdrift.models.protocols import state_copy

    torch.manual_seed(0)
    m = registry.build("cbramod")
    s = state_copy(m.module)
    assert all(v["abs"] == 0 and v["rel"] == 0 for v in displacement(s, s, m).values())
