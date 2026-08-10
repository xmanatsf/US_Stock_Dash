# -*- coding: utf-8 -*-
"""RenMac semiconductor market-timing scorer.

Reads the same daily-close workbook build_dashboard.py uses, scores seven
price-derivable pillars from the RenMac / deGraaf framework, and classifies the
semi complex into one named regime. See RENMAC_TIMING_FRAMEWORK.md for the
analytical derivation of every threshold in this file.

Design rules:
  - Every scored input is derivable from the price file. Nothing is left blank
    for a human to fill in.
  - A measure that the file cannot support returns status "insufficient-history"
    and is dropped from the composite, with the remaining weights renormalised.
    It never returns a fabricated zero.
  - The structure pillar (F) transcribes build_dashboard.main()'s inline
    peak/crack/retest/climax logic verbatim so the two agree on event dates,
    and adds the mirror bottoming sequence that the builder does not compute.

Usage:
    python renmac_score.py
    python renmac_score.py --xlsx "US semi stocks price 20260725.xlsx"
    python renmac_score.py --json
"""
import argparse
import json
import os
import sys

import build_dashboard as bd
from build_dashboard import ffill_small_gaps, sma, roc, daily_ret, rolling_z

HERE = os.path.dirname(os.path.abspath(__file__))

# Sub-baskets for the semiconductor-cycle pillar. Equipment/WFE leads at turns,
# analog/MCU broadening confirms a durable recovery, AI/compute carrying the
# composite alone is late-cycle narrowing. "Thematic" names (solar, quantum)
# trade on their own drivers and are reported but not scored.
SUBBASKETS = {
    "WFE/equipment": [
        "AMAT", "LRCX", "KLAC", "ONTO", "ACLS", "ENTG", "MKSI", "UCTT", "ICHR",
        "TER", "AMKR", "PLAB", "FORM", "AEHR", "VECO", "RTEC", "COHU", "ACMR",
        "SKYT",
    ],
    "AI/compute": ["NVDA", "AVGO", "AMD", "MRVL", "ALAB", "GFS", "INTC", "QCOM"],
    "Memory": ["MU", "RMBS"],
    "Analog/MCU": [
        "ADI", "TXN", "MCHP", "ON", "MPWR", "POWI", "DIOD", "ALGM", "SLAB",
        "SWKS", "QRVO", "SMTC", "AOSL", "SYNA", "MXL", "CRUS", "PI", "MTSI",
        "CEVA", "LSCC", "INDI", "MBLY", "NVTS", "AMBA", "SITM",
    ],
    "Thematic": ["ENPH", "FSLR", "RGTI", "KOPN", "NVEC", "OLED", "AXTI", "WOLF"],
}
CYCLE_BASKETS = ["WFE/equipment", "AI/compute", "Memory", "Analog/MCU"]

WEIGHTS = {"A": 10, "B": 25, "C": 10, "E": 15, "F": 20, "G": 15, "H": 5}

PILLAR_NAMES = {
    "A": "Positioning & extension",
    "B": "Breadth, trend & relative strength",
    "C": "Sentiment & crowding",
    "E": "Semiconductor-cycle position",
    "F": "Structure (accumulation / distribution)",
    "G": "Divergences",
    "H": "Catalyst & confirmation",
}

OK = "ok"
NO_HIST = "insufficient-history"


# ----------------------------------------------------------------- utilities

def pct_rank(series, i):
    """Percentile of series[i] among all valid values in the window (0-100).

    In-sample within this file: with ~1 year of data there is no out-of-sample
    history to rank against, so read these as 'where does today sit in the past
    12 months', not as RenMac's multi-decade percentiles.
    """
    vals = [v for v in series if v is not None]
    if series[i] is None or len(vals) < 30:
        return None
    return 100.0 * sum(v <= series[i] for v in vals) / len(vals)


def slope(series, i, lookback):
    """Change in a series over `lookback` sessions, skipping Nones."""
    j = i - lookback
    if j < 0 or series[i] is None or series[j] is None:
        return None
    return series[i] - series[j]


def ew_composite(cols, n):
    """Equal-weight composite (base 100) of a list of price columns."""
    out = []
    for i in range(n):
        vals = [c[i] / c[0] * 100 for c in cols if c[i] is not None and c[0]]
        out.append(sum(vals) / len(vals) if vals else None)
    return out


def stochastic(col, n=14):
    """14-day stochastic %K, RenMac's overbought/oversold measure."""
    out = [None] * len(col)
    for i in range(n - 1, len(col)):
        w = [v for v in col[i - n + 1 : i + 1] if v is not None]
        if len(w) < n or col[i] is None:
            continue
        lo, hi = min(w), max(w)
        out[i] = 50.0 if hi == lo else 100.0 * (col[i] - lo) / (hi - lo)
    return out


def band(x, cuts):
    """Map x onto -2..+2 given four ascending cut points."""
    for s, c in zip((-2, -1, 0, 1), cuts):
        if x < c:
            return s
    return 2


# -------------------------------------------------------------- data loading

def load(xlsx):
    bd.XLSX = xlsx
    # load_prices() also returns per-ticker volume and benchmark (SMH/SPY)
    # price dicts, both unused by this price-only scorer.
    dates, raw, _vol, _bench, dropped = bd.load_prices()
    n = len(dates)
    full, partial = {}, {}
    for t, col in raw.items():
        cov = sum(v is not None for v in col) / n
        if col[0] is not None and cov >= 0.95:
            full[t] = ffill_small_gaps(col)
        elif cov >= 0.10:
            partial[t] = col
        else:
            dropped.append(t)
    universe = {**full, **partial}
    comp = ew_composite([full[t] for t in full], n)
    return dates, n, full, partial, universe, comp, dropped


# ------------------------------------------------------- structure (pillar F)

def structure(comp, comp50, n):
    """Topping sequence (transcribed from build_dashboard.main()) plus its
    mirror bottoming sequence. Returns a dict of indices and flags."""
    s = {}
    peak_i = comp.index(max(comp))
    trough_i = comp.index(min(comp))
    s["peak_i"], s["trough_i"] = peak_i, trough_i
    s["post_min_i"] = min(range(peak_i, n), key=lambda i: comp[i])

    # --- topping side (verbatim from build_dashboard.main) ---
    crack1_i = next(
        (i for i in range(peak_i + 1, n) if comp[i] / comp[max(peak_i, i - 5)] - 1 <= -0.08),
        None,
    )
    retest_i = crack1_low_i = None
    if crack1_i is not None and crack1_i < n - 1:
        cand = max(range(crack1_i, n), key=lambda i: comp[i])
        lo = min(range(peak_i, cand + 1), key=lambda i: comp[i])
        if comp[cand] > comp[lo] * 1.05 and cand > crack1_i:
            retest_i, crack1_low_i = cand, lo
    if crack1_low_i is None and crack1_i is not None:
        crack1_low_i = min(range(peak_i, crack1_i + 1), key=lambda i: comp[i])

    start = retest_i if retest_i is not None else peak_i
    climax_i, climax_chg = None, 0.0
    for i in range(start + 5, n):
        chg = comp[i] / comp[i - 5] - 1
        if chg < climax_chg:
            climax_i, climax_chg = i, chg

    bounce_i = None
    if climax_i is not None and climax_i < n - 1:
        bounce_i = max(range(climax_i, n), key=lambda i: comp[i])

    ma_break_i = next(
        (i for i in range(peak_i, n) if comp50[i] is not None and comp[i] < comp50[i]), None
    )
    s.update(
        crack1_i=crack1_i, crack1_low_i=crack1_low_i, retest_i=retest_i,
        climax_i=climax_i, climax_chg=climax_chg, bounce_i=bounce_i,
        ma_break_i=ma_break_i,
    )

    # --- bottoming side (the mirror the builder does not compute) ---
    thrust_i = next(
        (i for i in range(trough_i + 1, n) if comp[i] / comp[max(trough_i, i - 5)] - 1 >= 0.08),
        None,
    )
    retest_hold = None
    if thrust_i is not None and thrust_i < n - 1:
        post = min(range(thrust_i, n), key=lambda i: comp[i])
        # a successful retest pulls back but does not undercut the trough
        retest_hold = comp[post] > comp[trough_i]
        s["retest_low_i"] = post
    breakout_i = None
    if thrust_i is not None:
        breakout_i = next(
            (
                i
                for i in range(thrust_i, n)
                if comp50[i] is not None
                and comp[i] > comp50[i]
                and (slope(comp50, i, 10) or 0) > 0
            ),
            None,
        )
    s.update(thrust_i=thrust_i, retest_hold=retest_hold, breakout_i=breakout_i)

    # Which anchor is live? The playbook's "where does the extremum sit
    # relative to now" step: the more recent extremum owns the narrative.
    s["anchor"] = "peak" if peak_i > trough_i else "trough"
    return s


# ------------------------------------------------------------------- pillars

def pillar_A(universe, comp, n, last_i):
    """Positioning & extension: high-beta vs low-beta, RenMac's 96th-percentile
    unease test. Peaks and contractions beat levels."""
    ev = []
    ev.append(
        "3-yr rolling Sharpe percentile: %s (needs ~750 sessions, file has %d)"
        % (NO_HIST, n)
    )
    cret = daily_ret(comp)
    betas = {}
    for t, col in universe.items():
        r = daily_ret(col)
        pairs = [(a, b) for a, b in zip(r, cret) if a is not None and b is not None]
        if len(pairs) < 100:
            continue
        mb = sum(b for _, b in pairs) / len(pairs)
        var = sum((b - mb) ** 2 for _, b in pairs)
        if var <= 0:
            continue
        ma = sum(a for a, _ in pairs) / len(pairs)
        betas[t] = sum((a - ma) * (b - mb) for a, b in pairs) / var
    if len(betas) < 25:
        return None, NO_HIST, ["fewer than 25 tickers with enough history to fit a beta"]

    ranked = sorted(betas, key=lambda t: betas[t])
    q = max(3, len(ranked) // 5)
    lo_b, hi_b = ranked[:q], ranked[-q:]
    hi_c = ew_composite([universe[t] for t in hi_b], n)
    lo_c = ew_composite([universe[t] for t in lo_b], n)
    spread = [
        None if (h is None or l is None or not l) else h / l * 100
        for h, l in zip(hi_c, lo_c)
    ]
    pr = pct_rank(spread, last_i)
    sl = slope(spread, last_i, 21)
    if pr is None or sl is None:
        return None, NO_HIST, ev + ["high/low-beta spread not computable"]

    ev.append(
        "high-beta vs low-beta spread in the %.0fth percentile of the window, "
        "%s over 21 sessions" % (pr, "rising" if sl > 0 else "falling")
    )
    if pr >= 90:
        score, why = (-2, "extension at an extreme and contracting - RenMac's mean-reversion setup") \
            if sl < 0 else (-1, "extension at an extreme but still rising - long fuse, stay long but sized")
    elif pr >= 70:
        score, why = (-1, "beta trade crowded and rolling over") if sl < 0 else (0, "beta trade extended but orderly")
    elif pr <= 20:
        score, why = (2, "beta reviving from a washed-out base - the early-recovery signature") \
            if sl > 0 else (-1, "beta dead and getting deader - risk appetite still contracting")
    else:
        score, why = (1, "extension mid-range with beta improving - 'not exhaustive'") if sl > 0 else \
                     (0, "extension mid-range, beta drifting")
    ev.append(why)
    return score, OK, ev


def pillar_B(universe, comp, comp50, n, last_i):
    """Breadth, trend and relative strength - the primary read."""
    ev = []
    mas20 = {t: sma(universe[t], 20) for t in universe}
    mas50 = {t: sma(universe[t], 50) for t in universe}
    mas65 = {t: sma(universe[t], 65) for t in universe}
    mas200 = {t: sma(universe[t], 200) for t in universe}

    def breadth(mas):
        out = [None] * n
        for i in range(n):
            cnt = tot = 0
            for t in universe:
                p, m = universe[t][i], mas[t][i]
                if p is None or m is None:
                    continue
                tot += 1
                cnt += p > m
            if tot >= 30:
                out[i] = 100.0 * cnt / tot
        return out

    b20, b50, b200 = breadth(mas20), breadth(mas50), breadth(mas200)

    # % of issues with 20-dma above 65-dma (RenMac's short-vs-intermediate trend chart)
    x2065 = [None] * n
    for i in range(n):
        cnt = tot = 0
        for t in universe:
            a, b = mas20[t][i], mas65[t][i]
            if a is None or b is None:
                continue
            tot += 1
            cnt += a > b
        if tot >= 30:
            x2065[i] = 100.0 * cnt / tot

    # 65-day highs minus 65-day lows, % of issues
    hml = [None] * n
    for i in range(65, n):
        hi = lo = tot = 0
        for t in universe:
            col = universe[t]
            if col[i] is None:
                continue
            w = [v for v in col[i - 64 : i + 1] if v is not None]
            if len(w) < 50:
                continue
            tot += 1
            hi += col[i] >= max(w)
            lo += col[i] <= min(w)
        if tot >= 30:
            hml[i] = 100.0 * (hi - lo) / tot

    # overbought minus oversold, 14-day stochastic
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
        if tot >= 30:
            obos[i] = 100.0 * (ob - os_) / tot

    if b20[last_i] is None or b50[last_i] is None:
        return None, NO_HIST, ["breadth not computable"]

    d20 = slope(b20, last_i, 21)
    ev.append("%.0f%% above the 20-dma (%+.0f pts over 21 sessions)" % (b20[last_i], d20 or 0))
    ev.append("%.0f%% above the 50-dma" % b50[last_i])
    if b200[last_i] is not None:
        n200 = sum(v is not None for v in b200)
        ev.append("%.0f%% above the 200-dma (level valid; only %d sessions of history for its trend)"
                  % (b200[last_i], n200))
    else:
        ev.append("200-dma breadth: %s (needs 200 sessions per ticker)" % NO_HIST)
    if x2065[last_i] is not None:
        ev.append("%.0f%% with the 20-dma above the 65-dma" % x2065[last_i])
    if hml[last_i] is not None:
        ev.append("65-day highs minus lows: %+.0f%% of issues" % hml[last_i])
    if obos[last_i] is not None:
        ev.append("overbought minus oversold: %+.0f%% of issues" % obos[last_i])

    # level score, then a directional overlay - direction over level
    lvl = band(b20[last_i], (15, 35, 55, 80))
    if b50[last_i] < 25:
        lvl = min(lvl, -1)
    if x2065[last_i] is not None and x2065[last_i] > 65 and b50[last_i] > 55:
        lvl = max(lvl, 1)
    if hml[last_i] is not None:
        lvl += 1 if hml[last_i] > 10 else (-1 if hml[last_i] < -10 else 0)
    if d20 is not None:
        lvl += 1 if d20 > 20 else (-1 if d20 < -20 else 0)
    score = max(-2, min(2, lvl))
    ev.append("breadth %s and %s" % (
        "washed out" if b20[last_i] < 15 else "weak" if b20[last_i] < 40
        else "healthy" if b20[last_i] < 80 else "extended",
        "improving" if (d20 or 0) > 5 else "deteriorating" if (d20 or 0) < -5 else "flat",
    ))
    return score, OK, ev, {"b20": b20, "b50": b50, "b200": b200, "hml": hml, "obos": obos,
                           "x2065": x2065, "mas20": mas20, "mas50": mas50}


def pillar_C(universe, full, comp, n, last_i):
    """Sentiment and crowding: vol alerts, leadership concentration, momentum
    dispersion. Bottoms are built from panic, tops from FOMO."""
    ev = []
    # RenMac vol alerts: an outsized daily move against trailing volatility.
    pos = neg = tot = 0
    for t, col in universe.items():
        z = rolling_z(daily_ret(col), 65)
        w = [v for v in z[max(0, last_i - 4) : last_i + 1] if v is not None]
        if not w:
            continue
        tot += 1
        pos += any(v >= 2.5 for v in w)
        neg += any(v <= -2.5 for v in w)
    if tot < 25:
        return None, NO_HIST, ["too few tickers with 65 sessions of returns for vol alerts"]
    pos_p, neg_p = 100.0 * pos / tot, 100.0 * neg / tot
    ev.append("vol alerts over the last 5 sessions: %.0f%% positive, %.0f%% negative" % (pos_p, neg_p))

    # Leadership concentration: bellwethers vs the equal-weight composite.
    bell = [t for t in bd.BELLWETHERS if t in full]
    conc_sl = None
    if len(bell) >= 4:
        bc = ew_composite([full[t] for t in bell], n)
        rel = [None if (b is None or c is None or not c) else b / c * 100 for b, c in zip(bc, comp)]
        conc_sl = slope(rel, last_i, 65)
        ev.append("bellwether basket vs equal-weight composite %+.1f pts over 65 sessions (%s)"
                  % (conc_sl, "leadership narrowing" if conc_sl > 0 else "leadership broadening"))

    # Momentum-quintile spread as a crowding gauge.
    rocs = {t: roc(universe[t], 65) for t in universe}
    spread = [None] * n
    for i in range(65, n):
        xs = sorted(v for v in (rocs[t][i] for t in universe) if v is not None)
        if len(xs) < 25:
            continue
        q = len(xs) // 5
        spread[i] = sum(xs[-q:]) / q - sum(xs[:q]) / q
    sp_pr = pct_rank(spread, last_i)
    sp_sl = slope(spread, last_i, 21)
    if sp_pr is not None:
        ev.append("momentum-quintile spread at percentile %.0f of the window, %s"
                  % (sp_pr, "widening" if (sp_sl or 0) > 0 else "compressing"))

    score = 0
    if pos_p >= 20 and neg_p < 10:
        score += 1
        ev.append("a buyer's panic - RenMac: these mark escape velocity, not tops")
    if neg_p >= 20:
        ev.append("a seller's panic - the raw material for a base, but not bullish on its own")
    if conc_sl is not None:
        score += -1 if conc_sl > 2 else (1 if conc_sl < -2 else 0)
    if sp_pr is not None and sp_pr >= 85 and (sp_sl or 0) < 0:
        score -= 1
        ev.append("crowded momentum leadership now compressing - the unwind signature")
    score = max(-2, min(2, score))
    return score, OK, ev, {"neg_panic": neg_p >= 20, "pos_panic": pos_p >= 20}


def pillar_E(universe, comp, comp50, n, last_i):
    """Semiconductor-cycle position from sub-basket relative strength.

    Equipment/WFE leads in both directions - it turns up first out of a trough
    and rolls first into a top - so its relative strength carries more weight
    than the raw count of baskets that happen to be positive. A basket needs at
    least three names to be scored; thinner ones are reported but not traded on.
    """
    ev = []
    comp_roc = roc(comp, 65)
    res = {}
    for name, tickers in SUBBASKETS.items():
        cols = [universe[t] for t in tickers if t in universe]
        if len(cols) < 2:
            continue
        c = ew_composite(cols, n)
        r = roc(c, 65)
        if r[last_i] is None:
            continue
        res[name] = (r[last_i], r[last_i] - (comp_roc[last_i] or 0), len(cols))
    core = {k: v for k, v in res.items() if k in CYCLE_BASKETS and v[2] >= 3}
    if not core:
        return None, NO_HIST, ["no cycle sub-basket has 3 names and 65 sessions of history"]

    for name in SUBBASKETS:
        if name in res:
            a, rel, cnt = res[name]
            thin = "" if (name not in CYCLE_BASKETS or cnt >= 3) else "  [thin, not scored]"
            ev.append("%-14s %+6.1f%% 65d (%+.1f vs composite, %d names)%s" % (name, a, rel, cnt, thin))

    npos = sum(v[0] > 0 for v in core.values())
    lead = max(core, key=lambda k: core[k][1])
    wfe = core.get("WFE/equipment")
    ev.append("%d of %d scored cycle baskets positive; leadership in %s" % (npos, len(core), lead))

    # Is the tape itself advancing? A 65-day ROC can still read positive well
    # into a drawdown, so "all baskets up" means nothing without this check.
    tape_down = (
        comp50[last_i] is not None
        and comp[last_i] < comp50[last_i]
        and (slope(comp50, last_i, 21) or 0) < 0
    )
    if tape_down:
        ev.append("composite is below a falling 50-dma - read these as a rolling cycle, "
                  "not a broad advance")
        if wfe is not None and wfe[1] > 5:
            score = 1
            ev.append("equipment outperforming into a weak tape - equipment leads at cycle turns, "
                      "the first constructive tell")
        elif wfe is not None and wfe[1] < -2:
            score = -2
            ev.append("equipment lagging into a weak tape - the cycle is rolling over, not turning up")
        else:
            score = -1
            ev.append("equipment neither leading nor badly lagging - no cycle turn signal yet")
    elif npos == len(core) and lead in ("WFE/equipment", "Analog/MCU"):
        score = 2
        ev.append("broad and led by the cycle-sensitive end - a durable, broadening advance")
    elif npos >= len(core) - 1:
        score = 1 if lead != "AI/compute" else 0
        ev.append("advance is broad" if score == 1 else
                  "broad but AI/compute is doing the leading - watch for narrowing")
    elif npos <= 1:
        score = -2
        ev.append("cycle has narrowed to one basket or none - late-cycle or outright breakdown")
    else:
        score = -1
        ev.append("cycle splitting - part of the complex has already rolled")
    return max(-2, min(2, score)), OK, ev


def pillar_F(s, comp, dates, n, last_i):
    """Structure: which sequence is actually on the tape."""
    ev = []
    peak_i, trough_i = s["peak_i"], s["trough_i"]
    ev.append("peak %s at %.0f; trough %s at %.0f; now %.0f (%+.0f%% off the peak)"
              % (dates[peak_i], comp[peak_i], dates[trough_i], comp[trough_i],
                 comp[last_i], (comp[last_i] / comp[peak_i] - 1) * 100))
    ev.append("live anchor: the %s (more recent extremum)" % s["anchor"])

    if s["anchor"] == "peak":
        bits, score = [], 0
        if s["crack1_i"] is not None:
            bits.append("first crack %s" % dates[s["crack1_i"]])
            score -= 1
        if s["retest_i"] is not None:
            bits.append("failed retest %s (%.1f%% under the high)"
                        % (dates[s["retest_i"]], abs((comp[s["retest_i"]] / comp[peak_i] - 1) * 100)))
            score -= 1
        if s["ma_break_i"] is not None:
            bits.append("50-dma break %s" % dates[s["ma_break_i"]])
        if s["climax_i"] is not None:
            bits.append("climax week %s (%.0f%%)" % (dates[s["climax_i"]], s["climax_chg"] * 100))
        if s["post_min_i"] == last_i:
            bits.append("closing at the post-peak low")
            score -= 1
        ev.append(" -> ".join(bits) if bits else "peak behind, no break yet")
        return max(-2, min(2, score)), OK, ev

    bits, score = [], 0
    if s["thrust_i"] is not None:
        bits.append("thrust %s" % dates[s["thrust_i"]])
        score += 1
    if s["retest_hold"]:
        bits.append("retest held above the trough")
        score += 1
    elif s["retest_hold"] is False:
        bits.append("retest undercut the trough")
        score -= 1
    if s["breakout_i"] is not None:
        bits.append("breakout above a rising 50-dma %s" % dates[s["breakout_i"]])
        score += 1
    ev.append(" -> ".join(bits) if bits else "trough behind, no thrust yet")
    return max(-2, min(2, score)), OK, ev


def pillar_G(universe, comp, b, n, last_i):
    """Divergences between price and what is happening underneath it."""
    ev = []
    b20, hml = b["b20"], b["hml"]
    comp_roc = roc(comp, 65)
    hi = max(comp)
    lo = min(comp)
    hi_i, lo_i = comp.index(hi), comp.index(lo)
    neg = pos = 0

    if comp[last_i] >= hi * 0.97 and b20[last_i] is not None and b20[hi_i] is not None:
        if b20[last_i] < b20[hi_i] - 10:
            neg += 1
            ev.append("price back near the high on %.0f%% breadth vs %.0f%% at the high - "
                      "negative breadth divergence" % (b20[last_i], b20[hi_i]))
    if comp[last_i] <= lo * 1.03 and b20[last_i] is not None and b20[lo_i] is not None:
        if b20[last_i] > b20[lo_i] + 10:
            pos += 1
            ev.append("price back near the low on %.0f%% breadth vs %.0f%% at the low - "
                      "positive breadth divergence" % (b20[last_i], b20[lo_i]))

    if comp_roc[last_i] is not None:
        rmax = max(v for v in comp_roc if v is not None)
        rmin = min(v for v in comp_roc if v is not None)
        if comp[last_i] >= hi * 0.97 and comp_roc[last_i] < rmax - 15:
            neg += 1
            ev.append("price near the high with 65d ROC at %+.0f%% vs a %+.0f%% peak - "
                      "momentum divergence" % (comp_roc[last_i], rmax))
        if comp[last_i] <= lo * 1.03 and comp_roc[last_i] > rmin + 15:
            pos += 1
            ev.append("price near the low with 65d ROC at %+.0f%% vs a %+.0f%% trough - "
                      "momentum improving under a flat price" % (comp_roc[last_i], rmin))

    # new lows expanding while the tape advances = distribution (and its mirror)
    lows = [None] * n
    highs = [None] * n
    for i in range(60, n):
        l = h = 0
        for t, col in universe.items():
            if col[i] is None:
                continue
            w = [v for v in col[max(0, i - 62) : i + 1] if v is not None]
            if len(w) < 50:
                continue
            l += col[i] <= min(w)
            h += col[i] >= max(w)
        lows[i], highs[i] = l, h
    adv = comp[last_i] > comp[last_i - 10] if last_i >= 10 else None
    dl, dh = slope(lows, last_i, 10), slope(highs, last_i, 10)
    if adv and (dl or 0) > 0:
        neg += 1
        ev.append("composite up over 10 sessions while 3-month lows expanded by %d - "
                  "distribution beneath the surface" % dl)
    if adv is False and (dh or 0) > 0:
        pos += 1
        ev.append("composite down over 10 sessions while 3-month highs expanded by %d - "
                  "accumulation beneath the surface" % dh)
    if hml[last_i] is not None and comp[last_i] >= hi * 0.97 and hml[last_i] < 0:
        neg += 1
        ev.append("price near the high with more new lows than new highs")

    # Price vs breadth away from the extremes. The composite can still show a
    # positive 65-day ROC well into a drawdown while participation collapses -
    # a shrinking group holding the index up. This is the divergence that fires
    # in the middle of the range, where the extremum-anchored tests are silent.
    db20 = slope(b20, last_i, 21)
    if comp_roc[last_i] is not None and db20 is not None:
        if comp_roc[last_i] > 0 and db20 < -20:
            neg += 1
            ev.append("composite still %+.0f%% over 65 sessions while breadth fell %.0f pts in 21 - "
                      "a shrinking group is holding the index up" % (comp_roc[last_i], -db20))
        if comp_roc[last_i] < 0 and db20 > 20:
            pos += 1
            ev.append("composite still %+.0f%% over 65 sessions while breadth gained %.0f pts in 21 - "
                      "participation is repairing under a weak index" % (comp_roc[last_i], db20))

    if not ev:
        ev.append("no active divergence in either direction")
    score = max(-2, min(2, pos - neg))
    return score, OK, ev, {"neg": neg, "pos": pos, "lows": lows, "highs": highs}


def pillar_H(comp, comp20, comp50, dates, n, last_i):
    """Catalyst and confirmation: trend system state, whipsaw count, and the
    price-side 'failure on good news' test."""
    ev = []
    if comp20[last_i] is None or comp50[last_i] is None:
        return None, NO_HIST, ["20/50-dma not available"]
    up = comp20[last_i] > comp50[last_i]
    crosses = sum(
        1
        for i in range(1, n)
        if comp20[i] is not None and comp50[i] is not None
        and comp20[i - 1] is not None and comp50[i - 1] is not None
        and (comp20[i] > comp50[i]) != (comp20[i - 1] > comp50[i - 1])
    )
    ev.append("20-dma is %s the 50-dma; %d crosses in the window (RenMac grades this system "
              "+A for efficacy but warns of whipsaw)" % ("above" if up else "below", crosses))

    # failure on good news: was the best up-day of the last 60 sessions retraced?
    rets = daily_ret(comp)
    lo = max(1, last_i - 59)
    best_i = max(range(lo, last_i + 1), key=lambda i: rets[i] if rets[i] is not None else -9)
    fail = None
    if rets[best_i] is not None and best_i + 3 <= last_i:
        end = min(best_i + 10, last_i)
        fail = comp[end] < comp[best_i - 1]
        ev.append("best up-day of the last 60 sessions was %s (%+.1f%%); %d sessions later the "
                  "composite is %s that day's starting level - %s"
                  % (dates[best_i], rets[best_i] * 100, end - best_i,
                     "below" if fail else "above",
                     "good news failed to hold" if fail else "good news held"))
    else:
        ev.append("best up-day of the last 60 sessions is too recent to test for follow-through")
    score = 1 if up else -1
    if fail:
        score -= 1
    elif fail is False and up:
        score += 1
    if crosses >= 4:
        score = 0 if score > 0 else score
        ev.append("four or more crosses - trend system is whipsawing, treat its signal as noise")
    return max(-2, min(2, score)), OK, ev


# ------------------------------------------------------------- classification

REGIME_PLAYBOOK = {
    "Capitulation / washout": dict(
        exposure="30-50%, scaling in", tilt="highest-beta and equipment first; avoid the late-cycle laggards",
        confirm="a retest that holds above the low, breadth back above 30%, 3-month lows contracting",
        invalidate="a lower low on expanding new lows - the washout was a way-station, not a bottom",
    ),
    # A washout that arrives AFTER a confirmed topping sequence is distribution,
    # not accumulation. RenMac's chip-top note is explicit: in this structure the
    # oversold bounces fail and the base case is 18-24 months of malaise. Same
    # measurements as the regime above, opposite instruction.
    "Capitulation inside a confirmed top": dict(
        exposure="15-35%, do NOT scale in yet",
        tilt="use the bounce to sell strength and cut relative laggards; rotate to value/cyclical leadership",
        confirm="only a held retest above this low plus breadth back over 30% turns this into a buyable base",
        invalidate="a thrust that holds on retest with 65-day highs expanding - then the top has fully discounted",
    ),
    "Breakdown": dict(
        exposure="0-25%", tilt="quality over beta, large over small; sell oversold bounces",
        confirm="nothing yet - wait for a climax and a held retest",
        invalidate="a thrust off a trough that holds on a retest",
    ),
    "Bottoming / base": dict(
        exposure="40-60%", tilt="equipment/WFE first, memory second; leave analog for later",
        confirm="reclaim of a rising 50-dma and 65-day highs beginning to expand",
        invalidate="an undercut of the trough, or breadth rolling back under 20%",
    ),
    "Early recovery": dict(
        exposure="60-80%", tilt="add cyclically - equipment, then memory, then analog as it broadens",
        confirm="breadth above 55% and holding, analog joining, dispersion widening",
        invalidate="breadth failing back under 35% or a close back below the 50-dma",
    ),
    "Confirmed uptrend": dict(
        exposure="80-100%", tilt="buy pullbacks in names still in uptrends; large over small",
        confirm="65-day-high spikes, breadth above 80% - momentum expansion",
        invalidate="a first crack, or two active negative divergences",
    ),
    "Momentum expansion": dict(
        exposure="90-100% but stop adding", tilt="stay with leadership; start monitoring extension percentiles daily",
        confirm="extension percentiles mid-range means the move is 'not exhaustive' - stay long",
        invalidate="extension percentile peaking and contracting, or breadth diverging from price",
    ),
    "Late-cycle topping": dict(
        exposure="25-50% and falling", tilt="sell strength, cut relative laggards, rotate to quality/value",
        confirm="a failed retest and a 50-dma break confirm the top",
        invalidate="a breadth thrust above 80% with new highs expanding - the top call is wrong",
    ),
    "Indeterminate": dict(
        exposure="hold current", tilt="no regime signal - do not force a trade",
        confirm="wait for breadth and structure to agree",
        invalidate="n/a",
    ),
}


def classify(scores, s, b, cflags, gflags, comp, n, last_i):
    live = {k: v for k, v in scores.items() if v is not None}
    wsum = sum(WEIGHTS[k] for k in live)
    total = sum(WEIGHTS[k] for k in WEIGHTS)
    composite = sum(scores[k] * WEIGHTS[k] for k in live) / (2.0 * wsum) * 100 if wsum else 0.0
    coverage = 100.0 * wsum / total

    b20 = b["b20"]
    b20_now = b20[last_i]
    d20 = slope(b20, last_i, 21) or 0
    comp_roc = roc(comp, 65)
    roc_now = comp_roc[last_i]
    droc = slope(comp_roc, last_i, 21) or 0

    # climax-magnitude drop inside the last 15 sessions
    recent_climax = any(
        comp[i] / comp[i - 5] - 1 <= -0.10 for i in range(max(5, last_i - 15), last_i + 1)
    )
    # RenMac's oversold zone is 2-15% above the 20-dma; a deeply washed-out
    # 50-dma reading counts too, since the two rarely bottom on the same day.
    washout = (b20_now is not None and b20_now <= 15) or (b["b50"][last_i] is not None
                                                          and b["b50"][last_i] <= 10)
    # Has the topping sequence already been confirmed? This changes what a
    # washout MEANS, so it is evaluated before any regime is assigned.
    top_confirmed = (
        s["anchor"] == "peak"
        and s["crack1_i"] is not None
        and (s["retest_i"] is not None or s["ma_break_i"] is not None)
    )

    # Gate ladder - first match wins.
    if composite <= -45 and washout and (recent_climax or cflags.get("neg_panic")):
        return ("Capitulation inside a confirmed top" if top_confirmed
                else "Capitulation / washout"), composite, coverage
    if composite <= -25 and s["post_min_i"] == last_i and (roc_now or 0) < 0 and droc < 0:
        return "Breakdown", composite, coverage
    if -25 <= composite < -5 and s["anchor"] == "trough" and s["retest_hold"] and d20 > 0:
        return "Bottoming / base", composite, coverage
    if -5 <= composite < 20 and s["thrust_i"] is not None and s["breakout_i"] is not None:
        return "Early recovery", composite, coverage
    if composite >= 50 and b20_now and b20_now > 80 and gflags["neg"] == 0:
        return "Momentum expansion", composite, coverage
    if 20 <= composite < 50 and b20_now and b20_now > 50 and (roc_now or 0) > 0 and gflags["neg"] == 0:
        return "Confirmed uptrend", composite, coverage
    # Checked late because a top can be forming while the score is still high.
    if top_confirmed or (gflags["neg"] >= 2 and d20 < 0):
        return "Late-cycle topping", composite, coverage
    if composite <= -25:
        return "Breakdown", composite, coverage
    if composite >= 20:
        return "Confirmed uptrend", composite, coverage
    return "Indeterminate", composite, coverage


# ----------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description="RenMac semiconductor regime scorer")
    ap.add_argument("--xlsx", default=bd.XLSX, help="daily-close workbook")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of a report")
    args = ap.parse_args()
    xlsx = args.xlsx if os.path.isabs(args.xlsx) else os.path.join(HERE, args.xlsx)
    if not os.path.exists(xlsx):
        sys.exit("no such file: %s" % xlsx)

    dates, n, full, partial, universe, comp, dropped = load(xlsx)
    last_i = n - 1
    comp20, comp50 = sma(comp, 20), sma(comp, 50)
    s = structure(comp, comp50, n)

    res = {}
    res["A"] = pillar_A(universe, comp, n, last_i)
    rb = pillar_B(universe, comp, comp50, n, last_i)
    res["B"], b = rb[:3], (rb[3] if len(rb) > 3 else None)
    if b is None:
        sys.exit("breadth could not be computed - check the workbook")
    rc = pillar_C(universe, full, comp, n, last_i)
    res["C"], cflags = rc[:3], (rc[3] if len(rc) > 3 else {})
    res["E"] = pillar_E(universe, comp, comp50, n, last_i)
    res["F"] = pillar_F(s, comp, dates, n, last_i)
    rg = pillar_G(universe, comp, b, n, last_i)
    res["G"], gflags = rg[:3], rg[3]
    res["H"] = pillar_H(comp, comp20, comp50, dates, n, last_i)

    scores = {k: v[0] for k, v in res.items()}
    regime, composite, coverage = classify(scores, s, b, cflags, gflags, comp, n, last_i)
    play = REGIME_PLAYBOOK[regime]

    if args.json:
        print(json.dumps({
            "file": os.path.basename(xlsx),
            "asOf": dates[last_i],
            "universe": {"full": len(full), "partial": len(partial), "dropped": dropped},
            "regime": regime,
            "composite": round(composite, 1),
            "coverage": round(coverage, 1),
            "pillars": {k: {"name": PILLAR_NAMES[k], "score": v[0], "status": v[1],
                            "weight": WEIGHTS[k], "evidence": v[2]} for k, v in res.items()},
            "playbook": play,
        }, indent=2))
        return

    w = 74
    print("=" * w)
    print("RenMac semiconductor regime score - %s" % os.path.basename(xlsx))
    print("as of %s | %d full-history + %d partial tickers" % (dates[last_i], len(full), len(partial)))
    print("=" * w)
    for k in ("A", "B", "C", "E", "F", "G", "H"):
        sc, st, ev = res[k]
        head = "%+d" % sc if sc is not None else "  -"
        print("\n[%s] %-42s %s  (weight %d)" % (k, PILLAR_NAMES[k], head, WEIGHTS[k]))
        if st != OK:
            print("     status: %s" % st)
        for line in ev:
            print("     - %s" % line)
    print("\n" + "-" * w)
    print("COMPOSITE  %+.1f / 100      (scored on %.0f%% of full pillar weight)" % (composite, coverage))
    print("REGIME     %s" % regime.upper())
    print("-" * w)
    print("exposure    : %s" % play["exposure"])
    print("tilt        : %s" % play["tilt"])
    print("confirms if : %s" % play["confirm"])
    print("invalidated : %s" % play["invalidate"])
    print("-" * w)
    print("Framework and thresholds: RENMAC_TIMING_FRAMEWORK.md")


if __name__ == "__main__":
    main()
