"""D33 convex probe: the objective normalisation, the tie rule and the two flags.

The normalisation test is the important one. An earlier draft of the protocol used the SUMMED
cross-entropy plus ||w||^2/(2C). That has the same minimiser but a gradient n times larger, so against
the fixed 1e-5 acceptance threshold it marked converged fits as non-converged.
"""

import warnings

import numpy as np
import pytest
import torch
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression

from eegdrift.probe import ProbeSpec
from eegdrift.probe_grid import (
    LOGREG_CS,
    LOGREG_GRAD_TOL,
    LOGREG_MAX_ITER,
    LOGREG_STABLE_TOL,
    LOGREG_TOL,
    LOGREG_VARIANTS,
    _sk_objective,
    logreg_probe,
)


def _data(n=1200, d=16, seed=0):
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, d))
    w = rng.normal(size=d)
    y = (rng.uniform(size=n) < 1 / (1 + np.exp(-(X @ w)))).astype(np.float64)
    return X, y


@pytest.mark.parametrize("c", [1e-4, 1.0, 100.0])
def test_objective_matches_sklearn_normalisation(c):
    """F and its gradient are sklearn's MEAN-normalised ones, so the 1e-5 threshold is reachable."""
    X, y = _data()
    clf = LogisticRegression(C=c, solver="lbfgs", max_iter=LOGREG_MAX_ITER, tol=LOGREG_TOL).fit(X, y)
    w, b = clf.coef_.ravel(), float(clf.intercept_[0])
    f, gnorm = _sk_objective(X, y, w, b, c)
    n = len(y)
    # the objective equals sklearn's own loss function value at the same point
    bce = np.mean(np.logaddexp(0.0, -(2 * y - 1) * (X @ w + b)))
    assert f == pytest.approx(bce + (w @ w) / (2 * c * n), rel=1e-9)
    # at the optimum the normalised gradient clears the acceptance threshold; the summed one does not
    assert gnorm < LOGREG_GRAD_TOL
    assert gnorm * n > LOGREG_GRAD_TOL, "the summed form would fail converged fits (the bug this pins)"


def test_gradient_matches_finite_differences():
    X, y = _data(seed=1)
    c, eps = 1.0, 1e-6
    rng = np.random.default_rng(2)
    w, b = rng.normal(scale=0.3, size=X.shape[1]), 0.2   # away from the optimum: a real gradient
    n = len(y)
    resid = (1 / (1 + np.exp(-(X @ w + b))) - y) / n
    analytic = np.concatenate([X.T @ resid + w / (c * n), [resid.sum()]])
    for i in (0, 3, 7, X.shape[1]):                      # last index is the intercept
        up, dn = w.copy(), w.copy()
        bu, bd = b, b
        if i < len(w):
            up[i] += eps
            dn[i] -= eps
        else:
            bu, bd = b + eps, b - eps
        fd = (_sk_objective(X, y, up, bu, c)[0] - _sk_objective(X, y, dn, bd, c)[0]) / (2 * eps)
        assert fd == pytest.approx(analytic[i], abs=1e-8)


def _feats(X, y):
    n = len(y)
    cut, cut2 = n // 2, 3 * n // 4
    sl = {"train": slice(0, cut), "val": slice(cut, cut2), "test": slice(cut2, n)}
    return {k: (torch.tensor(X[s], dtype=torch.float16), torch.tensor(y[s], dtype=torch.float32))
            for k, s in sl.items()}


def _spec():
    return ProbeSpec(model="biot", dataset="chbmit", variant="logreg", seed=42, n_classes=2,
                     window_s=10, split="paper", backbone_mode="eval")


def test_records_both_flags_the_c_grid_and_the_boundary():
    X, y = _data(seed=3)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)
        out = logreg_probe(_feats(X, y), _spec(), LOGREG_VARIANTS, log=lambda *_a: None)
    assert set(out) == set(LOGREG_VARIANTS)
    for variant, (rec, arrays) in out.items():
        assert len(rec["configs"]) == len(LOGREG_CS)
        assert [r["C"] for r in rec["configs"]] == list(LOGREG_CS)   # every C's val score is kept
        assert rec["selected"]["C"] in LOGREG_CS
        assert rec["selected"]["at_grid_boundary"] == (rec["selected"]["C"] in (LOGREG_CS[0], LOGREG_CS[-1]))
        # the two flags are independent fields, never one derived from the other
        assert isinstance(rec["numerically_converged"], bool)
        assert isinstance(rec["prediction_stable"], bool)
        assert rec["prediction_stable"] == (abs(rec["val_refit_delta"]) < LOGREG_STABLE_TOL)
        assert "test_refit_delta" in rec          # diagnostic only
        assert rec["standardized"] == (variant == "logreg_z")
        assert rec["head_params"] == X.shape[1] + 1
        assert arrays["test_scores"].shape == (len(y) - 3 * len(y) // 4,)


def test_ties_take_the_smaller_c():
    """Constant features make every C score identically, so the winner must be the smallest."""
    n, d = 400, 4
    X = np.ones((n, d))
    y = np.resize([0.0, 1.0], n)
    out = logreg_probe(_feats(X, y), _spec(), ("logreg",), log=lambda *_a: None)
    assert out["logreg"][0]["selected"]["C"] == LOGREG_CS[0]
