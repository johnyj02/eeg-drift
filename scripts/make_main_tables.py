#!/usr/bin/env python3
"""Regenerate the numbers of the paper's main tables from the saved records and check them against the LaTeX.

    .venv/bin/python scripts/make_main_tables.py                     # this repository
    python scripts/make_main_tables.py                               # the supplement folder (same layout)

CPU only, no window stores, no per-window scores, no window indices; about 10 s. Tables, found by label in
any paper/tmlr/sections/*.tex (--tex; without the sources, e.g. in the supplement, cells are UNCHECKED):
  tab:original   DL Table 1 against the released code and our runs (DL's split; the headline comparison)
  tab:d24a       revised-protocol contrasts (D24-A) and DL's split (D24-B): means, 95% t-intervals, rules
  tab:p1e        DL's split, arm levels and SA gain for the linear, shipped MLP and standardized heads
  tab:robust     SSL adaptation gain under every control (rows matched by the id in their label, e.g. "(E25)")
  tab:artifacts  the values of the release-issue table that come from saved records
Records: artifacts/s3-results/<unit>/results/*.json (our pipeline) and artifacts/released-root/ (the
released-code runs). ROC read only through scripts/read_d24.load (probe v4, eval mode, duplicate and
mixed-eval guards); wave-1 records (probe v2, released-code probe) and PR-AUC are read directly.
Rules: read_step1.paired (F/S/N), d17 (R), d19 (G/P/unclear); E29 firing = e29_dose_response.fires.
Each generated cell is compared with the paper cell as text (whole cell, or a token inside the cell for
tab:artifacts): PASS, FAIL, or SKIP (value not computable from records; reason printed).
Writes artifacts/tables/main/main_tables.{md,json}. Exit 1 on any FAIL.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
import time
from collections import Counter, defaultdict
from functools import cache
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts" / "analysis"), str(ROOT / "scripts" / "released")]
from bootstrap_d24 import cluster_ci  # noqa: E402
from e29_dose_response import fires  # noqa: E402
from read_d24 import CONTRASTS, ROTS, load  # noqa: E402
from read_released import SCREEN, agg  # noqa: E402
from read_released import load as load_released  # noqa: E402
from read_step1 import d17, d19, paired  # noqa: E402

TEX = ROOT / "paper" / "tmlr" / "sections"
OUT = ROOT / "artifacts" / "tables" / "main"
S_R = (42, 123, 2021, 3407, 8888)
SEEDS3 = {r: (S_R[i], 1000 + i, 2000 + i) for i, r in enumerate(ROTS)}
SEEDS1 = {r: (S_R[i],) for i, r in enumerate(ROTS)}
LETTER = {"first term wins": "F", "second term wins": "S", "no difference shown": "N",
          "random features explain it": "R", "SSL adds to random init": "SSL adds", "neither rule met": "neither",
          "the gain needs EEG data": "G", "perturbation alone explains it": "P", "unclear": "unclear"}
SETTINGS = {"CHB-MIT": ("chbmit", "S1", "S1E,S1M"), "Siena": ("siena", "S3", "S3E,S3M"),
            "Siena filt.": ("siena", "S3F", "S3FE,S3FM")}
MODELS = {"BIOT": "biot", "CBraMod": "cbramod"}
INDEX: dict = defaultdict(list)      # (dataset, run_tag) -> record paths
WAVE1: dict = defaultdict(dict)      # (model, arm, probe) -> {seed: (roc, pr)}, untagged probe-v2 paper split
FARM: list = []


class Missing(Exception):
    pass


# ---------- records ----------


def scan(local: Path) -> None:
    for p in local.rglob("results/*.json"):
        if p.name.startswith(("diag-", "test-index-", "val-index-", "report-")):
            continue
        r = json.loads(p.read_text())
        if r.get("smoke"):
            continue
        INDEX[(r["dataset"], r.get("run_tag"))].append(p)
        if not r.get("run_tag") and r["split"] == "paper" and r["versions"]["probe"] == 2:
            for probe, res in r["probes"].items():
                cell = WAVE1[(r["model"], r["arm"], probe)]
                if r["seed"] in cell:
                    raise SystemExit(f"two wave-1 records for {r['model']}/{r['arm']}/{probe} seed {r['seed']}")
                t = res["test_at_best"]
                cell[r["seed"]] = (100 * t["roc_auc"], 100 * t["pr_auc_trapz"])


@cache
def roc(dataset: str, tags: str) -> dict:
    """read_d24.load on a symlink farm of just these tags' records (one scan of the tree, not one per call)."""
    d = Path(tempfile.mkdtemp(dir=FARM[0]))
    for t in tags.split(","):
        for p in INDEX[(dataset, t)]:
            link = d / p.parent.parent.name / "results" / p.name
            link.parent.mkdir(parents=True, exist_ok=True)
            link.symlink_to(p.resolve())
    return load(str(d), dataset, set(tags.split(",")))


def rot(dataset, tags, model, arm, probe="linear", seeds=SEEDS3) -> list[float]:
    """The 5 rotation means over `seeds`."""
    R = roc(dataset, tags)
    out = []
    for r in ROTS:
        c = R.get((model, arm, r, probe), {})
        if not all(s in c for s in seeds[r]):
            raise Missing(f"{dataset} {tags} {model}/{arm}/{probe} {r}: seeds {sorted(c)}, need {seeds[r]}")
        out.append(float(np.mean([c[s] for s in seeds[r]])))
    return out


def paper(tags, model, arm, probe="linear") -> list[float]:
    """DL's split: the 5 seeds in S_R order."""
    c = roc("chbmit", tags).get((model, arm, "paper", probe), {})
    if not all(s in c for s in S_R):
        raise Missing(f"chbmit {tags} {model}/{arm}/{probe} paper: seeds {sorted(c)}")
    return [c[s] for s in S_R]


def wave1(model, arm, probe, k) -> list[float]:
    c = WAVE1.get((model, arm, probe), {})
    if not all(s in c for s in S_R):
        raise Missing(f"wave 1 {model}/{arm}/{probe}: seeds {sorted(c)}")
    return [c[s][k] for s in S_R]


# ---------- numbers and LaTeX text ----------


def d17d(d) -> str:
    """D17 on the per-unit differences last_randinit - lp_randinit (as stats_d25)."""
    return d17(d, [0.0] * len(d))


def diff(a, b) -> list[float]:
    return [x - y for x, y in zip(a, b, strict=True)]


def mse(v) -> tuple[float, float]:
    v = np.asarray(v, dtype=float)
    return float(v.mean()), float(v.std(ddof=1) / np.sqrt(len(v)))


def tint(v) -> tuple[float, float, float]:
    """Mean and 95% t-interval over the units (df n-1)."""
    m, se = mse(v)
    q = stats.t(len(v) - 1).ppf(0.975) * se
    return m, m - q, m + q


def sg(x: float, nd: int = 1) -> str:
    return f"{x:+.{nd}f}".replace("-", "$-$")


def un(x: float, nd: int = 1) -> str:
    return f"{x:.{nd}f}".replace("-", "$-$")


def cell(text: str, **num) -> dict:
    return {"text": text, **num}


def ci_cell(d, rule=None) -> dict:
    m, lo, hi = tint(d)
    letter = LETTER[rule(d)] if rule else None
    return cell(f"{sg(m)} [{sg(lo)}, {sg(hi)}]" + (f" {letter}" if letter else ""),
                mean=m, ci95=[lo, hi], units=d, rule=letter)


def ms_cell(v, nd=1) -> dict:
    m, se = mse(v)
    return cell(f"{un(m, nd)} $\\pm$ {un(se, nd)}", mean=m, sem=se, units=v)


def gain_cell(d, rule=paired) -> dict:
    """Value with its rule letter, e.g. '+1.9 N'."""
    m = float(np.mean(d))
    return cell(f"{sg(m)} {LETTER[rule(d)]}", mean=m, units=d, rule=LETTER[rule(d)])


def multi_cell(ds: list, rule, sep: str) -> dict:
    """'a / b P' (raw / standardized head) or 'a, b N' (two SSL draws); one letter if all agree."""
    means = [float(np.mean(d)) for d in ds]
    letters = [LETTER[rule(d)] for d in ds]
    text = (sep.join(sg(m) for m in means) + f" {letters[0]}" if len(set(letters)) == 1
            else sep.join(f"{sg(m)} {x}" for m, x in zip(means, letters, strict=True)))
    return cell(text, means=means, units=ds, rules=letters)


# ---------- the four tables ----------


def tab_d24a() -> dict:
    rows = {}
    pairs = [*((a, b) for a, b, _ in CONTRASTS), ("last_randinit", "lp_randinit")]
    for s, (ds, _, d24) in SETTINGS.items():
        for name, m in MODELS.items():
            rows[(s, name)] = [lambda a=a, b=b, m=m, ds=ds, d24=d24: ci_cell(
                diff(rot(ds, d24, m, a), rot(ds, d24, m, b)), d17d if b == "lp_randinit" and a != "lp" else paired)
                for a, b in pairs]
    for name, m in MODELS.items():   # D24-B: only the SA gain has a rule; D17 column = last_randinit - lp_randinit
        rows[("DL's split", name)] = [lambda a=a, b=b, m=m: ci_cell(
            diff(paper("P1E", m, a), paper("P1E", m, b)), paired if a == "last" else None) for a, b in pairs]
    return rows


def tab_p1e() -> dict:
    rows = {}
    for name, m in (("CBraMod", "cbramod"), ("BIOT", "biot")):
        for head, tags in (("linear", "P1E"), ("mlp\\_fullft", "P1E"), ("linear\\_z", "P1Z")):
            probe = head.replace("\\", "")
            nd = 2 if (m, probe) == ("cbramod", "linear") else 1

            def gain(m=m, tags=tags, probe=probe, nd=nd):
                d = diff(paper(tags, m, "last", probe), paper(tags, m, "lp", probe))
                mean, se = mse(d)
                if probe == "linear_z":   # post hoc cluster bootstrap over seeds (E26), fresh stream per cell
                    _, lo, hi = cluster_ci([d], np.random.default_rng(20261101))
                    ci, mark = (lo, hi), "$^\\dagger$"
                else:
                    ci, mark = tint(d)[1:], ""
                return cell(f"{un(mean, nd)} $\\pm$ {un(se, nd)} [{sg(ci[0])}, {sg(ci[1])}]{mark}",
                            mean=mean, sem=se, ci95=list(ci), units=d)

            rows[(name, head)] = [
                *(lambda a=a, m=m, tags=tags, probe=probe, nd=nd: ms_cell(
                    paper(tags, m, a, probe), nd if a in ("lp", "last") else 1)
                  for a in ("lp", "last", "lp_randinit", "last_randinit")),
                gain]
    return rows


def tab_robust() -> dict:
    """Row -> 6 cells (BIOT CHB-MIT, Siena, Siena filt.; CBraMod the same); None = '--' (not run)."""
    def sa(tagf, probe="linear"):
        return lambda m, ds, p, d24: gain_cell(diff(rot(ds, tagf(p, d24), m, "last", probe),
                                                    rot(ds, tagf(p, d24), m, "lp", probe)))

    def noise(tagf, probes, seeds=SEEDS3):
        return lambda m, ds, p, d24: multi_cell(
            [diff(rot(ds, t, m, "last", pr, seeds), rot(ds, t, m, "last_noise", pr, seeds))
             for t, pr in zip(tagf(p, d24), probes, strict=True)], d19, " / ")

    def e19(m, ds, p, d24):
        if m == "biot":
            return sa(lambda p, d24: f"{p}Q")(m, ds, p, d24)
        v = float(np.mean(diff(rot(ds, f"{p}C", m, "last"), rot(ds, d24, m, "lp"))))
        return cell(f"{sg(v)}$^\\dagger$", mean=v)

    def e28(m, ds, p, d24):
        lp = rot(ds, d24, m, "lp", seeds=SEEDS1)
        return multi_cell([diff(rot(ds, f"{p}D{k}", m, "last", seeds=SEEDS1), lp) for k in (11, 12)], paired, ", ")

    def e28n(m, ds, p, d24):
        return multi_cell([diff(rot(ds, f"{p}D{k},{p}DN{k}", m, "last", seeds=SEEDS1),
                                rot(ds, f"{p}D{k},{p}DN{k}", m, "last_noise", seeds=SEEDS1)) for k in (11, 12)],
                          d19, ", ")

    def e29(m, ds, p, d24):
        lp = rot(ds, d24, m, "lp", seeds=SEEDS1)
        ds_ = [diff(rot(ds, f"{p}LR{i}", m, "last", seeds=SEEDS1), lp) for i in range(1, 6)]
        n = sum(fires(d) for d in ds_)
        return cell(f"{n} of 5", n_firing=n, units=ds_)

    def e29n(m, ds, p, d24):
        cells_run = (1, 3, 4, 5) if ds == "chbmit" else (1, 2, 3, 4, 5)   # d27_cpu TOST_SETS A4 / A5
        out = [d19(diff(rot(ds, f"{p}LRN{i}", m, "last", seeds=SEEDS1),
                        rot(ds, f"{p}LRN{i}", m, "last_noise", seeds=SEEDS1))) for i in cells_run]
        n = sum(o == "perturbation alone explains it" for o in out)
        return cell(f"{n} of {len(out)} P$^\\dagger$", n_p=n, rules=out)

    def g(models, settings):
        return {(m, s) for m in models for s in settings}

    B, C, BC = ("biot",), ("cbramod",), ("biot", "cbramod")
    ALL, S1S3, S3, S3F = tuple(SETTINGS), ("CHB-MIT", "Siena"), ("Siena",), ("Siena filt.",)
    rows = {   # (id in the row label's parentheses, occurrence) -> (function, (model, setting) cells run)
        ("D24-A", 1): (sa(lambda p, d24: d24), g(BC, ALL)),
        ("D27-B", 1): (sa(lambda p, d24: f"{p}Z", "linear_z"), g(BC, ALL)),
        ("E25", 1): (sa(lambda p, d24: f"{p}L", "mlp_fullft"), g(BC, ALL)),
        ("D27 addition", 1): (noise(lambda p, d24: (f"{p}L,{p}NM", f"{p}Z,{p}NM"), ("mlp_fullft", "linear_z")),
                              g(B, S3 + S3F)),   # noise control of the E25 gains
        ("E27", 1): (noise(lambda p, d24: (f"{d24},{p}N",), ("linear",)), g(B, ALL) | g(C, S3 + S3F)),
        ("E19", 1): (e19, g(BC, ALL)),
        ("D27-A", 1): (noise(lambda p, d24: (f"{p}QN",) * 2, ("linear", "linear_z")), g(B, S3F)),   # q95
        ("E28", 1): (e28, g(BC, S1S3)),
        ("D27 addition", 2): (e28n, g(B, S3)),   # noise control of the E28 gains
        ("E32", 1): (sa(lambda p, d24: f"{p}R"), g(BC, S1S3)),
        ("D27-A", 2): (noise(lambda p, d24: (f"{p}R,{p}RN", f"{p}RZ,{p}RN"), ("linear", "linear_z")),
                       g(B, S1S3)),   # noise control on the second partition
        ("D26", 1): (sa(lambda p, d24: f"{p}RZ", "linear_z"), g(BC, S1S3)),
        ("E29", 1): (e29, g(BC, S1S3)),
        ("D27", 1): (e29n, g(B, S1S3)),   # noise control of the E29 cells
    }
    out = {}
    for label, (f, run) in rows.items():
        out[label] = [(lambda f=f, m=m, ds=ds, p=p, d24=d24: f(m, ds, p, d24)) if (m, s) in run else None
                      for m in BC for s, (ds, p, d24) in SETTINGS.items()]
    return out


def released(rel: dict, cid: str, w: str, seeds=None) -> tuple[float, float]:
    """Released-code run `cid`: ROC mean and SEM over seeds at epoch rule w (best / last)."""
    if cid not in rel:
        raise Missing(f"released-code run {cid}")
    m, s, _ = agg(rel[cid], w, seeds)
    return m[2], s[2]


def tab_original(rel: dict) -> dict:
    """DL Table 1 against the released code (E4) and our runs; the DL column is quoted from DL, not checked."""
    def pm(v, nd):
        m, se = mse(v)
        return f"{m:.{nd}f}$\\pm${se:.{nd}f}"

    def model(name, m, c, nd):
        def w1(arm):   # wave 1: released-code probe (BIOT train mode; CBraMod proj_out tap, train mode)
            return wave1(m, arm, "linear", 0)

        def rr(cid):
            return cell(" / ".join("{:.2f}$\\pm${:.2f}".format(*released(rel, cid, w)) for w in ("best", "last")))

        def gap_released():
            return cell(" / ".join(sg(released(rel, f"e4-{c}-sa", w)[0] - released(rel, f"e4-{c}-lp", w)[0])
                                   for w in ("best", "last")))

        def gap_random():
            return cell(sg(np.mean(w1("last_randinit")) - np.mean(w1("lp"))))

        def gap_pretrained():
            mean, se = mse(diff(w1("last"), w1("lp")))
            return cell(sg(mean), mean=mean, sem=se)   # difference of means, as the caption says

        def gap_encoder():
            mean, lo, hi = tint(diff(paper("P1E", m, "last"), paper("P1E", m, "lp")))
            return cell(f"{sg(mean, nd)} [{sg(lo, nd)}, {sg(hi, nd)}]", mean=mean, ci95=[lo, hi])

        return {   # None = the cell spanned by the LP row's \multicolumn (one LP for both starts)
            (f"{name} LP",): [lambda: rr(f"e4-{c}-lp"), lambda: cell(pm(w1("lp"), 2)), None,
                              lambda: cell(pm(paper("P1E", m, "lp"), nd))],
            (f"{name} SA",): [lambda: rr(f"e4-{c}-sa"), lambda: cell(pm(w1("last_randinit"), 2)),
                              lambda: cell(pm(w1("last"), 2)), lambda: cell(pm(paper("P1E", m, "last"), nd))],
            (f"{name} SA$-$LP",): [gap_released, gap_random, gap_pretrained, gap_encoder],
        }

    return {**model("BIOT", "biot", "b", 1), **model("CBraMod", "cbramod", "c", 2)}


def tab_artifacts(rel: dict) -> list:
    """(quantity cell of the row, column 0 = 'with the item' / 1 = 'with the change', builder or skip reason)."""
    def rr(cid):
        (a, b), (c, d) = released(rel, cid, "best"), released(rel, cid, "last")
        return cell(f"{a:.2f}~$\\pm$~{b:.2f} / {c:.2f}~$\\pm$~{d:.2f}", best=[a, b], last=[c, d])

    def rng_(prefix, tail):
        v = [released(rel, k, "best", SCREEN)[0] for k in rel if k.startswith(prefix)]
        return cell(f"set: {min(v):.2f} to {max(v):.2f} ({tail})", lo=min(v), hi=max(v), n_configs=len(v))

    def pm(d, nd, rule=None):
        m, se = mse(d)
        return cell(f"${sg(m, nd).replace('$-$', '-')}\\pm{se:.{nd}f}$" + (f", {LETTER[rule(d)]}" if rule else ""),
                    mean=m, sem=se, units=d)

    def tld(x, nd=2):
        m, se = mse(x)
        return f"{m:.{nd}f}~$\\pm$~{se:.{nd}f}", m, se

    def five_rot():
        d = diff(rot("chbmit", "S1E,S1M", "biot", "last_randinit"), rot("chbmit", "S1E,S1M", "biot", "last"))
        m, lo, hi = tint(d)
        return cell(f"five rotations: {sg(m).replace('$-$', '-')}, $t$ $[{lo:+.1f},{hi:+.1f}]$, "
                    f"{LETTER[paired(d)]}", mean=m, ci95=[lo, hi], units=d)

    def p1f():
        m = float(np.mean(diff(paper("P1F", "biot", "last_randinit"), paper("P1F", "biot", "last"))))
        return cell(f"stays at {sg(m)}", mean=m)

    lastr = "BIOT \\lastr$-$\\lastarm{} (ours, encoder-level probe)"
    pr = "BIOT \\lastr{} PR-AUC, shipped head (re-scored)"
    return [
        ("BIOT SA (DL 83.08)", 0, lambda: rr("e4-b-sa")),
        ("BIOT SA (DL 83.08)", 1, lambda: rng_("e5sa-b-fd1-", "released, 2 seeds")),
        ("BIOT SA (DL 83.08)", 1, lambda: pm(diff(paper("P1E", "biot", "last"), paper("P1E", "biot", "lp")), 1,
                                             paired)),
        ("CBraMod SA (DL 83.67)", 0, lambda: rr("e4-c-sa")),
        ("CBraMod SA (DL 83.67)", 1, lambda: rng_("e5sa-c-fd1-", "released, 2 seeds, best")),
        ("CBraMod LP, linear head (DL 54.14)", 0, lambda: rr("e5lp-c-ft0-b256")),
        ("CBraMod LP, linear head (DL 54.14)", 1, lambda: cell(
            "{:.2f}~$\\pm$~{:.2f} (released, both lines patched, 2 seeds)".format(
                *released(rel, "e7cbramod-c-tenc-meval-ft0", "best")))),
        ("CBraMod LP, linear head (DL 54.14)", 1, lambda: cell(
            (lambda t: f"{t[0]} (ours)")(tld(paper("P1E", "cbramod", "lp"))))),
        ("CBraMod SA gain, linear head (ours)", 0, lambda: pm(
            diff(wave1("cbramod", "last", "linear", 0), wave1("cbramod", "lp", "linear", 0)), 2, paired)),
        ("CBraMod SA gain, linear head (ours)", 1, lambda: pm(
            diff(paper("P1E", "cbramod", "last"), paper("P1E", "cbramod", "lp")), 2, paired)),
        (lastr, 0, lambda: pm(diff(paper("P1E", "biot", "last_randinit"), paper("P1E", "biot", "last")), 1)),
        (lastr, 1, five_rot),
        (pr, 0, lambda: cell(tld(wave1("biot", "last_randinit", "mlp_fullft", 1), 1)[0])),
        (pr, 1, "37.4~$\\pm$~1.2 is a re-scoring of per-window test scores with the revised labels and grid-only "
                "windows (scripts/posthoc_test.py on *.npz, not in the records)"),
        (pr, 1, p1f),
    ]


# ---------- paper cells and checking ----------


def tex_rows(label: str) -> tuple[str | None, list[list[str]]]:
    """(file, rows of cells) of the table with this label in any sections/*.tex; \\multicolumn{k} -> its text
    and k-1 SPAN cells. (None, []) if no file has the label (table removed, or no paper sources)."""
    for f in sorted(TEX.glob("*.tex")) if TEX.is_dir() else []:
        text = f.read_text()
        i = text.find(f"\\label{{{label}}}")
        if i < 0:
            continue
        rows = []
        for line in text[i:text.index("\\end{table}", i)].splitlines():
            line = re.sub(r"(?<!\\)%.*", "", line).strip()
            if "&" in line and line.endswith("\\\\"):
                row = []
                for c in (c.strip() for c in line[:-2].split("&")):
                    mc = re.fullmatch(r"\\multicolumn\{(\d+)\}\{[^}]*\}\{(.*)\}", c)
                    row += [mc.group(2), *[SPAN] * (int(mc.group(1)) - 1)] if mc else [c]
                rows.append(row)
        return f.name, rows
    return None, []


def status(text: str, pc: str | None, found: bool, inside: bool = False) -> str:
    if not found:
        return "UNCHECKED"   # no paper sources (the supplement) or the table is no longer in the paper
    if pc is None:
        return "FAIL"
    hit = re.search(r"(?<![\d.])" + re.escape(text) + r"(?!\d)", pc) if inside else text == pc
    return "PASS" if hit else "FAIL"


def run(builder) -> dict:
    if isinstance(builder, str):
        return {"status": "SKIP", "why": builder}
    try:
        return builder()
    except Missing as e:
        return {"text": f"records missing: {e}"}


def by_cols(n: int):
    """Rows keyed by their first n cells."""
    return lambda rows: {tuple(r[:n]): r for r in rows}


def by_id(rows) -> dict:
    """Rows keyed by (id in the label's last parentheses, occurrence), e.g. ('D27-A', 2): survives rewording."""
    seen, out = Counter(), {}
    for r in rows:
        m = re.search(r"\(([^()]*)\)$", r[0])
        if m:
            seen[m.group(1)] += 1
            out[(m.group(1), seen[m.group(1)])] = r
    return out


def check_grid(table: str, gen: dict, keys, first: int) -> list[dict]:
    """Generated cell j of a row is compared with paper cell first + j; None = not run ('--') or spanned."""
    tex, rows = tex_rows(table)
    paper_rows = keys(rows)
    out = []
    for key, cells in gen.items():
        prow = paper_rows.get(key)
        for j, b in enumerate(cells):
            pc = prow[first + j] if prow and first + j < len(prow) else None
            if b is None:
                if tex and pc not in ("--", SPAN):
                    out.append({"table": table, "tex": tex, "row": key, "label": prow and prow[0], "col": j,
                                "text": "--", "paper": pc, "status": "FAIL"})
                continue
            c = run(b)
            c.update(table=table, tex=tex, row=key, label=prow and prow[0], col=j, paper=pc,
                     status=status(c["text"], pc, bool(tex)))
            out.append(c)
    return out


def check_artifacts(rel: dict) -> list[dict]:
    tex, rows = tex_rows("tab:artifacts")
    paper_rows = {r[1]: r for r in rows}
    out = []
    for q, col, b in tab_artifacts(rel):
        pc = paper_rows[q][2 + col] if q in paper_rows else None
        c = run(b)
        if "status" not in c:
            c["status"] = status(c["text"], pc, bool(tex), inside=True)
        c.update(table="tab:artifacts", tex=tex, row=(q,), label=q, col=col, paper=pc)
        out.append(c)
    return out


STATUSES = ("PASS", "FAIL", "SKIP", "UNCHECKED")
SPAN = "<spanned by multicolumn>"
COLS = {"tab:original": ("released code (best / last)", "ours, released-code probe, random start",
                         "ours, released-code probe, pretrained start", "ours, encoder-level probe"),
        "tab:d24a": ("last-lp", "last_randinit-last", "lp-lp_randinit", "D17"),
        "tab:p1e": ("lp", "last", "lp_randinit", "last_randinit", "SA gain"),
        "tab:robust": ("BIOT CHB-MIT", "BIOT Siena", "BIOT Siena filt.", "CBraMod CHB-MIT", "CBraMod Siena",
                       "CBraMod Siena filt."),
        "tab:artifacts": ("with the item", "with the change")}


def main() -> int:
    global TEX
    ap = argparse.ArgumentParser()
    ap.add_argument("--local", default=str(ROOT / "artifacts" / "s3-results"))
    ap.add_argument("--released", default=str(ROOT / "artifacts" / "released-root"))
    ap.add_argument("--tex", default=str(TEX), help="paper sections folder; absent = tables written, not checked")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()
    TEX = Path(args.tex)
    t0 = time.time()
    scan(Path(args.local))
    rel = load_released(Path(args.released), False)
    with tempfile.TemporaryDirectory(prefix="main-tables-") as tmp:
        FARM.append(tmp)
        res = (check_grid("tab:original", tab_original(rel), by_cols(1), 2)
               + check_grid("tab:d24a", tab_d24a(), by_cols(2), 2)
               + check_grid("tab:p1e", tab_p1e(), by_cols(2), 2)
               + check_grid("tab:robust", tab_robust(), by_id, 2)
               + check_artifacts(rel))
    md = ["# Main tables regenerated from the saved records (scripts/make_main_tables.py)", "",
          "ours = text generated from the records; paper = the cell in paper/tmlr/sections/*.tex. "
          "tab:artifacts: ours must occur inside the paper cell.", ""]
    for table in COLS:
        rs = [r for r in res if r["table"] == table]
        n = {k: sum(r["status"] == k for r in rs) for k in STATUSES}
        tex = next((r["tex"] for r in rs if r["tex"]), None)
        md += [f"## {table} ({tex or 'not in the paper sources'}): "
               + ", ".join(f"{v} {k}" for k, v in n.items() if v), "",
               "| row | column | ours | paper | status |", "|---|---|---|---|---|"]
        for r in rs:
            ours = r.get("text") or f"({r.get('why')})"
            row = r["label"] or " / ".join(map(str, r["row"]))
            md.append(f"| {row} | {COLS[table][r['col']]} | `{ours}` | `{r['paper']}` | {r['status']} |")
            print(f"{r['status']:4s} {table} {row} | {COLS[table][r['col']]}: {ours}"
                  + ("" if r["status"] == "PASS" else f"  (paper: {r['paper']})"))
        md.append("")
    n = {k: sum(r["status"] == k for r in res) for k in STATUSES}
    summary = "TOTAL " + ", ".join(f"{v} {k}" for k, v in n.items() if v) + f" in {time.time() - t0:.0f} s"
    md.append(summary)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "main_tables.md").write_text("\n".join(md) + "\n")
    (out / "main_tables.json").write_text(json.dumps(res, indent=1, default=float))
    print(summary)
    return 1 if n["FAIL"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
