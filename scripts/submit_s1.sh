#!/usr/bin/env zsh
# Step 1 (corrected protocol, notes/decisions.md D18/D19): 2 models x 5 rotations, seed per rotation.
#   zsh scripts/submit_s1.sh --plan-only        # print the 10 specs
#   zsh scripts/submit_s1.sh --i-have-confirmation
#   DATASET=siena RUN_TAG=S3 zsh scripts/submit_s1.sh ...   # Step 3, same design (D21)
#   MODELS=cbramod RUN_TAG=S1E zsh scripts/submit_s1.sh ...   # D23 re-run, CBraMod only
#   RUN_TAG=S2 ARMS_biot=single_b01,single_b02 ARMS_cbramod=single_b01,...,single_b10 zsh ...  # D22
set -euo pipefail
cd "${0:A:h}/.."
SEEDS=(42 123 2021 3407 8888)
DATASET=${DATASET:-chbmit}
RUN_TAG=${RUN_TAG:-S1}
ARMS=lp_randinit,lp,last,first,first_block,embed_only,first_noise,all,last_randinit
for M in ${=MODELS:-biot cbramod}; do   # MODELS=cbramod for one model (zsh: ${=...} splits)
  V=ARMS_$M; A=${(P)V:-$ARMS}
  for R in 0 1 2 3 4; do
    .venv/bin/python scripts/submit_job.py --stage arms --model $M --dataset $DATASET --arms $A \
      --seeds ${SEEDS[R+1]} --split rot$R --labels overlap --probes linear --run-tag $RUN_TAG --tag ${RUN_TAG:l} "$@"
  done
done
