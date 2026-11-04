#!/usr/bin/env python3
"""D25-E14 no-op check: did SSL adaptation change the encoder? Pre-registered stop rule (E14).

    .venv/bin/python scripts/analysis/noop.py

Rule (notes/completeness-audit.md E14, adopted by D25): a (lp, last) or (lp_randinit, last_randinit)
pair at the same seed with Pearson r = 1 AND max |score difference| < 1e-6 is a bug: stop and
investigate. Otherwise report "weights moved X%, scores r = Y".
Scope as written: per-window test scores (val-selected epoch, `scores_best`) of P1E (both heads), S1M
and S1E. Siena (S3M+S3E, S3FM+S3FE) is added as a descriptive extension. From the records of every
adapted run in the same tags: steps, epoch losses (first vs kept), lr_sum, displacement rel and
coherence per group, and a check that groups outside the arm did not move.
Writes artifacts/analysis/noop/{noop.md, noop.json, *.png}.
"""

from __future__ import annotations

import json
import subprocess
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "artifacts" / "s3-results"
OUT = ROOT / "artifacts" / "analysis" / "noop"
SETTINGS = {"P1E": "chbmit paper split (P1E)", "S1M": "chbmit rotations (S1M+S1E)",
            "S1E": "chbmit rotations (S1M+S1E)", "S3M": "siena rotations (S3M+S3E)",
            "S3E": "siena rotations (S3M+S3E)", "S3FM": "siena filtered (S3FM+S3FE)",
            "S3FE": "siena filtered (S3FM+S3FE)"}
PRIMARY = ("chbmit paper split (P1E)", "chbmit rotations (S1M+S1E)")
PAIRS = (("lp", "last"), ("lp_randinit", "last_randinit"))
INK, INK2, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#fcfcfb"
ARM_COLOR = {"last": "#eb6834", "last_randinit": "#1baf7a", "all": "#e87ba4"}


def style(ax, title: str = "", ylabel: str = "") -> None:
    ax.set_facecolor(SURF)
    ax.grid(color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    for k in ("top", "right"):
        ax.spines[k].set_visible(False)
    ax.tick_params(colors=INK2, labelsize=7)
    ax.set_title(title, fontsize=8, color=INK, loc="left")
    ax.set_ylabel(ylabel, fontsize=8, color=INK2)


def load() -> tuple[dict, list[dict]]:
    """(setting, model, split, seed, head, arm) -> (record, npz path); plus all adapted records."""
    runs, adapted = {}, []
    for p in sorted(RES.rglob("results/*.json")):
        if p.name.startswith(("diag-", "test-index-", "val-index-", "report-")):
            continue
        r = json.loads(p.read_text())
        setting = SETTINGS.get(r.get("run_tag", ""))
        if r.get("smoke") or setting is None:
            continue
        r["_setting"] = setting
        if "adapt" in r:
            adapted.append(r)
        for head in r["probes"]:
            k = (setting, r["model"], r["split"], r["seed"], head, r["arm"])
            if k in runs:
                raise SystemExit(f"two records for {k}")
            runs[k] = (r, p.parent / f"{r['key']}.{head}.npz")
    return runs, adapted


def rerun_groups() -> dict:
    """Every adapted record in s3-results (all tags) grouped by its full AdaptSpec."""
    g = defaultdict(list)
    for p in sorted(RES.rglob("results/*.json")):
        if p.name.startswith(("diag-", "test-index-", "val-index-", "report-")):
            continue
        r = json.loads(p.read_text())
        if r.get("smoke") or "adapt" not in r:
            continue
        g[json.dumps([r["arm"], r["split"], r["adapt_spec"]], sort_keys=True)].append(
            (r.get("run_tag", ""), r["adapt"]["epoch_losses"], r["displacement"]))
    return {k: v for k, v in g.items() if len(v) > 1}


def pair_rows(runs: dict) -> list[dict]:
    rows = []
    for (setting, model, split, seed, head, arm), (ra, pa) in sorted(runs.items()):
        for a, b in PAIRS:
            if arm != a or (setting, model, split, seed, head, b) not in runs:
                continue
            rb, pb = runs[(setting, model, split, seed, head, b)]
            if ra["eval_hash"] != rb["eval_hash"]:
                raise SystemExit(f"{ra['key']} vs {rb['key']}: different test sets")
            A, B = np.load(pa), np.load(pb)
            if not np.array_equal(A["y_test"], B["y_test"]):
                raise SystemExit(f"{ra['key']} vs {rb['key']}: different test labels")
            row = {"setting": setting, "model": model, "split": split, "seed": seed, "head": head,
                   "pair": f"{a} vs {b}", "n": int(len(A["y_test"])),
                   "roc_a": 100 * ra["probes"][head]["test_at_best"]["roc_auc"],
                   "roc_b": 100 * rb["probes"][head]["test_at_best"]["roc_auc"],
                   "epoch_a": ra["probes"][head]["best_epoch"], "epoch_b": rb["probes"][head]["best_epoch"]}
            for which in ("scores_best", "scores_last"):
                x, y = A[which].astype(np.float64), B[which].astype(np.float64)
                row[f"r_{which}"] = float(np.corrcoef(x, y)[0, 1])
                row[f"maxabs_{which}"] = float(np.max(np.abs(x - y)))
            row["bug"] = bool(row["r_scores_best"] >= 1 - 1e-12 and row["maxabs_scores_best"] < 1e-6)
            rows.append(row)
    return rows


def adapt_rows(adapted: list[dict]) -> list[dict]:
    rows = []
    for r in adapted:
        a, disp, arm_groups = r["adapt"], r["displacement"], set(r["arm_spec"]["groups"])
        moved_outside = sorted(g for g, v in disp.items() if g not in arm_groups and v["abs"] != 0)
        frozen_inside = sorted(g for g, v in disp.items() if g in arm_groups and v["abs"] == 0)
        per_epoch = -(-r["adapt_spec"]["n_windows"] // r["adapt_spec"]["batch"])
        losses = a["epoch_losses"]
        main = [g for g in r["arm_spec"]["groups"] if g != "head"][-1]   # the adapted block (last of arm)
        rows.append({
            "setting": r["_setting"], "model": r["model"], "arm": r["arm"], "split": r["split"],
            "seed": r["seed"], "key": r["key"], "steps": a["steps"],
            "planned_steps": r["adapt_spec"]["epochs"] * per_epoch,
            "best_epoch": a["best_epoch"], "steps_to_kept": per_epoch * (a["best_epoch"] + 1),
            "skipped_nonfinite": a["skipped_nonfinite"], "loss_first": losses[0],
            "loss_kept": losses[a["best_epoch"]],
            "loss_change_pct": 100 * (losses[a["best_epoch"]] / losses[0] - 1), "lr_sum": a["lr_sum"],
            "main_group": main, "rel_main_pct": 100 * disp[main]["rel"], "coh_main": disp[main].get("coherence"),
            "rel_head_pct": 100 * disp["head"]["rel"], "coh_head": disp["head"].get("coherence"),
            "decay_baseline_pct": 100 * r["decay_baseline"],
            "epoch_losses": losses, "rel_by_group_pct": {g: 100 * v["rel"] for g, v in disp.items()},
            "coh_by_group": {g: v.get("coherence") for g, v in disp.items()},
            "moved_outside_arm": moved_outside, "unmoved_inside_arm": frozen_inside})
    return rows


def rng_str(v) -> str:
    v = np.asarray(v, dtype=float)
    return f"{np.median(v):.4g} [{v.min():.4g}, {v.max():.4g}]"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    runs, adapted = load()
    pairs, arows = pair_rows(runs), adapt_rows(adapted)
    cache_hits = subprocess.run(["grep", "-rIn", "-i", "--include=*.py", "cache", str(ROOT / "src" / "eegdrift")],
                                capture_output=True, text=True).stdout.strip()
    bugs = [p for p in pairs if p["bug"]]
    bad_groups = [a for a in arows if a["moved_outside_arm"] or a["unmoved_inside_arm"]]
    reruns = rerun_groups()
    unequal = {k: v for k, v in reruns.items() if len({json.dumps(x[1:]) for x in v}) > 1}
    md = ["# E14 no-op check: did SSL adaptation change the encoder?", "",
          "<!-- generated by scripts/analysis/noop.py; D25-E14 -->", "",
          "Rule (pre-registered, E14): Pearson r = 1 with max|Δ| < 1e-6 between the per-window test scores "
          "of lp and last (or lp_randinit and last_randinit) at the same seed is a bug (stop, investigate). "
          "Scores = logits at the validation-selected epoch (`scores_best`). Primary scope as written: P1E "
          "(both heads), S1M, S1E. Siena rows are a descriptive extension.", "",
          "## Verdict", ""]
    md.append(f"- pairs checked: {len(pairs)} ({sum(p['setting'] in PRIMARY for p in pairs)} in the "
              f"pre-registered scope); flagged by the stop rule: **{len(bugs)}**"
              + (" -> STOP, investigate: " + ", ".join(
                  f"{b['model']}/{b['split']}/s{b['seed']}/{b['head']}/{b['pair']}" for b in bugs)
                 if bugs else " -> no bug flagged; no CPU re-adaptation needed"))
    md.append(f"- adapted records: {len(arows)}; groups outside the arm that moved, or arm groups that did "
              f"not move: **{len(bad_groups)}**" + (f" ({[b['key'] for b in bad_groups]})" if bad_groups else ""))
    combos = sorted({" = ".join(sorted({x[0] or "wave1" for x in v})) for v in reruns.values()})
    md.append(f"- determinism (descriptive): {len(reruns)} identical AdaptSpecs were run under 2 or more run tags "
              f"({'; '.join(combos)}); epoch losses and displacement differ in **{len(unequal)}**"
              + (f": {sorted(unequal)}" if unequal else ": the same spec and seed reproduce the adapted weights' "
                 "statistics exactly, so paired probe differences across these tags come from the probe alone"))
    md.append("- feature cache: none. `grep -rIni cache src/eegdrift/*.py` "
              + (f"finds: {cache_hits}" if cache_hits else "finds nothing")
              + ". Reading the code: study.run_arm_seed builds `model`, adapt() trains it in place and reloads "
                "the lowest-loss epoch into model.module, and the same object goes to parity_probe, which "
                "recomputes model.features on every training batch and in _scores; nothing is reused across arms.")
    summary: dict = {}
    for setting in dict.fromkeys(SETTINGS.values()):
        for model in ("biot", "cbramod"):
            for arm in ("last", "last_randinit"):
                A = [a for a in arows if a["setting"] == setting and a["model"] == model and a["arm"] == arm]
                P = [p for p in pairs if p["setting"] == setting and p["model"] == model
                     and p["pair"].endswith(f" vs {arm}")]
                if not A or not P:
                    continue
                s = {"n_adapted": len(A), "n_pairs": len(P),
                     "rel_main_pct": [a["rel_main_pct"] for a in A], "r": [p["r_scores_best"] for p in P],
                     "maxabs": [p["maxabs_scores_best"] for p in P]}
                summary[f"{setting}/{model}/{arm}"] = s
                md.append(f"- {setting}, {model} {arm}: weights moved {np.median(s['rel_main_pct']):.2f}% "
                          f"(relative displacement of {A[0]['main_group']}, median over {len(A)} runs; range "
                          f"{min(s['rel_main_pct']):.2f}-{max(s['rel_main_pct']):.2f}%), scores r = "
                          f"{np.median(s['r']):.4f} (range {min(s['r']):.4f}-{max(s['r']):.4f}; "
                          f"smallest max|Δ| {min(s['maxabs']):.3g}) vs its unadapted pair")
    md += ["", "## Adaptation records per (setting, model, arm)", "",
           "| setting | model | arm | n | steps (planned) | kept epoch counts | steps to kept "
           "| SSL loss first -> kept (median %) | lr_sum | rel. displacement block % | coherence block "
           "| rel. displacement head % | weight-decay-only baseline % | skipped non-finite |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    groups = defaultdict(list)
    for a in arows:
        groups[(a["setting"], a["model"], a["arm"])].append(a)
    for (setting, model, arm), A in groups.items():
        ke = defaultdict(int)
        for a in A:
            ke[a["best_epoch"]] += 1
        md.append(f"| {setting} | {model} | {arm} | {len(A)} | {sorted({a['steps'] for a in A})} "
                  f"({sorted({a['planned_steps'] for a in A})}) | {dict(sorted(ke.items()))} | "
                  f"{rng_str([a['steps_to_kept'] for a in A])} | "
                  f"{rng_str([a['loss_first'] for a in A])} -> {rng_str([a['loss_kept'] for a in A])} "
                  f"({np.median([a['loss_change_pct'] for a in A]):+.1f}%) | "
                  f"{rng_str([a['lr_sum'] for a in A])} | "
                  f"{rng_str([a['rel_main_pct'] for a in A])} ({A[0]['main_group']}) | "
                  f"{rng_str([a['coh_main'] for a in A])} | {rng_str([a['rel_head_pct'] for a in A])} | "
                  f"{rng_str([a['decay_baseline_pct'] for a in A])} | {sum(a['skipped_nonfinite'] for a in A)} |")
    md += ["", "For `all`, the block column is the last encoder block; per-group values for every run are in "
           "noop.json (rel_by_group_pct, coh_by_group).", "",
           "## Score pairs per (setting, model, head, pair)", "",
           "| setting | model | head | pair | n pairs | Pearson r (best) | max abs Δ (best) "
           "| Pearson r (last epoch) | ROC a -> b, mean Δ | flagged |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    pg = defaultdict(list)
    for p in pairs:
        pg[(p["setting"], p["model"], p["head"], p["pair"])].append(p)
    for (setting, model, head, pair), P in pg.items():
        md.append(f"| {setting} | {model} | {head} | {pair} | {len(P)} | "
                  f"{rng_str([p['r_scores_best'] for p in P])} | "
                  f"{rng_str([p['maxabs_scores_best'] for p in P])} | "
                  f"{rng_str([p['r_scores_last'] for p in P])} | "
                  f"{np.mean([p['roc_b'] - p['roc_a'] for p in P]):+.2f} | {sum(p['bug'] for p in P)} |")
    md += ["", "## Per pair (pre-registered scope)", "",
           "| setting | model | split | seed | head | pair | r best | max abs Δ best | ROC a | ROC b "
           "| epochs a/b |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for p in pairs:
        if p["setting"] in PRIMARY:
            md.append(f"| {p['setting']} | {p['model']} | {p['split']} | {p['seed']} | {p['head']} | "
                      f"{p['pair']} | {p['r_scores_best']:.5f} | {p['maxabs_scores_best']:.4g} | "
                      f"{p['roc_a']:.2f} | {p['roc_b']:.2f} | {p['epoch_a']}/{p['epoch_b']} |")
    (OUT / "noop.md").write_text("\n".join(md) + "\n")
    (OUT / "noop.json").write_text(json.dumps({"pairs": pairs, "adapted": arows, "summary": summary,
                                               "flagged": bugs, "group_violations": bad_groups,
                                               "rerun_groups": len(reruns), "rerun_unequal": sorted(unequal),
                                               "cache_grep": cache_hits}, indent=1))
    figures(runs, pairs, arows)
    print("\n".join(md[:40]))
    return 2 if bugs else 0


def figures(runs: dict, pairs: list[dict], arows: list[dict]) -> None:
    # 1. scatter of paired scores, one example seed per setting
    ex = [("chbmit paper split (P1E)", "paper", 42), ("chbmit rotations (S1M+S1E)", "rot0", 42)]
    fig, axes = plt.subplots(2, 4, figsize=(13, 6.5), facecolor=SURF)
    for i, model in enumerate(("biot", "cbramod")):
        for j, ((setting, split, seed), (a, b)) in enumerate([(e, pr) for e in ex for pr in PAIRS]):
            ax = axes[i, j]
            ra, pa = runs[(setting, model, split, seed, "linear", a)]
            rb, pb = runs[(setting, model, split, seed, "linear", b)]
            A, B = np.load(pa), np.load(pb)
            y = A["y_test"].astype(bool)
            x1, x2 = A["scores_best"], B["scores_best"]
            ax.scatter(x1[~y], x2[~y], s=1, alpha=0.25, color="#2a78d6", rasterized=True, label="label 0")
            ax.scatter(x1[y], x2[y], s=3, alpha=0.6, color="#eb6834", rasterized=True, label="label 1")
            lim = [min(x1.min(), x2.min()), max(x1.max(), x2.max())]
            ax.plot(lim, lim, color=MUTED, lw=0.8, ls=":")
            r = np.corrcoef(x1, x2)[0, 1]
            style(ax, f"{model} {split} s{seed}: {a} vs {b}", f"{b} logit")
            ax.set_xlabel(f"{a} logit", fontsize=8, color=INK2)
            ax.text(0.03, 0.95, f"r = {r:.4f}\nmax|Δ| = {np.max(np.abs(x1 - x2)):.3g}", transform=ax.transAxes,
                    va="top", fontsize=7, color=INK)
    axes[0, 0].legend(fontsize=7, frameon=False, loc="lower right", markerscale=4)
    fig.suptitle("E14 per-window test logits, unadapted vs adapted encoder (same seed, linear head)", fontsize=10,
                 color=INK, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(OUT / "noop-scores-scatter.png", dpi=150)
    plt.close(fig)
    # 2. summary strips: r per group, displacement per group
    settings = list(dict.fromkeys(SETTINGS.values()))
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8), facecolor=SURF)
    labels, pos = [], 0
    for setting in settings:
        for model in ("biot", "cbramod"):
            for arm in ("last", "last_randinit"):
                P = [p["r_scores_best"] for p in pairs if p["setting"] == setting and p["model"] == model
                     and p["pair"].endswith(f" vs {arm}")]
                A = [a for a in arows if a["setting"] == setting and a["model"] == model and a["arm"] == arm]
                if not P:
                    continue
                jit = np.linspace(-0.15, 0.15, len(P))
                axes[0].scatter(pos + jit, P, s=10, color=ARM_COLOR[arm])
                axes[1].scatter(pos + np.linspace(-0.15, 0.15, len(A)), [a["rel_main_pct"] for a in A], s=10,
                                color=ARM_COLOR[arm])
                axes[1].scatter([pos + 0.3], [np.median([a["decay_baseline_pct"] for a in A])], marker="_", s=80,
                                color=INK)
                labels.append(f"{setting.split(' (')[0]}\n{model} {arm}")
                pos += 1
    style(axes[0], "Pearson r of per-window logits, unadapted vs adapted (1 = identical)", "r")
    style(axes[1], "relative displacement of the adapted block, % (black tick: weight-decay-only baseline)",
          "||Δθ|| / ||θ0||, %")
    for ax in axes:
        ax.set_xticks(range(len(labels)), labels, fontsize=5.5, rotation=60, ha="right")
    axes[0].axhline(1, color=MUTED, lw=0.8, ls=":")
    fig.tight_layout()
    fig.savefig(OUT / "noop-summary.png", dpi=150)
    plt.close(fig)
    # 3. SSL loss per epoch, every adapted run
    fig, axes = plt.subplots(2, len(settings), figsize=(13, 6), facecolor=SURF, sharex=True)
    for i, model in enumerate(("biot", "cbramod")):
        for j, setting in enumerate(settings):
            ax = axes[i, j]
            style(ax, f"{model}: {setting}", "SSL loss (epoch mean)" if j == 0 else "")
            for a in [r for r in arows if r["model"] == model and r["setting"] == setting]:
                ls = a["epoch_losses"]
                ax.plot(range(1, len(ls) + 1), ls, color=ARM_COLOR.get(a["arm"], MUTED), lw=0.8, alpha=0.7)
                ax.scatter([a["best_epoch"] + 1], [ls[a["best_epoch"]]], s=8, color=ARM_COLOR.get(a["arm"], MUTED))
            ax.set_yscale("log")
            ax.set_xticks([1, 2, 3])
            ax.set_xlabel("epoch (dot = kept)", fontsize=7, color=INK2)
    handles = [plt.Line2D([], [], color=c, label=k) for k, c in ARM_COLOR.items()]
    handles.append(plt.Line2D([], [], color=MUTED, label="other S1E/S3E arms (first, first_block, ...)"))
    axes[1, 1].legend(handles=handles, fontsize=7, frameon=False, loc="center right")
    fig.suptitle("E14 SSL adaptation loss per epoch, every adapted run (log scale)", fontsize=10, color=INK,
                 x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(OUT / "noop-ssl-loss.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    raise SystemExit(main())
