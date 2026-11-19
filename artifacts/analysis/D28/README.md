# D28: probe convergence (tuned, early-stopped linear probes on cached frozen features)

Protocol: notes/decisions.md "## D28", frozen in git (commit c0283f4) before any D28 run; applied as written. Probes: grid (raw features), grid_z (train-standardized); AdamW lr {1e-4, 3e-4, 1e-3, 3e-3} x wd {0, 1e-4, 1e-2, 1e-1} (16 configurations), batch 256, constant lr, BCE, <= 200 epochs, early stop after 20 epochs without a val ROC gain > 1e-4; configuration and epoch selected on val ROC-AUC; test read once there.
Units: rotation means over seeds [S_r, 1000+r, 2000+r] (95% t-interval df 4; Nadeau-Bengio corrected interval with n_test/n_train S1G 0.338, S3G 0.347, S3FG 0.347). DL's split: the 5 seeds 42/123/2021/3407/8888 on one fixed split (**seed uncertainty on one split**, no NB). Labels: **gain demonstrated** (95% t-interval excludes 0 and |mean| > 3 that way), **equivalent within +-3** (TOST margin 3, alpha 0.05 rejects), **not resolved**. D18 = the paired rule (|mean| > 3, same sign in >= 4/5), descriptive consistency criterion. Everything outside the labels and Q1-Q3 is descriptive. ROC-AUC x100.
Reading choices (NB label as sensitivity, Q3 = sign of the mean against D24-A/D24-B and D27-B, edges, 1-based epochs) were fixed before any aggregate; the outlier list, the epoch <= 2 count and the per-model Q3 grouping were added after the first output (descriptive). See the script docstring.

Command: `.venv/bin/python scripts/analysis/d28_read.py`

## Checks

- 505 D28 records (P1G 40, P1QG 15, S1G 150, S3G 150, S3FG 150), 1010 probe fits, 16160 configuration fits; 0 smoke records among them.
- P1G (DL's split): 40 records = 2 model(s) x 4 arms x 5 seeds; 1 per cell, 0 missing, 0 duplicates, 0 smoke; versions adapt 3 / probe 4 / grid 1; probes grid + grid_z; backbone eval, tap encoder, input_norm "", labels upstream; one eval set per split (both models)
  1280 configuration fits checked: grid fields = the frozen D28 search; selected configuration = first argmax of best val (ties among configurations: 13 fits); best_val = max of the logged curve; converged = stopped before epoch 200; early-stop replay on the logged (6-decimal) curves disagrees in 0 fits; non-finite train loss in 0; val ROC re-scored at the selection = best_val within 0e-9
  pairing with the fixed-recipe records of the same (model, arm, split, seed): linear SSL epoch losses identical: 20; linear paired: 40; linear_z SSL step losses identical: 20; linear_z paired: 40 (paired = same eval_hash, test index, val index, test n/prevalence, adapt_spec, arm_spec)
- P1QG (DL's split, BIOT q95 input): 15 records = 1 model(s) x 3 arms x 5 seeds; 1 per cell, 0 missing, 0 duplicates, 0 smoke; versions adapt 3 / probe 4 / grid 1; probes grid + grid_z; backbone eval, tap encoder, input_norm "q95", labels upstream; one eval set per split (both models)
  480 configuration fits checked: grid fields = the frozen D28 search; selected configuration = first argmax of best val (ties among configurations: 0 fits); best_val = max of the logged curve; converged = stopped before epoch 200; early-stop replay on the logged (6-decimal) curves disagrees in 0 fits; non-finite train loss in 0; val ROC re-scored at the selection = best_val within 0e-9
  pairing with the fixed-recipe records of the same (model, arm, split, seed): linear SSL step losses identical: 10; linear paired: 15; linear_z SSL step losses identical: 10; linear_z paired: 15 (paired = same eval_hash, test index, val index, test n/prevalence, adapt_spec, arm_spec)
- S1G (CHB-MIT rotations): 150 records = 2 model(s) x 5 arms x 5 rotations x 3 seeds; 1 per cell, 0 missing, 0 duplicates, 0 smoke; versions adapt 3 / probe 4 / grid 1; probes grid + grid_z; backbone eval, tap encoder, input_norm "", labels overlap; one eval set per split (both models)
  4800 configuration fits checked: grid fields = the frozen D28 search; selected configuration = first argmax of best val (ties among configurations: 20 fits); best_val = max of the logged curve; converged = stopped before epoch 200; early-stop replay on the logged (6-decimal) curves disagrees in 0 fits; non-finite train loss in 0; val ROC re-scored at the selection = best_val within 0e-9
  pairing with the fixed-recipe records of the same (model, arm, split, seed): linear SSL epoch losses identical: 60; linear SSL step losses identical: 15; linear missing: 15; linear paired: 135; linear_z SSL step losses identical: 60; linear_z missing: 30; linear_z paired: 120 (paired = same eval_hash, test index, val index, test n/prevalence, adapt_spec, arm_spec)
- S3G (Siena rotations): 150 records = 2 model(s) x 5 arms x 5 rotations x 3 seeds; 1 per cell, 0 missing, 0 duplicates, 0 smoke; versions adapt 3 / probe 4 / grid 1; probes grid + grid_z; backbone eval, tap encoder, input_norm "", labels overlap; one eval set per split (both models)
  4800 configuration fits checked: grid fields = the frozen D28 search; selected configuration = first argmax of best val (ties among configurations: 9 fits); best_val = max of the logged curve; converged = stopped before epoch 200; early-stop replay on the logged (6-decimal) curves disagrees in 0 fits; non-finite train loss in 0; val ROC re-scored at the selection = best_val within 0e-9
  pairing with the fixed-recipe records of the same (model, arm, split, seed): linear SSL epoch losses identical: 60; linear SSL step losses identical: 30; linear paired: 150; linear_z SSL step losses identical: 75; linear_z missing: 15; linear_z paired: 135 (paired = same eval_hash, test index, val index, test n/prevalence, adapt_spec, arm_spec)
- S3FG (Siena filtered rotations): 150 records = 2 model(s) x 5 arms x 5 rotations x 3 seeds; 1 per cell, 0 missing, 0 duplicates, 0 smoke; versions adapt 3 / probe 4 / grid 1; probes grid + grid_z; backbone eval, tap encoder, input_norm "", labels overlap; one eval set per split (both models)
  4800 configuration fits checked: grid fields = the frozen D28 search; selected configuration = first argmax of best val (ties among configurations: 18 fits); best_val = max of the logged curve; converged = stopped before epoch 200; early-stop replay on the logged (6-decimal) curves disagrees in 0 fits; non-finite train loss in 0; val ROC re-scored at the selection = best_val within 0e-9
  pairing with the fixed-recipe records of the same (model, arm, split, seed): linear SSL epoch losses identical: 60; linear SSL step losses identical: 30; linear paired: 150; linear_z SSL step losses identical: 75; linear_z missing: 15; linear_z paired: 135 (paired = same eval_hash, test index, val index, test n/prevalence, adapt_spec, arm_spec)
- Fixed-recipe contrasts re-derived from the records equal the published values: 48 D24-A/D24-B (raw) and D27-B (standardized) unit vectors (artifacts/analysis/D27B/d27b.json), 9 last - last_noise means (E27, A1, A6; artifacts/analysis/D27/noise.md).

## Answers

- **Q1** (any SA gain last - lp "gain demonstrated" with tuned probes?): **no**. 0 of 18 last - lp readings read "gain demonstrated" in the positive direction; labels: equivalent within +-3 16, not resolved 2.
- **Q2** (BIOT q95, DL's split, last - last_noise "gain demonstrated" with either variant?): **no**. grid: -0.3 [-1.5, +0.9], TOST p 0.002, equivalent within +-3, per seed +0.4, -0.4, -1.9, +0.0, +0.5 (fixed recipe linear +8.6); grid_z: -0.3 [-3.1, +2.5], TOST p 0.027, equivalent within +-3, per seed -0.8, +0.7, -3.8, +2.2, +0.2 (fixed recipe linear_z +0.5)
- **Q3** (pretrained-vs-random contrasts keep their direction vs D24-A / D27-B?): **BIOT 7 of 16 signs flip; CBraMod yes (all signs kept)**. BIOT: 9 of 16 keep the sign of the mean (4 "gain demonstrated" that way); of the 7 fixed-recipe readings with a D18 win, 6 keep the sign and 4 read "gain demonstrated". Sign flips: S1G grid last_randinit - last +0.2 (no difference shown) -> -7.4 (not resolved); S1G grid lp - lp_randinit -2.0 (no difference shown) -> +6.7 (not resolved); S1G grid_z last_randinit - last +0.1 (no difference shown) -> -6.8 (gain demonstrated); S1G grid_z lp - lp_randinit -0.2 (no difference shown) -> +6.8 (gain demonstrated); S3FG grid last_randinit - last -4.7 (second term wins) -> +4.6 (not resolved); S3FG grid lp - lp_randinit +1.0 (no difference shown) -> -4.2 (not resolved); S3FG grid_z last_randinit - last -2.2 (no difference shown) -> +7.9 (not resolved). CBraMod: 16 of 16 keep the sign of the mean (11 "gain demonstrated" that way); of the 16 fixed-recipe readings with a D18 win, 16 keep the sign and 11 read "gain demonstrated".

## Contrasts (registered labels)

| setting | model | variant | contrast | mean | 95% t | NB 95% | TOST p | **label** | label with NB SE | D18 | same sign | per unit (rotation means / seeds) | fixed recipe (mean, 95% t, D18) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DL's split | BIOT | grid | last - lp | -0.1 | [-0.7, +0.6] | - | 0.00012 | **equivalent within +-3** | - | no difference shown | 3/5 | +0.3, +0.0, -0.2, -0.9, +0.4 | linear -0.6 [-3.8, +2.6] no difference shown |
| DL's split | BIOT | grid | last_randinit - last | +14.3 | [+11.0, +17.5] | - | 1.000 | **gain demonstrated** | - | first term wins | 5/5 | +17.8, +12.9, +15.9, +11.2, +13.6 | linear +35.8 [+33.0, +38.5] first term wins |
| DL's split | BIOT | grid | lp - lp_randinit | -14.1 | [-17.9, -10.3] | - | 0.999 | **gain demonstrated** | - | second term wins | 5/5 | -18.3, -12.9, -15.5, -10.1, -13.8 | linear -35.1 [-35.9, -34.3] second term wins |
| DL's split | BIOT | grid_z | last - lp | -0.1 | [-3.1, +3.0] | - | 0.029 | **equivalent within +-3** | - | no difference shown | 4/5 | -0.7, -0.6, -0.7, -2.6, +4.1 | linear_z +0.2 [-2.1, +2.4] no difference shown |
| DL's split | BIOT | grid_z | last_randinit - last | +7.7 | [+5.2, +10.1] | - | 0.997 | **gain demonstrated** | - | first term wins | 5/5 | +10.8, +7.3, +6.5, +8.2, +5.5 | linear_z +9.1 [+4.5, +13.6] first term wins |
| DL's split | BIOT | grid_z | lp - lp_randinit | -7.3 | [-9.5, -5.1] | - | 0.997 | **gain demonstrated** | - | second term wins | 5/5 | -8.8, -6.8, -5.8, -5.5, -9.4 | linear_z -9.3 [-13.3, -5.2] second term wins |
| DL's split | CBraMod | grid | last - lp | -0.5 | [-1.2, +0.2] | - | 0.00031 | **equivalent within +-3** | - | no difference shown | 5/5 | -0.2, -0.1, -1.4, -0.9, -0.2 | linear +0.0 [-0.0, +0.0] no difference shown |
| DL's split | CBraMod | grid | last_randinit - last | -3.1 | [-6.9, +0.7] | - | 0.534 | **not resolved** | - | second term wins | 5/5 | -0.9, -8.4, -3.1, -1.7, -1.5 | linear -8.5 [-9.4, -7.6] second term wins |
| DL's split | CBraMod | grid | lp - lp_randinit | +4.0 | [+1.5, +6.5] | - | 0.837 | **gain demonstrated** | - | first term wins | 5/5 | +3.6, +4.6, +6.8, +3.7, +1.3 | linear +6.4 [+4.4, +8.5] first term wins |
| DL's split | CBraMod | grid_z | last - lp | +0.1 | [-0.1, +0.3] | - | 9e-07 | **equivalent within +-3** | - | no difference shown | 4/5 | +0.1, -0.1, +0.3, +0.3, +0.1 | linear_z +0.2 [-0.0, +0.4] no difference shown |
| DL's split | CBraMod | grid_z | last_randinit - last | -4.7 | [-7.4, -1.9] | - | 0.917 | **gain demonstrated** | - | second term wins | 5/5 | -3.0, -7.4, -5.5, -1.9, -5.4 | linear_z -3.6 [-7.0, -0.2] second term wins |
| DL's split | CBraMod | grid_z | lp - lp_randinit | +4.5 | [+1.7, +7.3] | - | 0.892 | **gain demonstrated** | - | first term wins | 5/5 | +3.0, +7.4, +5.2, +1.5, +5.4 | linear_z +3.4 [+0.0, +6.8] first term wins |
| DL's split, BIOT q95 input | BIOT | grid | last - lp | +0.9 | [-0.1, +1.8] | - | 0.001 | **equivalent within +-3** | - | no difference shown | 5/5 | +1.2, +0.3, +0.3, +0.4, +2.0 | linear +8.8 [+6.8, +10.8] first term wins |
| DL's split, BIOT q95 input | BIOT | grid | last - last_noise | -0.3 | [-1.5, +0.9] | - | 0.002 | **equivalent within +-3** | - | no difference shown | 3/5 | +0.4, -0.4, -1.9, +0.0, +0.5 | linear +8.6 [+5.9, +11.2] first term wins |
| DL's split, BIOT q95 input | BIOT | grid_z | last - lp | +0.6 | [-1.5, +2.8] | - | 0.018 | **equivalent within +-3** | - | no difference shown | 3/5 | -0.1, +0.2, -1.4, +3.2, +1.2 | linear_z +0.6 [-1.6, +2.8] no difference shown |
| DL's split, BIOT q95 input | BIOT | grid_z | last - last_noise | -0.3 | [-3.1, +2.5] | - | 0.027 | **equivalent within +-3** | - | no difference shown | 3/5 | -0.8, +0.7, -3.8, +2.2, +0.2 | linear_z +0.5 [-0.4, +1.3] no difference shown |
| CHB-MIT rotations | BIOT | grid | last - lp | -0.5 | [-1.0, -0.0] | [-1.3, +0.3] | 7.5e-05 | **equivalent within +-3** | equivalent within +-3 | no difference shown | 5/5 | -0.8, -0.1, -0.1, -0.6, -1.0 | linear +1.9 [-1.0, +4.8] no difference shown |
| CHB-MIT rotations | BIOT | grid | last_randinit - last | -7.4 | [-17.2, +2.3] | [-23.5, +8.6] | 0.863 | **not resolved** | not resolved | second term wins | 4/5 | -14.0, -6.1, -9.6, +5.5, -13.1 | linear +0.2 [-16.8, +17.1] no difference shown |
| CHB-MIT rotations | BIOT | grid | lp - lp_randinit | +6.7 | [-3.3, +16.8] | [-9.7, +23.2] | 0.820 | **not resolved** | not resolved | first term wins | 4/5 | +14.5, +3.5, +6.0, -4.7, +14.4 | linear -2.0 [-17.0, +13.1] no difference shown |
| CHB-MIT rotations | BIOT | grid | last - last_noise | -0.4 | [-1.6, +0.8] | [-2.4, +1.6] | 0.002 | **equivalent within +-3** | equivalent within +-3 | no difference shown | 4/5 | -1.4, -0.7, -0.1, -0.9, +1.2 | linear +0.8 [-3.3, +4.9] no difference shown |
| CHB-MIT rotations | BIOT | grid_z | last - lp | -0.4 | [-1.3, +0.5] | [-1.9, +1.1] | 0.00074 | **equivalent within +-3** | equivalent within +-3 | no difference shown | 3/5 | -1.4, +0.2, +0.5, -0.7, -0.5 | linear_z +0.1 [-1.1, +1.3] no difference shown |
| CHB-MIT rotations | BIOT | grid_z | last_randinit - last | -6.8 | [-13.2, -0.5] | [-17.2, +3.6] | 0.916 | **gain demonstrated** | not resolved | second term wins | 4/5 | -6.6, -7.6, -13.2, +1.0, -7.9 | linear_z +0.1 [-14.2, +14.4] no difference shown |
| CHB-MIT rotations | BIOT | grid_z | lp - lp_randinit | +6.8 | [+1.0, +12.7] | [-2.7, +16.4] | 0.929 | **gain demonstrated** | not resolved | first term wins | 4/5 | +6.1, +7.5, +12.7, -0.3, +8.3 | linear_z -0.2 [-14.4, +13.9] no difference shown |
| CHB-MIT rotations | BIOT | grid_z | last - last_noise | -0.2 | [-1.9, +1.5] | [-2.9, +2.6] | 0.005 | **equivalent within +-3** | equivalent within +-3 | no difference shown | 4/5 | -2.1, -0.1, +1.7, -0.1, -0.2 | - |
| CHB-MIT rotations | CBraMod | grid | last - lp | +0.7 | [-0.6, +1.9] | [-1.4, +2.8] | 0.004 | **equivalent within +-3** | equivalent within +-3 | no difference shown | 4/5 | +0.3, -0.3, +0.9, +0.1, +2.4 | linear -0.0 [-0.4, +0.4] no difference shown |
| CHB-MIT rotations | CBraMod | grid | last_randinit - last | -1.8 | [-6.4, +2.8] | [-9.3, +5.7] | 0.255 | **not resolved** | not resolved | no difference shown | 3/5 | -3.6, -4.7, -4.6, +0.3, +3.7 | linear -4.4 [-7.4, -1.4] second term wins |
| CHB-MIT rotations | CBraMod | grid | lp - lp_randinit | +2.5 | [-1.9, +7.0] | [-4.7, +9.8] | 0.391 | **not resolved** | not resolved | no difference shown | 4/5 | +3.2, +7.3, +0.9, +3.6, -2.4 | linear +5.5 [+2.5, +8.4] first term wins |
| CHB-MIT rotations | CBraMod | grid | last - last_noise | +0.3 | [-0.6, +1.2] | [-1.2, +1.8] | 0.00064 | **equivalent within +-3** | equivalent within +-3 | no difference shown | 3/5 | +0.0, +0.5, -0.2, -0.3, +1.5 | - |
| CHB-MIT rotations | CBraMod | grid_z | last - lp | -4.4 | [-10.6, +1.7] | [-14.5, +5.7] | 0.721 | **not resolved** | not resolved | second term wins | 4/5 | -10.4, -0.5, -2.7, +0.6, -9.0 | linear_z +0.4 [-0.6, +1.4] no difference shown |
| CHB-MIT rotations | CBraMod | grid_z | last_randinit - last | -1.9 | [-7.2, +3.5] | [-10.6, +6.9] | 0.293 | **not resolved** | not resolved | no difference shown | 3/5 | -0.3, -9.0, +2.2, -2.3, +0.1 | linear_z -5.6 [-12.4, +1.2] second term wins |
| CHB-MIT rotations | CBraMod | grid_z | lp - lp_randinit | +7.7 | [+1.2, +14.2] | [-3.0, +18.4] | 0.942 | **gain demonstrated** | not resolved | first term wins | 5/5 | +10.6, +11.2, +1.4, +2.7, +12.7 | linear_z +5.2 [-1.5, +12.0] first term wins |
| CHB-MIT rotations | CBraMod | grid_z | last - last_noise | -2.1 | [-4.3, +0.1] | [-5.7, +1.5] | 0.163 | **not resolved** | not resolved | no difference shown | 4/5 | -3.4, +0.0, -4.0, -0.5, -2.6 | - |
| Siena rotations | BIOT | grid | last - lp | +0.2 | [-1.4, +1.8] | [-2.4, +2.8] | 0.004 | **equivalent within +-3** | equivalent within +-3 | no difference shown | 4/5 | -1.9, +0.7, +0.5, +1.6, +0.0 | linear +9.2 [+2.3, +16.2] first term wins |
| Siena rotations | BIOT | grid | last_randinit - last | +5.5 | [-7.3, +18.2] | [-15.6, +26.5] | 0.691 | **not resolved** | not resolved | first term wins | 4/5 | -7.3, +19.5, +11.1, +0.2, +3.9 | linear +7.2 [-11.5, +25.9] no difference shown |
| Siena rotations | BIOT | grid | lp - lp_randinit | -6.4 | [-18.1, +5.2] | [-25.7, +12.8] | 0.771 | **not resolved** | not resolved | second term wins | 4/5 | +4.8, -20.2, -10.4, -2.6, -3.8 | linear -16.1 [-40.7, +8.6] second term wins |
| Siena rotations | BIOT | grid | last - last_noise | -0.4 | [-1.8, +0.9] | [-2.6, +1.7] | 0.003 | **equivalent within +-3** | equivalent within +-3 | no difference shown | 3/5 | +0.6, +0.6, -1.1, -0.5, -1.8 | linear +1.6 [-2.3, +5.5] no difference shown |
| Siena rotations | BIOT | grid_z | last - lp | -0.2 | [-4.6, +4.3] | [-7.5, +7.2] | 0.076 | **not resolved** | not resolved | no difference shown | 3/5 | -0.2, +2.6, -6.3, +1.2, +1.8 | linear_z +1.7 [-0.3, +3.6] no difference shown |
| Siena rotations | BIOT | grid_z | last_randinit - last | +5.9 | [-4.6, +16.4] | [-11.5, +23.2] | 0.754 | **not resolved** | not resolved | first term wins | 4/5 | -2.3, +7.7, +19.5, +0.7, +3.7 | linear_z +2.5 [-4.5, +9.6] no difference shown |
| Siena rotations | BIOT | grid_z | lp - lp_randinit | -4.8 | [-14.1, +4.4] | [-20.1, +10.4] | 0.694 | **not resolved** | not resolved | second term wins | 4/5 | +5.6, -10.3, -13.0, -0.8, -5.6 | linear_z -4.2 [-10.9, +2.5] second term wins |
| Siena rotations | BIOT | grid_z | last - last_noise | -1.2 | [-4.8, +2.3] | [-7.1, +4.6] | 0.121 | **not resolved** | not resolved | no difference shown | 3/5 | -2.7, +2.2, -5.3, +0.4, -0.8 | linear_z +0.4 [-1.2, +2.0] no difference shown |
| Siena rotations | CBraMod | grid | last - lp | +0.4 | [-0.1, +0.9] | [-0.5, +1.3] | 8.8e-05 | **equivalent within +-3** | equivalent within +-3 | no difference shown | 4/5 | +0.9, -0.2, +0.5, +0.6, +0.2 | linear +0.3 [-0.4, +0.9] no difference shown |
| Siena rotations | CBraMod | grid | last_randinit - last | -6.5 | [-12.9, -0.2] | [-17.1, +4.0] | 0.901 | **gain demonstrated** | not resolved | second term wins | 5/5 | -2.4, -5.9, -12.8, -0.9, -10.7 | linear -7.6 [-14.3, -0.9] second term wins |
| Siena rotations | CBraMod | grid | lp - lp_randinit | +6.4 | [-1.8, +14.6] | [-7.2, +20.0] | 0.844 | **not resolved** | not resolved | first term wins | 4/5 | -0.1, +3.9, +14.8, +1.4, +12.1 | linear +7.0 [-2.4, +16.3] first term wins |
| Siena rotations | CBraMod | grid | last - last_noise | +0.1 | [-0.2, +0.3] | [-0.3, +0.4] | 1.5e-06 | **equivalent within +-3** | equivalent within +-3 | no difference shown | 3/5 | -0.0, +0.3, +0.2, -0.1, -0.0 | linear -0.1 [-0.1, -0.0] no difference shown |
| Siena rotations | CBraMod | grid_z | last - lp | +0.6 | [-1.4, +2.6] | [-2.7, +3.9] | 0.014 | **equivalent within +-3** | not resolved | no difference shown | 3/5 | +2.8, -0.7, +0.4, -1.1, +1.5 | linear_z -0.3 [-1.3, +0.7] no difference shown |
| Siena rotations | CBraMod | grid_z | last_randinit - last | -9.9 | [-16.5, -3.3] | [-20.9, +1.0] | 0.978 | **gain demonstrated** | not resolved | second term wins | 5/5 | -7.2, -11.0, -18.8, -6.5, -6.1 | linear_z -8.6 [-16.2, -1.0] second term wins |
| Siena rotations | CBraMod | grid_z | lp - lp_randinit | +8.7 | [+1.0, +16.3] | [-3.9, +21.3] | 0.946 | **gain demonstrated** | not resolved | first term wins | 5/5 | +4.2, +9.5, +18.3, +8.9, +2.5 | linear_z +8.8 [+1.5, +16.2] first term wins |
| Siena rotations | CBraMod | grid_z | last - last_noise | +0.7 | [-1.1, +2.6] | [-2.3, +3.8] | 0.013 | **equivalent within +-3** | not resolved | no difference shown | 3/5 | +0.0, +3.4, +0.3, -0.0, -0.1 | - |
| Siena filtered rotations | BIOT | grid | last - lp | +0.7 | [-1.6, +3.0] | [-3.1, +4.5] | 0.024 | **equivalent within +-3** | not resolved | no difference shown | 3/5 | +3.5, -1.2, -0.1, +1.4, -0.3 | linear +4.1 [+0.1, +8.2] first term wins |
| Siena filtered rotations | BIOT | grid | last_randinit - last | +4.6 | [-10.6, +19.8] | [-20.5, +29.7] | 0.609 | **not resolved** | not resolved | first term wins | 4/5 | -13.8, +11.8, +3.0, +3.2, +18.9 | linear -4.7 [-34.5, +25.1] second term wins |
| Siena filtered rotations | BIOT | grid | lp - lp_randinit | -4.2 | [-18.6, +10.2] | [-28.1, +19.6] | 0.589 | **not resolved** | not resolved | second term wins | 4/5 | +13.5, -9.6, -3.2, -3.9, -18.1 | linear +1.0 [-32.6, +34.6] no difference shown |
| Siena filtered rotations | BIOT | grid | last - last_noise | -0.4 | [-3.0, +2.2] | [-4.7, +3.9] | 0.024 | **equivalent within +-3** | not resolved | no difference shown | 3/5 | +0.3, +2.1, +0.4, -3.4, -1.3 | linear +1.3 [-1.4, +3.9] no difference shown |
| Siena filtered rotations | BIOT | grid_z | last - lp | +0.7 | [-0.8, +2.2] | [-1.8, +3.2] | 0.006 | **equivalent within +-3** | equivalent within +-3 | no difference shown | 4/5 | +0.6, +2.7, -0.4, +0.3, +0.4 | linear_z +1.9 [-1.6, +5.5] no difference shown |
| Siena filtered rotations | BIOT | grid_z | last_randinit - last | +7.9 | [-4.0, +19.8] | [-11.8, +27.6] | 0.843 | **not resolved** | not resolved | first term wins | 4/5 | -0.2, +1.5, +8.9, +5.5, +23.9 | linear_z -2.2 [-18.9, +14.5] no difference shown |
| Siena filtered rotations | BIOT | grid_z | lp - lp_randinit | -9.1 | [-20.0, +1.9] | [-27.2, +9.0] | 0.901 | **not resolved** | not resolved | second term wins | 5/5 | -0.5, -7.3, -7.8, -5.7, -24.0 | linear_z -0.2 [-14.4, +13.9] no difference shown |
| Siena filtered rotations | BIOT | grid_z | last - last_noise | +0.5 | [-0.4, +1.4] | [-1.0, +2.0] | 0.00085 | **equivalent within +-3** | equivalent within +-3 | no difference shown | 4/5 | +1.8, +0.4, -0.0, +0.3, +0.1 | linear_z +1.1 [-1.8, +4.1] no difference shown |
| Siena filtered rotations | CBraMod | grid | last - lp | +0.2 | [+0.1, +0.2] | [+0.1, +0.3] | 1.2e-08 | **equivalent within +-3** | equivalent within +-3 | no difference shown | 5/5 | +0.1, +0.2, +0.2, +0.1, +0.2 | linear +0.1 [-0.0, +0.3] no difference shown |
| Siena filtered rotations | CBraMod | grid | last_randinit - last | -9.4 | [-15.3, -3.6] | [-19.1, +0.3] | 0.981 | **gain demonstrated** | not resolved | second term wins | 5/5 | -14.8, -3.9, -8.9, -6.0, -13.6 | linear -10.7 [-17.0, -4.4] second term wins |
| Siena filtered rotations | CBraMod | grid | lp - lp_randinit | +9.3 | [+2.5, +16.0] | [-1.8, +20.4] | 0.970 | **gain demonstrated** | not resolved | first term wins | 5/5 | +16.3, +3.2, +9.1, +4.9, +12.7 | linear +9.4 [+3.6, +15.3] first term wins |
| Siena filtered rotations | CBraMod | grid | last - last_noise | +0.1 | [-0.2, +0.4] | [-0.4, +0.6] | 7.1e-06 | **equivalent within +-3** | equivalent within +-3 | no difference shown | 3/5 | +0.5, -0.0, -0.1, +0.1, -0.0 | linear -0.0 [-0.0, +0.0] no difference shown |
| Siena filtered rotations | CBraMod | grid_z | last - lp | -1.3 | [-3.4, +0.8] | [-4.8, +2.2] | 0.043 | **equivalent within +-3** | not resolved | no difference shown | 3/5 | +0.0, -2.8, -0.6, +0.2, -3.4 | linear_z +0.3 [-0.2, +0.8] no difference shown |
| Siena filtered rotations | CBraMod | grid_z | last_randinit - last | -8.6 | [-16.9, -0.3] | [-22.3, +5.1] | 0.933 | **gain demonstrated** | not resolved | second term wins | 5/5 | -19.5, -9.9, -4.4, -6.3, -2.8 | linear_z -9.2 [-16.6, -1.7] second term wins |
| Siena filtered rotations | CBraMod | grid_z | lp - lp_randinit | +9.1 | [+1.2, +17.0] | [-4.0, +22.1] | 0.950 | **gain demonstrated** | not resolved | first term wins | 5/5 | +19.0, +11.9, +4.8, +5.9, +3.8 | linear_z +8.8 [+1.4, +16.2] first term wins |
| Siena filtered rotations | CBraMod | grid_z | last - last_noise | -0.8 | [-3.3, +1.7] | [-4.9, +3.3] | 0.034 | **equivalent within +-3** | not resolved | no difference shown | 3/5 | -0.0, -0.0, +0.5, +0.0, -4.3 | - |

## Per seed (rotations: S_r / 1000+r / 2000+r per rotation)

- P1G BIOT grid last - lp: +0.3, +0.0, -0.2, -0.9, +0.4
- P1G BIOT grid last_randinit - last: +17.8, +12.9, +15.9, +11.2, +13.6
- P1G BIOT grid lp - lp_randinit: -18.3, -12.9, -15.5, -10.1, -13.8
- P1G BIOT grid_z last - lp: -0.7, -0.6, -0.7, -2.6, +4.1
- P1G BIOT grid_z last_randinit - last: +10.8, +7.3, +6.5, +8.2, +5.5
- P1G BIOT grid_z lp - lp_randinit: -8.8, -6.8, -5.8, -5.5, -9.4
- P1G CBraMod grid last - lp: -0.2, -0.1, -1.4, -0.9, -0.2
- P1G CBraMod grid last_randinit - last: -0.9, -8.4, -3.1, -1.7, -1.5
- P1G CBraMod grid lp - lp_randinit: +3.6, +4.6, +6.8, +3.7, +1.3
- P1G CBraMod grid_z last - lp: +0.1, -0.1, +0.3, +0.3, +0.1
- P1G CBraMod grid_z last_randinit - last: -3.0, -7.4, -5.5, -1.9, -5.4
- P1G CBraMod grid_z lp - lp_randinit: +3.0, +7.4, +5.2, +1.5, +5.4
- P1QG BIOT grid last - lp: +1.2, +0.3, +0.3, +0.4, +2.0
- P1QG BIOT grid last - last_noise: +0.4, -0.4, -1.9, +0.0, +0.5
- P1QG BIOT grid_z last - lp: -0.1, +0.2, -1.4, +3.2, +1.2
- P1QG BIOT grid_z last - last_noise: -0.8, +0.7, -3.8, +2.2, +0.2
- S1G BIOT grid last - lp: rot0 -0.1/-0.5/-1.6; rot1 +2.1/-2.4/-0.0; rot2 +0.1/-0.5/+0.1; rot3 +0.3/-1.1/-1.1; rot4 -1.2/-0.8/-0.9
- S1G BIOT grid last_randinit - last: rot0 -13.1/-16.8/-12.0; rot1 -7.4/-4.7/-6.0; rot2 -12.1/-7.9/-8.7; rot3 +4.4/+5.7/+6.4; rot4 +5.7/-49.6/+4.6
- S1G BIOT grid lp - lp_randinit: rot0 +13.1/+17.1/+13.3; rot1 +5.2/+7.5/-2.3; rot2 -0.3/+9.4/+8.8; rot3 -4.4/-4.6/-5.2; rot4 -4.5/+51.4/-3.7
- S1G BIOT grid last - last_noise: rot0 +0.2/-1.5/-2.8; rot1 -2.4/+0.5/-0.3; rot2 -0.2/-0.1/-0.1; rot3 -0.1/-1.7/-1.0; rot4 +5.5/-2.7/+0.8
- S1G BIOT grid_z last - lp: rot0 +0.3/-4.4/-0.1; rot1 +0.6/+0.5/-0.7; rot2 +2.9/-3.1/+1.8; rot3 +0.1/-1.4/-0.7; rot4 +0.0/-0.1/-1.5
- S1G BIOT grid_z last_randinit - last: rot0 -14.7/-4.5/-0.5; rot1 -18.5/-3.7/-0.5; rot2 +0.2/-32.2/-7.6; rot3 +1.6/+0.2/+1.3; rot4 -13.6/-10.6/+0.3
- S1G BIOT grid_z lp - lp_randinit: rot0 +9.0/+8.7/+0.6; rot1 +18.0/+3.3/+1.2; rot2 -3.1/+35.3/+5.9; rot3 -1.6/+1.2/-0.6; rot4 +13.5/+10.0/+1.2
- S1G BIOT grid_z last - last_noise: rot0 -0.3/-4.4/-1.6; rot1 -0.3/+0.2/-0.1; rot2 +2.3/+0.6/+2.4; rot3 +0.5/-0.6/-0.3; rot4 +0.3/+0.2/-1.1
- S1G CBraMod grid last - lp: rot0 -0.5/+2.0/-0.6; rot1 -1.3/+1.7/-1.2; rot2 +2.4/+0.6/-0.4; rot3 +0.8/-1.1/+0.5; rot4 -1.3/+1.1/+7.3
- S1G CBraMod grid last_randinit - last: rot0 -0.8/-2.4/-7.6; rot1 +0.3/-12.9/-1.6; rot2 -6.3/-2.6/-4.9; rot3 +0.6/-0.0/+0.2; rot4 +5.5/+7.4/-1.8
- S1G CBraMod grid lp - lp_randinit: rot0 +3.4/+2.9/+3.3; rot1 +5.1/+14.9/+1.9; rot2 -1.1/+1.1/+2.9; rot3 -0.8/+4.8/+6.8; rot4 +3.8/-8.8/-2.2
- S1G CBraMod grid last - last_noise: rot0 -0.0/+0.0/+0.0; rot1 -0.9/+2.5/-0.1; rot2 -0.2/-0.4/-0.1; rot3 +0.2/-1.5/+0.4; rot4 -1.3/-0.6/+6.4
- S1G CBraMod grid_z last - lp: rot0 -21.5/-10.6/+0.9; rot1 -0.6/-0.1/-1.0; rot2 +3.1/+0.2/-11.5; rot3 +4.1/-0.2/-2.2; rot4 -9.6/-7.6/-9.7
- S1G CBraMod grid_z last_randinit - last: rot0 +2.9/+2.2/-5.9; rot1 -4.8/-14.3/-7.9; rot2 +4.6/-5.4/+7.4; rot3 -4.8/-3.7/+1.7; rot4 +11.2/-12.0/+1.1
- S1G CBraMod grid_z lp - lp_randinit: rot0 +18.5/+8.3/+5.0; rot1 +5.4/+15.7/+12.5; rot2 -5.0/+5.1/+4.0; rot3 -0.7/+4.3/+4.5; rot4 -2.0/+17.6/+22.3
- S1G CBraMod grid_z last - last_noise: rot0 -0.1/-10.3/+0.1; rot1 -0.0/+0.1/-0.1; rot2 -10.9/+1.9/-3.1; rot3 +3.2/-4.9/+0.3; rot4 +1.4/+1.7/-11.0
- S3G BIOT grid last - lp: rot0 -3.5/-1.3/-0.8; rot1 -1.4/+2.2/+1.2; rot2 +0.1/+1.2/+0.3; rot3 +1.7/+2.1/+0.9; rot4 +2.1/+0.2/-2.2
- S3G BIOT grid last_randinit - last: rot0 -6.6/-11.2/-4.1; rot1 +18.5/+19.3/+20.6; rot2 +17.0/+11.4/+4.8; rot3 -0.9/+0.4/+1.3; rot4 +1.4/+4.3/+5.9
- S3G BIOT grid lp - lp_randinit: rot0 +4.3/+12.5/-2.4; rot1 -17.1/-21.6/-21.8; rot2 -12.7/-12.6/-5.8; rot3 -1.7/-2.4/-3.6; rot4 -3.8/-4.6/-3.2
- S3G BIOT grid last - last_noise: rot0 +2.5/-0.6/-0.2; rot1 +0.5/+1.1/+0.2; rot2 -1.7/-0.5/-1.2; rot3 -0.9/-0.5/-0.1; rot4 -0.6/-1.0/-3.8
- S3G BIOT grid_z last - lp: rot0 -0.2/-1.1/+0.8; rot1 -0.0/+7.9/-0.1; rot2 -4.5/-14.2/-0.3; rot3 +0.9/+1.8/+1.0; rot4 +2.1/+0.8/+2.6
- S3G BIOT grid_z last_randinit - last: rot0 +3.7/-7.9/-2.6; rot1 +10.3/-1.1/+13.9; rot2 +12.3/+34.3/+11.8; rot3 -0.7/+2.7/+0.2; rot4 +3.0/+5.8/+2.4
- S3G BIOT grid_z lp - lp_randinit: rot0 +3.1/+11.7/+1.8; rot1 -10.3/-6.8/-13.7; rot2 -8.0/-19.7/-11.5; rot3 -0.1/-3.9/+1.5; rot4 -5.1/-6.6/-5.0
- S3G BIOT grid_z last - last_noise: rot0 -7.9/-0.4/+0.2; rot1 -0.2/+7.2/-0.5; rot2 -0.7/-9.5/-5.6; rot3 -0.1/+0.9/+0.4; rot4 -0.5/-1.1/-0.7
- S3G CBraMod grid last - lp: rot0 +1.3/+0.5/+0.9; rot1 +0.6/-0.5/-0.8; rot2 +0.4/+0.4/+0.8; rot3 +0.5/+0.8/+0.6; rot4 +0.3/+0.1/+0.2
- S3G CBraMod grid last_randinit - last: rot0 -1.3/+8.4/-14.4; rot1 -5.1/-11.3/-1.2; rot2 -21.8/-11.9/-4.6; rot3 +1.1/-2.6/-1.1; rot4 -4.9/-6.7/-20.5
- S3G CBraMod grid lp - lp_randinit: rot0 +2.3/-3.6/+1.1; rot1 +2.7/+9.8/-0.7; rot2 +22.0/+16.8/+5.6; rot3 -1.1/+4.5/+0.9; rot4 +10.9/+7.1/+18.2
- S3G CBraMod grid last - last_noise: rot0 -0.1/+0.1/-0.0; rot1 +0.7/+0.1/+0.1; rot2 -0.0/-0.1/+0.8; rot3 -0.1/-0.1/-0.1; rot4 -0.0/-0.0/-0.0
- S3G CBraMod grid_z last - lp: rot0 -1.3/+0.5/+9.3; rot1 +0.2/+0.7/-2.9; rot2 +2.0/-0.9/-0.0; rot3 +0.6/+0.6/-4.7; rot4 +1.5/+2.0/+1.0
- S3G CBraMod grid_z last_randinit - last: rot0 -3.8/-3.6/-14.1; rot1 -12.4/-16.9/-3.8; rot2 -33.9/-17.8/-4.7; rot3 -2.0/-13.7/-3.8; rot4 +1.8/+2.9/-23.1
- S3G CBraMod grid_z lp - lp_randinit: rot0 +4.9/+2.8/+4.8; rot1 +8.2/+14.3/+6.1; rot2 +31.9/+18.5/+4.4; rot3 +1.3/+16.8/+8.5; rot4 -3.4/-9.4/+20.5
- S3G CBraMod grid_z last - last_noise: rot0 +0.1/+0.0/+0.0; rot1 +0.0/+0.1/+10.0; rot2 -0.0/+0.1/+0.9; rot3 -0.0/-0.0/+0.0; rot4 -0.2/-0.0/-0.1
- S3FG BIOT grid last - lp: rot0 +0.3/+5.3/+5.0; rot1 -2.6/-1.9/+1.1; rot2 +0.1/+0.1/-0.4; rot3 +1.8/+3.0/-0.6; rot4 -0.9/-0.6/+0.8
- S3FG BIOT grid last_randinit - last: rot0 -14.5/-17.6/-9.3; rot1 +13.6/+13.1/+8.8; rot2 +2.0/+1.9/+4.9; rot3 -2.2/+7.5/+4.3; rot4 +18.9/+20.6/+17.3
- S3FG BIOT grid lp - lp_randinit: rot0 +13.8/+22.9/+3.9; rot1 -8.7/-10.9/-9.1; rot2 -3.2/-1.6/-4.7; rot3 +0.3/-10.3/-1.6; rot4 -16.9/-19.6/-17.8
- S3FG BIOT grid last - last_noise: rot0 +1.4/-0.1/-0.5; rot1 +1.0/+0.7/+4.6; rot2 +1.2/+0.2/-0.4; rot3 +0.4/-10.6/+0.0; rot4 -2.6/-1.4/-0.1
- S3FG BIOT grid_z last - lp: rot0 +0.9/+1.3/-0.5; rot1 -0.9/+7.2/+2.0; rot2 -0.1/-0.3/-0.9; rot3 +0.4/+0.6/-0.1; rot4 +0.3/+0.3/+0.4
- S3FG BIOT grid_z last_randinit - last: rot0 -2.4/+4.6/-2.8; rot1 +8.2/+5.0/-8.6; rot2 +10.9/+7.5/+8.3; rot3 +9.2/-1.0/+8.5; rot4 +26.5/+23.2/+21.9
- S3FG BIOT grid_z lp - lp_randinit: rot0 +1.4/-6.1/+3.1; rot1 -7.3/-12.1/-2.5; rot2 -10.8/-5.3/-7.4; rot3 -9.3/+0.6/-8.3; rot4 -26.9/-23.5/-21.5
- S3FG BIOT grid_z last - last_noise: rot0 +3.7/+1.1/+0.6; rot1 +0.3/+0.4/+0.6; rot2 -0.2/-0.2/+0.3; rot3 +0.4/+0.2/+0.3; rot4 -0.9/-1.3/+2.4
- S3FG CBraMod grid last - lp: rot0 -0.4/+0.2/+0.6; rot1 -0.2/+0.5/+0.3; rot2 +0.3/+0.0/+0.4; rot3 +0.2/+0.2/-0.0; rot4 +0.2/+0.2/+0.2
- S3FG CBraMod grid last_randinit - last: rot0 -16.1/-12.5/-15.7; rot1 -5.3/-2.3/-4.0; rot2 -9.9/-0.8/-16.0; rot3 -4.4/-4.2/-9.4; rot4 -13.5/-10.1/-17.3
- S3FG CBraMod grid lp - lp_randinit: rot0 +17.1/+15.3/+16.6; rot1 +3.1/+2.7/+3.9; rot2 +10.5/+1.1/+15.7; rot3 +4.7/+6.0/+4.1; rot4 +8.8/+10.7/+18.7
- S3FG CBraMod grid last - last_noise: rot0 -0.0/-0.0/+1.7; rot1 -0.0/-0.0/-0.0; rot2 -0.1/-0.1/-0.0; rot3 +0.2/+0.0/+0.0; rot4 -0.0/-0.0/+0.0
- S3FG CBraMod grid_z last - lp: rot0 +0.3/+0.3/-0.4; rot1 -1.0/-5.9/-1.4; rot2 -1.1/-0.4/-0.3; rot3 -0.2/+0.3/+0.5; rot4 +1.0/-11.0/-0.3
- S3FG CBraMod grid_z last_randinit - last: rot0 -22.3/-14.1/-22.3; rot1 -9.5/-14.6/-5.6; rot2 -7.8/+1.4/-6.8; rot3 -3.5/-6.6/-8.9; rot4 +1.1/+7.8/-17.3
- S3FG CBraMod grid_z lp - lp_randinit: rot0 +21.0/+13.3/+22.6; rot1 +10.4/+20.1/+5.1; rot2 +8.9/-1.1/+6.6; rot3 +3.7/+6.0/+8.1; rot4 -2.2/+3.4/+10.3
- S3FG CBraMod grid_z last - last_noise: rot0 -0.0/-0.0/-0.0; rot1 -0.0/-0.0/-0.0; rot2 +1.3/+0.1/+0.1; rot3 +0.0/-0.0/+0.0; rot4 -0.2/-12.6/-0.2

## Absolute test ROC-AUC per arm: tuned vs fixed recipe (same seeds)

| setting | model | arm | grid | linear (fixed) | grid - linear | grid_z | linear_z (fixed) | grid_z - linear_z | grid per unit | grid_z per unit |
|---|---|---|---|---|---|---|---|---|---|---|
| DL's split | BIOT | lp | 74.6 ± 1.4 | 55.0 | +19.6 | 81.9 ± 0.9 | 79.1 | +2.8 | 70.3, 76.7, 73.5, 78.2, 74.4 | 80.5, 83.1, 83.4, 83.8, 78.9 |
| DL's split | BIOT | last | 74.5 ± 1.2 | 54.4 | +20.1 | 81.8 ± 0.6 | 79.3 | +2.5 | 70.6, 76.7, 73.3, 77.2, 74.8 | 79.8, 82.5, 82.7, 81.2, 83.0 |
| DL's split | BIOT | last_randinit | 88.8 ± 0.3 | 90.2 | -1.4 | 89.5 ± 0.4 | 88.4 | +1.1 | 88.4, 89.6, 89.2, 88.4, 88.4 | 90.6, 89.8, 89.1, 89.4, 88.5 |
| DL's split | BIOT | lp_randinit | 88.7 ± 0.3 | 90.1 | -1.4 | 89.2 ± 0.2 | 88.4 | +0.8 | 88.7, 89.6, 89.0, 88.3, 88.2 | 89.3, 89.8, 89.2, 89.3, 88.4 |
| DL's split | CBraMod | lp | 90.7 ± 0.4 | 92.0 | -1.3 | 88.8 ± 0.3 | 88.5 | +0.4 | 89.8, 91.0, 92.0, 90.6, 90.4 | 89.5, 89.2, 87.8, 89.0, 88.6 |
| DL's split | CBraMod | last | 90.2 ± 0.3 | 92.0 | -1.8 | 88.9 ± 0.3 | 88.6 | +0.3 | 89.6, 90.9, 90.6, 89.7, 90.2 | 89.6, 89.1, 88.1, 89.2, 88.7 |
| DL's split | CBraMod | last_randinit | 87.1 ± 1.2 | 83.5 | +3.6 | 84.3 ± 1.1 | 85.0 | -0.8 | 88.7, 82.5, 87.5, 88.0, 88.7 | 86.5, 81.7, 82.6, 87.4, 83.2 |
| DL's split | CBraMod | lp_randinit | 86.8 ± 0.6 | 85.6 | +1.2 | 84.3 ± 1.1 | 85.1 | -0.8 | 86.2, 86.4, 85.2, 86.9, 89.1 | 86.5, 81.8, 82.6, 87.4, 83.2 |
| DL's split, BIOT q95 input | BIOT | lp | 72.4 ± 0.2 | 33.1 | +39.4 | 73.6 ± 0.8 | 70.2 | +3.3 | 72.0, 73.2, 71.9, 72.8, 72.2 | 74.8, 72.9, 71.2, 73.2, 75.7 |
| DL's split, BIOT q95 input | BIOT | last | 73.3 ± 0.3 | 41.9 | +31.4 | 74.2 ± 1.3 | 70.8 | +3.3 | 73.2, 73.5, 72.2, 73.2, 74.3 | 74.7, 73.1, 69.8, 76.4, 76.9 |
| DL's split, BIOT q95 input | BIOT | last_noise | 73.6 ± 0.2 | 33.3 | +40.3 | 74.5 ± 0.7 | 70.4 | +4.1 | 72.8, 73.9, 74.1, 73.2, 73.8 | 75.4, 72.4, 73.6, 74.2, 76.7 |
| CHB-MIT rotations | BIOT | lp | 76.2 ± 5.2 | 65.1 | +11.1 | 76.5 ± 5.9 | 72.3 | +4.2 | 68.8, 76.4, 88.8, 60.7, 86.1 | 60.3, 83.9, 87.3, 64.0, 86.9 |
| CHB-MIT rotations | BIOT | last | 75.6 ± 5.3 | 67.0 | +8.7 | 76.1 ± 6.2 | 72.4 | +3.7 | 68.1, 76.3, 88.7, 60.1, 85.1 | 58.9, 84.0, 87.8, 63.3, 86.4 |
| CHB-MIT rotations | BIOT | last_randinit | 68.2 ± 4.1 | 67.1 | +1.1 | 69.2 ± 4.9 | 72.5 | -3.2 | 54.1, 70.3, 79.1, 65.6, 72.0 | 52.4, 76.5, 74.6, 64.3, 78.5 |
| CHB-MIT rotations | BIOT | lp_randinit | 69.4 ± 4.7 | 67.0 | +2.4 | 69.6 ± 4.6 | 72.5 | -2.9 | 54.3, 73.0, 82.8, 65.4, 71.7 | 54.2, 76.4, 74.6, 64.3, 78.7 |
| CHB-MIT rotations | BIOT | last_noise | 76.0 ± 5.0 | 66.2 | +9.9 | 76.3 ± 5.8 | - | - | 69.4, 77.0, 88.8, 61.0, 83.9 | 61.1, 84.1, 86.1, 63.4, 86.6 |
| CHB-MIT rotations | CBraMod | lp | 78.0 ± 3.6 | 81.6 | -3.6 | 79.2 ± 3.7 | 79.3 | -0.1 | 69.4, 85.7, 86.8, 71.5, 76.6 | 76.2, 86.0, 83.7, 66.2, 84.0 |
| CHB-MIT rotations | CBraMod | last | 78.7 ± 3.6 | 81.6 | -3.0 | 74.8 ± 3.9 | 79.7 | -4.9 | 69.7, 85.4, 87.7, 71.6, 78.9 | 65.8, 85.5, 80.9, 66.8, 75.0 |
| CHB-MIT rotations | CBraMod | last_randinit | 76.9 ± 3.4 | 77.2 | -0.3 | 73.0 ± 3.5 | 74.1 | -1.2 | 66.1, 80.7, 83.0, 71.8, 82.6 | 65.5, 76.5, 83.2, 64.5, 75.1 |
| CHB-MIT rotations | CBraMod | lp_randinit | 75.5 ± 3.7 | 76.2 | -0.7 | 71.5 ± 3.4 | 74.1 | -2.6 | 66.2, 78.3, 85.9, 68.0, 78.9 | 65.6, 74.8, 82.3, 63.5, 71.3 |
| CHB-MIT rotations | CBraMod | last_noise | 78.4 ± 3.5 | - | - | 76.9 ± 3.8 | - | - | 69.7, 84.9, 87.9, 71.9, 77.4 | 69.3, 85.5, 85.0, 67.3, 77.6 |
| Siena rotations | BIOT | lp | 75.4 ± 4.9 | 51.3 | +24.0 | 77.3 ± 2.7 | 68.6 | +8.7 | 82.1, 59.8, 68.2, 82.1, 84.6 | 74.4, 76.8, 69.2, 83.1, 83.1 |
| Siena rotations | BIOT | last | 75.6 ± 4.7 | 60.6 | +15.0 | 77.1 ± 4.1 | 70.2 | +6.9 | 80.2, 60.4, 68.7, 83.7, 84.7 | 74.2, 79.4, 62.9, 84.3, 85.0 |
| Siena rotations | BIOT | last_randinit | 81.0 ± 2.6 | 67.8 | +13.3 | 83.0 ± 3.0 | 72.8 | +10.2 | 73.0, 79.9, 79.8, 83.9, 88.6 | 71.9, 87.1, 82.3, 85.0, 88.7 |
| Siena rotations | BIOT | lp_randinit | 81.8 ± 2.1 | 67.4 | +14.4 | 82.1 ± 3.5 | 72.8 | +9.4 | 77.3, 79.9, 78.6, 84.7, 88.5 | 68.8, 87.1, 82.2, 83.9, 88.7 |
| Siena rotations | BIOT | last_noise | 76.0 ± 4.9 | 59.0 | +17.0 | 78.4 ± 3.1 | 69.8 | +8.5 | 79.7, 59.8, 69.9, 84.2, 86.5 | 76.9, 77.3, 68.1, 83.9, 85.7 |
| Siena rotations | CBraMod | lp | 81.9 ± 2.2 | 81.4 | +0.5 | 79.4 ± 2.7 | 78.9 | +0.5 | 76.4, 84.2, 77.9, 82.6, 88.6 | 74.9, 87.7, 74.3, 84.2, 75.8 |
| Siena rotations | CBraMod | last | 82.3 ± 2.1 | 81.7 | +0.7 | 80.0 ± 2.2 | 78.7 | +1.3 | 77.3, 83.9, 78.4, 83.3, 88.8 | 77.8, 87.1, 74.7, 83.0, 77.3 |
| Siena rotations | CBraMod | last_randinit | 75.8 ± 2.8 | 74.0 | +1.7 | 70.0 ± 3.7 | 70.1 | -0.0 | 74.9, 78.0, 65.6, 82.4, 78.1 | 70.6, 76.1, 55.9, 76.5, 71.1 |
| Siena rotations | CBraMod | lp_randinit | 75.5 ± 3.2 | 74.4 | +1.1 | 70.7 ± 3.9 | 70.1 | +0.6 | 76.5, 80.2, 63.1, 81.2, 76.5 | 70.8, 78.2, 56.0, 75.3, 73.2 |
| Siena rotations | CBraMod | last_noise | 82.3 ± 2.1 | 81.8 | +0.5 | 79.2 ± 1.8 | - | - | 77.3, 83.7, 78.2, 83.4, 88.8 | 77.7, 83.7, 74.4, 83.1, 77.4 |
| Siena filtered rotations | BIOT | lp | 78.6 ± 2.3 | 69.8 | +8.8 | 76.3 ± 2.4 | 73.3 | +3.0 | 86.3, 76.0, 76.3, 81.2, 73.3 | 78.5, 82.2, 74.4, 78.5, 68.0 |
| Siena filtered rotations | BIOT | last | 79.3 ± 3.1 | 73.9 | +5.4 | 77.0 ± 2.8 | 75.2 | +1.8 | 89.8, 74.8, 76.2, 82.6, 73.0 | 79.1, 84.9, 73.9, 78.8, 68.3 |
| Siena filtered rotations | BIOT | last_randinit | 83.9 ± 2.8 | 69.2 | +14.7 | 84.9 ± 2.2 | 73.0 | +11.9 | 76.1, 86.6, 79.2, 85.8, 91.9 | 78.9, 86.4, 82.9, 84.4, 92.2 |
| Siena filtered rotations | BIOT | lp_randinit | 82.8 ± 3.1 | 68.8 | +14.0 | 85.4 ± 2.4 | 73.5 | +11.9 | 72.8, 85.6, 79.5, 85.0, 91.4 | 79.1, 89.5, 82.2, 84.2, 91.9 |
| Siena filtered rotations | BIOT | last_noise | 79.7 ± 3.4 | 72.6 | +7.1 | 76.5 ± 2.7 | 74.1 | +2.4 | 89.5, 72.7, 75.9, 86.0, 74.3 | 77.3, 84.5, 74.0, 78.5, 68.2 |
| Siena filtered rotations | CBraMod | lp | 89.7 ± 2.1 | 89.5 | +0.2 | 84.1 ± 2.4 | 82.8 | +1.3 | 92.2, 88.5, 82.4, 90.7, 94.9 | 86.6, 90.4, 75.9, 84.4, 83.3 |
| Siena filtered rotations | CBraMod | last | 89.9 ± 2.1 | 89.6 | +0.3 | 82.8 ± 2.3 | 83.1 | -0.3 | 92.3, 88.7, 82.7, 90.8, 95.1 | 86.7, 87.6, 75.4, 84.6, 79.8 |
| Siena filtered rotations | CBraMod | last_randinit | 80.5 ± 2.2 | 78.9 | +1.6 | 74.2 ± 2.2 | 74.0 | +0.3 | 77.6, 84.8, 73.7, 84.8, 81.5 | 67.1, 77.8, 71.0, 78.3, 77.1 |
| Siena filtered rotations | CBraMod | lp_randinit | 80.5 ± 2.5 | 80.0 | +0.4 | 75.0 ± 2.4 | 74.0 | +1.0 | 75.9, 85.2, 73.3, 85.7, 82.2 | 67.6, 78.5, 71.1, 78.5, 79.4 |
| Siena filtered rotations | CBraMod | last_noise | 89.8 ± 2.1 | 89.6 | +0.2 | 83.6 ± 2.3 | - | - | 91.8, 88.7, 82.7, 90.7, 95.1 | 86.7, 87.7, 74.9, 84.6, 84.2 |

## Fits: convergence, selected configurations, epochs, grid edges (descriptive)

Converged = early stopping fired before epoch 200. Epochs 1-based. Edge: lr 1e-4 or 3e-3, or wd 0 or 1e-1 (12 of 16 configurations touch an edge).

| setting | model | variant | fits | converged (selected) | converged (all 16) | selected epoch median [IQR] (min-max; at epoch <= 2) | epochs run, selected (median, max) | at an edge | lr edge | wd edge | selected lr/wd (count) | test ROC < 50 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DL's split | BIOT | grid | 20 | 20/20 | 318/320 | 34.5 [17, 46] (15-70; 0) | 54.5, 90 | 14/20 | {"lr 3e-3": 10} | {"wd 1e-1": 12, "wd 0": 2} | 0.003/0.1 (10), 0.001/0.0001 (4), 0.001/0 (2), 0.0003/0.1 (2), 0.0003/0.01 (1), 0.001/0.01 (1) | - |
| DL's split | BIOT | grid_z | 20 | 20/20 | 308/320 | 37 [24, 61] (4-70; 0) | 57, 90 | 19/20 | {"lr 1e-4": 4, "lr 3e-3": 11} | {"wd 0": 11, "wd 1e-1": 5} | 0.003/0 (5), 0.0001/0 (4), 0.003/0.1 (3), 0.0003/0.1 (2), 0.003/0.01 (2), 0.0003/0 (1), 0.003/0.0001 (1), 0.001/0 (1), 0.001/0.0001 (1) | - |
| DL's split | CBraMod | grid | 20 | 20/20 | 320/320 | 14 [9.75, 18.25] (1-37; 1) | 34, 57 | 17/20 | {"lr 3e-3": 15, "lr 1e-4": 1} | {"wd 1e-1": 16} | 0.003/0.1 (14), 0.0003/0.0001 (1), 0.003/0.0001 (1), 0.001/0.01 (1), 0.0003/0.1 (1), 0.0003/0.01 (1), 0.0001/0.1 (1) | - |
| DL's split | CBraMod | grid_z | 20 | 20/20 | 320/320 | 36 [31, 39] (21-55; 0) | 56, 75 | 20/20 | {"lr 1e-4": 20} | {"wd 1e-1": 10, "wd 0": 9} | 0.0001/0.1 (10), 0.0001/0 (9), 0.0001/0.01 (1) | - |
| DL's split, BIOT q95 input | BIOT | grid | 15 | 15/15 | 188/240 | 33 [33, 55] (20-78; 0) | 53, 98 | 15/15 | {"lr 3e-3": 15} | {"wd 0": 12} | 0.003/0 (12), 0.003/0.01 (2), 0.003/0.0001 (1) | - |
| DL's split, BIOT q95 input | BIOT | grid_z | 15 | 15/15 | 240/240 | 16 [5.5, 19] (1-33; 1) | 36, 53 | 15/15 | {"lr 3e-3": 15} | {"wd 0": 4, "wd 1e-1": 4} | 0.003/0.01 (5), 0.003/0 (4), 0.003/0.1 (4), 0.003/0.0001 (2) | - |
| CHB-MIT rotations | BIOT | grid | 75 | 75/75 | 1106/1200 | 29 [7, 54] (2-164; 3) | 49, 184 | 74/75 | {"lr 3e-3": 52, "lr 1e-4": 6} | {"wd 1e-1": 32, "wd 0": 18} | 0.003/0.1 (19), 0.003/0.01 (17), 0.001/0.1 (9), 0.003/0 (9), 0.003/0.0001 (7), 0.0001/0 (6), 0.0003/0.1 (4), 0.001/0 (3), 0.001/0.01 (1) | last_randinit rot4 s1004 34.9; lp_randinit rot4 s1004 33.9 |
| CHB-MIT rotations | BIOT | grid_z | 75 | 75/75 | 1196/1200 | 10 [3, 29] (1-82; 17) | 30, 100 | 70/75 | {"lr 3e-3": 36, "lr 1e-4": 12} | {"wd 0": 19, "wd 1e-1": 47} | 0.003/0.1 (26), 0.001/0.1 (11), 0.0001/0.1 (8), 0.003/0 (6), 0.001/0 (6), 0.0003/0.0001 (5), 0.003/0.01 (4), 0.0001/0 (4), 0.0003/0 (3), 0.0003/0.1 (2) | last_randinit rot0 s42 49.7 |
| CHB-MIT rotations | CBraMod | grid | 75 | 75/75 | 1171/1200 | 7 [3, 19.5] (1-43; 18) | 27, 63 | 68/75 | {"lr 3e-3": 47, "lr 1e-4": 12} | {"wd 0": 20, "wd 1e-1": 32} | 0.003/0.1 (22), 0.003/0 (9), 0.003/0.01 (9), 0.0001/0 (9), 0.001/0.1 (7), 0.003/0.0001 (7), 0.001/0.01 (4), 0.0003/0.01 (3), 0.0001/0.1 (3), 0.0003/0 (1), 0.001/0 (1) | - |
| CHB-MIT rotations | CBraMod | grid_z | 75 | 75/75 | 1200/1200 | 16 [11, 33.5] (1-85; 3) | 36, 105 | 62/75 | {"lr 3e-3": 14, "lr 1e-4": 25} | {"wd 0": 9, "wd 1e-1": 46} | 0.0001/0.1 (23), 0.0003/0.1 (13), 0.003/0.1 (6), 0.001/0.01 (5), 0.001/0.1 (4), 0.003/0 (3), 0.001/0.0001 (3), 0.0003/0 (3), 0.003/0.01 (3), 0.0003/0.01 (3), 0.001/0 (3), 0.003/0.0001 (2), 0.0001/0.01 (2), 0.0003/0.0001 (2) | - |
| Siena rotations | BIOT | grid | 75 | 67/75 | 902/1200 | 60 [26, 116] (5-200; 0) | 80, 200 | 71/75 | {"lr 3e-3": 56, "lr 1e-4": 2} | {"wd 0": 35, "wd 1e-1": 22} | 0.003/0 (32), 0.003/0.1 (11), 0.003/0.0001 (8), 0.001/0.1 (7), 0.003/0.01 (5), 0.0003/0.1 (4), 0.001/0.01 (2), 0.001/0 (2), 0.001/0.0001 (2), 0.0001/0.01 (1), 0.0001/0 (1) | - |
| Siena rotations | BIOT | grid_z | 75 | 68/75 | 1079/1200 | 49 [6, 93] (1-200; 3) | 69, 200 | 72/75 | {"lr 3e-3": 50} | {"wd 0": 27, "wd 1e-1": 29} | 0.003/0 (23), 0.003/0.1 (11), 0.0003/0.1 (10), 0.003/0.0001 (9), 0.001/0.1 (8), 0.003/0.01 (7), 0.001/0 (3), 0.0003/0.0001 (2), 0.0003/0 (1), 0.0003/0.01 (1) | last rot2 s1002 49.9 |
| Siena rotations | CBraMod | grid | 75 | 75/75 | 1200/1200 | 8 [3, 23] (1-76; 14) | 28, 96 | 70/75 | {"lr 3e-3": 24, "lr 1e-4": 17} | {"wd 0": 14, "wd 1e-1": 47} | 0.0001/0.1 (15), 0.0003/0.1 (14), 0.001/0.1 (11), 0.003/0 (10), 0.003/0.1 (7), 0.003/0.01 (4), 0.001/0.01 (3), 0.0003/0 (3), 0.003/0.0001 (3), 0.0001/0.01 (2), 0.001/0.0001 (2), 0.001/0 (1) | - |
| Siena rotations | CBraMod | grid_z | 75 | 75/75 | 1200/1200 | 11 [7, 22] (1-83; 1) | 31, 103 | 74/75 | {"lr 1e-4": 41, "lr 3e-3": 13} | {"wd 1e-1": 65, "wd 0": 4} | 0.0001/0.1 (40), 0.0003/0.1 (18), 0.003/0.1 (6), 0.003/0.01 (3), 0.003/0 (3), 0.0003/0.01 (1), 0.0003/0 (1), 0.003/0.0001 (1), 0.001/0.1 (1), 0.0001/0.01 (1) | last_randinit rot2 s2021 40.8; lp_randinit rot2 s2021 40.8 |
| Siena filtered rotations | BIOT | grid | 75 | 70/75 | 1021/1200 | 38 [14.5, 84.5] (1-189; 4) | 58, 200 | 69/75 | {"lr 3e-3": 52, "lr 1e-4": 4} | {"wd 0": 23, "wd 1e-1": 25} | 0.003/0 (16), 0.003/0.1 (16), 0.003/0.0001 (11), 0.003/0.01 (9), 0.001/0 (6), 0.001/0.0001 (5), 0.001/0.1 (5), 0.0001/0.1 (3), 0.0003/0 (1), 0.0001/0.01 (1), 0.001/0.01 (1), 0.0003/0.1 (1) | - |
| Siena filtered rotations | BIOT | grid_z | 75 | 71/75 | 1032/1200 | 25 [5.5, 81] (1-197; 12) | 45, 200 | 73/75 | {"lr 3e-3": 50, "lr 1e-4": 3} | {"wd 0": 27, "wd 1e-1": 31} | 0.003/0 (19), 0.003/0.1 (17), 0.003/0.0001 (10), 0.001/0.1 (10), 0.001/0 (5), 0.003/0.01 (4), 0.0003/0.1 (4), 0.0001/0 (2), 0.001/0.01 (2), 0.0003/0 (1), 0.0001/0.01 (1) | - |
| Siena filtered rotations | CBraMod | grid | 75 | 75/75 | 1200/1200 | 5 [2, 14] (1-50; 25) | 25, 70 | 66/75 | {"lr 3e-3": 32, "lr 1e-4": 2} | {"wd 1e-1": 34, "wd 0": 18} | 0.003/0.1 (12), 0.0003/0.1 (11), 0.001/0.1 (9), 0.001/0 (8), 0.003/0.01 (8), 0.003/0 (6), 0.003/0.0001 (6), 0.0003/0 (4), 0.001/0.0001 (4), 0.0003/0.0001 (2), 0.0001/0.1 (2), 0.001/0.01 (2), 0.0003/0.01 (1) | - |
| Siena filtered rotations | CBraMod | grid_z | 75 | 75/75 | 1200/1200 | 7 [4, 19] (1-53; 5) | 27, 73 | 75/75 | {"lr 1e-4": 49, "lr 3e-3": 6} | {"wd 1e-1": 66, "wd 0": 5} | 0.0001/0.1 (43), 0.0003/0.1 (14), 0.001/0.1 (6), 0.0001/0 (5), 0.003/0.0001 (3), 0.003/0.1 (3), 0.0001/0.01 (1) | - |

## Single-seed differences beyond +-25 (descriptive)

Each arm: selected lr / wd / epoch, val and test ROC-AUC x100 at the selection.

- S1G BIOT grid last_randinit - last rot4 s1004: -49.6 (last_randinit lr 0.0001 wd 0 epoch 2: val 67.8 test 34.9; last lr 0.003 wd 0.1 epoch 79: val 66.0 test 84.5)
- S1G BIOT grid lp - lp_randinit rot4 s1004: +51.4 (lp lr 0.003 wd 0.1 epoch 79: val 67.3 test 85.4; lp_randinit lr 0.0001 wd 0 epoch 2: val 67.8 test 33.9)
- S1G BIOT grid_z last_randinit - last rot2 s1002: -32.2 (last_randinit lr 0.003 wd 0.1 epoch 3: val 73.9 test 50.8; last lr 0.0001 wd 0.1 epoch 3: val 74.4 test 83.0)
- S1G BIOT grid_z lp - lp_randinit rot2 s1002: +35.3 (lp lr 0.0001 wd 0.1 epoch 5: val 75.6 test 86.1; lp_randinit lr 0.003 wd 0.1 epoch 3: val 73.9 test 50.9)
- S3G BIOT grid_z last_randinit - last rot2 s1002: +34.3 (last_randinit lr 0.003 wd 0 epoch 150: val 89.7 test 84.2; last lr 0.003 wd 0.0001 epoch 5: val 80.8 test 49.9)
- S3G CBraMod grid_z last_randinit - last rot2 s2021: -33.9 (last_randinit lr 0.0001 wd 0.1 epoch 41: val 76.1 test 40.8; last lr 0.0001 wd 0.1 epoch 50: val 85.2 test 74.7)
- S3G CBraMod grid_z lp - lp_randinit rot2 s2021: +31.9 (lp lr 0.001 wd 0.1 epoch 27: val 84.5 test 72.7; lp_randinit lr 0.0001 wd 0.1 epoch 41: val 76.2 test 40.8)
- S3FG BIOT grid_z last_randinit - last rot4 s8888: +26.5 (last_randinit lr 0.003 wd 0 epoch 130: val 91.0 test 92.5; last lr 0.003 wd 0 epoch 2: val 83.1 test 66.0)
- S3FG BIOT grid_z lp - lp_randinit rot4 s8888: -26.9 (lp lr 0.003 wd 0.0001 epoch 2: val 83.4 test 65.6; lp_randinit lr 0.003 wd 0 epoch 130: val 91.1 test 92.5)

## Figures

- artifacts/figures/f_d28_curves.pdf/png: selected configuration's val ROC-AUC per epoch, per arm, setting, model and variant (the D28 learning-curve figure).
- artifacts/figures/fig_effects_d28.pdf/png: the D28 contrasts with 95% t and Nadeau-Bengio intervals.
