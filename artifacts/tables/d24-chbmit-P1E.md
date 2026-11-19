# D24, chbmit, tags P1E: ROC-AUC x100, eval-mode probe, encoder tap

## biot, linear head
- lp: 55.0 ± 0.4 (n=5)
- lp_randinit: 90.1 ± 0.2 (n=5)
- last: 54.4 ± 1.1 (n=5)
- last_randinit: 90.2 ± 0.2 (n=5)
- SA helps? last - lp: -0.6 ± 1.2 (n=5), per seed -2.0, +1.8, -4.3, -0.1, +1.6 -> **no difference shown**
- random init beats pretrained? last_randinit - last: 35.8 ± 1.0 (n=5), per seed +36.7, +33.0, +38.8, +35.9, +34.5 -> (descriptive, not pre-registered)
- pretrained features beat random? lp - lp_randinit: -35.1 ± 0.3 (n=5), per seed -34.7, -34.7, -34.6, -35.7, -35.9 -> (descriptive, not pre-registered)
## biot, mlp_fullft head
- lp: 56.1 ± 0.1 (n=5)
- lp_randinit: 88.5 ± 0.2 (n=5)
- last: 54.9 ± 1.2 (n=5)
- last_randinit: 88.5 ± 0.2 (n=5)
- SA helps? last - lp: -1.2 ± 1.2 (n=5), per seed -3.2, -0.4, -4.7, -0.0, +2.3 -> **no difference shown**
- random init beats pretrained? last_randinit - last: 33.6 ± 1.2 (n=5), per seed +35.4, +33.1, +36.7, +33.1, +29.7 -> (descriptive, not pre-registered)
- pretrained features beat random? lp - lp_randinit: -32.4 ± 0.2 (n=5), per seed -32.4, -32.6, -31.6, -33.1, -32.3 -> (descriptive, not pre-registered)
## cbramod, linear head
- lp: 92.0 ± 0.0 (n=5)
- lp_randinit: 85.6 ± 0.7 (n=5)
- last: 92.0 ± 0.1 (n=5)
- last_randinit: 83.5 ± 0.3 (n=5)
- SA helps? last - lp: 0.0 ± 0.0 (n=5), per seed -0.0, +0.0, +0.0, +0.0, +0.0 -> **no difference shown**
- random init beats pretrained? last_randinit - last: -8.5 ± 0.3 (n=5), per seed -8.8, -9.4, -7.9, -8.7, -7.7 -> (descriptive, not pre-registered)
- pretrained features beat random? lp - lp_randinit: 6.4 ± 0.7 (n=5), per seed +4.2, +8.8, +6.0, +6.3, +6.8 -> (descriptive, not pre-registered)
## cbramod, mlp_fullft head
- lp: 91.7 ± 0.3 (n=5)
- lp_randinit: 89.5 ± 0.4 (n=5)
- last: 91.7 ± 0.2 (n=5)
- last_randinit: 89.7 ± 0.9 (n=5)
- SA helps? last - lp: 0.0 ± 0.1 (n=5), per seed +0.1, -0.5, +0.2, +0.3, +0.1 -> **no difference shown**
- random init beats pretrained? last_randinit - last: -2.0 ± 1.0 (n=5), per seed -0.5, -3.9, -1.6, +0.6, -4.6 -> (descriptive, not pre-registered)
- pretrained features beat random? lp - lp_randinit: 2.2 ± 0.6 (n=5), per seed +1.0, +3.2, +2.5, +0.7, +3.4 -> (descriptive, not pre-registered)
