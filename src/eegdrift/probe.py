"""Probes. Two DISTINCT result types so a table can never silently mix them.

ParityProbeResult reproduces upstream src/trainer.py + model_factory.py, except where D23 departs:
the frozen backbone runs in ProbeSpec.backbone_mode (upstream: TRAIN, dropout active; we use eval
for CBraMod, train for BIOT) and CBraMod is read at its encoder output. AdamW 4e-4 / wd 5e-2,
cosine to 1e-5 over 10 epochs, BCEWithLogits (binary) or CE with label smoothing 0.1, batch 256,
model selection on validation ROC-AUC (binary) / Cohen's kappa (multiclass), PR-AUC computed as
the trapezoid under the precision-recall curve. Two head variants:

* "mlp_fullft": the head the shipped config actually builds (training.full_ft: True): for
  CBraMod a 3-layer MLP on the flattened [16, S, 200] output (~64M params on 10 s windows), for
  BIOT ELU -> Linear. The paper calls this "linear probing".
* "linear": what the paper describes: one Linear layer on the same features.

StrongProbeResult is the deliverable-3 collapse audit only: sklearn logistic regression on
eval-mode pooled features, C chosen on validation.
"""

from __future__ import annotations

import copy
import time
from dataclasses import asdict, dataclass

import numpy as np
import torch
from sklearn.metrics import (
    auc,
    average_precision_score,
    balanced_accuracy_score,
    cohen_kappa_score,
    f1_score,
    precision_recall_curve,
    roc_auc_score,
)
from torch import Tensor, nn

from eegdrift.models.protocols import EEGModel, scale_input

VARIANTS = ("mlp_fullft", "linear", "linear_z", "ft")   # linear_z: train-standardized linear (D25-E26)
# ft: supervised full fine-tuning reference (D27): linear head AND the encoder train on the labels;
# the encoder learns at FT_BACKBONE_LR x the head lr. New variant only: no existing number changes.
FT_BACKBONE_LR = 0.1
DEFAULT_VARIANTS = ("mlp_fullft", "linear", "linear_z")   # run when no probe list is given; ft is opt-in
PROBE_CODE_VERSION = 4  # bump on ANY change that alters a probe number (3: logits; 4: CBraMod encoder tap, mode)


@dataclass(frozen=True)
class ProbeSpec:
    model: str
    dataset: str
    variant: str
    seed: int
    n_classes: int
    window_s: int
    split: str = "paper"
    epochs: int = 10
    lr: float = 4e-4
    weight_decay: float = 5e-2
    betas: tuple[float, float] = (0.9, 0.999)
    eta_min: float = 1e-5
    batch: int = 256
    label_smoothing: float = 0.1
    scale: float = 100.0
    backbone_mode: str = "train"   # "train" = upstream (dropout on in the frozen backbone); "eval"
    tap: str = "encoder"           # CBraMod "proj_out" = the released code's probe input (D23)
    input_norm: str = ""           # "" = / scale (upstream); "q95" = BIOT native (D25-E19)


@dataclass(frozen=True)
class ParityProbeResult:
    spec: ProbeSpec
    head_params: int
    best_epoch: int
    best_val: float
    test_at_best: dict
    test_last: dict
    val_curve: tuple[float, ...]
    seconds: float
    # per epoch: train loss, val loss + metrics, test metrics (PLOT ONLY; never used for selection)
    history: tuple = ()

    def to_record(self) -> dict:
        return {"type": "ParityProbeResult", **asdict(self)}


@dataclass(frozen=True)
class StrongProbeResult:
    model: str
    dataset: str
    split: str
    C: float
    val: dict
    test: dict

    def to_record(self) -> dict:
        return {"type": "StrongProbeResult", **asdict(self)}


class Standardize(nn.Module):
    """(x - mean) / std with train-split feature statistics (set by parity_probe), no parameters."""

    def __init__(self, d: int):
        super().__init__()
        self.register_buffer("mean", torch.zeros(d))
        self.register_buffer("std", torch.ones(d))

    def forward(self, x: Tensor) -> Tensor:
        return (x - self.mean) / self.std


def build_head(model_name: str, variant: str, n_classes: int, window_s: int) -> nn.Module:
    out = 1 if n_classes == 2 else n_classes
    if model_name == "biot":
        if variant == "mlp_fullft":
            return nn.Sequential(nn.ELU(), nn.Linear(256, out))
        if variant == "linear_z":
            return nn.Sequential(Standardize(256), nn.Linear(256, out))
        return nn.Linear(256, out)
    flat = 16 * window_s * 200
    if variant == "linear_z":
        return nn.Sequential(nn.Flatten(), Standardize(flat), nn.Linear(flat, out))
    if variant == "mlp_fullft":
        return nn.Sequential(
            nn.Flatten(), nn.Linear(flat, window_s * 200), nn.ELU(), nn.Dropout(0.1),
            nn.Linear(window_s * 200, 200), nn.ELU(), nn.Dropout(0.1), nn.Linear(200, out))
    return nn.Sequential(nn.Flatten(), nn.Linear(flat, out))


def metrics(y_true: np.ndarray, score: np.ndarray, n_classes: int, threshold: float = 0.5) -> dict:
    if n_classes == 2:
        pred = (score > threshold).astype(int)
        precision, recall, _ = precision_recall_curve(y_true, score, pos_label=1)
        return {"bal_acc": float(balanced_accuracy_score(y_true, pred)),
                "roc_auc": float(roc_auc_score(y_true, score)),
                "pr_auc_trapz": float(auc(recall, precision)),        # upstream's number
                "avg_precision": float(average_precision_score(y_true, score)),  # ours, labelled
                "prevalence": float(np.mean(y_true)), "n": int(len(y_true))}
    pred = score.argmax(1)
    return {"bal_acc": float(balanced_accuracy_score(y_true, pred)),
            "kappa": float(cohen_kappa_score(y_true, pred)),
            "f1_weighted": float(f1_score(y_true, pred, average="weighted")), "n": int(len(y_true))}


def _batches(x: Tensor, y: Tensor, batch: int, shuffle: bool, gen: torch.Generator | None):
    order = torch.randperm(len(x), generator=gen) if shuffle else torch.arange(len(x))
    for i in range(0, len(x), batch):
        idx = order[i:i + batch]
        yield x[idx], y[idx]


def _scores(model: EEGModel, head: nn.Module, x: Tensor, y: Tensor, spec: ProbeSpec,
            device: torch.device) -> tuple[np.ndarray, np.ndarray]:
    model.encoder().eval()
    head.eval()
    out = []
    with torch.no_grad():
        for xb, _ in _batches(x, y, spec.batch, False, None):
            logits = head(model.features(model.prepare(scale_input(xb.to(device), spec.scale, spec.input_norm)),
                                         spec.tap))
            # binary: raw logits. Same ranks as sigmoid, but sigmoid underflows to exactly 0/1 in
            # float32 for |logit| > ~100, and those ties lowered ROC on random-init encoders.
            out.append((logits.squeeze(-1) if spec.n_classes == 2
                        else torch.softmax(logits, 1)).cpu().numpy())
    return y.numpy(), np.concatenate(out)


@torch.no_grad()
def _fit_standardize(model: EEGModel, head: nn.Module, x: Tensor, spec: ProbeSpec, device: torch.device) -> None:
    """Per-feature mean/std over the TRAIN split, backbone in eval mode (one pass)."""
    model.encoder().eval()
    std_mod = next(m for m in head.modules() if isinstance(m, Standardize))
    s1 = s2 = None
    for i in range(0, len(x), spec.batch):
        f = model.features(model.prepare(scale_input(x[i:i + spec.batch].to(device), spec.scale, spec.input_norm)),
                           spec.tap).flatten(1).double()
        s1 = f.sum(0) if s1 is None else s1 + f.sum(0)
        s2 = (f * f).sum(0) if s2 is None else s2 + (f * f).sum(0)
    mean = s1 / len(x)
    std_mod.mean.copy_(mean.float())
    std_mod.std.copy_((s2 / len(x) - mean * mean).clamp_min(0).sqrt().clamp_min(1e-6).float())


LOGIT_T = 0.0   # decision threshold on logits (= probability 0.5); ignored for multi-class


def _bce(y: np.ndarray, z: np.ndarray) -> float:
    """Mean binary cross-entropy from logits, numerically stable (matches BCEWithLogitsLoss)."""
    z = z.astype(np.float64)
    return float(np.mean(np.maximum(z, 0) - z * y + np.log1p(np.exp(-np.abs(z)))))


def parity_probe(model: EEGModel, spec: ProbeSpec, data: dict[str, tuple[Tensor, Tensor]],
                 device: torch.device, log=print) -> tuple[ParityProbeResult, dict[str, np.ndarray]]:
    """data: split -> (x [N, 16, S, 200] unscaled float32, y [N]). Backbone must be final.

    Returns the result AND the per-window test scores at the selected and the last epoch, so
    subject-clustered bootstrap CIs can be computed later without re-running (code review)."""
    torch.manual_seed(spec.seed)
    ft = spec.variant == "ft"
    if ft:   # fine-tuning must never change the caller's encoder: restore it afterwards
        saved = copy.deepcopy(model.module.state_dict())
        try:
            return _parity_probe(model, spec, data, device, log, ft)
        finally:
            model.module.load_state_dict(saved)
            for p in model.module.parameters():
                p.requires_grad_(False)
    return _parity_probe(model, spec, data, device, log, ft)


def _parity_probe(model: EEGModel, spec: ProbeSpec, data: dict[str, tuple[Tensor, Tensor]],
                  device: torch.device, log, ft: bool) -> tuple[ParityProbeResult, dict[str, np.ndarray]]:
    for p in model.module.parameters():
        p.requires_grad_(False)
    model.module.to(device)
    head = build_head(model.name, spec.variant, spec.n_classes, spec.window_s).to(device)
    if spec.variant == "linear_z":
        _fit_standardize(model, head, data["train"][0], spec, device)
    groups = [{"params": list(head.parameters()), "lr": spec.lr}]
    if ft:
        enc = [p for p in model.encoder().parameters() if p.is_floating_point()]   # BIOT `index` is int64
        for p in enc:
            p.requires_grad_(True)
        groups.append({"params": enc, "lr": spec.lr * FT_BACKBONE_LR})
    opt = torch.optim.AdamW(groups, lr=spec.lr, weight_decay=spec.weight_decay, betas=spec.betas)
    xtr, ytr = data["train"]
    n_batches = -(-len(xtr) // spec.batch)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=spec.epochs * n_batches,
                                                       eta_min=spec.eta_min)
    crit = (nn.BCEWithLogitsLoss() if spec.n_classes == 2
            else nn.CrossEntropyLoss(label_smoothing=spec.label_smoothing))
    main = "roc_auc" if spec.n_classes == 2 else "kappa"
    gen = torch.Generator().manual_seed(spec.seed)
    t0, best_val, best_epoch, test_best, curve = time.time(), 0.0, -1, {}, []
    scores_best, scores_val_best, history = None, None, []
    for epoch in range(spec.epochs):
        model.encoder().train(spec.backbone_mode == "train")   # upstream: train -> dropout ON
        head.train()
        train_losses = []
        for xb, yb in _batches(xtr, ytr, spec.batch, True, gen):
            xb, yb = scale_input(xb.to(device), spec.scale, spec.input_norm), yb.to(device)
            with torch.set_grad_enabled(ft):   # frozen backbone: no graph, identical numerics
                feats = model.features(model.prepare(xb), spec.tap)
            logits = head(feats)
            loss = (crit(logits.reshape(-1, 1), yb.float().reshape(-1, 1)) if spec.n_classes == 2
                    else crit(logits, yb.long()))
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            sched.step()
            train_losses.append(loss.item())
        yv, sv = _scores(model, head, *data["val"], spec, device)
        val = metrics(yv, sv, spec.n_classes, LOGIT_T)
        yt, st = _scores(model, head, *data["test"], spec, device)
        history.append({"epoch": epoch, "train_loss": float(np.mean(train_losses)), "val": val,
                        "val_loss": _bce(yv, sv) if spec.n_classes == 2 else None,
                        "test_plot_only": metrics(yt, st, spec.n_classes, LOGIT_T)})
        curve.append(val[main])
        log(f"[probe {spec.model}/{spec.dataset}/{spec.variant} s{spec.seed}] epoch {epoch} "
            f"val {main} {val[main]:.4f}")
        if val[main] > best_val:
            best_val, best_epoch, scores_val_best = val[main], epoch, sv
            y_test, scores_best = _scores(model, head, *data["test"], spec, device)
            test_best = metrics(y_test, scores_best, spec.n_classes, LOGIT_T)
    y_test, scores_last = _scores(model, head, *data["test"], spec, device)
    test_last = metrics(y_test, scores_last, spec.n_classes, LOGIT_T)
    # best_epoch is 0-based; upstream logs it 1-based (best_epoch = epoch + 1). Convert on report.
    result = ParityProbeResult(spec, sum(p.numel() for p in head.parameters()), best_epoch,
                               float(best_val), test_best, test_last, tuple(curve), time.time() - t0,
                               tuple(history))
    arrays = {"y_test": y_test.astype(np.int8), "scores_last": scores_last.astype(np.float32)}
    if scores_best is not None:
        arrays["scores_best"] = scores_best.astype(np.float32)
        arrays["y_val"], arrays["scores_val_best"] = yv.astype(np.int8), scores_val_best.astype(np.float32)
    return result, arrays


@torch.no_grad()
def pooled_features(model: EEGModel, x: Tensor, scale: float, device: torch.device,
                    batch: int = 256) -> np.ndarray:
    model.encoder().eval()
    out = [model.pooled(model.prepare(x[i:i + batch].to(device) / scale)).cpu().numpy()
           for i in range(0, len(x), batch)]
    return np.concatenate(out)


def strong_probe(model_name: str, dataset: str, split: str, feats: dict[str, np.ndarray],
                 labels: dict[str, np.ndarray], n_classes: int,
                 grid=(1e-3, 1e-2, 1e-1, 1.0, 10.0)) -> StrongProbeResult:
    from sklearn.linear_model import LogisticRegression  # noqa: PLC0415
    from sklearn.preprocessing import StandardScaler  # noqa: PLC0415

    scaler = StandardScaler().fit(feats["train"])
    z = {k: scaler.transform(v) for k, v in feats.items()}
    best = None
    for c in grid:
        clf = LogisticRegression(C=c, max_iter=3000).fit(z["train"], labels["train"])
        score = (clf.predict_proba(z["val"])[:, 1] if n_classes == 2
                 else clf.predict_proba(z["val"]))
        m = metrics(labels["val"], score, n_classes)
        key = m["roc_auc"] if n_classes == 2 else m["kappa"]
        if best is None or key > best[0]:
            best = (key, c, clf, m)
    _, c, clf, val = best
    score = clf.predict_proba(z["test"])[:, 1] if n_classes == 2 else clf.predict_proba(z["test"])
    return StrongProbeResult(model_name, dataset, split, c, val,
                             metrics(labels["test"], score, n_classes))
