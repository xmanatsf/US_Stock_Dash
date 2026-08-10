"""Load and validate every configured universe. Run this before trusting any indicator.

    python scripts/validate_all.py            # console report
    python scripts/validate_all.py --json     # also write data/processed/validation_report.json

Exit code is 1 if any universe has a fatal finding, else 0. Warnings do not fail the run but are
printed -- the point is that they are reviewed, not that they are absent.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config as C           # noqa: E402
import loaders as L          # noqa: E402
import validators as V       # noqa: E402


def load_book(cfg: C.Config, key: str):
    u = cfg.universe(key)
    s = u["source"]
    path = L.resolve_input(cfg.raw_dir, s["stem"], s.get("dateStamped", True))
    book, findings = L.load_price_volume(
        path,
        price_sheet=s.get("priceSheet", "Price"),
        volume_sheet=s.get("volumeSheet", "Volume"),
        price_label=s.get("priceLabel", "Day Close Price"),
        volume_label=s.get("volumeLabel", "Volume"),
        strict_labels=s.get("strictLabels", True),
    )
    if not book.dates:
        return book, findings, path
    thr = cfg.parameters["calendar"]["holidayFlatlineThreshold"]
    book, _ = L.drop_calendar_days(book, thr)
    return book, findings, path


def validate(cfg: C.Config, key: str, books: dict) -> tuple[V.Report, dict, dict]:
    u = cfg.universe(key)
    par = cfg.parameters
    exp = par["calendar"]["expected"]
    book, load_findings, path = books[key]

    rep = V.Report(key)
    rep.add(load_findings)
    rep.add(V.check_date_grid(book.dates, exp.get("tradingDays"), exp.get("lastDate")))

    # cross-workbook duplication: this is what caught the first corrupt hardware export
    for other in u.get("crossCheckAgainst", []):
        if other in books and books[other][0].dates:
            rep.add(V.cross_workbook_identity(book, books[other][0], key, other))

    # Scan only what will actually be scored. A ticker already excluded by config with a written
    # reason is a resolved issue, not an outstanding fatal -- EXCLUDED_BY_CONFIG records it below.
    skip = set(u.get("excludeFromUniverse", [])) | {
        e["ticker"] for e in u.get("excludeTickers", [])
    }
    flat = V.scan_flatlines(book.px, book.vol, book.dates,
                            tickers=[t for t in book.tickers if t not in skip])
    rep.add(flat)
    pinned = []
    for f in flat:
        if f.code == "TERMINAL_FLATLINE":
            pinned = list(f.tickers)

    universe, coverage, cov_findings = V.build_universe(
        book, par,
        exclude=u.get("excludeFromUniverse", []),
        exclude_tickers=u.get("excludeTickers", []),
        pinned=pinned,
    )
    rep.add(cov_findings)
    rep.add(V.scan_gaps(universe))
    rep.add(V.check_extreme_returns(universe))

    sb = cfg.sub_baskets(key)
    if sb:
        rep.add(V.check_basket_membership(sb.get("baskets"), universe.keys()))

    if u.get("sectorMap"):
        src = cfg.sectors["sources"][u["sectorMap"]]
        mpath = L.resolve_input(cfg.raw_dir, src["file"]["stem"], src["file"].get("dateStamped", False))
        mapping, mf = L.load_mapping(mpath, sheet=src["sheet"],
                                     data_start_row=src["layout"]["dataStartRow"],
                                     columns=src["columns"])
        rep.add(mf)
        rep.add(V.check_mapping_coverage(list(universe.keys()), mapping))
        exp_cov = src.get("expectedCoverage") or {}
        if exp_cov:
            secs = {mapping[t]["sector"] for t in universe if t in mapping}
            igs = {mapping[t]["industryGroup"] for t in universe if t in mapping}
            if exp_cov.get("sectors") and len(secs) != exp_cov["sectors"]:
                rep.add([V.Finding("SECTOR_COUNT", "warn",
                                   f"{len(secs)} sectors, expected {exp_cov['sectors']}")])
            if exp_cov.get("industryGroups") and len(igs) != exp_cov["industryGroups"]:
                rep.add([V.Finding("INDUSTRY_GROUP_COUNT", "warn",
                                   f"{len(igs)} industry groups, expected {exp_cov['industryGroups']}")])

    return rep, coverage, {"path": path, "n": len(universe), "calendar": book.calendar}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="write data/processed/validation_report.json")
    ap.add_argument("--only", help="validate a single universe")
    args = ap.parse_args(argv)

    cfg = C.load()
    keys = [args.only] if args.only else cfg.universe_keys()

    books = {}
    for k in cfg.universe_keys():
        books[k] = load_book(cfg, k)

    out, worst = {}, 0
    grids = {}
    for k in keys:
        rep, coverage, meta = validate(cfg, k, books)
        cal = meta["calendar"] or {}
        print(f"\n=== {k}  ({os.path.basename(meta['path'])})")
        print(f"  rows {cal.get('rawRows')} -> weekends -{cal.get('weekendRows')} "
              f"-> holidays -{cal.get('holidayRows')} -> {cal.get('tradingDays')} trading days "
              f"({cal.get('sessionsPerYear')}/yr), {cal.get('firstDate')}..{cal.get('lastDate')}")
        print(f"  universe: {meta['n']} tickers scored")
        rep.print_console()
        out[k] = {"report": rep.to_dict(), "calendar": cal,
                  "universeSize": meta["n"], "source": os.path.basename(meta["path"])}
        grids[k] = books[k][0].dates
        worst = max(worst, 1 if rep.status != "ok" else 0)

    ref = grids.get("semis") or next(iter(grids.values()), None)
    same = {k: (v == ref) for k, v in grids.items()}
    print(f"\n=== trading-day grid identical across universes: {all(same.values())}")
    for k, v in same.items():
        if not v:
            print(f"    MISMATCH: {k} ({len(grids[k])} days vs {len(ref)})")
    out["_gridIdentical"] = all(same.values())

    if args.json:
        os.makedirs(cfg.processed_dir, exist_ok=True)
        p = os.path.join(cfg.processed_dir, "validation_report.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1)
        print(f"\nwrote {p}")

    print(f"\nOVERALL: {'FATAL FINDINGS PRESENT' if worst else 'no fatal findings'}")
    return worst


if __name__ == "__main__":
    raise SystemExit(main())
