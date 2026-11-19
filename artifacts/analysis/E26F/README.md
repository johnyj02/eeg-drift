# D25-E26-filt: filtered CHB-MIT under the corrected protocol, run tag S1FM

Rule: D18/D24 unchanged. D24 paired rule on per-rotation 3-seed means for last - lp,
last_randinit - last, lp - lp_randinit, plus D17. Reported for both heads (linear, mlp_fullft).
ROC-AUC x100, test at the val-selected epoch, eval-mode probe, encoder tap.
Full reader output: S1FM.md.

## Integrity and how filtered records are told apart
- 150 records (75 per model) = 5 arms (lp, lp_randinit, last, last_randinit, all) x 5 rotations x
  3 seeds [S_r, 1000+r, 2000+r]. Each record has both heads, so there are 300 (model, arm, split,
  seed, probe) cells, every one present once. 0 duplicate keys, 0 smoke. All records: probe v4,
  eval mode, encoder tap, labels overlap, adapt v3.
- Records do NOT store the data variant. `dataset` is "chbmit" and there is no data_variant field.
  Filtered records are told apart by run_tag S1FM (job suffix `-ffm`, submit_d25.sh E26F passes
  `--data-variant filt`) and by eval_hash. The eval_hash hashes the store meta. S1FM has 5 hashes
  (8a50249e, a6e0b006, 343043c8, 14371747, bb8e3816), and none equals the unfiltered
  S1E/S1M/S1L/S1Z hash of the same rotation. read_d24.load exits if one call mixes eval hashes
  within a (model, split), so S1FM cannot be silently pooled with S1M.
- The filtered store keeps the rotation and overlap index: test and val window keys are identical,
  in the same order, to the unfiltered store in all 5 rotations. Test n and prevalence are identical
  per rotation (S1FM vs S1L).
- Raw records read: biot all s1000 rot0, biot last s8888 rot4, biot all s1002 rot2 (both heads).
  The SSL data_hash equals the unfiltered runs' (only the eval store is filtered).

## Verdicts (pre-registered rule outputs)
| model | head | contrast | mean | per rotation (3-seed means) | rule output |
|---|---|---|---|---|---|
| BIOT | linear | last - lp | +1.3 | -0.7, +3.0, +0.3, -0.8, +4.7 | no difference shown |
| BIOT | linear | last_randinit - last | -1.6 | -9.4, -4.3, -9.2, +20.9, -6.2 | no difference shown |
| BIOT | linear | lp - lp_randinit | +0.4 | +9.9, +1.4, +9.0, -20.2, +1.9 | no difference shown |
| BIOT | linear | D17 | +0.1 | | random features explain it |
| BIOT | mlp_fullft | last - lp | +0.6 | -0.6, +2.6, +0.1, -1.2, +2.1 | no difference shown |
| BIOT | mlp_fullft | last_randinit - last | +1.9 | +1.5, -3.1, -4.2, +18.5, -3.2 | no difference shown |
| BIOT | mlp_fullft | lp - lp_randinit | -2.3 | -0.6, +0.9, +3.9, -17.0, +1.4 | no difference shown |
| BIOT | mlp_fullft | D17 | +0.2 | | random features explain it |
| CBraMod | linear | last - lp | +0.0 | -0.3, +0.2, +0.1, -0.1, +0.3 | no difference shown |
| CBraMod | linear | last_randinit - last | -3.9 | -0.4, -8.5, -3.7, -0.9, -6.3 | second term wins (pretrained wins) |
| CBraMod | linear | lp - lp_randinit | +5.2 | +5.7, +9.0, +4.0, +0.7, +6.8 | first term wins (pretrained features win) |
| CBraMod | linear | D17 | +1.3 | | random features explain it |
| CBraMod | mlp_fullft | last - lp | +0.1 | +1.9, -0.1, -0.4, -1.1, -0.1 | no difference shown |
| CBraMod | mlp_fullft | last_randinit - last | -4.9 | -12.5, -6.3, -2.0, +5.8, -9.4 | second term wins (pretrained wins) |
| CBraMod | mlp_fullft | lp - lp_randinit | +4.2 | +11.4, +4.6, +2.2, -5.8, +8.8 | first term wins (pretrained features win) |
| CBraMod | mlp_fullft | D17 | -0.6 | | random features explain it |

Arm means over rotations (linear): BIOT lp 66.6, lp_randinit 66.2, last 67.9, last_randinit 66.3,
all 76.7 (all - last +8.8, reference). CBraMod lp 82.7, lp_randinit 77.4, last 82.7, last_randinit
78.7, all 83.8 (+1.1). mlp_fullft: BIOT lp 68.6, CBraMod lp 84.6.

## Against unfiltered CHB-MIT (descriptive comparison)
Compared with D24-A linear (S1E+S1M) and E25 mlp_fullft (S1L), all 16 rule outputs are the same
(4 contrasts x 2 heads x 2 models).
- BIOT linear: +1.9 / +0.2 / -2.0 -> +1.3 / -1.6 / +0.4.
- BIOT mlp: +1.4 / +3.2 / -4.6 -> +0.6 / +1.9 / -2.3.
- CBraMod linear: -0.0 / -4.4 / +5.5 -> +0.0 / -3.9 / +5.2.
- CBraMod mlp: +0.2 / -4.3 / +3.1 -> +0.1 / -4.9 / +4.2.
Filtering CHB-MIT changes no verdict.

Post hoc, descriptive cluster-bootstrap 95% CIs (method of scripts/bootstrap_d24.py):
BIOT linear last - lp +1.3 [-0.6, +3.3]; CBraMod linear last_randinit - last -3.9 [-7.2, -0.6],
lp - lp_randinit +5.2 [+2.4, +7.8]; CBraMod mlp -4.9 [-10.1, +1.0], +4.2 [-1.3, +9.1].

## Commands
```
.venv/bin/python scripts/read_d24.py --dataset chbmit --tags S1FM > artifacts/analysis/E26F/S1FM.md
```
(The reader also writes artifacts/tables/d24-chbmit-S1FM.md.) The integrity checks and CIs came
from one-off inline scripts and were not saved.
