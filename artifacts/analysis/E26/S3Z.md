# D24, siena, tags S3Z: ROC-AUC x100, eval-mode probe, encoder tap

## biot, linear_z head
- lp: per-rotation seed means 68.3, 76.5, 74.3, 68.1, 64.2; over rotations 70.3 ± 2.2 (n=5); over runs (seeds not independent) 70.3 ± 2.2 (n=5)
- lp_randinit: per-rotation seed means 57.8, 86.3, 65.0, 71.7, 67.7; over rotations 69.7 ± 4.7 (n=5); over runs (seeds not independent) 69.7 ± 4.7 (n=5)
- last: per-rotation seed means 68.5, 77.1, 74.3, 67.8, 67.5; over rotations 71.1 ± 2.0 (n=5); over runs (seeds not independent) 71.1 ± 2.0 (n=5)
- last_randinit: per-rotation seed means 57.8, 86.3, 64.9, 71.6, 67.7; over rotations 69.7 ± 4.7 (n=5); over runs (seeds not independent) 69.7 ± 4.7 (n=5)
- all: INCOMPLETE, seeds per rotation [0, 0, 0, 0, 0]
- SA helps? last - lp: mean +0.8, per rotation +0.2, +0.6, +0.1, -0.3, +3.3 -> **no difference shown**
- random init beats pretrained? last_randinit - last: mean -1.4, per rotation -10.7, +9.1, -9.4, +3.8, +0.3 -> **no difference shown**
- pretrained features beat random? lp - lp_randinit: mean +0.6, per rotation +10.5, -9.8, +9.2, -3.6, -3.5 -> **no difference shown**
- D17: **random features explain it**
## cbramod, linear_z head
- lp: per-rotation seed means 75.6, 80.3, 76.8, 84.0, 77.4; over rotations 78.8 ± 1.5 (n=5); over runs (seeds not independent) 78.8 ± 1.5 (n=5)
- lp_randinit: per-rotation seed means 72.2, 83.2, 43.4, 77.5, 74.9; over rotations 70.2 ± 6.9 (n=5); over runs (seeds not independent) 70.2 ± 6.9 (n=5)
- last: per-rotation seed means 76.6, 81.8, 76.8, 84.9, 78.1; over rotations 79.6 ± 1.6 (n=5); over runs (seeds not independent) 79.6 ± 1.6 (n=5)
- last_randinit: per-rotation seed means 71.9, 83.2, 43.4, 77.5, 74.9; over rotations 70.2 ± 7.0 (n=5); over runs (seeds not independent) 70.2 ± 7.0 (n=5)
- all: INCOMPLETE, seeds per rotation [0, 0, 0, 0, 0]
- SA helps? last - lp: mean +0.8, per rotation +1.0, +1.5, -0.1, +0.9, +0.7 -> **no difference shown**
- random init beats pretrained? last_randinit - last: mean -9.4, per rotation -4.7, +1.4, -33.4, -7.4, -3.2 -> **second term wins**
- pretrained features beat random? lp - lp_randinit: mean +8.6, per rotation +3.4, -2.9, +33.4, +6.5, +2.5 -> **first term wins**
- D17: **random features explain it**

