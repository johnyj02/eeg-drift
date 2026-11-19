# D24, siena, tags S3FZ: ROC-AUC x100, eval-mode probe, encoder tap

## biot, linear_z head
- lp: per-rotation seed means 85.5, 76.9, 74.3, 72.6, 58.8; over rotations 73.6 ± 4.3 (n=5); over runs (seeds not independent) 73.6 ± 4.3 (n=5)
- lp_randinit: per-rotation seed means 60.9, 88.1, 74.4, 76.3, 70.5; over rotations 74.1 ± 4.4 (n=5); over runs (seeds not independent) 74.1 ± 4.4 (n=5)
- last: per-rotation seed means 85.7, 77.7, 74.3, 72.9, 59.3; over rotations 74.0 ± 4.3 (n=5); over runs (seeds not independent) 74.0 ± 4.3 (n=5)
- last_randinit: per-rotation seed means 54.0, 88.2, 74.5, 76.0, 70.4; over rotations 72.6 ± 5.5 (n=5); over runs (seeds not independent) 72.6 ± 5.5 (n=5)
- all: INCOMPLETE, seeds per rotation [0, 0, 0, 0, 0]
- SA helps? last - lp: mean +0.4, per rotation +0.2, +0.9, -0.1, +0.3, +0.5 -> **no difference shown**
- random init beats pretrained? last_randinit - last: mean -1.4, per rotation -31.7, +10.4, +0.2, +3.1, +11.1 -> **no difference shown**
- pretrained features beat random? lp - lp_randinit: mean -0.4, per rotation +24.6, -11.3, -0.1, -3.7, -11.7 -> **no difference shown**
- D17: **random features explain it**
## cbramod, linear_z head
- lp: per-rotation seed means 85.5, 88.2, 76.0, 81.4, 79.2; over rotations 82.1 ± 2.2 (n=5); over runs (seeds not independent) 82.1 ± 2.2 (n=5)
- lp_randinit: per-rotation seed means 69.5, 78.2, 63.6, 79.6, 75.1; over rotations 73.2 ± 3.0 (n=5); over runs (seeds not independent) 73.2 ± 3.0 (n=5)
- last: per-rotation seed means 85.6, 88.3, 75.5, 81.5, 80.3; over rotations 82.3 ± 2.2 (n=5); over runs (seeds not independent) 82.3 ± 2.2 (n=5)
- last_randinit: per-rotation seed means 69.2, 78.2, 63.6, 78.9, 75.2; over rotations 73.0 ± 2.9 (n=5); over runs (seeds not independent) 73.0 ± 2.9 (n=5)
- all: INCOMPLETE, seeds per rotation [0, 0, 0, 0, 0]
- SA helps? last - lp: mean +0.2, per rotation +0.2, +0.1, -0.4, +0.2, +1.1 -> **no difference shown**
- random init beats pretrained? last_randinit - last: mean -9.2, per rotation -16.4, -10.1, -11.9, -2.6, -5.1 -> **second term wins**
- pretrained features beat random? lp - lp_randinit: mean +8.8, per rotation +16.0, +10.0, +12.4, +1.8, +4.1 -> **first term wins**
- D17: **random features explain it**
