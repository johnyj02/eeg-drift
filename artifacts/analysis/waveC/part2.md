# D25 wave C, part 2: released code (d056cdf), OOM re-runs and E5 follow-up

Reader: `.venv/bin/python scripts/released/read_released.py --root artifacts/released-root` (2026-11-02),
outputs `released.md` / `released.json` in this directory. The part-1 outputs are kept unchanged as
`released_part1.md` / `released_part1.json`. Rules: notes/decisions.md "D25 wave C reading choices" and
"D25 wave C outcome, part 1" (incl. its reader fix), notes/completeness-audit.md E5, E6, E31 (E4, E7,
E30c unchanged). Values x100, bal / PR / ROC, mean ± SEM over seeds. Every rule at best_* and last_*
separately. Units = paper SEM with a 1-point floor; the E5 thresholds are widened by noise/max(SEM, 1)
with the part-1 noise floor (best 3.19 / 0.26 / 0.71, last 2.63 / 1.02 / 0.29). Harness times are UTC.

## Records

- 92 cells, 267 seed records (part 1: 197; new: 70 = 57 E5 follow-up + 13 OOM re-runs). Expected
  267 = E4 30 + E5 screen 56 + follow-up 19 x 3 + noise 1 + E6 21 + E7 16 + E30c 56 + E31 30. Every
  record: rc 0, DONE present, exactly one released CSV row, smoke False; 0 failed; no duplicates.
- All 197 part-1 records are unchanged byte for byte in the parsed values (best and last).
- Every seed of a cell ran the same command apart from seed/output_dir; all 116 harness attempts
  checked out d056cdf and staged the same split (test 16,964 / train 286,964 / val 23,065).
- env_freeze.txt: torch 2.4.1+cu121 in all 92 cells; cells with two jobs carry two identical freezes.
- Patches as designed: 84 cells none, 6 trainer.py (eval-mode E7 cells), 4 model_factory.py (E7 tenc).
- "non-finite SPT loss": 0 lines in all 267 run.logs. W&B mode tag matches the head in all 64 E5 rows.
  foundation_dir load lines match the cell setting everywhere (no warnings).
- OOM re-runs (e6-b-all 5 seeds; e6fd-b-all, e31layer-b-l1e-4, -l1e-2, -l1 2 seeds each): all DONE,
  rc 0, torch 2.4.1. harness.log holds two attempts: 2026-11-01 20:34-21:13 UTC, every seed exit 1
  after 7-23 s; then 2026-11-02 03:32-04:23 UTC start, all exit 0 (runs 3,755-3,928 s per seed, stage
  679 s vs 127-138 s before). harness.log does not name the instance type; the L40S (ml.g6e.2xlarge)
  attribution comes from notes/RUNLOG.md (jobs anon-DX-rel-1102-{7185,ed0a,80ff,ff98,c74e}).
- E5 follow-up: 19 cells x seeds 2021/3407/8888, all on ml.g5.8xlarge (RUNLOG), as the screen seeds.

Anomalies (no effect on any number):
- The 5 re-run cells' cell.json still names the failed 2026-11-01 job (e.g. anon-DX-rel-1101-7619-
  e6-b-all); the re-run job name is only in RUNLOG. The first attempt's run.log (with the failure
  trace) was overwritten by the re-run, so the OOM cause is not visible in the synced files.
- The E5 follow-up cell.json files list seeds [2021, 3407, 8888] only (rewritten by the follow-up job);
  the reader uses the seed directories, so all 5 seeds are read.
- E6 rows mix GPUs: last1/last2 ran on A10G, all (and its E31-layer lambda cells) on L40S. The released
  code is not bit-reproducible at a fixed seed anyway (part 1), so the GPU effect cannot be separated.
- e6fd-b-all has bal-acc 50.00 / 50.20 (one predicted class at the 0.5 threshold) at both rules.

## E5 "reaches" (5-seed mean D13-consistent, <= 3 widened units on all 3 metrics)

Paper T1: BIOT LP 50.74 ± 0.21 / 1.53 ± 0.03 / 46.93 ± 0.30; BIOT SA 52.71 ± 0.72 / 31.52 ± 1.21 /
83.08 ± 1.89; CBraMod LP 57.87 ± 0.20 / 17.35 ± 0.24 / 54.14 ± 1.39; CBraMod SA 61.37 ± 3.50 / 24.62 ±
2.31 / 83.67 ± 1.36. Widened thresholds (bal / PR / ROC units): BIOT LP 6.19 / 3.26 / 3.71 (best),
5.63 / 4.02 / 3.29 (last); BIOT SA 6.19 / 3.22 / 3.38, 5.63 / 3.84 / 3.15; CBraMod LP 6.19 / 3.26 /
3.51, 5.63 / 4.02 / 3.21; CBraMod SA 3.91 / 3.11 / 3.53, 3.75 / 3.44 / 3.21.

| target | rule | verdict | configuration(s) that reach, or the closest (5-seed gaps, units) |
|---|---|---|---|
| BIOT LP | best | no released configuration reaches | closest e5lp-b-ft0-b256: 50.48 / 1.77 / 52.11, -0.26 / +0.24 / +5.18 (ROC fails) |
| BIOT LP | last | no released configuration reaches | same cell, same values (best = last), ROC +5.18 vs 3.29 |
| BIOT SA | best | reaches | only e4-b-sa (E4 default): 58.14 ± 2.06 / 32.34 ± 3.78 / 86.48 ± 1.89, +5.43 / +0.68 / +1.80; bal passes only through the noise widening (6.19) |
| BIOT SA | last | no released configuration reaches | closest (worst excess) e5sa-b-fd0-ft1-b128-sR: 59.40 / 37.25 / 88.47, +6.69 / +4.73 / +2.85 (bal +1.06 over); fewest failing: fd0-ft0-b128-sR +3.18 / +5.43 / +2.92 and fd0-ft0-b256-sR +3.66 / +4.94 / +2.98 (PR only) |
| CBraMod LP | best | no released configuration reaches | closest e5lp-c-ft0-b256: 57.29 / 18.52 / 64.35, -0.58 / +1.17 / +7.35 (ROC fails) |
| CBraMod LP | last | no released configuration reaches | same cell: 57.09 / 18.38 / 63.93, -0.78 / +1.03 / +7.04 |
| CBraMod SA | best | reaches | fd0-ft0-b128-sR -1.39 / +0.37 / +1.18; fd0-ft0-b256-sR -0.79 / +1.24 / +1.79; fd1-ft0-b128-sR +0.48 / +2.51 / +2.05; fd1-ft1-b128-sR -1.54 / +2.25 / +0.42 |
| CBraMod SA | last | reaches | fd0-ft0-b128-sR -1.46 / +0.74 / +1.29; fd0-ft0-b256-sR -0.97 / +0.97 / +1.46; fd1-ft0-b128-sR +0.48 / +2.51 / +2.05; fd1-ft1-b128-sR -1.99 / +0.86 / -1.94; fd0-ft1-b128-sR -0.36 / +3.20 / +3.18 and fd1-ft1-b128-s4174 -1.58 / +3.04 / -0.24 (these two pass only through the widening) |

Notes (descriptive):
- Every BIOT LP and CBraMod LP configuration fails on ROC only (released LP ROC is above the paper).
  E4 defaults: BIOT LP +1.45 / +0.86 / +5.39; CBraMod LP -0.07 / +17.39 / +21.61 (best).
- BIOT SA at best: e4-b-sa per-seed ROC 88.67 / 78.92 / 88.07 / 88.21 / 88.51 (seed 123 kept probe
  epoch 1, bal 50.0). The three follow-up BIOT SA configurations fail on PR at best (+4.67, +3.59,
  +4.19 vs 3.22). At last e4-b-sa is +6.81 / +4.29 / +2.91 (fails bal and PR).
- CBraMod SA is reached only by non-default configurations; the E4 default e4-c-sa does not reach
  (best -0.76 / +5.10 / +4.63; last +0.34 / +2.78 / +3.45, ROC over 3.21). Robust reach at both rules
  without the widening: e5sa-c-fd0-ft0-b128-sR, 56.52 ± 2.63 / 25.48 ± 1.66 / 85.28 ± 0.74 (best),
  per-seed ROC 85.25 / 86.62 / 82.47 / 86.05 / 86.02.
- The 9 screened-out configurations (8 BIOT SA foundation_dir set, e5lp-c-ft1-b128) count as "does
  not reach" (part-1 reader fix); their 2-seed gaps are 12-25 units.

## E6 (main_layer, foundation_dir unset, 5 seeds; paper 88.67 / 88.44 / 88.60)

| rule | last1 ROC | last2 ROC | all ROC | fingerprint reproduced (all 3 within 2 ROC) |
|---|---|---|---|---|
| best | 86.08 ± 2.36 (-2.59) | 88.45 ± 0.26 (+0.01) | 88.07 ± 0.49 (-0.53) | **False** |
| last | 88.59 ± 0.20 (-0.08) | 88.39 ± 0.24 (-0.05) | 87.91 ± 0.47 (-0.69) | **True** |

- all, per seed (42 / 123 / 2021 / 3407 / 8888): best 88.80 / 89.01 / 86.91 / 86.86 / 88.79; last
  88.03 / 89.00 / 87.01 / 86.68 / 88.81; full row best 60.27 / 35.21 / 88.07, last 59.92 / 35.76 / 87.91.
- The best_* failure is last1 alone: seed 123 kept probe epoch 1 (ROC 76.67, bal 50.0); the other four
  seeds are 88.10-88.69.
- foundation_dir set, all (2 seeds, descriptive): 50.10 ± 0.10 / 27.46 ± 0.07 / 87.37 ± 0.34 at both
  rules (seeds 42 / 123: ROC 87.03 / 87.71, bal 50.00 / 50.20; val-selected epoch 10 = last). ROC is
  1.23 below 88.60, bal-acc at chance. Set last1 52.49, last2 63.45 (best) / 62.52 (last).
- "Entry points agree": **False**, unchanged (seeds 123 and 8888 fail at best only).

## E31-layer (BIOT main_layer all; SA(0) = e6-b-all seeds 42/123; "lambda matters" if |dROC| > 3)

| lambda | rule | ROC seeds 42 / 123 | 2-seed mean | SA(0) | dROC | lambda matters |
|---|---|---|---|---|---|---|
| 1e-4 | best | 88.77 / 89.09 | 88.93 | 88.91 | +0.02 | **False** |
| 1e-4 | last | 88.07 / 89.07 | 88.57 | 88.52 | +0.05 | **False** |
| 1e-2 | best | 88.52 / 89.02 | 88.77 | 88.91 | -0.14 | **False** |
| 1e-2 | last | 88.40 / 89.02 | 88.71 | 88.52 | +0.19 | **False** |
| 1 | best | 88.89 / 90.07 | 89.48 | 88.91 | +0.57 | **False** |
| 1 | last | 88.75 / 90.04 | 89.40 | 88.52 | +0.88 | **False** |

- L2-SP was active: logs say "Using L2-SP regularization with lambda=X" (lambda 0: "disabled"); final
  SPT loss (42 / 123) 0.0022 / 0.0023 (1e-4), 0.016 / 0.017 (1e-2), 0.245 / 0.275 (1) vs 0.0015 / 0.0016
  (0).
- Non-finite SPT loss: 0 in all 13 re-run seeds. Kept SPT epoch: 3 of 3 in every re-run seed (each SPT
  epoch saved a new best). Val-selected probe epoch: e6-b-all 3 / 8 / 6 / 8 / 7; e6fd-b-all 10 / 10;
  lambda 1e-4 3 / 9; 1e-2 6 / 10; 1 6 / 7.
- E31 overall: "lambda matters" fires in 8 of 30 readings (the part-1 8 of 24, plus 0 of 6 here). The
  bracket check is still not coded (needs lp_randinit).

## Changes to part-1 verdicts

None. The 48 verdicts resolved in part 1 are identical; the 15 pending ones are resolved above (E5 x 7,
E6 fingerprint x 2, E31-layer x 6). Numbers that moved without a verdict change: E7 "54.14 reachable"
closest cell (proj_out tap, train mode, full_ft False = e5lp-c-ft0-b256) is now 5 seeds: ROC 64.35
(+7.35 units, best) / 63.93 (+7.04, last), was 64.36 / 64.15 (+7.4 / +7.2) at 2 seeds.

## Reader fix (2026-11-02, AFTER the follow-up results were seen; no rule change)

The target-level E5 verdict tested `x is False`, but per-configuration results computed from 5 seeds
were numpy booleans, which fail that identity test. With every configuration resolved False, the
reader printed "pending (configurations without 5 seeds)" for BIOT LP, CBraMod LP (both rules) and
BIOT SA at last. Fix: the 5-seed result is cast to a Python bool (the E4 "released = ours" value too, so
released.json stores true/false instead of 1.0). The per-configuration True/False column was correct
before and after. Also added, descriptive only: the 5-seed gaps beside each "reaches" entry and the
closest configuration per target (smallest worst-metric excess over the widened threshold).
