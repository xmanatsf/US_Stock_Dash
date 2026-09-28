"""Build the monthly News Intelligence page (September 2026 and after).

A page, not a universe: no workbook, no composite, no regime. It renders CLAIMS, transcribed from the
monthly news-intelligence design canvas into `data/insights/monthly_<date>.json`. It is a sibling of
the weekly `news` page rather than a replacement, because the two have different contracts:

  * The weekly page resolves `{{cite:Key}}` against a source audit with one row per article.
  * The monthly canvas cites by OUTLET AND DATE ("WSJ · 25 Sep") and carries no article index, so
    that is the contract enforced here -- every Reported, Analysis and market-implied item must name
    a publication and a date, or the build fails.

What is generated rather than authored is the same split the weekly page draws: every brief count
comes from `monthly_census_<date>.json` (written by census_briefs.py from the brief files), is
substituted into `{{count:*}}` tokens, and the heatmap's briefs-per-day row is asserted against it.

Run via build_all (which owns index.json), or standalone while iterating:

    python scripts/build_monthly.py
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
SOURCE_RE = re.compile(r"^monthly_(\d{8})\.json$")
CENSUS_STEM = "monthly_census_"
OUT_DIR = "insights"
OUT_FILE = "monthly.json"

KINDS = ("reported", "analysis", "ours", "scenario", "market")
NEEDS_SOURCE = ("reported", "analysis", "market")
BLOCK_TYPES = ("prose", "tiles", "cards", "heatmap", "sourcebase", "timeline", "series", "bars",
               "events", "table", "steps", "ranking", "scenarios", "odds", "calendar", "conflicts",
               "flow")
THEMES_REQUIRED = ("econ", "geo", "ai", "biz")

# A source line must name a publication the briefs come from ("IEA via WSJ" counts, because the
# brief is the WSJ one) AND a date. Market-implied figures must also name the market.
PUB_RE = re.compile(r"WSJ|Wall Street Journal|Bloomberg|Barron|Reuters|MarketWatch")
DATE_RE = re.compile(r"\b\d{1,2}(?:[–-]\d{1,2})?\s+Sep\b|\bSept?\.?\s+\d{1,2}\b|\b1–26 Sep\b|· Sep\b")
MARKET_RE = re.compile(r"CME|Kalshi|swaps|Polymarket|futures|FedWatch", re.I)
TOKEN_RE = re.compile(r"\{\{([^}]*)\}\}")


class MonthlyError(Exception):
    pass


def _resolve_source(cfg: C.Config) -> str:
    d = cfg.path(SOURCE_DIR)
    cands = sorted(f for f in os.listdir(d) if SOURCE_RE.match(f))
    if not cands:
        raise MonthlyError(f"no monthly_<date>.json content file in {d}")
    return os.path.join(d, cands[-1])


def _load_census(cfg: C.Config, window_to: str) -> tuple[dict, str]:
    name = f"{CENSUS_STEM}{window_to.replace('-', '')}.json"
    path = os.path.join(cfg.path(SOURCE_DIR), name)
    if not os.path.exists(path):
        raise MonthlyError(
            f"missing {name}. Every brief count on this page is generated from it -- run "
            f"`python scripts/census_briefs.py --from <from> --to {window_to}` in the same step as "
            f"dropping the content file, so the counts and the prose cover the same window.")
    with open(path, encoding="utf-8") as f:
        return json.load(f), name


# ---------------------------------------------------------------------------- provenance

def _check_src(where: str, kind: str, src: str | None, problems: list, *, date_from=None) -> None:
    if kind not in NEEDS_SOURCE:
        return
    if not src:
        problems.append(f"{where}: a {kind} item carries no source")
        return
    if not PUB_RE.search(src):
        problems.append(f"{where}: source {src!r} names no publication (WSJ/Bloomberg/Barron's/Reuters)")
    if date_from is None and not DATE_RE.search(src):
        problems.append(f"{where}: source {src!r} carries no date")
    if kind == "market" and not MARKET_RE.search(src):
        problems.append(f"{where}: a market-implied figure must name the market (CME, swaps, "
                        f"Kalshi...) -- got {src!r}")


def _check_claim(where: str, cl: dict, problems: list, fallback_src: str | None = None) -> None:
    k = cl.get("kind")
    if k not in KINDS:
        problems.append(f"{where}: kind {k!r} not in {KINDS}")
        return
    if k in ("ours", "scenario") and any(x in cl for x in ("pct", "prob", "odds")):
        problems.append(f"{where}: a {k} item carries a probability -- only market prices do")
    _check_src(where, k, cl.get("src") or fallback_src, problems)


def _validate(doc: dict, census: dict, problems: list) -> None:
    for t in THEMES_REQUIRED:
        if t not in (doc.get("themes") or {}):
            problems.append(f"themes: missing {t!r}")
    ids = set()
    for s in doc.get("sections", []):
        sid = s.get("id")
        if not sid or sid in ids:
            problems.append(f"section id {sid!r} missing or duplicated")
        ids.add(sid)
        for bi, b in enumerate(s.get("blocks", [])):
            w = f"{sid}.blocks[{bi}] ({b.get('type')}: {b.get('title', '')[:40]})"
            typ = b.get("type")
            if typ not in BLOCK_TYPES:
                problems.append(f"{w}: unknown block type")
                continue
            kind = b.get("kind")
            bsrc = b.get("src")
            if kind and kind not in KINDS:
                problems.append(f"{w}: kind {kind!r} not in {KINDS}")
            if b.get("after"):
                _check_claim(f"{w}.after", b["after"], problems)
            if typ == "prose":
                _check_claim(w, {"kind": kind, "src": bsrc}, problems)
            elif typ in ("tiles", "steps"):
                for i, it in enumerate(b.get("items", [])):
                    if typ == "steps":
                        # A chain the page authors is Our read; each figure in it is still Reported.
                        _check_src(f"{w}.items[{i}]", "reported", it.get("src"), problems)
                    else:
                        _check_src(f"{w}.items[{i}]", kind, it.get("src") or bsrc, problems)
            elif typ == "cards":
                for ci, card in enumerate(b.get("cards", [])):
                    if card.get("theme") and card["theme"] not in doc["themes"]:
                        problems.append(f"{w}.cards[{ci}]: unknown theme {card['theme']!r}")
                    for j, cl in enumerate(card.get("claims", [])):
                        _check_claim(f"{w}.cards[{ci}].claims[{j}]", cl, problems)
            elif typ == "series":
                pts = b.get("points") or []
                if len(pts) < 2:
                    problems.append(f"{w}: a series needs at least two points")
                for i, p in enumerate(pts):
                    if not isinstance(p.get("v"), (int, float)):
                        problems.append(f"{w}.points[{i}]: non-numeric value {p.get('v')!r}")
                    if not re.match(r"^2026-(08|09)-\d{2}$", p.get("d", "")):
                        problems.append(f"{w}.points[{i}]: date {p.get('d')!r} outside the window")
                    # the point's own date is its date; it still needs its outlet
                    _check_src(f"{w}.points[{i}]", kind, p.get("src"), problems, date_from=p.get("d"))
                _check_src(w, kind, bsrc, problems)
            elif typ in ("bars", "table", "calendar", "events"):
                _check_src(w, kind, bsrc, problems) if typ in ("bars",) else None
                if typ == "table" and "srcCol" in b:
                    for i, row in enumerate(b.get("rows", [])):
                        _check_src(f"{w}.rows[{i}]", kind, row[b["srcCol"]], problems)
                elif typ == "table":
                    _check_src(w, kind, bsrc, problems)
                if typ in ("events", "calendar"):
                    for i, it in enumerate(b.get("items", [])):
                        _check_src(f"{w}.items[{i}]", kind if kind != "scenario" else "reported",
                                   it.get("src") or bsrc, problems)
            elif typ == "scenarios":
                for i, it in enumerate(b.get("items", [])):
                    if any(x in it for x in ("pct", "prob", "odds")):
                        problems.append(f"{w}.items[{i}]: scenarios carry no probabilities")
                    _check_src(f"{w}.items[{i}]", "reported", it.get("src"), problems)
            elif typ == "odds":
                if kind not in (None, "market"):
                    problems.append(f"{w}: odds blocks are market-implied only")
                _check_src(w, "market", bsrc, problems)
            elif typ == "flow":
                for ci, col in enumerate(b.get("columns", [])):
                    for ni, node in enumerate(col.get("nodes", [])):
                        _check_src(f"{w}.columns[{ci}].nodes[{ni}]", "reported", node.get("src"), problems)
            elif typ == "timeline":
                for si, st in enumerate(b.get("stories", [])):
                    if st.get("theme") not in doc["themes"]:
                        problems.append(f"{w}.stories[{si}]: unknown theme {st.get('theme')!r}")
                    if len(st.get("cells", [])) != len(b.get("weeks", [])):
                        problems.append(f"{w}.stories[{si}]: {len(st.get('cells', []))} cells for "
                                        f"{len(b.get('weeks', []))} weeks")
                    for ci, cell in enumerate(st.get("cells", [])):
                        _check_src(f"{w}.stories[{si}].cells[{ci}]", "reported", cell.get("s"), problems)
            elif typ == "heatmap":
                by_date = census["counts"]["byDate"]
                if list(b.get("dates", [])) != list(by_date.keys()):
                    problems.append(f"{w}: heatmap dates {b.get('dates')} do not match the census "
                                    f"file dates {list(by_date.keys())}")
                elif list(b.get("n", [])) != list(by_date.values()):
                    problems.append(f"{w}: heatmap briefs-per-day {b.get('n')} do not match the "
                                    f"census {list(by_date.values())}")
                for r in b.get("rows", []):
                    if len(r.get("v", [])) != len(b.get("dates", [])):
                        problems.append(f"{w}: row {r.get('name')!r} has {len(r.get('v', []))} "
                                        f"cells for {len(b.get('dates', []))} dates")
            elif typ == "conflicts":
                for i, r in enumerate(b.get("rows", [])):
                    for f in ("item", "a", "b", "treatment"):
                        if not r.get(f):
                            problems.append(f"{w}.rows[{i}]: missing {f!r}")


def _substitute(node, counts: dict, problems: list):
    """Fill {{count:*}} tokens from the census. Any other token is an error."""
    def one(s: str) -> str:
        def rep(m):
            key = m.group(1).strip()
            if key.startswith("count:"):
                k = key[6:]
                if k.startswith("pub:"):
                    v = (counts.get("byPublication") or {}).get(k[4:])
                else:
                    v = counts.get(k)
                if isinstance(v, int):
                    return f"{v:,}"
            problems.append(f"unresolvable token {{{{{key}}}}}")
            return m.group(0)
        return TOKEN_RE.sub(rep, s)

    if isinstance(node, str):
        return one(node)
    if isinstance(node, list):
        return [_substitute(v, counts, problems) for v in node]
    if isinstance(node, dict):
        return {k: _substitute(v, counts, problems) for k, v in node.items()}
    return node


# ---------------------------------------------------------------------------- build

def build(cfg: C.Config, built_at: str) -> dict:
    src = _resolve_source(cfg)
    with open(src, encoding="utf-8") as f:
        doc = json.load(f)
    doc["contentFile"] = os.path.basename(src)
    census, census_name = _load_census(cfg, doc["window"]["to"])
    if census["window"]["from"] != doc["window"]["from"]:
        raise MonthlyError(f"census window starts {census['window']['from']} but the content "
                           f"window starts {doc['window']['from']} -- rerun census_briefs.py")

    problems: list = []
    _validate(doc, census, problems)
    doc = _substitute(doc, census["counts"], problems)
    if problems:
        raise MonthlyError("content validation failed:\n  " + "\n  ".join(problems))

    counts = census["counts"]
    kinds = {k: 0 for k in KINDS}

    def tally(node):
        if isinstance(node, dict):
            if node.get("kind") in kinds and "text" in node:
                kinds[node["kind"]] += 1
            # scenario and odds items carry the kind on their block, not on each item
            if node.get("type") == "scenarios":
                kinds["scenario"] += len(node.get("items", []))
            if node.get("type") == "odds":
                kinds["market"] += len(node.get("items", []))
            for v in node.values():
                tally(v)
        elif isinstance(node, list):
            for v in node:
                tally(v)
    tally(doc["sections"])

    doc["generated"] = {
        "censusFile": census_name,
        "censusGeneratedAt": census.get("generated"),
        "counts": {k: counts[k] for k in ("briefs", "files", "dates")},
        "byPublication": [{"key": k, "label": census["publicationLabels"].get(k, k), "n": v}
                          for k, v in sorted(counts["byPublication"].items(), key=lambda kv: -kv[1])],
        "byDate": counts["byDate"],
        "claimKinds": kinds,
        "censusProblems": census.get("problems") or [],
    }

    volatile = ("builtAt", "version", "contentFile")
    doc["builtAt"] = built_at
    doc["version"] = P._version(
        doc["asOf"].replace("-", ""),
        [json.dumps({k: v for k, v in doc.items() if k not in volatile}, sort_keys=True, default=str)])
    return doc


def emit(cfg: C.Config, doc: dict) -> str:
    path = os.path.join(cfg.processed_dir, OUT_DIR, OUT_FILE)
    P._write(path, doc)
    return path


def index_entry(doc: dict) -> dict:
    return {
        "label": doc["label"], "tab": doc["tab"], "order": doc.get("order", 99),
        "kind": "insight", "version": doc["version"], "asOf": doc["asOf"],
        "dir": OUT_DIR, "file": OUT_FILE, "sourceDoc": doc.get("sourceDoc"),
    }


def print_console(doc: dict) -> None:
    g = doc["generated"]
    c = g["counts"]
    print(f"  content: {doc['contentFile']} ({len(doc['sections'])} sections, "
          f"{sum(len(s['blocks']) for s in doc['sections'])} blocks)")
    print(f"  generated from {g['censusFile']}: {c['briefs']} briefs in {c['files']} files over "
          f"{c['dates']} dates -- " + ", ".join(f"{p['label']} {p['n']}" for p in g["byPublication"]))
    print("  claims by kind: " + ", ".join(f"{k} {v}" for k, v in g["claimKinds"].items()))
    for p in g["censusProblems"]:
        print(f"  WARN census: {p}")


def main(argv=None) -> int:
    import datetime as dt
    sys.stdout.reconfigure(encoding="utf-8")
    cfg = C.load()
    built_at = dt.datetime.now().replace(microsecond=0).isoformat()
    try:
        doc = build(cfg, built_at)
    except MonthlyError as e:
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
