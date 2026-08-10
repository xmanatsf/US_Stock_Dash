"""Build every tab's data. Order is load-bearing.

    python scripts/build_all.py                 # build all, copy to site/data
    python scripts/build_all.py --only semis
    python scripts/build_all.py --no-copy

Benchmarks are extracted FIRST, once, from the configured source workbook: SPY and SMH exist
only in the semiconductor and hardware exports, and one extraction gives every universe the same
trading grid instead of four chances to disagree.

Exit code 1 if any universe ends in validation_failed.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config as C        # noqa: E402
import loaders as L       # noqa: E402
import pipeline as P      # noqa: E402
from validate_all import load_book  # noqa: E402


def load_mapping_for(cfg, key):
    """Sector mapping, if this universe has one. Layout comes from sectors.json, never hardcoded."""
    u = cfg.universe(key)
    if not u.get("sectorMap"):
        return None
    src = cfg.sectors["sources"][u["sectorMap"]]
    path = L.resolve_input(cfg.raw_dir, src["file"]["stem"], src["file"].get("dateStamped", False))
    mapping, _ = L.load_mapping(path, sheet=src["sheet"],
                                data_start_row=src["layout"]["dataStartRow"],
                                columns=src["columns"])
    return mapping


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", action="append", help="build a single universe (repeatable)")
    ap.add_argument("--no-copy", action="store_true", help="skip the copy into site/data")
    args = ap.parse_args(argv)

    cfg = C.load()
    built_at = dt.datetime.now().replace(microsecond=0).isoformat()
    keys = args.only or cfg.universe_keys()

    print("loading workbooks...")
    books = {}
    for k in cfg.universe_keys():
        books[k] = load_book(cfg, k)
        b = books[k][0]
        print(f"  {k:17} {len(b.tickers):3} columns, {len(b.dates)} trading days")

    print("\nextracting benchmarks (once, before any tab build)...")
    bench = P.build_benchmarks(cfg, books)
    os.makedirs(cfg.processed_dir, exist_ok=True)
    P._write(os.path.join(cfg.processed_dir, "benchmarks.json"), bench)
    print(f"  {sorted(bench['series'])} over {len(bench['dates'])} sessions")

    index = {"schemaVersion": 1, "builtAt": built_at, "universes": {}}
    worst = 0
    for k in keys:
        print(f"\n=== building {k}")
        summary, shards, rep = P.build_universe_payload(
            cfg, k, books, bench, built_at, mapping=load_mapping_for(cfg, k))
        man = P.emit(cfg, k, summary, shards, cfg.processed_dir)
        rep.print_console()
        if summary["status"] == "ok":
            v = summary["verdict"]
            m = summary["meta"]
            print(f"  regime: {v['regime']}  score {v['score']}  (pillar coverage {v['coverage']}%)")
            print(f"  composite {v['comp']} | peak {v['peakVal']} on {v['peakDate']} "
                  f"({v['drawdown']}%) | trough {v['troughVal']} on {v['troughDate']} "
                  f"(+{v['upFromTrough']}%)")
            print(f"  universe {m['nFull']} full / {m['nPartial']} partial / "
                  f"{len(m['dropped'])} dropped / {len(m['excluded'])} excluded")
            print(f"  breadth b20={summary['b20'][-1]}% b50={summary['b50'][-1]}% "
                  f"b200={summary['b200'][-1]}%")
            print(f"  events: {len(summary['events'])} | regime runs: {len(summary['runs'])}")
            for lvl, rows in (summary.get("rollups") or {}).items():
                scored = sum(1 for r in rows if r.get("comp"))
                print(f"  rollup[{lvl}]: {len(rows)} groups, {scored} scored, "
                      f"{len(rows)-scored} below the n>=3 minimum")
            if summary.get("compositeSplit"):
                cs = summary["compositeSplit"][0]
                print(f"  widest intra-sector spread: {cs['parent']} "
                      f"{cs['hiGroup']} {cs['hiRet']:+.0f}% vs {cs['loGroup']} {cs['loRet']:+.0f}%")
            sb = man.get("shardBytes", 0)
            print(f"  payload: summary {man.get('_summaryBytes',0)/1e6:.2f} MB + "
                  f"{len(man['tickers'])} shards {sb/1e6:.2f} MB "
                  f"(avg {sb/max(1,len(man['tickers']))/1e3:.0f} KB)")
        else:
            print(f"  STATUS {summary['status']} -- tab will render its validation banner")
            worst = 1
        index["universes"][k] = {
            "label": summary["label"], "tab": cfg.universe(k)["tab"],
            "order": cfg.universe(k).get("order", 99),
            "status": summary["status"], "version": summary["version"],
            "dir": k,
        }

    p = os.path.join(cfg.processed_dir, "index.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=1)

    if not args.no_copy:
        P.copy_to_site(cfg.processed_dir, cfg.site_data_dir)
        print(f"\ncopied data -> {cfg.site_data_dir}")

    print(f"\nOVERALL: {'validation failures present' if worst else 'all universes built clean'}")
    return worst


if __name__ == "__main__":
    raise SystemExit(main())
