"""Config facts about the released code (c3n-group/efficient-eeg-adapt @ d056cdf), checked with
Hydra against a LOCAL CLONE at test time (D25-E2). No upstream text is embedded here: every
config is composed from the clone's own YAML; the test skips if no clone is present.

Clone path: $EEA_CLONE, else ~/released/eea. Composition drops the `launchers` defaults entry
(`~launchers`), which only selects the SLURM launcher plugin and holds no run settings.

Facts used by the paper (what trainer.py reads): the SA trainers read
cfg.method.spt_anchor_l2sp_lambda (trainer.py:154) without a default, and read
cfg.model.get('foundation_dir', '') (trainer.py:364) to decide whether the SSL model starts
from the pretrained checkpoint.
"""

import os
import subprocess
from pathlib import Path

import pytest

hydra = pytest.importorskip("hydra")
from omegaconf.errors import ConfigAttributeError  # noqa: E402

PIN = "d056cdf94a6a680917218deae1f7815143ded27c"
CLONE = Path(os.environ.get("EEA_CLONE", "~/released/eea")).expanduser().resolve()
if not (CLONE / "src" / "conf" / "config.yaml").exists():
    pytest.skip(f"released clone not found at {CLONE} (set EEA_CLONE)", allow_module_level=True)

# entry point -> (config dir under src/, primary config name)
TREES = {
    "main": ("conf", "config"),
    "layer": ("ablation_layer/conf_layer", "config"),
    "diversityN": ("ablation_diversityN/conf_diversity", "config"),
    "diversityP": ("ablation_diversityP/confP", "configP"),
}


def compose(tree: str, *overrides: str):
    from hydra import compose as hcompose
    from hydra import initialize_config_dir

    conf_dir, name = TREES[tree]
    with initialize_config_dir(config_dir=str(CLONE / "src" / conf_dir), version_base=None):
        return hcompose(config_name=name, overrides=["~launchers", *overrides])


def test_clone_is_the_pinned_commit():
    if not (CLONE / ".git").exists():
        pytest.skip("clone has no .git")
    head = subprocess.run(["git", "-C", str(CLONE), "rev-parse", "HEAD"], capture_output=True,
                          text=True, check=True).stdout.strip()
    assert head == PIN


@pytest.mark.parametrize("tree", list(TREES))
@pytest.mark.parametrize("model", ["biot", "cbramod"])
def test_missing_l2sp_key_raises(tree, model):
    cfg = compose(tree, f"model={model}", "method=step_up", "dataset=chbmit")
    with pytest.raises(ConfigAttributeError):
        _ = cfg.method.spt_anchor_l2sp_lambda


@pytest.mark.parametrize("tree", list(TREES))
def test_adding_the_key_composes(tree):
    cfg = compose(tree, "model=cbramod", "method=step_up", "dataset=chbmit",
                  "+method.spt_anchor_l2sp_lambda=0")
    assert cfg.method.spt_anchor_l2sp_lambda == 0


@pytest.mark.parametrize("tree", list(TREES))
@pytest.mark.parametrize("model", ["biot", "cbramod"])
def test_foundation_dir_is_never_set(tree, model):
    cfg = compose(tree, f"model={model}", "method=step_up", "dataset=chbmit")
    assert cfg.model.get("foundation_dir", "") == ""


def test_main_chbmit_defaults():
    cfg = compose("main", "model=cbramod", "method=fm_freeze", "dataset=chbmit")
    assert cfg.training.full_ft is True            # the MLP head, not a linear probe
    assert cfg.training.batch_size == 256
    assert cfg.dataset.training.epochs == 10       # trainer reads dataset.training.epochs
    assert cfg.dataset.method.spt_epochs == 3      # ... and dataset.method.spt_epochs
    assert cfg.training.wandb is True


def test_layer_ablation_default_is_last1():
    cfg = compose("layer", "model=biot", "method=step_up", "dataset=chbmit")
    assert cfg.method.spt_unfreeze_layers == "last1"


@pytest.mark.parametrize("tree", ["diversityN", "diversityP"])
def test_compute_n_exists_so_plus_prefix_fails(tree):
    """`+dataset.compute_N=896` (append) fails because the key exists as a placeholder string."""
    from hydra.errors import ConfigCompositionException

    cfg = compose(tree, "model=biot", "method=step_up", "dataset=chbmit")
    assert isinstance(cfg.dataset.compute_N, str)
    with pytest.raises(ConfigCompositionException):
        compose(tree, "model=biot", "method=step_up", "dataset=chbmit", "+dataset.compute_N=896")
    assert compose(tree, "model=biot", "method=step_up", "dataset=chbmit",
                   "dataset.compute_N=896").dataset.compute_N == 896
