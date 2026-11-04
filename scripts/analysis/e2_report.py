#!/usr/bin/env python3
"""D25-E2: one table over the E2 runs (status.tsv + logs), the param counts and the E2(d) check.

Run where the raw logs are (desktop). Writes <out>/E2.md, e2_runs.json and <out>/logs/*.log:
log EXCERPTS (command, parameter-count lines, epoch metrics, traceback frames and exception
messages). Traceback source lines and the Hydra config dump are dropped, so no upstream (GPL)
text lands in the MIT repo; frames are cited as file:line only.

    python -I e2_report.py ~/released/e2 ~/released/e2/report
"""

import json
import re
import shutil
import sys
from pathlib import Path

d, out = Path(sys.argv[1]), Path(sys.argv[2])
(out / "logs").mkdir(parents=True, exist_ok=True)
for f in ("status.tsv", "param_counts.json", "e2d_strict_load.json", "ssl_4174.json"):
    if (d / f).exists():
        shutil.copy(d / f, out / f)

KEEP = re.compile(r"^(CMD:|Applying method|printing stats|Initial step_up|Starting Step-Up|Frozen parameters"
                  r"|.*Unfrozen for SPT|.*additionally unfrozen|\[\w+ SPT layer=|SPT Epoch \d+/\d+: Avg"
                  r"|Epoch \d+ Loss|.*Test Metrics|Error executing job|Traceback|[\w.]+(Error|Exception)\b"
                  r"|Could not append|Either remove|Or add a second)")
INDENTED_OK = re.compile(r"^(\s+File \"|\t|\s+(full_key|object_type|reference_type)"
                         r"|\s+(Trainable|Frozen) parameters)")


def excerpt(text: str) -> list[str]:
    keep = []
    for raw in text.splitlines():
        for ln in raw.split("\r"):          # tqdm redraws
            if (ln[:1].isspace() and INDENTED_OK.match(ln)) or (not ln[:1].isspace() and KEEP.match(ln)):
                keep.append(ln.rstrip())
    return keep


status = {}
for ln in (d / "status.tsv").read_text().splitlines():
    name, rc, sec = ln.split("\t")
    status[name] = (int(rc), int(sec))
counts = json.loads((d / "param_counts.json").read_text()) if (d / "param_counts.json").exists() else {}
ERR = re.compile(r"^([\w.]+(?:Error|Exception)): (.*)\n((?:\t.*\n)*)", re.M)
HYDRA = re.compile(r"^(Could not append to config\..*)$", re.M)
FRAME = re.compile(r'File "[^"]*/(?:eea|eea_l29)/src/([^"]+)", line (\d+), in (\w+)')
FINAL = re.compile(r"Final Test Metrics \(Last Epoch\): (\{.*\})")
rows = ["| run | exit | min | first failure (exception: message) | last released frame (file:line in fn) "
        "| SPT trainable (sum over printed names) | paper count | final test (last epoch) |",
        "|---|---|---|---|---|---|---|---|"]
res = {}
for name in sorted(status):
    t = (d / "logs" / f"{name}.log").read_text(errors="replace")
    (out / "logs" / f"{name}.log").write_text("\n".join(excerpt(t)) + "\n")
    rc, sec = status[name]
    err = ERR.findall(t)
    msg = (f"{err[0][0]}: {err[0][1]} {err[0][2].strip()}".strip() if err else
           (HYDRA.findall(t) or [""])[0] or ("timeout (5400 s)" if rc == 124 else ""))
    frames = FRAME.findall(t)
    where = f"{frames[-1][0]}:{frames[-1][1]} in {frames[-1][2]}" if frames and rc else ""
    fin = FINAL.findall(t)
    c = counts.get(name, {})
    tr = c.get("sum_numel_printed_names") or ""
    rows.append(f"| {name} | {rc} | {sec / 60:.0f} | {msg[:160].replace('|', '/')} | {where} | {tr} | "
                f"{c.get('paper') or ''} | {fin[-1] if fin else ''} |")
    res[name] = {"exit": rc, "seconds": sec, "error": msg or None, "where": where or None,
                 "spt_trainable": tr or None, "paper": c.get("paper"), "match": c.get("match"),
                 "final_test": fin[-1] if fin else None}
md = ["# D25-E2: the documented commands, run on CPU in the clone", "",
      "Data: 2,100-pickle symlink farm of the E1 released processed_seg (train 1500/100 pos, val 300/50, "
      "test 300/50, seed 2); SSL store: 4,174-key LMDB in the released pickle format (our parity subset, "
      "seed 4174). Paths, output_dir, weights_dir_base and training.wandb=False are Hydra overrides; "
      "nothing in the clone is edited (PYTHONDONTWRITEBYTECODE=1). `d_l29_*` run from a /tmp copy with "
      "model_factory.py:29 uncommented (the `#` removed, nothing else). Exit 124 = killed by the 90-min CPU "
      "timeout. Metrics are a CPU smoke on 2K windows: descriptive only.", ""]
md += rows
if (d / "e2d_strict_load.json").exists():
    e = json.loads((d / "e2d_strict_load.json").read_text())
    md += ["", "E2(d) 10-line check: strict load of a full CBraMod state_dict into a backbone with "
           f"proj_out = Identity -> {e['strict_load']}: `{' '.join(e.get('error', '').split())}`"]
(out / "E2.md").write_text("\n".join(md) + "\n")
(out / "e2_runs.json").write_text(json.dumps(res, indent=2))
print("\n".join(md))
