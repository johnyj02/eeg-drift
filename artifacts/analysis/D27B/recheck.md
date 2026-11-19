# D27-B re-check (2026-11-02)

Recomputed from the raw records (own loader; D18/D17 rules re-implemented; cluster_ci for CIs).

- Records: S1Z, S3Z, S3FZ 120 each with seeds [S_r, 1000+r, 2000+r]; P1Z 40 (5 seeds); 0 duplicates, 0 smoke;
  linear_z only, adapt 3 / probe 4, eval, tap encoder. Raw pairs S1E+S1M / S3E+S3M / S3FE+S3FM (170 each:
  CBraMod S_r from *E, rest from *M) and P1E: same eval_hash, test index, n, prevalence; adapt spec differs only in
  the input_norm field the old records lack; epoch SSL losses identical in 60/60 (20/20 P1Z).
- All 24 rotation verdicts, both heads, every per-rotation / per-seed value and arm row reproduced (0 mismatches);
  E26 at S_r re-derived = published E26 (24/24); D24-A re-derived = published D24-A (24/24); CIs within 0.2.
- Co-primary: 3 head-dependent (BIOT Siena last - lp; BIOT Siena filtered last - lp and last_randinit - last).
  CONFIRMED. Strictly D27-B covers the 24 rotation outputs (21 hold); the 2 P1Z rows (both hold) are an extension.
- Fragile "holds": BIOT Siena lp - lp_randinit (-4.2, 4/5) needs rot2 negative (-2.8), which comes from one run:
  S3Z BIOT rot2 seed 1002 lp test 50.7 (val 74.4; last 53.6). Without that seed rot2 is +5.5 and the string is
  "no difference shown" (descriptive). On the E32 partition the same cell is -1.6, none (D26).
- Count fix for the report: 3 of the 6 E26 1-seed verdict changes do not survive 3 seeds (not 2).
- Reproducibility: the documented E26 command `read_d24.py --tags S1Z --seeds-per-rot 1` now prints INCOMPLETE
  for every arm (cells hold 3 seeds); the E26 tables in artifacts/tables can no longer be regenerated with it.
