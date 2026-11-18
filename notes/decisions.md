# Decisions

Every entry states whether it was made BEFORE or AFTER seeing the relevant data. Corrections go
in place with a dated note; nothing is silently rewritten.

## D1. Licensing (2026-10-15, before any result)
Release under MIT. Model code vendored from the MIT BIOT and CBraMod repos (`src/eegdrift/models/
vendor/`, licences alongside). Upstream `c3n-group/efficient-eeg-adapt` is GPL-3.0: it is read
from a sibling clone (`../_upstream/`) and reimplemented from observed behaviour; no file of it is
copied. Data terms bind separately: TUAB/TUEV derivatives never ship; CHB-MIT (ODC-By) may.

## D2. Substrate (2026-10-15, before any result)
<JOB_LIBRARY>, us-east-1, stock SageMaker PyTorch 2.6 DLC (py312). GPU stages on `ml.g5.8xlarge`
(1 x A10G, 128 GB RAM; quota 144) so the 40 GB float32 CHB-MIT eval store fits in RAM at full
precision. Reason: the parity probe runs the frozen backbone in train mode (upstream behaviour:
dropout active), so features cannot be cached and the eval split is re-read every epoch.
`ml.g5.2xlarge` (quota 50, 32 GB RAM) would force fp16 storage, a parity deviation.

## D3. Configuration (2026-10-15)
Plain YAML loaded into frozen dataclasses, not Hydra. Hydra's value (CLI composition, launcher)
is unused: arms are declarative in `configs/adapt.yaml` and jobs are built by `JobSpec`. Hydra
is kept as a dev dependency only, to reproduce upstream config behaviour in a test.

## D4. CHB-MIT parity N (2026-10-15, BEFORE any adaptation or probe result)
The paper reports N_total = 4,174 CHB-MIT SSL windows. Reimplementing their documented SSL
pipeline (make_CHBMIT_for_pretraining.py behaviour) over chb01-chb22 yields **81,993** windows
(655 files; per-file counts match their code, e.g. chb01_03: 116 windows, 115 kept). We cannot
tell from the code how 4,174 arose. Parity runs therefore use a seeded uniform subsample of
exactly 4,174 windows (seed 4174); a full-N sensitivity arm is deferred until parity results
exist. The paper's own eval set is reproduced exactly (326,993 windows; test prevalence 252 /
16,964 = 1.486%, their "random baseline 1.48%").

## D5. Adaptation protocol for arms (2026-10-15, before any result)
Headline arm comparisons use upstream's Table-1 ("parity") path: batch 256, E = 3 (CHB-MIT,
TUAB) / 5 (TUEV) epochs of the parity N, AdamW 3e-5 / wd 5e-2, cosine to 1e-6, clip 1.0, keep the
lowest-training-loss epoch. CHB-MIT parity: 3 x ceil(4174/256) = 51 optimizer steps. The
fixed-compute (Fig. 1) path is implemented (`protocol: fixed_c`, S = 4 x ceil(N_total/128),
constant LR as in their diversity trainer) and run second.

## D6. Probe variants (2026-10-15, before any result)
Report both: `mlp_fullft` (what the shipped config builds: `training.full_ft: True`, a 3-layer
MLP of 64,402,401 params for CBraMod on 10 s windows; corrected 2026-10-15 from a typo'd 64,402,601) and `linear` (what the paper describes).
Never mix them in one table: distinct result types enforce it.

## D7. Release-faithful arm (2026-10-15, before any result)
Upstream loads pretrained weights into the SSL model only if `cfg.model.foundation_dir` exists;
no shipped config, README command or launcher sets it (tests/test_upstream_audit.py reproduces
this with Hydra). Arm `last_randinit` runs exactly that path. Also reproduced: as released,
`method=step_up` raises ConfigAttributeError at trainer.py:154 (`spt_anchor_l2sp_lambda` is in
no config), so the released code cannot have produced the paper's numbers unmodified.

## D8. Deliverable-2 pre-registration (2026-10-15, before any result)
`drift_topk` succeeds if non-inferior to `last` within delta = 1.0 AUCPR point (one-sided, paired
over seeds/rotations) at <= its parameter count (+-12% disclosed), superior if the paired
difference's 95% CI excludes 0. Primary metric: pr_auc_trapz (upstream's) with avg_precision
reported alongside.

## D9. Drift ranking statistic (2026-10-15, BEFORE any real diag result; code review CRITICAL)
Under AdamW every element moves ~lr per step regardless of gradient size, so the plan's relative
displacement ||dθ||/||θ0|| ≈ coherence · Σlr / RMS(θ0) ranks groups partly by weight scale.
`drift_topk` therefore ranks design A on Adam coherence ||dθ|| / (sqrt(n) · Σlr_t) and design C
on the RMS gradient ||g|| / sqrt(n), seed-mean over 5 seeds, with Kendall-τ stability reported.
The plan's ratios (rel) are still computed and reported beside them; a disagreement between the
two rankings is reported, not resolved silently. BIOT's design C is computed per seed because
its SSL loss runs through the randomly initialised `prediction` head.

## D10. Activation checkpointing (2026-10-15, before any result; code review CRITICAL)
Backprop through every block at batch 256 needs ~25-30 GiB; the A10G has 24 GB. Every
adaptation runs with per-block activation checkpointing (use_reentrant=False,
preserve_rng_state=True). tests/test_review_fixes.py shows gradients identical to the
uncheckpointed run (max |diff| < 1e-6, dropout active) for both models. Keyed in AdaptSpec anyway.

## D11. `all` arm trains CBraMod's mask token (2026-10-15, before any result; code review)
Upstream's layer-ablation "all" mode unfreezes every floating-point parameter, which includes
the (otherwise frozen) `patch_embedding.mask_encoding`. Our `all` arm does the same
(include_fixed), so CBraMod `all` trains 4,924,000 params; BIOT's integer `index` cannot train.

## Known residual deviations (2026-10-15)
- Eval windows are FFT-resampled from float32 (upstream: float64 pickles). Relative difference
  ~1e-7; not worth a 70 GB rebuild. Disclosed.
- Store content hashes cover meta + index (keys, labels, splits), not window values. A future
  rebuild with identical keys but different preprocessing MUST change the store description.

## D12. Reproduction screen and how it will be read (2026-10-15 18:10 local, BEFORE any result)
Eight jobs (notes/jobs-screen.txt), CHB-MIT, paper split, seeds 42 and 123, both probes:
R1 `last2_randinit`, `all_randinit` (wave-1 protocol, run_tag ""); R2 `last`, `last_randinit`
with the full 81,993-window SSL pool (run_tag R2-fullN); R3 `lp`, `last`, `last_randinit` at
batch 128 for SSL and probe (R3-b128); R4 the same arms on the paper-DESCRIBED eval
preprocessing (R4-filt, data prefix lmdb/chbmit_filt/). Reading rules, fixed now:
- "Random init explains BIOT SA" is supported if R1 BIOT rows are flat (all within 2 ROC points
  of `last_randinit`, 88.5) AND R2 pretrained `last` stays below 70 ROC.
- "The data budget explains it" is supported if R2 pretrained `last` reaches >= 78 ROC.
- A knob (R3 batch, R4 preprocessing) "moves" a cell if its 2-seed mean shifts by > 5 ROC points
  toward the paper's value; otherwise it is reported as not explaining the gap.
- None of these is proof of what the authors ran; the author email (notes/author-email-draft.md)
  is the only route to that.

### D12 outcome (2026-10-17, applied mechanically to the rules above)
- Random init explains BIOT SA: **SUPPORTED.** R1 BIOT random-init last/last2/all ROC 88.48 /
  88.51 / 88.49 (flat, within 0.03 of last_randinit; paper Table 2: 88.67 / 88.44 / 88.60). R2
  pretrained `last` on the full pool: 55.25 (< 70).
- Data budget explains it: **NOT SUPPORTED** for BIOT (55.25 < 78). For CBraMod the full pool lifts
  the LINEAR-probe `last` from 74.0 to 86.7; the MLP-probe `last` is unchanged (86.5 -> 85.2).
- R3 batch 128 moves BIOT lp and last by +6.6 / +6.8 (to 59.0 / 58.8): toward the paper for
  `last`, AWAY for `lp`; nothing near 83. No CBraMod cell moves by > 5.
- R4 paper-described eval preprocessing: BIOT lp 52.4 -> 61.5 (away), last 52.0 -> 58.6;
  CBraMod lp 85.3 -> 81.3 (mlp), 65.4 -> 46.9 (linear); CBraMod last mlp 86.5 -> 83.1 (paper 83.67).
- Unexplained: the paper's CBraMod LP (54.14 ROC). No knob reproduces it with either probe.

## D13. Reading the 5-seed confirmation (2026-10-19 14:20 local, BEFORE any result)
Configuration under test (the closest family found by the screen): linear probe, batch 128 for
SSL and probe, `last_randinit` as the SA arm; upstream eval (run_tag R3-b128, 5 seeds pooled) and
paper-described eval (C-filt-b128, 5 seeds). Per Table 1 cell, report the worst-metric gap
(bal/PR/ROC) in units of the paper's SEM (floor 1 point). A cell is "consistent" at <= 3 SEM on
all three metrics, "partially consistent" at <= 3 SEM on two of three, otherwise "not
consistent". The configuration is called consistent with Table 1 only if all four cells are at
least partially consistent under ONE of the two eval variants. The contrast that must also hold:
pretrained `last` stays "not consistent" for BIOT SA. Whatever the outcome, the note says
"consistent with", never "the authors ran".

### D13 outcome (2026-10-19 22:00 local, AFTER the results; rule applied as written)
Linear probe, batch 128, 5 seeds. Gaps in paper-SEM units (bal/PR/ROC):
- upstream eval: BIOT LP 0.2/2.7/11.6 partial; BIOT SA random 5.0/6.2/3.6 NOT; CBraMod LP
  0.3/2.6/10.6 partial; CBraMod SA random 0.5/0.3/1.2 consistent.
- filtered eval: BIOT LP 0.0/2.4/19.4 partial; BIOT SA random 5.2/4.0/3.3 NOT; CBraMod LP
  0.2/0.8/4.1 partial; CBraMod SA random 1.2/0.6/2.4 consistent.
- Contrast held: BIOT pretrained `last` NOT consistent (12.4 and 9.8 SEM on ROC).
**Verdict: the configuration is NOT consistent with Table 1 as a whole** (BIOT SA fails under
both eval variants: our random-init BIOT is ~6 ROC points ABOVE the paper, 89.9 vs 83.1).
CBraMod SA is reproduced (random init only; pretrained misses ROC by 5.0 and 15.8 SEM). The
LP rows match on balanced accuracy and PR but not ROC. No configuration we tried reproduces all
four cells; random init remains the only one that puts BIOT SA in the paper's regime.

## D14. Stop the replication search (2026-10-20, after D13)
The decisive comparison for the paper's claim C1 (pretrained vs random init) is settled: ~30
ROC-AUC points, stable across ~10 configurations. The residual (BIOT SA 89.9 vs 83.1) depends on
unrecoverable inputs (their 4,174 windows, seeds); only the authors can close it, and the email
asks. No further digit-matching runs. Exception (approved by the user 2026-10-20): the C2/C3
audit test (D15), which tests whether the paper's other two claims hold for the pretrained FM.

## D15. C2/C3 audit test design and reading rules (2026-10-20, BEFORE any run)
Shared: CHB-MIT, paper split, arm `last` with init pretrained AND random, linear probe at batch
128, model seed 42, ONE seed (so only differences > 3 ROC-AUC points are interpreted), both
models. Upstream's fixed-compute path (ablation_diversityN/P): S = 4 x ceil(4,174 / 128) = 132
optimizer steps at batch 128, constant lr 3e-5, lowest per-pass mean loss restored (D16).
- C2 ("peak performance needs only 20-50% of the data"): N in {896, 1664, 2048, 4174} (upstream's
  ladder rounding of 20/40/50/100% of 4,174), subsets drawn from the 4,174-window parity pool
  with upstream's seed rule rng(data_seed * 1,000,003 + N_total), data_seed 1.
  Reading: C2 is "supported for the pretrained FM" only if the pretrained curve's best N is <= 2048
  AND it beats both its N = 4174 value and the LP baseline by > 3 ROC points. LP baseline =
  5-seed `lp`, linear probe, batch 128 (run_tag R3-b128: BIOT 58.6, CBraMod 68.9 ROC), the same
  probe batch as this test. [Corrected 2026-10-20 BEFORE any C2/C3 run: this said the wave-1
  batch-256 lp (52.0 / 65.4), which uses a different probe batch.] If the pretrained curve stays within 3 points of LP at every N, C2 is "not testable for
  the pretrained FM: adaptation adds nothing at any N" (the curve has no peak to locate).
- C3 ("patient count does not matter at fixed N"): N = 2048, P in {3, 11, 21} subjects (chb01 and
  chb21 count as one subject), drawn seeded from the chb01-chb22 SSL pool (81,993 windows), about
  N/P windows per subject (upstream-style stratified allocation).
  Reading: "flat" if max - min ROC across P <= 3 points. Flatness supports C3 for the pretrained
  FM only if the pretrained curve is also > 3 points above LP; flat at the LP level means
  "uninformative" (adaptation changes nothing, so nothing can vary with P).
- Estimated cost: 28 runs, ~10 GPU-h, ~$34-40.

## D16. Fixed-compute mode restores the lowest-loss pass (2026-10-20, before any fixed_c run)
Upstream's diversity trainer (trainer_diversityN.py ~line 270-303) evaluates the mean SSL loss at
the end of every pass over the subset and restores the lowest-loss pass before transfer. Our
`fixed_c` kept the final state. Fixed before the C2/C3 test; ADAPT_CODE_VERSION bumped.

### D15 outcome (2026-10-20 13:30 local, AFTER the results; rule applied as written)
Seed 42, linear probe, fixed_c 132 steps. ROC-AUC x100 (LP baseline R3-b128: BIOT 58.6, CBraMod 68.9).
| model, init | N896 | N1664 | N2048 | N4174 | P3 | P11 | P21 |
|---|---|---|---|---|---|---|---|
| BIOT pretrained | 59.2 | 58.9 | 59.1 | 59.2 | 58.1 | 59.3 | 59.2 |
| BIOT random | 89.8 | 89.8 | 89.8 | 89.8 | 89.8 | 89.8 | 89.8 |
| CBraMod pretrained | 76.2 | 76.5 | 76.3 | 76.6 | 76.7 | 76.4 | 76.4 |
| CBraMod random | 88.7 | 88.0 | 87.8 | 86.1 | 87.9 | 88.2 | 87.8 |
- C2, BIOT pretrained: **not testable** (within 0.6 of LP at every N: adaptation adds nothing).
- C2, CBraMod pretrained: **not supported** (best N is 4174, range 0.5; no peak at 20-50%). The
  curve is flat and +7.3 to +7.7 above LP at every N, so 21% of the data gives the same result.
- C3, BIOT pretrained: **uninformative** (flat at the LP level, range 1.2).
- C3, CBraMod pretrained: **supported as written** (range 0.3, +7.5 above LP). Caveat: C2 shows the
  result does not depend on N either, so "patients do not matter" may mean "the data does not matter".
- Observation (not a D15 rule): BIOT random init gives 89.80-89.84 at every N and P (range 0.04).
  The SSL data does not change the random-init result, so its gain over pretrained is consistent
  with probing random features, not with SSL adaptation. Tested by D17.

## D17. Random-weights probe control `lp_randinit` (2026-10-20, AFTER seeing the D15 data)
Added because of the observation above, so it is a post-hoc control and the note says so.
Arm: random-init encoder (same seeded init as `last_randinit`), no adaptation, linear probe.
Reading (fixed now, before any lp_randinit run): per model, over the 5 corrected-protocol
rotations (D18), "the random-init SA result is explained by random features" if
|mean(last_randinit) - mean(lp_randinit)| <= 3 ROC points; "SSL adds to random init" if
last_randinit - lp_randinit > 3 in mean and in >= 4/5 rotations.

## D18. Corrected protocol, Step 1 (2026-10-20, BEFORE any run; go read from the user's "proceed with the next steps", 2026-10-20)
- Labels: a 10 s window is positive iff it overlaps any seizure interval by >= 1 sample (the
  posthoc "fixed" rule; seizure table configs/chbmit_seizures.json from the 24 PhysioNet summaries).
- Windows: val and test use grid windows only (no oversampled duplicates). Train keeps grid +
  oversampled seizure windows, relabelled by the same overlap rule (augmentation only in train).
- Splits: 5 subject rotations rot0-rot4 (configs/data.yaml seed 20261014), chb01/chb21 together,
  4-5 test subjects per fold, 21-41 seizures per test fold. SSL pool = SSL store minus the
  rotation's test subjects (chb23/chb24 are not in the SSL store; H1 skipped: it only shrinks a
  >= 60k-window pool from which 4,174 windows are drawn).
- Everything else unchanged: upstream eval preprocessing, parity SSL protocol (batch 256, 3
  epochs, N = 4,174), linear probe, default probe batch 256, seed 42 per rotation (rotations are
  the replicates). Arms: lp, last, first, first2, all, last_randinit, lp_randinit; both models.
- Reading, ROC-AUC, paired by rotation (PR-AUC reported, not used: prevalence varies by fold):
  - Primary (Paper B): d = first - last, pretrained. "Early beats late" for a model if mean d > 3
    AND d > 0 in >= 4/5 rotations; "late beats early" if mean d < -3 AND d < 0 in >= 4/5;
    otherwise "no difference shown". Same rule for first2 - last (secondary).
  - Paper A: "last-layer SA helps the pretrained FM" if last - lp > 3 in mean and >= 4/5
    rotations; "pretrained vs random" contrast = last_randinit - last, same rule.
  - all - last reported as the capacity reference, no verdict.
- Estimated cost: 70 runs, ~25-30 GPU-h, ~$80-95.

### D18 amendments (2026-10-20 14:00 local, BEFORE any Step 1 run; from the adversarial review)
- Seizure bounds: the table now holds TRUE [onset, offset) samples (seconds x 256). The first
  version used upstream's seconds x 256 - 1, which labelled 13 windows ending exactly at onset
  positive (paper-split test: 114 true positives, not 116; the posthoc "fixed" count of 116 had
  the same off-by-one and is re-scored). The eval hash now includes the table and a rule version.
- Seeds: rotation r uses seed [42, 123, 2021, 3407, 8888][r] for all its arms, so the five
  rotations do not share one random draw. Pairing inside a rotation is unchanged.
- Arms: first2 dropped from Step 1; added first_block, embed_only, first_noise (D19). Final list:
  lp, last, first, first_block, embed_only, first_noise, all, last_randinit, lp_randinit.
- Every verdict holds "with a linear head" only; the shipped MLP head is not tested under the
  corrected protocol.
- Smoke subsamples keep up to 25 positives per split so the smoke exercises val selection.
- Estimated cost: 90 runs, ~30 GPU-h, ~$90-110.

## D19. Paper B controls (2026-10-20, BEFORE any run)
Why: `first` (embed + block00) differs from `last` (one block) in both depth and the embedding,
and a gain could come from any perturbation of pretrained early layers (pretrained BIOT is ~30
ROC below random init on CHB-MIT, so moving away from the checkpoint might help by itself).
- first_block = block00 + SSL head: depth contrast at the same parameter count as `last`.
- embed_only = patch embedding + SSL head: the embedding's share.
- first_noise = `first` groups and protocol, SSL inputs replaced by Gaussian noise with the
  SSL sample's per-channel mean and std (seeded per run).
Reading (paired rule of D18, ROC, 5 rotations, linear head):
- "Depth matters at equal parameters" if first_block - last wins by the rule.
- "The gain needs EEG data" if first - first_noise wins by the rule; "perturbation alone
  explains it" if |mean(first - first_noise)| <= 3; otherwise "unclear".
- embed_only - lp reported with the same rule.

## D20. Binary probe scores are logits (2026-10-20 13:55 local, BEFORE any Step 1 run)
The Step 1 GPU smoke gave `lp_randinit` (CBraMod) test scores of exactly 0.0 for all 500
windows: float32 sigmoid underflows for logits below about -100, so every window tied and
ROC-AUC read 0.500. Earlier runs had the same effect in a small way: 5 of 296 saved score files
(all CBraMod `last_randinit`, linear head) have 0.1-1.8% of test windows tied at exactly 0 or 1,
which can only LOWER their ROC-AUC (conservative for the random-init finding). [Corrected
2026-10-20 22:25: a tied pair counts 0.5, so ties can move ROC-AUC either way; the effect is
bounded by the 0.1-1.8% of windows involved.] Fix: binary
scores are now raw logits (same ranks, threshold 0 = probability 0.5), PROBE_CODE_VERSION 3.
Earlier numbers are not re-run. Step 1 arm order puts lp_randinit and lp first, so a degenerate
control shows in the job log within ~30 min.

## D21. Siena Scalp EEG pipeline (2026-10-20, BEFORE any Siena data is windowed or run)
Spec: notes/siena-spec.md. Choices for its open questions, fixed now:
- Eval preprocessing: PRIMARY = the CHB-MIT eval path (unfiltered, per-window FFT resample to
  2,000 samples, /100), so the two datasets differ only in data. SECONDARY = filtered
  (0.3-75 Hz, 50 Hz notch) as data variant `filt`, reported as a robustness row only.
- Labels: D18 overlap rule on TRUE [onset, offset) bounds; oversampled windows in train only.
  Annotation fixes exactly as in the spec (PNO->PN0 names, PN00-3 end 18.29.29, EDF header start
  as clock origin, midnight wrap; PN10 alternatives -> union).
- Channels: 16 BIOT bipolar pairs from Siena's referential electrodes (T3/T4/T5/T6 = T7/T8/P7/P8);
  QC is reported, never used to drop data (no zero-fill, no file dropped).
- Splits: 5 subject rotations, seed 20261014 (index.rotations unchanged); no paper split.
- Protocol, arms, seeds and reading rules: identical to Step 1 (D18/D19/D20), run_tag S3.
- Not done: CSBrain-split reference, signal spot-checks of annotations (YAGNI; noted in limitations).

## D22. Step 2: does a label-free diagnostic say where to adapt? (2026-10-20 15:30 local, BEFORE any
Step 2 run and before any Step 1 arm with adaptation was read; only rot0 lp/lp_randinit seen)
- Outcome per group k and rotation r: gain(k, r) = ROC(single-group arm k) - ROC(lp), same
  corrected protocol, seeds and linear head as Step 1 (D18). Single-group arms adapt group k +
  SSL head: BIOT embed, block00 (first_block), block01, block02, block03 (last); CBraMod embed,
  block00 to block11. New arms: single_b01 .. single_b10 (BIOT uses b01, b02 only).
- Diagnostic: design C, RMS SSL gradient of the frozen pretrained model per group, computed on
  each rotation's OWN adaptation pool (scripts/diag_c_rotations.py, 5 seeds, label-free, run
  before any Step 2 result exists). Design A (post-adaptation displacement) exists only for the
  paper split and is reported descriptively.
- Reading, per model and dataset (n groups: BIOT 5, CBraMod 13):
  - "Design C predicts where to adapt" if Spearman rho(design-C score, gain) over groups is
    >= 0.5 in the mean over rotations AND > 0 in >= 4/5 rotations.
  - "Top-1 hit rate": rotations whose design-C top-1 group is also the best single group
    (chance: 1/5 BIOT, 1/13 CBraMod). Reported, no verdict.
  - Otherwise "no predictive value shown".
- Datasets: CHB-MIT (run_tag S2) and Siena (run_tag S4). Estimated cost ~$75 for both.

### D17/D18/D19 outcome (2026-10-20 22:30 local, AFTER the results; rules applied as written)
Step 1 (CHB-MIT, S1) and Step 3 (Siena, S3, unfiltered primary eval), 5 rotations, 1 seed each,
linear head, ROC-AUC x100, mean of paired differences (tables: artifacts/tables/chbmit-S1.md,
siena-S3.md). Verdict strings are the rule outputs of scripts/read_step1.py.
| contrast | BIOT CHB-MIT | CBraMod CHB-MIT | BIOT Siena | CBraMod Siena |
|---|---|---|---|---|
| primary first - last | +4.2, early wins | -1.4, none | +3.5 (3/5), none | -5.7, LATE wins |
| first_block - last (equal params) | +1.0, none | -1.1, none | +6.9, early wins | -0.2, none |
| embed_only - lp | +2.7, none | +6.1, embed helps | +0.9, none | -9.0, embed hurts |
| first - first_noise (D19) | +1.9, perturbation alone | +2.2, perturbation alone | +4.4, unclear | +1.3, perturbation alone |
| last - lp (Paper A) | +2.9, none | +8.6, SA helps | +7.0, SA helps | -0.5, none |
| last_randinit - last | -4.2, PRETRAINED wins | +3.7, none | +5.4, none | +25.1, random wins |
| D17 last_randinit vs lp_randinit | random features | random features | random features | random features |
| all - last (reference) | +8.9 | -6.2 | +8.3 | -4.2 |
Reading:
- Paper B's primary claim holds only for BIOT on CHB-MIT, and there the D19 control says a
  noise-input update of the same layers gives the same gain. It is not a general finding: no
  effect for CBraMod on CHB-MIT, reversed for CBraMod on Siena. Equal-parameter depth effect only
  for BIOT on Siena.
- Paper A: under the corrected protocol the released code's random-init path no longer beats
  the pretrained checkpoint for BIOT on CHB-MIT (it did on the paper split: 88.5 vs 52.0), and
  for both models and datasets the random-init SA number equals random features with no SSL at
  all (D17). Last-layer SA helps pretrained CBraMod on CHB-MIT and BIOT on Siena only.
- Per-rotation spread is large (e.g. BIOT CHB-MIT lp 43.7 to 91.0); several cells are below 50.
- Caveat raised after the data: pretrained CBraMod is at chance on unfiltered Siena (lp 51.0;
  random features 76.5). Strong 50 Hz mains (79 QC flags) is a candidate cause; the D21
  filtered robustness row (run_tag S3F) is running. Not a new rule: it was pre-registered.
- Design C (per rotation, 5 seeds): ranking identical in every rotation (Kendall tau 1.0).
  CHB-MIT: BIOT embed > block02 > block01 > block03 > block00; CBraMod embed > block00 > block07
  > ... > block11. Siena BIOT block02 first. Step 2 (D22) NOT run yet.

### D21 robustness row outcome (2026-10-20 22:55 local, AFTER the results)
Siena with filtered eval (0.3-75 Hz, 50 Hz notch; run_tag S3F; artifacts/tables/siena-S3F.md):
- The 50 Hz explanation is NOT supported: pretrained CBraMod lp stays at chance (51.6 vs 51.0
  unfiltered) while random features give 81.8.
- Same direction as the primary row, stronger for CBraMod: last beats early (first - last -18.2,
  5/5; first_block - last -12.4, 5/5); last-layer SA helps pretrained CBraMod (+12.5, 5/5) and
  BIOT (+3.9, 4/5); BIOT primary and depth contrasts not shown; D17 random features for both.

## D23. CBraMod probe layer (2026-10-26, AFTER seeing data: post hoc, from the CBraMod check)
Finding (workflow wf_5c953a6c-3c7; weights, inputs and records verified correct): every CBraMod
probe so far read the output of `proj_out`, the masked-reconstruction head, by parity with
upstream src/model_factory.py:29 [corrected 2026-10-27 from :28] where `#backbone.proj_out = nn.Identity()` is commented out.
Official CBraMod downstream models probe the encoder output (proj_out = Identity). The pretrained
`proj_out` is nearly singular (condition number 7.5e6 [corrected 2026-10-27: 8.0e6 in a float64 SVD]; it suppresses directions holding 67% of the
encoder variance) and its output is ~100x smaller than a random head's, so a linear head at
lr 4e-4 / 10 epochs under-fits. Backbone dropout during probe training (train mode, upstream and
official parity) hurts pretrained CBraMod further. Evidence, Siena filtered, parity-style probe
with dropout off: pretrained encoder 89.4 vs random encoder 80.2 (vs logged 51.6 vs 81.8).
BIOT is NOT affected (it already probes its encoder output; dropout on/off changes it little).
Consequences: EVERY CBraMod number (wave 1, screen, D13, C2/C3, S1, S3, S3F) and every CBraMod
verdict is invalid as a statement about the pretrained model; they remain valid only as "what the
released code's probe computes". Adaptation arms also retrain proj_out, so CBraMod SA gains are
confounded with re-fitting the probed layer.
Decision (proposed, needs the user's go for GPU): primary CBraMod probe = encoder output, backbone
mode unchanged (train, as upstream and official CBraMod); secondary = encoder output, eval mode.
The old reading is kept as probe tap `upstream_proj`. Re-run run_tags S1E/S3E/S3FE, same D17-D19
rules. Minimum cost ~$70 (CBraMod S1 + S3 + S3F).
D23 approved by the user 2026-10-26 ("GO ahead with the code fix and the rerun"). Implemented:
CBraModAdapter.features/pooled read m.encoder(m.patch_embedding(x)); PROBE_CODE_VERSION 4; test
pins equality with the vendored model with proj_out = Identity. Primary only (encoder tap,
backbone train mode as before); the eval-mode secondary is NOT run on GPU (CPU numbers from the
check are in notes/cbramod-check.md). Re-run: CBraMod, 9 arms, 5 rotations, run_tags S1E (CHB-MIT),
S3E (Siena), S3FE (Siena filtered); BIOT keeps its S1/S3/S3F records. Rules: D17-D19 unchanged.
D23 amendment (2026-10-26, BEFORE any re-run result; based on the check, not on re-run data):
the CBraMod re-run probes in EVAL mode (dropout off in the frozen backbone), the standard frozen-
probe protocol and the judge's recommendation, because the check showed dropout moves pretrained
CBraMod features by 2.3x their between-window spread (random init: 1.1x). Local 1-epoch smoke,
rot3: pretrained lp 44.2 (train mode) -> 64.3 (eval mode). BIOT records stay in train mode
(as run); the check measured BIOT mode effects of -4.4 to +2.2 points on two rotations, stated
as a limitation; a BIOT eval-mode re-run (~$54) is offered, not run. Implemented as
ProbeSpec.backbone_mode, set per model in study.probe_template; recorded in every result.
D23 correction (2026-10-26, before any re-run): the "Implemented" paragraph above is superseded by
the amendment: the S1E/S3E/S3FE CBraMod runs use the encoder tap in EVAL mode. No live
`upstream_proj` tap exists; the released code's reading survives only in the v3 records
(S1/S3/S3F, wave 1, screen, C2/C3). Review (wf_1081af16-14e) noted the probe mode differs by model
(CBraMod eval, BIOT train as run), so cross-model comparisons are not made; within-model
contrasts (all D17-D19 rules) compare arms under one mode.

### D23 re-run outcome (2026-10-27 03:20 local, AFTER the results; D17-D19 rules applied as written)
CBraMod, encoder tap, eval-mode probe, 5 rotations, linear head (tables: artifacts/tables/
chbmit-S1E.md, siena-S3E.md, siena-S3FE.md). Mean ROC x100, CHB-MIT / Siena / Siena filtered:
- Frozen pretrained (lp): 81.8 / 80.8 / 89.4. Random features (lp_randinit): 77.2 / 74.1 / 80.2.
  Old (proj_out tap, train mode) lp was 67.4 / 51.0 / 51.6: the "pretrained at chance" result was
  the probe artifact.
- Last-layer SSL adaptation (the paper's method) adds nothing: last - lp = +0.1 / +0.6 / +0.2
  (no difference shown in all three). The old "+8.6 / +12.5, SA helps" came from adapting
  proj_out, the layer the old probe read.
- Early vs last: +1.1 / +1.9 (no difference shown) / -3.5 (last wins by the rule, small).
  first_block - last, embed_only - lp: no difference shown in all three. first - first_noise:
  "perturbation alone explains it" in all three.
- Pretrained vs random init (last_randinit - last): -2.9 (no difference shown) / -8.0 / -9.9
  (pretrained wins). D17: random-init SA = random features in all three.
Reading: with a correct probe, frozen pretrained CBraMod is a good seizure encoder and beats
random weights; SSL adaptation of any layer changes ROC by at most ~2 points (only `first` on
filtered Siena moves by -3.5).

## D24. Paper A strengthening runs (2026-10-31, BEFORE any of these runs; user: "cost is not a
issue ... any other experiments to run if so then run"; Paper B dropped)
All new runs: encoder tap, probe backbone in EVAL mode for BOTH models (--backbone-mode eval), so
BIOT and CBraMod are finally probed the same way. PROBE_CODE_VERSION 4.
- A. Corrected protocol, more seeds (run_tag S1M / S3M / S3FM; CHB-MIT, Siena, Siena filtered).
  Arms lp, lp_randinit, last, last_randinit, all; linear head. Seeds per rotation r:
  [S_r, 1000 + r, 2000 + r] with S_r = [42, 123, 2021, 3407, 8888][r]. CBraMod reuses its S_r
  run from S1E/S3E/S3FE (identical code path) and runs the 2 new seeds; BIOT runs all 3.
  Reading (scripts/read_d24.py): per rotation, mean over its 3 seeds; then the D18 paired rule
  (|mean| > 3 and same sign in >= 4/5 rotations) on: last - lp ("SA helps"), last_randinit - last
  ("pretrained vs random init"), lp - lp_randinit ("pretrained features beat random features",
  new, fixed now), and D17 (last_randinit vs lp_randinit). Also mean +/- SEM over all 15 runs.
- B. The paper's own setting with the fixed probe (run_tag P1E): paper split, upstream labels,
  parity protocol, arms lp, last, last_randinit, lp_randinit, seeds 42/123/2021/3407/8888, probes
  linear AND mlp_fullft. Reported as mean +/- SEM next to the paper's Table 1; "SA gain" =
  last - lp paired by seed; called a gain if mean > 3 and positive for >= 4/5 seeds.
- C. C2/C3 with the fixed probe (run_tags C2E-*, C3E-*): exactly D15's design and rules, arms last
  and last_randinit; LP baseline = new 5-seed lp at batch 128, eval mode (run_tag R3E-b128).
- D. Free: count published papers that use the BIOT/CBraMod CHB-MIT protocol (process2.py split,
  start/end label rule, oversampled test windows); bootstrap CIs over (rotation, seed) runs.
Not run: Paper B arms (first, first_block, embed_only, first_noise), TUH (no access).

### D24 outcome (2026-10-31 17:45 local, AFTER the results; rules applied as written)
44 jobs, $246.44. Eval-mode probe and encoder tap for BOTH models. Tables: artifacts/tables/
d24-chbmit-S1E+S1M.md, d24-siena-S3E+S3M.md, d24-siena-S3FE+S3FM.md, d24-chbmit-P1E.md.
A. Corrected protocol, 3 seeds per rotation (per-rotation seed means; ROC x100; CHB-MIT / Siena /
Siena filtered):
| contrast | BIOT | CBraMod |
|---|---|---|
| last - lp ("SA helps") | +1.9 none / +9.2 HELPS / +4.1 HELPS | -0.0 / +0.3 / +0.1, none in all |
| last_randinit - last | +0.2 none / +7.2 none / -4.7 pretrained wins | -4.4 / -7.6 / -10.7, pretrained wins in all |
| lp - lp_randinit (new) | -2.0 none / -16.1 RANDOM wins / +1.0 none | +5.5 / +7.0 / +9.4, pretrained wins in all |
| D17 | random features explain it (all) | random features explain it (all) |
Means: CBraMod lp 81.6 / 81.4 / 89.5 (SEM over rotations 2.3-3.3); BIOT lp 65.1 / 51.3 / 69.8.
B. The paper's own split and labels, fixed probe, 5 seeds (linear / MLP head):
- CBraMod lp 92.0 / 91.7 (paper LP 54.14), last 92.0 / 91.7 (paper SA 83.67); SA gain 0.0 / 0.0,
  "no difference shown". With a correct probe, frozen CBraMod on the paper's split is already
  above the paper's adapted number, and adaptation adds nothing.
- BIOT lp 55.0 / 56.1 (paper 46.93), last 54.4 / 54.9 (paper 83.08); SA gain -0.6 / -1.2, "no
  difference shown". Random init 90.2 / 88.5 (descriptive): the +35 random-init advantage exists
  on the 2-test-patient paper split but not under 5 rotations (+0.2, part A).
C. C2/C3 with the fixed probe (seed 42; LP baseline R3E-b128: BIOT 65.1, CBraMod 92.0):
- CBraMod last 92.21-92.23 at every N and P (within 0.3 of LP): C2 "not testable: adaptation adds
  nothing at any N"; C3 "uninformative".
- BIOT last 61.8-62.5 (range 0.6, 2.6-3.2 BELOW LP): C2 "not supported" (no peak; the
  not-testable condition fails only because two N points are 3.0-3.2 below LP); C3 "uninformative".
Reading: across both models, 3 settings and the paper's own split, last-layer SSL adaptation
gives a gain only for BIOT on Siena (+9.2, +4.1). For CBraMod it changes ROC by <= 0.5 everywhere.

## D25. Completeness programme for Paper A (2026-11-01, BEFORE any D25 run or analysis)
User: "have you completed all experiments required? be thorough ... you have my approval to run
the jobs" and "all graphs required ... training epoch vs validation ... log it all, re-run if
required". D25 ADOPTS the designs and reading rules of items E1-E34 in notes/completeness-audit.md
(written 2026-11-01 by the reviewer-style audit wf_310e0a5f-3cd, before any D25 run), as written
there, with these amendments fixed now:
- Paper dispersion (E3): Table 1 is mean ± SEM over 5 seeds (artifacts/paper/paper.txt l.156, 241).
- E12 primary metric: partial AUC up to 2 false alarms/h, D18 paired rule with margin 0.05.
- E22: no git commits (the user has not asked for commits); timestamps come from file mtimes,
  SageMaker CreationTime and S3 LastModified.
- E2: tests/test_upstream_audit.py is rewritten so it composes Hydra against the clone at test
  time and embeds no upstream text.
- Phase 5 "nice" items (E33a, E33b) are also run.
- E25 doubles as the logged re-run for the figures: every run records per-step SSL loss and per-
  epoch probe train loss, val loss + metrics and plot-only test metrics; validation scores saved.
  Its linear cells must reproduce S1M/S3M/S3FM within 0.5 ROC per run, else stop and investigate.
- All new our-pipeline runs: eval-mode probe, encoder tap, unless the item tests tap or mode.
Every result is read only with these rules; anything else is labelled descriptive/post hoc.
D25 parameters fixed (2026-11-01, BEFORE any D25 GPU run; our-pipeline items):
- Run tags: E17 P1PE (CBraMod proj_out tap, eval) and P1ET (encoder tap, train mode) on the paper
  split; S1PE / S1ET on rotations at seed S_r. E18 P1F, S1U. E19 BIOT q95: S1Q, S3Q, S3FQ, P1Q;
  CBraMod ssl_scale=100: S1C, S3C, S3FC (arms last, all). E25 S1L, S3L, S3FL (+ P1L, a logged
  re-run of P1E; both must reproduce their originals within 0.5 ROC per run). E26-filt S1FM.
  E27 S1N (BIOT), S3N, S3FN. E28 ssl_seed draws {11,12,13,14} on the paper split (P1D<k>) and
  {11,12} on rotations (S1D<k>, S3D<k>). E29 cells lr {3e-5, 3e-4, 1e-3} x budget {N=4,174 x 3
  epochs, whole pool x 3 epochs} minus the existing cell (S1LR<i>, S3LR<i>). E30a extra seeds
  123/2021/3407/8888 and data_seed {2,3} (C2X, C3X); E30b Siena fixed_c (S3C2/S3C3 + LP at batch
  128, both settings). E32 fold_seed 20261101 (S1R, S3R).
- Feasibility checked on the desktop: Siena P2/P5/P10 at N2048 have enough eligible subjects in
  every rotation (P2: 2-5 eligible; P10: 10-11).
- E26 (standardized probe on GPU) waits for E15's gate. E33a/E33b are pre-registered separately
  before they run.
D25 wave C reading choices (2026-11-01 10:30 local, BEFORE any released-code GPU run; only a 1-epoch
CPU smoke on ~320 windows has been seen, and it is not read). These fix what the audit leaves open.
They are coded in scripts/released/read_released.py, and the grid is configs/released_grid.yaml:
- Every rule is read at best_* and at last_* separately. Metrics are bal/PR/ROC x100. D13 units =
  paper SEM with a 1-point floor (the coverage.py d13).
- E4 "released = ours" uses ROC only. Pooled SEM = sqrt(SEM_rel^2 + SEM_ours^2). Ours = wave 1,
  mlp_fullft (full_ft True).
- E5 noise floor = |repeat - E4| at CBraMod step_up default, seed 42 (cell e5noise-c). It widens
  every unit threshold by delta/max(SEM, 1). The screen uses seeds 42/123. A configuration screens
  in if it passes at either epoch rule; "reaches" needs >= 5 seeds. The E4 default cells' seeds
  42/123 count as the screen of the default configuration.
- E6 fingerprint uses the 5-seed mean ROC of main_layer last1/last2/all (foundation unset). E6
  agreement compares all 6 numbers per seed within the noise floor.
- E7: tap and mode effects use ROC at seeds 42/123. The (proj_out tap, train mode) cell is E4 lp
  (full_ft True) / E5-LP ft0-b256 (full_ft False).
- E31 SA(0) = E4 sa (unset), E5-SA fd1-ft1-b256-sR (set), E6 all (main_layer), seeds 42/123. The
  E31 bracket check is not coded (it needs lp_randinit, which wave 1 lacks). E30c is tabulated only.

### D25-E15 outcome (2026-11-01 09:30 local, AFTER the results; rule applied as written)
artifacts/analysis/E15/biot_probe.md. Desktop CPU, eval-mode BIOT encoder features, all windows,
seed S_r per rotation. Fidelity: our cached parity head reproduces the 50 D24 records within 0.02
ROC (test keys identical); CPU re-adaptation of Siena `last` matches the GPU losses within 1e-4.
Reading choices fixed in the script docstring before any probe was fit (09:16 UTC first fit;
script 08:16 UTC): rule 1 delta = c[probe] - c[parity raw] with c = lp - lp_randinit, |delta| > 3
counted (literal), same-sign count reported next to it; rule 2 read with the pipeline's own head
(parity raw), z / LR descriptive.
- Feature std (/100 input): pretrained 1.18 / 1.20 / 0.41 (CHB-MIT / Siena / Siena filtered),
  random init 4.1-4.4 / 8.2-8.8 / 4.4-4.7, i.e. random features are 4-11x larger.
- Rule 1: rotations with |delta| > 3, z-scored head / LR: CHB-MIT 5/5 / 3/5, Siena 4/5 / 3/5,
  Siena filtered 4/5 / 4/5 -> "BIOT conclusions are probe-limited" on all three; E26 TRIGGERED.
  Same-sign reading: fires only on Siena (z, 4/5, all upward). Mean lp - lp_randinit raw / z / LR:
  +3.2 / +1.1 / +4.0, -16.8 / +0.6 / -3.3, +0.4 / -0.4 / -3.7.
- Rule 2: lp(q95) - lp(/100) > +3 (parity raw): 0/5, 1/5, 0/5 -> "input scale matters" does NOT
  fire (z and LR: at most 3/5). q95 lowers lp (mean raw -16.7 / -6.8 / -16.6). E19 runs anyway.
- Descriptive: Siena last - lp raw +6.9 (= record) vs z +0.8 vs LR -2.2; Siena filtered +3.6 /
  +0.4 / -0.9, so the D24-A BIOT "SA helps" on Siena may be a raw-head artifact (E26 tests it with
  D24 rules). Paper split lp 55.0 / 79.1 / 84.0 vs lp_randinit 90.1 / 88.4 / 89.1.
- Caveats: 48 of 90 LR fits chose C at a grid edge (1e-4 or 10; grid fixed before data, not
  widened); the raw head's best epoch is its last in 58/90 fits (under-trained at 10 epochs).
D25 additions (2026-11-01 ~10:45 local, BEFORE these runs):
- E26 (triggered by E15: "BIOT conclusions are probe-limited" fired on all 3 datasets): new probe
  variant `linear_z` (linear head on features standardized with TRAIN-split mean/std, backbone
  in eval mode for the statistics). Runs, eval mode, both models: rotations at seed S_r on
  CHB-MIT, Siena, Siena filtered (arms lp, lp_randinit, last, last_randinit; run tags S1Z, S3Z,
  S3FZ) and the paper split, 5 seeds (P1Z). Reading: the D24 paired rule on last - lp,
  last_randinit - last, lp - lp_randinit at 1 seed per rotation (descriptive, like S1), D17;
  paper split by the D24-B rule for last - lp.
- E33b: Siena published-style split "pub": test PN13, PN14, PN16, PN17 (CSBrain), val PN10, PN12,
  rest train; arms lp, last, lp_randinit; 3 seeds (42, 1000, 2000); both settings; both models;
  eval mode; run tags S3P / S3FP. Descriptive (one split).
- E33a: an extended CHB-MIT eval store with chb12, chb13, chb17 and chb02_16+ added (label-based
  channel selection; n_present reported), 23-subject rotations (seed 20261014), D24-A arms,
  3 seeds, linear, eval mode, run tag S1X; D24 rules. Built on the desktop before running.
D25-E25 check (2026-11-01 11:20 local, rule fixed in D25): the logged re-runs S1L/S3L/P1L/S3FL reproduce
S1E+S1M / S3E+S3M / P1E / S3FE+S3FM exactly: 484 of 484 linear-head pairs with |diff| < 1e-6 ROC
(rule: within 0.5). The pipeline is bit-reproducible on SageMaker; the history logging changed no
number.

### D25 outcomes, wave B part 1 (2026-11-01 ~12:30 local, AFTER the results; each verdict
re-checked by an independent agent: all CONFIRMED; details artifacts/analysis/<item>/)
- E17 (CBraMod tap x mode): no single factor explains the artifact (linear head): lp tap effect
  +15.2, mode effect +11.4, both > 3, strong interaction. An SA gain appears ONLY with both
  artifacts (proj_out tap + train mode, wave 1: +8.7, 5/5 seeds); either fix alone removes it
  (+2.1, +0.4; both fixed 0.0). MLP head: the tap explains lp; no SA gain in any cell.
- E18 (labels, split): the label fix on the paper split removes no win (BIOT random-init
  advantage +35.8 -> +30.9, still a win); the split fix (rotations) removes BIOT's random-init
  advantage. E13(d) waterfall finished (artifacts/analysis/E18/).
- E19 (input scaling): Rule 1 FIRES: BIOT with its native q95 input changes 6 of 12 D24-A verdict
  strings (e.g. CHB-MIT last_randinit - last +0.2 -> +18.5 "first wins"; Siena last - lp +9.2
  "first wins" -> +2.1 "none"). Rule 2 does not fire (q95 LOWERS BIOT lp). Rule 3 does not fire
  (CBraMod SSL scale /100 vs /700: no difference on all 3 datasets).
- E25 (MLP head, logged re-runs): same verdict as the linear head in 25 of 26 rule outputs (the
  one change: BIOT Siena-filtered last_randinit - last, pretrained wins -> no difference).
- E27 (last_noise): "perturbation alone explains it" in all 5 cells, incl. BIOT Siena where
  last - lp was a win: the SSL "gain" does not need EEG data.
- E28 (other SSL draws): "D4 NOT robust" by the rule: CHB-MIT last_randinit - last changes under
  new draws (BIOT both draws, CBraMod one); every last - lp verdict and D17 holds; BIOT
  last_randinit on the paper split identical across draws.
- E29 (SSL dose): "more SSL helps" only for BIOT on Siena (all 5 cells), which the base cell
  already showed; nothing on CHB-MIT or for CBraMod. 20 cells tested (exploratory).
- E33b (Siena pub split): all contrasts inside the D24 5-rotation range; same direction for 3 of
  4 contrast groups (exception BIOT lp - lp_randinit on Siena filtered).
Reading: the CBraMod "SA gain" needs both released-code probe artifacts at once; BIOT's only SA
gain (Siena) is matched by a noise-input control and disappears with BIOT's native input
normalisation. No configuration shows an EEG-specific SSL adaptation gain.

### D25 outcomes, wave B part 2 (2026-11-01 ~20:30 local, AFTER the results; each verdict
re-checked by an independent agent that recomputed it from the raw records)
- E30a/b (C2/C3 re-tested; artifacts/analysis/E30/, scripts/analysis/e30_c2c3.py; re-check
  CONFIRMED, no mismatching number). Reading choices the rule leaves open were fixed by the reader
  in the script docstring after reading raw records but BEFORE any E30 aggregate (5-seed mean as
  the primary curve; rotation mean of 3-seed means; |v - LP| <= 3 at every N; C3 "> 3 above LP"
  at every P); the re-check found none contrary to the D15 text.
  - CHB-MIT, BIOT pretrained last, 5 seeds (LP R3E-b128 65.09): C2 "not testable" (best N4174,
    range 0.17, v - LP -0.67 to -0.50); C3 "uninformative" (range 1.06). D24's C2 "not supported"
    becomes "not testable": seed 42 is the lowest seed (curve ~62.2 vs 63.0-66.6), not a change in
    shape; at seed 42 the string also depends on the data draw (data_seed 1 and 3 "not supported",
    2 "not testable"). C2 is supported in no reading (best N - N4174 <= +0.2).
  - Siena (LP batch 128 57.70): C2 "not supported" (range 0.13, curve +12.6 above LP); C3
    "supported as written" (range 0.76). Siena filtered (LP 74.43): C2 "not supported"; C3
    "supported as written" (range 0.17, +4.4 to +4.6 above LP). Caveat: C2 is flat within 0.13, so
    "patients do not matter" may mean "the data does not matter" (E27: a noise input matches BIOT
    Siena last). Siena filtered C3 holds in only 3 of 5 rotations (descriptive; not part of the rule).
  - CBraMod control: C2 "not supported or not testable", C3 "flat, supported vs uninformative
    undetermined": no CBraMod LP at probe batch 128 was run on Siena (design gap; not re-run).
- E26 (standardized linear head `linear_z`; artifacts/analysis/E26/, recheck.md; re-check
  CONFIRMED to 0.1 ROC). 1 seed S_r per rotation (descriptive, like S1) + P1Z (D24-B):
  - BIOT Siena last - lp: +9.2 "SA helps" (D24-A raw head, 3 seeds) -> +0.8 "no difference
    shown"; Siena filtered +4.1 -> +0.4. Not a seed-count effect: the raw head at the same seed
    S_r still reads "SA helps" (+6.9, +3.6), and the SSL losses are identical in 20/20 cells, so
    only the head differs. The BIOT Siena "SA gain" is a raw-head artifact (fits E15, E19, E27).
  - Every last - lp is "no difference shown" for both models on all 3 datasets; P1Z BIOT +0.2,
    CBraMod +0.2, "no difference shown". D17 "random features explain it" everywhere (unchanged).
  - Verdict changes vs D24-A (3 seeds): BIOT 4 of 9, CBraMod 2 of 9. Seed-matched (raw head at S_r
    vs linear_z): BIOT 6 of 9 (adds CHB-MIT last_randinit - last -5.9 "pretrained wins" and
    lp - lp_randinit +3.2 -> none), CBraMod 1 of 9. CBraMod Siena and Siena filtered keep
    "pretrained wins" / "pretrained features win".
  - Anomaly: BIOT CHB-MIT rot0 linear_z test ROC 49.9 / 50.0 (lp / last) with val 0.89; scores not
    constant (AP 0.083 vs prevalence 0.0066), consistent with subject heterogeneity; per-subject
    check needs the npz (desktop).
  - Provenance gap: records do not store the data variant (filtered runs are identified by
    run_tag and eval_hash only).
- E26-filt (S1FM, filtered CHB-MIT, 3 seeds, both heads; artifacts/analysis/E26F/; re-check
  CONFIRMED): all 16 rule outputs equal unfiltered CHB-MIT (D24-A linear, E25 MLP). CBraMod
  "pretrained wins" / "pretrained features win"; BIOT all "no difference shown"; last - lp
  "no difference shown" for both. Filtering changes no conclusion.
- E32 (second subject partition, fold_seed 20261101; artifacts/analysis/E32/, recheck.md;
  re-check CONFIRMED). 13 of 16 verdicts "replicated" (same string, CIs overlap). Siena (both
  models) and CBraMod CHB-MIT replicate in full. The 3 failures are all BIOT CHB-MIT, each on the
  verdict string (CIs overlap): last - lp +1.9 none -> +3.6 "first term wins" (5/5 positive, but
  rot3 +12.1 carries it; without rot3 +1.5, post hoc); last_randinit - last +0.2 none -> +7.8
  "first term wins"; lp - lp_randinit -2.0 none -> -11.6 "second term wins" (these two survive
  dropping any rotation). Under the stricter reading "original mean inside the new CI": 11 of 16
  (adds Siena CBraMod lp - lp_randinit and D17). Descriptive: on this partition BIOT's raw linear
  head is under-trained on pretrained features (best epoch = last in 30/30 pretrained runs; rot3
  lp 41-47, below chance), the pattern E15/E26 found; E32 has no standardized-head run, so it
  cannot say whether these 3 changes are raw-head effects. Test: D26.
- E33a (S1X, 23 subjects, 683 EDFs = 605 + 78; artifacts/analysis/E33A/; re-check CONFIRMED):
  8 of 8 verdict strings equal D24-A CHB-MIT (descriptive comparison; no rule was registered).
  The store also added chb24_02 and chb24_22 (same label rule; logged before the runs, but not
  in the pre-registered wording).

## D26. Standardized head on the second partition (2026-11-01 ~20:50 local, AFTER seeing E32; post hoc, BEFORE any D26 run)
Why: E32's 3 non-replications are all BIOT CHB-MIT, and E32's raw linear head is under-trained on
pretrained BIOT features (the E15/E26 pattern). E26 removed a raw-head "SA helps" on Siena; D26
asks the same question on the E32 partition. Cost is not a constraint (user), approval covers the
completeness runs (user: "you have my approval to run the jobs").
- Runs: E32 design exactly (fold_seed 20261101, arms lp, last, last_randinit, lp_randinit, seeds
  [S_r, 1000+r, 2000+r], overlap labels, eval mode, encoder tap) with `--probes linear_z`; CHB-MIT
  and Siena; both models; run tags S1RZ, S3RZ. 20 jobs. No new code path (linear_z ran in E26,
  fold_seed in E32), so no smoke.
- Rule: D24 rules (3-seed means per rotation, D18 paired rule, D17) on the 3 contrasts. For each
  of the 3 E32 BIOT CHB-MIT non-replications: "raw-head effect" if the linear_z verdict is "no
  difference shown"; "partition effect" if the linear_z verdict equals the E32 raw-head verdict;
  anything else is reported as it is. Other cells are descriptive (compare with E26 at S_r and
  with E32).

### D25 wave C outcome, part 1 (2026-11-01 ~21:00 local, AFTER the results; reader
scripts/released/read_released.py, artifacts/analysis/waveC/released.md; re-check CONFIRMED all 7
claims and reproduced released.md byte for byte; recheck.md). Every rule at best_* and last_*.
Pending: E6 fingerprint at last, E31-layer and the E5 "reaches" verdicts that need the follow-up
seeds (5 OOM cells re-running on ml.g6e.2xlarge; E5 follow-up running).
- Checks: torch 2.4.1+cu121 in all 92 cells; E7 patch numstat as designed; 0 "non-finite SPT
  loss" lines; the released code is NOT bit-reproducible at a fixed seed (E5 noise floor at seed
  42: best 3.19 / 0.26 / 0.71, last 2.63 / 1.02 / 0.29 bal/PR/ROC).
- E4: "released = ours" True in all 8 cells (ROC; the tightest, BIOT SA at best, passes 2.00 vs
  3.80 only because seed 123 picked epoch 1). "Random features explain released SA" True for both
  models at both rules (|SA - LPrand| ROC: BIOT 2.05 / 0.12, CBraMod 0.52 / 1.40).
- E5: 19 non-default configurations screen in, 9 out (all 8 BIOT SA with foundation_dir set, at
  ROC 49-60, and e5lp-c-ft1-b128). "BIOT SA at best REACHES" via the E4 default: bal +5.43 units
  passes only because the noise floor widens the threshold to 6.19. Others pending the follow-up.
- E6: "entry points agree" False (seeds 123 and 8888 at best only; all 5 seeds agree within 0.2 at
  last). Fingerprint at best already False (last1 86.08 vs 88.67); at last pending e6-b-all.
- E7: "54.14 reachable in released code" False at best and at last; the closest is proj_out tap,
  train mode, full_ft False at ROC 64.36 (+7.2 to +7.4 units). Tap/mode: "mode explains" only at
  full_ft True / last (driven by a collapse in tenc-mtrain-ft1 at last); elsewhere neither alone.
- E30c: released random-init curves flat on ROC for both models, N and P, both rules (ranges
  0.08-1.92); the pretrained (foundation_dir set) curves are also flat (<= 2.91), so flatness is
  not specific to random init. Not flat on bal-acc at best (the trainers select on bal-acc; val
  bal-acc ties at 0.5 often keep epoch 1). C2 supported in no curve (descriptive; LP chosen after
  seeing the data).
- E31: "lambda matters" fires in 8 of 24 readings: BIOT foundation_dir unset at best (an artifact
  of the lambda-0 baseline's seed 123 picking epoch 1; at last all within 0.66) and CBraMod
  foundation_dir set (real, not monotone: lambda 1e-2 worst, ROC 52.6 best / 42.6 last).
- Reader fix (2026-11-01 21:00, after the re-check, BEFORE any follow-up seed result): a
  configuration that fails the E5 screen at both epoch rules gets no follow-up seeds, so it now
  counts as "does not reach" (False), not "pending". The output changes only in those 9 rows.
- Correction (2026-11-01 ~22:30 local) to "D25 wave C outcome, part 1", E4 bullet: "the tightest, BIOT
  SA at best, passes 2.00 vs 3.80 only because seed 123 picked epoch 1" is imprecise. The smallest
  margin is CBraMod LP at last (1.39 vs 2.00). For BIOT SA at best, seed 123's epoch-1 pick both
  creates most of the 2.00 gap and widens the threshold. No verdict changes. Also: released BIOT SA
  at best is 86.48 +- 1.89 (5 seeds, recomputed from the CSVs); its SEM equals the paper's 83.08 +-
  1.89 by coincidence, not by a copy error.

## D27. Controls asked for by the internal review r1 (2026-11-01 ~23:30 local; post hoc: designed AFTER all D24-D26 data were seen and after the review notes/review-r1.md; BEFORE any D27 run)
Why: the review found BIOT SA cells that pass a rule but have no noise control (M3b), a primary
BIOT head that is under-trained (M9), no fine-tuning reference or pretrained-BIOT sanity check
(M10, M13), a CBraMod C3 reading that cannot be completed (no CBraMod LP at probe batch 128 on
Siena), and equivalence claimed from |mean| <= 3 (M11). Cost is not a constraint (user); approval
covers the completeness runs. All runs: eval mode, encoder tap, overlap labels on rotations,
upstream labels on the paper split.
- A. Noise controls (arm last_noise) on every rule-passing BIOT SA cell without one:
  A1 P1QN: paper split, input_norm q95, arms lp,last,last_noise, 5 seeds, probes
     linear,mlp_fullft,linear_z (lp/last must reproduce P1Q exactly, bit-reproducibility check).
  A2 S3FQN: Siena filtered, q95, arms lp,last,last_noise, 5 rotations x 3 seeds, probes
     linear,linear_z (lp/last reproduce S3FQ exactly).
  A3 S1RN, S3RN: E32 partition (fold_seed 20261101), CHB-MIT and Siena, arm last_noise, 3 seeds,
     probes linear,linear_z (pairs: S1R/S3R linear, S1RZ/S3RZ linear_z).
  A4 S1LRN<i>, i in {1,3,4,5}: the E29 CHB-MIT BIOT cells that read "first term wins", arms
     last,last_noise at the cell's ssl_lr/ssl_n, seed S_r, probes linear,linear_z (last linear
     reproduces E29 exactly; lp linear_z = S1Z at S_r).
  Rule: D19 three-way on last - last_noise ("the gain needs EEG data" if it wins by the paired
  rule; "perturbation alone explains it" if |mean| <= 3; else "unclear"), rotations as units
  (seeds on the paper split, D24-B sign count); A4 descriptive (1 seed). Each head separately.
  Also TOST (margin 3, alpha 0.05) on last - last_noise, here and for E27: "equivalent" only if
  TOST rejects.
- B. Standardized head, 3 seeds (co-primary with the raw head): add seeds 1000+r and 2000+r to
  S1Z, S3Z, S3FZ (arms lp, lp_randinit, last, last_randinit; both models; probe linear_z; same
  run tags). Rule: D24 rules on 3-seed means (3 contrasts + D17). The paper reports raw and
  standardized heads side by side; a conclusion holds only if both heads agree, else it is
  reported as head-dependent.
- C. CBraMod LP at probe batch 128 on Siena and Siena filtered (S3CLPB, S3FCLPB), arm lp, 3 seeds.
  Rule: the E30 C2/C3 rules for the CBraMod control curve (seed S_r) against LP at seed S_r.
- D. Supervised fine-tuning reference: new probe variant `ft` (linear head + encoder trained on
  the labels; encoder lr 0.1 x head lr = 4e-5; AdamW wd 0.05; cosine to 1e-5; 10 epochs; batch
  256; val-ROC selection; eval-mode scoring; the caller's encoder restored afterwards). Arms lp
  (pretrained init) and lp_randinit (random init), probe ft; CHB-MIT paper split 5 seeds (P1FT),
  CHB-MIT rotations 3 seeds (S1FT), Siena rotations 3 seeds (S3FT); both models. Smoke first.
  Rule: descriptive reference for LP and SA; one pre-stated contrast: "pretraining helps
  fine-tuning" if ft(lp) - ft(lp_randinit) wins (D18 rule on rotations; D24-B on the paper split).
  BIOT's published CHB-MIT fine-tuning numbers are compared descriptively (different recipe).
- E. CPU, descriptive: leave-one-rotation-out for every primary verdict (D24-A raw, B, E32, D26),
  as a table; step-0 SSL loss pretrained vs random from the records.
- D27-E detail (2026-11-02, BEFORE any leave-one-rotation-out output exists): with one rotation
  dropped, the paired rule is read as |mean| > 3 and the same sign in at least 3 of 4 rotations
  (the 4-of-5 condition scaled down). TOST on last - last_noise: margin 3, alpha 0.05, t-test over
  rotation means (df 4; seeds on the paper split).
### D27-E outcome, part 1: CPU on existing records (2026-11-02, AFTER the results; script
scripts/analysis/d27_cpu.py, artifacts/analysis/D27/cpu.md; self-checks re-derive the published
D24-A, E26, E32, E10 and E27 strings; NOT yet re-checked by an independent agent; re-run when the
D27 GPU records arrive)
- Leave-one-rotation-out (descriptive): 15 of 64 verdicts change when one rotation is dropped
  (D24-A 6/24, E32 2/16, E26 1-seed 7/24); 12 of the 15 are BIOT. Robust to every drop: D24-A
  Siena BIOT "SA helps" (+9.2), every D17 verdict, every D24-A and E32 CBraMod verdict. Fragile:
  D24-A Siena filtered BIOT "SA helps" (+4.1 -> none without rot1, +2.9) and E32 CHB-MIT BIOT
  "SA helps" (+3.6 -> none without rot3, +1.5). Note: E10 (stats_d25.py) had already printed
  leave-one-out strings for the 24 D24-A verdicts with the same 3-of-4 rule.
- TOST (margin 3) on last - last_noise, E27: equivalence shown for CBraMod (Siena p 4.7e-9,
  Siena filtered p < 1e-4); NOT shown for BIOT (CHB-MIT p 0.106, Siena 0.186, Siena filtered
  0.069; 90% intervals reach +4.0, +4.6, +3.3). So for BIOT the D19 reading "perturbation alone
  explains it" means "no difference shown", not "equivalent". The paper must say so.
- Step-0 SSL loss: BIOT pretrained ~1.0 (cosine loss) = random init ~1.0; CBraMod pretrained
  0.029 vs random 64.6. Cause checked directly (2026-11-02): the BIOT checkpoint is an encoder
  state_dict (57 tensors; all load exactly into model.biot, none missing or extra); it has no
  SSL `prediction` head, so that head starts random in both arms (configs/models.yaml already
  says so). The released code does the same. Not a loading bug; a property of BIOT SA worth
  stating in the paper (the SSL head is learned from scratch in 51 steps).
- Timestamp correction (2026-11-01 23:00 local, from SageMaker CreationTime): the clock times I
  wrote in the headers of D26 ("~20:50 local") and D27 ("~23:30 local") and in the D27-E detail
  ("2026-11-02") were estimates and are wrong. Real anchors: E5 follow-up jobs created from
  19:30 local; D26 jobs from 19:40 local; D27 smokes 20:54 local; D27 jobs 21:10-21:31 local (all
  2026-11-01). D26 was written before 19:40 and D27 before 20:54, i.e. still BEFORE their runs;
  the BEFORE/AFTER labels stand. The D27-E detail was written after the D27 submission and before
  any CPU output. Use these anchors in the paper's timeline (UTC = local + 8 h).

### D27 addition (2026-11-02 00:45 local; post hoc, after the framing review found BIOT Siena SA gains without a noise control; BEFORE any of these runs)
D27-A covered every rule-passing BIOT SA cell on CHB-MIT and the q95/E32 cells. Still uncovered, all
BIOT on Siena with the raw head: E25 MLP head (+11.9), E28 other SSL draws (+6.8), E29 dose cells
(+18.8 to +21.5). Same rule as D27-A (D19 three-way on last - last_noise; TOST margin 3).
- A5 S3LRN<i>, i = 1..5: the E29 Siena cells, arms last,last_noise at the cell's ssl_lr/ssl_n, seed
  S_r, probes linear,linear_z (last linear reproduces E29 exactly). Descriptive (1 seed), like E29.
- A6 S3NM, S3FNM: Siena and Siena filtered, arm last_noise, seeds S_r/1000+r/2000+r, probes
  mlp_fullft,linear_z (pairs: S3L/S3FL mlp_fullft; S3Z/S3FZ linear_z after D27-B).
- A7 S3DN11, S3DN12: Siena, arm last_noise with ssl_seed 11 / 12, seed S_r, probe linear (pairs: the
  E28 S3D11/S3D12 last and the S3 lp at S_r).

### D26 / D27 / wave C part 2 outcomes (2026-11-02 05:24 local, AFTER the results; rules applied as written; each group re-checked by an independent re-computation from the raw records: all verdicts CONFIRMED; corrections from the re-checks folded in below)
- D26 (artifacts/analysis/D26/): all 3 E32 BIOT CHB-MIT non-replications are "raw-head effect" (standardized
  head: last - lp +0.7, last_randinit - last +2.6, lp - lp_randinit -3.4, all "no difference shown"; the
  last fails only on the sign count, 3 of 5). The standardized head also removes the E32 Siena BIOT
  last - lp win (+9.0 -> +1.7): 7 of 16 E32 strings change (re-check count; the reader said 3 wins).
- D27-B (artifacts/analysis/D27B/; standardized head, 3 seeds, co-primary): 23 of 26 rule outputs hold
  with both heads; 3 are head-dependent, all BIOT Siena: Siena last - lp (raw +9.2 F vs standardized +1.7
  N), Siena filtered last - lp (+4.1 F vs +1.9 N), Siena filtered last_randinit - last (-4.7 S vs -2.2 N).
  Every standardized-head last - lp reads "no difference shown". P1Z holds (BIOT +0.2, CBraMod +0.2).
  Fragile "holds" (re-check): BIOT Siena lp - lp_randinit (-4.2) needs one near-chance run (rot2 seed 1002).
- D27-A and addition (artifacts/analysis/D27/noise.md, cpu.md; TOST margin 3): registered rows (A1-A3, A6,
  A7 under the literal text; the reader had A7 as descriptive): 2 read "the gain needs EEG data", both A1
  (BIOT, q95 input, DL's split): raw linear last - last_noise +8.58 [+6.5, +10.6], MLP +9.06, 5/5 seeds.
  BUT with the raw heads all three arms score BELOW CHANCE (linear: lp 33.1, last 41.9, noise 33.3; MLP
  32.5 / 41.1 / 32.1), the raw heads pick their final epoch 30/30 (under-trained), and the standardized
  head gives +0.46, equivalent by TOST (p 0.0005), with all arms ~70. "Head-dependent" for A1 is our
  reading (it borrows the D27-B both-heads rule; D27-A says "each head separately"): descriptive.
  All other registered rows read "perturbation alone explains it" (18); 7 pass TOST (all standardized
  head); raw/MLP-head rows do not reach equivalence (e.g. A6 Siena MLP +1.98, p 0.159; A3 Siena linear
  +1.62, p 0.055). The E25 MLP (+11.9), E28 draws (+6.8) and E29 Siena (+9.9 to +21.5) gains therefore
  show no difference from noise input (not equivalence). Descriptive 1-seed: A4 cell 3 linear (+3.98)
  and cell 5 linear_z (+3.95) read "gain needs EEG data", each carried by rot4 (+15.4 to +19.7; without
  rot4 cell 3 is +0.05); A5 cell 1 "unclear". Bit-reproducibility: P1QN = P1Q (20/20), S3FQN = S3FQ
  (30/30), S1LRN/S3LRN last = E29 (45/45). A4 reruns: the last arm came from the original g5.8xlarge
  jobs, last_noise from the g5.16xlarge reruns (same A10G GPU).
- D27-E: LORO 18 of 80 verdicts change when one rotation is dropped, all BIOT; no D17 or CBraMod verdict;
  no standardized-head last - lp verdict changes.
- D27-C (artifacts/analysis/D27CD/): CBraMod control curve vs CBraMod LP at batch 128 (seed S_r): Siena
  C2 "not testable", C3 "uninformative" (curve +2.0 above LP); Siena filtered the same (+0.1).
- D27-D fine-tuning reference (probe ft; pretraining helps if ft(lp) - ft(lp_randinit) wins):
  CBraMod: helps on CHB-MIT rotations (+7.2) and Siena (+11.8, 5/5), no difference on DL's split (-0.8).
  BIOT: helps on CHB-MIT rotations (+3.2; fragile: survives 2 of 5 rotation drops and 2 of 3 seeds),
  random init better on DL's split (-3.1, descriptive string), none on Siena (+0.3). ft(lp) vs frozen:
  BIOT +32.5 (DL split), +17.7 (rotations); CBraMod frozen LP 92.0 beats its ft 85.0 on DL's split (our
  10-epoch recipe). Published (descriptive, different recipes): BIOT PREST+SHHS fine-tuned AUROC 0.8752
  (arXiv 2305.10351v1 Table 2) vs our BIOT ft(lp) 0.8753; CBraMod 0.8892 (arXiv 2412.07236v6 Table 8) vs
  ours 0.8498. So the pretrained BIOT checkpoint gives BIOT's own fine-tuning number in our pipeline.
- Wave C part 2 (artifacts/analysis/waveC/part2.md; reader fix after seeing the follow-up: numpy booleans
  failed the "is False" test, no rule change): E5 reaches: BIOT LP no (both rules; closest ROC +5.2 units);
  BIOT SA yes at best (E4 default, only via the noise-widened bal threshold), no at last; CBraMod LP no
  (closest 64.35, +7.35 units); CBraMod SA yes at both rules, only by non-default configurations (e.g.
  foundation_dir unset, full_ft False, batch 128: 85.28, inside 3 units even without widening). E6
  fingerprint True at last (88.59 / 88.39 / 87.91 vs 88.67 / 88.44 / 88.60), False at best (last1 86.08,
  2.59 off; would read True if the 2-ROC tolerance were widened by the 0.71 noise floor: reading choice).
  E31-layer "lambda matters" False in all 6 readings (8 of 30 across E31). The 5 rerun cells ran on L40S
  (identified from RUNLOG; the failed attempt's run.log was overwritten).
- Consequence for the paper: "no remaining gain is shown to need EEG data" is FALSE as written for the raw
  heads (A1). Every registered BIOT gain disappears with the standardized head; the one gain that exceeds
  its noise control does so between below-chance arms. The headline (title) is unaffected (it is at the
  released input scaling). Abstract/intro/discussion wording: user decision pending.
- Paper wording decided by the user (2026-11-02 09:21 local): "Smaller BIOT gains remain with
  unstandardized probe heads, and none survives a standardized head; the one that exceeds a noise-input
  control (BIOT's native input scaling, DL's split) lies between below-chance scores (ROC 33 vs 42). We do
  not claim that SSL adaptation never helps." (replaces "none is shown to need EEG data").
- Correction (2026-11-02 10:25 local, found by the fill editor and confirmed in artifacts/analysis/D27/noise.md):
  "7 pass TOST (all standardized head)" in the D27 outcome is wrong: the 7 equivalent rows are CBraMod's two
  E27 cells (raw linear head) and five BIOT standardized-head rows. Also: the user wording "none survives a
  standardized head" holds for every standardized-head gain a rule reads; the one-seed E29 Siena dose cells
  (descriptive, no rule) have standardized last - lp of -0.9 to +4.3 (cells 1 and 4: +3.89, +4.29, 4 of 5
  positive), and their standardized noise controls read "perturbation alone explains it" (+1.90, +1.95).
- User decisions (2026-11-02 11:02 local): the abstract says "none survives a standardized head in our
  pre-set tests" (the one-seed E29 doses, read by no rule, give up to +4.3 with the standardized head); the
  main text is cut to at most 12 pages (TMLR 2-week review), moving detail to the appendices.
- Author contact and authorship (user, 2026-11-02 13:22 local): the user sent the author email on
  2026-10-28 16:23 (assumed: the 2026-10-27 version in notes/author-email-draft.md, i.e. questions 1-6 of the
  paper's Appendix I); no reply as of 2026-11-02. The paper is single-author: Joseph Sankoorikal Johny.

## D28. Probe convergence: equally tuned, early-stopped linear probes on cached frozen features (2026-11-04; post hoc: designed after all earlier data and after an external review; BEFORE any D28 run; frozen in the local git repository before the runs)
Why: every conclusion so far uses one fixed probe recipe (10 epochs, lr 4e-4, weight decay 0.05, cosine);
the raw BIOT head picks its last epoch in most fits (under-trained), and standardizing the features changes
optimisation and regularisation, not only scale. D28 asks whether the adaptation conclusions survive
adequately trained probes that get the same tuning budget in every arm.
- Probe: one linear layer on the encoder output (encoder tap, backbone in eval mode), trained on features
  computed once per (arm, seed) after the unchanged adaptation step (same seeds; the pipeline is
  bit-reproducible). Two feature variants: raw ("grid") and train-split standardized ("grid_z").
- Same search for every arm and variant: AdamW, lr {1e-4, 3e-4, 1e-3, 3e-3} x weight decay {0, 1e-4,
  1e-2, 1e-1} (16 configurations), batch 256, constant lr, BCE on logits, at most 200 epochs, early stop
  when validation ROC-AUC has not improved by more than 1e-4 for 20 epochs. Selected epoch = best
  validation ROC-AUC; selected configuration = best validation ROC-AUC over the 16 (ties: smaller lr,
  then smaller weight decay). Test metrics are read only at the selected configuration and epoch.
  A fit "converged" if early stopping fired before epoch 200 (fraction reported).
- Settings and arms: (a) DL's split, upstream labels, 5 seeds {42, 123, 2021, 3407, 8888}: lp, last,
  last_randinit, lp_randinit, both models; plus BIOT with q95 input: lp, last, last_noise. (b) Rotations
  rot0-4, overlap labels, seeds [S_r, 1000+r, 2000+r], CHB-MIT, Siena, Siena filtered: lp, last,
  last_randinit, lp_randinit, last_noise, both models.
- Reading (effect sizes primary): for each contrast (last - lp; last_randinit - last; lp - lp_randinit;
  last - last_noise) and variant: the mean paired difference with a 95% t-interval over the 5 rotation
  means (df 4; uncertainty across held-out patients) and the Nadeau-Bengio corrected interval; on DL's
  split the 5 seeds (seed uncertainty on one fixed split, labelled as such). Labels: "gain demonstrated"
  if the 95% t-interval excludes 0 and |mean| > 3 in that direction; "equivalent within +-3" if TOST
  (margin 3, alpha 0.05) rejects; else "not resolved". The D18 paired rule is reported as a descriptive
  consistency criterion. Primary questions: (Q1) does any SA gain (last - lp) read "gain demonstrated"
  with tuned probes? (Q2) does the BIOT q95 case (last - last_noise on DL's split) read "gain
  demonstrated" with either variant? (Q3) do the pretrained-vs-random contrasts keep their direction?
- Learning curves: per-epoch validation ROC-AUC and train loss for all 16 configurations are recorded;
  figure: the selected configuration's validation curve per arm and setting.

## D29. C2/C3 controls at the fixed-compute budget, and PR-AUC readings (2026-11-04; post hoc, same review; BEFORE any D29 run; frozen in git)
- Runs (BIOT, Siena and Siena filtered, fixed-compute protocol: 132 steps, batch 128, constant lr 3e-5,
  lowest-loss pass restored; 5 rotations x 3 seeds): (a) last_noise on the same subsets as E30b (N896,
  N1664, N2048, N4174; P2, P5, P10 at N2048); (b) the E30b last curve and the batch-128 LP re-run with
  probes linear and linear_z (the linear values must reproduce E30b exactly).
- Rules: the E30 C2/C3 rules, applied to each head separately. Noise control: "the plateau needs EEG
  data" only if at every N (every P) the 95% t-interval of last - last_noise over rotation means
  excludes 0 with mean > 3; otherwise "no difference demonstrated"; TOST (margin 3) reported.
- PR-AUC (CPU, descriptive, existing records): C1, C2 and C3 read again with average precision (and the
  trapezoid PR-AUC the release reports), on DL's split and the rotations.
- Paper (user decisions 2026-11-04): if D29 shows no EEG-specific plateau, C2/C3 are presented as
  exploratory, not as a main contribution.
- User decisions (2026-11-04 15:19 local) on the external review: abstract without exceptional
  configurations (suggestion 8; replaces the earlier "state the exception" choice for the abstract only;
  the q95 case stays in the body); local git freeze of new protocols; run D28 and D29.

### D28 / D29 outcomes (2026-11-05 00:19 local, AFTER the results; frozen rules (c0283f4) applied as written; each re-checked by an independent re-computation from the raw records: all rule outputs CONFIRMED; refuted descriptive side claims corrected below)
- D28 (artifacts/analysis/D28/README.md, d28.json, recheck.md; 505 records, 1,010 probe fits, 16,160 config
  fits; replaying selection and early stopping gives 0 disagreements; 986 of 1,010 selected fits converged):
  - Q1 (any SA gain last - lp "gain demonstrated"?): NO in 0 of 18 readings; 16 read "equivalent within
    +-3" (TOST), 2 "not resolved" (BIOT Siena grid_z -0.2, TOST p 0.076; CBraMod CHB-MIT grid_z -4.4, lp
    ahead of last, not driven by a single fit).
  - Q2 (BIOT q95 on DL's split, last - last_noise): NO: grid -0.3 [-1.5, +0.9], TOST p 0.0017; grid_z -0.3
    [-3.1, +2.5], p 0.027; both equivalent. With tuned probes the arms are no longer below chance (lp / last
    / last_noise 72.4 / 73.3 / 73.6 vs 33.1 / 41.9 / 33.3 with the fixed raw head): the one gain that beat its
    noise control (D27-A1) was an artifact of the under-trained fixed raw head.
  - Q3 (pretrained-vs-random directions): CBraMod 16 of 16 keep the sign (11 "gain demonstrated"; 3 earlier
    gains become "not resolved"). BIOT 9 of 16 keep the sign (sign-of-mean reading, the reader's choice; the
    rule text does not define "direction"); 6 of the 7 flips start from fixed-recipe means within +-2.2 (no
    established direction); the only flip of an established direction is Siena filtered grid last_randinit
    - last (-4.7 -> +4.6, both "not resolved"). BIOT on DL's split: random init still ahead but smaller
    (last_randinit - last +14.3 raw / +7.7 standardized vs +35.8 / +9.1 fixed). CHB-MIT rotations, BIOT
    standardized: pretrained features ahead (lp - lp_randinit +6.8, t-interval excludes 0, Nadeau-Bengio
    does not). No rotation contrast is "gain demonstrated" with the Nadeau-Bengio interval.
  - Descriptive: 944 of 1,010 selected configurations sit at a grid edge (lr 3e-3: 498; wd 1e-1: 523);
    BIOT q95 grid picked lr 3e-3 in 15/15; CBraMod grid_z on DL's split lr 1e-4 in 20/20 (the grid may not
    bracket every optimum; reported as a limitation). Re-check corrections: test ROC < 50 in 6 fits (not
    7); validation and test do NOT disagree more with tuning (SD of test - val 11.2 tuned vs 13.3 fixed);
    the wide BIOT pretrained-vs-random intervals come from rotation spread the fixed recipe already had.
- D29 (artifacts/analysis/D29/README.md, d29.json; 450 records; last and lp linear reproduce E30b exactly,
  240/240): no setting or head shows an EEG-specific plateau: the noise rule reads "no difference
  demonstrated" for C2 and C3 in all 4 setting x head cells (Siena raw head last - last_noise about +3.8 at
  every N, t-intervals include 0). C3 "supported as written" holds only with the raw head (and the noise
  curve passes the same C3 rule); with the standardized head C2 is "not testable" and C3 "uninformative"
  on both Siena paths (Siena v - LP +2.85 to +2.91, just under the 3-point cut). Per the user decision of
  2026-11-04, C2/C3 are presented as exploratory. Re-check correction: the raw head does reach TOST
  equivalence in one cell (Siena filtered linear at P2N2048, p 0.037), so "no equivalence with the raw head"
  holds for all but that cell. PR-AUC readings: artifacts/analysis/D29/README.md (descriptive).
- User decision (2026-11-05 09:14 local) on the abstract after D28: use exactly "With linear probes
  tuned to convergence using the same hyperparameter search for every arm, no adaptation gain is
  demonstrated across 18 tested comparisons; 16 establish equivalence to zero within ±3 ROC-AUC points. We do
  not claim that SSL adaptation never helps." Keep the headline reproduction results earlier in the abstract;
  "18 tested comparisons", never "any setting"; the body replaces the q95 exception with the D28 result (arms
  at about 73 ROC-AUC, gain removed); the methods state D28's timing and exploratory/confirmatory status.

## D30. PR-AUC read without the ROC threshold, and the EEG-vs-noise PR-AUC finding (2026-11-05 19:54 local; post hoc: in answer to external review r2, AFTER all data; supersedes the PR-AUC part of "## D29" and the "PR-AUC readings ... (descriptive)" line of the D29 outcomes)
Why: D29 read PR-AUC with the ROC rules, including the 3-point margin. Review r2 showed that this hides
measured differences: BIOT on Siena, average precision 1.65 (LP) -> 2.20 (SA), difference +0.55
[+0.14, +0.96], about +33% relative, was labelled "no consistent difference" only because 0.55 < 3.
I verified that example from the raw records myself: AP 1.6547 -> 2.2039, +0.5492 [+0.1417, +0.9567],
+33.2%; trapezoid PR-AUC +0.5409 [+0.1864, +0.8955]; test prevalence 0.43-0.99% per rotation.
- New PR-AUC reading (scripts/analysis/d29_read.py; artifacts/analysis/D29/pr_auc.md, pr_auc_table.tex):
  report both arm means, the absolute difference with its 95% t-interval over the stated units, the
  relative change in percent, and whether the interval excludes 0 (the only inference claim). NO
  practical-importance label and no margin-3 TOST: defining a PR-AUC margin now would be a post hoc
  threshold, and the statement says so and points to the prevalence-scaled measures in the artifacts.
  Every ROC reading is unchanged (verified byte-identical), and the ROC numbers that lived only in the old
  PR section are kept verbatim as reference tables.
- Withdrawn: the old counts "3 string changes" / "6 string changes" / "31 of 34 rows agree with the ROC
  string" have no referent any more. artifacts/analysis/D29/recheck.md confirmed the VALUES, which still
  hold; only its two label-count lines are superseded (dated note appended there).
- NEW FINDING, and the matched test of it (both recomputed by me from the raw records today):
  At the same parity SSL budget, BIOT on Siena, last - last_noise in average precision x100 over the 5
  rotation means (95% t-interval, df 4): fixed-recipe linear probe +0.28 [+0.05, +0.52], 5 of 5 rotations
  positive, interval excludes 0 (+14.7% of the 1.92 noise baseline); tuned probe -0.72 [-1.68, +0.24],
  1 of 5 positive, interval includes 0. CHB-MIT and Siena filtered show no difference with either probe.
  At the fixed-compute budget (D29) the fixed-recipe probe gives the same picture more strongly: +0.35 to
  +0.50 at all 7 subsets, 5 of 5 positive, t AND Nadeau-Bengio intervals exclude 0 (one NB lower bound at
  +0.00), on a 2.2 AP baseline; with the standardized head and on filtered Siena every interval includes 0.
  Reading: the one place where EEG adaptation beats noise adaptation on a conservative interval is the
  fixed-recipe raw probe on Siena, measured in PR-AUC, and tuned probes remove it and reverse its sign.
  This is the paper's thesis in PR-AUC terms, and it must be reported with the fixed-recipe result shown,
  not only the tuned one. Absolute levels rise with tuning (Siena last 2.20 -> 5.25 AP), so the fixed-recipe
  difference sits between two poorly-performing arms.

## Clarification 2026-11-07: "bit-reproducible"

Two earlier entries of this log call the pipeline "bit-reproducible" (the D20-era entry on the history
logging, and the D28 entry on the feature pass). That wording is too strong and the earlier entries are
left exactly as written. What was measured, and what the paper reports, is agreement within an absolute
tolerance of 1e-6: 484 of 484 re-run pairs, the 95 of 95 D27 repeat values, and the 240 of 240 D29
records matching the recorded E30b values. Read every earlier "bit-reproducible" in this log as
"reproducible within 1e-6 on the same hardware and container". Raised by the supplement review of
2026-11-08; no number changes.

## D31 (2026-11-14, BEFORE the runs): expanded probe search

**Status: additional analysis, motivated by the existing D28 results.** Freezing this protocol does not make
any earlier decision prospective. The D28 family stays exactly as published until this protocol's runs are
read; see "Reporting" below for what replaces what.

**Why.** D28 selected 498 of 1,010 fits at the largest learning rate (3e-3) and 944 at a grid edge, and 24
selected fits reached the 200-epoch cap. The search may therefore not bracket the optimum, which the paper
already states. This expansion tests that boundary once.

**Grid (frozen).** lr in {3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2} x wd in {0, 1e-4, 1e-2, 1e-1, 1} = 30
configurations, which contains D28's 16 as a subset. Both feature variants (raw "grid", standardized
"grid_z"). Identical search and selection for EVERY compared arm.

**Budget (frozen).** Common maximum of 500 epochs, batch 256, constant lr, BCE on logits, the existing
early-stopping rule unchanged (val ROC-AUC, min_delta 1e-4, patience 20). Selection on VALIDATION only:
best_val = max(curve), best_epoch = first argmax, selected configuration = first argmax over (lr, then wd).
Test is scored once, after selection.

**Coverage (frozen).** The existing 18-comparison family in full: P1G and P1QG on DL's split (5 seeds) and
S1G, S3G, S3FG rotations (5 rotations x 3 seeds), both models except the q95 setting, which is BIOT only.
If any part cannot run, that part is reported separately and the original family's counts are retained.

**Records (frozen).** Stopping epoch, selected lr and wd, whether the selection sits at a grid edge, the
per-epoch training loss and validation ROC-AUC curve of every configuration, and absolute test ROC-AUC and
average precision per arm.

**Analysis (frozen).** The same statistics as D28: paired last - lp and last - last_noise differences, 95%
t-intervals over the 5 units (df 4), Nadeau-Bengio intervals for the rotation comparisons only, TOST at
margin 3 and alpha 0.05, and the post hoc margin sweep at 1, 2 and 3 points. Reporting absolute performance
alongside every paired difference.

**What this can and cannot establish (frozen).** Fewer boundary selections and earlier stopping do NOT
establish optimization convergence, and the paper must not claim they do. The claim is bounded: a wider
equal-budget search than D28's either changes the paired adaptation effects or does not.

**Stopping rule (frozen).** This expansion runs ONCE. If an effect is still sensitive to the search, that
sensitivity is disclosed. The search is not enlarged again to reach a preferred result.

**Reporting (decided 2026-11-14, by the author, BEFORE the runs).** The expanded search REPLACES D28 as the
primary tuned-probe analysis, and the equivalence counts, the margin sweep and the abstract numbers are
recomputed from it. D28's counts remain in the paper as the narrower pre-registered search, and the change
between the two is reported. The prespecified-analysis label stays attached to the ordinary t-based inference,
not to the grid.

## D32 (2026-11-14, BEFORE the runs): tuned probes and matched noise controls for the large E29 gains

**Status: additional analysis, motivated by the existing E29 results.** Not prospective for E29 itself.

**Why.** The largest surviving gains in the project are E29 Siena BIOT at ssl_lr 1e-3: cell 2 (4,174 SSL
windows) last - lp +21.1 and cell 5 (full eligible pool) +21.5, each firing the exploratory rule in 4 of 5
rotations (artifacts/analysis/E29/e29.md). Their only noise controls are the one-seed descriptive A5 rows of
D27X. They have never had tuned probes. The paper discloses this (Appendix C, E29 paragraph), and D32 turns
the disclosure into measurement.

**Configurations (frozen).** Exactly the two E29 recipes, unchanged: BIOT, Siena, labels overlap, backbone
mode eval, --set ssl_lr=1e-3, cell 2 without --ssl-n all and cell 5 with it. No other parameter moves. The
recorded update count of each recipe is reported, because learning rate, data exposure and duration must not
change together.

**Arms (frozen).** lp (pretrained, no adaptation), last (EEG-adapted) and last_noise (noise-adapted),
matched to last on learning rate, update count, initialization and every other training setting; the noise
arm differs only in arm and data_hash.

**Units (frozen).** 5 rotations x 3 seeds [S_r, 1000+r, 2000+r].

**Probes (frozen).** The D31 expanded search and selection, identically for all three arms.

**Outcomes (frozen).** Absolute ROC-AUC and average precision; paired EEG-minus-LP and EEG-minus-noise
differences; per-rotation values; 95% t-intervals, Nadeau-Bengio intervals and TOST at margin 3. Average
precision is read WITHOUT the ROC margin (D30).

**Decision (frozen).** If a substantial gain survives matched tuning, it is given prominence in the main text
and the interpretation is revised: that would change the empirical adaptation finding, and it would NOT
reverse the two verified code findings, which are static facts about the release.

**CHB-MIT extension.** Cell 5 for BIOT on CHB-MIT is conditional on the Siena result and on cost; it is not
part of this freeze.

**Stopping rule (frozen).** Runs once per configuration. No search for a larger step budget or a different
recipe if the result is unwelcome.

## D32 outcome (2026-11-15, AFTER the results; frozen protocol of "## D32" applied as written)

**The large E29 gains do not survive equal-budget tuned probes.** E29's fixed-recipe \lastarm$-$\lparm{} was
+21.1 (cell 2, 4,174 SSL windows) and +21.5 (cell 5, full eligible pool), each firing the exploratory rule in
4 of 5 rotations. With the D31 search (30 configurations, 500 epochs, validation-only selection) applied
identically to all three arms, the same comparisons read (5 rotation means over 3 seeds, df 4):

| cell | features | contrast | mean | 95% t | NB 95% | t verdict | NB verdict |
|---|---|---|---|---|---|---|---|
| 2 | raw | last - lp | +2.4 | [-2.2, +7.0] | [-5.3, +10.0] | not resolved | not resolved |
| 2 | raw | last - last_noise | +0.8 | [-3.6, +5.3] | [-6.5, +8.2] | not resolved | not resolved |
| 2 | std | last - lp | -1.0 | [-4.5, +2.6] | [-6.8, +4.9] | not resolved | not resolved |
| 2 | std | last - last_noise | +0.4 | [-2.3, +3.0] | [-4.0, +4.8] | equivalent within +-3 | not resolved |
| 5 | raw | last - lp | +3.1 | [-1.8, +8.0] | [-5.1, +11.2] | not resolved | not resolved |
| 5 | raw | last - last_noise | +1.1 | [-1.8, +4.0] | [-3.7, +5.9] | not resolved | not resolved |
| 5 | std | last - lp | +0.8 | [-0.4, +2.0] | [-1.2, +2.8] | equivalent within +-3 | equivalent within +-3 |
| 5 | std | last - last_noise | +1.5 | [-0.7, +3.7] | [-2.1, +5.1] | not resolved | not resolved |

**What this establishes.** None of the 8 contrasts demonstrates a gain: the +21 effects fall to +2.4 and
+3.1 on raw features and to -1.0 and +0.8 on standardized features, and every interval contains 0. The large
fixed-probe gains were substantially reduced under equal-budget tuned probes, indicating substantial
sensitivity to probe evaluation.

**Why the causal wording was softened (2026-11-15, after the review).** An earlier draft of this entry said
the gains "were therefore a probe-training artifact". That attributes the change to probe training alone,
which this design cannot support: E29 used ONE seed per rotation and D32 uses three, so seed count and probe
training moved together. A matched-seed comparison would be needed to attribute the reduction specifically to
probe training. The dependence-adjusted raw-feature intervals also still allow benefits up to +10.0 (cell 2)
and +11.2 (cell 5), so "the large gains were not recovered" is the supportable claim and smaller benefits
stay unresolved.

**What it does NOT establish, stated plainly.** Only 2 of the 8 contrasts establish equivalence within +-3
under t, and only 1 of those survives the Nadeau-Bengio correction. The other 6 are unresolved: with 5
rotation units at df 4 the intervals are wide (up to +-8 points on raw features). So the evidence bounds
these effects well below +21 but does not show them to be zero.

**Stopping diagnostics (corrected 2026-11-15).** All 180 selected configurations stopped before 500 epochs.
In 54 searches, at least one candidate reached the cap; 263 of 5,400 candidates were capped. The longest
selected configuration ran 283 epochs. The earlier wording incorrectly treated a search with a capped
candidate as a capped selected fit. Early stopping still does not establish optimization convergence.

**Integrity checks (all pass).** 90 records = 2 cells x 5 rotations x 3 arms x 3 seeds, 0 smoke, 0 missing.
Every record carries 30 configurations, grid version 2 and max_epochs 500. Every adapted arm has
adapt_spec lr 0.001, matching the real E29 S3LR2 record. 10 of 10 jobs Completed, 0 Failed, 19,642 billable
seconds, about $16.70.

**Reporting.** D32 is an additional analysis motivated by E29 (per its freeze). It does not change the
18-comparison family; D31 does that.

## D31 outcome (2026-11-15, AFTER the results; frozen protocol of "## D31" applied as written)

**Integrity (all pass).** 505 records = P1W 40, P1QW 15, S1W 150, S3W 150, S3FW 150; 0 smoke, 0 missing.
0 of the 1,010 selected fits violates the frozen spec (30 configurations, version 2, 500 epochs, batch 256,
patience 20, min_delta 1e-4, constant schedule, float16 features). 3 raw records were read individually
before any aggregate was trusted. 41 of 41 jobs Completed, 0 Failed, 265,474 billable seconds, about $225.65.

**The expanded search does NOT simply confirm D28. It moves the numbers, and the paper must say so.**

| quantity | D28 (16 configs, 200 epochs) | D31 (30 configs, 500 epochs) |
|---|---|---|
| \lastarm$-$\lparm{} range over the 18 | $-4.4$ to $+0.9$ | $-1.1$ to $+5.7$ |
| equivalent within $\pm3$, ordinary $t$ | 16 of 18 | 14 of 18 |
| equivalent within $\pm3$, dependence-adjusted | 13 of 18 | 12 of 18 |
| margin sweep, ordinary (1 / 2 / 3 points) | 5 / 11 / 16 | 4 / 10 / 14 |
| margin sweep, adjusted (1 / 2 / 3 points) | 3 / 8 / 13 | 2 / 6 / 12 |
| comparisons labelled "gain demonstrated" | 0 | 0 |

**What survives.** No comparison meets the registered gain criterion, which needs a 95% t-interval excluding
0 AND a mean above 3 points. No positive effect has a dependence-adjusted 95% interval excluding 0. The
headline conclusion therefore stands: the expanded equal-budget search recovers no demonstrated adaptation
gain in any of the 18 comparisons.

**What weakens, stated plainly.** The bound is looser than D28's. The largest effect rises from +0.9 to
+5.7 (BIOT q95 standardized, 95% t [-1.0, +12.3], unresolved), so "differences range from -4.4 to +0.9"
must become "-1.1 to +5.7". Under ordinary inference two previously equivalent comparisons become unresolved. Under corrected
inference, five lose equivalence and four gain it, giving a net change from 13 to 12. Six of the 18 are unresolved under dependence-adjusted inference.

**Two comparisons need a careful sentence (raised by the review).** S3W BIOT raw and standardized both read
+1.7 with ordinary t95 [+0.1, +3.3] and [+0.3, +3.1], which EXCLUDE zero. Their Nadeau-Bengio intervals
[-1.0, +4.4] and [-0.7, +4.1] include zero, and both fail the registered criterion because the mean is below
3. So "no adaptation gain is demonstrated" is too blunt: the supportable claim is that no positive effect has
a 95% interval excluding zero under dependence-adjusted inference.

**The search-boundary concern is REDUCED, NOT RESOLVED.** 864 of 1,010 selected fits still sit on a grid
edge (85.5%, against D28's 944 of 1,010 = 93.5%), and 428 of 1,010 chose the new largest learning rate 1e-2
(against 498 choosing D28's largest, 3e-3). All 1,010 selected configurations stopped before the 500-epoch cap; 491 of 30,300 candidate
configurations reached it, in 109 searches. The previous count of 109 capped selected fits was a counting
error (corrected 2026-11-15). The epoch allowance increased 2.5-fold and the maximum configuration-by-epoch
allowance 4.69-fold. The boundary selections remain a limitation; the paper must not claim optimization
convergence, and under D31's own
stopping rule the search is NOT enlarged again.

**Noise controls under D31.** 14 \lastarm$-$\lastnoise{} comparisons: 13 equivalent within +-3 under
ordinary t (D28: 12), 8 under dependence-adjusted inference (D28: 9).

**Reporting (the author's pre-run decision, "## D31").** D31 REPLACES D28 as the primary tuned-probe
analysis; the equivalence counts, the margin sweep and the abstract are recomputed from it, and D28 stays in
the paper as the narrower pre-registered search with the change between the two reported.


## Reporting and stopping-count correction (2026-11-15, AFTER the D31/D32 results)

The manuscript now uses D31 as primary, as decided before its runs, and reports D32 separately.
A re-computation from selected configurations corrects the capped-fit wording above: the probe-level
`epochs_run` is the maximum over all candidates, not the run length of the selected candidate.
No selected D31 or D32 configuration reached 500 epochs. The paired effects, intervals, equivalence
counts and margin sweep are unchanged. The original narrower search and its complete results remain
in the supplement; repeated prose and identifier catalogues were moved there to shorten the manuscript.


## Reporting revision (2026-11-16, AFTER D31/D32 results)

The title now describes non-recovery of the large reported gains. The main-text random-feature advantage
on DL's split is corrected from the older-search value of 14 to the primary D31 value of 12.2 points
(frozen LP minus frozen random features; this is distinct from the 11.4-point adapted random-initialization
contrast). Original runtime overrides or a different code version remain possibilities, not established
facts. The prose refers to the study's gain criterion rather than using its three-point mean threshold
as the definition of any statistical improvement.

Figure 2 now displays Nadeau–Bengio corrected intervals for subject rotations and ordinary seed intervals
on DL's fixed split. Its four panels focus on EEG adaptation against LP and noise. The full random-feature
contrasts and uncertainty remain in the existing result tables, and absolute levels remain in Figure 3.
All 59 displayed interval readings agree with the saved D31 results; no effect estimate, equivalence count,
margin sweep or raw record is changed by this reporting pass.

A targeted separately implemented logistic-probe solver check is proposed for BIOT on DL's q95 split
and the primary Siena rotations, using matched LP, EEG and noise arms with raw and standardized features.
It is not yet frozen, implemented or run. No new experiment is claimed by this revision, and no GPU run
was launched. The verified author-contact cutoff remains 2026-11-02 until the author supplies an updated
status.


## Title wording confirmed (2026-11-16, AFTER the reporting revision)

The author requested the title “Large Reported CHB-MIT Adaptation Gains Disappear with Pretrained
Encoders and Matched Probes.” This replaces the “Are Not Recovered” wording selected earlier in the
reporting pass. The qualifier “Large Reported” refers to the published headline gains. The abstract and
body continue to report 12 of 18 equivalences and six unresolved comparisons, and do not exclude smaller
benefits. This title-only change does not change any result, statistical analysis or experimental protocol.
The manuscript metadata, supplementary source title, release README and current revision checklist use
the confirmed wording. Previously built PDFs and archives still need regeneration.


## Author-correspondence update (2026-11-16, author-confirmed)

The author reports first contacting the original authors around 2026-09-10 and following up on
2026-10-28, with still no response as of 2026-11-16. The September date is approximate, as reported;
its message contents have not been specified. The October follow-up retains the previously documented
questions 1–6. The manuscript now reports both contacts and the verified 2026-11-16 cutoff in ordinary
text. The correspondence checklist item is complete. Earlier 2026-11-02 status entries remain historical
records rather than being rewritten or back-dated.

## D33 (2026-11-16, BEFORE the runs): convex-probe optimization check

**Status: additional analysis, motivated by D31's own diagnostic.** Freezing this protocol does not make any
earlier decision prospective. It does NOT change the 18-comparison family of D31, which stays the primary
tuned-probe analysis; D33 is reported separately.

**Why.** D31 widened the search to 30 configurations and 500 epochs and still left 864 of 1,010 selected
fits at a grid edge and 428 at the largest learning rate [AMENDED A3: the cap clause of this sentence
was wrong and is corrected in the D33 amendment below]. Early stopping is a
stopping rule, so neither D28 nor D31 can claim the probe reached its optimum. A logistic-regression probe
makes that claim checkable: the objective is convex, so a converged solver is at the global optimum of the
probe, and convergence can be VERIFIED rather than assumed.

**Scope (frozen).** BIOT only, the two settings where the probe mattered most: DL's split with the q95 input
(5 seeds) and Siena rotations (5 rotations x 3 seeds). Arms lp (pretrained, no adaptation), last
(EEG-adapted) and last_noise (noise-adapted, matched to last on learning rate, update count, initialization
and every other training setting). Both feature variants: raw and train-standardized.

**Probe (frozen).** scikit-learn LogisticRegression, solver lbfgs, L2 penalty, on the SAME cached frozen
encoder features that the tuned probes use (backbone in eval mode, encoder tap, the parity probe's path).
Regularization C in {1e-4, 1e-3, 1e-2, 1e-1, 1, 10, 100}, selected on VALIDATION ROC-AUC only; ties take the
smaller C. max_iter 20000, tol 1e-6. Test is scored once, after selection.

**Convergence must be verified, not assumed (frozen).** Every fit records n_iter, max_iter, tol and a
boolean converged = the solver stopped before max_iter without a ConvergenceWarning. A setting is reported
as optimization-converged only if EVERY arm's selected fit in it converged. Any non-converged fit is
reported as such and not silently dropped.

**Outcomes (frozen).** Absolute test ROC-AUC and average precision per arm; paired last - lp and
last - last_noise differences; per-rotation values; 95% t-intervals over the 5 units (df 4), Nadeau-Bengio
intervals for the rotation setting, and TOST at margin 3 with alpha 0.05. Average precision is read WITHOUT
the ROC margin (D30).

**What this can and cannot establish (frozen).** It can establish that a convex probe on these frozen
features reached its optimum, so a remaining difference cannot be blamed on probe under-training. It CANNOT
establish anything about the non-convex probes of D28 and D31, and it does not make their searches
convergent in retrospect. A logistic probe is also a different hypothesis class from the SGD-trained linear
head, so its absolute numbers are not interchangeable with theirs.

**Stopping rule (frozen).** Runs once per setting. If a difference is still sensitive to the probe, that
sensitivity is disclosed. The C grid is not widened afterwards to reach a preferred result.

**Reporting (frozen).** A compact sensitivity table plus the convergence diagnostics, kept separate from
D31's 18 comparisons. The conclusion or the title changes only if a benefit is demonstrated under this
probe, by the same criterion used elsewhere: a 95% interval excluding zero AND a mean above 3 points.

## D33 amendment (2026-11-16, BEFORE the runs; cb531a6 preserved, superseded only where stated)

Six corrections to the D33 freeze. The scope is unchanged: BIOT, DL's q95 split and Siena rotations, arms
lp / last / last_noise, raw and standardized features. No model and no dataset is added.

**A1. The "non-convex" and "different hypothesis class" wording is withdrawn.** It was wrong. The D28 and
D31 probes already fit an AFFINE head with binary cross-entropy on frozen features
(src/eegdrift/probe_grid.py:119; head_params 257 = 256 weights + bias), so logistic regression is the SAME
linear hypothesis class, differing in the optimizer and the regularizer. That makes D33 a MORE direct check
of the optimization objection, not a parallel one. The superseded sentence claimed the opposite.

**A2. Convergence is solver-reported, and the claim is narrowed to match.** No warning plus n_iter <
max_iter establishes that L-BFGS-B's own stopping test fired, not an exact optimum: it can stop on a small
objective change (ftol) OR a small projected gradient (gtol). Each fit therefore records n_iter, max_iter,
ftol, gtol, the final regularized objective and the final gradient infinity-norm. **Acceptance criterion,
fixed now, before any run:** a fit counts as numerically converged if n_iter < max_iter AND no
ConvergenceWarning AND the final gradient infinity-norm is below 1e-5. Every selected model is then refit at
tol 1e-9 as a stability check, and the refit must move test ROC-AUC by less than 0.001 in absolute terms;
any fit that fails either test is reported as non-converged and is NOT dropped. The result is described as
numerical convergence of the fixed-C training objective, never as globally optimal probe performance.

**A3. The epoch-cap sentence in cb531a6 is corrected.** The freeze said "109 at the epoch cap". That is
wrong, and the error was mine: it read the top-level epochs_run, which is not the selected configuration's
(the D28 recheck already recorded that the two differ in 848 of 1,010 fits). Re-counted from the records
2026-11-16: **0 of the 1,010 selected D31 fits reached the 500-epoch cap**; 491 of 30,300 candidate
configuration fits reached it, spread over 109 searches. D32 has the same shape: 0 of 180 selected fits, 263
of 5,400 candidates, over 54 searches. The paper already states both correctly
(paper/tmlr/sections/s7-main.tex:218, app-c-robust.tex:559). The boundary concern stands on the edge counts,
864 of 1,010 selected fits and 428 at the largest learning rate, not on the cap.

**A4. Comparison and diagnostics made precise (frozen).** [CORRECTED by C2 below: arms necessarily have
different features; the requirement is identical split definitions and extraction procedures, with each
arm's raw and standardized probes sharing that arm's one feature matrix and its train-only statistics.] Validation ROC-AUC is recorded for EVERY C in the grid, not just the winner, together with a
flag for whether the selected C sits at either boundary of {1e-4, ..., 100}. Binary ROC-AUC and average
precision are computed from decision_function scores, not predict_proba, so the linear confidence scores are
what is scored. For Siena the three seeds are averaged WITHIN each rotation first, giving five units, and
dependence-adjusted inference is the primary reading for that setting.

**A5. The ">3 points" rule for changing conclusions is removed.** Any credible positive effect informs the
discussion, including one below 3 points. Equivalence within +-3 and evidence of a positive difference can
coexist and will both be reported. The title stays defensible while the large reported gains remain
unrecovered, but the interpretation follows all of the results, not a threshold.

**A6. The cache and cost claims are marked provisional.** src/eegdrift/study.py:339 shares one feature
extraction among the existing grid variants but does not yet expose that cache to the logistic helper;
sharing one extraction between the raw and standardized logistic fits is feasible and is what will be
implemented. The historical D31 caches were NOT persisted, and CPU fitting inside a GPU job still bills GPU
time. The frozen scope implies 60 cells x 2 variants x 7 C values = **840 candidate logistic fits** before
any stability refits. The $40 to $70 estimate is provisional until a representative timing run.

**Replacement for the strongest claim of cb531a6.** D33 tests whether the targeted BIOT findings persist
with numerically converged, validation-selected regularized linear probes on the same frozen encoder
features. It assesses sensitivity to probe fitting but does not establish optimal test performance or
convergence of the earlier D28 and D31 procedures.

**Reporting (unchanged).** A compact targeted sensitivity analysis with its convergence diagnostics, kept
separate from D31's primary 18-comparison family.

## D33 clarifications (2026-11-16, BEFORE the runs; refine A2, A4 and A6 of the amendment)

**C1. Numerical convergence and prediction stability are two separate flags.** Each fit records BOTH, and
neither is reported as the other:
- `numerically_converged`: n_iter < max_iter AND no ConvergenceWarning AND the final gradient
  infinity-norm is below 1e-5. The objective and gradient are computed against the EXACT objective the
  solver minimises, which for scikit-learn 1.6.1 with unweighted samples is the MEAN-NORMALISED form

      F(w, b) = (1/n) * sum_i BCE(y_i, w.x_i + b) + ||w||^2 / (2 C n),

  with the intercept unpenalised. Verified in the installed source: `l2_reg_strength = 1.0 / (C * sw_sum)`
  with `sw_sum = n_samples` (_logistic.py:447), `loss = loss.sum() / sw_sum` plus
  `l2_penalty = 0.5 * l2_reg_strength * ||w||^2` (_linear_loss.py:323 and :207), and
  `grad_pointwise /= sw_sum` (_linear_loss.py:326).

  [CORRECTED 2026-11-16, before any run: C1 first wrote this as the SUMMED cross-entropy plus
  ||w||^2 / (2C). That has the same minimiser but a gradient n times larger, so against the fixed 1e-5
  threshold it would have marked converged fits as non-converged, with n in the thousands here. The
  threshold stays 1e-5 and the normalisation is corrected.]

  L-BFGS-B stops on either its objective tolerance (ftol) or its projected-gradient tolerance (gtol), so
  both are recorded with the gradient norm.
- `prediction_stable`: the tol 1e-9 refit of the selected model moves **validation** ROC-AUC by less than
  0.001 in absolute terms, which is **0.1 ROC-AUC percentage points** on the x100 scale the paper uses.
  Validation, not test, is the acceptance criterion.

The same refit comparison on the TEST score is recorded as a reported diagnostic only. It never controls
model selection, exclusion, or any further tuning. A fit that fails `prediction_stable` while passing
`numerically_converged` is described as numerically converged with unstable predictions, not as a
convergence failure.

**C2. A4's "identical cached features" is corrected; it was wrong.** LP, EEG-adapted and noise-adapted
encoders are different encoders and must produce different features; identical features across arms would
mean the adaptation did nothing. The frozen requirement is:

> All arms use identical split definitions and feature-extraction procedures. Within each arm, raw and
> standardized logistic probes share one extracted feature matrix; standardization statistics are fitted on
> that arm's training features only.

**C3. The smoke cannot price the production runs, and will not be used to.** Verified in
src/eegdrift/study.py:216 and 175: a smoke caps the train split at 1,500 windows and val and test at 500,
caps the SSL pool at 256 windows, and runs 1 adaptation epoch. Its runtime says nothing about production
cost. The sequence is therefore: smoke for CORRECTNESS only, then ONE production-sized job timed end to end,
including the full 7-point C grid and the selected-model refits, and that timed job COUNTS as one of the
eight planned jobs rather than being extra. The provisional $40 to $70 estimate is replaced by a measured
per-job cost from that pilot before the remaining jobs are submitted.

**Unchanged:** the scope (BIOT, DL's q95 split and Siena rotations, arms lp / last / last_noise, raw and
standardized features), the stopping rule, and the separation from D31's primary 18-comparison statistics.
Every convergence failure, every boundary selection of C, and every scientific outcome is reported.

## D33 reporting wording (2026-11-16, fixed before any result is written up)

Three statements about the D33 diagnostics, to be used verbatim in the paper and in every status report.

**W1. Similar ROC-AUC does not establish similar features.** ROC-AUC scores the ranking of predictions, not
the similarity of representations. Nothing in the smoke measured feature or parameter change, so the
correct sentence about the reduced-budget smoke is: "The reduced-budget smoke produced similar test ROC-AUC
across arms; it does not assess adaptation effects." The earlier phrasing, "the encoder barely moves", is
withdrawn: it was an inference about the representation from a ranking metric, which the measurement does
not support.

**W2. `prediction_stable` is the frozen validation-AUC stability check, and nothing wider.** A zero refit
delta establishes that validation ROC-AUC is unchanged by the tol 1e-9 refit. It does NOT establish
unchanged coefficients, unchanged decision scores or unchanged individual predictions, because ROC-AUC
depends only on the ordering of the scores. The flag is always named as the validation-AUC stability check.

**W3. A boundary C is reported as what it is.** A selected C at either end of {1e-4, ..., 100} means
validation chose the strongest (or weakest) regularization the grid offered. It does not undermine numerical
convergence at that selected C, and it does not establish that the optimal regularization lies outside the
grid. Per the stopping rule the grid is not widened afterwards; the boundary selection is disclosed.

## D33 reporting wording, part 2 (2026-11-16, after the pilot, before the full read)

**W4. The Siena effect is a rotation-level paired difference, and the frozen inference is unchanged.** For
each rotation r,

    d_r = mean_s[ AUC(last, r, s) ] - AUC(lp, r),

and the frozen procedure (95% t-interval over the 5 units at df 4, Nadeau-Bengio for the rotation setting,
TOST at margin 3) is applied to those five d_r. The repeated LP values are a SHARED BASELINE, not three
independent LP replicates. Paired inference uses the variability of the differences, so a constant baseline
does not invalidate it. The same form applies to last - last_noise, where both arms do vary with seed.

**W5. Why LP is identical across seed-labelled runs.** Attribute it to fixed inputs and a fixed fitting
procedure: the LP arm performs no adaptation, so its features, data and splits are identical across the
three seed labels, and scikit-learn's lbfgs solver does not consume random_state. Do NOT attribute it to
convexity alone, which is a property of the objective, not an explanation of why nothing varied.
Frozen sentence: "Within each split, LP produced identical results across seed-labelled runs because its
inputs and fitting procedure were fixed. Adaptation effects were averaged across seeds within each Siena
rotation, and inference used five rotation-level differences."

**W6. What the DL-split intervals describe.** Five-seed intervals on DL's fixed split describe adaptation
randomness CONDITIONAL on those patients and that data. They do not measure uncertainty across new
patients. LP's zero observed seed variation on that split must never be presented as certainty about LP's
population performance; it is the absence of one variance component, not evidence of precision.

**W7. The boundary selections in the pilot were NOT ties (checked).** All 18 pilot fits selected C = 1e-4
with a UNIQUE validation maximum, and validation ROC-AUC fell monotonically as C grew in every fit: for
example last, seed 42, raw features gave 85.42 at 1e-4 against 52.42 at 100. So the frozen tie rule did not
decide these; validation preferred the strongest regularization offered by a wide margin. This is reported
as a boundary selection, and it still does not establish that the optimal regularization lies outside the
grid, nor does it bear on numerical convergence at the selected C. Ties, if any appear in the remaining
jobs, will be reported as ties resolved by the frozen rule.

## D33 outcome (2026-11-16, AFTER the results; frozen protocol, amendment and clarifications applied as written)

**Integrity.** 60 records = Siena 45 (5 rotations x 3 arms x 3 seeds, tag S3L) + DL's q95 split 15 (3 arms x
5 seeds, tag P1QL); 60 distinct result keys, 0 smoke. 6 of 6 jobs Completed, 0 Failed, 8,292 billable
seconds, about $7.05. Manifest of every key and source directory: artifacts/analysis/D33/manifest.json.

**Convergence, the deliverable.** All 840 candidate fits satisfied the numerical convergence criterion
(n_iter < 20000, no ConvergenceWarning, gradient infinity-norm below 1e-5 on the mean-normalised objective),
and all 120 selected models passed the validation-AUC stability check (a tol 1e-9 refit moved validation
ROC-AUC by less than 0.1 percentage points). 0 failures of either kind.

**Result (primary inference: ordinary t for DL's fixed split, dependence-adjusted for Siena rotations).**

| setting | features | contrast | mean | 95% interval | TOST p | verdict |
|---|---|---|---|---|---|---|
| DL q95 | raw | last - lp | +0.19 | [-1.33, +1.71] | 0.003 | equivalent within +-3 |
| DL q95 | raw | last - last_noise | -0.90 | [-2.41, +0.61] | 0.009 | equivalent within +-3 |
| DL q95 | std | last - lp | +0.61 | [-0.70, +1.92] | 0.004 | equivalent within +-3 |
| DL q95 | std | last - last_noise | +0.49 | [-2.64, +3.63] | 0.045 | equivalent within +-3 |
| Siena | std | last - last_noise | +0.46 | [-0.57, +1.49] | 0.001 | equivalent within +-3 |
| Siena | std | last - lp | +0.38 | [-4.82, +5.59] | 0.118 | NOT RESOLVED |
| Siena | raw | last - last_noise | +1.82 | [-6.25, +9.88] | 0.352 | NOT RESOLVED |
| Siena | raw | last - lp | +2.87 | [-5.10, +10.83] | 0.483 | NOT RESOLVED |

All D33 candidate fits satisfied the numerical convergence criterion, and all selected models passed the
validation-AUC stability check. None of the eight adaptation contrasts demonstrated an improvement. Five
supported equivalence within +-3 ROC-AUC points under the applicable primary inference procedure; three
Siena comparisons remained unresolved.

**CORRECTION to my own first summary (2026-11-16).** I first reported 6 of 8 equivalent and named only the
two raw Siena comparisons as unresolved. That was wrong twice over: equivalence is the TOST decision, not
whether the displayed 95% interval sits inside the margin, and the primary procedure is dependence-adjusted
for Siena. Siena standardized last - lp is equivalent under ordinary TOST but has adjusted TOST p = 0.118,
so it is UNRESOLVED under the primary reading. Ordinary t throughout would give 6 of 8; the primary
procedure gives **5 of 8 equivalent and 3 unresolved**, and that is the count to report.

**Conclusion wording (frozen).** "In the targeted BIOT settings, numerically converged regularized linear
probes did not reveal a statistically demonstrated adaptation gain. This reduces concern that the findings
arise from insufficient probe optimization, but does not establish convergence of the earlier SGD-trained
probes." The earlier phrasing, "the earlier results cannot be blamed on probe under-training", is withdrawn
as too strong. The raw Siena interval still permits a substantial positive effect, up to +10.8 points, and
that uncertainty stays prominent.

**Regularization selected (descriptive).** 45 of 120 selected fits sit at a grid boundary. The selected C
spreads across the grid: 39 at 1e-4, 35 at 1, 16 at 1e-3, 13 at 0.1, 9 at 0.01, 6 at 100, 2 at 10. The
pilot's uniform 1e-4 was not representative of the full set. Per the stopping rule the grid is not widened.

**MY NAMING ERROR, recorded.** I ran the Siena cells under --run-tag S3L, which E25 already used (the
shipped-MLP-head wave, decisions.md:454, RUNLOG 2026-11-01 rows). No data was harmed: 195 records carry that
tag, 150 from E25 and 45 from D33, with 195 distinct result keys, 0 clashes, and separate unit directories
(E25 in *-l3, D33 in *-ld0..ld4). The tag alone is nonetheless ambiguous, so D33 is selected by
artifacts/analysis/D33/manifest.json or by the presence of the 'logreg' probe, never by run_tag alone. Both
waves keep their recorded tags; nothing is rewritten.

**Reporting.** One compact table plus a short main-text paragraph. D31's primary 18-comparison statistics
are unchanged.

## D33 artifact metadata clarification (2026-11-16, AFTER the results)

The raw D33 result records store tol, max_iter, final objective, gradient infinity-norm and the
two separate flags, but do not separately store ftol or gtol despite the pre-run wording. For
the pinned scikit-learn 1.6.1 lbfgs implementation, gtol is the passed tol and ftol is
64 * eps(float64). These are implementation-derived values, not independently captured runtime
fields. The original records are unchanged. The record reader documents this metadata limitation;
the convergence criterion and all eight contrast results are unchanged.

## Rule 3 exception 1 (2026-11-18, user-approved): the "confirmed (code)" definition in Paper A

Paper A is frozen (CLAUDE.md Rule 3). The user approved ONE exception, limited to one clause of one
sentence in paper/tmlr/sections/app-a-census.tex.

**What was wrong.** The definition read: confirmed (code) if the code copies process2.py, "or its
repository points to CBraMod's preprocessing or reads its output, which determines the split, the
start/end label rule and the duplicate windows". The word "determines" does not hold for the
reads-its-output branch: a loader or config that reads processed_seg shows that a paper adopted someone
else's files, and says nothing about how those files were labelled or segmented. The next sentence already
hedged the text class correctly, so the code class was the inconsistent one.

**What it now says** (the user's wording): "A copied script specifies the split, label rule and duplicate
windows; references to upstream preprocessing or compatible loaders support adoption without establishing
how the evaluated files were produced."

**Scope.** No number, count, table or verdict changes. The 14-plus-5 tally in s6-artifact3.tex:41 was
already correct and is untouched. This is a precision fix to an evidence definition, not a retraction.

**Two further points raised in the same review, NOT applied to Paper A and carried to Paper C instead,
because they would change claims rather than tighten a definition:**
- Copied baselines: BIOT averages two assignments after swapping its validation and test patients, so
  reusing BIOT's published numbers beside a single fixed-split experiment is a comparability question
  separate from preprocessing.
- Target-dataset pretraining is not contamination: BIOT states it trains on CHB-MIT's TRAINING splits, so
  test-subject exposure needs its own evidence and must not be inferred from pretraining on the dataset.
