# D24, chbmit, tags S1FM: ROC-AUC x100, eval-mode probe, encoder tap

## biot, linear head
- lp: per-rotation seed means 64.3, 63.5, 92.7, 42.4, 70.3; over rotations 66.6 ± 8.0 (n=5); over runs (seeds not independent) 66.6 ± 4.3 (n=15)
- lp_randinit: per-rotation seed means 54.4, 62.1, 83.7, 62.6, 68.4; over rotations 66.2 ± 4.9 (n=5); over runs (seeds not independent) 66.2 ± 3.3 (n=15)
- last: per-rotation seed means 63.6, 66.5, 93.0, 41.6, 75.0; over rotations 67.9 ± 8.3 (n=5); over runs (seeds not independent) 67.9 ± 4.5 (n=15)
- last_randinit: per-rotation seed means 54.1, 62.2, 83.8, 62.5, 68.8; over rotations 66.3 ± 5.0 (n=5); over runs (seeds not independent) 66.3 ± 3.3 (n=15)
- all: per-rotation seed means 62.8, 82.6, 95.1, 55.3, 87.8; over rotations 76.7 ± 7.6 (n=5); over runs (seeds not independent) 76.7 ± 4.1 (n=15)
- SA helps? last - lp: mean +1.3, per rotation -0.7, +3.0, +0.3, -0.8, +4.7 -> **no difference shown**
- random init beats pretrained? last_randinit - last: mean -1.6, per rotation -9.4, -4.3, -9.2, +20.9, -6.2 -> **no difference shown**
- pretrained features beat random? lp - lp_randinit: mean +0.4, per rotation +9.9, +1.4, +9.0, -20.2, +1.9 -> **no difference shown**
- D17: **random features explain it**
- all - last (reference): +8.8
## biot, mlp_fullft head
- lp: per-rotation seed means 65.8, 65.7, 93.1, 46.1, 72.2; over rotations 68.6 ± 7.5 (n=5); over runs (seeds not independent) 68.6 ± 4.0 (n=15)
- lp_randinit: per-rotation seed means 66.5, 64.8, 89.2, 63.1, 70.8; over rotations 70.9 ± 4.8 (n=5); over runs (seeds not independent) 70.9 ± 3.7 (n=15)
- last: per-rotation seed means 65.2, 68.3, 93.2, 44.9, 74.3; over rotations 69.2 ± 7.8 (n=5); over runs (seeds not independent) 69.2 ± 4.2 (n=15)
- last_randinit: per-rotation seed means 66.7, 65.1, 89.0, 63.4, 71.1; over rotations 71.0 ± 4.7 (n=5); over runs (seeds not independent) 71.0 ± 3.6 (n=15)
- all: per-rotation seed means 62.7, 82.0, 95.1, 47.7, 89.5; over rotations 75.4 ± 8.8 (n=5); over runs (seeds not independent) 75.4 ± 4.8 (n=15)
- SA helps? last - lp: mean +0.6, per rotation -0.6, +2.6, +0.1, -1.2, +2.1 -> **no difference shown**
- random init beats pretrained? last_randinit - last: mean +1.9, per rotation +1.5, -3.1, -4.2, +18.5, -3.2 -> **no difference shown**
- pretrained features beat random? lp - lp_randinit: mean -2.3, per rotation -0.6, +0.9, +3.9, -17.0, +1.4 -> **no difference shown**
- D17: **random features explain it**
- all - last (reference): +6.2
## cbramod, linear head
- lp: per-rotation seed means 75.8, 85.1, 89.2, 74.9, 88.4; over rotations 82.7 ± 3.1 (n=5); over runs (seeds not independent) 82.7 ± 1.6 (n=15)
- lp_randinit: per-rotation seed means 70.1, 76.1, 85.2, 74.2, 81.5; over rotations 77.4 ± 2.7 (n=5); over runs (seeds not independent) 77.4 ± 1.6 (n=15)
- last: per-rotation seed means 75.5, 85.3, 89.3, 74.8, 88.7; over rotations 82.7 ± 3.2 (n=5); over runs (seeds not independent) 82.7 ± 1.7 (n=15)
- last_randinit: per-rotation seed means 75.1, 76.8, 85.6, 73.9, 82.4; over rotations 78.7 ± 2.2 (n=5); over runs (seeds not independent) 78.7 ± 1.5 (n=15)
- all: per-rotation seed means 77.9, 86.7, 88.3, 75.5, 90.6; over rotations 83.8 ± 3.0 (n=5); over runs (seeds not independent) 83.8 ± 1.6 (n=15)
- SA helps? last - lp: mean +0.0, per rotation -0.3, +0.2, +0.1, -0.1, +0.3 -> **no difference shown**
- random init beats pretrained? last_randinit - last: mean -3.9, per rotation -0.4, -8.5, -3.7, -0.9, -6.3 -> **second term wins**
- pretrained features beat random? lp - lp_randinit: mean +5.2, per rotation +5.7, +9.0, +4.0, +0.7, +6.8 -> **first term wins**
- D17: **random features explain it**
- all - last (reference): +1.1
## cbramod, mlp_fullft head
- lp: per-rotation seed means 79.7, 85.9, 91.8, 72.1, 93.5; over rotations 84.6 ± 4.0 (n=5); over runs (seeds not independent) 84.6 ± 2.1 (n=15)
- lp_randinit: per-rotation seed means 68.3, 81.2, 89.6, 77.9, 84.7; over rotations 80.3 ± 3.6 (n=5); over runs (seeds not independent) 80.3 ± 1.9 (n=15)
- last: per-rotation seed means 81.6, 85.8, 91.3, 71.0, 93.4; over rotations 84.6 ± 4.0 (n=5); over runs (seeds not independent) 84.6 ± 2.1 (n=15)
- last_randinit: per-rotation seed means 69.2, 79.5, 89.3, 76.8, 84.0; over rotations 79.8 ± 3.4 (n=5); over runs (seeds not independent) 79.8 ± 1.9 (n=15)
- all: per-rotation seed means 85.1, 87.0, 87.5, 72.0, 89.9; over rotations 84.3 ± 3.2 (n=5); over runs (seeds not independent) 84.3 ± 1.7 (n=15)
- SA helps? last - lp: mean +0.1, per rotation +1.9, -0.1, -0.4, -1.1, -0.1 -> **no difference shown**
- random init beats pretrained? last_randinit - last: mean -4.9, per rotation -12.5, -6.3, -2.0, +5.8, -9.4 -> **second term wins**
- pretrained features beat random? lp - lp_randinit: mean +4.2, per rotation +11.4, +4.6, +2.2, -5.8, +8.8 -> **first term wins**
- D17: **random features explain it**
- all - last (reference): -0.3

