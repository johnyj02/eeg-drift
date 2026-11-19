# D27-C / D27-D re-check

Independent re-check, recomputed from the raw records in artifacts/s3-results (all `results/*.json` scanned, not only the reader's directories). The code is separate from scripts/analysis/d27_cd.py. Only `read_step1.paired` and `bootstrap_d24.cluster_ci` were imported, after checking them against the D18 and D24-D text. The C2/C3 rule was re-coded from the D15 text and the E30 reading choices.

Verdict: **CONFIRMED.** Every verdict string and every key number matches to the printed precision. Nothing is refuted.

## What was checked

- **Records.** 170 records: S3CLPB 15, S3FCLPB 15, P1FT 20, S1FT 60, S3FT 60. 0 duplicates and 0 smoke records anywhere in the store. Seeds are as expected: [S_r, 1000+r, 2000+r] on rotations, 42/123/2021/3407/8888 on the paper split.
- **Record contents.** Versions are adapt 3 / probe 4, eval mode, encoder tap. Labels are upstream on the paper split and overlap on rotations. The checkpoint sha is pinned on lp, with no checkpoint on lp_randinit. Head size is 257 for BIOT and 32,001 for CBraMod.
- **History.** Every record has a 10-epoch history. best_epoch is the argmax of val ROC, and test_at_best and test_last equal the logged epochs. Best-epoch counts match the README.
- **eval_hash.** There is one eval_hash per (data, split) across S3CC, S3CLPB, S3E, S3M, S3FT and S3L. The same holds for S3FCC, S3FCLPB, S3FE and S3FM, for S1E, S1M, S1FT and S1L, and for P1E, P1FT and P1L.
- **Data variant of S3FT.** S3FT is unfiltered Siena despite the "S3F" prefix (its eval_hash is the S3E one). The reader paired it correctly.
- **C (D15 rules with the E30 choices, at S_r).**
  - Siena: LP 82.57, curve 84.56 to 84.61, v - LP +1.99 to +2.03, range 0.05. Result: "not testable" / "uninformative".
  - Siena filtered: LP 89.95, v - LP +0.11. Same strings.
  - Per rotation, rot0 is the exception (+6.2, LP seed 42 at epoch 0: 83.40 vs 87.85 and 87.16).
  - Probe batch effect (b128 - b256): +1.75 on Siena, +0.55 on Siena filtered.
- **D (D18 rule on 3-seed rotation means; D24-B on the paper split).**
  - Recomputed differences: -3.13, -0.80, +3.22, +7.19, +0.28, +11.76, each with the same per-unit values, sign counts, t intervals, leave-one-out strings and frozen-reference differences.
  - The bootstrap CIs agree to 0.1 (same seed 20261101).
- **Encoder training.** Built on CPU, the encoder has 3,186,688 parameters with a gradient for BIOT and 4,883,600 of 4,924,000 for CBraMod (mask_encoding and proj_out have no gradient). The minimum train-loss gap to the logged linear run is 2.71e-4, and ft is lower at epoch 9 in 140/140 records.
- **Published values.** Re-read from arXiv 2305.10351v1 (Table 2, CHB-MIT Balanced Acc. / AUC-PR / AUROC) and arXiv 2412.07236v6 (Table 8, plus fine-tuning Table 6: lr 1e-4, batch 64, 50 epochs, clip 1, dropout 0.1). The quoted values and the recipe text are exact.
- **Upstream code** (read only):
  - BIOT `supervised()` raises NotImplementedError for anything but TUAB. It uses BCE (focal loss is commented out), Adam with weight_decay 1e-5, EarlyStopping patience 5, and a default batch of 512.
  - CBraMod multi_lr sets the head lr to 0.001 * sqrt(64/256) = 5e-4.
  - Both process2.py files use test chb23/24 and val chb21/22.
- **Gate:** 78 passed, 2 skipped, ruff clean. e30_c2c3.py is unchanged since E30 (same mtime as the E30 README).

## Additions (descriptive)

- The BIOT CHB-MIT "pretraining helps fine-tuning" verdict depends on the seed as well as the rotation. Read with one seed per rotation: S_r +4.28 (helps), 1000+r +4.31 (helps), 2000+r +1.06 ("no difference shown", 4/5 > 0). The CBraMod verdicts hold at every seed index (CHB-MIT +5.55 / +6.26 / +9.76; Siena +11.52 / +11.66 / +12.10).
- The two C tables in README.md (lines 31-32 and 57-58) have 8 header cells but 9 delimiter cells, so GitHub-flavoured Markdown will not render them as tables.
- The ft spec records label_smoothing 0.1, but it is not applied for binary tasks (BCEWithLogitsLoss, src/eegdrift/probe.py l.231). The README's "BCE on logits" is correct, but the stored field is misleading.
- BIOT's "Pretrained BIOT (6 EEG datasets)" row, which CBraMod's Table 8 cites as "BIOT", comes from a model further trained on the CHB-MIT training set (BIOT section 3.6). It is not an unsupervised-pretraining-only number.
- The D24-B rule defines only a gain. So for BIOT on the paper split, "second term wins" is a paired() output, not a D24-B outcome. The README already labels it descriptive.
