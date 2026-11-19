# D27-C and D27-D: CBraMod LP at probe batch 128 (E30 C2/C3 control) and the fine-tuning reference

Post hoc controls (notes/decisions.md "## D27", designed after all D24-D26 data were seen, before any D27 run). ROC-AUC x100 at the val-selected epoch. Script: scripts/analysis/d27_cd.py. Anything not named a rule below is descriptive/post hoc.

## Verdicts (rule outputs; numbers and checks below)

- C, CBraMod control, Siena: C2 **not testable: adaptation adds nothing at any N** (best N 896 (84.59), best - N4174 +0.00, range 0.00, v - LP +2.01 to +2.01); C3 **uninformative** (range 0.05, v - LP +1.99 to +2.03); LP b128 at S_r 82.57, control 84.58 (N4174)
- C, CBraMod control, Siena filtered: C2 **not testable: adaptation adds nothing at any N** (best N 896 (90.06), best - N4174 +0.00, range 0.00, v - LP +0.11 to +0.11); C3 **uninformative** (range 0.00, v - LP +0.11 to +0.11); LP b128 at S_r 89.95, control 90.06 (N4174)
- D, CHB-MIT paper split, biot: ft(lp) 87.5 ± 1.1 vs ft(lp_randinit) 90.7 ± 0.1, diff -3.13 (0/5 > 0) -> **pretraining helps fine-tuning: not shown** (second term wins)
- D, CHB-MIT paper split, cbramod: ft(lp) 85.0 ± 1.1 vs ft(lp_randinit) 85.8 ± 0.3, diff -0.80 (2/5 > 0) -> **pretraining helps fine-tuning: not shown** (no difference shown)
- D, CHB-MIT rotations, biot: ft(lp) 82.7 ± 4.4 vs ft(lp_randinit) 79.5 ± 4.1, diff +3.22 (4/5 > 0) -> **pretraining helps fine-tuning** (first term wins)
- D, CHB-MIT rotations, cbramod: ft(lp) 84.8 ± 4.1 vs ft(lp_randinit) 77.6 ± 2.9, diff +7.19 (4/5 > 0) -> **pretraining helps fine-tuning** (first term wins)
- D, Siena rotations, biot: ft(lp) 90.0 ± 0.9 vs ft(lp_randinit) 89.7 ± 2.1, diff +0.28 (3/5 > 0) -> **pretraining helps fine-tuning: not shown** (no difference shown)
- D, Siena rotations, cbramod: ft(lp) 90.2 ± 1.4 vs ft(lp_randinit) 78.4 ± 1.3, diff +11.76 (5/5 > 0) -> **pretraining helps fine-tuning** (first term wins)

## Record checks

- one eval_hash per (eval data, split) across the new records, the records they pair with (E30 S3CC/S3FCC, S3E/S3M, S3FE/S3FM, S1E/S1M, P1E, the logged linear P1L/S1L/S3L) and both models: 16 (data, split) cells; Siena filtered differs from unfiltered in all 5 rotations (the records do not store the data variant: identified by run_tag and eval_hash)
- S3CLPB (Siena): 15 records = 5 rotations x 3 seeds [S_r, 1000+r, 2000+r], 0 duplicate, 0 smoke; CBraMod lp, pretrained checkpoint (sha pinned), probe v4 / adapt v3, linear head 32,001 params, eval mode, encoder tap, probe batch 128, overlap labels; probe spec identical to the E30 control's (S3CC) apart from the seed; eval_hash = the control's in every rotation; best epoch (0-based) counts {0: 1, 1: 1, 2: 1, 4: 1, 5: 2, 6: 1, 7: 6, 9: 2}
- S3FCLPB (Siena filtered): 15 records = 5 rotations x 3 seeds [S_r, 1000+r, 2000+r], 0 duplicate, 0 smoke; CBraMod lp, pretrained checkpoint (sha pinned), probe v4 / adapt v3, linear head 32,001 params, eval mode, encoder tap, probe batch 128, overlap labels; probe spec identical to the E30 control's (S3FCC) apart from the seed; eval_hash = the control's in every rotation; best epoch (0-based) counts {1: 2, 2: 2, 3: 1, 4: 1, 6: 1, 7: 4, 9: 4}
- P1FT (CHB-MIT paper split): 20 records = 2 models x 2 arms x 5 seeds, 0 duplicate, 0 smoke; probe `ft` only, v4 / adapt v3, no SSL step (groups [], adapt False), lp = pinned pretrained checkpoint, lp_randinit = random init (no checkpoint); spec ft / eval mode / encoder tap / batch 256 / 10 epochs / head lr 4e-4 (encoder 0.1x) / wd 0.05 / cosine to 1e-5; head params BIOT 257, CBraMod 32,001; labels upstream; 10-epoch history present, best_epoch = argmax(val ROC), test_at_best and test_last equal the logged epochs' metrics; eval_hash = P1E/P1L in every split
- S1FT (CHB-MIT rotations): 60 records = 2 models x 2 arms x 5 rotations x 3 seeds, 0 duplicate, 0 smoke; probe `ft` only, v4 / adapt v3, no SSL step (groups [], adapt False), lp = pinned pretrained checkpoint, lp_randinit = random init (no checkpoint); spec ft / eval mode / encoder tap / batch 256 / 10 epochs / head lr 4e-4 (encoder 0.1x) / wd 0.05 / cosine to 1e-5; head params BIOT 257, CBraMod 32,001; labels overlap; 10-epoch history present, best_epoch = argmax(val ROC), test_at_best and test_last equal the logged epochs' metrics; eval_hash = S1E/S1M/S1L in every split
- S3FT (Siena rotations): 60 records = 2 models x 2 arms x 5 rotations x 3 seeds, 0 duplicate, 0 smoke; probe `ft` only, v4 / adapt v3, no SSL step (groups [], adapt False), lp = pinned pretrained checkpoint, lp_randinit = random init (no checkpoint); spec ft / eval mode / encoder tap / batch 256 / 10 epochs / head lr 4e-4 (encoder 0.1x) / wd 0.05 / cosine to 1e-5; head params BIOT 257, CBraMod 32,001; labels overlap; 10-epoch history present, best_epoch = argmax(val ROC), test_at_best and test_last equal the logged epochs' metrics; eval_hash = S3E/S3M/S3L in every split

## C. CBraMod LP at probe batch 128: the E30 C2/C3 reading for the CBraMod control

Rule (D27-C): the E30 C2/C3 rules (D15 rules; decisions.md "## D15") for the CBraMod control curve (E30 run tags S3CC / S3FCC, arm `last`, fixed_c 132 SSL steps, N896 / N4174 / P2N2048 / P10N2048, seed S_r) against LP at seed S_r. E30 reader choices (decisions.md "D25 outcomes, wave B part 2"): curve and LP = mean over the 5 rotations; "within 3 of LP at every N" = |v - LP| <= 3 for every N; C3 "> 3 above LP" = every P point; flat but not > 3 above LP = "uninformative". Verdict code imported from scripts/analysis/e30_c2c3.py (c2, c3, describe).

### Siena (S3CC control vs S3CLPB)

| rotation (S_r) | N896 | N4174 | P2N2048 | P10N2048 | LP b128 at S_r | LP b128 3-seed mean | LP b256 at S_r (S3E) |
|---|---|---|---|---|---|---|---|---|
| rot0 (42) | 89.6 | 89.6 | 89.6 | 89.6 | 83.4 | 86.1 | 78.8 |
| rot1 (123) | 83.0 | 83.0 | 83.0 | 83.1 | 81.1 | 81.0 | 80.0 |
| rot2 (2021) | 78.4 | 78.4 | 78.4 | 78.4 | 76.9 | 76.8 | 75.0 |
| rot3 (3407) | 83.3 | 83.3 | 83.3 | 83.3 | 82.3 | 82.4 | 80.6 |
| rot4 (8888) | 88.6 | 88.6 | 88.6 | 88.6 | 89.1 | 89.1 | 89.6 |
| **mean ± SEM** | **84.6 ± 2.0** | **84.6 ± 2.0** | **84.6 ± 2.0** | **84.6 ± 2.0** | **82.6 ± 2.0** | 83.1 ± 2.1 | 80.8 ± 2.4 |

| reading | C2 verdict | numbers | C3 verdict | numbers |
|---|---|---|---|---|
| control at S_r vs LP b128 at S_r, rotation means (D27-C RULE) | **not testable: adaptation adds nothing at any N** | best N 896 (84.59), best - N4174 +0.00, range 0.00, v - LP +2.01 to +2.01 | **uninformative** | range 0.05, v - LP +1.99 to +2.03 |
| control at S_r vs LP b128 3-seed rotation means (descriptive/post hoc) | not testable: adaptation adds nothing at any N | best N 896 (84.59), best - N4174 +0.00, range 0.00, v - LP +1.49 to +1.50 | uninformative | range 0.05, v - LP +1.47 to +1.51 |

Per rotation, control vs that rotation's LP at S_r (descriptive/post hoc): C2 {'not supported': 1, 'not testable: adaptation adds nothing at any N': 4}; C3 {'supported as written': 1, 'uninformative': 4}.

- rot0: C2 not supported (best N 896 (89.62), best - N4174 +0.02, range 0.02, v - LP +6.20 to +6.22); C3 supported as written (range 0.03, v - LP +6.19 to +6.22)
- rot1: C2 not testable: adaptation adds nothing at any N (best N 896 (83.04), best - N4174 +0.00, range 0.00, v - LP +1.92 to +1.92); C3 uninformative (range 0.06, v - LP +1.88 to +1.94)
- rot2: C2 not testable: adaptation adds nothing at any N (best N 896 (78.39), best - N4174 +0.01, range 0.01, v - LP +1.46 to +1.47); C3 uninformative (range 0.03, v - LP +1.46 to +1.50)
- rot3: C2 not testable: adaptation adds nothing at any N (best N 4174 (83.31), best - N4174 +0.00, range 0.01, v - LP +1.00 to +1.02); C3 uninformative (range 0.07, v - LP +0.97 to +1.04)
- rot4: C2 not testable: adaptation adds nothing at any N (best N 896 (88.58), best - N4174 +0.00, range 0.00, v - LP -0.55 to -0.54); C3 uninformative (range 0.04, v - LP -0.57 to -0.53)

CBraMod probe batch (descriptive/post hoc): LP b128 - b256, per rotation at S_r +4.6, +1.1, +1.9, +1.7, -0.5 (mean +1.7); 3-seed means +4.4, +1.2, +1.8, +1.6, -0.6 (mean +1.7).

### Siena filtered (S3FCC control vs S3FCLPB)

| rotation (S_r) | N896 | N4174 | P2N2048 | P10N2048 | LP b128 at S_r | LP b128 3-seed mean | LP b256 at S_r (S3FE) |
|---|---|---|---|---|---|---|---|---|
| rot0 (42) | 93.6 | 93.6 | 93.6 | 93.6 | 92.2 | 92.5 | 91.5 |
| rot1 (123) | 88.4 | 88.4 | 88.4 | 88.4 | 88.9 | 88.9 | 89.4 |
| rot2 (2021) | 82.9 | 82.9 | 82.9 | 82.9 | 83.3 | 83.2 | 81.2 |
| rot3 (3407) | 91.3 | 91.3 | 91.3 | 91.3 | 90.5 | 90.7 | 90.4 |
| rot4 (8888) | 94.1 | 94.1 | 94.1 | 94.1 | 94.8 | 94.8 | 94.5 |
| **mean ± SEM** | **90.1 ± 2.0** | **90.1 ± 2.1** | **90.1 ± 2.0** | **90.1 ± 2.1** | **89.9 ± 1.9** | 90.0 ± 2.0 | 89.4 ± 2.2 |

| reading | C2 verdict | numbers | C3 verdict | numbers |
|---|---|---|---|---|
| control at S_r vs LP b128 at S_r, rotation means (D27-C RULE) | **not testable: adaptation adds nothing at any N** | best N 896 (90.06), best - N4174 +0.00, range 0.00, v - LP +0.11 to +0.11 | **uninformative** | range 0.00, v - LP +0.11 to +0.11 |
| control at S_r vs LP b128 3-seed rotation means (descriptive/post hoc) | not testable: adaptation adds nothing at any N | best N 896 (90.06), best - N4174 +0.00, range 0.00, v - LP +0.07 to +0.07 | uninformative | range 0.00, v - LP +0.07 to +0.07 |

Per rotation, control vs that rotation's LP at S_r (descriptive/post hoc): C2 {'not testable: adaptation adds nothing at any N': 5}; C3 {'uninformative': 5}.

- rot0: C2 not testable: adaptation adds nothing at any N (best N 896 (93.58), best - N4174 +0.01, range 0.01, v - LP +1.40 to +1.41); C3 uninformative (range 0.01, v - LP +1.41 to +1.42)
- rot1: C2 not testable: adaptation adds nothing at any N (best N 4174 (88.39), best - N4174 +0.00, range 0.00, v - LP -0.50 to -0.50); C3 uninformative (range 0.04, v - LP -0.52 to -0.48)
- rot2: C2 not testable: adaptation adds nothing at any N (best N 896 (82.92), best - N4174 +0.01, range 0.01, v - LP -0.43 to -0.42); C3 uninformative (range 0.00, v - LP -0.43 to -0.43)
- rot3: C2 not testable: adaptation adds nothing at any N (best N 4174 (91.33), best - N4174 +0.00, range 0.00, v - LP +0.78 to +0.78); C3 uninformative (range 0.01, v - LP +0.77 to +0.78)
- rot4: C2 not testable: adaptation adds nothing at any N (best N 896 (94.09), best - N4174 +0.00, range 0.00, v - LP -0.73 to -0.72); C3 uninformative (range 0.02, v - LP -0.74 to -0.72)

CBraMod probe batch (descriptive/post hoc): LP b128 - b256, per rotation at S_r +0.7, -0.5, +2.2, +0.1, +0.3 (mean +0.6); 3-seed means +0.6, -0.5, +2.1, +0.1, +0.2 (mean +0.5).

Relation to E30 (decisions.md "D25 outcomes, wave B part 2"): the recorded CBraMod-control strings were C2 "not supported or not testable" and C3 "flat, supported vs uninformative undetermined" (no batch-128 LP). With S3CLPB / S3FCLPB they resolve to the strings above. The E30 descriptive reading against the batch-256 LP (Siena: C2 "not supported", C3 "supported as written", +3.76 above LP) does not hold against the batch-128 LP: part of that +3.76 was probe batch, not adaptation.

## D. Supervised fine-tuning reference (probe `ft`)

Recipe (D27-D, from the records): linear head on the encoder output + the whole encoder trained on the labels; head lr 4e-4, encoder lr 0.1 x (4e-5); AdamW wd 0.05; cosine (both groups) to 1e-5; 10 epochs; batch 256; BCE on logits; selection on val ROC; the encoder runs in EVAL mode during training and scoring (dropout off: `backbone_mode eval`); the caller's encoder is restored afterwards. Trained encoder parameters (from the code, models built at random init on CPU): BIOT 3,186,688 (all of `biot`); CBraMod 4,883,600 of 4,924,000 (`mask_encoding` and `proj_out` get no gradient on the encoder tap, so AdamW leaves them unchanged). The records store only the head size (BIOT 257, CBraMod 32,001).

Rule (D27-D, pre-stated): "pretraining helps fine-tuning" if ft(lp) - ft(lp_randinit) wins: D18 paired rule on rotations (mean > 3 and > 0 in >= 4/5 rotations; per-rotation 3-seed means as in D24-A), D24-B on the paper split (mean > 3 and > 0 for >= 4/5 seeds). The rule output string of read_step1.paired() is shown next to it ("second term wins" is not a pre-stated verdict; read it as descriptive). CIs are descriptive (cluster bootstrap of scripts/bootstrap_d24.py, 10,000 resamples, seed 20261101; t 95% over the 5 units).

### ft ROC per arm (units: rotations = 3-seed means; paper split = seeds)

| setting | model | arm | unit 1 | unit 2 | unit 3 | unit 4 | unit 5 | mean ± SEM over units | mean ± SEM over runs (seeds not independent) |
|---|---|---|---|---|---|---|---|---|---|
| CHB-MIT paper split | biot | ft(lp) | 89.6 | 90.0 | 84.7 | 87.9 | 85.4 | **87.5 ± 1.1** | 87.5 ± 1.1 |
| CHB-MIT paper split | biot | ft(lp_randinit) | 90.4 | 90.9 | 90.4 | 90.5 | 91.1 | **90.7 ± 0.1** | 90.7 ± 0.1 |
| CHB-MIT paper split | cbramod | ft(lp) | 82.3 | 88.1 | 86.1 | 85.5 | 82.9 | **85.0 ± 1.1** | 85.0 ± 1.1 |
| CHB-MIT paper split | cbramod | ft(lp_randinit) | 84.9 | 86.5 | 85.4 | 86.3 | 85.9 | **85.8 ± 0.3** | 85.8 ± 0.3 |
| CHB-MIT rotations | biot | ft(lp) | 74.1 | 82.7 | 94.2 | 71.9 | 90.8 | **82.7 ± 4.4** | 82.7 ± 2.5 |
| CHB-MIT rotations | biot | ft(lp_randinit) | 67.6 | 76.0 | 91.2 | 76.8 | 86.0 | **79.5 ± 4.1** | 79.5 ± 2.2 |
| CHB-MIT rotations | cbramod | ft(lp) | 81.2 | 87.6 | 92.8 | 70.8 | 91.7 | **84.8 ± 4.1** | 84.8 ± 2.2 |
| CHB-MIT rotations | cbramod | ft(lp_randinit) | 74.1 | 73.5 | 88.3 | 72.8 | 79.4 | **77.6 ± 2.9** | 77.6 ± 1.7 |
| Siena rotations | biot | ft(lp) | 92.7 | 91.3 | 88.4 | 89.8 | 88.0 | **90.0 ± 0.9** | 90.0 ± 0.6 |
| Siena rotations | biot | ft(lp_randinit) | 94.5 | 84.5 | 85.6 | 89.6 | 94.5 | **89.7 ± 2.1** | 89.7 ± 1.3 |
| Siena rotations | cbramod | ft(lp) | 94.3 | 89.2 | 85.8 | 90.9 | 90.6 | **90.2 ± 1.4** | 90.2 ± 0.8 |
| Siena rotations | cbramod | ft(lp_randinit) | 79.5 | 79.2 | 73.2 | 80.5 | 79.5 | **78.4 ± 1.3** | 78.4 ± 1.4 |

Units: paper split seeds 42, 123, 2021, 3407, 8888; rotations rot0-rot4 (seeds S_r, 1000+r, 2000+r).

### Pre-stated contrast: ft(lp) - ft(lp_randinit)

| setting | model | ft(lp) | ft(lp_randinit) | mean diff | per unit | > 0 | cluster bootstrap 95% | t 95% | verdict (rule output) | without unit 1..5 (descriptive) |
|---|---|---|---|---|---|---|---|---|---|---|
| CHB-MIT paper split | biot | 87.5 ± 1.1 | 90.7 ± 0.1 | **-3.13** | -0.7, -1.0, -5.7, -2.6, -5.6 | 0/5 | [-5.1, -1.2] | [-6.1, -0.1] | **pretraining helps fine-tuning: not shown** (second term wins) | 2nd wins, 2nd wins, none, 2nd wins, none |
| CHB-MIT paper split | cbramod | 85.0 ± 1.1 | 85.8 ± 0.3 | **-0.80** | -2.6, +1.7, +0.7, -0.8, -3.0 | 2/5 | [-2.4, +0.8] | [-3.3, +1.7] | **pretraining helps fine-tuning: not shown** (no difference shown) | none, none, none, none, none |
| CHB-MIT rotations | biot | 82.7 ± 4.4 | 79.5 ± 4.1 | **+3.22** | +6.5, +6.7, +3.0, -4.9, +4.8 | 4/5 | [-1.0, +6.7] | [-2.7, +9.2] | **pretraining helps fine-tuning** (first term wins) | none, none, 1st wins, 1st wins, none |
| CHB-MIT rotations | cbramod | 84.8 ± 4.1 | 77.6 ± 2.9 | **+7.19** | +7.1, +14.1, +4.5, -2.1, +12.3 | 4/5 | [+1.8, +12.1] | [-0.8, +15.2] | **pretraining helps fine-tuning** (first term wins) | 1st wins, 1st wins, 1st wins, 1st wins, 1st wins |
| Siena rotations | biot | 90.0 ± 0.9 | 89.7 ± 2.1 | **+0.28** | -1.8, +6.8, +2.8, +0.1, -6.5 | 3/5 | [-3.8, +4.4] | [-5.9, +6.4] | **pretraining helps fine-tuning: not shown** (no difference shown) | none, none, none, none, none |
| Siena rotations | cbramod | 90.2 ± 1.4 | 78.4 ± 1.3 | **+11.76** | +14.8, +9.9, +12.6, +10.4, +11.1 | 5/5 | [+9.3, +14.7] | [+9.3, +14.2] | **pretraining helps fine-tuning** (first term wins) | 1st wins, 1st wins, 1st wins, 1st wins, 1st wins |

### Where LP and SA sit relative to ft (descriptive/post hoc)

Frozen references: D24-A linear head (rotations; S1E+S1M, S3E+S3M) and D24-B linear and MLP heads (paper split; P1E); same seeds and eval data as ft, eval-mode probe. Pretrained arms (lp, last = SA) are compared with ft(lp), random-init arms with ft(lp_randinit); differences per unit.

| setting | model | reference arm (head) | reference mean ± SEM | ft - reference |
|---|---|---|---|---|
| CHB-MIT paper split | biot | lp (linear) | 55.0 ± 0.4 | ft(lp) - lp: **+32.5** (+34.3, +34.2, +28.9, +34.0, +31.1; > 0 in 5/5) |
| CHB-MIT paper split | biot | last (linear) | 54.4 ± 1.1 | ft(lp) - last: **+33.1** (+36.4, +32.4, +33.2, +34.1, +29.5; > 0 in 5/5) |
| CHB-MIT paper split | biot | lp_randinit (linear) | 90.1 ± 0.2 | ft(lp_randinit) - lp_randinit: **+0.5** (+0.4, +0.4, -0.0, +0.9, +0.8; > 0 in 4/5) |
| CHB-MIT paper split | biot | last_randinit (linear) | 90.2 ± 0.2 | ft(lp_randinit) - last_randinit: **+0.5** (+0.4, +0.4, +0.1, +0.9, +0.7; > 0 in 5/5) |
| CHB-MIT paper split | biot | lp (mlp_fullft) | 56.1 ± 0.1 | ft(lp) - lp: **+31.4** (+33.7, +33.6, +28.4, +32.2, +29.3; > 0 in 5/5) |
| CHB-MIT paper split | biot | last (mlp_fullft) | 54.9 ± 1.2 | ft(lp) - last: **+32.6** (+36.9, +34.0, +33.0, +32.2, +27.0; > 0 in 5/5) |
| CHB-MIT paper split | biot | lp_randinit (mlp_fullft) | 88.5 ± 0.2 | ft(lp_randinit) - lp_randinit: **+2.2** (+2.1, +2.0, +2.4, +1.7, +2.6; > 0 in 5/5) |
| CHB-MIT paper split | biot | last_randinit (mlp_fullft) | 88.5 ± 0.2 | ft(lp_randinit) - last_randinit: **+2.2** (+2.2, +1.9, +2.0, +1.7, +2.9; > 0 in 5/5) |
| CHB-MIT paper split | cbramod | lp (linear) | 92.0 ± 0.0 | ft(lp) - lp: **-7.0** (-9.7, -3.9, -5.8, -6.5, -9.3; > 0 in 0/5) |
| CHB-MIT paper split | cbramod | last (linear) | 92.0 ± 0.1 | ft(lp) - last: **-7.0** (-9.6, -3.9, -5.8, -6.5, -9.3; > 0 in 0/5) |
| CHB-MIT paper split | cbramod | lp_randinit (linear) | 85.6 ± 0.7 | ft(lp_randinit) - lp_randinit: **+0.2** (-2.9, +3.3, -0.5, +0.6, +0.6; > 0 in 3/5) |
| CHB-MIT paper split | cbramod | last_randinit (linear) | 83.5 ± 0.3 | ft(lp_randinit) - last_randinit: **+2.3** (+1.8, +3.9, +1.3, +3.0, +1.4; > 0 in 5/5) |
| CHB-MIT paper split | cbramod | lp (mlp_fullft) | 91.7 ± 0.3 | ft(lp) - lp: **-6.7** (-8.9, -4.3, -5.0, -5.9, -9.3; > 0 in 0/5) |
| CHB-MIT paper split | cbramod | last (mlp_fullft) | 91.7 ± 0.2 | ft(lp) - last: **-6.7** (-9.0, -3.8, -5.3, -6.2, -9.4; > 0 in 0/5) |
| CHB-MIT paper split | cbramod | lp_randinit (mlp_fullft) | 89.5 ± 0.4 | ft(lp_randinit) - lp_randinit: **-3.7** (-5.3, -2.7, -3.3, -4.4, -3.0; > 0 in 0/5) |
| CHB-MIT paper split | cbramod | last_randinit (mlp_fullft) | 89.7 ± 0.9 | ft(lp_randinit) - last_randinit: **-3.9** (-5.9, -1.5, -4.4, -6.0, -1.9; > 0 in 0/5) |
| CHB-MIT rotations | biot | lp (linear) | 65.1 ± 7.9 | ft(lp) - lp: **+17.7** (+13.1, +19.1, +4.2, +31.0, +20.9; > 0 in 5/5) |
| CHB-MIT rotations | biot | last (linear) | 67.0 ± 8.3 | ft(lp) - last: **+15.8** (+11.5, +16.1, +3.3, +32.1, +15.8; > 0 in 5/5) |
| CHB-MIT rotations | biot | lp_randinit (linear) | 67.0 ± 5.1 | ft(lp_randinit) - lp_randinit: **+12.5** (+13.2, +14.2, +6.1, +12.8, +16.3; > 0 in 5/5) |
| CHB-MIT rotations | biot | last_randinit (linear) | 67.1 ± 5.2 | ft(lp_randinit) - last_randinit: **+12.4** (+13.3, +14.0, +6.1, +12.6, +15.9; > 0 in 5/5) |
| CHB-MIT rotations | cbramod | lp (linear) | 81.6 ± 3.3 | ft(lp) - lp: **+3.2** (+9.2, +3.8, +3.9, -5.2, +4.1; > 0 in 4/5) |
| CHB-MIT rotations | cbramod | last (linear) | 81.6 ± 3.4 | ft(lp) - last: **+3.2** (+9.7, +3.3, +3.9, -5.1, +4.2; > 0 in 4/5) |
| CHB-MIT rotations | cbramod | lp_randinit (linear) | 76.2 ± 3.6 | ft(lp_randinit) - lp_randinit: **+1.5** (+8.1, -1.0, +2.6, +1.0, -3.3; > 0 in 3/5) |
| CHB-MIT rotations | cbramod | last_randinit (linear) | 77.2 ± 3.0 | ft(lp_randinit) - last_randinit: **+0.4** (+5.8, -2.9, +3.1, -1.3, -2.5; > 0 in 2/5) |
| Siena rotations | biot | lp (linear) | 51.3 ± 6.4 | ft(lp) - lp: **+38.7** (+28.7, +55.0, +28.3, +54.7, +26.7; > 0 in 5/5) |
| Siena rotations | biot | last (linear) | 60.6 ± 4.8 | ft(lp) - last: **+29.4** (+21.2, +36.7, +24.9, +44.7, +19.7; > 0 in 5/5) |
| Siena rotations | biot | lp_randinit (linear) | 67.4 ± 3.9 | ft(lp_randinit) - lp_randinit: **+22.3** (+31.6, +2.6, +16.4, +28.1, +32.8; > 0 in 5/5) |
| Siena rotations | biot | last_randinit (linear) | 67.8 ± 4.0 | ft(lp_randinit) - last_randinit: **+22.0** (+30.7, +1.8, +15.8, +29.1, +32.4; > 0 in 5/5) |
| Siena rotations | cbramod | lp (linear) | 81.4 ± 2.4 | ft(lp) - lp: **+8.7** (+12.6, +9.3, +10.8, +10.2, +0.9; > 0 in 5/5) |
| Siena rotations | cbramod | last (linear) | 81.7 ± 2.3 | ft(lp) - last: **+8.5** (+13.1, +9.0, +10.2, +9.2, +0.9; > 0 in 5/5) |
| Siena rotations | cbramod | lp_randinit (linear) | 74.4 ± 3.7 | ft(lp_randinit) - lp_randinit: **+4.0** (+2.5, -0.3, +12.9, -0.3, +5.1; > 0 in 3/5) |
| Siena rotations | cbramod | last_randinit (linear) | 74.0 ± 3.1 | ft(lp_randinit) - last_randinit: **+4.3** (+4.8, +2.0, +11.1, +1.0, +2.9; > 0 in 5/5) |

### ft records: was the encoder trained? best epochs

Train loss of ft vs the logged linear probe of the same model / arm / split / seed (P1L, S1L, S3L: same head lr, batch, epochs, eval mode). An untrained encoder would give the linear curve.

| setting | model | arm | n | epoch-0 train loss ft / linear (mean) | epoch-9 train loss ft / linear (mean) | ft ep9 < linear ep9 | min over epochs of abs(ft - linear) | ROC ft - linear (mean) | best epoch (0-based) counts | best = last epoch |
|---|---|---|---|---|---|---|---|---|---|---|
| CHB-MIT paper split | biot | lp | 5 | 0.0294 / 0.2843 | 0.0060 / 0.0386 | 5/5 | 3.21e-02 | +32.5 | {0: 3, 2: 1, 3: 1} | 0/5 |
| CHB-MIT paper split | biot | lp_randinit | 5 | 0.0391 / 0.0581 | 0.0176 / 0.0341 | 5/5 | 5.68e-03 | +0.5 | {3: 1, 4: 1, 5: 2, 7: 1} | 0/5 |
| CHB-MIT paper split | cbramod | lp | 5 | 0.0235 / 0.0297 | 0.0004 / 0.0124 | 5/5 | 5.34e-03 | -7.0 | {1: 1, 3: 3, 4: 1} | 0/5 |
| CHB-MIT paper split | cbramod | lp_randinit | 5 | 0.0787 / 0.1545 | 0.0008 / 0.0048 | 5/5 | 3.61e-03 | +0.2 | {3: 1, 4: 2, 5: 1, 8: 1} | 0/5 |
| CHB-MIT rotations | biot | lp | 15 | 0.0324 / 0.3443 | 0.0015 / 0.0518 | 15/15 | 3.83e-02 | +17.7 | {0: 1, 1: 3, 2: 1, 3: 2, 4: 4, 5: 2, 6: 1, 8: 1} | 0/15 |
| CHB-MIT rotations | biot | lp_randinit | 15 | 0.0470 / 0.0754 | 0.0152 / 0.0396 | 15/15 | 5.93e-03 | +12.5 | {0: 3, 2: 1, 6: 1, 7: 2, 8: 2, 9: 6} | 6/15 |
| CHB-MIT rotations | cbramod | lp | 15 | 0.0243 / 0.0339 | 0.0000 / 0.0105 | 15/15 | 4.07e-03 | +3.2 | {0: 5, 1: 3, 3: 2, 4: 4, 8: 1} | 0/15 |
| CHB-MIT rotations | cbramod | lp_randinit | 15 | 0.0976 / 0.1686 | 0.0000 / 0.0023 | 15/15 | 5.44e-04 | +1.5 | {0: 3, 1: 1, 2: 1, 3: 3, 5: 2, 6: 3, 7: 2} | 0/15 |
| Siena rotations | biot | lp | 15 | 0.1031 / 0.5349 | 0.0090 / 0.1413 | 15/15 | 9.84e-02 | +38.7 | {0: 4, 2: 3, 3: 2, 4: 1, 5: 1, 6: 2, 9: 2} | 2/15 |
| Siena rotations | biot | lp_randinit | 15 | 0.1523 / 0.2849 | 0.0422 / 0.0846 | 15/15 | 2.61e-02 | +22.3 | {0: 3, 2: 1, 3: 3, 4: 1, 6: 1, 7: 2, 8: 2, 9: 2} | 2/15 |
| Siena rotations | cbramod | lp | 15 | 0.0782 / 0.0959 | 0.0003 / 0.0346 | 15/15 | 1.16e-02 | +8.7 | {0: 2, 1: 5, 2: 2, 3: 1, 4: 1, 5: 2, 9: 2} | 2/15 |
| Siena rotations | cbramod | lp_randinit | 15 | 0.4198 / 0.7277 | 0.0044 / 0.0089 | 15/15 | 2.71e-04 | +4.0 | {0: 2, 1: 3, 2: 2, 3: 1, 5: 1, 6: 1, 7: 1, 8: 2, 9: 2} | 2/15 |

### Published CHB-MIT fine-tuning numbers (descriptive; different recipes)

BIOT: Yang, Westover, Sun, arXiv 2305.10351v1 (10 May 2023), **Table 2** "EEG classification tasks", column group "CHB-MIT (seizure detection)", columns Balanced Acc. / AUC-PR / AUROC (mean ± std over 5 random seeds; the paper reports the average of two settings, val/test swapped). CBraMod: Wang et al., ICLR 2025 (text of arXiv 2412.07236v6, "Published as a conference paper at ICLR 2025"; the OpenReview PDF NPNUHgHF2w was behind a browser check), **Table 8** "The results of different methods on seizure detection (CHB-MIT, 2-class)", columns Balanced Accuracy / AUC-PR / AUROC (mean ± std, 5 seeds).

| source | row | Balanced Acc. | AUC-PR | AUROC |
|---|---|---|---|---|
| BIOT Table 2 | (Vanilla) BIOT (random init) | 0.6640 ± 0.0037 | 0.2573 ± 0.0088 | 0.8646 ± 0.0030 |
| BIOT Table 2 | Pretrained BIOT (PREST) | 0.6942 ± 0.0431 | 0.3072 ± 0.1187 | 0.8679 ± 0.0106 |
| BIOT Table 2 | Pretrained BIOT (PREST+SHHS) (= our checkpoint) | 0.6788 ± 0.0036 | 0.3090 ± 0.0003 | 0.8752 ± 0.0022 |
| BIOT Table 2 | Pretrained BIOT (6 EEG datasets) | 0.7068 ± 0.0457 | 0.3277 ± 0.0460 | 0.8761 ± 0.0284 |
| CBraMod Table 8 | BIOT (as cited by CBraMod) | 0.7068 ± 0.0457 | 0.3277 ± 0.0460 | 0.8761 ± 0.0284 |
| CBraMod Table 8 | LaBraM-Base | 0.7075 ± 0.0358 | 0.3287 ± 0.0402 | 0.8679 ± 0.0199 |
| CBraMod Table 8 | CBraMod | 0.7398 ± 0.0284 | 0.3689 ± 0.0382 | 0.8892 ± 0.0154 |
| ours P1FT (paper split, 5 seeds, mean ± SD) | biot ft(lp) | 0.5604 ± 0.0228 | AP 0.3017 ± 0.0404; trapz 0.2996 ± 0.0401 | 0.8753 ± 0.0239 |
| ours P1FT (paper split, 5 seeds, mean ± SD) | biot ft(lp_randinit) | 0.6391 ± 0.0109 | AP 0.4518 ± 0.0167; trapz 0.4496 ± 0.0167 | 0.9066 ± 0.0033 |
| ours P1FT (paper split, 5 seeds, mean ± SD) | cbramod ft(lp) | 0.6782 ± 0.0169 | AP 0.3543 ± 0.0616; trapz 0.3528 ± 0.0627 | 0.8498 ± 0.0241 |
| ours P1FT (paper split, 5 seeds, mean ± SD) | cbramod ft(lp_randinit) | 0.6075 ± 0.0542 | AP 0.1958 ± 0.0314; trapz 0.1933 ± 0.0312 | 0.8577 ± 0.0067 |

Recipe differences (ours: P1FT records and src/eegdrift/probe.py; theirs: paper text and the MIT code clones in ../_upstream/BIOT and ../_upstream/CBraMod, read only):

| | ours (ft) | BIOT paper / code | CBraMod paper / code |
|---|---|---|---|
| split | process2.py split: test chb23, chb24; val chb21, chb22; one setting | text: train 1-19, val 20-21, test 22-23, then val/test swapped, average of the two; code process2.py: test chb23-24, val chb21-22 | text: train 1-19, val 20-21, test 22-23; code process2.py: test chb23-24, val chb21-22 |
| windows / labels | upstream: 10 s grid + seizure windows re-cut at 5 s stride in every split (incl. test); start/end-in-window label | same pipeline (Appendix A.1: "5 seconds as overlaps to split the seizure regions"; ~0.6% positives in train) | "consistent with BIOT", 326,993 samples |
| epochs / selection | 10, best val ROC | max 100 (Lightning), monitor val AUROC; code: EarlyStopping patience 5 | 50, val AUROC |
| optimizer / lr | AdamW, head 4e-4, encoder 4e-5, wd 0.05, cosine to 1e-5, no clip | Adam lr 1e-3, L2 1e-5, no scheduler (code) | AdamW, backbone 1e-4, head 1e-3 x sqrt(64/256) = 5e-4 (multi_lr), wd 5e-2, cosine to 1e-6, clip 1 |
| batch | 256 | not stated for CHB-MIT; code default 512 (README TUAB runs 512) | 64 |
| loss / sampling | BCE, shuffled, no class weighting or sampler | text: focal loss; code: BCE (focal commented out), shuffle, no sampler; supervised() in run_binary_supervised.py implements TUAB only | BCE, shuffle, no sampler |
| head / dropout | one Linear on the encoder output; dropout OFF (eval mode) while training | BIOT classifier (ELU + Linear), train mode | 3-layer MLP on the flattened 16x10x200 output (`all_patch_reps`, dropout 0.1), proj_out = Identity, train mode |
| checkpoint | EEG-SHHS+PREST-18-channels | PREST / PREST+SHHS / 6 datasets rows | CBraMod pretrained_weights.pth |
| metrics | AP (= pyhealth pr_auc) and trapezoid PR; bal acc at logit 0 | pyhealth: pr_auc = average precision; bal acc at a val-derived threshold (top-k positives) | trapezoid PR-AUC (auc(recall, precision)); bal acc at 0.5 |

## Commands

```
.venv/bin/python scripts/analysis/d27_cd.py
# inputs: artifacts/s3-results (already synced); jobs notes/jobs-d27.txt (tags cb3/cbf, fz*, fn1/fn3); specs scripts/submit_d25.sh (want D27, items C and D)
.venv/bin/python -m pytest -q && .venv/bin/python -m ruff check src tests scripts sm_entry.py
```

