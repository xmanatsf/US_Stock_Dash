# -*- coding: utf-8 -*-
"""Build the RenMac regime dashboard from the 5-year price + volume workbook.

Implements RENMAC_TIMING_FRAMEWORK.md against
"US semi stocks 5y price and volume 20260807.xlsx" (sheets: Price, Volume) and
renders US_Semi_RenMac_Regime_Dashboard.html.

What five years of history unlocks over the one-year file:
  - bubble signal (RenMac's actual rule: a double within TWO years)
  - true 52-week highs and lows, not expanding-window period-low proxies
  - 200-dma breadth with a readable trend, not just a valid level
  - rolling 3-year Sharpe percentile - the "not exhaustive" test
  - causal (expanding-window) percentiles instead of in-sample ones
  - volume: up/down volume ratio, distribution/accumulation day counts, and
    on-balance volume
  - MACD/RSI momentum on the composite
  - a rolling regime history, so the framework can be checked against the
    2022 bottom and 2023 recovery rather than only the current tape
  - SMH/SPY benchmark columns: absolute and relative-strength comparison of
    the semi composite against the sector ETF and the broad market

Source-file quirks handled here (see the console QC block):
  - rows are CALENDAR days: weekends and market holidays carry the prior
    close AND the prior volume forward. Left in, a "20-day" average spans
    ~14 trading days and weekend volume is counted three times. Filtered out.
  - CapIQ 'NA' string placeholders sit in otherwise-numeric columns.
  - sheets are read by name, never by position.

Rerun after refreshing the workbook:  python build_renmac_dashboard.py
"""
import json
import os
import sys

import openpyxl

from build_dashboard import (
    sma, roc, daily_ret, ffill_small_gaps, r1, r2,
    macd, rsi, obv, rel_vol, BENCHMARKS,
)
from renmac_score import SUBBASKETS, CYCLE_BASKETS, WEIGHTS, PILLAR_NAMES, REGIME_PLAYBOOK

HERE = os.path.dirname(os.path.abspath(__file__))
XLSX = os.path.join(HERE, "US semi stocks 5y price and volume 20260807.xlsx")
TEMPLATE = os.path.join(HERE, "dashboard_template_renmac.html")
OUT = os.path.join(HERE, "US_Semi_RenMac_Regime_Dashboard.html")

BELLWETHERS = {"NVDA", "AVGO", "AMD", "MU", "AMAT", "LRCX", "KLAC", "TXN", "MRVL", "INTC"}
WARMUP = 252          # one year before any regime is emitted
YR = 252              # trading days per year


# --------------------------------------------------------------- data loading

def num(v):
    """CapIQ writes 'NA'/'NM' as literal strings into numeric columns."""
    return v if isinstance(v, (int, float)) else None


def load():
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    for want in ("Price", "Volume"):
        if want not in wb.sheetnames:
            sys.exit("sheet %r not found; workbook has %s" % (want, wb.sheetnames))

    def grab(name):
        rows = [r for r in wb[name].iter_rows(values_only=True)]
        # A blank spacer column (no ticker in the header) can sit between two
        # real columns as a paste/add-in artifact - drop it before anything
        # downstream assumes Price and Volume share the same column layout.
        keep_cols = [j for j, x in enumerate(rows[0][1:], 1) if x is not None]
        hdr = [str(rows[0][j]) for j in keep_cols]
        data_rows = [r for r in rows[1:] if r[0] is not None]
        trimmed = [(r[0],) + tuple(r[j] for j in keep_cols) for r in data_rows]
        return hdr, trimmed

    phdr, prows = grab("Price")
    vhdr, vrows = grab("Volume")
    if phdr != vhdr:
        sys.exit("Price and Volume ticker columns differ")
    # Join on date rather than row position - the two sheets happen to share a
    # date index here, but a vendor-side range mismatch would otherwise shift
    # every volume reading silently against the wrong close.
    vby = {r[0]: r for r in vrows}
    missing = [r[0] for r in prows if r[0] not in vby]
    prows = [r for r in prows if r[0] in vby]
    vrows = [vby[r[0]] for r in prows]

    # Drop non-trading rows: weekends, plus any weekday where essentially the
    # whole universe repeats the prior row's price AND volume (a market holiday
    # forward-filled by the vendor).
    keep, holidays = [], []
    for i in range(len(prows)):
        if prows[i][0].weekday() >= 5:
            continue
        if i > 0:
            same = tot = 0
            for j in range(1, len(phdr) + 1):
                a, b = num(prows[i][j]), num(prows[i - 1][j])
                c, d = num(vrows[i][j]), num(vrows[i - 1][j])
                if a is None or b is None:
                    continue
                tot += 1
                same += (a == b and c == d)
            if tot and same / tot > 0.95:
                holidays.append(prows[i][0])
                continue
        keep.append(i)

    dates = [prows[i][0].strftime("%Y-%m-%d") for i in keep]
    n = len(dates)
    px, vol, empty, bench = {}, {}, [], {}
    for j, t in enumerate(phdr, 1):
        p = [num(prows[i][j]) for i in keep]
        if not any(v is not None for v in p):
            empty.append(t)
        elif t in BENCHMARKS:
            # SMH/SPY ride along in the same sheets as benchmark columns, not
            # semiconductor-universe members - excluded from the composite,
            # breadth, and every universe-wide measure below.
            bench[t] = ffill_small_gaps(p)
        else:
            px[t] = p
            # Volume is never forward-filled: a filled volume print fabricates
            # activity that did not happen. Missing stays missing.
            vol[t] = [num(vrows[i][j]) for i in keep]
    return dates, n, px, vol, bench, empty, len(prows), len(holidays), missing


# ------------------------------------------------------------------- helpers

def ew(cols, n):
    """Daily-rebalanced equal-weight index, base 100.

    Chains the cross-sectional mean of daily returns rather than averaging
    prices normalised to a base date. Over a one-year window the two are
    close; over five years, normalising to a fixed base lets a stock that
    has risen 20x dominate an index that is still labelled "equal-weight" -
    reintroducing precisely the concentration distortion this framework
    exists to detect. It also keeps late-listing tickers from jolting the
    index on the day they enter.
    """
    out = [None] * n
    lvl = 100.0
    started = False
    for i in range(n):
        rets = []
        for c in cols:
            if i > 0 and c[i] is not None and c[i - 1] not in (None, 0):
                rets.append(c[i] / c[i - 1] - 1)
        if not started:
            if any(c[i] is not None for c in cols):
                started = True
                out[i] = lvl
            continue
        if rets:
            lvl *= 1 + sum(rets) / len(rets)
        out[i] = lvl
    return out


def expanding_pct(series, warm=252):
    """Causal percentile: rank of series[i] within series[0..i]. Unlike a
    whole-window rank this never uses future data, so the regime history is
    honest about what was knowable at the time."""
    out = [None] * len(series)
    seen = []
    for i, v in enumerate(series):
        if v is not None:
            seen.append(v)
        if v is not None and len(seen) >= warm:
            out[i] = 100.0 * sum(x <= v for x in seen) / len(seen)
    return out


def rolling_sharpe(comp, win=3 * YR):
    """Annualised rolling Sharpe of the composite - RenMac's extension test."""
    rets = daily_ret(comp)
    out = [None] * len(comp)
    for i in range(win, len(comp)):
        w = [v for v in rets[i - win + 1 : i + 1] if v is not None]
        if len(w) < win * 0.9:
            continue
        m = sum(w) / len(w)
        sd = (sum((x - m) ** 2 for x in w) / (len(w) - 1)) ** 0.5
        if sd > 0:
            out[i] = m / sd * (YR ** 0.5)
    return out


def slope(series, i, back):
    j = i - back
    if j < 0 or series[i] is None or series[j] is None:
        return None
    return series[i] - series[j]


def stochastic(col, k=14):
    out = [None] * len(col)
    for i in range(k - 1, len(col)):
        w = [v for v in col[i - k + 1 : i + 1] if v is not None]
        if len(w) < k or col[i] is None:
            continue
        lo, hi = min(w), max(w)
        out[i] = 50.0 if hi == lo else 100.0 * (col[i] - lo) / (hi - lo)
    return out


def rolling_z(series, win):
    out = [None] * len(series)
    for i in range(len(series)):
        if series[i] is None:
            continue
        w = [v for v in series[max(0, i - win + 1) : i + 1] if v is not None]
        if len(w) < win:
            continue
        m = sum(w) / len(w)
        sd = (sum((x - m) ** 2 for x in w) / (len(w) - 1)) ** 0.5
        if sd > 0:
            out[i] = (series[i] - m) / sd
    return out


# ------------------------------------------------------------------ measures

def build_measures(dates, n, universe, vol, full, comp):
    M = {}
    M["comp"] = comp
    M["comp20"], M["comp50"] = sma(comp, 20), sma(comp, 50)
    M["comp200"] = sma(comp, 200)
    M["roc65"] = roc(comp, 65)

    mas20 = {t: sma(universe[t], 20) for t in universe}
    mas50 = {t: sma(universe[t], 50) for t in universe}
    mas65 = {t: sma(universe[t], 65) for t in universe}
    mas200 = {t: sma(universe[t], 200) for t in universe}

    def breadth(mas):
        out = [None] * n
        for i in range(n):
            c = tot = 0
            for t in universe:
                p, m = universe[t][i], mas[t][i]
                if p is None or m is None:
                    continue
                tot += 1
                c += p > m
            if tot >= 25:
                out[i] = 100.0 * c / tot
        return out

    M["b20"], M["b50"], M["b200"] = breadth(mas20), breadth(mas50), breadth(mas200)

    x2065 = [None] * n
    for i in range(n):
        c = tot = 0
        for t in universe:
            a, b = mas20[t][i], mas65[t][i]
            if a is None or b is None:
                continue
            tot += 1
            c += a > b
        if tot >= 25:
            x2065[i] = 100.0 * c / tot
    M["x2065"] = x2065

    # True 52-week highs and lows - now measurable, not a period-low proxy.
    hi52, lo52, hml52 = [None] * n, [None] * n, [None] * n
    lows63 = [None] * n
    for i in range(YR, n):
        h = l = tot = 0
        l63 = 0
        for t in universe:
            col = universe[t]
            if col[i] is None:
                continue
            w = [v for v in col[i - YR + 1 : i + 1] if v is not None]
            if len(w) < YR * 0.8:
                continue
            tot += 1
            h += col[i] >= max(w)
            l += col[i] <= min(w)
            w63 = [v for v in col[max(0, i - 62) : i + 1] if v is not None]
            l63 += col[i] <= min(w63)
        if tot >= 25:
            hi52[i], lo52[i] = h, l
            hml52[i] = 100.0 * (h - l) / tot
        lows63[i] = l63
    M["hi52"], M["lo52"], M["hml52"], M["lows63"] = hi52, lo52, hml52, lows63

    # 65-day highs minus lows
    hml65 = [None] * n
    for i in range(65, n):
        h = l = tot = 0
        for t in universe:
            col = universe[t]
            if col[i] is None:
                continue
            w = [v for v in col[i - 64 : i + 1] if v is not None]
            if len(w) < 50:
                continue
            tot += 1
            h += col[i] >= max(w)
            l += col[i] <= min(w)
        if tot >= 25:
            hml65[i] = 100.0 * (h - l) / tot
    M["hml65"] = hml65

    stos = {t: stochastic(universe[t]) for t in universe}
    obos = [None] * n
    for i in range(n):
        ob = os_ = tot = 0
        for t in universe:
            v = stos[t][i]
            if v is None:
                continue
            tot += 1
            ob += v >= 80
            os_ += v <= 20
        if tot >= 25:
            obos[i] = 100.0 * (ob - os_) / tot
    M["obos"] = obos

    # momentum-quintile spread (crowding)
    rocs = {t: roc(universe[t], 65) for t in universe}
    spread = [None] * n
    for i in range(65, n):
        xs = sorted(v for v in (rocs[t][i] for t in universe) if v is not None)
        if len(xs) < 25:
            continue
        q = len(xs) // 5
        spread[i] = sum(xs[-q:]) / q - sum(xs[:q]) / q
    M["spread"] = spread
    M["spreadPct"] = expanding_pct(spread)
    M["rocs"] = rocs

    # high-beta vs low-beta (positioning / extension)
    cret = daily_ret(comp)
    betas = {}
    for t, col in universe.items():
        r = daily_ret(col)
        pr = [(a, b) for a, b in zip(r, cret) if a is not None and b is not None]
        if len(pr) < 250:
            continue
        mb = sum(b for _, b in pr) / len(pr)
        var = sum((b - mb) ** 2 for _, b in pr)
        if var <= 0:
            continue
        ma = sum(a for a, _ in pr) / len(pr)
        betas[t] = sum((a - ma) * (b - mb) for a, b in pr) / var
    ranked = sorted(betas, key=lambda t: betas[t])
    q = max(3, len(ranked) // 5)
    hb = ew([universe[t] for t in ranked[-q:]], n)
    lb = ew([universe[t] for t in ranked[:q]], n)
    bs = [None if (h is None or l is None or not l) else h / l * 100 for h, l in zip(hb, lb)]
    M["betaSpread"] = bs
    M["betaPct"] = expanding_pct(bs)
    M["hiBetaNames"] = sorted(ranked[-q:])
    M["loBetaNames"] = sorted(ranked[:q])

    # rolling 3-yr Sharpe - unlocked by the 5-yr file
    M["sharpe"] = rolling_sharpe(comp)
    M["sharpePct"] = expanding_pct(M["sharpe"], warm=126)

    # bubble signal: RenMac's actual rule, a double within two years
    dbl = [None] * n
    for i in range(2 * YR, n):
        c = tot = 0
        for t in full:
            col = full[t]
            if col[i] is None or col[i - 2 * YR] in (None, 0):
                continue
            tot += 1
            c += col[i] / col[i - 2 * YR] >= 2
        if tot >= 25:
            dbl[i] = 100.0 * c / tot
    M["doubled2y"] = dbl

    # vol alerts (RenMac-native sentiment proxy)
    zs = {t: rolling_z(daily_ret(universe[t]), 65) for t in universe}
    vap, van = [None] * n, [None] * n
    for i in range(65, n):
        p = ng = tot = 0
        for t in universe:
            w = [v for v in zs[t][max(0, i - 4) : i + 1] if v is not None]
            if not w:
                continue
            tot += 1
            p += any(v >= 2.5 for v in w)
            ng += any(v <= -2.5 for v in w)
        if tot >= 25:
            vap[i], van[i] = 100.0 * p / tot, 100.0 * ng / tot
    M["volAlertPos"], M["volAlertNeg"] = vap, van

    # leadership concentration
    bell = [t for t in BELLWETHERS if t in full]
    bc = ew([full[t] for t in bell], n)
    M["bellRel"] = [None if (b is None or c is None or not c) else b / c * 100
                    for b, c in zip(bc, comp)]
    M["bellNames"] = sorted(bell)

    # ---- volume: the measures the price-only file could not support ----
    # Universe-wide up/down volume ratio over 20 sessions, and distribution /
    # accumulation day counts on the composite over 25 sessions.
    upv, dnv = [0.0] * n, [0.0] * n
    for t in universe:
        p, v = universe[t], vol.get(t)
        if not v:
            continue
        for i in range(1, n):
            if p[i] is None or p[i - 1] is None or v[i] is None:
                continue
            if p[i] > p[i - 1]:
                upv[i] += v[i]
            elif p[i] < p[i - 1]:
                dnv[i] += v[i]
    udr = [None] * n
    for i in range(20, n):
        u = sum(upv[i - 19 : i + 1])
        d = sum(dnv[i - 19 : i + 1])
        if d > 0:
            udr[i] = u / d
    M["upDownVol"] = udr

    tot_vol = [None] * n
    for i in range(n):
        s = [vol[t][i] for t in universe if vol.get(t) and vol[t][i] is not None]
        tot_vol[i] = sum(s) if s else None
    M["totVol"] = tot_vol
    M["totVol50"] = sma(tot_vol, 50)

    dist, accum = [None] * n, [None] * n
    for i in range(25, n):
        d = a = 0
        for k in range(i - 24, i + 1):
            if (comp[k] is None or comp[k - 1] is None or tot_vol[k] is None
                    or tot_vol[k - 1] is None):
                continue
            chg = comp[k] / comp[k - 1] - 1
            if chg <= -0.005 and tot_vol[k] > tot_vol[k - 1]:
                d += 1
            elif chg >= 0.005 and tot_vol[k] > tot_vol[k - 1]:
                a += 1
        dist[i], accum[i] = d, a
    M["distDays"], M["accumDays"] = dist, accum

    # OBV restricted to full-history tickers only (unlike totVol above, which
    # spans the whole universe): a partial ticker entering mid-window would
    # otherwise show up as a volume/OBV step change that is composition, not
    # a change in trading activity.
    tot_vol_full = [None] * n
    for i in range(n):
        s = [vol[t][i] for t in full if vol.get(t) and vol[t][i] is not None]
        tot_vol_full[i] = sum(s) if s else None
    M["obv"] = obv(comp, tot_vol_full)

    # ---- composite momentum indicators ----
    ml, sl, hi = macd(comp)
    M["macdLine"], M["macdSignal"], M["macdHist"] = ml, sl, hi
    M["rsi"] = rsi(comp)

    # ---- sub-basket cycle relatives ----
    baskets = {}
    for name, tick in SUBBASKETS.items():
        cols = [universe[t] for t in tick if t in universe]
        if len(cols) < 2:
            continue
        c = ew(cols, n)
        baskets[name] = {"comp": c, "roc": roc(c, 65), "n": len(cols),
                         "members": sorted(t for t in tick if t in universe)}
    M["baskets"] = baskets
    return M


# ------------------------------------------------------- causal structure

STRUCT_WIN = 252      # the sequence is read off the trailing year only


def structure_series(comp, comp50, n, win=STRUCT_WIN):
    """Causal peak/crack/retest and trough/thrust/breakout state at every index,
    read off a trailing `win`-session window and using only data up to i.

    The window matters. Searching from an all-time anchor makes every event
    flag permanent: a thrust and a 50-dma breakout that happened in Nov-2022
    stay 'true' for the next four years, so the bottoming gate matches forever
    and the classifier reports early-recovery in the middle of a crash. RenMac's
    sequence describes the structure that is *currently* on the tape, so the
    search window has to move with it.
    """
    out = []
    for i in range(n):
        lo = max(0, i - win + 1)
        rng = range(lo, i + 1)
        peak_i = max(rng, key=lambda k: comp[k])
        trough_i = min(rng, key=lambda k: comp[k])
        s = {"peak_i": peak_i, "trough_i": trough_i,
             "anchor": "peak" if peak_i > trough_i else "trough"}

        crack = next((j for j in range(peak_i + 1, i + 1)
                      if comp[j] / comp[max(peak_i, j - 5)] - 1 <= -0.08), None)
        s["crack_i"] = crack
        retest = None
        if crack is not None and crack < i:
            cand = max(range(crack, i + 1), key=lambda k: comp[k])
            clo = min(range(peak_i, cand + 1), key=lambda k: comp[k])
            if comp[cand] > comp[clo] * 1.05 and cand > crack and comp[cand] < comp[peak_i]:
                retest = cand
        s["retest_i"] = retest
        s["ma_break_i"] = next((j for j in range(peak_i, i + 1)
                                if comp50[j] is not None and comp[j] < comp50[j]), None)

        thrust = next((j for j in range(trough_i + 1, i + 1)
                       if comp[j] / comp[max(trough_i, j - 5)] - 1 >= 0.08), None)
        s["thrust_i"] = thrust
        s["retest_hold"] = None
        if thrust is not None and thrust < i:
            post = min(range(thrust, i + 1), key=lambda k: comp[k])
            s["retest_hold"] = comp[post] > comp[trough_i]
        s["breakout_i"] = None
        if thrust is not None:
            s["breakout_i"] = next(
                (j for j in range(thrust, i + 1)
                 if comp50[j] is not None and comp[j] > comp50[j]
                 and (slope(comp50, j, 10) or 0) > 0), None)
        wc = 0.0
        for j in range(max(peak_i + 5, 5), i + 1):
            wc = min(wc, comp[j] / comp[j - 5] - 1)
        s["worst5"] = wc
        # Needs real distance from the peak: with peak_i == i the window is a
        # single element and the test is trivially true, which scored the
        # structure pillar negative on the exact day the composite peaked.
        s["at_low_since_peak"] = (i - peak_i >= 5
                                  and comp[i] <= min(comp[peak_i : i + 1]) * 1.001)
        s["off_peak"] = comp[i] / comp[peak_i] - 1
        s["off_trough"] = comp[i] / comp[trough_i] - 1
        out.append(s)
    return out


# --------------------------------------------------------------- scoring

def score_at(i, M, S):
    """Apply the framework thresholds at index i. Returns {pillar: (score, [evidence])}
    with None for pillars whose inputs are not yet available."""
    p = {}
    g = lambda k: M[k][i] if M[k][i] is not None else None

    # A - positioning & extension
    ev, sc = [], None
    bp, bsl = g("betaPct"), slope(M["betaSpread"], i, 21)
    shp = g("sharpePct")
    if bp is not None and bsl is not None:
        if bp >= 90:
            sc = -2 if bsl < 0 else -1
        elif bp >= 70:
            sc = -1 if bsl < 0 else 0
        elif bp <= 20:
            sc = 2 if bsl > 0 else -1
        else:
            sc = 1 if bsl > 0 else 0
        ev.append("high/low-beta spread at percentile %.0f, %s"
                  % (bp, "rising" if bsl > 0 else "falling"))
        # Peaks and contractions, never levels (framework principle 1). An
        # extension gauge parked at the 95th percentile is a condition, not a
        # signal - RenMac's own example is beta sitting above the 90th
        # percentile for all of 2021 without mean-reverting. Penalise only
        # once the gauge rolls over; reward only once a washed-out one turns up.
        if shp is not None:
            ssl = slope(M["sharpePct"], i, 21) or 0
            ev.append("rolling 3-yr Sharpe at percentile %.0f (%.2f), %s"
                      % (shp, M["sharpe"][i], "rolling over" if ssl < 0 else "still rising"))
            if shp >= 90 and ssl < 0:
                sc -= 1
            elif shp <= 15 and ssl > 0:
                sc += 1
        db = g("doubled2y")
        if db is not None:
            dsl = slope(M["doubled2y"], i, 21) or 0
            ev.append("%.0f%% of the universe has doubled within 2 years (RenMac bubble signal), %s"
                      % (db, "cohort shrinking" if dsl < 0 else "cohort still growing"))
            if db >= 25 and dsl < 0:
                sc -= 1
        sc = max(-2, min(2, sc))
    p["A"] = (sc, ev)

    # B - breadth, trend, relative strength (+ volume)
    ev, sc = [], None
    b20, b50, b200 = g("b20"), g("b50"), g("b200")
    if b20 is not None and b50 is not None:
        d20 = slope(M["b20"], i, 21) or 0
        sc = -2 if b20 < 15 else -1 if b20 < 35 else 0 if b20 < 55 else 1 if b20 < 80 else 2
        if b50 < 25:
            sc = min(sc, -1)
        if M["x2065"][i] is not None and M["x2065"][i] > 65 and b50 > 55:
            sc = max(sc, 1)
        h65 = g("hml65")
        if h65 is not None:
            sc += 1 if h65 > 10 else (-1 if h65 < -10 else 0)
        sc += 1 if d20 > 20 else (-1 if d20 < -20 else 0)
        udr = g("upDownVol")
        if udr is not None:
            sc += 1 if udr > 1.4 else (-1 if udr < 0.75 else 0)
            ev.append("up/down volume ratio %.2f over 20 sessions" % udr)
        dd, ad = g("distDays"), g("accumDays")
        if dd is not None:
            ev.append("%d distribution vs %d accumulation days in 25 sessions" % (dd, ad))
            if dd >= 6 and dd > ad:
                sc -= 1
        ev.insert(0, "breadth %.0f%% >20-dma (%+.0f pts/21d), %.0f%% >50-dma, %s"
                  % (b20, d20, b50,
                     "%.0f%% >200-dma" % b200 if b200 is not None else "200-dma n/a"))
        if g("hml52") is not None:
            ev.append("52-week highs minus lows %+.1f%% of issues" % g("hml52"))
        sc = max(-2, min(2, sc))
    p["B"] = (sc, ev)

    # C - sentiment & crowding
    ev, sc = [], None
    vp, vn = g("volAlertPos"), g("volAlertNeg")
    if vp is not None:
        sc = 0
        ev.append("vol alerts: %.0f%% positive, %.0f%% negative (5 sessions)" % (vp, vn))
        if vp >= 20 and vn < 10:
            sc += 1
            ev.append("a buyer's panic - escape velocity, not a top")
        if vn >= 20:
            ev.append("a seller's panic - raw material for a base, not bullish on its own")
        bsl = slope(M["bellRel"], i, 65)
        if bsl is not None:
            sc += -1 if bsl > 2 else (1 if bsl < -2 else 0)
            ev.append("bellwethers vs equal-weight %+.1f pts/65d (%s)"
                      % (bsl, "narrowing" if bsl > 0 else "broadening"))
        spp, sps = g("spreadPct"), slope(M["spread"], i, 21)
        if spp is not None:
            ev.append("momentum-quintile spread at percentile %.0f, %s"
                      % (spp, "widening" if (sps or 0) > 0 else "compressing"))
            if spp >= 85 and (sps or 0) < 0:
                sc -= 1
        sc = max(-2, min(2, sc))
    p["C"] = (sc, ev)

    # E - cycle position
    ev, sc = [], None
    core = {k: v for k, v in M["baskets"].items()
            if k in CYCLE_BASKETS and v["n"] >= 3 and v["roc"][i] is not None}
    if core:
        cr = M["roc65"][i] or 0
        rel = {k: v["roc"][i] - cr for k, v in core.items()}
        npos = sum(v["roc"][i] > 0 for v in core.values())
        lead = max(rel, key=rel.get)
        wfe = rel.get("WFE/equipment")
        tape_down = (M["comp50"][i] is not None and M["comp"][i] < M["comp50"][i]
                     and (slope(M["comp50"], i, 21) or 0) < 0)
        for k in sorted(rel, key=rel.get, reverse=True):
            ev.append("%-14s %+6.1f%% 65d (%+.1f vs composite)" % (k, core[k]["roc"][i], rel[k]))
        if tape_down:
            if wfe is not None and wfe > 5:
                sc = 1
                ev.append("equipment leading into a weak tape - equipment turns first at cycle bottoms")
            elif wfe is not None and wfe < -2:
                sc = -2
                ev.append("equipment lagging into a weak tape - the cycle is rolling, not turning")
            else:
                sc = -1
                ev.append("no cycle turn signal from equipment yet")
        elif npos == len(core) and lead in ("WFE/equipment", "Analog/MCU"):
            sc = 2
            ev.append("broad and led by the cycle-sensitive end - durable advance")
        elif npos >= len(core) - 1:
            sc = 1 if lead != "AI/compute" else 0
            ev.append("advance is broad" if sc == 1 else "broad but AI/compute is leading - watch for narrowing")
        elif npos <= 1:
            sc = -2
            ev.append("cycle narrowed to one basket or none")
        else:
            sc = -1
            ev.append("cycle splitting - part of the complex has rolled")
    p["E"] = (sc, ev)

    # F - structure
    s = S[i]
    ev, sc = [], 0
    if s["anchor"] == "peak":
        bits = []
        if s["crack_i"] is not None:
            bits.append("first crack"); sc -= 1
        if s["retest_i"] is not None:
            bits.append("failed retest"); sc -= 1
        if s["ma_break_i"] is not None:
            bits.append("50-dma break")
        if s["at_low_since_peak"]:
            bits.append("at the post-peak low"); sc -= 1
        ev.append("peak anchor: " + (" -> ".join(bits) if bits else "no break yet"))
    else:
        bits = []
        if s["thrust_i"] is not None:
            bits.append("thrust"); sc += 1
        if s["retest_hold"]:
            bits.append("retest held"); sc += 1
        elif s["retest_hold"] is False:
            bits.append("retest undercut"); sc -= 1
        if s["breakout_i"] is not None:
            bits.append("breakout over a rising 50-dma"); sc += 1
        ev.append("trough anchor: " + (" -> ".join(bits) if bits else "no thrust yet"))
    p["F"] = (max(-2, min(2, sc)), ev)

    # G - divergences
    ev, neg, pos = [], 0, 0
    comp, b20s = M["comp"], M["b20"]
    hi = max(comp[: i + 1]); lo = min(comp[: i + 1])
    hi_i = comp.index(hi, 0, i + 1); lo_i = comp.index(lo, 0, i + 1)
    if comp[i] >= hi * 0.97 and b20s[i] is not None and b20s[hi_i] is not None and b20s[i] < b20s[hi_i] - 10:
        neg += 1; ev.append("price near the high on materially thinner breadth")
    if comp[i] <= lo * 1.03 and b20s[i] is not None and b20s[lo_i] is not None and b20s[i] > b20s[lo_i] + 10:
        pos += 1; ev.append("price near the low on materially better breadth")
    dr = slope(M["b20"], i, 21)
    if M["roc65"][i] is not None and dr is not None:
        if M["roc65"][i] > 0 and dr < -20:
            neg += 1; ev.append("composite still positive over 65d while breadth collapsed - a shrinking group is holding it up")
        if M["roc65"][i] < 0 and dr > 20:
            pos += 1; ev.append("composite still negative over 65d while breadth repaired")
    if M["lows63"][i] is not None and i >= 10 and comp[i] > comp[i - 10]:
        d = slope(M["lows63"], i, 10)
        if d is not None and d > 0:
            neg += 1; ev.append("new lows expanding while the composite advances - distribution")
    if M["hml52"][i] is not None and comp[i] >= hi * 0.97 and M["hml52"][i] < 0:
        neg += 1; ev.append("price near the high with more 52-week lows than highs")
    if not ev:
        ev.append("no active divergence")
    p["G"] = (max(-2, min(2, pos - neg)), ev)
    p["_div"] = (neg, pos)

    # H - catalyst & confirmation
    ev, sc = [], None
    c20, c50 = M["comp20"][i], M["comp50"][i]
    if c20 is not None and c50 is not None:
        up = c20 > c50
        lo_i2 = max(1, i - 251)
        crosses = sum(1 for k in range(lo_i2, i + 1)
                      if M["comp20"][k] is not None and M["comp50"][k] is not None
                      and M["comp20"][k - 1] is not None and M["comp50"][k - 1] is not None
                      and (M["comp20"][k] > M["comp50"][k]) != (M["comp20"][k - 1] > M["comp50"][k - 1]))
        sc = 1 if up else -1
        ev.append("20-dma %s 50-dma; %d crosses in the trailing year"
                  % ("above" if up else "below", crosses))
        rets = daily_ret(comp)
        st = max(1, i - 59)
        bi = max(range(st, i + 1), key=lambda k: rets[k] if rets[k] is not None else -9)
        if rets[bi] is not None and bi + 3 <= i:
            end = min(bi + 10, i)
            fail = comp[end] < comp[bi - 1]
            ev.append("best up-day (%+.1f%%) %s held" % (rets[bi] * 100, "has NOT" if fail else "has"))
            sc += -1 if fail else (1 if up else 0)
        if crosses >= 4:
            sc = min(sc, 0)
            ev.append("four or more crosses - trend system whipsawing, treat as noise")
        sc = max(-2, min(2, sc))
    p["H"] = (sc, ev)
    return p


def classify(p, M, S, i, override_score=None):
    live = {k: v[0] for k, v in p.items() if k in WEIGHTS and v[0] is not None}
    if not live:
        return None, None, 0.0
    wsum = sum(WEIGHTS[k] for k in live)
    comp_score = sum(live[k] * WEIGHTS[k] for k in live) / (2.0 * wsum) * 100
    coverage = 100.0 * wsum / sum(WEIGHTS.values())
    # the regime history bands a smoothed score; the gates below still use the
    # current day's structure and breadth
    if override_score is not None:
        comp_score = override_score

    s = S[i]
    b20, b50 = M["b20"][i], M["b50"][i]
    d20 = slope(M["b20"], i, 21) or 0
    r65 = M["roc65"][i]
    dr = slope(M["roc65"], i, 21) or 0
    neg, _ = p["_div"]

    recent_climax = any(
        M["comp"][k] / M["comp"][k - 5] - 1 <= -0.10 for k in range(max(5, i - 15), i + 1))
    washout = (b20 is not None and b20 <= 15) or (b50 is not None and b50 <= 10)
    panic = (M["volAlertNeg"][i] or 0) >= 20
    top_confirmed = (s["anchor"] == "peak" and s["crack_i"] is not None
                     and (s["retest_i"] is not None or s["ma_break_i"] is not None))

    if comp_score <= -45 and washout and (recent_climax or panic):
        return ("Capitulation inside a confirmed top" if top_confirmed
                else "Capitulation / washout"), comp_score, coverage
    if comp_score <= -25 and s["at_low_since_peak"] and (r65 or 0) < 0 and dr < 0:
        return "Breakdown", comp_score, coverage
    if -25 <= comp_score < -5 and s["anchor"] == "trough" and s["retest_hold"] and d20 > 0:
        return "Bottoming / base", comp_score, coverage
    # The bottoming side requires the trough to be the live anchor. Without it,
    # a stale thrust/breakout pair matches in the middle of a decline.
    if (-5 <= comp_score < 20 and s["anchor"] == "trough"
            and s["thrust_i"] is not None and s["breakout_i"] is not None):
        return "Early recovery", comp_score, coverage
    # Uptrend regimes additionally require price to be near its trailing high -
    # a good score 20% off the peak is a rally inside a downtrend, not a trend.
    near_high = s["off_peak"] > -0.10
    if comp_score >= 50 and b20 and b20 > 80 and neg == 0 and near_high:
        return "Momentum expansion", comp_score, coverage
    # One divergence is noise; the framework only treats two-or-more with
    # deteriorating breadth as a regime signal. Demanding zero here left
    # healthy advances with a single narrowing tell falling through to
    # "indeterminate", which is not a reading anyone can act on.
    if 20 <= comp_score < 50 and b20 and b20 > 50 and (r65 or 0) > 0 and neg <= 1 and near_high:
        return "Confirmed uptrend", comp_score, coverage
    if top_confirmed or (neg >= 2 and d20 < 0):
        return "Late-cycle topping", comp_score, coverage
    if comp_score <= -25:
        return "Breakdown", comp_score, coverage
    if comp_score >= 20:
        return "Confirmed uptrend", comp_score, coverage
    return "Indeterminate", comp_score, coverage


REGIME_ORDER = ["Capitulation inside a confirmed top", "Capitulation / washout", "Breakdown",
                "Bottoming / base", "Early recovery", "Confirmed uptrend",
                "Momentum expansion", "Late-cycle topping", "Indeterminate"]
REGIME_COLOR = {
    "Capitulation inside a confirmed top": "#8c1d1d",
    "Capitulation / washout": "#d03b3b",
    "Breakdown": "#ec835a",
    "Bottoming / base": "#fab219",
    "Early recovery": "#9dc63b",
    "Confirmed uptrend": "#1baf7a",
    "Momentum expansion": "#0d8f5f",
    "Late-cycle topping": "#b5462f",
    "Indeterminate": "#898781",
}


# ------------------------------------------------------------------- main

def main():
    dates, n, px, vol, bench, empty, raw_rows, n_hol, missing = load()

    full, partial, dropped = {}, {}, list(empty)
    for t, col in px.items():
        cov = sum(v is not None for v in col) / n
        if col[0] is not None and cov >= 0.95:
            full[t] = ffill_small_gaps(col)
        elif cov >= 0.10:
            partial[t] = col
        else:
            dropped.append(t)
    universe = {**full, **partial}
    comp = ew([full[t] for t in full], n)

    print("QC")
    print("  raw rows %d -> %d trading days (%d weekend, %d holiday rows dropped)"
          % (raw_rows, n, raw_rows - n - n_hol, n_hol))
    print("  %s -> %s  (%.1f sessions/yr)" % (dates[0], dates[-1], n / ((len(dates)) / 252.0) / 1))
    print("  universe: %d full + %d partial, dropped %s" % (len(full), len(partial), dropped))
    if missing:
        print("  dates in Price with no Volume row: %d" % len(missing))

    M = build_measures(dates, n, universe, vol, full, comp)
    S = structure_series(comp, M["comp50"], n)

    # ---- rolling regime history ----
    # The raw classifier is evaluated every session and then debounced. It is
    # NOT run on a smoothed score: stacking a 21-day score average on top of
    # the hysteresis below cost about four weeks of lag, which defeats the
    # purpose of a turning-point framework (it reported "indeterminate"
    # through the whole June-July 2026 break). The structural gates are
    # already persistent by construction - crack/retest/50-dma-break do not
    # flicker - so the score is used raw and only the *label* is debounced.
    DWELL = 10
    from collections import Counter
    raw_reg, scores = [None] * n, [None] * n
    for i in range(WARMUP, n):
        p = score_at(i, M, S)
        rg, sc, cov = classify(p, M, S, i)
        raw_reg[i], scores[i] = rg, sc
    # smoothed score kept for the chart only, never for gating
    scores_smooth = [None] * n
    for i in range(WARMUP, n):
        w = [v for v in scores[max(WARMUP, i - 20) : i + 1] if v is not None]
        if w:
            scores_smooth[i] = sum(w) / len(w)

    # Hysteresis: switch once the classifier has disagreed with the held regime
    # for DWELL sessions, adopting whichever regime dominated that stretch.
    # Counting only *consecutive* days of one candidate does not work - when the
    # raw signal alternates between two adjacent bearish regimes neither ever
    # accumulates and the held regime sticks straight through a crash.
    held, dissent = None, []
    regimes = [None] * n
    for i in range(WARMUP, n):
        r = raw_reg[i]
        if r == held:
            dissent = []
        else:
            dissent.append(r)
            if len(dissent) >= DWELL:
                held = Counter(dissent).most_common(1)[0][0]
                dissent = []
        regimes[i] = held or r

    last_i = n - 1
    pnow = score_at(last_i, M, S)
    regime, score_now, coverage = classify(pnow, M, S, last_i)

    # compress regime history into runs for the strip chart
    runs = []
    for i in range(WARMUP, n):
        if runs and runs[-1]["r"] == regimes[i]:
            runs[-1]["e"] = i
        else:
            runs.append({"r": regimes[i], "s": i, "e": i})
    runs = [r for r in runs if r["r"]]

    # events: regime transitions worth naming
    events = []
    for r in runs:
        if r["e"] - r["s"] < 10:
            continue
        events.append({
            "date": dates[r["s"]], "i": r["s"], "title": r["r"],
            "detail": "%s through %s (%d sessions). Composite score %+.0f at entry."
                      % (dates[r["s"]], dates[r["e"]], r["e"] - r["s"] + 1, scores[r["s"]]),
            "kind": "critical" if "Capitulation" in r["r"] or r["r"] in ("Breakdown", "Late-cycle topping")
                    else "info" if r["r"] in ("Confirmed uptrend", "Momentum expansion", "Early recovery")
                    else "serious",
        })

    # per-stock table
    stocks = []
    for t in sorted(universe):
        col = universe[t]
        fi = next(i for i in range(n) if col[i] is not None)
        li = max(i for i in range(n) if col[i] is not None)
        valid = [(i, v) for i, v in enumerate(col) if v is not None]
        hi_i, hi_v = max(valid, key=lambda x: x[1])
        w52 = [v for v in col[max(0, li - YR + 1) : li + 1] if v is not None]
        dbl2y = (t in full and li >= 2 * YR and col[li - 2 * YR]
                 and col[li] / col[li - 2 * YR] >= 2)
        vv = [v for v in (vol.get(t) or [])[max(0, li - 19) : li + 1] if v is not None]
        avg_vol20 = sum(vv) / len(vv) if vv else None
        last_vol = (vol.get(t) or [None] * n)[li]
        stocks.append({
            "t": t, "px": r2(col[li]), "ret5y": r1((col[li] / col[fi] - 1) * 100),
            "ret1y": r1((col[li] / col[li - YR] - 1) * 100) if li >= YR and col[li - YR] else None,
            "offHi": r1((col[li] / hi_v - 1) * 100), "hiDate": dates[hi_i],
            "roc": r1(M["rocs"][t][li]),
            "a20": None, "a50": None,
            "hi52": bool(w52 and col[li] >= max(w52)), "lo52": bool(w52 and col[li] <= min(w52)),
            "dbl": bool(dbl2y), "bell": t in BELLWETHERS, "part": t in partial,
            "advol": r1(avg_vol20 / 1e6) if avg_vol20 else None,
            "relVol": r2(last_vol / avg_vol20) if last_vol is not None and avg_vol20 else None,
        })
    mas20 = {t: sma(universe[t], 20) for t in universe}
    mas50 = {t: sma(universe[t], 50) for t in universe}
    for s in stocks:
        t = s["t"]
        li = max(i for i in range(n) if universe[t][i] is not None)
        s["a20"] = None if mas20[t][li] is None else universe[t][li] > mas20[t][li]
        s["a50"] = None if mas50[t][li] is None else universe[t][li] > mas50[t][li]

    slim = lambda x: [r2(v) for v in x]
    pill = []
    for k in ("A", "B", "C", "E", "F", "G", "H"):
        sc, ev = pnow[k]
        pill.append({"key": k, "name": PILLAR_NAMES[k], "score": sc,
                     "weight": WEIGHTS[k], "evidence": ev,
                     "status": "insufficient-history" if sc is None else
                               ("bull" if sc > 0 else "bear" if sc < 0 else "neutral")})

    data = {
        "dates": dates,
        "comp": slim(comp), "comp50": slim(M["comp50"]), "comp200": slim(M["comp200"]),
        "b20": slim(M["b20"]), "b50": slim(M["b50"]), "b200": slim(M["b200"]),
        "roc65": slim(M["roc65"]), "spread": slim(M["spread"]),
        "hml52": slim(M["hml52"]), "hi52": M["hi52"], "lo52": M["lo52"],
        "obos": slim(M["obos"]), "x2065": slim(M["x2065"]),
        "betaSpread": slim(M["betaSpread"]), "betaPct": slim(M["betaPct"]),
        "sharpe": slim(M["sharpe"]), "sharpePct": slim(M["sharpePct"]),
        "doubled2y": slim(M["doubled2y"]),
        "volAlertPos": slim(M["volAlertPos"]), "volAlertNeg": slim(M["volAlertNeg"]),
        "bellRel": slim(M["bellRel"]),
        "upDownVol": slim(M["upDownVol"]), "distDays": M["distDays"], "accumDays": M["accumDays"],
        "totVol": [None if v is None else round(v / 1e6, 1) for v in M["totVol"]],
        "totVol50": [None if v is None else round(v / 1e6, 1) for v in M["totVol50"]],
        "obv": [None if v is None else round(v / 1e6, 1) for v in M["obv"]],
        "macdLine": slim(M["macdLine"]), "macdSignal": slim(M["macdSignal"]), "macdHist": slim(M["macdHist"]),
        "rsi": slim(M["rsi"]),
        # Raw benchmark price levels (not rebased) - the dashboard rebases to
        # 100 and computes the composite ratio client-side for whichever
        # period the viewer selects, same pattern as the sub-basket charts.
        "bench": {bt: slim(c) for bt, c in bench.items()},
        # "comp" is the basket's own rebalanced equal-weight level series; the
        # dashboard rebases it (and its ratio to the universe composite) to the
        # start of whichever period the viewer selects.
        "baskets": {k: {"roc": slim(v["roc"]), "comp": slim(v["comp"]),
                        "n": v["n"], "members": v["members"]}
                    for k, v in M["baskets"].items()},
        "cycleBaskets": [k for k in CYCLE_BASKETS if k in M["baskets"]],
        "scores": slim(scores), "scoresSmooth": slim(scores_smooth),
        "regimes": regimes,
        "runs": runs,
        "regimeOrder": REGIME_ORDER, "regimeColor": REGIME_COLOR,
        "events": events,
        "pillars": pill,
        "verdict": {
            "regime": regime, "score": r1(score_now), "coverage": r1(coverage),
            "lastDate": dates[last_i], "comp": r1(comp[last_i]),
            "peakDate": dates[S[last_i]["peak_i"]], "peakVal": r1(comp[S[last_i]["peak_i"]]),
            "drawdown": r1((comp[last_i] / comp[S[last_i]["peak_i"]] - 1) * 100),
            "ret5y": r1(comp[last_i] - 100),
            "playbook": REGIME_PLAYBOOK[regime],
        },
        "stocks": stocks,
        "meta": {
            "nFull": len(full), "nPartial": len(partial), "dropped": dropped,
            "partial": sorted(partial), "built": dates[last_i],
            "rawRows": raw_rows, "holidays": n_hol, "tradingDays": n,
            "hiBeta": M["hiBetaNames"], "loBeta": M["loBetaNames"], "bell": M["bellNames"],
            "source": os.path.basename(XLSX),
            "benchmarks": sorted(bench),
        },
    }

    with open(TEMPLATE, encoding="utf-8") as f:
        html = f.read()
    if "/*__DATA__*/" not in html:
        sys.exit("marker not found in template")
    html = html.replace("/*__DATA__*/", "const DATA = " + json.dumps(data, separators=(",", ":")) + ";")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)

    print("\nOK -> %s" % OUT)
    print("  regime: %s  (score %+.1f, coverage %.0f%%)" % (regime, score_now, coverage))
    print("  pillars: %s" % {k: pnow[k][0] for k in ("A", "B", "C", "E", "F", "G", "H")})
    print("  peak %s @ %.0f | last %.0f (%.0f%% off)"
          % (data["verdict"]["peakDate"], data["verdict"]["peakVal"],
             comp[last_i], data["verdict"]["drawdown"]))
    print("  regime runs (>=10 sessions):")
    for r in runs:
        if r["e"] - r["s"] >= 9:
            print("    %s -> %s  %s" % (dates[r["s"]], dates[r["e"]], r["r"]))
    print("  benchmarks: %s | up/down vol %.2f | dist/accum days %s/%s"
          % (sorted(bench), M["upDownVol"][last_i] or 0, M["distDays"][last_i], M["accumDays"][last_i]))
    print("  composite RSI(14) %.1f | MACD hist %.2f" % (M["rsi"][last_i] or 0, M["macdHist"][last_i] or 0))


if __name__ == "__main__":
    main()
