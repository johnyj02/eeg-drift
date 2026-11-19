# Step 1 (S3F): corrected protocol, ROC-AUC x100 (PR-AUC in brackets)

| model | arm | rot0 | rot1 | rot2 | rot3 | rot4 | mean |
|---|---|---|---|---|---|---|---|
| biot | lp | 87.4 (15.8) | 42.4 (1.3) | 69.8 (1.9) | 70.8 (1.6) | 73.4 (4.7) | 68.8 |
| biot | last | 87.6 (10.8) | 57.2 (1.8) | 67.6 (1.6) | 76.6 (3.8) | 74.1 (6.7) | 72.6 |
| biot | first | 76.7 (2.0) | 80.3 (9.0) | 78.5 (3.1) | 71.9 (3.3) | 76.9 (15.2) | 76.9 |
| biot | first_block | 81.3 (5.2) | 81.5 (9.9) | 77.4 (3.2) | 73.2 (5.2) | 77.9 (13.4) | 78.3 |
| biot | embed_only | 83.8 (4.1) | 56.0 (1.6) | 74.0 (2.3) | 68.1 (4.0) | 61.0 (1.3) | 68.6 |
| biot | first_noise | 81.4 (3.1) | 49.1 (2.0) | 63.4 (2.1) | 73.1 (3.9) | 88.5 (21.9) | 71.1 |
| biot | all | 73.4 (1.7) | 85.4 (2.6) | 58.8 (1.2) | 82.0 (11.0) | 78.5 (6.2) | 75.6 |
| biot | last_randinit | 58.7 (1.1) | 90.4 (13.2) | 64.8 (2.2) | 70.7 (10.3) | 65.0 (1.5) | 69.9 |
| biot | lp_randinit | 57.9 (1.1) | 90.1 (13.5) | 63.2 (2.3) | 70.6 (10.5) | 63.9 (1.5) | 69.1 |
| cbramod | lp | 54.4 (1.1) | 59.2 (28.2) | 43.8 (0.9) | 56.4 (9.4) | 44.4 (0.8) | 51.6 |
| cbramod | last | 69.2 (2.2) | 74.3 (20.8) | 50.0 (1.1) | 61.6 (9.7) | 65.3 (1.4) | 64.1 |
| cbramod | first | 47.3 (0.9) | 73.6 (3.0) | 38.3 (0.8) | 34.8 (10.2) | 35.5 (3.2) | 45.9 |
| cbramod | first_block | 54.0 (1.0) | 68.1 (9.9) | 38.6 (0.7) | 46.5 (8.7) | 51.3 (0.9) | 51.7 |
| cbramod | embed_only | 55.4 (1.0) | 76.7 (4.3) | 34.9 (0.8) | 41.0 (10.4) | 48.8 (0.8) | 51.4 |
| cbramod | first_noise | 48.0 (0.9) | 73.3 (2.8) | 38.2 (0.8) | 35.7 (10.3) | 33.7 (3.2) | 45.8 |
| cbramod | all | 24.4 (0.6) | 57.2 (9.3) | 36.9 (0.7) | 29.7 (5.8) | 30.2 (0.6) | 35.7 |
| cbramod | last_randinit | 76.8 (2.9) | 83.2 (15.8) | 74.6 (2.3) | 83.5 (15.9) | 86.1 (25.1) | 80.8 |
| cbramod | lp_randinit | 77.6 (3.2) | 86.3 (13.2) | 74.8 (2.3) | 85.3 (15.3) | 85.2 (27.2) | 81.8 |

## Verdicts (D17, D18)
- biot primary: first - last: mean +4.2, per rotation -10.9, +23.1, +11.0, -4.7, +2.8 -> **no difference shown**
- biot depth, equal params: first_block - last: mean +5.6, per rotation -6.3, +24.3, +9.8, -3.4, +3.7 -> **no difference shown**
- biot embedding alone: embed_only - lp: mean -0.2, per rotation -3.5, +13.6, +4.2, -2.6, -12.4 -> **no difference shown**
- biot needs EEG data: first - first_noise: mean +5.8, per rotation -4.7, +31.2, +15.2, -1.2, -11.6 -> **unclear**
- biot Paper A: last - lp: mean +3.9, per rotation +0.3, +14.8, -2.3, +5.8, +0.7 -> **first term wins**
- biot Paper A: last_randinit - last: mean -2.7, per rotation -29.0, +33.1, -2.8, -5.9, -9.1 -> **no difference shown**
- biot all - last (reference): mean +3.0
- biot D17: **random features explain it**
- cbramod primary: first - last: mean -18.2, per rotation -21.9, -0.7, -11.8, -26.8, -29.8 -> **second term wins**
- cbramod depth, equal params: first_block - last: mean -12.4, per rotation -15.2, -6.2, -11.5, -15.1, -14.0 -> **second term wins**
- cbramod embedding alone: embed_only - lp: mean -0.2, per rotation +1.1, +17.6, -8.9, -15.4, +4.5 -> **no difference shown**
- cbramod needs EEG data: first - first_noise: mean +0.1, per rotation -0.7, +0.3, +0.1, -0.8, +1.8 -> **perturbation alone explains it**
- cbramod Paper A: last - lp: mean +12.5, per rotation +14.8, +15.2, +6.2, +5.2, +20.9 -> **first term wins**
- cbramod Paper A: last_randinit - last: mean +16.7, per rotation +7.6, +8.8, +24.6, +21.9, +20.8 -> **first term wins**
- cbramod all - last (reference): mean -28.4
- cbramod D17: **random features explain it**
