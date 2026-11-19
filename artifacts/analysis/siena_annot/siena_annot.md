# E18-free: Siena annotation alignment and cross-check (D25)

Pre-registered rule (completeness-audit E18-free): every onset/offset difference against epilepsy2bids must be 0 or explained;
any unexplained difference larger than 1 window (10 s) triggers relabelling and a re-score of Siena.

## 1. Cross-check against epilepsy2bids 0.0.7

- Siena: 47 seizures compared (table: 47); identical 43; differ 4; explained 4; unexplained 0 (of which > 10 s: 0); loader errors / count mismatches 0.
- CHB-MIT: 198 seizures compared (table: 198); identical 198; differ 0; loader errors / count mismatches / EDFs not in the table 0; table entries without an EDF 0.
- CHB-MIT EDFs absent from the table, with no seizure in epilepsy2bids either (not listed in their summary file): 10 (chb24_02, chb24_05, chb24_08, chb24_10, chb24_12, chb24_16, chb24_18, chb24_19, chb24_20, chb24_22).
- configs/siena_seizures.json equals the preprocessing output artifacts/siena/siena_seizures.json: True.
- **Rule outcome: not triggered** (0 unexplained Siena differences > 10 s; 0 Siena loader problems).

| stem | k | ours on-off (s) | epilepsy2bids on-off (s) | d on | d off | explained | why |
|---|---|---|---|---|---|---|---|
| PN05-3 | 0 | 6846-6876 | 6836-6866 | -10 | -10 | yes | clock origin: EDF header start minus txt Registration start = -10 s (D21) |
| PN10-2 | 0 | 7798-7849 | 7798-7828 | +0 | -21 | yes | two times on the txt line (onset +0 s, offset -21 s): D21 takes the first (union of the alternatives), epilepsy2bids the last |
| PN10-3 | 0 | 7835-7904 | 7841-7904 | +6 | +0 | yes | two times on the txt line (onset +6 s, offset +0 s): D21 takes the first (union of the alternatives), epilepsy2bids the last |
| PN14-3 | 0 | 6740-6781 | 17540-17581 | +10800 | +10800 | yes | clock origin: EDF header start minus txt Registration start = +10800 s (D21) |

## 2. Onset-locked line length and 1-30 Hz power, all Siena seizures

z = (ictal-window mean - baseline mean) / baseline SD of the channel-mean log ratio; rise iff z >= 2 (fixed before computing).

- line length (0.5-45 Hz): no rise (z < 2) in **27 / 47** seizures; no rise on any channel in 12; median z 1.8 [IQR 0.3, 3.6]; median fold change 1.43; signal onset found in 32 / 47, median lag +6 s, |lag| > 10 s in 12 (descriptive).
- 1-30 Hz power: no rise (z < 2) in **25 / 47** seizures; no rise on any channel in 9; median z 1.6 [IQR 1.2, 3.2]; median fold change 3.18; signal onset found in 33 / 47, median lag +9 s, |lag| > 10 s in 16 (descriptive).
- No rise in either feature (channel mean): 21 / 47

| seizure | duration s | z LL | z LL any ch | z power | z power any ch | fold LL | lag LL s | lag pw s |
|---|---|---|---|---|---|---|---|---|
| PN00-1#0 | 70 | 0.3 | 2.3 | 0.9 | 2.1 | 1.08 | +9 | +38 |
| PN00-2#0 | 54 | 8.2 | 12.5 | 2.3 | 4.0 | 3.13 | -4 | +5 |
| PN00-3#0 | 60 | 0.1 | 1.5 | 0.6 | 1.7 | 1.04 | - | +50 |
| PN00-4#0 | 74 | 1.4 | 5.7 | 1.4 | 4.2 | 1.22 | +8 | +39 |
| PN00-5#0 | 67 | 5.1 | 10.0 | 1.2 | 2.7 | 2.30 | +4 | +36 |
| PN01-1#0 | 54 | 0.6 | 1.9 | 1.5 | 6.9 | 1.60 | - | - |
| PN01-1#1 | 74 | 1.8 | 4.5 | 4.0 | 8.6 | 2.49 | +0 | +0 |
| PN03-1#0 | 111 | 13.3 | 17.6 | 5.8 | 6.8 | 2.28 | +6 | +9 |
| PN03-2#0 | 133 | 8.6 | 24.9 | 3.4 | 5.7 | 3.34 | +6 | +9 |
| PN05-2#0 | 35 | -0.4 | 0.3 | 0.1 | 1.3 | 0.84 | - | - |
| PN05-3#0 | 30 | -0.9 | 0.1 | -0.8 | 0.8 | 0.73 | - | - |
| PN05-4#0 | 39 | -0.0 | 1.5 | 0.6 | 2.3 | 1.00 | +61 | -5 |
| PN06-1#0 | 64 | 13.5 | 14.8 | 3.0 | 3.0 | 2.90 | +5 | +8 |
| PN06-2#0 | 69 | 1.7 | 4.6 | 3.6 | 4.7 | 1.12 | +25 | +0 |
| PN06-3#0 | 42 | -0.2 | 1.9 | 2.8 | 4.4 | 0.98 | - | +0 |
| PN06-4#0 | 63 | -0.1 | 1.3 | 0.7 | 1.9 | 0.97 | - | - |
| PN06-5#0 | 44 | 2.1 | 2.6 | 1.4 | 1.9 | 1.43 | +23 | - |
| PN07-1#0 | 62 | 5.0 | 14.7 | 3.9 | 5.3 | 1.33 | -23 | -23 |
| PN09-1#0 | 80 | -0.1 | 1.0 | 1.4 | 2.9 | 0.97 | - | - |
| PN09-2#0 | 59 | 1.2 | 3.9 | 3.7 | 7.1 | 1.16 | +31 | +0 |
| PN09-3#0 | 64 | 0.3 | 2.0 | 0.6 | 1.5 | 1.07 | - | - |
| PN10-1#0 | 69 | 2.8 | 5.1 | 2.2 | 5.5 | 2.48 | +17 | +22 |
| PN10-10#0 | 14 | 2.7 | 5.2 | 1.6 | 5.4 | 1.87 | +3 | - |
| PN10-2#0 | 51 | 1.3 | 2.2 | 1.3 | 4.8 | 1.42 | - | +41 |
| PN10-3#0 | 69 | 0.3 | 1.0 | 1.2 | 1.8 | 1.15 | - | - |
| PN10-4.5.6#0 | 5 | 5.3 | 9.6 | 2.4 | 7.8 | 2.90 | -1 | - |
| PN10-4.5.6#1 | 19 | 1.3 | 4.3 | 1.3 | 5.0 | 1.40 | - | - |
| PN10-4.5.6#2 | 57 | 1.1 | 2.0 | 1.6 | 2.4 | 1.36 | +5 | - |
| PN10-7.8.9#0 | 48 | 1.9 | 3.1 | 2.0 | 4.9 | 1.43 | +1 | +21 |
| PN10-7.8.9#1 | 18 | 0.4 | 2.5 | 3.1 | 7.0 | 1.21 | - | +1 |
| PN10-7.8.9#2 | 15 | 3.3 | 6.1 | 3.0 | 10.1 | 1.71 | +7 | +7 |
| PN11-1#0 | 55 | 1.8 | 2.9 | 1.4 | 2.3 | 1.83 | +0 | +0 |
| PN12-1.2#0 | 63 | 3.2 | 4.4 | 3.3 | 4.2 | 1.63 | -20 | +7 |
| PN12-1.2#1 | 68 | 0.2 | 1.5 | 1.3 | 2.1 | 1.09 | +81 | +74 |
| PN12-3#0 | 96 | -0.3 | 3.8 | 1.6 | 4.2 | 0.80 | - | +56 |
| PN12-4#0 | 63 | -1.4 | 1.5 | 0.3 | 1.5 | 0.47 | - | - |
| PN13-1#0 | 48 | -1.2 | 2.7 | 1.5 | 4.2 | 0.70 | - | +75 |
| PN13-2#0 | 65 | 0.7 | 2.3 | 1.1 | 3.4 | 1.33 | +104 | +104 |
| PN13-3#0 | 151 | 5.7 | 9.5 | 4.1 | 6.7 | 2.65 | +1 | +8 |
| PN14-1#0 | 27 | 1.9 | 3.2 | 1.0 | 2.7 | 1.63 | +6 | - |
| PN14-2#0 | 12 | 3.9 | 5.5 | 2.5 | 2.9 | 2.15 | +3 | +3 |
| PN14-3#0 | 41 | 2.8 | 4.7 | 0.7 | 1.9 | 1.59 | +22 | +28 |
| PN14-4#0 | 83 | 8.2 | 8.8 | 4.8 | 5.2 | 5.06 | +1 | +1 |
| PN16-1#0 | 123 | 5.6 | 10.9 | 4.6 | 6.6 | 2.35 | +13 | +12 |
| PN16-2#0 | 107 | 13.3 | 27.6 | 8.3 | 12.6 | 3.78 | +9 | +11 |
| PN17-1#0 | 70 | 3.4 | 5.1 | 2.1 | 4.3 | 2.06 | +9 | +14 |
| PN17-2#0 | 83 | 3.1 | 5.4 | 3.4 | 3.5 | 1.92 | +12 | +6 |

## 3. Zero-parameter line-length ROC per rotation (test ROC x100; probe test windows and labels)

| setting | row | rot0 | rot1 | rot2 | rot3 | rot4 | mean ± SEM |
|---|---|---|---|---|---|---|---|
| chbmit | line length, zero-parameter | 69.2 | 79.8 | 91.5 | 73.2 | 82.0 | 79.1 ± 3.9 |
| chbmit | line length, zero-parameter, >=50% labels | 70.0 | 81.6 | 93.0 | 78.2 | 84.3 | 81.4 ± 3.8 |
| chbmit | hand-crafted LR | 66.6 | 88.7 | 90.0 | 63.2 | 89.2 | 79.5 ± 6.0 |
| chbmit | biot lp (3-seed mean) | 61.0 | 63.6 | 90.0 | 40.9 | 69.9 | 65.1 ± 7.9 |
| chbmit | cbramod lp (3-seed mean) | 72.0 | 83.8 | 88.9 | 75.9 | 87.6 | 81.6 ± 3.3 |
| siena | line length, zero-parameter | 55.8 | 80.3 | 38.0 | 74.3 | 80.7 | 65.8 ± 8.3 |
| siena | line length, zero-parameter, >=50% labels | 54.8 | 80.9 | 36.9 | 76.6 | 81.6 | 66.2 ± 8.8 |
| siena | hand-crafted LR | 78.3 | 89.9 | 67.3 | 88.6 | 92.7 | 83.4 ± 4.7 |
| siena | biot lp (3-seed mean) | 64.0 | 36.3 | 60.1 | 35.0 | 61.3 | 51.3 ± 6.4 |
| siena | cbramod lp (3-seed mean) | 81.8 | 79.8 | 75.0 | 80.8 | 89.6 | 81.4 ± 2.4 |
| siena_filt | line length, zero-parameter | 61.5 | 88.3 | 63.3 | 74.8 | 79.6 | 73.5 ± 5.0 |
| siena_filt | line length, zero-parameter, >=50% labels | 60.5 | 88.7 | 62.6 | 77.1 | 80.4 | 73.9 ± 5.4 |
| siena_filt | hand-crafted LR | 76.8 | 86.1 | 76.7 | 87.3 | 93.3 | 84.0 ± 3.2 |
| siena_filt | biot lp (3-seed mean) | 85.0 | 44.3 | 73.3 | 72.9 | 73.3 | 69.8 ± 6.8 |
| siena_filt | cbramod lp (3-seed mean) | 91.9 | 89.4 | 81.1 | 90.5 | 94.5 | 89.5 ± 2.3 |

Siena rows answer the item; the CHB-MIT row is descriptive.

