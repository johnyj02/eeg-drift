"""Paper C survey, stage 5: three independent routes to the repositories stage 4 could not find.

Stage 4 read arXiv's abstract page and HTML rendering and found no repository for 6 of 12 papers. That is
an extraction limit, not evidence that no code exists, so this tries:
  R1. the PDF text, which carries footnotes the HTML rendering drops;
  R2. the Semantic Scholar record, for a linked repository;
  R3. GitHub code search for the pipeline's own marker next to the paper's model name.

Evidence only. A tier-A verdict needs a file in THAT paper's OWN repository; a third-party
reimplementation is recorded and stays tier C (survey-protocol.md Amendment A3).
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
C1 = ROOT / "artifacts" / "analysis" / "C1"
UA = {"User-Agent": "EEGDrift-survey/1.0 (independent research; one request at a time)"}
TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB = re.compile(r"github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git|[)\s\"'<>,\]]|$)")
SKIP = {"github", "features", "about", "topics", "sponsors", "orgs", "apps", "site", "readme"}


def get(url: str, as_json: bool = False, binary: bool = False):
    headers = dict(UA)
    if as_json and TOKEN and "api.github.com" in url:
        headers["Authorization"] = f"Bearer {TOKEN}"
    for _ in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=90) as r:
                raw = r.read()
                if binary:
                    return raw
                body = raw.decode("utf-8", "replace")
                return json.loads(body) if as_json else body
        except urllib.error.HTTPError as e:
            if e.code in (403, 404, 409, 451):
                return None
            time.sleep(4)
        except Exception:
            time.sleep(4)
    return None


def repos_in(text: str) -> list[str]:
    out = []
    for owner, repo in GITHUB.findall(text or ""):
        if owner.lower() in SKIP:
            continue
        slug = f"{owner}/{repo}"
        if slug not in out:
            out.append(slug)
    return out


def pdf_text(aid: str) -> str:
    raw = get(f"https://arxiv.org/pdf/{aid}", binary=True)
    if not raw:
        return ""
    tmp = pathlib.Path("/tmp") / f"c1-{aid}.pdf"
    tmp.write_bytes(raw)
    try:
        return subprocess.run(["pdftotext", "-layout", str(tmp), "-"],
                              capture_output=True, text=True, timeout=120).stdout
    except Exception:
        return ""
    finally:
        tmp.unlink(missing_ok=True)


def main() -> int:
    stage4 = json.loads((C1 / "stage4-repos.json").read_text())["papers"]
    verd = {r["arxiv"]: r for r in json.loads((C1 / "verdicts.json").read_text())["rows"]}
    todo = [a for a, r in stage4.items() if not r["trees"]]
    print(f"deep dive on {len(todo)} papers with no repository located: {todo}\n", flush=True)
    out = {}
    for aid in todo:
        name = verd[aid]["short_name"]
        rec = {"short_name": name, "r1_pdf": [], "r2_s2": [], "r3_codesearch": []}
        txt = pdf_text(aid)
        rec["pdf_chars"] = len(txt)
        rec["r1_pdf"] = repos_in(txt)
        time.sleep(2)
        s2 = get("https://api.semanticscholar.org/graph/v1/paper/arXiv:" + aid
                 + "?fields=title,externalIds,openAccessPdf", as_json=True)
        if s2:
            rec["r2_s2"] = repos_in(json.dumps(s2))
        time.sleep(3)
        if TOKEN:
            q = urllib.parse.quote(f'"test_pats" {name.split()[0]}')
            cs = get(f"https://api.github.com/search/code?q={q}", as_json=True)
            if cs:
                rec["r3_codesearch"] = [i["repository"]["full_name"] for i in cs.get("items", [])][:5]
        else:
            rec["r3_codesearch"] = ["SKIPPED: no GITHUB_TOKEN, the code-search API needs auth"]
        found = sorted(set(rec["r1_pdf"] + rec["r2_s2"]))
        rec["located"] = found
        print(f"{aid} {name[:30]:30s} pdf_chars={rec['pdf_chars']:>7} "
              f"r1={len(rec['r1_pdf'])} r2={len(rec['r2_s2'])} -> {found[:3] if found else 'NONE'}", flush=True)
        out[aid] = rec
        (C1 / "stage5-deepdive.json").write_text(
            json.dumps({"search_date": "2026-11-18", "papers": out}, indent=1) + "\n")
    n = sum(1 for r in out.values() if r["located"])
    print(f"\nrepositories newly located: {n} of {len(todo)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
