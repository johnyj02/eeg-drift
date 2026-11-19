"""Paper C survey, stage 4: find each candidate's repository and its CHB-MIT preprocessing script.

Evidence only; verdicts are assigned by reading the recorded lines (survey-protocol.md Amendment A3).

Why the GitHub trees API and not a path guess: a first version guessed 8 plausible paths and found files in
only 2 of 12 repositories. Checking the paths the hand census actually used showed the guess list was the
problem, missing `datasets_processing/CHB-MIT/process_2.py`,
`preprocessing/preprocessing_for_finetuning/CHB-MIT/process2.py` and `data_preprocessing/CHB-MIT/`. The
tree listing removes the guess: every file in the repository is enumerated, then filtered by pattern.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
C1 = ROOT / "artifacts" / "analysis" / "C1"
UA = {"User-Agent": "EEGDrift-survey/1.0 (independent research; one request at a time)"}
TOKEN = os.environ.get("GITHUB_TOKEN", "")

GITHUB = re.compile(r"github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git|[)\s\"'<>,]|$)")
SKIP_OWNERS = {"github", "features", "about", "topics", "sponsors", "orgs", "apps", "site"}
# any file whose path looks like CHB-MIT preprocessing, however the repo spells it
PREPROC = re.compile(r"(chb[\s_-]?mit|chbmit)", re.I)
PYFILE = re.compile(r"\.py$", re.I)
SPLIT = {
    "test_pats": re.compile(r"test_pats\s*=.*", re.I),
    "val_pats": re.compile(r"val_pats\s*=.*", re.I),
    "chb23_24": re.compile(r".*chb_?23.*chb_?24.*", re.I),
    "excluded_12_13_17": re.compile(r".*chb_?12.*chb_?13.*chb_?17.*", re.I),
    "stride_or_overlap": re.compile(r".*(stride|overlap|step_size)\s*=.*", re.I),
    "label_start_end": re.compile(r".*(start|onset).*(end|offset).*", re.I),
}


def fetch(url: str, json_api: bool = False):
    headers = dict(UA)
    if json_api and TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    for _ in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as r:
                body = r.read().decode("utf-8", "replace")
                return json.loads(body) if json_api else body
        except urllib.error.HTTPError as e:
            if e.code in (403, 404, 409, 451):
                return None
            time.sleep(4)
        except Exception:
            time.sleep(4)
    return None


def tree(owner: str, repo: str) -> list[str]:
    """Every file path in the repository's default branch, via one API call."""
    meta = fetch(f"https://api.github.com/repos/{owner}/{repo}", json_api=True)
    if not meta or not meta.get("default_branch"):
        return []
    t = fetch(f"https://api.github.com/repos/{owner}/{repo}/git/trees/"
              f"{meta['default_branch']}?recursive=1", json_api=True)
    if not t:
        return []
    return [n["path"] for n in t.get("tree", []) if n.get("type") == "blob"]


def main() -> int:
    targets = json.loads((C1 / "verdicts.json").read_text())["rows"]
    out_path = C1 / "stage4-repos.json"
    done = {}
    for row in targets:
        aid = row["arxiv"]
        page = fetch(f"https://arxiv.org/abs/{aid}") or ""
        html = fetch(f"https://arxiv.org/html/{aid}v1") or fetch(f"https://arxiv.org/html/{aid}") or ""
        repos: list[tuple[str, str]] = []
        for owner, repo in GITHUB.findall(page + " " + html):
            if owner.lower() in SKIP_OWNERS or (owner, repo) in repos:
                continue
            repos.append((owner, repo))
        rec = {"short_name": row["short_name"], "repos_seen": [f"{o}/{r}" for o, r in repos[:8]],
               "html_found": bool(html), "trees": {}, "files": {}}
        for owner, repo in repos[:4]:
            paths = tree(owner, repo)
            time.sleep(1)
            if not paths:
                continue
            cands = [p for p in paths if PYFILE.search(p) and PREPROC.search(p)]
            rec["trees"][f"{owner}/{repo}"] = {"n_files": len(paths), "chbmit_py": cands[:12]}
            for p in cands[:6]:
                url = f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/{p}"
                body = fetch(url)
                time.sleep(1)
                if not body:
                    continue
                hits = {n: [" ".join(m.group(0).split())[:200] for m in pat.finditer(body)][:3]
                        for n, pat in SPLIT.items()}
                rec["files"][url] = {"bytes": len(body), "hits": {k: v for k, v in hits.items() if v}}
        done[aid] = rec
        keys = sorted({k for f in rec["files"].values() for k in f["hits"]})
        print(f"{aid} {row['short_name'][:30]:30s} repos={len(rec['repos_seen'])} "
              f"trees={len(rec['trees'])} chbmit_py={sum(len(t['chbmit_py']) for t in rec['trees'].values())} "
              f"read={len(rec['files'])} {','.join(keys) if keys else ''}", flush=True)
        out_path.write_text(json.dumps({"search_date": "2026-11-18", "papers": done}, indent=1) + "\n")
    print(f"\nrepositories enumerated for {sum(1 for r in done.values() if r['trees'])} of {len(done)} papers",
          flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
