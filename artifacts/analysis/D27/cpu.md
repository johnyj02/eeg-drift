# D27 CPU items: LORO (D27-E), TOST on last - last_noise (D27-A), step-0 SSL loss (D27-E)

Script: scripts/analysis/d27_cpu.py. ROC-AUC x100, eval-mode probe, encoder tap. Post hoc and descriptive; the registered verdicts stay primary.

## 1. Leave-one-rotation-out

Per rotation: mean over its seeds ([S_r, 1000+r, 2000+r]; S_r only where marked 1), as read_d24.py. All 5 rotations: the D18 paired rule (|mean| > 3 and same sign in >= 4 of 5) and D17 (|mean| <= 3: random features explain it; mean > 3 and >= 4 of 5 positive: SSL adds to random init; else neither). **Adaptation for 4 rotations (post hoc choice, made before looking at any LORO output of this script): the same rules with 'same sign in at least 3 of 4' and the same |mean| > 3 (D17: |mean| <= 3; mean > 3 and >= 3 of 4 positive).** This is read_step1.paired / d17 applied to 4 values (their n - 1 sign count). Disclosure: stats_d25.py E10(e) had already printed leave-one-out strings with this rule for the 24 D24-A verdicts (artifacts/analysis/stats/e10-stats.md); they are checked equal below.

Self-checks passed before any row was written:
- artifacts/tables/d24-chbmit-S1E+S1M.md: 8 verdict lines (means, per-rotation values, verdict)
- artifacts/tables/d24-siena-S3E+S3M.md: 8 verdict lines (means, per-rotation values, verdict)
- artifacts/tables/d24-siena-S3FE+S3FM.md: 8 verdict lines (means, per-rotation values, verdict)
- artifacts/analysis/E32/e32.json S1R: 8 verdicts and means
- artifacts/analysis/E32/e32.json S3R: 8 verdicts and means
- artifacts/analysis/D27B/S1Z.md: 8 verdict lines (means, per-rotation values, verdict)
- artifacts/analysis/D27B/S3Z.md: 8 verdict lines (means, per-rotation values, verdict)
- artifacts/analysis/D27B/S3FZ.md: 8 verdict lines (means, per-rotation values, verdict)
- artifacts/analysis/D26/S1RZ.md: 8 verdict lines (means, per-rotation values, verdict)
- artifacts/analysis/D26/S3RZ.md: 8 verdict lines (means, per-rotation values, verdict)
- artifacts/analysis/stats/stats.json E10(e) leave-one-out strings: 24 D24-A verdicts agree

**18 of 80 verdicts change when one rotation is dropped** (25 of 400 drops; D24-A 6 of 24, E32 2 of 16, E26/D27-B 6 of 24, D26 4 of 16):
- D24-A CHB-MIT biot linear random init beats pretrained? last_randinit - last: no difference shown -> without rot3: second term wins (-5.9)
- D24-A CHB-MIT biot linear pretrained features beat random? lp - lp_randinit: no difference shown -> without rot3: first term wins (+3.3)
- D24-A Siena biot linear random init beats pretrained? last_randinit - last: no difference shown -> without rot0: first term wins (+10.9); without rot4: first term wins (+10.6)
- D24-A Siena filtered biot linear SA helps? last - lp: first term wins -> without rot1: no difference shown (+2.9)
- D24-A Siena filtered biot linear random init beats pretrained? last_randinit - last: second term wins -> without rot0: no difference shown (+0.2); without rot3: no difference shown (-2.4); without rot4: no difference shown (-2.6)
- D24-A Siena filtered biot linear pretrained features beat random? lp - lp_randinit: no difference shown -> without rot1: first term wins (+12.8)
- E32 CHB-MIT biot linear SA helps? last - lp: first term wins -> without rot3: no difference shown (+1.5)
- E32 Siena biot linear random init beats pretrained? last_randinit - last: no difference shown -> without rot0: first term wins (+10.5); without rot2: first term wins (+12.3)
- E26/D27-B CHB-MIT biot linear_z random init beats pretrained? last_randinit - last: no difference shown -> without rot0: second term wins (-3.2)
- E26/D27-B CHB-MIT biot linear_z pretrained features beat random? lp - lp_randinit: no difference shown -> without rot1: second term wins (-4.6)
- E26/D27-B Siena biot linear_z random init beats pretrained? last_randinit - last: no difference shown -> without rot0: first term wins (+4.4)
- E26/D27-B Siena biot linear_z pretrained features beat random? lp - lp_randinit: second term wins -> without rot1: no difference shown (-2.5)
- E26/D27-B Siena filtered biot linear_z random init beats pretrained? last_randinit - last: no difference shown -> without rot1: second term wins (-5.1); without rot4: second term wins (-5.3)
- E26/D27-B Siena filtered biot linear_z pretrained features beat random? lp - lp_randinit: no difference shown -> without rot1: first term wins (+3.1)
- D26 CHB-MIT biot linear_z random init beats pretrained? last_randinit - last: no difference shown -> without rot0: first term wins (+4.6); without rot2: first term wins (+3.1)
- D26 CHB-MIT biot linear_z pretrained features beat random? lp - lp_randinit: no difference shown -> without rot0: second term wins (-5.3); without rot2: second term wins (-4.5)
- D26 Siena biot linear_z random init beats pretrained? last_randinit - last: no difference shown -> without rot2: first term wins (+4.6)
- D26 Siena biot linear_z pretrained features beat random? lp - lp_randinit: no difference shown -> without rot0: first term wins (+4.9)

| item | setting | model | head | seeds/rot | contrast | per rotation (rot0..rot4) | 5 rotations | without rot0 | without rot1 | without rot2 | without rot3 | without rot4 | changes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D24-A | CHB-MIT | biot | linear | 3 | SA helps? last - lp | +1.7, +3.1, +0.9, -1.1, +5.0 | +1.9 none | +2.0 none | +1.6 none | +2.2 none | +2.7 none | +1.1 none | 0 |
| D24-A | CHB-MIT | biot | linear | 3 | random init beats pretrained? last_randinit - last | -8.3, -4.7, -5.8, +24.4, -4.9 | +0.2 none | +2.3 none | +1.4 none | +1.6 none | **-5.9 2nd wins** | +1.4 none | 1 |
| D24-A | CHB-MIT | biot | linear | 3 | pretrained features beat random? lp - lp_randinit | +6.5, +1.8, +4.9, -23.1, +0.2 | -2.0 none | -4.1 none | -2.9 none | -3.7 none | **+3.3 1st wins** | -2.5 none | 1 |
| D24-A | CHB-MIT | biot | linear | 3 | D17 | -0.2, +0.2, +0.1, +0.1, +0.4 | +0.1 explains | +0.2 explains | +0.1 explains | +0.1 explains | +0.1 explains | +0.0 explains | 0 |
| D24-A | CHB-MIT | cbramod | linear | 3 | SA helps? last - lp | -0.4, +0.5, +0.0, -0.1, -0.1 | -0.0 none | +0.1 none | -0.1 none | -0.0 none | +0.0 none | +0.0 none | 0 |
| D24-A | CHB-MIT | cbramod | linear | 3 | random init beats pretrained? last_randinit - last | -3.2, -7.9, -3.7, -1.7, -5.6 | -4.4 2nd wins | -4.7 2nd wins | -3.5 2nd wins | -4.6 2nd wins | -5.1 2nd wins | -4.1 2nd wins | 0 |
| D24-A | CHB-MIT | cbramod | linear | 3 | pretrained features beat random? lp - lp_randinit | +5.9, +9.3, +3.1, +4.1, +4.9 | +5.5 1st wins | +5.4 1st wins | +4.5 1st wins | +6.1 1st wins | +5.8 1st wins | +5.6 1st wins | 0 |
| D24-A | CHB-MIT | cbramod | linear | 3 | D17 | +2.3, +1.8, -0.5, +2.3, -0.8 | +1.0 explains | +0.7 explains | +0.8 explains | +1.4 explains | +0.7 explains | +1.5 explains | 0 |
| D24-A | Siena | biot | linear | 3 | SA helps? last - lp | +7.5, +18.3, +3.4, +10.0, +7.0 | +9.2 1st wins | +9.7 1st wins | +7.0 1st wins | +10.7 1st wins | +9.0 1st wins | +9.8 1st wins | 0 |
| D24-A | Siena | biot | linear | 3 | random init beats pretrained? last_randinit - last | -7.7, +28.1, +6.4, +15.5, -6.3 | +7.2 none | **+10.9 1st wins** | +2.0 none | +7.4 none | +5.1 none | **+10.6 1st wins** | 2 |
| D24-A | Siena | biot | linear | 3 | pretrained features beat random? lp - lp_randinit | +1.1, -45.7, -9.1, -26.5, -0.3 | -16.1 2nd wins | -20.4 2nd wins | -8.7 2nd wins | -17.8 2nd wins | -13.5 2nd wins | -20.0 2nd wins | 0 |
| D24-A | Siena | biot | linear | 3 | D17 | +0.9, +0.7, +0.7, -1.0, +0.4 | +0.3 explains | +0.2 explains | +0.2 explains | +0.3 explains | +0.7 explains | +0.3 explains | 0 |
| D24-A | Siena | cbramod | linear | 3 | SA helps? last - lp | -0.5, +0.3, +0.5, +1.0, +0.0 | +0.3 none | +0.5 none | +0.3 none | +0.2 none | +0.1 none | +0.3 none | 0 |
| D24-A | Siena | cbramod | linear | 3 | random init beats pretrained? last_randinit - last | -6.6, -2.9, -13.4, -2.2, -13.0 | -7.6 2nd wins | -7.9 2nd wins | -8.8 2nd wins | -6.2 2nd wins | -9.0 2nd wins | -6.3 2nd wins | 0 |
| D24-A | Siena | cbramod | linear | 3 | pretrained features beat random? lp - lp_randinit | +4.8, +0.3, +14.7, -0.0, +15.2 | +7.0 1st wins | +7.5 1st wins | +8.7 1st wins | +5.1 1st wins | +8.7 1st wins | +4.9 1st wins | 0 |
| D24-A | Siena | cbramod | linear | 3 | D17 | -2.2, -2.3, +1.8, -1.3, +2.2 | -0.4 explains | +0.1 explains | +0.1 explains | -0.9 explains | -0.1 explains | -1.0 explains | 0 |
| D24-A | Siena filtered | biot | linear | 3 | SA helps? last - lp | +1.3, +8.9, +0.9, +5.0, +4.4 | +4.1 1st wins | +4.8 1st wins | **+2.9 none** | +4.9 1st wins | +3.9 1st wins | +4.0 1st wins | 1 |
| D24-A | Siena filtered | biot | linear | 3 | random init beats pretrained? last_randinit - last | -24.3, +37.1, -9.3, -13.8, -13.2 | -4.7 2nd wins | **+0.2 none** | -15.1 2nd wins | -3.5 2nd wins | **-2.4 none** | **-2.6 none** | 3 |
| D24-A | Siena filtered | biot | linear | 3 | pretrained features beat random? lp - lp_randinit | +23.3, -46.2, +9.2, +8.9, +9.6 | +1.0 none | -4.6 none | **+12.8 1st wins** | -1.1 none | -1.0 none | -1.2 none | 1 |
| D24-A | Siena filtered | biot | linear | 3 | D17 | +0.3, -0.1, +0.8, +0.1, +0.9 | +0.4 explains | +0.4 explains | +0.5 explains | +0.3 explains | +0.5 explains | +0.3 explains | 0 |
| D24-A | Siena filtered | cbramod | linear | 3 | SA helps? last - lp | +0.3, -0.1, +0.2, +0.2, +0.1 | +0.1 none | +0.1 none | +0.2 none | +0.1 none | +0.1 none | +0.1 none | 0 |
| D24-A | Siena filtered | cbramod | linear | 3 | random init beats pretrained? last_randinit - last | -15.3, -7.7, -8.3, -5.2, -16.9 | -10.7 2nd wins | -9.6 2nd wins | -11.4 2nd wins | -11.3 2nd wins | -12.1 2nd wins | -9.1 2nd wins | 0 |
| D24-A | Siena filtered | cbramod | linear | 3 | pretrained features beat random? lp - lp_randinit | +16.2, +6.7, +7.3, +4.8, +12.3 | +9.4 1st wins | +7.8 1st wins | +10.1 1st wins | +10.0 1st wins | +10.6 1st wins | +8.7 1st wins | 0 |
| D24-A | Siena filtered | cbramod | linear | 3 | D17 | +1.3, -1.2, -0.9, -0.3, -4.5 | -1.1 explains | -1.7 explains | -1.1 explains | -1.2 explains | -1.3 explains | -0.3 explains | 0 |
| E32 | CHB-MIT | biot | linear | 3 | SA helps? last - lp | +1.3, +2.4, +0.1, +12.1, +2.1 | +3.6 1st wins | +4.2 1st wins | +3.9 1st wins | +4.5 1st wins | **+1.5 none** | +4.0 1st wins | 1 |
| E32 | CHB-MIT | biot | linear | 3 | random init beats pretrained? last_randinit - last | +4.9, +1.2, +4.1, +18.3, +10.6 | +7.8 1st wins | +8.6 1st wins | +9.5 1st wins | +8.8 1st wins | +5.2 1st wins | +7.1 1st wins | 0 |
| E32 | CHB-MIT | biot | linear | 3 | pretrained features beat random? lp - lp_randinit | -6.3, -4.2, -4.6, -30.3, -12.6 | -11.6 2nd wins | -12.9 2nd wins | -13.5 2nd wins | -13.3 2nd wins | -6.9 2nd wins | -11.3 2nd wins | 0 |
| E32 | CHB-MIT | biot | linear | 3 | D17 | -0.0, -0.5, -0.4, +0.1, +0.2 | -0.1 explains | -0.2 explains | -0.1 explains | -0.1 explains | -0.2 explains | -0.2 explains | 0 |
| E32 | CHB-MIT | cbramod | linear | 3 | SA helps? last - lp | -0.2, +0.0, -0.2, -0.0, +0.2 | -0.0 none | +0.0 none | -0.0 none | +0.0 none | -0.0 none | -0.1 none | 0 |
| E32 | CHB-MIT | cbramod | linear | 3 | random init beats pretrained? last_randinit - last | -4.8, -2.5, -2.7, -4.0, -8.0 | -4.4 2nd wins | -4.3 2nd wins | -4.9 2nd wins | -4.8 2nd wins | -4.5 2nd wins | -3.5 2nd wins | 0 |
| E32 | CHB-MIT | cbramod | linear | 3 | pretrained features beat random? lp - lp_randinit | +5.1, +3.2, +1.1, +5.2, +8.4 | +4.6 1st wins | +4.4 1st wins | +4.9 1st wins | +5.4 1st wins | +4.4 1st wins | +3.6 1st wins | 0 |
| E32 | CHB-MIT | cbramod | linear | 3 | D17 | +0.2, +0.6, -1.8, +1.2, +0.5 | +0.1 explains | +0.1 explains | +0.0 explains | +0.6 explains | -0.1 explains | +0.0 explains | 0 |
| E32 | Siena | biot | linear | 3 | SA helps? last - lp | +13.7, +0.6, +12.3, +8.3, +10.2 | +9.0 1st wins | +7.9 1st wins | +11.1 1st wins | +8.2 1st wins | +9.2 1st wins | +8.7 1st wins | 0 |
| E32 | Siena | biot | linear | 3 | random init beats pretrained? last_randinit - last | -13.3, +27.7, -20.6, +18.3, +16.6 | +5.7 none | **+10.5 1st wins** | +0.2 none | **+12.3 1st wins** | +2.6 none | +3.0 none | 2 |
| E32 | Siena | biot | linear | 3 | pretrained features beat random? lp - lp_randinit | -0.1, -28.2, +8.7, -26.8, -27.0 | -14.7 2nd wins | -18.3 2nd wins | -11.3 2nd wins | -20.5 2nd wins | -11.6 2nd wins | -11.6 2nd wins | 0 |
| E32 | Siena | biot | linear | 3 | D17 | +0.3, +0.1, +0.4, -0.2, -0.2 | +0.1 explains | +0.0 explains | +0.1 explains | -0.0 explains | +0.2 explains | +0.1 explains | 0 |
| E32 | Siena | cbramod | linear | 3 | SA helps? last - lp | -0.1, -0.1, -0.0, +0.8, +0.5 | +0.2 none | +0.3 none | +0.3 none | +0.3 none | +0.1 none | +0.2 none | 0 |
| E32 | Siena | cbramod | linear | 3 | random init beats pretrained? last_randinit - last | -12.8, -17.7, -5.4, -5.4, -8.5 | -9.9 2nd wins | -9.2 2nd wins | -8.0 2nd wins | -11.1 2nd wins | -11.1 2nd wins | -10.3 2nd wins | 0 |
| E32 | Siena | cbramod | linear | 3 | pretrained features beat random? lp - lp_randinit | +15.7, +19.9, +10.4, +6.3, +9.5 | +12.4 1st wins | +11.5 1st wins | +10.5 1st wins | +12.8 1st wins | +13.9 1st wins | +13.1 1st wins | 0 |
| E32 | Siena | cbramod | linear | 3 | D17 | +2.9, +2.1, +5.0, +1.8, +1.5 | +2.6 explains | +2.6 explains | +2.8 explains | +2.1 explains | +2.9 explains | +2.9 explains | 0 |
| E26/D27-B | CHB-MIT | biot | linear_z | 3 | SA helps? last - lp | -0.4, +0.4, +1.6, -1.1, +0.1 | +0.1 none | +0.2 none | +0.1 none | -0.2 none | +0.4 none | +0.1 none | 0 |
| E26/D27-B | CHB-MIT | biot | linear_z | 3 | random init beats pretrained? last_randinit - last | +13.5, -17.5, -0.8, -0.9, +6.3 | +0.1 none | **-3.2 2nd wins** | +4.5 none | +0.4 none | +0.4 none | -1.4 none | 1 |
| E26/D27-B | CHB-MIT | biot | linear_z | 3 | pretrained features beat random? lp - lp_randinit | -13.3, +17.2, -0.7, +2.0, -6.4 | -0.2 none | +3.0 none | **-4.6 2nd wins** | -0.1 none | -0.8 none | +1.3 none | 1 |
| E26/D27-B | CHB-MIT | biot | linear_z | 3 | D17 | -0.2, +0.1, +0.0, +0.0, -0.1 | -0.0 explains | +0.0 explains | -0.0 explains | -0.0 explains | -0.0 explains | -0.0 explains | 0 |
| E26/D27-B | CHB-MIT | cbramod | linear_z | 3 | SA helps? last - lp | +1.5, -0.7, +0.4, +0.7, +0.2 | +0.4 none | +0.1 none | +0.7 none | +0.4 none | +0.4 none | +0.5 none | 0 |
| E26/D27-B | CHB-MIT | cbramod | linear_z | 3 | random init beats pretrained? last_randinit - last | -11.4, -7.8, -5.9, +3.4, -6.0 | -5.6 2nd wins | -4.1 2nd wins | -5.0 2nd wins | -5.5 2nd wins | -7.8 2nd wins | -5.5 2nd wins | 0 |
| E26/D27-B | CHB-MIT | cbramod | linear_z | 3 | pretrained features beat random? lp - lp_randinit | +9.9, +8.5, +5.5, -4.0, +6.2 | +5.2 1st wins | +4.1 1st wins | +4.4 1st wins | +5.2 1st wins | +7.5 1st wins | +5.0 1st wins | 0 |
| E26/D27-B | CHB-MIT | cbramod | linear_z | 3 | D17 | -0.0, -0.1, -0.0, +0.1, +0.4 | +0.1 explains | +0.1 explains | +0.1 explains | +0.1 explains | +0.1 explains | -0.0 explains | 0 |
| E26/D27-B | Siena | biot | linear_z | 3 | SA helps? last - lp | +0.9, -0.2, +1.5, +4.0, +2.0 | +1.7 none | +1.8 none | +2.1 none | +1.7 none | +1.1 none | +1.6 none | 0 |
| E26/D27-B | Siena | biot | linear_z | 3 | random init beats pretrained? last_randinit - last | -4.8, +11.1, +1.3, +2.2, +2.9 | +2.5 none | **+4.4 1st wins** | +0.4 none | +2.8 none | +2.6 none | +2.4 none | 1 |
| E26/D27-B | Siena | biot | linear_z | 3 | pretrained features beat random? lp - lp_randinit | +3.9, -10.9, -2.8, -6.1, -4.8 | -4.2 2nd wins | -6.2 2nd wins | **-2.5 none** | -4.5 2nd wins | -3.7 2nd wins | -4.0 2nd wins | 1 |
| E26/D27-B | Siena | biot | linear_z | 3 | D17 | +0.0, +0.0, -0.1, +0.0, +0.1 | +0.0 explains | +0.0 explains | +0.0 explains | +0.0 explains | +0.0 explains | -0.0 explains | 0 |
| E26/D27-B | Siena | cbramod | linear_z | 3 | SA helps? last - lp | +0.3, -1.0, -0.2, -1.2, +0.7 | -0.3 none | -0.4 none | -0.1 none | -0.3 none | -0.0 none | -0.5 none | 0 |
| E26/D27-B | Siena | cbramod | linear_z | 3 | random init beats pretrained? last_randinit - last | -9.0, -3.1, -18.9, -5.4, -6.6 | -8.6 2nd wins | -8.5 2nd wins | -10.0 2nd wins | -6.0 2nd wins | -9.4 2nd wins | -9.1 2nd wins | 0 |
| E26/D27-B | Siena | cbramod | linear_z | 3 | pretrained features beat random? lp - lp_randinit | +8.6, +4.1, +19.0, +6.5, +5.9 | +8.8 1st wins | +8.9 1st wins | +10.0 1st wins | +6.3 1st wins | +9.4 1st wins | +9.6 1st wins | 0 |
| E26/D27-B | Siena | cbramod | linear_z | 3 | D17 | -0.1, -0.0, +0.0, -0.1, +0.0 | -0.0 explains | -0.0 explains | -0.0 explains | -0.1 explains | -0.0 explains | -0.1 explains | 0 |
| E26/D27-B | Siena filtered | biot | linear_z | 3 | SA helps? last - lp | +6.1, +3.7, +0.1, +0.0, -0.3 | +1.9 none | +0.9 none | +1.5 none | +2.4 none | +2.4 none | +2.5 none | 0 |
| E26/D27-B | Siena filtered | biot | linear_z | 3 | random init beats pretrained? last_randinit - last | -22.2, +9.8, -2.3, -6.5, +10.5 | -2.2 none | +2.9 none | **-5.1 2nd wins** | -2.1 none | -1.1 none | **-5.3 2nd wins** | 2 |
| E26/D27-B | Siena filtered | biot | linear_z | 3 | pretrained features beat random? lp - lp_randinit | +13.6, -13.4, +2.2, +6.5, -10.1 | -0.2 none | -3.7 none | **+3.1 1st wins** | -0.9 none | -1.9 none | +2.2 none | 1 |
| E26/D27-B | Siena filtered | biot | linear_z | 3 | D17 | -2.4, +0.0, +0.0, -0.0, +0.1 | -0.5 explains | +0.0 explains | -0.6 explains | -0.6 explains | -0.6 explains | -0.6 explains | 0 |
| E26/D27-B | Siena filtered | cbramod | linear_z | 3 | SA helps? last - lp | +0.2, -0.0, +0.8, -0.0, +0.7 | +0.3 none | +0.4 none | +0.4 none | +0.2 none | +0.4 none | +0.3 none | 0 |
| E26/D27-B | Siena filtered | cbramod | linear_z | 3 | random init beats pretrained? last_randinit - last | -19.6, -6.4, -8.8, -6.1, -4.9 | -9.2 2nd wins | -6.5 2nd wins | -9.8 2nd wins | -9.2 2nd wins | -9.9 2nd wins | -10.2 2nd wins | 0 |
| E26/D27-B | Siena filtered | cbramod | linear_z | 3 | pretrained features beat random? lp - lp_randinit | +19.2, +6.5, +8.0, +5.8, +4.4 | +8.8 1st wins | +6.2 1st wins | +9.4 1st wins | +9.0 1st wins | +9.5 1st wins | +9.9 1st wins | 0 |
| E26/D27-B | Siena filtered | cbramod | linear_z | 3 | D17 | -0.2, +0.0, +0.0, -0.2, +0.2 | -0.0 explains | -0.0 explains | -0.1 explains | -0.1 explains | +0.0 explains | -0.1 explains | 0 |
| D26 | CHB-MIT | biot | linear_z | 3 | SA helps? last - lp | +0.7, +1.3, -1.6, +1.7, +1.5 | +0.7 none | +0.7 none | +0.6 none | +1.3 none | +0.5 none | +0.5 none | 0 |
| D26 | CHB-MIT | biot | linear_z | 3 | random init beats pretrained? last_randinit - last | -5.3, +1.3, +0.6, +7.7, +8.8 | +2.6 none | **+4.6 1st wins** | +2.9 none | **+3.1 1st wins** | +1.4 none | +1.1 none | 2 |
| D26 | CHB-MIT | biot | linear_z | 3 | pretrained features beat random? lp - lp_randinit | +4.5, -2.6, +1.0, -9.4, -10.3 | -3.4 none | **-5.3 2nd wins** | -3.6 none | **-4.5 2nd wins** | -1.8 none | -1.6 none | 2 |
| D26 | CHB-MIT | biot | linear_z | 3 | D17 | -0.0, +0.0, -0.0, -0.1, -0.0 | -0.0 explains | -0.0 explains | -0.0 explains | -0.0 explains | -0.0 explains | -0.0 explains | 0 |
| D26 | CHB-MIT | cbramod | linear_z | 3 | SA helps? last - lp | +0.4, +1.9, -0.9, -0.4, -1.1 | -0.0 none | -0.1 none | -0.5 none | +0.2 none | +0.1 none | +0.3 none | 0 |
| D26 | CHB-MIT | cbramod | linear_z | 3 | random init beats pretrained? last_randinit - last | +0.4, -2.5, +5.7, -2.3, -5.5 | -0.9 none | -1.2 none | -0.4 none | -2.5 none | -0.5 none | +0.3 none | 0 |
| D26 | CHB-MIT | cbramod | linear_z | 3 | pretrained features beat random? lp - lp_randinit | -0.7, +0.6, -4.7, +2.7, +6.4 | +0.8 none | +1.2 none | +0.9 none | +2.2 none | +0.4 none | -0.6 none | 0 |
| D26 | CHB-MIT | cbramod | linear_z | 3 | D17 | +0.0, -0.0, -0.0, +0.0, -0.2 | -0.0 explains | -0.1 explains | -0.0 explains | -0.0 explains | -0.1 explains | +0.0 explains | 0 |
| D26 | Siena | biot | linear_z | 3 | SA helps? last - lp | +1.7, -1.2, +6.7, +0.9, +0.5 | +1.7 none | +1.7 none | +2.4 none | +0.5 none | +1.9 none | +2.0 none | 0 |
| D26 | Siena | biot | linear_z | 3 | random init beats pretrained? last_randinit - last | +25.6, +0.4, -19.0, -9.6, +2.1 | -0.1 none | -6.5 none | -0.2 none | **+4.6 1st wins** | +2.3 none | -0.7 none | 1 |
| D26 | Siena | biot | linear_z | 3 | pretrained features beat random? lp - lp_randinit | -27.3, +0.9, +12.4, +8.8, -2.6 | -1.6 none | **+4.9 1st wins** | -2.2 none | -5.1 none | -4.2 none | -1.3 none | 1 |
| D26 | Siena | biot | linear_z | 3 | D17 | +0.1, -0.0, +0.1, +0.0, +0.0 | +0.0 explains | +0.0 explains | +0.0 explains | +0.0 explains | +0.0 explains | +0.0 explains | 0 |
| D26 | Siena | cbramod | linear_z | 3 | SA helps? last - lp | +0.6, -0.8, -1.3, +0.3, -0.0 | -0.3 none | -0.5 none | -0.1 none | +0.0 none | -0.4 none | -0.3 none | 0 |
| D26 | Siena | cbramod | linear_z | 3 | random init beats pretrained? last_randinit - last | -9.1, -13.9, -5.2, -11.6, -11.6 | -10.3 2nd wins | -10.6 2nd wins | -9.4 2nd wins | -11.6 2nd wins | -10.0 2nd wins | -10.0 2nd wins | 0 |
| D26 | Siena | cbramod | linear_z | 3 | pretrained features beat random? lp - lp_randinit | +8.4, +14.7, +6.6, +11.1, +11.5 | +10.5 1st wins | +11.0 1st wins | +9.4 1st wins | +11.4 1st wins | +10.3 1st wins | +10.2 1st wins | 0 |
| D26 | Siena | cbramod | linear_z | 3 | D17 | -0.1, -0.0, +0.0, -0.2, -0.1 | -0.1 explains | -0.1 explains | -0.1 explains | -0.1 explains | -0.0 explains | -0.1 explains | 0 |

## 2. TOST on last - last_noise (margin 3, alpha 0.05)

Units: 5 rotation means (seeds paired within rotation) or the 5 paper-split seeds; t with df 4; TOST p = max of the two one-sided t tests (stats_d25.tost_p); 'equivalent' only if p < 0.05 (90% t-interval inside (-3, +3)). D19 (registered): 'the gain needs EEG data' if last wins by the paired rule; 'perturbation alone explains it' if |mean| <= 3; else 'unclear'. A4 (S1LRN<i>), A5 (S3LRN<i>) and A7 (S3DN11/12) have 1 seed per rotation: D19 and TOST p are descriptive. last - lp and last_noise - lp are descriptive (lp from the tags in the 'lp from' column, same seeds). Asserted before writing: E27 rows equal artifacts/analysis/E27/e27.json (last - last_noise mean and rule, last - lp); A4/A5 linear lp equals the E29 lp (e29.json); A6 mlp_fullft last - lp equals E25 (e25_verdicts.json); A7 last - lp equals E28 (e28.json).

| item | setting | model | head | last / noise tags | lp from | units | per unit (last - last_noise) | mean | SD | 90% t | TOST p | equivalent | D19 | last - lp | last_noise - lp |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E27 | CHB-MIT | biot | linear | S1E,S1M,S1N | S1E,S1M,S1N | 5 rotations x 3 seeds | -2.04, +1.59, -0.22, -1.45, +6.17 | +0.81 | 3.30 | [-2.34, +3.96] | 0.1063 | no | perturbation alone explains it | +1.91 | +1.10 |
| E27 | Siena | biot | linear | S3E,S3M,S3N | S3E,S3M,S3N | 5 rotations x 3 seeds | +1.01, +4.52, +2.81, +3.18, -3.60 | +1.58 | 3.16 | [-1.43, +4.60] | 0.1864 | no | perturbation alone explains it | +9.23 | +7.65 |
| E27 | Siena | cbramod | linear | S3E,S3M,S3N | S3E,S3M,S3N | 5 rotations x 3 seeds | -0.07, -0.09, -0.06, -0.13, -0.02 | -0.07 | 0.04 | [-0.11, -0.03] | 4.7e-09 | yes | perturbation alone explains it | +0.27 | +0.34 |
| E27 | Siena filtered | biot | linear | S3FE,S3FM,S3FN | S3FE,S3FM,S3FN | 5 rotations x 3 seeds | +0.02, +4.13, -1.03, +2.70, +0.45 | +1.26 | 2.11 | [-0.75, +3.26] | 0.0688 | no | perturbation alone explains it | +4.11 | +2.85 |
| E27 | Siena filtered | cbramod | linear | S3FE,S3FM,S3FN | S3FE,S3FM,S3FN | 5 rotations x 3 seeds | -0.01, -0.02, -0.05, +0.00, -0.02 | -0.02 | 0.02 | [-0.04, -0.00] | 2.3e-10 | yes | perturbation alone explains it | +0.14 | +0.16 |
| A1 | CHB-MIT paper split, q95 | biot | linear | P1QN | P1QN | 5 seeds | +6.52, +10.56, +11.20, +7.11, +7.49 | +8.58 | 2.14 | [+6.53, +10.62] | 0.9978 | no | the gain needs EEG data | +8.80 | +0.22 |
| A1 | CHB-MIT paper split, q95 | biot | mlp_fullft | P1QN | P1QN | 5 seeds | +7.26, +9.91, +12.63, +6.53, +8.94 | +9.06 | 2.40 | [+6.76, +11.35] | 0.9976 | no | the gain needs EEG data | +8.61 | -0.44 |
| A1 | CHB-MIT paper split, q95 | biot | linear_z | P1QN | P1QN | 5 seeds | +1.11, -0.02, -0.43, +0.58, +1.04 | +0.46 | 0.67 | [-0.18, +1.10] | 0.0005 | yes | perturbation alone explains it | +0.62 | +0.16 |
| A2 | Siena filtered, q95 | biot | linear | S3FQN | S3FQN | 5 rotations x 3 seeds | +0.39, +6.65, +3.07, -2.93, -0.02 | +1.43 | 3.61 | [-2.01, +4.87] | 0.1933 | no | perturbation alone explains it | +3.75 | +2.31 |
| A2 | Siena filtered, q95 | biot | linear_z | S3FQN | S3FQN | 5 rotations x 3 seeds | +0.24, +0.65, -0.68, -0.49, +2.06 | +0.36 | 1.09 | [-0.68, +1.40] | 0.0028 | yes | perturbation alone explains it | +0.36 | +0.00 |
| A3 | CHB-MIT, E32 partition | biot | linear | S1R,S1RN | S1R,S1RN | 5 rotations x 3 seeds | +0.35, +1.16, -2.13, +4.62, +3.09 | +1.42 | 2.59 | [-1.05, +3.89] | 0.1217 | no | perturbation alone explains it | +3.61 | +2.19 |
| A3 | CHB-MIT, E32 partition | biot | linear_z | S1RZ,S1RN | S1RZ,S1RN | 5 rotations x 3 seeds | +0.71, +0.44, -2.24, +1.13, +1.44 | +0.30 | 1.47 | [-1.10, +1.70] | 0.0073 | yes | perturbation alone explains it | +0.71 | +0.41 |
| A3 | Siena, E32 partition | biot | linear | S3R,S3RN | S3R,S3RN | 5 rotations x 3 seeds | +0.19, -0.14, +2.53, +2.26, +3.26 | +1.62 | 1.50 | [+0.19, +3.06] | 0.0549 | no | perturbation alone explains it | +9.04 | +7.42 |
| A3 | Siena, E32 partition | biot | linear_z | S3RZ,S3RN | S3RZ,S3RN | 5 rotations x 3 seeds | +0.79, -1.37, +2.11, +0.51, +0.11 | +0.43 | 1.26 | [-0.77, +1.62] | 0.0051 | yes | perturbation alone explains it | +1.70 | +1.27 |
| A4 | CHB-MIT, E29 cell S1LR1 | biot | linear | S1LRN1 | S1E,S1M,S1Z | 5 rotations | -3.93, -0.23, -0.38, -1.66, +15.37 | +1.84 | 7.71 | [-5.52, +9.19] | 0.3762 (descriptive) | - (descriptive) | perturbation alone explains it (descriptive) | +5.92 | +4.09 |
| A4 | CHB-MIT, E29 cell S1LR1 | biot | linear_z | S1LRN1 | S1E,S1M,S1Z | 5 rotations | -5.67, +3.90, +1.55, -2.50, +8.37 | +1.13 | 5.47 | [-4.08, +6.35] | 0.2438 (descriptive) | - (descriptive) | perturbation alone explains it (descriptive) | +1.39 | +0.25 |
| A4 | CHB-MIT, E29 cell S1LR3 | biot | linear | S1LRN3 | S1E,S1M,S1Z | 5 rotations | -2.85, +2.17, +0.38, +0.51, +19.69 | +3.98 | 8.97 | [-4.57, +12.53] | 0.5904 (descriptive) | - (descriptive) | the gain needs EEG data (descriptive) | +6.13 | +2.16 |
| A4 | CHB-MIT, E29 cell S1LR3 | biot | linear_z | S1LRN3 | S1E,S1M,S1Z | 5 rotations | -3.99, +1.65, +1.75, -5.19, -2.25 | -1.60 | 3.19 | [-4.65, +1.44] | 0.1919 (descriptive) | - (descriptive) | perturbation alone explains it (descriptive) | -0.87 | +0.74 |
| A4 | CHB-MIT, E29 cell S1LR4 | biot | linear | S1LRN4 | S1E,S1M,S1Z | 5 rotations | -8.75, +0.99, +0.41, +0.41, +18.10 | +2.23 | 9.76 | [-7.07, +11.53] | 0.4345 (descriptive) | - (descriptive) | perturbation alone explains it (descriptive) | +6.37 | +4.13 |
| A4 | CHB-MIT, E29 cell S1LR4 | biot | linear_z | S1LRN4 | S1E,S1M,S1Z | 5 rotations | -5.33, +3.61, +2.64, -0.90, +13.11 | +2.63 | 6.83 | [-3.89, +9.14] | 0.4541 (descriptive) | - (descriptive) | perturbation alone explains it (descriptive) | +2.79 | +0.17 |
| A4 | CHB-MIT, E29 cell S1LR5 | biot | linear | S1LRN5 | S1E,S1M,S1Z | 5 rotations | -12.16, +2.43, +1.86, -0.93, +16.78 | +1.60 | 10.33 | [-8.25, +11.44] | 0.3882 (descriptive) | - (descriptive) | perturbation alone explains it (descriptive) | +6.76 | +5.16 |
| A4 | CHB-MIT, E29 cell S1LR5 | biot | linear_z | S1LRN5 | S1E,S1M,S1Z | 5 rotations | -8.17, +6.49, +4.03, +2.02, +15.39 | +3.95 | 8.48 | [-4.14, +12.04] | 0.5929 (descriptive) | - (descriptive) | the gain needs EEG data (descriptive) | +3.54 | -0.42 |
| A5 | Siena, E29 cell S3LR1 | biot | linear | S3LRN1 | S3M,S3Z | 5 rotations | +7.16, -5.09, +4.76, +10.23, -0.76 | +3.26 | 6.16 | [-2.62, +9.13] | 0.5350 (descriptive) | - (descriptive) | unclear (descriptive) | +18.75 | +15.50 |
| A5 | Siena, E29 cell S3LR1 | biot | linear_z | S3LRN1 | S3M,S3Z | 5 rotations | +1.61, +1.69, +1.07, +7.30, -2.17 | +1.90 | 3.41 | [-1.35, +5.15] | 0.2550 (descriptive) | - (descriptive) | perturbation alone explains it (descriptive) | +3.89 | +1.99 |
| A5 | Siena, E29 cell S3LR2 | biot | linear | S3LRN2 | S3M,S3Z | 5 rotations | +7.50, -9.89, +2.38, +5.59, +4.47 | +2.01 | 6.91 | [-4.58, +8.60] | 0.3824 (descriptive) | - (descriptive) | perturbation alone explains it (descriptive) | +21.12 | +19.11 |
| A5 | Siena, E29 cell S3LR2 | biot | linear_z | S3LRN2 | S3M,S3Z | 5 rotations | +1.09, -6.13, -8.50, +8.61, -0.63 | -1.11 | 6.70 | [-7.50, +5.27] | 0.2814 (descriptive) | - (descriptive) | perturbation alone explains it (descriptive) | +3.25 | +4.36 |
| A5 | Siena, E29 cell S3LR3 | biot | linear | S3LRN3 | S3M,S3Z | 5 rotations | +3.72, +5.61, +1.44, +4.09, -2.00 | +2.57 | 2.96 | [-0.25, +5.39] | 0.3814 (descriptive) | - (descriptive) | perturbation alone explains it (descriptive) | +9.89 | +7.32 |
| A5 | Siena, E29 cell S3LR3 | biot | linear_z | S3LRN3 | S3M,S3Z | 5 rotations | +0.11, +1.84, +3.13, -0.11, +1.40 | +1.28 | 1.33 | [+0.01, +2.54] | 0.0220 (descriptive) | - (descriptive) | perturbation alone explains it (descriptive) | +0.55 | -0.73 |
| A5 | Siena, E29 cell S3LR4 | biot | linear | S3LRN4 | S3M,S3Z | 5 rotations | +7.33, -7.21, +4.20, +10.14, -0.02 | +2.89 | 6.79 | [-3.58, +9.37] | 0.4865 (descriptive) | - (descriptive) | perturbation alone explains it (descriptive) | +18.85 | +15.96 |
| A5 | Siena, E29 cell S3LR4 | biot | linear_z | S3LRN4 | S3M,S3Z | 5 rotations | +1.82, +2.58, -0.49, +7.42, -1.59 | +1.95 | 3.49 | [-1.38, +5.28] | 0.2686 (descriptive) | - (descriptive) | perturbation alone explains it (descriptive) | +4.29 | +2.35 |
| A5 | Siena, E29 cell S3LR5 | biot | linear | S3LRN5 | S3M,S3Z | 5 rotations | +7.63, -11.03, +2.99, +5.64, +4.80 | +2.01 | 7.47 | [-5.12, +9.13] | 0.3905 (descriptive) | - (descriptive) | perturbation alone explains it (descriptive) | +21.47 | +19.46 |
| A5 | Siena, E29 cell S3LR5 | biot | linear_z | S3LRN5 | S3M,S3Z | 5 rotations | +0.74, -6.53, -8.55, +8.89, +1.51 | -0.79 | 6.97 | [-7.44, +5.86] | 0.2586 (descriptive) | - (descriptive) | perturbation alone explains it (descriptive) | +3.64 | +4.43 |
| A6 | Siena | biot | mlp_fullft | S3L,S3NM | S3L,S3NM | 5 rotations x 3 seeds | +0.96, +4.19, +3.82, +1.47, -0.53 | +1.98 | 1.99 | [+0.09, +3.88] | 0.1586 | no | perturbation alone explains it | +11.89 | +9.90 |
| A6 | Siena | biot | linear_z | S3Z,S3NM | S3Z,S3NM | 5 rotations x 3 seeds | +0.23, -0.07, +0.60, +2.33, -1.10 | +0.40 | 1.25 | [-0.79, +1.59] | 0.0048 | yes | perturbation alone explains it | +1.65 | +1.26 |
| A6 | Siena filtered | biot | mlp_fullft | S3FL,S3FNM | S3FL,S3FNM | 5 rotations x 3 seeds | +0.32, +5.48, -0.79, +0.59, -0.22 | +1.08 | 2.52 | [-1.32, +3.47] | 0.0812 | no | perturbation alone explains it | +4.06 | +2.99 |
| A6 | Siena filtered | biot | linear_z | S3FZ,S3FNM | S3FZ,S3FNM | 5 rotations x 3 seeds | +0.47, +5.40, -0.14, -0.10, +0.03 | +1.13 | 2.40 | [-1.15, +3.42] | 0.0783 | no | perturbation alone explains it | +1.93 | +0.80 |
| A7 | Siena, ssl_seed 11 | biot | linear | S3D11,S3DN11 | S3M | 5 rotations | +1.94, +3.70, +3.72, +5.10, -0.89 | +2.71 | 2.30 | [+0.52, +4.91] | 0.3973 (descriptive) | - (descriptive) | perturbation alone explains it (descriptive) | +6.84 | +4.13 |
| A7 | Siena, ssl_seed 12 | biot | linear | S3D12,S3DN12 | S3M | 5 rotations | +1.95, +3.69, +3.70, +5.18, -0.84 | +2.73 | 2.30 | [+0.54, +4.93] | 0.4047 (descriptive) | - (descriptive) | perturbation alone explains it (descriptive) | +6.84 | +4.11 |

### Reproduction checks (D27 design: lp/last under the new tags reproduce the earlier runs)

ROC x100 at the val-selected epoch, paired by (model, arm, split, head, seed); 'identical' = difference exactly 0.

| check | records | paired | identical | max abs diff |
|---|---|---|---|---|
| P1QN vs P1Q (lp/last; linear/mlp_fullft) | 20 | 20 | 20 | 0 |
| S3FQN vs S3FQ (lp/last; linear) | 30 | 30 | 30 | 0 |
| S1LRN1 last linear vs E29 cell 1 (S_r) | 5 | 5 | 5 | 0 |
| S1LRN3 last linear vs E29 cell 3 (S_r) | 5 | 5 | 5 | 0 |
| S1LRN4 last linear vs E29 cell 4 (S_r) | 5 | 5 | 5 | 0 |
| S1LRN5 last linear vs E29 cell 5 (S_r) | 5 | 5 | 5 | 0 |
| S3LRN1 last linear vs E29 cell 1 (S_r) | 5 | 5 | 5 | 0 |
| S3LRN2 last linear vs E29 cell 2 (S_r) | 5 | 5 | 5 | 0 |
| S3LRN3 last linear vs E29 cell 3 (S_r) | 5 | 5 | 5 | 0 |
| S3LRN4 last linear vs E29 cell 4 (S_r) | 5 | 5 | 5 | 0 |
| S3LRN5 last linear vs E29 cell 5 (S_r) | 5 | 5 | 5 | 0 |

### Pairing checks and record counts

Per row: one record each for last, last_noise and lp per (model, split, seed, head); same eval_hash, labels (overlap on rotations, upstream on the paper split), versions (adapt 3, probe 4), test index, test n/prevalence and probe spec (eval mode, encoder tap); last and last_noise share the adapt spec (lr, epochs, N, ...) and the noise SSL sample is _hash(last data_hash, 'noise'). No record is used twice within a row (read_d24.load refuses duplicates).

| item | setting | heads | triples | SSL config | records used (tag model arm: n) | gaps |
|---|---|---|---|---|---|---|
| E27 | CHB-MIT | linear | 15 | lr 3e-05, N sample, 3 ep | S1M biot last: 15, S1M biot lp: 15, S1N biot last_noise: 15 | none |
| E27 | Siena | linear | 30 | lr 3e-05, N sample, 3 ep | S3E cbramod last: 5, S3E cbramod lp: 5, S3M biot last: 15, S3M biot lp: 15, S3M cbramod last: 10, S3M cbramod lp: 10, S3N biot last_noise: 15, S3N cbramod last_noise: 15 | none |
| E27 | Siena filtered | linear | 30 | lr 3e-05, N sample, 3 ep | S3FE cbramod last: 5, S3FE cbramod lp: 5, S3FM biot last: 15, S3FM biot lp: 15, S3FM cbramod last: 10, S3FM cbramod lp: 10, S3FN biot last_noise: 15, S3FN cbramod last_noise: 15 | none |
| A1 | CHB-MIT paper split, q95 | linear/mlp_fullft/linear_z | 15 | lr 3e-05, N sample, 3 ep | P1QN biot last: 5, P1QN biot last_noise: 5, P1QN biot lp: 5 | none |
| A2 | Siena filtered, q95 | linear/linear_z | 30 | lr 3e-05, N sample, 3 ep | S3FQN biot last: 15, S3FQN biot last_noise: 15, S3FQN biot lp: 15 | none |
| A3 | CHB-MIT, E32 partition | linear | 15 | lr 3e-05, N sample, 3 ep | S1R biot last: 15, S1R biot lp: 15, S1RN biot last_noise: 15 | none |
| A3 | CHB-MIT, E32 partition | linear_z | 15 | lr 3e-05, N sample, 3 ep | S1RN biot last_noise: 15, S1RZ biot last: 15, S1RZ biot lp: 15 | none |
| A3 | Siena, E32 partition | linear | 15 | lr 3e-05, N sample, 3 ep | S3R biot last: 15, S3R biot lp: 15, S3RN biot last_noise: 15 | none |
| A3 | Siena, E32 partition | linear_z | 15 | lr 3e-05, N sample, 3 ep | S3RN biot last_noise: 15, S3RZ biot last: 15, S3RZ biot lp: 15 | none |
| A4 | CHB-MIT, E29 cell S1LR1 | linear/linear_z | 10 | lr 0.0003, N sample, 3 ep | S1LRN1 biot last: 5, S1LRN1 biot last_noise: 5, S1M biot lp: 15, S1Z biot lp: 15 | none |
| A4 | CHB-MIT, E29 cell S1LR3 | linear/linear_z | 10 | lr 3e-05, whole pool, 3 ep | S1LRN3 biot last: 5, S1LRN3 biot last_noise: 5, S1M biot lp: 15, S1Z biot lp: 15 | none |
| A4 | CHB-MIT, E29 cell S1LR4 | linear/linear_z | 10 | lr 0.0003, whole pool, 3 ep | S1LRN4 biot last: 5, S1LRN4 biot last_noise: 5, S1M biot lp: 15, S1Z biot lp: 15 | none |
| A4 | CHB-MIT, E29 cell S1LR5 | linear/linear_z | 10 | lr 0.001, whole pool, 3 ep | S1LRN5 biot last: 5, S1LRN5 biot last_noise: 5, S1M biot lp: 15, S1Z biot lp: 15 | none |
| A5 | Siena, E29 cell S3LR1 | linear/linear_z | 10 | lr 0.0003, N sample, 3 ep | S3LRN1 biot last: 5, S3LRN1 biot last_noise: 5, S3M biot lp: 15, S3Z biot lp: 15 | none |
| A5 | Siena, E29 cell S3LR2 | linear/linear_z | 10 | lr 0.001, N sample, 3 ep | S3LRN2 biot last: 5, S3LRN2 biot last_noise: 5, S3M biot lp: 15, S3Z biot lp: 15 | none |
| A5 | Siena, E29 cell S3LR3 | linear/linear_z | 10 | lr 3e-05, whole pool, 3 ep | S3LRN3 biot last: 5, S3LRN3 biot last_noise: 5, S3M biot lp: 15, S3Z biot lp: 15 | none |
| A5 | Siena, E29 cell S3LR4 | linear/linear_z | 10 | lr 0.0003, whole pool, 3 ep | S3LRN4 biot last: 5, S3LRN4 biot last_noise: 5, S3M biot lp: 15, S3Z biot lp: 15 | none |
| A5 | Siena, E29 cell S3LR5 | linear/linear_z | 10 | lr 0.001, whole pool, 3 ep | S3LRN5 biot last: 5, S3LRN5 biot last_noise: 5, S3M biot lp: 15, S3Z biot lp: 15 | none |
| A6 | Siena | mlp_fullft | 15 | lr 3e-05, N sample, 3 ep | S3L biot last: 15, S3L biot lp: 15, S3NM biot last_noise: 15 | none |
| A6 | Siena | linear_z | 15 | lr 3e-05, N sample, 3 ep | S3NM biot last_noise: 15, S3Z biot last: 15, S3Z biot lp: 15 | none |
| A6 | Siena filtered | mlp_fullft | 15 | lr 3e-05, N sample, 3 ep | S3FL biot last: 15, S3FL biot lp: 15, S3FNM biot last_noise: 15 | none |
| A6 | Siena filtered | linear_z | 15 | lr 3e-05, N sample, 3 ep | S3FNM biot last_noise: 15, S3FZ biot last: 15, S3FZ biot lp: 15 | none |
| A7 | Siena, ssl_seed 11 | linear | 5 | lr 3e-05, N sample, 3 ep, ssl_seed 11 | S3D11 biot last: 5, S3DN11 biot last_noise: 5, S3M biot lp: 15 | none |
| A7 | Siena, ssl_seed 12 | linear | 5 | lr 3e-05, N sample, 3 ep, ssl_seed 12 | S3D12 biot last: 5, S3DN12 biot last_noise: 5, S3M biot lp: 15 | none |

## 3. Step-0 SSL loss, pretrained vs random init

step_losses[0] = SSL loss on the first batch, before the first optimizer step (src/eegdrift/adapt.py); epoch 1 = mean loss over the first pass. Over every adapted run of the tag (rotations x seeds, or the 5 paper-split seeds).

| setting | tag | model | arm | init | n | step 0 mean [min, max] | epoch 1 mean [min, max] |
|---|---|---|---|---|---|---|---|
| CHB-MIT rotations | S1L | biot | all | pretrained | 15 | 0.9928 [0.8987, 1.0694] | 0.4154 [0.3624, 0.4903] |
| CHB-MIT rotations | S1L | biot | last | pretrained | 15 | 0.9928 [0.8987, 1.0694] | 0.6432 [0.5726, 0.7150] |
| CHB-MIT rotations | S1L | biot | last_randinit | random | 15 | 0.9755 [0.8510, 1.1153] | 0.8017 [0.6871, 0.9522] |
| CHB-MIT rotations | S1L | cbramod | all | pretrained | 15 | 0.0292 [0.0284, 0.0306] | 0.0126 [0.0121, 0.0135] |
| CHB-MIT rotations | S1L | cbramod | last | pretrained | 15 | 0.0292 [0.0284, 0.0306] | 0.0278 [0.0270, 0.0288] |
| CHB-MIT rotations | S1L | cbramod | last_randinit | random | 15 | 64.6085 [50.0559, 76.2964] | 59.8513 [46.5737, 70.4578] |
| Siena | S3L | biot | all | pretrained | 15 | 1.0070 [0.9244, 1.1227] | 0.4079 [0.3601, 0.4833] |
| Siena | S3L | biot | last | pretrained | 15 | 1.0070 [0.9244, 1.1227] | 0.6312 [0.5749, 0.7372] |
| Siena | S3L | biot | last_randinit | random | 15 | 0.9862 [0.8678, 1.0959] | 0.8025 [0.6782, 0.9234] |
| Siena | S3L | cbramod | all | pretrained | 15 | 0.0256 [0.0255, 0.0259] | 0.0092 [0.0092, 0.0094] |
| Siena | S3L | cbramod | last | pretrained | 15 | 0.0256 [0.0255, 0.0259] | 0.0242 [0.0241, 0.0243] |
| Siena | S3L | cbramod | last_randinit | random | 15 | 65.9959 [50.6415, 77.7400] | 60.9474 [46.9666, 71.6543] |
| Siena filtered | S3FL | biot | all | pretrained | 15 | 1.0070 [0.9244, 1.1227] | 0.4079 [0.3601, 0.4833] |
| Siena filtered | S3FL | biot | last | pretrained | 15 | 1.0070 [0.9244, 1.1227] | 0.6312 [0.5749, 0.7372] |
| Siena filtered | S3FL | biot | last_randinit | random | 15 | 0.9862 [0.8678, 1.0959] | 0.8025 [0.6782, 0.9234] |
| Siena filtered | S3FL | cbramod | all | pretrained | 15 | 0.0256 [0.0255, 0.0259] | 0.0092 [0.0092, 0.0094] |
| Siena filtered | S3FL | cbramod | last | pretrained | 15 | 0.0256 [0.0255, 0.0259] | 0.0242 [0.0241, 0.0243] |
| Siena filtered | S3FL | cbramod | last_randinit | random | 15 | 65.9959 [50.6415, 77.7400] | 60.9474 [46.9666, 71.6543] |
| CHB-MIT paper split | P1L | biot | last | pretrained | 5 | 1.0236 [0.9687, 1.0637] | 0.6698 [0.6212, 0.7152] |
| CHB-MIT paper split | P1L | biot | last_randinit | random | 5 | 1.0065 [0.8577, 1.1181] | 0.8278 [0.7002, 0.9533] |
| CHB-MIT paper split | P1L | cbramod | last | pretrained | 5 | 0.0292 [0.0290, 0.0295] | 0.0278 [0.0277, 0.0278] |
| CHB-MIT paper split | P1L | cbramod | last_randinit | random | 5 | 63.2507 [50.0000, 74.5840] | 58.4939 [46.5488, 68.5048] |

S3FL equals S3L in 6 of 6 rows: Siena filtered changes only the eval preprocessing; the SSL sample (adapt_spec.data_hash) is the same.

## Skipped or partial inputs

- none
