#!/usr/bin/env python3
"""D25 wave C: one SageMaker job per cell of configs/released_grid.yaml (the RELEASED code).

    python scripts/released/submit_released.py --plan-only                      # every cell, overrides, hours
    python scripts/released/submit_released.py --only '^e4-' --smoke --i-have-confirmation
    python scripts/released/submit_released.py --only '^e4-' --i-have-confirmation
    python scripts/released/submit_released.py --only '^e5sa-c-fd1-ft0-b128-sR$' --seeds 2021,3407,8888 ...
    python scripts/released/submit_released.py --stage DIR --only ...           # write job bundles only

A job bundle is sm_released_entry.py + cell.json + released-freeze.txt (the E1 freeze) + weights/;
nothing from the released repo (the container clones it). Same checkpoint prefix per cell, so a
resubmission (e.g. the E5 3-more-seeds follow-up) skips seeds already DONE. Credentials, the
confirmation gate and the base config are those of scripts/submit_job.py.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import re
import shutil
import sys
import tempfile
import uuid
from datetime import UTC, datetime
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO / "scripts"))
from jobspec import BUCKET, NAME_RE  # noqa: E402
from submit_job import JOBLIB_SRC, refresh_credentials  # noqa: E402

GRID = REPO / "configs" / "released_grid.yaml"
FREEZE = REPO / "artifacts" / "analysis" / "E1" / "env" / "env_11_freeze_final.txt"
DATA_URI = f"{BUCKET}/released/chbmit-d056cdf/"
MAX_RUN_CAP = 5 * 86400


def cells(grid: dict) -> list[dict]:
    """Expand items x factor levels; drop excluded combinations; assert the audit's run counts."""
    out = []
    for item, spec in grid["items"].items():
        s = {**grid["defaults"], **spec}
        names = list(s["factors"])
        n_runs = 0
        for combo in itertools.product(*(s["factors"][n].items() for n in names)):
            codes = [code for code, _ in combo]
            if any(set(ex) <= set(codes) for ex in s["exclude"]):
                continue
            ov = [*s["base"], *(o for _, level in combo for o in level)]
            out.append({"id": "-".join([item.lower().replace("-", ""), *codes]), "item": item,
                        "entry": s["entry"], "levels": dict(zip(names, codes, strict=True)),
                        "overrides": [o for o in ov if not o.startswith("@")],
                        "patches": [o[1:] for o in ov if o.startswith("@")], "seeds": list(s["seeds"]),
                        "parallel": s["parallel"], "hours_per_run": s["hours_per_run"],
                        "stage_hours": s["stage_hours"]})
            n_runs += len(s["seeds"])
        if n_runs != s["audit_runs"]:
            raise SystemExit(f"{item}: grid gives {n_runs} runs, the audit specifies {s['audit_runs']}")
    ids = [c["id"] for c in out]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate cell ids")
    return out


def hours(c: dict) -> float:
    return c["stage_hours"] + math.ceil(len(c["seeds"]) / c["parallel"]) * c["hours_per_run"]


def job_name(cid: str, smoke: bool, now: datetime) -> str:
    name = f"anon-DX-rel-{now:%m%d}-{uuid.uuid4().hex[:4]}-{cid}" + ("-smoke" if smoke else "")
    if not NAME_RE.match(name) or len(name) > 63:
        raise SystemExit(f"job name invalid or longer than 63 characters: {name}")
    return name


def stage(c: dict, dest: Path) -> Path:
    dest.mkdir(parents=True)
    shutil.copy2(HERE / "sm_released_entry.py", dest)
    shutil.copy2(FREEZE, dest / "released-freeze.txt")
    shutil.copytree(REPO / "weights", dest / "weights")
    (dest / "cell.json").write_text(json.dumps(c, indent=2))
    return dest


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--grid", default=str(GRID))
    ap.add_argument("--only", default="", help="regex on cell ids")
    ap.add_argument("--seeds", default="", help="override the seeds of the selected cells (comma list)")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--plan-only", action="store_true")
    ap.add_argument("--stage", default="", help="write the job bundles to DIR/<cell>/ and stop")
    ap.add_argument("--instance-type", default="", help="override configs/sm_job.yaml (e.g. ml.g6e.2xlarge, "
                    "48 GB, for the cells that run out of memory on the 24 GB A10G)")
    ap.add_argument("--wait", action="store_true")
    ap.add_argument("--i-have-confirmation", action="store_true")
    args = ap.parse_args()

    sel = [c for c in cells(yaml.safe_load(Path(args.grid).read_text())) if re.search(args.only, c["id"])]
    if args.seeds:
        for c in sel:
            c["seeds"] = [int(s) for s in args.seeds.split(",")]
    if not sel:
        raise SystemExit("no cell matches --only")
    now = datetime.now(UTC)
    by_item: dict = {}
    for c in sel:
        c["job_name"] = job_name(c["id"], args.smoke, now)
        h = 0.5 + c["stage_hours"] if args.smoke else hours(c)
        c["max_run"] = min(MAX_RUN_CAP, int(3 * 3600 if args.smoke else 1.5 * h * 3600))
        runs = 1 if args.smoke else len(c["seeds"])
        it = by_item.setdefault(c["item"], [0, 0, 0.0])
        it[0], it[1], it[2] = it[0] + 1, it[1] + runs, it[2] + h
        seeds = c["seeds"][:1] if args.smoke else c["seeds"]
        print(f"{c['job_name']}  [{len(c['job_name'])}]  {c['entry']}  seeds {seeds}"
              f"  est {h:.1f} h  max_run {c['max_run']} s")
        patches = f"   patches: {c['patches']}" if c["patches"] else ""
        print(f"    overrides: {' '.join(c['overrides'])}{patches}")
    print("\nitem         jobs  runs  est instance-h (ml.g5.8xlarge)")
    for item, (j, r, h) in by_item.items():
        print(f"{item:12s} {j:5d} {r:5d}  {h:8.1f}")
    tot = [sum(v[i] for v in by_item.values()) for i in range(3)]
    print(f"{'TOTAL':12s} {tot[0]:5d} {tot[1]:5d}  {tot[2]:8.1f}"
          f"   (input {DATA_URI}; smoke={args.smoke}; seeds sequential unless parallel > 1)")
    if args.plan_only:
        print("\n--plan-only: nothing submitted.")
        return 0
    if args.stage:
        for c in sel:
            stage(c, Path(args.stage).expanduser() / c["id"])
        print(f"\nstaged {len(sel)} bundles under {args.stage}; nothing submitted.")
        return 0
    if not args.i_have_confirmation:
        sys.stderr.write("\nREFUSING TO SUBMIT: billable jobs need --i-have-confirmation.\n")
        return 2

    base = yaml.safe_load((REPO / "configs" / "sm_job.yaml").read_text())
    refresh_credentials(base["profile"])
    sys.path.insert(0, str(JOBLIB_SRC))
    from job_library.config import JobConfig  # noqa: PLC0415
    from job_library.runner import submit  # noqa: PLC0415

    for c in sel:
        with tempfile.TemporaryDirectory(prefix="dx-rel-") as tmp:   # ~34 MB each: never left on the Mac
            src = stage(c, Path(tmp) / "src")
            ckpt = f"{BUCKET}/released/checkpoints{'-smoke' if args.smoke else ''}/{c['id']}/"
            config = {**base, "job_name": c["job_name"], "entry_point": "sm_released_entry.py",
                      "source_dir": str(src), "max_run": c["max_run"], "volume_size": 400,
                      "checkpoint_s3_uri": ckpt, "instance_type": args.instance_type or base["instance_type"],
                      "inputs": {"data": DATA_URI}, "hyperparameters": {"smoke": "1" if args.smoke else "0"}}
            handle = submit(JobConfig.from_dict(config), wait=args.wait)
        print(json.dumps({"job_name": handle.name, "cell": c["id"], "submitted": True}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
