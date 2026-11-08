# Paper A completeness audit (2026-11-01, workflow wf_310e0a5f-3cd)

> **Historical experiment plan, recorded 2026-11-01.** Statements below about incomplete experiments
> describe the project on that date. They are kept as recorded and were not updated. The released code has
> since been run (92 released-code cells are in `artifacts/released-root/`), and the completed runs and
> their outcomes are in `notes/RUNLOG.md`, `notes/decisions.md` and `artifacts/analysis/`. Added 2026-11-07.

**Experiment plan: Paper A reproducibility audit (deduplicated, ordered)**

Not all required experiments are complete. The biggest gap is that no upstream code has ever run: every "released path" number in the draft comes from our reimplementation. Below, 47 reviewer items are merged into 33. The 8 "dropped or already done" entries at the end are separate from these 33.

Cost units:
- **Our pipeline**, from RUNLOG, on ml.g5.8xlarge: CHB-MIT rotations about 0.27 GPU-h per (arm, seed) with the linear head. Siena about 0.05. Paper split about 0.53 (BIOT) or 0.63 (CBraMod) per (arm, seed) with both heads.
- **Released code**: about 3-6 h wall per run, because the CHB-MIT DataLoaders set no `num_workers` (LoadDataset) and scipy resampling runs in the main process. Packing 2-4 processes per instance (shared page cache, 900 GB NVMe) gives about 1.2 instance-h per run. The E4 smoke must measure this and the estimates should be revised from it.

---

### Phase 0: free, now (desktop or Mac)

**E1 [must] Run the released preprocessing unmodified; audit the environment** (repro 1)
- Clone `c3n-group/efficient-eeg-adapt` at d056cdf into `~/released/eea`, outside the MIT repo.
- Make a py3.12 venv and run `pip install -r requirements.txt`. Log every ImportError. Known missing: einops, linear_attention_transformer, mne, pyedflib, seaborn, matplotlib, umap-learn. Then add pinned versions.
- Create a `'$WORK'` symlink to `~/dxdata/chbmit/1.0.0` and run process1.py, process2.py and make_CHBMIT_for_pretraining.py.
- Record:
  - per-split file and label counts;
  - the number of `-s-` files in test;
  - LMDB `len(__keys__)`;
  - max abs diff against our stores, on about 2,000 seeded keys per store.
- New code: one small comparison script, outside the repo or in `scripts/`, that imports nothing from upstream.
- GPU: 0.
- Rule: the "reproduces" claims in the draft (326,993 / 252 / 206 / 70-of-114 / 81,993 / chb12, 13, 17 dropped) stand only if the counts match exactly and max|diff| ≤ 1e-5 relative. Any mismatch replaces the draft number with the released-script number.
- Unblocks E4-E8 and E21, and the S3 staging. Tar the pickles into shards; 327K small files will not stage well.

**E2 [must] Run the documented commands verbatim and capture the real failure points** (repro 2)
- CPU, in the clone. Use a symlink farm of about 2K pickles as `datasets_dir` and the 4,174-key LMDB from E11 as the SSL store, so no upstream code is edited.
- (a) `main.py method=step_up` for biot and cbramod: save the tracebacks.
- (b) Add `+method.spt_anchor_l2sp_lambda=0`. Save the "Trainable parameters" and SPT-layer lines and check them against 920,576 / 1,709,568 / 442,800 / 845,400.
- (c) Run the ablation entry points (main_layer, main_diversityN with `+dataset.compute_N=896`, main_diversityP), each with and without the key.
- (d) A 10-line CPU check needing no data: build CBraMod with `proj_out = nn.Identity()` and strict-load a full CBraMod state_dict, as trainer.py:309 does. Expect "Unexpected key(s) proj_out.*". Repeat in a /tmp copy with model_factory.py:29 uncommented: step_up should fail and fm_freeze should run.
- Replace `tests/test_upstream_audit.py`. It currently embeds upstream YAML text in the MIT repo, which also conflicts with D1. The new test should compose Hydra against `~/released/eea/src/conf` at test time and skip if the clone is absent.
- GPU: 0.
- Rule: if (d) raises, the paper's CBraMod SA cells were computed with the proj_out tap unless two lines were changed. That answers part of author question 3 without the authors.

**E3 [must] Pre-register D25 before any new run or new analysis**
- Write one dated entry in `notes/decisions.md` holding every reading rule below, with sub-IDs D25-E4 … D25-E33.
- Also log the 2026-11-01 code changes:
  - `--probe-tap`, whose help text already cites "D25" although no D25 exists;
  - full logging.
- Fix the dispersion convention first, from the arXiv PDF (no local copy): SD or SEM, and n. All D13-style distances use it.
- GPU: 0.

### Phase 1: free analyses on existing records (run in parallel with Phase 2)

**E9 [must] Coverage matrix for the paper's CHB-MIT Tables 1-2** (repro 8, part of stats waterfall)
- Extend `scripts/collect_results.py`.
- For every paper cell:
  - paper value and dispersion type;
  - closest reimplementation run (wave 1, R1-R4, C1/C2, P1E, R3E) by D13 distance, separately for test_at_best and test_last (`test_last` is already in every record);
  - the failing metric;
  - a "released-code run" column, filled after E4-E7.
- Add bal/PR/ROC for P1E (4 arms × 2 heads) to draft Table 2.
- AUCPR panel for the "20× AUCPR" claim: PR-AUC and PR/prevalence for lp, last and last_randinit across released path, fixed probe, posthoc dedup/fixed, and corrected protocol.
- Mark TUAB/TUEV "not tested (no TUH)".
- GPU: 0.
- Rule (D25-E9): a cell is "matched" only if D13-consistent at one fixed epoch rule (best or last) across all four Table 1 cells. Report which epoch rule fits better; no mixing within a configuration.

**E10 [must] Statistics on existing records: intervals, equivalence, power, threshold sensitivity, multiplicity, variance components** (stats CI, power, threshold, multiplicity; repro 18)
- Extend `scripts/bootstrap_d24.py`. For every D24-A/B contrast and D17:
  - (a) a t-interval over 5 rotation means, df=4;
  - (b) a Nadeau-Bengio corrected interval;
  - (c) the existing bootstrap, labelled "pre-registered D24-D, under-covers at n=5";
  - (d) one-sided 95% upper bound, plus TOST at ±1, ±2 and ±3, and against +36.2 / +29.5;
  - (e) verdicts at thresholds 0-10 (step 0.5) × k ∈ {3, 4, 5}, flip points, and leave-one-rotation-out verdicts;
  - (f) a power and false-positive simulation of the 3-point, 4/5 rule under normal, t3 and centred-resample errors, using each contrast's SD; report power at 3/5/10/36 and the 80%-power effect;
  - (g) Holm within the families C1, Artifact 1, features and D17, with exact sign-flip p (32 patterns);
  - (h) variance components (rotation, seed, subject).
- The stats reviewer's numbers (e.g. "t [-1.0, +4.8]", "FPR 17%") were computed in memory and are unverified. Only the script output may be cited.
- GPU: 0.
- Rule: descriptive and post hoc. D24 verdicts stay primary. The abstract wording becomes bounds.

**E11 [must] Subject-level and test-set uncertainty** (stats subject-level and 2-patient split; clinical per-patient and cluster bootstrap)
- New script over `artifacts/s3-results/**/results/*.json`, the `.linear.npz` files (y_test, scores_best) and `test-index-*.json`. The `subject` field is present; checked.
- Compute:
  - per-subject ROC/AP per arm and seed, then paired differences for the three D24 contrasts and D17;
  - Wilcoxon, sign-flip, and a mixed model (diff ~ 1 + (1|rotation));
  - a forest plot;
  - macro-over-subjects next to the pooled-fold value;
  - outlier-fold breakdowns (CHB-MIT rot3 +24.4; Siena-filtered rot1 +37.1);
  - chb23 vs chb24 separately in P1E.
- Two-stage bootstrap: subjects within rotation, recompute the pooled ROC, then seeds; 10k reps.
- Seizure-event cluster bootstrap for P1E and Table 4 (upstream, dedup and fixed scorings).
- GPU: 0.
- Rule: label post hoc, because the reviewer has already seen in-memory numbers. TOST at ±3 with a 90% CI is the equivalence statement.

**E12 [must] Event-level (SzCORE) metrics** (clinical)
- New CPU script over the npz files and test indices. Keys are `<file>-grid-<start>`. Seizure intervals come from `configs/*_seizures.json`.
- Moving-average smoothing k ∈ {1, 3, 5}; merge alarms closer than 90 s; tolerance 30 s before / 60 s after; split events longer than 5 min.
- Report sensitivity at 0.5, 1 and 2 FA/h, partial AUC up to 2 FA/h, a non-oracle threshold chosen leave-one-test-subject-out within each fold, and median latency.
- Data: D24-A, P1E and wave 1. Paired last − lp, lp − lp_randinit and last_randinit − last per rotation.
- Check the timescoring licence before using it as an external tool; do not vendor it.
- GPU: 0. Redo with validation thresholds after E25.
- Rule (pre-register in D25 before computing): the D18 paired rule on partial AUC (FA/h ≤ 2) with a margin of 0.05 (an assumption; fix it in D25). Others descriptive.

**E13 [must] Free part of the protocol-fix decomposition** (clinical fix part 1, stats waterfall)
- (a) Run `posthoc_test.py --dataset chbmit --run-tag P1E` against local `artifacts/s3-results`, adding a "dups kept + overlap labels" cell.
- (b) Re-score the S1M/S1E grid test windows with the upstream start/end rule (bounds seconds × 256 − 1).
- (c) Probe-mode pairs: BIOT S1 vs S1M at seed S_r; CBraMod S1 vs S1E.
- (d) A waterfall script (SA level and SA gain, per model and head) with an "unreproduced residual" bar and Shapley values over the 8 existing cells. Re-run after E17 and E18.
- GPU: 0.
- Rule: descriptive. CIs as in E11.

**E14 [must] No-op check: did adaptation change the encoder?** (repro 15, clinical no-op)
- The probe has no feature cache (no cache code in `src/eegdrift/probe.py`), so the cache sub-question is answered by reading the code.
- From the npz files (P1E, S1M, S1E): per-seed Pearson r and max |Δ| between lp and last scores, and between lp_randinit and last_randinit.
- From the records: steps, epoch_losses (first vs kept), lr_sum, displacement rel/coherence per group.
- GPU: 0.
- Rule: r = 1 with max|Δ| < 1e-6 for any pair is a bug (stop, investigate). Otherwise report "weights moved X%, scores r = Y". CPU re-adaptation only if a bug is flagged.

**E15 [must] BIOT probe strength, feature scale and input-scaling precheck** (stats BIOT probe; clinical strong-probe and q95 prechecks)
- Desktop, 192 CPUs. Extract eval-mode BIOT encoder features for lp and lp_randinit on the paper split, 5 CHB-MIT rotations, Siena and Siena filtered. Inputs are /100 (as run) and per-channel q95.
- Report feature std. Fit standardized logistic regression (C on validation) and the parity linear head on z-scored features, following the h3/h5 scripts in `notes/cbramod-check.md`.
- Re-adapt `last` on CPU at seed S_r for Siena only (51 steps, small).
- GPU: 0.
- Rule (D25-E15): "BIOT conclusions are probe-limited" if z-scoring or LR moves lp − lp_randinit by > 3 in ≥ 4/5 rotations on a dataset. That gates E26. "Input scale matters" if q95 lp − /100 lp > 3 in ≥ 4/5. Either way E19 runs (must).

**E16 [must] Hand-verify the protocol census** (repro 12, clinical census)
- For each of the 16 confirmed and 3 likely entries in `paper/protocol-census.md`, record a permalink or quote (split, label rule, duplicate test windows), the commit, and the verifier.
- Downgrade anything without a verifiable line, then update Table 3 and the abstract count.
- GPU: 0. Manual.

**E17-free [should] Search for the origin of 4,174** (repro 10, stats D4 rebuild)
- (a) Counts on our 81,993 SSL store: max|x| < T for T from 100 to 700 µV over the full 30 s, per subject, at /700 and at the "6×" variant.
- (b) Throwaway copies of the released LMDB script with variants: as released; ×6 before the threshold; 100 µV; 800 µV; min_channels=16; chb01-24; 10 s windows; MNE 1.6.
- (c) Cumulative per-file and per-patient sums: single patient, val-only, first-k files in seed-1 order, seizure files only.
- Test hits on 4,174, 86,592 and 86,592/0.4.
- GPU: 0 (CPU on the desktop).
- Rule (D25, before computing): a "match" is a rule reaching 4,174 ± 0 exactly, or ± 1% labelled "near". The variant list is fixed in D25. A match feeds E23.

**E18-free [should] Siena annotation alignment and cross-check** (repro 20, clinical annotation)
- `pip install epilepsy2bids`. Diff its onsets and offsets against both seizure JSONs; each difference must be 0 or explained.
- Onset-locked line length and 1-30 Hz power (−120 to +120 s) for all 47 Siena seizures; count seizures with no rise.
- Zero-parameter line-length ROC per rotation.
- GPU: 0.
- Rule: any unexplained offset larger than 1 window triggers relabelling and a re-score of Siena.

**E19-free [should] Montage/QC sensitivity and chb12/13/17 counts** (clinical QC; free part of chb12/13/17)
- From the preprocess reports: files with n_present < 16 or a QC flag, and affected test windows per fold.
- Re-score the D24-A contrasts without those windows.
- State in §2.2/§5.1: 142 of 198 seizures tested; chb12/13/17 and chb02_16+ dropped, and why.
- GPU: 0.
- Rule: report the contrast change. A verdict flip is flagged as a limitation.

**E20-free [should] Hand-crafted baseline and robustness re-scores** (clinical baseline, clinical free re-scores, stats secondary metrics)
- Log band power (delta-gamma), line length and variance → LR (C on validation), per rotation and on the paper split. An existing single-split value is 91.2 (cbramod-check §4).
- Paired AP and PR lift per rotation; contrasts with scores_last; ≥50%-overlap labels; balanced accuracy at a validation-chosen threshold (after E25).
- GPU: 0.
- Rule: descriptive, appendix.

**E21 [should] Differential test: our reimplementation vs the released modules** (repro 14)
- pytest that imports from `~/released/eea/src` via sys.path at test time and skips if absent.
- Same start state_dict (random and pretrained); 2 SSL steps on 16 windows with the mask and perturbation seeded identically; transfer; 1 probe epoch on 512 windows.
- Compare losses, weights, logits and metrics within 1e-5, for biot/cbramod × linear/mlp_fullft.
- GPU: 0.
- Rule: equality supports "runs exactly this path". If E4 diverges from ours by more than the E5 noise floor, this test locates the cause.

**E22-free [must] Pre-registered vs post-hoc hygiene** (stats)
- Re-read D24-A CBraMod excluding the S_r seeds (in-memory filter, or `--exclude-seeds` in `read_d24.py`).
- Tag every row and abstract number P / P* / H / D. Add a deviations table:
  - 15-run SEM dropped;
  - D18 went from 1 seed per rotation to 3;
  - D24-D bootstrap not cited.
- Check decision timestamps against SageMaker CreationTime and S3 LastModified (read-only, profile <AWS_PROFILE>).
- `git init` and commit; get an archived timestamp before submission.
- GPU: 0.

### Phase 2: released code on GPU (harness clones d056cdf inside the container; only logs, CSVs and .npy come back)

**E4 [must] The four CHB-MIT Table 1 cells as documented plus the missing key; released random-features control** (repro 3)
- Harness: clone and pin in the container; install the E1 env; stage the shards to local NVMe; `'$WORK'` symlink; `training.wandb=False`. Symlink checkpoints to names without '+' for Hydra.
- Grid: {biot, cbramod} × {fm_freeze, step_up + `+method.spt_anchor_l2sp_lambda=0`} × seeds 42/123/2021/3407/8888. Add fm_freeze with `model.use_pretrained_weights=false` × 2 models × 5 seeds. 30 runs.
- Defaults otherwise: full_ft True, batch 256, foundation_dir unset, train-mode probe, 10 epochs, whole LMDB.
- Smoke first (`dataset.training.epochs=1`, the symlink-farm subset).
- New code: a harness script in our repo (clone and run only).
- About 36 instance-h (25-45).
- Rule (D25-E4):
  - per cell, best_* and last_*, D13 distance in E3's dispersion units;
  - "released = ours" if |released − matching wave-1 arm| ≤ max(2 ROC, 2 × pooled SEM) (fm_freeze↔lp mlp_fullft train; step_up↔last_randinit);
  - "random features explain released SA" if |step_up − fm_freeze(random)| ≤ 3 ROC.

**E5 [must] Factorial over the knobs only the authors can confirm** (repro 4)
- LP: fm_freeze × full_ft {T, F} × batch {128, 256}.
- SA: step_up (key 0) × foundation_dir {unset, set via `+model.foundation_dir`} × full_ft × batch.
- For foundation_dir set: SSL store {released LMDB, 4,174-key LMDB}. Write the 4,174-key LMDB with our own seeded script, same pickle and `__keys__` format.
- Screen seeds 42 and 123 (56 new runs, excluding E4 defaults). Then 3 more seeds for every configuration within the screen threshold (≤ about 24 runs). Repeat one same-seed run to measure the noise floor.
- About 95 instance-h (70-120).
- Rule (D25-E5):
  - screen pass at ≤ 5 units on 2 of 3 metrics;
  - "reaches cell" if the 5-seed mean is D13-consistent (≤ 3 units on all 3), at best_* or last_* stated in advance as separate tests;
  - "no released configuration reaches cell X" if none passes;
  - the noise floor widens thresholds by the measured same-seed |Δ|.
  - The W&B mode tag (trainer.py:55) is logged as a check that full_ft=False is the linear head.

**E6 [must] Released Table 2 trainer vs main.py** (repro 7)
- `ablation_layer/main_layer.py model=biot method=step_up method.spt_unfreeze_layers={last1, last2, all}` × 5 seeds × foundation_dir unset (15 runs), plus foundation_dir set × 3 layers × seeds 42 and 123 (6). Key 0. 21 runs, about 25 instance-h.
- Ours: `--arms last2_randinit,all_randinit --seeds 2021,3407,8888 --split paper`, wave-1 protocol (train mode, both heads). About 3 GPU-h.
- Rule:
  - "entry points agree" if per-seed |main_layer last1 − E4 step_up| ≤ the E5 noise floor on all metrics;
  - "fingerprint reproduced in released code" if all three rows are within 2 ROC of 88.67 / 88.44 / 88.60 (D12 tolerance);
  - if the entry points agree, question 8 narrows to "a configuration not in the release".

**E7 [must] Probe tap × backbone mode for LP in the released code** (repro 5b, trimmed)
- Throwaway in-container patches applied by sed from the harness, never committed:
  - (i) uncomment model_factory.py:29;
  - (ii) add `self.model.backbone.eval()` after `self.model.train()` at trainer.py:597.
- CBraMod fm_freeze: 3 new {tap, mode} combinations × full_ft {T, F} × seeds 42 and 123 (12 runs).
- BIOT fm_freeze eval mode × full_ft × 2 seeds (4 runs).
- 3 more seeds where within threshold (≤ 9).
- About 30 instance-h.
- The SA arm with a strict=False patch is dropped: E2(d) answers whether Identity could have been active for SA.
- Rule: "54.14 reachable in released code" if any configuration is D13-consistent with 57.87 / 17.35 / 54.14. Tap effect and mode effect are each averaged over the other factor; "explains" means |effect| > 3 while the other's is ≤ 3.

### Phase 3: our pipeline, must

**E17 [must] Missing Artifact 2 cells in our pipeline** (repro 5a, clinical, stats waterfall a)
- CBraMod, the two missing cells: `--probe-tap proj_out --backbone-mode eval` and default tap with `--backbone-mode train`.
- Paper split: arms lp, last, last_randinit; 5 seeds; `--probes linear,mlp_fullft`.
- Rotations rot0-4: lp and last at seed S_r (pairs with S1 and S1E).
- No new code (flags exist). `--plan-only` then `--smoke`.
- About 26 GPU-h.
- Rule: the 2×2 decomposition as in E7. Paper split uses the D24-B gain rule; rotations use the D18 rule at 1 seed (descriptive, like S1).

**E18 [must] Effect of training labels and split: P1F and S1U** (clinical fix part 2, stats waterfall b and c)
- P1F: `--split paper --labels overlap --backbone-mode eval`, arms lp, last, last_randinit, lp_randinit; 5 seeds; both heads; both models. About 23 GPU-h.
- S1U: rot0-4 with upstream labels (duplicates in val and test); same 4 arms; seed S_r only; linear; both models. About 14 GPU-h. Seed SD is 0.3-0.9 against a rotation SD of 7-18 on CHB-MIT, so one seed suffices.
- `--plan-only` must confirm that upstream labels on rotation splits keep the duplicates in val and test.
- Rule: a fix "removes the gain" for a contrast if the rule reads a win before the fix and "no difference shown" after. Shapley values are descriptive (finish E13d).

**E19 [must] Native input scaling: BIOT q95 normalisation, CBraMod SSL at /100** (clinical; covers repro 16 "matched SSL/eval")
- New code: `input_norm: q95` (per channel per window, x/(q95|x| + 1e-8)) for BIOT SSL and eval; CBraMod SSL scale 100 instead of 700. Bump code versions, add a unit test, smoke.
- Runs:
  - BIOT, D24-A arms (lp, lp_randinit, last, last_randinit, all) on CHB-MIT, Siena and Siena filtered; 5 rotations × 3 seeds;
  - BIOT P1E arms on the paper split, 5 seeds, both heads;
  - CBraMod last and all only, 3 settings × 5 rotations × 3 seeds.
- About 50 GPU-h.
- Rule (D25-E19):
  - "input scaling changes the BIOT conclusion" if any D24-A BIOT verdict string changes;
  - "frozen BIOT input-limited" if lp(q95) − lp(/100) > 3 in ≥ 4/5 rotations;
  - CBraMod "SSL scale matters" if last(/100) − last(/700) wins by the D18 rule.

### Phase 4: should

**E25 [should] D24-A re-run with validation scores, full logging and both heads** (MLP head ×3 reviewers; clinical validation scores)
- New code: save val scores and the val index in the npz.
- D24-A specs with `--probes linear,mlp_fullft`, eval mode, all 3 seeds re-run, new run tags.
- About 80 GPU-h.
- Rule: the linear cells must reproduce S1M/S3M/S3FM within 0.5 ROC per run (if not, stop and investigate). MLP verdicts use the unchanged D24 rules. Enables validation thresholds in E12 and E20, and ROC- vs bal-acc-selection from the per-epoch history.

**E26-filt [should] Filtered CHB-MIT under the corrected protocol (S1FM)** (repro 16, clinical)
- `--data-variant filt --labels overlap --backbone-mode eval`, rot0-4, D24-A arms, 3 seeds, both models, `--probes linear,mlp_fullft`.
- Plan-only check that `chbmit_filt` carries the rotation and overlap index.
- About 50 GPU-h.
- Rule: D18/D24 unchanged.

**E27 [should] `last_noise` control for the positive BIOT verdicts** (repro 17)
- New code: add the arm `last_noise: {groups: [LAST, head], init: pretrained, ssl_input: noise}` to `configs/adapt.yaml` (the first_noise path already exists).
- Siena and Siena filtered, both models; plus BIOT CHB-MIT, whose +1.9 bootstrap CI excludes 0. 5 rotations × the D24 seeds; eval mode; linear. Pair with the existing last and lp.
- About 10 GPU-h.
- Rule: D19 on last − last_noise.

**E28 [should] Different 4,174-window SSL draws, and the full pool under the fixed probe** (stats D4, clinical subsample seed; repro 21 and stats c)
- New code: an `--ssl-seed` override (`study.load_ssl`, submit_job, sm_entry) and a `data_seed` override.
- (a) Paper split, eval mode, linear; last and last_randinit; 4 extra draws × seeds 42 and 123; both models. Include the E17-free structured set if one is found.
- (b) Rotations, CHB-MIT and Siena: last and last_randinit; 2 extra draws; seed S_r.
- About 26 GPU-h.
- Rule: "D4 robust" if every D24 verdict holds under each draw and BIOT last_randinit on the paper split stays within 2 ROC across draws.

**E29 [should] SSL dose-response** (clinical, repro 21, stats D4c)
- New code: expose the adapt lr and epochs (or reuse `--ssl-n all`).
- Arms last and all; lr {3e-5, 3e-4, 1e-3} × budget {51 steps at N = 4,174; `--ssl-n all`, E = 3}, minus the existing cell; CHB-MIT and Siena rotations; seed S_r; both models; eval mode.
- About 50 GPU-h.
- Rule: exploratory. "More SSL helps" if any cell gives last − lp > 3 in ≥ 4/5 rotations. Report the number of cells tested.

**E30 [should] C2/C3 re-tested** (repro 13, stats D24-C seeds, clinical Siena C2/C3)
- (a) Ours: BIOT pretrained `last` only, C2E/C3E subsets, seeds 123/2021/3407/8888, plus 2 more data_seed draws at seed 42. About 12 GPU-h. CBraMod extra seeds are dropped (range 0.02 at 92.2).
- (b) Siena: BIOT `last` with `--protocol fixed_c` over N896-N4174 and P2/P5/P10 at N2048; LP at batch 128; 5 rotations × 3 seeds; both settings. CBraMod control at seed S_r. Plan-only checks N/P feasibility. About 14 GPU-h.
- (c) Released code: main_diversityN with `compute_N` in {896, 1664, 2048, 4174} and main_diversityP with `compute_P` in {3, 11, 21} at N = 2048; × foundation_dir {unset, set}; × seeds 42 and 123; both models; key 0; released LMDB only. 56 runs, about 65 instance-h.
- Rule: D15 rules on seed means. For (c), bal-acc selection is primary as released and ROC is secondary. Report whether released random-init curves are flat; that would match "invariance" as an artifact.

**E31 [should] Released-code L2-SP sweep** (repro 6a)
- step_up with λ in {1e-4, 1e-2, 1} × foundation_dir {unset, set} × 2 models × seeds 42 and 123 (24 runs).
- Plus main_layer BIOT `spt_unfreeze_layers=all` × the same 3 λ × 2 seeds, foundation_dir unset (6 runs). λ = 0 comes from E4/E5.
- Grep counts of "non-finite SPT loss"; record the kept epoch.
- About 36 instance-h.
- Rule:
  - "λ matters" if |SA(λ) − SA(0)| > 3 ROC in the 2-seed mean;
  - bracket check: unset within [lp_randinit − 3, last_randinit + 3]; set within [lp − 3, last + 3].
- Our-pipeline L2-SP is dropped unless "λ matters".

**E32 [should] Second subject partition** (stats)
- New code: a fold-seed override and run tag S1R.
- lp, lp_randinit, last, last_randinit; linear; eval mode; overlap labels; 3 seeds; 5 rotations; CHB-MIT and Siena; both models.
- About 40 GPU-h.
- Rule: "replicated" if the same verdict string holds and the CI overlaps the original.

**E26 [should, conditional on E15] Strong or standardized probe on GPU** (clinical strong probe, stats nice)
- Only if E15 says BIOT conclusions are probe-limited.
- Add a standardized-linear probe (train-split statistics) or dump eval-mode pooled features for `strong_probe`.
- Arms lp, lp_randinit, last, last_randinit; rotations at S_r and the paper split.
- About 12 GPU-h.
- Rule: recompute the 3 contrasts and D17 with D24 rules.

### Phase 5: nice

**E33a [nice] Add chb12/13/17 and chb02_16+**
- New store windows (label-based `select_bipolar`; report n_present) and 23-subject rotations (seed 20261014).
- D24-A arms, 3 seeds, linear, S1X; also report on the old folds.
- About 45 GPU-h.

**E33b [nice] Siena published split** (test PN13/14/16/17)
- lp, last, lp_randinit; 3 seeds; both settings.
- About 5 GPU-h.

### Last [must, writing]: E34 correct the draft (repro 11, stats CI citation)

Do these after E1, E2, E4 and E10, and before re-sending `notes/author-email-draft.md`:
- §1 "reading and running": true only after E2 and E4.
- §3 "reproduced in a unit test" → the E2 traceback.
- Seeds: the README lists 42/123/2021/3407/8888. Drop or rephrase question 7.
- "Released path" used a 4,174 subsample, while the documented command uses the whole LMDB.
- Add a deviations table for the diversity trainers:
  - bal-acc selection (`trainer_diversityN.py:502`);
  - LP eta_min 1e-6 (`:152`);
  - drop_last (`:173`);
  - budget from len(LMDB) (`main_diversityN.py:316`);
  - P subsets in `compute_P.py`.
- Cite the CIs; abstract and §6 as bounds (BIOT CHB-MIT last − lp +1.9 [CI], not "no gain").
- The email's "your script gives 81,993" becomes the E1 number.

### Dropped or already done

- **Fixed probe on the paper split, both heads**: D24-B / P1E already ran (encoder + eval cell). Only the 2 missing cells remain (E17).
- **Bootstrap CIs**: they exist (`artifacts/tables/d24-bootstrap.md`) and only need citing. The WORKLOG line "CIs agree with every verdict" is wrong for BIOT CHB-MIT, whose CI [+0.1, +3.9] excludes 0.
- **Already built** (2026-11-01): the `--probe-tap` code and full logging. Only re-runs are needed (E17, E25).
- **Already in the records**: test_last, subject fields, displacement, lr_sum and epoch losses. No run needed for E9, E11 or E14.
- **Released SA tap × mode** (strict=False patch): settled by E2(d).
- **Our-pipeline L2-SP arm**: conditional on E31.
- **4,174-key LMDB for foundation_dir unset; CBraMod C2/C3 extra seeds; released spt_epochs {1,5}**: dropped. Random init is invariant to N (range ≤ 0.07), CBraMod is flat at 92.2, and dose-response is covered by E29.
- **Duplicates merged**: MLP head (×3), tap × mode (×3), census (×2), no-op (×2), filtered CHB-MIT (×2), SSL draws (×2), C2/C3 seeds (×3), 4,174 search (×2), strong probe (×3), annotations (×2).

### Totals

| priority | GPU or instance hours |
|---|---|
| must | about 315: E4 36, E5 95, E6 28, E7 30, E17 26, E18 37, E19 50 |
| should | about 435: E25 80, S1FM 50, E27 10, E28 26, E29 50, E30 91, E31 36, E32 40, E26 12 if triggered |
| nice | about 50 |

All released-code hours are provisional until the E4 smoke measures the real data-loading rate.