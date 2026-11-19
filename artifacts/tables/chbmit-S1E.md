# Step 1 (S1E): corrected protocol, ROC-AUC x100 (PR-AUC in brackets)

| model | arm | rot0 | rot1 | rot2 | rot3 | rot4 | mean |
|---|---|---|---|---|---|---|---|
| cbramod | lp | 72.2 (28.1) | 83.7 (27.4) | 88.9 (34.5) | 76.3 (10.2) | 87.6 (15.5) | 81.8 |
| cbramod | last | 72.0 (28.0) | 84.4 (27.2) | 89.0 (34.6) | 76.1 (10.3) | 87.5 (15.5) | 81.8 |
| cbramod | first | 72.3 (24.0) | 86.6 (26.5) | 90.1 (42.2) | 76.1 (10.4) | 89.2 (14.6) | 82.9 |
| cbramod | first_block | 67.8 (26.9) | 84.6 (26.9) | 89.1 (44.0) | 76.8 (12.3) | 87.6 (15.4) | 81.2 |
| cbramod | embed_only | 68.1 (26.0) | 85.2 (23.5) | 89.6 (38.9) | 75.5 (10.7) | 88.5 (13.7) | 81.4 |
| cbramod | first_noise | 74.4 (24.5) | 87.1 (27.6) | 90.8 (44.1) | 76.6 (10.2) | 88.7 (17.4) | 83.5 |
| cbramod | all | 76.9 (25.8) | 85.6 (15.6) | 89.4 (36.7) | 76.5 (13.0) | 88.9 (12.3) | 83.5 |
| cbramod | last_randinit | 70.0 (7.0) | 80.4 (6.0) | 83.9 (12.0) | 74.8 (8.5) | 85.6 (1.2) | 78.9 |
| cbramod | lp_randinit | 65.1 (6.8) | 76.9 (5.4) | 84.9 (10.1) | 75.2 (6.7) | 84.1 (1.0) | 77.2 |

## Verdicts (D17, D18)
- cbramod primary: first - last: mean +1.1, per rotation +0.3, +2.2, +1.1, -0.0, +1.7 -> **no difference shown**
- cbramod depth, equal params: first_block - last: mean -0.6, per rotation -4.2, +0.2, +0.2, +0.6, +0.1 -> **no difference shown**
- cbramod embedding alone: embed_only - lp: mean -0.4, per rotation -4.2, +1.6, +0.7, -0.9, +0.8 -> **no difference shown**
- cbramod needs EEG data: first - first_noise: mean -0.6, per rotation -2.0, -0.4, -0.8, -0.5, +0.5 -> **perturbation alone explains it**
- cbramod Paper A: last - lp: mean +0.1, per rotation -0.2, +0.7, +0.1, -0.2, -0.1 -> **no difference shown**
- cbramod Paper A: last_randinit - last: mean -2.9, per rotation -2.0, -4.0, -5.1, -1.3, -1.9 -> **no difference shown**
- cbramod all - last (reference): mean +1.7
- cbramod D17: **random features explain it**
