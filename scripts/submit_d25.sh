#!/usr/bin/env zsh
# D25 our-pipeline GPU items (notes/decisions.md D25 + "D25 parameters fixed").
#   zsh scripts/submit_d25.sh --plan-only | --i-have-confirmation
#   START=n resumes after a partial submission; ONLY=E19 runs one item.
set -euo pipefail
cd "${0:A:h}/.."
N=0
# Shared account: keep at most CAP (default 120) of OUR jobs in progress, so others keep slots.
ours() { local n
  n=$(aws sagemaker list-training-jobs --profile <AWS_PROFILE> --region us-east-1 --name-contains anon-DX- \
        --status-equals InProgress --creation-time-after 2026-10-01 --page-size 100 --query 'length(TrainingJobSummaries)' \
        --output text 2>/dev/null) || { echo 999; return; }        # unknown count = assume full
  echo "$n" | awk '{s+=$1} END {print s+0}'; }                     # one count per result page
refresh() { <CREDENTIAL_REFRESH_CMD> >/dev/null 2>&1; }
# On ResourceLimitExceeded (account quota 144 ml.g5.8xlarge) wait and retry; re-check the cap first.
sub() { N=$((N + 1)); (( N < ${START:-1} )) && return 0
  local out c
  while true; do
    if [[ " $* $EXTRA " != *" --plan-only "* ]]; then
      refresh
      while c=$(ours); (( c >= ${CAP:-120} )); do
        echo "[$(date +%H:%M)] spec $N: $c of our jobs running (cap ${CAP:-120}), wait 10 min" >&2
        sleep 600; refresh
      done
    fi
    out=$(.venv/bin/python scripts/submit_job.py --stage arms "$@" $EXTRA 2>&1) && { print -r -- "$out"; return 0; }
    if [[ $out == *ResourceLimitExceeded* ]]; then
      echo "[$(date +%H:%M)] spec $N: quota full, retry in 10 min" >&2; sleep 600; continue
    fi
    print -r -- "$out"; return 1
  done; }
want() { [[ -z ${ONLY:-} || ${ONLY} == $1 ]]; }
EXTRA="${(j: :)@}"
BASE=(42 123 2021 3407 8888)
A5=lp,lp_randinit,last,last_randinit,all
A4=lp,last,last_randinit,lp_randinit
s3() { echo "${BASE[$1+1]},$((1000 + $1)),$((2000 + $1))"; }   # D24 seeds of rotation r
typeset -A DS=(chbmit chbmit siena siena siena_filt siena)
typeset -A VAR=(chbmit "" siena "" siena_filt "--data-variant filt")
typeset -A T1=(chbmit S1 siena S3 siena_filt S3F)
typeset -A SH=(chbmit 1 siena 3 siena_filt f)          # short unit tags
typeset -A AS=(lp lp last la last_randinit lr lp_randinit pr)
COR=(--labels overlap --probes linear --backbone-mode eval)

if want E17; then   # CBraMod tap x mode cells
  for A in lp last last_randinit; do
    sub --model cbramod --dataset chbmit --arms $A --seeds ${(j:,:)BASE} --split paper --backbone-mode eval --probe-tap proj_out --run-tag P1PE --tag pp${AS[$A]}
    sub --model cbramod --dataset chbmit --arms $A --seeds ${(j:,:)BASE} --split paper --backbone-mode train --run-tag P1ET --tag pt${AS[$A]}
  done
  for R in 0 1 2 3 4; do
    sub --model cbramod --dataset chbmit --arms lp,last --seeds ${BASE[R+1]} --split rot$R --labels overlap --probes linear --backbone-mode eval --probe-tap proj_out --run-tag S1PE --tag spe
    sub --model cbramod --dataset chbmit --arms lp,last --seeds ${BASE[R+1]} --split rot$R --labels overlap --probes linear --backbone-mode train --run-tag S1ET --tag set
  done
fi
if want E18; then   # training labels and split
  for M in biot cbramod; do for A in lp last last_randinit lp_randinit; do
    sub --model $M --dataset chbmit --arms $A --seeds ${(j:,:)BASE} --split paper --labels overlap --backbone-mode eval --run-tag P1F --tag pf${AS[$A]}
  done; done
  for M in biot cbramod; do for R in 0 1 2 3 4; do
    sub --model $M --dataset chbmit --arms $A4 --seeds ${BASE[R+1]} --split rot$R --probes linear --backbone-mode eval --run-tag S1U --tag s1u
  done; done
fi
if want E19; then   # native input scaling
  for D in chbmit siena siena_filt; do for R in 0 1 2 3 4; do
    sub --model biot --dataset ${DS[$D]} ${=VAR[$D]} --arms $A5 --seeds $(s3 $R) --split rot$R $COR --set input_norm=q95 --run-tag ${T1[$D]}Q --tag q${SH[$D]}
    sub --model cbramod --dataset ${DS[$D]} ${=VAR[$D]} --arms last,all --seeds $(s3 $R) --split rot$R $COR --set ssl_scale=100 --run-tag ${T1[$D]}C --tag c${SH[$D]}
  done; done
  for A in lp last last_randinit lp_randinit; do
    sub --model biot --dataset chbmit --arms $A --seeds ${(j:,:)BASE} --split paper --backbone-mode eval --set input_norm=q95 --run-tag P1Q --tag pq${AS[$A]}
  done
fi
if want E25; then   # logged re-runs, both heads
  for D in chbmit siena siena_filt; do for M in biot cbramod; do for R in 0 1 2 3 4; do
    sub --model $M --dataset ${DS[$D]} ${=VAR[$D]} --arms $A5 --seeds $(s3 $R) --split rot$R --labels overlap --probes linear,mlp_fullft --backbone-mode eval --run-tag ${T1[$D]}L --tag l${SH[$D]}
  done; done; done
  for M in biot cbramod; do for A in lp last last_randinit lp_randinit; do
    sub --model $M --dataset chbmit --arms $A --seeds ${(j:,:)BASE} --split paper --backbone-mode eval --run-tag P1L --tag pl${AS[$A]}
  done; done
fi
if want E26F; then  # filtered CHB-MIT, corrected protocol
  for M in biot cbramod; do for R in 0 1 2 3 4; do
    sub --model $M --dataset chbmit --data-variant filt --arms $A5 --seeds $(s3 $R) --split rot$R --labels overlap --probes linear,mlp_fullft --backbone-mode eval --run-tag S1FM --tag ffm
  done; done
fi
if want E27; then   # last_noise control
  for D in siena siena_filt; do for M in biot cbramod; do for R in 0 1 2 3 4; do
    sub --model $M --dataset ${DS[$D]} ${=VAR[$D]} --arms last_noise --seeds $(s3 $R) --split rot$R $COR --run-tag ${T1[$D]}N --tag n${SH[$D]}
  done; done; done
  for R in 0 1 2 3 4; do
    sub --model biot --dataset chbmit --arms last_noise --seeds $(s3 $R) --split rot$R $COR --run-tag S1N --tag n1
  done
fi
if want E28; then   # other 4,174-window SSL draws
  for M in biot cbramod; do for K in 11 12 13 14; do
    sub --model $M --dataset chbmit --arms last,last_randinit --seeds 42,123 --split paper --probes linear --backbone-mode eval --set ssl_seed=$K --run-tag P1D$K --tag pd$K
  done; done
  for D in chbmit siena; do for M in biot cbramod; do for R in 0 1 2 3 4; do for K in 11 12; do
    sub --model $M --dataset ${DS[$D]} --arms last,last_randinit --seeds ${BASE[R+1]} --split rot$R $COR --set ssl_seed=$K --run-tag ${T1[$D]}D$K --tag d${SH[$D]}${K: -1}
  done; done; done; done
fi
if want E29; then   # SSL dose-response
  CELLS=("ssl_lr=3e-4" "ssl_lr=1e-3" "ssl_lr=3e-5" "ssl_lr=3e-4" "ssl_lr=1e-3")
  FULL=(0 0 1 1 1)
  for D in chbmit siena; do for M in biot cbramod; do for R in 0 1 2 3 4; do for I in 1 2 3 4 5; do
    NARG=(); (( FULL[I] )) && NARG=(--ssl-n all)
    sub --model $M --dataset ${DS[$D]} --arms last,all --seeds ${BASE[R+1]} --split rot$R $COR $NARG --set ${CELLS[I]} --run-tag ${T1[$D]}LR$I --tag r${SH[$D]}$I
  done; done; done; done
fi
if want E30; then   # C2/C3 re-tests
  sub --model biot --dataset chbmit --arms last --seeds 123,2021,3407,8888 --split paper --batch 128 --probes linear --backbone-mode eval --protocol fixed_c --ssl-subsets N896,N1664,N2048,N4174 --run-tag C2X --tag c2x
  sub --model biot --dataset chbmit --arms last --seeds 123,2021,3407,8888 --split paper --batch 128 --probes linear --backbone-mode eval --protocol fixed_c --ssl-subsets P3N2048,P11N2048,P21N2048 --run-tag C3X --tag c3x
  for K in 2 3; do
    sub --model biot --dataset chbmit --arms last --seeds 42 --split paper --batch 128 --probes linear --backbone-mode eval --protocol fixed_c --ssl-subsets N896,N1664,N2048,N4174 --set data_seed=$K --run-tag C2X$K --tag c2x$K
    sub --model biot --dataset chbmit --arms last --seeds 42 --split paper --batch 128 --probes linear --backbone-mode eval --protocol fixed_c --ssl-subsets P3N2048,P11N2048,P21N2048 --set data_seed=$K --run-tag C3X$K --tag c3x$K
  done
  for D in siena siena_filt; do for R in 0 1 2 3 4; do
    sub --model biot --dataset ${DS[$D]} ${=VAR[$D]} --arms last --seeds $(s3 $R) --split rot$R $COR --batch 128 --protocol fixed_c --ssl-subsets N896,N1664,N2048,N4174 --run-tag ${T1[$D]}C2 --tag x2${SH[$D]}
    sub --model biot --dataset ${DS[$D]} ${=VAR[$D]} --arms last --seeds $(s3 $R) --split rot$R $COR --batch 128 --protocol fixed_c --ssl-subsets P2N2048,P5N2048,P10N2048 --run-tag ${T1[$D]}C3 --tag x3${SH[$D]}
    sub --model biot --dataset ${DS[$D]} ${=VAR[$D]} --arms lp --seeds $(s3 $R) --split rot$R $COR --batch 128 --run-tag ${T1[$D]}LPB --tag xb${SH[$D]}
    sub --model cbramod --dataset ${DS[$D]} ${=VAR[$D]} --arms last --seeds ${BASE[R+1]} --split rot$R $COR --batch 128 --protocol fixed_c --ssl-subsets N896,N4174,P2N2048,P10N2048 --run-tag ${T1[$D]}CC --tag xc${SH[$D]}
  done; done
fi
if want E32; then   # second subject partition
  for D in chbmit siena; do for M in biot cbramod; do for R in 0 1 2 3 4; do
    sub --model $M --dataset ${DS[$D]} --arms $A4 --seeds $(s3 $R) --split rot$R $COR --set fold_seed=20261101 --run-tag ${T1[$D]}R --tag p${SH[$D]}
  done; done; done
fi
if want D27X; then  # D27 addition: BIOT Siena SA gains without a noise control (notes/decisions.md)
  CELLS=("ssl_lr=3e-4" "ssl_lr=1e-3" "ssl_lr=3e-5" "ssl_lr=3e-4" "ssl_lr=1e-3"); FULL=(0 0 1 1 1)
  for I in 1 2 3 4 5; do for R in 0 1 2 3 4; do   # A5: E29 Siena cells
    NARG=(); (( FULL[I] )) && NARG=(--ssl-n all)
    sub --model biot --dataset siena --arms last,last_noise --seeds ${BASE[R+1]} --split rot$R --labels overlap --probes linear,linear_z --backbone-mode eval $NARG --set ${CELLS[I]} --run-tag S3LRN$I --tag dn$I
  done; done
  for D in siena siena_filt; do for R in 0 1 2 3 4; do   # A6: MLP head (and linear_z) noise control
    sub --model biot --dataset ${DS[$D]} ${=VAR[$D]} --arms last_noise --seeds $(s3 $R) --split rot$R --labels overlap --probes mlp_fullft,linear_z --backbone-mode eval --run-tag ${T1[$D]}NM --tag nm${SH[$D]}
  done; done
  for K in 11 12; do for R in 0 1 2 3 4; do   # A7: other SSL draws
    sub --model biot --dataset siena --arms last_noise --seeds ${BASE[R+1]} --split rot$R $COR --set ssl_seed=$K --run-tag S3DN$K --tag w3${K: -1}
  done; done
fi
if want D27; then   # review r1 controls (post hoc, notes/decisions.md D27)
  typeset -A AN=(lp lp last la last_noise ln)
  for A in lp last last_noise; do   # A1: q95 paper split + noise control
    sub --model biot --dataset chbmit --arms $A --seeds ${(j:,:)BASE} --split paper --probes linear,mlp_fullft,linear_z --backbone-mode eval --set input_norm=q95 --run-tag P1QN --tag pn${AN[$A]}
  done
  for R in 0 1 2 3 4; do   # A2: q95 Siena filtered + noise control
    sub --model biot --dataset siena --data-variant filt --arms lp,last,last_noise --seeds $(s3 $R) --split rot$R --labels overlap --probes linear,linear_z --backbone-mode eval --set input_norm=q95 --run-tag S3FQN --tag nqf
  done
  for D in chbmit siena; do for R in 0 1 2 3 4; do   # A3: E32 partition noise control
    sub --model biot --dataset ${DS[$D]} --arms last_noise --seeds $(s3 $R) --split rot$R --labels overlap --probes linear,linear_z --backbone-mode eval --set fold_seed=20261101 --run-tag ${T1[$D]}RN --tag rn${SH[$D]}
  done; done
  CELLS=("ssl_lr=3e-4" "ssl_lr=1e-3" "ssl_lr=3e-5" "ssl_lr=3e-4" "ssl_lr=1e-3"); FULL=(0 0 1 1 1)
  for I in 1 3 4 5; do for R in 0 1 2 3 4; do   # A4: E29 CHB-MIT BIOT cells that read F
    NARG=(); (( FULL[I] )) && NARG=(--ssl-n all)
    sub --model biot --dataset chbmit --arms last,last_noise --seeds ${BASE[R+1]} --split rot$R --labels overlap --probes linear,linear_z --backbone-mode eval $NARG --set ${CELLS[I]} --run-tag S1LRN$I --tag dn$I
  done; done
  for D in chbmit siena siena_filt; do for M in biot cbramod; do for R in 0 1 2 3 4; do   # B: 3-seed linear_z
    sub --model $M --dataset ${DS[$D]} ${=VAR[$D]} --arms $A4 --seeds $((1000 + R)),$((2000 + R)) --split rot$R --labels overlap --probes linear_z --backbone-mode eval --run-tag ${T1[$D]}Z --tag zb${SH[$D]}
  done; done; done
  for D in siena siena_filt; do for R in 0 1 2 3 4; do   # C: CBraMod LP at probe batch 128
    sub --model cbramod --dataset ${DS[$D]} ${=VAR[$D]} --arms lp --seeds $(s3 $R) --split rot$R $COR --batch 128 --run-tag ${T1[$D]}CLPB --tag cb${SH[$D]}
  done; done
  for M in biot cbramod; do for A in lp lp_randinit; do   # D: supervised fine-tuning reference
    sub --model $M --dataset chbmit --arms $A --seeds ${(j:,:)BASE} --split paper --probes ft --backbone-mode eval --run-tag P1FT --tag fz${AS[$A]}
  done; done
  for D in chbmit siena; do for M in biot cbramod; do for R in 0 1 2 3 4; do
    sub --model $M --dataset ${DS[$D]} --arms lp,lp_randinit --seeds $(s3 $R) --split rot$R --labels overlap --probes ft --backbone-mode eval --run-tag ${T1[$D]}FT --tag fn${SH[$D]}
  done; done; done
fi
if want D26; then   # linear_z on the E32 partition (post hoc, notes/decisions.md D26)
  for D in chbmit siena; do for M in biot cbramod; do for R in 0 1 2 3 4; do
    sub --model $M --dataset ${DS[$D]} --arms $A4 --seeds $(s3 $R) --split rot$R --labels overlap --probes linear_z --backbone-mode eval --set fold_seed=20261101 --run-tag ${T1[$D]}RZ --tag rz${SH[$D]}
  done; done; done
fi
if want E26; then   # train-standardized linear probe (triggered by E15)
  for D in chbmit siena siena_filt; do for M in biot cbramod; do for R in 0 1 2 3 4; do
    sub --model $M --dataset ${DS[$D]} ${=VAR[$D]} --arms $A4 --seeds ${BASE[R+1]} --split rot$R --labels overlap --probes linear_z --backbone-mode eval --run-tag ${T1[$D]}Z --tag z${SH[$D]}
  done; done; done
  for M in biot cbramod; do for A in lp last last_randinit lp_randinit; do
    sub --model $M --dataset chbmit --arms $A --seeds ${(j:,:)BASE} --split paper --probes linear_z --backbone-mode eval --run-tag P1Z --tag pz${AS[$A]}
  done; done
fi
if want E33B; then  # Siena published-style split
  for D in siena siena_filt; do for M in biot cbramod; do
    sub --model $M --dataset ${DS[$D]} ${=VAR[$D]} --arms lp,last,lp_randinit --seeds 42,1000,2000 --split pub --labels overlap --probes linear --backbone-mode eval --run-tag ${T1[$D]}P --tag pb${SH[$D]}
  done; done
fi
if want E33A; then  # extended CHB-MIT (chb12/13/17 + chb02_16+ + chb24_02/22), 23-subject rotations
  for M in biot cbramod; do for R in 0 1 2 3 4; do
    sub --model $M --dataset chbmit_x --arms $A5 --seeds $(s3 $R) --split rot$R $COR --run-tag S1X --tag s1x
  done; done
fi
if want D28; then   # probe convergence: tuned, early-stopped linear probes on cached features (notes/decisions.md D28)
  typeset -A AN=(lp lp last la last_noise ln)
  for M in biot cbramod; do for A in lp last last_randinit lp_randinit; do   # (a) DL's split, upstream labels
    sub --model $M --dataset chbmit --arms $A --seeds ${(j:,:)BASE} --split paper --probes grid,grid_z --backbone-mode eval --run-tag P1G --tag g${AS[$A]}
  done; done
  for A in lp last last_noise; do   # (a) BIOT with its native q95 input
    sub --model biot --dataset chbmit --arms $A --seeds ${(j:,:)BASE} --split paper --probes grid,grid_z --backbone-mode eval --set input_norm=q95 --run-tag P1QG --tag gq${AN[$A]}
  done
  for D in chbmit siena siena_filt; do for M in biot cbramod; do for R in 0 1 2 3 4; do   # (b) rotations
    sub --model $M --dataset ${DS[$D]} ${=VAR[$D]} --arms lp,last,last_randinit,lp_randinit,last_noise --seeds $(s3 $R) --split rot$R --labels overlap --probes grid,grid_z --backbone-mode eval --run-tag ${T1[$D]}G --tag g${SH[$D]}
  done; done; done
fi
if want D29; then   # C2/C3 noise and standardized-head controls at the fixed-compute budget (notes/decisions.md D29)
  ZH=(--labels overlap --probes linear,linear_z --backbone-mode eval)
  for D in siena siena_filt; do for R in 0 1 2 3 4; do   # E30b flags; last re-run (must reproduce E30b linear) + last_noise
    sub --model biot --dataset ${DS[$D]} ${=VAR[$D]} --arms last,last_noise --seeds $(s3 $R) --split rot$R $ZH --batch 128 --protocol fixed_c --ssl-subsets N896,N1664,N2048,N4174 --run-tag ${T1[$D]}C2D --tag y2${SH[$D]}
    sub --model biot --dataset ${DS[$D]} ${=VAR[$D]} --arms last,last_noise --seeds $(s3 $R) --split rot$R $ZH --batch 128 --protocol fixed_c --ssl-subsets P2N2048,P5N2048,P10N2048 --run-tag ${T1[$D]}C3D --tag y3${SH[$D]}
    sub --model biot --dataset ${DS[$D]} ${=VAR[$D]} --arms lp --seeds $(s3 $R) --split rot$R $ZH --batch 128 --run-tag ${T1[$D]}LPBD --tag yb${SH[$D]}
  done; done
fi
