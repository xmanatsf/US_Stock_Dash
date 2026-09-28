"""Count the article briefs behind a monthly News Intelligence page.

The monthly page (build_monthly.py) never types a brief count. This script produces the census it
reads them from, by counting the brief files themselves in `Cowork Playground/WSJ/`, which owns
them. It is the monthly page's analogue of the weekly page's copied source audit: run it in the
same step as dropping a new `monthly_<date>.json`, so the counts and the prose come from the same
window.

A brief file is `<publication>_insights_<YYYY-MM-DD>.md`; each brief inside it opens with a level-1
`# ` title followed by a `**Source:**` line, and the two counts must agree or the file is reported.

    python scripts/census_briefs.py --from 2026-09-04 --to 2026-09-25
    python scripts/census_briefs.py --from 2026-09-04 --to 2026-09-25 --src "../WSJ"

Writes data/insights/monthly_census_<to-date>.json.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEFAULT_SRC = os.path.join(os.path.dirname(ROOT), "WSJ")
OUT_DIR = os.path.join(ROOT, "data", "insights")

FILE_RE = re.compile(r"^([a-z]+)_insights_(\d{4}-\d{2}-\d{2})\.md$")
TITLE_RE = re.compile(r"^# (.+)$", re.M)
SOURCE_RE = re.compile(r"^\*\*Source:\*\*", re.M)
LABEL = {"wsj": "WSJ", "bloomberg": "Bloomberg", "barrons": "Barron’s / MarketWatch", "reuters": "Reuters"}


def census(src: str, d_from: str, d_to: str) -> dict:
    files, problems = [], []
    for name in sorted(os.listdir(src)):
        m = FILE_RE.match(name)
        if not m or not (d_from <= m.group(2) <= d_to):
            continue
        with open(os.path.join(src, name), encoding="utf-8") as f:
            text = f.read()
        titles = TITLE_RE.findall(text)
        n_src = len(SOURCE_RE.findall(text))
        if len(titles) != n_src:
            problems.append(f"{name}: {len(titles)} titles but {n_src} **Source:** lines")
        files.append({"file": name, "publication": m.group(1), "date": m.group(2),
                      "briefs": len(titles), "titles": titles})

    by_pub, by_date = {}, {}
    for f in files:
        by_pub[f["publication"]] = by_pub.get(f["publication"], 0) + f["briefs"]
        by_date[f["date"]] = by_date.get(f["date"], 0) + f["briefs"]
    return {
        "schemaVersion": 1,
        "generated": dt.datetime.now().replace(microsecond=0).isoformat(),
        "source": "Cowork Playground/WSJ",
        "window": {"from": d_from, "to": d_to},
        "counts": {"briefs": sum(f["briefs"] for f in files), "files": len(files),
                   "dates": len(by_date), "byPublication": by_pub, "byDate": dict(sorted(by_date.items()))},
        "publicationLabels": {k: LABEL.get(k, k) for k in by_pub},
        "files": files,
        "problems": problems,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="d_from", required=True)
    ap.add_argument("--to", dest="d_to", required=True)
    ap.add_argument("--src", default=DEFAULT_SRC)
    args = ap.parse_args(argv)
    if not os.path.isdir(args.src):
        print(f"FATAL brief folder not found: {args.src}")
        return 1
    doc = census(args.src, args.d_from, args.d_to)
    c = doc["counts"]
    if not c["files"]:
        print(f"FATAL no brief files dated {args.d_from}..{args.d_to} in {args.src}")
        return 1
    out = os.path.join(OUT_DIR, f"monthly_census_{args.d_to.replace('-', '')}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    print(f"  {c['briefs']} briefs in {c['files']} files over {c['dates']} dates "
          f"({args.d_from}..{args.d_to}): " + ", ".join(f"{k} {v}" for k, v in c["byPublication"].items()))
    for p in doc["problems"]:
        print(f"  WARN {p}")
    print(f"  wrote {out}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
