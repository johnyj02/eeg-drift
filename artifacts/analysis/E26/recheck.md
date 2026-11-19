# E26 / E26-filt adversarial re-check (2026-11-01)

Own loader over artifacts/s3-results/**/results/*.json (diag-/test-index-/val-index-/report- skipped,
no smoke records exist), own paired rule and D17 rule; read_d24.load not used. Scripts were in /tmp, not kept.

1. Integrity CONFIRMED. S1Z/S3Z/S3FZ/P1Z each have 40 records = 2 models x 4 arms x 5 (rotation at S_r, or paper seed).
   Every record has probe linear_z only, probe v4, eval mode, tap encoder, input_norm "". No duplicate cells.
   eval_hash matches S1M/S1L, S3M, S3FM and P1E in 10/10, 10/10, 10/10 and 2/2 (model, split) cells. S3Z and S3FZ hashes are disjoint.
   S1FM has 150 records (300 head cells), seeds [S_r, 1000+r, 2000+r], 5 eval hashes, 0 of them shared with S1M/S1E/S1L/S1Z.
   Test and val index lists are identical to S1L in all 5 rotations; n and prevalence are identical; the SSL data_hash is identical.
   E26 adaptation matches D24-A at S_r: SSL epoch_losses are identical in 20/20 cells per (tag, model), and the probe spec differs only in `variant`.
2. Every E26, P1Z and S1FM mean, per-rotation value and rule string CONFIRMED (to 0.1 ROC). Spot-check bootstrap CIs agree within 0.1.
3. CONFIRMED. BIOT Siena last - lp: D24-A +9.23 (FIRST), linear_z +0.79 (none).
   The S_r seed for BIOT is in S3M/S3FM/S1M; S3E/S3FE/S1E hold CBraMod only.
   Raw head at S_r: +6.85 [+7.9, +11.7, -5.6, +12.5, +7.7], FIRST. Siena filt: +3.63, FIRST.
4. CONFIRMED, no bug sign. rot0 BIOT lp/last test ROC 49.91/50.01, val 0.8876/0.8917.
   The scores are not constant: AP is 0.083/0.087 against a prevalence of 0.0066, and the raw head's AP at the same rotation is 0.011.
   Per-epoch test ROC goes 0.39 -> 0.50 and AP 0.006 -> 0.083. The E15 CPU z-head (StandardScaler zero-variance rule) gives the same 49.9.
   The minimum per-dim feature std is 0.187, so the 1e-6 std clamp is not involved.
5. CONFIRMED as stated (BIOT 4/9, CBraMod 2/9 against 3-seed D24-A).
   Caveat: at matched seeds (raw head at S_r vs linear_z) BIOT changes 6/9 and CBraMod 1/9.
   The 2 extra BIOT changes are both on CHB-MIT: last_randinit - last goes from SECOND to none, and lp - lp_randinit from FIRST to none.
   The CBraMod CHB-MIT last_randinit - last change is a seed-count effect. D17 is unchanged everywhere.
