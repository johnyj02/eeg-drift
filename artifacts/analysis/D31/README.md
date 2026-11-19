# D31: equal-budget, early-stopped linear probes on frozen features

Protocol: notes/decisions.md "## D31", frozen in git (commit 222d090) before any D31 run; applied as written. Probes: grid (raw features), grid_z (train-standardized); AdamW lr {3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2} x wd {0, 1e-4, 1e-2, 1e-1, 1} (30 configurations), batch 256, constant lr, BCE, <= 500 epochs, early stop after 20 epochs without a val ROC gain > 1e-4; configuration and epoch selected on val ROC-AUC; test read once there.
Units: rotation means over seeds [S_r, 1000+r, 2000+r] (95% t-interval df 4; Nadeau-Bengio corrected interval with n_test/n_train S1W 0.338, S3W 0.347, S3FW 0.347). DL's split: the 5 seeds 42/123/2021/3407/8888 on one fixed split (**seed uncertainty on one split**, no NB). Labels: **gain demonstrated** (95% t-interval excludes 0 and |mean| > 3 that way), **equivalent within +-3** (TOST margin 3, alpha 0.05 rejects), **not resolved**. D18 = the paired rule (|mean| > 3, same sign in >= 4/5), descriptive consistency criterion. Everything outside the labels and Q1-Q3 is descriptive. ROC-AUC x100.
D31 inherits the following reading choices from D28. Reading choices (NB label as sensitivity, Q3 = sign of the mean against D24-A/D24-B and D27-B, edges, 1-based epochs) were fixed before any D28 aggregate; the outlier list, the epoch <= 2 count and the per-model Q3 grouping were added after the first output (descriptive). See the script docstring.

Command: `.venv/bin/python scripts/analysis/d28_read.py --d31`

## Checks

- 505 D31 records (P1W 40, P1QW 15, S1W 150, S3W 150, S3FW 150), 1010 probe fits, 30300 configuration fits; 0 smoke records among them.
- P1W (DL's split): 40 records = 2 model(s) x 4 arms x 5 seeds; 1 per cell, 0 missing, 0 duplicates, 0 smoke; versions adapt 3 / probe 4 / grid 2; probes grid + grid_z; backbone eval, tap encoder, input_norm "", labels upstream; one eval set per split (both models)
  2400 configuration fits checked: grid fields = the frozen D31 search; selected configuration = first argmax of best val (ties among configurations: 7 fits); best_val = max of the logged curve; stopped early = stopped before epoch 500; early-stop replay on the logged (6-decimal) curves disagrees in 2 fits; non-finite train loss in 0; val ROC re-scored at the selection = best_val within 0e-9
  pairing with the fixed-recipe records of the same (model, arm, split, seed): linear SSL epoch losses identical: 20; linear paired: 40; linear_z SSL step losses identical: 20; linear_z paired: 40 (paired = same eval_hash, test index, val index, test n/prevalence, adapt_spec, arm_spec)
- P1QW (DL's split, BIOT q95 input): 15 records = 1 model(s) x 3 arms x 5 seeds; 1 per cell, 0 missing, 0 duplicates, 0 smoke; versions adapt 3 / probe 4 / grid 2; probes grid + grid_z; backbone eval, tap encoder, input_norm "q95", labels upstream; one eval set per split (both models)
  900 configuration fits checked: grid fields = the frozen D31 search; selected configuration = first argmax of best val (ties among configurations: 0 fits); best_val = max of the logged curve; stopped early = stopped before epoch 500; early-stop replay on the logged (6-decimal) curves disagrees in 0 fits; non-finite train loss in 0; val ROC re-scored at the selection = best_val within 0e-9
  pairing with the fixed-recipe records of the same (model, arm, split, seed): linear SSL step losses identical: 10; linear paired: 15; linear_z SSL step losses identical: 10; linear_z paired: 15 (paired = same eval_hash, test index, val index, test n/prevalence, adapt_spec, arm_spec)
- S1W (CHB-MIT rotations): 150 records = 2 model(s) x 5 arms x 5 rotations x 3 seeds; 1 per cell, 0 missing, 0 duplicates, 0 smoke; versions adapt 3 / probe 4 / grid 2; probes grid + grid_z; backbone eval, tap encoder, input_norm "", labels overlap; one eval set per split (both models)
  9000 configuration fits checked: grid fields = the frozen D31 search; selected configuration = first argmax of best val (ties among configurations: 11 fits); best_val = max of the logged curve; stopped early = stopped before epoch 500; early-stop replay on the logged (6-decimal) curves disagrees in 0 fits; non-finite train loss in 0; val ROC re-scored at the selection = best_val within 0e-9
  pairing with the fixed-recipe records of the same (model, arm, split, seed): linear SSL epoch losses identical: 60; linear SSL step losses identical: 15; linear missing: 15; linear paired: 135; linear_z SSL step losses identical: 60; linear_z missing: 30; linear_z paired: 120 (paired = same eval_hash, test index, val index, test n/prevalence, adapt_spec, arm_spec)
- S3W (Siena rotations): 150 records = 2 model(s) x 5 arms x 5 rotations x 3 seeds; 1 per cell, 0 missing, 0 duplicates, 0 smoke; versions adapt 3 / probe 4 / grid 2; probes grid + grid_z; backbone eval, tap encoder, input_norm "", labels overlap; one eval set per split (both models)
  9000 configuration fits checked: grid fields = the frozen D31 search; selected configuration = first argmax of best val (ties among configurations: 3 fits); best_val = max of the logged curve; stopped early = stopped before epoch 500; early-stop replay on the logged (6-decimal) curves disagrees in 0 fits; non-finite train loss in 0; val ROC re-scored at the selection = best_val within 0e-9
  pairing with the fixed-recipe records of the same (model, arm, split, seed): linear SSL epoch losses identical: 60; linear SSL step losses identical: 30; linear paired: 150; linear_z SSL step losses identical: 75; linear_z missing: 15; linear_z paired: 135 (paired = same eval_hash, test index, val index, test n/prevalence, adapt_spec, arm_spec)
- S3FW (Siena filtered rotations): 150 records = 2 model(s) x 5 arms x 5 rotations x 3 seeds; 1 per cell, 0 missing, 0 duplicates, 0 smoke; versions adapt 3 / probe 4 / grid 2; probes grid + grid_z; backbone eval, tap encoder, input_norm "", labels overlap; one eval set per split (both models)
  9000 configuration fits checked: grid fields = the frozen D31 search; selected configuration = first argmax of best val (ties among configurations: 5 fits); best_val = max of the logged curve; stopped early = stopped before epoch 500; early-stop replay on the logged (6-decimal) curves disagrees in 3 fits; non-finite train loss in 0; val ROC re-scored at the selection = best_val within 0e-9
  pairing with the fixed-recipe records of the same (model, arm, split, seed): linear SSL epoch losses identical: 60; linear SSL step losses identical: 30; linear paired: 150; linear_z SSL step losses identical: 75; linear_z missing: 15; linear_z paired: 135 (paired = same eval_hash, test index, val index, test n/prevalence, adapt_spec, arm_spec)
- Fixed-recipe contrasts re-derived from the records equal the published values: 48 D24-A/D24-B (raw) and D27-B (standardized) unit vectors (artifacts/analysis/D27B/d27b.json), 9 last - last_noise means (E27, A1, A6; artifacts/analysis/D27/noise.md).

## Answers

- **Q1** (any SA gain last - lp "gain demonstrated" with tuned probes?): **no**. 0 of 18 last - lp readings read "gain demonstrated" in the positive direction; labels: equivalent within +-3 14, not resolved 4.
- **Q2** (BIOT q95, DL's split, last - last_noise "gain demonstrated" with either variant?): **no**. grid: -0.6 [-1.5, +0.2], TOST p 0.0007, equivalent within +-3, per seed -0.5, +0.3, -1.5, -0.5, -1.0 (fixed recipe linear +8.6); grid_z: +1.6 [-3.2, +6.3], TOST p 0.225, not resolved, per seed +2.2, -0.1, -1.5, +8.0, -0.8 (fixed recipe linear_z +0.5)
- **Q3** (pretrained-vs-random contrasts keep their direction vs D24-A / D27-B?): **BIOT 7 of 16 signs flip; CBraMod yes (all signs kept)**. BIOT: 9 of 16 keep the sign of the mean (2 "gain demonstrated" that way); of the 7 fixed-recipe readings with a D18 win, 6 keep the sign and 2 read "gain demonstrated". Sign flips: S1W grid last_randinit - last +0.2 (no difference shown) -> -3.4 (not resolved); S1W grid lp - lp_randinit -2.0 (no difference shown) -> +8.9 (not resolved); S1W grid_z last_randinit - last +0.1 (no difference shown) -> -10.0 (not resolved); S1W grid_z lp - lp_randinit -0.2 (no difference shown) -> +10.8 (not resolved); S3FW grid last_randinit - last -4.7 (second term wins) -> +3.5 (not resolved); S3FW grid lp - lp_randinit +1.0 (no difference shown) -> -4.6 (not resolved); S3FW grid_z last_randinit - last -2.2 (no difference shown) -> +7.4 (not resolved). CBraMod: 16 of 16 keep the sign of the mean (7 "gain demonstrated" that way); of the 16 fixed-recipe readings with a D18 win, 16 keep the sign and 7 read "gain demonstrated".

## Contrasts (registered labels)

| setting | model | variant | contrast | mean | 95% t | NB 95% | TOST p | **label** | label with NB SE | D18 | same sign | per unit (rotation means / seeds) | fixed recipe (mean, 95% t, D18) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DL's split | BIOT | grid | last - lp | +0.9 | [-1.7, +3.4] | - | 0.040 | **equivalent within +-3** | - | no difference shown | 4/5 | +1.7, +0.1, -2.3, +1.7, +3.1 | linear -0.6 [-3.8, +2.6] no difference shown |
| DL's split | BIOT | grid | last_randinit - last | +11.4 | [+6.3, +16.6] | - | 0.995 | **gain demonstrated** | - | first term wins | 5/5 | +12.5, +7.0, +16.6, +13.8, +7.3 | linear +35.8 [+33.0, +38.5] first term wins |
| DL's split | BIOT | grid | lp - lp_randinit | -12.2 | [-16.6, -7.9] | - | 0.998 | **gain demonstrated** | - | second term wins | 5/5 | -14.4, -7.1, -14.1, -15.4, -10.2 | linear -35.1 [-35.9, -34.3] second term wins |
| DL's split | BIOT | grid_z | last - lp | -0.5 | [-8.9, +7.9] | - | 0.226 | **not resolved** | - | no difference shown | 3/5 | -0.2, -11.0, +7.9, +0.9, -0.1 | linear_z +0.2 [-2.1, +2.4] no difference shown |
| DL's split | BIOT | grid_z | last_randinit - last | +5.8 | [-3.5, +15.0] | - | 0.774 | **not resolved** | - | first term wins | 4/5 | +7.4, +18.0, +2.5, +1.1, -0.2 | linear_z +9.1 [+4.5, +13.6] first term wins |
| DL's split | BIOT | grid_z | lp - lp_randinit | -5.0 | [-10.4, +0.4] | - | 0.821 | **not resolved** | - | second term wins | 4/5 | -6.0, -7.0, -10.5, -1.9, +0.4 | linear_z -9.3 [-13.3, -5.2] second term wins |
| DL's split | CBraMod | grid | last - lp | -1.1 | [-2.7, +0.6] | - | 0.014 | **equivalent within +-3** | - | no difference shown | 5/5 | -0.3, -0.5, -3.3, -0.0, -1.1 | linear +0.0 [-0.0, +0.0] no difference shown |
| DL's split | CBraMod | grid | last_randinit - last | -3.8 | [-8.0, +0.5] | - | 0.678 | **not resolved** | - | second term wins | 5/5 | -2.0, -9.5, -0.6, -3.6, -3.1 | linear -8.5 [-9.4, -7.6] second term wins |
| DL's split | CBraMod | grid | lp - lp_randinit | +6.2 | [+2.6, +9.9] | - | 0.965 | **gain demonstrated** | - | first term wins | 5/5 | +4.8, +6.4, +11.2, +3.6, +5.1 | linear +6.4 [+4.4, +8.5] first term wins |
| DL's split | CBraMod | grid_z | last - lp | +0.1 | [-0.3, +0.4] | - | 8e-06 | **equivalent within +-3** | - | no difference shown | 3/5 | +0.2, -0.1, +0.0, +0.4, -0.3 | linear_z +0.2 [-0.0, +0.4] no difference shown |
| DL's split | CBraMod | grid_z | last_randinit - last | -3.2 | [-6.4, +0.0] | - | 0.563 | **not resolved** | - | second term wins | 5/5 | -2.4, -2.2, -7.7, -2.7, -1.1 | linear_z -3.6 [-7.0, -0.2] second term wins |
| DL's split | CBraMod | grid_z | lp - lp_randinit | +3.1 | [-0.0, +6.3] | - | 0.540 | **not resolved** | - | first term wins | 5/5 | +2.3, +2.3, +7.6, +2.2, +1.3 | linear_z +3.4 [+0.0, +6.8] first term wins |
| DL's split, BIOT q95 input | BIOT | grid | last - lp | +0.6 | [-0.0, +1.3] | - | 0.00024 | **equivalent within +-3** | - | no difference shown | 5/5 | +0.1, +0.9, +0.6, +0.2, +1.3 | linear +8.8 [+6.8, +10.8] first term wins |
| DL's split, BIOT q95 input | BIOT | grid | last - last_noise | -0.6 | [-1.5, +0.2] | - | 0.0007 | **equivalent within +-3** | - | no difference shown | 4/5 | -0.5, +0.3, -1.5, -0.5, -1.0 | linear +8.6 [+5.9, +11.2] first term wins |
| DL's split, BIOT q95 input | BIOT | grid_z | last - lp | +5.7 | [-1.0, +12.3] | - | 0.837 | **not resolved** | - | first term wins | 5/5 | +1.1, +12.9, +5.5, +8.8, +0.1 | linear_z +0.6 [-1.6, +2.8] no difference shown |
| DL's split, BIOT q95 input | BIOT | grid_z | last - last_noise | +1.6 | [-3.2, +6.3] | - | 0.225 | **not resolved** | - | no difference shown | 3/5 | +2.2, -0.1, -1.5, +8.0, -0.8 | linear_z +0.5 [-0.4, +1.3] no difference shown |
| CHB-MIT rotations | BIOT | grid | last - lp | -0.5 | [-1.6, +0.6] | [-2.3, +1.4] | 0.002 | **equivalent within +-3** | equivalent within +-3 | no difference shown | 3/5 | -0.3, +0.0, -0.4, -2.1, +0.3 | linear +1.9 [-1.0, +4.8] no difference shown |
| CHB-MIT rotations | BIOT | grid | last_randinit - last | -3.4 | [-12.7, +6.0] | [-18.7, +12.0] | 0.540 | **not resolved** | not resolved | no difference shown | 3/5 | -10.8, +2.5, -4.4, +6.1, -10.2 | linear +0.2 [-16.8, +17.1] no difference shown |
| CHB-MIT rotations | BIOT | grid | lp - lp_randinit | +8.9 | [-4.7, +22.5] | [-13.4, +31.2] | 0.852 | **not resolved** | not resolved | no difference shown | 3/5 | +9.0, -0.5, +24.4, -2.4, +14.0 | linear -2.0 [-17.0, +13.1] no difference shown |
| CHB-MIT rotations | BIOT | grid | last - last_noise | -0.1 | [-3.5, +3.2] | [-5.6, +5.4] | 0.038 | **equivalent within +-3** | not resolved | no difference shown | 4/5 | -2.4, -0.9, -0.1, -1.7, +4.4 | linear +0.8 [-3.3, +4.9] no difference shown |
| CHB-MIT rotations | BIOT | grid_z | last - lp | +0.3 | [-0.7, +1.2] | [-1.3, +1.8] | 0.00066 | **equivalent within +-3** | equivalent within +-3 | no difference shown | 3/5 | +0.8, +0.7, -0.6, +0.9, -0.5 | linear_z +0.1 [-1.1, +1.3] no difference shown |
| CHB-MIT rotations | BIOT | grid_z | last_randinit - last | -10.0 | [-27.9, +8.0] | [-39.4, +19.5] | 0.829 | **not resolved** | not resolved | second term wins | 4/5 | -1.7, +0.7, -33.4, -0.8, -14.5 | linear_z +0.1 [-14.2, +14.4] no difference shown |
| CHB-MIT rotations | BIOT | grid_z | lp - lp_randinit | +10.8 | [-10.9, +32.5] | [-24.8, +46.4] | 0.812 | **not resolved** | not resolved | no difference shown | 3/5 | +0.9, -1.5, +39.8, -0.2, +15.0 | linear_z -0.2 [-14.4, +13.9] no difference shown |
| CHB-MIT rotations | BIOT | grid_z | last - last_noise | +0.4 | [-0.6, +1.4] | [-1.2, +2.0] | 0.00097 | **equivalent within +-3** | equivalent within +-3 | no difference shown | 3/5 | -0.3, +1.1, -0.0, +1.4, -0.2 | - |
| CHB-MIT rotations | CBraMod | grid | last - lp | +0.3 | [-6.7, +7.3] | [-11.1, +11.8] | 0.175 | **not resolved** | not resolved | no difference shown | 3/5 | +0.6, -0.2, +8.8, -0.5, -7.1 | linear -0.0 [-0.4, +0.4] no difference shown |
| CHB-MIT rotations | CBraMod | grid | last_randinit - last | -3.0 | [-10.0, +4.0] | [-14.5, +8.4] | 0.505 | **not resolved** | not resolved | second term wins | 4/5 | -9.3, -4.0, -0.1, -6.7, +5.0 | linear -4.4 [-7.4, -1.4] second term wins |
| CHB-MIT rotations | CBraMod | grid | lp - lp_randinit | +1.5 | [-6.7, +9.6] | [-11.9, +14.8] | 0.313 | **not resolved** | not resolved | no difference shown | 3/5 | +8.5, +1.8, -8.6, +5.7, -0.2 | linear +5.5 [+2.5, +8.4] first term wins |
| CHB-MIT rotations | CBraMod | grid | last - last_noise | -0.2 | [-2.7, +2.3] | [-4.2, +3.9] | 0.017 | **equivalent within +-3** | not resolved | no difference shown | 3/5 | +0.3, +0.6, +2.1, -0.6, -3.3 | - |
| CHB-MIT rotations | CBraMod | grid_z | last - lp | +0.1 | [-1.9, +2.0] | [-3.1, +3.2] | 0.007 | **equivalent within +-3** | equivalent within +-3 | no difference shown | 4/5 | +0.4, +0.1, -2.4, +0.6, +1.8 | linear_z +0.4 [-0.6, +1.4] no difference shown |
| CHB-MIT rotations | CBraMod | grid_z | last_randinit - last | -4.1 | [-9.4, +1.2] | [-12.7, +4.6] | 0.698 | **not resolved** | not resolved | second term wins | 4/5 | -2.5, -8.6, -0.7, +0.1, -8.7 | linear_z -5.6 [-12.4, +1.2] second term wins |
| CHB-MIT rotations | CBraMod | grid_z | lp - lp_randinit | +4.3 | [-1.6, +10.2] | [-5.4, +14.0] | 0.713 | **not resolved** | not resolved | first term wins | 4/5 | +2.1, +10.2, +1.1, -0.5, +8.6 | linear_z +5.2 [-1.5, +12.0] first term wins |
| CHB-MIT rotations | CBraMod | grid_z | last - last_noise | -0.0 | [-1.4, +1.4] | [-2.3, +2.2] | 0.002 | **equivalent within +-3** | equivalent within +-3 | no difference shown | 3/5 | +1.4, +0.9, -1.2, -0.5, -0.7 | - |
| Siena rotations | BIOT | grid | last - lp | +1.7 | [+0.1, +3.3] | [-1.0, +4.4] | 0.045 | **equivalent within +-3** | not resolved | no difference shown | 5/5 | +1.6, +1.4, +3.8, +1.5, +0.2 | linear +9.2 [+2.3, +16.2] first term wins |
| Siena rotations | BIOT | grid | last_randinit - last | +6.3 | [-4.5, +17.1] | [-11.6, +24.1] | 0.776 | **not resolved** | not resolved | first term wins | 4/5 | -1.5, +19.6, +10.4, +2.2, +0.7 | linear +7.2 [-11.5, +25.9] no difference shown |
| Siena rotations | BIOT | grid | lp - lp_randinit | -7.3 | [-20.1, +5.5] | [-28.5, +13.9] | 0.797 | **not resolved** | not resolved | second term wins | 4/5 | +4.4, -22.0, -12.9, -4.5, -1.5 | linear -16.1 [-40.7, +8.6] second term wins |
| Siena rotations | BIOT | grid | last - last_noise | +0.1 | [-0.7, +1.0] | [-1.2, +1.5] | 0.00032 | **equivalent within +-3** | equivalent within +-3 | no difference shown | 3/5 | +0.4, +1.1, -0.1, -0.2, -0.6 | linear +1.6 [-2.3, +5.5] no difference shown |
| Siena rotations | BIOT | grid_z | last - lp | +1.7 | [+0.3, +3.1] | [-0.7, +4.1] | 0.033 | **equivalent within +-3** | not resolved | no difference shown | 5/5 | +0.1, +2.0, +3.3, +1.2, +1.8 | linear_z +1.7 [-0.3, +3.6] no difference shown |
| Siena rotations | BIOT | grid_z | last_randinit - last | +3.4 | [-5.0, +11.7] | [-10.4, +17.1] | 0.544 | **not resolved** | not resolved | no difference shown | 3/5 | -4.9, +7.6, +12.3, -0.1, +1.9 | linear_z +2.5 [-4.5, +9.6] no difference shown |
| Siena rotations | BIOT | grid_z | lp - lp_randinit | -4.6 | [-14.0, +4.8] | [-20.2, +11.0] | 0.672 | **not resolved** | not resolved | second term wins | 4/5 | +4.7, -7.7, -15.5, -0.9, -3.7 | linear_z -4.2 [-10.9, +2.5] second term wins |
| Siena rotations | BIOT | grid_z | last - last_noise | +0.8 | [-1.2, +2.8] | [-2.5, +4.2] | 0.020 | **equivalent within +-3** | not resolved | no difference shown | 4/5 | -0.9, +0.9, +3.5, +0.5, +0.1 | linear_z +0.4 [-1.2, +2.0] no difference shown |
| Siena rotations | CBraMod | grid | last - lp | +0.0 | [-2.0, +2.0] | [-3.3, +3.3] | 0.007 | **equivalent within +-3** | equivalent within +-3 | no difference shown | 4/5 | +1.1, -2.8, +0.5, +1.0, +0.3 | linear +0.3 [-0.4, +0.9] no difference shown |
| Siena rotations | CBraMod | grid | last_randinit - last | -8.0 | [-15.6, -0.3] | [-20.6, +4.7] | 0.927 | **gain demonstrated** | not resolved | second term wins | 4/5 | -9.9, -3.4, -15.1, +0.0, -11.6 | linear -7.6 [-14.3, -0.9] second term wins |
| Siena rotations | CBraMod | grid | lp - lp_randinit | +7.3 | [-0.6, +15.2] | [-5.7, +20.4] | 0.899 | **not resolved** | not resolved | first term wins | 4/5 | +6.5, +5.2, +16.0, -1.2, +10.2 | linear +7.0 [-2.4, +16.3] first term wins |
| Siena rotations | CBraMod | grid | last - last_noise | -0.3 | [-1.7, +1.1] | [-2.6, +2.0] | 0.003 | **equivalent within +-3** | equivalent within +-3 | no difference shown | 3/5 | -0.7, -2.0, -0.0, +0.9, +0.2 | linear -0.1 [-0.1, -0.0] no difference shown |
| Siena rotations | CBraMod | grid_z | last - lp | +0.3 | [-1.4, +2.0] | [-2.5, +3.1] | 0.006 | **equivalent within +-3** | equivalent within +-3 | no difference shown | 3/5 | +2.4, +0.5, -0.4, +0.2, -1.3 | linear_z -0.3 [-1.3, +0.7] no difference shown |
| Siena rotations | CBraMod | grid_z | last_randinit - last | -9.4 | [-16.7, -2.2] | [-21.4, +2.5] | 0.965 | **gain demonstrated** | not resolved | second term wins | 5/5 | -6.2, -9.0, -19.5, -7.5, -4.9 | linear_z -8.6 [-16.2, -1.0] second term wins |
| Siena rotations | CBraMod | grid_z | lp - lp_randinit | +8.1 | [-0.8, +16.9] | [-6.5, +22.6] | 0.906 | **not resolved** | not resolved | first term wins | 5/5 | +0.8, +5.8, +19.8, +8.3, +5.5 | linear_z +8.8 [+1.5, +16.2] first term wins |
| Siena rotations | CBraMod | grid_z | last - last_noise | -0.3 | [-1.4, +0.7] | [-2.1, +1.4] | 0.001 | **equivalent within +-3** | equivalent within +-3 | no difference shown | 3/5 | -0.2, +0.9, +0.0, -1.2, -1.2 | - |
| Siena filtered rotations | BIOT | grid | last - lp | -0.1 | [-1.7, +1.5] | [-2.7, +2.6] | 0.004 | **equivalent within +-3** | equivalent within +-3 | no difference shown | 3/5 | -0.0, -2.3, +0.1, +0.9, +0.9 | linear +4.1 [+0.1, +8.2] first term wins |
| Siena filtered rotations | BIOT | grid | last_randinit - last | +3.5 | [-13.2, +20.2] | [-24.1, +31.1] | 0.529 | **not resolved** | not resolved | first term wins | 4/5 | -17.9, +11.2, +3.5, +2.7, +17.8 | linear -4.7 [-34.5, +25.1] second term wins |
| Siena filtered rotations | BIOT | grid | lp - lp_randinit | -4.6 | [-18.2, +9.0] | [-27.1, +17.9] | 0.620 | **not resolved** | not resolved | second term wins | 4/5 | +11.7, -8.4, -4.0, -3.5, -18.8 | linear +1.0 [-32.6, +34.6] no difference shown |
| Siena filtered rotations | BIOT | grid | last - last_noise | -1.2 | [-3.4, +1.0] | [-4.9, +2.5] | 0.045 | **equivalent within +-3** | not resolved | no difference shown | 3/5 | -0.1, -2.2, +0.2, -3.9, +0.0 | linear +1.3 [-1.4, +3.9] no difference shown |
| Siena filtered rotations | BIOT | grid_z | last - lp | +1.3 | [-3.1, +5.8] | [-6.0, +8.7] | 0.178 | **not resolved** | not resolved | no difference shown | 3/5 | -0.1, +4.2, +0.5, +5.5, -3.4 | linear_z +1.9 [-1.6, +5.5] no difference shown |
| Siena filtered rotations | BIOT | grid_z | last_randinit - last | +7.4 | [-8.0, +22.8] | [-18.1, +32.9] | 0.764 | **not resolved** | not resolved | first term wins | 4/5 | -8.8, +4.6, +5.1, +10.4, +25.6 | linear_z -2.2 [-18.9, +14.5] no difference shown |
| Siena filtered rotations | BIOT | grid_z | lp - lp_randinit | -8.8 | [-23.6, +5.9] | [-33.2, +15.6] | 0.833 | **not resolved** | not resolved | second term wins | 4/5 | +8.8, -8.9, -5.5, -15.8, -22.7 | linear_z -0.2 [-14.4, +13.9] no difference shown |
| Siena filtered rotations | BIOT | grid_z | last - last_noise | -0.7 | [-2.5, +1.1] | [-3.7, +2.3] | 0.012 | **equivalent within +-3** | not resolved | no difference shown | 4/5 | +0.9, -2.9, -0.1, -0.1, -1.4 | linear_z +1.1 [-1.8, +4.1] no difference shown |
| Siena filtered rotations | CBraMod | grid | last - lp | +0.1 | [-0.1, +0.4] | [-0.3, +0.6] | 3.5e-06 | **equivalent within +-3** | equivalent within +-3 | no difference shown | 4/5 | +0.2, +0.2, +0.3, -0.2, +0.1 | linear +0.1 [-0.0, +0.3] no difference shown |
| Siena filtered rotations | CBraMod | grid | last_randinit - last | -9.2 | [-16.8, -1.6] | [-21.7, +3.4] | 0.957 | **gain demonstrated** | not resolved | second term wins | 5/5 | -15.9, -4.4, -5.6, -4.2, -15.8 | linear -10.7 [-17.0, -4.4] second term wins |
| Siena filtered rotations | CBraMod | grid | lp - lp_randinit | +8.3 | [+1.8, +14.7] | [-2.5, +19.0] | 0.956 | **gain demonstrated** | not resolved | first term wins | 5/5 | +14.8, +2.2, +5.8, +6.0, +12.6 | linear +9.4 [+3.6, +15.3] first term wins |
| Siena filtered rotations | CBraMod | grid | last - last_noise | +0.5 | [-0.8, +1.9] | [-1.7, +2.8] | 0.004 | **equivalent within +-3** | equivalent within +-3 | no difference shown | 3/5 | +2.5, +0.1, -0.0, +0.1, -0.0 | linear -0.0 [-0.0, +0.0] no difference shown |
| Siena filtered rotations | CBraMod | grid_z | last - lp | -0.1 | [-1.0, +0.8] | [-1.7, +1.5] | 0.00051 | **equivalent within +-3** | equivalent within +-3 | no difference shown | 3/5 | +0.7, -0.9, +0.3, -0.9, +0.3 | linear_z +0.3 [-0.2, +0.8] no difference shown |
| Siena filtered rotations | CBraMod | grid_z | last_randinit - last | -10.6 | [-18.4, -2.8] | [-23.4, +2.3] | 0.973 | **gain demonstrated** | not resolved | second term wins | 5/5 | -19.6, -14.2, -5.4, -5.0, -8.8 | linear_z -9.2 [-16.6, -1.7] second term wins |
| Siena filtered rotations | CBraMod | grid_z | lp - lp_randinit | +11.1 | [+4.8, +17.5] | [+0.6, +21.6] | 0.988 | **gain demonstrated** | gain demonstrated | first term wins | 5/5 | +18.6, +13.0, +4.8, +9.0, +10.1 | linear_z +8.8 [+1.4, +16.2] first term wins |
| Siena filtered rotations | CBraMod | grid_z | last - last_noise | +0.1 | [-0.7, +0.9] | [-1.3, +1.5] | 0.00033 | **equivalent within +-3** | equivalent within +-3 | no difference shown | 3/5 | +0.0, +1.0, +0.4, -0.8, -0.1 | - |

## Per seed (rotations: S_r / 1000+r / 2000+r per rotation)

- P1W BIOT grid last - lp: +1.7, +0.1, -2.3, +1.7, +3.1
- P1W BIOT grid last_randinit - last: +12.5, +7.0, +16.6, +13.8, +7.3
- P1W BIOT grid lp - lp_randinit: -14.4, -7.1, -14.1, -15.4, -10.2
- P1W BIOT grid_z last - lp: -0.2, -11.0, +7.9, +0.9, -0.1
- P1W BIOT grid_z last_randinit - last: +7.4, +18.0, +2.5, +1.1, -0.2
- P1W BIOT grid_z lp - lp_randinit: -6.0, -7.0, -10.5, -1.9, +0.4
- P1W CBraMod grid last - lp: -0.3, -0.5, -3.3, -0.0, -1.1
- P1W CBraMod grid last_randinit - last: -2.0, -9.5, -0.6, -3.6, -3.1
- P1W CBraMod grid lp - lp_randinit: +4.8, +6.4, +11.2, +3.6, +5.1
- P1W CBraMod grid_z last - lp: +0.2, -0.1, +0.0, +0.4, -0.3
- P1W CBraMod grid_z last_randinit - last: -2.4, -2.2, -7.7, -2.7, -1.1
- P1W CBraMod grid_z lp - lp_randinit: +2.3, +2.3, +7.6, +2.2, +1.3
- P1QW BIOT grid last - lp: +0.1, +0.9, +0.6, +0.2, +1.3
- P1QW BIOT grid last - last_noise: -0.5, +0.3, -1.5, -0.5, -1.0
- P1QW BIOT grid_z last - lp: +1.1, +12.9, +5.5, +8.8, +0.1
- P1QW BIOT grid_z last - last_noise: +2.2, -0.1, -1.5, +8.0, -0.8
- S1W BIOT grid last - lp: rot0 -0.1/-0.4/-0.3; rot1 -1.0/+0.8/+0.3; rot2 -0.6/-0.9/+0.4; rot3 +0.3/-0.1/-6.3; rot4 +1.1/+0.6/-0.8
- S1W BIOT grid last_randinit - last: rot0 -9.7/-11.4/-11.4; rot1 +13.8/-1.4/-4.9; rot2 -1.6/+0.9/-12.6; rot3 +5.6/+4.3/+8.5; rot4 -7.1/-23.4/-0.1
- S1W BIOT grid lp - lp_randinit: rot0 +4.7/+11.0/+11.4; rot1 -7.6/+10.8/-4.8; rot2 +25.8/+38.2/+9.2; rot3 -3.6/-1.1/-2.4; rot4 +9.1/+24.6/+8.1
- S1W BIOT grid last - last_noise: rot0 -4.9/-1.1/-1.2; rot1 -5.5/+0.6/+2.3; rot2 +0.1/-0.4/+0.1; rot3 -0.0/+0.7/-5.7; rot4 +0.9/+12.0/+0.4
- S1W BIOT grid_z last - lp: rot0 +1.8/-1.2/+1.8; rot1 +3.3/+0.3/-1.3; rot2 +0.1/-2.8/+0.9; rot3 +1.3/+0.7/+0.9; rot4 +0.0/-0.1/-1.5
- S1W BIOT grid_z last_randinit - last: rot0 -6.0/+0.5/+0.3; rot1 -12.4/+7.5/+6.9; rot2 -20.6/-41.8/-37.9; rot3 -1.7/-1.0/+0.5; rot4 -17.5/+0.4/-26.4
- S1W BIOT grid_z lp - lp_randinit: rot0 +4.1/+0.7/-2.0; rot1 +9.1/-8.0/-5.6; rot2 +37.3/+44.6/+37.3; rot3 +0.4/+0.3/-1.3; rot4 +17.5/-0.3/+27.8
- S1W BIOT grid_z last - last_noise: rot0 -0.3/+0.2/-0.8; rot1 +2.5/+0.0/+0.9; rot2 -1.0/+0.8/+0.2; rot3 +3.3/+1.0/-0.1; rot4 +0.3/+0.2/-1.1
- S1W CBraMod grid last - lp: rot0 -0.7/+0.5/+2.2; rot1 +0.5/+0.6/-1.7; rot2 +2.2/+8.3/+15.8; rot3 +0.8/-2.9/+0.7; rot4 -8.4/-5.9/-6.9
- S1W CBraMod grid last_randinit - last: rot0 -8.9/-8.0/-11.1; rot1 +0.0/-5.8/-6.3; rot2 -4.8/+2.6/+1.8; rot3 +0.6/-5.9/-14.7; rot4 +9.5/-3.3/+8.8
- S1W CBraMod grid lp - lp_randinit: rot0 +7.2/+7.1/+11.1; rot1 +0.7/-0.1/+4.8; rot2 -1.7/-6.9/-17.2; rot3 +6.2/+10.3/+0.7; rot4 +0.0/-0.7/+0.1
- S1W CBraMod grid last - last_noise: rot0 -0.7/-1.6/+3.2; rot1 -0.1/-5.5/+7.4; rot2 +5.2/+4.0/-2.9; rot3 -0.8/-1.5/+0.6; rot4 -5.0/+1.9/-6.8
- S1W CBraMod grid_z last - lp: rot0 -3.3/+0.5/+3.9; rot1 +1.5/-0.3/-1.0; rot2 +6.2/-10.6/-3.0; rot3 +4.1/-0.2/-2.2; rot4 +8.7/-2.8/-0.4
- S1W CBraMod grid_z last_randinit - last: rot0 -4.4/+2.0/-5.1; rot1 -9.2/-13.1/-3.4; rot2 -3.0/-1.8/+2.7; rot3 +2.7/-3.7/+1.2; rot4 -5.1/-8.3/-12.7
- S1W CBraMod grid_z lp - lp_randinit: rot0 +7.7/-2.6/+1.1; rot1 +3.3/+14.7/+12.5; rot2 -3.3/+7.8/-1.1; rot3 -6.7/+4.3/+1.0; rot4 -2.6/+13.2/+15.3
- S1W CBraMod grid_z last - last_noise: rot0 +4.2/-0.1/+0.1; rot1 +2.7/+0.1/-0.1; rot2 +9.5/-7.3/-5.8; rot3 +3.2/-4.9/+0.3; rot4 -4.4/+2.1/+0.2
- S3W BIOT grid last - lp: rot0 +2.9/+0.9/+1.1; rot1 -0.1/+3.8/+0.7; rot2 +4.1/+9.1/-1.9; rot3 +1.3/+1.2/+1.8; rot4 +1.5/-0.6/-0.4
- S3W BIOT grid last_randinit - last: rot0 +0.6/-5.0/-0.1; rot1 +18.5/+20.8/+19.4; rot2 +17.0/+7.1/+7.0; rot3 +1.4/+3.3/+1.8; rot4 -2.5/+3.5/+1.1
- S3W BIOT grid lp - lp_randinit: rot0 +3.9/+5.6/+3.9; rot1 -18.2/-24.3/-23.6; rot2 -16.8/-16.2/-5.8; rot3 -3.7/-4.5/-5.1; rot4 -1.4/-3.0/-0.1
- S3W BIOT grid last - last_noise: rot0 +0.5/+0.1/+0.6; rot1 +0.5/+3.8/-0.9; rot2 +3.5/-0.4/-3.3; rot3 -1.9/-0.1/+1.2; rot4 -0.6/-0.6/-0.6
- S3W BIOT grid_z last - lp: rot0 -0.1/-0.2/+0.7; rot1 -2.3/+7.9/+0.3; rot2 -4.6/+15.2/-0.6; rot3 +1.2/+1.8/+0.7; rot4 +0.5/+1.2/+3.8
- S3W BIOT grid_z last_randinit - last: rot0 -5.7/-8.9/-0.1; rot1 +11.2/+0.5/+11.1; rot2 +15.4/+10.9/+10.6; rot3 -1.8/+2.7/-1.2; rot4 +1.9/+3.3/+0.5
- S3W BIOT grid_z lp - lp_randinit: rot0 +5.8/+9.0/-0.5; rot1 -9.0/-8.4/-5.7; rot2 -10.5/-26.1/-9.9; rot3 +0.7/-3.9/+0.5; rot4 -2.4/-4.5/-4.3
- S3W BIOT grid_z last - last_noise: rot0 +0.2/+0.2/-2.9; rot1 -0.1/+2.6/+0.1; rot2 -0.8/+13.3/-2.0; rot3 +1.2/+0.9/-0.4; rot4 -1.9/+1.9/+0.2
- S3W CBraMod grid last - lp: rot0 +0.8/-2.1/+4.5; rot1 -3.8/-0.5/-4.1; rot2 +1.1/+0.8/-0.4; rot3 +5.3/+0.7/-3.0; rot4 +0.8/+0.3/-0.3
- S3W CBraMod grid last_randinit - last: rot0 -6.1/-9.2/-14.3; rot1 +1.8/-12.6/+0.7; rot2 -29.2/-13.4/-2.7; rot3 +1.9/-4.5/+2.7; rot4 -7.8/-6.8/-20.1
- S3W CBraMod grid lp - lp_randinit: rot0 +5.6/+6.5/+7.3; rot1 +2.4/+10.7/+2.6; rot2 +25.2/+15.9/+6.9; rot3 -6.0/+1.7/+0.6; rot4 +5.3/+7.0/+18.3
- S3W CBraMod grid last - last_noise: rot0 +0.7/-2.8/+0.1; rot1 -1.9/+0.1/-4.3; rot2 -0.0/+0.0/-0.0; rot3 +4.4/+2.1/-3.7; rot4 +0.7/-0.0/-0.0
- S3W CBraMod grid_z last - lp: rot0 -10.5/+0.4/+17.2; rot1 +0.2/+3.5/-2.1; rot2 -0.4/-0.9/-0.1; rot3 +0.6/+2.4/-2.4; rot4 +1.5/-6.4/+1.1
- S3W CBraMod grid_z last_randinit - last: rot0 +5.5/-14.2/-10.0; rot1 -7.3/-8.9/-10.8; rot2 -32.6/-21.5/-4.4; rot3 -3.7/-13.1/-5.8; rot4 -0.9/+2.8/-16.6
- S3W CBraMod grid_z lp - lp_randinit: rot0 +4.8/+4.9/-7.2; rot1 +7.2/+4.2/+6.0; rot2 +33.0/+22.3/+4.2; rot3 +1.3/+15.2/+8.2; rot4 -0.7/-0.9/+18.2
- S3W CBraMod grid_z last - last_noise: rot0 -0.6/-0.0/+0.0; rot1 +0.0/+3.3/-0.7; rot2 -0.0/+0.1/+0.0; rot3 -0.1/-0.0/-3.4; rot4 -0.2/-0.2/-3.1
- S3FW BIOT grid last - lp: rot0 +0.3/-0.7/+0.3; rot1 -6.6/-0.3/+0.1; rot2 +1.3/-0.5/-0.4; rot3 +0.9/+2.3/-0.6; rot4 +1.2/-0.3/+1.9
- S3FW BIOT grid last_randinit - last: rot0 -22.0/-16.1/-15.6; rot1 +11.7/+12.1/+9.6; rot2 +3.2/+2.6/+4.9; rot3 -1.3/+8.2/+1.3; rot4 +17.0/+19.7/+16.8
- S3FW BIOT grid lp - lp_randinit: rot0 +5.0/+17.6/+12.3; rot1 -6.1/-11.8/-7.4; rot2 -5.6/-1.6/-4.7; rot3 +0.4/-10.3/-0.6; rot4 -18.7/-19.0/-18.6
- S3FW BIOT grid last - last_noise: rot0 -2.2/-0.3/+2.1; rot1 -5.8/-1.1/+0.2; rot2 +1.4/-0.4/-0.4; rot3 -0.4/-11.4/+0.0; rot4 -0.5/-0.0/+0.5
- S3FW BIOT grid_z last - lp: rot0 -0.5/-0.1/+0.3; rot1 +4.3/+7.2/+1.2; rot2 -0.1/+0.6/+0.9; rot3 +1.4/+12.8/+2.3; rot4 -0.8/-4.6/-4.9
- S3FW BIOT grid_z last_randinit - last: rot0 +1.7/-10.1/-18.0; rot1 +6.9/+5.0/+2.0; rot2 +5.2/+5.1/+5.2; rot3 +13.7/+13.9/+3.7; rot4 +20.2/+27.0/+29.6
- S3FW BIOT grid_z lp - lp_randinit: rot0 -1.2/+10.1/+17.6; rot1 -11.4/-12.1/-3.1; rot2 -4.4/-4.5/-7.6; rot3 -15.0/-26.5/-6.1; rot4 -22.2/-22.8/-23.2
- S3FW BIOT grid_z last - last_noise: rot0 -2.4/+0.1/+5.0; rot1 -9.7/+0.4/+0.7; rot2 -0.2/-0.4/+0.3; rot3 -7.7/-4.1/+11.4; rot4 -0.3/+0.9/-4.7
- S3FW CBraMod grid last - lp: rot0 +0.6/-0.9/+0.8; rot1 -0.2/+0.7/-0.1; rot2 -1.6/+2.0/+0.6; rot3 +0.1/-1.1/+0.3; rot4 +0.1/+0.2/+0.1
- S3FW CBraMod grid last_randinit - last: rot0 -19.3/-15.2/-13.3; rot1 -5.2/-3.3/-4.7; rot2 -5.5/-2.7/-8.6; rot3 -4.6/-4.1/-4.0; rot4 -13.7/-8.4/-25.1
- S3FW CBraMod grid lp - lp_randinit: rot0 +15.8/+16.1/+12.4; rot1 +3.1/+0.6/+2.9; rot2 +10.6/+1.1/+5.7; rot3 +4.7/+7.9/+5.3; rot4 +13.8/+11.0/+12.9
- S3FW CBraMod grid last - last_noise: rot0 +2.8/+5.3/-0.7; rot1 -0.0/+0.2/-0.0; rot2 -2.0/+1.4/+0.5; rot3 +0.0/+0.3/+0.0; rot4 -0.0/-0.0/-0.0
- S3FW CBraMod grid_z last - lp: rot0 -0.0/+2.1/+0.1; rot1 -1.0/-0.2/-1.3; rot2 +1.4/-0.4/-0.0; rot3 -0.2/-0.6/-2.1; rot4 +1.1/+0.9/-1.0
- S3FW CBraMod grid_z last_randinit - last: rot0 -23.5/-12.8/-22.5; rot1 -9.3/-20.4/-12.8; rot2 -7.0/+1.6/-10.6; rot3 -2.5/-6.5/-5.9; rot4 -4.0/-2.2/-20.1
- S3FW CBraMod grid_z lp - lp_randinit: rot0 +23.4/+10.1/+22.4; rot1 +10.2/+23.3/+5.4; rot2 +5.6/-1.3/+10.2; rot3 +2.5/+16.5/+7.9; rot4 +15.5/+1.6/+13.3
- S3FW CBraMod grid_z last - last_noise: rot0 +0.1/-0.0/+0.0; rot1 -2.3/+5.3/-0.0; rot2 +1.2/+0.1/+0.0; rot3 +0.0/-0.0/-2.5; rot4 -0.2/-0.2/-0.1

## Absolute test ROC-AUC per arm: tuned vs fixed recipe (same seeds)

| setting | model | arm | grid | linear (fixed) | grid - linear | grid_z | linear_z (fixed) | grid_z - linear_z | grid per unit | grid_z per unit |
|---|---|---|---|---|---|---|---|---|---|---|
| DL's split | BIOT | lp | 76.5 ± 1.7 | 55.0 | +21.5 | 83.9 ± 1.7 | 79.1 | +4.8 | 74.3, 82.5, 74.9, 72.9, 78.0 | 83.3, 82.8, 78.7, 86.2, 88.8 |
| DL's split | BIOT | last | 77.4 ± 1.9 | 54.4 | +23.0 | 83.5 ± 3.1 | 79.3 | +4.2 | 75.9, 82.6, 72.6, 74.6, 81.1 | 83.1, 71.8, 86.6, 87.1, 88.7 |
| DL's split | BIOT | last_randinit | 88.8 ± 0.3 | 90.2 | -1.4 | 89.2 ± 0.4 | 88.4 | +0.9 | 88.4, 89.6, 89.2, 88.4, 88.4 | 90.6, 89.8, 89.1, 88.2, 88.5 |
| DL's split | BIOT | lp_randinit | 88.7 ± 0.3 | 90.1 | -1.4 | 89.0 ± 0.3 | 88.4 | +0.6 | 88.7, 89.6, 89.0, 88.3, 88.2 | 89.3, 89.8, 89.2, 88.1, 88.4 |
| DL's split | CBraMod | lp | 92.0 ± 0.3 | 92.0 | -0.0 | 89.4 ± 0.4 | 88.5 | +1.0 | 91.1, 92.5, 91.8, 91.6, 92.9 | 88.7, 89.2, 90.2, 90.3, 88.6 |
| DL's split | CBraMod | last | 90.9 ± 0.6 | 92.0 | -1.1 | 89.5 ± 0.4 | 88.6 | +0.8 | 90.8, 92.0, 88.5, 91.6, 91.7 | 88.9, 89.1, 90.3, 90.7, 88.4 |
| DL's split | CBraMod | last_randinit | 87.2 ± 1.2 | 83.5 | +3.7 | 86.3 ± 1.0 | 85.0 | +1.2 | 88.7, 82.5, 88.0, 88.0, 88.7 | 86.5, 87.0, 82.6, 88.1, 87.3 |
| DL's split | CBraMod | lp_randinit | 85.8 ± 1.3 | 85.6 | +0.2 | 86.3 ± 1.0 | 85.1 | +1.2 | 86.2, 86.1, 80.6, 88.1, 87.8 | 86.5, 87.0, 82.6, 88.1, 87.3 |
| DL's split, BIOT q95 input | BIOT | lp | 72.5 ± 0.4 | 33.1 | +39.4 | 70.1 ± 2.2 | 70.2 | -0.1 | 73.7, 72.5, 71.6, 72.9, 71.7 | 74.8, 63.9, 66.1, 71.4, 74.3 |
| DL's split, BIOT q95 input | BIOT | last | 73.1 ± 0.3 | 41.9 | +31.3 | 75.8 ± 1.4 | 70.8 | +4.9 | 73.9, 73.4, 72.3, 73.0, 73.1 | 75.8, 76.8, 71.6, 80.2, 74.4 |
| DL's split, BIOT q95 input | BIOT | last_noise | 73.8 ± 0.2 | 33.3 | +40.5 | 74.2 ± 0.8 | 70.4 | +3.8 | 74.4, 73.1, 73.8, 73.6, 74.0 | 73.6, 76.9, 73.1, 72.2, 75.2 |
| CHB-MIT rotations | BIOT | lp | 76.4 ± 5.3 | 65.1 | +11.3 | 77.1 ± 6.0 | 72.3 | +4.8 | 66.9, 78.3, 89.0, 61.8, 85.7 | 61.5, 84.1, 89.2, 63.6, 86.9 |
| CHB-MIT rotations | BIOT | last | 75.9 ± 5.6 | 67.0 | +8.9 | 77.3 ± 5.7 | 72.4 | +5.0 | 66.6, 78.3, 88.7, 59.8, 86.0 | 62.3, 84.8, 88.6, 64.6, 86.4 |
| CHB-MIT rotations | BIOT | last_randinit | 72.5 ± 5.2 | 67.1 | +5.4 | 67.4 ± 5.3 | 72.5 | -5.1 | 55.8, 80.8, 84.3, 65.9, 75.8 | 60.5, 85.5, 55.2, 63.8, 71.9 |
| CHB-MIT rotations | BIOT | lp_randinit | 67.5 ± 3.6 | 67.0 | +0.5 | 66.3 ± 6.0 | 72.5 | -6.2 | 57.9, 78.8, 64.7, 64.2, 71.8 | 60.5, 85.6, 49.5, 63.8, 71.9 |
| CHB-MIT rotations | BIOT | last_noise | 76.0 ± 4.8 | 66.2 | +9.8 | 76.9 ± 5.8 | - | - | 69.0, 79.2, 88.8, 61.5, 81.6 | 62.6, 83.7, 88.7, 63.2, 86.6 |
| CHB-MIT rotations | CBraMod | lp | 76.3 ± 2.6 | 81.6 | -5.3 | 75.8 ± 4.0 | 79.3 | -3.5 | 70.2, 83.8, 74.6, 72.1, 80.9 | 67.1, 85.1, 83.6, 66.2, 77.3 |
| CHB-MIT rotations | CBraMod | last | 76.7 ± 2.8 | 81.6 | -4.9 | 75.9 ± 3.7 | 79.7 | -3.8 | 70.9, 83.6, 83.4, 71.7, 73.9 | 67.4, 85.1, 81.1, 66.8, 79.1 |
| CHB-MIT rotations | CBraMod | last_randinit | 73.6 ± 4.3 | 77.2 | -3.5 | 71.8 ± 2.9 | 74.1 | -2.3 | 61.5, 79.6, 83.3, 65.0, 78.9 | 64.9, 76.6, 80.4, 66.9, 70.4 |
| CHB-MIT rotations | CBraMod | lp_randinit | 74.9 ± 4.5 | 76.2 | -1.3 | 71.5 ± 3.2 | 74.1 | -2.5 | 61.7, 82.0, 83.2, 66.4, 81.1 | 65.0, 74.9, 82.4, 66.7, 68.7 |
| CHB-MIT rotations | CBraMod | last_noise | 76.9 ± 2.4 | - | - | 75.9 ± 3.9 | - | - | 70.6, 83.0, 81.3, 72.2, 77.2 | 66.0, 84.2, 82.3, 67.3, 79.8 |
| Siena rotations | BIOT | lp | 73.6 ± 4.7 | 51.3 | +22.2 | 77.5 ± 3.2 | 68.6 | +8.9 | 73.8, 61.2, 65.7, 80.3, 86.9 | 73.5, 78.7, 67.5, 83.1, 84.7 |
| Siena rotations | BIOT | last | 75.3 ± 4.3 | 60.6 | +14.7 | 79.2 ± 3.0 | 70.2 | +8.9 | 75.5, 62.7, 69.4, 81.7, 87.1 | 73.6, 80.7, 70.8, 84.3, 86.5 |
| Siena rotations | BIOT | last_randinit | 81.6 ± 2.3 | 67.8 | +13.8 | 82.5 ± 3.6 | 72.8 | +9.8 | 74.0, 82.3, 79.8, 83.9, 87.8 | 68.7, 88.3, 83.1, 84.2, 88.4 |
| Siena rotations | BIOT | lp_randinit | 80.9 ± 3.3 | 67.4 | +13.5 | 82.1 ± 3.5 | 72.8 | +9.4 | 69.4, 83.3, 78.6, 84.7, 88.5 | 68.7, 86.4, 83.0, 84.0, 88.4 |
| Siena rotations | BIOT | last_noise | 75.2 ± 4.6 | 59.0 | +16.2 | 78.4 ± 3.4 | 69.8 | +8.5 | 75.1, 61.6, 69.5, 82.0, 87.7 | 74.5, 79.8, 67.3, 83.8, 86.5 |
| Siena rotations | CBraMod | lp | 82.6 ± 1.9 | 81.4 | +1.2 | 78.2 ± 2.3 | 78.9 | -0.7 | 81.4, 85.2, 77.3, 80.6, 88.4 | 71.2, 82.6, 75.3, 83.8, 78.1 |
| Siena rotations | CBraMod | last | 82.6 ± 1.7 | 81.7 | +0.9 | 78.5 ± 2.1 | 78.7 | -0.2 | 82.4, 82.4, 77.8, 81.6, 88.7 | 73.6, 83.1, 74.9, 84.0, 76.9 |
| Siena rotations | CBraMod | last_randinit | 74.6 ± 3.3 | 74.0 | +0.6 | 69.1 ± 3.7 | 70.1 | -1.0 | 72.6, 79.0, 62.7, 81.6, 77.1 | 67.4, 74.1, 55.4, 76.5, 72.0 |
| Siena rotations | CBraMod | lp_randinit | 75.2 ± 3.7 | 74.4 | +0.8 | 70.2 ± 3.8 | 70.1 | +0.1 | 74.9, 80.0, 61.3, 81.8, 78.2 | 70.4, 76.8, 55.5, 75.6, 72.6 |
| Siena rotations | CBraMod | last_noise | 82.9 ± 1.8 | 81.8 | +1.1 | 78.8 ± 2.2 | - | - | 83.1, 84.5, 77.8, 80.6, 88.4 | 73.8, 82.3, 74.8, 85.2, 78.1 |
| Siena filtered rotations | BIOT | lp | 79.4 ± 2.7 | 69.8 | +9.7 | 75.1 ± 3.2 | 73.3 | +1.8 | 87.9, 80.3, 75.5, 81.2, 72.3 | 85.8, 78.5, 73.8, 68.8, 68.6 |
| Siena filtered rotations | BIOT | last | 79.4 ± 2.6 | 73.9 | +5.5 | 76.4 ± 3.6 | 75.2 | +1.2 | 87.9, 78.0, 75.6, 82.1, 73.3 | 85.7, 82.7, 74.2, 74.3, 65.2 |
| Siena filtered rotations | BIOT | last_randinit | 82.8 ± 3.8 | 69.2 | +13.6 | 83.8 ± 2.6 | 73.0 | +10.8 | 70.0, 89.2, 79.2, 84.7, 91.1 | 76.9, 87.3, 79.4, 84.7, 90.9 |
| Siena filtered rotations | BIOT | lp_randinit | 84.1 ± 2.8 | 68.8 | +15.3 | 83.9 ± 2.6 | 73.5 | +10.4 | 76.3, 88.7, 79.5, 84.7, 91.1 | 77.0, 87.4, 79.3, 84.7, 91.4 |
| Siena filtered rotations | BIOT | last_noise | 80.6 ± 2.9 | 72.6 | +8.0 | 77.2 ± 3.6 | 74.1 | +3.1 | 88.0, 80.3, 75.4, 86.0, 73.2 | 84.8, 85.6, 74.3, 74.4, 66.6 |
| Siena filtered rotations | CBraMod | lp | 89.7 ± 2.2 | 89.5 | +0.3 | 84.6 ± 2.3 | 82.8 | +1.8 | 91.6, 89.4, 81.9, 90.6, 95.1 | 86.8, 90.3, 76.3, 85.1, 84.4 |
| Siena filtered rotations | CBraMod | last | 89.9 ± 2.1 | 89.6 | +0.2 | 84.5 ± 2.2 | 83.1 | +1.4 | 91.8, 89.6, 82.2, 90.4, 95.3 | 87.5, 89.4, 76.6, 84.2, 84.7 |
| Siena filtered rotations | CBraMod | last_randinit | 80.7 ± 2.1 | 78.9 | +1.7 | 73.9 ± 2.0 | 74.0 | -0.1 | 75.9, 85.2, 76.7, 86.2, 79.5 | 67.8, 75.2, 71.3, 79.2, 76.0 |
| Siena filtered rotations | CBraMod | lp_randinit | 81.5 ± 2.2 | 80.0 | +1.4 | 73.5 ± 1.7 | 74.0 | -0.5 | 76.8, 87.2, 76.1, 84.7, 82.6 | 68.1, 77.3, 71.5, 76.1, 74.3 |
| Siena filtered rotations | CBraMod | last_noise | 89.3 ± 2.1 | 89.6 | -0.3 | 84.4 ± 2.2 | - | - | 89.3, 89.5, 82.3, 90.3, 95.3 | 87.4, 88.4, 76.2, 85.0, 84.9 |

## Fits: early stopping, selected configurations, epochs, grid edges (descriptive)

Stopped early = the stopping rule fired before epoch 500; this does not establish optimization convergence. Epochs 1-based. Edge: lr 3e-5 or 1e-2, or wd 0 or 1 (18 of 30 configurations touch an edge).

| setting | model | variant | fits | stopped early (selected) | stopped early (all 30) | selected epoch median [IQR] (min-max; at epoch <= 2) | epochs run, selected (median, max) | at an edge | lr edge | wd edge | selected lr/wd (count) | test ROC < 50 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DL's split | BIOT | grid | 20 | 20/20 | 600/600 | 32.5 [15, 46] (9-70; 0) | 52.5, 90 | 12/20 | {"lr 1e-2": 10} | {"wd 0": 2} | 0.01/0.1 (10), 0.001/0.0001 (4), 0.0003/0.1 (2), 0.001/0 (2), 0.0003/0.01 (1), 0.001/0.01 (1) | - |
| DL's split | BIOT | grid_z | 20 | 20/20 | 600/600 | 36 [21, 41.5] (9-70; 0) | 56, 90 | 16/20 | {"lr 1e-2": 11} | {"wd 1": 10, "wd 0": 4} | 0.01/1 (9), 0.003/0 (3), 0.01/0.01 (2), 0.001/1 (1), 0.001/0 (1), 0.003/0.1 (1), 0.003/0.0001 (1), 0.001/0.0001 (1), 0.003/0.01 (1) | - |
| DL's split | CBraMod | grid | 20 | 20/20 | 600/600 | 16.5 [10, 19] (6-52; 0) | 36.5, 72 | 15/20 | {"lr 1e-2": 5} | {"wd 1": 13} | 0.001/1 (7), 0.01/1 (3), 0.003/0.1 (3), 0.01/0.1 (2), 0.0003/1 (1), 0.003/0.0001 (1), 0.003/1 (1), 0.0001/1 (1), 0.001/0.01 (1) | - |
| DL's split | CBraMod | grid_z | 20 | 20/20 | 600/600 | 39 [27, 47] (10-88; 0) | 59, 108 | 16/20 | {"lr 3e-5": 13} | {"wd 1": 4, "wd 0": 7} | 3e-05/0.1 (4), 3e-05/1 (4), 3e-05/0 (4), 0.0001/0 (3), 0.0001/0.1 (3), 3e-05/0.01 (1), 0.0001/0.01 (1) | - |
| DL's split, BIOT q95 input | BIOT | grid | 15 | 15/15 | 450/450 | 18 [16, 33] (14-44; 0) | 38, 64 | 15/15 | {"lr 1e-2": 15} | {"wd 0": 3} | 0.01/0.0001 (7), 0.01/0.01 (5), 0.01/0 (3) | - |
| DL's split, BIOT q95 input | BIOT | grid_z | 15 | 15/15 | 450/450 | 16 [16, 25] (3-40; 0) | 36, 60 | 14/15 | {"lr 1e-2": 6} | {"wd 1": 8} | 0.01/0.01 (4), 0.003/1 (3), 0.001/1 (3), 0.0003/1 (2), 0.01/0.1 (2), 0.003/0.1 (1) | - |
| CHB-MIT rotations | BIOT | grid | 75 | 75/75 | 2190/2250 | 24 [13.5, 32] (2-102; 3) | 44, 122 | 70/75 | {"lr 1e-2": 57} | {"wd 1": 21, "wd 0": 10} | 0.01/0.01 (20), 0.01/0.1 (17), 0.01/1 (13), 0.001/1 (6), 0.01/0 (5), 0.003/0.01 (3), 0.0001/0 (2), 0.01/0.0001 (2), 0.003/1 (2), 0.003/0 (2), 0.003/0.0001 (1), 0.003/0.1 (1), 0.001/0 (1) | - |
| CHB-MIT rotations | BIOT | grid_z | 75 | 75/75 | 2250/2250 | 15 [4.5, 30.5] (1-82; 14) | 35, 100 | 73/75 | {"lr 1e-2": 39} | {"wd 1": 50, "wd 0": 12} | 0.01/1 (25), 0.003/1 (16), 0.01/0.1 (6), 0.001/0 (6), 0.001/1 (4), 0.01/0.01 (3), 0.01/0 (3), 0.0001/1 (3), 0.0001/0 (2), 0.0003/0.0001 (2), 0.01/0.0001 (2), 0.0003/1 (2), 0.0003/0 (1) | last_randinit rot2 s1002 43.4; lp_randinit rot2 s1002 43.4 |
| CHB-MIT rotations | CBraMod | grid | 75 | 75/75 | 2223/2250 | 15 [5.5, 25] (1-62; 11) | 35, 82 | 64/75 | {"lr 1e-2": 45, "lr 3e-5": 7} | {"wd 1": 32, "wd 0": 12} | 0.01/1 (22), 0.01/0.1 (15), 3e-05/0 (7), 0.003/0.1 (6), 0.003/1 (5), 0.01/0.0001 (3), 0.001/1 (3), 0.01/0 (3), 0.01/0.01 (2), 0.001/0.1 (2), 0.0001/1 (1), 0.003/0.0001 (1), 0.0003/1 (1), 0.0003/0.1 (1), 0.0003/0 (1), 0.003/0 (1), 0.003/0.01 (1) | - |
| CHB-MIT rotations | CBraMod | grid_z | 75 | 75/75 | 2250/2250 | 26 [15, 38] (5-66; 0) | 46, 86 | 45/75 | {"lr 3e-5": 12, "lr 1e-2": 10} | {"wd 0": 7, "wd 1": 34} | 0.0001/1 (13), 3e-05/1 (10), 0.0003/0.1 (9), 0.01/1 (6), 0.003/0.01 (5), 0.003/0 (3), 0.001/0.0001 (3), 0.003/1 (3), 0.001/0.1 (3), 0.001/0.01 (2), 0.001/0 (2), 0.003/0.0001 (2), 0.0003/1 (2), 3e-05/0.1 (2), 0.01/0 (2), 0.0001/0.1 (2), 0.0003/0.01 (2), 0.01/0.0001 (1), 0.01/0.01 (1), 0.003/0.1 (1), 0.0003/0.0001 (1) | - |
| Siena rotations | BIOT | grid | 75 | 75/75 | 2078/2250 | 44 [24, 116] (3-238; 0) | 64, 258 | 59/75 | {"lr 1e-2": 39, "lr 3e-5": 1} | {"wd 0": 23, "wd 1": 18} | 0.01/0 (15), 0.01/0.0001 (9), 0.003/1 (9), 0.003/0 (6), 0.01/1 (6), 0.01/0.01 (6), 0.003/0.0001 (5), 0.001/0.1 (4), 0.001/1 (3), 0.01/0.1 (3), 0.001/0.0001 (2), 0.0003/0.1 (2), 0.003/0.01 (2), 0.001/0.01 (1), 0.0001/0 (1), 3e-05/0 (1) | - |
| Siena rotations | BIOT | grid_z | 75 | 75/75 | 2194/2250 | 28 [13, 71] (1-233; 2) | 48, 253 | 71/75 | {"lr 1e-2": 39} | {"wd 1": 32, "wd 0": 20} | 0.01/0 (12), 0.01/0.0001 (10), 0.003/1 (10), 0.001/1 (9), 0.01/1 (8), 0.01/0.1 (7), 0.0003/1 (5), 0.003/0 (5), 0.001/0 (3), 0.01/0.01 (2), 0.003/0.0001 (1), 0.001/0.1 (1), 0.0003/0.01 (1), 0.0003/0.0001 (1) | - |
| Siena rotations | CBraMod | grid | 75 | 75/75 | 2250/2250 | 9 [4, 28] (1-58; 7) | 29, 78 | 66/75 | {"lr 1e-2": 26, "lr 3e-5": 1} | {"wd 1": 52, "wd 0": 7} | 0.01/1 (18), 0.001/1 (18), 0.003/1 (12), 0.01/0.1 (7), 0.003/0 (4), 0.003/0.1 (3), 0.003/0.0001 (3), 0.0003/1 (2), 0.001/0.0001 (2), 0.0001/1 (1), 0.0003/0 (1), 0.003/0.01 (1), 3e-05/1 (1), 0.001/0 (1), 0.01/0 (1) | last_randinit rot2 s2021 50.0 |
| Siena rotations | CBraMod | grid_z | 75 | 75/75 | 2250/2250 | 18 [10, 25.5] (3-83; 0) | 38, 103 | 69/75 | {"lr 3e-5": 15, "lr 1e-2": 10} | {"wd 1": 63, "wd 0": 2} | 0.0001/1 (22), 0.0003/1 (16), 3e-05/1 (15), 0.01/1 (5), 0.003/1 (4), 0.003/0.1 (3), 0.01/0.0001 (2), 0.01/0.01 (2), 0.003/0.01 (2), 0.001/1 (1), 0.01/0 (1), 0.003/0.0001 (1), 0.003/0 (1) | last_randinit rot2 s2021 42.3; lp_randinit rot2 s2021 42.3 |
| Siena filtered rotations | BIOT | grid | 75 | 75/75 | 2151/2250 | 34 [19, 79] (1-256; 2) | 54, 276 | 59/75 | {"lr 1e-2": 37, "lr 3e-5": 2} | {"wd 0": 11, "wd 1": 29} | 0.01/1 (18), 0.01/0.1 (11), 0.003/0.01 (7), 0.003/1 (7), 0.003/0 (5), 0.003/0.0001 (5), 0.001/1 (4), 0.001/0 (4), 0.01/0.0001 (3), 0.01/0.01 (3), 0.001/0.0001 (3), 0.01/0 (2), 3e-05/0.1 (1), 3e-05/0.01 (1), 0.001/0.01 (1) | - |
| Siena filtered rotations | BIOT | grid_z | 75 | 75/75 | 2173/2250 | 26 [15, 57] (1-390; 5) | 46, 400 | 66/75 | {"lr 1e-2": 50} | {"wd 0": 17, "wd 1": 34} | 0.01/1 (25), 0.01/0 (10), 0.01/0.1 (8), 0.003/1 (7), 0.01/0.0001 (5), 0.003/0 (5), 0.003/0.0001 (3), 0.01/0.01 (2), 0.001/1 (2), 0.003/0.1 (2), 0.003/0.01 (2), 0.001/0 (2), 0.001/0.01 (1), 0.001/0.0001 (1) | - |
| Siena filtered rotations | CBraMod | grid | 75 | 75/75 | 2250/2250 | 12 [3, 22] (1-61; 18) | 32, 81 | 65/75 | {"lr 1e-2": 26} | {"wd 1": 56, "wd 0": 6} | 0.01/1 (22), 0.003/1 (17), 0.0003/1 (11), 0.001/1 (6), 0.003/0.1 (3), 0.003/0 (2), 0.0003/0 (2), 0.001/0.01 (2), 0.003/0.01 (2), 0.01/0.1 (2), 0.01/0 (1), 0.0003/0.0001 (1), 0.001/0.0001 (1), 0.001/0 (1), 0.003/0.0001 (1), 0.01/0.01 (1) | - |
| Siena filtered rotations | CBraMod | grid_z | 75 | 75/75 | 2250/2250 | 12 [7, 29] (2-64; 3) | 32, 84 | 69/75 | {"lr 1e-2": 3, "lr 3e-5": 23} | {"wd 1": 67, "wd 0": 1} | 0.0001/1 (26), 3e-05/1 (22), 0.0003/1 (11), 0.003/1 (4), 0.003/0.0001 (3), 0.01/1 (2), 0.001/1 (2), 0.001/0.1 (2), 0.01/0.01 (1), 3e-05/0 (1), 0.003/0.1 (1) | - |

## Single-seed differences beyond +-25 (descriptive)

Each arm: selected lr / wd / epoch, val and test ROC-AUC x100 at the selection.

- S1W BIOT grid lp - lp_randinit rot2 s2021: +25.8 (lp lr 0.01 wd 0.01 epoch 31: val 64.9 test 89.8; lp_randinit lr 0.01 wd 0.01 epoch 48: val 71.3 test 64.0)
- S1W BIOT grid lp - lp_randinit rot2 s1002: +38.2 (lp lr 0.003 wd 0 epoch 102: val 64.4 test 88.8; lp_randinit lr 0.01 wd 1 epoch 3: val 77.3 test 50.6)
- S1W BIOT grid_z last_randinit - last rot2 s1002: -41.8 (last_randinit lr 0.01 wd 0.1 epoch 7: val 76.5 test 43.4; last lr 0.0001 wd 1 epoch 3: val 75.2 test 85.2)
- S1W BIOT grid_z last_randinit - last rot2 s2002: -37.9 (last_randinit lr 0.01 wd 1 epoch 11: val 75.4 test 53.5; last lr 0.01 wd 1 epoch 14: val 74.8 test 91.4)
- S1W BIOT grid_z last_randinit - last rot4 s2004: -26.4 (last_randinit lr 0.01 wd 1 epoch 14: val 75.0 test 59.4; last lr 0.001 wd 0 epoch 31: val 67.5 test 85.8)
- S1W BIOT grid_z lp - lp_randinit rot2 s2021: +37.3 (lp lr 0.01 wd 1 epoch 15: val 77.2 test 89.2; lp_randinit lr 0.003 wd 1 epoch 29: val 74.5 test 51.9)
- S1W BIOT grid_z lp - lp_randinit rot2 s1002: +44.6 (lp lr 0.0001 wd 1 epoch 5: val 76.2 test 88.0; lp_randinit lr 0.01 wd 0.1 epoch 7: val 76.6 test 43.4)
- S1W BIOT grid_z lp - lp_randinit rot2 s2002: +37.3 (lp lr 0.01 wd 1 epoch 18: val 75.3 test 90.5; lp_randinit lr 0.01 wd 1 epoch 11: val 75.4 test 53.2)
- S1W BIOT grid_z lp - lp_randinit rot4 s2004: +27.8 (lp lr 0.001 wd 0 epoch 31: val 68.2 test 87.4; lp_randinit lr 0.01 wd 1 epoch 14: val 75.1 test 59.5)
- S3W BIOT grid_z lp - lp_randinit rot2 s1002: -26.1 (lp lr 0.01 wd 0.1 epoch 3: val 81.8 test 57.6; lp_randinit lr 0.003 wd 0 epoch 150: val 89.8 test 83.7)
- S3W CBraMod grid last_randinit - last rot2 s2021: -29.2 (last_randinit lr 0.01 wd 0.1 epoch 13: val 81.4 test 50.0; last lr 0.001 wd 1 epoch 38: val 86.4 test 79.2)
- S3W CBraMod grid lp - lp_randinit rot2 s2021: +25.2 (lp lr 0.0001 wd 1 epoch 50: val 85.3 test 78.1; lp_randinit lr 0.01 wd 1 epoch 42: val 81.1 test 52.9)
- S3W CBraMod grid_z last_randinit - last rot2 s2021: -32.6 (last_randinit lr 3e-05 wd 1 epoch 38: val 77.9 test 42.3; last lr 0.0001 wd 1 epoch 50: val 85.8 test 74.9)
- S3W CBraMod grid_z lp - lp_randinit rot2 s2021: +33.0 (lp lr 0.0001 wd 1 epoch 50: val 84.8 test 75.3; lp_randinit lr 3e-05 wd 1 epoch 38: val 77.9 test 42.3)
- S3FW BIOT grid_z last_randinit - last rot4 s1004: +27.0 (last_randinit lr 0.01 wd 0.0001 epoch 75: val 94.2 test 92.5; last lr 0.01 wd 0.1 epoch 33: val 86.9 test 65.5)
- S3FW BIOT grid_z last_randinit - last rot4 s2004: +29.6 (last_randinit lr 0.01 wd 0 epoch 95: val 93.4 test 91.8; last lr 0.01 wd 0 epoch 1: val 85.6 test 62.2)
- S3FW BIOT grid_z lp - lp_randinit rot3 s1003: -26.5 (lp lr 0.01 wd 1 epoch 35: val 85.7 test 56.5; lp_randinit lr 0.003 wd 0 epoch 128: val 93.5 test 83.0)
- S3FW CBraMod grid last_randinit - last rot4 s2004: -25.1 (last_randinit lr 0.01 wd 0.1 epoch 43: val 80.5 test 70.1; last lr 0.0003 wd 1 epoch 22: val 93.7 test 95.3)

## Figures

- artifacts/figures/f_d31_curves.pdf/png: selected configuration's val ROC-AUC per epoch, per arm, setting, model and variant (the D31 learning-curve figure).
- artifacts/figures/fig_effects_d31.pdf/png: the D31 contrasts with 95% t and Nadeau-Bengio intervals.
