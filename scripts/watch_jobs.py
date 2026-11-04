#!/usr/bin/env python3
"""Watch several SageMaker jobs until all are terminal (or --minutes elapses). Prints changes only.

    .venv/bin/python scripts/watch_jobs.py JOB [JOB ...] [--minutes 20] [--interval 60]

describe_training_job on exact names (O(1)); refreshes <PROVIDER> credentials on expiry.
"""

from __future__ import annotations

import argparse
import subprocess
import time

import boto3
from botocore.exceptions import ClientError

TERMINAL = {"Completed", "Failed", "Stopped"}


def client():
    return boto3.Session(profile_name="<AWS_PROFILE>", region_name="us-east-1").client("sagemaker")


def refresh() -> None:
    subprocess.run(["<CREDENTIAL_REFRESH_CMD>", "--account", "<ACCOUNT_ID>",
                    "--role", "<ROLE_NAME>", "--profile", "<AWS_PROFILE>", "--once"],
                   capture_output=True, timeout=120)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("jobs", nargs="+")
    ap.add_argument("--minutes", type=float, default=20)
    ap.add_argument("--interval", type=int, default=60)
    args = ap.parse_args()
    sm, last, deadline = client(), {}, time.time() + 60 * args.minutes
    while True:
        states = {}
        for j in args.jobs:
            try:
                d = sm.describe_training_job(TrainingJobName=j)
            except ClientError as exc:
                if "ExpiredToken" in str(exc) or "InvalidClientToken" in str(exc):
                    refresh()
                    sm = client()
                    d = sm.describe_training_job(TrainingJobName=j)
                else:
                    raise
            s = (d["TrainingJobStatus"], d.get("SecondaryStatus", ""))
            states[j] = (s, d)
            if last.get(j) != s:
                tail = ""
                if s[0] in TERMINAL:
                    tail = f"  billable={d.get('BillableTimeInSeconds')}s  {d.get('FailureReason', '')}"
                print(f"[{time.strftime('%H:%M:%S')}] {j[26:]}: {s[0]}/{s[1]}{tail}", flush=True)
                last[j] = s
        if all(s[0] in TERMINAL for s, _ in states.values()) or time.time() > deadline:
            break
        time.sleep(args.interval)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
