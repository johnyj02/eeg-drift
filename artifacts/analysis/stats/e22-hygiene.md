# E22: pre-registered vs post-hoc hygiene (D25)

Script: scripts/analysis/stats_d25.py.

## 1. D24-A CBraMod without the S_r seeds

D24-A reuses CBraMod's S_r run (seed [42, 123, 2021, 3407, 8888][r]) from the D23 re-run, which had been read before D24 was written. Same reading as read_d24.py (per-rotation seed mean, D18 rule, D17), in memory, linear head. BIOT ran all 3 seeds inside D24 and is not affected.

| setting | contrast | 3 seeds (D24 as logged) | 2 new seeds (no S_r) | S_r only (D23 re-run) | D24 verdict holds without S_r |
|---|---|---|---|---|---|
| CHB-MIT | last - lp | -0.0 (-0.4, +0.5, +0.0, -0.1, -0.1): no difference shown | -0.0 (-0.5, +0.4, +0.0, -0.0, -0.1): no difference shown | +0.1 (-0.2, +0.7, +0.1, -0.2, -0.1): no difference shown | yes |
| CHB-MIT | last_randinit - last | -4.4 (-3.2, -7.9, -3.7, -1.7, -5.6): second term wins | -5.2 (-3.8, -9.9, -3.0, -1.9, -7.4): second term wins | -2.9 (-2.0, -4.0, -5.1, -1.3, -1.9): no difference shown | yes |
| CHB-MIT | lp - lp_randinit | +5.5 (+5.9, +9.3, +3.1, +4.1, +4.9): first term wins | +5.9 (+5.3, +10.5, +2.7, +5.6, +5.6): first term wins | +4.6 (+7.2, +6.8, +4.1, +1.2, +3.6): first term wins | yes |
| CHB-MIT | last_randinit - lp_randinit | +1.0 (+2.3, +1.8, -0.5, +2.3, -0.8): random features explain it | +0.7 (+1.0, +1.0, -0.3, +3.7, -2.0): random features explain it | +1.7 (+5.0, +3.5, -1.0, -0.3, +1.5): random features explain it | yes |
| Siena | last - lp | +0.3 (-0.5, +0.3, +0.5, +1.0, +0.0): no difference shown | +0.1 (-1.4, +0.3, +0.5, +1.0, -0.0): no difference shown | +0.6 (+1.4, +0.3, +0.5, +1.0, +0.1): no difference shown | yes |
| Siena | last_randinit - last | -7.6 (-6.6, -2.9, -13.4, -2.2, -13.0): second term wins | -7.4 (-7.0, -4.0, -9.0, -3.2, -14.1): second term wins | -8.0 (-5.8, -0.7, -22.3, -0.3, -11.0): second term wins | yes |
| Siena | lp - lp_randinit | +7.0 (+4.8, +0.3, +14.7, -0.0, +15.2): first term wins | +7.1 (+5.3, +0.3, +10.8, +1.2, +18.0): first term wins | +6.7 (+3.7, +0.3, +22.4, -2.6, +9.6): first term wins | yes |
| Siena | last_randinit - lp_randinit | -0.4 (-2.2, -2.3, +1.8, -1.3, +2.2): random features explain it | -0.2 (-3.1, -3.4, +2.4, -1.0, +3.9): random features explain it | -0.6 (-0.6, -0.2, +0.6, -1.8, -1.3): random features explain it | yes |
| Siena filtered | last - lp | +0.1 (+0.3, -0.1, +0.2, +0.2, +0.1): no difference shown | +0.1 (+0.3, -0.1, +0.2, +0.2, +0.1): no difference shown | +0.2 (+0.4, -0.1, +0.2, +0.2, +0.1): no difference shown | yes |
| Siena filtered | last_randinit - last | -10.7 (-15.3, -7.7, -8.3, -5.2, -16.9): second term wins | -11.1 (-14.4, -8.1, -7.9, -6.2, -18.9): second term wins | -9.9 (-17.0, -7.0, -9.2, -3.3, -12.9): second term wins | yes |
| Siena filtered | lp - lp_randinit | +9.4 (+16.2, +6.7, +7.3, +4.8, +12.3): first term wins | +9.6 (+16.3, +6.9, +6.9, +5.6, +12.2): first term wins | +9.2 (+16.2, +6.3, +7.9, +3.1, +12.5): first term wins | yes |
| Siena filtered | last_randinit - lp_randinit | -1.1 (+1.3, -1.2, -0.9, -0.3, -4.5): random features explain it | -1.4 (+2.2, -1.3, -0.8, -0.4, -6.6): random features explain it | -0.5 (-0.4, -0.8, -1.1, +0.0, -0.3): random features explain it | yes |

## 2. Tags: P / P* / H / D

- **P**: design and reading rule fixed before any data of the runs it reads, applied as written.
- **P\***: rule fixed before the runs, with a disclosed deviation: set after related data had been seen (same rotations at fewer seeds or another probe mode, a reused run, a reference value already seen), or its registered output changed.
- **H**: post hoc: the control, rule or analysis was chosen after, or because of, the data it is read on.
- **D**: descriptive: no reading rule (means, per-unit values, counts, references, quoted paper values).

### Abstract numbers

| number or claim | tag | basis |
|---|---|---|
| +36.2 ROC-AUC headline gain (BIOT) | D | paper value, quoted |
| 88.48 ± 0.19 (5 seeds), 88.51 ± 0.53, 88.49 ± 0.40: random-init BIOT last / last2 / all | P* | D12 'supported'; the rule's reference (wave-1 last_randinit, 88.5) was seen before D12 was written; the R1 rows are new screen data |
| 88.67, 88.44, 88.60 (paper Table 2) | D | paper values |
| 51.99 ± 1.30: pretrained BIOT last (5 seeds) | D | wave 1; D5/D6 fix the protocol, no reading rule |
| 92.0 ± 0.0: frozen CBraMod on the paper split, fixed probe | D | D24-B arm mean; the probe fix (D23) is post hoc; the level was previewed by the CPU check (92.6, notes/cbramod-check.md section 4) |
| paper LP 54.14 | D | paper value |
| SSL adaptation adds 0.0 ± 0.0 (CBraMod, paper split) | P | D24-B SA-gain rule, fixed before any P1E run |
| 2 test patients; 206 of 252 test positives are duplicates; 70 of 114 ictal windows labelled negative | D | data counts (from the post-hoc re-scoring work); E1 re-checks them with the released scripts |
| 16 papers in the census | D | compiled by search, not verified by hand (E16) |
| 3 seeds per rotation | P* | D24 raised D18's 1 seed per rotation to 3 after the 1-seed results (deviation 2) |
| BIOT +1.9, CBraMod -0.0, 'no difference shown' (CHB-MIT, corrected protocol) | P* | D18 rule through D24-A; deviations 2, 6, 9 |
| random-init result matches random features (within 3 points) | H | D17, a post-hoc control |
| Siena: BIOT +9.2 / +4.1 'first term wins', not CBraMod | P* | D24-A; deviations 2, 6, 9 |
| C2 and C3 not supported with the fixed probe (1 seed) | P | D24-C applies D15's rules as written |
| 'not consistent with Table 1 as a whole' | P | D13 rule, fixed before the confirmation results |

### Every row of the draft's Tables 1-8 (paper/reproducibility-note-draft.md)

| table | row | tag |
|---|---|---|
| 1 | last block | 88.48 ± 0.19 (5) | P* (random init, D12) / D (pretrained init, wave 1) / paper |
| 1 | last two blocks | 88.51 ± 0.53 (2) | P* (D12 reading; the reference value was seen before the rule) |
| 1 | all blocks | 88.49 ± 0.40 (2) | P* (D12 reading; the reference value was seen before the rule) |
| 2 | CBraMod | linear | P (SA gain and verdict, D24-B) / D (arm means; probe fixed post hoc in D23) |
| 2 | CBraMod | mlp_fullft | P (SA gain and verdict, D24-B) / D (arm means; probe fixed post hoc in D23) |
| 2 | BIOT | linear | P (SA gain and verdict, D24-B) / D (arm means; probe fixed post hoc in D23) |
| 2 | BIOT | mlp_fullft | P (SA gain and verdict, D24-B) / D (arm means; probe fixed post hoc in D23) |
| 3 | 1 | BIOT [2] | D (search census, not verified by hand) |
| 3 | 2 | CBraMod [3] | D (search census, not verified by hand) |
| 3 | 3 | EEGMamba (Wang et al.) | D (search census, not verified by hand) |
| 3 | 4 | CodeBrain (arXiv 2506.09110) | D (search census, not verified by hand) |
| 3 | 5 | CSBrain (arXiv 2506.23075) | D (search census, not verified by hand) |
| 3 | 6 | TFM-Tokenizer (arXiv 2502.16060) | D (search census, not verified by hand) |
| 3 | 7 | EEGDM (arXiv 2508.14086) | D (search census, not verified by hand) |
| 3 | 8 | BrainRVQ (arXiv 2602.16951) | D (search census, not verified by hand) |
| 3 | 9 | DeeperBrain (arXiv 2601.06134) | D (search census, not verified by hand) |
| 3 | 10 | Brain-OF (arXiv 2602.23410) | D (search census, not verified by hand) |
| 3 | 11 | MTDP (arXiv 2603.04478) | D (search census, not verified by hand) |
| 3 | 12 | TRACE (arXiv 2605.11380) | D (search census, not verified by hand) |
| 3 | 13 | CAMEL-CLIP (arXiv 2603.13272) | D (search census, not verified by hand) |
| 3 | 14 | Dani and Liebe [1] | D (search census, not verified by hand) |
| 3 | 15 | MSBraM (arXiv 2607.21402) | D (search census, not verified by hand) |
| 3 | 16 | SCOPE (arXiv 2602.17251) | D (search census, not verified by hand) |
| 4 | BIOT | lp | linear | H (post-hoc re-scoring of saved scores) |
| 4 | BIOT | lp | mlp_fullft | H (post-hoc re-scoring of saved scores) |
| 4 | BIOT | last | linear | H (post-hoc re-scoring of saved scores) |
| 4 | BIOT | last | mlp_fullft | H (post-hoc re-scoring of saved scores) |
| 4 | BIOT | last_randinit | linear | H (post-hoc re-scoring of saved scores) |
| 4 | BIOT | last_randinit | mlp_fullft | H (post-hoc re-scoring of saved scores) |
| 4 | CBraMod | lp | linear | H (post-hoc re-scoring of saved scores) |
| 4 | CBraMod | lp | mlp_fullft | H (post-hoc re-scoring of saved scores) |
| 4 | CBraMod | last | linear | H (post-hoc re-scoring of saved scores) |
| 4 | CBraMod | last | mlp_fullft | H (post-hoc re-scoring of saved scores) |
| 4 | CBraMod | last_randinit | linear | H (post-hoc re-scoring of saved scores) |
| 4 | CBraMod | last_randinit | mlp_fullft | H (post-hoc re-scoring of saved scores) |
| 5 | CHB-MIT | BIOT | lp | D (per-rotation means behind the Table 6 verdicts) |
| 5 | CHB-MIT | BIOT | last | D (per-rotation means behind the Table 6 verdicts) |
| 5 | CHB-MIT | BIOT | all | D (per-rotation means behind the Table 6 verdicts) |
| 5 | CHB-MIT | BIOT | last_randinit | D (per-rotation means behind the Table 6 verdicts) |
| 5 | CHB-MIT | BIOT | lp_randinit | D (per-rotation means behind the Table 6 verdicts) |
| 5 | CHB-MIT | CBraMod | lp | D (per-rotation means behind the Table 6 verdicts) |
| 5 | CHB-MIT | CBraMod | last | D (per-rotation means behind the Table 6 verdicts) |
| 5 | CHB-MIT | CBraMod | all | D (per-rotation means behind the Table 6 verdicts) |
| 5 | CHB-MIT | CBraMod | last_randinit | D (per-rotation means behind the Table 6 verdicts) |
| 5 | CHB-MIT | CBraMod | lp_randinit | D (per-rotation means behind the Table 6 verdicts) |
| 5 | Siena | BIOT | lp | D (per-rotation means behind the Table 6 verdicts) |
| 5 | Siena | BIOT | last | D (per-rotation means behind the Table 6 verdicts) |
| 5 | Siena | BIOT | all | D (per-rotation means behind the Table 6 verdicts) |
| 5 | Siena | BIOT | last_randinit | D (per-rotation means behind the Table 6 verdicts) |
| 5 | Siena | BIOT | lp_randinit | D (per-rotation means behind the Table 6 verdicts) |
| 5 | Siena | CBraMod | lp | D (per-rotation means behind the Table 6 verdicts) |
| 5 | Siena | CBraMod | last | D (per-rotation means behind the Table 6 verdicts) |
| 5 | Siena | CBraMod | all | D (per-rotation means behind the Table 6 verdicts) |
| 5 | Siena | CBraMod | last_randinit | D (per-rotation means behind the Table 6 verdicts) |
| 5 | Siena | CBraMod | lp_randinit | D (per-rotation means behind the Table 6 verdicts) |
| 5 | Siena filtered | BIOT | lp | D (per-rotation means behind the Table 6 verdicts) |
| 5 | Siena filtered | BIOT | last | D (per-rotation means behind the Table 6 verdicts) |
| 5 | Siena filtered | BIOT | all | D (per-rotation means behind the Table 6 verdicts) |
| 5 | Siena filtered | BIOT | last_randinit | D (per-rotation means behind the Table 6 verdicts) |
| 5 | Siena filtered | BIOT | lp_randinit | D (per-rotation means behind the Table 6 verdicts) |
| 5 | Siena filtered | CBraMod | lp | D (per-rotation means behind the Table 6 verdicts) |
| 5 | Siena filtered | CBraMod | last | D (per-rotation means behind the Table 6 verdicts) |
| 5 | Siena filtered | CBraMod | all | D (per-rotation means behind the Table 6 verdicts) |
| 5 | Siena filtered | CBraMod | last_randinit | D (per-rotation means behind the Table 6 verdicts) |
| 5 | Siena filtered | CBraMod | lp_randinit | D (per-rotation means behind the Table 6 verdicts) |
| 6 | CHB-MIT | BIOT | P* (last - lp, last_randinit - last, lp - lp_randinit) / H (D17) / D (all - last) |
| 6 | CHB-MIT | CBraMod | P* (last - lp, last_randinit - last, lp - lp_randinit) / H (D17) / D (all - last) |
| 6 | Siena | BIOT | P* (last - lp, last_randinit - last, lp - lp_randinit) / H (D17) / D (all - last) |
| 6 | Siena | CBraMod | P* (last - lp, last_randinit - last, lp - lp_randinit) / H (D17) / D (all - last) |
| 6 | Siena filtered | BIOT | P* (last - lp, last_randinit - last, lp - lp_randinit) / H (D17) / D (all - last) |
| 6 | Siena filtered | CBraMod | P* (last - lp, last_randinit - last, lp - lp_randinit) / H (D17) / D (all - last) |
| 7 | BIOT pretrained `last` | P (D24-C, D15 rules as written, 1 seed) |
| 7 | BIOT random `last` | D (D15 rules do not cover random init) |
| 7 | CBraMod pretrained `last` | P (D24-C, D15 rules as written, 1 seed) |
| 7 | CBraMod random `last` | D (D15 rules do not cover random init) |
| 7 | C2 | P (D24-C, D15 rules as written, 1 seed) |
| 7 | C3 | P (D24-C, D15 rules as written, 1 seed) |
| 8 | BIOT | lp | mlp_fullft | D (wave-1 means; no reading rule) |
| 8 | BIOT | lp | linear | D (wave-1 means; no reading rule) |
| 8 | BIOT | last | mlp_fullft | D (wave-1 means; no reading rule) |
| 8 | BIOT | last | linear | D (wave-1 means; no reading rule) |
| 8 | BIOT | last_randinit | mlp_fullft | D (wave-1 means; no reading rule) |
| 8 | BIOT | last_randinit | linear | D (wave-1 means; no reading rule) |
| 8 | CBraMod | lp | mlp_fullft | D (wave-1 means; no reading rule) |
| 8 | CBraMod | lp | linear | D (wave-1 means; no reading rule) |
| 8 | CBraMod | last | mlp_fullft | D (wave-1 means; no reading rule) |
| 8 | CBraMod | last | linear | D (wave-1 means; no reading rule) |
| 8 | CBraMod | last_randinit | mlp_fullft | D (wave-1 means; no reading rule) |
| 8 | CBraMod | last_randinit | linear | D (wave-1 means; no reading rule) |

Untagged: the method tables of sections 2.4-2.5 (no results). E10/E11 outputs are H/D.

## 3. Deviations from the registrations

| registered | what was done | consequence |
|---|---|---|
| D24-A: 'also mean +/- SEM over all 15 runs' | the draft reports only the SEM over the 5 rotation means; read_d24.py prints the 15-run SEM labelled 'seeds not independent' and the draft drops it (section 2.6) | statistically right (seeds share a split), but the registered output is not reported; disclose |
| D18: one seed per rotation (S_r, per the D18 amendment) | D24-A uses 3 seeds per rotation [S_r, 1000+r, 2000+r] and its verdicts are primary | decided 2026-10-31 after every 1-seed result (S1, S3, S3F, S1E, S3E, S3FE) had been read; 3 verdicts changed (draft section 6); CBraMod reuses its S_r run, so 1/3 of its D24-A data was seen (part 1) |
| D24-D: bootstrap CIs, to be reported | computed 2026-11-01 (artifacts/tables/d24-bootstrap.md), not cited in the draft; WORKLOG 2026-11-01 says 'CIs agree with every D24 verdict', which is wrong for: CHB-MIT | biot | linear | last - lp (no difference shown, bootstrap [+0.1, +3.9]); Siena filtered | biot | linear | last_randinit - last (second term wins, bootstrap [-19.2, +17.0]); Siena filtered | cbramod | linear | last - lp (no difference shown, bootstrap [+0.0, +0.3]) | cite as pre-registered D24-D with the under-coverage caveat (E10c) |
| D24-D: 'bootstrap CIs over (rotation, seed) runs' | implemented as a two-stage bootstrap (rotations, then seeds inside each drawn rotation) after the D24 review | a refinement; it still under-covers with 5 rotations (E10c coverage check) |
| D24-A: lp - lp_randinit rule 'new, fixed now' | fixed 2026-10-31, after the D23 re-run had shown CBraMod lp above lp_randinit in 14 of 15 rotation-settings | tag P*, not P (draft section 10 discloses it) |
| BIOT probe mode | train mode in S1/S3/S3F; D24 moved BIOT to eval mode after all train-mode BIOT results were seen (registered in D24 before the runs) | disclosed; two BIOT verdicts changed between the two |
| D17 lp_randinit control | added after the D15 data; its rule was fixed before any lp_randinit run | H wherever it appears (the draft says 'post hoc') |
| D23 CBraMod probe | changed after every earlier CBraMod result; the eval-mode amendment came after the CPU check and a local 1-epoch smoke | every fixed-probe CBraMod number rests on a post-hoc protocol change |
| D12 screen rule | its reference value (wave-1 last_randinit 88.5) was seen before the rule; jobs logged as submitted ~18:05 local, rule timestamped 18:10 local | rule precedes every screen result, not the submission: P* |
| D13 confirmation rule | jobs logged as submitted ~14:15 local, rule timestamped 14:20 local | matches its own wording ('BEFORE any result'); not 'before any run' |
| D25: 'BEFORE any D25 run or analysis' | the adopted audit already quotes in-memory statistics by the stats reviewer ('t [-1.0, +4.8]', 'FPR 17%') computed before D25 | E10 and E11 are post hoc; cite script output only |
| E22: 'git init and commit; archived timestamp' | D25 amendment: no git commits | timing rests on file mtimes and the logs; get an archived timestamp before submission |
| E22: SageMaker CreationTime and S3 LastModified via AWS | this run: local file mtimes only (no AWS calls); logged submission times stand in for CreationTime | CreationTime unverified |

## 4. Decision timestamps against result-object times

Object times are the local mtimes under artifacts/s3-results. aws s3 sync sets a downloaded file's mtime to the object's S3 LastModified; the cache was re-synced from S3 on 2026-10-26 (WORKLOG) yet wave-1 files still carry 2026-10-15, so the mtimes are upload times, not download times. Within a job they increase by about one arm's run time. Submission times are the '~HH:MM local' headers of notes/jobs-*.txt (logged by hand; they stand in for SageMaker CreationTime, which was not queried). All times are local clock times. 'first object' includes the test-index file a job writes at its start. Newest local object: 10-31 17:27.

Check: a BEFORE claim must precede the first governed run (logged submission or first object) or result; an AFTER claim must follow the last governed record. Date-only entries can be checked only against the calendar day; a WORKLOG time is used as a secondary check when one exists.

| entry | stated (decisions.md) | claim | objects | submitted (log) | job-name date = UTC date | first object | first record | last record | check |
|---|---|---|---|---|---|---|---|---|---|
| D4-D11 | 2026-10-15 | before any result | 226 | 10-15 01:35 | 20261015 yes | 10-15 01:51 | 10-15 02:21 | 10-15 05:53 | same day: holds only if written before 10-15 02:21 |
| D12 | 2026-10-15 18:10 | BEFORE any result | 128 | 10-15 18:05 | 20261016 yes | 10-15 19:42 | 10-15 20:11 | 10-16 01:19 | consistent (margin +2:01:16) |
| D12 outcome | 2026-10-17 | after the results | 128 | - | - | 10-15 19:42 | 10-15 20:11 | 10-16 01:19 | consistent |
| D13 | 2026-10-19 14:20 | BEFORE any result | 100 | 10-19 14:15 | 20261019 yes | 10-19 14:33 | 10-19 14:49 | 10-19 21:43 | consistent (margin +0:29:38) |
| D13 outcome | 2026-10-19 22:00 | AFTER the results | 100 | - | - | 10-19 14:33 | 10-19 14:49 | 10-19 21:43 | consistent (margin +0:16:19) |
| D15 | 2026-10-20 | BEFORE any run | 60 | 10-20 01:35 | 20261020 yes | 10-20 01:55 | 10-20 02:12 | 10-20 04:56 | same day: holds only if written before 10-20 01:35 |
| D15 outcome | 2026-10-20 13:30 | AFTER the results | 60 | - | - | 10-20 01:55 | 10-20 02:12 | 10-20 04:56 | consistent (margin +8:33:33) |
| D17 | 2026-10-20 | after the D15 data | 60 | - | - | 10-20 01:55 | 10-20 02:12 | 10-20 04:56 | same day: holds only if written after 10-20 04:56; WORKLOG time 13:45 local -> consistent (margin +8:48:33) |
| D17 rule | 2026-10-20 | before any lp_randinit run | 30 | 10-20 14:00 | 20261020 yes | 10-20 14:35 | 10-20 14:35 | 10-20 22:20 | same day: holds only if written before 10-20 14:00; WORKLOG time 13:45 local -> consistent (margin +0:15:00) |
| D18 | 2026-10-20 | BEFORE any run | 190 | 10-20 14:00 | 20261020 yes | 10-20 14:17 | 10-20 14:35 | 10-20 21:10 | same day: holds only if written before 10-20 14:00 |
| D18 amendments | 2026-10-20 14:00 | BEFORE any Step 1 run | 190 | 10-20 14:00 | 20261020 yes | 10-20 14:17 | 10-20 14:35 | 10-20 21:10 | tie with the logged '~' submission (+0:00:00) |
| D19 | 2026-10-20 | BEFORE any run | 30 | 10-20 14:00 | 20261020 yes | 10-20 15:55 | 10-20 15:55 | 10-20 20:32 | same day: holds only if written before 10-20 14:00 |
| D20 | 2026-10-20 13:55 | BEFORE any Step 1 run (after the GPU smoke) | 190 | 10-20 14:00 | 20261020 yes | 10-20 14:17 | 10-20 14:35 | 10-20 21:10 | consistent (margin +0:05:00) |
| D21 | 2026-10-20 | BEFORE any Siena data is windowed or run | 380 | 10-20 19:00 | 20261021 yes | 10-20 19:01 | 10-20 19:03 | 10-20 22:54 | same day: holds only if written before 10-20 19:00; WORKLOG time 14:10 local -> consistent (margin +4:50:00) |
| D22 | 2026-10-20 15:30 | before any Step 1 adaptation arm was read; only rot0 lp/lp_randinit seen | 190 | - | - | 10-20 14:17 | 10-20 14:35 | 10-20 21:10 | 6 records had landed by 10-20 15:30: cbra lp_randinit rot0 (10-20 14:35), biot lp_randinit rot0 (10-20 14:53), cbra lp rot0 (10-20 14:54), biot lp rot0 (10-20 15:08), cbra last rot0 (10-20 15:14), biot last rot0 (10-20 15:24). Adaptation-arm records among them (cbra last rot0 (10-20 15:14), biot last rot0 (10-20 15:24)): that they were not read cannot be confirmed from timestamps |
| D17/D18/D19 outcome | 2026-10-20 22:30 | AFTER the results | 380 | - | - | 10-20 14:17 | 10-20 14:35 | 10-20 21:10 | consistent (margin +1:19:16) |
| D21 robustness outcome | 2026-10-20 22:55 | AFTER the results | 190 | - | - | 10-20 22:16 | 10-20 22:18 | 10-20 22:54 | consistent (margin +0:00:42) |
| D23 | 2026-10-26 | AFTER seeing every earlier CBraMod result | 525 | - | - | 10-15 01:53 | 10-15 02:38 | 10-20 22:54 | consistent |
| D23 amendment | 2026-10-26 | BEFORE any re-run result | 285 | 10-27 00:25 | 20261027 yes | 10-27 00:28 | 10-27 00:30 | 10-27 03:13 | consistent |
| D23 re-run outcome | 2026-10-27 03:20 | AFTER the results | 285 | - | - | 10-27 00:28 | 10-27 00:30 | 10-27 03:13 | consistent (margin +0:06:34) |
| D24 | 2026-10-31 | BEFORE any of these runs | 990 | 10-31 13:40 | 20261031 yes | 10-31 13:43 | 10-31 13:44 | 10-31 17:27 | same day: holds only if written before 10-31 13:40; WORKLOG time 13:15 local -> consistent (margin +0:25:00) |
| D24 outcome | 2026-10-31 17:45 | AFTER the results | 990 | - | - | 10-31 13:43 | 10-31 13:44 | 10-31 17:27 | consistent (margin +0:17:29) |
| D25 | 2026-11-01 | BEFORE any D25 run | 2359 | - | - | 10-15 01:51 | 10-15 02:21 | 10-31 17:27 | consistent: newest local object 10-31 17:27 |

Not verifiable here: SageMaker CreationTime and S3 LastModified as returned by AWS (no AWS call); the time of day of date-only entries; the content of decisions.md at a given time (no version history, no git).
