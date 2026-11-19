# D29 re-check (independent recomputation from the raw records)

Standalone code, not part of the repository. It imports only `stats_d25.tost_p` and `read_step1.paired`, both checked against the rule text. The C2/C3 rules were re-implemented from the D15 text and the E30 reader choices, and the noise rule from the D29 text at commit c0283f4.

## Record selection: CONFIRMED
- 450 D29 records: 2 settings x 5 rotations x seeds [S_r, 1000+r, 2000+r] x (7 subsets x {last, last_noise} + lp). There is exactly one record per cell, and no other model, arm or seed appears under these tags. 240 E30b partner records, also one per cell.
- Every record is probe v4 / adapt v3, overlap labels, eval mode, encoder tap and probe batch 128. The linear and linear_z specs differ only in the variant, and the linear spec equals E30b's. Every adapted record is fixed_c, 132 steps, 0 non-finite steps, with n_windows = N and ssl_subjects = E30b's (= P for C3).
- There is one eval_hash per (setting, rotation) across D29, E30b and D24 S3M/S3FM. Filtered differs from unfiltered in every rotation. The test-index files are identical between the two, so the windows and prevalence are the same.
- `last` has the same adapt_spec, arm_spec and per-pass and per-step SSL losses as E30b, and the same restored pass. `last_noise` differs from E30b only in arm and data_hash, with data_hash = _hash(E30b data_hash, "noise").
- The D29 last and lp linear values equal E30b exactly in 240 of 240 records (test_at_best, test_last, val_curve, best_epoch, best_val).
- Per-tag counts: 2266, equal to the reader's list.

## Rule 1 (E30 C2/C3, each head): CONFIRMED
Every curve value, range, v - LP span, best N and per-rotation verdict count matches the README to 0.01. Siena linear_z reaches v - LP +2.91 at most.

## Rule 2 (noise control): CONFIRMED
For each subset, the mean, sd, 95% t-interval, TOST p (margin 3) and per-rotation values match. No subset has lo > 0 with mean > 3, so all four setting x head combinations read "no difference demonstrated" for both C2 and C3. The NB ratio is 0.3471 (Siena and filtered) and 0.3379 (CHB-MIT).

## Selection facts: CONFIRMED
The selected epoch is 9 (the last of 10) in 147/210 last-linear fits, 145/210 last_noise-linear, 22/30 lp-linear, 40/210 last-linear_z, 43/210 last_noise-linear_z and 6/30 lp-linear_z.

## PR-AUC: CONFIRMED (descriptive)
- C1: all 34 rows x 3 metrics match. The same 3 string changes appear.
- C2/C3 on DL's split and on the rotations: all values and the 6 string changes match.
- Test prevalence: DL's split 1.49; CHB-MIT 0.66/0.33/0.21/0.32/0.16; Siena and filtered 0.98/0.43/0.99/0.54/0.91.

## Mismatch
In the summary, the E27-caveat line says the raw head shows no equivalence and that filtered TOST p is "0.04-0.15". In fact, Siena filtered linear P2N2048 gives TOST p 0.037 < 0.05: +0.90 [-1.53, +3.33], equivalent within +-3 at that one subset. The README table already shows 0.037; only the prose is wrong.

## Additions
- The linear_z "bimodality" is an epoch-selection flip:
  - Siena filtered rot0 seed 2000: epoch 2 gives ROC about 81.5, epoch 0 gives about 66.9. Val ROC differs by under 0.6 between the two (79.2-79.8).
  - Siena rot3 seed 3407 last_noise: epoch 0 gives 65.3 (val 59.2), epoch 9 at P2 gives 72.6 (val 58.7).
  - No rule outcome depends on these flips.
- The filtered raw-head noise curve passes C3 "supported as written" by only +0.02. Its minimum is +3.02 over LP.
- On Siena linear, all 7 noise-rule intervals also exclude 0 on trapz, not only on AP; every mean is below 0.5.
- The C1 PR reading leaves out existing records that read "first term wins" on ROC. On AP and on trapz, every one of them reads "no difference shown":
  - E32 S1R BIOT: ROC +3.61
  - E32 S3R BIOT: ROC +9.04, AP +2.07
  - q95 P1Q BIOT linear: ROC +8.80, AP +0.14
  - q95 P1Q BIOT MLP: ROC +8.61
  - S3FQ BIOT: ROC +3.75, AP +0.30
  - S1FM, S1RZ, S3RZ and S1X read "no difference shown" on all three metrics.
- Code gate: green now (pytest 87 passed, 2 skipped; ruff clean, including d28_read.py).

## Dated note (2026-11-05): the two label-count lines above ("3 string changes", "6 string changes") are
superseded by D30: PR-AUC no longer carries ROC-derived labels. This re-check confirmed the PR-AUC VALUES
(34 rows x 3 metrics, the C2/C3 values, the prevalences) and those confirmations still hold unchanged.
