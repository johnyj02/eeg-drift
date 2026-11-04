"""Registry parity: groups partition the parameters, arm counts reproduce the paper's Table 2
accounting, every tap fires exactly once, and the adapters enforce model limits."""

import pytest
import torch

from eegdrift.arms import resolve
from eegdrift.models.protocols import group_param_names, set_trainable

PAPER = {  # (model, arm): trainable params, verified 2026-10-15 against the paper's Table 2
    ("biot", "last"): 920_576, ("biot", "last2"): 1_709_568,
    ("cbramod", "last"): 442_800, ("cbramod", "last2"): 845_400,
}


@pytest.fixture(scope="module")
def adapt_cfg(root):
    import yaml

    return yaml.safe_load((root / "configs/adapt.yaml").read_text())


@pytest.mark.parametrize("name", ["biot", "cbramod"])
def test_groups_partition_parameters(registry, name):
    torch.manual_seed(0)
    m = registry.build(name)
    names = [n for g in m.groups for n in group_param_names(m, g)]
    every = {n for n, _ in m.module.named_parameters() if n not in m.fixed_params}
    assert len(names) == len(set(names)), "a parameter is in two groups"
    assert set(names) == every, f"uncovered: {sorted(every - set(names))[:5]}"


@pytest.mark.parametrize(("name", "arm"), list(PAPER))
def test_arm_counts_match_paper(registry, adapt_cfg, name, arm):
    torch.manual_seed(0)
    m = registry.build(name)
    a = resolve(arm, adapt_cfg, registry, name)
    groups = [g for g in m.groups if g.key in a.groups]
    assert set_trainable(m, groups) == PAPER[(name, arm)]
    assert set_trainable(m, groups) == PAPER[(name, arm)], "set_trainable must be idempotent"


def test_cbramod_total_includes_frozen_mask_encoding(registry):
    m = registry.build("cbramod")
    assert sum(p.numel() for p in m.module.parameters()) == 4_924_000
    assert set_trainable(m, list(m.groups)) == 4_923_800  # mask_encoding frozen unless include_fixed


@pytest.mark.parametrize("name", ["biot", "cbramod"])
def test_every_tap_fires_once(registry, name):
    torch.manual_seed(0)
    m = registry.build(name)
    m.module.eval()
    with torch.no_grad():
        got = m.forward_with_taps(m.prepare(torch.randn(2, 16, 30, 200)), m.taps)
    assert set(got) == set(m.taps)


def test_biot_token_ceiling(registry):
    m = registry.build("biot")
    m.prepare(torch.zeros(1, 16, 30, 200))            # 944 tokens: fine
    with pytest.raises(ValueError, match="max_seq_len"):
        m.prepare(torch.zeros(1, 18, 30, 200))        # 1,062 tokens: overflow


def test_depth_fracs_are_monotone(registry):
    for name in ("biot", "cbramod"):
        fr = [t.depth_frac for t in registry.taps(name) if t.kind == "post_block"]
        assert fr == sorted(fr) and fr[-1] == 1.0
