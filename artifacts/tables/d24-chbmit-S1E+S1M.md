# D24, chbmit, tags S1E,S1M: ROC-AUC x100, eval-mode probe, encoder tap

## biot, linear head
- lp: per-rotation seed means 61.0, 63.6, 90.0, 40.9, 69.9; over rotations 65.1 ± 7.9 (n=5); over runs (seeds not independent) 65.1 ± 4.2 (n=15)
- lp_randinit: per-rotation seed means 54.5, 61.8, 85.1, 64.0, 69.7; over rotations 67.0 ± 5.1 (n=5); over runs (seeds not independent) 67.0 ± 3.3 (n=15)
- last: per-rotation seed means 62.6, 66.6, 90.9, 39.8, 74.9; over rotations 67.0 ± 8.3 (n=5); over runs (seeds not independent) 67.0 ± 4.5 (n=15)
- last_randinit: per-rotation seed means 54.3, 62.0, 85.1, 64.2, 70.1; over rotations 67.1 ± 5.2 (n=5); over runs (seeds not independent) 67.1 ± 3.4 (n=15)
- all: per-rotation seed means 65.3, 81.2, 94.8, 56.6, 85.9; over rotations 76.8 ± 6.9 (n=5); over runs (seeds not independent) 76.8 ± 3.8 (n=15)
- SA helps? last - lp: mean +1.9, per rotation +1.7, +3.1, +0.9, -1.1, +5.0 -> **no difference shown**
- random init beats pretrained? last_randinit - last: mean +0.2, per rotation -8.3, -4.7, -5.8, +24.4, -4.9 -> **no difference shown**
- pretrained features beat random? lp - lp_randinit: mean -2.0, per rotation +6.5, +1.8, +4.9, -23.1, +0.2 -> **no difference shown**
- D17: **random features explain it**
- all - last (reference): +9.8
## cbramod, linear head
- lp: per-rotation seed means 72.0, 83.8, 88.9, 75.9, 87.6; over rotations 81.6 ± 3.3 (n=5); over runs (seeds not independent) 81.6 ± 1.8 (n=15)
- lp_randinit: per-rotation seed means 66.0, 74.6, 85.7, 71.8, 82.7; over rotations 76.2 ± 3.6 (n=5); over runs (seeds not independent) 76.2 ± 2.0 (n=15)
- last: per-rotation seed means 71.5, 84.3, 88.9, 75.8, 87.5; over rotations 81.6 ± 3.4 (n=5); over runs (seeds not independent) 81.6 ± 1.8 (n=15)
- last_randinit: per-rotation seed means 68.3, 76.4, 85.2, 74.2, 81.9; over rotations 77.2 ± 3.0 (n=5); over runs (seeds not independent) 77.2 ± 1.7 (n=15)
- all: per-rotation seed means 75.8, 85.6, 89.4, 76.3, 89.1; over rotations 83.2 ± 3.0 (n=5); over runs (seeds not independent) 83.2 ± 1.6 (n=15)
- SA helps? last - lp: mean -0.0, per rotation -0.4, +0.5, +0.0, -0.1, -0.1 -> **no difference shown**
- random init beats pretrained? last_randinit - last: mean -4.4, per rotation -3.2, -7.9, -3.7, -1.7, -5.6 -> **second term wins**
- pretrained features beat random? lp - lp_randinit: mean +5.5, per rotation +5.9, +9.3, +3.1, +4.1, +4.9 -> **first term wins**
- D17: **random features explain it**
- all - last (reference): +1.6
