#!/usr/bin/env python3
"""D25-E1: markdown table + figure from e1_compare.json (written by e1_compare_released.py).

    .venv/bin/python scripts/analysis/e1_report.py artifacts/analysis/E1
"""

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

d = Path(sys.argv[1])
r = json.loads((d / "e1_compare.json").read_text())
lines = ["# D25-E1: released CHB-MIT preprocessing vs our stores", "",
         "Rule (pre-registered, notes/completeness-audit.md E1): the draft's \"reproduces\" claims stand "
         "only if counts match exactly and max|diff| <= 1e-5 relative.", "",
         "| claim | released script | draft | match |", "|---|---|---|---|"]
lines += [f"| {k} | {v['released']} | {v['draft']} | {'yes' if v['match'] else 'NO'} |"
          for k, v in r["checks"].items()]
ek, ev, sk, sv = r["eval_keys"], r["eval_values"], r["ssl"], r["ssl_values"]
lines += ["", "| split | files | positives | -s- files | short (<2560) |", "|---|---|---|---|---|"]
lines += [f"| {s} | {v['files']} | {v['pos']} | {v['s_files']} | {v['short']} |"
          for s, v in r["released_eval"]["by_split"].items()]
lines += ["", f"Eval keys: ours {ek['ours_total']}, released {ek['released_total']}, common {ek['common']}, "
          f"only ours {ek['n_only_ours']}, only released {ek['n_only_released']}, split mismatches "
          f"{ek['split_mismatch']}, label mismatches {ek['label_mismatch']}.",
          f"Eval values ({ev['n']} seeded windows, compared after the released loader's FFT resample): "
          f"max|diff| {ev['max_abs']:.3g} uV, max relative {ev['max_rel']:.3g}, over tol {ev['n_rel_over_tol']}.",
          f"SSL LMDB: released len(__keys__) {sk['released_len_keys']}, entries-1 "
          f"{sk['released_lmdb_entries_minus_keys']}, duplicates {sk['released_duplicate_keys']}; "
          f"ours {sk['ours_n']}; "
          f"common {sk['common']}, only ours {sk['n_only_ours']}, only released {sk['n_only_released']}; "
          f"files released {sk['released_files']} / ours {sk['our_files']}.",
          f"SSL values ({sv['n']} seeded windows): max|diff| {sv['max_abs']:.3g} uV, max relative "
          f"{sv['max_rel']:.3g}, over tol {sv['n_rel_over_tol']}.",
          f"process1 recordings: {r['process1_total_recordings']} over {len(r['process1'])} cases.", "",
          f"**Verdict:** counts exact = {r['verdict']['counts_exact']}, values within 1e-5 = "
          f"{r['verdict']['values_within_tol']} -> draft claims stand = "
          f"{r['verdict']['draft_reproduces_claims_stand']}."]
(d / "E1.md").write_text("\n".join(lines) + "\n")

fig, ax = plt.subplots(1, 2, figsize=(9, 3.2))
for a, name, title in ((ax[0], "eval_rel_diffs.npy", "eval windows (10 s)"),
                       (ax[1], "ssl_rel_diffs.npy", "SSL windows (30 s)")):
    x = np.load(d / name)
    if not x.any():
        title += ": all diffs exactly 0 (drawn at 1e-12)"
    x = np.log10(np.maximum(x, 1e-12))
    a.hist(x, bins=50, color="C0")
    a.axvline(-5, color="r", ls="--", lw=1, label="tolerance 1e-5")
    a.set(title=f"{title}, n={len(x)}", xlabel="log10(max|ours - released| / max|released|) per window",
          ylabel="windows")
    a.legend(fontsize=8)
fig.suptitle("D25-E1: our stores vs the released preprocessing outputs", fontsize=9)
fig.tight_layout()
fig.savefig(d / "e1_value_diffs.png", dpi=130)
print((d / "E1.md").read_text())
