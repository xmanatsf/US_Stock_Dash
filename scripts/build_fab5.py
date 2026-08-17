"""Build the Fab5 cross-source page.

This is not a universe. There is no workbook, no composite and no regime — the content is a
hand-authored reading of `Fab5_Cross_Source_Synthesis_20260814.md`, which is prose and cannot be
honestly parsed. What this script adds on top of that hand-authored file is the one thing the
page must not get wrong: every ticker it names is joined to the SAME pipeline output the other
four tabs render, at build time, so the page can never quietly become a second and divergent
source of prices.

Two rules follow from that, and both are enforced below rather than trusted:

  * A ticker is either resolvable against a built universe, or it carries an explicit
    `external: true` with a written reason. There is no third case, and an unresolved ticker is a
    fatal build error — silently dropping it would turn a missing join into a missing bullet.
  * Nothing here computes an indicator. Every number in the strip is read out of
    data/processed/<universe>/, so "the tab disagrees with the dashboard" is not expressible.

Run via build_all (which owns index.json), or standalone for a quick iteration on the content:

    python scripts/build_fab5.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config as C        # noqa: E402
import pipeline as P      # noqa: E402

SOURCE = os.path.join("data", "insights", "fab5_20260814.json")
OUT_DIR = "insights"
OUT_FILE = "fab5.json"

GRADES = ("a", "b", "c", "d")
DIRECTIONS = ("bull", "bear", "neutral")

# Most specific universe wins. A name in both semis and market_internals belongs to semis: the
# focused tab carries all four z-windows and a peer set that means something, the broad tab
# carries one z-window and 495 peers.
RESOLUTION_ORDER = ["semis", "hw_networking", "software", "market_internals"]


class Fab5Error(Exception):
    pass


def _load_universe_index(processed_dir: str) -> tuple[dict, dict]:
    """ticker -> universe key, plus universe key -> (manifest, summary)."""
    owner, unis = {}, {}
    for key in RESOLUTION_ORDER:
        d = os.path.join(processed_dir, key)
        mp = os.path.join(d, "manifest.json")
        sp = os.path.join(d, "summary.json")
        if not (os.path.exists(mp) and os.path.exists(sp)):
            continue
        with open(mp, encoding="utf-8") as f:
            man = json.load(f)
        with open(sp, encoding="utf-8") as f:
            summ = json.load(f)
        if man.get("status") != "ok":
            continue
        unis[key] = (man, summ)
        for t in man.get("tickers", {}):
            owner.setdefault(t, key)          # setdefault == first in RESOLUTION_ORDER wins
    return owner, unis


def _strip(processed_dir: str, key: str, ticker: str, unis: dict) -> dict:
    """The live technical strip. Every field is READ, never recomputed."""
    man, summ = unis[key]
    row = next((r for r in summ.get("stocks", []) if r["t"] == ticker), None)
    meta = man["tickers"][ticker]
    with open(os.path.join(processed_dir, key, meta["f"]), encoding="utf-8") as f:
        shard = json.load(f)

    rsi = next((v for v in reversed(shard.get("rsi") or []) if v is not None), None)
    verdict = summ.get("verdict") or {}
    return {
        "universe": key,
        "universeLabel": man["label"],
        "tab": _TAB_OF[key],
        "asOf": man["lastDate"],
        "px": row and row["px"],
        "ret1y": row and row["ret1y"],
        "offHi": row and row["offHi"],
        "hiDate": row and row["hiDate"],
        "roc": row and row["roc"],
        "a20": row and row["a20"],
        "a50": row and row["a50"],
        "relVol": row and row["relVol"],
        "rsi": rsi,
        "pinned": bool(meta.get("pinned")),
        "partial": bool(meta.get("part")),
        "regime": verdict.get("regime"),
        "regimeScore": verdict.get("score"),
        "signals": shard.get("signals") or [],
    }


_TAB_OF: dict = {}


def build(cfg: C.Config, built_at: str) -> dict:
    global _TAB_OF
    _TAB_OF = {k: cfg.universe(k)["tab"] for k in cfg.universes["universes"]}

    src = cfg.path(SOURCE)
    if not os.path.exists(src):
        raise Fab5Error(f"missing content file: {src}")
    with open(src, encoding="utf-8") as f:
        doc = json.load(f)

    owner, unis = _load_universe_index(cfg.processed_dir)
    if not unis:
        raise Fab5Error(
            "no universe has been built yet, so no ticker can be joined. Run build_all.py — "
            "this page is built after the universes on purpose."
        )

    # ---------------------------------------------------------------- validate the content
    problems = []
    for i, ins in enumerate(doc.get("insights", [])):
        where = f"insights[{i}] ({ins.get('id') or 'no id'})"
        for field in ("id", "headline", "claim", "evidence", "sources", "grade", "direction"):
            if not ins.get(field):
                problems.append(f"{where}: missing {field!r}")
        if ins.get("grade") not in GRADES:
            problems.append(f"{where}: grade {ins.get('grade')!r} not in {GRADES}")
        if ins.get("direction") not in DIRECTIONS:
            problems.append(f"{where}: direction {ins.get('direction')!r} not in {DIRECTIONS}")
    for i, imp in enumerate(doc.get("implications", [])):
        where = f"implications[{i}] ({imp.get('ticker') or 'no ticker'})"
        for field in ("ticker", "line", "direction", "sources", "grade"):
            if not imp.get(field):
                problems.append(f"{where}: missing {field!r}")
        if imp.get("grade") not in GRADES:
            problems.append(f"{where}: grade {imp.get('grade')!r} not in {GRADES}")
        if imp.get("direction") not in DIRECTIONS:
            problems.append(f"{where}: direction {imp.get('direction')!r} not in {DIRECTIONS}")
    if problems:
        raise Fab5Error("content validation failed:\n  " + "\n  ".join(problems))

    # ---------------------------------------------------------------- join
    unresolved, joined, external = [], 0, 0
    for imp in doc["implications"]:
        t = imp["ticker"]
        key = owner.get(t)
        if key:
            imp["live"] = _strip(cfg.processed_dir, key, t, unis)
            joined += 1
            if imp.get("external"):
                problems.append(
                    f"{t} is marked external but resolves to {key}; remove the flag or the reason "
                    f"is stale")
        elif imp.get("external"):
            if not imp.get("externalReason"):
                problems.append(f"{t} is marked external with no externalReason")
            imp["live"] = None
            external += 1
        else:
            unresolved.append(t)

    if unresolved:
        problems.append(
            "these tickers resolve to no built universe and are not marked external: "
            + ", ".join(sorted(unresolved))
            + ". Either they are absent from this workbook vintage (mark external with a reason) "
              "or the ticker is wrong. They are NOT dropped silently.")
    if problems:
        raise Fab5Error("join failed:\n  " + "\n  ".join(problems))

    # Tickers named on an insight but never given an implication row would be a dead link in the
    # UI, so they are reported rather than rendered.
    named = {t for ins in doc["insights"] for t in ins.get("tickers", [])}
    have = {imp["ticker"] for imp in doc["implications"]}
    doc["insightTickersWithoutImplication"] = sorted(named - have)

    grids = {k: (m["lastDate"], m["dateCount"]) for k, (m, _) in unis.items()}
    doc["universeAsOf"] = sorted({g[0] for g in grids.values()})
    doc["builtAt"] = built_at
    doc["version"] = P._version(
        doc["asOf"].replace("-", ""),
        [json.dumps(doc.get("insights"), sort_keys=True),
         json.dumps(doc.get("implications"), sort_keys=True)])
    doc["joinStats"] = {"joined": joined, "external": external,
                        "universes": {k: len(m.get("tickers", {})) for k, (m, _) in unis.items()}}
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
    js = doc["joinStats"]
    print(f"  content: {len(doc['insights'])} insights, {len(doc['agreement'])} agreements, "
          f"{len(doc['disputes'])} disputes, {len(doc['checklist'])} checklist items")
    print(f"  implications: {len(doc['implications'])} tickers -- "
          f"{js['joined']} joined to a live universe, {js['external']} external (no price data)")
    print(f"  universe as-of: {', '.join(doc['universeAsOf'])}")
    orphan = doc["insightTickersWithoutImplication"]
    if orphan:
        print(f"  NOTE {len(orphan)} ticker(s) named on an insight have no implication row "
              f"(not rendered as links): {', '.join(orphan)}")


def main(argv=None) -> int:
    import datetime as dt
    cfg = C.load()
    built_at = dt.datetime.now().replace(microsecond=0).isoformat()
    try:
        doc = build(cfg, built_at)
    except Fab5Error as e:
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
