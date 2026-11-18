"""Paper C survey, stage 1: the citation sweep of BIOT and CBraMod (survey-protocol.md section 2).

Writes artifacts/analysis/C1/s2-citations.json. Polite: one request at a time, exponential backoff on
429, and it resumes from whatever it already wrote.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.semanticscholar.org/graph/v1"
OUT = pathlib.Path(__file__).resolve().parents[2] / "artifacts" / "analysis" / "C1"
UA = {"User-Agent": "EEGDrift-survey/1.0 (independent research; one request at a time)"}


def get(path: str, **params) -> dict:
    url = f"{API}/{path}?" + urllib.parse.urlencode(params)
    delay = 4.0
    for attempt in range(8):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == 7:
                raise
            print(f"  429, sleeping {delay:.0f}s", flush=True)
            time.sleep(delay)
            delay = min(delay * 2, 120)
        except Exception:
            if attempt == 7:
                raise
            time.sleep(delay)
    raise RuntimeError("unreachable")


SEEDS = {
    "BIOT": "BIOT: Biosignal Transformer for Cross-data Learning",
    "CBraMod": "CBraMod: A Criss-Cross Brain Foundation Model for EEG Decoding",
}
FIELDS = "paperId,externalIds,title,year,venue,publicationTypes,abstract,citationCount"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    seeds, cites = {}, {}
    for name, title in SEEDS.items():
        time.sleep(4)
        hits = get("paper/search", query=title, fields="paperId,title,year,citationCount", limit=5).get("data", [])
        best = max(hits, key=lambda d: d.get("citationCount") or 0) if hits else None
        if not best:
            print(f"{name}: NOT FOUND", flush=True)
            continue
        seeds[name] = best
        print(f"{name}: {best['title'][:60]} ({best.get('year')}), "
              f"{best.get('citationCount')} citations, id {best['paperId']}", flush=True)
        rows, offset = [], 0
        while True:
            time.sleep(4)
            page = get(f"paper/{best['paperId']}/citations", fields=FIELDS, limit=100, offset=offset)
            data = page.get("data", [])
            rows += [d["citingPaper"] for d in data if d.get("citingPaper")]
            print(f"  {name}: {len(rows)} citing papers so far", flush=True)
            if len(data) < 100:
                break
            offset += 100
        cites[name] = rows
    (OUT / "s2-citations.json").write_text(json.dumps(
        {"source": "Semantic Scholar graph API", "search_date": "2026-11-18",
         "seeds": seeds, "counts": {k: len(v) for k, v in cites.items()},
         "citing_papers": cites}, indent=1) + "\n")
    print("wrote", OUT / "s2-citations.json", flush=True)
    print("counts:", {k: len(v) for k, v in cites.items()}, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
