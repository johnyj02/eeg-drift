# D29: C2/C3 controls at the fixed-compute budget (Siena) and PR-AUC readings

Protocol: notes/decisions.md "## D29" (frozen in git, commit c0283f4, before any D29 run). Script scripts/analysis/d29_read.py. ROC-AUC x100 at the val-selected epoch unless stated. BIOT, fixed_c (132 SSL steps, batch 128, constant lr 3e-5, lowest-loss pass restored), probes linear and linear_z at batch 128, eval mode, encoder tap; 5 rotations x 3 seeds [S_r, 1000+r, 2000+r]. Anything not called a rule is descriptive/post hoc.

Rules applied: (1) the E30 C2/C3 rules (D15 text, E30 reader choices: curve and LP = mean over the 5 rotations of 3-seed means; "within 3" = |v - LP| <= 3 at every N; C3 "> 3 above LP" at every P), each head separately, LP = S3LPBD / S3FLPBD with the same head. (2) Noise control: "the plateau needs EEG data" only if at every N (every P) the 95% t-interval (df 4) of last - last_noise over the 5 rotation means excludes 0 with mean > 3; else "no difference demonstrated"; TOST margin 3 per N and P.

## Verdicts (rule outputs)

- Siena, linear: E30 C2 **not supported** (best N 896 (70.45), best - N4174 +0.13, range 0.13, v - LP +12.61 to +12.75); C3 **supported as written** (range 0.76, v - LP +12.07 to +12.83); LP 57.70
- Siena, linear: noise control C2 **no difference demonstrated**, C3 **no difference demonstrated**; last - last_noise N896 +3.94 [-1.39, +9.28] TOST p 0.675, N1664 +3.81 [-1.67, +9.29] TOST p 0.649, N2048 +3.76 [-1.35, +8.87] TOST p 0.649, N4174 +3.77 [-1.53, +9.07] TOST p 0.646, P2N2048 +2.96 [-2.27, +8.19] TOST p 0.492, P5N2048 +4.24 [-0.55, +9.04] TOST p 0.744, P10N2048 +4.08 [-1.08, +9.24] TOST p 0.704
- Siena, linear_z: E30 C2 **not testable: adaptation adds nothing at any N** (best N 1664 (73.49), best - N4174 +0.01, range 0.05, v - LP +2.85 to +2.91); C3 **uninformative** (range 0.06, v - LP +2.80 to +2.86); LP 70.58
- Siena, linear_z: noise control C2 **no difference demonstrated**, C3 **no difference demonstrated**; last - last_noise N896 +1.02 [-1.98, +4.01] TOST p 0.070, N1664 +1.06 [-1.97, +4.09] TOST p 0.075, N2048 +1.02 [-1.95, +4.00] TOST p 0.069, N4174 +1.06 [-1.93, +4.04] TOST p 0.072, P2N2048 +0.40 [-1.27, +2.07] TOST p 0.006, P5N2048 +1.16 [-1.80, +4.12] TOST p 0.080, P10N2048 +1.11 [-1.83, +4.04] TOST p 0.074
- Siena filtered, linear: E30 C2 **not supported** (best N 896 (79.02), best - N4174 +0.01, range 0.10, v - LP +4.49 to +4.59); C3 **supported as written** (range 0.17, v - LP +4.39 to +4.56); LP 74.43
- Siena filtered, linear: noise control C2 **no difference demonstrated**, C3 **no difference demonstrated**; last - last_noise N896 +1.35 [-1.79, +4.49] TOST p 0.109, N1664 +1.30 [-1.77, +4.37] TOST p 0.100, N2048 +1.24 [-1.83, +4.31] TOST p 0.094, N4174 +1.34 [-1.75, +4.44] TOST p 0.106, P2N2048 +0.90 [-1.53, +3.33] TOST p 0.037, P5N2048 +1.54 [-1.79, +4.87] TOST p 0.146, P10N2048 +1.43 [-2.00, +4.86] TOST p 0.137
- Siena filtered, linear_z: E30 C2 **not testable: adaptation adds nothing at any N** (best N 1664 (74.73), best - N4174 +0.06, range 0.06, v - LP +0.82 to +0.88); C3 **uninformative** (range 0.69, v - LP -0.00 to +0.69); LP 73.84
- Siena filtered, linear_z: noise control C2 **no difference demonstrated**, C3 **no difference demonstrated**; last - last_noise N896 -0.05 [-1.20, +1.09] TOST p 0.001, N1664 +0.91 [-2.63, +4.44] TOST p 0.088, N2048 +0.86 [-2.63, +4.36] TOST p 0.082, N4174 +0.84 [-2.68, +4.36] TOST p 0.082, P2N2048 -0.03 [-0.92, +0.87] TOST p 0.00039, P5N2048 -0.20 [-1.55, +1.14] TOST p 0.002, P10N2048 -0.38 [-1.71, +0.95] TOST p 0.003

Descriptive (no rule):

- older D19 three-way string on last - last_noise (the E27 / D27-A rule): Siena linear: N896 the gain needs EEG data, N1664 the gain needs EEG data, N2048 the gain needs EEG data, N4174 the gain needs EEG data, P2N2048 perturbation alone explains it, P5N2048 the gain needs EEG data, P10N2048 the gain needs EEG data; Siena linear_z: N896 perturbation alone explains it, N1664 perturbation alone explains it, N2048 perturbation alone explains it, N4174 perturbation alone explains it, P2N2048 perturbation alone explains it, P5N2048 perturbation alone explains it, P10N2048 perturbation alone explains it; Siena filtered linear: N896 perturbation alone explains it, N1664 perturbation alone explains it, N2048 perturbation alone explains it, N4174 perturbation alone explains it, P2N2048 perturbation alone explains it, P5N2048 perturbation alone explains it, P10N2048 perturbation alone explains it; Siena filtered linear_z: N896 perturbation alone explains it, N1664 perturbation alone explains it, N2048 perturbation alone explains it, N4174 perturbation alone explains it, P2N2048 perturbation alone explains it, P5N2048 perturbation alone explains it, P10N2048 perturbation alone explains it
- PR-AUC (re-read 2026-11-05): no ROC-derived threshold and no practical-importance label is applied to a PR-AUC contrast. C1: 10 of 68 intervals exclude 0; C2/C3 and noise: excludes 0, positive 27, includes 0 115, no interval (1 unit) 14. Full tables: artifacts/analysis/D29/pr_auc.md.

## Record checks

- 2266 records read (0 duplicate, 0 smoke used); per tag: C2E 16, C2X 16, C3E 12, C3X 12, P1E 40, P1G 40, P1Z 40, R3E 10, S1E 45, S1G 150, S1M 125, S1Z 120, S3C2 60, S3C2D 120, S3C3 45, S3C3D 90, S3CC 20, S3CLPB 15, S3E 45, S3FC2 60, S3FC2D 120, S3FC3 45, S3FC3D 90, S3FCC 20, S3FCLPB 15, S3FE 45, S3FG 150, S3FLPB 15, S3FLPBD 15, S3FM 125, S3FZ 120, S3G 150, S3LPB 15, S3LPBD 15, S3M 125, S3Z 120
- every record: probe v4, eval mode, encoder tap, probe variant = probe name; labels upstream on DL's split, overlap on rotations; one eval_hash per (eval data, split) over ALL these records and both models (16 cells); Siena filtered differs from Siena in every rotation
- D29: 450 records = 2 settings x 5 rotations x 3 seeds x (7 subsets x 2 arms + lp), exactly the expected cells (0 missing, 0 extra, 0 duplicate)
- every D29 record: probe v4 / adapt v3, probes linear and linear_z with specs identical apart from the variant (batch 128, 10 epochs, lr 4e-4, wd 0.05, eval mode, encoder tap), linear spec = the E30b record's; eval_hash = the E30b record's in every rotation
- adapted cells: fixed_c, SSL batch 128, lr 3e-5, n_total 4174, pretrained init, groups block03 + head, 132 steps, 0 non-finite steps, n_windows = N, ssl_subjects = P (C3) and = E30b's; `last` adapt_spec, arm_spec, per-pass SSL losses and restored pass identical to E30b; `last_noise` adapt_spec differs from E30b `last` only in arm and data_hash, data_hash = _hash(EEG subset hash, 'noise') (same window subset, noise input), arm ssl_input noise
- reproduction: D29 last and lp linear = E30b linear EXACTLY (test_at_best, test_last, val_curve, best_epoch, best_val equal as floats) in 240 of 240 records (last 210, lp 30)
- selected probe epoch (0-based; 9 = the last of 10) counts: last linear {0: 14, 1: 8, 2: 5, 4: 1, 6: 8, 7: 9, 8: 18, 9: 147}; last linear_z {0: 22, 1: 21, 2: 20, 3: 8, 4: 21, 5: 7, 6: 14, 7: 21, 8: 36, 9: 40}; last_noise linear {0: 14, 1: 14, 5: 8, 6: 8, 7: 7, 8: 14, 9: 145}; last_noise linear_z {0: 31, 1: 21, 2: 10, 4: 21, 5: 16, 6: 21, 7: 14, 8: 33, 9: 43}; lp linear {0: 3, 5: 1, 6: 1, 7: 2, 8: 1, 9: 22}; lp linear_z {0: 4, 1: 3, 2: 2, 3: 1, 4: 3, 5: 1, 6: 2, 7: 3, 8: 5, 9: 6}
- Nadeau-Bengio ratio n_test/n_train (mean over rotations, from the D24 test-index files, same eval_hash as the D29 records): S1E,S1M 0.338, S3E,S3M 0.347, S3FE,S3FM 0.347

## Rule readings (ROC)

### Siena, head linear

3-seed mean per rotation; LP = S3LPBD linear (batch 128).

| arm | rotation | N896 | N1664 | N2048 | N4174 | P2N2048 | P5N2048 | P10N2048 | LP |
|---|---|---|---|---|---|---|---|---|---|
| last | rot0 | 74.4 | 74.4 | 74.4 | 74.4 | 74.0 | 74.5 | 74.4 | 67.8 |
| last | rot1 | 69.5 | 69.4 | 69.7 | 69.5 | 68.2 | 69.8 | 69.9 | 53.3 |
| last | rot2 | 67.1 | 67.1 | 67.1 | 67.0 | 66.8 | 67.3 | 67.3 | 61.9 |
| last | rot3 | 63.2 | 63.1 | 62.5 | 62.8 | 62.7 | 62.6 | 62.6 | 41.7 |
| last | rot4 | 78.0 | 77.8 | 78.1 | 77.8 | 77.0 | 78.5 | 78.1 | 63.8 |
| **last** | **mean** | **70.45** | **70.34** | **70.35** | **70.32** | **69.77** | **70.53** | **70.44** | **57.70** |
| last_noise | rot0 | 72.6 | 72.7 | 72.7 | 72.7 | 72.7 | 72.7 | 72.6 | 67.8 |
| last_noise | rot1 | 63.0 | 62.9 | 63.0 | 63.0 | 63.3 | 62.8 | 62.9 | 53.3 |
| last_noise | rot2 | 62.8 | 62.9 | 62.9 | 62.9 | 63.1 | 62.5 | 62.6 | 61.9 |
| last_noise | rot3 | 54.1 | 54.0 | 54.2 | 54.0 | 54.7 | 54.0 | 53.9 | 41.7 |
| last_noise | rot4 | 80.0 | 80.1 | 80.1 | 80.1 | 80.2 | 79.5 | 79.8 | 63.8 |
| **last_noise** | **mean** | **66.51** | **66.53** | **66.59** | **66.55** | **66.81** | **66.29** | **66.36** | **57.70** |

| reading | C2 | numbers | C3 | numbers |
|---|---|---|---|---|
| last (PRIMARY) | **not supported** | best N 896 (70.45), best - N4174 +0.13, range 0.13, v - LP +12.61 to +12.75 | **supported as written** | range 0.76, v - LP +12.07 to +12.83 |
| last_noise (descriptive) | **not supported** | best N 2048 (66.59), best - N4174 +0.04, range 0.08, v - LP +8.81 to +8.89 | **supported as written** | range 0.52, v - LP +8.59 to +9.11 |

Per-rotation `last` verdicts vs the rotation's own LP (descriptive): C2 {'not supported': 5}; C3 {'supported as written': 5}.

Noise control (rule), last - last_noise, units = 5 rotation means of 3 paired seeds:

| subset | mean | sd | 95% t-interval | passes (lo > 0, mean > 3) | TOST p (margin 3) | NB 95% | TOST p NB | per rotation | > 0 | D19 string (descriptive) |
|---|---|---|---|---|---|---|---|---|---|---|
| N896 | +3.94 | 4.30 | [-1.39, +9.28] | no | 0.675 | [-4.88, +12.77] | 0.609 | +1.83, +6.48, +4.30, +9.15, -2.04 | 4/5 | the gain needs EEG data |
| N1664 | +3.81 | 4.41 | [-1.67, +9.29] | no | 0.649 | [-5.25, +12.87] | 0.592 | +1.69, +6.44, +4.22, +9.08, -2.39 | 4/5 | the gain needs EEG data |
| N2048 | +3.76 | 4.12 | [-1.35, +8.87] | no | 0.649 | [-4.70, +12.21] | 0.592 | +1.63, +6.61, +4.18, +8.38, -2.03 | 4/5 | the gain needs EEG data |
| N4174 | +3.77 | 4.27 | [-1.53, +9.07] | no | 0.646 | [-5.00, +12.53] | 0.590 | +1.67, +6.55, +4.09, +8.74, -2.22 | 4/5 | the gain needs EEG data |
| P2N2048 | +2.96 | 4.21 | [-2.27, +8.19] | no | 0.492 | [-5.69, +11.61] | 0.495 | +1.35, +4.91, +3.73, +8.05, -3.22 | 4/5 | perturbation alone explains it |
| P5N2048 | +4.24 | 3.86 | [-0.55, +9.04] | no | 0.744 | [-3.69, +12.18] | 0.657 | +1.86, +6.97, +4.76, +8.61, -0.98 | 4/5 | the gain needs EEG data |
| P10N2048 | +4.08 | 4.15 | [-1.08, +9.24] | no | 0.704 | [-4.45, +12.61] | 0.629 | +1.78, +6.97, +4.61, +8.75, -1.69 | 4/5 | the gain needs EEG data |

Noise rule: C2 (every N) **no difference demonstrated**; C3 (every P) **no difference demonstrated**.

Per-seed last - last_noise (seeds S_r / 1000+r / 2000+r):

- N896: rot0 +2.84, +1.40, +1.24; rot1 +7.76, +4.95, +6.73; rot2 +1.30, +7.57, +4.02; rot3 +10.43, +9.35, +7.67; rot4 -4.25, +0.36, -2.22
- N1664: rot0 +2.78, +1.24, +1.06; rot1 +8.10, +3.95, +7.27; rot2 +1.18, +7.66, +3.82; rot3 +10.49, +9.33, +7.43; rot4 -4.34, -0.33, -2.50
- N2048: rot0 +2.74, +1.14, +1.03; rot1 +8.18, +4.64, +7.03; rot2 +1.30, +7.55, +3.69; rot3 +9.68, +8.69, +6.77; rot4 -4.27, +0.53, -2.36
- N4174: rot0 +2.75, +1.18, +1.08; rot1 +8.07, +4.66, +6.93; rot2 +1.15, +7.45, +3.69; rot3 +10.04, +9.09, +7.09; rot4 -4.26, -0.02, -2.38
- P2N2048: rot0 +2.15, +0.98, +0.90; rot1 +6.48, +0.52, +7.73; rot2 +1.56, +6.09, +3.53; rot3 +10.24, +7.85, +6.05; rot4 -5.35, -0.66, -3.64
- P5N2048: rot0 +3.11, +1.21, +1.25; rot1 +9.12, +4.08, +7.72; rot2 +1.18, +9.00, +4.10; rot3 +9.69, +9.21, +6.93; rot4 -3.63, +1.41, -0.71
- P10N2048: rot0 +2.92, +1.28, +1.13; rot1 +8.82, +5.07, +7.02; rot2 +1.81, +8.33, +3.68; rot3 +10.17, +9.04, +7.04; rot4 -4.09, +0.65, -1.64

### Siena, head linear_z

3-seed mean per rotation; LP = S3LPBD linear_z (batch 128).

| arm | rotation | N896 | N1664 | N2048 | N4174 | P2N2048 | P5N2048 | P10N2048 | LP |
|---|---|---|---|---|---|---|---|---|---|
| last | rot0 | 68.7 | 68.8 | 68.8 | 68.7 | 68.4 | 68.8 | 68.7 | 67.5 |
| last | rot1 | 77.7 | 77.7 | 77.7 | 77.7 | 77.5 | 77.8 | 77.7 | 78.6 |
| last | rot2 | 66.6 | 66.6 | 66.6 | 66.6 | 66.6 | 66.7 | 66.5 | 63.6 |
| last | rot3 | 77.3 | 77.4 | 77.3 | 77.3 | 77.4 | 77.3 | 77.2 | 70.8 |
| last | rot4 | 76.9 | 77.1 | 76.9 | 77.0 | 77.0 | 76.6 | 76.9 | 72.5 |
| **last** | **mean** | **73.44** | **73.49** | **73.45** | **73.48** | **73.39** | **73.45** | **73.43** | **70.58** |
| last_noise | rot0 | 69.2 | 69.2 | 69.1 | 69.2 | 69.2 | 69.2 | 69.2 | 67.5 |
| last_noise | rot1 | 78.1 | 78.1 | 78.1 | 78.1 | 78.1 | 78.1 | 78.2 | 78.6 |
| last_noise | rot2 | 65.9 | 65.9 | 65.9 | 65.9 | 65.8 | 65.9 | 65.9 | 63.6 |
| last_noise | rot3 | 72.0 | 72.0 | 72.1 | 72.0 | 74.8 | 72.0 | 72.0 | 70.8 |
| last_noise | rot4 | 76.9 | 76.9 | 76.9 | 76.9 | 76.9 | 76.2 | 76.4 | 72.5 |
| **last_noise** | **mean** | **72.42** | **72.43** | **72.42** | **72.42** | **72.99** | **72.28** | **72.32** | **70.58** |

| reading | C2 | numbers | C3 | numbers |
|---|---|---|---|---|
| last (PRIMARY) | **not testable: adaptation adds nothing at any N** | best N 1664 (73.49), best - N4174 +0.01, range 0.05, v - LP +2.85 to +2.91 | **uninformative** | range 0.06, v - LP +2.80 to +2.86 |
| last_noise (descriptive) | **not testable: adaptation adds nothing at any N** | best N 1664 (72.43), best - N4174 +0.01, range 0.01, v - LP +1.84 to +1.85 | **uninformative** | range 0.70, v - LP +1.70 to +2.40 |

Per-rotation `last` verdicts vs the rotation's own LP (descriptive): C2 {'not testable: adaptation adds nothing at any N': 2, 'not supported': 3}; C3 {'uninformative': 3, 'supported as written': 2}.

Noise control (rule), last - last_noise, units = 5 rotation means of 3 paired seeds:

| subset | mean | sd | 95% t-interval | passes (lo > 0, mean > 3) | TOST p (margin 3) | NB 95% | TOST p NB | per rotation | > 0 | D19 string (descriptive) |
|---|---|---|---|---|---|---|---|---|---|---|
| N896 | +1.02 | 2.41 | [-1.98, +4.01] | no | 0.070 | [-3.93, +5.97] | 0.164 | -0.45, -0.46, +0.65, +5.25, +0.09 | 3/5 | perturbation alone explains it |
| N1664 | +1.06 | 2.44 | [-1.97, +4.09] | no | 0.075 | [-3.96, +6.08] | 0.172 | -0.39, -0.49, +0.70, +5.35, +0.14 | 3/5 | perturbation alone explains it |
| N2048 | +1.02 | 2.39 | [-1.95, +4.00] | no | 0.069 | [-3.89, +5.94] | 0.163 | -0.39, -0.48, +0.74, +5.22, +0.03 | 3/5 | perturbation alone explains it |
| N4174 | +1.06 | 2.40 | [-1.93, +4.04] | no | 0.072 | [-3.88, +5.99] | 0.168 | -0.41, -0.46, +0.72, +5.27, +0.16 | 3/5 | perturbation alone explains it |
| P2N2048 | +0.40 | 1.34 | [-1.27, +2.07] | no | 0.006 | [-2.36, +3.16] | 0.030 | -0.76, -0.60, +0.71, +2.57, +0.08 | 3/5 | perturbation alone explains it |
| P5N2048 | +1.16 | 2.38 | [-1.80, +4.12] | no | 0.080 | [-3.73, +6.06] | 0.178 | -0.33, -0.38, +0.74, +5.33, +0.44 | 3/5 | perturbation alone explains it |
| P10N2048 | +1.11 | 2.36 | [-1.83, +4.04] | no | 0.074 | [-3.75, +5.96] | 0.170 | -0.45, -0.45, +0.65, +5.23, +0.56 | 3/5 | perturbation alone explains it |

Noise rule: C2 (every N) **no difference demonstrated**; C3 (every P) **no difference demonstrated**.

Per-seed last - last_noise (seeds S_r / 1000+r / 2000+r):

- N896: rot0 -2.03, +0.75, -0.05; rot1 +0.72, +0.71, -2.82; rot2 -2.34, +1.36, +2.94; rot3 +10.98, +3.81, +0.96; rot4 +1.24, -0.27, -0.71
- N1664: rot0 -1.97, +0.81, +0.01; rot1 +0.72, +0.59, -2.80; rot2 -2.16, +1.30, +2.96; rot3 +11.00, +3.84, +1.21; rot4 +1.35, -0.33, -0.60
- N2048: rot0 -2.02, +0.78, +0.07; rot1 +0.73, +0.62, -2.78; rot2 -1.96, +1.28, +2.90; rot3 +10.77, +3.84, +1.05; rot4 +1.09, -0.26, -0.75
- N4174: rot0 -2.02, +0.76, +0.03; rot1 +0.74, +0.64, -2.75; rot2 -2.06, +1.31, +2.92; rot3 +10.83, +3.85, +1.12; rot4 +1.30, -0.30, -0.53
- P2N2048: rot0 -2.67, +0.41, -0.01; rot1 +0.66, +0.27, -2.72; rot2 -1.53, +1.04, +2.63; rot3 +3.27, +3.54, +0.89; rot4 +1.33, -0.78, -0.30
- P5N2048: rot0 -1.66, +0.81, -0.15; rot1 +0.83, +0.60, -2.56; rot2 -2.50, +1.64, +3.09; rot3 +10.99, +3.83, +1.18; rot4 +0.82, +0.15, +0.36
- P10N2048: rot0 -1.95, +0.72, -0.12; rot1 +0.79, +0.60, -2.75; rot2 -2.63, +1.57, +3.02; rot3 +10.82, +3.98, +0.88; rot4 +1.17, +0.16, +0.34

### Siena filtered, head linear

3-seed mean per rotation; LP = S3FLPBD linear (batch 128).

| arm | rotation | N896 | N1664 | N2048 | N4174 | P2N2048 | P5N2048 | P10N2048 | LP |
|---|---|---|---|---|---|---|---|---|---|
| last | rot0 | 85.8 | 85.9 | 85.8 | 85.8 | 85.9 | 86.0 | 85.8 | 85.5 |
| last | rot1 | 71.7 | 71.5 | 71.5 | 71.7 | 70.6 | 71.7 | 72.1 | 65.7 |
| last | rot2 | 74.2 | 74.2 | 74.1 | 74.2 | 74.6 | 74.0 | 74.0 | 74.8 |
| last | rot3 | 83.5 | 83.5 | 83.4 | 83.4 | 83.3 | 83.4 | 83.4 | 74.9 |
| last | rot4 | 79.9 | 79.8 | 79.8 | 79.9 | 79.8 | 79.8 | 79.8 | 71.2 |
| **last** | **mean** | **79.02** | **78.96** | **78.92** | **79.01** | **78.82** | **78.99** | **78.99** | **74.43** |
| last_noise | rot0 | 86.4 | 86.4 | 86.4 | 86.4 | 86.4 | 86.4 | 86.4 | 85.5 |
| last_noise | rot1 | 68.3 | 68.2 | 68.2 | 68.2 | 69.0 | 67.7 | 67.9 | 65.7 |
| last_noise | rot2 | 75.9 | 75.9 | 75.9 | 75.9 | 75.9 | 75.9 | 75.9 | 74.8 |
| last_noise | rot3 | 79.4 | 79.4 | 79.4 | 79.4 | 79.6 | 79.4 | 79.4 | 74.9 |
| last_noise | rot4 | 78.3 | 78.4 | 78.4 | 78.4 | 78.6 | 77.7 | 78.2 | 71.2 |
| **last_noise** | **mean** | **77.67** | **77.66** | **77.68** | **77.67** | **77.92** | **77.44** | **77.55** | **74.43** |

| reading | C2 | numbers | C3 | numbers |
|---|---|---|---|---|
| last (PRIMARY) | **not supported** | best N 896 (79.02), best - N4174 +0.01, range 0.10, v - LP +4.49 to +4.59 | **supported as written** | range 0.17, v - LP +4.39 to +4.56 |
| last_noise (descriptive) | **not supported** | best N 2048 (77.68), best - N4174 +0.01, range 0.01, v - LP +3.24 to +3.25 | **supported as written** | range 0.48, v - LP +3.02 to +3.49 |

Per-rotation `last` verdicts vs the rotation's own LP (descriptive): C2 {'not testable: adaptation adds nothing at any N': 2, 'not supported': 3}; C3 {'uninformative': 2, 'supported as written': 3}.

Noise control (rule), last - last_noise, units = 5 rotation means of 3 paired seeds:

| subset | mean | sd | 95% t-interval | passes (lo > 0, mean > 3) | TOST p (margin 3) | NB 95% | TOST p NB | per rotation | > 0 | D19 string (descriptive) |
|---|---|---|---|---|---|---|---|---|---|---|
| N896 | +1.35 | 2.53 | [-1.79, +4.49] | no | 0.109 | [-3.85, +6.54] | 0.214 | -0.64, +3.42, -1.73, +4.15, +1.54 | 3/5 | perturbation alone explains it |
| N1664 | +1.30 | 2.48 | [-1.77, +4.37] | no | 0.100 | [-3.78, +6.38] | 0.203 | -0.57, +3.29, -1.73, +4.10, +1.40 | 3/5 | perturbation alone explains it |
| N2048 | +1.24 | 2.47 | [-1.83, +4.31] | no | 0.094 | [-3.83, +6.32] | 0.196 | -0.61, +3.31, -1.80, +3.97, +1.35 | 3/5 | perturbation alone explains it |
| N4174 | +1.34 | 2.49 | [-1.75, +4.44] | no | 0.106 | [-3.77, +6.46] | 0.210 | -0.58, +3.45, -1.71, +4.04, +1.52 | 3/5 | perturbation alone explains it |
| P2N2048 | +0.90 | 1.96 | [-1.53, +3.33] | no | 0.037 | [-3.12, +4.92] | 0.110 | -0.56, +1.56, -1.36, +3.64, +1.23 | 3/5 | perturbation alone explains it |
| P5N2048 | +1.54 | 2.68 | [-1.79, +4.87] | no | 0.146 | [-3.97, +7.05] | 0.252 | -0.44, +4.01, -1.97, +4.01, +2.10 | 3/5 | perturbation alone explains it |
| P10N2048 | +1.43 | 2.76 | [-2.00, +4.86] | no | 0.137 | [-4.24, +7.10] | 0.243 | -0.67, +4.20, -1.97, +4.04, +1.57 | 3/5 | perturbation alone explains it |

Noise rule: C2 (every N) **no difference demonstrated**; C3 (every P) **no difference demonstrated**.

Per-seed last - last_noise (seeds S_r / 1000+r / 2000+r):

- N896: rot0 -1.11, +0.04, -0.86; rot1 +2.19, +8.66, -0.59; rot2 -2.48, -1.28, -1.41; rot3 +5.90, +2.91, +3.64; rot4 +0.64, +0.48, +3.49
- N1664: rot0 -1.16, +0.20, -0.74; rot1 +2.41, +8.15, -0.68; rot2 -2.53, -1.34, -1.32; rot3 +5.87, +2.86, +3.58; rot4 +0.70, +0.13, +3.35
- N2048: rot0 -1.13, +0.11, -0.80; rot1 +2.23, +8.32, -0.62; rot2 -2.60, -1.43, -1.38; rot3 +5.70, +2.70, +3.52; rot4 +0.62, +0.07, +3.36
- N4174: rot0 -1.16, +0.18, -0.77; rot1 +2.26, +8.84, -0.75; rot2 -2.47, -1.33, -1.34; rot3 +5.82, +2.77, +3.54; rot4 +0.77, +0.36, +3.44
- P2N2048: rot0 -0.93, -0.26, -0.50; rot1 +1.70, +4.21, -1.23; rot2 -2.03, -0.72, -1.34; rot3 +5.64, +2.51, +2.77; rot4 +0.22, +0.48, +2.99
- P5N2048: rot0 -1.13, +0.64, -0.84; rot1 +2.98, +9.47, -0.43; rot2 -2.73, -1.90, -1.28; rot3 +5.71, +2.63, +3.71; rot4 +0.84, +0.85, +4.61
- P10N2048: rot0 -1.20, +0.14, -0.95; rot1 +2.80, +9.73, +0.08; rot2 -2.78, -1.65, -1.48; rot3 +5.89, +2.78, +3.45; rot4 +0.59, +0.18, +3.92

### Siena filtered, head linear_z

3-seed mean per rotation; LP = S3FLPBD linear_z (batch 128).

| arm | rotation | N896 | N1664 | N2048 | N4174 | P2N2048 | P5N2048 | P10N2048 | LP |
|---|---|---|---|---|---|---|---|---|---|
| last | rot0 | 81.5 | 81.5 | 81.4 | 81.5 | 76.5 | 81.6 | 81.5 | 75.9 |
| last | rot1 | 76.8 | 76.9 | 76.8 | 76.7 | 76.5 | 76.0 | 76.9 | 77.6 |
| last | rot2 | 77.8 | 77.8 | 77.7 | 77.7 | 77.9 | 77.9 | 76.3 | 77.2 |
| last | rot3 | 74.4 | 74.3 | 74.3 | 74.3 | 74.9 | 74.1 | 74.1 | 75.8 |
| last | rot4 | 63.1 | 63.2 | 63.1 | 63.1 | 63.3 | 63.0 | 63.1 | 62.7 |
| **last** | **mean** | **74.72** | **74.73** | **74.68** | **74.66** | **73.84** | **74.53** | **74.37** | **73.84** |
| last_noise | rot0 | 80.5 | 75.7 | 75.7 | 75.7 | 75.7 | 80.5 | 80.5 | 75.9 |
| last_noise | rot1 | 76.7 | 76.7 | 76.7 | 76.7 | 77.0 | 76.6 | 76.6 | 77.6 |
| last_noise | rot2 | 77.4 | 77.4 | 77.4 | 77.4 | 77.4 | 77.4 | 77.4 | 77.2 |
| last_noise | rot3 | 75.8 | 75.8 | 75.8 | 75.8 | 75.8 | 75.8 | 75.8 | 75.8 |
| last_noise | rot4 | 63.4 | 63.4 | 63.4 | 63.4 | 63.5 | 63.4 | 63.4 | 62.7 |
| **last_noise** | **mean** | **74.77** | **73.82** | **73.82** | **73.82** | **73.87** | **74.74** | **74.75** | **73.84** |

| reading | C2 | numbers | C3 | numbers |
|---|---|---|---|---|
| last (PRIMARY) | **not testable: adaptation adds nothing at any N** | best N 1664 (74.73), best - N4174 +0.06, range 0.06, v - LP +0.82 to +0.88 | **uninformative** | range 0.69, v - LP -0.00 to +0.69 |
| last_noise (descriptive) | **not testable: adaptation adds nothing at any N** | best N 896 (74.77), best - N4174 +0.95, range 0.95, v - LP -0.02 to +0.93 | **uninformative** | range 0.89, v - LP +0.02 to +0.91 |

Per-rotation `last` verdicts vs the rotation's own LP (descriptive): C2 {'not supported': 1, 'not testable: adaptation adds nothing at any N': 4}; C3 {'not flat: not supported': 1, 'uninformative': 4}.

Noise control (rule), last - last_noise, units = 5 rotation means of 3 paired seeds:

| subset | mean | sd | 95% t-interval | passes (lo > 0, mean > 3) | TOST p (margin 3) | NB 95% | TOST p NB | per rotation | > 0 | D19 string (descriptive) |
|---|---|---|---|---|---|---|---|---|---|---|
| N896 | -0.05 | 0.92 | [-1.20, +1.09] | no | 0.001 | [-1.95, +1.84] | 0.006 | +1.03, +0.10, +0.36, -1.46, -0.29 | 3/5 | perturbation alone explains it |
| N1664 | +0.91 | 2.85 | [-2.63, +4.44] | no | 0.088 | [-4.94, +6.75] | 0.188 | +5.83, +0.16, +0.34, -1.53, -0.27 | 3/5 | perturbation alone explains it |
| N2048 | +0.86 | 2.81 | [-2.63, +4.36] | no | 0.082 | [-4.91, +6.64] | 0.181 | +5.73, +0.11, +0.33, -1.52, -0.34 | 3/5 | perturbation alone explains it |
| N4174 | +0.84 | 2.84 | [-2.68, +4.36] | no | 0.082 | [-4.98, +6.66] | 0.181 | +5.75, -0.01, +0.32, -1.54, -0.33 | 2/5 | perturbation alone explains it |
| P2N2048 | -0.03 | 0.72 | [-0.92, +0.87] | no | 0.00039 | [-1.51, +1.46] | 0.003 | +0.86, -0.46, +0.53, -0.92, -0.13 | 2/5 | perturbation alone explains it |
| P5N2048 | -0.20 | 1.09 | [-1.55, +1.14] | no | 0.002 | [-2.44, +2.03] | 0.013 | +1.12, -0.51, +0.52, -1.72, -0.43 | 2/5 | perturbation alone explains it |
| P10N2048 | -0.38 | 1.07 | [-1.71, +0.95] | no | 0.003 | [-2.58, +1.82] | 0.015 | +0.98, +0.29, -1.13, -1.69, -0.35 | 2/5 | perturbation alone explains it |

Noise rule: C2 (every N) **no difference demonstrated**; C3 (every P) **no difference demonstrated**.

Per-seed last - last_noise (seeds S_r / 1000+r / 2000+r):

- N896: rot0 +0.22, +2.48, +0.38; rot1 -0.82, +0.89, +0.23; rot2 -0.09, -0.22, +1.38; rot3 -0.30, -2.75, -1.33; rot4 -1.10, -0.46, +0.67
- N1664: rot0 +0.24, +2.49, +14.74; rot1 -0.31, +0.81, -0.01; rot2 -0.14, -0.26, +1.43; rot3 -0.35, -2.77, -1.47; rot4 -0.98, -0.46, +0.64
- N2048: rot0 +0.23, +2.31, +14.66; rot1 -0.44, +0.73, +0.03; rot2 -0.13, -0.29, +1.42; rot3 -0.35, -2.87, -1.33; rot4 -1.04, -0.56, +0.59
- N4174: rot0 +0.20, +2.37, +14.69; rot1 -0.86, +0.78, +0.04; rot2 -0.08, -0.32, +1.38; rot3 -0.37, -2.87, -1.38; rot4 -1.13, -0.57, +0.72
- P2N2048: rot0 +0.14, +2.34, +0.09; rot1 +0.08, +0.42, -1.88; rot2 +0.16, -0.08, +1.50; rot3 -0.19, -1.90, -0.67; rot4 -1.25, +0.07, +0.78
- P5N2048: rot0 +0.22, +2.66, +0.48; rot1 -1.06, +0.10, -0.56; rot2 -0.05, +0.18, +1.43; rot3 -0.26, -3.30, -1.60; rot4 -1.14, -0.64, +0.48
- P10N2048: rot0 +0.11, +2.50, +0.32; rot1 -0.77, +0.99, +0.65; rot2 -0.13, -4.59, +1.32; rot3 -0.35, -3.08, -1.64; rot4 -1.08, -0.47, +0.49

## PR-AUC readings (descriptive; D29 PR-AUC item; re-read 2026-11-05 without any ROC threshold)

No ROC-derived threshold is applied to a PR-AUC contrast, and no practical-importance label is attached to one. The frozen D29 text asks only for C1, C2 and C3 "read again with average precision (and the trapezoid PR-AUC the release reports)" and defines no PR-AUC margin; the first version of this reader reused the ROC rule strings (D18 |mean| > 3 with 4 of 5 units agreeing; the E30 C2/C3 "within 3" / "> 3 above LP" cuts; the D29 noise rule's "mean > 3") and the margin-3 TOST. That compared one fixed 3-point margin against AP baselines from 1.5 to 44 points and hid measured differences: Siena BIOT raw head AP 1.65 -> 2.20, +0.55 [+0.14, +0.96], about +33% relative, was labelled "no difference shown" because 0.55 < 3. Those labels and the margin-3 TOST are withdrawn here (change made 2026-11-05, AFTER the results, in answer to an external review; post hoc). Each PR-AUC contrast now reports the two arm means, the absolute difference with its 95% t-interval over the stated units, the relative change in percent of the baseline arm, and whether the interval excludes 0 - which is the only inference claim made. A relative change on a near-zero baseline is unstable, so the baseline is printed next to every percentage and should be read with it. No PR-AUC margin is defined in its place: defining one now, after seeing the data, would be a post hoc threshold, and the prevalence-scaled alternatives already in the artifacts (AP / prevalence, scripts/analysis/coverage.py and handcrafted_baseline.py) are reported there rather than turned into a cut here. Every ROC reading in these files is unchanged.

Test prevalence x100 (the scale AP lives on): DL's split 1.49; CHB-MIT rotations 0.66/0.33/0.21/0.32/0.16; Siena 0.98/0.43/0.99/0.54/0.91; Siena filtered 0.98/0.43/0.99/0.54/0.91.

**Full tables for every contrast (C1, C2/C3 on DL's split and on the rotations, the noise arm, both PR metrics): artifacts/analysis/D29/pr_auc.md.** The rows below are the ones whose interval excludes 0.

### C1 (SA - LP = last - lp): the intervals that exclude 0

10 of 68 C1 PR-AUC contrasts (34 rows x 2 metrics) have an interval that excludes 0: 10 positive, 0 negative. Units: 5 seeds on DL's split, 5 rotation means of 3 seeds elsewhere. ROC column for reference (unchanged, with its D18 rule string).

| setting | model | head (tags) | metric | unit | base mean | arm mean | difference | 95% t | relative | excludes 0 | per unit | ROC |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DL's split | cbramod | linear (P1E) | AP | seed (one split) | 42.21 | 42.41 | +0.20 | [+0.08, +0.32] | +0.5% | yes | +0.10, +0.12, +0.27, +0.18, +0.33 | +0.01 no difference shown |
| DL's split | cbramod | linear (P1E) | PR-AUC trapz | seed (one split) | 42.03 | 42.23 | +0.20 | [+0.08, +0.32] | +0.5% | yes | +0.10, +0.12, +0.27, +0.18, +0.33 | +0.01 no difference shown |
| DL's split | cbramod | linear_z (P1Z) | AP | seed (one split) | 34.12 | 34.70 | +0.58 | [+0.30, +0.86] | +1.7% | yes | +0.84, +0.45, +0.45, +0.81, +0.37 | +0.18 no difference shown |
| DL's split | cbramod | linear_z (P1Z) | PR-AUC trapz | seed (one split) | 33.85 | 34.45 | +0.60 | [+0.28, +0.92] | +1.8% | yes | +0.84, +0.42, +0.45, +0.91, +0.37 | +0.18 no difference shown |
| DL's split | cbramod | grid_z (P1G) | AP | seed (one split) | 35.28 | 35.85 | +0.57 | [+0.10, +1.04] | +1.6% | yes | +0.84, -0.09, +0.78, +0.70, +0.64 | +0.12 no difference shown |
| DL's split | cbramod | grid_z (P1G) | PR-AUC trapz | seed (one split) | 35.09 | 35.66 | +0.57 | [+0.09, +1.05] | +1.6% | yes | +0.84, -0.10, +0.78, +0.70, +0.63 | +0.12 no difference shown |
| Siena | biot | linear (S3E+S3M) | AP | rotation mean of 3 seeds | 1.65 | 2.20 | +0.55 | [+0.14, +0.96] | +33.2% | yes | +0.07, +0.50, +0.55, +0.64, +0.99 | +9.23 first term wins |
| Siena | biot | linear (S3E+S3M) | PR-AUC trapz | rotation mean of 3 seeds | 1.49 | 2.03 | +0.54 | [+0.19, +0.90] | +36.2% | yes | +0.16, +0.48, +0.49, +0.61, +0.96 | +9.23 first term wins |
| Siena | biot | linear_z (S3Z) | AP | rotation mean of 3 seeds | 6.37 | 6.55 | +0.18 | [+0.01, +0.35] | +2.8% | yes | +0.03, +0.25, +0.08, +0.37, +0.15 | +1.65 no difference shown |
| Siena | biot | linear_z (S3Z) | PR-AUC trapz | rotation mean of 3 seeds | 6.18 | 6.37 | +0.19 | [+0.00, +0.37] | +3.0% | yes | +0.03, +0.32, +0.08, +0.37, +0.14 | +1.65 no difference shown |

The review's example, re-read: Siena BIOT raw head (S3E+S3M, linear). AP 1.65 -> 2.20, +0.55 [+0.14, +0.96], +33.2% relative on a baseline of 1.65 AP points; trapz 1.49 -> 2.03, +0.54 [+0.19, +0.90], +36.2%. Both intervals exclude 0; the AP baseline sits near the test prevalence (0.43 to 0.99 per rotation), which is why the relative change is large and why it is also unstable. The earlier reading labelled this "no difference shown" because 0.55 < 3, the ROC margin; that label is withdrawn.

### C2/C3 (DL's split and the rotations) and the noise arm

156 PR-AUC readings (every curve point against LP, and `last` against `last_noise` on the rotations): excludes 0, positive 27, includes 0 115, no interval (1 unit) 14. Full numbers in pr_auc.md sections 2-5. Spans over the 7 subsets (N896-N4174 and P2/P5/P10 at N2048) of the rotation contrasts, BIOT, units = 5 rotation means; `excl 0` counts the subsets whose t-interval excludes 0, `NB` the same with the Nadeau-Bengio interval:

| setting | head | metric | vs LP: LP; curve | difference | relative | excl 0 | NB | vs last_noise: difference | relative | excl 0 | NB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Siena | linear | AP | 1.64; 2.59-2.70 | +0.95 to +1.05 | +57.7% to +64.1% | 6/7 | 0/7 | +0.35 to +0.50 | +15.7% to +22.9% | 7/7 | 7/7 |
| Siena | linear | PR-AUC trapz | 1.52; 2.44-2.54 | +0.92 to +1.02 | +60.7% to +67.3% | 7/7 | 0/7 | +0.35 to +0.49 | +16.7% to +24.1% | 7/7 | 7/7 |
| Siena | linear_z | AP | 6.24; 6.68-6.78 | +0.44 to +0.54 | +7.1% to +8.6% | 0/7 | 0/7 | +0.17 to +0.43 | +2.5% to +6.7% | 0/7 | 0/7 |
| Siena | linear_z | PR-AUC trapz | 6.03; 6.46-6.55 | +0.43 to +0.52 | +7.1% to +8.6% | 0/7 | 0/7 | +0.15 to +0.41 | +2.4% to +6.7% | 0/7 | 0/7 |
| Siena filtered | linear | AP | 5.77; 5.53-5.74 | -0.24 to -0.03 | -4.1% to -0.6% | 0/7 | 0/7 | +0.58 to +0.77 | +11.6% to +15.6% | 0/7 | 0/7 |
| Siena filtered | linear | PR-AUC trapz | 5.42; 5.24-5.41 | -0.18 to -0.01 | -3.4% to -0.3% | 0/7 | 0/7 | +0.56 to +0.72 | +12.1% to +15.5% | 0/7 | 0/7 |
| Siena filtered | linear_z | AP | 5.66; 5.64-5.73 | -0.02 to +0.08 | -0.3% to +1.4% | 0/7 | 0/7 | -0.11 to +0.06 | -1.9% to +1.1% | 0/7 | 0/7 |
| Siena filtered | linear_z | PR-AUC trapz | 5.43; 5.41-5.51 | -0.02 to +0.08 | -0.3% to +1.4% | 0/7 | 0/7 | -0.11 to +0.06 | -2.0% to +1.1% | 0/7 | 0/7 |

Reading of that table: on Siena with the raw head the `last` curve sits about +0.95 to +1.05 AP points above LP (58% to 64% of a 1.64-point baseline) and +0.35 to +0.50 above its own noise arm (16% to 23%). The EEG-vs-noise difference is the one that also survives the Nadeau-Bengio interval (7 of 7 subsets); the gain over LP does not (0 of 7). `last_noise` itself sits above LP (2.19 to 2.24 against 1.64 AP), so most of the gain over LP is reproduced by perturbing with noise. With the standardized head, and on filtered Siena, every interval includes 0. The ROC reading of the same noise contrast does not resolve it either way (means +2.96 to +4.24 ROC points, intervals include 0, so the D29 noise rule reads "no difference demonstrated"); that ROC verdict stands and is not a PR-AUC claim.

DL's split C2/C3 (pr_auc.md section 2): BIOT every point vs LP AP -0.49 to +0.04 (LP 5.56, 0/7 exclude 0); PR-AUC trapz -0.51 to +0.04 (LP 5.40, 0/7 exclude 0); CBraMod has one curve seed, so no interval. CBraMod fixed-compute control on the rotations (section 5): Siena AP +2.01 to +2.04 (LP 12.85, 0/4 exclude 0); Siena PR-AUC trapz +1.89 to +1.92 (LP 12.50, 0/4 exclude 0); Siena filtered AP +4.92 to +5.18 (LP 28.01, 0/4 exclude 0); Siena filtered PR-AUC trapz +4.97 to +5.22 (LP 27.49, 0/4 exclude 0).

## Commands

```
.venv/bin/python scripts/analysis/d29_read.py
# inputs: artifacts/s3-results (synced); specs: scripts/submit_d25.sh (want D29; E30 for the pairs)
.venv/bin/python -m pytest -q && .venv/bin/python -m ruff check src tests scripts sm_entry.py
```

