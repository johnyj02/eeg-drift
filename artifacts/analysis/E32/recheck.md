# E32 / E33a adversarial re-check (2026-11-01)

My own loader over artifacts/s3-results/*/results/*.json (skip diag-/test-index-/val-index-/report-, skip
smoke). It does not use e32_e33a.py or read_d24.load. It reuses paired()/d17() (scripts/read_step1.py)
and cluster_ci() (scripts/bootstrap_d24.py), which I checked first: paired() is D18 (mean > 3 and > 0 in
>= n-1 rotations, mirrored for < -3); d17() is D17 (|mean| <= 3 means random features explain it);
cluster_ci() resamples rotations, then seeds, 10,000 times (D24-D). I used a fresh rng(20261101) for each
contrast, so CI bounds differ from the README by Monte Carlo error only (up to 0.5).
The script is /tmp/recheck_e32/recheck.py (not kept in the repo).

## 1. Integrity: CONFIRMED
- S1R 120 and S3R 120 (2 models x lp/lp_randinit/last/last_randinit x 5 rotations x seeds S_r/1000+r/2000+r).
  S1X 150 (the same plus `all`). 1 record per cell, 0 duplicate keys, 0 smoke. Every record has probe v4,
  a linear head, eval mode and overlap labels.
- fold_seed: 20261101 on all 240 S1R/S3R records. S1X has none.
- eval_hash: one per rotation, and it differs from S1E+S1M / S3E+S3M in all 15 (dataset, rotation) cells.
- Test subjects shared with D24-A: CHB-MIT 0/0/0/0/1 (rot4: chb03). Siena 1/1/1/2/0. Test and validation
  subjects and test window counts match the README partition tables. I did not re-check the positive-window
  counts (the indexes carry no labels).

## 2. E32 numbers: CONFIRMED (all 16 means, all per-rotation values, all verdicts; CIs agree within MC error)
The three non-replications are all BIOT on CHB-MIT, and the rule outputs are correct:
| contrast | mean | per rotation | sign count | E32 CI (mine) | rule | D24-A |
|---|---|---|---|---|---|---|
| last - lp | +3.61 | +1.30, +2.43, +0.11, +12.12, +2.11 | 5/5 > 0 | [+0.9, +8.1] | first term wins | +1.91, 4/5 > 0, no difference shown (mean below 3) |
| last_randinit - last | +7.84 | +4.94, +1.23, +4.08, +18.32, +10.64 | 5/5 > 0 | [+2.5, +13.9] | first term wins | +0.15, 1/5 > 0, no difference shown |
| lp - lp_randinit | -11.60 | -6.26, -4.16, -4.63, -30.34, -12.60 | 5/5 < 0 | [-21.4, -4.4] | second term wins | -1.95, 4/5 > 0, no difference shown |
Sensitivity (post hoc): dropping rot3 removes only the last - lp verdict (mean +1.48). The other two survive
dropping any one rotation (means +5.2 to +9.5, and -6.9 to -13.5).
CI overlap holds for all 16 contrasts, and none is borderline (the narrowest overlap is Siena CBraMod D17,
+0.6 to +1.7).

## 3. 13 of 16 replicated: CONFIRMED
If "overlaps the original" is read as "the original mean lies inside the new CI" (post hoc), the count is
11/16. The two extra misses are Siena CBraMod lp - lp_randinit (D24-A +7.0, new CI [+7.8, +17.3]) and
Siena CBraMod D17 (D24-A -0.4, new CI [+0.6, +5.6]).

## 4. E33a: CONFIRMED
- The S1X verdict strings equal the D24-A CHB-MIT strings in 8 of 8 cases. BIOT: none / none / none /
  random features. CBraMod: none / pretrained wins / pretrained features win / random features. The
  means match the README.
- Test indexes over the 5 rotations: chbmit_x has 683 EDFs and 23 subjects. The S1E/S1M (chbmit_eval10)
  indexes have 605 EDFs and 20 subjects. 78 EDFs were added and 0 removed: chb02_16+ (1), chb12 (21),
  chb13 (33), chb17a/b/c (21), chb24_02 and chb24_22 (2). The two chb24 files are outside the
  pre-registered wording. They were logged before the runs (WORKLOG 2026-11-01 10:55; scripts/submit_d25.sh
  E33A comment).

## 5. BIOT raw head on the new CHB-MIT partition (descriptive)
- rot3 lp is below chance: 41.4 / 47.2 / 45.0 (mean 44.5; validation 57.9-59.6). rot3 last scores 50.5 / 59.0 / 60.5.
- Pretrained BIOT lp and last pick the final epoch (9) in 30 of 30 runs. Random-init runs pick epochs 0-8.
  The per-epoch test ROC of the pretrained arms starts below chance (rot3 lp 26.3 at epoch 0) and is still
  rising at epoch 9. The raw head is under-trained on pretrained features, as E15 found.
- In rot0/1/4 the last - lp gap shrinks over epochs, so `last` looks like `lp` a little further along.
  In rot3 the gap grows (6.5 to 12.1).
- On the D24-A partition, E26 (linear_z, seed S_r) cut BIOT CHB-MIT last - lp from +1.9 to +0.2. It also
  lifted the rot3 lp that the raw head left below chance (40.9 raw, 3 seeds) to 67.7. E32 has no linear_z
  run. So the E32 BIOT CHB-MIT "SA helps" fits the same raw-head effect E26 found on Siena (it rests on
  the one rotation where the raw lp head is below chance), but E32 data cannot test that. The two "random
  init wins" non-replications point the way the raw-head bias predicts (random features are 4-11x larger,
  E15). They do not depend on rot3. They are untested with a standardized head on this partition.
