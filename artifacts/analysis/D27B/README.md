# D27-B: standardized head (`linear_z`) at 3 seeds per rotation, co-primary with the raw head

Rule (notes/decisions.md "## D27", item B, written before the runs): D24 rules on 3-seed means (per-rotation means over S_r / 1000+r / 2000+r; D18 paired rule |mean| > 3 and same sign in >= 4/5; D17) on last - lp, last_randinit - last, lp - lp_randinit. A conclusion **holds** only if the raw head (D24-A: S1E+S1M, S3E+S3M, S3FE+S3FM, linear) and the standardized head agree (same verdict string), else it is **head-dependent**. P1Z (paper split, 5 seeds) by D24-B on last - lp, against P1E linear; other paper-split contrasts descriptive.
ROC-AUC x100 at the val-selected epoch, eval-mode probe, encoder tap. CIs: cluster bootstrap (rotations, then seeds; paper split: seeds; 10,000 resamples; rng 20261101), descriptive; raw-head CIs recomputed the same way (artifacts/tables/d24-bootstrap.md differs by Monte Carlo error only).

Command: `.venv/bin/python scripts/analysis/d26_d27b.py` (reader outputs: `scripts/read_d24.py --tags S1Z|S3Z|S3FZ --out artifacts/analysis/D27B/<tag>.md`; P1Z: artifacts/analysis/E26/P1Z.md)

## Checks

- S1Z: 120 records = 2 models x 4 arms x 5 rotations x 3 seeds [S_r, 1000+r, 2000+r]; exactly 1 per cell, 0 missing, 0 duplicates, 0 smoke (records per seed: 42: 8, 123: 8, 1000: 8, 1001: 8, 1002: 8, 1003: 8, 1004: 8, 2000: 8, 2001: 8, 2002: 8, 2003: 8, 2004: 8, 2021: 8, 3407: 8, 8888: 8)
  probe `linear_z` only, versions adapt 3 / probe 4, backbone eval, tap encoder, input_norm "", labels overlap, fold_seed override none (config seed)
  every record pairs with the S1E,S1M raw-head record of the same (model, arm, split, seed): same eval_hash, test index, test n and prevalence, adapt_spec and arm_spec, val index (120 raw records predate the val_index field); probe spec differs only in `variant` (fields the raw records predate: tap = encoder, input_norm = ""); SSL losses identical in 60 of 60 adapted runs (0 per step, 60 per epoch: older raw records log epoch losses only)
  eval sets per split (both models): rot0 1, rot1 1, rot2 1, rot3 1, rot4 1
  verdict lines equal the scripts/read_d24.py output artifacts/analysis/D27B/S1Z.md
- S3Z: 120 records = 2 models x 4 arms x 5 rotations x 3 seeds [S_r, 1000+r, 2000+r]; exactly 1 per cell, 0 missing, 0 duplicates, 0 smoke (records per seed: 42: 8, 123: 8, 1000: 8, 1001: 8, 1002: 8, 1003: 8, 1004: 8, 2000: 8, 2001: 8, 2002: 8, 2003: 8, 2004: 8, 2021: 8, 3407: 8, 8888: 8)
  probe `linear_z` only, versions adapt 3 / probe 4, backbone eval, tap encoder, input_norm "", labels overlap, fold_seed override none (config seed)
  every record pairs with the S3E,S3M raw-head record of the same (model, arm, split, seed): same eval_hash, test index, test n and prevalence, adapt_spec and arm_spec, val index (120 raw records predate the val_index field); probe spec differs only in `variant` (fields the raw records predate: tap = encoder, input_norm = ""); SSL losses identical in 60 of 60 adapted runs (0 per step, 60 per epoch: older raw records log epoch losses only)
  eval sets per split (both models): rot0 1, rot1 1, rot2 1, rot3 1, rot4 1
  verdict lines equal the scripts/read_d24.py output artifacts/analysis/D27B/S3Z.md
- S3FZ: 120 records = 2 models x 4 arms x 5 rotations x 3 seeds [S_r, 1000+r, 2000+r]; exactly 1 per cell, 0 missing, 0 duplicates, 0 smoke (records per seed: 42: 8, 123: 8, 1000: 8, 1001: 8, 1002: 8, 1003: 8, 1004: 8, 2000: 8, 2001: 8, 2002: 8, 2003: 8, 2004: 8, 2021: 8, 3407: 8, 8888: 8)
  probe `linear_z` only, versions adapt 3 / probe 4, backbone eval, tap encoder, input_norm "", labels overlap, fold_seed override none (config seed)
  every record pairs with the S3FE,S3FM raw-head record of the same (model, arm, split, seed): same eval_hash, test index, test n and prevalence, adapt_spec and arm_spec, val index (120 raw records predate the val_index field); probe spec differs only in `variant` (fields the raw records predate: tap = encoder, input_norm = ""); SSL losses identical in 60 of 60 adapted runs (0 per step, 60 per epoch: older raw records log epoch losses only)
  eval sets per split (both models): rot0 1, rot1 1, rot2 1, rot3 1, rot4 1
  verdict lines equal the scripts/read_d24.py output artifacts/analysis/D27B/S3FZ.md
- P1Z: 40 records = 2 models x 4 arms x 5 seeds (42/123/2021/3407/8888), paper split; exactly 1 per cell, 0 missing, 0 duplicates, 0 smoke (records per seed: 42: 8, 123: 8, 2021: 8, 3407: 8, 8888: 8)
  probe `linear_z` only, versions adapt 3 / probe 4, backbone eval, tap encoder, input_norm "", labels upstream, fold_seed override none (config seed)
  every record pairs with the P1E raw-head record of the same (model, arm, split, seed): same eval_hash, test index, test n and prevalence, adapt_spec and arm_spec, val index (40 raw records predate the val_index field); probe spec differs only in `variant` (fields the raw records predate: tap = encoder, input_norm = ""); SSL losses identical in 20 of 20 adapted runs (0 per step, 20 per epoch: older raw records log epoch losses only)
  eval sets per split (both models): paper 1
  verdict lines equal the scripts/read_d24.py output artifacts/analysis/E26/P1Z.md
- Raw-head verdicts re-derived from the D24-A records equal the published D24-A strings (24 of 24); the S_r-only linear_z reading equals the published E26 strings (24 of 24).

## Co-primary outcome

**23 of 26 rule outputs hold (both heads agree); 3 are head-dependent:** Siena biot last - lp; Siena filtered biot last - lp; Siena filtered biot last_randinit - last.

| setting | model | contrast | linear_z mean ± SEM | linear_z per rotation (seed on paper split) | linear_z mean [95% CI] | linear_z verdict | raw mean ± SEM | raw per rotation | raw mean [95% CI] | raw verdict | **co-primary** | E26 at S_r (linear_z, 1 seed) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CHB-MIT | biot | last - lp | +0.1 ± 0.4 | -0.4, +0.4, +1.6, -1.1, +0.1 | +0.1 [-0.7, +1.0] | no difference shown | +1.9 ± 1.0 | +1.7, +3.1, +0.9, -1.1, +5.0 | +1.9 [+0.1, +3.9] | no difference shown | **holds** | +0.2 no difference shown |
| CHB-MIT | biot | last_randinit - last | +0.1 ± 5.1 | +13.5, -17.5, -0.8, -0.9, +6.3 | +0.1 [-9.7, +8.7] | no difference shown | +0.2 ± 6.1 | -8.3, -4.7, -5.8, +24.4, -4.9 | +0.2 [-9.2, +12.3] | no difference shown | **holds** | -1.3 no difference shown |
| CHB-MIT | biot | lp - lp_randinit | -0.2 ± 5.1 | -13.3, +17.2, -0.7, +2.0, -6.4 | -0.2 [-8.7, +9.7] | no difference shown | -2.0 ± 5.4 | +6.5, +1.8, +4.9, -23.1, +0.2 | -2.0 [-12.9, +6.3] | no difference shown | **holds** | +1.1 no difference shown |
| CHB-MIT | biot | D17 | -0.0 ± 0.0 | -0.2, +0.1, +0.0, +0.0, -0.1 | -0.0 [-0.1, +0.1] | random features explain it | +0.1 ± 0.1 | -0.2, +0.2, +0.1, +0.1, +0.4 | +0.1 [-0.1, +0.4] | random features explain it | **holds** | +0.0 random features explain it |
| CHB-MIT | cbramod | last - lp | +0.4 ± 0.4 | +1.5, -0.7, +0.4, +0.7, +0.2 | +0.4 [-0.3, +1.5] | no difference shown | -0.0 ± 0.2 | -0.4, +0.5, +0.0, -0.1, -0.1 | -0.0 [-0.3, +0.3] | no difference shown | **holds** | +0.3 no difference shown |
| CHB-MIT | cbramod | last_randinit - last | -5.6 ± 2.4 | -11.4, -7.8, -5.9, +3.4, -6.0 | -5.6 [-9.6, -0.7] | second term wins | -4.4 ± 1.1 | -3.2, -7.9, -3.7, -1.7, -5.6 | -4.4 [-6.8, -2.2] | second term wins | **holds** | -2.3 no difference shown |
| CHB-MIT | cbramod | lp - lp_randinit | +5.2 ± 2.4 | +9.9, +8.5, +5.5, -4.0, +6.2 | +5.2 [+0.1, +9.2] | first term wins | +5.5 ± 1.1 | +5.9, +9.3, +3.1, +4.1, +4.9 | +5.5 [+3.5, +7.7] | first term wins | **holds** | +2.1 no difference shown |
| CHB-MIT | cbramod | D17 | +0.1 ± 0.1 | -0.0, -0.1, -0.0, +0.1, +0.4 | +0.1 [-0.1, +0.3] | random features explain it | +1.0 ± 0.7 | +2.3, +1.8, -0.5, +2.3, -0.8 | +1.0 [-0.5, +2.6] | random features explain it | **holds** | +0.0 random features explain it |
| Siena | biot | last - lp | +1.7 ± 0.7 | +0.9, -0.2, +1.5, +4.0, +2.0 | +1.7 [+0.4, +3.3] | no difference shown | +9.2 ± 2.5 | +7.5, +18.3, +3.4, +10.0, +7.0 | +9.2 [+4.6, +15.6] | first term wins | **head-dependent** | +0.8 no difference shown |
| Siena | biot | last_randinit - last | +2.5 ± 2.5 | -4.8, +11.1, +1.3, +2.2, +2.9 | +2.5 [-3.0, +8.8] | no difference shown | +7.2 ± 6.7 | -7.7, +28.1, +6.4, +15.5, -6.3 | +7.2 [-4.4, +19.5] | no difference shown | **holds** | -1.4 no difference shown |
| Siena | biot | lp - lp_randinit | -4.2 ± 2.4 | +3.9, -10.9, -2.8, -6.1, -4.8 | -4.2 [-10.1, +1.6] | second term wins | -16.1 ± 8.9 | +1.1, -45.7, -9.1, -26.5, -0.3 | -16.1 [-33.1, -1.7] | second term wins | **holds** | +0.6 no difference shown |
| Siena | biot | D17 | +0.0 ± 0.0 | +0.0, +0.0, -0.1, +0.0, +0.1 | +0.0 [-0.0, +0.1] | random features explain it | +0.3 ± 0.3 | +0.9, +0.7, +0.7, -1.0, +0.4 | +0.3 [-0.4, +1.0] | random features explain it | **holds** | -0.0 random features explain it |
| Siena | cbramod | last - lp | -0.3 ± 0.4 | +0.3, -1.0, -0.2, -1.2, +0.7 | -0.3 [-1.4, +0.6] | no difference shown | +0.3 ± 0.2 | -0.5, +0.3, +0.5, +1.0, +0.0 | +0.3 [-0.7, +0.8] | no difference shown | **holds** | +0.8 no difference shown |
| Siena | cbramod | last_randinit - last | -8.6 ± 2.7 | -9.0, -3.1, -18.9, -5.4, -6.6 | -8.6 [-15.5, -4.3] | second term wins | -7.6 ± 2.4 | -6.6, -2.9, -13.4, -2.2, -13.0 | -7.6 [-13.0, -3.0] | second term wins | **holds** | -9.4 second term wins |
| Siena | cbramod | lp - lp_randinit | +8.8 ± 2.7 | +8.6, +4.1, +19.0, +6.5, +5.9 | +8.8 [+4.3, +15.4] | first term wins | +7.0 ± 3.4 | +4.8, +0.3, +14.7, -0.0, +15.2 | +7.0 [+0.9, +13.7] | first term wins | **holds** | +8.6 first term wins |
| Siena | cbramod | D17 | -0.0 ± 0.0 | -0.1, -0.0, +0.0, -0.1, +0.0 | -0.0 [-0.1, +0.1] | random features explain it | -0.4 ± 1.0 | -2.2, -2.3, +1.8, -1.3, +2.2 | -0.4 [-2.3, +1.7] | random features explain it | **holds** | -0.0 random features explain it |
| Siena filtered | biot | last - lp | +1.9 ± 1.3 | +6.1, +3.7, +0.1, +0.0, -0.3 | +1.9 [-0.3, +5.4] | no difference shown | +4.1 ± 1.5 | +1.3, +8.9, +0.9, +5.0, +4.4 | +4.1 [+1.4, +6.9] | first term wins | **head-dependent** | +0.4 no difference shown |
| Siena filtered | biot | last_randinit - last | -2.2 ± 6.0 | -22.2, +9.8, -2.3, -6.5, +10.5 | -2.2 [-13.5, +7.9] | no difference shown | -4.7 ± 10.7 | -24.3, +37.1, -9.3, -13.8, -13.2 | -4.7 [-19.1, +17.0] | second term wins | **head-dependent** | -1.4 no difference shown |
| Siena filtered | biot | lp - lp_randinit | -0.2 ± 5.1 | +13.6, -13.4, +2.2, +6.5, -10.1 | -0.2 [-9.3, +9.1] | no difference shown | +1.0 ± 12.1 | +23.3, -46.2, +9.2, +8.9, +9.6 | +1.0 [-23.8, +17.2] | no difference shown | **holds** | -0.4 no difference shown |
| Siena filtered | biot | D17 | -0.5 ± 0.5 | -2.4, +0.0, +0.0, -0.0, +0.1 | -0.5 [-1.9, +0.1] | random features explain it | +0.4 ± 0.2 | +0.3, -0.1, +0.8, +0.1, +0.9 | +0.4 [-0.1, +0.9] | random features explain it | **holds** | -1.5 random features explain it |
| Siena filtered | cbramod | last - lp | +0.3 ± 0.2 | +0.2, -0.0, +0.8, -0.0, +0.7 | +0.3 [-0.3, +1.3] | no difference shown | +0.1 ± 0.1 | +0.3, -0.1, +0.2, +0.2, +0.1 | +0.1 [+0.0, +0.3] | no difference shown | **holds** | +0.2 no difference shown |
| Siena filtered | cbramod | last_randinit - last | -9.2 ± 2.7 | -19.6, -6.4, -8.8, -6.1, -4.9 | -9.2 [-14.7, -5.0] | second term wins | -10.7 ± 2.3 | -15.3, -7.7, -8.3, -5.2, -16.9 | -10.7 [-15.8, -6.4] | second term wins | **holds** | -9.2 second term wins |
| Siena filtered | cbramod | lp - lp_randinit | +8.8 ± 2.7 | +19.2, +6.5, +8.0, +5.8, +4.4 | +8.8 [+4.6, +14.3] | first term wins | +9.4 ± 2.1 | +16.2, +6.7, +7.3, +4.8, +12.3 | +9.4 [+5.4, +13.7] | first term wins | **holds** | +8.8 first term wins |
| Siena filtered | cbramod | D17 | -0.0 ± 0.1 | -0.2, +0.0, +0.0, -0.2, +0.2 | -0.0 [-0.2, +0.1] | random features explain it | -1.1 ± 0.9 | +1.3, -1.2, -0.9, -0.3, -4.5 | -1.1 [-3.8, +0.7] | random features explain it | **holds** | -0.2 random features explain it |
| CHB-MIT paper split | biot | last - lp | +0.2 ± 0.8 | -0.8, -1.0, -0.2, -0.5, +3.4 | +0.2 [-0.8, +1.8] | no difference shown | -0.6 ± 1.2 | -2.0, +1.8, -4.3, -0.1, +1.6 | -0.6 [-2.7, +1.4] | no difference shown | **holds** | - |
| CHB-MIT paper split | biot | last_randinit - last | +9.1 ± 1.6 | +11.4, +6.4, +7.3, +14.4, +5.9 | +9.1 [+6.4, +12.2] | descriptive (D24-B registers last - lp only) | +35.8 ± 1.0 | +36.7, +33.0, +38.8, +35.9, +34.5 | +35.8 [+34.1, +37.5] | descriptive (D24-B registers last - lp only) | - | - |
| CHB-MIT paper split | biot | lp - lp_randinit | -9.3 ± 1.5 | -10.6, -5.4, -7.1, -13.9, -9.2 | -9.3 [-11.9, -6.9] | descriptive (D24-B registers last - lp only) | -35.1 ± 0.3 | -34.7, -34.7, -34.6, -35.7, -35.9 | -35.1 [-35.6, -34.6] | descriptive (D24-B registers last - lp only) | - | - |
| CHB-MIT paper split | biot | D17 | -0.0 ± 0.0 | +0.0, -0.0, -0.0, -0.0, +0.0 | -0.0 [-0.0, +0.0] | descriptive (D24-B registers last - lp only) | +0.0 ± 0.0 | -0.0, +0.0, -0.1, +0.1, +0.2 | +0.0 [-0.0, +0.1] | descriptive (D24-B registers last - lp only) | - | - |
| CHB-MIT paper split | cbramod | last - lp | +0.2 ± 0.1 | +0.4, +0.2, +0.3, -0.0, +0.0 | +0.2 [+0.0, +0.3] | no difference shown | +0.0 ± 0.0 | -0.0, +0.0, +0.0, +0.0, +0.0 | +0.0 [-0.0, +0.0] | no difference shown | **holds** | - |
| CHB-MIT paper split | cbramod | last_randinit - last | -3.6 ± 1.2 | -0.4, -3.9, -7.8, -2.1, -3.7 | -3.6 [-5.9, -1.7] | descriptive (D24-B registers last - lp only) | -8.5 ± 0.3 | -8.8, -9.4, -7.9, -8.7, -7.7 | -8.5 [-9.0, -8.0] | descriptive (D24-B registers last - lp only) | - | - |
| CHB-MIT paper split | cbramod | lp - lp_randinit | +3.4 ± 1.2 | +0.0, +3.6, +7.5, +2.2, +3.6 | +3.4 [+1.5, +5.7] | descriptive (D24-B registers last - lp only) | +6.4 ± 0.7 | +4.2, +8.8, +6.0, +6.3, +6.8 | +6.4 [+5.2, +7.8] | descriptive (D24-B registers last - lp only) | - | - |
| CHB-MIT paper split | cbramod | D17 | -0.0 ± 0.0 | -0.0, -0.1, -0.1, +0.0, -0.0 | -0.0 [-0.1, +0.0] | descriptive (D24-B registers last - lp only) | -2.1 ± 0.7 | -4.6, -0.6, -1.8, -2.4, -0.8 | -2.1 [-3.4, -0.9] | descriptive (D24-B registers last - lp only) | - | - |

D17 CI = last_randinit - lp_randinit. Paper split: units are seeds 42/123/2021/3407/8888.

## Per seed, linear_z (rotation: S_r/1000+r/2000+r)

- CHB-MIT biot last - lp: rot0 +0.1/-1.8/+0.6; rot1 +0.3/+0.4/+0.4; rot2 +1.0/+1.9/+1.8; rot3 -1.0/-1.5/-0.8; rot4 +0.4/-1.1/+1.0
- CHB-MIT biot last_randinit - last: rot0 +10.7/+16.0/+13.8; rot1 -20.7/-23.9/-7.9; rot2 -1.1/-0.6/-0.8; rot3 -4.0/-2.7/+4.1; rot4 +8.8/+13.7/-3.7
- CHB-MIT biot lp - lp_randinit: rot0 -11.0/-14.5/-14.4; rot1 +20.6/+23.5/+7.4; rot2 +0.2/-1.4/-0.9; rot3 +5.0/+4.3/-3.4; rot4 -9.2/-12.8/+2.8
- CHB-MIT cbramod last - lp: rot0 +0.1/-0.6/+5.1; rot1 +0.1/-0.9/-1.5; rot2 +0.4/+0.7/+0.1; rot3 +0.7/+0.6/+0.6; rot4 +0.2/+0.4/+0.1
- CHB-MIT cbramod last_randinit - last: rot0 -8.8/-11.1/-14.4; rot1 -4.1/-9.6/-9.8; rot2 -6.6/-5.7/-5.6; rot3 +7.5/-0.8/+3.5; rot4 +0.4/-6.2/-12.2
- CHB-MIT cbramod lp - lp_randinit: rot0 +8.8/+11.5/+9.3; rot1 +4.0/+10.4/+11.1; rot2 +6.1/+5.0/+5.4; rot3 -8.1/+0.3/-4.1; rot4 -0.4/+5.9/+13.1
- Siena biot last - lp: rot0 +0.2/+1.9/+0.6; rot1 +0.6/+0.2/-1.3; rot2 +0.1/+2.9/+1.5; rot3 -0.3/+4.9/+7.4; rot4 +3.3/+0.7/+2.1
- Siena biot last_randinit - last: rot0 -10.7/+1.7/-5.4; rot1 +9.1/+0.5/+23.6; rot2 -9.4/+16.5/-3.2; rot3 +3.8/-5.0/+7.8; rot4 +0.3/+1.1/+7.4
- Siena biot lp - lp_randinit: rot0 +10.5/-3.5/+4.8; rot1 -9.8/-0.7/-22.2; rot2 +9.2/-19.5/+1.7; rot3 -3.6/+0.1/-15.0; rot4 -3.5/-1.4/-9.6
- Siena cbramod last - lp: rot0 +1.0/-0.1/-0.2; rot1 +1.5/-4.6/+0.1; rot2 -0.1/-0.8/+0.4; rot3 +0.9/-4.1/-0.3; rot4 +0.7/+1.0/+0.6
- Siena cbramod last_randinit - last: rot0 -4.7/-10.2/-12.2; rot1 +1.4/-6.3/-4.4; rot2 -33.4/-18.7/-4.4; rot3 -7.4/-6.3/-2.6; rot4 -3.2/-4.1/-12.5
- Siena cbramod lp - lp_randinit: rot0 +3.4/+10.1/+12.4; rot1 -2.9/+11.0/+4.1; rot2 +33.4/+19.7/+4.0; rot3 +6.5/+10.3/+2.8; rot4 +2.5/+3.7/+11.3
- Siena filtered biot last - lp: rot0 +0.2/+1.4/+16.8; rot1 +0.9/+0.1/+10.1; rot2 -0.1/+0.1/+0.3; rot3 +0.3/+0.6/-0.9; rot4 +0.5/-2.3/+0.9
- Siena filtered biot last_randinit - last: rot0 -31.7/-16.0/-18.9; rot1 +10.4/+11.6/+7.2; rot2 +0.2/-0.4/-6.6; rot3 +3.1/-18.5/-4.2; rot4 +11.1/+12.8/+7.6
- Siena filtered biot lp - lp_randinit: rot0 +24.6/+14.7/+1.7; rot1 -11.3/-11.8/-17.3; rot2 -0.1/+0.3/+6.3; rot3 -3.7/+18.1/+5.2; rot4 -11.7/-10.5/-8.3
- Siena filtered cbramod last - lp: rot0 +0.2/+0.2/+0.2; rot1 +0.1/+0.2/-0.3; rot2 -0.4/-1.7/+4.7; rot3 +0.2/+0.3/-0.5; rot4 +1.1/+2.6/-1.7
- Siena filtered cbramod last_randinit - last: rot0 -16.4/-22.6/-19.7; rot1 -10.1/-0.0/-9.2; rot2 -11.9/-1.0/-13.5; rot3 -2.6/-7.5/-8.1; rot4 -5.1/-3.0/-6.6
- Siena filtered cbramod lp - lp_randinit: rot0 +16.0/+22.3/+19.4; rot1 +10.0/-0.1/+9.5; rot2 +12.4/+2.6/+9.0; rot3 +1.8/+7.4/+8.4; rot4 +4.1/+0.9/+8.1

## Arms (descriptive)

| setting | model | arm | linear_z mean ± SEM | linear_z per rotation (seed on paper split) | raw head mean ± SEM | raw head per rotation (seed on paper split) |
|---|---|---|---|---|---|---|
| CHB-MIT | biot | lp | 72.3 ± 7.0 | 48.6, 83.1, 87.9, 65.2, 76.4 | 65.1 ± 7.9 | 61.0, 63.6, 90.0, 40.9, 69.9 |
| CHB-MIT | biot | lp_randinit | 72.5 ± 5.5 | 61.9, 65.9, 88.6, 63.3, 82.8 | 67.0 ± 5.1 | 54.5, 61.8, 85.1, 64.0, 69.7 |
| CHB-MIT | biot | last | 72.4 ± 7.4 | 48.3, 83.5, 89.5, 64.1, 76.5 | 67.0 ± 8.3 | 62.6, 66.6, 90.9, 39.8, 74.9 |
| CHB-MIT | biot | last_randinit | 72.5 ± 5.5 | 61.8, 66.0, 88.7, 63.3, 82.7 | 67.1 ± 5.2 | 54.3, 62.0, 85.1, 64.2, 70.1 |
| CHB-MIT | cbramod | lp | 79.3 ± 4.2 | 77.5, 83.9, 90.7, 65.2, 79.2 | 81.6 ± 3.3 | 72.0, 83.8, 88.9, 75.9, 87.6 |
| CHB-MIT | cbramod | lp_randinit | 74.1 ± 3.1 | 67.7, 75.4, 85.1, 69.2, 73.0 | 76.2 ± 3.6 | 66.0, 74.6, 85.7, 71.8, 82.7 |
| CHB-MIT | cbramod | last | 79.7 ± 4.1 | 79.0, 83.1, 91.1, 65.9, 79.4 | 81.6 ± 3.4 | 71.5, 84.3, 88.9, 75.8, 87.5 |
| CHB-MIT | cbramod | last_randinit | 74.1 ± 3.1 | 67.6, 75.3, 85.1, 69.3, 73.4 | 77.2 ± 3.0 | 68.3, 76.4, 85.2, 74.2, 81.9 |
| Siena | biot | lp | 68.6 ± 1.6 | 66.0, 75.0, 67.2, 67.0, 67.7 | 51.3 ± 6.4 | 64.0, 36.3, 60.1, 35.0, 61.3 |
| Siena | biot | lp_randinit | 72.8 ± 3.8 | 62.1, 85.9, 70.1, 73.1, 72.5 | 67.4 ± 3.9 | 62.9, 81.9, 69.2, 61.5, 61.6 |
| Siena | biot | last | 70.2 ± 1.3 | 66.9, 74.9, 68.7, 71.0, 69.7 | 60.6 ± 4.8 | 71.5, 54.6, 63.5, 45.0, 68.3 |
| Siena | biot | last_randinit | 72.8 ± 3.8 | 62.1, 86.0, 70.0, 73.1, 72.7 | 67.8 ± 4.0 | 63.8, 82.7, 69.8, 60.5, 62.0 |
| Siena | cbramod | lp | 78.9 ± 2.0 | 75.2, 83.7, 76.0, 83.9, 75.9 | 81.4 ± 2.4 | 81.8, 79.8, 75.0, 80.8, 89.6 |
| Siena | cbramod | lp_randinit | 70.1 ± 4.0 | 66.5, 79.6, 57.0, 77.4, 70.0 | 74.4 ± 3.7 | 77.0, 79.6, 60.3, 80.8, 74.4 |
| Siena | cbramod | last | 78.7 ± 1.7 | 75.5, 82.7, 75.9, 82.7, 76.6 | 81.7 ± 2.3 | 81.3, 80.2, 75.6, 81.7, 89.7 |
| Siena | cbramod | last_randinit | 70.1 ± 4.0 | 66.4, 79.6, 57.0, 77.3, 70.0 | 74.0 ± 3.1 | 74.7, 77.3, 62.1, 79.5, 76.6 |
| Siena filtered | biot | lp | 73.3 ± 3.0 | 76.6, 74.2, 76.6, 77.5, 61.5 | 69.8 ± 6.8 | 85.0, 44.3, 73.3, 72.9, 73.3 |
| Siena filtered | biot | lp_randinit | 73.5 ± 4.0 | 63.0, 87.6, 74.4, 71.0, 71.6 | 68.8 ± 5.4 | 61.7, 90.5, 64.1, 64.0, 63.7 |
| Siena filtered | biot | last | 75.2 ± 3.7 | 82.8, 77.9, 76.7, 77.5, 61.2 | 73.9 ± 5.5 | 86.3, 53.2, 74.1, 77.9, 77.7 |
| Siena filtered | biot | last_randinit | 73.0 ± 4.3 | 60.6, 87.6, 74.4, 71.0, 71.7 | 69.2 ± 5.3 | 62.0, 90.3, 64.9, 64.1, 64.6 |
| Siena filtered | cbramod | lp | 82.8 ± 2.0 | 86.3, 87.6, 76.7, 83.1, 80.2 | 89.5 ± 2.3 | 91.9, 89.4, 81.1, 90.5, 94.5 |
| Siena filtered | cbramod | lp_randinit | 74.0 ± 2.7 | 67.1, 81.2, 68.7, 77.3, 75.8 | 80.0 ± 2.3 | 75.7, 82.7, 73.8, 85.7, 82.2 |
| Siena filtered | cbramod | last | 83.1 ± 1.8 | 86.5, 87.6, 77.5, 83.1, 80.9 | 89.6 ± 2.3 | 92.2, 89.3, 81.3, 90.7, 94.6 |
| Siena filtered | cbramod | last_randinit | 74.0 ± 2.7 | 66.9, 81.2, 68.7, 77.0, 76.0 | 78.9 ± 2.1 | 77.0, 81.5, 72.9, 85.5, 77.7 |
| CHB-MIT paper split | biot | lp | 79.1 ± 1.8 | 77.5, 84.4, 80.3, 73.7, 79.7 | 55.0 ± 0.4 | 55.3, 55.8, 55.8, 53.9, 54.3 |
| CHB-MIT paper split | biot | lp_randinit | 88.4 ± 0.4 | 88.1, 89.8, 87.4, 87.7, 88.9 | 90.1 ± 0.2 | 90.0, 90.5, 90.4, 89.6, 90.2 |
| CHB-MIT paper split | biot | last | 79.3 ± 1.9 | 76.7, 83.4, 80.1, 73.3, 83.1 | 54.4 ± 1.1 | 53.3, 57.6, 51.5, 53.8, 55.9 |
| CHB-MIT paper split | biot | last_randinit | 88.4 ± 0.5 | 88.1, 89.8, 87.4, 87.6, 89.0 | 90.2 ± 0.2 | 89.9, 90.5, 90.3, 89.7, 90.4 |
| CHB-MIT paper split | cbramod | lp | 88.5 ± 0.4 | 87.7, 88.0, 88.5, 88.1, 90.1 | 92.0 ± 0.0 | 92.0, 92.0, 91.9, 92.0, 92.2 |
| CHB-MIT paper split | cbramod | lp_randinit | 85.1 ± 1.2 | 87.7, 84.4, 81.0, 85.8, 86.5 | 85.6 ± 0.7 | 87.7, 83.2, 85.9, 85.7, 85.3 |
| CHB-MIT paper split | cbramod | last | 88.6 ± 0.4 | 88.1, 88.3, 88.7, 88.0, 90.1 | 92.0 ± 0.1 | 91.9, 92.0, 91.9, 92.0, 92.2 |
| CHB-MIT paper split | cbramod | last_randinit | 85.0 ± 1.2 | 87.7, 84.4, 80.9, 85.9, 86.4 | 83.5 ± 0.3 | 83.1, 82.6, 84.0, 83.3, 84.5 |

## Anomalies, CHB-MIT (descriptive, linear_z)

| model | arm | best epoch = last epoch (10) | test ROC < 50 | which (test ROC, val ROC x100) |
|---|---|---|---|---|
| biot | lp | 0 of 15 | 2 | rot0 s42: test 49.9 (val 88.8); rot0 s1000: test 44.8 (val 86.6) |
| biot | lp_randinit | 0 of 15 | 0 | - |
| biot | last | 0 of 15 | 1 | rot0 s1000: test 43.0 (val 86.5) |
| biot | last_randinit | 0 of 15 | 0 | - |
| cbramod | lp | 1 of 15 | 0 | - |
| cbramod | lp_randinit | 7 of 15 | 0 | - |
| cbramod | last | 2 of 15 | 0 | - |
| cbramod | last_randinit | 7 of 15 | 0 | - |

## Anomalies, Siena (descriptive, linear_z)

| model | arm | best epoch = last epoch (10) | test ROC < 50 | which (test ROC, val ROC x100) |
|---|---|---|---|---|
| biot | lp | 4 of 15 | 0 | - |
| biot | lp_randinit | 0 of 15 | 0 | - |
| biot | last | 6 of 15 | 0 | - |
| biot | last_randinit | 0 of 15 | 0 | - |
| cbramod | lp | 1 of 15 | 0 | - |
| cbramod | lp_randinit | 2 of 15 | 1 | rot2 s2021: test 43.4 (val 73.4) |
| cbramod | last | 1 of 15 | 0 | - |
| cbramod | last_randinit | 2 of 15 | 1 | rot2 s2021: test 43.4 (val 73.3) |

## Anomalies, Siena filtered (descriptive, linear_z)

| model | arm | best epoch = last epoch (10) | test ROC < 50 | which (test ROC, val ROC x100) |
|---|---|---|---|---|
| biot | lp | 5 of 15 | 0 | - |
| biot | lp_randinit | 3 of 15 | 0 | - |
| biot | last | 5 of 15 | 0 | - |
| biot | last_randinit | 3 of 15 | 0 | - |
| cbramod | lp | 0 of 15 | 0 | - |
| cbramod | lp_randinit | 2 of 15 | 0 | - |
| cbramod | last | 0 of 15 | 0 | - |
| cbramod | last_randinit | 1 of 15 | 0 | - |

## Anomalies, CHB-MIT paper split (descriptive, linear_z)

| model | arm | best epoch = last epoch (10) | test ROC < 50 | which (test ROC, val ROC x100) |
|---|---|---|---|---|
| biot | lp | 0 of 5 | 0 | - |
| biot | lp_randinit | 0 of 5 | 0 | - |
| biot | last | 0 of 5 | 0 | - |
| biot | last_randinit | 0 of 5 | 0 | - |
| cbramod | lp | 2 of 5 | 0 | - |
| cbramod | lp_randinit | 3 of 5 | 0 | - |
| cbramod | last | 2 of 5 | 0 | - |
| cbramod | last_randinit | 3 of 5 | 0 | - |
