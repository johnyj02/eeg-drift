#!/usr/bin/env bash
# D25-E1: run the RELEASED CHB-MIT preprocessing (c3n-group/efficient-eeg-adapt @ d056cdf) unmodified.
# Runs on the desktop. Nothing from the released repo is copied; we only execute it from its
# own clone (~/released/eea) in its own env (~/released/eea-env).
#
# Path wiring (the only adaptation): the released scripts hard-code the RELATIVE path
# "$WORK/datasets/physionet.org/files/chbmit/..." (a literal '$WORK', never expanded by os.path).
# We run them with cwd=~/released/run, where '$WORK' is a real directory and
#   ~/released/run/$WORK/datasets/physionet.org/files/chbmit/1.0.0 -> ~/dxdata/chbmit/1.0.0
# is a symlink. All outputs land under ~/released/run/$WORK/datasets/physionet.org/files/chbmit/.
#
#   bash e1_run_released_preprocessing.sh {process1|process2|lmdb}
set -euo pipefail
REL=~/released
PY=$REL/eea-env/bin/python
RUN=$REL/run
CHB="$RUN/\$WORK/datasets/physionet.org/files/chbmit"
mkdir -p "$CHB" "$REL/logs"
[ -L "$CHB/1.0.0" ] || ln -s ~/dxdata/chbmit/1.0.0 "$CHB/1.0.0"
cd "$RUN"
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 PYTHONUNBUFFERED=1
case "$1" in
  # mp.Pool(mp.cpu_count()) inside: taskset bounds the CPUs actually used (<= 48 threads rule)
  process1) exec taskset -c 0-23 "$PY" "$REL/eea/data_preprocessing/CHB-MIT/process1.py" ;;
  process2) exec taskset -c 0-23 "$PY" "$REL/eea/data_preprocessing/CHB-MIT/process2.py" ;;
  # The released script commits one LMDB write transaction per window (82K fsyncs); on the shared
  # disk that ran at ~4 windows/s (attempt 1, killed after 140 files). So the output path is a
  # symlink to tmpfs (fsync = no-op, bytes identical); the finished LMDB is copied back to disk.
  lmdb)
    SHM=/dev/shm/eea_chbmit_preprocessed_30S.lmdb
    [ -e "$CHB/chbmit_preprocessed_30S.lmdb" ] && { echo "remove the old LMDB first" >&2; exit 3; }
    mkdir -p "$SHM" && ln -s "$SHM" "$CHB/chbmit_preprocessed_30S.lmdb"
    taskset -c 24-31 "$PY" "$REL/eea/dataset_pretrain/make_CHBMIT_for_pretraining.py" || exit $?
    rm "$CHB/chbmit_preprocessed_30S.lmdb" && cp -a "$SHM" "$CHB/chbmit_preprocessed_30S.lmdb" && rm -rf "$SHM" ;;
  *) echo "usage: $0 process1|process2|lmdb" >&2; exit 2 ;;
esac
