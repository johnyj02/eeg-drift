#!/usr/bin/env bash
# D25-E2: run the README's documented commands (and the audit's variants) on CPU, in the clone.
# Desktop only. Nothing in the clone is edited: data paths, output_dir, weights_dir_base and
# training.wandb=False are Hydra overrides (the README says to set them); bytecode writes are
# off. The E2(d) second half runs from a /tmp COPY with model_factory.py:29 uncommented.
#
#   bash e2_run_documented.sh <farm_dir> <ssl_lmdb> [jobs-file]
# Writes ~/released/e2/logs/<run>.log and ~/released/e2/status.tsv (run, exit code, seconds).
set -uo pipefail
FARM=$1 SSL=$2
REL=~/released PY=~/released/eea-env/bin/python
E2=$REL/e2 TMPCOPY=/tmp/eea_l29
mkdir -p "$E2/logs" "$E2/out"
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 WANDB_MODE=disabled

if [ ! -d $TMPCOPY ]; then   # E2(d): throwaway copy, one line uncommented, never committed
  cp -r $REL/eea $TMPCOPY && rm -rf $TMPCOPY/.git
  sed -i '29s/^\(\s*\)#backbone.proj_out = nn.Identity()/\1backbone.proj_out = nn.Identity()/' $TMPCOPY/src/model_factory.py
  diff $REL/eea/src/model_factory.py $TMPCOPY/src/model_factory.py > "$E2/l29.diff"
fi

KEY=+method.spt_anchor_l2sp_lambda=0
run() {   # run <name> <clone-root> <entry> <overrides...>
  local name=$1 root=$2 entry=$3; shift 3
  local paths=(output_dir="$E2/out/$name" weights_dir_base="$REL/weights"
               dataset.datasets_dir="$FARM" dataset.pretrain_datasets_dir="$SSL" training.wandb=False)
  local t0=$SECONDS
  ( cd "$root/src" && echo "CMD: cd $root/src && python $entry $* ${paths[*]}" &&
    timeout 5400 taskset -c "$CPUS" "$PY" "$entry" "$@" "${paths[@]}" ) > "$E2/logs/$name.log" 2>&1
  local rc=$?
  printf "%s\t%s\t%s\n" "$name" "$rc" "$((SECONDS - t0))" >> "$E2/status.tsv"
}

C=$REL/eea
case "${3:-all}" in
  all)
    jobs=(
      "a_main_biot_stepup|$C|main.py|model=biot dataset=chbmit method=step_up seed=42"
      "a_main_cbramod_stepup|$C|main.py|model=cbramod dataset=chbmit method=step_up seed=42"
      "b_main_biot_stepup_key|$C|main.py|model=biot dataset=chbmit method=step_up seed=42 $KEY"
      "b_main_cbramod_stepup_key|$C|main.py|model=cbramod dataset=chbmit method=step_up seed=42 $KEY"
      "b_main_biot_fmfreeze|$C|main.py|model=biot dataset=chbmit method=fm_freeze seed=42"
      "b_main_cbramod_fmfreeze|$C|main.py|model=cbramod dataset=chbmit method=fm_freeze seed=42"
      "c_layer_biot|$C|ablation_layer/main_layer.py|model=biot method=step_up"
      "c_layer_cbramod|$C|ablation_layer/main_layer.py|model=cbramod method=step_up"
      "c_layer_biot_key|$C|ablation_layer/main_layer.py|model=biot method=step_up $KEY"
      "c_layer_cbramod_key|$C|ablation_layer/main_layer.py|model=cbramod method=step_up $KEY"
      "c_layer_biot_key_last2|$C|ablation_layer/main_layer.py|model=biot method=step_up method.spt_unfreeze_layers=last2 $KEY"
      "c_layer_cbramod_key_last2|$C|ablation_layer/main_layer.py|model=cbramod method=step_up method.spt_unfreeze_layers=last2 $KEY"
      "c_divN_biot_plusN|$C|ablation_diversityN/main_diversityN.py|model=biot method=step_up +dataset.compute_N=896"
      "c_divN_cbramod_plusN|$C|ablation_diversityN/main_diversityN.py|model=cbramod method=step_up +dataset.compute_N=896"
      "c_divN_biot_plusN_key|$C|ablation_diversityN/main_diversityN.py|model=biot method=step_up +dataset.compute_N=896 $KEY"
      "c_divN_cbramod_plusN_key|$C|ablation_diversityN/main_diversityN.py|model=cbramod method=step_up +dataset.compute_N=896 $KEY"
      "c_divN_biot_N|$C|ablation_diversityN/main_diversityN.py|model=biot method=step_up dataset.compute_N=896"
      "c_divN_cbramod_N|$C|ablation_diversityN/main_diversityN.py|model=cbramod method=step_up dataset.compute_N=896"
      "c_divN_biot_N_key|$C|ablation_diversityN/main_diversityN.py|model=biot method=step_up dataset.compute_N=896 $KEY"
      "c_divN_cbramod_N_key|$C|ablation_diversityN/main_diversityN.py|model=cbramod method=step_up dataset.compute_N=896 $KEY"
      "c_divP_biot|$C|ablation_diversityP/main_diversityP.py|model=biot method=step_up"
      "c_divP_cbramod|$C|ablation_diversityP/main_diversityP.py|model=cbramod method=step_up"
      "c_divP_biot_key|$C|ablation_diversityP/main_diversityP.py|model=biot method=step_up $KEY"
      "c_divP_cbramod_key|$C|ablation_diversityP/main_diversityP.py|model=cbramod method=step_up $KEY"
      "c_divP_biot_NP|$C|ablation_diversityP/main_diversityP.py|model=biot method=step_up dataset.compute_N=896 dataset.compute_P=3"
      "c_divP_cbramod_NP|$C|ablation_diversityP/main_diversityP.py|model=cbramod method=step_up dataset.compute_N=896 dataset.compute_P=3"
      "c_divP_biot_NP_key|$C|ablation_diversityP/main_diversityP.py|model=biot method=step_up dataset.compute_N=896 dataset.compute_P=3 $KEY"
      "c_divP_cbramod_NP_key|$C|ablation_diversityP/main_diversityP.py|model=cbramod method=step_up dataset.compute_N=896 dataset.compute_P=3 $KEY"
      "d_l29_cbramod_stepup_key|$TMPCOPY|main.py|model=cbramod dataset=chbmit method=step_up seed=42 $KEY"
      "d_l29_cbramod_fmfreeze|$TMPCOPY|main.py|model=cbramod dataset=chbmit method=fm_freeze seed=42"
    ) ;;
esac

# at most 6 concurrent runs x 8 threads = 48 threads, on cores 48-95
CPUS=48-95
for j in "${jobs[@]}"; do
  IFS='|' read -r name root entry ov <<< "$j"
  while (( $(jobs -rp | wc -l) >= 6 )); do wait -n; done
  # shellcheck disable=SC2086
  run "$name" "$root" "$entry" $ov &
done
wait
