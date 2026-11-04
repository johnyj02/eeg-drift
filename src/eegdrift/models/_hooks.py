"""Shared tap-capture mechanics for the adapters. Hooks are registry-declared, never ad hoc."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from contextlib import contextmanager

from torch import Tensor, nn

from eegdrift.models.protocols import TapId


@contextmanager
def capture(module: nn.Module, taps: Sequence[TapId], hook_kind: Callable[[TapId], str]):
    """Yield a dict that fills with {TapId: activation} during one forward pass.

    hook kinds: "output" (module output), "input" (first positional input), and "residual"
    (input + output: the residual stream after a pre-norm sublayer whose residual add lives in
    the parent's loop, which is how lucidrains' SequentialSequence applies x = x + g(x)).
    A tap that fires twice in one pass raises: that would mean the registry is wrong.
    """
    out: dict[TapId, Tensor] = {}
    handles = []

    def store(tap: TapId, value: Tensor) -> None:
        if tap in out:
            raise RuntimeError(f"tap {tap.key} fired twice in one forward pass")
        out[tap] = value.detach()

    for tap in taps:
        sub = module.get_submodule(tap.module)
        kind = hook_kind(tap)
        if kind == "output":
            handles.append(sub.register_forward_hook(lambda m, i, o, t=tap: store(t, o)))
        elif kind == "input":
            handles.append(sub.register_forward_pre_hook(lambda m, i, t=tap: store(t, i[0])))
        elif kind == "residual":
            handles.append(sub.register_forward_hook(lambda m, i, o, t=tap: store(t, i[0] + o)))
        else:
            raise ValueError(f"unknown hook kind {kind!r} for {tap.key}")
    try:
        yield out
    finally:
        for h in handles:
            h.remove()
