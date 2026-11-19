# D25-E26: standardized linear probe (`linear_z`), run tags S1Z / S3Z / S3FZ / P1Z

Rule (D25 additions, fixed before the runs): D24 paired rule (|mean| > 3 and same sign in >= 4/5)
on last - lp, last_randinit - last, lp - lp_randinit at 1 seed (S_r) per rotation ("descriptive,
like S1"), plus D17; paper split (P1Z, 5 seeds) by the D24-B rule on last - lp only.
ROC-AUC x100, test at the val-selected epoch, eval-mode probe, encoder tap.
Full reader output: S1Z.md, S3Z.md, S3FZ.md, P1Z.md in this folder.

## Integrity
- 160 records, 0 smoke, 0 duplicate keys, 0 duplicate (model, arm, split, seed, probe) cells.
  S1Z / S3Z / S3FZ: 40 each = 2 models x 4 arms (lp, lp_randinit, last, last_randinit) x 5 rotations,
  seed S_r = 42/123/2021/3407/8888 for rot0-4. P1Z: 40 = 2 x 4 arms x 5 seeds, paper split.
- Every record: probe `linear_z` only, probe v4, backbone eval, tap encoder, input_norm "".
  Labels overlap (rotations), upstream (P1Z).
- eval_hash per (model, split) equals the D24 tag it pairs with (S1M, S3M, S3FM, P1E): 0 mismatches.
  S3FZ is the filtered Siena store (eval_hash = S3FM's), S3Z the unfiltered one.
- Raw records read: biot chbmit last rot0, biot siena last rot1, cbramod siena-filt last rot4,
  biot paper lp s42 (spec, history, test_at_best checked).
- Anomaly (checked, not a bug): BIOT CHB-MIT rot0 lp / last test ROC 49.9 / 50.0 with val 0.89.
  The per-epoch test curve rises 0.39 -> 0.50, so it is not tied scores. Score npz files were not synced.
- Cross-check: E26 GPU means equal the E15 CPU z-scored head (lp - lp_randinit +1.1 / +0.6 / -0.4;
  Siena last - lp +0.8, filtered +0.4; paper lp 79.1).

## Verdicts (pre-registered rule outputs; 1 seed per rotation)
| model | dataset | contrast | mean | per rotation | rule output |
|---|---|---|---|---|---|
| BIOT | CHB-MIT | last - lp | +0.2 | +0.1, +0.3, +1.0, -1.0, +0.4 | no difference shown |
| BIOT | CHB-MIT | last_randinit - last | -1.3 | +10.7, -20.7, -1.1, -4.0, +8.8 | no difference shown |
| BIOT | CHB-MIT | lp - lp_randinit | +1.1 | -11.0, +20.6, +0.2, +5.0, -9.2 | no difference shown |
| BIOT | CHB-MIT | D17 | +0.0 | | random features explain it |
| BIOT | Siena | last - lp | +0.8 | +0.2, +0.6, +0.1, -0.3, +3.3 | no difference shown |
| BIOT | Siena | last_randinit - last | -1.4 | -10.7, +9.1, -9.4, +3.8, +0.3 | no difference shown |
| BIOT | Siena | lp - lp_randinit | +0.6 | +10.5, -9.8, +9.2, -3.6, -3.5 | no difference shown |
| BIOT | Siena | D17 | -0.0 | | random features explain it |
| BIOT | Siena filt | last - lp | +0.4 | +0.2, +0.9, -0.1, +0.3, +0.5 | no difference shown |
| BIOT | Siena filt | last_randinit - last | -1.4 | -31.7, +10.4, +0.2, +3.1, +11.1 | no difference shown |
| BIOT | Siena filt | lp - lp_randinit | -0.4 | +24.6, -11.3, -0.1, -3.7, -11.7 | no difference shown |
| BIOT | Siena filt | D17 | -1.5 | | random features explain it |
| CBraMod | CHB-MIT | last - lp | +0.3 | +0.1, +0.1, +0.4, +0.7, +0.2 | no difference shown |
| CBraMod | CHB-MIT | last_randinit - last | -2.3 | -8.8, -4.1, -6.6, +7.5, +0.4 | no difference shown |
| CBraMod | CHB-MIT | lp - lp_randinit | +2.1 | +8.8, +4.0, +6.1, -8.1, -0.4 | no difference shown |
| CBraMod | CHB-MIT | D17 | +0.0 | | random features explain it |
| CBraMod | Siena | last - lp | +0.8 | +1.0, +1.5, -0.1, +0.9, +0.7 | no difference shown |
| CBraMod | Siena | last_randinit - last | -9.4 | -4.7, +1.4, -33.4, -7.4, -3.2 | second term wins (pretrained wins) |
| CBraMod | Siena | lp - lp_randinit | +8.6 | +3.4, -2.9, +33.4, +6.5, +2.5 | first term wins (pretrained features win) |
| CBraMod | Siena | D17 | -0.0 | | random features explain it |
| CBraMod | Siena filt | last - lp | +0.2 | +0.2, +0.1, -0.4, +0.2, +1.1 | no difference shown |
| CBraMod | Siena filt | last_randinit - last | -9.2 | -16.4, -10.1, -11.9, -2.6, -5.1 | second term wins (pretrained wins) |
| CBraMod | Siena filt | lp - lp_randinit | +8.8 | +16.0, +10.0, +12.4, +1.8, +4.1 | first term wins (pretrained features win) |
| CBraMod | Siena filt | D17 | -0.2 | | random features explain it |

Paper split (P1Z, 5 seeds 42/123/2021/3407/8888), D24-B on last - lp:
| model | last - lp mean ± SEM | per seed | rule output |
|---|---|---|---|
| BIOT | +0.2 ± 0.8 | -0.8, -1.0, -0.2, -0.5, +3.4 | no difference shown |
| CBraMod | +0.2 ± 0.1 | +0.4, +0.2, +0.3, -0.0, +0.0 | no difference shown |
Descriptive (not pre-registered on the paper split): BIOT lp 79.1, last 79.3, lp_randinit 88.4,
last_randinit 88.4 (last_randinit - last +9.1, 5/5 seeds positive). CBraMod lp 88.5, last 88.6,
lp_randinit 85.1, last_randinit 85.0. P1E (raw linear) for reference: BIOT lp 55.0, last 54.4;
CBraMod lp 92.0.

## Against D24-A (raw linear, 3 seeds per rotation) — comparison is descriptive
| model | dataset | contrast | D24-A | E26 linear_z | |
|---|---|---|---|---|---|
| BIOT | CHB-MIT | last - lp | +1.9 none | +0.2 none | kept |
| BIOT | CHB-MIT | last_randinit - last | +0.2 none | -1.3 none | kept |
| BIOT | CHB-MIT | lp - lp_randinit | -2.0 none | +1.1 none | kept |
| BIOT | Siena | last - lp | +9.2 SA helps | +0.8 none | CHANGED |
| BIOT | Siena | last_randinit - last | +7.2 none | -1.4 none | kept |
| BIOT | Siena | lp - lp_randinit | -16.1 random wins | +0.6 none | CHANGED |
| BIOT | Siena filt | last - lp | +4.1 SA helps | +0.4 none | CHANGED |
| BIOT | Siena filt | last_randinit - last | -4.7 pretrained wins | -1.4 none | CHANGED |
| BIOT | Siena filt | lp - lp_randinit | +1.0 none | -0.4 none | kept |
| CBraMod | CHB-MIT | last_randinit - last | -4.4 pretrained wins | -2.3 none | CHANGED |
| CBraMod | CHB-MIT | lp - lp_randinit | +5.5 pretrained wins | +2.1 none | CHANGED |
| CBraMod | all other 7 contrasts | | | | kept |
D17: "random features explain it" in all 6 model x dataset cells, before and after.

Post hoc, descriptive (seed-matched control). D24-A raw linear restricted to seed S_r, so the
seeds match E26:
- BIOT CHB-MIT: last - lp +2.6 none; last_randinit - last -5.9 second wins; lp - lp_randinit +3.2 first wins.
- BIOT Siena: last - lp +6.9 (+7.9, +11.7, -5.6, +12.5, +7.7) first wins; last_randinit - last +10.0 none; lp - lp_randinit -16.8 second wins.
- BIOT Siena filt: last - lp +3.6 (+1.0, +10.8, -3.9, +5.6, +4.7) first wins; last_randinit - last -3.2 second wins; lp - lp_randinit +0.4 none.
- CBraMod CHB-MIT: +0.1 none; -2.9 none; +4.6 first wins. Siena and Siena filt: same strings as E26.
- D17 at S_r: random features explain it in all 6.
So at the same seeds, the BIOT Siena / Siena-filt "SA helps" strings flip from raw head to
standardized head. That is a probe effect, not a seed-count effect. The CBraMod CHB-MIT
last_randinit - last change is already present at 1 raw seed (-2.9 none).

Post hoc, descriptive cluster-bootstrap 95% CIs (method of scripts/bootstrap_d24.py, rotations only):
BIOT last - lp CHB-MIT +0.2 [-0.4, +0.7], Siena +0.8 [-0.1, +2.1], Siena filt +0.4 [+0.1, +0.6];
paper +0.2 [-0.8, +1.8]. CBraMod last - lp: CHB-MIT +0.3 [+0.1, +0.5], Siena +0.8 [+0.3, +1.2],
Siena filt +0.2 [-0.2, +0.7], paper +0.2 [+0.0, +0.3] (all < 1 ROC point).

## Commands
```
.venv/bin/python scripts/read_d24.py --dataset chbmit --tags S1Z --seeds-per-rot 1 > artifacts/analysis/E26/S1Z.md
.venv/bin/python scripts/read_d24.py --dataset siena  --tags S3Z --seeds-per-rot 1 > artifacts/analysis/E26/S3Z.md
.venv/bin/python scripts/read_d24.py --dataset siena  --tags S3FZ --seeds-per-rot 1 > artifacts/analysis/E26/S3FZ.md
.venv/bin/python scripts/read_d24.py --dataset chbmit --tags P1Z --paper > artifacts/analysis/E26/P1Z.md
```
(The reader also writes artifacts/tables/d24-<dataset>-<tag>.md.) The post hoc S_r-only rows and
CIs came from a one-off inline script. It imports `load` (read_d24), `paired`/`d17` (read_step1)
and `cluster_ci` (bootstrap_d24, rng seed 20261101) and was not saved.
Code change: scripts/read_d24.py gets `--seeds-per-rot` (default 3, so existing calls are unchanged).
