# D24, siena, tags S3FE,S3FM: ROC-AUC x100, eval-mode probe, encoder tap

## biot, linear head
- lp: per-rotation seed means 85.0, 44.3, 73.3, 72.9, 73.3; over rotations 69.8 ± 6.8 (n=5); over runs (seeds not independent) 69.8 ± 3.6 (n=15)
- lp_randinit: per-rotation seed means 61.7, 90.5, 64.1, 64.0, 63.7; over rotations 68.8 ± 5.4 (n=5); over runs (seeds not independent) 68.8 ± 3.0 (n=15)
- last: per-rotation seed means 86.3, 53.2, 74.1, 77.9, 77.7; over rotations 73.9 ± 5.5 (n=5); over runs (seeds not independent) 73.9 ± 3.0 (n=15)
- last_randinit: per-rotation seed means 62.0, 90.3, 64.9, 64.1, 64.6; over rotations 69.2 ± 5.3 (n=5); over runs (seeds not independent) 69.2 ± 3.0 (n=15)
- all: per-rotation seed means 70.6, 71.9, 67.7, 81.3, 80.0; over rotations 74.3 ± 2.7 (n=5); over runs (seeds not independent) 74.3 ± 1.8 (n=15)
- SA helps? last - lp: mean +4.1, per rotation +1.3, +8.9, +0.9, +5.0, +4.4 -> **first term wins**
- random init beats pretrained? last_randinit - last: mean -4.7, per rotation -24.3, +37.1, -9.3, -13.8, -13.2 -> **second term wins**
- pretrained features beat random? lp - lp_randinit: mean +1.0, per rotation +23.3, -46.2, +9.2, +8.9, +9.6 -> **no difference shown**
- D17: **random features explain it**
- all - last (reference): +0.4
## cbramod, linear head
- lp: per-rotation seed means 91.9, 89.4, 81.1, 90.5, 94.5; over rotations 89.5 ± 2.3 (n=5); over runs (seeds not independent) 89.5 ± 1.2 (n=15)
- lp_randinit: per-rotation seed means 75.7, 82.7, 73.8, 85.7, 82.2; over rotations 80.0 ± 2.3 (n=5); over runs (seeds not independent) 80.0 ± 1.6 (n=15)
- last: per-rotation seed means 92.2, 89.3, 81.3, 90.7, 94.6; over rotations 89.6 ± 2.3 (n=5); over runs (seeds not independent) 89.6 ± 1.2 (n=15)
- last_randinit: per-rotation seed means 77.0, 81.5, 72.9, 85.5, 77.7; over rotations 78.9 ± 2.1 (n=5); over runs (seeds not independent) 78.9 ± 1.8 (n=15)
- all: per-rotation seed means 91.1, 89.5, 77.9, 92.5, 93.2; over rotations 88.8 ± 2.8 (n=5); over runs (seeds not independent) 88.8 ± 1.5 (n=15)
- SA helps? last - lp: mean +0.1, per rotation +0.3, -0.1, +0.2, +0.2, +0.1 -> **no difference shown**
- random init beats pretrained? last_randinit - last: mean -10.7, per rotation -15.3, -7.7, -8.3, -5.2, -16.9 -> **second term wins**
- pretrained features beat random? lp - lp_randinit: mean +9.4, per rotation +16.2, +6.7, +7.3, +4.8, +12.3 -> **first term wins**
- D17: **random features explain it**
- all - last (reference): -0.8
