# Matched probe tuning for two larger-dose Siena BIOT recipes

Protocol: notes/decisions.md D32, frozen at 222d090 before its runs. Additional analysis motivated by E29; not an external replication.
Command: `.venv/bin/python scripts/analysis/tuned_metrics.py`

Selection uses validation ROC-AUC only. Unit: mean of three seeds within each of five rotations. The correction uses the saved D31 Siena train/test ratio. ROC TOST margin is 3; no ROC margin is applied to AP or trapezoidal PR-AUC.

## Record and optimization checks

{"any_candidate_capped": 54, "candidate_capped": 263, "candidate_fits": 5400, "records": 90, "selected_capped": 0, "selected_fits": 180, "selected_max_epochs": 283}

A capped candidate is distinct from a capped selected configuration. Early stopping does not establish optimization convergence.

- Cell 2: matched EEG/noise adaptation steps across rotations: [51].
- Cell 5: matched EEG/noise adaptation steps across rotations: [96, 117, 141, 147, 153].

## roc_auc

| cell | features | contrast | mean | 95% t | 95% NB |
|---|---|---|---|---|---|
| Cell 2 | grid | last - lp | +2.4 | [-2.2, +7.0] | [-5.3, +10.0] |
| Cell 2 | grid | last - last_noise | +0.8 | [-3.6, +5.3] | [-6.5, +8.2] |
| Cell 2 | grid_z | last - lp | -1.0 | [-4.5, +2.6] | [-6.8, +4.9] |
| Cell 2 | grid_z | last - last_noise | +0.4 | [-2.3, +3.0] | [-4.0, +4.8] |
| Cell 5 | grid | last - lp | +3.1 | [-1.8, +8.0] | [-5.1, +11.2] |
| Cell 5 | grid | last - last_noise | +1.1 | [-1.8, +4.0] | [-3.7, +5.9] |
| Cell 5 | grid_z | last - lp | +0.8 | [-0.4, +2.0] | [-1.2, +2.8] |
| Cell 5 | grid_z | last - last_noise | +1.5 | [-0.7, +3.7] | [-2.1, +5.1] |

## avg_precision

| cell | features | contrast | mean | 95% t | 95% NB |
|---|---|---|---|---|---|
| Cell 2 | grid | last - lp | +0.3 | [-1.6, +2.3] | [-2.9, +3.6] |
| Cell 2 | grid | last - last_noise | -1.1 | [-4.4, +2.3] | [-6.6, +4.5] |
| Cell 2 | grid_z | last - lp | -0.6 | [-2.3, +1.0] | [-3.3, +2.0] |
| Cell 2 | grid_z | last - last_noise | -1.0 | [-4.2, +2.1] | [-6.3, +4.2] |
| Cell 5 | grid | last - lp | +1.2 | [-1.5, +3.9] | [-3.2, +5.6] |
| Cell 5 | grid | last - last_noise | -0.3 | [-2.4, +1.9] | [-3.8, +3.3] |
| Cell 5 | grid_z | last - lp | -0.4 | [-1.7, +1.0] | [-2.6, +1.9] |
| Cell 5 | grid_z | last - last_noise | -1.3 | [-4.2, +1.7] | [-6.1, +3.6] |

## pr_auc_trapz

| cell | features | contrast | mean | 95% t | 95% NB |
|---|---|---|---|---|---|
| Cell 2 | grid | last - lp | +0.3 | [-1.5, +2.2] | [-2.7, +3.3] |
| Cell 2 | grid | last - last_noise | -1.1 | [-4.4, +2.2] | [-6.5, +4.4] |
| Cell 2 | grid_z | last - lp | -0.6 | [-2.2, +0.9] | [-3.2, +2.0] |
| Cell 2 | grid_z | last - last_noise | -1.0 | [-4.2, +2.2] | [-6.3, +4.3] |
| Cell 5 | grid | last - lp | +1.1 | [-1.4, +3.7] | [-3.1, +5.3] |
| Cell 5 | grid | last - last_noise | -0.3 | [-2.4, +1.9] | [-3.8, +3.3] |
| Cell 5 | grid_z | last - lp | -0.4 | [-1.7, +0.9] | [-2.6, +1.7] |
| Cell 5 | grid_z | last - last_noise | -1.3 | [-4.2, +1.7] | [-6.1, +3.6] |
