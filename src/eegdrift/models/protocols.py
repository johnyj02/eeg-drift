"""Seam 2: the EEGModel protocol, and the identity types the registry issues.

Nothing outside models/ may name a layer by string. Callers hold TapId / TapGroup objects issued
by the Registry; the activation record's layer fields are their serialization only.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict, dataclass
from typing import Protocol

import torch
from torch import Tensor, nn


@dataclass(frozen=True, order=True)
class TapId:
    model: str
    key: str           # registry key: "patch_embed", "block07", "attn07", "pooled_out"
    kind: str          # patch_embed | post_block | post_attn | pooled_out
    module: str        # serialized module path inside the SSL module
    index: int         # position in network order (patch embed = 0)
    depth_frac: float  # index / n_blocks; cross-model comparisons use THIS, never raw index

    def to_record(self) -> dict:
        return asdict(self)


@dataclass(frozen=True, order=True)
class TapGroup:
    """A trainable unit for layer masks and per-layer displacement."""

    model: str
    key: str                     # "embed", "block00".., "head"
    prefixes: tuple[str, ...]    # parameter-name prefixes inside the SSL module
    depth_frac: float


class EEGModel(Protocol):
    name: str
    module: nn.Module                 # the SSL module: encoder + SSL loss head
    taps: tuple[TapId, ...]
    groups: tuple[TapGroup, ...]
    fixed_params: frozenset[str]      # declared never-trainable (buffers in all but name)

    def prepare(self, windows: Tensor) -> Tensor:
        """[B, 16, S, 200] scaled windows -> this model's input. Asserts model limits."""
        ...

    def forward_with_taps(self, x: Tensor, taps: Sequence[TapId]) -> dict[TapId, Tensor]: ...

    def features(self, x: Tensor) -> Tensor:
        """What the parity probe consumes: the encoder output (CBraMod: before proj_out, D23)."""
        ...

    def pooled(self, x: Tensor) -> Tensor:
        """[B, d] window embedding for the strong probe."""
        ...

    def encoder(self) -> nn.Module:
        """The backbone the probe wraps (shares parameters with `module`)."""
        ...

    def checkpoint_units(self) -> list[nn.Module]:
        """Modules to activation-checkpoint when backprop reaches deep (models/_ckpt.py)."""
        ...


def group_param_names(model: EEGModel, group: TapGroup) -> list[str]:
    return [n for n, _ in model.module.named_parameters()
            if n.startswith(group.prefixes) and n not in model.fixed_params]


def group(model: EEGModel, key: str) -> TapGroup:
    for g in model.groups:
        if g.key == key:
            return g
    raise KeyError(f"{model.name} has no tap group {key!r}: {[g.key for g in model.groups]}")


def set_trainable(model: EEGModel, groups: Sequence[TapGroup], include_fixed: bool = False) -> int:
    """Freeze everything, then unfreeze exactly `groups`. Idempotent. Returns trainable count.

    include_fixed=True additionally unfreezes the declared-fixed FLOATING-POINT parameters
    (CBraMod's mask_encoding; BIOT's index is integer and can never train). Upstream's layer
    ablation "all" mode does exactly this (`if param.is_floating_point(): requires_grad = True`).
    """
    wanted = {n for g in groups for n in group_param_names(model, g)}
    for n, p in model.module.named_parameters():
        fixed_ok = include_fixed and n in model.fixed_params and p.is_floating_point()
        p.requires_grad_(n in wanted or fixed_ok)
    return sum(p.numel() for p in model.module.parameters() if p.requires_grad)


@torch.no_grad()
def state_copy(module: nn.Module) -> dict[str, Tensor]:
    return {k: v.detach().clone().cpu() for k, v in module.state_dict().items()}


def scale_input(x: Tensor, scale: float, norm: str = "") -> Tensor:
    """Model input from unscaled uV windows [B, C, S, P]. norm "" = divide by `scale` (upstream);
    "q95" = BIOT's native per-channel, per-window x / (95th percentile of |x| + 1e-8) (D25-E19;
    kthvalue, so no interpolation between order statistics)."""
    if norm == "":
        return x / scale
    if norm != "q95":
        raise ValueError(f"unknown input_norm {norm!r}")
    flat = x.abs().reshape(*x.shape[:2], -1)
    q = flat.kthvalue(max(1, int(round(0.95 * flat.shape[-1]))), dim=-1).values
    return x / (q[..., None, None] + 1e-8)
