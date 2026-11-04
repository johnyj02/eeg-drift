#!/usr/bin/env python3
"""D25-E2(b): count the SSL-trainable parameters the released runs actually unfroze.

Reads the E2 run logs, collects the parameter names the released trainer printed as unfrozen
("Unfrozen for SPT: <name>", "additionally unfrozen: <name>") plus its own count lines
("Trainable parameters: N", "[... SPT layer=...] trainable=N"), and sums numel over the printed
names on the released model classes (imported from the clone at run time; nothing copied).

    ~/released/eea-env/bin/python e2_param_counts.py --clone ~/released/eea --logs ~/released/e2/logs \
        --out ~/released/e2/param_counts.json
"""

import argparse
import json
import re
import sys
from pathlib import Path

PAPER = {("biot", "last1"): 920_576, ("biot", "last2"): 1_709_568,
         ("cbramod", "last1"): 442_800, ("cbramod", "last2"): 845_400}
NAME = re.compile(r"(?:Unfrozen for SPT|additionally unfrozen): (\S+)")
COUNT = re.compile(r"Trainable parameters: ([\d,]+)")
LAYER = re.compile(r"\[(\w+) SPT layer=(\w+)\] trainable=([\d,]+)")

ap = argparse.ArgumentParser()
ap.add_argument("--clone", required=True)
ap.add_argument("--logs", required=True)
ap.add_argument("--out", required=True)
args = ap.parse_args()
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(args.clone) / "src"))
from models.biot import UnsupervisedPretrain  # noqa: E402  (released modules)
from models.cbramod import CBraMod  # noqa: E402

models = {"biot": UnsupervisedPretrain(emb_size=256, heads=8, depth=4, n_channels=18),
          "cbramod": CBraMod(200, 200, 200, 800, 30, 12, 8)}
numel = {k: {n: p.numel() for n, p in m.named_parameters()} for k, m in models.items()}
rows = {}
for log in sorted(Path(args.logs).glob("*.log")):
    text = log.read_text(errors="replace")
    model = "cbramod" if "model=cbramod" in text.splitlines()[0] else "biot"
    names = sorted(set(NAME.findall(text)))
    layer = LAYER.findall(text)
    mode = layer[0][1] if layer else ("last1" if names else None)
    row = {"model": model, "n_names": len(names),
           "sum_numel_printed_names": sum(numel[model][n] for n in names) if names else None,
           "trainable_lines": [int(c.replace(",", "")) for c in COUNT.findall(text)],
           "layer_trainable_line": int(layer[0][2].replace(",", "")) if layer else None, "mode": mode}
    if names and mode:
        row["paper"] = PAPER.get((model, mode))
        row["match"] = row["sum_numel_printed_names"] == row["paper"]
    rows[log.stem] = row
Path(args.out).write_text(json.dumps(rows, indent=2))
print(json.dumps(rows, indent=2))
