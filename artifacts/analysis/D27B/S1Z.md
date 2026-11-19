# D24, chbmit, tags S1Z: ROC-AUC x100, eval-mode probe, encoder tap

## biot, linear_z head
- lp: per-rotation seed means 48.6, 83.1, 87.9, 65.2, 76.4; over rotations 72.3 ± 7.0 (n=5); over runs (seeds not independent) 72.3 ± 3.8 (n=15)
- lp_randinit: per-rotation seed means 61.9, 65.9, 88.6, 63.3, 82.8; over rotations 72.5 ± 5.5 (n=5); over runs (seeds not independent) 72.5 ± 3.2 (n=15)
- last: per-rotation seed means 48.3, 83.5, 89.5, 64.1, 76.5; over rotations 72.4 ± 7.4 (n=5); over runs (seeds not independent) 72.4 ± 4.0 (n=15)
- last_randinit: per-rotation seed means 61.8, 66.0, 88.7, 63.3, 82.7; over rotations 72.5 ± 5.5 (n=5); over runs (seeds not independent) 72.5 ± 3.2 (n=15)
- all: INCOMPLETE, seeds per rotation [0, 0, 0, 0, 0]
- SA helps? last - lp: mean +0.1, per rotation -0.4, +0.4, +1.6, -1.1, +0.1 -> **no difference shown**
- random init beats pretrained? last_randinit - last: mean +0.1, per rotation +13.5, -17.5, -0.8, -0.9, +6.3 -> **no difference shown**
- pretrained features beat random? lp - lp_randinit: mean -0.2, per rotation -13.3, +17.2, -0.7, +2.0, -6.4 -> **no difference shown**
- D17: **random features explain it**
## cbramod, linear_z head
- lp: per-rotation seed means 77.5, 83.9, 90.7, 65.2, 79.2; over rotations 79.3 ± 4.2 (n=5); over runs (seeds not independent) 79.3 ± 2.3 (n=15)
- lp_randinit: per-rotation seed means 67.7, 75.4, 85.1, 69.2, 73.0; over rotations 74.1 ± 3.1 (n=5); over runs (seeds not independent) 74.1 ± 1.9 (n=15)
- last: per-rotation seed means 79.0, 83.1, 91.1, 65.9, 79.4; over rotations 79.7 ± 4.1 (n=5); over runs (seeds not independent) 79.7 ± 2.2 (n=15)
- last_randinit: per-rotation seed means 67.6, 75.3, 85.1, 69.3, 73.4; over rotations 74.1 ± 3.1 (n=5); over runs (seeds not independent) 74.1 ± 1.9 (n=15)
- all: INCOMPLETE, seeds per rotation [0, 0, 0, 0, 0]
- SA helps? last - lp: mean +0.4, per rotation +1.5, -0.7, +0.4, +0.7, +0.2 -> **no difference shown**
- random init beats pretrained? last_randinit - last: mean -5.6, per rotation -11.4, -7.8, -5.9, +3.4, -6.0 -> **second term wins**
- pretrained features beat random? lp - lp_randinit: mean +5.2, per rotation +9.9, +8.5, +5.5, -4.0, +6.2 -> **first term wins**
- D17: **random features explain it**
