"""Equal-budget, early-stopped linear probes on cached frozen features. D28 (notes/decisions.md "## D28")
froze the 16-configuration, 200-epoch search; D31 ("## D31") expands it to 30 configurations and 500 epochs
and is the primary tuned analysis. GRID_CODE_VERSION distinguishes the two in the result key.
Opt-in probe variants "grid" (raw features) and "grid_z" (features
standardized with TRAIN-split mean/std). New variants only: no existing probe number changes.

* Features are computed ONCE per (arm, seed): backbone in eval mode, exactly the parity probe's path
  (scale_input incl. input_norm -> prepare -> features(tap)), flattened (CBraMod 16 x S x 200),
  stored float16 in CPU memory. Mini-batches reach the GPU through one pinned staging buffer (the
  cache itself stays pageable: torch's pinned allocator rounds blocks up to a power of two, which
  would turn CBraMod's ~18 GB CHB-MIT train cache into 32 GB of locked host memory).
* Same search for every arm and variant: AdamW, lr in LRS x weight decay in WDS (30 configurations,
  which contain D28's 16 as a subset), batch 256, constant lr, BCE on logits, at most 500 epochs,
  early stop when val ROC-AUC has not
  improved by more than 1e-4 for 20 epochs (the reference moves only on such an improvement).
  All heads of all requested variants train in parallel in one data pass per epoch: same seeded
  shuffle, same initial weights (the "linear" probe's nn.Linear init at this seed), one AdamW
  parameter group (own state) per head. A stopped head gets no further step and no weight decay.
* Per variant: selected configuration = best val ROC-AUC over the 30 (ties: smaller lr, then
  smaller wd), selected epoch = its best val epoch (snapshot of that head's weights). Val and test
  metrics are computed only there. The test split is read once, after every choice is made.
"""

from __future__ import annotations

import time
from dataclasses import asdict, replace

import numpy as np
import torch
import torch.nn.functional as F
from sklearn.metrics import roc_auc_score
from torch import Tensor, nn

from eegdrift.models.protocols import EEGModel, scale_input
from eegdrift.probe import LOGIT_T, ProbeSpec, metrics

GRID_VARIANTS = ("grid", "grid_z")
GRID_CODE_VERSION = 2   # 1 = D28 (16 configs, 200 epochs); 2 = D31. In the result key of grid runs only.
LRS = (3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2)
WDS = (0.0, 1e-4, 1e-2, 1e-1, 1.0)
CONFIGS = tuple((lr, wd) for lr in LRS for wd in WDS)   # lr-major, ascending: index order IS the tie rule
BATCH, MAX_EPOCHS, PATIENCE, MIN_DELTA = 256, 500, 20, 1e-4
BETAS = (0.9, 0.999)
EVAL_BATCH = 1024   # scoring and statistics only; never changes a training step

Feats = dict[str, tuple[Tensor, Tensor]]


@torch.no_grad()
def cache_features(model: EEGModel, spec: ProbeSpec, data: dict[str, tuple[Tensor, Tensor]],
                   device: torch.device) -> Feats:
    """split -> (float16 [N, D] CPU features, labels), backbone in eval mode (probe._scores' path)."""
    model.module.to(device)
    model.encoder().eval()
    out = {}
    for split, (x, y) in data.items():
        buf = None
        for i in range(0, len(x), spec.batch):
            f = model.features(model.prepare(scale_input(x[i:i + spec.batch].to(device), spec.scale,
                                                         spec.input_norm)), spec.tap).flatten(1).half()
            if not torch.isfinite(f).all():
                raise ValueError(f"{split} features overflow float16 ({spec.model}, seed {spec.seed})")
            if buf is None:
                buf = torch.empty((len(x), f.shape[1]), dtype=torch.float16)
            buf[i:i + len(f)].copy_(f)
        out[split] = (buf, y)
    return out


def _mover(d: int, device: torch.device):
    """rows of a CPU float16 cache -> float32 on `device`, through one pinned staging buffer."""
    buf = torch.empty((max(BATCH, EVAL_BATCH), d), dtype=torch.float16, pin_memory=device.type == "cuda")

    def move(x: Tensor, idx: Tensor) -> Tensor:
        out = buf[:len(idx)]
        torch.index_select(x, 0, idx, out=out)
        return out.to(device).float()   # blocking copy (or, on CPU, .float() copies): buf is free again
    return move


@torch.no_grad()
def train_stats(x: Tensor, move) -> tuple[Tensor, Tensor]:
    """Per-feature mean/std of the TRAIN features (float64 sums; std floor 1e-6 as probe.Standardize)."""
    s1 = s2 = 0.0
    for i in range(0, len(x), EVAL_BATCH):
        f = move(x, torch.arange(i, min(i + EVAL_BATCH, len(x)))).double()
        s1, s2 = s1 + f.sum(0), s2 + (f * f).sum(0)
    mean = s1 / len(x)
    return mean.float(), (s2 / len(x) - mean * mean).clamp_min(0).sqrt().clamp_min(1e-6).float()


@torch.no_grad()
def _score(x: Tensor, params: dict, view, move) -> dict[str, np.ndarray]:
    """variant -> logits [N, H] for weights W [H, D], bias b [H]."""
    out = {v: [] for v in params}
    for i in range(0, len(x), EVAL_BATCH):
        xb = move(x, torch.arange(i, min(i + EVAL_BATCH, len(x))))
        for v, (w, b) in params.items():
            out[v].append((view(v, xb) @ w.t() + b).cpu().numpy())
    return {v: np.concatenate(o) for v, o in out.items()}


def fit_grid(feats: Feats, variants, seed: int, device: torch.device, log=print,
             max_epochs: int = MAX_EPOCHS) -> dict[str, tuple[dict, dict[str, np.ndarray]]]:
    """Binary only. feats: split -> (float16 [N, D] CPU features, labels). variant -> (record, arrays)."""
    variants = tuple(variants)
    if not variants or set(variants) - set(GRID_VARIANTS):
        raise ValueError(f"grid variants must be a subset of {GRID_VARIANTS}, got {variants}")
    xtr, ytr = feats["train"]
    n, d = xtr.shape
    move = _mover(d, device)
    mean, std = train_stats(xtr, move) if "grid_z" in variants else (None, None)

    def view(v: str, x: Tensor) -> Tensor:
        return x if v == "grid" else (x - mean) / std

    torch.manual_seed(seed)
    init = nn.Linear(d, 1)   # = the "linear" probe's head init at this seed (probe.py seeds, then builds)
    heads = {v: [(nn.Parameter(init.weight.detach()[0].clone().to(device)),
                  nn.Parameter(init.bias.detach().clone().to(device))) for _ in CONFIGS] for v in variants}
    opt = torch.optim.AdamW([{"params": list(heads[v][k]), "lr": lr, "weight_decay": wd}
                             for v in variants for k, (lr, wd) in enumerate(CONFIGS)], betas=BETAS,
                            fused=device.type == "cuda")   # 32 groups: one kernel each, not ~10
    st = {v: [{"val_curve": [], "train_loss": [], "best_val": -np.inf, "best_epoch": -1, "ref": -np.inf,
               "wait": 0, "stopped": False} for _ in CONFIGS] for v in variants}

    def stacked(v: str) -> tuple[Tensor, Tensor]:
        return torch.stack([w for w, _ in heads[v]]), torch.cat([b for _, b in heads[v]])

    best = {v: tuple(t.detach().clone() for t in stacked(v)) for v in variants}
    yv = feats["val"][1].numpy()
    gen = torch.Generator().manual_seed(seed)
    t0 = time.time()
    for epoch in range(max_epochs):
        if all(h["stopped"] for v in variants for h in st[v]):
            break
        loss_sum = {v: torch.zeros(len(CONFIGS), device=device) for v in variants}
        n_b = 0
        order = torch.randperm(n, generator=gen)
        for i in range(0, n, BATCH):
            idx = order[i:i + BATCH]
            x, yb = move(xtr, idx), ytr[idx].to(device).float()[:, None]
            opt.zero_grad(set_to_none=True)
            total = 0.0
            for v in variants:
                w, b = stacked(v)
                logits = view(v, x) @ w.t() + b
                per_head = F.binary_cross_entropy_with_logits(logits, yb.expand_as(logits),
                                                              reduction="none").mean(0)
                loss_sum[v] += per_head.detach()
                total = total + per_head.sum()   # head k's gradient = that of its own mean BCE
            total.backward()
            for v in variants:
                for (w, b), h in zip(heads[v], st[v], strict=True):
                    if h["stopped"]:
                        w.grad = b.grad = None   # AdamW skips parameters without a gradient
            opt.step()
            n_b += 1
        vs = _score(feats["val"][0], {v: stacked(v) for v in variants}, view, move)
        for v in variants:
            losses = (loss_sum[v] / n_b).tolist()
            for k, h in enumerate(st[v]):
                if h["stopped"]:
                    continue
                roc = float(roc_auc_score(yv, vs[v][:, k]))
                h["val_curve"].append(roc)
                h["train_loss"].append(losses[k])
                if roc > h["best_val"]:
                    h["best_val"], h["best_epoch"] = roc, epoch
                    best[v][0][k], best[v][1][k] = heads[v][k][0].detach(), heads[v][k][1].detach()[0]
                if roc > h["ref"] + MIN_DELTA:
                    h["ref"], h["wait"] = roc, 0
                else:
                    h["wait"] += 1
                h["stopped"] = h["wait"] >= PATIENCE
        log(f"[grid s{seed}] epoch {epoch} active "
            f"{sum(not h['stopped'] for v in variants for h in st[v])}/{len(variants) * len(CONFIGS)} "
            + " ".join(f"{v} best val {max(h['best_val'] for h in st[v]):.4f}" for v in variants))

    # every choice is made: per variant, best config (np.argmax = first max = smaller lr, then wd)
    sel = {v: int(np.argmax([h["best_val"] for h in st[v]])) for v in variants}
    sv = _score(feats["val"][0], best, view, move)   # same shapes as during training: identical logits
    ts = _score(feats["test"][0], {v: (best[v][0][sel[v]:sel[v] + 1], best[v][1][sel[v]:sel[v] + 1])
                                    for v in variants}, view, move)   # first and only test read
    yt = feats["test"][1].numpy()
    out = {}
    for v in variants:
        k, h = sel[v], st[v][sel[v]]
        sval, stest = sv[v][:, k], ts[v][:, 0]
        configs = [{"lr": lr, "weight_decay": wd, "best_epoch": c["best_epoch"], "best_val": c["best_val"],
                    "epochs_run": len(c["val_curve"]), "converged": _converged(c, max_epochs),
                    "val_curve": [round(r, 6) for r in c["val_curve"]],
                    "train_loss": [round(r, 6) for r in c["train_loss"]]}
                   for (lr, wd), c in zip(CONFIGS, st[v], strict=True)]
        record = {"type": "GridProbeResult",
                  "grid": {"lr": LRS, "weight_decay": WDS, "batch": BATCH, "max_epochs": max_epochs,
                           "patience": PATIENCE, "min_delta": MIN_DELTA, "betas": BETAS, "schedule": "constant",
                           "loss": "BCE on logits", "standardized": v == "grid_z", "features": "float16",
                           "version": GRID_CODE_VERSION},
                  "head_params": d + 1, "configs": configs,
                  "selected": {"index": k, "lr": CONFIGS[k][0], "weight_decay": CONFIGS[k][1]},
                  "best_epoch": h["best_epoch"], "best_val": h["best_val"], "converged": configs[k]["converged"],
                  "epochs_run": max(c["epochs_run"] for c in configs),
                  "val_at_best": metrics(yv, sval, 2, LOGIT_T), "test_at_best": metrics(yt, stest, 2, LOGIT_T),
                  "seconds": time.time() - t0}
        arrays = {"y_test": yt.astype(np.int8), "scores_best": stest.astype(np.float32),
                  "y_val": yv.astype(np.int8), "scores_val_best": sval.astype(np.float32)}
        out[v] = (record, arrays)
    return out


def _converged(h: dict, max_epochs: int) -> bool:
    """D28: early stopping fired before epoch `max_epochs` (patience used up at the last epoch: no)."""
    return h["stopped"] and len(h["val_curve"]) < max_epochs


def grid_probe(model: EEGModel, spec: ProbeSpec, data: dict[str, tuple[Tensor, Tensor]], device: torch.device,
               variants=GRID_VARIANTS, log=print, max_epochs: int = MAX_EPOCHS,
               feats: Feats | None = None) -> dict[str, tuple[dict, dict]]:
    """One feature cache, every requested grid variant. spec: the probe template (its epochs/lr/wd/
    eta_min/label_smoothing are not used; the record's "grid" holds what ran; spec.batch sets only
    the feature pass)."""
    if spec.backbone_mode != "eval" or spec.n_classes != 2:
        raise ValueError("grid probes cache eval-mode features of a binary task: use --backbone-mode eval")
    t0 = time.time()
    feats = feats if feats is not None else cache_features(model, spec, data, device)
    cache_s = time.time() - t0
    log(f"[grid] {spec.model}/{spec.dataset} s{spec.seed}: features {tuple(feats['train'][0].shape)} "
        f"cached in {cache_s:.0f}s")
    out = fit_grid(feats, variants, spec.seed, device, log, max_epochs)
    for v, (rec, _) in out.items():
        rec.update(spec=asdict(replace(spec, variant=v)), cache_seconds=cache_s)
    return out


# ---------- D33: convex probe (notes/decisions.md "## D33" + its amendment and clarifications) ----------
LOGREG_VARIANTS = ("logreg", "logreg_z")
LOGREG_CS = (1e-4, 1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0)
LOGREG_MAX_ITER, LOGREG_TOL, LOGREG_REFIT_TOL = 20000, 1e-6, 1e-9
LOGREG_GRAD_TOL = 1e-5     # on the MEAN-normalised objective sklearn minimises, not the summed one
LOGREG_STABLE_TOL = 1e-3   # 0.001 absolute ROC-AUC = 0.1 percentage points, on VALIDATION
LOGREG_CODE_VERSION = 1


def _sk_objective(X: np.ndarray, y: np.ndarray, w: np.ndarray, b: float, c: float) -> tuple[float, float]:
    """scikit-learn 1.6.1's lbfgs objective and its gradient infinity-norm, unweighted samples.

        F(w, b) = (1/n) sum_i BCE(y_i, w.x_i + b) + ||w||^2 / (2 C n),   intercept unpenalised.

    Verified against the installed source: l2_reg_strength = 1/(C * sw_sum) with sw_sum = n_samples
    (_logistic.py:447), loss.sum()/sw_sum + 0.5*l2_reg_strength*||w||^2 (_linear_loss.py:323, :207),
    grad_pointwise /= sw_sum (_linear_loss.py:326). The summed form has the same minimiser but scales
    the gradient by n; normalization must match the convergence threshold.
    """
    n = len(y)
    raw = X @ w + b
    # log(1 + exp(-|raw|)) + max(-raw, 0) is log(1+exp(-raw)) without overflow
    bce = np.mean(np.log1p(np.exp(-np.abs(raw))) + np.maximum(-raw, 0.0) + (1.0 - y) * raw)
    strength = 1.0 / (c * n)
    f = float(bce + 0.5 * strength * (w @ w))
    resid = (1.0 / (1.0 + np.exp(-raw)) - y) / n
    g = np.concatenate([X.T @ resid + strength * w, [resid.sum()]])
    return f, float(np.max(np.abs(g)))


def logreg_probe(feats: Feats, spec: ProbeSpec, variants=LOGREG_VARIANTS,
                 log=print) -> dict[str, tuple[dict, dict]]:
    """Validation-selected L2 logistic regression on one arm's cached features (D33).

    Per variant: fit every C in LOGREG_CS, select on validation ROC-AUC (ties take the smaller C), then
    score test after selection. Records every C's validation score, whether the winner sits at a grid boundary,
    `numerically_converged` (n_iter < max_iter, no ConvergenceWarning, gradient inf-norm < LOGREG_GRAD_TOL)
    and `prediction_stable` (a LOGREG_REFIT_TOL refit moves validation ROC-AUC by < LOGREG_STABLE_TOL).
    The same refit comparison on test is recorded as a diagnostic only and never selects or excludes.
    """
    import warnings  # noqa: PLC0415

    from sklearn.exceptions import ConvergenceWarning  # noqa: PLC0415
    from sklearn.linear_model import LogisticRegression  # noqa: PLC0415

    if set(variants) - set(LOGREG_VARIANTS):
        raise ValueError(f"logreg variants must be a subset of {LOGREG_VARIANTS}, got {tuple(variants)}")
    X = {k: v[0].numpy().astype(np.float64) for k, v in feats.items()}
    y = {k: v[1].numpy().astype(np.float64).ravel() for k, v in feats.items()}
    out: dict[str, tuple[dict, dict]] = {}
    for variant in variants:
        t0 = time.time()
        if variant == "logreg_z":            # train-only statistics, this arm's own features
            mu, sd = X["train"].mean(0), X["train"].std(0)
            sd = np.where(sd > 0, sd, 1.0)
            Z = {k: (v - mu) / sd for k, v in X.items()}
        else:
            Z = X
        per_c, best = [], None
        for c in LOGREG_CS:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always", ConvergenceWarning)
                clf = LogisticRegression(C=c, solver="lbfgs", penalty="l2", max_iter=LOGREG_MAX_ITER,
                                         tol=LOGREG_TOL).fit(Z["train"], y["train"])
            warned = any(issubclass(w.category, ConvergenceWarning) for w in caught)
            n_iter = int(np.ravel(clf.n_iter_)[0])
            f, gnorm = _sk_objective(Z["train"], y["train"], clf.coef_.ravel(), float(clf.intercept_[0]), c)
            val = metrics(y["val"], clf.decision_function(Z["val"]), 2)   # linear scores, not probabilities
            per_c.append({"C": c, "val_roc_auc": val["roc_auc"], "n_iter": n_iter, "warned": warned,
                          "objective": f, "grad_inf_norm": gnorm,
                          "numerically_converged": bool(n_iter < LOGREG_MAX_ITER and not warned
                                                        and gnorm < LOGREG_GRAD_TOL)})
            if best is None or val["roc_auc"] > best[0] + 1e-12:   # ties keep the smaller C (grid ascends)
                best = (val["roc_auc"], c, clf, val)
        _, c_sel, clf, val_sel = best
        refit = LogisticRegression(C=c_sel, solver="lbfgs", penalty="l2", max_iter=LOGREG_MAX_ITER,
                                   tol=LOGREG_REFIT_TOL).fit(Z["train"], y["train"])
        val_refit = metrics(y["val"], refit.decision_function(Z["val"]), 2)
        test = metrics(y["test"], clf.decision_function(Z["test"]), 2)
        test_refit = metrics(y["test"], refit.decision_function(Z["test"]), 2)
        sel = next(r for r in per_c if r["C"] == c_sel)
        rec = {
            "type": "logreg", "spec": {**asdict(replace(spec, variant=variant))},
            "version": LOGREG_CODE_VERSION, "solver": "lbfgs", "penalty": "l2",
            "max_iter": LOGREG_MAX_ITER, "tol": LOGREG_TOL, "refit_tol": LOGREG_REFIT_TOL,
            "grad_tol": LOGREG_GRAD_TOL, "stable_tol": LOGREG_STABLE_TOL,
            "standardized": variant == "logreg_z", "Cs": list(LOGREG_CS), "configs": per_c,
            "selected": {"C": c_sel, "index": LOGREG_CS.index(c_sel),
                         "at_grid_boundary": c_sel in (LOGREG_CS[0], LOGREG_CS[-1])},
            "n_iter": sel["n_iter"], "objective": sel["objective"], "grad_inf_norm": sel["grad_inf_norm"],
            "numerically_converged": sel["numerically_converged"],
            "prediction_stable": bool(abs(val_refit["roc_auc"] - val_sel["roc_auc"]) < LOGREG_STABLE_TOL),
            "val_refit_delta": float(val_refit["roc_auc"] - val_sel["roc_auc"]),
            "test_refit_delta": float(test_refit["roc_auc"] - test["roc_auc"]),   # diagnostic only
            "head_params": int(clf.coef_.size + 1), "val_at_best": val_sel, "test_at_best": test,
            "n_train": int(len(y["train"])), "seconds": round(time.time() - t0, 1),
        }
        log(f"[logreg] {variant}: C={c_sel:g}"
            f"{' (grid edge)' if rec['selected']['at_grid_boundary'] else ''} "
            f"n_iter={sel['n_iter']} |g|={sel['grad_inf_norm']:.2e} "
            f"conv={rec['numerically_converged']} stable={rec['prediction_stable']} "
            f"test_auroc={test['roc_auc']:.4f}")
        out[variant] = (rec, {"test_scores": clf.decision_function(Z["test"]).astype(np.float32)})
    return out
