# D27-A noise controls: last - last_noise (summary of cpu.md section 2)

Script: scripts/analysis/d27_cpu.py (same run as cpu.md / cpu.json). ROC-AUC x100, val-selected epoch, eval-mode probe, encoder tap. Rule (notes/decisions.md D27-A and 'D27 addition'): D19 three-way on last - last_noise per head ('the gain needs EEG data' if last wins by the D18 paired rule, |mean| > 3 and >= 4 of 5 units positive; 'perturbation alone explains it' if |mean| <= 3; else 'unclear'); units = 5 rotation means over the seeds S_r/1000+r/2000+r, or the 5 paper-split seeds (A1); TOST margin 3, alpha 0.05, t df 4, 'equivalent' only if TOST rejects. A4, A5 and A7 have 1 seed per rotation and are descriptive. last - lp and last_noise - lp are descriptive.

## Registered readings (18 rows)

| item | setting | model | head | last - last_noise, mean [90% t] | per unit | D19 | TOST p | equivalent | last - lp / last_noise - lp | lp / last / last_noise |
|---|---|---|---|---|---|---|---|---|---|---|
| E27 | CHB-MIT | biot | linear | +0.81 [-2.34, +3.96] | -2.0, +1.6, -0.2, -1.5, +6.2 | perturbation alone explains it | 0.1063 | no | +1.9 / +1.1 | 65.1 / 67.0 / 66.2 |
| E27 | Siena | biot | linear | +1.58 [-1.43, +4.60] | +1.0, +4.5, +2.8, +3.2, -3.6 | perturbation alone explains it | 0.1864 | no | +9.2 / +7.6 | 51.3 / 60.6 / 59.0 |
| E27 | Siena | cbramod | linear | -0.07 [-0.11, -0.03] | -0.1, -0.1, -0.1, -0.1, -0.0 | perturbation alone explains it | 4.7e-09 | yes | +0.3 / +0.3 | 81.4 / 81.7 / 81.8 |
| E27 | Siena filtered | biot | linear | +1.26 [-0.75, +3.26] | +0.0, +4.1, -1.0, +2.7, +0.5 | perturbation alone explains it | 0.0688 | no | +4.1 / +2.9 | 69.8 / 73.9 / 72.6 |
| E27 | Siena filtered | cbramod | linear | -0.02 [-0.04, -0.00] | -0.0, -0.0, -0.1, +0.0, -0.0 | perturbation alone explains it | 2.3e-10 | yes | +0.1 / +0.2 | 89.5 / 89.6 / 89.6 |
| A1 | CHB-MIT paper split, q95 | biot | linear | +8.58 [+6.53, +10.62] | +6.5, +10.6, +11.2, +7.1, +7.5 | the gain needs EEG data | 0.9978 | no | +8.8 / +0.2 | 33.1 / 41.9 / 33.3 |
| A1 | CHB-MIT paper split, q95 | biot | mlp_fullft | +9.06 [+6.76, +11.35] | +7.3, +9.9, +12.6, +6.5, +8.9 | the gain needs EEG data | 0.9976 | no | +8.6 / -0.4 | 32.5 / 41.1 / 32.1 |
| A1 | CHB-MIT paper split, q95 | biot | linear_z | +0.46 [-0.18, +1.10] | +1.1, -0.0, -0.4, +0.6, +1.0 | perturbation alone explains it | 0.0005 | yes | +0.6 / +0.2 | 70.2 / 70.8 / 70.4 |
| A2 | Siena filtered, q95 | biot | linear | +1.43 [-2.01, +4.87] | +0.4, +6.6, +3.1, -2.9, -0.0 | perturbation alone explains it | 0.1933 | no | +3.7 / +2.3 | 54.1 / 57.9 / 56.5 |
| A2 | Siena filtered, q95 | biot | linear_z | +0.36 [-0.68, +1.40] | +0.2, +0.6, -0.7, -0.5, +2.1 | perturbation alone explains it | 0.0028 | yes | +0.4 / +0.0 | 71.5 / 71.8 / 71.5 |
| A3 | CHB-MIT, E32 partition | biot | linear | +1.42 [-1.05, +3.89] | +0.4, +1.2, -2.1, +4.6, +3.1 | perturbation alone explains it | 0.1217 | no | +3.6 / +2.2 | 61.0 / 64.6 / 63.2 |
| A3 | CHB-MIT, E32 partition | biot | linear_z | +0.30 [-1.10, +1.70] | +0.7, +0.4, -2.2, +1.1, +1.4 | perturbation alone explains it | 0.0073 | yes | +0.7 / +0.4 | 72.6 / 73.3 / 73.0 |
| A3 | Siena, E32 partition | biot | linear | +1.62 [+0.19, +3.06] | +0.2, -0.1, +2.5, +2.3, +3.3 | perturbation alone explains it | 0.0549 | no | +9.0 / +7.4 | 50.7 / 59.8 / 58.2 |
| A3 | Siena, E32 partition | biot | linear_z | +0.43 [-0.77, +1.62] | +0.8, -1.4, +2.1, +0.5, +0.1 | perturbation alone explains it | 0.0051 | yes | +1.7 / +1.3 | 69.4 / 71.1 / 70.6 |
| A6 | Siena | biot | mlp_fullft | +1.98 [+0.09, +3.88] | +1.0, +4.2, +3.8, +1.5, -0.5 | perturbation alone explains it | 0.1586 | no | +11.9 / +9.9 | 51.3 / 63.2 / 61.2 |
| A6 | Siena | biot | linear_z | +0.40 [-0.79, +1.59] | +0.2, -0.1, +0.6, +2.3, -1.1 | perturbation alone explains it | 0.0048 | yes | +1.7 / +1.3 | 68.6 / 70.2 / 69.8 |
| A6 | Siena filtered | biot | mlp_fullft | +1.08 [-1.32, +3.47] | +0.3, +5.5, -0.8, +0.6, -0.2 | perturbation alone explains it | 0.0812 | no | +4.1 / +3.0 | 70.1 / 74.2 / 73.1 |
| A6 | Siena filtered | biot | linear_z | +1.13 [-1.15, +3.42] | +0.5, +5.4, -0.1, -0.1, +0.0 | perturbation alone explains it | 0.0783 | no | +1.9 / +0.8 | 73.3 / 75.2 / 74.1 |

## Descriptive, 1 seed per rotation (20 rows)

| item | setting | model | head | last - last_noise, mean [90% t] | per unit | D19 | TOST p | equivalent | last - lp / last_noise - lp | lp / last / last_noise |
|---|---|---|---|---|---|---|---|---|---|---|
| A4 | CHB-MIT, E29 cell S1LR1 | biot | linear | +1.84 [-5.52, +9.19] | -3.9, -0.2, -0.4, -1.7, +15.4 | perturbation alone explains it | 0.3762 | - | +5.9 / +4.1 | 64.9 / 70.9 / 69.0 |
| A4 | CHB-MIT, E29 cell S1LR1 | biot | linear_z | +1.13 [-4.08, +6.35] | -5.7, +3.9, +1.6, -2.5, +8.4 | perturbation alone explains it | 0.2438 | - | +1.4 / +0.3 | 72.9 / 74.2 / 73.1 |
| A4 | CHB-MIT, E29 cell S1LR3 | biot | linear | +3.98 [-4.57, +12.53] | -2.9, +2.2, +0.4, +0.5, +19.7 | the gain needs EEG data | 0.5904 | - | +6.1 / +2.2 | 64.9 / 71.1 / 67.1 |
| A4 | CHB-MIT, E29 cell S1LR3 | biot | linear_z | -1.60 [-4.65, +1.44] | -4.0, +1.7, +1.7, -5.2, -2.2 | perturbation alone explains it | 0.1919 | - | -0.9 / +0.7 | 72.9 / 72.0 / 73.6 |
| A4 | CHB-MIT, E29 cell S1LR4 | biot | linear | +2.23 [-7.07, +11.53] | -8.8, +1.0, +0.4, +0.4, +18.1 | perturbation alone explains it | 0.4345 | - | +6.4 / +4.1 | 64.9 / 71.3 / 69.1 |
| A4 | CHB-MIT, E29 cell S1LR4 | biot | linear_z | +2.63 [-3.89, +9.14] | -5.3, +3.6, +2.6, -0.9, +13.1 | perturbation alone explains it | 0.4541 | - | +2.8 / +0.2 | 72.9 / 75.7 / 73.0 |
| A4 | CHB-MIT, E29 cell S1LR5 | biot | linear | +1.60 [-8.25, +11.44] | -12.2, +2.4, +1.9, -0.9, +16.8 | perturbation alone explains it | 0.3882 | - | +6.8 / +5.2 | 64.9 / 71.7 / 70.1 |
| A4 | CHB-MIT, E29 cell S1LR5 | biot | linear_z | +3.95 [-4.14, +12.04] | -8.2, +6.5, +4.0, +2.0, +15.4 | the gain needs EEG data | 0.5929 | - | +3.5 / -0.4 | 72.9 / 76.4 / 72.4 |
| A5 | Siena, E29 cell S3LR1 | biot | linear | +3.26 [-2.62, +9.13] | +7.2, -5.1, +4.8, +10.2, -0.8 | unclear | 0.5350 | - | +18.8 / +15.5 | 52.2 / 71.0 / 67.7 |
| A5 | Siena, E29 cell S3LR1 | biot | linear_z | +1.90 [-1.35, +5.15] | +1.6, +1.7, +1.1, +7.3, -2.2 | perturbation alone explains it | 0.2550 | - | +3.9 / +2.0 | 70.3 / 74.2 / 72.3 |
| A5 | Siena, E29 cell S3LR2 | biot | linear | +2.01 [-4.58, +8.60] | +7.5, -9.9, +2.4, +5.6, +4.5 | perturbation alone explains it | 0.3824 | - | +21.1 / +19.1 | 52.2 / 73.3 / 71.3 |
| A5 | Siena, E29 cell S3LR2 | biot | linear_z | -1.11 [-7.50, +5.27] | +1.1, -6.1, -8.5, +8.6, -0.6 | perturbation alone explains it | 0.2814 | - | +3.2 / +4.4 | 70.3 / 73.5 / 74.6 |
| A5 | Siena, E29 cell S3LR3 | biot | linear | +2.57 [-0.25, +5.39] | +3.7, +5.6, +1.4, +4.1, -2.0 | perturbation alone explains it | 0.3814 | - | +9.9 / +7.3 | 52.2 / 62.1 / 59.5 |
| A5 | Siena, E29 cell S3LR3 | biot | linear_z | +1.28 [+0.01, +2.54] | +0.1, +1.8, +3.1, -0.1, +1.4 | perturbation alone explains it | 0.0220 | - | +0.5 / -0.7 | 70.3 / 70.8 / 69.5 |
| A5 | Siena, E29 cell S3LR4 | biot | linear | +2.89 [-3.58, +9.37] | +7.3, -7.2, +4.2, +10.1, -0.0 | perturbation alone explains it | 0.4865 | - | +18.9 / +16.0 | 52.2 / 71.1 / 68.2 |
| A5 | Siena, E29 cell S3LR4 | biot | linear_z | +1.95 [-1.38, +5.28] | +1.8, +2.6, -0.5, +7.4, -1.6 | perturbation alone explains it | 0.2686 | - | +4.3 / +2.3 | 70.3 / 74.6 / 72.6 |
| A5 | Siena, E29 cell S3LR5 | biot | linear | +2.01 [-5.12, +9.13] | +7.6, -11.0, +3.0, +5.6, +4.8 | perturbation alone explains it | 0.3905 | - | +21.5 / +19.5 | 52.2 / 73.7 / 71.7 |
| A5 | Siena, E29 cell S3LR5 | biot | linear_z | -0.79 [-7.44, +5.86] | +0.7, -6.5, -8.6, +8.9, +1.5 | perturbation alone explains it | 0.2586 | - | +3.6 / +4.4 | 70.3 / 73.9 / 74.7 |
| A7 | Siena, ssl_seed 11 | biot | linear | +2.71 [+0.52, +4.91] | +1.9, +3.7, +3.7, +5.1, -0.9 | perturbation alone explains it | 0.3973 | - | +6.8 / +4.1 | 52.2 / 59.1 / 56.3 |
| A7 | Siena, ssl_seed 12 | biot | linear | +2.73 [+0.54, +4.93] | +1.9, +3.7, +3.7, +5.2, -0.8 | perturbation alone explains it | 0.4047 | - | +6.8 / +4.1 | 52.2 / 59.1 / 56.3 |

## Counts

- registered, 'the gain needs EEG data': 2 of 18; TOST equivalent in 0: A1 CHB-MIT paper split, q95 biot linear +8.58; A1 CHB-MIT paper split, q95 biot mlp_fullft +9.06
- registered, 'unclear': 0 of 18; TOST equivalent in 0
- registered, 'perturbation alone explains it': 16 of 18; TOST equivalent in 7
- descriptive, 'the gain needs EEG data': 2 of 20: A4 CHB-MIT, E29 cell S1LR3 biot linear +3.98; A4 CHB-MIT, E29 cell S1LR5 biot linear_z +3.95
- descriptive, 'unclear': 1 of 20: A5 Siena, E29 cell S3LR1 biot linear +3.26
- descriptive, 'perturbation alone explains it': 17 of 20

Head-dependent D19 readings (raw head and linear_z disagree): A1 CHB-MIT paper split, q95 biot: linear the gain needs EEG data, linear_z perturbation alone explains it, mlp_fullft the gain needs EEG data; A4 CHB-MIT, E29 cell S1LR3 biot: linear the gain needs EEG data, linear_z perturbation alone explains it; A4 CHB-MIT, E29 cell S1LR5 biot: linear perturbation alone explains it, linear_z the gain needs EEG data; A5 Siena, E29 cell S3LR1 biot: linear unclear, linear_z perturbation alone explains it

Rows where lp, last and last_noise all average below ROC 50 (the difference is between below-chance scores): A1 CHB-MIT paper split, q95 biot linear; A1 CHB-MIT paper split, q95 biot mlp_fullft

## Checks

- P1QN vs P1Q (lp/last; linear/mlp_fullft): 20 of 20 paired values identical (max |diff| 0)
- S3FQN vs S3FQ (lp/last; linear): 30 of 30 paired values identical (max |diff| 0)
- S1LRN1 last linear vs E29 cell 1 (S_r): 5 of 5 paired values identical (max |diff| 0)
- S1LRN3 last linear vs E29 cell 3 (S_r): 5 of 5 paired values identical (max |diff| 0)
- S1LRN4 last linear vs E29 cell 4 (S_r): 5 of 5 paired values identical (max |diff| 0)
- S1LRN5 last linear vs E29 cell 5 (S_r): 5 of 5 paired values identical (max |diff| 0)
- S3LRN1 last linear vs E29 cell 1 (S_r): 5 of 5 paired values identical (max |diff| 0)
- S3LRN2 last linear vs E29 cell 2 (S_r): 5 of 5 paired values identical (max |diff| 0)
- S3LRN3 last linear vs E29 cell 3 (S_r): 5 of 5 paired values identical (max |diff| 0)
- S3LRN4 last linear vs E29 cell 4 (S_r): 5 of 5 paired values identical (max |diff| 0)
- S3LRN5 last linear vs E29 cell 5 (S_r): 5 of 5 paired values identical (max |diff| 0)
- Pairing and provenance (one record per last / last_noise / lp, same eval data, labels, versions, test index, probe spec, adapt spec, derived noise sample): 24 of 24 rows with no gap (340 triples)
- Lp pairings asserted equal to E25 (A6 mlp_fullft), E28 (A7) and E29 (A4/A5 linear lp); E27 rows equal artifacts/analysis/E27/e27.json.

Leave-one-rotation-out (cpu.md section 1): 18 of 80 verdicts change when one rotation is dropped.

## Skipped or partial inputs

- none
