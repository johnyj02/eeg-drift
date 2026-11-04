# Released-code harness (D25 wave C: E4, E5, E6, E7, E30c, E31)

This harness runs the released code, c3n-group/efficient-eeg-adapt at d056cdf (GPL). The code is
cloned inside the container at job start and is never vendored into this repo. Our files:

- `sm_released_entry.py` is the SageMaker entry point (stdlib only). It runs one grid cell: clone
  and verify the checkout, build a venv from the E1 freeze, unpack the shards, create the `$WORK`
  symlinks, apply the E7 sed patches if the cell lists them, and run the cell's seeds one after
  another. Logs, CSVs, prediction `.npy` files and the Hydra config go to `/opt/ml/checkpoints` and
  then to `/opt/ml/model`.
- `submit_released.py` turns `configs/released_grid.yaml` into one job per cell. It supports
  `--plan-only`, `--smoke`, `--stage DIR` (write job bundles only), `--only REGEX`, `--seeds` and
  the `--i-have-confirmation` guard.
- `read_released.py` reads the outputs and applies the D25-E4/E5/E6/E7 rules (plus the E31 λ rule).
  It writes `artifacts/analysis/waveC/released.{md,json}`.

## 1. Stage the data to S3 (orchestrator only, from the desktop)

The staged shards live on the desktop in `~/released/stage/`: 18 processed_seg tars, the released
LMDB tar, the 4,174-key LMDB tar (`chbmit_ssl_4174.lmdb.tar`) and `MANIFEST.tsv` (20 rows). The
total is 140.7 GB (copy: `artifacts/analysis/waveC/stage_MANIFEST.tsv`). Credentials go over stdin only, as for the Siena stores (WORKLOG 2026-10-20).
They are never written to the desktop disk and never appear on a command line. Run this on the Mac:

```bash
<CREDENTIAL_REFRESH_CMD>
aws configure export-credentials --profile <AWS_PROFILE> --format env-no-export \
  | ssh <HOST> \
      'set -a; . /dev/stdin; set +a; cd ~/released/stage && aws s3 cp . s3://<BUCKET>/<PREFIX>/released/chbmit-d056cdf/ --recursive --exclude "*" --include "*.tar" --include MANIFEST.tsv --region us-east-1 --only-show-errors'
```

To verify, list the prefix the same way and compare object count and sizes with `MANIFEST.tsv`
(expect 21 objects: 20 tars plus the manifest):

```bash
aws configure export-credentials --profile <AWS_PROFILE> --format env-no-export \
  | ssh <HOST> \
      'set -a; . /dev/stdin; set +a; aws s3 ls s3://<BUCKET>/<PREFIX>/released/chbmit-d056cdf/ --region us-east-1'
```

The entry script checks every shard's size against `MANIFEST.tsv` and each split's pickle count
after unpacking. sha256 values are recorded in the manifest. They were verified on the desktop
(VERIFY.tsv) but are not re-hashed in the job.

## 2. Plan, smoke, submit (from the Mac)

```bash
.venv/bin/python scripts/released/submit_released.py --plan-only                 # 92 jobs, 210 runs
.venv/bin/python scripts/released/submit_released.py --only '^e4-' --smoke --i-have-confirmation
.venv/bin/python scripts/released/submit_released.py --only '^e4-' --i-have-confirmation
# E5 follow-up (separate, later): 3 more seeds for each configuration that passes the screen
.venv/bin/python scripts/released/submit_released.py --only '^<cell>$' --seeds 2021,3407,8888 --i-have-confirmation
```

Each cell keeps the same checkpoint prefix across submissions
(`.../released/checkpoints/<cell>/`), so a resubmission skips seeds already marked `DONE`. A job
bundle is about 34 MB and is staged in a temp dir that is deleted after submission.

## 3. Read

Download `.../released/checkpoints/` (or the model.tar.gz files) to the desktop, then:

```bash
.venv/bin/python scripts/released/read_released.py --root <dir with <cell>/s<seed>/>
```

## Desktop CPU test (no SageMaker)

```bash
python scripts/released/submit_released.py --smoke --stage ~/released/waveC/bundles --only '<regex>'
python ~/released/waveC/bundles/<cell>/sm_released_entry.py --cell ~/released/waveC/bundles/<cell>/cell.json \
    --data ~/released/stage --work ~/released/waveC/work-<cell> --ckpt ~/released/waveC/ckpt \
    --model-dir ~/released/waveC/model --smoke 1
```
