# D24, siena, tags S3FZ: ROC-AUC x100, eval-mode probe, encoder tap

## biot, linear_z head
- lp: per-rotation seed means 76.6, 74.2, 76.6, 77.5, 61.5; over rotations 73.3 ± 3.0 (n=5); over runs (seeds not independent) 73.3 ± 2.1 (n=15)
- lp_randinit: per-rotation seed means 63.0, 87.6, 74.4, 71.0, 71.6; over rotations 73.5 ± 4.0 (n=5); over runs (seeds not independent) 73.5 ± 2.2 (n=15)
- last: per-rotation seed means 82.8, 77.9, 76.7, 77.5, 61.2; over rotations 75.2 ± 3.7 (n=5); over runs (seeds not independent) 75.2 ± 2.2 (n=15)
- last_randinit: per-rotation seed means 60.6, 87.6, 74.4, 71.0, 71.7; over rotations 73.0 ± 4.3 (n=5); over runs (seeds not independent) 73.0 ± 2.4 (n=15)
- all: INCOMPLETE, seeds per rotation [0, 0, 0, 0, 0]
- SA helps? last - lp: mean +1.9, per rotation +6.1, +3.7, +0.1, +0.0, -0.3 -> **no difference shown**
- random init beats pretrained? last_randinit - last: mean -2.2, per rotation -22.2, +9.8, -2.3, -6.5, +10.5 -> **no difference shown**
- pretrained features beat random? lp - lp_randinit: mean -0.2, per rotation +13.6, -13.4, +2.2, +6.5, -10.1 -> **no difference shown**
- D17: **random features explain it**
## cbramod, linear_z head
- lp: per-rotation seed means 86.3, 87.6, 76.7, 83.1, 80.2; over rotations 82.8 ± 2.0 (n=5); over runs (seeds not independent) 82.8 ± 1.2 (n=15)
- lp_randinit: per-rotation seed means 67.1, 81.2, 68.7, 77.3, 75.8; over rotations 74.0 ± 2.7 (n=5); over runs (seeds not independent) 74.0 ± 1.7 (n=15)
- last: per-rotation seed means 86.5, 87.6, 77.5, 83.1, 80.9; over rotations 83.1 ± 1.8 (n=5); over runs (seeds not independent) 83.1 ± 1.0 (n=15)
- last_randinit: per-rotation seed means 66.9, 81.2, 68.7, 77.0, 76.0; over rotations 74.0 ± 2.7 (n=5); over runs (seeds not independent) 74.0 ± 1.7 (n=15)
- all: INCOMPLETE, seeds per rotation [0, 0, 0, 0, 0]
- SA helps? last - lp: mean +0.3, per rotation +0.2, -0.0, +0.8, -0.0, +0.7 -> **no difference shown**
- random init beats pretrained? last_randinit - last: mean -9.2, per rotation -19.6, -6.4, -8.8, -6.1, -4.9 -> **second term wins**
- pretrained features beat random? lp - lp_randinit: mean +8.8, per rotation +19.2, +6.5, +8.0, +5.8, +4.4 -> **first term wins**
- D17: **random features explain it**
