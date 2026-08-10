"""Data validation. Runs before any indicator is computed.

Consolidates checks that were previously inline and duplicated across the three legacy scripts.
In particular `classify_coverage` replaces THREE byte-identical copies of the same logic
(build_dashboard.py:356-365, build_renmac_dashboard.py:842-851, renmac_score.py:131-140).

Design rule: nothing here raises. A corrupt workbook must still produce a Report, because the
dashboard's own validation banner is rendered FROM that report. Blowing up in the validator
means the tab can never explain why it is empty.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

SEVERITY_ORDER = {"info": 0, "warn": 1, "fatal": 2}


@dataclass
class Finding:
    code: str
    severity: str
    message: str
    tickers: list = field(default_factory=list)
    count: int | None = None
    detail: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: dict) -> "Finding":
        return cls(
            code=d["code"], severity=d["severity"], message=d["message"],
            tickers=d.get("tickers", []) or [], count=d.get("count"),
            detail=d.get("detail", {}) or {},
        )

    def to_dict(self) -> dict:
        out = {"code": self.code, "severity": self.severity, "message": self.message}
        if self.tickers:
            out["tickers"] = self.tickers
        if self.count is not None:
            out["count"] = self.count
        if self.detail:
            out["detail"] = self.detail
        return out


@dataclass
class Report:
    universe: str
    findings: list = field(default_factory=list)

    def add(self, items):
        for it in items or []:
            self.findings.append(it if isinstance(it, Finding) else Finding.from_dict(it))
        return self

    @property
    def status(self) -> str:
        return "validation_failed" if any(f.severity == "fatal" for f in self.findings) else "ok"

    def counts(self) -> dict:
        c = {"info": 0, "warn": 0, "fatal": 0}
        for f in self.findings:
            c[f.severity] = c.get(f.severity, 0) + 1
        return c

    def to_dict(self) -> dict:
        return {
            "universe": self.universe,
            "status": self.status,
            "counts": self.counts(),
            "findings": [f.to_dict() for f in self.findings],
        }

    def print_console(self) -> None:
        c = self.counts()
        print(f"  validation [{self.universe}] status={self.status} "
              f"fatal={c['fatal']} warn={c['warn']} info={c['info']}")
        for f in sorted(self.findings, key=lambda x: -SEVERITY_ORDER[x.severity]):
            tick = f" {f.tickers[:12]}" if f.tickers else ""
            print(f"    {f.severity.upper():5} {f.code}: {f.message}{tick}")


# ---------------------------------------------------------------- individual checks


def check_date_grid(dates, expected_trading_days=None, expected_last=None) -> list:
    out = []
    if not dates:
        return [Finding("DATE_EMPTY", "fatal", "no dates parsed")]
    dup = sorted({d for d in dates if dates.count(d) > 1}) if len(dates) < 4000 else []
    if dup:
        out.append(Finding("DATE_DUPLICATE", "fatal", f"{len(dup)} duplicate dates", tickers=dup[:20]))
    if any(dates[i] >= dates[i + 1] for i in range(len(dates) - 1)):
        out.append(Finding("DATE_NONMONOTONIC", "fatal", "dates are not strictly increasing"))
    if expected_trading_days and len(dates) != expected_trading_days:
        out.append(Finding(
            "TRADING_DAY_COUNT", "warn",
            f"{len(dates)} trading days, expected {expected_trading_days}",
            count=len(dates)))
    if expected_last and dates[-1] != expected_last:
        out.append(Finding(
            "LAST_DATE_UNEXPECTED", "warn",
            f"last trading day is {dates[-1]}, expected {expected_last}"))
    return out


def scan_gaps(px: dict, tickers=None) -> list:
    """Classify every missing run as leading / interior / trailing.

    Leading is a listing date and entirely normal. Interior is a real gap and needs bounded
    ffill. Trailing means the feed stopped -- which may be a delisting OR a live name whose
    vendor feed went stale, so it is reported by name rather than silently dropped.
    """
    out = []
    lead, interior, trailing = {}, {}, {}
    for t in (tickers or px.keys()):
        col = px[t]
        n = len(col)
        i0 = 0
        while i0 < n and col[i0] is None:
            i0 += 1
        if i0 == n:
            lead[t] = n
            continue
        tr = 0
        while tr < n and col[n - 1 - tr] is None:
            tr += 1
        miss = sum(1 for v in col if v is None)
        it = miss - i0 - tr
        if i0:
            lead[t] = i0
        if it > 0:
            interior[t] = it
        if tr:
            trailing[t] = tr

    if lead:
        out.append(Finding(
            "LEADING_NA", "info",
            f"{len(lead)} ticker(s) have leading-only missing history (listing date, not a gap)",
            tickers=sorted(lead), count=len(lead),
            detail={"bars": dict(sorted(lead.items(), key=lambda kv: -kv[1])[:20])}))
    if interior:
        out.append(Finding(
            "INTERIOR_GAP", "warn",
            f"{len(interior)} ticker(s) have interior gaps; bounded forward-fill applies",
            tickers=sorted(interior), count=len(interior),
            detail={"bars": interior}))
    if trailing:
        out.append(Finding(
            "TRAILING_NA", "warn",
            f"{len(trailing)} ticker(s) stop before the last trading day -- confirm delisting "
            f"vs a stale feed before trusting or dropping them",
            tickers=sorted(trailing), count=len(trailing),
            detail={"bars": trailing}))
    return out


def scan_flatlines(px: dict, vol: dict, dates, tickers=None,
                   historical_min_run: int = 10, terminal_min_run: int = 20) -> list:
    """Position-aware flatline detection. WHERE the run sits determines what it means.

    Three distinct outcomes, because conflating them either drops good data or trusts bad:

    CONSTANT_SERIES -- one distinct value across the entire history. Never a real price. This
      is the only case safe to auto-exclude on evidence alone: Dominion Energy (`D`) ships a
      flat 15 for all 1,255 sessions in the 2026-08-09 SP500 export while the real stock trades
      near $50-60. The column holds some other metric entirely.

    TERMINAL_FLATLINE -- pinned at one value through the last bar. This is genuinely ambiguous
      from price and volume alone. In the 2026-08-09 software file all eight cases are real M&A
      take-privates pinned at their deal terms (OLO $10.25, Informatica $25.00, Couchbase
      $24.50, MeridianLink $20.00, Verint $20.50, PROS $23.25, Jamf $13.05, Confluent $30.99),
      which is correct data about a real situation. But `BNY` and `COR` in the SP500 file look
      identical on every price/volume statistic and are NOT -- they are wrong-metric columns.
      Volume ratio does not separate them (BNY and CFLT are both 1% of prior).
      So: never auto-drop these. Report every one BY NAME, and exclude them from momentum,
      breadth and z-score measures, where a pinned price otherwise fabricates 'unchanged, above
      its 20-dma, RSI 50'. Genuinely bad ones go in the universe's `excludeTickers` config with
      a written reason, which is the playbook's documented remedy.

    HISTORICAL_FLATLINE -- a run that ended in the past and the name trades normally now
      (CRH, SW, BMNR). Almost always early low-liquidity history. Informational only.
    """
    out = []
    constant, terminal, historical = {}, {}, {}

    for t in (tickers or px.keys()):
        col = px[t]
        vals = [v for v in col if v is not None]
        if len(vals) < 60:
            continue

        if len(set(vals)) == 1:
            constant[t] = vals[0]
            continue

        n = len(col)
        last = col[n - 1]
        tr = 0
        if last is not None:
            tr = 1
            for i in range(n - 2, -1, -1):
                if col[i] == last:
                    tr += 1
                else:
                    break
        if tr >= terminal_min_run:
            start = n - tr
            prior = col[start - 1] if start > 0 else None
            during = [x for x in vol.get(t, [])[start:] if x is not None]
            before = [x for x in vol.get(t, [])[max(0, start - 60):start] if x is not None]
            av = (sum(during) / len(during)) if during else 0.0
            bv = (sum(before) / len(before)) if before else 0.0
            terminal[t] = {
                "sessions": tr, "pinnedAt": last, "since": dates[start] if start < len(dates) else None,
                "priorClose": prior,
                "volVsPrior": round(av / bv, 4) if bv else None,
            }
            continue

        run = best = 1
        for i in range(1, len(vals)):
            run = run + 1 if vals[i] == vals[i - 1] else 1
            best = max(best, run)
        if best >= historical_min_run:
            historical[t] = best

    if constant:
        out.append(Finding(
            "CONSTANT_SERIES", "fatal",
            f"{len(constant)} ticker(s) hold a single value across the entire history -- this is "
            f"not a price series. Add to the universe's excludeTickers with a reason, or fix the "
            f"source column.",
            tickers=sorted(constant), count=len(constant), detail={"value": constant}))
    if terminal:
        out.append(Finding(
            "TERMINAL_FLATLINE", "warn",
            f"{len(terminal)} ticker(s) are pinned at one price through the last session. Real "
            f"M&A deal-price pinning and a broken feed are indistinguishable here -- each is "
            f"named below. They are excluded from momentum, breadth and z-score measures because "
            f"a pinned price otherwise reads as 'unchanged and above its moving average'.",
            tickers=sorted(terminal), count=len(terminal), detail=terminal))
    if historical:
        out.append(Finding(
            "HISTORICAL_FLATLINE", "info",
            f"{len(historical)} ticker(s) had a flat run in the past but trade normally now "
            f"(typically early low-liquidity history)",
            tickers=sorted(historical), count=len(historical), detail={"longestRun": historical}))
    return out


def check_extreme_returns(px: dict, tickers=None, threshold: float = 10.0) -> list:
    """Flag >threshold-x moves for eyeball review (not an error on its own).

    A genuine 10x over five years exists (NVDA). A 10x that appears alongside a flatline run is
    the WAL pattern. The two findings are meant to be read together.
    """
    out, big = [], {}
    for t in (tickers or px.keys()):
        col = [v for v in px[t] if v is not None]
        if len(col) < 60 or col[0] in (None, 0):
            continue
        mult = col[-1] / col[0]
        if mult >= threshold:
            big[t] = round(mult, 1)
    if big:
        out.append(Finding(
            "EXTREME_RETURN", "info",
            f"{len(big)} ticker(s) up {threshold}x or more over their history -- confirm real "
            f"before they drive the composite or the bubble-signal roster",
            tickers=sorted(big, key=lambda k: -big[k]), count=len(big), detail={"multiple": big}))
    return out


def _fingerprint(col) -> str:
    vals = [v for v in col if v is not None]
    return hashlib.sha1(repr(vals).encode()).hexdigest() if vals else ""


def cross_workbook_identity(book_a, book_b, name_a: str, name_b: str, min_frac: float = 0.5) -> list:
    """Detect a workbook that is another workbook's data under different headers.

    This caught the first hardware/networking export: 34 of 36 columns byte-identical to the
    semiconductor workbook, because unresolved CapIQ formulas meant the file saved the previous
    query's cached values under new ticker names. AAPL appeared at $110.11 -- AMD's price.

    Matching is by value fingerprint, so it catches the column-shifted variant too (the playbook
    documents a 'corrected' file where the same corrupt blocks simply moved one column over).
    Benchmarks are excluded: SPY and SMH legitimately appear in more than one workbook.
    """
    bench = {"SPY", "SMH"}
    fp_b = {}
    for t in book_b.tickers:
        if t in bench:
            continue
        f = _fingerprint(book_b.px[t])
        if f:
            fp_b.setdefault(f, t)

    pairs, checked = [], 0
    for t in book_a.tickers:
        if t in bench:
            continue
        checked += 1
        f = _fingerprint(book_a.px[t])
        if f and f in fp_b and fp_b[f] != t:
            pairs.append((t, fp_b[f]))

    if not pairs or not checked:
        return []
    frac = len(pairs) / checked
    sev = "fatal" if frac >= min_frac else "warn"
    return [Finding(
        "DUPLICATED_SOURCE", sev,
        f"{len(pairs)} of {checked} columns in {name_a} carry values identical to a DIFFERENTLY "
        f"NAMED column in {name_b} ({frac:.0%}). The export almost certainly saved another "
        f"query's cached values under these headers.",
        count=len(pairs),
        detail={"pairs": dict(pairs[:25]), "fraction": round(frac, 4)})]


def check_mapping_coverage(tickers, mapping: dict, level_fields=("sector", "industryGroup")) -> list:
    out = []
    unmapped = [t for t in tickers if t not in mapping]
    if unmapped:
        out.append(Finding(
            "UNMAPPED_TICKER", "warn",
            f"{len(unmapped)} priced ticker(s) have no sector mapping and are excluded from "
            f"rollups -- reported, never silently dropped",
            tickers=sorted(unmapped), count=len(unmapped)))
    for f in level_fields:
        blank = [t for t in tickers if t in mapping and not mapping[t].get(f)]
        if blank:
            out.append(Finding(
                f"MAPPING_BLANK_{f.upper()}", "warn",
                f"{len(blank)} ticker(s) map to a blank {f}",
                tickers=sorted(blank), count=len(blank)))
    return out


def check_benchmark_alignment(book_dates, bench_dates, bench_name: str) -> list:
    if book_dates == bench_dates:
        return []
    missing = [d for d in book_dates if d not in set(bench_dates)]
    return [Finding(
        "BENCH_DATE_MISMATCH", "fatal" if missing else "warn",
        f"benchmark {bench_name} does not share the universe trading grid "
        f"({len(missing)} universe dates absent from the benchmark series)",
        count=len(missing), detail={"firstMissing": missing[0] if missing else None})]


def check_basket_membership(baskets: dict, universe_tickers) -> list:
    """Report basket members absent from this workbook, and priced names in no basket."""
    out = []
    U = set(universe_tickers)
    seen = {}
    dupes = []
    for name, members in (baskets or {}).items():
        for t in members:
            if t in seen:
                dupes.append((t, seen[t], name))
            seen[t] = name
    absent = sorted(set(seen) - U)
    unassigned = sorted(U - set(seen))
    if dupes:
        out.append(Finding(
            "BASKET_DUPLICATE_MEMBER", "fatal",
            f"{len(dupes)} ticker(s) appear in more than one sub-basket, which double-counts "
            f"them in every basket-relative calculation",
            count=len(dupes), detail={"pairs": [list(d) for d in dupes[:20]]}))
    if absent:
        out.append(Finding(
            "BASKET_MEMBER_ABSENT", "info",
            f"{len(absent)} configured basket member(s) are not in this workbook vintage",
            tickers=absent, count=len(absent)))
    if unassigned:
        out.append(Finding(
            "BASKET_UNASSIGNED", "warn",
            f"{len(unassigned)} priced ticker(s) belong to no sub-basket and are therefore "
            f"invisible to the cycle-position pillar",
            tickers=unassigned, count=len(unassigned)))
    return out


# ---------------------------------------------------------------- coverage classification


def classify_coverage(col, full: float = 0.95, partial: float = 0.10):
    """THE single copy. Returns (class, coverage_fraction, first_real_index).

    `full`    -- has a value on the first bar and >= `full` coverage; eligible for bounded ffill
    `partial` -- >= `partial` coverage; kept, but never forward-filled and excluded from
                 measures where a mid-window entrant would read as activity rather than
                 composition change (OBV, total volume)
    `drop`    -- below `partial`; excluded from the universe with a logged reason
    """
    n = len(col)
    if n == 0:
        return "drop", 0.0, None
    valid = sum(1 for v in col if v is not None)
    cov = valid / n
    i0 = next((i for i, v in enumerate(col) if v is not None), None)
    if i0 == 0 and cov >= full:
        return "full", cov, i0
    if cov >= partial:
        return "partial", cov, i0
    return "drop", cov, i0


def build_universe(book, params, exclude=(), exclude_tickers=(), pinned=()) -> tuple[dict, dict, list]:
    """Split a PriceBook into the scored universe plus a coverage map.

    Returns (universe_px, coverage, findings).

    `exclude`          -- benchmark columns. SMH/SPY ride along in the same sheets but are NOT
                          universe members and must stay out of the composite, breadth, and
                          every universe-wide measure.
    `exclude_tickers`  -- [{ticker, reason}] from config. The playbook's documented remedy for a
                          positively-identified bad column: drop it at load time WITH a written
                          reason, never silently.
    `pinned`           -- tickers flagged TERMINAL_FLATLINE. Kept in the universe and rendered,
                          but marked so momentum/breadth/z-score measures can skip them.
    """
    cov_cfg = params["coverage"]
    exclude = set(exclude)
    pinned = set(pinned)
    reasons = {e["ticker"]: e.get("reason", "") for e in (exclude_tickers or [])}
    universe, coverage = {}, {}
    dropped, partial, excluded = [], [], []

    for t in book.tickers:
        if t in exclude:
            continue
        if t in reasons:
            excluded.append(t)
            coverage[t] = {"cls": "excluded", "cov": None, "i0": None, "reason": reasons[t]}
            continue
        cls, cov, i0 = classify_coverage(book.px[t], cov_cfg["full"], cov_cfg["partial"])
        rec = {"cls": cls, "cov": round(cov, 4), "i0": i0}
        if t in pinned:
            rec["pinned"] = True
        coverage[t] = rec
        if cls == "drop":
            dropped.append(t)
            continue
        if cls == "partial":
            partial.append(t)
        universe[t] = book.px[t]

    findings = []
    if excluded:
        findings.append(Finding(
            "EXCLUDED_BY_CONFIG", "warn",
            f"{len(excluded)} ticker(s) excluded at load time by configuration, each with a "
            f"documented reason",
            tickers=sorted(excluded), count=len(excluded),
            detail={t: reasons[t] for t in sorted(excluded)}))
    if dropped:
        findings.append(Finding(
            "COVERAGE_DROPPED", "info",
            f"{len(dropped)} ticker(s) below {cov_cfg['partial']:.0%} coverage, excluded from "
            f"the universe",
            tickers=sorted(dropped), count=len(dropped)))
    if partial:
        findings.append(Finding(
            "COVERAGE_PARTIAL", "info",
            f"{len(partial)} ticker(s) have partial history; kept, never forward-filled, and "
            f"excluded from OBV and total-volume aggregates",
            tickers=sorted(partial), count=len(partial)))
    return universe, coverage, findings
