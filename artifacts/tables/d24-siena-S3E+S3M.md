# D24, siena, tags S3E,S3M: ROC-AUC x100, eval-mode probe, encoder tap

## biot, linear head
- lp: per-rotation seed means 64.0, 36.3, 60.1, 35.0, 61.3; over rotations 51.3 ± 6.4 (n=5); over runs (seeds not independent) 51.3 ± 3.6 (n=15)
- lp_randinit: per-rotation seed means 62.9, 81.9, 69.2, 61.5, 61.6; over rotations 67.4 ± 3.9 (n=5); over runs (seeds not independent) 67.4 ± 2.3 (n=15)
- last: per-rotation seed means 71.5, 54.6, 63.5, 45.0, 68.3; over rotations 60.6 ± 4.8 (n=5); over runs (seeds not independent) 60.6 ± 2.8 (n=15)
- last_randinit: per-rotation seed means 63.8, 82.7, 69.8, 60.5, 62.0; over rotations 67.8 ± 4.0 (n=5); over runs (seeds not independent) 67.8 ± 2.3 (n=15)
- all: per-rotation seed means 70.8, 65.6, 69.0, 67.0, 83.4; over rotations 71.2 ± 3.2 (n=5); over runs (seeds not independent) 71.2 ± 2.6 (n=15)
- SA helps? last - lp: mean +9.2, per rotation +7.5, +18.3, +3.4, +10.0, +7.0 -> **first term wins**
- random init beats pretrained? last_randinit - last: mean +7.2, per rotation -7.7, +28.1, +6.4, +15.5, -6.3 -> **no difference shown**
- pretrained features beat random? lp - lp_randinit: mean -16.1, per rotation +1.1, -45.7, -9.1, -26.5, -0.3 -> **second term wins**
- D17: **random features explain it**
- all - last (reference): +10.6
## cbramod, linear head
- lp: per-rotation seed means 81.8, 79.8, 75.0, 80.8, 89.6; over rotations 81.4 ± 2.4 (n=5); over runs (seeds not independent) 81.4 ± 1.3 (n=15)
- lp_randinit: per-rotation seed means 77.0, 79.6, 60.3, 80.8, 74.4; over rotations 74.4 ± 3.7 (n=5); over runs (seeds not independent) 74.4 ± 2.4 (n=15)
- last: per-rotation seed means 81.3, 80.2, 75.6, 81.7, 89.7; over rotations 81.7 ± 2.3 (n=5); over runs (seeds not independent) 81.7 ± 1.2 (n=15)
- last_randinit: per-rotation seed means 74.7, 77.3, 62.1, 79.5, 76.6; over rotations 74.0 ± 3.1 (n=5); over runs (seeds not independent) 74.0 ± 2.2 (n=15)
- all: per-rotation seed means 87.2, 85.4, 69.5, 88.9, 87.5; over rotations 83.7 ± 3.6 (n=5); over runs (seeds not independent) 83.7 ± 1.9 (n=15)
- SA helps? last - lp: mean +0.3, per rotation -0.5, +0.3, +0.5, +1.0, +0.0 -> **no difference shown**
- random init beats pretrained? last_randinit - last: mean -7.6, per rotation -6.6, -2.9, -13.4, -2.2, -13.0 -> **second term wins**
- pretrained features beat random? lp - lp_randinit: mean +7.0, per rotation +4.8, +0.3, +14.7, -0.0, +15.2 -> **first term wins**
- D17: **random features explain it**
- all - last (reference): +2.0
