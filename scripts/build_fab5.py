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

SOURCE_DIR = os.path.join("data", "insights")
SOURCE_STEM = "fab5_"
OUT_DIR = "insights"
OUT_FILE = "fab5.json"

GRADES = ("a", "b", "c", "d")
DIRECTIONS = ("bull", "bear", "neutral")
VERDICTS = ("confirmed", "contradicted", "unresolved", "new")
CK_STATUS = ("ok", "warn", "bad", "new")
HORIZONS = ("near", "medium")

# Most specific universe wins. A name in both semis and market_internals belongs to semis: the
# focused tab carries all four z-windows and a peer set that means something, the broad tab
# carries one z-window and 495 peers.
RESOLUTION_ORDER = ["semis", "hw_networking", "software", "market_internals"]


class Fab5Error(Exception):
    pass


def _resolve_source(cfg: C.Config) -> str:
    """Newest dated fab5_<date>.json, the way loaders.resolve_input picks a workbook vintage.

    A content refresh drops a new dated file beside the old one and keeps both, so pinning a
    filename here would silently keep rendering the previous run after a refresh.
    """
    d = cfg.path(SOURCE_DIR)
    if not os.path.isdir(d):
        raise Fab5Error(f"missing content directory: {d}")
    cands = sorted(f for f in os.listdir(d)
                   if f.startswith(SOURCE_STEM) and f.endswith(".json"))
    if not cands:
        raise Fab5Error(f"no {SOURCE_STEM}<date>.json content file in {d}")
    return os.path.join(d, cands[-1])


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

    src = _resolve_source(cfg)
    with open(src, encoding="utf-8") as f:
        doc = json.load(f)
    doc["contentFile"] = os.path.basename(src)

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

    # ------------------------------------------------------- schemaVersion 2: the infographic
    # The infographic is a CLAIM surface, so its gate is provenance rather than arithmetic:
    # there is nothing to recompute, only the question of whether each figure came from
    # somewhere. A stat with no `sources` is the exact failure this is here to catch -- it
    # renders as a confident number with nobody behind it.
    if doc.get("schemaVersion", 1) >= 2:
        for i, st in enumerate(doc.get("stats", [])):
            where = f"stats[{i}] ({st.get('kicker') or 'no kicker'})"
            for field in ("kicker", "num", "lab", "sources", "grade"):
                if not st.get(field):
                    problems.append(f"{where}: missing {field!r} -- an infographic figure must "
                                    f"resolve to a generated count or an explicitly sourced field")
            if st.get("grade") not in GRADES:
                problems.append(f"{where}: grade {st.get('grade')!r} not in {GRADES}")

        wc = doc.get("whatChanged") or {}
        if not wc:
            problems.append("whatChanged: missing -- the delta banner has nothing to render")
        else:
            for field in ("priorBaseline", "headline", "body", "bullets"):
                if not wc.get(field):
                    problems.append(f"whatChanged: missing {field!r}")
            if wc.get("priorBaseline") and wc["priorBaseline"] != doc.get("priorBaseline"):
                problems.append(
                    f"whatChanged.priorBaseline {wc['priorBaseline']!r} disagrees with the "
                    f"document's own priorBaseline {doc.get('priorBaseline')!r}. A stale value "
                    f"silently mislabels which claims are new.")
            for j, b in enumerate(wc.get("bullets", [])):
                if not b.get("sources"):
                    problems.append(f"whatChanged.bullets[{j}] ({b.get('title')}): missing sources")

        for i, ins in enumerate(doc.get("insights", [])):
            pr = ins.get("priorRun")
            where = f"insights[{i}] ({ins.get('id')})"
            if not pr:
                problems.append(f"{where}: missing priorRun -- the momentum row counts these")
                continue
            if pr.get("verdict") not in VERDICTS:
                problems.append(f"{where}: priorRun.verdict {pr.get('verdict')!r} not in {VERDICTS}")
            for field in ("predicted", "outcome"):
                if not pr.get(field):
                    problems.append(f"{where}: priorRun missing {field!r}")

        for i, ck in enumerate(doc.get("checklist", [])):
            where = f"checklist[{i}] (#{ck.get('n')})"
            if ck.get("status") not in CK_STATUS:
                problems.append(f"{where}: status {ck.get('status')!r} not in {CK_STATUS}")
            if not ck.get("statusLabel"):
                problems.append(f"{where}: missing statusLabel -- the bucket is ours, the label "
                                f"is the source's own word and both are rendered")

        for i, d in enumerate(doc.get("disputes", [])):
            for j, side in enumerate(d.get("sides", [])):
                if not isinstance(side, dict) or not side.get("house") or not side.get("position"):
                    problems.append(f"disputes[{i}].sides[{j}]: schemaVersion 2 requires "
                                    f"{{house, position}} so a side is attributable")

        near = [s for s in doc.get("scenarios", []) if s.get("horizon") == "near"]
        for i, s in enumerate(doc.get("scenarios", [])):
            where = f"scenarios[{i}] ({s.get('name')} / {s.get('horizon')})"
            if s.get("horizon") not in HORIZONS:
                problems.append(f"{where}: horizon {s.get('horizon')!r} not in {HORIZONS}")
            if not s.get("sources"):
                problems.append(f"{where}: missing sources")
            if s.get("horizon") == "near" and not isinstance(s.get("pct"), (int, float)):
                problems.append(f"{where}: a near-term scenario must carry a numeric pct")
        if near:
            total = sum(s["pct"] for s in near if isinstance(s.get("pct"), (int, float)))
            if round(total) != 100:
                problems.append(f"scenarios: near-term probabilities sum to {total}, not 100")

        for i, c in enumerate(doc.get("calendar", [])):
            for field in ("date", "body", "sources"):
                if not c.get(field):
                    problems.append(f"calendar[{i}] ({c.get('date') or 'no date'}): missing {field!r}")

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

    # The infographic's counts are GENERATED here rather than typed into the content file, which
    # is the split that keeps the page honest: a count is never dressed up as a judgement, and
    # the hand-authored rows above always carry a source. Anything the build can count, it counts.
    if doc.get("schemaVersion", 1) >= 2:
        def _tally(seq, key):
            out = {}
            for item in seq:
                out[key(item)] = out.get(key(item), 0) + 1
            return out

        ck = doc.get("checklist", [])
        doc["infographic"] = {
            "checklistCounts": {s: sum(1 for c in ck if c.get("status") == s) for s in CK_STATUS},
            "checklistTotal": len(ck),
            "addendumCount": sum(1 for c in ck if c.get("addendum")),
            "verdictCounts": {v: sum(1 for i in doc["insights"]
                                     if (i.get("priorRun") or {}).get("verdict") == v)
                              for v in VERDICTS},
            "disputeStatusCounts": _tally(doc.get("disputes", []),
                                          lambda d: d.get("status") or "unlabelled"),
            "namedDevelopments": sum(1 for i in doc["implications"] if i.get("scope") == "name"),
            "directionCounts": _tally(doc["implications"], lambda i: i["direction"]),
            "houseCount": len(doc.get("sources", [])),
            "layerCount": len(doc.get("layers", [])),
        }
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
    print(f"  content: {doc.get('contentFile')} (schemaVersion {doc.get('schemaVersion', 1)})")
    print(f"  content: {len(doc['insights'])} insights, {len(doc['agreement'])} agreements, "
          f"{len(doc['disputes'])} disputes, {len(doc['checklist'])} checklist items")
    if doc.get("schemaVersion", 1) >= 2:
        ig = doc["infographic"]
        print(f"  infographic: {len(doc['stats'])} stat tiles, "
              f"{len(doc['whatChanged']['bullets'])} what-changed movements, "
              f"{len(doc['scenarios'])} scenarios, {len(doc['calendar'])} dated catalysts")
        print(f"    signal board: " + ", ".join(f"{k} {v}" for k, v in ig["checklistCounts"].items())
              + f" (addendum {ig['addendumCount']})")
        print(f"    prior-run verdicts: "
              + ", ".join(f"{k} {v}" for k, v in ig["verdictCounts"].items()))
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
