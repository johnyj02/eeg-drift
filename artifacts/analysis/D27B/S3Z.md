# D24, siena, tags S3Z: ROC-AUC x100, eval-mode probe, encoder tap

## biot, linear_z head
- lp: per-rotation seed means 66.0, 75.0, 67.2, 67.0, 67.7; over rotations 68.6 ± 1.6 (n=5); over runs (seeds not independent) 68.6 ± 2.2 (n=15)
- lp_randinit: per-rotation seed means 62.1, 85.9, 70.1, 73.1, 72.5; over rotations 72.8 ± 3.8 (n=5); over runs (seeds not independent) 72.8 ± 2.2 (n=15)
- last: per-rotation seed means 66.9, 74.9, 68.7, 71.0, 69.7; over rotations 70.2 ± 1.3 (n=5); over runs (seeds not independent) 70.2 ± 2.0 (n=15)
- last_randinit: per-rotation seed means 62.1, 86.0, 70.0, 73.1, 72.7; over rotations 72.8 ± 3.8 (n=5); over runs (seeds not independent) 72.8 ± 2.2 (n=15)
- all: INCOMPLETE, seeds per rotation [0, 0, 0, 0, 0]
- SA helps? last - lp: mean +1.7, per rotation +0.9, -0.2, +1.5, +4.0, +2.0 -> **no difference shown**
- random init beats pretrained? last_randinit - last: mean +2.5, per rotation -4.8, +11.1, +1.3, +2.2, +2.9 -> **no difference shown**
- pretrained features beat random? lp - lp_randinit: mean -4.2, per rotation +3.9, -10.9, -2.8, -6.1, -4.8 -> **second term wins**
- D17: **random features explain it**
## cbramod, linear_z head
- lp: per-rotation seed means 75.2, 83.7, 76.0, 83.9, 75.9; over rotations 78.9 ± 2.0 (n=5); over runs (seeds not independent) 78.9 ± 1.2 (n=15)
- lp_randinit: per-rotation seed means 66.5, 79.6, 57.0, 77.4, 70.0; over rotations 70.1 ± 4.0 (n=5); over runs (seeds not independent) 70.1 ± 2.8 (n=15)
- last: per-rotation seed means 75.5, 82.7, 75.9, 82.7, 76.6; over rotations 78.7 ± 1.7 (n=5); over runs (seeds not independent) 78.7 ± 1.1 (n=15)
- last_randinit: per-rotation seed means 66.4, 79.6, 57.0, 77.3, 70.0; over rotations 70.1 ± 4.0 (n=5); over runs (seeds not independent) 70.1 ± 2.8 (n=15)
- all: INCOMPLETE, seeds per rotation [0, 0, 0, 0, 0]
- SA helps? last - lp: mean -0.3, per rotation +0.3, -1.0, -0.2, -1.2, +0.7 -> **no difference shown**
- random init beats pretrained? last_randinit - last: mean -8.6, per rotation -9.0, -3.1, -18.9, -5.4, -6.6 -> **second term wins**
- pretrained features beat random? lp - lp_randinit: mean +8.8, per rotation +8.6, +4.1, +19.0, +6.5, +5.9 -> **first term wins**
- D17: **random features explain it**
