# Step 1 (S3E): corrected protocol, ROC-AUC x100 (PR-AUC in brackets)

| model | arm | rot0 | rot1 | rot2 | rot3 | rot4 | mean |
|---|---|---|---|---|---|---|---|
| cbramod | lp | 78.8 (2.2) | 80.0 (3.0) | 75.0 (8.2) | 80.6 (13.2) | 89.6 (25.6) | 80.8 |
| cbramod | last | 80.2 (2.3) | 80.3 (3.1) | 75.5 (6.8) | 81.6 (13.4) | 89.7 (27.6) | 81.5 |
| cbramod | first | 83.5 (2.9) | 82.3 (2.4) | 76.7 (4.4) | 86.1 (18.3) | 88.1 (22.6) | 83.3 |
| cbramod | first_block | 80.8 (2.3) | 78.6 (3.5) | 76.0 (6.8) | 83.3 (14.9) | 90.4 (28.4) | 81.8 |
| cbramod | embed_only | 82.2 (2.7) | 84.2 (3.2) | 76.5 (5.2) | 84.4 (14.9) | 90.0 (25.1) | 83.5 |
| cbramod | first_noise | 86.9 (4.0) | 81.0 (2.3) | 75.6 (3.8) | 86.6 (19.7) | 88.9 (23.1) | 83.8 |
| cbramod | all | 85.1 (3.3) | 85.6 (3.7) | 69.3 (2.6) | 88.9 (20.9) | 87.5 (19.9) | 83.3 |
| cbramod | last_randinit | 74.5 (2.2) | 79.6 (7.0) | 53.2 (1.3) | 81.4 (8.2) | 78.7 (9.5) | 73.5 |
| cbramod | lp_randinit | 75.1 (2.3) | 79.8 (7.1) | 52.6 (1.1) | 83.2 (6.4) | 80.0 (9.4) | 74.1 |

## Verdicts (D17, D18)
- cbramod primary: first - last: mean +1.9, per rotation +3.3, +2.0, +1.2, +4.5, -1.6 -> **no difference shown**
- cbramod depth, equal params: first_block - last: mean +0.4, per rotation +0.6, -1.7, +0.5, +1.7, +0.7 -> **no difference shown**
- cbramod embedding alone: embed_only - lp: mean +2.6, per rotation +3.4, +4.2, +1.5, +3.7, +0.4 -> **no difference shown**
- cbramod needs EEG data: first - first_noise: mean -0.4, per rotation -3.3, +1.3, +1.0, -0.4, -0.7 -> **perturbation alone explains it**
- cbramod Paper A: last - lp: mean +0.6, per rotation +1.4, +0.3, +0.5, +1.0, +0.1 -> **no difference shown**
- cbramod Paper A: last_randinit - last: mean -8.0, per rotation -5.8, -0.7, -22.3, -0.3, -11.0 -> **second term wins**
- cbramod all - last (reference): mean +1.8
- cbramod D17: **random features explain it**
