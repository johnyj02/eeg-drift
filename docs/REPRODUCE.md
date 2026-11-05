# Reproducing the paper

Three levels, from cheapest to most expensive:

1. **CPU, from the saved records (seconds).** Every number in the main tables is recomputed from the result
   records (`artifacts/s3-results/<unit>/results/*.json`, one per run) and the released-code run outputs
   (`artifacts/released-root/`), and compared with the LaTeX.
2. **CPU, from per-window scores, window indices or window stores.** A few readings re-score test windows;
   they need files that are not in the records (listed below).
3. **GPU, retraining.** Every run itself: SSL adaptation, then the probe. Needed to re-derive any number
   from the raw EEG.

Commands run from the project root (or the supplement folder, which has the same layout), Python 3.12,
`pip install -e ".[dev,preprocess]"` (see the supplement README for versions).

## 1. The main tables from the saved records (CPU, one command)

```bash
.venv/bin/python scripts/make_main_tables.py
```

About 10 s on a laptop CPU. It reads the records once, recomputes the cells of five tables and compares
each with the cell of the same table in `paper/tmlr/sections/*.tex` (found by its label, so tables may move
between files), printing PASS / FAIL / SKIP per cell:

| table | cells | what |
|---|---|---|
| `tab:original` | 22 | DL Table 1 against the released code (E4) and our runs: the headline comparison on DL's split |
| `tab:d24a` | 32 | revised-protocol contrasts (D24-A: mean, 95% t-interval over rotation means, rule) and DL's split (D24-B) |
| `tab:p1e` | 30 | DL's split: arm levels and SA gain for the linear, shipped MLP and standardized heads |
| `tab:robust` | 53 | the SSL adaptation gain under every control; rows matched by the id in their label, e.g. `(E25)` (the `--` cells are not run and not counted) |
| `tab:artifacts` | 15 | the record-derived values of the release-issue table (our runs and the released-code runs) |

Current result (2026-11-04 paper sources): 151 PASS, 0 FAIL, 1 SKIP. The SKIP is the PR-AUC 37.4 ± 1.2 in
`tab:artifacts` (row 3b), a re-scoring of per-window test scores with the revised labels (level 2, below),
not a value stored in a record. DL's own values (DL column, DL LP / SA) are quoted from DL's paper and not
checked.

Outputs: `artifacts/tables/main/main_tables.md` (ours next to the paper, per cell) and `main_tables.json`
(the same cells with their numbers: per-unit values, means, intervals, rule outputs). Exit status 1 on any
FAIL. Without the paper sources (`--tex <dir>` missing, e.g. in the supplement) the cells are written as
UNCHECKED; a table whose label is no longer in the paper is reported UNCHECKED too.

The rules are the logged ones, reused from the reading scripts: `read_step1.paired` (F / S / N),
`read_step1.d17` (R), `read_step1.d19` (P / G / unclear), `e29_dose_response.fires`; ROC is read through
`read_d24.load`, which refuses any record that is not probe v4 in eval mode, duplicates, and tag sets that
mix evaluation data.

The other reading scripts (D24-A/B per-arm tables, bootstrap intervals, E17-E33, D26, D27, figures) are
listed with their command lines in the supplement README ("Reading scripts"); all are CPU-only and
deterministic.

## 2. Readings that need more than the records (CPU)

| reading | needs | script |
|---|---|---|
| PR-AUC re-scored with revised labels / grid-only windows (`tab:artifacts` 3b, 37.4) | per-window test scores (`*.npz`, 1.6 GB, not in the supplement) and the window indices | `scripts/posthoc_test.py` |
| E13 waterfall, E11 subject-level, E12 event-level | `*.npz` scores, window indices | `scripts/analysis/decompose.py`, `subject_level.py`, `event_level.py` |
| E18 labels/split (the +30.9 itself is in the records) | window indices (`artifacts/window-index/`, restore with the loop in the supplement README) | `scripts/analysis/e18_labels_split.py` |
| E10 variance components, part (h) | `*.npz` scores | `scripts/analysis/stats_d25.py` |
| F7 (CBraMod singular values) | CBraMod checkpoint and the pilot store | `scripts/figures.py` |

## 3. What needs retraining (GPU)

Every number in the paper comes from a run; re-deriving it from the EEG means re-running that run.
The job specifications are in `scripts/submit_*.sh` (our pipeline) and `scripts/released/` (the released
code at `d056cdf`, cloned inside each job). Each job used one NVIDIA A10G (24 GB) with 128 GB host RAM
(`ml.g5.8xlarge`); billable seconds per job are in `notes/RUNLOG.md`.

| finding | paper (labels) | runs to repeat | specs |
|---|---|---|---|
| Headline: on DL's split, from pretrained weights with the encoder-level probe, the SA gain is −0.6 ± 1.2 (BIOT) and +0.01 ± 0.01 (CBraMod) | `sec:p1e`, `tab:original` last column, `tab:p1e`, `tab:d24a` bottom | P1E (lp, last; plus last_randinit, lp_randinit for every row), P1Z (standardized head) | `scripts/reproduce_headline.sh`; `submit_d24.sh` part B; `submit_d25.sh` ONLY=E26 |
| Revised protocol (D24-A): five rotations, three settings, 3 seeds | `sec:d24a`, `tab:d24a`, `fig:forest` | S1E/S3E/S3FE (D23) and S1M/S3M/S3FM | `submit_s1.sh`, `submit_d24.sh` part A |
| Issue 1 (SSL adapts a random encoder): released-code cells and the fingerprint | `sec:a1`, `tab:original` released-code column, `tab:artifacts` row 1, `app-b-released.tex` E4-E6 | released-code E4, E5, E6 | `scripts/released/` (README there) |
| Issue 2 (CBraMod probe reads `proj_out` with dropout on) | `sec:a2`, `tab:original` released-code-probe columns, `tab:artifacts` row 2 | released-code E7; our E17 cells (P1PE, P1ET) and the wave-1 runs (released-code probe) | `scripts/released/`; `submit_d25.sh` ONLY=E17; wave 1 = the arms jobs of 2026-10-15 in `notes/RUNLOG.md`, run with probe code version 2 |
| Issue 3 (two-patient split, start/end labels) | `sec:a3`, `tab:artifacts` row 3 | P1E, D24-A, P1F | as above; `submit_d25.sh` ONLY=E18 |
| Controls (noise inputs, standardized head, input scaling, SSL draws, second partition, dose) | `sec:controls`, `tab:robust`, `app-c-robust.tex` | E19, E25-E29, E32, D26, D27 tags | `submit_d25.sh` ONLY=E19 / E25 / E26 / E27 / E28 / E29 / E32 / D26 / D27 / D27X |
| C2/C3 (SSL data size and diversity) | `sec:c2c3`, `tab:c2c3` | C2E/C3E and E30 re-tests | `submit_d24.sh` part C; `submit_d25.sh` ONLY=E30 |

Code evidence for the issues (file and line references in `sec:a1`, `sec:a2`) needs no run: read the release at
`d056cdf`; `tests/test_upstream_audit.py` and `tests/test_released_differential.py` check it against a clone.

Not yet run (protocols fixed in `notes/decisions.md`, results pending in the paper):
- **D28** (probe convergence): GPU for the adaptation step and one feature pass per (arm, seed); the
  16-configuration probe search then runs on the cached features.
- **D29** (C2/C3 noise and standardized-probe controls on Siena at the fixed-compute budget): GPU runs.
  Its PR-AUC readings are CPU-only from the existing records (`avg_precision` and `pr_auc_trapz` are stored
  in every record); that reading script is not written yet.

### The headline comparison, one command

```bash
zsh scripts/reproduce_headline.sh sagemaker                        # prints the 4 job specs, submits nothing
zsh scripts/reproduce_headline.sh sagemaker --i-have-confirmation  # submits them (billable)
zsh scripts/reproduce_headline.sh local                            # the same runs on a local GPU
zsh scripts/reproduce_headline.sh read artifacts/local             # read the new records
```

It runs DL's split with the start/end labels and DL's SSL protocol, BIOT and CBraMod, arms `lp` and `last`
from the pretrained weights, the encoder-level probe with the backbone in eval mode, 5 seeds
(42, 123, 2021, 3407, 8888), linear and shipped MLP heads: the runs behind the encoder-level column of `tab:original` and the SA gains in `tab:p1e`.
`ARMS="lp last last_randinit lp_randinit"` adds the random-init columns. The `read` step writes
`artifacts/tables/main/headline-<dir>.md` (scripts/read_d24.py `--paper`: arm levels, SA gain per seed,
D24-B rule) and prints, per cell, the largest difference from the saved P1E records.

- **SageMaker**: one job per (model, arm), with fresh checkpoint prefixes (`rp1e*`), so nothing resumes
  from the original runs. The original jobs took 9,250 to 11,520 billable seconds each (notes/RUNLOG.md,
  P1E rows): lp + last for both models about 42,000 s (11.7 GPU-hours, about $36 at list price), all four
  arms about 84,000 s (23 GPU-hours, about $71). Fetch the records with
  `aws s3 sync <BUCKET>/checkpoints/ artifacts/repro-headline --exclude '*' --include 'arms-*-chb-rp1e*/results/*.json'`
  (`<BUCKET>` = `BUCKET` in `scripts/jobspec.py`), then `read artifacts/repro-headline`. The jobs read the
  stores from `<BUCKET>/lmdb/chbmit/`; running in another account means changing `BUCKET` and
  `configs/sm_job.yaml`.
- **Local**: `sm_entry.py` outside SageMaker, one process per model, records in `artifacts/local/results/`
  (it resumes from there). Needs a CUDA GPU with 24 GB, at least 64 GB of host RAM (the CHB-MIT evaluation
  store is about 40 GB as float32 and is held in memory), the two checkpoints in `weights/` and the stores
  in `$DATA` (default `data/lmdb/chbmit`). Expect about the same 11.7 hours on one A10G.
- The pipeline was bit-reproducible on the same hardware and container (D27 re-ran lp/last under new
  tags with identical ROC); on other GPUs or library versions expect small differences, so compare the
  rule outputs and the means at the paper's precision.

## Rebuilding the data

1. Download from PhysioNet: CHB-MIT Scalp EEG 1.0.0 (ODC-By 1.0) and, for the Siena results, Siena Scalp
   EEG 1.0.0 (CC BY 4.0); about 64 GB of EDF for both.
2. Pretrained checkpoints into `weights/` (URLs and SHA-256 in the supplement README and `configs/models.yaml`).
3. Window stores (LMDB; about 172 GB for every variant; the headline needs only `chbmit_ssl30`, about
   32 GB, and `chbmit_eval10`, about 40 GB). Both scripts verify every EDF against PhysioNet's
   `SHA256SUMS.txt` first:

```bash
python scripts/preprocess_chbmit.py --root <physionet>/chbmit/1.0.0 --out data/lmdb/chbmit --workers 32
python scripts/preprocess_chbmit.py --root <physionet>/chbmit/1.0.0 --out data/lmdb/chbmit_filt --eval-only --filtered
python scripts/preprocess_chbmit.py --root <physionet>/chbmit/1.0.0 --out data/lmdb/chbmit_x --eval-only --extended
python scripts/preprocess_siena.py --root <physionet>/siena-scalp-eeg/1.0.0 --out data/lmdb --workers 8
```

A run reads the stores of one directory, `$SM_CHANNEL_DATA` (SageMaker: the `data` channel,
`lmdb/<dataset>/` or `lmdb/<dataset>_filt/`; locally `$DATA` in `reproduce_headline.sh`). The filtered and
extended directories also need the dataset's SSL store (link it in). `configs/data.yaml` names the stores
each dataset uses. Build the stores on a machine with the disk for them, not on a laptop.
