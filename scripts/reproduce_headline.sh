#!/usr/bin/env zsh
# Re-run the headline comparison (D24-B: paper Table tab:p1e and the bottom rows of tab:d24a): DL's split,
# start/end labels, DL's SSL protocol, pretrained weights, encoder-level probe with the backbone in eval
# mode, BIOT and CBraMod, arms lp and last, 5 seeds, linear and shipped MLP heads. GPU work; docs/REPRODUCE.md.
#
#   zsh scripts/reproduce_headline.sh sagemaker                        # print the 4 job specs (--plan-only)
#   zsh scripts/reproduce_headline.sh sagemaker --i-have-confirmation  # submit them (billable, about $35)
#   zsh scripts/reproduce_headline.sh local                            # the same runs on this machine's GPU
#   zsh scripts/reproduce_headline.sh read artifacts/local             # read new records, compare with saved
#
# Env: ARMS (default "lp last"; "lp last last_randinit lp_randinit" = every arm of tab:p1e), DATA (local data
# root holding chbmit_ssl30/ and chbmit_eval10/; default data/lmdb/chbmit), PY (default .venv/bin/python).
# SageMaker jobs get fresh checkpoint prefixes (tag rp1e*), so nothing resumes from the original P1E runs.
# Fetch their records, then read them:
#   aws s3 sync s3://<BUCKET>/<PREFIX>/checkpoints/ artifacts/repro-headline \
#     --exclude '*' --include 'arms-*-chb-rp1e*/results/*.json' --profile <AWS_PROFILE>
#   zsh scripts/reproduce_headline.sh read artifacts/repro-headline
set -euo pipefail
cd "${0:A:h}/.."
PY=${PY:-.venv/bin/python}
SEEDS=42,123,2021,3407,8888
ARMS=(${=ARMS:-lp last})
typeset -A SHORT=(lp lp last la last_randinit lr lp_randinit pr)   # job names <= 63 chars
mode=${1:?usage: reproduce_headline.sh sagemaker|local|read DIR}
shift

case $mode in
  sagemaker)
    plan=(--plan-only)
    (( ${@[(Ie)--i-have-confirmation]} )) && plan=()
    for M in biot cbramod; do
      for A in $ARMS; do
        $PY scripts/submit_job.py --stage arms --backbone-mode eval --model $M --dataset chbmit --arms $A \
          --seeds $SEEDS --split paper --run-tag P1E --tag rp1e${SHORT[$A]} $plan "$@"
      done
    done ;;
  local)   # sm_entry.py outside SageMaker writes artifacts/local/results/ and resumes from it
    for M in biot cbramod; do
      SM_CHANNEL_DATA=${DATA:-data/lmdb/chbmit} $PY sm_entry.py --stage arms --model $M --dataset chbmit \
        --arms ${(j:,:)ARMS} --seeds $SEEDS --split paper --run_tag P1E --backbone_mode eval
    done
    echo "next: zsh scripts/reproduce_headline.sh read artifacts/local" ;;
  read)
    dir=${1:?read needs the directory that holds <unit>/results/*.json}
    $PY scripts/read_d24.py --local $dir --dataset chbmit --tags P1E --paper \
      --out artifacts/tables/main/headline-${dir:t}.md
    $PY - $dir <<'EOF'
import sys
sys.path.insert(0, "scripts")
from read_d24 import load
new, old = load(sys.argv[1], "chbmit", {"P1E"}), load("artifacts/s3-results", "chbmit", {"P1E"})
for k in sorted(new):
    d = [abs(v - old[k][s]) for s, v in new[k].items() if s in old.get(k, {})]
    print(f"{'/'.join(k)}: {len(new[k])} seeds, {len(d)} with a saved twin, max |new - saved| ROC x100 = "
          + (f"{max(d):.4f}" if d else "n/a"))
EOF
    ;;
  *) echo "unknown mode $mode (sagemaker | local | read DIR)" >&2; exit 2 ;;
esac
