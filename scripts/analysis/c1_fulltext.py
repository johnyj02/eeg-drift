"""Paper C survey, stage 3: fetch candidate full texts and scan for the defect signatures.

Reads artifacts/analysis/C1/stage2-candidates.json, fetches each arXiv paper's HTML (falling back to the
abstract page), and records whether CHB-MIT appears and which defect signatures are present. It records
EVIDENCE ONLY. No verdict is assigned here; verdicts need the per-defect standard of
paper/jne/survey-protocol.md section 6 and are decided by reading the quoted context.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
C1 = ROOT / "artifacts" / "analysis" / "C1"
UA = {"User-Agent": "EEGDrift-survey/1.0 (independent research; one request at a time)"}

CHBMIT = re.compile(r"chb[\s\-_]?mit", re.I)
SIGNATURES = {
    # the fixed two-patient split (D-a)
    "test_pats_literal": re.compile(r"test_pats\s*=", re.I),
    "chb23_chb24": re.compile(r"chb_?23\D{0,12}chb_?24", re.I),
    "two_test_subjects": re.compile(r"(two|2)\s+(test|held[\s-]?out)\s+(patients|subjects)", re.I),
    # the start/end label rule (D-b)
    "start_end_label": re.compile(r"(start|onset)\s+(or|and)\s+end\s+of\s+(the\s+)?seizure", re.I),
    # duplicate windows / the inherited sample count (D-c and the pipeline fingerprint)
    "count_326993": re.compile(r"326[,\s]?993"),
    "ten_second_window": re.compile(r"10[\s-]?second", re.I),
    # the pipeline's own file name, a strong code-reuse tell
    "process2_py": re.compile(r"process2\.py", re.I),
}
CONTEXT = 160


def fetch(url: str) -> str | None:
    delay = 3.0
    for _attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code in (403, 404):
                return None
            time.sleep(delay)
            delay *= 2
        except Exception:
            time.sleep(delay)
            delay *= 2
    return None


def strip_html(s: str) -> str:
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s, flags=re.S | re.I)
    return " ".join(re.sub(r"<[^>]+>", " ", s).split())


def main() -> int:
    cand = json.loads((C1 / "stage2-candidates.json").read_text())["entries"]
    todo = {k: v for k, v in cand.items() if (v.get("externalIds") or {}).get("ArXiv")}
    out_path = C1 / "stage3-fulltext.json"
    done = json.loads(out_path.read_text())["papers"] if out_path.exists() else {}
    print(f"{len(todo)} candidates with an arXiv id; {len(done)} already scanned", flush=True)
    for i, (key, meta) in enumerate(sorted(todo.items()), 1):
        if key in done:
            continue
        aid = (meta["externalIds"] or {})["ArXiv"]
        html = fetch(f"https://arxiv.org/html/{aid}v1")
        source = "html"
        if not html:
            html = fetch(f"https://arxiv.org/abs/{aid}")
            source = "abs_page_only"
        rec = {"title": meta.get("title"), "year": meta.get("year"), "venue": meta.get("venue"),
               "arxiv": aid, "seeds": meta.get("seeds"), "source": source if html else "unfetchable",
               "chbmit": False, "signatures": {}, "quotes": {}}
        if html:
            text = strip_html(html)
            rec["chars"] = len(text)
            rec["chbmit"] = bool(CHBMIT.search(text))
            for name, pat in SIGNATURES.items():
                m = pat.search(text)
                rec["signatures"][name] = bool(m)
                if m:
                    a, b = max(0, m.start() - CONTEXT), min(len(text), m.end() + CONTEXT)
                    rec["quotes"][name] = text[a:b]
        done[key] = rec
        flag = "CHB-MIT" if rec["chbmit"] else "-------"
        sig = ",".join(k for k, v in rec["signatures"].items() if v) or "none"
        print(f"[{i}/{len(todo)}] {aid} {flag} {rec['source']:14s} sig: {sig}", flush=True)
        out_path.write_text(
            json.dumps({"search_date": "2026-11-18", "n": len(done), "papers": done}, indent=1) + "\n")
        time.sleep(3)
    n_chb = sum(1 for r in done.values() if r["chbmit"])
    print(f"\nscanned {len(done)} | mention CHB-MIT: {n_chb} | unfetchable: "
          f"{sum(1 for r in done.values() if r['source'] == 'unfetchable')}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
