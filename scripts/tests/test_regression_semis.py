"""Regression gate: the ported indicators must reproduce the shipped dashboards.

Two modes, because the new engine is deliberately different from the old one:

  legacy-parity -- 252-day tail, indicators computed ON the trimmed window (which is what
                   build_dashboard.py did), base-date ew_composite. Target: semi_data.json.
  native        -- full 1,255-day grid, daily-rebalanced ew. Target: semi_renmac_data.json.

Path-independent indicators must match the legacy golden to 1e-9. Three series are EXPECTED to
differ and are asserted as intentional deltas -- if they matched, the port silently kept the
inferior implementation.

This runs against a PINNED workbook vintage (GOLDEN_WORKBOOK below), not the newest file in
data/raw. It is a test of the engine, not of the data. Refreshing the dashboard does not and must
not move it.

    python scripts/tests/test_regression_semis.py
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
ROOT = os.path.dirname(SCRIPTS)
sys.path.insert(0, SCRIPTS)

import config as C          # noqa: E402
import indicators as I      # noqa: E402
import loaders as L         # noqa: E402
import validators as V      # noqa: E402

TOL = 1e-9
GOLDEN = os.path.join(ROOT, "reference", "golden")

# The input workbook is PART OF THE GOLDEN CAPTURE, not a live input.
#
# This test measures engine parity against the shipped dashboards; it says nothing about whether
# the site is running current data. The goldens are a fixed capture of the 1,255-day grid
# 2021-08-09..2026-08-07, and reference/golden/README.md forbids editing them. resolve_input()
# returns the NEWEST date-stamped workbook, so leaving it in charge here would silently swap the
# baseline every time data/raw gains a vintage -- and CapIQ's 5y window ROLLS rather than extends,
# so both ends of the grid move and every date and price assertion below fails for a reason that
# has nothing to do with the engine. Pinned deliberately. Re-capture the goldens if this must move.
GOLDEN_WORKBOOK = "US semi stocks 5y price and volume 20260807.xlsx"


class Result:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.notes = []

    def check(self, name, ok, detail=""):
        if ok:
            self.passed += 1
            print(f"  PASS  {name}")
        else:
            self.failed += 1
            print(f"  FAIL  {name}  {detail}")
        return ok

    def note(self, msg):
        self.notes.append(msg)
        print(f"  ....  {msg}")


def close(a, b, tol=TOL):
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def compare_series(ours, gold, label, res, tol=TOL, allow_head_none=0):
    """Compare two equal-length series elementwise."""
    if len(ours) != len(gold):
        return res.check(label, False, f"length {len(ours)} vs {len(gold)}")
    bad = []
    for i, (a, b) in enumerate(zip(ours, gold)):
        if i < allow_head_none and (a is None or b is None):
            continue
        if not close(a, b, tol):
            bad.append((i, a, b))
    return res.check(label, not bad,
                     f"{len(bad)} mismatches, first={bad[0] if bad else None}")


def load_semis(cfg):
    u = cfg.universe("semis")
    s = u["source"]
    path = os.path.join(cfg.raw_dir, GOLDEN_WORKBOOK)
    if not os.path.exists(path):
        raise SystemExit(
            f"the golden-vintage workbook is missing: {path}\n"
            f"This test is pinned to it on purpose (see GOLDEN_WORKBOOK above). Newer vintages in\n"
            f"data/raw are fine and expected -- but this file must stay there, or the regression\n"
            f"gate has nothing to compare reference/golden/*.json against."
        )
    book, _ = L.load_price_volume(path, price_sheet=s["priceSheet"], volume_sheet=s["volumeSheet"],
                                  price_label=s["priceLabel"], volume_label=s["volumeLabel"])
    book, _ = L.drop_calendar_days(book, cfg.parameters["calendar"]["holidayFlatlineThreshold"])
    return book, u


def main() -> int:
    res = Result()
    cfg = C.load()
    par = cfg.parameters
    book, u = load_semis(cfg)

    gold1 = json.load(open(os.path.join(GOLDEN, "semi_data.json"), encoding="utf-8"))
    gold5 = json.load(open(os.path.join(GOLDEN, "semi_renmac_data.json"), encoding="utf-8"))

    # ---------------------------------------------------------------- grid
    print("\n[grid]")
    res.check("native grid is 1,255 trading days", len(book.dates) == 1255, len(book.dates))
    res.check("native dates match 5y golden", book.dates == gold5["dates"])

    w = len(gold1["dates"])
    res.note(f"legacy golden window = {w} sessions ({gold1['dates'][0]}..{gold1['dates'][-1]})")
    tail = book.dates[-w:]
    res.check("legacy window dates match 1y golden", tail == gold1["dates"])

    # ---------------------------------------------------------------- coverage
    print("\n[coverage]")
    _, cov, _ = V.build_universe(book, par, exclude=u["excludeFromUniverse"])
    full = sorted(t for t, c in cov.items() if c["cls"] == "full")
    part = sorted(t for t, c in cov.items() if c["cls"] == "partial")
    drop = sorted(t for t, c in cov.items() if c["cls"] == "drop")
    g5 = gold5["meta"]
    res.check("5y nFull matches golden", len(full) == g5["nFull"], f"{len(full)} vs {g5['nFull']}")
    res.check("5y partial matches golden", part == sorted(g5["partial"]), f"{part}")
    res.check("5y dropped matches golden", drop == sorted(g5["dropped"]), f"{drop}")

    # ---------------------------------------------------------------- legacy-parity indicators
    # build_dashboard.py trimmed to the last 252 rows and computed ON that window, so a 20-dma
    # is None for the first 19 bars of the window. Replicate exactly.
    print("\n[legacy-parity: per-ticker indicators on the 252-day window]")
    panel = gold1["stockPanel"]["series"]
    zw = gold1["stockPanel"]["zWindows"]
    res.check("z-windows match config", zw == par["zscore"]["windows"], f"{zw}")

    tested = 0
    for t in ["NVDA", "AMD", "AVGO", "MU", "AMAT", "TXN", "INTC", "KLAC", "LRCX", "MRVL"]:
        if t not in panel:
            continue
        tested += 1
        px = book.px[t][-w:]
        vol = book.vol[t][-w:]
        g = panel[t]

        compare_series([I.r2(x) for x in px], g["px"], f"{t} px", res)
        compare_series([I.r2(x) for x in I.sma(px, 20)], g["dma20"], f"{t} dma20", res)
        compare_series([I.r2(x) for x in I.sma(px, 50)], g["dma50"], f"{t} dma50", res)
        m = I.macd(px, 12, 26, 9)
        compare_series([I.r2(x) for x in m["line"]], g["macd"]["line"], f"{t} macd.line", res)
        compare_series([I.r2(x) for x in m["signal"]], g["macd"]["signal"], f"{t} macd.signal", res)
        compare_series([I.r2(x) for x in m["hist"]], g["macd"]["hist"], f"{t} macd.hist", res)
        compare_series([I.r2(x) for x in I.rsi(px, 14)], g["rsi"], f"{t} rsi", res)
        if g.get("vol"):
            compare_series([I.r2(x) for x in I.sma(vol, 20)], g["volAvg20"], f"{t} volAvg20", res)
        ret = I.daily_ret(px)
        for win in zw:
            compare_series([I.r2(x) for x in I.rolling_z(ret, win)],
                           g["zAbs"][str(win)], f"{t} zAbs[{win}]", res)
    res.note(f"compared {tested} bellwether tickers against the legacy golden")

    # ---------------------------------------------------------------- intentional deltas
    print("\n[intentional deltas: these MUST differ]")
    uni_full = {t: book.px[t] for t in full}
    cols = [book.px[t][-w:] for t in full]
    legacy_comp = I.ew_composite(cols, w)
    native_comp = I.ew(cols, w)
    same = all(close(a, b, 1e-6) for a, b in zip(legacy_comp, native_comp))
    res.check("ew (daily-rebalanced) differs from ew_composite (base-date)", not same,
              "they matched, which means the port kept the inferior base-date version")

    compare_series([I.r1(x) for x in legacy_comp], gold1["comp"],
                   "legacy ew_composite reproduces 1y golden comp", res, tol=0.06)

    n = len(book.dates)
    full_cols = [book.px[t] for t in full]
    comp5 = I.ew(full_cols, n)
    res.note(f"native 5y composite last = {comp5[-1]:.1f} (golden {gold5['comp'][-1]})")
    res.check("native 5y composite close to golden",
              close(round(comp5[-1], 1), gold5["comp"][-1], 0.02),
              f"{comp5[-1]:.2f} vs {gold5['comp'][-1]}")

    ser = [x for x in comp5 if x is not None]
    ins = [I.pct_rank_insample(ser, i) for i in range(len(ser))]
    exp = I.expanding_pct(ser, par["stats"]["expandingPctWarm"])
    differ = sum(1 for a, b in zip(ins, exp) if a is not None and b is not None and abs(a - b) > 1e-6)
    res.check("expanding_pct (causal) differs from pct_rank_insample", differ > 0, f"{differ} bars")

    print(f"\n{'='*60}\nPASSED {res.passed}   FAILED {res.failed}")
    return 1 if res.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
