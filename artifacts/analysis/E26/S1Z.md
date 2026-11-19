# D24, chbmit, tags S1Z: ROC-AUC x100, eval-mode probe, encoder tap

## biot, linear_z head
- lp: per-rotation seed means 49.9, 81.4, 88.3, 67.7, 77.0; over rotations 72.9 ± 6.6 (n=5); over runs (seeds not independent) 72.9 ± 6.6 (n=5)
- lp_randinit: per-rotation seed means 61.0, 60.8, 88.1, 62.7, 86.3; over rotations 71.8 ± 6.3 (n=5); over runs (seeds not independent) 71.8 ± 6.3 (n=5)
- last: per-rotation seed means 50.0, 81.7, 89.3, 66.8, 77.4; over rotations 73.0 ± 6.8 (n=5); over runs (seeds not independent) 73.0 ± 6.8 (n=5)
- last_randinit: per-rotation seed means 60.8, 61.0, 88.1, 62.8, 86.2; over rotations 71.8 ± 6.3 (n=5); over runs (seeds not independent) 71.8 ± 6.3 (n=5)
- all: INCOMPLETE, seeds per rotation [0, 0, 0, 0, 0]
- SA helps? last - lp: mean +0.2, per rotation +0.1, +0.3, +1.0, -1.0, +0.4 -> **no difference shown**
- random init beats pretrained? last_randinit - last: mean -1.3, per rotation +10.7, -20.7, -1.1, -4.0, +8.8 -> **no difference shown**
- pretrained features beat random? lp - lp_randinit: mean +1.1, per rotation -11.0, +20.6, +0.2, +5.0, -9.2 -> **no difference shown**
- D17: **random features explain it**
## cbramod, linear_z head
- lp: per-rotation seed means 78.9, 83.8, 90.2, 61.9, 80.8; over rotations 79.1 ± 4.7 (n=5); over runs (seeds not independent) 79.1 ± 4.7 (n=5)
- lp_randinit: per-rotation seed means 70.1, 79.8, 84.0, 70.0, 81.2; over rotations 77.0 ± 2.9 (n=5); over runs (seeds not independent) 77.0 ± 2.9 (n=5)
- last: per-rotation seed means 78.9, 84.0, 90.6, 62.6, 81.0; over rotations 79.4 ± 4.6 (n=5); over runs (seeds not independent) 79.4 ± 4.6 (n=5)
- last_randinit: per-rotation seed means 70.1, 79.9, 84.0, 70.1, 81.4; over rotations 77.1 ± 2.9 (n=5); over runs (seeds not independent) 77.1 ± 2.9 (n=5)
- all: INCOMPLETE, seeds per rotation [0, 0, 0, 0, 0]
- SA helps? last - lp: mean +0.3, per rotation +0.1, +0.1, +0.4, +0.7, +0.2 -> **no difference shown**
- random init beats pretrained? last_randinit - last: mean -2.3, per rotation -8.8, -4.1, -6.6, +7.5, +0.4 -> **no difference shown**
- pretrained features beat random? lp - lp_randinit: mean +2.1, per rotation +8.8, +4.0, +6.1, -8.1, -0.4 -> **no difference shown**
- D17: **random features explain it**

