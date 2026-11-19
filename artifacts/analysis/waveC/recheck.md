# Wave C adversarial re-check (2026-11-01)

Independent code: /tmp/recheck_waveC/recheck.py. It reads the CSVs directly, imports only
coverage.d13/T1/T2, and needs DONE + rc 0 per seed. The current read_released.py, run to a temp
dir, reproduces released.md byte for byte.

| # | claim | verdict | recomputed |
|---|---|---|---|
| 1 | E4 5-seed means; released = ours (8/8 True); random features explain SA | CONFIRMED | all means/SEM equal to 2 dp; BIOT SA best diff 2.00 vs thr 3.80; abs(SA-LPrand) BIOT 2.05/0.12, CBraMod 0.52/1.40 |
| 2 | E5 floor, 19 in / 9 out, BIOT SA best reaches | CONFIRMED | floor best 3.19/0.26/0.71, last 2.63/1.02/0.29; out = e5lp-c-ft1-b128 + 8 BIOT fd1 SA; e4-b-sa best gaps 5.43/0.68/1.80 vs widened 6.19/3.22/3.38 (k=3), unwidened k=2 |
| 3 | E6 agree False (123, 8888 at best only); last1/last2 ROC | CONFIRMED | s123 best PR 0.48>0.26, ROC 2.25>0.71; s8888 best PR 1.22>0.26; every seed passes at last; last1 86.08±2.36 / 88.59±0.20, last2 88.45±0.26 / 88.39±0.24 |
| 4 | E7 54.14 not reachable (best, last); tap/mode table; mode explains at ft1/last | CONFIRMED | closest config is tproj/mtrain/ft0 (e5lp-c-ft0-b256), ROC +7.4/+7.2 units vs widened 3.51/3.21; ft1 last tap +0.60, mode +7.94 |
| 5 | E31 8/24 fire; BIOT fd0 best firings come from lambda-0 seed 123 = epoch 1 | CONFIRMED | per-seed dROC at seed 42 +0.28/+0.14/+0.13, at seed 123 +11.41/+10.97/+10.25; e4-b-sa s123 best epoch 1 (test ROC 78.92, bal 50.0; last 89.24); the lambda cells' s123 best epochs are 8/8/5 |
| 6 | E30c random-init curves flat on ROC | CONFIRMED (ROC) | ROC ranges best/last: BIOT N 0.97/0.08, P 1.46/0.10; CBraMod N 0.23/0.84, P 0.86/1.92 |
| 7 | reader edits change no numbers or rules | CONFIRMED | 8 Edit calls in the transcript: warnings, E6/E31 PENDING, E7 split by epoch rule only |

Caveats (no verdict changes today):
- E5 aggregation: a configuration that fails the screen keeps rc=None, so it counts as "pending"
  instead of "not reaching". "No released configuration reaches" can then never fire for groups
  that hold a screened-out configuration: CBraMod LP (e5lp-c-ft1-b128) and BIOT SA (8 fd1 cells).
  This will matter when the E5 follow-up is read.
- E5 "BIOT SA reaches at best" depends on a single CBraMod same-seed bal delta (3.19). The margin
  is 0.76 units.
- E6 fingerprint at best is already False: last1 86.08 is 2.59 from 88.67, so e6-b-all cannot
  change it. The reader prints PENDING.
- E30c on bal-acc, the released selection metric, is not flat at best: BIOT N 3.63, BIOT P 9.04,
  CBraMod P 4.98 (CBraMod P at last: 3.96). Val bal-acc ties at 0.5 in the diversity trainer, so
  epoch 1 is often kept. The pretrained (fd1) curves are flat on ROC too (max range 2.91).
- WORKLOG 20:15 says "closest is +21 ROC units" for E7. The closest E7 configuration is
  tproj/mtrain/ft0 at +7.2-7.4. Among the new E7 runs the closest is +20.4.

# Wave C part 2 adversarial re-check (2026-11-02)

Independent code: /tmp/recheck_waveC2/{load,rules}.py. It reads status.json, DONE, the CSVs and the
run.logs directly; paper T1/T2 re-typed from artifacts/paper/paper.txt (l.167-175, 403-412). The
current read_released.py, run to a temp dir, reproduces released.md and released.json byte for byte.

| claim | verdict | recomputed |
|---|---|---|
| 92 cells / 267 records, 70 new (57 + 13), rc 0, DONE, 1 CSV row, no smoke, no duplicates; 197 part-1 records unchanged | CONFIRMED | status seed = dir = CSV seed everywhere; per-cell commands identical apart from seed/output_dir; 19 follow-up cells have exactly 2021/3407/8888 new |
| torch 2.4.1+cu121 in 92 cells; 116 attempts, d056cdf, same split; reruns 2 attempts, first exit 1 after 7-23 s, second exit 0; GPU not in harness.log | CONFIRMED | double freezes identical; L40S only from RUNLOG (g6e.2xlarge rows 696-708); last1/last2 on g5.8xlarge |
| noise floor best 3.19/0.26/0.71, last 2.63/1.02/0.29; 19 in / 9 out | CONFIRMED | |
| E5 BIOT LP none (best, last); BIOT SA reaches at best (e4-b-sa only), none at last; CBraMod LP none; CBraMod SA reaches (4 configs best, 6 last), e4-c-sa does not | CONFIRMED | all quoted means, SEMs and gaps match to 2 dp except below |
| "every LP configuration fails on ROC only" | REFUTED | e5lp-b-ft1-b128 also fails PR (+5.38 vs 3.26 best / 4.02 last); e4-c-lp fails PR (+17.39 / +14.67); verdicts unchanged |
| "the three BIOT SA follow-up configurations fail on PR at best" | CONFIRMED, incomplete | fd0-ft0-b256-sR also fails bal (+6.53 vs 6.19) |
| CBraMod SA fd1-ft0-b128-sR bal +0.48 | typo | +0.47 (0.4746), both rules |
| E6 fingerprint best False (last1 86.08, -2.59; s123 epoch 1, ROC 76.67), last True (88.59/88.39/87.91); fd all 50.10/27.46/87.37, epoch 10; agree False (s123, s8888 at best) | CONFIRMED | |
| E31-layer: dROC +0.02/+0.05, -0.14/+0.19, +0.57/+0.88, all False; SA(0) 88.91/88.52; L2-SP lines; 0 non-finite; SPT kept 3 of 3; E31 8 of 30 | CONFIRMED | final SPT losses and probe epochs match |
| E7 reachable False; closest 64.35 (+7.35) / 63.93 (+7.04) at 5 seeds | CONFIRMED | 2-seed 64.36 / 64.15 |
| reader fix (numpy bool vs "is False") changes no rule; 5 targets would read pending | CONFIRMED | |
| tests 78 passed, 2 skipped; read_released.py ruff-clean; gate red on other files | CONFIRMED | at 05:09 local the red file is scripts/analysis/d27_cd.py (1 E501), still not the reader's |

Not in the report:
- E6 fingerprint at best is False by 0.59 ROC (2.59 vs 2.00). T2 has no SEM, so a unit is 1 point;
  if the "2 ROC" tolerance were read as a unit threshold and widened by the ROC noise floor (0.71),
  the threshold would be 2.71 and best would read True. Literal reading: the tolerance is in ROC
  points, not units, so False stands (as recorded in part 1).
- The "W&B mode tag" check is a proxy: training.wandb=False, so no tag is logged; the check is
  full_ft vs the printed classifier head (ELU = MLP). It holds in all 133 E4/E5 seed logs.
