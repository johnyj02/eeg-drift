# D24, siena, tags S3RZ: ROC-AUC x100, eval-mode probe, encoder tap

## biot, linear_z head
- lp: per-rotation seed means 50.9, 74.0, 63.2, 81.1, 77.8; over rotations 69.4 ± 5.5 (n=5); over runs (seeds not independent) 69.4 ± 3.7 (n=15)
- lp_randinit: per-rotation seed means 78.1, 73.1, 50.8, 72.3, 80.4; over rotations 70.9 ± 5.3 (n=5); over runs (seeds not independent) 70.9 ± 2.9 (n=15)
- last: per-rotation seed means 52.6, 72.8, 69.8, 82.0, 78.3; over rotations 71.1 ± 5.1 (n=5); over runs (seeds not independent) 71.1 ± 3.4 (n=15)
- last_randinit: per-rotation seed means 78.2, 73.1, 50.8, 72.4, 80.4; over rotations 71.0 ± 5.3 (n=5); over runs (seeds not independent) 71.0 ± 2.9 (n=15)
- all: INCOMPLETE, seeds per rotation [0, 0, 0, 0, 0]
- SA helps? last - lp: mean +1.7, per rotation +1.7, -1.2, +6.7, +0.9, +0.5 -> **no difference shown**
- random init beats pretrained? last_randinit - last: mean -0.1, per rotation +25.6, +0.4, -19.0, -9.6, +2.1 -> **no difference shown**
- pretrained features beat random? lp - lp_randinit: mean -1.6, per rotation -27.3, +0.9, +12.4, +8.8, -2.6 -> **no difference shown**
- D17: **random features explain it**
## cbramod, linear_z head
- lp: per-rotation seed means 79.6, 78.7, 71.9, 87.9, 82.9; over rotations 80.2 ± 2.6 (n=5); over runs (seeds not independent) 80.2 ± 1.6 (n=15)
- lp_randinit: per-rotation seed means 71.1, 64.0, 65.3, 76.8, 71.3; over rotations 69.7 ± 2.3 (n=5); over runs (seeds not independent) 69.7 ± 1.8 (n=15)
- last: per-rotation seed means 80.2, 77.9, 70.5, 88.2, 82.9; over rotations 79.9 ± 2.9 (n=5); over runs (seeds not independent) 79.9 ± 1.7 (n=15)
- last_randinit: per-rotation seed means 71.1, 64.0, 65.3, 76.6, 71.2; over rotations 69.6 ± 2.3 (n=5); over runs (seeds not independent) 69.6 ± 1.8 (n=15)
- all: INCOMPLETE, seeds per rotation [0, 0, 0, 0, 0]
- SA helps? last - lp: mean -0.3, per rotation +0.6, -0.8, -1.3, +0.3, -0.0 -> **no difference shown**
- random init beats pretrained? last_randinit - last: mean -10.3, per rotation -9.1, -13.9, -5.2, -11.6, -11.6 -> **second term wins**
- pretrained features beat random? lp - lp_randinit: mean +10.5, per rotation +8.4, +14.7, +6.6, +11.1, +11.5 -> **first term wins**
- D17: **random features explain it**
