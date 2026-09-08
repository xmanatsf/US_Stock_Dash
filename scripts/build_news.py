"""Build the News Intelligence page.

This is not a universe. There is no workbook, no composite and no regime -- like fab5 it renders
CLAIMS rather than measurements. What makes it different from fab5 is where the numbers come from:

  * The ANALYTICAL PROSE is hand-authored in `data/insights/news_<date>.json`.
  * Every COUNT, every article row and every citation LINK is generated here from
    `data/insights/narrative_dashboard_source_audit.json`.

That split is the upstream generator's own contract -- "the template carries every analytical
claim; this script carries every number and every link" -- and it is preserved rather than
reinvented, because it is the thing that keeps the page honest. Two rules follow, both enforced
below rather than trusted:

  * A `{{cite:Key}}` resolves by title substring against the audit's `articles[]` and must match
    EXACTLY ONE. Zero matches or two are a fatal build error, exactly as upstream. A silently
    wrong citation is worse than no page.
  * The section counts the authored prose spells out in words -- eighteen indicators, nine
    movements, ten disagreements -- are asserted against the arrays. Adding a row without
    rewriting the sentence that counts it fails the build.

`Cowork Playground/WSJ/` owns the briefs and the reference build. This script never reads the
assembled HTML: that copy is downstream and gets overwritten there.

Run via build_all (which owns index.json), or standalone while iterating on the content:

    python scripts/build_news.py
"""

from __future__ import annotations

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config as C        # noqa: E402
import pipeline as P      # noqa: E402

SOURCE_DIR = os.path.join("data", "insights")
SOURCE_STEM = "news_"
AUDIT_FILE = "narrative_dashboard_source_audit.json"
PRIOR_AUDIT_STEM = "narrative_dashboard_source_audit_"   # optional: ..._<date>.json
OUT_DIR = "insights"
OUT_FILE = "news.json"

CITE_RE = re.compile(r"\{\{cite:([^}]+)\}\}")
TOKEN_RE = re.compile(r"\{\{[^}]*\}\}")

# The upstream generator's status vocabulary, carried rather than remapped.
ST_LABEL = {"ok": "Confirmed", "bad": "Escalated", "warn": "In motion", "new": "New this week"}

# Counts the authored prose spells out in words. If a row is added or removed, the sentence that
# counts it has to be rewritten too -- so they are pinned here, the same way upstream pins them.
PINNED = {"signals": 18, "timeline": 9, "conflicts": 10}


class NewsError(Exception):
    pass


def _resolve_source(cfg: C.Config) -> str:
    d = cfg.path(SOURCE_DIR)
    if not os.path.isdir(d):
        raise NewsError(f"missing content directory: {d}")
    cands = sorted(f for f in os.listdir(d)
                   if f.startswith(SOURCE_STEM) and f.endswith(".json"))
    if not cands:
        raise NewsError(f"no {SOURCE_STEM}<date>.json content file in {d}")
    return os.path.join(d, cands[-1])


def _load_audit(cfg: C.Config) -> dict:
    path = os.path.join(cfg.path(SOURCE_DIR), AUDIT_FILE)
    if not os.path.exists(path):
        raise NewsError(
            f"missing {AUDIT_FILE} in {cfg.path(SOURCE_DIR)}. Every count, index row and link on "
            f"this page is generated from it -- copy it from Cowork Playground/WSJ/, which owns it. "
            f"Without it the page would have to hand-type 108 index rows, which is the thing the "
            f"upstream contract exists to prevent.")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _load_prior_audit(cfg: C.Config) -> dict | None:
    """A prior window's audit, if one has been kept. Its absence is a rendered state, not a zero."""
    d = cfg.path(SOURCE_DIR)
    cands = sorted(f for f in os.listdir(d)
                   if f.startswith(PRIOR_AUDIT_STEM) and f.endswith(".json"))
    if not cands:
        return None
    with open(os.path.join(d, cands[-1]), encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------- citations

def _build_citer(articles: list, problems: list):
    """Upstream's `cite()`, ported. Exactly one match or the build fails."""
    used: dict = {}

    def resolve(key: str) -> None:
        key = key.strip()
        if key in used:
            return
        hits = [a for a in articles if key in a["title"]]
        if not hits:
            problems.append(f"{{{{cite:{key}}}}} matched NO article title")
            return
        if len(hits) > 1:
            titles = "\n        - ".join(h["title"] for h in hits)
            problems.append(
                f"{{{{cite:{key}}}}} is AMBIGUOUS -- matched {len(hits)} articles:\n"
                f"        - {titles}\n"
                f"      Lengthen the key so it matches exactly one.")
            return
        a = hits[0]
        used[key] = {"id": a["id"], "publication": a["publication"], "date": a["date"],
                     "title": a["title"], "url": a["url"]}

    return resolve, used


def _walk_strings(node, fn):
    """Apply fn to every string anywhere in the document."""
    if isinstance(node, str):
        fn(node)
    elif isinstance(node, list):
        for v in node:
            _walk_strings(v, fn)
    elif isinstance(node, dict):
        for v in node.values():
            _walk_strings(v, fn)


# ---------------------------------------------------------------------------- build

def build(cfg: C.Config, built_at: str) -> dict:
    src = _resolve_source(cfg)
    with open(src, encoding="utf-8") as f:
        doc = json.load(f)
    doc["contentFile"] = os.path.basename(src)

    audit = _load_audit(cfg)
    articles = audit.get("articles") or []
    counts = audit.get("counts") or {}
    if not articles:
        raise NewsError(f"{AUDIT_FILE} carries no articles[] -- nothing can be generated from it")

    problems = []

    # ---------------------------------------------------------------- pinned section counts
    for key, expected in PINNED.items():
        got = len(doc.get(key) or [])
        if got != expected:
            problems.append(
                f"{key}: {got} entries but the build pins {expected}. The authored prose spells "
                f"this count out in words -- update both, or change PINNED deliberately.")

    # ---------------------------------------------------------------- citations
    resolve, cite_map = _build_citer(articles, problems)

    def collect(s: str) -> None:
        for m in CITE_RE.finditer(s):
            resolve(m.group(1))

    _walk_strings(doc, collect)

    # `cites` arrays name keys directly rather than inline, so they resolve the same way.
    def collect_lists(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "cites" and isinstance(v, list):
                    for key in v:
                        resolve(key)
                else:
                    collect_lists(v)
        elif isinstance(node, list):
            for v in node:
                collect_lists(v)

    collect_lists(doc)

    # A token that is not a citation would render as literal braces on the page.
    stray = set()

    def find_stray(s: str) -> None:
        for m in TOKEN_RE.finditer(s):
            if not m.group(0).startswith("{{cite:"):
                stray.add(m.group(0))

    _walk_strings(doc, find_stray)
    if stray:
        problems.append(f"non-citation tokens left in the content: {sorted(stray)}. Counts are "
                        f"generated into the payload, not substituted into prose.")

    # ---------------------------------------------------------------- infographic provenance
    # Rows 1 and 4 are judgements, so they must carry a source. Rows 2, 3 and 5 are counts and
    # carry none, because they are arithmetic over the audit file.
    for i, st in enumerate(doc.get("stats", [])):
        where = f"stats[{i}] ({st.get('kicker') or 'no kicker'})"
        for field in ("kicker", "num", "lab", "grade"):
            if not st.get(field):
                problems.append(f"{where}: missing {field!r}")
        if not st.get("cites"):
            problems.append(f"{where}: missing cites -- an infographic figure must resolve to a "
                            f"generated count or an explicitly cited authored field")
    for i, r in enumerate((doc.get("narratives") or {}).get("reads", [])):
        if not r.get("cites"):
            problems.append(f"narratives.reads[{i}] ({r.get('title')}): missing cites. This row is "
                            f"authored precisely because counts cannot produce it, so it carries a "
                            f"source or it is not shipped.")
    if not (doc.get("narratives") or {}).get("thesis"):
        problems.append("narratives.thesis: missing -- the band's first line is the one a reader "
                        "should be able to stop at")
    for i, t in enumerate(doc.get("themeLinks", [])):
        if not t.get("cites"):
            problems.append(f"themeLinks[{i}] ({t.get('from')} -> {t.get('to')}): missing cites")
        if not (t.get("from") and t.get("to")):
            problems.append(f"themeLinks[{i}]: needs both from and to")

    for i, s in enumerate(doc.get("signals", [])):
        if s.get("status") not in ST_LABEL:
            problems.append(f"signals[{i}] (#{s.get('n')}): status {s.get('status')!r} not in "
                            f"{tuple(ST_LABEL)}")
    near = doc.get("scenarios", [])
    if near:
        total = sum(s.get("pct") or 0 for s in near)
        if round(total) != 100:
            problems.append(f"scenarios: probabilities sum to {total}, not 100")

    if problems:
        raise NewsError("content validation failed:\n  " + "\n  ".join(problems))

    # ---------------------------------------------------------------- generated content
    pubs = doc.get("publications") or list((counts.get("byPublication") or {}).keys())
    by_theme = counts.get("byTheme") or {}
    by_tp = counts.get("byThemeAndPublication") or {}

    prior = _load_prior_audit(cfg)
    prior_by_theme = ((prior or {}).get("counts") or {}).get("byTheme")

    coverage = []
    for theme, n in by_theme.items():
        row = {"theme": theme, "n": n,
               "byPublication": {p: (by_tp.get(theme) or {}).get(p, 0) for p in pubs}}
        if prior_by_theme is None:
            # Never a zero. A missing prior window and a collapse to nothing look identical as a
            # number and mean opposite things, so the page says which one it is.
            row["prior"] = None
            row["delta"] = None
        else:
            row["prior"] = prior_by_theme.get(theme, 0)
            row["delta"] = n - row["prior"]
        coverage.append(row)

    st_counts = {k: sum(1 for s in doc["signals"] if s["status"] == k) for k in ST_LABEL}

    doc["generated"] = {
        "auditGeneratedAt": audit.get("generated"),
        "window": audit.get("window"),
        "articles": articles,
        "counts": counts,
        "coverage": coverage,
        "priorWindow": bool(prior_by_theme),
        "kpis": [
            {"label": "article entries", "n": counts.get("articles", len(articles))},
            {"label": "briefs", "n": counts.get("files")},
            {"label": "brief dates", "n": counts.get("days")},
            {"label": "publications", "n": len(pubs)},
            {"label": "citations resolved", "n": len(cite_map)},
        ],
        "signalCounts": st_counts,
        "signalLabels": ST_LABEL,
        "themes": list(by_theme.keys()),
        "publications": pubs,
        "byFile": counts.get("byFile") or {},
        "auditNotes": audit.get("notes") or [],
    }
    doc["citeMap"] = cite_map
    doc["builtAt"] = built_at
    doc["version"] = P._version(
        doc["asOf"].replace("-", ""),
        [json.dumps(doc.get("signals"), sort_keys=True),
         json.dumps(doc.get("timeline"), sort_keys=True),
         json.dumps(counts, sort_keys=True)])
    return doc


def emit(cfg: C.Config, doc: dict) -> str:
    path = os.path.join(cfg.processed_dir, OUT_DIR, OUT_FILE)
    P._write(path, doc)
    return path


def index_entry(doc: dict) -> dict:
    return {
        "label": doc["label"], "tab": doc["tab"], "order": doc.get("order", 99),
        "kind": "insight", "version": doc["version"], "asOf": doc["asOf"],
        "dir": OUT_DIR, "file": OUT_FILE,
        "sourceDoc": doc.get("sourceDoc"),
    }


def print_console(doc: dict) -> None:
    g = doc["generated"]
    c = g["counts"]
    print(f"  content: {doc['contentFile']}")
    print(f"  authored: {len(doc['reads'])} reads, {len(doc['timeline'])} timeline movements, "
          f"{len(doc['conflicts'])} conflicts, {len(doc['signals'])} signals, "
          f"{len(doc['calendar'])} dated catalysts")
    print(f"  generated from the audit: {c.get('articles')} article entries, {c.get('files')} "
          f"briefs, {c.get('days')} brief dates, {len(doc['citeMap'])} citations resolved")
    print(f"  coverage: " + ", ".join(f"{r['theme']} {r['n']}" for r in g["coverage"]))
    if not g["priorWindow"]:
        print("  NOTE no prior-window audit file present -- the coverage map renders "
              "'no prior window' rather than a zero delta")
    print("  signal board: " + ", ".join(
        f"{g['signalLabels'][k]} {v}" for k, v in g["signalCounts"].items() if v))


def main(argv=None) -> int:
    import datetime as dt
    cfg = C.load()
    built_at = dt.datetime.now().replace(microsecond=0).isoformat()
    try:
        doc = build(cfg, built_at)
    except NewsError as e:
        print(f"FATAL {e}")
        return 1
    path = emit(cfg, doc)
    print_console(doc)
    print(f"  wrote {path}")
    P.copy_to_site(cfg.processed_dir, cfg.site_data_dir)
    print("  NOTE index.json is owned by build_all.py; run it to register the nav entry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
