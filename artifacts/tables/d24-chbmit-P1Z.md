# D24, chbmit, tags P1Z: ROC-AUC x100, eval-mode probe, encoder tap

## biot, linear_z head
- lp: 79.1 ± 1.8 (n=5)
- lp_randinit: 88.4 ± 0.4 (n=5)
- last: 79.3 ± 1.9 (n=5)
- last_randinit: 88.4 ± 0.5 (n=5)
- SA helps? last - lp: 0.2 ± 0.8 (n=5), per seed -0.8, -1.0, -0.2, -0.5, +3.4 -> **no difference shown**
- random init beats pretrained? last_randinit - last: 9.1 ± 1.6 (n=5), per seed +11.4, +6.4, +7.3, +14.4, +5.9 -> (descriptive, not pre-registered)
- pretrained features beat random? lp - lp_randinit: -9.3 ± 1.5 (n=5), per seed -10.6, -5.4, -7.1, -13.9, -9.2 -> (descriptive, not pre-registered)
## cbramod, linear_z head
- lp: 88.5 ± 0.4 (n=5)
- lp_randinit: 85.1 ± 1.2 (n=5)
- last: 88.6 ± 0.4 (n=5)
- last_randinit: 85.0 ± 1.2 (n=5)
- SA helps? last - lp: 0.2 ± 0.1 (n=5), per seed +0.4, +0.2, +0.3, -0.0, +0.0 -> **no difference shown**
- random init beats pretrained? last_randinit - last: -3.6 ± 1.2 (n=5), per seed -0.4, -3.9, -7.8, -2.1, -3.7 -> (descriptive, not pre-registered)
- pretrained features beat random? lp - lp_randinit: 3.4 ± 1.2 (n=5), per seed +0.0, +3.6, +7.5, +2.2, +3.6 -> (descriptive, not pre-registered)
