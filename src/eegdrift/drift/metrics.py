"""Drift metrics. Pure functions over arrays/tensors: ALL I/O goes through data/store.py.

Linear CKA is written out (ten lines) because the metric is the thing a reviewer audits.
tests/test_metrics.py pins its identities.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import numpy as np
import torch
from scipy.stats import kendalltau

from eegdrift.models.protocols import EEGModel, group_param_names, set_trainable


def _flat(a: np.ndarray) -> np.ndarray:
    return a.reshape(a.shape[0], -1).astype(np.float64)


def gram(a: np.ndarray) -> np.ndarray:
    """Centered linear Gram matrix over windows: rows = windows, any trailing shape flattened."""
    x = _flat(a)
    x = x - x.mean(axis=0, keepdims=True)
    return x @ x.T


def cka_from_grams(k: np.ndarray, l: np.ndarray) -> float:  # noqa: E741
    """Linear CKA = HSIC(K, L) / sqrt(HSIC(K, K) HSIC(L, L)) on already-centered Grams."""
    hsic = float(np.sum(k * l))
    return hsic / float(np.sqrt(np.sum(k * k) * np.sum(l * l)))


def linear_cka(a: np.ndarray, b: np.ndarray) -> float:
    if a.shape[0] != b.shape[0]:
        raise ValueError("CKA needs the same windows in both views")
    return cka_from_grams(gram(a), gram(b))


def token_mean(a: np.ndarray) -> np.ndarray:
    """[n, ..., d] -> [n, d]: mean over every token axis (BIOT [n,T,d], CBraMod [n,C,P,d])."""
    return a.reshape(a.shape[0], -1, a.shape[-1]).mean(axis=1)


def half(a: np.ndarray, which: str) -> np.ndarray:
    """CBraMod criss-cross halves of the last axis: spatial (0-99) or temporal (100-199)."""
    d = a.shape[-1] // 2
    return a[..., :d] if which == "spatial" else a[..., d:]


def displacement(state0: Mapping[str, torch.Tensor], state1: Mapping[str, torch.Tensor],
                 model: EEGModel, lr_sum: float | None = None) -> dict[str, dict]:
    """Per tap group: raw and relative weight change, plus Adam-coherence when lr_sum is known.

    Under Adam(W) every element moves by ~lr per step whatever its gradient's size, so the plan's
    relative displacement ||dtheta|| / ||theta0|| is ~ coherence * sum(lr) / RMS(theta0): it ranks
    groups partly by WEIGHT SCALE (code review 2026-10-15). The scale-free statistic is

        coherence = ||dtheta|| / (sqrt(n) * sum_t lr_t)       (1 = every element moved the full
                                                               lr in one direction every step)

    which is what drift_topk ranks on (notes/decisions.md D9). Both are reported.
    """
    out = {}
    for g in model.groups:
        names = group_param_names(model, g)
        d2 = sum(float((state1[n].double() - state0[n].double()).pow(2).sum()) for n in names)
        t2 = sum(float(state0[n].double().pow(2).sum()) for n in names)
        n = sum(state0[k].numel() for k in names)
        row = {"abs": float(np.sqrt(d2)), "theta0": float(np.sqrt(t2)), "n": int(n),
               "rel": float(np.sqrt(d2) / np.sqrt(t2)) if t2 > 0 else float("nan")}
        if lr_sum:
            row["coherence"] = float(np.sqrt(d2) / (np.sqrt(n) * lr_sum)) if n else float("nan")
        out[g.key] = row
    return out


def decay_baseline(lr: float, weight_decay: float, steps: int) -> float:
    """Relative shrinkage from decoupled weight decay alone: 1 - (1 - lr*wd)^steps."""
    return 1.0 - (1.0 - lr * weight_decay) ** steps


def grad_pressure(model: EEGModel, objective, windows: torch.Tensor, scale: float,
                  device: torch.device, batch: int = 64) -> dict[str, dict]:
    """Design C: per group gradient of the FROZEN model's own SSL loss, one pass, no step.

    Reports ||g||, ||theta||, n, the plan's ratio ||g||/||theta|| ("rel") and the scale-free
    RMS gradient ||g||/sqrt(n) ("rms"), which is what the top-k ranks on (D9). Gradients are
    accumulated over chunks as the mean of per-chunk mean losses.
    """
    from eegdrift.models._ckpt import checkpointing  # noqa: PLC0415

    set_trainable(model, model.groups)
    model.module.to(device).train()
    model.module.zero_grad(set_to_none=True)
    n_chunks = 0
    with checkpointing(model.checkpoint_units()):
        for i in range(0, len(windows), batch):
            loss = objective.loss(model, windows[i:i + batch].to(device, torch.float32) / scale)
            loss.backward()
            n_chunks += 1
    named = dict(model.module.named_parameters())
    out = {}
    for g in model.groups:
        names = group_param_names(model, g)
        g2 = sum(float((named[n].grad.double() / n_chunks).pow(2).sum())
                 for n in names if named[n].grad is not None)
        t2 = sum(float(named[n].detach().double().pow(2).sum()) for n in names)
        n = sum(named[k].numel() for k in names)
        out[g.key] = {"grad": float(np.sqrt(g2)), "theta": float(np.sqrt(t2)), "n": int(n),
                      "rel": float(np.sqrt(g2) / np.sqrt(t2)) if t2 > 0 else float("nan"),
                      "rms": float(np.sqrt(g2 / n)) if n else float("nan")}
    model.module.zero_grad(set_to_none=True)
    model.module.eval()
    return out


def seed_mean(per_seed: Sequence[Mapping[str, Mapping]], field: str) -> dict[str, float]:
    keys = per_seed[0].keys()
    return {k: float(np.mean([d[k][field] for d in per_seed])) for k in keys}


def per_seed_field(per_seed: Sequence[Mapping[str, Mapping]], field: str) -> list[dict[str, float]]:
    return [{k: v[field] for k, v in d.items()} for d in per_seed]


def rank_stability(per_seed: Sequence[Mapping[str, float]], keys: Sequence[str]) -> dict:
    """Mean pairwise Kendall tau of per-group rankings across seeds (1.0 = identical order)."""
    vecs = [np.array([d[k] for k in keys]) for d in per_seed]
    taus = [kendalltau(vecs[i], vecs[j]).statistic
            for i in range(len(vecs)) for j in range(i + 1, len(vecs))]
    return {"mean_tau": float(np.mean(taus)) if taus else float("nan"),
            "min_tau": float(np.min(taus)) if taus else float("nan"), "pairs": len(taus)}


def top_k(scores: Mapping[str, float], k: int, exclude: Sequence[str] = ("head",)) -> list[str]:
    ranked = sorted((s, key) for key, s in scores.items() if key not in exclude)
    return [key for _, key in ranked[::-1][:k]]
