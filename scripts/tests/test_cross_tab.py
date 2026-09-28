"""Cross-tab consistency: a ticker that appears in two universes must read identically.

ADBE is in both the S&P 500 and the software universes; AAPL is in both the S&P 500 and the
hardware universes; SNDK is in the S&P 500 and hardware. If the two tabs disagree on price, MACD
or RSI for the same ticker on the same date, one of the loaders or the calendar drop is wrong.

Also checks that every universe shares one trading grid, and that the shared benchmark series is
byte-identical wherever it appears.

    python scripts/tests/test_cross_tab.py
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DATA = os.path.join(ROOT, "data", "processed")

TOL = 1e-9
PAIRS = [
    ("ADBE", "market_internals", "software"),
    ("AAPL", "market_internals", "hw_networking"),
    ("SNDK", "market_internals", "hw_networking"),
    ("MSFT", "market_internals", "software"),
    ("NVDA", "market_internals", "semis"),
    ("AVGO", "market_internals", "semis"),
    ("MU",   "market_internals", "semis"),
    ("INTC", "market_internals", "semis"),
    # biotech and pharma, added with the 20260927 vintage
    ("AMGN", "market_internals", "biotech"),
    ("VRTX", "market_internals", "biotech"),
    ("ABBV", "market_internals", "biotech"),
    ("LLY",  "market_internals", "pharma"),
    ("MRK",  "market_internals", "pharma"),
    ("ZTS",  "market_internals", "pharma"),
]


def load(uni, name):
    p = os.path.join(DATA, uni, name)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def shard(uni, t):
    return load(uni, os.path.join("tickers", f"{t}.json"))


def align(rec, n):
    """Pad a shard's arrays back onto the universe grid."""
    off = rec.get("i0", 0)
    pad = lambda a: (None if a is None else [None] * off + a)
    return {
        "px": pad(rec["px"]),
        "rsi": pad(rec["rsi"]),
        "macdLine": pad(rec["macd"]["line"]),
        "macdHist": pad(rec["macd"]["hist"]),
        "vol": pad(rec.get("vol")),
        "obv": pad(rec.get("obv")),
    }


def main() -> int:
    passed = failed = 0

    def check(label, ok, detail=""):
        nonlocal passed, failed
        if ok:
            passed += 1
            print(f"  PASS  {label}")
        else:
            failed += 1
            print(f"  FAIL  {label}  {detail}")

    unis = [d for d in os.listdir(DATA) if os.path.isdir(os.path.join(DATA, d))]
    print("[grids]")
    grids = {}
    for u in unis:
        s = load(u, "summary.json")
        if s:
            grids[u] = s["dates"]
    ref = grids.get("semis") or next(iter(grids.values()))
    for u, d in grids.items():
        check(f"{u} shares the reference trading grid ({len(d)} days)", d == ref,
              f"{len(d)} vs {len(ref)}")

    print("\n[benchmarks]")
    bench = load(".", "benchmarks.json") or json.load(
        open(os.path.join(DATA, "benchmarks.json"), encoding="utf-8"))
    check("benchmark grid matches the universe grid", bench["dates"] == ref)
    for u, d in grids.items():
        s = load(u, "summary.json")
        for b in ("SPY", "SMH"):
            if b in (s.get("bench") or {}) and b in bench["series"]:
                same = all(
                    (x is None and y is None) or (x is not None and y is not None and abs(x - y) <= TOL)
                    for x, y in zip(s["bench"][b], bench["series"][b]))
                check(f"{u}: {b} matches the canonical benchmark series", same)

    print("\n[shared tickers]")
    n = len(ref)
    tested = 0
    for t, a, b in PAIRS:
        ra, rb = shard(a, t), shard(b, t)
        if not ra or not rb:
            print(f"  ....  {t} not in both {a} and {b}; skipped")
            continue
        tested += 1
        A, B = align(ra, n), align(rb, n)
        for field in ("px", "rsi", "macdLine", "macdHist"):
            x, y = A[field], B[field]
            bad = [(i, p, q) for i, (p, q) in enumerate(zip(x, y))
                   if not ((p is None and q is None) or
                           (p is not None and q is not None and abs(p - q) <= TOL))]
            check(f"{t}: {field} identical in {a} and {b}",
                  not bad, f"{len(bad)} mismatches, first={bad[0] if bad else None}")

    print(f"\n  ....  {tested} shared tickers compared across universes")
    print(f"\n{'='*60}\nPASSED {passed}   FAILED {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
