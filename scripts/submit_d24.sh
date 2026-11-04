#!/usr/bin/env zsh
# D24 (notes/decisions.md): Paper A strengthening runs, all with an eval-mode, encoder-tap probe.
#   zsh scripts/submit_d24.sh --plan-only            # print every spec, submit nothing
#   zsh scripts/submit_d24.sh --i-have-confirmation  # 44 jobs
set -euo pipefail
cd "${0:A:h}/.."
# START=n skips the first n-1 specs (resume a half-finished submission without duplicates)
N=0
sub() { N=$((N + 1)); (( N < ${START:-1} )) && { echo "skip $N"; return 0; }
        .venv/bin/python scripts/submit_job.py --stage arms --backbone-mode eval "$@"; }
BASE=(42 123 2021 3407 8888)
A_ARMS=lp,lp_randinit,last,last_randinit,all

# A. corrected protocol, 3 seeds per rotation (CBraMod's base seed already ran under S1E/S3E/S3FE)
for D in chbmit siena siena_filt; do
  case $D in
    chbmit) DS=chbmit; RT=S1M; TG=s1m; VAR=() ;;
    siena) DS=siena; RT=S3M; TG=s3m; VAR=() ;;
    siena_filt) DS=siena; RT=S3FM; TG=sfm; VAR=(--data-variant filt) ;;
  esac
  for M in biot cbramod; do
    for R in 0 1 2 3 4; do
      S="$((1000 + R)),$((2000 + R))"
      [[ $M == biot ]] && S="${BASE[R+1]},$S"
      sub --model $M --dataset $DS --arms $A_ARMS --seeds $S --split rot$R --labels overlap \
        --probes linear --run-tag $RT --tag $TG $VAR "$@"
    done
  done
done

# B. the paper's own setting (paper split, upstream labels, parity), both heads, 5 seeds
typeset -A SHORT=(lp lp last la last_randinit lr lp_randinit pr)   # job names <= 63 chars
for M in biot cbramod; do
  for A in lp last last_randinit lp_randinit; do
    sub --model $M --dataset chbmit --arms $A --seeds ${(j:,:)BASE} --split paper \
      --run-tag P1E --tag p1e${SHORT[$A]} "$@"
  done
done

# C. C2/C3 with the fixed probe (D15 design) + its 5-seed LP baseline at batch 128
for M in biot cbramod; do
  sub --model $M --dataset chbmit --arms last,last_randinit --seeds 42 --split paper --batch 128 \
    --probes linear --protocol fixed_c --ssl-subsets N896,N1664,N2048,N4174 --run-tag C2E --tag c2e "$@"
  sub --model $M --dataset chbmit --arms last,last_randinit --seeds 42 --split paper --batch 128 \
    --probes linear --protocol fixed_c --ssl-subsets P3N2048,P11N2048,P21N2048 --run-tag C3E --tag c3e "$@"
  sub --model $M --dataset chbmit --arms lp --seeds ${(j:,:)BASE} --split paper --batch 128 \
    --probes linear --run-tag R3E-b128 --tag r3e "$@"
done
