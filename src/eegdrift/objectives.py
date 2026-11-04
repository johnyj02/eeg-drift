"""Seam 1: SSLObjective. Each model's own pretraining loss, as the upstream adaptation used it.

adapt.py holds ONE loop and calls only this interface; it never branches on a model name.
"""

from __future__ import annotations

from typing import Protocol

import torch
from torch import Tensor, nn

from eegdrift.models.protocols import EEGModel, TapGroup, group


class SSLObjective(Protocol):
    name: str

    def loss(self, model: EEGModel, windows: Tensor) -> Tensor:
        """windows: [B, 16, S, 200], already scaled. Returns a scalar loss."""
        ...

    def head_groups(self, model: EEGModel) -> list[TapGroup]:
        """Groups that must be trainable in every adaptation arm (the SSL loss head)."""
        ...


class ContrastiveBIOT:
    """BIOT UnsupervisedPretrain: perturbed-view embedding -> `prediction` head, pulled toward
    the clean-view embedding with CosineEmbeddingLoss(target=+1). Both views carry gradient.
    The perturbation draws from numpy's GLOBAL RNG (vendored code): seed it per run."""

    name = "contrastive_biot"

    def __init__(self) -> None:
        self._criterion = nn.CosineEmbeddingLoss()

    def loss(self, model: EEGModel, windows: Tensor) -> Tensor:
        x = model.prepare(windows)
        emb, pred_emb = model.module(x)
        target = torch.ones(x.shape[0], device=x.device)
        return self._criterion(emb, pred_emb, target)

    def head_groups(self, model: EEGModel) -> list[TapGroup]:
        return [group(model, "head")]


class MaskedCBraMod:
    """CBraMod masked patch reconstruction: Bernoulli(mask_ratio) over (B, C, P) patches,
    masked patches replaced by the (zero, frozen) mask_encoding, MSE on masked patches only."""

    name = "masked_cbramod"

    def __init__(self, mask_ratio: float = 0.5) -> None:
        self.mask_ratio = mask_ratio

    def loss(self, model: EEGModel, windows: Tensor) -> Tensor:
        x = model.prepare(windows)
        b, c, p, _ = x.shape
        mask = torch.zeros((b, c, p), dtype=torch.long, device=x.device).bernoulli_(self.mask_ratio)
        y = model.module(x, mask=mask)
        return nn.functional.mse_loss(y[mask == 1], x[mask == 1])

    def head_groups(self, model: EEGModel) -> list[TapGroup]:
        return [group(model, "head")]


def objective_for(model: EEGModel, mask_ratio: float = 0.5) -> SSLObjective:
    """The ONE place a model name maps to its objective (the registry's dual for losses)."""
    return {"biot": ContrastiveBIOT, "cbramod": lambda: MaskedCBraMod(mask_ratio)}[model.name]()
