#!/usr/bin/env python3
"""D25 wave C: run ONE grid cell (configs/released_grid.yaml) of the RELEASED code.

The released repo (c3n-group/efficient-eeg-adapt, GPL) is cloned and checked out at d056cdf at job
start and run from that clone; nothing from it is vendored here. Stdlib only: this runs under the
DLC python before the released env exists. Steps, all logged to <ckpt>/harness.log:
  1. clone + checkout d056cdf (verified), 2. venv from the E1 freeze (released-freeze.txt),
  3. unpack the staged shards (data channel, MANIFEST.tsv) to local disk, 4. '$WORK' symlinks and
  weight names, 5. the E7 sed patches if the cell lists any (git diff --numstat verified),
  6. the cell's entry point once per seed (training.wandb=False, output_dir on local disk),
  7. per seed: logs, CSVs, prediction .npy and the Hydra config -> <ckpt>/<cell>/s<seed>/ (DONE
     marks a finished seed; a resubmission skips it), at the end -> SM_MODEL_DIR.
--smoke 1: first seed only, 1 SPT epoch, 1 probe epoch, a seeded ~320-window symlink farm, and the
4,174-key SSL store (except diversityP, whose P subsets need the whole LMDB).

  SageMaker: entry point; cell.json, released-freeze.txt and weights/ sit next to this file.
  Desktop:   python sm_released_entry.py --cell cell.json --data ~/released/stage --work W --ckpt C \
                 --model-dir M --smoke 1
"""

from __future__ import annotations

import argparse
import json
import os
import random
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_URL = "https://github.com/c3n-group/efficient-eeg-adapt.git"
COMMIT = "d056cdf94a6a680917218deae1f7815143ded27c"
TORCH_INDEX = "https://download.pytorch.org/whl/cu121"   # the released README's index for +cu121
ENTRIES = {"main": "main.py", "layer": "ablation_layer/main_layer.py",
           "divN": "ablation_diversityN/main_diversityN.py",
           "divP": "ablation_diversityP/main_diversityP.py"}
# E7 throwaway patches (audit E7 i/ii): sed expression, file, expected `git diff --numstat` row.
PATCHES = {
    "encoder_tap": (r"29s/^\(\s*\)#backbone.proj_out = nn.Identity()/\1backbone.proj_out = nn.Identity()/",
                    "src/model_factory.py", "1\t1\tsrc/model_factory.py"),
    "backbone_eval": (r"597s/^\(\s*\)self.model.train()$/&\n\1self.model.backbone.eval()/",
                      "src/trainer.py", "1\t0\tsrc/trainer.py"),
}
# released file names -> our weights/ (same bytes, sha256 checked in E1); '+'-free names for Hydra
WEIGHTS = {"EEG-SHHS+PREST-18-channels.ckpt": "biot_EEG-SHHS+PREST-18-channels.ckpt",
           "cbramod_main_pretrained_weights.pth": "cbramod_pretrained_weights.pth",
           "biot_foundation.ckpt": "biot_EEG-SHHS+PREST-18-channels.ckpt",
           "cbramod_foundation.pth": "cbramod_pretrained_weights.pth"}
FOUNDATION = {"biot": "biot_foundation.ckpt", "cbramod": "cbramod_foundation.pth"}
KEEP = {".csv", ".log", ".yaml", ".json"}   # plus predictions/*.npy; no weights, features or PNGs
SMOKE_FARM = {"train": 200, "val": 60, "test": 60}


def log(path: Path, msg: str) -> None:
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(path, "a") as f:
        f.write(line + "\n")


# SageMaker's DLC sets PYTHONPATH to its own site-packages, which leaks the container's torch,
# numpy and protobuf into the released venv; every command runs without it.
CLEAN = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP")}


def sh(cmd, logf: Path, **kw) -> None:
    """Run, append stdout+stderr to logf, raise on failure."""
    cmd = [str(c) for c in cmd]
    kw.setdefault("env", CLEAN)
    with open(logf, "a") as f:
        f.write("$ " + " ".join(cmd) + "\n")
        f.flush()
        subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, check=True, **kw)


def clone(repo: str, dest: Path, logf: Path) -> None:
    if not (dest / ".git").exists():
        sh(["git", "clone", "--quiet", repo, dest], logf)
    sh(["git", "-C", dest, "checkout", "--quiet", "--force", COMMIT], logf)   # drops old patches
    sh(["git", "-C", dest, "clean", "-fdxq"], logf)
    head = subprocess.check_output(["git", "-C", str(dest), "rev-parse", "HEAD"], text=True).strip()
    if head != COMMIT:
        raise SystemExit(f"clone is at {head}, expected {COMMIT}")


def make_env(venv: Path, logf: Path) -> Path:
    py = venv / "bin" / "python"
    if not (venv / "INSTALLED").exists():   # desktop re-runs reuse it; a container always builds
        sh([sys.executable, "-m", "venv", "--clear", venv], logf)
        sh([py, "-m", "pip", "install", "-q", "--no-cache-dir", "-r", HERE / "released-freeze.txt",
            "--extra-index-url", TORCH_INDEX], logf)
        (venv / "INSTALLED").write_text(time.ctime())
    return py


def stage(data: Path, dest: Path, logf: Path) -> dict:
    """Unpack every shard in MANIFEST.tsv (size-checked) and check the per-split pickle counts."""
    rows = [r.split("\t") for r in (data / "MANIFEST.tsv").read_text().splitlines()[1:] if r]
    want: dict = {}

    def one(row):
        name, n, size, _sha = row
        if name.startswith("chbmit_seg-"):
            split = name.split("-")[1]
            want[split] = want.get(split, 0) + int(n)
        done = dest / f".{name}.done"
        if done.exists():
            return
        got = (data / name).stat().st_size
        if got != int(size):
            raise SystemExit(f"{name}: {got} bytes, manifest says {size}")
        sub = dest / "processed_seg" if name.startswith("chbmit_seg-") else dest
        # each shard unpacks into its own folder first: 8 tars writing into one split folder at
        # once raced ("Cannot open: No such file or directory" in 2 of 5 GPU smokes)
        tmp = dest / f".unpack-{name}"
        shutil.rmtree(tmp, ignore_errors=True)
        tmp.mkdir(parents=True)
        subprocess.run(["tar", "-xf", str(data / name), "-C", str(tmp)], check=True)
        for root, dirs, files in os.walk(tmp):
            rel = Path(root).relative_to(tmp)
            (sub / rel).mkdir(parents=True, exist_ok=True)
            for f in files:
                os.replace(Path(root) / f, sub / rel / f)
            for d in dirs:
                (sub / rel / d).mkdir(parents=True, exist_ok=True)
        shutil.rmtree(tmp, ignore_errors=True)
        done.touch()

    with ThreadPoolExecutor(8) as ex:
        list(ex.map(one, rows))
    have = {s: len(os.listdir(dest / "processed_seg" / s)) for s in want}
    if have != want:
        raise SystemExit(f"pickle counts {have} != manifest {want}")
    log(logf, f"[stage] {len(rows)} shards unpacked; processed_seg counts {have}")
    return have


def smoke_farm(seg: Path, farm: Path) -> None:
    """Seeded symlink farm, a quarter '-s-' (seizure) windows so val/test hold both classes."""
    rng = random.Random(0)
    for split, k in SMOKE_FARM.items():
        names = sorted(os.listdir(seg / split))
        rng.shuffle(names)
        pick = [n for n in names if "-s-" in n][: k // 4]
        pick += [n for n in names if "-s-" not in n][: k - len(pick)]
        (farm / split).mkdir(parents=True, exist_ok=True)
        for n in pick:
            if not (farm / split / n).exists():
                (farm / split / n).symlink_to(seg / split / n)


def resolve(cell: dict, data: Path, weights: Path, farm: Path | None, smoke: bool) -> list[str]:
    """Fill placeholders; in smoke mode replace (not duplicate) the keys the smoke changes."""
    model = next(o.split("=", 1)[1] for o in cell["overrides"] if o.startswith("model="))
    ov = [o.replace("{data}", str(data)).replace("{foundation}", str(weights / FOUNDATION[model]))
          for o in cell["overrides"]]
    if smoke:
        extra = ["dataset.training.epochs=1", "dataset.method.spt_epochs=1", f"dataset.datasets_dir={farm}"]
        if cell["entry"] != "divP":
            extra.append(f"dataset.pretrain_datasets_dir={data}/chbmit_ssl_4174.lmdb")
        keys = {e.split("=", 1)[0] for e in extra}
        ov = [o for o in ov if o.split("=", 1)[0].lstrip("+") not in keys] + extra
    return ov


def collect(out: Path, dest: Path) -> None:
    for p in [p for p in out.rglob("*") if p.is_file()]:
        if p.suffix in KEEP or (p.suffix == ".npy" and p.parent.name == "predictions"):
            (dest / p.relative_to(out)).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dest / p.relative_to(out))


def main() -> int:
    sm = Path("/opt/ml/input").exists()
    chan = Path(os.environ.get("SM_CHANNEL_DATA", "/opt/ml/input/data/data"))
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", default=str(HERE / "cell.json"))
    ap.add_argument("--smoke", default="0")
    ap.add_argument("--data", default=str(chan), help="dir with the shards + MANIFEST.tsv")
    ap.add_argument("--work", default=str(chan.parents[1] / "work"), help="local disk: clone, env, data")
    ap.add_argument("--ckpt", default="/opt/ml/checkpoints")
    ap.add_argument("--model-dir", default=os.environ.get("SM_MODEL_DIR", "/opt/ml/model"))
    ap.add_argument("--repo", default=REPO_URL)
    args, _ = ap.parse_known_args()
    cell, smoke = json.loads(Path(args.cell).read_text()), args.smoke == "1"
    work, data = Path(args.work).expanduser(), Path(args.data).expanduser()
    ckpt = Path(args.ckpt).expanduser() / cell["id"]
    ckpt.mkdir(parents=True, exist_ok=True)
    hlog = ckpt / "harness.log"
    (ckpt / "cell.json").write_text(json.dumps({**cell, "smoke": smoke}, indent=2))
    t = {"start": time.time()}
    log(hlog, f"[cell] {cell['id']} smoke={smoke} entry={cell['entry']} seeds={cell['seeds']}")

    eea, local = work / "eea", work / "data"
    clone(args.repo, eea, hlog)
    t["clone"] = time.time()
    py = make_env(work / "venv", hlog)
    sh([py, "-m", "pip", "freeze"], ckpt / "env_freeze.txt")
    probe = subprocess.run([str(py), "-c", "import torch; print(torch.__version__, torch.cuda.is_available())"],
                           capture_output=True, text=True, check=True, env=CLEAN).stdout.split()
    log(hlog, f"[env] torch {probe[0]} cuda={probe[1]}")
    if not probe[0].startswith("2.4.1"):   # the E1 freeze pins torch 2.4.1+cu121
        raise SystemExit(f"released env has torch {probe[0]}, not the pinned 2.4.1: environment leak")
    if sm and probe[1] != "True":
        raise SystemExit("no CUDA in the released env on a GPU instance")
    t["env"] = time.time()
    stage(data, local, hlog)
    t["stage"] = time.time()

    chb = eea / "src" / "$WORK" / "datasets" / "physionet.org" / "files" / "chbmit"   # literal '$WORK'
    chb.mkdir(parents=True, exist_ok=True)
    weights = work / "weights"
    weights.mkdir(exist_ok=True)
    for link, target in [(chb / n, local / n) for n in ("processed_seg", "chbmit_preprocessed_30S.lmdb")] + \
            [(weights / n, HERE / "weights" / f) for n, f in WEIGHTS.items()]:
        link.unlink(missing_ok=True)
        link.symlink_to(target)

    for name in cell["patches"]:
        expr, path, _row = PATCHES[name]
        sh(["sed", "-i", expr, eea / path], hlog)
    numstat = subprocess.check_output(["git", "-C", str(eea), "diff", "--numstat"], text=True).splitlines()
    (ckpt / "patches.numstat").write_text("\n".join(numstat) + "\n")
    if sorted(numstat) != sorted(PATCHES[n][2] for n in cell["patches"]):
        raise SystemExit(f"patch check failed: numstat {numstat} for patches {cell['patches']}")

    farm = None
    if smoke:
        farm = work / "smoke_farm"
        smoke_farm(local / "processed_seg", farm)
    overrides = resolve(cell, local, weights, farm, smoke)
    env = {**CLEAN, "WANDB_MODE": "disabled", "PYTHONUNBUFFERED": "1", "PYTHONDONTWRITEBYTECODE": "1",
           "TQDM_MININTERVAL": "30"}

    def run_seed(seed: int) -> int:
        sd = ckpt / f"s{seed}"
        if (sd / "DONE").exists():
            log(hlog, f"[seed {seed}] DONE in checkpoint, skipped")
            return 0
        out = work / "out" / cell["id"] / f"s{seed}"
        shutil.rmtree(out, ignore_errors=True)
        out.mkdir(parents=True)
        cmd = [str(py), ENTRIES[cell["entry"]], *overrides, f"seed={seed}", f"output_dir={out}",
               f"weights_dir_base={weights}", "training.wandb=False"]
        log(hlog, f"[seed {seed}] cd {eea / 'src'} && {' '.join(cmd)}")
        t0 = time.time()
        with open(out / "run.log", "w") as f:
            rc = subprocess.run(cmd, cwd=eea / "src", env=env, stdout=f, stderr=subprocess.STDOUT).returncode
        sd.mkdir(parents=True, exist_ok=True)
        collect(out, sd)
        (sd / "status.json").write_text(json.dumps({"seed": seed, "rc": rc, "seconds": round(time.time() - t0),
                                                    "cmd": cmd, "smoke": smoke}, indent=2))
        if rc == 0:
            (sd / "DONE").touch()
        log(hlog, f"[seed {seed}] exit {rc} after {round(time.time() - t0)} s")
        return rc

    seeds = cell["seeds"][:1] if smoke else cell["seeds"]
    with ThreadPoolExecutor(int(cell.get("parallel", 1))) as ex:   # 1 = sequential (default)
        rcs = list(ex.map(run_seed, seeds))
    t["runs"] = time.time()
    keys = list(t)
    timing = {f"{b}_s": round(t[b] - t[a]) for a, b in zip(keys, keys[1:], strict=False)}
    (ckpt / "harness.json").write_text(json.dumps({"rcs": dict(zip(seeds, rcs, strict=True)), **timing,
                                                   "overrides": overrides}, indent=2))
    log(hlog, f"[done] exit codes {rcs}; timing {timing}")
    # the checkpoint uploader adds and removes *.sagemaker-uploaded markers while we copy (race)
    shutil.copytree(ckpt, Path(args.model_dir).expanduser() / cell["id"], dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("*.sagemaker-uploaded"))
    return 0 if not any(rcs) else 1


if __name__ == "__main__":
    raise SystemExit(main())
