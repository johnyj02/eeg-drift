# Step 1 (S3FE): corrected protocol, ROC-AUC x100 (PR-AUC in brackets)

| model | arm | rot0 | rot1 | rot2 | rot3 | rot4 | mean |
|---|---|---|---|---|---|---|---|
| cbramod | lp | 91.5 (17.2) | 89.4 (30.0) | 81.2 (9.2) | 90.4 (24.9) | 94.5 (49.4) | 89.4 |
| cbramod | last | 91.9 (22.4) | 89.3 (28.3) | 81.4 (9.8) | 90.7 (25.2) | 94.6 (50.8) | 89.5 |
| cbramod | first | 82.8 (2.9) | 87.5 (5.2) | 77.1 (5.6) | 89.7 (26.8) | 93.1 (45.8) | 86.0 |
| cbramod | first_block | 93.2 (31.9) | 88.3 (20.5) | 78.0 (9.0) | 91.8 (24.4) | 94.5 (53.6) | 89.1 |
| cbramod | embed_only | 93.2 (33.8) | 89.2 (8.0) | 80.2 (7.3) | 89.7 (27.3) | 94.6 (45.2) | 89.4 |
| cbramod | first_noise | 84.1 (3.2) | 87.2 (5.5) | 77.9 (5.9) | 91.1 (26.9) | 93.2 (45.5) | 86.7 |
| cbramod | all | 91.3 (36.5) | 89.5 (12.6) | 77.9 (5.3) | 92.5 (27.9) | 93.2 (42.9) | 88.9 |
| cbramod | last_randinit | 74.9 (2.2) | 82.3 (11.6) | 72.2 (2.1) | 87.4 (12.4) | 81.6 (23.4) | 79.7 |
| cbramod | lp_randinit | 75.3 (2.2) | 83.1 (6.5) | 73.3 (2.2) | 87.4 (11.9) | 81.9 (17.0) | 80.2 |

## Verdicts (D17, D18)
- cbramod primary: first - last: mean -3.5, per rotation -9.1, -1.8, -4.2, -1.0, -1.5 -> **second term wins**
- cbramod depth, equal params: first_block - last: mean -0.4, per rotation +1.3, -1.0, -3.4, +1.1, -0.1 -> **no difference shown**
- cbramod embedding alone: embed_only - lp: mean -0.0, per rotation +1.7, -0.2, -1.0, -0.8, +0.1 -> **no difference shown**
- cbramod needs EEG data: first - first_noise: mean -0.7, per rotation -1.3, +0.3, -0.8, -1.4, -0.2 -> **perturbation alone explains it**
- cbramod Paper A: last - lp: mean +0.2, per rotation +0.4, -0.1, +0.2, +0.2, +0.1 -> **no difference shown**
- cbramod Paper A: last_randinit - last: mean -9.9, per rotation -17.0, -7.0, -9.2, -3.3, -12.9 -> **second term wins**
- cbramod all - last (reference): mean -0.7
- cbramod D17: **random features explain it**
