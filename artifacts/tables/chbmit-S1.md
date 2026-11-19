# Step 1 (S1): corrected protocol, ROC-AUC x100 (PR-AUC in brackets)

| model | arm | rot0 | rot1 | rot2 | rot3 | rot4 | mean |
|---|---|---|---|---|---|---|---|
| biot | lp | 52.9 (0.7) | 60.0 (0.4) | 91.0 (3.8) | 43.7 (0.7) | 65.9 (0.2) | 62.7 |
| biot | last | 56.1 (0.8) | 64.7 (0.5) | 91.0 (18.9) | 42.9 (1.4) | 73.4 (0.3) | 65.6 |
| biot | first | 59.4 (0.9) | 65.7 (0.5) | 89.7 (44.4) | 52.5 (6.5) | 81.7 (1.1) | 69.8 |
| biot | first_block | 54.0 (0.7) | 66.1 (1.7) | 88.2 (9.9) | 46.2 (0.4) | 78.7 (0.6) | 66.6 |
| biot | embed_only | 63.2 (1.1) | 53.1 (0.4) | 88.8 (34.6) | 53.0 (6.3) | 68.7 (0.5) | 65.4 |
| biot | first_noise | 63.8 (1.3) | 64.5 (0.5) | 79.6 (8.2) | 55.3 (2.8) | 76.2 (0.5) | 67.9 |
| biot | all | 60.3 (1.4) | 76.2 (0.9) | 93.7 (50.1) | 53.4 (0.8) | 88.8 (3.5) | 74.5 |
| biot | last_randinit | 54.7 (6.7) | 57.2 (14.0) | 84.1 (17.9) | 63.0 (6.5) | 48.2 (2.4) | 61.5 |
| biot | lp_randinit | 54.7 (6.6) | 57.3 (14.7) | 84.3 (17.7) | 62.7 (6.5) | 48.9 (2.3) | 61.6 |

## Verdicts (D17, D18)
- biot primary: first - last: mean +4.2, per rotation +3.2, +1.1, -1.3, +9.6, +8.3 -> **first term wins**
- biot depth, equal params: first_block - last: mean +1.0, per rotation -2.2, +1.4, -2.8, +3.3, +5.3 -> **no difference shown**
- biot embedding alone: embed_only - lp: mean +2.7, per rotation +10.3, -6.9, -2.2, +9.3, +2.9 -> **no difference shown**
- biot needs EEG data: first - first_noise: mean +1.9, per rotation -4.4, +1.2, +10.1, -2.8, +5.5 -> **perturbation alone explains it**
- biot Paper A: last - lp: mean +2.9, per rotation +3.2, +4.7, -0.0, -0.8, +7.6 -> **no difference shown**
- biot Paper A: last_randinit - last: mean -4.2, per rotation -1.4, -7.5, -6.9, +20.1, -25.2 -> **second term wins**
- biot all - last (reference): mean +8.9
- biot D17: **random features explain it**
