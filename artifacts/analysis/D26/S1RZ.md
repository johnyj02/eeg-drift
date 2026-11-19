# D24, chbmit, tags S1RZ: ROC-AUC x100, eval-mode probe, encoder tap

## biot, linear_z head
- lp: per-rotation seed means 63.9, 81.1, 67.5, 71.9, 78.5; over rotations 72.6 ± 3.2 (n=5); over runs (seeds not independent) 72.6 ± 1.8 (n=15)
- lp_randinit: per-rotation seed means 59.4, 83.7, 66.5, 81.3, 88.8; over rotations 75.9 ± 5.6 (n=5); over runs (seeds not independent) 75.9 ± 3.0 (n=15)
- last: per-rotation seed means 64.6, 82.4, 65.9, 73.6, 80.0; over rotations 73.3 ± 3.6 (n=5); over runs (seeds not independent) 73.3 ± 1.9 (n=15)
- last_randinit: per-rotation seed means 59.3, 83.7, 66.4, 81.3, 88.8; over rotations 75.9 ± 5.6 (n=5); over runs (seeds not independent) 75.9 ± 3.0 (n=15)
- all: INCOMPLETE, seeds per rotation [0, 0, 0, 0, 0]
- SA helps? last - lp: mean +0.7, per rotation +0.7, +1.3, -1.6, +1.7, +1.5 -> **no difference shown**
- random init beats pretrained? last_randinit - last: mean +2.6, per rotation -5.3, +1.3, +0.6, +7.7, +8.8 -> **no difference shown**
- pretrained features beat random? lp - lp_randinit: mean -3.4, per rotation +4.5, -2.6, +1.0, -9.4, -10.3 -> **no difference shown**
- D17: **random features explain it**
## cbramod, linear_z head
- lp: per-rotation seed means 64.6, 81.3, 64.6, 91.3, 86.8; over rotations 77.7 ± 5.6 (n=5); over runs (seeds not independent) 77.7 ± 3.1 (n=15)
- lp_randinit: per-rotation seed means 65.3, 80.7, 69.3, 88.6, 80.4; over rotations 76.9 ± 4.2 (n=5); over runs (seeds not independent) 76.9 ± 2.3 (n=15)
- last: per-rotation seed means 65.0, 83.2, 63.6, 90.9, 85.7; over rotations 77.7 ± 5.6 (n=5); over runs (seeds not independent) 77.7 ± 3.1 (n=15)
- last_randinit: per-rotation seed means 65.3, 80.7, 69.3, 88.6, 80.1; over rotations 76.8 ± 4.2 (n=5); over runs (seeds not independent) 76.8 ± 2.3 (n=15)
- all: INCOMPLETE, seeds per rotation [0, 0, 0, 0, 0]
- SA helps? last - lp: mean -0.0, per rotation +0.4, +1.9, -0.9, -0.4, -1.1 -> **no difference shown**
- random init beats pretrained? last_randinit - last: mean -0.9, per rotation +0.4, -2.5, +5.7, -2.3, -5.5 -> **no difference shown**
- pretrained features beat random? lp - lp_randinit: mean +0.8, per rotation -0.7, +0.6, -4.7, +2.7, +6.4 -> **no difference shown**
- D17: **random features explain it**
