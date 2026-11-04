#!/usr/bin/env python3
"""D25-E21: table + figure from the "E21 {...}" lines that tests/test_released_differential.py prints.

    .venv/bin/python scripts/analysis/e21_report.py artifacts/analysis/E21 pytest_desktop.log pytest_mac.log
"""

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

d = Path(sys.argv[1])
lines = ["# D25-E21: our reimplementation vs the released modules (same process, same start state)", "",
         "Rule (notes/completeness-audit.md E21): equality within 1e-5 supports \"runs exactly this path\". "
         "Asserted: SSL step losses, adapted weights, probe loss, head weights, test logits (relative), "
         "test metrics under the released scoring (float32 sigmoid), input transform (relative). "
         "`ssl_update_rel` = max|update difference| / max|update|. `native` = our own scoring (raw logits, "
         "PROBE_CODE_VERSION 3) vs released, descriptive.", ""]
rows = {}
for log in sys.argv[2:]:
    recs = [json.loads(ln[4:]) for ln in (d / log).read_text().splitlines() if ln.startswith("E21 ")]
    result = [ln for ln in (d / log).read_text().splitlines() if " passed" in ln or " failed" in ln]
    lines += [f"## {log}: {result[-1].strip() if result else 'no summary line'}", "",
              "| model | head | start | max asserted diff | ssl_update_rel | ROC released | ROC ours (native) "
              "| native ROC diff |", "|---|---|---|---|---|---|---|---|"]
    for r in recs:
        m = r["maxdiff"]
        worst = max(v for k, v in m.items() if k not in ("ssl_moved", "ssl_update_rel"))
        lines.append(f"| {r['model']} | {r['variant']} | {r['init']} | {worst:.2g} | {m['ssl_update_rel']:.2g} | "
                     f"{r['roc_released']:.4f} | {r['roc_ours']:.4f} | {r['descriptive']['roc_auc_native']:.4f} |")
        rows[(log, r["model"], r["variant"], r["init"])] = r
    lines.append("")
(d / "E21.md").write_text("\n".join(lines) + "\n")

first = sys.argv[2]
cases = [k for k in rows if k[0] == first]
fig, ax = plt.subplots(figsize=(8, 3.2))
x = range(len(cases))
ax.bar([i - 0.2 for i in x], [rows[k]["roc_released"] for k in cases], 0.4, label="released (float32 sigmoid)")
ax.bar([i + 0.2 for i in x], [rows[k]["roc_ours"] for k in cases], 0.4, label="ours (raw logits)")
ax.set_xticks(list(x), [f"{k[1]}\n{k[2]}\n{k[3]}" for k in cases], fontsize=7)
ax.set(ylabel="test ROC-AUC (synthetic data)", title=f"E21: identical logits, scoring convention only ({first})")
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig(d / "e21_roc_scoring.png", dpi=130)
print((d / "E21.md").read_text())
