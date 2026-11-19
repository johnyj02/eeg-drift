# D25-E30 (a) and (b): C2/C3 re-tested, our pipeline

Rule (pre-registered, notes/completeness-audit.md E30): D15 rules on seed means (notes/decisions.md "## D15"; verdict strings as in "### D15 outcome"). ROC-AUC x100 at the val-selected epoch, linear head at batch 128, eval mode, encoder tap, fixed_c 132 SSL steps (batch 128, lr 3e-5), BIOT arm `last` (block03 + head). Only differences > 3 are interpreted.

D15: C2 is "supported for the pretrained FM" only if the best N is <= 2048 AND beats both N4174 and LP by > 3; "not testable: adaptation adds nothing at any N" if within 3 of LP at every N; else "not supported". C3 "flat" if max - min across P <= 3; flat supports C3 only if > 3 above LP; flat at the LP level = "uninformative".

Reader choices (not in the rule text; fixed before any E30 aggregate, after reading raw records; see the script docstring): (a) primary = 5-seed mean at data_seed 1, each data_seed draw at seed 42 read as a 1-seed D15 curve; (b) primary = mean over 5 rotations of 3-seed means, LP = S3LPB / S3FLPB the same way; |v - LP| <= 3 = "within 3"; C3 "> 3 above LP" = every P point; flat but not above LP = "uninformative" (D24-C precedent). Everything else below is labelled descriptive/post hoc.

## Record checks

- 374 records read, exactly 1 per expected cell (0 missing, 0 duplicate); other records in the same directories, not used: C2E x4, C3E x3, S3E x40, S3FE x40, S3FM x60, S3M x60 (other arms / last_randinit)
- every record: probe v4, adapt code v3, linear head, eval mode, encoder tap, one eval_hash per (dataset, split); adapted cells: fixed_c, SSL batch 128, 132 steps, 0 non-finite steps, n_windows = N, ssl_subjects = P; probe batch 128 (the descriptive lp b256 records S3E/S3FE CBraMod, S3M/S3FM BIOT: 256)
- every seed of a cell saw the same SSL subset (one data_hash per cell); the seed-42 D24 records (C2E/C3E) have the same probe, adapt and arm specs as C2X/C3X apart from the seed
- SSL subset across data_seed 1/2/3 (data_hash): N896 different, N1664 different, N2048 different, N4174 same, P3N2048 different, P11N2048 different, P21N2048 different (N4174 is the whole 4,174-window sample, so it cannot change with data_seed)
- CBraMod control and BIOT saw the same SSL subset (data_hash equal) in: Siena 20/20, Siena filtered 20/20

## (a) CHB-MIT paper split, BIOT pretrained `last`

LP baseline (D15/D24-C): R3E-b128, BIOT lp, linear, batch 128, eval mode, 5 seeds: **65.09** (per seed 42: 64.82, 123: 65.25, 2021: 65.46, 3407: 64.70, 8888: 65.24).

| curve | N896 | N1664 | N2048 | N4174 | P3N2048 | P11N2048 | P21N2048 |
|---|---|---|---|---|---|---|---|
| seed 42 (= D24 C2E/C3E) | 62.4 | 61.9 | 62.1 | 62.3 | 61.8 | 62.0 | 62.4 |
| seed 123 | 66.3 | 66.5 | 66.5 | 66.6 | 65.4 | 66.1 | 66.7 |
| seed 2021 | 63.1 | 62.9 | 62.9 | 63.1 | 61.2 | 63.0 | 62.8 |
| seed 3407 | 64.2 | 64.1 | 64.1 | 64.3 | 62.8 | 64.3 | 64.3 |
| seed 8888 | 66.4 | 66.6 | 66.6 | 66.6 | 66.7 | 66.0 | 66.8 |
| seed 42, data_seed 2 | 62.2 | 62.4 | 62.5 | 62.3 | 62.9 | 62.2 | 62.4 |
| seed 42, data_seed 3 | 62.5 | 62.0 | 62.3 | 62.3 | 63.3 | 63.3 | 62.7 |
| **5-seed mean ± SEM, data_seed 1** | **64.5** ± 0.8 | **64.4** ± 0.9 | **64.4** ± 0.9 | **64.6** ± 0.9 | **63.6** ± 1.1 | **64.3** ± 0.8 | **64.6** ± 0.9 |
| 3-draw mean ± SEM at seed 42 (descriptive) | 62.4 ± 0.1 | 62.1 ± 0.2 | 62.3 ± 0.1 | 62.3 ± 0.0 | 62.7 ± 0.4 | 62.5 ± 0.4 | 62.5 ± 0.1 |
| LP baseline R3E-b128 | 65.1 | | | | | | |

| reading | C2 verdict | numbers | C3 verdict | numbers |
|---|---|---|---|---|
| 5-seed mean, data_seed 1 (PRIMARY) | **not testable: adaptation adds nothing at any N** | best N 4174 (64.60), best - N4174 +0.00, range 0.17, v - LP -0.67 to -0.50 | **uninformative** | range 1.06, v - LP -1.53 to -0.48 |
| seed 42, data_seed 1 (1 seed, D15 as written) | **not supported** | best N 896 (62.45), best - N4174 +0.12, range 0.54, v - LP -3.19 to -2.65 | **uninformative** | range 0.61, v - LP -3.27 to -2.66 |
| seed 42, data_seed 2 (1 seed, D15 as written) | **not testable: adaptation adds nothing at any N** | best N 2048 (62.52), best - N4174 +0.20, range 0.31, v - LP -2.88 to -2.57 | **uninformative** | range 0.79, v - LP -2.94 to -2.15 |
| seed 42, data_seed 3 (1 seed, D15 as written) | **not supported** | best N 896 (62.49), best - N4174 +0.17, range 0.48, v - LP -3.09 to -2.61 | **uninformative** | range 0.62, v - LP -2.39 to -1.77 |
| 3-draw mean at seed 42 (descriptive/post hoc) | **not testable: adaptation adds nothing at any N** | best N 896 (62.38), best - N4174 +0.06, range 0.27, v - LP -2.99 to -2.71 | **uninformative** | range 0.18, v - LP -2.59 to -2.41 |
| seed 123 alone (descriptive/post hoc) | **not testable: adaptation adds nothing at any N** | best N 4174 (66.62), best - N4174 +0.00, range 0.32, v - LP +1.21 to +1.52 | **uninformative** | range 1.37, v - LP +0.26 to +1.64 |
| seed 2021 alone (descriptive/post hoc) | **not testable: adaptation adds nothing at any N** | best N 896 (63.11), best - N4174 +0.01, range 0.19, v - LP -2.18 to -1.98 | **uninformative** | range 1.83, v - LP -3.93 to -2.10 |
| seed 3407 alone (descriptive/post hoc) | **not testable: adaptation adds nothing at any N** | best N 4174 (64.29), best - N4174 +0.00, range 0.17, v - LP -0.97 to -0.81 | **uninformative** | range 1.56, v - LP -2.32 to -0.76 |
| seed 8888 alone (descriptive/post hoc) | **not testable: adaptation adds nothing at any N** | best N 4174 (66.65), best - N4174 +0.00, range 0.20, v - LP +1.35 to +1.55 | **uninformative** | range 0.81, v - LP +0.89 to +1.70 |

D24-C (seed 42, published): C2 "not supported", C3 "uninformative". Re-derived here from the C2E/C3E records: C2 "not supported", C3 "uninformative". Same string in every pre-registered reading (5-seed mean, data_seed 2, data_seed 3): C2 **NO** (5-seed mean, data_seed 1: not testable: adaptation adds nothing at any N; seed 42, data_seed 1: not supported; seed 42, data_seed 2: not testable: adaptation adds nothing at any N; seed 42, data_seed 3: not supported), C3 **yes**. C2 is supported in no reading: best N - N4174 <= +0.2.

## (b) Siena, 5 rotations

LP baseline: S3LPB, BIOT lp, linear, batch 128, eval mode, 3 seeds per rotation (the same seeds as the curves): **57.70** ± 4.66 (SEM over rotation means).

BIOT pretrained `last`, 3-seed mean per rotation:

| rotation (seeds) | N896 | N1664 | N2048 | N4174 | P2N2048 | P5N2048 | P10N2048 | LP |
|---|---|---|---|---|---|---|---|---|
| rot0 (42/1000/2000) | 74.4 | 74.4 | 74.4 | 74.4 | 74.0 | 74.5 | 74.4 | 67.8 |
| rot1 (123/1001/2001) | 69.5 | 69.4 | 69.7 | 69.5 | 68.2 | 69.8 | 69.9 | 53.3 |
| rot2 (2021/1002/2002) | 67.1 | 67.1 | 67.1 | 67.0 | 66.8 | 67.3 | 67.3 | 61.9 |
| rot3 (3407/1003/2003) | 63.2 | 63.1 | 62.5 | 62.8 | 62.7 | 62.6 | 62.6 | 41.7 |
| rot4 (8888/1004/2004) | 78.0 | 77.8 | 78.1 | 77.8 | 77.0 | 78.5 | 78.1 | 63.8 |
| **mean ± SEM over rotations** | **70.5** ± 2.6 | **70.3** ± 2.6 | **70.3** ± 2.7 | **70.3** ± 2.7 | **69.8** ± 2.6 | **70.5** ± 2.8 | **70.4** ± 2.7 | **57.7** ± 4.7 |

CBraMod control `last` at seed S_r (one run per rotation; lp b256 = S3E lp at S_r, descriptive only):

| rotation (seed) | N896 | N4174 | P2N2048 | P10N2048 | lp b256 |
|---|---|---|---|---|---|
| rot0 (42) | 89.6 | 89.6 | 89.6 | 89.6 | 78.8 |
| rot1 (123) | 83.0 | 83.0 | 83.0 | 83.1 | 80.0 |
| rot2 (2021) | 78.4 | 78.4 | 78.4 | 78.4 | 75.0 |
| rot3 (3407) | 83.3 | 83.3 | 83.3 | 83.3 | 80.6 |
| rot4 (8888) | 88.6 | 88.6 | 88.6 | 88.6 | 89.6 |
| **mean ± SEM** | **84.6** ± 2.0 | **84.6** ± 2.0 | **84.6** ± 2.0 | **84.6** ± 2.0 | 80.8 ± 2.4 |

Probe batch matters (descriptive/post hoc): BIOT lp b128 (S3LPB) - lp b256 (S3M), same seeds, per rotation +3.8, +17.0, +1.8, +6.6, +2.5 (mean +6.4). So the CBraMod row against the b256 lp mixes probe batch with adaptation and is not a C2/C3 reading.

| reading | C2 verdict | numbers | C3 verdict | numbers |
|---|---|---|---|---|
| BIOT, mean over 5 rotations of 3-seed means (PRIMARY) | **not supported** | best N 896 (70.45), best - N4174 +0.13, range 0.13, v - LP +12.61 to +12.75 | **supported as written** | range 0.76, v - LP +12.07 to +12.83 |
| CBraMod control, mean over 5 rotations at S_r (pre-registered rule, no batch-128 LP) | **not supported or not testable (no batch-128 LP; no N <= 2048 beats N4174 by > 3)** | best N 896 (84.59), best - N4174 +0.00, range 0.00 | **flat; supported vs uninformative undetermined (no batch-128 LP)** | range 0.05 |
| CBraMod control vs batch-256 lp S3E/S3FE at S_r (descriptive/post hoc) | **not supported** | best N 896 (84.59), best - N4174 +0.00, range 0.00, v - LP +3.76 to +3.76 | **supported as written** | range 0.05, v - LP +3.73 to +3.78 |

Per-rotation verdicts, BIOT, 3-seed mean vs the rotation's own LP (descriptive/post hoc): C2 {'not supported': 5}; C3 {'supported as written': 5}.

- rot0: C2 not supported (best N 896 (74.42), best - N4174 +0.03, range 0.04, v - LP +6.55 to +6.59); C3 supported as written (range 0.47, v - LP +6.21 to +6.69)
- rot1: C2 not supported (best N 2048 (69.65), best - N4174 +0.11, range 0.28, v - LP +16.07 to +16.35); C3 supported as written (range 1.67, v - LP +14.91 to +16.57)
- rot2: C2 not supported (best N 896 (67.12), best - N4174 +0.09, range 0.09, v - LP +5.16 to +5.25); C3 supported as written (range 0.45, v - LP +4.96 to +5.40)
- rot3: C2 not supported (best N 896 (63.22), best - N4174 +0.45, range 0.68, v - LP +20.89 to +21.56); C3 supported as written (range 0.15, v - LP +20.93 to +21.08)
- rot4: C2 not supported (best N 2048 (78.06), best - N4174 +0.22, range 0.31, v - LP +13.90 to +14.22); C3 supported as written (range 1.45, v - LP +13.18 to +14.63)

## (b) Siena filtered, 5 rotations

LP baseline: S3FLPB, BIOT lp, linear, batch 128, eval mode, 3 seeds per rotation (the same seeds as the curves): **74.43** ± 3.23 (SEM over rotation means).

BIOT pretrained `last`, 3-seed mean per rotation:

| rotation (seeds) | N896 | N1664 | N2048 | N4174 | P2N2048 | P5N2048 | P10N2048 | LP |
|---|---|---|---|---|---|---|---|---|
| rot0 (42/1000/2000) | 85.8 | 85.9 | 85.8 | 85.8 | 85.9 | 86.0 | 85.8 | 85.5 |
| rot1 (123/1001/2001) | 71.7 | 71.5 | 71.5 | 71.7 | 70.6 | 71.7 | 72.1 | 65.7 |
| rot2 (2021/1002/2002) | 74.2 | 74.2 | 74.1 | 74.2 | 74.6 | 74.0 | 74.0 | 74.8 |
| rot3 (3407/1003/2003) | 83.5 | 83.5 | 83.4 | 83.4 | 83.3 | 83.4 | 83.4 | 74.9 |
| rot4 (8888/1004/2004) | 79.9 | 79.8 | 79.8 | 79.9 | 79.8 | 79.8 | 79.8 | 71.2 |
| **mean ± SEM over rotations** | **79.0** ± 2.7 | **79.0** ± 2.7 | **78.9** ± 2.7 | **79.0** ± 2.7 | **78.8** ± 2.8 | **79.0** ± 2.7 | **79.0** ± 2.6 | **74.4** ± 3.2 |

CBraMod control `last` at seed S_r (one run per rotation; lp b256 = S3FE lp at S_r, descriptive only):

| rotation (seed) | N896 | N4174 | P2N2048 | P10N2048 | lp b256 |
|---|---|---|---|---|---|
| rot0 (42) | 93.6 | 93.6 | 93.6 | 93.6 | 91.5 |
| rot1 (123) | 88.4 | 88.4 | 88.4 | 88.4 | 89.4 |
| rot2 (2021) | 82.9 | 82.9 | 82.9 | 82.9 | 81.2 |
| rot3 (3407) | 91.3 | 91.3 | 91.3 | 91.3 | 90.4 |
| rot4 (8888) | 94.1 | 94.1 | 94.1 | 94.1 | 94.5 |
| **mean ± SEM** | **90.1** ± 2.0 | **90.1** ± 2.1 | **90.1** ± 2.0 | **90.1** ± 2.1 | 89.4 ± 2.2 |

Probe batch matters (descriptive/post hoc): BIOT lp b128 (S3FLPB) - lp b256 (S3FM), same seeds, per rotation +0.5, +21.4, +1.5, +2.0, -2.2 (mean +4.7). So the CBraMod row against the b256 lp mixes probe batch with adaptation and is not a C2/C3 reading.

| reading | C2 verdict | numbers | C3 verdict | numbers |
|---|---|---|---|---|
| BIOT, mean over 5 rotations of 3-seed means (PRIMARY) | **not supported** | best N 896 (79.02), best - N4174 +0.01, range 0.10, v - LP +4.49 to +4.59 | **supported as written** | range 0.17, v - LP +4.39 to +4.56 |
| CBraMod control, mean over 5 rotations at S_r (pre-registered rule, no batch-128 LP) | **not supported or not testable (no batch-128 LP; no N <= 2048 beats N4174 by > 3)** | best N 896 (90.06), best - N4174 +0.00, range 0.00 | **flat; supported vs uninformative undetermined (no batch-128 LP)** | range 0.00 |
| CBraMod control vs batch-256 lp S3E/S3FE at S_r (descriptive/post hoc) | **not testable: adaptation adds nothing at any N** | best N 896 (90.06), best - N4174 +0.00, range 0.00, v - LP +0.66 to +0.66 | **uninformative** | range 0.00, v - LP +0.66 to +0.66 |

Per-rotation verdicts, BIOT, 3-seed mean vs the rotation's own LP (descriptive/post hoc): C2 {'not testable: adaptation adds nothing at any N': 2, 'not supported': 3}; C3 {'uninformative': 2, 'supported as written': 3}.

- rot0: C2 not testable: adaptation adds nothing at any N (best N 1664 (85.85), best - N4174 +0.02, range 0.06, v - LP +0.31 to +0.36); C3 uninformative (range 0.22, v - LP +0.28 to +0.50)
- rot1: C2 not supported (best N 896 (71.70), best - N4174 +0.04, range 0.24, v - LP +5.75 to +5.98); C3 supported as written (range 1.45, v - LP +4.89 to +6.34)
- rot2: C2 not testable: adaptation adds nothing at any N (best N 4174 (74.21), best - N4174 +0.00, range 0.11, v - LP -0.68 to -0.58); C3 uninformative (range 0.61, v - LP -0.84 to -0.23)
- rot3: C2 not supported (best N 896 (83.55), best - N4174 +0.13, range 0.16, v - LP +8.44 to +8.60); C3 supported as written (range 0.16, v - LP +8.31 to +8.47)
- rot4: C2 not supported (best N 4174 (79.94), best - N4174 +0.00, range 0.17, v - LP +8.58 to +8.74); C3 supported as written (range 0.10, v - LP +8.56 to +8.65)

## Commands

```
.venv/bin/python scripts/analysis/e30_c2c3.py
# inputs: artifacts/s3-results (already synced); jobs: notes/jobs-d25b.txt after '# E30';
# specs: scripts/submit_d25.sh (want E30), D24 C2E/C3E/R3E: scripts/submit_d24.sh
.venv/bin/python -m pytest -q && .venv/bin/python -m ruff check src tests scripts sm_entry.py
```

