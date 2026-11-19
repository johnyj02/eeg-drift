# D25-E32: second subject partition (fold_seed 20261101), read with the D24 rules

Pre-registered rule (completeness-audit.md E32, adopted by D25): **replicated** if the same verdict string holds AND the CI overlaps the original (D24-A, S1E+S1M / S3E+S3M; CIs from artifacts/tables/d24-bootstrap.md). ROC-AUC x100, linear head, eval-mode probe, encoder tap.
Verdicts: per-rotation 3-seed means, D18 paired rule (|mean| > 3, same sign >= 4/5) and D17. CIs: cluster bootstrap (rotations, then seeds), 10,000 resamples, rng 20261101 per set. "CI overlaps" = the two 95% intervals intersect. The column "orig mean in new CI" is post hoc (the other possible reading of "overlaps the original"). 3 seeds per rotation ran: no adaptation.

Command: `.venv/bin/python scripts/analysis/e32_e33a.py`

## Checks

- S1R: 120 records = 2 models x 4 arms x 5 rotations x 3 seeds [S_r, 1000+r, 2000+r]; exactly 1 per cell, 0 missing, 0 duplicates, 0 smoke
  labels overlap, versions adapt 3 / probe 4, probe/adapt/arm specs = S1E,S1M (except seed, split, data_hash, n_total, dataset), fold_seed override 20261101; one eval set per rotation shared by both models, every rotation's eval_hash differs from S1E,S1M
- S3R: 120 records = 2 models x 4 arms x 5 rotations x 3 seeds [S_r, 1000+r, 2000+r]; exactly 1 per cell, 0 missing, 0 duplicates, 0 smoke
  labels overlap, versions adapt 3 / probe 4, probe/adapt/arm specs = S3E,S3M (except seed, split, data_hash, n_total, dataset), fold_seed override 20261101; one eval set per rotation shared by both models, every rotation's eval_hash differs from S3E,S3M
- Method check: re-bootstrapping the D24-A records with a fresh rng(20261101) moves the published CI bounds by at most 0.3 ROC (Monte Carlo error; the published bounds are used)

## Verdicts

**Replicated (pre-registered rule): 13 of 16 verdicts.** Not replicated: CHB-MIT biot last - lp; CHB-MIT biot last_randinit - last; CHB-MIT biot lp - lp_randinit.

| dataset | model | contrast | E32 mean ± SEM (rot) | E32 per rotation | E32 95% CI | E32 verdict | D24-A mean | D24-A per rotation | D24-A 95% CI | D24-A verdict | same verdict | CI overlap | **replicated** | orig mean in new CI (post hoc) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CHB-MIT | biot | last - lp | +3.6 ± 2.2 | +1.3, +2.4, +0.1, +12.1, +2.1 | [+0.8, +8.1] | first term wins | +1.9 | +1.7, +3.1, +0.9, -1.1, +5.0 | [+0.1, +3.9] | no difference shown | NO | yes | **NO** | yes |
| CHB-MIT | biot | last_randinit - last | +7.8 ± 3.0 | +4.9, +1.2, +4.1, +18.3, +10.6 | [+2.7, +13.8] | first term wins | +0.2 | -8.3, -4.7, -5.8, +24.4, -4.9 | [-8.9, +12.4] | no difference shown | NO | yes | **NO** | no |
| CHB-MIT | biot | lp - lp_randinit | -11.6 ± 4.9 | -6.3, -4.2, -4.6, -30.3, -12.6 | [-21.5, -4.5] | second term wins | -2.0 | +6.5, +1.8, +4.9, -23.1, +0.2 | [-12.9, +6.1] | no difference shown | NO | yes | **NO** | no |
| CHB-MIT | biot | D17 | -0.1 ± 0.1 | -0.0, -0.5, -0.4, +0.1, +0.2 | [-0.9, +0.4] | random features explain it | +0.1 | -0.2, +0.2, +0.1, +0.1, +0.4 | [-0.1, +0.4] | random features explain it | yes | yes | **yes** | yes |
| CHB-MIT | cbramod | last - lp | -0.0 ± 0.1 | -0.2, +0.0, -0.2, -0.0, +0.2 | [-0.2, +0.1] | no difference shown | -0.0 | -0.4, +0.5, +0.0, -0.1, -0.1 | [-0.3, +0.3] | no difference shown | yes | yes | **yes** | yes |
| CHB-MIT | cbramod | last_randinit - last | -4.4 ± 1.0 | -4.8, -2.5, -2.7, -4.0, -8.0 | [-6.6, -2.4] | second term wins | -4.4 | -3.2, -7.9, -3.7, -1.7, -5.6 | [-6.9, -2.2] | second term wins | yes | yes | **yes** | yes |
| CHB-MIT | cbramod | lp - lp_randinit | +4.6 ± 1.2 | +5.1, +3.2, +1.1, +5.2, +8.4 | [+2.0, +7.0] | first term wins | +5.5 | +5.9, +9.3, +3.1, +4.1, +4.9 | [+3.5, +7.7] | first term wins | yes | yes | **yes** | yes |
| CHB-MIT | cbramod | D17 | +0.1 ± 0.5 | +0.2, +0.6, -1.8, +1.2, +0.5 | [-1.1, +1.4] | random features explain it | +1.0 | +2.3, +1.8, -0.5, +2.3, -0.8 | [-0.5, +2.6] | random features explain it | yes | yes | **yes** | yes |
| Siena | biot | last - lp | +9.0 ± 2.3 | +13.7, +0.6, +12.3, +8.3, +10.2 | [+4.6, +12.6] | first term wins | +9.2 | +7.5, +18.3, +3.4, +10.0, +7.0 | [+4.6, +15.7] | first term wins | yes | yes | **yes** | yes |
| Siena | biot | last_randinit - last | +5.7 ± 9.5 | -13.3, +27.7, -20.6, +18.3, +16.6 | [-11.5, +22.2] | no difference shown | +7.2 | -7.7, +28.1, +6.4, +15.5, -6.3 | [-4.4, +19.6] | no difference shown | yes | yes | **yes** | yes |
| Siena | biot | lp - lp_randinit | -14.7 ± 7.9 | -0.1, -28.2, +8.7, -26.8, -27.0 | [-28.2, -0.2] | second term wins | -16.1 | +1.1, -45.7, -9.1, -26.5, -0.3 | [-33.2, -1.7] | second term wins | yes | yes | **yes** | yes |
| Siena | biot | D17 | +0.1 ± 0.1 | +0.3, +0.1, +0.4, -0.2, -0.2 | [-0.4, +0.5] | random features explain it | +0.3 | +0.9, +0.7, +0.7, -1.0, +0.4 | [-0.4, +1.0] | random features explain it | yes | yes | **yes** | yes |
| Siena | cbramod | last - lp | +0.2 ± 0.2 | -0.1, -0.1, -0.0, +0.8, +0.5 | [-0.1, +0.6] | no difference shown | +0.3 | -0.5, +0.3, +0.5, +1.0, +0.0 | [-0.6, +0.8] | no difference shown | yes | yes | **yes** | yes |
| Siena | cbramod | last_randinit - last | -9.9 ± 2.4 | -12.8, -17.7, -5.4, -5.4, -8.5 | [-14.7, -5.5] | second term wins | -7.6 | -6.6, -2.9, -13.4, -2.2, -13.0 | [-12.8, -3.0] | second term wins | yes | yes | **yes** | yes |
| Siena | cbramod | lp - lp_randinit | +12.4 ± 2.4 | +15.7, +19.9, +10.4, +6.3, +9.5 | [+7.6, +17.3] | first term wins | +7.0 | +4.8, +0.3, +14.7, -0.0, +15.2 | [+0.9, +13.7] | first term wins | yes | yes | **yes** | no |
| Siena | cbramod | D17 | +2.6 ± 0.6 | +2.9, +2.1, +5.0, +1.8, +1.5 | [+0.6, +5.5] | random features explain it | -0.4 | -2.2, -2.3, +1.8, -1.3, +2.2 | [-2.3, +1.7] | random features explain it | yes | yes | **yes** | no |

For D17 the CI is that of last_randinit - lp_randinit (the D17 difference).

## Arms (descriptive)

| dataset, model | arm | E32 mean ± SEM (rot) | E32 per rotation | D24-A mean ± SEM | D24-A per rotation |
|---|---|---|---|---|---|
| CHB-MIT, biot | lp | 61.0 ± 6.2 | 53.4, 76.0, 56.0, 44.5, 75.1 | 65.1 ± 7.9 | 61.0, 63.6, 90.0, 40.9, 69.9 |
| CHB-MIT, biot | lp_randinit | 72.6 ± 5.5 | 59.6, 80.1, 60.6, 74.9, 87.7 | 67.0 ± 5.1 | 54.5, 61.8, 85.1, 64.0, 69.7 |
| CHB-MIT, biot | last | 64.6 ± 5.4 | 54.7, 78.4, 56.1, 56.7, 77.2 | 67.0 ± 8.3 | 62.6, 66.6, 90.9, 39.8, 74.9 |
| CHB-MIT, biot | last_randinit | 72.4 ± 5.5 | 59.6, 79.6, 60.2, 75.0, 87.9 | 67.1 ± 5.2 | 54.3, 62.0, 85.1, 64.2, 70.1 |
| CHB-MIT, cbramod | lp | 82.4 ± 4.8 | 73.3, 84.6, 69.4, 93.5, 91.5 | 81.6 ± 3.3 | 72.0, 83.8, 88.9, 75.9, 87.6 |
| CHB-MIT, cbramod | lp_randinit | 77.9 ± 4.1 | 68.2, 81.4, 68.3, 88.3, 83.1 | 76.2 ± 3.6 | 66.0, 74.6, 85.7, 71.8, 82.7 |
| CHB-MIT, cbramod | last | 82.4 ± 4.9 | 73.1, 84.6, 69.2, 93.5, 91.7 | 81.6 ± 3.4 | 71.5, 84.3, 88.9, 75.8, 87.5 |
| CHB-MIT, cbramod | last_randinit | 78.0 ± 4.5 | 68.3, 82.0, 66.6, 89.5, 83.6 | 77.2 ± 3.0 | 68.3, 76.4, 85.2, 74.2, 81.9 |
| Siena, biot | lp | 50.7 ± 4.2 | 64.6, 43.9, 51.9, 40.2, 53.2 | 51.3 ± 6.4 | 64.0, 36.3, 60.1, 35.0, 61.3 |
| Siena, biot | lp_randinit | 65.4 ± 6.2 | 64.6, 72.0, 43.2, 67.0, 80.3 | 67.4 ± 3.9 | 62.9, 81.9, 69.2, 61.5, 61.6 |
| Siena, biot | last | 59.8 ± 6.1 | 78.2, 44.5, 64.2, 48.5, 63.4 | 60.6 ± 4.8 | 71.5, 54.6, 63.5, 45.0, 68.3 |
| Siena, biot | last_randinit | 65.5 ± 6.1 | 64.9, 72.2, 43.6, 66.8, 80.1 | 67.8 ± 4.0 | 63.8, 82.7, 69.8, 60.5, 62.0 |
| Siena, cbramod | lp | 83.9 ± 3.0 | 93.3, 79.9, 76.3, 87.9, 82.3 | 81.4 ± 2.4 | 81.8, 79.8, 75.0, 80.8, 89.6 |
| Siena, cbramod | lp_randinit | 71.6 ± 3.9 | 77.5, 60.0, 65.9, 81.6, 72.9 | 74.4 ± 3.7 | 77.0, 79.6, 60.3, 80.8, 74.4 |
| Siena, cbramod | last | 84.2 ± 3.1 | 93.2, 79.8, 76.3, 88.8, 82.8 | 81.7 ± 2.3 | 81.3, 80.2, 75.6, 81.7, 89.7 |
| Siena, cbramod | last_randinit | 74.2 ± 3.7 | 80.4, 62.1, 70.9, 83.4, 74.4 | 74.0 ± 3.1 | 74.7, 77.3, 62.1, 79.5, 76.6 |

## Partition, CHB-MIT (descriptive)

| rotation | S1R test subjects | n test windows | positive windows | S1R val subjects | S1E,S1M test subjects | shared test subjects |
|---|---|---|---|---|---|---|
| rot0 | chb06, chb16, chb20, chb22 | 51,957 | 98 | chb02, chb05, chb07, chb14 | chb10, chb11, chb15, chb18 | 0 |
| rot1 | chb02, chb05, chb07, chb14 | 59,874 | 133 | chb08, chb09, chb15, chb23 | chb01, chb08, chb09, chb19 | 0 |
| rot2 | chb08, chb09, chb15, chb23 | 55,592 | 391 | chb04, chb10, chb11, chb19 | chb02, chb05, chb07, chb16 | 0 |
| rot3 | chb04, chb10, chb11, chb19 | 97,481 | 201 | chb01, chb03, chb18, chb24 | chb06, chb14, chb23, chb24 | 0 |
| rot4 | chb01, chb03, chb18, chb24 | 60,124 | 222 | chb06, chb16, chb20, chb22 | chb03, chb04, chb20, chb22 | 1 |

## Partition, Siena (descriptive)

| rotation | S3R test subjects | n test windows | positive windows | S3R val subjects | S3E,S3M test subjects | shared test subjects |
|---|---|---|---|---|---|---|
| rot0 | PN09, PN13, PN17 | 7,426 | 68 | PN05, PN07, PN16 | PN05, PN12, PN13 | 1 |
| rot1 | PN05, PN07, PN16 | 7,071 | 46 | PN01, PN10, PN11 | PN01, PN03, PN16 | 1 |
| rot2 | PN01, PN10, PN11 | 12,461 | 69 | PN06, PN12, PN14 | PN00, PN07, PN11 | 1 |
| rot3 | PN06, PN12, PN14 | 13,904 | 83 | PN00, PN03 | PN06, PN10, PN14 | 2 |
| rot4 | PN00, PN03 | 9,887 | 63 | PN09, PN13, PN17 | PN09, PN17 | 0 |
