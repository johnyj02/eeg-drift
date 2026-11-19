# D29 PR-AUC readings: full tables (no ROC-derived threshold)

No ROC-derived threshold is applied to a PR-AUC contrast, and no practical-importance label is attached to one. The frozen D29 text asks only for C1, C2 and C3 "read again with average precision (and the trapezoid PR-AUC the release reports)" and defines no PR-AUC margin; the first version of this reader reused the ROC rule strings (D18 |mean| > 3 with 4 of 5 units agreeing; the E30 C2/C3 "within 3" / "> 3 above LP" cuts; the D29 noise rule's "mean > 3") and the margin-3 TOST. That compared one fixed 3-point margin against AP baselines from 1.5 to 44 points and hid measured differences: Siena BIOT raw head AP 1.65 -> 2.20, +0.55 [+0.14, +0.96], about +33% relative, was labelled "no difference shown" because 0.55 < 3. Those labels and the margin-3 TOST are withdrawn here (change made 2026-11-05, AFTER the results, in answer to an external review; post hoc). Each PR-AUC contrast now reports the two arm means, the absolute difference with its 95% t-interval over the stated units, the relative change in percent of the baseline arm, and whether the interval excludes 0 - which is the only inference claim made. A relative change on a near-zero baseline is unstable, so the baseline is printed next to every percentage and should be read with it. No PR-AUC margin is defined in its place: defining one now, after seeing the data, would be a post hoc threshold, and the prevalence-scaled alternatives already in the artifacts (AP / prevalence, scripts/analysis/coverage.py and handcrafted_baseline.py) are reported there rather than turned into a cut here. Every ROC reading in these files is unchanged.

Test prevalence x100 (the scale AP lives on): DL's split 1.49; CHB-MIT rotations 0.66/0.33/0.21/0.32/0.16; Siena 0.98/0.43/0.99/0.54/0.91; Siena filtered 0.98/0.43/0.99/0.54/0.91.

Script scripts/analysis/d29_read.py (one run writes README.md, this file and d29.json). Every number below is x100 at the ROC-selected probe epoch (probe selection unchanged, so these are the same fitted probes the ROC readings use). AP = average precision (sklearn), trapz = the trapezoid PR-AUC the release reports. ROC columns are shown for reference only and are unchanged from the ROC readings.

## 1. C1 (SA - LP = `last` - `lp`)

Units: 5 seeds on DL's split (seed uncertainty on one split), 5 rotation means of 3 seeds elsewhere. NB 95% = Nadeau-Bengio interval (rotation settings only, ratio n_test/n_train). ROC column: the D18 / D24-B rule string, which does apply to ROC (F = first term wins, S = second, N = no difference shown).

| setting | model | head (tags) | metric | unit | base mean | arm mean | difference | 95% t | relative | excludes 0 | NB 95% | > 0 | per unit | ROC |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DL's split | biot | linear (P1E) | AP | seed (one split) | 1.94 | 1.91 | -0.03 | [-0.41, +0.36] | -1.4% | no | - | 1/5 | -0.18, +0.50, -0.21, -0.00, -0.25 | -0.60 no difference shown |
| DL's split | biot | linear (P1E) | PR-AUC trapz | seed (one split) | 1.91 | 1.89 | -0.03 | [-0.40, +0.34] | -1.5% | no | - | 1/5 | -0.17, +0.48, -0.21, -0.00, -0.24 | -0.60 no difference shown |
| DL's split | cbramod | linear (P1E) | AP | seed (one split) | 42.21 | 42.41 | +0.20 | [+0.08, +0.32] | +0.5% | yes | - | 5/5 | +0.10, +0.12, +0.27, +0.18, +0.33 | +0.01 no difference shown |
| DL's split | cbramod | linear (P1E) | PR-AUC trapz | seed (one split) | 42.03 | 42.23 | +0.20 | [+0.08, +0.32] | +0.5% | yes | - | 5/5 | +0.10, +0.12, +0.27, +0.18, +0.33 | +0.01 no difference shown |
| DL's split | biot | mlp_fullft (P1E) | AP | seed (one split) | 3.14 | 2.67 | -0.47 | [-1.22, +0.27] | -15.0% | no | - | 2/5 | -0.72, +0.27, -0.90, +0.07, -1.07 | -1.19 no difference shown |
| DL's split | biot | mlp_fullft (P1E) | PR-AUC trapz | seed (one split) | 3.08 | 2.61 | -0.47 | [-1.18, +0.25] | -15.2% | no | - | 2/5 | -0.70, +0.24, -0.89, +0.05, -1.03 | -1.19 no difference shown |
| DL's split | cbramod | mlp_fullft (P1E) | AP | seed (one split) | 39.21 | 38.58 | -0.63 | [-2.85, +1.60] | -1.6% | no | - | 2/5 | -0.76, -3.57, +0.52, -0.36, +1.04 | +0.03 no difference shown |
| DL's split | cbramod | mlp_fullft (P1E) | PR-AUC trapz | seed (one split) | 39.03 | 38.40 | -0.63 | [-2.85, +1.58] | -1.6% | no | - | 2/5 | -0.78, -3.56, +0.49, -0.35, +1.03 | +0.03 no difference shown |
| DL's split | biot | linear_z (P1Z) | AP | seed (one split) | 20.24 | 21.92 | +1.68 | [-3.40, +6.76] | +8.3% | no | - | 3/5 | -0.09, -0.78, +0.01, +0.29, +8.97 | +0.18 no difference shown |
| DL's split | biot | linear_z (P1Z) | PR-AUC trapz | seed (one split) | 19.93 | 21.61 | +1.68 | [-3.40, +6.76] | +8.4% | no | - | 3/5 | -0.09, -0.78, +0.01, +0.29, +8.97 | +0.18 no difference shown |
| DL's split | cbramod | linear_z (P1Z) | AP | seed (one split) | 34.12 | 34.70 | +0.58 | [+0.30, +0.86] | +1.7% | yes | - | 5/5 | +0.84, +0.45, +0.45, +0.81, +0.37 | +0.18 no difference shown |
| DL's split | cbramod | linear_z (P1Z) | PR-AUC trapz | seed (one split) | 33.85 | 34.45 | +0.60 | [+0.28, +0.92] | +1.8% | yes | - | 5/5 | +0.84, +0.42, +0.45, +0.91, +0.37 | +0.18 no difference shown |
| DL's split | biot | grid (P1G) | AP | seed (one split) | 12.63 | 13.02 | +0.39 | [-0.31, +1.09] | +3.1% | no | - | 3/5 | -0.04, +0.49, +1.27, -0.18, +0.41 | -0.08 no difference shown |
| DL's split | biot | grid (P1G) | PR-AUC trapz | seed (one split) | 12.45 | 12.84 | +0.39 | [-0.31, +1.09] | +3.1% | no | - | 3/5 | -0.04, +0.49, +1.26, -0.18, +0.41 | -0.08 no difference shown |
| DL's split | cbramod | grid (P1G) | AP | seed (one split) | 37.29 | 35.92 | -1.37 | [-4.66, +1.92] | -3.7% | no | - | 1/5 | -0.54, -1.03, -5.82, +1.31, -0.78 | -0.54 no difference shown |
| DL's split | cbramod | grid (P1G) | PR-AUC trapz | seed (one split) | 37.08 | 35.70 | -1.38 | [-4.63, +1.86] | -3.7% | no | - | 1/5 | -0.53, -1.13, -5.75, +1.27, -0.78 | -0.54 no difference shown |
| DL's split | biot | grid_z (P1G) | AP | seed (one split) | 20.18 | 18.44 | -1.74 | [-9.09, +5.62] | -8.6% | no | - | 1/5 | -0.18, -0.45, -0.51, -11.72, +4.18 | -0.09 no difference shown |
| DL's split | biot | grid_z (P1G) | PR-AUC trapz | seed (one split) | 19.96 | 18.21 | -1.75 | [-9.14, +5.63] | -8.8% | no | - | 1/5 | -0.18, -0.45, -0.51, -11.79, +4.17 | -0.09 no difference shown |
| DL's split | cbramod | grid_z (P1G) | AP | seed (one split) | 35.28 | 35.85 | +0.57 | [+0.10, +1.04] | +1.6% | yes | - | 4/5 | +0.84, -0.09, +0.78, +0.70, +0.64 | +0.12 no difference shown |
| DL's split | cbramod | grid_z (P1G) | PR-AUC trapz | seed (one split) | 35.09 | 35.66 | +0.57 | [+0.09, +1.05] | +1.6% | yes | - | 4/5 | +0.84, -0.10, +0.78, +0.70, +0.63 | +0.12 no difference shown |
| CHB-MIT | biot | linear (S1E+S1M) | AP | rotation mean of 3 seeds | 0.92 | 1.56 | +0.64 | [-1.00, +2.28] | +70.0% | no | [-2.05, +3.33] | 5/5 | +0.06, +0.08, +3.00, +0.01, +0.07 | +1.91 no difference shown |
| CHB-MIT | biot | linear (S1E+S1M) | PR-AUC trapz | rotation mean of 3 seeds | 0.89 | 1.54 | +0.65 | [-1.01, +2.30] | +72.3% | no | [-2.06, +3.35] | 5/5 | +0.07, +0.07, +3.02, +0.01, +0.06 | +1.91 no difference shown |
| CHB-MIT | cbramod | linear (S1E+S1M) | AP | rotation mean of 3 seeds | 23.02 | 23.29 | +0.27 | [-0.33, +0.87] | +1.2% | no | [-0.71, +1.25] | 4/5 | -0.01, +1.12, +0.07, +0.14, +0.02 | -0.02 no difference shown |
| CHB-MIT | cbramod | linear (S1E+S1M) | PR-AUC trapz | rotation mean of 3 seeds | 22.95 | 23.22 | +0.27 | [-0.33, +0.87] | +1.2% | no | [-0.71, +1.26] | 4/5 | -0.01, +1.13, +0.08, +0.14, +0.02 | -0.02 no difference shown |
| CHB-MIT | biot | linear_z (S1Z) | AP | rotation mean of 3 seeds | 6.80 | 7.19 | +0.39 | [-0.39, +1.17] | +5.7% | no | [-0.89, +1.66] | 4/5 | +0.22, +0.24, +1.49, -0.03, +0.02 | +0.11 no difference shown |
| CHB-MIT | biot | linear_z (S1Z) | PR-AUC trapz | rotation mean of 3 seeds | 6.67 | 7.05 | +0.38 | [-0.39, +1.15] | +5.7% | no | [-0.88, +1.64] | 4/5 | +0.22, +0.22, +1.46, -0.03, +0.02 | +0.11 no difference shown |
| CHB-MIT | cbramod | linear_z (S1Z) | AP | rotation mean of 3 seeds | 28.75 | 29.58 | +0.82 | [-0.19, +1.84] | +2.9% | no | [-0.84, +2.49] | 5/5 | +1.07, +2.12, +0.60, +0.11, +0.21 | +0.41 no difference shown |
| CHB-MIT | cbramod | linear_z (S1Z) | PR-AUC trapz | rotation mean of 3 seeds | 28.69 | 29.51 | +0.82 | [-0.19, +1.84] | +2.9% | no | [-0.84, +2.49] | 5/5 | +1.07, +2.12, +0.60, +0.11, +0.22 | +0.41 no difference shown |
| CHB-MIT | biot | grid (S1G) | AP | rotation mean of 3 seeds | 11.51 | 11.61 | +0.09 | [-0.92, +1.11] | +0.8% | no | [-1.57, +1.76] | 2/5 | +0.26, +1.43, -0.57, -0.19, -0.48 | -0.51 no difference shown |
| CHB-MIT | biot | grid (S1G) | PR-AUC trapz | rotation mean of 3 seeds | 11.43 | 11.54 | +0.11 | [-0.88, +1.11] | +1.0% | no | [-1.52, +1.75] | 2/5 | +0.27, +1.43, -0.57, -0.15, -0.41 | -0.51 no difference shown |
| CHB-MIT | cbramod | grid (S1G) | AP | rotation mean of 3 seeds | 19.39 | 19.75 | +0.36 | [-1.58, +2.29] | +1.8% | no | [-2.82, +3.53] | 2/5 | +2.45, -0.95, -0.92, -0.37, +1.57 | +0.66 no difference shown |
| CHB-MIT | cbramod | grid (S1G) | PR-AUC trapz | rotation mean of 3 seeds | 19.31 | 19.68 | +0.37 | [-1.59, +2.32] | +1.9% | no | [-2.84, +3.57] | 2/5 | +2.46, -0.95, -0.92, -0.38, +1.62 | +0.66 no difference shown |
| CHB-MIT | biot | grid_z (S1G) | AP | rotation mean of 3 seeds | 8.67 | 8.57 | -0.10 | [-1.55, +1.35] | -1.2% | no | [-2.48, +2.28] | 1/5 | -0.15, -1.24, +1.80, -0.83, -0.08 | -0.39 no difference shown |
| CHB-MIT | biot | grid_z (S1G) | PR-AUC trapz | rotation mean of 3 seeds | 8.50 | 8.40 | -0.10 | [-1.55, +1.35] | -1.1% | no | [-2.47, +2.28] | 1/5 | -0.14, -1.26, +1.82, -0.76, -0.14 | -0.39 no difference shown |
| CHB-MIT | cbramod | grid_z (S1G) | AP | rotation mean of 3 seeds | 25.60 | 25.36 | -0.24 | [-3.63, +3.14] | -0.9% | no | [-5.80, +5.31] | 2/5 | -4.26, -0.32, +3.29, +0.76, -0.69 | -4.42 second term wins |
| CHB-MIT | cbramod | grid_z (S1G) | PR-AUC trapz | rotation mean of 3 seeds | 25.54 | 25.31 | -0.23 | [-3.63, +3.17] | -0.9% | no | [-5.80, +5.34] | 2/5 | -4.26, -0.32, +3.31, +0.78, -0.67 | -4.42 second term wins |
| Siena | biot | linear (S3E+S3M) | AP | rotation mean of 3 seeds | 1.65 | 2.20 | +0.55 | [+0.14, +0.96] | +33.2% | yes | [-0.12, +1.22] | 5/5 | +0.07, +0.50, +0.55, +0.64, +0.99 | +9.23 first term wins |
| Siena | biot | linear (S3E+S3M) | PR-AUC trapz | rotation mean of 3 seeds | 1.49 | 2.03 | +0.54 | [+0.19, +0.90] | +36.2% | yes | [-0.05, +1.13] | 5/5 | +0.16, +0.48, +0.49, +0.61, +0.96 | +9.23 first term wins |
| Siena | cbramod | linear (S3E+S3M) | AP | rotation mean of 3 seeds | 10.50 | 10.84 | +0.34 | [-0.83, +1.50] | +3.2% | no | [-1.59, +2.26] | 3/5 | -0.31, +0.10, -0.19, +0.12, +1.98 | +0.27 no difference shown |
| Siena | cbramod | linear (S3E+S3M) | PR-AUC trapz | rotation mean of 3 seeds | 10.13 | 10.44 | +0.30 | [-0.92, +1.53] | +3.0% | no | [-1.73, +2.34] | 3/5 | -0.30, +0.10, -0.41, +0.11, +2.02 | +0.27 no difference shown |
| Siena | biot | linear_z (S3Z) | AP | rotation mean of 3 seeds | 6.37 | 6.55 | +0.18 | [+0.01, +0.35] | +2.8% | yes | [-0.11, +0.46] | 5/5 | +0.03, +0.25, +0.08, +0.37, +0.15 | +1.65 no difference shown |
| Siena | biot | linear_z (S3Z) | PR-AUC trapz | rotation mean of 3 seeds | 6.18 | 6.37 | +0.19 | [+0.00, +0.37] | +3.0% | yes | [-0.12, +0.50] | 5/5 | +0.03, +0.32, +0.08, +0.37, +0.14 | +1.65 no difference shown |
| Siena | cbramod | linear_z (S3Z) | AP | rotation mean of 3 seeds | 9.05 | 9.09 | +0.04 | [-0.98, +1.06] | +0.4% | no | [-1.65, +1.73] | 2/5 | +0.22, -0.72, -0.08, -0.57, +1.35 | -0.26 no difference shown |
| Siena | cbramod | linear_z (S3Z) | PR-AUC trapz | rotation mean of 3 seeds | 8.63 | 8.64 | +0.00 | [-1.02, +1.03] | +0.0% | no | [-1.69, +1.70] | 2/5 | +0.21, -0.84, -0.08, -0.57, +1.28 | -0.26 no difference shown |
| Siena | biot | grid (S3G) | AP | rotation mean of 3 seeds | 5.71 | 5.25 | -0.46 | [-1.32, +0.40] | -8.0% | no | [-1.88, +0.97] | 1/5 | -1.33, -0.14, -0.83, +0.50, -0.50 | +0.18 no difference shown |
| Siena | biot | grid (S3G) | PR-AUC trapz | rotation mean of 3 seeds | 5.32 | 4.87 | -0.46 | [-1.29, +0.38] | -8.6% | no | [-1.84, +0.93] | 1/5 | -1.28, -0.15, -0.84, +0.49, -0.50 | +0.18 no difference shown |
| Siena | cbramod | grid (S3G) | AP | rotation mean of 3 seeds | 13.33 | 13.14 | -0.19 | [-2.55, +2.17] | -1.4% | no | [-4.10, +3.72] | 4/5 | +0.06, +0.35, -3.36, +0.24, +1.78 | +0.40 no difference shown |
| Siena | cbramod | grid (S3G) | PR-AUC trapz | rotation mean of 3 seeds | 12.88 | 12.71 | -0.17 | [-2.44, +2.10] | -1.3% | no | [-3.93, +3.59] | 4/5 | +0.06, +0.29, -3.20, +0.23, +1.77 | +0.40 no difference shown |
| Siena | biot | grid_z (S3G) | AP | rotation mean of 3 seeds | 6.99 | 7.42 | +0.43 | [-0.70, +1.56] | +6.1% | no | [-1.44, +2.30] | 3/5 | -0.10, +1.09, -0.84, +1.42, +0.57 | -0.17 no difference shown |
| Siena | biot | grid_z (S3G) | PR-AUC trapz | rotation mean of 3 seeds | 6.60 | 7.02 | +0.43 | [-0.67, +1.53] | +6.5% | no | [-1.39, +2.24] | 3/5 | -0.10, +1.05, -0.79, +1.40, +0.59 | -0.17 no difference shown |
| Siena | cbramod | grid_z (S3G) | AP | rotation mean of 3 seeds | 9.00 | 9.33 | +0.33 | [-1.00, +1.65] | +3.7% | no | [-1.86, +2.52] | 4/5 | +0.64, -1.16, +0.08, +0.29, +1.80 | +0.57 no difference shown |
| Siena | cbramod | grid_z (S3G) | PR-AUC trapz | rotation mean of 3 seeds | 8.60 | 8.89 | +0.29 | [-1.05, +1.62] | +3.3% | no | [-1.92, +2.50] | 4/5 | +0.61, -1.27, +0.08, +0.28, +1.73 | +0.57 no difference shown |
| Siena filtered | biot | linear (S3FE+S3FM) | AP | rotation mean of 3 seeds | 6.23 | 6.05 | -0.18 | [-4.03, +3.67] | -2.9% | no | [-6.55, +6.19] | 3/5 | -5.23, +0.06, -0.37, +2.79, +1.85 | +4.11 first term wins |
| Siena filtered | biot | linear (S3FE+S3FM) | PR-AUC trapz | rotation mean of 3 seeds | 5.87 | 5.69 | -0.18 | [-3.91, +3.55] | -3.1% | no | [-6.34, +5.98] | 3/5 | -5.07, +0.04, -0.34, +2.70, +1.76 | +4.11 first term wins |
| Siena filtered | cbramod | linear (S3FE+S3FM) | AP | rotation mean of 3 seeds | 27.28 | 28.23 | +0.94 | [-1.99, +3.88] | +3.5% | no | [-3.92, +5.80] | 4/5 | +4.57, -1.96, +0.62, +0.19, +1.29 | +0.14 no difference shown |
| Siena filtered | cbramod | linear (S3FE+S3FM) | PR-AUC trapz | rotation mean of 3 seeds | 26.84 | 27.82 | +0.97 | [-2.02, +3.97] | +3.6% | no | [-3.98, +5.92] | 4/5 | +4.71, -1.93, +0.60, +0.19, +1.30 | +0.14 no difference shown |
| Siena filtered | biot | linear_z (S3FZ) | AP | rotation mean of 3 seeds | 5.49 | 5.77 | +0.28 | [-0.16, +0.71] | +5.1% | no | [-0.44, +1.00] | 3/5 | +0.45, +0.67, -0.13, +0.46, -0.05 | +1.93 no difference shown |
| Siena filtered | biot | linear_z (S3FZ) | PR-AUC trapz | rotation mean of 3 seeds | 5.27 | 5.55 | +0.28 | [-0.15, +0.70] | +5.2% | no | [-0.43, +0.98] | 3/5 | +0.46, +0.64, -0.13, +0.45, -0.05 | +1.93 no difference shown |
| Siena filtered | cbramod | linear_z (S3FZ) | AP | rotation mean of 3 seeds | 10.91 | 11.09 | +0.18 | [-0.57, +0.93] | +1.6% | no | [-1.07, +1.43] | 4/5 | +0.46, -0.88, +0.29, +0.38, +0.64 | +0.34 no difference shown |
| Siena filtered | cbramod | linear_z (S3FZ) | PR-AUC trapz | rotation mean of 3 seeds | 10.51 | 10.71 | +0.20 | [-0.58, +0.97] | +1.9% | no | [-1.09, +1.48] | 4/5 | +0.44, -0.88, +0.29, +0.37, +0.75 | +0.34 no difference shown |
| Siena filtered | biot | grid (S3FG) | AP | rotation mean of 3 seeds | 8.84 | 11.08 | +2.23 | [-4.68, +9.15] | +25.3% | no | [-9.20, +13.67] | 2/5 | +12.16, -0.69, -0.60, +0.48, -0.18 | +0.69 no difference shown |
| Siena filtered | biot | grid (S3FG) | PR-AUC trapz | rotation mean of 3 seeds | 8.37 | 10.60 | +2.23 | [-4.72, +9.19] | +26.7% | no | [-9.27, +13.74] | 2/5 | +12.23, -0.66, -0.59, +0.37, -0.18 | +0.69 no difference shown |
| Siena filtered | cbramod | grid (S3FG) | AP | rotation mean of 3 seeds | 27.08 | 28.57 | +1.49 | [-0.59, +3.56] | +5.5% | no | [-1.95, +4.92] | 4/5 | +2.75, +2.56, -1.35, +1.37, +2.11 | +0.18 no difference shown |
| Siena filtered | cbramod | grid (S3FG) | PR-AUC trapz | rotation mean of 3 seeds | 26.50 | 28.04 | +1.54 | [-0.54, +3.63] | +5.8% | no | [-1.91, +4.99] | 4/5 | +2.94, +2.57, -1.27, +1.36, +2.11 | +0.18 no difference shown |
| Siena filtered | biot | grid_z (S3FG) | AP | rotation mean of 3 seeds | 7.56 | 7.90 | +0.34 | [-0.84, +1.52] | +4.5% | no | [-1.61, +2.29] | 4/5 | +0.04, +1.37, -1.04, +1.08, +0.24 | +0.71 no difference shown |
| Siena filtered | biot | grid_z (S3FG) | PR-AUC trapz | rotation mean of 3 seeds | 7.23 | 7.49 | +0.26 | [-1.04, +1.56] | +3.6% | no | [-1.88, +2.41] | 4/5 | +0.04, +1.31, -1.34, +1.07, +0.23 | +0.71 no difference shown |
| Siena filtered | cbramod | grid_z (S3FG) | AP | rotation mean of 3 seeds | 11.63 | 11.19 | -0.44 | [-1.61, +0.74] | -3.8% | no | [-2.38, +1.51] | 3/5 | +0.35, -0.86, +0.19, +0.04, -1.91 | -1.30 no difference shown |
| Siena filtered | cbramod | grid_z (S3FG) | PR-AUC trapz | rotation mean of 3 seeds | 11.25 | 10.84 | -0.41 | [-1.51, +0.69] | -3.6% | no | [-2.22, +1.40] | 3/5 | +0.34, -0.88, +0.19, +0.04, -1.74 | -1.30 no difference shown |

10 of 68 C1 PR-AUC intervals exclude 0 (10 positive, 0 negative). Largest relative changes among them: Siena biot linear PR-AUC trapz 1.49 -> 2.03 (+0.54, +36.2%); Siena biot linear AP 1.65 -> 2.20 (+0.55, +33.2%); Siena biot linear_z PR-AUC trapz 6.18 -> 6.37 (+0.19, +3.0%); Siena biot linear_z AP 6.37 -> 6.55 (+0.18, +2.8%); DL's split cbramod linear_z PR-AUC trapz 33.85 -> 34.45 (+0.60, +1.8%); DL's split cbramod linear_z AP 34.12 -> 34.70 (+0.58, +1.7%).

### 1b. ROC reference for the same 34 rows (unchanged; the 3-point margin is a ROC margin)

| setting | model | head (tags) | lp | last | last - lp | 95% t | NB 95% | TOST p (margin 3) | > 0 | rule | per unit |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DL's split | biot | linear (P1E) | 55.02 | 54.42 | -0.60 | [-3.81, +2.60] | - | 0.053 | 2/5 | no difference shown | -2.04, +1.82, -4.28, -0.12, +1.61 |
| DL's split | cbramod | linear (P1E) | 92.00 | 92.02 | +0.01 | [-0.02, +0.04] | - | 7.6e-10 | 4/5 | no difference shown | -0.03, +0.01, +0.02, +0.03, +0.04 |
| DL's split | biot | mlp_fullft (P1E) | 56.09 | 54.90 | -1.19 | [-4.59, +2.21] | - | 0.107 | 1/5 | no difference shown | -3.15, -0.37, -4.67, -0.04, +2.27 |
| DL's split | cbramod | mlp_fullft (P1E) | 91.66 | 91.70 | +0.03 | [-0.36, +0.43] | - | 1.6e-05 | 4/5 | no difference shown | +0.06, -0.51, +0.22, +0.30, +0.10 |
| DL's split | biot | linear_z (P1Z) | 79.12 | 79.31 | +0.18 | [-2.07, +2.44] | - | 0.013 | 1/5 | no difference shown | -0.81, -1.00, -0.19, -0.47, +3.39 |
| DL's split | cbramod | linear_z (P1Z) | 88.47 | 88.65 | +0.18 | [-0.04, +0.39] | - | 1.6e-06 | 4/5 | no difference shown | +0.37, +0.25, +0.27, -0.03, +0.02 |
| DL's split | biot | grid (P1G) | 74.62 | 74.53 | -0.08 | [-0.73, +0.57] | - | 0.00012 | 3/5 | no difference shown | +0.27, +0.04, -0.16, -0.95, +0.37 |
| DL's split | cbramod | grid (P1G) | 90.75 | 90.21 | -0.54 | [-1.24, +0.16] | - | 0.00031 | 0/5 | no difference shown | -0.19, -0.09, -1.38, -0.87, -0.16 |
| DL's split | biot | grid_z (P1G) | 81.92 | 81.83 | -0.09 | [-3.15, +2.97] | - | 0.029 | 1/5 | no difference shown | -0.66, -0.58, -0.72, -2.56, +4.06 |
| DL's split | cbramod | grid_z (P1G) | 88.82 | 88.94 | +0.12 | [-0.07, +0.30] | - | 9e-07 | 4/5 | no difference shown | +0.12, -0.11, +0.25, +0.26, +0.06 |
| CHB-MIT | biot | linear (S1E+S1M) | 65.07 | 66.98 | +1.91 | [-0.96, +4.78] | [-2.79, +6.61] | 0.175 | 4/5 | no difference shown | +1.65, +3.06, +0.86, -1.09, +5.05 |
| CHB-MIT | cbramod | linear (S1E+S1M) | 81.63 | 81.61 | -0.02 | [-0.43, +0.40] | [-0.70, +0.67] | 1.9e-05 | 2/5 | no difference shown | -0.43, +0.50, +0.05, -0.09, -0.10 |
| CHB-MIT | biot | linear_z (S1Z) | 72.27 | 72.38 | +0.11 | [-1.11, +1.33] | [-1.89, +2.11] | 0.001 | 3/5 | no difference shown | -0.36, +0.37, +1.57, -1.09, +0.09 |
| CHB-MIT | cbramod | linear_z (S1Z) | 79.30 | 79.72 | +0.41 | [-0.60, +1.43] | [-1.25, +2.07] | 0.001 | 4/5 | no difference shown | +1.52, -0.75, +0.42, +0.66, +0.22 |
| CHB-MIT | biot | grid (S1G) | 76.16 | 75.65 | -0.51 | [-1.01, -0.02] | [-1.32, +0.30] | 7.5e-05 | 0/5 | no difference shown | -0.75, -0.10, -0.11, -0.62, -0.98 |
| CHB-MIT | cbramod | grid (S1G) | 78.00 | 78.66 | +0.66 | [-0.61, +1.94] | [-1.43, +2.76] | 0.004 | 4/5 | no difference shown | +0.30, -0.25, +0.87, +0.05, +2.35 |
| CHB-MIT | biot | grid_z (S1G) | 76.47 | 76.09 | -0.39 | [-1.32, +0.55] | [-1.92, +1.15] | 0.00074 | 2/5 | no difference shown | -1.39, +0.15, +0.54, -0.69, -0.53 |
| CHB-MIT | cbramod | grid_z (S1G) | 79.24 | 74.82 | -4.42 | [-10.58, +1.75] | [-14.53, +5.70] | 0.721 | 1/5 | second term wins | -10.39, -0.55, -2.75, +0.55, -8.96 |
| Siena | biot | linear (S3E+S3M) | 51.35 | 60.58 | +9.23 | [+2.28, +16.19] | [-2.27, +20.74] | 0.966 | 5/5 | first term wins | +7.49, +18.32, +3.37, +9.99, +6.99 |
| Siena | cbramod | linear (S3E+S3M) | 81.41 | 81.68 | +0.27 | [-0.41, +0.94] | [-0.85, +1.38] | 0.00018 | 4/5 | no difference shown | -0.48, +0.31, +0.52, +0.97, +0.01 |
| Siena | biot | linear_z (S3Z) | 68.59 | 70.24 | +1.65 | [-0.26, +3.56] | [-1.50, +4.81] | 0.061 | 4/5 | no difference shown | +0.89, -0.15, +1.50, +3.98, +2.05 |
| Siena | cbramod | linear_z (S3Z) | 78.93 | 78.67 | -0.26 | [-1.26, +0.74] | [-1.92, +1.40] | 0.00081 | 2/5 | no difference shown | +0.27, -0.99, -0.16, -1.16, +0.74 |
| Siena | biot | grid (S3G) | 75.37 | 75.56 | +0.18 | [-1.40, +1.77] | [-2.44, +2.80] | 0.004 | 4/5 | no difference shown | -1.87, +0.66, +0.51, +1.58, +0.05 |
| Siena | cbramod | grid (S3G) | 81.93 | 82.33 | +0.40 | [-0.13, +0.94] | [-0.48, +1.29] | 8.8e-05 | 4/5 | no difference shown | +0.89, -0.23, +0.52, +0.62, +0.22 |
| Siena | biot | grid_z (S3G) | 77.32 | 77.15 | -0.17 | [-4.62, +4.28] | [-7.53, +7.19] | 0.076 | 3/5 | no difference shown | -0.20, +2.59, -6.32, +1.25, +1.83 |
| Siena | cbramod | grid_z (S3G) | 79.40 | 79.97 | +0.57 | [-1.43, +2.57] | [-2.74, +3.88] | 0.014 | 3/5 | no difference shown | +2.82, -0.66, +0.36, -1.14, +1.48 |
| Siena filtered | biot | linear (S3FE+S3FM) | 69.77 | 73.87 | +4.11 | [+0.06, +8.15] | [-2.58, +10.79] | 0.755 | 5/5 | first term wins | +1.32, +8.93, +0.87, +5.01, +4.39 |
| Siena filtered | cbramod | linear (S3FE+S3FM) | 89.48 | 89.62 | +0.14 | [-0.05, +0.33] | [-0.17, +0.45] | 9.5e-07 | 4/5 | no difference shown | +0.32, -0.09, +0.16, +0.20, +0.11 |
| Siena filtered | biot | linear_z (S3FZ) | 73.27 | 75.20 | +1.93 | [-1.63, +5.49] | [-3.95, +7.82] | 0.226 | 4/5 | no difference shown | +6.15, +3.69, +0.10, +0.01, -0.29 |
| Siena filtered | cbramod | linear_z (S3FZ) | 82.79 | 83.12 | +0.34 | [-0.15, +0.82] | [-0.47, +1.14] | 5.5e-05 | 3/5 | no difference shown | +0.19, -0.01, +0.85, -0.00, +0.65 |
| Siena filtered | biot | grid (S3FG) | 78.60 | 79.29 | +0.69 | [-1.60, +2.98] | [-3.10, +4.48] | 0.024 | 2/5 | no difference shown | +3.54, -1.17, -0.08, +1.42, -0.27 |
| Siena filtered | cbramod | grid (S3FG) | 89.73 | 89.91 | +0.18 | [+0.12, +0.25] | [+0.08, +0.29] | 1.2e-08 | 5/5 | no difference shown | +0.13, +0.20, +0.24, +0.13, +0.21 |
| Siena filtered | biot | grid_z (S3FG) | 76.31 | 77.02 | +0.71 | [-0.78, +2.20] | [-1.76, +3.17] | 0.006 | 4/5 | no difference shown | +0.57, +2.74, -0.44, +0.30, +0.36 |
| Siena filtered | cbramod | grid_z (S3FG) | 84.13 | 82.83 | -1.30 | [-3.39, +0.79] | [-4.75, +2.15] | 0.043 | 2/5 | no difference shown | +0.03, -2.76, -0.57, +0.22, -3.43 |

## 2. C2/C3 on DL's split (CHB-MIT paper split; E30a / D24-C records)

Every curve point against LP. BIOT: 5 seeds at data_seed 1 (C2E seed 42 + C2X/C3X), paired by seed with the R3E-b128 LP. CBraMod: one curve seed (42, as D24-C) against the 5-seed LP mean, so there is no interval and no inference claim at all for CBraMod here.

| model | metric | point | unit | base mean | arm mean | difference | 95% t | relative | excludes 0 | per unit |
|---|---|---|---|---|---|---|---|---|---|---|
| biot | AP | N896 | seed (one split) | 5.56 | 5.28 | -0.28 | [-1.73, +1.16] | -5.1% | no | -0.83, +1.25, +0.41, -0.46, -1.80 |
| biot | AP | N1664 | seed (one split) | 5.56 | 5.39 | -0.18 | [-1.74, +1.39] | -3.2% | no | -0.99, +1.50, +0.56, -0.26, -1.71 |
| biot | AP | N2048 | seed (one split) | 5.56 | 5.38 | -0.18 | [-1.72, +1.36] | -3.2% | no | -0.93, +1.54, +0.47, -0.33, -1.65 |
| biot | AP | N4174 | seed (one split) | 5.56 | 5.47 | -0.09 | [-1.62, +1.44] | -1.7% | no | -0.83, +1.59, +0.59, -0.23, -1.57 |
| biot | AP | P3N2048 | seed (one split) | 5.56 | 5.07 | -0.49 | [-1.58, +0.60] | -8.8% | no | -0.99, +0.72, +0.11, -0.90, -1.40 |
| biot | AP | P11N2048 | seed (one split) | 5.56 | 5.60 | +0.04 | [-1.58, +1.66] | +0.7% | no | -0.62, +1.97, +0.68, -0.48, -1.35 |
| biot | AP | P21N2048 | seed (one split) | 5.56 | 5.45 | -0.12 | [-1.55, +1.31] | -2.1% | no | -0.69, +1.51, +0.44, -0.34, -1.51 |
| biot | PR-AUC trapz | N896 | seed (one split) | 5.40 | 5.11 | -0.29 | [-1.66, +1.07] | -5.4% | no | -0.72, +1.12, +0.40, -0.52, -1.74 |
| biot | PR-AUC trapz | N1664 | seed (one split) | 5.40 | 5.21 | -0.19 | [-1.66, +1.28] | -3.5% | no | -0.88, +1.37, +0.54, -0.32, -1.67 |
| biot | PR-AUC trapz | N2048 | seed (one split) | 5.40 | 5.21 | -0.19 | [-1.64, +1.26] | -3.6% | no | -0.82, +1.41, +0.46, -0.39, -1.61 |
| biot | PR-AUC trapz | N4174 | seed (one split) | 5.40 | 5.30 | -0.11 | [-1.55, +1.33] | -2.0% | no | -0.73, +1.46, +0.57, -0.30, -1.54 |
| biot | PR-AUC trapz | P3N2048 | seed (one split) | 5.40 | 4.90 | -0.51 | [-1.53, +0.51] | -9.4% | no | -0.91, +0.60, +0.10, -0.95, -1.37 |
| biot | PR-AUC trapz | P11N2048 | seed (one split) | 5.40 | 5.44 | +0.04 | [-1.55, +1.63] | +0.7% | no | -0.53, +1.94, +0.66, -0.54, -1.33 |
| biot | PR-AUC trapz | P21N2048 | seed (one split) | 5.40 | 5.27 | -0.13 | [-1.48, +1.21] | -2.5% | no | -0.60, +1.38, +0.43, -0.40, -1.48 |
| cbramod | AP | N896 | 1 seed (no interval) | 41.68 | 44.03 | +2.36 | n/a (1 unit) | +5.7% | n/a | +2.36 |
| cbramod | AP | N1664 | 1 seed (no interval) | 41.68 | 44.03 | +2.35 | n/a (1 unit) | +5.6% | n/a | +2.35 |
| cbramod | AP | N2048 | 1 seed (no interval) | 41.68 | 44.07 | +2.39 | n/a (1 unit) | +5.7% | n/a | +2.39 |
| cbramod | AP | N4174 | 1 seed (no interval) | 41.68 | 44.05 | +2.37 | n/a (1 unit) | +5.7% | n/a | +2.37 |
| cbramod | AP | P3N2048 | 1 seed (no interval) | 41.68 | 43.96 | +2.28 | n/a (1 unit) | +5.5% | n/a | +2.28 |
| cbramod | AP | P11N2048 | 1 seed (no interval) | 41.68 | 44.09 | +2.42 | n/a (1 unit) | +5.8% | n/a | +2.42 |
| cbramod | AP | P21N2048 | 1 seed (no interval) | 41.68 | 44.12 | +2.44 | n/a (1 unit) | +5.9% | n/a | +2.44 |
| cbramod | PR-AUC trapz | N896 | 1 seed (no interval) | 41.50 | 43.84 | +2.34 | n/a (1 unit) | +5.6% | n/a | +2.34 |
| cbramod | PR-AUC trapz | N1664 | 1 seed (no interval) | 41.50 | 43.83 | +2.33 | n/a (1 unit) | +5.6% | n/a | +2.33 |
| cbramod | PR-AUC trapz | N2048 | 1 seed (no interval) | 41.50 | 43.87 | +2.37 | n/a (1 unit) | +5.7% | n/a | +2.37 |
| cbramod | PR-AUC trapz | N4174 | 1 seed (no interval) | 41.50 | 43.85 | +2.35 | n/a (1 unit) | +5.7% | n/a | +2.35 |
| cbramod | PR-AUC trapz | P3N2048 | 1 seed (no interval) | 41.50 | 43.76 | +2.26 | n/a (1 unit) | +5.5% | n/a | +2.26 |
| cbramod | PR-AUC trapz | P11N2048 | 1 seed (no interval) | 41.50 | 43.90 | +2.40 | n/a (1 unit) | +5.8% | n/a | +2.40 |
| cbramod | PR-AUC trapz | P21N2048 | 1 seed (no interval) | 41.50 | 43.92 | +2.42 | n/a (1 unit) | +5.8% | n/a | +2.42 |

ROC reference for the same curves (unchanged; the E30 rules do apply to ROC):

| model | N896 | N1664 | N2048 | N4174 | P3N2048 | P11N2048 | P21N2048 | LP | C2 | numbers | C3 | numbers |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| biot | 64.50 | 64.42 | 64.43 | 64.60 | 63.56 | 64.29 | 64.62 | 65.09 | not testable: adaptation adds nothing at any N | best N 4174 (64.60), best - N4174 +0.00, range 0.17, v - LP -0.67 to -0.50 | uninformative | range 1.06, v - LP -1.53 to -0.48 |
| cbramod | 92.22 | 92.22 | 92.23 | 92.23 | 92.21 | 92.23 | 92.23 | 92.01 | not testable: adaptation adds nothing at any N | best N 2048 (92.23), best - N4174 +0.00, range 0.01, v - LP +0.21 to +0.22 | uninformative | range 0.03, v - LP +0.20 to +0.23 |

## 3. C2/C3 on the Siena rotations, BIOT: every curve point against LP

The D29 records (`last`; LP = S3LPBD / S3FLPBD, same head). Units = the 5 rotation means of 3 seeds. N896-N4174 are the C2 ladder, P2-P10 the C3 points at N2048.

| setting | head | metric | point | base mean | arm mean | difference | 95% t | relative | excludes 0 | NB 95% | > 0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Siena | linear | AP | N896 | 1.64 | 2.64 | +0.99 | [+0.05, +1.93] | +60.5% | yes | [-0.56, +2.55] | 5/5 |
| Siena | linear | AP | N1664 | 1.64 | 2.64 | +1.00 | [+0.04, +1.95] | +60.5% | yes | [-0.58, +2.57] | 5/5 |
| Siena | linear | AP | N2048 | 1.64 | 2.64 | +0.99 | [+0.03, +1.95] | +60.4% | yes | [-0.59, +2.58] | 5/5 |
| Siena | linear | AP | N4174 | 1.64 | 2.63 | +0.99 | [+0.04, +1.93] | +60.0% | yes | [-0.58, +2.55] | 5/5 |
| Siena | linear | AP | P2N2048 | 1.64 | 2.59 | +0.95 | [-0.01, +1.91] | +57.7% | no | [-0.64, +2.54] | 5/5 |
| Siena | linear | AP | P5N2048 | 1.64 | 2.70 | +1.05 | [+0.04, +2.07] | +64.1% | yes | [-0.62, +2.73] | 5/5 |
| Siena | linear | AP | P10N2048 | 1.64 | 2.69 | +1.04 | [+0.06, +2.03] | +63.5% | yes | [-0.58, +2.67] | 5/5 |
| Siena | linear | PR-AUC trapz | N896 | 1.52 | 2.49 | +0.97 | [+0.08, +1.85] | +63.6% | yes | [-0.50, +2.43] | 5/5 |
| Siena | linear | PR-AUC trapz | N1664 | 1.52 | 2.49 | +0.97 | [+0.07, +1.86] | +63.7% | yes | [-0.52, +2.45] | 5/5 |
| Siena | linear | PR-AUC trapz | N2048 | 1.52 | 2.48 | +0.97 | [+0.06, +1.87] | +63.5% | yes | [-0.53, +2.46] | 5/5 |
| Siena | linear | PR-AUC trapz | N4174 | 1.52 | 2.48 | +0.96 | [+0.07, +1.85] | +63.2% | yes | [-0.51, +2.43] | 5/5 |
| Siena | linear | PR-AUC trapz | P2N2048 | 1.52 | 2.44 | +0.92 | [+0.02, +1.83] | +60.7% | yes | [-0.57, +2.42] | 5/5 |
| Siena | linear | PR-AUC trapz | P5N2048 | 1.52 | 2.54 | +1.02 | [+0.07, +1.97] | +67.3% | yes | [-0.55, +2.60] | 5/5 |
| Siena | linear | PR-AUC trapz | P10N2048 | 1.52 | 2.53 | +1.01 | [+0.09, +1.94] | +66.6% | yes | [-0.52, +2.54] | 5/5 |
| Siena | linear_z | AP | N896 | 6.24 | 6.69 | +0.44 | [-0.37, +1.26] | +7.1% | no | [-0.91, +1.80] | 4/5 |
| Siena | linear_z | AP | N1664 | 6.24 | 6.69 | +0.45 | [-0.39, +1.28] | +7.2% | no | [-0.94, +1.83] | 4/5 |
| Siena | linear_z | AP | N2048 | 6.24 | 6.69 | +0.45 | [-0.36, +1.27] | +7.2% | no | [-0.90, +1.80] | 4/5 |
| Siena | linear_z | AP | N4174 | 6.24 | 6.70 | +0.45 | [-0.35, +1.26] | +7.3% | no | [-0.88, +1.78] | 4/5 |
| Siena | linear_z | AP | P2N2048 | 6.24 | 6.68 | +0.44 | [-0.40, +1.28] | +7.1% | no | [-0.95, +1.83] | 4/5 |
| Siena | linear_z | AP | P5N2048 | 6.24 | 6.78 | +0.54 | [-0.20, +1.27] | +8.6% | no | [-0.67, +1.74] | 5/5 |
| Siena | linear_z | AP | P10N2048 | 6.24 | 6.70 | +0.46 | [-0.32, +1.24] | +7.4% | no | [-0.83, +1.75] | 4/5 |
| Siena | linear_z | PR-AUC trapz | N896 | 6.03 | 6.46 | +0.43 | [-0.40, +1.27] | +7.2% | no | [-0.95, +1.81] | 4/5 |
| Siena | linear_z | PR-AUC trapz | N1664 | 6.03 | 6.46 | +0.43 | [-0.42, +1.29] | +7.2% | no | [-0.98, +1.85] | 4/5 |
| Siena | linear_z | PR-AUC trapz | N2048 | 6.03 | 6.47 | +0.44 | [-0.39, +1.27] | +7.3% | no | [-0.94, +1.82] | 4/5 |
| Siena | linear_z | PR-AUC trapz | N4174 | 6.03 | 6.47 | +0.44 | [-0.38, +1.26] | +7.3% | no | [-0.92, +1.80] | 4/5 |
| Siena | linear_z | PR-AUC trapz | P2N2048 | 6.03 | 6.46 | +0.43 | [-0.43, +1.29] | +7.1% | no | [-0.99, +1.85] | 4/5 |
| Siena | linear_z | PR-AUC trapz | P5N2048 | 6.03 | 6.55 | +0.52 | [-0.23, +1.27] | +8.6% | no | [-0.72, +1.76] | 5/5 |
| Siena | linear_z | PR-AUC trapz | P10N2048 | 6.03 | 6.48 | +0.45 | [-0.35, +1.24] | +7.4% | no | [-0.87, +1.77] | 4/5 |
| Siena filtered | linear | AP | N896 | 5.77 | 5.66 | -0.11 | [-4.83, +4.61] | -2.0% | no | [-7.92, +7.69] | 3/5 |
| Siena filtered | linear | AP | N1664 | 5.77 | 5.60 | -0.17 | [-4.83, +4.49] | -2.9% | no | [-7.88, +7.54] | 3/5 |
| Siena filtered | linear | AP | N2048 | 5.77 | 5.59 | -0.18 | [-4.81, +4.45] | -3.1% | no | [-7.83, +7.48] | 3/5 |
| Siena filtered | linear | AP | N4174 | 5.77 | 5.62 | -0.15 | [-4.82, +4.52] | -2.6% | no | [-7.87, +7.57] | 3/5 |
| Siena filtered | linear | AP | P2N2048 | 5.77 | 5.74 | -0.03 | [-4.75, +4.69] | -0.6% | no | [-7.84, +7.78] | 3/5 |
| Siena filtered | linear | AP | P5N2048 | 5.77 | 5.63 | -0.14 | [-4.72, +4.43] | -2.5% | no | [-7.71, +7.42] | 3/5 |
| Siena filtered | linear | AP | P10N2048 | 5.77 | 5.53 | -0.24 | [-4.82, +4.35] | -4.1% | no | [-7.82, +7.35] | 3/5 |
| Siena filtered | linear | PR-AUC trapz | N896 | 5.42 | 5.36 | -0.07 | [-4.59, +4.46] | -1.2% | no | [-7.55, +7.42] | 3/5 |
| Siena filtered | linear | PR-AUC trapz | N1664 | 5.42 | 5.30 | -0.12 | [-4.59, +4.35] | -2.2% | no | [-7.51, +7.28] | 3/5 |
| Siena filtered | linear | PR-AUC trapz | N2048 | 5.42 | 5.30 | -0.13 | [-4.57, +4.31] | -2.3% | no | [-7.47, +7.22] | 3/5 |
| Siena filtered | linear | PR-AUC trapz | N4174 | 5.42 | 5.32 | -0.10 | [-4.58, +4.37] | -1.9% | no | [-7.50, +7.30] | 3/5 |
| Siena filtered | linear | PR-AUC trapz | P2N2048 | 5.42 | 5.41 | -0.01 | [-4.53, +4.50] | -0.3% | no | [-7.48, +7.45] | 3/5 |
| Siena filtered | linear | PR-AUC trapz | P5N2048 | 5.42 | 5.33 | -0.09 | [-4.49, +4.30] | -1.7% | no | [-7.36, +7.17] | 3/5 |
| Siena filtered | linear | PR-AUC trapz | P10N2048 | 5.42 | 5.24 | -0.18 | [-4.58, +4.22] | -3.4% | no | [-7.46, +7.10] | 3/5 |
| Siena filtered | linear_z | AP | N896 | 5.66 | 5.73 | +0.08 | [-0.33, +0.48] | +1.4% | no | [-0.59, +0.75] | 2/5 |
| Siena filtered | linear_z | AP | N1664 | 5.66 | 5.73 | +0.07 | [-0.33, +0.48] | +1.3% | no | [-0.59, +0.74] | 2/5 |
| Siena filtered | linear_z | AP | N2048 | 5.66 | 5.72 | +0.06 | [-0.34, +0.47] | +1.1% | no | [-0.60, +0.73] | 2/5 |
| Siena filtered | linear_z | AP | N4174 | 5.66 | 5.71 | +0.06 | [-0.35, +0.46] | +1.0% | no | [-0.61, +0.72] | 2/5 |
| Siena filtered | linear_z | AP | P2N2048 | 5.66 | 5.69 | +0.04 | [-0.36, +0.44] | +0.7% | no | [-0.62, +0.70] | 2/5 |
| Siena filtered | linear_z | AP | P5N2048 | 5.66 | 5.70 | +0.05 | [-0.37, +0.46] | +0.8% | no | [-0.64, +0.73] | 2/5 |
| Siena filtered | linear_z | AP | P10N2048 | 5.66 | 5.64 | -0.02 | [-0.57, +0.53] | -0.3% | no | [-0.93, +0.89] | 2/5 |
| Siena filtered | linear_z | PR-AUC trapz | N896 | 5.43 | 5.51 | +0.08 | [-0.32, +0.48] | +1.4% | no | [-0.58, +0.74] | 2/5 |
| Siena filtered | linear_z | PR-AUC trapz | N1664 | 5.43 | 5.50 | +0.08 | [-0.32, +0.47] | +1.4% | no | [-0.58, +0.73] | 2/5 |
| Siena filtered | linear_z | PR-AUC trapz | N2048 | 5.43 | 5.49 | +0.06 | [-0.33, +0.46] | +1.2% | no | [-0.59, +0.72] | 2/5 |
| Siena filtered | linear_z | PR-AUC trapz | N4174 | 5.43 | 5.49 | +0.06 | [-0.34, +0.45] | +1.1% | no | [-0.60, +0.71] | 2/5 |
| Siena filtered | linear_z | PR-AUC trapz | P2N2048 | 5.43 | 5.47 | +0.04 | [-0.35, +0.43] | +0.7% | no | [-0.61, +0.68] | 2/5 |
| Siena filtered | linear_z | PR-AUC trapz | P5N2048 | 5.43 | 5.48 | +0.05 | [-0.36, +0.46] | +0.9% | no | [-0.63, +0.72] | 2/5 |
| Siena filtered | linear_z | PR-AUC trapz | P10N2048 | 5.43 | 5.41 | -0.02 | [-0.55, +0.52] | -0.3% | no | [-0.90, +0.87] | 2/5 |

## 4. The noise arm on the rotations, BIOT: `last` against `last_noise`

Same subset, SSL input replaced by noise. Units = the 5 rotation means of 3 paired seeds. The D29 noise rule ("mean > 3 and the interval excludes 0") is a ROC rule and is NOT applied here; the columns below are the measurement.

| setting | head | metric | point | base mean | arm mean | difference | 95% t | relative | excludes 0 | NB 95% | > 0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Siena | linear | AP | N896 | 2.22 | 2.64 | +0.42 | [+0.23, +0.60] | +18.7% | yes | [+0.11, +0.72] | 5/5 |
| Siena | linear | AP | N1664 | 2.23 | 2.64 | +0.41 | [+0.22, +0.61] | +18.6% | yes | [+0.09, +0.74] | 5/5 |
| Siena | linear | AP | N2048 | 2.23 | 2.64 | +0.41 | [+0.21, +0.61] | +18.3% | yes | [+0.08, +0.74] | 5/5 |
| Siena | linear | AP | N4174 | 2.23 | 2.63 | +0.40 | [+0.21, +0.60] | +18.2% | yes | [+0.09, +0.72] | 5/5 |
| Siena | linear | AP | P2N2048 | 2.24 | 2.59 | +0.35 | [+0.18, +0.52] | +15.7% | yes | [+0.07, +0.63] | 5/5 |
| Siena | linear | AP | P5N2048 | 2.19 | 2.70 | +0.50 | [+0.20, +0.80] | +22.9% | yes | [+0.00, +1.00] | 5/5 |
| Siena | linear | AP | P10N2048 | 2.21 | 2.69 | +0.48 | [+0.22, +0.74] | +21.7% | yes | [+0.05, +0.91] | 5/5 |
| Siena | linear | PR-AUC trapz | N896 | 2.07 | 2.49 | +0.41 | [+0.20, +0.62] | +19.9% | yes | [+0.07, +0.76] | 5/5 |
| Siena | linear | PR-AUC trapz | N1664 | 2.08 | 2.49 | +0.41 | [+0.19, +0.63] | +19.8% | yes | [+0.04, +0.78] | 5/5 |
| Siena | linear | PR-AUC trapz | N2048 | 2.08 | 2.48 | +0.40 | [+0.18, +0.63] | +19.4% | yes | [+0.04, +0.77] | 5/5 |
| Siena | linear | PR-AUC trapz | N4174 | 2.08 | 2.48 | +0.40 | [+0.19, +0.62] | +19.4% | yes | [+0.05, +0.76] | 5/5 |
| Siena | linear | PR-AUC trapz | P2N2048 | 2.09 | 2.44 | +0.35 | [+0.15, +0.55] | +16.7% | yes | [+0.02, +0.68] | 5/5 |
| Siena | linear | PR-AUC trapz | P5N2048 | 2.05 | 2.54 | +0.49 | [+0.20, +0.79] | +24.1% | yes | [+0.00, +0.99] | 5/5 |
| Siena | linear | PR-AUC trapz | P10N2048 | 2.06 | 2.53 | +0.47 | [+0.21, +0.73] | +22.9% | yes | [+0.04, +0.90] | 5/5 |
| Siena | linear_z | AP | N896 | 6.37 | 6.69 | +0.32 | [-0.33, +0.96] | +5.0% | no | [-0.75, +1.38] | 3/5 |
| Siena | linear_z | AP | N1664 | 6.37 | 6.69 | +0.32 | [-0.34, +0.98] | +5.1% | no | [-0.77, +1.42] | 3/5 |
| Siena | linear_z | AP | N2048 | 6.37 | 6.69 | +0.32 | [-0.32, +0.97] | +5.1% | no | [-0.74, +1.39] | 3/5 |
| Siena | linear_z | AP | N4174 | 6.37 | 6.70 | +0.33 | [-0.31, +0.96] | +5.1% | no | [-0.72, +1.38] | 3/5 |
| Siena | linear_z | AP | P2N2048 | 6.52 | 6.68 | +0.17 | [-0.24, +0.57] | +2.5% | no | [-0.50, +0.83] | 3/5 |
| Siena | linear_z | AP | P5N2048 | 6.35 | 6.78 | +0.43 | [-0.17, +1.03] | +6.7% | no | [-0.57, +1.42] | 4/5 |
| Siena | linear_z | AP | P10N2048 | 6.35 | 6.70 | +0.35 | [-0.26, +0.96] | +5.5% | no | [-0.66, +1.37] | 4/5 |
| Siena | linear_z | PR-AUC trapz | N896 | 6.16 | 6.46 | +0.31 | [-0.36, +0.97] | +5.0% | no | [-0.79, +1.40] | 3/5 |
| Siena | linear_z | PR-AUC trapz | N1664 | 6.15 | 6.46 | +0.31 | [-0.37, +0.99] | +5.1% | no | [-0.81, +1.44] | 3/5 |
| Siena | linear_z | PR-AUC trapz | N2048 | 6.16 | 6.47 | +0.31 | [-0.35, +0.97] | +5.1% | no | [-0.78, +1.41] | 3/5 |
| Siena | linear_z | PR-AUC trapz | N4174 | 6.15 | 6.47 | +0.32 | [-0.34, +0.97] | +5.2% | no | [-0.76, +1.40] | 3/5 |
| Siena | linear_z | PR-AUC trapz | P2N2048 | 6.31 | 6.46 | +0.15 | [-0.25, +0.56] | +2.4% | no | [-0.52, +0.83] | 3/5 |
| Siena | linear_z | PR-AUC trapz | P5N2048 | 6.14 | 6.55 | +0.41 | [-0.20, +1.03] | +6.7% | no | [-0.61, +1.44] | 4/5 |
| Siena | linear_z | PR-AUC trapz | P10N2048 | 6.14 | 6.48 | +0.34 | [-0.29, +0.97] | +5.5% | no | [-0.70, +1.38] | 3/5 |
| Siena filtered | linear | AP | N896 | 4.99 | 5.66 | +0.67 | [-1.08, +2.41] | +13.4% | no | [-2.22, +3.55] | 3/5 |
| Siena filtered | linear | AP | N1664 | 4.95 | 5.60 | +0.65 | [-1.01, +2.31] | +13.1% | no | [-2.10, +3.40] | 3/5 |
| Siena filtered | linear | AP | N2048 | 4.95 | 5.59 | +0.64 | [-0.99, +2.28] | +13.0% | no | [-2.06, +3.34] | 3/5 |
| Siena filtered | linear | AP | N4174 | 4.95 | 5.62 | +0.67 | [-1.01, +2.35] | +13.4% | no | [-2.11, +3.44] | 3/5 |
| Siena filtered | linear | AP | P2N2048 | 4.97 | 5.74 | +0.77 | [-0.92, +2.47] | +15.6% | no | [-2.03, +3.58] | 3/5 |
| Siena filtered | linear | AP | P5N2048 | 4.98 | 5.63 | +0.64 | [-0.95, +2.24] | +12.9% | no | [-1.99, +3.28] | 3/5 |
| Siena filtered | linear | AP | P10N2048 | 4.96 | 5.53 | +0.58 | [-1.05, +2.20] | +11.6% | no | [-2.11, +3.26] | 3/5 |
| Siena filtered | linear | PR-AUC trapz | N896 | 4.71 | 5.36 | +0.65 | [-1.03, +2.33] | +13.8% | no | [-2.13, +3.42] | 3/5 |
| Siena filtered | linear | PR-AUC trapz | N1664 | 4.67 | 5.30 | +0.63 | [-0.97, +2.23] | +13.5% | no | [-2.02, +3.28] | 3/5 |
| Siena filtered | linear | PR-AUC trapz | N2048 | 4.67 | 5.30 | +0.63 | [-0.94, +2.20] | +13.4% | no | [-1.97, +3.23] | 3/5 |
| Siena filtered | linear | PR-AUC trapz | N4174 | 4.67 | 5.32 | +0.65 | [-0.96, +2.25] | +13.8% | no | [-2.02, +3.31] | 3/5 |
| Siena filtered | linear | PR-AUC trapz | P2N2048 | 4.68 | 5.41 | +0.72 | [-0.90, +2.34] | +15.5% | no | [-1.96, +3.40] | 3/5 |
| Siena filtered | linear | PR-AUC trapz | P5N2048 | 4.70 | 5.33 | +0.63 | [-0.92, +2.17] | +13.3% | no | [-1.93, +3.19] | 3/5 |
| Siena filtered | linear | PR-AUC trapz | P10N2048 | 4.68 | 5.24 | +0.56 | [-1.00, +2.13] | +12.1% | no | [-2.02, +3.15] | 3/5 |
| Siena filtered | linear_z | AP | N896 | 5.75 | 5.73 | -0.02 | [-0.20, +0.16] | -0.4% | no | [-0.32, +0.28] | 3/5 |
| Siena filtered | linear_z | AP | N1664 | 5.67 | 5.73 | +0.06 | [-0.31, +0.43] | +1.1% | no | [-0.55, +0.67] | 3/5 |
| Siena filtered | linear_z | AP | N2048 | 5.67 | 5.72 | +0.04 | [-0.32, +0.41] | +0.8% | no | [-0.57, +0.65] | 3/5 |
| Siena filtered | linear_z | AP | N4174 | 5.67 | 5.71 | +0.04 | [-0.32, +0.41] | +0.8% | no | [-0.56, +0.65] | 3/5 |
| Siena filtered | linear_z | AP | P2N2048 | 5.68 | 5.69 | +0.02 | [-0.11, +0.15] | +0.3% | no | [-0.19, +0.23] | 4/5 |
| Siena filtered | linear_z | AP | P5N2048 | 5.75 | 5.70 | -0.05 | [-0.28, +0.19] | -0.8% | no | [-0.43, +0.34] | 2/5 |
| Siena filtered | linear_z | AP | P10N2048 | 5.75 | 5.64 | -0.11 | [-0.50, +0.28] | -1.9% | no | [-0.76, +0.53] | 3/5 |
| Siena filtered | linear_z | PR-AUC trapz | N896 | 5.53 | 5.51 | -0.02 | [-0.20, +0.15] | -0.4% | no | [-0.31, +0.26] | 3/5 |
| Siena filtered | linear_z | PR-AUC trapz | N1664 | 5.45 | 5.50 | +0.06 | [-0.30, +0.42] | +1.1% | no | [-0.54, +0.66] | 3/5 |
| Siena filtered | linear_z | PR-AUC trapz | N2048 | 5.45 | 5.49 | +0.04 | [-0.32, +0.41] | +0.8% | no | [-0.56, +0.65] | 3/5 |
| Siena filtered | linear_z | PR-AUC trapz | N4174 | 5.44 | 5.49 | +0.04 | [-0.32, +0.40] | +0.8% | no | [-0.55, +0.64] | 3/5 |
| Siena filtered | linear_z | PR-AUC trapz | P2N2048 | 5.45 | 5.47 | +0.02 | [-0.10, +0.14] | +0.3% | no | [-0.18, +0.21] | 4/5 |
| Siena filtered | linear_z | PR-AUC trapz | P5N2048 | 5.52 | 5.48 | -0.05 | [-0.27, +0.18] | -0.8% | no | [-0.42, +0.33] | 2/5 |
| Siena filtered | linear_z | PR-AUC trapz | P10N2048 | 5.52 | 5.41 | -0.11 | [-0.49, +0.26] | -2.0% | no | [-0.73, +0.51] | 3/5 |

## 5. The CBraMod fixed-compute control on the rotations (D27-C reading)

S3CC / S3FCC `last` at seed S_r against its batch-128 LP S3CLPB / S3FCLPB at S_r; linear head only (no CBraMod linear_z or noise run at fixed compute). Units = the 5 rotations, 1 seed each.

| setting | metric | point | base mean | arm mean | difference | 95% t | relative | excludes 0 | > 0 |
|---|---|---|---|---|---|---|---|---|---|
| Siena | AP | N896 | 12.85 | 14.89 | +2.03 | [-2.87, +6.94] | +15.8% | no | 3/5 |
| Siena | AP | N4174 | 12.85 | 14.87 | +2.01 | [-2.88, +6.90] | +15.7% | no | 3/5 |
| Siena | AP | P2N2048 | 12.85 | 14.86 | +2.01 | [-2.85, +6.87] | +15.6% | no | 3/5 |
| Siena | AP | P10N2048 | 12.85 | 14.89 | +2.04 | [-2.87, +6.95] | +15.9% | no | 3/5 |
| Siena | PR-AUC trapz | N896 | 12.50 | 14.41 | +1.91 | [-2.89, +6.71] | +15.3% | no | 3/5 |
| Siena | PR-AUC trapz | N4174 | 12.50 | 14.39 | +1.89 | [-2.89, +6.67] | +15.1% | no | 3/5 |
| Siena | PR-AUC trapz | P2N2048 | 12.50 | 14.39 | +1.89 | [-2.87, +6.64] | +15.1% | no | 3/5 |
| Siena | PR-AUC trapz | P10N2048 | 12.50 | 14.41 | +1.92 | [-2.88, +6.72] | +15.3% | no | 3/5 |
| Siena filtered | AP | N896 | 28.01 | 33.03 | +5.02 | [-6.86, +16.91] | +17.9% | no | 4/5 |
| Siena filtered | AP | N4174 | 28.01 | 33.03 | +5.02 | [-6.88, +16.93] | +17.9% | no | 4/5 |
| Siena filtered | AP | P2N2048 | 28.01 | 32.93 | +4.92 | [-6.98, +16.82] | +17.6% | no | 4/5 |
| Siena filtered | AP | P10N2048 | 28.01 | 33.18 | +5.18 | [-6.58, +16.94] | +18.5% | no | 4/5 |
| Siena filtered | PR-AUC trapz | N896 | 27.49 | 32.53 | +5.04 | [-7.12, +17.20] | +18.3% | no | 4/5 |
| Siena filtered | PR-AUC trapz | N4174 | 27.49 | 32.54 | +5.04 | [-7.14, +17.23] | +18.3% | no | 4/5 |
| Siena filtered | PR-AUC trapz | P2N2048 | 27.49 | 32.46 | +4.97 | [-7.18, +17.13] | +18.1% | no | 4/5 |
| Siena filtered | PR-AUC trapz | P10N2048 | 27.49 | 32.71 | +5.22 | [-6.79, +17.23] | +19.0% | no | 4/5 |

ROC reference for the same control (unchanged):

| setting | N896 | N4174 | P2N2048 | P10N2048 | LP | C2 | numbers | C3 | numbers |
|---|---|---|---|---|---|---|---|---|---|
| Siena | 84.59 | 84.58 | 84.56 | 84.60 | 82.57 | not testable: adaptation adds nothing at any N | best N 896 (84.59), best - N4174 +0.00, range 0.00, v - LP +2.01 to +2.01 | uninformative | range 0.05, v - LP +1.99 to +2.03 |
| Siena filtered | 90.06 | 90.06 | 90.06 | 90.06 | 89.95 | not testable: adaptation adds nothing at any N | best N 896 (90.06), best - N4174 +0.00, range 0.00, v - LP +0.11 to +0.11 | uninformative | range 0.00, v - LP +0.11 to +0.11 |

## 6. Counts

- C1: 10 of 68 PR-AUC intervals exclude 0.
- C2/C3 and noise contrasts (156 PR-AUC readings): excludes 0, positive 27, includes 0 115, no interval (1 unit) 14
- No practical-importance label is attached to any of them: no PR-AUC margin is defined (see the statement at the top of this file).

## Commands

```
.venv/bin/python scripts/analysis/d29_read.py
```
