#!/usr/bin/env python3
"""SageMaker entry point. One job = one stage over one (model, dataset).

Hyperparameters (all strings, SageMaker passes them as --key value):
  stage    calibrate | diag | arms
  model    biot | cbramod          (calibrate: ignored, runs both)
  dataset  chbmit | tuab | tuev | siena
  arms     comma list (arms stage)
  seeds    comma list (default: configs/adapt.yaml seeds)
  run_id   artifact namespace, e.g. drift-v1
  smoke    0 | 1
Results land in /opt/ml/checkpoints/results (continuous S3 sync, resume) and are copied to
/opt/ml/model at the end. Activation dumps go straight to S3 via S3StreamingStore.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import resource
import shutil
import signal
import subprocess
import sys
import time
import traceback
from functools import partial
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import torch  # noqa: E402

from eegdrift.data.store import LocalStore, S3StreamingStore  # noqa: E402
from eegdrift.study import (  # noqa: E402
    Context,
    load_eval,
    load_ssl,
    run_arm_seed,
    run_arms,
    run_diag,
)

ARTIFACT_URI = "s3://<BUCKET>/<PREFIX>/artifacts/activations"


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def env_report() -> dict:
    info = {"python": platform.python_version(), "torch": torch.__version__,
            "cuda": torch.version.cuda, "cuda_available": torch.cuda.is_available(),
            "cpus": os.cpu_count()}
    if torch.cuda.is_available():
        info["gpu"] = torch.cuda.get_device_name(0)
        info["gpu_mem_gb"] = round(torch.cuda.get_device_properties(0).total_memory / 2**30, 1)
    try:
        info["nvidia_smi"] = subprocess.run(["nvidia-smi", "--query-gpu=driver_version,name",
                                             "--format=csv,noheader"], capture_output=True,
                                            text=True, timeout=30).stdout.strip()
    except Exception as exc:  # noqa: BLE001 - report, never fail the job on a probe
        info["nvidia_smi"] = f"unavailable: {exc}"
    return info


def _forward(m, x) -> None:
    m.features(m.prepare(x))


def _ssl_step(m, obj, opt, x) -> None:
    opt.zero_grad(set_to_none=True)
    obj.loss(m, x).backward()
    opt.step()


def _timed(fn, batch: int, dev: torch.device, iters: int = 8) -> float:
    """Windows per second over `iters` calls after one warm-up call."""
    fn()
    if dev.type == "cuda":
        torch.cuda.synchronize()
    t0 = time.time()
    for _ in range(iters):
        fn()
    if dev.type == "cuda":
        torch.cuda.synchronize()
    return round(iters * batch / (time.time() - t0), 1)


def throughput(ctx: Context) -> dict:
    """§6.6 items 1-3: windows/s for forward, SSL step and probe forward; peak VRAM."""
    from eegdrift.adapt import seed_everything
    from eegdrift.models._ckpt import checkpointing
    from eegdrift.models.protocols import group, set_trainable
    from eegdrift.objectives import objective_for

    def safe(fn):
        """One measurement; an OOM is a RESULT to record, not a reason to lose the others."""
        try:
            return fn()
        except torch.OutOfMemoryError:
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            return "OOM"

    dev, out = ctx.device, {}
    for name in ("biot", "cbramod"):
        seed_everything(0)
        m = ctx.registry.build(name)
        m.module.to(dev)
        obj = objective_for(m)
        res = {}
        for b in (128, 256):
            x30 = torch.randn(b, 16, 30, 200, device=dev)
            x10 = torch.randn(b, 16, 10, 200, device=dev)
            if dev.type == "cuda":
                torch.cuda.reset_peak_memory_stats()
            m.module.eval()
            with torch.no_grad():
                res[f"fwd30_wps_B{b}"] = safe(partial(_timed, partial(_forward, m, x30), b, dev))
                m.module.train()
                res[f"probefwd10_wps_B{b}"] = safe(partial(_timed, partial(_forward, m, x10), b, dev))
            for arm, groups in (("last", [m.groups[-2], group(m, "head")]), ("all", list(m.groups))):
                set_trainable(m, groups)
                opt = torch.optim.AdamW([p for p in m.module.parameters() if p.requires_grad], lr=1e-9)
                step = partial(_timed, partial(_ssl_step, m, obj, opt, x30), b, dev, 4)
                with checkpointing(m.checkpoint_units()):   # production runs checkpointed
                    res[f"ssl_step_{arm}_ckpt_wps_B{b}"] = safe(step)
                res[f"ssl_step_{arm}_nockpt_wps_B{b}"] = safe(step)
            if dev.type == "cuda":
                res[f"peak_vram_gb_B{b}"] = round(torch.cuda.max_memory_allocated() / 2**30, 2)
        out[name] = res
        log(f"[calibrate] {name}: {res}")
    out["peak_host_rss_gb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20, 2)
    return out


SET_KEYS = {"input_norm", "ssl_scale", "ssl_seed", "data_seed", "ssl_lr", "ssl_epochs", "fold_seed"}


def parse_sets(text: str) -> dict[str, str]:
    """'k=v,k=v' -> dict; only known keys, so a typo cannot silently do nothing. Comma, not ';':
    SageMaker runs the entry command through a shell, where ';' ends the command."""
    out = {}
    for kv in filter(None, text.split(",")):
        k, _, v = kv.partition("=")
        if k not in SET_KEYS or not v:
            raise ValueError(f"bad --set item {kv!r}; known keys: {sorted(SET_KEYS)}")
        out[k] = v
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True)
    ap.add_argument("--model", default="biot")
    ap.add_argument("--dataset", default="chbmit")
    ap.add_argument("--arms", default="")
    ap.add_argument("--seeds", default="")
    ap.add_argument("--run_id", default="drift-v1")
    ap.add_argument("--smoke", default="0")
    ap.add_argument("--split", default="paper")
    ap.add_argument("--batch", default="")
    ap.add_argument("--ssl_n", default="parity")
    ap.add_argument("--run_tag", default="")
    ap.add_argument("--probes", default="")
    ap.add_argument("--protocol", default="parity")
    ap.add_argument("--ssl_subsets", default="")
    ap.add_argument("--labels", default="")
    ap.add_argument("--backbone_mode", default="")
    ap.add_argument("--probe_tap", default="")
    ap.add_argument("--set", default="", help="extra overrides 'k=v,k=v' (D25)")
    args, _ = ap.parse_known_args()
    smoke = args.smoke == "1"
    run_id = args.run_id + ("-smoke" if smoke else "")

    data_root = Path(os.environ.get("SM_CHANNEL_DATA", ROOT / "data" / "lmdb"))
    out = Path("/opt/ml/checkpoints") if Path("/opt/ml").exists() else ROOT / "artifacts" / "local"
    in_sm = Path("/opt/ml").exists()
    artifacts = (S3StreamingStore(f"{ARTIFACT_URI}/{run_id}") if in_sm
                 else LocalStore(ROOT / "artifacts" / "activations" / run_id))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    overrides = {k: v for k, v in (("batch", args.batch), ("ssl_n", args.ssl_n),
                                   ("run_tag", args.run_tag), ("probes", args.probes),
                                   ("protocol", args.protocol), ("ssl_subsets", args.ssl_subsets),
                                   ("labels", args.labels), ("backbone_mode", args.backbone_mode),
                                   ("probe_tap", args.probe_tap))
                 if v not in ("", "parity")}
    overrides.update(parse_sets(args.set))
    ctx = Context(root=ROOT, data_root=data_root, out=out, artifacts=artifacts, device=device,
                  smoke=smoke, log=log, overrides=overrides)
    seeds = [int(s) for s in args.seeds.split(",") if s] or ctx.adapt_cfg["seeds"]
    if smoke:
        seeds = seeds[:1]
    report = {"stage": args.stage, "args": vars(args), "env": env_report(), "started": time.time()}
    report_path = out / f"report-{args.stage}-{args.model}-{args.dataset}-{args.split}.json"

    def save_report() -> None:   # written as the stage goes, so a max_run kill keeps what ran
        report_path.write_text(json.dumps(report, indent=2, default=str))

    def on_sigterm(signum, _frame):   # SageMaker sends SIGTERM at max_run / StopTrainingJob
        report["error"] = f"terminated by signal {signum}"
        save_report()
        raise SystemExit(143)

    signal.signal(signal.SIGTERM, on_sigterm)
    log(f"[env] {json.dumps(report['env'])}")
    save_report()
    status = 0
    try:
        if args.stage == "calibrate":
            report["throughput"] = throughput(ctx)
            save_report()
            t0 = time.time()
            ssl = load_ssl(ctx, args.dataset)
            report["load_ssl_s"] = round(time.time() - t0)
            t0 = time.time()
            ev = load_eval(ctx, args.dataset, "paper")   # ~42 GB float32: load ONCE
            report["load_eval_s"] = round(time.time() - t0)
            save_report()
            for name in ("biot", "cbramod"):
                for arm in ("lp", "last"):
                    t1 = time.time()
                    run_arm_seed(ctx, name, args.dataset, arm, seeds[0], ssl, ev)
                    report.setdefault("unit_runs", []).append(
                        {"model": name, "arm": arm, "seed": seeds[0], "run_s": round(time.time() - t1)})
                    save_report()
        elif args.stage == "diag":
            report["diag"] = run_diag(ctx, args.model, args.dataset, seeds, run_id)
        elif args.stage == "arms":
            arms = [a for a in args.arms.split(",") if a]
            if not arms:
                raise ValueError("--arms is required for the arms stage")
            run_arms(ctx, args.model, args.dataset, arms, seeds, args.split)
        else:
            raise ValueError(f"unknown stage {args.stage}")
    except Exception:  # noqa: BLE001 - record the failure in the report, then fail the job
        report["error"] = traceback.format_exc()
        log(report["error"])
        status = 1
    report["finished"] = time.time()
    report["seconds"] = round(report["finished"] - report["started"])
    report["peak_host_rss_gb_stage"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20, 2)
    save_report()
    model_dir = Path(os.environ.get("SM_MODEL_DIR", out.parent / f"{out.name}-model"))
    model_dir.mkdir(parents=True, exist_ok=True)
    # Materialise the list BEFORE copying: a lazy rglob would see its own copies if model_dir
    # ever sat inside `out` (it did once, and nested model/model/... until ENAMETOOLONG).
    for f in [p for p in out.rglob("*.json") if model_dir not in p.parents]:
        dest = model_dir / f.relative_to(out)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dest)
    log(f"[exit] status {status} after {report['seconds']}s")
    return status


if __name__ == "__main__":
    raise SystemExit(main())
