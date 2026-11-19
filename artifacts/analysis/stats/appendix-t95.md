# 95% t-intervals for appendix contrasts (post hoc, descriptive)

Script: scripts/analysis/appendix_t95.py (see its docstring for inputs and checks; all asserted).
t with df 4 over the 5 units; ROC-AUC x100. A1 and E19 DL's-split units are seeds on that split
(seed uncertainty on one split). Rule output = the string printed by the item's reading script.

| item | setting | model | head | contrast | mean | t 95% | t 90% | rule output |
|---|---|---|---|---|---|---|---|---|
| E32 | CHB-MIT | biot | linear | last - lp | +3.61 | [-2.40, +9.62] | [-1.00, +8.23] | first term wins |
| E32 | CHB-MIT | biot | linear | last_randinit - last | +7.84 | [-0.58, +16.26] | [+1.38, +14.31] | first term wins |
| E32 | CHB-MIT | biot | linear | lp - lp_randinit | -11.60 | [-25.27, +2.07] | [-22.09, -1.10] | second term wins |
| E32 | CHB-MIT | biot | linear | last_randinit - lp_randinit | -0.14 | [-0.53, +0.24] | [-0.44, +0.15] | random features explain it |
| E32 | CHB-MIT | cbramod | linear | last - lp | -0.03 | [-0.24, +0.17] | [-0.19, +0.13] | no difference shown |
| E32 | CHB-MIT | cbramod | linear | last_randinit - last | -4.39 | [-7.18, -1.61] | [-6.53, -2.26] | second term wins |
| E32 | CHB-MIT | cbramod | linear | lp - lp_randinit | +4.57 | [+1.22, +7.93] | [+2.00, +7.15] | first term wins |
| E32 | CHB-MIT | cbramod | linear | last_randinit - lp_randinit | +0.15 | [-1.25, +1.55] | [-0.93, +1.22] | random features explain it |
| E32 | Siena | biot | linear | last - lp | +9.04 | [+2.68, +15.39] | [+4.16, +13.92] | first term wins |
| E32 | Siena | biot | linear | last_randinit - last | +5.72 | [-20.71, +32.16] | [-14.57, +26.02] | no difference shown |
| E32 | Siena | biot | linear | lp - lp_randinit | -14.68 | [-36.55, +7.19] | [-31.47, +2.11] | second term wins |
| E32 | Siena | biot | linear | last_randinit - lp_randinit | +0.08 | [-0.26, +0.43] | [-0.18, +0.35] | random features explain it |
| E32 | Siena | cbramod | linear | last - lp | +0.23 | [-0.30, +0.76] | [-0.18, +0.63] | no difference shown |
| E32 | Siena | cbramod | linear | last_randinit - last | -9.94 | [-16.51, -3.38] | [-14.98, -4.90] | second term wins |
| E32 | Siena | cbramod | linear | lp - lp_randinit | +12.36 | [+5.65, +19.08] | [+7.21, +17.52] | first term wins |
| E32 | Siena | cbramod | linear | last_randinit - lp_randinit | +2.65 | [+0.91, +4.39] | [+1.31, +3.99] | random features explain it |
| E27 | CHB-MIT | biot | linear | last - last_noise | +0.81 | [-3.29, +4.91] | [-2.34, +3.96] | perturbation alone explains it |
| E27 | Siena | biot | linear | last - last_noise | +1.58 | [-2.34, +5.51] | [-1.43, +4.60] | perturbation alone explains it |
| E27 | Siena | cbramod | linear | last - last_noise | -0.07 | [-0.13, -0.02] | [-0.11, -0.03] | perturbation alone explains it |
| E27 | Siena filtered | biot | linear | last - last_noise | +1.26 | [-1.36, +3.87] | [-0.75, +3.26] | perturbation alone explains it |
| E27 | Siena filtered | cbramod | linear | last - last_noise | -0.02 | [-0.04, +0.01] | [-0.04, -0.00] | perturbation alone explains it |
| A1 | CHB-MIT paper split, q95 | biot | linear | last - last_noise | +8.58 | [+5.92, +11.24] | [+6.53, +10.62] | the gain needs EEG data |
| A1 | CHB-MIT paper split, q95 | biot | mlp_fullft | last - last_noise | +9.06 | [+6.07, +12.04] | [+6.76, +11.35] | the gain needs EEG data |
| A1 | CHB-MIT paper split, q95 | biot | linear_z | last - last_noise | +0.46 | [-0.38, +1.29] | [-0.18, +1.10] | perturbation alone explains it |
| A2 | Siena filtered, q95 | biot | linear | last - last_noise | +1.43 | [-3.05, +5.91] | [-2.01, +4.87] | perturbation alone explains it |
| A2 | Siena filtered, q95 | biot | linear_z | last - last_noise | +0.36 | [-1.00, +1.72] | [-0.68, +1.40] | perturbation alone explains it |
| A3 | CHB-MIT, E32 partition | biot | linear | last - last_noise | +1.42 | [-1.80, +4.63] | [-1.05, +3.89] | perturbation alone explains it |
| A3 | CHB-MIT, E32 partition | biot | linear_z | last - last_noise | +0.30 | [-1.52, +2.12] | [-1.10, +1.70] | perturbation alone explains it |
| A3 | Siena, E32 partition | biot | linear | last - last_noise | +1.62 | [-0.25, +3.49] | [+0.19, +3.06] | perturbation alone explains it |
| A3 | Siena, E32 partition | biot | linear_z | last - last_noise | +0.43 | [-1.13, +1.99] | [-0.77, +1.62] | perturbation alone explains it |
| A4 | CHB-MIT, E29 cell S1LR1 | biot | linear | last - last_noise | +1.84 | [-7.74, +11.41] | [-5.52, +9.19] | perturbation alone explains it |
| A4 | CHB-MIT, E29 cell S1LR1 | biot | linear_z | last - last_noise | +1.13 | [-5.66, +7.92] | [-4.08, +6.35] | perturbation alone explains it |
| A4 | CHB-MIT, E29 cell S1LR3 | biot | linear | last - last_noise | +3.98 | [-7.16, +15.12] | [-4.57, +12.53] | the gain needs EEG data |
| A4 | CHB-MIT, E29 cell S1LR3 | biot | linear_z | last - last_noise | -1.60 | [-5.57, +2.36] | [-4.65, +1.44] | perturbation alone explains it |
| A4 | CHB-MIT, E29 cell S1LR4 | biot | linear | last - last_noise | +2.23 | [-9.88, +14.35] | [-7.07, +11.53] | perturbation alone explains it |
| A4 | CHB-MIT, E29 cell S1LR4 | biot | linear_z | last - last_noise | +2.63 | [-5.86, +11.11] | [-3.89, +9.14] | perturbation alone explains it |
| A4 | CHB-MIT, E29 cell S1LR5 | biot | linear | last - last_noise | +1.60 | [-11.23, +14.42] | [-8.25, +11.44] | perturbation alone explains it |
| A4 | CHB-MIT, E29 cell S1LR5 | biot | linear_z | last - last_noise | +3.95 | [-6.58, +14.48] | [-4.14, +12.04] | the gain needs EEG data |
| A5 | Siena, E29 cell S3LR1 | biot | linear | last - last_noise | +3.26 | [-4.39, +10.91] | [-2.62, +9.13] | unclear |
| A5 | Siena, E29 cell S3LR1 | biot | linear_z | last - last_noise | +1.90 | [-2.34, +6.13] | [-1.35, +5.15] | perturbation alone explains it |
| A5 | Siena, E29 cell S3LR2 | biot | linear | last - last_noise | +2.01 | [-6.57, +10.59] | [-4.58, +8.60] | perturbation alone explains it |
| A5 | Siena, E29 cell S3LR2 | biot | linear_z | last - last_noise | -1.11 | [-9.43, +7.21] | [-7.50, +5.27] | perturbation alone explains it |
| A5 | Siena, E29 cell S3LR3 | biot | linear | last - last_noise | +2.57 | [-1.10, +6.25] | [-0.25, +5.39] | perturbation alone explains it |
| A5 | Siena, E29 cell S3LR3 | biot | linear_z | last - last_noise | +1.28 | [-0.37, +2.93] | [+0.01, +2.54] | perturbation alone explains it |
| A5 | Siena, E29 cell S3LR4 | biot | linear | last - last_noise | +2.89 | [-5.54, +11.32] | [-3.58, +9.37] | perturbation alone explains it |
| A5 | Siena, E29 cell S3LR4 | biot | linear_z | last - last_noise | +1.95 | [-2.39, +6.28] | [-1.38, +5.28] | perturbation alone explains it |
| A5 | Siena, E29 cell S3LR5 | biot | linear | last - last_noise | +2.01 | [-7.27, +11.29] | [-5.12, +9.13] | perturbation alone explains it |
| A5 | Siena, E29 cell S3LR5 | biot | linear_z | last - last_noise | -0.79 | [-9.45, +7.87] | [-7.44, +5.86] | perturbation alone explains it |
| A6 | Siena | biot | mlp_fullft | last - last_noise | +1.98 | [-0.49, +4.46] | [+0.09, +3.88] | perturbation alone explains it |
| A6 | Siena | biot | linear_z | last - last_noise | +0.40 | [-1.15, +1.95] | [-0.79, +1.59] | perturbation alone explains it |
| A6 | Siena filtered | biot | mlp_fullft | last - last_noise | +1.08 | [-2.05, +4.20] | [-1.32, +3.47] | perturbation alone explains it |
| A6 | Siena filtered | biot | linear_z | last - last_noise | +1.13 | [-1.84, +4.11] | [-1.15, +3.42] | perturbation alone explains it |
| A7 | Siena, ssl_seed 11 | biot | linear | last - last_noise | +2.71 | [-0.15, +5.57] | [+0.52, +4.91] | perturbation alone explains it |
| A7 | Siena, ssl_seed 12 | biot | linear | last - last_noise | +2.73 | [-0.13, +5.59] | [+0.54, +4.93] | perturbation alone explains it |
| E19 q95 | CHB-MIT | biot | linear | last - lp | -1.06 | [-11.54, +9.41] | [-9.10, +6.98] | no difference shown |
| E19 q95 | CHB-MIT | biot | linear | last_randinit - last | +18.52 | [+1.02, +36.02] | [+5.08, +31.96] | first term wins |
| E19 q95 | CHB-MIT | biot | linear | lp - lp_randinit | -17.66 | [-32.91, -2.41] | [-29.37, -5.95] | second term wins |
| E19 q95 | CHB-MIT | biot | linear | last_randinit - lp_randinit | -0.20 | [-0.64, +0.24] | [-0.54, +0.13] | random features explain it |
| E19 q95 | Siena | biot | linear | last - lp | +2.09 | [-4.22, +8.40] | [-2.75, +6.94] | no difference shown |
| E19 q95 | Siena | biot | linear | last_randinit - last | +27.98 | [+9.34, +46.61] | [+13.67, +42.28] | first term wins |
| E19 q95 | Siena | biot | linear | lp - lp_randinit | -30.02 | [-43.03, -17.01] | [-40.01, -20.03] | second term wins |
| E19 q95 | Siena | biot | linear | last_randinit - lp_randinit | +0.04 | [-0.41, +0.50] | [-0.30, +0.39] | random features explain it |
| E19 q95 | Siena filtered | biot | linear | last - lp | +3.75 | [-0.49, +7.98] | [+0.49, +7.00] | first term wins |
| E19 q95 | Siena filtered | biot | linear | last_randinit - last | +18.18 | [-1.06, +37.43] | [+3.41, +32.96] | first term wins |
| E19 q95 | Siena filtered | biot | linear | lp - lp_randinit | -21.87 | [-41.93, -1.82] | [-37.27, -6.47] | second term wins |
| E19 q95 | Siena filtered | biot | linear | last_randinit - lp_randinit | +0.06 | [-0.30, +0.41] | [-0.22, +0.33] | random features explain it |
| E19 q95 | DL's split (seeds) | biot | linear | last - lp | +8.80 | [+6.78, +10.82] | [+7.25, +10.35] | first term wins |
| E19 q95 | DL's split (seeds) | biot | mlp_fullft | last - lp | +8.61 | [+6.24, +10.98] | [+6.79, +10.43] | first term wins |
| E25 | CHB-MIT | biot | mlp_fullft | last - lp | +1.42 | [-0.97, +3.81] | [-0.41, +3.26] | none |
| E25 | CHB-MIT | biot | mlp_fullft | last_randinit - last | +3.23 | [-9.67, +16.12] | [-6.67, +13.12] | none |
| E25 | CHB-MIT | biot | mlp_fullft | lp - lp_randinit | -4.58 | [-15.75, +6.59] | [-13.16, +4.00] | none |
| E25 | CHB-MIT | biot | mlp_fullft | D17 | +0.07 | [-0.11, +0.25] | [-0.07, +0.21] | random features explain it |
| E25 | CHB-MIT | cbramod | mlp_fullft | last - lp | +0.18 | [-1.04, +1.41] | [-0.76, +1.12] | none |
| E25 | CHB-MIT | cbramod | mlp_fullft | last_randinit - last | -4.34 | [-13.10, +4.41] | [-11.06, +2.38] | PRETRAINED wins |
| E25 | CHB-MIT | cbramod | mlp_fullft | lp - lp_randinit | +3.13 | [-5.04, +11.31] | [-3.14, +9.41] | pretrained features win |
| E25 | CHB-MIT | cbramod | mlp_fullft | D17 | -1.03 | [-2.31, +0.25] | [-2.01, -0.04] | random features explain it |
| E25 | Siena | biot | mlp_fullft | last - lp | +11.89 | [-0.16, +23.94] | [+2.63, +21.14] | SA helps |
| E25 | Siena | biot | mlp_fullft | last_randinit - last | +5.21 | [-6.55, +16.97] | [-3.82, +14.24] | none |
| E25 | Siena | biot | mlp_fullft | lp - lp_randinit | -16.24 | [-32.17, -0.31] | [-28.47, -4.01] | RANDOM features win |
| E25 | Siena | biot | mlp_fullft | D17 | +0.86 | [-1.80, +3.51] | [-1.18, +2.90] | random features explain it |
| E25 | Siena | cbramod | mlp_fullft | last - lp | +0.14 | [-0.78, +1.06] | [-0.56, +0.85] | none |
| E25 | Siena | cbramod | mlp_fullft | last_randinit - last | -7.47 | [-18.04, +3.10] | [-15.59, +0.65] | PRETRAINED wins |
| E25 | Siena | cbramod | mlp_fullft | lp - lp_randinit | +8.10 | [-2.87, +19.07] | [-0.33, +16.52] | pretrained features win |
| E25 | Siena | cbramod | mlp_fullft | D17 | +0.77 | [-0.41, +1.95] | [-0.14, +1.67] | random features explain it |
| E25 | Siena filtered | biot | mlp_fullft | last - lp | +4.06 | [-0.90, +9.03] | [+0.26, +7.87] | SA helps |
| E25 | Siena filtered | biot | mlp_fullft | last_randinit - last | +3.63 | [-11.16, +18.41] | [-7.72, +14.98] | none |
| E25 | Siena filtered | biot | mlp_fullft | lp - lp_randinit | -7.51 | [-25.79, +10.77] | [-21.55, +6.52] | none |
| E25 | Siena filtered | biot | mlp_fullft | D17 | +0.18 | [-0.79, +1.15] | [-0.57, +0.93] | random features explain it |
| E25 | Siena filtered | cbramod | mlp_fullft | last - lp | +0.05 | [-0.20, +0.30] | [-0.15, +0.24] | none |
| E25 | Siena filtered | cbramod | mlp_fullft | last_randinit - last | -8.17 | [-15.38, -0.95] | [-13.71, -2.62] | PRETRAINED wins |
| E25 | Siena filtered | cbramod | mlp_fullft | lp - lp_randinit | +7.71 | [+0.06, +15.37] | [+1.83, +13.59] | pretrained features win |
| E25 | Siena filtered | cbramod | mlp_fullft | D17 | -0.41 | [-1.39, +0.58] | [-1.16, +0.35] | random features explain it |
| E28 D24 | CHB-MIT | biot | linear | last - lp | +1.91 | [-0.96, +4.78] | [-0.29, +4.11] | no difference shown |
| E28 D24 | CHB-MIT | biot | linear | last_randinit - last | +0.15 | [-16.76, +17.06] | [-12.83, +13.13] | no difference shown |
| E28 D24 | CHB-MIT | biot | linear | lp - lp_randinit | -1.95 | [-16.98, +13.08] | [-13.49, +9.59] | no difference shown |
| E28 D24 | CHB-MIT | biot | linear | D17 | +0.11 | [-0.13, +0.34] | [-0.07, +0.29] | random features explain it |
| E28 4174 | CHB-MIT | biot | linear | last - lp | +2.65 | [-0.90, +6.19] | [-0.08, +5.37] | no difference shown |
| E28 4174 | CHB-MIT | biot | linear | last_randinit - last | -5.89 | [-28.06, +16.29] | [-22.92, +11.14] | second term wins |
| E28 4174 | CHB-MIT | biot | linear | lp - lp_randinit | +3.16 | [-15.69, +22.00] | [-11.31, +17.63] | first term wins |
| E28 4174 | CHB-MIT | biot | linear | D17 | -0.08 | [-0.56, +0.39] | [-0.45, +0.28] | random features explain it |
| E28 S1D11 | CHB-MIT | biot | linear | last - lp | +2.66 | [-0.87, +6.18] | [-0.05, +5.36] | no difference shown |
| E28 S1D11 | CHB-MIT | biot | linear | last_randinit - last | -5.90 | [-28.07, +16.27] | [-22.92, +11.12] | second term wins |
| E28 S1D11 | CHB-MIT | biot | linear | lp - lp_randinit | +3.16 | [-15.69, +22.00] | [-11.31, +17.63] | first term wins |
| E28 S1D11 | CHB-MIT | biot | linear | D17 | -0.08 | [-0.56, +0.39] | [-0.45, +0.28] | random features explain it |
| E28 S1D12 | CHB-MIT | biot | linear | last - lp | +2.65 | [-0.87, +6.18] | [-0.06, +5.36] | no difference shown |
| E28 S1D12 | CHB-MIT | biot | linear | last_randinit - last | -5.90 | [-28.07, +16.27] | [-22.92, +11.12] | second term wins |
| E28 S1D12 | CHB-MIT | biot | linear | lp - lp_randinit | +3.16 | [-15.69, +22.00] | [-11.31, +17.63] | first term wins |
| E28 S1D12 | CHB-MIT | biot | linear | D17 | -0.08 | [-0.56, +0.39] | [-0.45, +0.28] | random features explain it |
| E28 D24 | CHB-MIT | cbramod | linear | last - lp | -0.02 | [-0.43, +0.40] | [-0.34, +0.31] | no difference shown |
| E28 D24 | CHB-MIT | cbramod | linear | last_randinit - last | -4.42 | [-7.42, -1.43] | [-6.72, -2.13] | second term wins |
| E28 D24 | CHB-MIT | cbramod | linear | lp - lp_randinit | +5.47 | [+2.54, +8.40] | [+3.22, +7.72] | first term wins |
| E28 D24 | CHB-MIT | cbramod | linear | D17 | +1.03 | [-0.90, +2.97] | [-0.45, +2.52] | random features explain it |
| E28 4174 | CHB-MIT | cbramod | linear | last - lp | +0.05 | [-0.45, +0.55] | [-0.33, +0.44] | no difference shown |
| E28 4174 | CHB-MIT | cbramod | linear | last_randinit - last | -2.87 | [-4.88, -0.86] | [-4.41, -1.33] | no difference shown |
| E28 4174 | CHB-MIT | cbramod | linear | lp - lp_randinit | +4.55 | [+1.48, +7.63] | [+2.20, +6.91] | first term wins |
| E28 4174 | CHB-MIT | cbramod | linear | D17 | +1.74 | [-1.40, +4.87] | [-0.67, +4.14] | random features explain it |
| E28 S1D11 | CHB-MIT | cbramod | linear | last - lp | +0.05 | [-0.45, +0.55] | [-0.33, +0.44] | no difference shown |
| E28 S1D11 | CHB-MIT | cbramod | linear | last_randinit - last | -5.39 | [-9.40, -1.39] | [-8.47, -2.32] | second term wins |
| E28 S1D11 | CHB-MIT | cbramod | linear | lp - lp_randinit | +4.55 | [+1.48, +7.63] | [+2.20, +6.91] | first term wins |
| E28 S1D11 | CHB-MIT | cbramod | linear | D17 | -0.79 | [-2.29, +0.72] | [-1.94, +0.37] | random features explain it |
| E28 S1D12 | CHB-MIT | cbramod | linear | last - lp | +0.05 | [-0.44, +0.55] | [-0.33, +0.44] | no difference shown |
| E28 S1D12 | CHB-MIT | cbramod | linear | last_randinit - last | -2.86 | [-6.84, +1.12] | [-5.92, +0.19] | no difference shown |
| E28 S1D12 | CHB-MIT | cbramod | linear | lp - lp_randinit | +4.55 | [+1.48, +7.63] | [+2.20, +6.91] | first term wins |
| E28 S1D12 | CHB-MIT | cbramod | linear | D17 | +1.75 | [-1.67, +5.16] | [-0.88, +4.37] | random features explain it |
| E28 D24 | Siena | biot | linear | last - lp | +9.23 | [+2.28, +16.19] | [+3.89, +14.57] | first term wins |
| E28 D24 | Siena | biot | linear | last_randinit - last | +7.19 | [-11.53, +25.91] | [-7.18, +21.56] | no difference shown |
| E28 D24 | Siena | biot | linear | lp - lp_randinit | -16.08 | [-40.72, +8.55] | [-35.00, +2.83] | second term wins |
| E28 D24 | Siena | biot | linear | D17 | +0.34 | [-0.61, +1.29] | [-0.39, +1.07] | random features explain it |
| E28 4174 | Siena | biot | linear | last - lp | +6.85 | [-2.21, +15.92] | [-0.11, +13.81] | first term wins |
| E28 4174 | Siena | biot | linear | last_randinit - last | +9.95 | [-12.58, +32.49] | [-7.35, +27.26] | no difference shown |
| E28 4174 | Siena | biot | linear | lp - lp_randinit | -16.81 | [-42.80, +9.18] | [-36.77, +3.15] | second term wins |
| E28 4174 | Siena | biot | linear | D17 | -0.00 | [-1.31, +1.31] | [-1.01, +1.01] | random features explain it |
| E28 S3D11 | Siena | biot | linear | last - lp | +6.84 | [-2.19, +15.87] | [-0.09, +13.77] | first term wins |
| E28 S3D11 | Siena | biot | linear | last_randinit - last | +9.97 | [-12.57, +32.52] | [-7.34, +27.28] | no difference shown |
| E28 S3D11 | Siena | biot | linear | lp - lp_randinit | -16.81 | [-42.80, +9.18] | [-36.77, +3.15] | second term wins |
| E28 S3D11 | Siena | biot | linear | D17 | +0.00 | [-1.31, +1.32] | [-1.01, +1.01] | random features explain it |
| E28 S3D12 | Siena | biot | linear | last - lp | +6.84 | [-2.23, +15.92] | [-0.12, +13.81] | first term wins |
| E28 S3D12 | Siena | biot | linear | last_randinit - last | +9.97 | [-12.57, +32.50] | [-7.34, +27.27] | no difference shown |
| E28 S3D12 | Siena | biot | linear | lp - lp_randinit | -16.81 | [-42.80, +9.18] | [-36.77, +3.15] | second term wins |
| E28 S3D12 | Siena | biot | linear | D17 | +0.00 | [-1.32, +1.32] | [-1.01, +1.01] | random features explain it |
| E28 D24 | Siena | cbramod | linear | last - lp | +0.27 | [-0.41, +0.94] | [-0.25, +0.79] | no difference shown |
| E28 D24 | Siena | cbramod | linear | last_randinit - last | -7.63 | [-14.32, -0.94] | [-12.76, -2.50] | second term wins |
| E28 D24 | Siena | cbramod | linear | lp - lp_randinit | +6.99 | [-2.35, +16.33] | [-0.18, +14.16] | first term wins |
| E28 D24 | Siena | cbramod | linear | D17 | -0.37 | [-3.10, +2.35] | [-2.46, +1.72] | random features explain it |
| E28 4174 | Siena | cbramod | linear | last - lp | +0.64 | [-0.05, +1.33] | [+0.11, +1.17] | no difference shown |
| E28 4174 | Siena | cbramod | linear | last_randinit - last | -7.99 | [-19.29, +3.31] | [-16.67, +0.68] | second term wins |
| E28 4174 | Siena | cbramod | linear | lp - lp_randinit | +6.70 | [-5.59, +18.98] | [-2.74, +16.13] | first term wins |
| E28 4174 | Siena | cbramod | linear | D17 | -0.65 | [-1.83, +0.53] | [-1.56, +0.26] | random features explain it |
| E28 S3D11 | Siena | cbramod | linear | last - lp | +0.64 | [-0.05, +1.34] | [+0.11, +1.17] | no difference shown |
| E28 S3D11 | Siena | cbramod | linear | last_randinit - last | -8.29 | [-20.19, +3.62] | [-17.43, +0.85] | second term wins |
| E28 S3D11 | Siena | cbramod | linear | lp - lp_randinit | +6.70 | [-5.59, +18.98] | [-2.74, +16.13] | first term wins |
| E28 S3D11 | Siena | cbramod | linear | D17 | -0.95 | [-1.73, -0.16] | [-1.55, -0.34] | random features explain it |
| E28 S3D12 | Siena | cbramod | linear | last - lp | +0.64 | [-0.05, +1.33] | [+0.11, +1.17] | no difference shown |
| E28 S3D12 | Siena | cbramod | linear | last_randinit - last | -7.96 | [-19.31, +3.38] | [-16.67, +0.75] | second term wins |
| E28 S3D12 | Siena | cbramod | linear | lp - lp_randinit | +6.70 | [-5.59, +18.98] | [-2.74, +16.13] | first term wins |
| E28 S3D12 | Siena | cbramod | linear | D17 | -0.62 | [-1.73, +0.48] | [-1.47, +0.23] | random features explain it |
| E33a | CHB-MIT extended | biot | linear | last - lp | +1.59 | [-0.62, +3.81] | [-0.11, +3.29] | no difference shown |
| E33a | CHB-MIT extended | biot | linear | last_randinit - last | +1.38 | [-12.31, +15.07] | [-9.13, +11.89] | no difference shown |
| E33a | CHB-MIT extended | biot | linear | lp - lp_randinit | -2.93 | [-16.85, +10.99] | [-13.62, +7.76] | no difference shown |
| E33a | CHB-MIT extended | biot | linear | D17 | +0.04 | [-0.10, +0.19] | [-0.07, +0.15] | random features explain it |
| E33a | CHB-MIT extended | biot | linear | all - last | +6.73 | [+2.75, +10.72] | [+3.68, +9.79] | reference only |
| E33a | CHB-MIT extended | cbramod | linear | last - lp | -0.02 | [-0.21, +0.17] | [-0.16, +0.13] | no difference shown |
| E33a | CHB-MIT extended | cbramod | linear | last_randinit - last | -4.83 | [-7.36, -2.31] | [-6.77, -2.90] | second term wins |
| E33a | CHB-MIT extended | cbramod | linear | lp - lp_randinit | +3.93 | [+0.37, +7.49] | [+1.19, +6.66] | first term wins |
| E33a | CHB-MIT extended | cbramod | linear | D17 | -0.92 | [-2.76, +0.91] | [-2.33, +0.48] | random features explain it |
| E33a | CHB-MIT extended | cbramod | linear | all - last | +1.06 | [-2.29, +4.42] | [-1.51, +3.64] | reference only |
