#!/usr/bin/env python3
"""D25-E2: per-epoch curves from the released runs' own stdout (descriptive; CPU smoke data).

Parses the lines the released trainers print: "SPT Epoch e/E: Avg Loss=..., LR=...",
"Epoch e Loss: L Val roc_auc: V", "New Best Val! Test Metrics: {...}" and
"Final Test Metrics (Last Epoch): {...}". One figure per completed run, plus curves.json.

    .venv/bin/python scripts/analysis/e2_plot_curves.py artifacts/analysis/E2/logs artifacts/analysis/E2
"""

import ast
import json
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SPT = re.compile(r"SPT Epoch (\d+)/(\d+): Avg Loss=([-\d.e+naninf]+), LR=([-\d.e+]+)")
EP = re.compile(r"^Epoch (\d+) Loss: ([-\d.e+naninf]+) Val (\w+): ([-\d.e+naninf]+)", re.M)
FINAL = re.compile(r"Final Test Metrics \(Last Epoch\): (\{.*\})")


def metrics(text: str) -> dict:
    return {k: float(v) for k, v in ast.literal_eval(re.sub(r"np\.float64\(([^)]*)\)", r"\1", text)).items()}


def main(logs: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    allc = {}
    for log in sorted(logs.glob("*.log")):
        t = log.read_text(errors="replace")
        spt = [(int(e), float(loss), float(lr)) for e, _, loss, lr in SPT.findall(t)]
        ep = [(int(e), float(loss), m, float(v)) for e, loss, m, v in EP.findall(t)]
        final = FINAL.findall(t)
        if not ep:
            continue
        c = {"spt": spt, "epochs": ep, "final_test": metrics(final[-1]) if final else None}
        allc[log.stem] = c
        fig, ax = plt.subplots(1, 3 if spt else 2, figsize=(12 if spt else 8, 3.2))
        i = 0
        if spt:
            ax[0].plot([s[0] for s in spt], [s[1] for s in spt], "o-")
            ax[0].set(title="SSL (SPT) epoch mean loss", xlabel="SPT epoch", ylabel="loss")
            i = 1
        ax[i].plot([e[0] for e in ep], [e[1] for e in ep], "o-", color="C1")
        ax[i].set(title="probe train loss", xlabel="probe epoch", ylabel="BCE")
        ax[i + 1].plot([e[0] for e in ep], [e[3] for e in ep], "o-", color="C2", label=f"val {ep[0][2]}")
        if c["final_test"]:
            ax[i + 1].axhline(c["final_test"]["roc_auc"], ls="--", color="k", lw=0.8, label="test (last)")
        ax[i + 1].set(title="validation", xlabel="probe epoch", ylabel=ep[0][2])
        ax[i + 1].legend(fontsize=8)
        fig.suptitle(f"{log.stem} (released code, CPU, 2K-window farm; descriptive)", fontsize=9)
        fig.tight_layout()
        fig.savefig(out / f"curves_{log.stem}.png", dpi=120)
        plt.close(fig)
    (out / "curves.json").write_text(json.dumps(allc, indent=2))
    print(f"{len(allc)} runs with probe epochs -> {out}")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
