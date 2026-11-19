# Step 1 (S3): corrected protocol, ROC-AUC x100 (PR-AUC in brackets)

| model | arm | rot0 | rot1 | rot2 | rot3 | rot4 | mean |
|---|---|---|---|---|---|---|---|
| biot | lp | 65.8 (1.9) | 45.2 (0.9) | 68.8 (2.2) | 36.6 (0.4) | 60.7 (1.9) | 55.4 |
| biot | last | 75.4 (3.1) | 61.9 (1.1) | 63.5 (2.2) | 45.9 (2.3) | 65.4 (2.2) | 62.4 |
| biot | first | 70.9 (1.7) | 71.1 (9.2) | 74.6 (9.6) | 43.9 (2.1) | 68.8 (4.5) | 65.9 |
| biot | first_block | 72.8 (1.9) | 71.6 (3.0) | 72.6 (6.0) | 57.4 (4.5) | 72.0 (4.5) | 69.3 |
| biot | embed_only | 62.4 (1.5) | 59.5 (1.0) | 71.1 (4.3) | 31.4 (0.4) | 57.1 (3.1) | 56.3 |
| biot | first_noise | 74.9 (2.4) | 40.8 (2.9) | 62.4 (2.1) | 54.6 (4.5) | 74.9 (7.3) | 61.5 |
| biot | all | 70.8 (1.6) | 79.9 (2.1) | 56.2 (1.2) | 67.6 (4.7) | 79.1 (6.6) | 70.7 |
| biot | last_randinit | 58.2 (1.2) | 84.5 (18.0) | 69.2 (4.1) | 65.3 (10.3) | 62.0 (2.0) | 67.8 |
| biot | lp_randinit | 58.1 (1.2) | 84.4 (17.6) | 68.3 (4.0) | 67.0 (10.5) | 65.9 (1.8) | 68.7 |
| cbramod | lp | 52.8 (1.1) | 73.2 (11.1) | 37.8 (0.7) | 48.6 (11.4) | 42.3 (0.7) | 51.0 |
| cbramod | last | 54.1 (1.1) | 73.5 (7.1) | 36.0 (0.7) | 45.5 (10.3) | 42.9 (0.7) | 50.4 |
| cbramod | first | 40.9 (0.8) | 70.7 (7.7) | 41.0 (0.9) | 31.1 (10.3) | 39.6 (1.1) | 44.7 |
| cbramod | first_block | 46.0 (0.9) | 74.5 (7.9) | 44.5 (0.8) | 43.3 (10.5) | 42.5 (1.1) | 50.2 |
| cbramod | embed_only | 47.0 (0.9) | 54.5 (6.8) | 35.3 (0.7) | 32.9 (10.0) | 40.2 (0.9) | 42.0 |
| cbramod | first_noise | 36.8 (0.8) | 68.1 (4.7) | 39.4 (0.9) | 33.7 (10.3) | 39.0 (1.1) | 43.4 |
| cbramod | all | 37.9 (0.8) | 63.1 (2.9) | 47.9 (1.0) | 35.6 (2.9) | 46.6 (1.1) | 46.2 |
| cbramod | last_randinit | 75.9 (2.3) | 83.2 (9.2) | 49.8 (0.9) | 82.5 (11.7) | 86.4 (16.9) | 75.6 |
| cbramod | lp_randinit | 77.3 (2.3) | 83.2 (8.6) | 51.3 (1.0) | 84.2 (11.8) | 86.3 (15.1) | 76.5 |

## Verdicts (D17, D18)
- biot primary: first - last: mean +3.5, per rotation -4.5, +9.2, +11.1, -2.0, +3.4 -> **no difference shown**
- biot depth, equal params: first_block - last: mean +6.9, per rotation -2.5, +9.7, +9.1, +11.5, +6.6 -> **first term wins**
- biot embedding alone: embed_only - lp: mean +0.9, per rotation -3.4, +14.3, +2.4, -5.2, -3.6 -> **no difference shown**
- biot needs EEG data: first - first_noise: mean +4.4, per rotation -3.9, +30.3, +12.2, -10.7, -6.1 -> **unclear**
- biot Paper A: last - lp: mean +7.0, per rotation +9.6, +16.7, -5.2, +9.4, +4.7 -> **first term wins**
- biot Paper A: last_randinit - last: mean +5.4, per rotation -17.2, +22.6, +5.7, +19.4, -3.4 -> **no difference shown**
- biot all - last (reference): mean +8.3
- biot D17: **random features explain it**
- cbramod primary: first - last: mean -5.7, per rotation -13.2, -2.8, +5.0, -14.4, -3.3 -> **second term wins**
- cbramod depth, equal params: first_block - last: mean -0.2, per rotation -8.1, +1.0, +8.5, -2.2, -0.4 -> **no difference shown**
- cbramod embedding alone: embed_only - lp: mean -9.0, per rotation -5.9, -18.7, -2.5, -15.8, -2.0 -> **second term wins**
- cbramod needs EEG data: first - first_noise: mean +1.3, per rotation +4.1, +2.6, +1.6, -2.6, +0.7 -> **perturbation alone explains it**
- cbramod Paper A: last - lp: mean -0.5, per rotation +1.3, +0.3, -1.8, -3.1, +0.6 -> **no difference shown**
- cbramod Paper A: last_randinit - last: mean +25.1, per rotation +21.7, +9.7, +13.7, +37.0, +43.5 -> **first term wins**
- cbramod all - last (reference): mean -4.2
- cbramod D17: **random features explain it**
