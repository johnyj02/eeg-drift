#!/usr/bin/env python3
"""E20-free (notes/completeness-audit.md, adopted by D25): hand-crafted baseline and robustness
re-scores of the D24-A records. Pre-registered rule: descriptive, appendix.

Baseline. Per window and channel, on the eval-store window the probes see ([16, 2000] at 200 Hz,
before /100): log band power delta 0.5-4, theta 4-8, alpha 8-13, beta 13-30, gamma 30-45 Hz
(periodogram; 45 Hz keeps the 50 and 60 Hz mains out), log line length (mean |dx|) and log
variance: 16 x 7 = 112 features. Standardized on train, logistic regression, C chosen on
validation ROC-AUC, same train/val/test windows and labels as the probes (study.load_eval):
rotations with overlap labels (train grid + add, val/test grid only), and the paper split with
upstream labels (P1E's protocol) and with overlap labels (P1F's protocol, descriptive).

Re-scores of the D24-A records (S1E+S1M, S3E+S3M, S3FE+S3FM; linear head; the D24-A contrasts):
paired AP and PR lift (AP / prevalence) per rotation; ROC from scores_last; ROC with >=50%-
overlap test labels (a window is positive iff >= 5 of its 10 s are in a seizure). D18-form
strings on these are descriptive. Balanced accuracy at a validation threshold needs validation
scores, which only E25 saves: computed for the baseline only.

  # desktop (stores). Throwaway venv (the /tmp/dxtest-overlay sklearn/torch is gone):
  #   ~/dxenv/bin/python -m venv /tmp/eegd-an-venv && /tmp/eegd-an-venv/bin/pip install --only-binary=:all: \
  #       scikit-learn==1.6.1 numpy==2.2.4 scipy==1.15.2 mne lmdb pyyaml
  # python = /tmp/eegd-an-venv/bin/python; the script puts <repo>/src on sys.path itself.
  PYTHONPATH=~/EEGDrift/src python scripts/analysis/handcrafted_baseline.py extract \
      --lmdb ~/dxdata/lmdb --work /tmp/eegd-analysis/handcrafted
  PYTHONPATH=~/EEGDrift/src python scripts/analysis/handcrafted_baseline.py fit \
      --work /tmp/eegd-analysis/handcrafted       # writes <work>/fit/*.json|npz
  # Mac, after copying <work>/fit to artifacts/analysis/handcrafted/fit
  .venv/bin/python scripts/analysis/handcrafted_baseline.py report
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from multiprocessing import Pool
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "2")  # before numpy: many single-threaded workers
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from eegdrift.data.chbmit import overlap_label  # noqa: E402
from eegdrift.data.index import rotations  # noqa: E402

OUT = ROOT / "artifacts" / "analysis" / "handcrafted"
RESULTS = ROOT / "artifacts" / "s3-results"
FS = 200
BANDS = ((0.5, 4), (4, 8), (8, 13), (13, 30), (30, 45))
FEATS = ("delta", "theta", "alpha", "beta", "gamma", "line_length", "variance")
EPS = 1e-6
# First run used 1e-4..100; validation picked the lower edge (1e-4) in 5 of 17 fits, so the grid
# was extended downward (a validation-driven change, made after the first run's test values were
# printed; that run is kept in fit-grid1e-4/ and summarized in the report).
GRID = (1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0)
ROTS = tuple(f"rot{i}" for i in range(5))
# setting -> (dataset, eval store under the lmdb root, D24-A run tags)
SETTINGS = {
    "chbmit": ("chbmit", "chbmit_eval10", ("S1E", "S1M")),
    "siena": ("siena", "siena/siena_eval10", ("S3E", "S3M")),
    "siena_filt": ("siena", "siena_filt/siena_eval10", ("S3FE", "S3FM")),
}
WIN = {"chbmit": 2560, "siena": 5120}  # 10 s in native samples (the seizure tables' units)
ARMS = ("lp", "lp_randinit", "last", "last_randinit", "all")
CONTRASTS = (("last", "lp"), ("last_randinit", "last"), ("lp", "lp_randinit"))
MODELS = ("biot", "cbramod")


# ---------------------------------------------------------------- features (desktop)
def window_features(x: np.ndarray) -> np.ndarray:
    """[n, 16, T] uV at 200 Hz -> [n, 16, 7] log features (FEATS order)."""
    x = x.astype(np.float64)
    p = np.abs(np.fft.rfft(x, axis=-1)) ** 2
    f = np.fft.rfftfreq(x.shape[-1], 1 / FS)
    cols = [p[..., (f >= lo) & (f < hi)].sum(-1) for lo, hi in BANDS]
    cols += [np.abs(np.diff(x, axis=-1)).mean(-1), x.var(-1)]
    return np.log(np.stack(cols, -1) + EPS).astype(np.float32)


def _chunk(job: tuple[str, str, tuple, list[str], str]) -> str:
    """Features of `keys` -> <out>.npy (skipped if present, so a killed run resumes)."""
    import lmdb  # noqa: PLC0415  (desktop only)

    path, dtype, shape, keys, out_path = job
    if Path(out_path).exists():
        return out_path
    env = lmdb.open(path, readonly=True, lock=False, subdir=True, readahead=True, meminit=False)
    out = np.empty((len(keys), 16, len(FEATS)), np.float32)
    with env.begin() as txn:
        for a in range(0, len(keys), 256):
            x = np.stack([np.frombuffer(txn.get(k.encode()), dtype).reshape(shape) for k in keys[a : a + 256]])
            out[a : a + len(x)] = window_features(x)
    env.close()
    np.save(out_path + ".tmp.npy", out)
    os.replace(out_path + ".tmp.npy", out_path)
    return out_path


def extract(args) -> None:
    from eegdrift.data.windows import WindowStore  # noqa: PLC0415

    work = Path(args.work)
    (work / "chunks").mkdir(parents=True, exist_ok=True)
    for setting, (_, store, _) in SETTINGS.items():
        if (work / f"features-{setting}.npz").exists():
            continue
        path = str(Path(args.lmdb).expanduser() / store)
        st = WindowStore(path)
        n = len(st)
        keys = [r["key"] for r in st.index]
        order = sorted(range(n), key=lambda i: keys[i].encode())  # LMDB key order: sequential reads
        step = 2048
        jobs = [
            (
                path,
                st.dtype.str,
                st.shape,
                [keys[i] for i in order[a : a + step]],
                str(work / "chunks" / f"{setting}-{a // step:05d}.npy"),
            )
            for a in range(0, n, step)
        ]
        with Pool(args.workers) as pool:
            for j, _ in enumerate(pool.imap_unordered(_chunk, jobs), 1):
                if j % 20 == 0 or j == len(jobs):
                    print(f"[extract] {setting}: {j}/{len(jobs)} chunks", flush=True)
        X = np.empty((n, 16, len(FEATS)), np.float32)
        X[np.array(order)] = np.concatenate([np.load(job[4]) for job in jobs])
        meta = {
            k: np.array([str(r.get(k) or "") for r in st.index]) for k in ("key", "case", "kind", "file", "split")
        }
        meta |= {k: np.array([int(r[k]) for r in st.index]) for k in ("start", "n_samples", "label")}
        np.savez(work / f"features-{setting}.npz", X=X, **{f"m_{k}": v for k, v in meta.items()})
        print(f"[extract] {setting}: {n} windows from {path}", flush=True)


# ---------------------------------------------------------------- splits and labels
def overlap_frac(file: str, start: int, n: int, table: dict) -> float:
    """Share of [start, start + n) inside any seizure (TRUE [onset, offset) bounds)."""
    return sum(max(0, min(start + n, b) - max(start, a)) for a, b in table.get(file, [])) / n


def seizures(dataset: str) -> dict:
    return json.loads((ROOT / "configs" / f"{dataset}_seizures.json").read_text())


def parts(meta, dataset: str, split: str, labels: str) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """part -> (positions, y), exactly as study.load_eval selects and labels them."""
    import yaml  # noqa: PLC0415

    rot = yaml.safe_load((ROOT / "configs" / "data.yaml").read_text())[dataset]["rotations"]
    if split == "paper":
        part = meta["split"]
    else:
        cs = rotations(sorted(set(meta["case"].tolist())), rot["n_folds"], rot["seed"])[int(split[3:])]
        part = np.array([cs[c] for c in meta["case"]])
    table = seizures(dataset)
    out = {}
    for p in ("train", "val", "test"):
        keep = (part == p) & ((meta["kind"] == "grid") | (labels == "upstream") | (p == "train"))
        pos = np.flatnonzero(keep)
        y = (
            meta["label"][pos]
            if labels == "upstream"
            else np.array(
                [
                    overlap_label(
                        {
                            "file": meta["file"][i],
                            "start": int(meta["start"][i]),
                            "n_samples": int(meta["n_samples"][i]),
                        },
                        table,
                    )
                    for i in pos
                ]
            )
        )
        out[p] = (pos, y.astype(int))
    return out


def label50(keys, dataset: str) -> np.ndarray:
    """>=50%-overlap labels for grid keys '<file>-grid-<start>' (native samples)."""
    table = seizures(dataset)
    out = []
    for k in keys:
        file, _, start = k.rsplit("-", 2)
        out.append(int(overlap_frac(file, int(start), WIN[dataset], table) >= 0.5))
    return np.array(out)


# ---------------------------------------------------------------- metrics
def metrics(y, s, thr: float = 0.0) -> dict:
    """The probe's binary metrics (eegdrift.probe.metrics, without the torch import) + PR lift."""
    from sklearn.metrics import (  # noqa: PLC0415
        auc,
        average_precision_score,
        balanced_accuracy_score,
        precision_recall_curve,
        roc_auc_score,
    )

    precision, recall, _ = precision_recall_curve(y, s, pos_label=1)
    ap = float(average_precision_score(y, s))
    return {
        "bal_acc": float(balanced_accuracy_score(y, (s > thr).astype(int))),
        "roc_auc": float(roc_auc_score(y, s)),
        "pr_auc_trapz": float(auc(recall, precision)),
        "avg_precision": ap,
        "prevalence": float(np.mean(y)),
        "pr_lift": ap / float(np.mean(y)),
        "n": int(len(y)),
        "n_pos": int(np.sum(y)),
    }


def youden_threshold(y, s) -> float:
    """Threshold maximizing balanced accuracy (TPR - FPR) on validation; applied as s >= t."""
    from sklearn.metrics import roc_curve  # noqa: PLC0415

    fpr, tpr, thr = roc_curve(y, s)
    return float(thr[int(np.argmax(tpr - fpr))])


# ---------------------------------------------------------------- fit (desktop)
def fit_one(job: tuple[str, str, str, str]) -> str:
    from sklearn.linear_model import LogisticRegression  # noqa: PLC0415
    from sklearn.metrics import roc_auc_score  # noqa: PLC0415
    from sklearn.preprocessing import StandardScaler  # noqa: PLC0415

    work, setting, split, labels = job
    dataset = SETTINGS[setting][0]
    d = np.load(Path(work) / f"features-{setting}.npz")
    meta = {k[2:]: d[k] for k in d.files if k.startswith("m_")}
    X3 = d["X"]
    X = X3.reshape(len(X3), -1)
    P = parts(meta, dataset, split, labels)
    sc = StandardScaler().fit(X[P["train"][0]])
    Z = {p: sc.transform(X[pos]) for p, (pos, _) in P.items()}
    y = {p: v for p, (_, v) in P.items()}
    curve, best = [], None
    for C in GRID:
        clf = LogisticRegression(C=C, max_iter=5000).fit(Z["train"], y["train"])
        s = {p: clf.decision_function(Z[p]) for p in Z}
        row = {
            "C": C,
            "n_iter": int(clf.n_iter_[0]),
            "train_roc": float(roc_auc_score(y["train"], s["train"])),
            "val_roc": float(roc_auc_score(y["val"], s["val"])),
            "test_roc_plot_only": float(roc_auc_score(y["test"], s["test"])),
        }  # never selects
        curve.append(row)
        if best is None or row["val_roc"] > best[0]["val_roc"]:  # ties keep the smaller C
            best = (row, clf, s)
    row, clf, s = best
    t = youden_threshold(y["val"], s["val"])
    test = metrics(y["test"], s["test"])
    test["bal_acc_val_threshold"] = float(
        np.mean(
            [
                np.mean(s["test"][y["test"] == c] >= t) if c else np.mean(s["test"][y["test"] == c] < t)
                for c in (0, 1)
            ]
        )
    )
    keys = {p: meta["key"][pos] for p, (pos, _) in P.items()}
    # zero-parameter line length: channel mean of the raw (un-logged) line length, no fitting
    ll = {p: np.exp(X3[pos][:, :, FEATS.index("line_length")]).mean(1) for p, (pos, _) in P.items()}
    rec = {
        "setting": setting,
        "dataset": dataset,
        "split": split,
        "labels": labels,
        "C": row["C"],
        "curve": curve,
        "val": metrics(y["val"], s["val"]),
        "test": test,
        "val_threshold": t,
        "counts": {p: [int(len(v)), int(v.sum())] for p, v in y.items()},
        "line_length_zero_param": {p: metrics(y[p], ll[p]) for p in ("val", "test")},
        "top_coef": sorted(
            ((f"{FEATS[i % 7]}@ch{i // 7}", float(c)) for i, c in enumerate(clf.coef_[0])),
            key=lambda kv: -abs(kv[1]),
        )[:12],
    }
    if labels == "overlap":
        y50 = label50(keys["test"], dataset)
        rec["test_label50"] = metrics(y50, s["test"])
        rec["line_length_zero_param"]["test_label50"] = metrics(y50, ll["test"])
    name = f"{setting}-{split}-{labels}"
    out = Path(work) / "fit"
    out.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        out / f"{name}.npz",
        key_val=keys["val"],
        y_val=y["val"],
        s_val=s["val"],
        key_test=keys["test"],
        y_test=y["test"],
        s_test=s["test"],
        ll_test=ll["test"],
        coef=clf.coef_[0],
    )
    (out / f"{name}.json").write_text(json.dumps(rec, indent=1))
    return f"{name}: C={row['C']} val {row['val_roc']:.4f} test {test['roc_auc']:.4f}"


def fit(args) -> None:
    jobs = [(args.work, s, r, "overlap") for s in SETTINGS for r in ROTS]
    jobs += [(args.work, "chbmit", "paper", "upstream"), (args.work, "chbmit", "paper", "overlap")]
    with Pool(min(args.workers, len(jobs))) as pool:
        for msg in pool.imap_unordered(fit_one, sorted(jobs, key=lambda j: j[1] != "chbmit")):
            print("[fit]", msg, flush=True)


# ---------------------------------------------------------------- model records (Mac)
def model_runs(dataset: str, tags: set[str], split_kind: str = "rot") -> dict:
    """(model, arm, split, seed, head) -> per-run metrics from the saved test scores, checked
    against the record. Refuses non-v4 / non-eval / duplicate records (as read_d24.load)."""
    from sklearn.metrics import roc_auc_score  # noqa: PLC0415

    out: dict = {}
    index_cache: dict = {}
    for p in sorted(RESULTS.rglob("results/*.json")):
        if p.name.startswith(("diag-", "test-index-", "report-")):
            continue
        r = json.loads(p.read_text())
        if (
            r.get("smoke")
            or r["dataset"] != dataset
            or r.get("run_tag") not in tags
            or not r["split"].startswith(split_kind)
        ):
            continue
        heads = ("linear",) if split_kind == "rot" else tuple(r["probes"])
        ip = p.parent / r["test_index"]
        if ip not in index_cache:
            index_cache[ip] = [t["key"] for t in json.loads(ip.read_text())]
        keys = index_cache[ip]
        for head in heads:
            res = r["probes"][head]
            if r["versions"]["probe"] != 4 or res["spec"].get("backbone_mode") != "eval":
                raise SystemExit(f"{p.name}: not a probe-v4 eval-mode record")
            cell = (r["model"], r["arm"], r["split"], r["seed"], head)
            if cell in out:
                raise SystemExit(f"two records for {cell}")
            z = np.load(p.with_name(f"{p.stem}.{head}.npz"))
            y, sb, sl = z["y_test"].astype(int), z["scores_best"], z["scores_last"]
            m = {"roc_best": roc_auc_score(y, sb), "roc_last": roc_auc_score(y, sl)}
            for k, ref in (
                ("roc_best", res["test_at_best"]["roc_auc"]),
                ("roc_last", res["test_last"]["roc_auc"]),
            ):
                if abs(m[k] - ref) > 1e-6:
                    raise SystemExit(f"{p.name} {head}: {k} {m[k]:.6f} from scores != record {ref:.6f}")
            if split_kind == "rot":
                mb = metrics(y, sb)
                m |= {
                    "ap_best": mb["avg_precision"],
                    "lift_best": mb["pr_lift"],
                    "roc50_best": roc_auc_score(label50(keys, dataset), sb),
                }
            out[cell] = {k: 100 * v if k != "lift_best" else v for k, v in m.items()} | {
                "keys": keys,
                "y": y,
                "path": str(p.relative_to(ROOT)),
            }
    return out


def rot_means(runs: dict, model: str, arm: str, metric: str, head: str = "linear") -> list[float] | None:
    """Per-rotation mean over the 3 D24-A seeds; None unless every rotation has exactly 3."""
    cells = [
        [v[metric] for (m, a, s, _, h), v in runs.items() if (m, a, s, h) == (model, arm, r, head)] for r in ROTS
    ]
    return [float(np.mean(c)) for c in cells] if all(len(c) == 3 for c in cells) else None


def ms(v) -> str:
    v = np.asarray(v, dtype=float)
    return f"{v.mean():.1f} ± {v.std(ddof=1) / np.sqrt(len(v)):.1f}"


# ---------------------------------------------------------------- report (Mac)
def report(args) -> None:
    import matplotlib  # noqa: PLC0415

    matplotlib.use("Agg")
    from read_step1 import d17, paired  # noqa: PLC0415

    fitdir = Path(args.fit)
    fits = {p.stem: json.loads(p.read_text()) for p in sorted(fitdir.glob("*.json"))}
    arr = {p.stem: np.load(p) for p in sorted(fitdir.glob("*.npz"))}
    expected = [f"{s}-{r}-overlap" for s in SETTINGS for r in ROTS] + [
        "chbmit-paper-upstream",
        "chbmit-paper-overlap",
    ]
    missing = [e for e in expected if e not in fits]
    if missing:
        raise SystemExit(f"missing fit outputs: {missing}")
    runs = {s: model_runs(ds, set(tags)) for s, (ds, _, tags) in SETTINGS.items()}
    p1e = model_runs("chbmit", {"P1E"}, split_kind="paper")

    # the baseline must score exactly the probes' test windows, in the same order, with the same labels
    checks = []
    for s, rr in runs.items():
        for r in ROTS:
            a = arr[f"{s}-{r}-overlap"]
            run = next(v for (m, _, sp, _, _), v in rr.items() if sp == r)
            if list(a["key_test"]) != run["keys"] or not np.array_equal(a["y_test"], run["y"]):
                raise SystemExit(f"{s} {r}: baseline test windows/labels differ from the probes'")
            checks.append(
                f"{s}/{r}: {len(run['keys'])} test windows, {int(run['y'].sum())} positives = probe test set"
            )
    a, run = arr["chbmit-paper-upstream"], next(iter(p1e.values()))
    if list(a["key_test"]) != run["keys"] or not np.array_equal(a["y_test"], run["y"]):
        raise SystemExit("paper split: baseline test windows/labels differ from P1E's")
    checks.append(
        f"chbmit/paper upstream labels: {len(run['keys'])} test windows, {int(run['y'].sum())} "
        "positives = P1E test set"
    )

    L = [
        "# E20-free: hand-crafted baseline and robustness re-scores (descriptive, appendix; D25)",
        "",
        "Pre-registered rule (completeness-audit E20-free): **descriptive, appendix**. No verdict is drawn;",
        "D18-form strings below are descriptive re-readings, the D24 verdicts stay primary.",
        "",
        "Baseline: log band power (delta 0.5-4, theta 4-8, alpha 8-13, beta 13-30, gamma 30-45 Hz), log line",
        "length and log variance per channel (112 features) -> standardized logistic regression, C from "
        f"{list(GRID)} by validation ROC-AUC. ROC/AP x100; PR lift = AP / prevalence.",
        "",
        "## Checks",
        *[f"- {c}" for c in checks],
        f"- every model ROC recomputed from the saved scores equals its record (|diff| <= 1e-6): "
        f"{sum(len(v) for v in runs.values()) + len(p1e)} run-heads",
        "",
    ]

    # 1. baseline per split
    L += [
        "## 1. Baseline per split (test)",
        "",
        "| setting | split | labels | C | val ROC | test ROC | AP | PR lift | bal-acc @0.5 | bal-acc @val thr "
        "| ROC, >=50% labels | test n / pos |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for name in expected:
        f = fits[name]
        t = f["test"]
        l50 = f"{100 * f['test_label50']['roc_auc']:.1f}" if "test_label50" in f else "-"
        L.append(
            f"| {f['setting']} | {f['split']} | {f['labels']} | {f['C']:g} | {100 * f['val']['roc_auc']:.1f} | "
            f"{100 * t['roc_auc']:.1f} | {100 * t['avg_precision']:.1f} | {t['pr_lift']:.1f} | "
            f"{100 * t['bal_acc']:.1f} | {100 * t['bal_acc_val_threshold']:.1f} | {l50} | "
            f"{t['n']} / {t['n_pos']} |"
        )
    L.append("")
    for s in SETTINGS:
        v = [100 * fits[f"{s}-{r}-overlap"]["test"]["roc_auc"] for r in ROTS]
        L.append(f"- {s}: baseline test ROC over rotations {ms(v)} (mean ± SEM, n=5)")
    L += [
        "- Reference: cbramod-check §4 reported 91.2 for log band power + LR (C=0.01, 5 bands incl. 30-70 Hz,",
        "  train = paper-train cases with negatives subsampled to 3,000, test = chb21-24); not the same windows.",
        "",
    ]
    first = fitdir.parent / "fit-grid1e-4"
    if first.exists():
        L += [
            "### C-grid sensitivity: first run (C 1e-4..100) vs final grid (1e-6..100)",
            "",
            "| fit | C, first | test ROC, first | C, final | test ROC, final |",
            "|---|---|---|---|---|",
        ]
        for name in expected:
            f1, f2 = json.loads((first / f"{name}.json").read_text()), fits[name]
            L.append(
                f"| {name} | {f1['C']:g} | {100 * f1['test']['roc_auc']:.1f} | {f2['C']:g} | "
                f"{100 * f2['test']['roc_auc']:.1f} |"
            )
        L.append("")

    # 2. baseline vs models per rotation
    L += ["## 2. Baseline vs probes per rotation (test ROC x100; probes = mean of the 3 D24-A seeds)", ""]
    hc = {s: [100 * fits[f"{s}-{r}-overlap"]["test"]["roc_auc"] for r in ROTS] for s in SETTINGS}
    for s in SETTINGS:
        L += [
            f"### {s}",
            "",
            "| row | " + " | ".join(ROTS) + " | mean ± SEM | arm - baseline: mean, rotations > 0 |",
            "|---|" + "---|" * 7,
            f"| hand-crafted LR | {' | '.join(f'{x:.1f}' for x in hc[s])} | {ms(hc[s])} | |",
        ]
        for m in MODELS:
            for arm in ARMS:
                v = rot_means(runs[s], m, arm, "roc_best")
                if v:
                    d = np.subtract(v, hc[s])
                    L.append(
                        f"| {m} {arm} | {' | '.join(f'{x:.1f}' for x in v)} | {ms(v)} | "
                        f"{d.mean():+.1f}, {int((d > 0).sum())}/5 |"
                    )
        L.append("")

    # 3. paper split
    L += [
        "## 3. Paper split (test chb23-24): P1E arms vs the baseline (test ROC x100, mean ± SEM over 5 seeds)",
        "",
        "| row | linear head | mlp_fullft head |",
        "|---|---|---|",
    ]
    for m in MODELS:
        for arm in ("lp", "last", "lp_randinit", "last_randinit"):
            cell = [
                ms([v["roc_best"] for (mm, a, _, _, h), v in p1e.items() if (mm, a, h) == (m, arm, head)])
                for head in ("linear", "mlp_fullft")
            ]
            L.append(f"| {m} {arm} | {cell[0]} | {cell[1]} |")
    for lab in ("upstream", "overlap"):
        f = fits[f"chbmit-paper-{lab}"]
        L.append(f"| hand-crafted LR, {lab} labels | {100 * f['test']['roc_auc']:.1f} (one fit) | |")
    L += [
        "",
        "P1E uses upstream labels with the oversampled windows kept in test (the paper's protocol); the "
        "overlap-label row uses the corrected labels (grid windows only in val/test), as P1F will.",
        "",
    ]

    # 4. robustness re-scores of the D24-A contrasts
    L += [
        "## 4. Robustness re-scores of the D24-A contrasts (linear head; per-rotation seed means)",
        "",
        "Primary = ROC at the val-selected epoch with >=1-sample overlap labels (the D24-A reading). Re-scores:",
        "ROC from scores_last; ROC with >=50%-overlap test labels; AP x100 and PR lift (paired per rotation).",
        "Strings apply the D18 form (|mean| > 3, sign in >= 4/5) and are descriptive; AP and lift get no string.",
        "Balanced accuracy at a validation-chosen threshold: NOT computed for the probes (no validation",
        "scores before E25).",
        "",
        "| setting | model | contrast | primary ROC | ROC, scores_last | ROC, >=50% labels | AP x100 | PR lift | "
        "string changes vs primary |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    robust: dict = {}
    for s in SETTINGS:
        for m in MODELS:
            for a, b in (*CONTRASTS, ("last_randinit", "lp_randinit")):
                cells, strings = [], []
                for metric in ("roc_best", "roc_last", "roc50_best", "ap_best", "lift_best"):
                    A, B = rot_means(runs[s], m, a, metric), rot_means(runs[s], m, b, metric)
                    d = np.subtract(A, B)
                    robust[(s, m, a, b, metric)] = d
                    pos = f"{int((d > 0).sum())}/5 > 0"
                    if metric.startswith("roc"):
                        st = d17(A, B) if a == "last_randinit" and b == "lp_randinit" else paired(d)
                        strings.append(st)
                        cells.append(f"{d.mean():+.1f} ({pos}) {st}")
                    else:
                        cells.append(
                            f"{d.mean():+.2f} ({pos})" if metric == "lift_best" else f"{d.mean():+.1f} ({pos})"
                        )
                change = ", ".join(
                    n for n, st in zip(("last", ">=50%"), strings[1:], strict=True) if st != strings[0]
                )
                L.append(
                    f"| {s} | {m} | {'D17 ' if b == 'lp_randinit' and a == 'last_randinit' else ''}{a} - {b} | "
                    + " | ".join(cells)
                    + f" | {change or 'none'} |"
                )
    L.append("")
    L += [
        "### Per-rotation paired differences (x100; AP in AP points, lift in lift units)",
        "",
        "| setting | model | contrast | metric | " + " | ".join(ROTS) + " |",
        "|---|---|---|---|" + "---|" * 5,
    ]
    for (s, m, a, b, metric), d in robust.items():
        fmt = "{:+.2f}" if metric == "lift_best" else "{:+.1f}"
        L.append(f"| {s} | {m} | {a} - {b} | {metric} | " + " | ".join(fmt.format(x) for x in d) + " |")
    text = "\n".join(L) + "\n"
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "handcrafted.md").write_text(text)
    (OUT / "handcrafted.json").write_text(
        json.dumps(
            {
                "baseline": fits,
                "robust": {"|".join(k): list(map(float, v)) for k, v in robust.items()},
                "probe_rot_means": {
                    f"{s}|{m}|{arm}|{metric}": rot_means(runs[s], m, arm, metric)
                    for s in SETTINGS
                    for m in MODELS
                    for arm in ARMS
                    for metric in ("roc_best", "roc_last", "roc50_best", "ap_best", "lift_best")
                },
                "p1e": {"|".join(map(str, k)): v["roc_best"] for k, v in p1e.items()},
            },
            indent=1,
        )
    )
    figures(fits, arr, runs, robust, hc)
    print(text)


def figures(fits, arr, runs, robust, hc) -> None:
    import matplotlib.pyplot as plt  # noqa: PLC0415
    from sklearn.metrics import roc_curve  # noqa: PLC0415

    ink, muted = "#0b0b0b", "#52514e"
    c1, c2, c3, c4, c5 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"
    plt.rcParams.update(
        {
            "font.size": 8,
            "axes.edgecolor": muted,
            "axes.labelcolor": ink,
            "xtick.color": muted,
            "ytick.color": muted,
            "axes.grid": True,
            "grid.color": "#e4e3df",
            "grid.linewidth": 0.6,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "legend.frameon": False,
        }
    )

    # C sweep: train vs validation ROC (test plot-only), the baseline's "training vs validation" curve
    rows = [*SETTINGS, "paper"]
    fig, axes = plt.subplots(len(rows), 5, figsize=(13, 9), sharex=True, sharey="row")
    for i, s in enumerate(rows):
        names = (
            [f"{s}-{r}-overlap" for r in ROTS]
            if s != "paper"
            else ["chbmit-paper-upstream", "chbmit-paper-overlap"]
        )
        for j in range(5):
            ax = axes[i, j]
            if j >= len(names):
                ax.set_visible(False)
                continue
            f = fits[names[j]]
            C = [c["C"] for c in f["curve"]]
            ax.plot(C, [100 * c["train_roc"] for c in f["curve"]], color=c1, lw=2, marker="o", ms=4, label="train")
            ax.plot(
                C, [100 * c["val_roc"] for c in f["curve"]], color=c2, lw=2, marker="o", ms=4, label="validation"
            )
            ax.plot(
                C,
                [100 * c["test_roc_plot_only"] for c in f["curve"]],
                color=c3,
                lw=1.5,
                ls="--",
                label="test (plot only)",
            )
            ax.axvline(f["C"], color=muted, lw=0.8, ls=":")
            ax.set_xscale("log")
            ax.tick_params(labelbottom=True)
            ax.set_title(f"{f['setting']} {f['split']} ({f['labels']})", color=ink)
            if j == 0:
                ax.set_ylabel("ROC-AUC x100")
            if i == len(rows) - 1:
                ax.set_xlabel("C (inverse L2 strength)")
    fig.legend(*axes[0, 0].get_legend_handles_labels(), loc="lower right", bbox_to_anchor=(0.9, 0.08), fontsize=9)
    fig.suptitle("Hand-crafted LR: train vs validation ROC over C (dotted = C chosen on validation)", color=ink)
    fig.tight_layout()
    fig.savefig(OUT / "fig_c_sweep_train_vs_val.png", dpi=150)
    plt.close(fig)

    # test ROC curves of the baseline
    fig, axes = plt.subplots(1, 4, figsize=(13, 3.4))
    pal = (c1, c2, c3, c4, c5)
    for ax, s in zip(axes, rows, strict=True):
        names = (
            [f"{s}-{r}-overlap" for r in ROTS]
            if s != "paper"
            else ["chbmit-paper-upstream", "chbmit-paper-overlap"]
        )
        for k, n in enumerate(names):
            a = arr[n]
            fpr, tpr, _ = roc_curve(a["y_test"], a["s_test"])
            ax.plot(
                fpr,
                tpr,
                color=pal[k],
                lw=1.5,
                label=f"{n.split('-', 1)[1]} ({100 * fits[n]['test']['roc_auc']:.1f})",
            )
        ax.plot([0, 1], [0, 1], color=muted, lw=0.8, ls=":")
        ax.set_title(s, color=ink)
        ax.set_xlabel("false positive rate")
        ax.legend(loc="lower right", fontsize=6.5)
    axes[0].set_ylabel("true positive rate")
    fig.suptitle("Hand-crafted LR: test ROC curves", color=ink)
    fig.tight_layout()
    fig.savefig(OUT / "fig_roc_curves.png", dpi=150)
    plt.close(fig)

    # baseline vs probes per rotation
    fig, axes = plt.subplots(2, 3, figsize=(12, 6), sharey=True)
    x = np.arange(5)
    for i, m in enumerate(MODELS):
        for j, s in enumerate(SETTINGS):
            ax = axes[i, j]
            ax.plot(x, hc[s], color=ink, lw=0, marker="s", ms=8, label="hand-crafted LR")
            for k, (arm, col, mk) in enumerate((("lp", c1, "o"), ("last", c2, "^"), ("lp_randinit", c3, "D"))):
                v = rot_means(runs[s], m, arm, "roc_best")
                ax.plot(
                    x + 0.12 * (k + 1),
                    v,
                    color=col,
                    lw=0,
                    marker=mk,
                    ms=7,
                    label=arm,
                    markeredgecolor="white",
                    markeredgewidth=1,
                )
            ax.set_xticks(x + 0.2, ROTS)
            ax.set_title(f"{m}, {s}", color=ink)
            if j == 0:
                ax.set_ylabel("test ROC-AUC x100")
    fig.legend(*axes[0, 0].get_legend_handles_labels(), loc="lower center", ncol=4)
    fig.suptitle("Hand-crafted baseline vs frozen / adapted probes (3-seed means per rotation)", color=ink)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(OUT / "fig_baseline_vs_probes.png", dpi=150)
    plt.close(fig)

    # robustness: per-contrast mean difference under each scoring, per-rotation points
    fig, axes = plt.subplots(2, 3, figsize=(12, 6), sharey=True)
    variants = (("roc_best", "primary", c1), ("roc_last", "scores_last", c2), ("roc50_best", ">=50% labels", c3))
    cons = (*CONTRASTS, ("last_randinit", "lp_randinit"))
    for i, m in enumerate(MODELS):
        for j, s in enumerate(SETTINGS):
            ax = axes[i, j]
            for k, (metric, lab, col) in enumerate(variants):
                for c, (a, b) in enumerate(cons):
                    d = robust[(s, m, a, b, metric)]
                    xx = c + (k - 1) * 0.22
                    ax.scatter(np.full(5, xx), d, s=10, color=col, alpha=0.45, linewidths=0)
                    ax.plot(
                        [xx - 0.08, xx + 0.08], [d.mean()] * 2, color=col, lw=2.5, label=lab if c == 0 else None
                    )
            ax.axhline(0, color=muted, lw=0.8)
            for t in (3, -3):
                ax.axhline(t, color=muted, lw=0.6, ls=":")
            ax.set_xticks(range(len(cons)), [f"{a}\n- {b}" for a, b in cons], fontsize=6.5)
            ax.set_title(f"{m}, {s}", color=ink)
            if j == 0:
                ax.set_ylabel("paired ROC difference x100")
    axes[0, 0].legend(loc="upper left")
    fig.suptitle("D24-A contrasts re-scored (bar = mean over rotations, dots = rotations, dotted = ±3)", color=ink)
    fig.tight_layout()
    fig.savefig(OUT / "fig_robustness_contrasts.png", dpi=150)
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("extract")
    e.add_argument("--lmdb", required=True)
    e.add_argument("--work", required=True)
    e.add_argument("--workers", type=int, default=48)
    f = sub.add_parser("fit")
    f.add_argument("--work", required=True)
    f.add_argument("--workers", type=int, default=17)
    r = sub.add_parser("report")
    r.add_argument("--fit", default=str(OUT / "fit"))
    args = ap.parse_args()
    {"extract": extract, "fit": fit, "report": report}[args.cmd](args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
