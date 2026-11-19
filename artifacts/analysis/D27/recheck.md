# Re-check of D27 noise controls + LORO (cpu.md / cpu.json / noise.md)

The numbers were recomputed from the raw result JSONs in artifacts/s3-results, using separate code. That code did not import d27_cpu.py. It reused only read_step1.paired/d17/d19 and stats_d25.tost_p, which were read first and match the rule text. The selection rule was exactly one non-smoke record per (tag set, model, arm, split, seed, head), and each record was asserted to be adapt v3 / probe v4, eval mode, encoder tap, with overlap labels (upstream on the paper split).

## Result: every number and verdict is CONFIRMED

- **D19 verdicts and TOST:** all 38 rows match (18 registered, 20 at 1 seed). That covers the means, the 90% t-intervals, the TOST p values, the D19 strings, the per-unit values, last - lp and last_noise - lp. The totals also match: 2 "gain needs EEG data" (A1 linear and mlp_fullft), 16 "perturbation", and 7 TOST-equivalent.
- **LORO:** 18 of 80 verdicts change, from 25 of 400 drops (D24-A 6/24, E32 2/16, D27-B 6/24, D26 4/16). All 18 are BIOT, and none is D17 or a last - lp verdict. The earlier E26 1-seed reading also checks out: 7 of 24 change there, 3 of them CBraMod.
- **Bit-reproducibility:**
  - P1QN vs P1Q: 20/20 identical.
  - S3FQN vs S3FQ: 30/30 identical.
  - S1LRN/S3LRN last linear vs S1LR/S3LR: 45/45 identical.
  - Every last_noise data_hash equals _hash(last data_hash, "noise").
  - S1R/S1RZ, S3R/S3RZ, S3L/S3Z and S3FL/S3FZ use the same last SSL sample.
- **Pairing:** 340 triples with the same eval_hash, test index and test n/prevalence. The probe specs differ only in default fields that the older S1M/S3M records omit (tap and input_norm). There are no duplicate records anywhere in the tree.
- **Reader output:** d27_cpu.py, run to a temporary directory, reproduces cpu.md, cpu.json and noise.md byte for byte. The gate is green (78 passed, 2 skipped; ruff clean).

## Imprecise or missed

1. **A7 is not called descriptive in the rule text.** The "D27 addition" calls only A5 descriptive, and D27-A calls only A4 descriptive. Read literally, A7 is registered. Its outcome would not change: "perturbation alone explains it", TOST p 0.397 / 0.405, not equivalent. The registered count would become 20 rows: 2 gain, 18 perturbation, 7 equivalent.
2. **"Only the last arm differs" (A7) is imprecise.** The S3D11 and S3D12 last values are within 0.07 ROC of the S3M last at S_r, and the noise values are within 0.06 of S3N. A7 last - last_noise (+2.71 / +2.73) equals E27 at S_r (+2.71). Both arms reproduce E27.
3. **The A4 re-run cells are not re-runs in both arms.** In the 9 cells (cells 3/4/5, rot0/2/3), the last records were written at 22:19 by the original ml.g5.8xlarge jobs, which then ran out of memory (RUNLOG). Only last_noise (02:10) comes from the ml.g5.16xlarge re-runs. So each pair mixes instance types, both on A10G. Each cell still has exactly one record.
4. **rot4 drives the A4 raw-head differences.** With the linear head, rot4 gives last - last_noise of +15.4 to +19.7 in every cell, and rot0 gives -2.9 to -12.2. Without rot4, cell 3 linear ("gain needs EEG data") is +0.05, and its 4-of-5 positive count includes +0.4 and +0.5. This is descriptive and post hoc.
5. **The raw heads are under-trained here too.** The best epoch is the final one in P1QN linear and mlp_fullft 30/30, S1RN linear 15/15, S3RN linear 15/15, S3NM mlp_fullft 15/15 and S1LRN linear 39/40. So the A1 raw-head "gain needs EEG data" sits on below-chance arms and on heads that select their last epoch. This is descriptive.
6. **The quoted E29 range leaves out a cell.** The "D27 addition" quotes E29 as +18.8 to +21.5, but Siena cell 3 is +9.89 (e29.json). The reader's "quoted gains reproduce" passes over this.
7. **The "head-dependent" label for A1 is an interpretation.** It borrows the D27-B both-heads rule, but D27-A says "each head separately". Calling A1 head-dependent is therefore descriptive, not a rule output.
8. **One descriptive row passes TOST.** A5 S3LRN3 linear_z has TOST p 0.022. It is descriptive and not read.
