# Converged linear probes

Analysis identifier: D33. Selection: `manifest.json`.

Results are reconstructed from saved ROC-AUC values; numerical diagnostics are checked against the reported criteria. Training gradients cannot be recomputed without the omitted features.

Primary inference supports equivalence within ±3 in 5/8 comparisons. Siena uses dependence-adjusted inference; DL uses seed intervals on one fixed split.

| Setting | Features | Contrast | Mean | Primary 95% interval | TOST p | Outcome |
|---|---|---|---:|---|---:|---|
| chbmit | logreg | last - lp | +0.19 | [-1.33, +1.71] | 0.00342835 | equivalent |
| chbmit | logreg | last - last_noise | -0.90 | [-2.41, +0.61] | 0.00902655 | equivalent |
| chbmit | logreg_z | last - lp | +0.61 | [-0.70, +1.92] | 0.00357464 | equivalent |
| chbmit | logreg_z | last - last_noise | +0.49 | [-2.64, +3.63] | 0.0453166 | equivalent |
| siena | logreg | last - lp | +2.87 | [-5.10, +10.83] | 0.482506 | unresolved |
| siena | logreg | last - last_noise | +1.82 | [-6.25, +9.88] | 0.352313 | unresolved |
| siena | logreg_z | last - lp | +0.38 | [-4.82, +5.59] | 0.11773 | unresolved |
| siena | logreg_z | last - last_noise | +0.46 | [-0.57, +1.49] | 0.00118809 | equivalent |

Recorded diagnostics:

```json
{
  "records": 60,
  "candidate_fits": 840,
  "selected_fits": 120,
  "nonconverged_candidates": 0,
  "nonconverged_selected": 0,
  "validation_auc_unstable_selected": 0,
  "boundary_selected": 45,
  "selected_C_counts": {
    "0.0001": 39,
    "0.001": 16,
    "0.01": 9,
    "0.1": 13,
    "1.0": 35,
    "10.0": 2,
    "100.0": 6
  }
}
```

The raw records store the solver tolerance, iteration cap and gradient diagnostics. They do not separately store ftol and gtol. For the pinned scikit-learn 1.6.1 L-BFGS implementation, gtol equals the passed tol and ftol is 64 times float64 machine epsilon; these values follow from the implementation, not independent runtime capture.
