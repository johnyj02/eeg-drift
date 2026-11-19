# E10: statistics on the D24 records (D25; post hoc and descriptive, D24 verdicts stay primary)

Script: scripts/analysis/stats_d25.py. ROC-AUC x100. Units: D24-A = the 5 rotation means of the paired per-seed differences (3 seeds each); D24-B (paper split, P1E) = the 5 seeds on one split, so its intervals cover seed noise only, not test-set sampling. n = 5, df = 4 everywhere.
Nadeau-Bengio: SE = SD * sqrt(1/5 + n_test/n_train), n_test/n_train = mean over rotations from the test-index sizes (grid windows; train = the 3 folds that are neither test nor val): CHB-MIT 0.338 (fold sizes [57761, 68822, 57354, 50141, 90950]); Siena 0.347 (fold sizes [7483, 15332, 5177, 18449, 4308]); Siena filtered 0.347 (fold sizes [7483, 15332, 5177, 18449, 4308]). Not defined for the paper split (one fixed split, no resampling of data): n/a.
Bootstrap (c) = pre-registered D24-D, under-covers at n=5; it reproduces artifacts/tables/d24-bootstrap.md exactly (checked). Coverage check, 95% percentile bootstrap of a mean of 5 iid normals: 0.850 (t-interval: 0.954; 4,000 sims x 2,000 resamples).

The audit's in-memory numbers, checked here: 't [-1.0, +4.8]' is the t-interval of CHB-MIT BIOT last - lp, [-1.0, +4.8] in this script; 'FPR 17%' names no contrast: the FPR at true effect 0 (normal errors) of the D24-A rule contrasts runs from 0.000 to 0.352, e.g. Siena BIOT last - lp (SD 5.6) 0.175.

## (a)-(c) 95% intervals

| setting | model | head | contrast | family | mean | per unit | t 95% | NB 95% | bootstrap 95% (D24-D, under-covers) | excludes 0 (t/NB/boot) | D24 verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| CHB-MIT | biot | linear | last - lp | C1 | +1.9 | +1.7, +3.1, +0.9, -1.1, +5.0 | [-1.0, +4.8] | [-2.8, +6.6] | [+0.1, +3.9] | n/n/y | no difference shown |
| CHB-MIT | biot | linear | last_randinit - last | Artifact 1 | +0.2 | -8.3, -4.7, -5.8, +24.4, -4.9 | [-16.8, +17.1] | [-27.6, +27.9] | [-8.9, +12.4] | n/n/n | no difference shown |
| CHB-MIT | biot | linear | lp - lp_randinit | features | -2.0 | +6.5, +1.8, +4.9, -23.1, +0.2 | [-17.0, +13.1] | [-26.6, +22.7] | [-12.9, +6.1] | n/n/n | no difference shown |
| CHB-MIT | biot | linear | last_randinit - lp_randinit | D17 | +0.1 | -0.2, +0.2, +0.1, +0.1, +0.4 | [-0.1, +0.3] | [-0.3, +0.5] | [-0.1, +0.4] | n/n/n | random features explain it |
| CHB-MIT | biot | linear | all - last | reference | +9.8 | +2.7, +14.6, +3.9, +16.8, +10.9 | [+2.0, +17.6] | [-3.0, +22.6] | [+4.6, +14.8] | y/n/y | reference, no rule |
| CHB-MIT | cbramod | linear | last - lp | C1 | -0.0 | -0.4, +0.5, +0.0, -0.1, -0.1 | [-0.4, +0.4] | [-0.7, +0.7] | [-0.3, +0.3] | n/n/n | no difference shown |
| CHB-MIT | cbramod | linear | last_randinit - last | Artifact 1 | -4.4 | -3.2, -7.9, -3.7, -1.7, -5.6 | [-7.4, -1.4] | [-9.3, +0.5] | [-6.9, -2.2] | y/n/y | second term wins |
| CHB-MIT | cbramod | linear | lp - lp_randinit | features | +5.5 | +5.9, +9.3, +3.1, +4.1, +4.9 | [+2.5, +8.4] | [+0.7, +10.3] | [+3.5, +7.7] | y/y/y | first term wins |
| CHB-MIT | cbramod | linear | last_randinit - lp_randinit | D17 | +1.0 | +2.3, +1.8, -0.5, +2.3, -0.8 | [-0.9, +3.0] | [-2.1, +4.2] | [-0.5, +2.6] | n/n/n | random features explain it |
| CHB-MIT | cbramod | linear | all - last | reference | +1.6 | +4.3, +1.3, +0.5, +0.5, +1.6 | [-0.3, +3.6] | [-1.6, +4.9] | [+0.6, +3.0] | n/n/y | reference, no rule |
| Siena | biot | linear | last - lp | C1 | +9.2 | +7.5, +18.3, +3.4, +10.0, +7.0 | [+2.3, +16.2] | [-2.3, +20.7] | [+4.6, +15.7] | y/n/y | first term wins |
| Siena | biot | linear | last_randinit - last | Artifact 1 | +7.2 | -7.7, +28.1, +6.4, +15.5, -6.3 | [-11.5, +25.9] | [-23.8, +38.2] | [-4.4, +19.6] | n/n/n | no difference shown |
| Siena | biot | linear | lp - lp_randinit | features | -16.1 | +1.1, -45.7, -9.1, -26.5, -0.3 | [-40.7, +8.6] | [-56.8, +24.7] | [-33.2, -1.7] | n/n/y | second term wins |
| Siena | biot | linear | last_randinit - lp_randinit | D17 | +0.3 | +0.9, +0.7, +0.7, -1.0, +0.4 | [-0.6, +1.3] | [-1.2, +1.9] | [-0.4, +1.0] | n/n/n | random features explain it |
| Siena | biot | linear | all - last | reference | +10.6 | -0.7, +11.0, +5.5, +22.0, +15.1 | [-0.2, +21.4] | [-7.3, +28.5] | [+3.1, +17.7] | n/n/y | reference, no rule |
| Siena | cbramod | linear | last - lp | C1 | +0.3 | -0.5, +0.3, +0.5, +1.0, +0.0 | [-0.4, +0.9] | [-0.8, +1.4] | [-0.6, +0.8] | n/n/n | no difference shown |
| Siena | cbramod | linear | last_randinit - last | Artifact 1 | -7.6 | -6.6, -2.9, -13.4, -2.2, -13.0 | [-14.3, -0.9] | [-18.7, +3.4] | [-12.8, -3.0] | y/n/y | second term wins |
| Siena | cbramod | linear | lp - lp_randinit | features | +7.0 | +4.8, +0.3, +14.7, -0.0, +15.2 | [-2.4, +16.3] | [-8.5, +22.4] | [+0.9, +13.7] | n/n/y | first term wins |
| Siena | cbramod | linear | last_randinit - lp_randinit | D17 | -0.4 | -2.2, -2.3, +1.8, -1.3, +2.2 | [-3.1, +2.3] | [-4.9, +4.1] | [-2.3, +1.7] | n/n/n | random features explain it |
| Siena | cbramod | linear | all - last | reference | +2.0 | +5.9, +5.3, -6.1, +7.1, -2.2 | [-5.2, +9.2] | [-9.9, +13.9] | [-2.9, +6.3] | n/n/n | reference, no rule |
| Siena filtered | biot | linear | last - lp | C1 | +4.1 | +1.3, +8.9, +0.9, +5.0, +4.4 | [+0.1, +8.2] | [-2.6, +10.8] | [+1.4, +6.9] | y/n/y | first term wins |
| Siena filtered | biot | linear | last_randinit - last | Artifact 1 | -4.7 | -24.3, +37.1, -9.3, -13.8, -13.2 | [-34.5, +25.1] | [-54.0, +44.6] | [-19.2, +17.0] | n/n/n | second term wins |
| Siena filtered | biot | linear | lp - lp_randinit | features | +1.0 | +23.3, -46.2, +9.2, +8.9, +9.6 | [-32.6, +34.6] | [-54.6, +56.5] | [-23.8, +17.4] | n/n/n | no difference shown |
| Siena filtered | biot | linear | last_randinit - lp_randinit | D17 | +0.4 | +0.3, -0.1, +0.8, +0.1, +0.9 | [-0.1, +0.9] | [-0.5, +1.3] | [-0.1, +0.9] | n/n/n | random features explain it |
| Siena filtered | biot | linear | all - last | reference | +0.4 | -15.7, +18.7, -6.4, +3.4, +2.2 | [-15.4, +16.3] | [-25.8, +26.7] | [-9.4, +10.8] | n/n/n | reference, no rule |
| Siena filtered | cbramod | linear | last - lp | C1 | +0.1 | +0.3, -0.1, +0.2, +0.2, +0.1 | [-0.0, +0.3] | [-0.2, +0.5] | [+0.0, +0.3] | n/n/y | no difference shown |
| Siena filtered | cbramod | linear | last_randinit - last | Artifact 1 | -10.7 | -15.3, -7.7, -8.3, -5.2, -16.9 | [-17.0, -4.4] | [-21.1, -0.2] | [-15.7, -6.2] | y/y/y | second term wins |
| Siena filtered | cbramod | linear | lp - lp_randinit | features | +9.4 | +16.2, +6.7, +7.3, +4.8, +12.3 | [+3.6, +15.3] | [-0.2, +19.1] | [+5.4, +13.7] | y/n/y | first term wins |
| Siena filtered | cbramod | linear | last_randinit - lp_randinit | D17 | -1.1 | +1.3, -1.2, -0.9, -0.3, -4.5 | [-3.7, +1.5] | [-5.5, +3.2] | [-3.9, +0.7] | n/n/n | random features explain it |
| Siena filtered | cbramod | linear | all - last | reference | -0.8 | -1.1, +0.2, -3.4, +1.8, -1.4 | [-3.2, +1.6] | [-4.7, +3.2] | [-2.3, +0.7] | n/n/n | reference, no rule |
| paper split | biot | linear | last - lp | C1 | -0.6 | -2.0, +1.8, -4.3, -0.1, +1.6 | [-3.8, +2.6] | n/a | [-2.6, +1.4] | n/-/n | no difference shown |
| paper split | biot | linear | last_randinit - last | Artifact 1 | +35.8 | +36.7, +33.0, +38.8, +35.9, +34.5 | [+33.0, +38.5] | n/a | [+34.0, +37.5] | y/-/y | descriptive (no rule on the paper split) |
| paper split | biot | linear | lp - lp_randinit | features | -35.1 | -34.7, -34.7, -34.6, -35.7, -35.9 | [-35.9, -34.3] | n/a | [-35.6, -34.6] | y/-/y | descriptive (no rule on the paper split) |
| paper split | biot | linear | last_randinit - lp_randinit | D17 | +0.0 | -0.0, +0.0, -0.1, +0.1, +0.2 | [-0.1, +0.1] | n/a | [-0.0, +0.1] | n/-/n | descriptive (no rule on the paper split) |
| paper split | biot | mlp_fullft | last - lp | C1 | -1.2 | -3.2, -0.4, -4.7, -0.0, +2.3 | [-4.6, +2.2] | n/a | [-3.4, +0.8] | n/-/n | no difference shown |
| paper split | biot | mlp_fullft | last_randinit - last | Artifact 1 | +33.6 | +35.4, +33.1, +36.7, +33.1, +29.7 | [+30.3, +36.9] | n/a | [+31.5, +35.7] | y/-/y | descriptive (no rule on the paper split) |
| paper split | biot | mlp_fullft | lp - lp_randinit | features | -32.4 | -32.4, -32.6, -31.6, -33.1, -32.3 | [-33.1, -31.7] | n/a | [-32.8, -32.0] | y/-/y | descriptive (no rule on the paper split) |
| paper split | biot | mlp_fullft | last_randinit - lp_randinit | D17 | -0.0 | -0.1, +0.1, +0.3, -0.0, -0.3 | [-0.3, +0.3] | n/a | [-0.2, +0.2] | n/-/n | descriptive (no rule on the paper split) |
| paper split | cbramod | linear | last - lp | C1 | +0.0 | -0.0, +0.0, +0.0, +0.0, +0.0 | [-0.0, +0.0] | n/a | [-0.0, +0.0] | n/-/n | no difference shown |
| paper split | cbramod | linear | last_randinit - last | Artifact 1 | -8.5 | -8.8, -9.4, -7.9, -8.7, -7.7 | [-9.4, -7.6] | n/a | [-9.0, -8.0] | y/-/y | descriptive (no rule on the paper split) |
| paper split | cbramod | linear | lp - lp_randinit | features | +6.4 | +4.2, +8.8, +6.0, +6.3, +6.8 | [+4.4, +8.5] | n/a | [+5.2, +7.8] | y/-/y | descriptive (no rule on the paper split) |
| paper split | cbramod | linear | last_randinit - lp_randinit | D17 | -2.1 | -4.6, -0.6, -1.8, -2.4, -0.8 | [-4.1, -0.1] | n/a | [-3.4, -0.9] | y/-/y | descriptive (no rule on the paper split) |
| paper split | cbramod | mlp_fullft | last - lp | C1 | +0.0 | +0.1, -0.5, +0.2, +0.3, +0.1 | [-0.4, +0.4] | n/a | [-0.3, +0.2] | n/-/n | no difference shown |
| paper split | cbramod | mlp_fullft | last_randinit - last | Artifact 1 | -2.0 | -0.5, -3.9, -1.6, +0.6, -4.6 | [-4.7, +0.8] | n/a | [-3.7, -0.2] | n/-/y | descriptive (no rule on the paper split) |
| paper split | cbramod | mlp_fullft | lp - lp_randinit | features | +2.2 | +1.0, +3.2, +2.5, +0.7, +3.4 | [+0.6, +3.7] | n/a | [+1.2, +3.1] | y/-/y | descriptive (no rule on the paper split) |
| paper split | cbramod | mlp_fullft | last_randinit - lp_randinit | D17 | +0.2 | +0.6, -1.2, +1.1, +1.6, -1.1 | [-1.4, +1.8] | n/a | [-0.8, +1.2] | n/-/n | descriptive (no rule on the paper split) |

## (d) One-sided bounds, equivalence (TOST) and the paper's gains

One-sided 95% bounds = the 90% two-sided interval. TOST p at margin d: max of the two one-sided t tests; 'equivalent' at alpha 0.05 iff p < 0.05 (90% interval inside (-d, +d)). Paper gain test (C1 rows only): H0 effect >= paper gain (BIOT +36.2, CBraMod +29.5), one-sided t.

| setting | model | head | contrast | 90% t | 90% NB | TOST p d=1/2/3 (t) | TOST p d=1/2/3 (NB) | p(effect >= paper gain) t / NB |
|---|---|---|---|---|---|---|---|---|
| CHB-MIT | biot | linear | last - lp | [-0.3, +4.1] | [-1.7, +5.5] | 0.785/0.467/0.175 | 0.690/0.480/0.277 | 2.5e-06 / 1.8e-05 |
| CHB-MIT | biot | linear | last_randinit - last | [-12.8, +13.1] | [-21.1, +21.4] | 0.448/0.388/0.332 | 0.468/0.431/0.395 | - |
| CHB-MIT | biot | linear | lp - lp_randinit | [-13.5, +9.6] | [-20.9, +17.0] | 0.565/0.497/0.428 | 0.540/0.498/0.456 | - |
| CHB-MIT | biot | linear | last_randinit - lp_randinit | [-0.1, +0.3] | [-0.2, +0.4] | 0.000/0.000/0.000 | 0.002/0.000/0.000 | - |
| CHB-MIT | biot | linear | all - last | [+3.8, +15.8] | [-0.1, +19.6] | 0.982/0.975/0.963 | 0.935/0.916/0.892 | - |
| CHB-MIT | cbramod | linear | last - lp | [-0.3, +0.3] | [-0.5, +0.5] | 0.001/0.000/0.000 | 0.008/0.001/0.000 | 2e-09 / 1.5e-08 |
| CHB-MIT | cbramod | linear | last_randinit - last | [-6.7, -2.1] | [-8.2, -0.7] | 0.983/0.956/0.871 | 0.938/0.879/0.767 | - |
| CHB-MIT | cbramod | linear | lp - lp_randinit | [+3.2, +7.7] | [+1.8, +9.2] | 0.993/0.985/0.961 | 0.970/0.942/0.887 | - |
| CHB-MIT | cbramod | linear | last_randinit - lp_randinit | [-0.5, +2.5] | [-1.4, +3.5] | 0.518/0.119/0.024 | 0.511/0.223/0.080 | - |
| CHB-MIT | cbramod | linear | all - last | [+0.1, +3.1] | [-0.8, +4.1] | 0.787/0.314/0.062 | 0.691/0.382/0.151 | - |
| Siena | biot | linear | last - lp | [+3.9, +14.6] | [+0.4, +18.1] | 0.985/0.978/0.966 | 0.941/0.922/0.896 | 0.00021 / 0.0014 |
| Siena | biot | linear | last_randinit - last | [-7.2, +21.6] | [-16.6, +31.0] | 0.795/0.758/0.716 | 0.696/0.667/0.637 | - |
| Siena | biot | linear | lp - lp_randinit | [-35.0, +2.8] | [-47.4, +15.2] | 0.918/0.906/0.893 | 0.819/0.804/0.788 | - |
| Siena | biot | linear | last_randinit - lp_randinit | [-0.4, +1.1] | [-0.9, +1.5] | 0.063/0.004/0.001 | 0.154/0.021/0.005 | - |
| Siena | biot | linear | all - last | [+2.3, +18.9] | [-3.2, +24.3] | 0.965/0.954/0.938 | 0.894/0.873/0.848 | - |
| Siena | cbramod | linear | last - lp | [-0.3, +0.8] | [-0.6, +1.1] | 0.020/0.001/0.000 | 0.071/0.006/0.001 | 1.4e-08 / 1.1e-07 |
| Siena | cbramod | linear | last_randinit - last | [-12.8, -2.5] | [-16.1, +0.9] | 0.974/0.960/0.937 | 0.914/0.885/0.845 | - |
| Siena | cbramod | linear | lp - lp_randinit | [-0.2, +14.2] | [-4.9, +18.9] | 0.925/0.894/0.849 | 0.829/0.790/0.743 | - |
| Siena | cbramod | linear | last_randinit - lp_randinit | [-2.5, +1.7] | [-3.8, +3.1] | 0.279/0.086/0.028 | 0.360/0.186/0.090 | - |
| Siena | cbramod | linear | all - last | [-3.5, +7.5] | [-7.2, +11.2] | 0.640/0.500/0.360 | 0.586/0.500/0.414 | - |
| Siena filtered | biot | linear | last - lp | [+1.0, +7.2] | [-1.0, +9.2] | 0.950/0.889/0.755 | 0.867/0.784/0.665 | 1.3e-05 / 9.2e-05 |
| Siena filtered | biot | linear | last_randinit - last | [-27.6, +18.2] | [-42.6, +33.2] | 0.626/0.593/0.559 | 0.577/0.556/0.536 | - |
| Siena filtered | biot | linear | lp - lp_randinit | [-24.8, +26.8] | [-41.7, +43.6] | 0.499/0.468/0.438 | 0.500/0.481/0.462 | - |
| Siena filtered | biot | linear | last_randinit - lp_randinit | [-0.0, +0.8] | [-0.3, +1.1] | 0.016/0.001/0.000 | 0.063/0.003/0.001 | - |
| Siena filtered | biot | linear | all - last | [-11.8, +12.6] | [-19.7, +20.6] | 0.464/0.400/0.339 | 0.478/0.439/0.400 | - |
| Siena filtered | cbramod | linear | last - lp | [-0.0, +0.3] | [-0.1, +0.4] | 0.000/0.000/0.000 | 0.001/0.000/0.000 | 8.6e-11 / 6.4e-10 |
| Siena filtered | cbramod | linear | last_randinit - last | [-15.5, -5.8] | [-18.7, -2.7] | 0.993/0.991/0.986 | 0.969/0.959/0.945 | - |
| Siena filtered | cbramod | linear | lp - lp_randinit | [+5.0, +13.9] | [+2.0, +16.9] | 0.992/0.988/0.981 | 0.964/0.950/0.931 | - |
| Siena filtered | cbramod | linear | last_randinit - lp_randinit | [-3.1, +0.9] | [-4.4, +2.2] | 0.542/0.200/0.058 | 0.526/0.300/0.147 | - |
| Siena filtered | cbramod | linear | all - last | [-2.6, +1.0] | [-3.8, +2.2] | 0.408/0.116/0.031 | 0.444/0.221/0.097 | - |
| paper split | biot | linear | last - lp | [-3.1, +1.9] | n/a | 0.374/0.146/0.053 | n/a | 2.9e-06 / n/a |
| paper split | biot | linear | last_randinit - last | [+33.7, +37.9] | n/a | 1.000/1.000/1.000 | n/a | - |
| paper split | biot | linear | lp - lp_randinit | [-35.7, -34.5] | n/a | 1.000/1.000/1.000 | n/a | - |
| paper split | biot | linear | last_randinit - lp_randinit | [-0.1, +0.1] | n/a | 0.000/0.000/0.000 | n/a | - |
| paper split | biot | mlp_fullft | last - lp | [-3.8, +1.4] | n/a | 0.559/0.273/0.107 | n/a | 3.4e-06 / n/a |
| paper split | biot | mlp_fullft | last_randinit - last | [+31.1, +36.1] | n/a | 1.000/1.000/1.000 | n/a | - |
| paper split | biot | mlp_fullft | lp - lp_randinit | [-32.9, -31.9] | n/a | 1.000/1.000/1.000 | n/a | - |
| paper split | biot | mlp_fullft | last_randinit - lp_randinit | [-0.2, +0.2] | n/a | 0.000/0.000/0.000 | n/a | - |
| paper split | cbramod | linear | last - lp | [-0.0, +0.0] | n/a | 0.000/0.000/0.000 | n/a | 8e-14 / n/a |
| paper split | cbramod | linear | last_randinit - last | [-9.2, -7.8] | n/a | 1.000/1.000/1.000 | n/a | - |
| paper split | cbramod | linear | lp - lp_randinit | [+4.9, +8.0] | n/a | 0.999/0.998/0.995 | n/a | - |
| paper split | cbramod | linear | last_randinit - lp_randinit | [-3.6, -0.5] | n/a | 0.893/0.530/0.130 | n/a | - |
| paper split | cbramod | mlp_fullft | last - lp | [-0.3, +0.3] | n/a | 0.001/0.000/0.000 | n/a | 1.7e-09 / n/a |
| paper split | cbramod | mlp_fullft | last_randinit - last | [-4.1, +0.1] | n/a | 0.809/0.491/0.181 | n/a | - |
| paper split | cbramod | mlp_fullft | lp - lp_randinit | [+1.0, +3.3] | n/a | 0.946/0.603/0.102 | n/a | - |
| paper split | cbramod | mlp_fullft | last_randinit - lp_randinit | [-1.0, +1.4] | n/a | 0.122/0.018/0.004 | n/a | - |

## (e) Threshold x k sweep, flip points, leave-one-out

Each string has one symbol per threshold 0, 0.5, ..., 10 (21 symbols): '+' first term wins, '-' second term wins, '.' no difference shown; D17 rows: 'E' = |mean| <= threshold (random features explain it). Flip points: a win holds for threshold < |mean| and k <= the same-sign count. Leave-one-out (rotation or seed) uses the rule with k = n - 1 = 3 of 4, as read_step1.paired does; one symbol per left-out unit (rot0..rot4 or seeds in order).

| setting | model | head | contrast | D18 verdict (3, 4/5) | abs(mean) | same-sign count | k=3 | k=4 | k=5 | leave-one-out | LOO stable |
|---|---|---|---|---|---|---|---|---|---|---|---|
| CHB-MIT | biot | linear | last - lp | . | 1.9 | 4/5 | `++++.................` | `++++.................` | `.....................` | `.....` | yes |
| CHB-MIT | biot | linear | last_randinit - last | . | 0.2 | 1/5 | `.....................` | `.....................` | `.....................` | `...-.` | NO |
| CHB-MIT | biot | linear | lp - lp_randinit | . | 2.0 | 1/5 | `.....................` | `.....................` | `.....................` | `...+.` | NO |
| CHB-MIT | biot | linear | last_randinit - lp_randinit | E | 0.1 | 4/5 | `+EEEEEEEEEEEEEEEEEEEE` | `+EEEEEEEEEEEEEEEEEEEE` | `.EEEEEEEEEEEEEEEEEEEE` | `EEEEE` | yes |
| CHB-MIT | biot | linear | all - last | + | 9.8 | 5/5 | `++++++++++++++++++++.` | `++++++++++++++++++++.` | `++++++++++++++++++++.` | `+++++` | yes |
| CHB-MIT | cbramod | linear | last - lp | . | 0.0 | 3/5 | `-....................` | `.....................` | `.....................` | `.....` | yes |
| CHB-MIT | cbramod | linear | last_randinit - last | - | 4.4 | 5/5 | `---------............` | `---------............` | `---------............` | `-----` | yes |
| CHB-MIT | cbramod | linear | lp - lp_randinit | + | 5.5 | 5/5 | `+++++++++++..........` | `+++++++++++..........` | `+++++++++++..........` | `+++++` | yes |
| CHB-MIT | cbramod | linear | last_randinit - lp_randinit | E | 1.0 | 3/5 | `+++EEEEEEEEEEEEEEEEEE` | `...EEEEEEEEEEEEEEEEEE` | `...EEEEEEEEEEEEEEEEEE` | `EEEEE` | yes |
| CHB-MIT | cbramod | linear | all - last | . | 1.6 | 5/5 | `++++.................` | `++++.................` | `++++.................` | `.....` | yes |
| Siena | biot | linear | last - lp | + | 9.2 | 5/5 | `+++++++++++++++++++..` | `+++++++++++++++++++..` | `+++++++++++++++++++..` | `+++++` | yes |
| Siena | biot | linear | last_randinit - last | . | 7.2 | 3/5 | `+++++++++++++++......` | `.....................` | `.....................` | `+...+` | NO |
| Siena | biot | linear | lp - lp_randinit | - | 16.1 | 4/5 | `---------------------` | `---------------------` | `.....................` | `-----` | yes |
| Siena | biot | linear | last_randinit - lp_randinit | E | 0.3 | 4/5 | `+EEEEEEEEEEEEEEEEEEEE` | `+EEEEEEEEEEEEEEEEEEEE` | `.EEEEEEEEEEEEEEEEEEEE` | `EEEEE` | yes |
| Siena | biot | linear | all - last | + | 10.6 | 4/5 | `+++++++++++++++++++++` | `+++++++++++++++++++++` | `.....................` | `+++++` | yes |
| Siena | cbramod | linear | last - lp | . | 0.3 | 4/5 | `+....................` | `+....................` | `.....................` | `.....` | yes |
| Siena | cbramod | linear | last_randinit - last | - | 7.6 | 5/5 | `----------------.....` | `----------------.....` | `----------------.....` | `-----` | yes |
| Siena | cbramod | linear | lp - lp_randinit | + | 7.0 | 4/5 | `++++++++++++++.......` | `++++++++++++++.......` | `.....................` | `+++++` | yes |
| Siena | cbramod | linear | last_randinit - lp_randinit | E | 0.4 | 3/5 | `-EEEEEEEEEEEEEEEEEEEE` | `.EEEEEEEEEEEEEEEEEEEE` | `.EEEEEEEEEEEEEEEEEEEE` | `EEEEE` | yes |
| Siena | cbramod | linear | all - last | . | 2.0 | 3/5 | `+++++................` | `.....................` | `.....................` | `..+.+` | NO |
| Siena filtered | biot | linear | last - lp | + | 4.1 | 5/5 | `+++++++++............` | `+++++++++............` | `+++++++++............` | `+.+++` | NO |
| Siena filtered | biot | linear | last_randinit - last | - | 4.7 | 4/5 | `----------...........` | `----------...........` | `.....................` | `.--..` | NO |
| Siena filtered | biot | linear | lp - lp_randinit | . | 1.0 | 4/5 | `++...................` | `++...................` | `.....................` | `.+...` | NO |
| Siena filtered | biot | linear | last_randinit - lp_randinit | E | 0.4 | 4/5 | `+EEEEEEEEEEEEEEEEEEEE` | `+EEEEEEEEEEEEEEEEEEEE` | `.EEEEEEEEEEEEEEEEEEEE` | `EEEEE` | yes |
| Siena filtered | biot | linear | all - last | . | 0.4 | 3/5 | `+....................` | `.....................` | `.....................` | `+....` | NO |
| Siena filtered | cbramod | linear | last - lp | . | 0.1 | 4/5 | `+....................` | `+....................` | `.....................` | `.....` | yes |
| Siena filtered | cbramod | linear | last_randinit - last | - | 10.7 | 5/5 | `---------------------` | `---------------------` | `---------------------` | `-----` | yes |
| Siena filtered | cbramod | linear | lp - lp_randinit | + | 9.4 | 5/5 | `+++++++++++++++++++..` | `+++++++++++++++++++..` | `+++++++++++++++++++..` | `+++++` | yes |
| Siena filtered | cbramod | linear | last_randinit - lp_randinit | E | 1.1 | 4/5 | `---EEEEEEEEEEEEEEEEEE` | `---EEEEEEEEEEEEEEEEEE` | `...EEEEEEEEEEEEEEEEEE` | `EEEEE` | yes |
| Siena filtered | cbramod | linear | all - last | . | 0.8 | 3/5 | `--...................` | `.....................` | `.....................` | `.....` | yes |
| paper split | biot | linear | last - lp | . | 0.6 | 3/5 | `--...................` | `.....................` | `.....................` | `.....` | yes |
| paper split | biot | linear | last_randinit - last | + | 35.8 | 5/5 | `+++++++++++++++++++++` | `+++++++++++++++++++++` | `+++++++++++++++++++++` | `+++++` | yes |
| paper split | biot | linear | lp - lp_randinit | - | 35.1 | 5/5 | `---------------------` | `---------------------` | `---------------------` | `-----` | yes |
| paper split | biot | linear | last_randinit - lp_randinit | E | 0.0 | 3/5 | `+EEEEEEEEEEEEEEEEEEEE` | `.EEEEEEEEEEEEEEEEEEEE` | `.EEEEEEEEEEEEEEEEEEEE` | `EEEEE` | yes |
| paper split | biot | mlp_fullft | last - lp | . | 1.2 | 4/5 | `---..................` | `---..................` | `.....................` | `.....` | yes |
| paper split | biot | mlp_fullft | last_randinit - last | + | 33.6 | 5/5 | `+++++++++++++++++++++` | `+++++++++++++++++++++` | `+++++++++++++++++++++` | `+++++` | yes |
| paper split | biot | mlp_fullft | lp - lp_randinit | - | 32.4 | 5/5 | `---------------------` | `---------------------` | `---------------------` | `-----` | yes |
| paper split | biot | mlp_fullft | last_randinit - lp_randinit | E | 0.0 | 3/5 | `-EEEEEEEEEEEEEEEEEEEE` | `.EEEEEEEEEEEEEEEEEEEE` | `.EEEEEEEEEEEEEEEEEEEE` | `EEEEE` | yes |
| paper split | cbramod | linear | last - lp | . | 0.0 | 4/5 | `+....................` | `+....................` | `.....................` | `.....` | yes |
| paper split | cbramod | linear | last_randinit - last | - | 8.5 | 5/5 | `------------------...` | `------------------...` | `------------------...` | `-----` | yes |
| paper split | cbramod | linear | lp - lp_randinit | + | 6.4 | 5/5 | `+++++++++++++........` | `+++++++++++++........` | `+++++++++++++........` | `+++++` | yes |
| paper split | cbramod | linear | last_randinit - lp_randinit | E | 2.1 | 5/5 | `-----EEEEEEEEEEEEEEEE` | `-----EEEEEEEEEEEEEEEE` | `-----EEEEEEEEEEEEEEEE` | `EEEEE` | yes |
| paper split | cbramod | mlp_fullft | last - lp | . | 0.0 | 4/5 | `+....................` | `+....................` | `.....................` | `.....` | yes |
| paper split | cbramod | mlp_fullft | last_randinit - last | . | 2.0 | 4/5 | `----.................` | `----.................` | `.....................` | `.....` | yes |
| paper split | cbramod | mlp_fullft | lp - lp_randinit | . | 2.2 | 5/5 | `+++++................` | `+++++................` | `+++++................` | `.....` | yes |
| paper split | cbramod | mlp_fullft | last_randinit - lp_randinit | E | 0.2 | 3/5 | `+EEEEEEEEEEEEEEEEEEEE` | `.EEEEEEEEEEEEEEEEEEEE` | `.EEEEEEEEEEEEEEEEEEEE` | `EEEEE` | yes |

## (f) Power and false positives of the 3-point, 4/5 rule

Simulation: 5 units = true effect + errors with each contrast's SD (over its 5 units), 200,000 replicates per error model (normal; t3 scaled to the SD; centred resample of the contrast's own 5 values, rescaled to the SD). Computed exactly per replicate: the rule says 'first term wins' iff the true effect exceeds max(3 - mean(e), -e_(2)). Cells: normal / t3 / resample. FPR = P(any win) at true effect 0. Power = P(first term wins) at true effect 3, 5, 10, 36. Effect80 = smallest true effect with 80% power. D17 rows add P(|mean| <= 3) at true effect 0 / 3 / 5.

| setting | model | head | contrast | SD | FPR at 0 | power at 3 | at 5 | at 10 | at 36 | effect80 | D17 P(explain) at 0/3/5 (normal) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| CHB-MIT | biot | linear | last - lp | 2.3 | 0.004 / 0.007 / 0.002 | 0.50 / 0.50 / 0.45 | 0.97 / 0.98 / 0.98 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 3.9 / 3.7 / 3.9 | - |
| CHB-MIT | biot | linear | last_randinit - last | 13.6 | 0.322 / 0.281 / 0.335 | 0.29 / 0.34 / 0.01 | 0.39 / 0.50 / 0.01 | 0.66 / 0.82 / 0.88 | 1.00 / 1.00 / 1.00 | 13.2 / 9.6 / 9.5 | - |
| CHB-MIT | biot | linear | lp - lp_randinit | 12.1 | 0.313 / 0.266 / 0.334 | 0.30 / 0.36 / 0.51 | 0.42 / 0.54 / 0.72 | 0.72 / 0.86 / 0.74 | 1.00 / 1.00 / 1.00 | 11.8 / 8.7 / 23.7 | - |
| CHB-MIT | biot | linear | last_randinit - lp_randinit | 0.2 | 0.000 / 0.000 / 0.000 | 0.50 / 0.50 / 0.49 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 3.1 / 3.1 / 3.1 | 1.00/0.50/0.00 |
| CHB-MIT | biot | linear | all - last | 6.3 | 0.207 / 0.135 / 0.237 | 0.40 / 0.45 / 0.33 | 0.65 / 0.77 / 0.34 | 0.97 / 0.98 / 0.99 | 1.00 / 1.00 / 1.00 | 6.5 / 5.3 / 7.9 | - |
| CHB-MIT | cbramod | linear | last - lp | 0.3 | 0.000 / 0.000 / 0.000 | 0.50 / 0.50 / 0.47 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 3.1 / 3.1 / 3.1 | - |
| CHB-MIT | cbramod | linear | last_randinit - last | 2.4 | 0.005 / 0.008 / 0.002 | 0.50 / 0.50 / 0.50 | 0.97 / 0.97 / 0.97 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 3.9 / 3.8 / 3.9 | - |
| CHB-MIT | cbramod | linear | lp - lp_randinit | 2.4 | 0.005 / 0.008 / 0.005 | 0.50 / 0.50 / 0.46 | 0.97 / 0.97 / 0.99 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 3.9 / 3.7 / 4.0 | - |
| CHB-MIT | cbramod | linear | last_randinit - lp_randinit | 1.6 | 0.000 / 0.001 / 0.000 | 0.50 / 0.50 / 0.50 | 1.00 / 0.99 / 1.00 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 3.6 / 3.5 / 3.6 | 1.00/0.50/0.00 |
| CHB-MIT | cbramod | linear | all - last | 1.6 | 0.000 / 0.002 / 0.000 | 0.50 / 0.50 / 0.45 | 1.00 / 0.99 / 1.00 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 3.6 / 3.5 / 3.7 | - |
| Siena | biot | linear | last - lp | 5.6 | 0.175 / 0.110 / 0.175 | 0.42 / 0.46 / 0.46 | 0.70 / 0.81 / 0.65 | 0.99 / 0.99 / 1.00 | 1.00 / 1.00 / 1.00 | 5.9 / 5.0 / 6.6 | - |
| Siena | biot | linear | last_randinit - last | 15.1 | 0.329 / 0.293 / 0.354 | 0.28 / 0.32 / 0.32 | 0.37 / 0.47 / 0.33 | 0.61 / 0.78 / 0.34 | 1.00 / 1.00 / 1.00 | 14.6 / 10.6 / 16.6 | - |
| Siena | biot | linear | lp - lp_randinit | 19.8 | 0.342 / 0.315 / 0.411 | 0.25 / 0.29 / 0.34 | 0.32 / 0.40 / 0.34 | 0.50 / 0.66 / 0.34 | 0.99 / 0.99 / 1.00 | 19.1 / 13.7 / 33.1 | - |
| Siena | biot | linear | last_randinit - lp_randinit | 0.8 | 0.000 / 0.000 / 0.000 | 0.50 / 0.50 / 0.52 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 3.3 / 3.2 / 3.3 | 1.00/0.50/0.00 |
| Siena | biot | linear | all - last | 8.7 | 0.273 / 0.206 / 0.286 | 0.35 / 0.41 / 0.32 | 0.52 / 0.65 / 0.34 | 0.87 / 0.94 / 0.74 | 1.00 / 1.00 / 1.00 | 8.6 / 6.6 / 12.6 | - |
| Siena | cbramod | linear | last - lp | 0.5 | 0.000 / 0.000 / 0.000 | 0.50 / 0.50 / 0.49 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 3.2 / 3.2 / 3.2 | - |
| Siena | cbramod | linear | last_randinit - last | 5.4 | 0.167 / 0.101 / 0.202 | 0.42 / 0.47 / 0.34 | 0.72 / 0.82 / 0.34 | 0.99 / 0.99 / 1.00 | 1.00 / 1.00 / 1.00 | 5.7 / 4.8 / 6.5 | - |
| Siena | cbramod | linear | lp - lp_randinit | 7.5 | 0.246 / 0.175 / 0.318 | 0.37 / 0.43 / 0.31 | 0.58 / 0.71 / 0.34 | 0.93 / 0.97 / 0.99 | 1.00 / 1.00 / 1.00 | 7.5 / 5.9 / 7.9 | - |
| Siena | cbramod | linear | last_randinit - lp_randinit | 2.2 | 0.002 / 0.005 / 0.000 | 0.50 / 0.50 / 0.46 | 0.98 / 0.98 / 0.99 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 3.8 / 3.7 / 3.9 | 1.00/0.50/0.02 |
| Siena | cbramod | linear | all - last | 5.8 | 0.186 / 0.117 / 0.185 | 0.41 / 0.46 / 0.34 | 0.68 / 0.79 / 0.68 | 0.98 / 0.99 / 0.99 | 1.00 / 1.00 / 1.00 | 6.1 / 5.1 / 9.1 | - |
| Siena filtered | biot | linear | last - lp | 3.3 | 0.038 / 0.025 / 0.030 | 0.48 / 0.49 / 0.30 | 0.90 / 0.94 / 0.94 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 4.3 / 4.0 / 4.1 | - |
| Siena filtered | biot | linear | last_randinit - last | 24.0 | 0.348 / 0.325 / 0.391 | 0.24 / 0.27 / 0.01 | 0.30 / 0.35 / 0.01 | 0.44 / 0.58 / 0.29 | 0.96 / 0.98 / 1.00 | 23.1 / 16.6 / 21.9 | - |
| Siena filtered | biot | linear | lp - lp_randinit | 27.1 | 0.352 / 0.331 / 0.440 | 0.24 / 0.26 / 0.54 | 0.28 / 0.34 / 0.61 | 0.41 / 0.54 / 0.74 | 0.93 / 0.97 / 0.74 | 26.2 / 18.5 / 52.7 | - |
| Siena filtered | biot | linear | last_randinit - lp_randinit | 0.4 | 0.000 / 0.000 / 0.000 | 0.50 / 0.50 / 0.48 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 3.2 / 3.1 / 3.2 | 1.00/0.50/0.00 |
| Siena filtered | biot | linear | all - last | 12.8 | 0.318 / 0.272 / 0.313 | 0.30 / 0.35 / 0.31 | 0.41 / 0.52 / 0.34 | 0.69 / 0.84 / 0.72 | 1.00 / 1.00 / 1.00 | 12.4 / 9.1 / 18.1 | - |
| Siena filtered | cbramod | linear | last - lp | 0.2 | 0.000 / 0.000 / 0.000 | 0.50 / 0.50 / 0.49 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 3.1 / 3.0 / 3.1 | - |
| Siena filtered | cbramod | linear | last_randinit - last | 5.1 | 0.149 / 0.089 / 0.174 | 0.43 / 0.47 / 0.34 | 0.74 / 0.83 / 0.34 | 0.99 / 0.99 / 1.00 | 1.00 / 1.00 / 1.00 | 5.5 / 4.7 / 7.0 | - |
| Siena filtered | cbramod | linear | lp - lp_randinit | 4.7 | 0.127 / 0.074 / 0.137 | 0.44 / 0.48 / 0.28 | 0.77 / 0.85 / 0.66 | 1.00 / 0.99 / 1.00 | 1.00 / 1.00 / 1.00 | 5.2 / 4.6 / 5.2 | - |
| Siena filtered | cbramod | linear | last_randinit - lp_randinit | 2.1 | 0.002 / 0.005 / 0.002 | 0.50 / 0.50 / 0.50 | 0.98 / 0.98 / 0.97 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 3.8 / 3.7 / 3.8 | 1.00/0.50/0.02 |
| Siena filtered | cbramod | linear | all - last | 1.9 | 0.000 / 0.003 / 0.000 | 0.50 / 0.50 / 0.48 | 0.99 / 0.99 / 0.99 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 3.7 / 3.6 / 3.7 | - |
| paper split | biot | linear | last - lp | 2.6 | 0.009 / 0.011 / 0.007 | 0.49 / 0.50 / 0.50 | 0.96 / 0.97 / 0.95 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 4.0 / 3.8 / 4.1 | - |
| paper split | biot | linear | last_randinit - last | 2.2 | 0.002 / 0.005 / 0.001 | 0.50 / 0.50 / 0.46 | 0.98 / 0.98 / 0.98 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 3.8 / 3.7 / 3.8 | - |
| paper split | biot | linear | lp - lp_randinit | 0.6 | 0.000 / 0.000 / 0.000 | 0.50 / 0.50 / 0.49 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 3.2 / 3.2 / 3.3 | - |
| paper split | biot | linear | last_randinit - lp_randinit | 0.1 | 0.000 / 0.000 / 0.000 | 0.50 / 0.50 / 0.47 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 3.0 / 3.0 / 3.0 | 1.00/0.50/0.00 |
| paper split | biot | mlp_fullft | last - lp | 2.7 | 0.014 / 0.013 / 0.009 | 0.49 / 0.50 / 0.46 | 0.94 / 0.96 / 0.95 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 4.1 / 3.9 / 4.0 | - |
| paper split | biot | mlp_fullft | last_randinit - last | 2.6 | 0.011 / 0.012 / 0.007 | 0.49 / 0.50 / 0.48 | 0.95 / 0.96 / 0.93 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 4.0 / 3.8 / 4.3 | - |
| paper split | biot | mlp_fullft | lp - lp_randinit | 0.5 | 0.000 / 0.000 / 0.000 | 0.50 / 0.50 / 0.49 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 3.2 / 3.2 / 3.2 | - |
| paper split | biot | mlp_fullft | last_randinit - lp_randinit | 0.2 | 0.000 / 0.000 / 0.000 | 0.50 / 0.50 / 0.47 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 3.1 / 3.1 / 3.1 | 1.00/0.50/0.00 |
| paper split | cbramod | linear | last - lp | 0.0 | 0.000 / 0.000 / 0.000 | 0.50 / 0.50 / 0.51 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 3.0 / 3.0 / 3.0 | - |
| paper split | cbramod | linear | last_randinit - last | 0.7 | 0.000 / 0.000 / 0.000 | 0.50 / 0.50 / 0.48 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 3.3 / 3.2 / 3.3 | - |
| paper split | cbramod | linear | lp - lp_randinit | 1.6 | 0.000 / 0.002 / 0.000 | 0.50 / 0.50 / 0.51 | 1.00 / 0.99 / 1.00 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 3.6 / 3.5 / 3.6 | - |
| paper split | cbramod | linear | last_randinit - lp_randinit | 1.6 | 0.000 / 0.002 / 0.000 | 0.50 / 0.50 / 0.51 | 1.00 / 0.99 / 0.99 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 3.6 / 3.5 / 3.6 | 1.00/0.50/0.00 |
| paper split | cbramod | mlp_fullft | last - lp | 0.3 | 0.000 / 0.000 / 0.000 | 0.50 / 0.50 / 0.51 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 3.1 / 3.1 / 3.1 | - |
| paper split | cbramod | mlp_fullft | last_randinit - last | 2.2 | 0.003 / 0.006 / 0.000 | 0.50 / 0.50 / 0.49 | 0.98 / 0.98 / 0.98 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 3.8 / 3.7 / 3.9 | - |
| paper split | cbramod | mlp_fullft | lp - lp_randinit | 1.2 | 0.000 / 0.001 / 0.000 | 0.50 / 0.50 / 0.50 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 3.5 / 3.4 / 3.5 | - |
| paper split | cbramod | mlp_fullft | last_randinit - lp_randinit | 1.3 | 0.000 / 0.001 / 0.000 | 0.50 / 0.50 / 0.49 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 3.5 / 3.4 / 3.5 | 1.00/0.50/0.00 |

Generic power curves (normal and t3 errors, SD 0.5, 2, 5, 10, 15, 25): power-rule.png. Observed contrast SDs: D24-A 0.2 to 27.1; paper split 0.03 to 2.7.

## (g) Multiplicity: exact sign-flip p and Holm within families

Exact two-sided sign-flip p over the 32 sign patterns of the 5 units (statistic |mean|); the smallest possible p is 2/32 = 0.0625, so no contrast can reach 0.05 with 5 units, before or after Holm. Families: C1 = last - lp, Artifact 1 = last_randinit - last, features = lp - lp_randinit, D17 = last_randinit - lp_randinit; each family = its 6 D24-A rows + its 4 paper-split rows (10 tests). The t-test p (df 4) and its Holm adjustment are shown for comparison.

| family | setting | model | head | contrast | sign-flip p | Holm | t p | Holm (t) |
|---|---|---|---|---|---|---|---|---|
| C1 | CHB-MIT | biot | linear | last - lp | 0.1875 | 1.0000 | 0.14 | 0.97 |
| C1 | CHB-MIT | cbramod | linear | last - lp | 0.8750 | 1.0000 | 0.92 | 1 |
| C1 | Siena | biot | linear | last - lp | 0.0625 | 0.6250 | 0.021 | 0.21 |
| C1 | Siena | cbramod | linear | last - lp | 0.3125 | 1.0000 | 0.33 | 1 |
| C1 | Siena filtered | biot | linear | last - lp | 0.0625 | 0.6250 | 0.048 | 0.43 |
| C1 | Siena filtered | cbramod | linear | last - lp | 0.1250 | 1.0000 | 0.11 | 0.85 |
| C1 | paper split | biot | linear | last - lp | 0.5625 | 1.0000 | 0.63 | 1 |
| C1 | paper split | biot | mlp_fullft | last - lp | 0.3125 | 1.0000 | 0.38 | 1 |
| C1 | paper split | cbramod | linear | last - lp | 0.3750 | 1.0000 | 0.37 | 1 |
| C1 | paper split | cbramod | mlp_fullft | last - lp | 0.8125 | 1.0000 | 0.83 | 1 |
| Artifact 1 | CHB-MIT | biot | linear | last_randinit - last | 1.0000 | 1.0000 | 0.98 | 1 |
| Artifact 1 | CHB-MIT | cbramod | linear | last_randinit - last | 0.0625 | 0.6250 | 0.015 | 0.089 |
| Artifact 1 | Siena | biot | linear | last_randinit - last | 0.3750 | 1.0000 | 0.35 | 1 |
| Artifact 1 | Siena | cbramod | linear | last_randinit - last | 0.0625 | 0.6250 | 0.034 | 0.17 |
| Artifact 1 | Siena filtered | biot | linear | last_randinit - last | 0.6875 | 1.0000 | 0.68 | 1 |
| Artifact 1 | Siena filtered | cbramod | linear | last_randinit - last | 0.0625 | 0.6250 | 0.0093 | 0.065 |
| Artifact 1 | paper split | biot | linear | last_randinit - last | 0.0625 | 0.6250 | 3.5e-06 | 3.5e-05 |
| Artifact 1 | paper split | biot | mlp_fullft | last_randinit - last | 0.0625 | 0.6250 | 9.1e-06 | 8.2e-05 |
| Artifact 1 | paper split | cbramod | linear | last_randinit - last | 0.0625 | 0.6250 | 1.1e-05 | 9.2e-05 |
| Artifact 1 | paper split | cbramod | mlp_fullft | last_randinit - last | 0.1875 | 0.7500 | 0.12 | 0.47 |
| features | CHB-MIT | biot | linear | lp - lp_randinit | 1.0000 | 1.0000 | 0.74 | 1 |
| features | CHB-MIT | cbramod | linear | lp - lp_randinit | 0.0625 | 0.6250 | 0.0066 | 0.046 |
| features | Siena | biot | linear | lp - lp_randinit | 0.1875 | 0.6250 | 0.14 | 0.43 |
| features | Siena | cbramod | linear | lp - lp_randinit | 0.1250 | 0.6250 | 0.11 | 0.43 |
| features | Siena filtered | biot | linear | lp - lp_randinit | 1.0000 | 1.0000 | 0.94 | 1 |
| features | Siena filtered | cbramod | linear | lp - lp_randinit | 0.0625 | 0.6250 | 0.011 | 0.066 |
| features | paper split | biot | linear | lp - lp_randinit | 0.0625 | 0.6250 | 2.6e-08 | 2.3e-07 |
| features | paper split | biot | mlp_fullft | lp - lp_randinit | 0.0625 | 0.6250 | 1.8e-08 | 1.8e-07 |
| features | paper split | cbramod | linear | lp - lp_randinit | 0.0625 | 0.6250 | 0.00094 | 0.0075 |
| features | paper split | cbramod | mlp_fullft | lp - lp_randinit | 0.0625 | 0.6250 | 0.018 | 0.091 |
| D17 | CHB-MIT | biot | linear | last_randinit - lp_randinit | 0.3125 | 1.0000 | 0.27 | 1 |
| D17 | CHB-MIT | cbramod | linear | last_randinit - lp_randinit | 0.2500 | 1.0000 | 0.21 | 1 |
| D17 | Siena | biot | linear | last_randinit - lp_randinit | 0.3750 | 1.0000 | 0.37 | 1 |
| D17 | Siena | cbramod | linear | last_randinit - lp_randinit | 0.6875 | 1.0000 | 0.72 | 1 |
| D17 | Siena filtered | biot | linear | last_randinit - lp_randinit | 0.1875 | 1.0000 | 0.11 | 0.99 |
| D17 | Siena filtered | cbramod | linear | last_randinit - lp_randinit | 0.3750 | 1.0000 | 0.31 | 1 |
| D17 | paper split | biot | linear | last_randinit - lp_randinit | 0.5000 | 1.0000 | 0.47 | 1 |
| D17 | paper split | biot | mlp_fullft | last_randinit - lp_randinit | 1.0000 | 1.0000 | 0.98 | 1 |
| D17 | paper split | cbramod | linear | last_randinit - lp_randinit | 0.0625 | 0.6250 | 0.046 | 0.46 |
| D17 | paper split | cbramod | mlp_fullft | last_randinit - lp_randinit | 0.7500 | 1.0000 | 0.73 | 1 |

## (h) Variance components

(h1) Rotation vs seed, from the run-level ROC (arms) or the paired per-seed differences (contrasts): one-way random effects, balanced (5 rotations x 3 seeds), method of moments. Paper split: seed SD only (one split).

| setting | model | quantity | SD rotation | SD seed | rotation share of variance |
|---|---|---|---|---|---|
| CHB-MIT | biot | lp | 17.66 | 0.86 | 1.00 |
| CHB-MIT | biot | lp_randinit | 10.31 | 8.71 | 0.58 |
| CHB-MIT | biot | last | 18.64 | 1.04 | 1.00 |
| CHB-MIT | biot | last_randinit | 10.29 | 9.04 | 0.56 |
| CHB-MIT | biot | all | 15.40 | 3.22 | 0.96 |
| CHB-MIT | biot | last - lp | 2.16 | 1.41 | 0.70 |
| CHB-MIT | biot | last_randinit - last | 12.52 | 9.28 | 0.65 |
| CHB-MIT | biot | lp - lp_randinit | 11.06 | 8.51 | 0.63 |
| CHB-MIT | biot | last_randinit - lp_randinit | 0.00 | 0.50 | 0.00 |
| CHB-MIT | biot | all - last | 5.89 | 3.80 | 0.71 |
| CHB-MIT | cbramod | lp | 7.39 | 0.34 | 1.00 |
| CHB-MIT | cbramod | lp_randinit | 7.89 | 2.65 | 0.90 |
| CHB-MIT | cbramod | last | 7.58 | 0.36 | 1.00 |
| CHB-MIT | cbramod | last_randinit | 6.31 | 3.40 | 0.78 |
| CHB-MIT | cbramod | all | 6.71 | 0.48 | 0.99 |
| CHB-MIT | cbramod | last - lp | 0.32 | 0.16 | 0.80 |
| CHB-MIT | cbramod | last_randinit - last | 1.58 | 3.16 | 0.20 |
| CHB-MIT | cbramod | lp - lp_randinit | 1.87 | 2.48 | 0.36 |
| CHB-MIT | cbramod | last_randinit - lp_randinit | 0.73 | 2.39 | 0.09 |
| CHB-MIT | cbramod | all - last | 1.57 | 0.36 | 0.95 |
| Siena | biot | lp | 14.16 | 4.54 | 0.91 |
| Siena | biot | lp_randinit | 8.29 | 4.52 | 0.77 |
| Siena | biot | last | 10.46 | 4.54 | 0.84 |
| Siena | biot | last_randinit | 8.72 | 4.19 | 0.81 |
| Siena | biot | all | 5.03 | 8.77 | 0.25 |
| Siena | biot | last - lp | 3.41 | 7.70 | 0.16 |
| Siena | biot | last_randinit - last | 14.63 | 6.30 | 0.84 |
| Siena | biot | lp - lp_randinit | 19.49 | 6.44 | 0.90 |
| Siena | biot | last_randinit - lp_randinit | 0.52 | 0.97 | 0.22 |
| Siena | biot | all - last | 7.65 | 7.22 | 0.53 |
| Siena | cbramod | lp | 5.21 | 1.40 | 0.93 |
| Siena | cbramod | lp_randinit | 7.49 | 5.99 | 0.61 |
| Siena | cbramod | last | 5.08 | 0.60 | 0.99 |
| Siena | cbramod | last_randinit | 5.66 | 6.77 | 0.41 |
| Siena | cbramod | all | 8.02 | 0.89 | 0.99 |
| Siena | cbramod | last - lp | 0.00 | 1.43 | 0.00 |
| Siena | cbramod | last_randinit - last | 3.85 | 6.52 | 0.26 |
| Siena | cbramod | lp - lp_randinit | 6.59 | 6.29 | 0.52 |
| Siena | cbramod | last_randinit - lp_randinit | 1.52 | 2.73 | 0.24 |
| Siena | cbramod | all - last | 5.79 | 0.90 | 0.98 |
| Siena filtered | biot | lp | 15.13 | 0.96 | 1.00 |
| Siena filtered | biot | lp_randinit | 11.94 | 3.99 | 0.90 |
| Siena filtered | biot | last | 12.33 | 2.08 | 0.97 |
| Siena filtered | biot | last_randinit | 11.62 | 4.20 | 0.88 |
| Siena filtered | biot | all | 5.15 | 5.34 | 0.48 |
| Siena filtered | biot | last - lp | 2.98 | 2.29 | 0.63 |
| Siena filtered | biot | last_randinit - last | 23.88 | 4.46 | 0.97 |
| Siena filtered | biot | lp - lp_randinit | 26.94 | 4.39 | 0.97 |
| Siena filtered | biot | last_randinit - lp_randinit | 0.00 | 0.86 | 0.00 |
| Siena filtered | biot | all - last | 12.61 | 3.81 | 0.92 |
| Siena filtered | cbramod | lp | 5.06 | 0.16 | 1.00 |
| Siena filtered | cbramod | lp_randinit | 4.27 | 4.66 | 0.46 |
| Siena filtered | cbramod | last | 5.08 | 0.14 | 1.00 |
| Siena filtered | cbramod | last_randinit | 3.17 | 6.19 | 0.21 |
| Siena filtered | cbramod | all | 6.28 | 0.10 | 1.00 |
| Siena filtered | cbramod | last - lp | 0.15 | 0.03 | 0.96 |
| Siena filtered | cbramod | last_randinit - last | 3.63 | 6.17 | 0.26 |
| Siena filtered | cbramod | lp - lp_randinit | 3.87 | 4.66 | 0.41 |
| Siena filtered | cbramod | last_randinit - lp_randinit | 0.00 | 3.85 | 0.00 |
| Siena filtered | cbramod | all - last | 1.92 | 0.23 | 0.99 |
| paper split | biot | lp (linear) | n/a | 0.86 | n/a |
| paper split | biot | lp (mlp_fullft) | n/a | 0.29 | n/a |
| paper split | biot | lp_randinit (linear) | n/a | 0.36 | n/a |
| paper split | biot | lp_randinit (mlp_fullft) | n/a | 0.40 | n/a |
| paper split | biot | last (linear) | n/a | 2.37 | n/a |
| paper split | biot | last (mlp_fullft) | n/a | 2.71 | n/a |
| paper split | biot | last_randinit (linear) | n/a | 0.36 | n/a |
| paper split | biot | last_randinit (mlp_fullft) | n/a | 0.42 | n/a |
| paper split | biot | last - lp (linear) | n/a | 2.58 | n/a |
| paper split | biot | last_randinit - last (linear) | n/a | 2.21 | n/a |
| paper split | biot | lp - lp_randinit (linear) | n/a | 0.64 | n/a |
| paper split | biot | last_randinit - lp_randinit (linear) | n/a | 0.09 | n/a |
| paper split | biot | last - lp (mlp_fullft) | n/a | 2.74 | n/a |
| paper split | biot | last_randinit - last (mlp_fullft) | n/a | 2.64 | n/a |
| paper split | biot | lp - lp_randinit (mlp_fullft) | n/a | 0.54 | n/a |
| paper split | biot | last_randinit - lp_randinit (mlp_fullft) | n/a | 0.25 | n/a |
| paper split | cbramod | lp (linear) | n/a | 0.10 | n/a |
| paper split | cbramod | lp (mlp_fullft) | n/a | 0.61 | n/a |
| paper split | cbramod | lp_randinit (linear) | n/a | 1.61 | n/a |
| paper split | cbramod | lp_randinit (mlp_fullft) | n/a | 0.87 | n/a |
| paper split | cbramod | last (linear) | n/a | 0.11 | n/a |
| paper split | cbramod | last (mlp_fullft) | n/a | 0.43 | n/a |
| paper split | cbramod | last_randinit (linear) | n/a | 0.75 | n/a |
| paper split | cbramod | last_randinit (mlp_fullft) | n/a | 1.91 | n/a |
| paper split | cbramod | last - lp (linear) | n/a | 0.03 | n/a |
| paper split | cbramod | last_randinit - last (linear) | n/a | 0.71 | n/a |
| paper split | cbramod | lp - lp_randinit (linear) | n/a | 1.65 | n/a |
| paper split | cbramod | last_randinit - lp_randinit (linear) | n/a | 1.61 | n/a |
| paper split | cbramod | last - lp (mlp_fullft) | n/a | 0.32 | n/a |
| paper split | cbramod | last_randinit - last (mlp_fullft) | n/a | 2.23 | n/a |
| paper split | cbramod | lp - lp_randinit (mlp_fullft) | n/a | 1.25 | n/a |
| paper split | cbramod | last_randinit - lp_randinit (mlp_fullft) | n/a | 1.29 | n/a |

(h2) Rotation / subject / seed, from per-subject ROC-AUC (npz scores, subjects with both classes in test), subjects nested in rotations, ANOVA-type moments with the harmonic mean subject count. The rules use the pooled-fold ROC, not per-subject ROC, so these SDs describe heterogeneity, not the rule's units. Every npz was checked: labels recomputed from the window keys equal y_test, and the pooled ROC equals the record.

| setting | model | quantity | SD rotation (beyond its subjects) | SD subject | SD seed | subjects |
|---|---|---|---|---|---|---|
| CHB-MIT | biot | lp | 14.42 | 19.35 | 1.02 | 20 |
| CHB-MIT | biot | lp_randinit | 0.00 | 23.66 | 11.26 | 20 |
| CHB-MIT | biot | last | 15.82 | 19.25 | 2.12 | 20 |
| CHB-MIT | biot | last_randinit | 0.00 | 23.34 | 11.46 | 20 |
| CHB-MIT | biot | all | 6.55 | 17.95 | 5.85 | 20 |
| CHB-MIT | biot | last - lp | 1.49 | 2.63 | 2.05 | 20 |
| CHB-MIT | biot | last_randinit - last | 11.58 | 20.60 | 11.88 | 20 |
| CHB-MIT | biot | lp - lp_randinit | 10.22 | 20.50 | 11.18 | 20 |
| CHB-MIT | biot | last_randinit - lp_randinit | 0.00 | 0.00 | 1.27 | 20 |
| CHB-MIT | biot | all - last | 0.00 | 18.21 | 6.50 | 20 |
| CHB-MIT | cbramod | lp | 0.00 | 12.75 | 0.42 | 20 |
| CHB-MIT | cbramod | lp_randinit | 0.00 | 14.58 | 4.58 | 20 |
| CHB-MIT | cbramod | last | 0.00 | 13.06 | 0.29 | 20 |
| CHB-MIT | cbramod | last_randinit | 0.00 | 13.33 | 4.18 | 20 |
| CHB-MIT | cbramod | all | 4.11 | 12.23 | 0.32 | 20 |
| CHB-MIT | cbramod | last - lp | 0.00 | 0.82 | 0.33 | 20 |
| CHB-MIT | cbramod | last_randinit - last | 0.00 | 5.14 | 4.21 | 20 |
| CHB-MIT | cbramod | lp - lp_randinit | 0.00 | 5.41 | 4.42 | 20 |
| CHB-MIT | cbramod | last_randinit - lp_randinit | 0.66 | 1.02 | 3.72 | 20 |
| CHB-MIT | cbramod | all - last | 1.11 | 4.61 | 0.40 | 20 |
| Siena | biot | lp | 0.00 | 21.35 | 6.02 | 14 |
| Siena | biot | lp_randinit | 12.32 | 18.13 | 8.42 | 14 |
| Siena | biot | last | 0.00 | 21.37 | 6.26 | 14 |
| Siena | biot | last_randinit | 11.55 | 19.20 | 8.13 | 14 |
| Siena | biot | all | 4.44 | 15.24 | 13.49 | 14 |
| Siena | biot | last - lp | 0.00 | 4.89 | 8.55 | 14 |
| Siena | biot | last_randinit - last | 8.79 | 20.73 | 10.79 | 14 |
| Siena | biot | lp - lp_randinit | 14.31 | 20.73 | 11.13 | 14 |
| Siena | biot | last_randinit - lp_randinit | 0.00 | 0.40 | 2.56 | 14 |
| Siena | biot | all - last | 5.53 | 6.32 | 12.57 | 14 |
| Siena | cbramod | lp | 0.00 | 23.29 | 1.26 | 14 |
| Siena | cbramod | lp_randinit | 0.00 | 4.61 | 7.73 | 14 |
| Siena | cbramod | last | 0.00 | 23.32 | 0.70 | 14 |
| Siena | cbramod | last_randinit | 0.00 | 7.46 | 8.59 | 14 |
| Siena | cbramod | all | 0.00 | 17.02 | 1.01 | 14 |
| Siena | cbramod | last - lp | 0.00 | 0.53 | 1.27 | 14 |
| Siena | cbramod | last_randinit - last | 5.91 | 17.22 | 8.44 | 14 |
| Siena | cbramod | lp - lp_randinit | 6.92 | 18.86 | 7.88 | 14 |
| Siena | cbramod | last_randinit - lp_randinit | 0.46 | 0.00 | 5.36 | 14 |
| Siena | cbramod | all - last | 0.00 | 7.04 | 1.12 | 14 |
| Siena filtered | biot | lp | 0.00 | 25.43 | 1.83 | 14 |
| Siena filtered | biot | lp_randinit | 9.64 | 19.84 | 6.63 | 14 |
| Siena filtered | biot | last | 0.00 | 20.34 | 5.31 | 14 |
| Siena filtered | biot | last_randinit | 8.87 | 20.07 | 6.37 | 14 |
| Siena filtered | biot | all | 0.00 | 14.30 | 10.06 | 14 |
| Siena filtered | biot | last - lp | 0.00 | 5.26 | 5.83 | 14 |
| Siena filtered | biot | last_randinit - last | 20.35 | 20.37 | 8.83 | 14 |
| Siena filtered | biot | lp - lp_randinit | 20.80 | 23.08 | 6.97 | 14 |
| Siena filtered | biot | last_randinit - lp_randinit | 0.00 | 0.00 | 1.59 | 14 |
| Siena filtered | biot | all - last | 9.50 | 12.31 | 6.43 | 14 |
| Siena filtered | cbramod | lp | 0.00 | 24.65 | 0.33 | 14 |
| Siena filtered | cbramod | lp_randinit | 0.00 | 6.52 | 9.72 | 14 |
| Siena filtered | cbramod | last | 0.00 | 24.59 | 0.32 | 14 |
| Siena filtered | cbramod | last_randinit | 0.00 | 6.13 | 9.87 | 14 |
| Siena filtered | cbramod | all | 0.00 | 20.74 | 0.32 | 14 |
| Siena filtered | cbramod | last - lp | 0.15 | 0.23 | 0.04 | 14 |
| Siena filtered | cbramod | last_randinit - last | 6.71 | 18.84 | 9.79 | 14 |
| Siena filtered | cbramod | lp - lp_randinit | 4.75 | 19.39 | 9.65 | 14 |
| Siena filtered | cbramod | last_randinit - lp_randinit | 1.77 | 0.00 | 4.25 | 14 |
| Siena filtered | cbramod | all - last | 0.00 | 4.03 | 0.44 | 14 |

## Bounds for the abstract (input to E34)

- CHB-MIT | biot | linear | last - lp: +1.9, t 95% [-1.0, +4.8], NB 95% [-2.8, +6.6], bootstrap [+0.1, +3.9]; TOST +-3 p (t) 0.175; verdict: no difference shown
- CHB-MIT | biot | linear | last_randinit - lp_randinit: +0.1, t 95% [-0.1, +0.3], NB 95% [-0.3, +0.5], bootstrap [-0.1, +0.4]; TOST +-3 p (t) 0.000; verdict: random features explain it
- CHB-MIT | cbramod | linear | last - lp: -0.0, t 95% [-0.4, +0.4], NB 95% [-0.7, +0.7], bootstrap [-0.3, +0.3]; TOST +-3 p (t) 0.000; verdict: no difference shown
- CHB-MIT | cbramod | linear | last_randinit - lp_randinit: +1.0, t 95% [-0.9, +3.0], NB 95% [-2.1, +4.2], bootstrap [-0.5, +2.6]; TOST +-3 p (t) 0.024; verdict: random features explain it
- Siena | biot | linear | last - lp: +9.2, t 95% [+2.3, +16.2], NB 95% [-2.3, +20.7], bootstrap [+4.6, +15.7]; TOST +-3 p (t) 0.966; verdict: first term wins
- Siena | biot | linear | last_randinit - lp_randinit: +0.3, t 95% [-0.6, +1.3], NB 95% [-1.2, +1.9], bootstrap [-0.4, +1.0]; TOST +-3 p (t) 0.001; verdict: random features explain it
- Siena | cbramod | linear | last - lp: +0.3, t 95% [-0.4, +0.9], NB 95% [-0.8, +1.4], bootstrap [-0.6, +0.8]; TOST +-3 p (t) 0.000; verdict: no difference shown
- Siena | cbramod | linear | last_randinit - lp_randinit: -0.4, t 95% [-3.1, +2.3], NB 95% [-4.9, +4.1], bootstrap [-2.3, +1.7]; TOST +-3 p (t) 0.028; verdict: random features explain it
- Siena filtered | biot | linear | last - lp: +4.1, t 95% [+0.1, +8.2], NB 95% [-2.6, +10.8], bootstrap [+1.4, +6.9]; TOST +-3 p (t) 0.755; verdict: first term wins
- Siena filtered | biot | linear | last_randinit - lp_randinit: +0.4, t 95% [-0.1, +0.9], NB 95% [-0.5, +1.3], bootstrap [-0.1, +0.9]; TOST +-3 p (t) 0.000; verdict: random features explain it
- Siena filtered | cbramod | linear | last - lp: +0.1, t 95% [-0.0, +0.3], NB 95% [-0.2, +0.5], bootstrap [+0.0, +0.3]; TOST +-3 p (t) 0.000; verdict: no difference shown
- Siena filtered | cbramod | linear | last_randinit - lp_randinit: -1.1, t 95% [-3.7, +1.5], NB 95% [-5.5, +3.2], bootstrap [-3.9, +0.7]; TOST +-3 p (t) 0.058; verdict: random features explain it
- paper split | biot | linear | last - lp: -0.6, t 95% [-3.8, +2.6], NB 95% n/a, bootstrap [-2.6, +1.4]; TOST +-3 p (t) 0.053; verdict: no difference shown
- paper split | biot | linear | last_randinit - lp_randinit: +0.0, t 95% [-0.1, +0.1], NB 95% n/a, bootstrap [-0.0, +0.1]; TOST +-3 p (t) 0.000; verdict: descriptive (no rule on the paper split)
- paper split | cbramod | linear | last - lp: +0.0, t 95% [-0.0, +0.0], NB 95% n/a, bootstrap [-0.0, +0.0]; TOST +-3 p (t) 0.000; verdict: no difference shown
- paper split | cbramod | linear | last_randinit - lp_randinit: -2.1, t 95% [-4.1, -0.1], NB 95% n/a, bootstrap [-3.4, -0.9]; TOST +-3 p (t) 0.130; verdict: descriptive (no rule on the paper split)
