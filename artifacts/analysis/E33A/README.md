# D25-E33a: extended CHB-MIT store chbmit_x (23 subjects), read with the D24 rules

Pre-registered (decisions.md "D25 additions"): chbmit_x store (chb12, chb13, chb17, chb02_16+ added; label-based channel selection), 23-subject rotations (seed 20261014), D24-A arms, 3 seeds, linear, eval mode, run tag S1X; D24 rules. ROC-AUC x100.
Verdicts: per-rotation 3-seed means, D18 paired rule and D17 (as read_d24). CIs: the D24-D cluster bootstrap (rotations, then seeds; 10,000 resamples, rng 20261101). The comparison with D24-A CHB-MIT (S1E+S1M, 22 subjects, other folds) has no pre-registered rule: **descriptive/post hoc**.

Command: `.venv/bin/python scripts/analysis/e32_e33a.py`

## Checks

- S1X: 150 records = 2 models x 5 arms x 5 rotations x 3 seeds [S_r, 1000+r, 2000+r]; exactly 1 per cell, 0 missing, 0 duplicates, 0 smoke
  labels overlap, versions adapt 3 / probe 4, probe/adapt/arm specs = S1E,S1M (except seed, split, data_hash, n_total, dataset), fold_seed override none (config seed); one eval set per rotation shared by both models, every rotation's eval_hash differs from S1E,S1M
- Method check: re-bootstrapping the D24-A records with a fresh rng(20261101) moves the published CI bounds by at most 0.3 ROC (Monte Carlo error; the published bounds are used)
- Store content seen in the test indexes (5 rotations cover every subject once): 683 EDFs vs 605 in chbmit_eval10; 78 added: chb02_16+; chb12 x21; chb13 x33; chb17 x21; chb24_02, chb24_22
- Nothing removed: 0 chbmit_eval10 EDFs missing from chbmit_x.
- n_present is not stored in the result records. The store report (chbmit_x_preprocess_report.json, desktop only) as logged in notes/WORKLOG.md 2026-11-01 10:55: all 78 added EDFs n_present 16/16; left out chb12_27/28/29 (0/16 by label, referential montage; 13 of chb12's 40 seizures).
- Deviation from the pre-registered wording: the same label rule also added chb24_02 and chb24_22 (logged before the runs: WORKLOG 10:55, scripts/submit_d25.sh E33A comment).
- The audit's "also report on the old folds" has no runs (no chbmit_x jobs on the 22-subject folds); D24-A (S1E+S1M) is the old-fold reference below.

## Verdicts (pre-registered: D24 rules)

**Same verdict string as D24-A CHB-MIT (descriptive): 8 of 8.**

| model | contrast | S1X mean ± SEM (rot) | S1X per rotation | S1X 95% CI | S1X verdict | D24-A mean | D24-A per rotation | D24-A 95% CI | D24-A verdict | same verdict (descr.) | CI overlap (descr.) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| biot | last - lp | +1.6 ± 0.8 | +2.2, +2.8, +0.6, +3.4, -1.0 | [+0.1, +2.9] | no difference shown | +1.9 | +1.7, +3.1, +0.9, -1.1, +5.0 | [+0.1, +3.9] | no difference shown | yes | yes |
| biot | last_randinit - last | +1.4 ± 4.9 | -16.9, +11.9, +0.6, +7.3, +4.0 | [-8.0, +8.8] | no difference shown | +0.2 | -8.3, -4.7, -5.8, +24.4, -4.9 | [-8.9, +12.4] | no difference shown | yes | yes |
| biot | lp - lp_randinit | -2.9 ± 5.0 | +14.5, -14.5, -1.1, -10.6, -2.9 | [-11.1, +6.2] | no difference shown | -2.0 | +6.5, +1.8, +4.9, -23.1, +0.2 | [-12.9, +6.1] | no difference shown | yes | yes |
| biot | D17 | +0.0 ± 0.1 | -0.2, +0.1, +0.1, +0.1, +0.1 | [-0.2, +0.2] | random features explain it | +0.1 | -0.2, +0.2, +0.1, +0.1, +0.4 | [-0.1, +0.4] | random features explain it | yes | yes |
| biot | all - last | +6.7 ± 1.4 | +3.2, +4.8, +5.7, +8.7, +11.2 | [+4.0, +9.8] | reference only | +9.8 | +2.7, +14.6, +3.9, +16.8, +10.9 | [+4.6, +14.8] | reference only |  | yes |
| cbramod | last - lp | -0.0 ± 0.1 | -0.2, +0.1, +0.2, -0.0, -0.1 | [-0.2, +0.1] | no difference shown | -0.0 | -0.4, +0.5, +0.0, -0.1, -0.1 | [-0.3, +0.3] | no difference shown | yes | yes |
| cbramod | last_randinit - last | -4.8 ± 0.9 | -5.4, -2.4, -7.9, -4.0, -4.5 | [-6.6, -3.2] | second term wins | -4.4 | -3.2, -7.9, -3.7, -1.7, -5.6 | [-6.9, -2.2] | second term wins | yes | yes |
| cbramod | lp - lp_randinit | +3.9 ± 1.3 | +6.8, +1.6, +7.4, +2.1, +1.9 | [+1.4, +6.9] | first term wins | +5.5 | +5.9, +9.3, +3.1, +4.1, +4.9 | [+3.5, +7.7] | first term wins | yes | yes |
| cbramod | D17 | -0.9 ± 0.7 | +1.1, -0.7, -0.4, -2.0, -2.6 | [-2.8, +1.0] | random features explain it | +1.0 | +2.3, +1.8, -0.5, +2.3, -0.8 | [-0.5, +2.6] | random features explain it | yes | yes |
| cbramod | all - last | +1.1 ± 1.2 | -1.1, +1.5, +5.6, -0.0, -0.6 | [-0.7, +3.4] | reference only | +1.6 | +4.3, +1.3, +0.5, +0.5, +1.6 | [+0.6, +3.0] | reference only |  | yes |

D17 CI = last_randinit - lp_randinit. all - last is a reference (no rule), as in D24.

## Arms (descriptive)

| model | arm | S1X mean ± SEM (rot) | S1X per rotation | D24-A mean ± SEM | D24-A per rotation |
|---|---|---|---|---|---|
| biot | lp | 70.5 ± 3.7 | 61.4, 73.0, 66.7, 68.3, 83.2 | 65.1 ± 7.9 | 61.0, 63.6, 90.0, 40.9, 69.9 |
| biot | lp_randinit | 73.4 ± 7.5 | 46.9, 87.5, 67.8, 78.9, 86.1 | 67.0 ± 5.1 | 54.5, 61.8, 85.1, 64.0, 69.7 |
| biot | last | 72.1 ± 3.3 | 63.6, 75.8, 67.2, 71.7, 82.2 | 67.0 ± 8.3 | 62.6, 66.6, 90.9, 39.8, 74.9 |
| biot | last_randinit | 73.5 ± 7.5 | 46.7, 87.7, 67.9, 79.0, 86.2 | 67.1 ± 5.2 | 54.3, 62.0, 85.1, 64.2, 70.1 |
| biot | all | 78.8 ± 4.5 | 66.8, 80.5, 73.0, 80.4, 93.5 | 76.8 ± 6.9 | 65.3, 81.2, 94.8, 56.6, 85.9 |
| cbramod | lp | 79.1 ± 7.1 | 53.0, 88.9, 75.2, 85.7, 92.8 | 81.6 ± 3.3 | 72.0, 83.8, 88.9, 75.9, 87.6 |
| cbramod | lp_randinit | 75.2 ± 8.2 | 46.3, 87.3, 67.8, 83.6, 90.9 | 76.2 ± 3.6 | 66.0, 74.6, 85.7, 71.8, 82.7 |
| cbramod | last | 79.1 ± 7.2 | 52.8, 88.9, 75.4, 85.7, 92.7 | 81.6 ± 3.4 | 71.5, 84.3, 88.9, 75.8, 87.5 |
| cbramod | last_randinit | 74.3 ± 7.6 | 47.4, 86.6, 67.5, 81.6, 88.2 | 77.2 ± 3.0 | 68.3, 76.4, 85.2, 74.2, 81.9 |
| cbramod | all | 80.1 ± 7.4 | 51.6, 90.5, 80.9, 85.7, 92.1 | 83.2 ± 3.0 | 75.8, 85.6, 89.4, 76.3, 89.1 |

## Partition (descriptive; the D24-A rotations are over 22 subjects, so rotation r is NOT the same fold)

| rotation | S1X test subjects | n test windows | positive windows | S1X val subjects | S1E,S1M test subjects | shared test subjects |
|---|---|---|---|---|---|---|
| rot0 | chb05, chb10, chb12, chb14, chb20 | 58,787 | 294 | chb03, chb04, chb06, chb11, chb24 | chb10, chb11, chb15, chb18 | 1 |
| rot1 | chb03, chb04, chb06, chb11, chb24 | 114,069 | 259 | chb08, chb13, chb15, chb17, chb18 | chb01, chb08, chb09, chb19 | 0 |
| rot2 | chb08, chb13, chb15, chb17, chb18 | 53,874 | 448 | chb01, chb09, chb19, chb22 | chb02, chb05, chb07, chb16 | 0 |
| rot3 | chb01, chb09, chb19, chb22 | 72,781 | 156 | chb02, chb07, chb16, chb23 | chb06, chb14, chb23, chb24 | 0 |
| rot4 | chb02, chb07, chb16, chb23 | 53,231 | 119 | chb05, chb10, chb12, chb14, chb20 | chb03, chb04, chb20, chb22 | 0 |
