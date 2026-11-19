# D25-E33b: Siena published-style split 'pub' (test PN13/14/16/17, val PN10/12)

Pre-registered (decisions.md D25 additions): descriptive, one split; no verdict rule.
ROC-AUC x100, linear head, eval-mode probe, encoder tap. pub = mean +/- SEM over 3 seeds (42/1000/2000; SEM is seed noise only, one fixed split). D24 = mean +/- SEM over 5 rotation seed-means (S3E+S3M / S3FE+S3FM). test_last and the 3/3 flag are post hoc.

## Checks

- S3P: 18 records = 2 models x 3 arms x 3 seeds, exactly 1 per cell
  eval_hash 94a5fcd57beffff8 (one for both models), labels overlap, versions {"adapt": 3, "probe": 4} and probe/adapt/arm specs = S3E,S3M, SSL data_hash 76fd53cf3be317f5 (10 subjects), test ['PN13', 'PN14', 'PN16', 'PN17'] n=14083 pos=90, val ['PN10', 'PN12']
- S3FP: 18 records = 2 models x 3 arms x 3 seeds, exactly 1 per cell
  eval_hash 40c74d7a8e77222c (one for both models), labels overlap, versions {"adapt": 3, "probe": 4} and probe/adapt/arm specs = S3FE,S3FM, SSL data_hash 76fd53cf3be317f5 (10 subjects), test ['PN13', 'PN14', 'PN16', 'PN17'] n=14083 pos=90, val ['PN10', 'PN12']
- S3P and S3FP test on the same 14,083 window keys (filtered signal, different eval_hash)

## Results

| setting | model | quantity | pub mean ± SEM (3 seeds) | pub per seed (42/1000/2000) | pub test_last (post hoc) | 3/3 flag (post hoc) | D24 5-rot mean ± SEM | D24 per rotation | D24 verdict | pub inside D24 range? |
|---|---|---|---|---|---|---|---|---|---|---|
| Siena | biot | lp | 50.7 ± 2.7 | 48.9, 47.3, 56.0 | 50.7 ± 2.7 |  | 51.3 ± 6.4 | 64.0, 36.3, 60.1, 35.0, 61.3 |  | yes [35.0, 64.0] |
| Siena | biot | last | 58.2 ± 4.0 | 55.6, 52.9, 66.0 | 58.2 ± 4.0 |  | 60.6 ± 4.8 | 71.5, 54.6, 63.5, 45.0, 68.3 |  | yes [45.0, 71.5] |
| Siena | biot | lp_randinit | 60.6 ± 18.0 | 24.9, 82.1, 74.8 | 60.1 ± 15.6 |  | 67.4 ± 3.9 | 62.9, 81.9, 69.2, 61.5, 61.6 |  | NO [61.5, 81.9] |
| Siena | biot | last - lp | +7.4 ± 1.3 | +6.7, +5.6, +9.9 | +7.4 ± 1.3 | 3/3 +, >3 | +9.2 ± 2.5 | +7.5, +18.3, +3.4, +10.0, +7.0 | first term wins | yes [+3.4, +18.3] |
| Siena | biot | lp - lp_randinit | -9.8 ± 17.6 | +24.0, -34.8, -18.7 | -9.4 ± 15.0 | - | -16.1 ± 8.9 | +1.1, -45.7, -9.1, -26.5, -0.3 | second term wins | yes [-45.7, +1.1] |
| Siena | cbramod | lp | 83.4 ± 0.4 | 83.3, 84.1, 82.8 | 83.0 ± 0.1 |  | 81.4 ± 2.4 | 81.8, 79.8, 75.0, 80.8, 89.6 |  | yes [75.0, 89.6] |
| Siena | cbramod | last | 83.8 ± 0.4 | 83.5, 84.6, 83.4 | 83.5 ± 0.1 |  | 81.7 ± 2.3 | 81.3, 80.2, 75.6, 81.7, 89.7 |  | yes [75.6, 89.7] |
| Siena | cbramod | lp_randinit | 72.0 ± 2.9 | 76.4, 72.9, 66.6 | 70.9 ± 1.5 |  | 74.4 ± 3.7 | 77.0, 79.6, 60.3, 80.8, 74.4 |  | yes [60.3, 80.8] |
| Siena | cbramod | last - lp | +0.4 ± 0.1 | +0.2, +0.5, +0.6 | +0.5 ± 0.0 | - | +0.3 ± 0.2 | -0.5, +0.3, +0.5, +1.0, +0.0 | no difference shown | yes [-0.5, +1.0] |
| Siena | cbramod | lp - lp_randinit | +11.4 ± 2.7 | +6.8, +11.2, +16.2 | +12.1 ± 1.5 | 3/3 +, >3 | +7.0 ± 3.4 | +4.8, +0.3, +14.7, -0.0, +15.2 | first term wins | yes [-0.0, +15.2] |
| Siena filtered | biot | lp | 75.6 ± 1.2 | 75.7, 73.5, 77.8 | 75.6 ± 1.2 |  | 69.8 ± 6.8 | 85.0, 44.3, 73.3, 72.9, 73.3 |  | yes [44.3, 85.0] |
| Siena filtered | biot | last | 80.4 ± 0.9 | 80.4, 78.9, 81.9 | 81.3 ± 0.4 |  | 73.9 ± 5.5 | 86.3, 53.2, 74.1, 77.9, 77.7 |  | yes [53.2, 86.3] |
| Siena filtered | biot | lp_randinit | 83.1 ± 1.1 | 82.0, 85.2, 82.0 | 82.2 ± 0.1 |  | 68.8 ± 5.4 | 61.7, 90.5, 64.1, 64.0, 63.7 |  | yes [61.7, 90.5] |
| Siena filtered | biot | last - lp | +4.8 ± 0.4 | +4.7, +5.4, +4.2 | +5.6 ± 1.1 | 3/3 +, >3 | +4.1 ± 1.5 | +1.3, +8.9, +0.9, +5.0, +4.4 | first term wins | yes [+0.9, +8.9] |
| Siena filtered | biot | lp - lp_randinit | -7.4 ± 2.2 | -6.4, -11.7, -4.2 | -6.6 ± 1.3 | 3/3 -, < -3 | +1.0 ± 12.1 | +23.3, -46.2, +9.2, +8.9, +9.6 | no difference shown | yes [-46.2, +23.3] |
| Siena filtered | cbramod | lp | 91.2 ± 0.0 | 91.2, 91.2, 91.2 | 91.0 ± 0.0 |  | 89.5 ± 2.3 | 91.9, 89.4, 81.1, 90.5, 94.5 |  | yes [81.1, 94.5] |
| Siena filtered | cbramod | last | 91.3 ± 0.1 | 91.4, 91.2, 91.2 | 91.0 ± 0.0 |  | 89.6 ± 2.3 | 92.2, 89.3, 81.3, 90.7, 94.6 |  | yes [81.3, 94.6] |
| Siena filtered | cbramod | lp_randinit | 83.0 ± 1.5 | 85.1, 83.8, 80.1 | 79.1 ± 1.3 |  | 80.0 ± 2.3 | 75.7, 82.7, 73.8, 85.7, 82.2 |  | yes [73.8, 85.7] |
| Siena filtered | cbramod | last - lp | +0.0 ± 0.0 | +0.1, -0.0, -0.0 | +0.1 ± 0.0 | - | +0.1 ± 0.1 | +0.3, -0.1, +0.2, +0.2, +0.1 | no difference shown | yes [-0.1, +0.3] |
| Siena filtered | cbramod | lp - lp_randinit | +8.2 ± 1.5 | +6.2, +7.3, +11.1 | +11.8 ± 1.2 | 3/3 +, >3 | +9.4 ± 2.1 | +16.2, +6.7, +7.3, +4.8, +12.3 | first term wins | yes [+4.8, +16.2] |

Verdict (pre-registered): descriptive only (one split); no rule is applied to these numbers.
