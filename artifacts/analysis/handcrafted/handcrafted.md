# E20-free: hand-crafted baseline and robustness re-scores (descriptive, appendix; D25)

Pre-registered rule (completeness-audit E20-free): **descriptive, appendix**. No verdict is drawn;
D18-form strings below are descriptive re-readings, the D24 verdicts stay primary.

Baseline: log band power (delta 0.5-4, theta 4-8, alpha 8-13, beta 13-30, gamma 30-45 Hz), log line
length and log variance per channel (112 features) -> standardized logistic regression, C from [1e-06, 1e-05, 0.0001, 0.001, 0.01, 0.1, 1.0, 10.0, 100.0] by validation ROC-AUC. ROC/AP x100; PR lift = AP / prevalence.

## Checks
- chbmit/rot0: 57761 test windows, 384 positives = probe test set
- chbmit/rot1: 68822 test windows, 229 positives = probe test set
- chbmit/rot2: 57354 test windows, 123 positives = probe test set
- chbmit/rot3: 50141 test windows, 162 positives = probe test set
- chbmit/rot4: 90950 test windows, 147 positives = probe test set
- siena/rot0: 7483 test windows, 73 positives = probe test set
- siena/rot1: 15332 test windows, 66 positives = probe test set
- siena/rot2: 5177 test windows, 51 positives = probe test set
- siena/rot3: 18449 test windows, 100 positives = probe test set
- siena/rot4: 4308 test windows, 39 positives = probe test set
- siena_filt/rot0: 7483 test windows, 73 positives = probe test set
- siena_filt/rot1: 15332 test windows, 66 positives = probe test set
- siena_filt/rot2: 5177 test windows, 51 positives = probe test set
- siena_filt/rot3: 18449 test windows, 100 positives = probe test set
- siena_filt/rot4: 4308 test windows, 39 positives = probe test set
- chbmit/paper upstream labels: 16964 test windows, 252 positives = P1E test set
- every model ROC recomputed from the saved scores equals its record (|diff| <= 1e-6): 590 run-heads

## 1. Baseline per split (test)

| setting | split | labels | C | val ROC | test ROC | AP | PR lift | bal-acc @0.5 | bal-acc @val thr | ROC, >=50% labels | test n / pos |
|---|---|---|---|---|---|---|---|---|---|---|---|
| chbmit | rot0 | overlap | 0.001 | 92.8 | 66.6 | 16.1 | 24.2 | 50.0 | 62.3 | 67.6 | 57761 / 384 |
| chbmit | rot1 | overlap | 1e-06 | 95.0 | 88.7 | 4.1 | 12.4 | 50.0 | 80.8 | 90.5 | 68822 / 229 |
| chbmit | rot2 | overlap | 0.001 | 70.4 | 90.0 | 8.8 | 41.0 | 65.7 | 79.5 | 92.0 | 57354 / 123 |
| chbmit | rot3 | overlap | 0.0001 | 91.4 | 63.2 | 3.8 | 11.7 | 50.0 | 57.8 | 67.1 | 50141 / 162 |
| chbmit | rot4 | overlap | 1e-06 | 66.7 | 89.2 | 1.4 | 8.4 | 50.0 | 77.6 | 91.0 | 90950 / 147 |
| siena | rot0 | overlap | 1e-05 | 89.3 | 78.3 | 2.1 | 2.2 | 50.0 | 72.8 | 78.1 | 7483 / 73 |
| siena | rot1 | overlap | 0.001 | 72.9 | 89.9 | 14.5 | 33.7 | 79.7 | 86.8 | 91.2 | 15332 / 66 |
| siena | rot2 | overlap | 0.001 | 90.7 | 67.3 | 1.7 | 1.7 | 52.1 | 60.0 | 68.2 | 5177 / 51 |
| siena | rot3 | overlap | 0.001 | 90.6 | 88.6 | 16.9 | 31.3 | 53.0 | 70.3 | 91.0 | 18449 / 100 |
| siena | rot4 | overlap | 0.01 | 88.3 | 92.7 | 30.1 | 33.2 | 52.6 | 81.8 | 93.8 | 4308 / 39 |
| siena_filt | rot0 | overlap | 1e-06 | 89.3 | 76.8 | 2.0 | 2.0 | 50.0 | 70.8 | 76.4 | 7483 / 73 |
| siena_filt | rot1 | overlap | 10 | 85.7 | 86.1 | 6.8 | 15.9 | 80.2 | 82.4 | 87.1 | 15332 / 66 |
| siena_filt | rot2 | overlap | 0.001 | 90.2 | 76.7 | 2.3 | 2.3 | 50.9 | 61.7 | 77.6 | 5177 / 51 |
| siena_filt | rot3 | overlap | 0.01 | 91.8 | 87.3 | 22.6 | 41.7 | 54.5 | 71.1 | 90.0 | 18449 / 100 |
| siena_filt | rot4 | overlap | 0.01 | 89.1 | 93.3 | 28.8 | 31.8 | 55.1 | 82.1 | 94.1 | 4308 / 39 |
| chbmit | paper | upstream | 0.001 | 95.9 | 90.3 | 42.8 | 28.8 | 50.0 | 81.3 | - | 16964 / 252 |
| chbmit | paper | overlap | 0.001 | 95.4 | 90.5 | 43.7 | 64.3 | 50.0 | 84.7 | 94.3 | 16758 / 114 |

- chbmit: baseline test ROC over rotations 79.5 ± 6.0 (mean ± SEM, n=5)
- siena: baseline test ROC over rotations 83.4 ± 4.7 (mean ± SEM, n=5)
- siena_filt: baseline test ROC over rotations 84.0 ± 3.2 (mean ± SEM, n=5)
- Reference: cbramod-check §4 reported 91.2 for log band power + LR (C=0.01, 5 bands incl. 30-70 Hz,
  train = paper-train cases with negatives subsampled to 3,000, test = chb21-24); not the same windows.

### C-grid sensitivity: first run (C 1e-4..100) vs final grid (1e-6..100)

| fit | C, first | test ROC, first | C, final | test ROC, final |
|---|---|---|---|---|
| chbmit-rot0-overlap | 0.001 | 66.6 | 0.001 | 66.6 |
| chbmit-rot1-overlap | 0.0001 | 83.4 | 1e-06 | 88.7 |
| chbmit-rot2-overlap | 0.001 | 90.0 | 0.001 | 90.0 |
| chbmit-rot3-overlap | 0.0001 | 63.2 | 0.0001 | 63.2 |
| chbmit-rot4-overlap | 0.0001 | 89.5 | 1e-06 | 89.2 |
| siena-rot0-overlap | 0.0001 | 81.7 | 1e-05 | 78.3 |
| siena-rot1-overlap | 0.001 | 89.9 | 0.001 | 89.9 |
| siena-rot2-overlap | 0.001 | 67.3 | 0.001 | 67.3 |
| siena-rot3-overlap | 0.001 | 88.6 | 0.001 | 88.6 |
| siena-rot4-overlap | 0.01 | 92.7 | 0.01 | 92.7 |
| siena_filt-rot0-overlap | 0.0001 | 79.9 | 1e-06 | 76.8 |
| siena_filt-rot1-overlap | 10 | 86.1 | 10 | 86.1 |
| siena_filt-rot2-overlap | 0.001 | 76.7 | 0.001 | 76.7 |
| siena_filt-rot3-overlap | 0.01 | 87.3 | 0.01 | 87.3 |
| siena_filt-rot4-overlap | 0.01 | 93.3 | 0.01 | 93.3 |
| chbmit-paper-upstream | 0.001 | 90.3 | 0.001 | 90.3 |
| chbmit-paper-overlap | 0.001 | 90.5 | 0.001 | 90.5 |

## 2. Baseline vs probes per rotation (test ROC x100; probes = mean of the 3 D24-A seeds)

### chbmit

| row | rot0 | rot1 | rot2 | rot3 | rot4 | mean ± SEM | arm - baseline: mean, rotations > 0 |
|---|---|---|---|---|---|---|---|
| hand-crafted LR | 66.6 | 88.7 | 90.0 | 63.2 | 89.2 | 79.5 ± 6.0 | |
| biot lp | 61.0 | 63.6 | 90.0 | 40.9 | 69.9 | 65.1 ± 7.9 | -14.5, 0/5 |
| biot lp_randinit | 54.5 | 61.8 | 85.1 | 64.0 | 69.7 | 67.0 ± 5.1 | -12.5, 1/5 |
| biot last | 62.6 | 66.6 | 90.9 | 39.8 | 74.9 | 67.0 ± 8.3 | -12.6, 1/5 |
| biot last_randinit | 54.3 | 62.0 | 85.1 | 64.2 | 70.1 | 67.1 ± 5.2 | -12.4, 1/5 |
| biot all | 65.3 | 81.2 | 94.8 | 56.6 | 85.9 | 76.8 ± 6.9 | -2.8, 1/5 |
| cbramod lp | 72.0 | 83.8 | 88.9 | 75.9 | 87.6 | 81.6 ± 3.3 | +2.1, 2/5 |
| cbramod lp_randinit | 66.0 | 74.6 | 85.7 | 71.8 | 82.7 | 76.2 ± 3.6 | -3.4, 1/5 |
| cbramod last | 71.5 | 84.3 | 88.9 | 75.8 | 87.5 | 81.6 ± 3.4 | +2.1, 2/5 |
| cbramod last_randinit | 68.3 | 76.4 | 85.2 | 74.2 | 81.9 | 77.2 ± 3.0 | -2.3, 2/5 |
| cbramod all | 75.8 | 85.6 | 89.4 | 76.3 | 89.1 | 83.2 ± 3.0 | +3.7, 2/5 |

### siena

| row | rot0 | rot1 | rot2 | rot3 | rot4 | mean ± SEM | arm - baseline: mean, rotations > 0 |
|---|---|---|---|---|---|---|---|
| hand-crafted LR | 78.3 | 89.9 | 67.3 | 88.6 | 92.7 | 83.4 ± 4.7 | |
| biot lp | 64.0 | 36.3 | 60.1 | 35.0 | 61.3 | 51.3 ± 6.4 | -32.0, 0/5 |
| biot lp_randinit | 62.9 | 81.9 | 69.2 | 61.5 | 61.6 | 67.4 ± 3.9 | -15.9, 1/5 |
| biot last | 71.5 | 54.6 | 63.5 | 45.0 | 68.3 | 60.6 ± 4.8 | -22.8, 0/5 |
| biot last_randinit | 63.8 | 82.7 | 69.8 | 60.5 | 62.0 | 67.8 ± 4.0 | -15.6, 1/5 |
| biot all | 70.8 | 65.6 | 69.0 | 67.0 | 83.4 | 71.2 ± 3.2 | -12.2, 1/5 |
| cbramod lp | 81.8 | 79.8 | 75.0 | 80.8 | 89.6 | 81.4 ± 2.4 | -1.9, 2/5 |
| cbramod lp_randinit | 77.0 | 79.6 | 60.3 | 80.8 | 74.4 | 74.4 ± 3.7 | -8.9, 0/5 |
| cbramod last | 81.3 | 80.2 | 75.6 | 81.7 | 89.7 | 81.7 ± 2.3 | -1.7, 2/5 |
| cbramod last_randinit | 74.7 | 77.3 | 62.1 | 79.5 | 76.6 | 74.0 ± 3.1 | -9.3, 0/5 |
| cbramod all | 87.2 | 85.4 | 69.5 | 88.9 | 87.5 | 83.7 ± 3.6 | +0.3, 3/5 |

### siena_filt

| row | rot0 | rot1 | rot2 | rot3 | rot4 | mean ± SEM | arm - baseline: mean, rotations > 0 |
|---|---|---|---|---|---|---|---|
| hand-crafted LR | 76.8 | 86.1 | 76.7 | 87.3 | 93.3 | 84.0 ± 3.2 | |
| biot lp | 85.0 | 44.3 | 73.3 | 72.9 | 73.3 | 69.8 ± 6.8 | -14.3, 1/5 |
| biot lp_randinit | 61.7 | 90.5 | 64.1 | 64.0 | 63.7 | 68.8 ± 5.4 | -15.2, 1/5 |
| biot last | 86.3 | 53.2 | 74.1 | 77.9 | 77.7 | 73.9 ± 5.5 | -10.1, 1/5 |
| biot last_randinit | 62.0 | 90.3 | 64.9 | 64.1 | 64.6 | 69.2 ± 5.3 | -14.8, 1/5 |
| biot all | 70.6 | 71.9 | 67.7 | 81.3 | 80.0 | 74.3 ± 2.7 | -9.7, 0/5 |
| cbramod lp | 91.9 | 89.4 | 81.1 | 90.5 | 94.5 | 89.5 ± 2.3 | +5.5, 5/5 |
| cbramod lp_randinit | 75.7 | 82.7 | 73.8 | 85.7 | 82.2 | 80.0 ± 2.3 | -4.0, 0/5 |
| cbramod last | 92.2 | 89.3 | 81.3 | 90.7 | 94.6 | 89.6 ± 2.3 | +5.6, 5/5 |
| cbramod last_randinit | 77.0 | 81.5 | 72.9 | 85.5 | 77.7 | 78.9 ± 2.1 | -5.1, 1/5 |
| cbramod all | 91.1 | 89.5 | 77.9 | 92.5 | 93.2 | 88.8 ± 2.8 | +4.8, 4/5 |

## 3. Paper split (test chb23-24): P1E arms vs the baseline (test ROC x100, mean ± SEM over 5 seeds)

| row | linear head | mlp_fullft head |
|---|---|---|
| biot lp | 55.0 ± 0.4 | 56.1 ± 0.1 |
| biot last | 54.4 ± 1.1 | 54.9 ± 1.2 |
| biot lp_randinit | 90.1 ± 0.2 | 88.5 ± 0.2 |
| biot last_randinit | 90.2 ± 0.2 | 88.5 ± 0.2 |
| cbramod lp | 92.0 ± 0.0 | 91.7 ± 0.3 |
| cbramod last | 92.0 ± 0.1 | 91.7 ± 0.2 |
| cbramod lp_randinit | 85.6 ± 0.7 | 89.5 ± 0.4 |
| cbramod last_randinit | 83.5 ± 0.3 | 89.7 ± 0.9 |
| hand-crafted LR, upstream labels | 90.3 (one fit) | |
| hand-crafted LR, overlap labels | 90.5 (one fit) | |

P1E uses upstream labels with the oversampled windows kept in test (the paper's protocol); the overlap-label row uses the corrected labels (grid windows only in val/test), as P1F will.

## 4. Robustness re-scores of the D24-A contrasts (linear head; per-rotation seed means)

Primary = ROC at the val-selected epoch with >=1-sample overlap labels (the D24-A reading). Re-scores:
ROC from scores_last; ROC with >=50%-overlap test labels; AP x100 and PR lift (paired per rotation).
Strings apply the D18 form (|mean| > 3, sign in >= 4/5) and are descriptive; AP and lift get no string.
Balanced accuracy at a validation-chosen threshold: NOT computed for the probes (no validation
scores before E25).

| setting | model | contrast | primary ROC | ROC, scores_last | ROC, >=50% labels | AP x100 | PR lift | string changes vs primary |
|---|---|---|---|---|---|---|---|---|
| chbmit | biot | last - lp | +1.9 (4/5 > 0) no difference shown | +1.9 (4/5 > 0) no difference shown | +1.9 (4/5 > 0) no difference shown | +0.6 (5/5 > 0) | +2.95 (5/5 > 0) | none |
| chbmit | biot | last_randinit - last | +0.2 (1/5 > 0) no difference shown | +3.2 (2/5 > 0) no difference shown | +0.3 (1/5 > 0) no difference shown | +8.2 (5/5 > 0) | +29.22 (5/5 > 0) | none |
| chbmit | biot | lp - lp_randinit | -2.0 (4/5 > 0) no difference shown | -5.1 (3/5 > 0) no difference shown | -2.0 (3/5 > 0) no difference shown | -8.9 (0/5 > 0) | -32.20 (0/5 > 0) | none |
| chbmit | biot | D17 last_randinit - lp_randinit | +0.1 (4/5 > 0) random features explain it | +0.0 (3/5 > 0) random features explain it | +0.1 (4/5 > 0) random features explain it | -0.0 (3/5 > 0) | -0.02 (3/5 > 0) | none |
| chbmit | cbramod | last - lp | -0.0 (2/5 > 0) no difference shown | -0.0 (2/5 > 0) no difference shown | -0.0 (1/5 > 0) no difference shown | +0.3 (4/5 > 0) | +0.85 (4/5 > 0) | none |
| chbmit | cbramod | last_randinit - last | -4.4 (0/5 > 0) second term wins | -6.8 (0/5 > 0) second term wins | -4.5 (0/5 > 0) second term wins | -14.4 (0/5 > 0) | -51.01 (0/5 > 0) | none |
| chbmit | cbramod | lp - lp_randinit | +5.5 (5/5 > 0) first term wins | +6.6 (5/5 > 0) first term wins | +5.8 (5/5 > 0) first term wins | +16.0 (5/5 > 0) | +56.05 (5/5 > 0) | none |
| chbmit | cbramod | D17 last_randinit - lp_randinit | +1.0 (3/5 > 0) random features explain it | -0.2 (2/5 > 0) random features explain it | +1.2 (3/5 > 0) random features explain it | +1.9 (4/5 > 0) | +5.89 (4/5 > 0) | none |
| siena | biot | last - lp | +9.2 (5/5 > 0) first term wins | +8.3 (5/5 > 0) first term wins | +9.6 (5/5 > 0) first term wins | +0.5 (5/5 > 0) | +0.81 (5/5 > 0) | none |
| siena | biot | last_randinit - last | +7.2 (3/5 > 0) no difference shown | +7.0 (3/5 > 0) no difference shown | +7.8 (3/5 > 0) no difference shown | +4.4 (3/5 > 0) | +9.31 (3/5 > 0) | none |
| siena | biot | lp - lp_randinit | -16.1 (1/5 > 0) second term wins | -15.3 (1/5 > 0) second term wins | -17.1 (2/5 > 0) no difference shown | -4.9 (2/5 > 0) | -10.09 (2/5 > 0) | >=50% |
| siena | biot | D17 last_randinit - lp_randinit | +0.3 (4/5 > 0) random features explain it | -0.0 (3/5 > 0) random features explain it | +0.3 (4/5 > 0) random features explain it | +0.0 (3/5 > 0) | +0.04 (3/5 > 0) | none |
| siena | cbramod | last - lp | +0.3 (4/5 > 0) no difference shown | +0.5 (5/5 > 0) no difference shown | +0.2 (4/5 > 0) no difference shown | +0.3 (3/5 > 0) | +0.42 (3/5 > 0) | none |
| siena | cbramod | last_randinit - last | -7.6 (0/5 > 0) second term wins | -9.6 (0/5 > 0) second term wins | -8.1 (0/5 > 0) second term wins | -6.0 (2/5 > 0) | -6.71 (2/5 > 0) | none |
| siena | cbramod | lp - lp_randinit | +7.0 (4/5 > 0) first term wins | +9.4 (5/5 > 0) first term wins | +7.6 (5/5 > 0) first term wins | +6.3 (3/5 > 0) | +7.62 (3/5 > 0) | none |
| siena | cbramod | D17 last_randinit - lp_randinit | -0.4 (2/5 > 0) random features explain it | +0.3 (3/5 > 0) random features explain it | -0.3 (2/5 > 0) random features explain it | +0.7 (3/5 > 0) | +1.34 (3/5 > 0) | none |
| siena_filt | biot | last - lp | +4.1 (5/5 > 0) first term wins | +3.5 (5/5 > 0) first term wins | +4.4 (5/5 > 0) first term wins | -0.2 (3/5 > 0) | +0.32 (3/5 > 0) | none |
| siena_filt | biot | last_randinit - last | -4.7 (1/5 > 0) second term wins | -5.2 (1/5 > 0) second term wins | -4.4 (1/5 > 0) second term wins | -0.9 (2/5 > 0) | +2.06 (2/5 > 0) | none |
| siena_filt | biot | lp - lp_randinit | +1.0 (4/5 > 0) no difference shown | +2.0 (4/5 > 0) no difference shown | +0.4 (4/5 > 0) no difference shown | +0.9 (3/5 > 0) | -2.87 (3/5 > 0) | none |
| siena_filt | biot | D17 last_randinit - lp_randinit | +0.4 (4/5 > 0) random features explain it | +0.4 (5/5 > 0) random features explain it | +0.4 (4/5 > 0) random features explain it | -0.2 (3/5 > 0) | -0.50 (3/5 > 0) | none |
| siena_filt | cbramod | last - lp | +0.1 (4/5 > 0) no difference shown | +0.1 (4/5 > 0) no difference shown | +0.1 (4/5 > 0) no difference shown | +0.9 (4/5 > 0) | +0.51 (4/5 > 0) | none |
| siena_filt | cbramod | last_randinit - last | -10.7 (0/5 > 0) second term wins | -15.0 (0/5 > 0) second term wins | -10.8 (0/5 > 0) second term wins | -21.1 (0/5 > 0) | -30.32 (0/5 > 0) | none |
| siena_filt | cbramod | lp - lp_randinit | +9.4 (5/5 > 0) first term wins | +14.6 (5/5 > 0) first term wins | +9.7 (5/5 > 0) first term wins | +19.7 (5/5 > 0) | +28.98 (5/5 > 0) | none |
| siena_filt | cbramod | D17 last_randinit - lp_randinit | -1.1 (1/5 > 0) random features explain it | -0.3 (2/5 > 0) random features explain it | -1.0 (2/5 > 0) random features explain it | -0.4 (2/5 > 0) | -0.84 (2/5 > 0) | none |

### Per-rotation paired differences (x100; AP in AP points, lift in lift units)

| setting | model | contrast | metric | rot0 | rot1 | rot2 | rot3 | rot4 |
|---|---|---|---|---|---|---|---|---|
| chbmit | biot | last - lp | roc_best | +1.7 | +3.1 | +0.9 | -1.1 | +5.0 |
| chbmit | biot | last - lp | roc_last | +1.7 | +3.1 | +0.9 | -1.1 | +5.0 |
| chbmit | biot | last - lp | roc50_best | +1.7 | +3.0 | +0.8 | -1.2 | +5.2 |
| chbmit | biot | last - lp | ap_best | +0.1 | +0.1 | +3.0 | +0.0 | +0.1 |
| chbmit | biot | last - lp | lift_best | +0.09 | +0.23 | +14.01 | +0.02 | +0.42 |
| chbmit | biot | last_randinit - last | roc_best | -8.3 | -4.7 | -5.8 | +24.4 | -4.9 |
| chbmit | biot | last_randinit - last | roc_last | -9.7 | -8.3 | -5.1 | +24.7 | +14.3 |
| chbmit | biot | last_randinit - last | roc50_best | -9.2 | -4.6 | -6.2 | +25.6 | -4.3 |
| chbmit | biot | last_randinit - last | ap_best | +4.9 | +14.1 | +14.2 | +6.3 | +1.7 |
| chbmit | biot | last_randinit - last | lift_best | +7.42 | +42.26 | +66.26 | +19.42 | +10.75 |
| chbmit | biot | lp - lp_randinit | roc_best | +6.5 | +1.8 | +4.9 | -23.1 | +0.2 |
| chbmit | biot | lp - lp_randinit | roc_last | +7.9 | +5.4 | +4.3 | -23.5 | -19.4 |
| chbmit | biot | lp - lp_randinit | roc50_best | +7.4 | +1.8 | +5.4 | -24.2 | -0.5 |
| chbmit | biot | lp - lp_randinit | ap_best | -5.1 | -14.3 | -17.1 | -6.3 | -1.8 |
| chbmit | biot | lp - lp_randinit | lift_best | -7.72 | -42.84 | -79.83 | -19.44 | -11.16 |
| chbmit | biot | last_randinit - lp_randinit | roc_best | -0.2 | +0.2 | +0.1 | +0.1 | +0.4 |
| chbmit | biot | last_randinit - lp_randinit | roc_last | -0.2 | +0.1 | +0.1 | +0.1 | -0.0 |
| chbmit | biot | last_randinit - lp_randinit | roc50_best | -0.2 | +0.2 | +0.0 | +0.2 | +0.4 |
| chbmit | biot | last_randinit - lp_randinit | ap_best | -0.1 | -0.1 | +0.1 | +0.0 | +0.0 |
| chbmit | biot | last_randinit - lp_randinit | lift_best | -0.20 | -0.35 | +0.44 | +0.01 | +0.01 |
| chbmit | cbramod | last - lp | roc_best | -0.4 | +0.5 | +0.0 | -0.1 | -0.1 |
| chbmit | cbramod | last - lp | roc_last | -0.2 | +0.3 | +0.0 | -0.1 | -0.1 |
| chbmit | cbramod | last - lp | roc50_best | -0.5 | +0.5 | -0.0 | -0.2 | -0.1 |
| chbmit | cbramod | last - lp | ap_best | -0.0 | +1.1 | +0.1 | +0.1 | +0.0 |
| chbmit | cbramod | last - lp | lift_best | -0.02 | +3.38 | +0.33 | +0.42 | +0.15 |
| chbmit | cbramod | last_randinit - last | roc_best | -3.2 | -7.9 | -3.7 | -1.7 | -5.6 |
| chbmit | cbramod | last_randinit - last | roc_last | -6.9 | -11.0 | -4.2 | -1.6 | -10.2 |
| chbmit | cbramod | last_randinit - last | roc50_best | -2.9 | -8.0 | -3.3 | -2.8 | -5.6 |
| chbmit | cbramod | last_randinit - last | ap_best | -19.4 | -24.8 | -13.4 | -0.4 | -14.1 |
| chbmit | cbramod | last_randinit - last | lift_best | -29.13 | -74.55 | -62.54 | -1.34 | -87.50 |
| chbmit | cbramod | lp - lp_randinit | roc_best | +5.9 | +9.3 | +3.1 | +4.1 | +4.9 |
| chbmit | cbramod | lp - lp_randinit | roc_last | +7.3 | +10.1 | +3.9 | +1.7 | +9.9 |
| chbmit | cbramod | lp - lp_randinit | roc50_best | +5.9 | +9.6 | +3.0 | +5.1 | +5.3 |
| chbmit | cbramod | lp - lp_randinit | ap_best | +21.6 | +24.3 | +16.0 | +4.1 | +14.1 |
| chbmit | cbramod | lp - lp_randinit | lift_best | +32.56 | +73.16 | +74.68 | +12.69 | +87.17 |
| chbmit | cbramod | last_randinit - lp_randinit | roc_best | +2.3 | +1.8 | -0.5 | +2.3 | -0.8 |
| chbmit | cbramod | last_randinit - lp_randinit | roc_last | +0.2 | -0.5 | -0.3 | +0.0 | -0.5 |
| chbmit | cbramod | last_randinit - lp_randinit | roc50_best | +2.5 | +2.1 | -0.3 | +2.1 | -0.4 |
| chbmit | cbramod | last_randinit - lp_randinit | ap_best | +2.3 | +0.7 | +2.7 | +3.8 | -0.0 |
| chbmit | cbramod | last_randinit - lp_randinit | lift_best | +3.42 | +1.99 | +12.46 | +11.77 | -0.18 |
| siena | biot | last - lp | roc_best | +7.5 | +18.3 | +3.4 | +10.0 | +7.0 |
| siena | biot | last - lp | roc_last | +7.5 | +12.4 | +3.4 | +8.1 | +9.9 |
| siena | biot | last - lp | roc50_best | +7.4 | +18.5 | +3.7 | +11.0 | +7.2 |
| siena | biot | last - lp | ap_best | +0.1 | +0.5 | +0.5 | +0.6 | +1.0 |
| siena | biot | last - lp | lift_best | +0.07 | +1.15 | +0.55 | +1.19 | +1.09 |
| siena | biot | last_randinit - last | roc_best | -7.7 | +28.1 | +6.4 | +15.5 | -6.3 |
| siena | biot | last_randinit - last | roc_last | -8.5 | +27.6 | +6.1 | +15.2 | -5.4 |
| siena | biot | last_randinit - last | roc50_best | -8.8 | +32.7 | +6.3 | +15.8 | -6.9 |
| siena | biot | last_randinit - last | ap_best | -0.5 | +14.1 | +2.6 | +7.4 | -1.8 |
| siena | biot | last_randinit - last | lift_best | -0.47 | +32.78 | +2.59 | +13.61 | -1.95 |
| siena | biot | lp - lp_randinit | roc_best | +1.1 | -45.7 | -9.1 | -26.5 | -0.3 |
| siena | biot | lp - lp_randinit | roc_last | +1.3 | -39.7 | -8.8 | -24.3 | -4.8 |
| siena | biot | lp - lp_randinit | roc50_best | +2.4 | -50.6 | -9.5 | -28.0 | +0.2 |
| siena | biot | lp - lp_randinit | ap_best | +0.4 | -14.5 | -3.0 | -8.1 | +0.7 |
| siena | biot | lp - lp_randinit | lift_best | +0.43 | -33.74 | -3.09 | -14.86 | +0.82 |
| siena | biot | last_randinit - lp_randinit | roc_best | +0.9 | +0.7 | +0.7 | -1.0 | +0.4 |
| siena | biot | last_randinit - lp_randinit | roc_last | +0.3 | +0.2 | +0.6 | -1.0 | -0.3 |
| siena | biot | last_randinit - lp_randinit | roc50_best | +1.0 | +0.7 | +0.6 | -1.1 | +0.4 |
| siena | biot | last_randinit - lp_randinit | ap_best | +0.0 | +0.1 | +0.1 | -0.0 | -0.0 |
| siena | biot | last_randinit - lp_randinit | lift_best | +0.03 | +0.20 | +0.06 | -0.06 | -0.04 |
| siena | cbramod | last - lp | roc_best | -0.5 | +0.3 | +0.5 | +1.0 | +0.0 |
| siena | cbramod | last - lp | roc_last | +0.6 | +0.3 | +0.5 | +1.0 | +0.0 |
| siena | cbramod | last - lp | roc50_best | -0.6 | +0.3 | +0.5 | +0.9 | +0.1 |
| siena | cbramod | last - lp | ap_best | -0.3 | +0.1 | -0.2 | +0.1 | +2.0 |
| siena | cbramod | last - lp | lift_best | -0.32 | +0.22 | -0.20 | +0.22 | +2.19 |
| siena | cbramod | last_randinit - last | roc_best | -6.6 | -2.9 | -13.4 | -2.2 | -13.0 |
| siena | cbramod | last_randinit - last | roc_last | -12.4 | -2.9 | -14.9 | -2.2 | -15.8 |
| siena | cbramod | last_randinit - last | roc50_best | -5.8 | -2.5 | -13.3 | -4.2 | -14.7 |
| siena | cbramod | last_randinit - last | ap_best | +0.3 | +3.3 | -5.5 | -6.9 | -20.9 |
| siena | cbramod | last_randinit - last | lift_best | +0.26 | +7.65 | -5.58 | -12.75 | -23.11 |
| siena | cbramod | lp - lp_randinit | roc_best | +4.8 | +0.3 | +14.7 | -0.0 | +15.2 |
| siena | cbramod | lp - lp_randinit | roc_last | +11.7 | +3.3 | +14.6 | +1.0 | +16.3 |
| siena | cbramod | lp - lp_randinit | roc50_best | +4.3 | +0.1 | +14.6 | +2.2 | +16.6 |
| siena | cbramod | lp - lp_randinit | ap_best | -0.0 | -1.9 | +5.7 | +8.0 | +20.0 |
| siena | cbramod | lp - lp_randinit | lift_best | -0.05 | -4.37 | +5.75 | +14.72 | +22.04 |
| siena | cbramod | last_randinit - lp_randinit | roc_best | -2.2 | -2.3 | +1.8 | -1.3 | +2.2 |
| siena | cbramod | last_randinit - lp_randinit | roc_last | -0.1 | +0.8 | +0.3 | -0.2 | +0.6 |
| siena | cbramod | last_randinit - lp_randinit | roc50_best | -2.2 | -2.1 | +1.7 | -1.1 | +2.0 |
| siena | cbramod | last_randinit - lp_randinit | ap_best | -0.1 | +1.5 | -0.0 | +1.2 | +1.0 |
| siena | cbramod | last_randinit - lp_randinit | lift_best | -0.10 | +3.50 | -0.02 | +2.19 | +1.12 |
| siena_filt | biot | last - lp | roc_best | +1.3 | +8.9 | +0.9 | +5.0 | +4.4 |
| siena_filt | biot | last - lp | roc_last | +1.3 | +8.9 | +0.9 | +2.6 | +3.9 |
| siena_filt | biot | last - lp | roc50_best | +1.2 | +9.2 | +0.6 | +5.9 | +5.1 |
| siena_filt | biot | last - lp | ap_best | -5.2 | +0.1 | -0.4 | +2.8 | +1.8 |
| siena_filt | biot | last - lp | lift_best | -5.36 | +0.13 | -0.38 | +5.14 | +2.04 |
| siena_filt | biot | last_randinit - last | roc_best | -24.3 | +37.1 | -9.3 | -13.8 | -13.2 |
| siena_filt | biot | last_randinit - last | roc_last | -22.5 | +37.3 | -9.0 | -19.3 | -12.4 |
| siena_filt | biot | last_randinit - last | roc50_best | -25.6 | +39.7 | -9.3 | -12.9 | -14.1 |
| siena_filt | biot | last_randinit - last | ap_best | -9.4 | +9.8 | -0.2 | +3.5 | -8.2 |
| siena_filt | biot | last_randinit - last | lift_best | -9.67 | +22.78 | -0.20 | +6.46 | -9.09 |
| siena_filt | biot | lp - lp_randinit | roc_best | +23.3 | -46.2 | +9.2 | +8.9 | +9.6 |
| siena_filt | biot | lp - lp_randinit | roc_last | +21.2 | -46.2 | +8.9 | +16.9 | +9.4 |
| siena_filt | biot | lp - lp_randinit | roc50_best | +24.7 | -49.1 | +9.3 | +7.2 | +9.9 |
| siena_filt | biot | lp - lp_randinit | ap_best | +14.7 | -11.0 | +0.5 | -6.2 | +6.4 |
| siena_filt | biot | lp - lp_randinit | lift_best | +15.03 | -25.65 | +0.55 | -11.39 | +7.11 |
| siena_filt | biot | last_randinit - lp_randinit | roc_best | +0.3 | -0.1 | +0.8 | +0.1 | +0.9 |
| siena_filt | biot | last_randinit - lp_randinit | roc_last | +0.0 | +0.0 | +0.8 | +0.2 | +0.9 |
| siena_filt | biot | last_randinit - lp_randinit | roc50_best | +0.3 | -0.1 | +0.6 | +0.2 | +0.9 |
| siena_filt | biot | last_randinit - lp_randinit | ap_best | +0.0 | -1.2 | -0.0 | +0.1 | +0.0 |
| siena_filt | biot | last_randinit - lp_randinit | lift_best | +0.01 | -2.75 | -0.03 | +0.21 | +0.05 |
| siena_filt | cbramod | last - lp | roc_best | +0.3 | -0.1 | +0.2 | +0.2 | +0.1 |
| siena_filt | cbramod | last - lp | roc_last | +0.2 | -0.1 | +0.2 | +0.2 | +0.1 |
| siena_filt | cbramod | last - lp | roc50_best | +0.4 | -0.1 | +0.1 | +0.2 | +0.1 |
| siena_filt | cbramod | last - lp | ap_best | +4.6 | -2.0 | +0.6 | +0.2 | +1.3 |
| siena_filt | cbramod | last - lp | lift_best | +4.69 | -4.55 | +0.63 | +0.35 | +1.42 |
| siena_filt | cbramod | last_randinit - last | roc_best | -15.3 | -7.7 | -8.3 | -5.2 | -16.9 |
| siena_filt | cbramod | last_randinit - last | roc_last | -17.0 | -10.0 | -12.2 | -12.3 | -23.6 |
| siena_filt | cbramod | last_randinit - last | roc50_best | -15.9 | -7.4 | -6.4 | -5.9 | -18.3 |
| siena_filt | cbramod | last_randinit - last | ap_best | -23.2 | -22.4 | -7.8 | -14.0 | -38.2 |
| siena_filt | cbramod | last_randinit - last | lift_best | -23.76 | -52.06 | -7.87 | -25.79 | -42.15 |
| siena_filt | cbramod | lp - lp_randinit | roc_best | +16.2 | +6.7 | +7.3 | +4.8 | +12.3 |
| siena_filt | cbramod | lp - lp_randinit | roc_last | +16.9 | +10.3 | +10.9 | +11.6 | +23.3 |
| siena_filt | cbramod | lp - lp_randinit | roc50_best | +16.7 | +6.3 | +5.5 | +5.9 | +14.1 |
| siena_filt | cbramod | lp - lp_randinit | ap_best | +18.9 | +22.6 | +6.9 | +14.2 | +35.9 |
| siena_filt | cbramod | lp - lp_randinit | lift_best | +19.33 | +52.58 | +7.02 | +26.28 | +39.68 |
| siena_filt | cbramod | last_randinit - lp_randinit | roc_best | +1.3 | -1.2 | -0.9 | -0.3 | -4.5 |
| siena_filt | cbramod | last_randinit - lp_randinit | roc_last | +0.1 | +0.2 | -1.1 | -0.5 | -0.1 |
| siena_filt | cbramod | last_randinit - lp_randinit | roc50_best | +1.2 | -1.2 | -0.8 | +0.2 | -4.2 |
| siena_filt | cbramod | last_randinit - lp_randinit | ap_best | +0.3 | -1.7 | -0.2 | +0.5 | -0.9 |
| siena_filt | cbramod | last_randinit - lp_randinit | lift_best | +0.26 | -4.03 | -0.22 | +0.84 | -1.04 |
