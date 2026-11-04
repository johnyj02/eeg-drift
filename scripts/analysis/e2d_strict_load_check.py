#!/usr/bin/env python3
"""D25-E2(d): does the released SA transfer survive `backbone.proj_out = nn.Identity()`?

Runs in the RELEASED env against the clone (imports its modules at run time; nothing copied):

    ~/released/eea-env/bin/python e2d_strict_load_check.py --clone ~/released/eea [--ckpt W]

Builds the released CBraMod twice: the SPT model (full, as trainer.setup_cbramod_spt builds it)
and the probe backbone with proj_out replaced by Identity (model_factory.py:29 uncommented), then
strict-loads the SPT state_dict into the backbone exactly as trainer.py:309 does. Also shows the
model_factory.py:27 pretrained load (before the Identity swap) still works.
"""

import argparse
import json
import os
import sys
import traceback

import torch
from torch import nn

ap = argparse.ArgumentParser()
ap.add_argument("--clone", default=os.path.expanduser("~/released/eea"))
ap.add_argument("--ckpt", default="")
ap.add_argument("--out", default="")
args = ap.parse_args()
sys.path.insert(0, os.path.join(args.clone, "src"))
from models.cbramod import CBraMod  # noqa: E402  (released module)

kw = dict(in_dim=200, out_dim=200, d_model=200, dim_feedforward=800, seq_len=30, n_layer=12, nhead=8)
res = {}
spt = CBraMod(**kw)
backbone = CBraMod(**kw)
if args.ckpt:
    backbone.load_state_dict(torch.load(args.ckpt, map_location="cpu"))  # model_factory.py:27
    res["pretrained_load_before_identity"] = "ok"
backbone.proj_out = nn.Identity()                                          # model_factory.py:29
try:
    backbone.load_state_dict(spt.state_dict())                             # trainer.py:309
    res["strict_load"] = "ok"
except RuntimeError as e:
    res["strict_load"] = "raised"
    res["error"] = str(e)
    res["traceback"] = traceback.format_exc()
print(json.dumps(res, indent=2))
if args.out:
    with open(args.out, "w") as f:
        json.dump(res, f, indent=2)
