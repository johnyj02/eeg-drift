# D26 re-check (2026-11-02)

Recomputed from the raw records (own loader over artifacts/s3-results; read_step1 paired()/d17() rule
logic re-implemented, bootstrap_d24.cluster_ci for CIs). Not imported: scripts/analysis/d26_d27b.py.

- Records: S1RZ, S3RZ 120 each (2 models x 4 arms x 5 rotations x 3 seeds [S_r, 1000+r, 2000+r]), 0 duplicates,
  0 smoke; probe linear_z only, adapt 3 / probe 4, eval, tap encoder, input_norm "", overlap labels,
  fold_seed 20261101. Each pairs with S1R/S3R (same eval_hash, test index, n, prevalence, adapt and arm spec;
  probe spec differs only in variant; epoch and step SSL losses identical in 60/60 adapted runs). One eval set
  per rotation; every RZ eval_hash differs from S1Z/S3Z (partition change took effect).
- Every contrast mean, per-rotation and per-seed value, verdict and arm row in README.md reproduced (0 mismatches);
  CIs within 0.2 (Monte Carlo).
- D26 rule: all 3 E32 BIOT CHB-MIT non-replications read "no difference shown" with linear_z -> "raw-head effect"
  (last - lp +0.7; last_randinit - last +2.6, 3/5 positive; lp - lp_randinit -3.4, 3/5 negative). CONFIRMED.
- Descriptive counts 9 / 16 / 13 (E32 raw / E26 at S_r / D27-B) CONFIRMED. Anomaly rows CONFIRMED.
- Note: outside the 3 registered cells the standardized head removes 4 raw-head wins on this partition, not 3:
  BIOT Siena last - lp +9.0 "first term wins" -> +1.7 "no difference shown" is the fourth (post hoc).
