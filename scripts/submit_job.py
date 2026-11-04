#!/usr/bin/env python3
"""Submit one EEGDrift stage via <JOB_LIBRARY>. Ported from QuantArtifact/scripts/submit_job.py.

    python scripts/submit_job.py --stage calibrate --model biot --dataset chbmit --plan-only
    python scripts/submit_job.py --stage calibrate --model biot --dataset chbmit --smoke --i-have-confirmation
    python scripts/submit_job.py --stage arms --model cbramod --dataset chbmit --arms lp,last --tag a1 \
        --i-have-confirmation

Three things <JOB_LIBRARY> does not do for us: <PROVIDER> credential refresh (its refresh omits
--provider <PROVIDER>), the confirmation gate, and naming/prefix derivation (scripts/jobspec.py).
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
JOBLIB_SRC = Path.home() / "workspaces" / "<JOB_LIBRARY>" / "src" / "<JOB_LIBRARY>" / "src"

from jobspec import STAGES, JobSpec  # noqa: E402

# Allowlist, never a denylist: the SDK tars ALL of source_dir and honours no ignore file.
INCLUDE_DIRS = ("src", "configs", "weights")
INCLUDE_FILES = ("sm_entry.py",)


def refresh_credentials(profile: str) -> None:
    cmd = ["<CREDENTIAL_REFRESH_CMD>", "--account", "<ACCOUNT_ID>",
           "--role", "<ROLE_NAME>", "--profile", profile, "--once"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise SystemExit("credential refresh FAILED (Midway expired? run `mwinit -s`):\n"
                         + (r.stderr or r.stdout))


def stage_source() -> Path:
    staged = Path(tempfile.mkdtemp(prefix="dx-src-"))
    for d in INCLUDE_DIRS:
        shutil.copytree(REPO / d, staged / d,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"))
    for f in INCLUDE_FILES:
        shutil.copy2(REPO / f, staged / f)
    shutil.copy2(REPO / "requirements-job.txt", staged / "requirements.txt")
    size = sum(p.stat().st_size for p in staged.rglob("*") if p.is_file()) / 1e6
    print(f"staged       : {staged} ({size:.1f} MB)")
    return staged


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--model", required=True, choices=["biot", "cbramod"])
    ap.add_argument("--dataset", required=True, choices=["chbmit", "tuab", "tuev", "siena", "chbmit_x"])
    ap.add_argument("--arms", default="")
    ap.add_argument("--seeds", default="")
    ap.add_argument("--tag", default="")
    ap.add_argument("--run-id", default="drift-v1")
    ap.add_argument("--split", default="paper", help="paper | rot0..rot4")
    ap.add_argument("--batch", default="", help="override SSL+probe batch (upstream: one batch size)")
    ap.add_argument("--ssl-n", default="", help="'all' = whole SSL pool instead of the paper's N")
    ap.add_argument("--run-tag", default="", help="label stored in every record and the resume key")
    ap.add_argument("--data-variant", default="", help="'filt' = lmdb/<dataset>_filt/ eval store")
    ap.add_argument("--probes", default="", help="comma list of probe variants (default: all)")
    ap.add_argument("--protocol", default="", help="'fixed_c' = upstream Fig. 1/2 fixed-compute path")
    ap.add_argument("--ssl-subsets", default="", help="e.g. N896,N2048 or P3N2048,P11N2048")
    ap.add_argument("--labels", default="", help="'overlap' = corrected labels + grid-only val/test (D18)")
    ap.add_argument("--backbone-mode", default="", help="'eval' | 'train' probe backbone mode (D24)")
    ap.add_argument("--probe-tap", default="", help="CBraMod 'proj_out' = released-code probe input (D25)")
    ap.add_argument("--set", default="", help="extra overrides 'k=v,k=v' (sm_entry.SET_KEYS, D25)")
    ap.add_argument("--instance-type", default="", help="override configs/sm_job.yaml, e.g. ml.g5.16xlarge "
                    "(same A10G GPU, 256 GB RAM) for whole-pool jobs that exceed 128 GB")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--plan-only", action="store_true")
    ap.add_argument("--wait", action="store_true")
    ap.add_argument("--i-have-confirmation", action="store_true")
    args = ap.parse_args()

    spec = JobSpec.build(args.stage, args.model, args.dataset,
                         arms=[a for a in args.arms.split(",") if a],
                         seeds=[s for s in args.seeds.split(",") if s],
                         run_id=args.run_id, tag=args.tag, split=args.split, batch=args.batch,
                         ssl_n=args.ssl_n, run_tag=args.run_tag, data_variant=args.data_variant,
                         probes=args.probes, protocol=args.protocol, ssl_subsets=args.ssl_subsets,
                         labels=args.labels, backbone_mode=args.backbone_mode,
                         probe_tap=args.probe_tap, sets=args.set)
    if args.smoke:
        spec = spec.smoked()
    config = yaml.safe_load((REPO / "configs" / "sm_job.yaml").read_text())
    config.update(job_name=spec.name, entry_point="sm_entry.py", source_dir=str(REPO),
                  max_run=spec.max_run, checkpoint_s3_uri=spec.checkpoint_s3_uri,
                  inputs=spec.inputs, hyperparameters=spec.hyperparameters)
    if args.instance_type:
        config["instance_type"] = args.instance_type

    print(f"stage        : {spec.stage} — {STAGES[spec.stage][1]}")
    print(f"job name     : {spec.name}")
    print(f"instance     : {config['instance_type']}  region {config['region']}  max_run {spec.max_run}s")
    print(f"image        : PyTorch DLC {config['framework_version']} {config['py_version']}")
    print(f"inputs       : {spec.inputs}")
    print(f"checkpoints  : {spec.checkpoint_s3_uri}  (resume unit {spec.resume_unit()})")
    print(f"hyperparams  : {spec.hyperparameters}")
    if args.plan_only:
        print("\n--plan-only: nothing submitted.")
        return 0
    if not args.i_have_confirmation:
        sys.stderr.write("\nREFUSING TO SUBMIT: billable jobs need --i-have-confirmation.\n")
        return 2

    config["source_dir"] = str(stage_source())
    refresh_credentials(config["profile"])
    sys.path.insert(0, str(JOBLIB_SRC))
    from job_library.config import JobConfig  # noqa: PLC0415
    from job_library.runner import submit  # noqa: PLC0415

    handle = submit(JobConfig.from_dict(config), wait=args.wait)
    print(json.dumps({"job_name": handle.name, "submitted": True}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
