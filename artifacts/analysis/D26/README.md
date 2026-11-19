# D26: standardized head (`linear_z`) on the second partition (fold_seed 20261101)

Rule (notes/decisions.md "## D26", written before the runs, post hoc to E32): D24 rules (3-seed means per rotation, D18 paired rule |mean| > 3 and same sign in >= 4/5 rotations, D17) on last - lp, last_randinit - last, lp - lp_randinit. For each of the 3 E32 BIOT CHB-MIT non-replications: **raw-head effect** if the linear_z verdict is "no difference shown"; **partition effect** if it equals the E32 raw-head verdict; anything else is reported as it is. Other cells are descriptive (compared with E32, raw head, and with E26 = linear_z at seed S_r on the original partition).
ROC-AUC x100 at the val-selected epoch, eval-mode probe, encoder tap, overlap labels. CIs: cluster bootstrap (rotations, then seeds; 10,000 resamples; rng 20261101), descriptive. Run tags S1RZ / S3RZ; raw-head pairs S1R / S3R (E32).

Command: `.venv/bin/python scripts/analysis/d26_d27b.py` (reader outputs: `scripts/read_d24.py --tags S1RZ|S3RZ --out artifacts/analysis/D26/<tag>.md`)

## Checks

- S1RZ: 120 records = 2 models x 4 arms x 5 rotations x 3 seeds [S_r, 1000+r, 2000+r]; exactly 1 per cell, 0 missing, 0 duplicates, 0 smoke (records per seed: 42: 8, 123: 8, 1000: 8, 1001: 8, 1002: 8, 1003: 8, 1004: 8, 2000: 8, 2001: 8, 2002: 8, 2003: 8, 2004: 8, 2021: 8, 3407: 8, 8888: 8)
  probe `linear_z` only, versions adapt 3 / probe 4, backbone eval, tap encoder, input_norm "", labels overlap, fold_seed override 20261101
  every record pairs with the S1R raw-head record of the same (model, arm, split, seed): same eval_hash, test index, test n and prevalence, adapt_spec and arm_spec, val index (0 raw records predate the val_index field); probe spec differs only in `variant` (fields the raw records predate: tap = encoder, input_norm = ""); SSL losses identical in 60 of 60 adapted runs (60 per step, 0 per epoch: older raw records log epoch losses only)
  eval sets per split (both models): rot0 1, rot1 1, rot2 1, rot3 1, rot4 1
  verdict lines equal the scripts/read_d24.py output artifacts/analysis/D26/S1RZ.md
- S3RZ: 120 records = 2 models x 4 arms x 5 rotations x 3 seeds [S_r, 1000+r, 2000+r]; exactly 1 per cell, 0 missing, 0 duplicates, 0 smoke (records per seed: 42: 8, 123: 8, 1000: 8, 1001: 8, 1002: 8, 1003: 8, 1004: 8, 2000: 8, 2001: 8, 2002: 8, 2003: 8, 2004: 8, 2021: 8, 3407: 8, 8888: 8)
  probe `linear_z` only, versions adapt 3 / probe 4, backbone eval, tap encoder, input_norm "", labels overlap, fold_seed override 20261101
  every record pairs with the S3R raw-head record of the same (model, arm, split, seed): same eval_hash, test index, test n and prevalence, adapt_spec and arm_spec, val index (0 raw records predate the val_index field); probe spec differs only in `variant` (fields the raw records predate: tap = encoder, input_norm = ""); SSL losses identical in 60 of 60 adapted runs (60 per step, 0 per epoch: older raw records log epoch losses only)
  eval sets per split (both models): rot0 1, rot1 1, rot2 1, rot3 1, rot4 1
  verdict lines equal the scripts/read_d24.py output artifacts/analysis/D26/S3RZ.md
- Raw-head verdicts re-derived from S1R / S3R equal the published E32 strings (16 of 16); E26 at S_r re-derived from S1Z / S3Z equals the published E26 strings.

## D26 rule outputs (the 3 E32 BIOT CHB-MIT non-replications)

| contrast | linear_z mean [95% CI] | linear_z per rotation | linear_z verdict | E32 raw mean [CI] | E32 raw verdict | **D26 outcome** |
|---|---|---|---|---|---|---|
| last - lp | +0.7 [-0.6, +1.6] | +0.7, +1.3, -1.6, +1.7, +1.5 | no difference shown | +3.6 [+0.8, +8.1] | first term wins | **raw-head effect** |
| last_randinit - last | +2.6 [-2.0, +7.2] | -5.3, +1.3, +0.6, +7.7, +8.8 | no difference shown | +7.8 [+2.7, +13.8] | first term wins | **raw-head effect** |
| lp - lp_randinit | -3.4 [-8.6, +1.8] | +4.5, -2.6, +1.0, -9.4, -10.3 | no difference shown | -11.6 [-21.5, -4.5] | second term wins | **raw-head effect** |

Per seed (linear_z, BIOT CHB-MIT; rotation: S_r/1000+r/2000+r):
- last - lp: rot0 +1.1/+1.0/+0.1; rot1 +1.5/+0.4/+1.8; rot2 -0.2/-1.4/-3.2; rot3 +1.0/+2.2/+1.9; rot4 +0.8/+0.8/+2.8
- last_randinit - last: rot0 -6.0/-2.2/-7.6; rot1 +2.8/+3.2/-2.0; rot2 -1.8/+1.9/+1.6; rot3 +1.6/+11.3/+10.1; rot4 +8.3/+11.3/+6.8
- lp - lp_randinit: rot0 +4.8/+1.1/+7.5; rot1 -4.3/-3.5/+0.2; rot2 +2.1/-0.6/+1.5; rot3 -2.8/-13.5/-12.0; rot4 -9.2/-12.2/-9.6

## All cells (D24 rules on linear_z; comparisons descriptive)

| dataset | model | contrast | linear_z mean ± SEM | per rotation | 95% CI (bootstrap) | t95 | linear_z verdict | E32 raw mean [CI] | E32 raw verdict | E26 at S_r (1 seed) | D27-B 3 seeds, original partition (post hoc) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| CHB-MIT | biot | last - lp | +0.7 ± 0.6 | +0.7, +1.3, -1.6, +1.7, +1.5 | [-0.6, +1.6] | [-1.0, +2.4] | no difference shown | +3.6 [+0.8, +8.1] | first term wins | +0.2 no difference shown | +0.1 no difference shown |
| CHB-MIT | biot | last_randinit - last | +2.6 ± 2.6 | -5.3, +1.3, +0.6, +7.7, +8.8 | [-2.0, +7.2] | [-4.5, +9.7] | no difference shown | +7.8 [+2.7, +13.8] | first term wins | -1.3 no difference shown | +0.1 no difference shown |
| CHB-MIT | biot | lp - lp_randinit | -3.4 ± 2.9 | +4.5, -2.6, +1.0, -9.4, -10.3 | [-8.6, +1.8] | [-11.4, +4.6] | no difference shown | -11.6 [-21.5, -4.5] | second term wins | +1.1 no difference shown | -0.2 no difference shown |
| CHB-MIT | biot | D17 | -0.0 ± 0.0 | -0.0, +0.0, -0.0, -0.1, -0.0 | [-0.1, +0.0] | [-0.1, +0.0] | random features explain it | -0.1 [-0.9, +0.4] | random features explain it | +0.0 random features explain it | -0.0 random features explain it |
| CHB-MIT | cbramod | last - lp | -0.0 ± 0.6 | +0.4, +1.9, -0.9, -0.4, -1.1 | [-1.9, +1.6] | [-1.6, +1.5] | no difference shown | -0.0 [-0.2, +0.1] | no difference shown | +0.3 no difference shown | +0.4 no difference shown |
| CHB-MIT | cbramod | last_randinit - last | -0.9 ± 1.9 | +0.4, -2.5, +5.7, -2.3, -5.5 | [-4.5, +2.8] | [-6.1, +4.4] | no difference shown | -4.4 [-6.6, -2.4] | second term wins | -2.3 no difference shown | -5.6 second term wins |
| CHB-MIT | cbramod | lp - lp_randinit | +0.8 ± 1.8 | -0.7, +0.6, -4.7, +2.7, +6.4 | [-2.8, +4.5] | [-4.3, +6.0] | no difference shown | +4.6 [+2.0, +7.0] | first term wins | +2.1 no difference shown | +5.2 first term wins |
| CHB-MIT | cbramod | D17 | -0.0 ± 0.0 | +0.0, -0.0, -0.0, +0.0, -0.2 | [-0.2, +0.0] | [-0.2, +0.1] | random features explain it | +0.1 [-1.1, +1.4] | random features explain it | +0.0 random features explain it | +0.1 random features explain it |
| Siena | biot | last - lp | +1.7 ± 1.3 | +1.7, -1.2, +6.7, +0.9, +0.5 | [-0.3, +4.7] | [-2.0, +5.4] | no difference shown | +9.0 [+4.6, +12.6] | first term wins | +0.8 no difference shown | +1.7 no difference shown |
| Siena | biot | last_randinit - last | -0.1 ± 7.5 | +25.6, +0.4, -19.0, -9.6, +2.1 | [-12.8, +14.4] | [-20.8, +20.6] | no difference shown | +5.7 [-11.5, +22.2] | no difference shown | -1.4 no difference shown | +2.5 no difference shown |
| Siena | biot | lp - lp_randinit | -1.6 ± 7.0 | -27.3, +0.9, +12.4, +8.8, -2.6 | [-15.4, +10.0] | [-20.9, +17.8] | no difference shown | -14.7 [-28.2, -0.2] | second term wins | +0.6 no difference shown | -4.2 second term wins |
| Siena | biot | D17 | +0.0 ± 0.0 | +0.1, -0.0, +0.1, +0.0, +0.0 | [-0.0, +0.1] | [-0.0, +0.1] | random features explain it | +0.1 [-0.4, +0.5] | random features explain it | -0.0 random features explain it | +0.0 random features explain it |
| Siena | cbramod | last - lp | -0.3 ± 0.4 | +0.6, -0.8, -1.3, +0.3, -0.0 | [-1.0, +0.4] | [-1.3, +0.7] | no difference shown | +0.2 [-0.1, +0.6] | no difference shown | +0.8 no difference shown | -0.3 no difference shown |
| Siena | cbramod | last_randinit - last | -10.3 ± 1.5 | -9.1, -13.9, -5.2, -11.6, -11.6 | [-13.9, -6.5] | [-14.4, -6.2] | second term wins | -9.9 [-14.7, -5.5] | second term wins | -9.4 second term wins | -8.6 second term wins |
| Siena | cbramod | lp - lp_randinit | +10.5 ± 1.4 | +8.4, +14.7, +6.6, +11.1, +11.5 | [+6.8, +14.3] | [+6.6, +14.3] | first term wins | +12.4 [+7.6, +17.3] | first term wins | +8.6 first term wins | +8.8 first term wins |
| Siena | cbramod | D17 | -0.1 ± 0.0 | -0.1, -0.0, +0.0, -0.2, -0.1 | [-0.2, +0.0] | [-0.2, +0.1] | random features explain it | +2.6 [+0.6, +5.5] | random features explain it | -0.0 random features explain it | -0.0 random features explain it |

Descriptive counts (16 cells): same string as E32 raw head 9; as E26 at S_r 16; as D27-B (linear_z, 3 seeds, original partition; post hoc) 13. D17 CI = last_randinit - lp_randinit.

## Arms (descriptive; 3-seed means per rotation)

| setting | model | arm | linear_z mean ± SEM | linear_z per rotation | raw head mean ± SEM | raw head per rotation |
|---|---|---|---|---|---|---|
| CHB-MIT | biot | lp | 72.6 ± 3.2 | 63.9, 81.1, 67.5, 71.9, 78.5 | 61.0 ± 6.2 | 53.4, 76.0, 56.0, 44.5, 75.1 |
| CHB-MIT | biot | lp_randinit | 75.9 ± 5.6 | 59.4, 83.7, 66.5, 81.3, 88.8 | 72.6 ± 5.5 | 59.6, 80.1, 60.6, 74.9, 87.7 |
| CHB-MIT | biot | last | 73.3 ± 3.6 | 64.6, 82.4, 65.9, 73.6, 80.0 | 64.6 ± 5.4 | 54.7, 78.4, 56.1, 56.7, 77.2 |
| CHB-MIT | biot | last_randinit | 75.9 ± 5.6 | 59.3, 83.7, 66.4, 81.3, 88.8 | 72.4 ± 5.5 | 59.6, 79.6, 60.2, 75.0, 87.9 |
| CHB-MIT | cbramod | lp | 77.7 ± 5.6 | 64.6, 81.3, 64.6, 91.3, 86.8 | 82.4 ± 4.8 | 73.3, 84.6, 69.4, 93.5, 91.5 |
| CHB-MIT | cbramod | lp_randinit | 76.9 ± 4.2 | 65.3, 80.7, 69.3, 88.6, 80.4 | 77.9 ± 4.1 | 68.2, 81.4, 68.3, 88.3, 83.1 |
| CHB-MIT | cbramod | last | 77.7 ± 5.6 | 65.0, 83.2, 63.6, 90.9, 85.7 | 82.4 ± 4.9 | 73.1, 84.6, 69.2, 93.5, 91.7 |
| CHB-MIT | cbramod | last_randinit | 76.8 ± 4.2 | 65.3, 80.7, 69.3, 88.6, 80.1 | 78.0 ± 4.5 | 68.3, 82.0, 66.6, 89.5, 83.6 |
| Siena | biot | lp | 69.4 ± 5.5 | 50.9, 74.0, 63.2, 81.1, 77.8 | 50.7 ± 4.2 | 64.6, 43.9, 51.9, 40.2, 53.2 |
| Siena | biot | lp_randinit | 70.9 ± 5.3 | 78.1, 73.1, 50.8, 72.3, 80.4 | 65.4 ± 6.2 | 64.6, 72.0, 43.2, 67.0, 80.3 |
| Siena | biot | last | 71.1 ± 5.1 | 52.6, 72.8, 69.8, 82.0, 78.3 | 59.8 ± 6.1 | 78.2, 44.5, 64.2, 48.5, 63.4 |
| Siena | biot | last_randinit | 71.0 ± 5.3 | 78.2, 73.1, 50.8, 72.4, 80.4 | 65.5 ± 6.1 | 64.9, 72.2, 43.6, 66.8, 80.1 |
| Siena | cbramod | lp | 80.2 ± 2.6 | 79.6, 78.7, 71.9, 87.9, 82.9 | 83.9 ± 3.0 | 93.3, 79.9, 76.3, 87.9, 82.3 |
| Siena | cbramod | lp_randinit | 69.7 ± 2.3 | 71.1, 64.0, 65.3, 76.8, 71.3 | 71.6 ± 3.9 | 77.5, 60.0, 65.9, 81.6, 72.9 |
| Siena | cbramod | last | 79.9 ± 2.9 | 80.2, 77.9, 70.5, 88.2, 82.9 | 84.2 ± 3.1 | 93.2, 79.8, 76.3, 88.8, 82.8 |
| Siena | cbramod | last_randinit | 69.6 ± 2.3 | 71.1, 64.0, 65.3, 76.6, 71.2 | 74.2 ± 3.7 | 80.4, 62.1, 70.9, 83.4, 74.4 |

## Anomalies, CHB-MIT (descriptive, linear_z)

| model | arm | best epoch = last epoch (10) | test ROC < 50 | which (test ROC, val ROC x100) |
|---|---|---|---|---|
| biot | lp | 1 of 15 | 0 | - |
| biot | lp_randinit | 0 of 15 | 0 | - |
| biot | last | 1 of 15 | 0 | - |
| biot | last_randinit | 0 of 15 | 0 | - |
| cbramod | lp | 2 of 15 | 0 | - |
| cbramod | lp_randinit | 7 of 15 | 0 | - |
| cbramod | last | 2 of 15 | 0 | - |
| cbramod | last_randinit | 7 of 15 | 0 | - |

## Anomalies, Siena (descriptive, linear_z)

| model | arm | best epoch = last epoch (10) | test ROC < 50 | which (test ROC, val ROC x100) |
|---|---|---|---|---|
| biot | lp | 6 of 15 | 1 | rot0 s2000: test 34.8 (val 76.3) |
| biot | lp_randinit | 0 of 15 | 1 | rot2 s1002: test 49.2 (val 79.0) |
| biot | last | 6 of 15 | 1 | rot0 s2000: test 33.9 (val 76.8) |
| biot | last_randinit | 0 of 15 | 1 | rot2 s1002: test 49.1 (val 79.1) |
| cbramod | lp | 0 of 15 | 0 | - |
| cbramod | lp_randinit | 0 of 15 | 0 | - |
| cbramod | last | 1 of 15 | 0 | - |
| cbramod | last_randinit | 0 of 15 | 0 | - |
