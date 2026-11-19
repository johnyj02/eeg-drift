# D28 recheck (independent recomputation from the raw records)

Rule text: notes/decisions.md "## D28", identical to commit c0283f4. Own loader and statistics; only
`read_step1.paired` (D18) was reused. The t quantile is df 4, the NB SE is sd*sqrt(1/5 + n_test/n_train),
and TOST is two one-sided t tests at margin 3.

## Confirmed
- 505 records (P1G 40, P1QG 15, S1G 150, S3G 150, S3FG 150). Exactly one per (tag, model, arm, split, seed),
  none missing, no extras, 0 smoke. Versions adapt 3 / probe 4 / grid 1. Eval mode, encoder tap, input_norm
  "" (q95 for P1QG, both in adapt_spec and in the probe spec). Labels upstream on the paper split and
  overlap on rotations. One (eval_hash, test index, val index) per tag and split. Grid fields equal the
  frozen search.
- Selection replay over all 16160 configurations: 0 disagreements for best_val = max(curve), best_epoch =
  first argmax, early stopping (ref moves only on a gain > 1e-4, patience 20), converged = stopped before
  200, and selected = first argmax (lr, then wd). val_at_best equals best_val. Ties: 13 / 0 / 20 / 9 / 18.
  The top-level epochs_run differs from the selected configuration's in 848 of 1010 fits.
- Fixed-recipe partners (same eval_hash, adapt_spec, arm_spec, test and val index, test n and prevalence,
  identical SSL losses). The missing sets are exactly as stated. The partner means reproduce D24-A/B
  and D27-B. E27 BIOT TOST p is 0.106 / 0.186 / 0.069. A1 is +8.58 (linear) and +0.46 (linear_z, p 0.0005).
- NB ratios: 0.338 / 0.347 / 0.347.
- All 66 readings (mean, 95% t, NB, TOST p, label, D18, per-unit values) match the README.
  Q1 no (16 equivalent, 2 not resolved). Q2 no (grid -0.27, p 0.0017; grid_z -0.28, p 0.027). Q3 counts:
  BIOT 9/16 keep the sign and the 7 flips are as listed; CBraMod 16/16. No rotation contrast is a gain
  with the NB SE. 13 readings are a D18 win but labelled not resolved.
- Convergence: 986/1010 selected fits, 15201/16160 configurations. Edges: 944 (lr 3e-3 498, lr 1e-4 198,
  wd 1e-1 523, wd 0 257). P1QG grid lr 3e-3 15/15, P1G CBraMod grid_z lr 1e-4 20/20. The per-cell fit table
  matches. The absolute ROC values match.

## Not confirmed
- "Test ROC fell below 50 in 7 fits": there are **6**, and both lists show 6.
- "Validation and test disagree more than with the fixed recipe": **not supported**. Over 935 paired fits,
  SD(test - val) is 11.2 tuned vs 13.3 fixed, smaller in 16 of 18 cells. Within (setting, model, variant,
  split), the residual SD is 5.9 vs 7.5, and tuned is more variable in only 22 of 66 groups. Only val - test
  drops > 20 are slightly more frequent (96 vs 84).
- "Selection effects plausibly explain the wide BIOT pretrained-vs-random intervals": **not supported**.
  The rotation-unit SD is smaller with tuning in 10 of 12 BIOT readings (e.g. S3FG grid 12.2 vs 24.0;
  S1G grid_z 5.1 vs 11.5). The exceptions are S3G grid_z (8.5 vs 5.7; 7.4 vs 5.4). Without rot4 s1004,
  S1G grid last_randinit - last is -3.8 (lp - lp_randinit +3.0).
- "CBraMod CHB-MIT rot0 s42 drives grid_z last - lp -4.4": **overstated**. Without that fit the contrast is -3.3.
  rot4 gives -9.0 with no outlier: last is below lp in all 3 seeds (74.1/78.4/72.6 vs 83.7/86.0/82.3).
- Q3 "not for BIOT (7 of 16 flip)" holds under the sign-of-mean reading, which the rule text does not define.
  In 6 of the 7 flips, the fixed mean was within +-2.2 (D18 none, D28 label not resolved). The only flip
  of a fixed D18 direction is S3FG grid last_randinit - last (-4.7 to +4.6), and both are not resolved.
  All 4 BIOT fixed "gain demonstrated" readings keep their sign and stay a gain. For CBraMod, 13 fixed
  gains are kept in sign, and 10 stay a gain (P1G grid last_randinit - last and both S1G grid contrasts
  become not resolved).
- Changes item 4: the grid_z comparator is linear_z +9.1 (P1Z), not +35.8.
