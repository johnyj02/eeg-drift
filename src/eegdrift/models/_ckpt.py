"""Per-block activation checkpointing, applied from outside the vendored code.

Why: backprop through every block at the parity batch (256) needs ~30 GiB of saved activations
(code review 2026-10-15); the A10G has 24 GB. Upstream ran on A100s. Checkpointing recomputes each
block's forward during backward instead of storing it. With use_reentrant=False and
preserve_rng_state=True the recomputation replays the same dropout masks, so gradients are those
of the uncheckpointed run (up to floating-point nondeterminism). BIOT's numpy perturbation runs
outside the blocks and is not replayed.

Forward hooks still fire exactly once: they live in Module.__call__, while the recomputation
calls the original bound forward directly.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from functools import partial

import torch
from torch import nn
from torch.utils.checkpoint import checkpoint


def _checkpointed(original, *args, **kwargs):
    if torch.is_grad_enabled():
        return checkpoint(original, *args, use_reentrant=False, preserve_rng_state=True, **kwargs)
    return original(*args, **kwargs)


@contextmanager
def checkpointing(units: list[nn.Module]) -> Iterator[None]:
    """Shadow each unit's forward with a checkpointed call; restore on exit, even on error."""
    for u in units:
        if "forward" in u.__dict__:
            raise RuntimeError(f"{type(u).__name__}.forward is already shadowed")
        u.forward = partial(_checkpointed, u.forward)  # instance attribute shadows the method
    try:
        yield
    finally:
        for u in units:
            u.__dict__.pop("forward", None)
