# -*- coding: utf-8 -*-
"""Build the US Semi 'Anatomy of a Chip Top' dashboard.

Reads the daily-close + volume workbook, computes RenMac-framework metrics
plus MACD/RSI/volume/benchmark technicals, and injects the resulting JSON
into dashboard_template.html to produce the standalone
US_Semi_Chip_Top_Dashboard.html. Rerun after refreshing the xlsx.

Sources from the 5-yr "Price" and "Volume" sheets (see
build_renmac_dashboard.py), trimmed to the most recent ~1yr trading-day
window: this dashboard's equal-weight composite (rebased to the window's
first row) drifts away from equal-weight over multi-year spans, so it stays
on a 1yr window rather than the full 5yr history (see
build_renmac_dashboard.py's daily-rebalanced index for the multi-year-safe
version).

SMH and SPY ride along as benchmark columns in the same Price/Volume sheets
(BENCHMARKS set below) - excluded from the semiconductor universe/composite/
breadth/etc., used only for absolute and relative-strength comparison.
"""
import json
import math
import os
import sys

import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
XLSX = os.path.join(HERE, "US semi stocks 5y price and volume 20260807.xlsx")
TEMPLATE = os.path.join(HERE, "dashboard_template.html")
OUT = os.path.join(HERE, "US_Semi_Chip_Top_Dashboard.html")

BELLWETHERS = {"NVDA", "AVGO", "AMD", "MU", "AMAT", "LRCX", "KLAC", "TXN", "MRVL", "INTC"}
BENCHMARKS = {"SMH", "SPY"}
WINDOW = 252  # ~1yr of trading days, kept from the tail of the 5yr file


def num(v):
    """CapIQ writes 'NA'/'NM' as literal strings into otherwise-numeric columns."""
    return v if isinstance(v, (int, float)) else None


def load_prices():
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)

    def grab(name):
        # Row 0 is the ticker header. It (and a "Day Close Price"/"Volume"
        # sub-header row directly beneath it) both carry None in column A, so
        # take row 0 unconditionally as the header and only filter *data* rows
        # on a non-None first cell - filtering before splitting off the header
        # would drop the header itself along with the sub-header row.
        rows = list(wb[name].iter_rows(values_only=True))
        return rows[0], [r for r in rows[1:] if r[0] is not None]

    phdr, prows = grab("Price")
    vhdr, vrows = grab("Volume")
    # Join Volume to Price by date, not row position - a vendor-side range
    # mismatch would otherwise shift every volume reading against the wrong close.
    vby = {r[0]: r for r in vrows}
    prows = [r for r in prows if r[0] in vby]
    vrows = [vby[r[0]] for r in prows]

    # Drop non-trading rows: weekends, plus any weekday where essentially the
    # whole universe repeats the prior row's price AND volume (a market holiday
    # forward-filled by the vendor). Same detection as build_renmac_dashboard.py.
    keep = []
    for i in range(len(prows)):
        if prows[i][0].weekday() >= 5:
            continue
        if i > 0:
            same = tot = 0
            for j in range(1, len(phdr)):
                a, b = num(prows[i][j]), num(prows[i - 1][j])
                c, d = num(vrows[i][j]), num(vrows[i - 1][j])
                if a is None or b is None:
                    continue
                tot += 1
                same += a == b and c == d
            if tot and same / tot > 0.95:
                continue
        keep.append(i)
    keep = keep[-WINDOW:]

    dates = [prows[i][0].strftime("%Y-%m-%d") for i in keep]
    series, vol, empty, bench = {}, {}, [], {}
    for j, t in enumerate(phdr[1:], 1):
        t = str(t)
        col = [num(prows[i][j]) for i in keep]
        vcol = [num(vrows[i][j]) for i in keep]
        if not any(v is not None for v in col):
            empty.append(t)
        elif t in BENCHMARKS:
            bench[t] = ffill_small_gaps(col)
        else:
            series[t] = col
            vol[t] = vcol
    return dates, series, vol, bench, empty


def ffill_small_gaps(col, max_gap=3):
    out = list(col)
    run = 0
    for i in range(len(out)):
        if out[i] is None:
            run += 1
            if 0 < run <= max_gap and i - run >= 0 and out[i - run] is not None:
                out[i] = out[i - run]
        else:
            run = 0
    return out


def sma(col, n):
    out = [None] * len(col)
    for i in range(n - 1, len(col)):
        w = col[i - n + 1 : i + 1]
        if all(v is not None for v in w):
            out[i] = sum(w) / n
    return out


def roc(col, n):
    out = [None] * len(col)
    for i in range(n, len(col)):
        if col[i] is not None and col[i - n] not in (None, 0):
            out[i] = (col[i] / col[i - n] - 1) * 100
    return out


def daily_ret(col):
    out = [None] * len(col)
    for i in range(1, len(col)):
        if col[i] is not None and col[i - 1] not in (None, 0):
            out[i] = col[i] / col[i - 1] - 1
    return out


def ema_from(col, n):
    """EMA of col, span n. Seeded with the SMA of the first full window; restarts
    (reseeds with SMA) after any None gap rather than carrying a stale average
    across missing data."""
    out = [None] * len(col)
    k = 2 / (n + 1)
    val = None
    run = []
    for i, v in enumerate(col):
        if v is None:
            val = None
            run = []
            continue
        if val is None:
            run.append(v)
            if len(run) >= n:
                val = sum(run) / n
                out[i] = val
        else:
            val = v * k + val * (1 - k)
            out[i] = val
    return out


def macd(col, fast=12, slow=26, signal=9):
    """Returns (macd_line, signal_line, histogram) using EMA(fast)-EMA(slow), and
    EMA(signal) of the macd line."""
    ema_fast, ema_slow = ema_from(col, fast), ema_from(col, slow)
    macd_line = [None if a is None or b is None else a - b for a, b in zip(ema_fast, ema_slow)]
    signal_line = ema_from(macd_line, signal)
    hist = [None if a is None or b is None else a - b for a, b in zip(macd_line, signal_line)]
    return macd_line, signal_line, hist


def rsi(col, n=14):
    """Wilder's RSI. Restarts its running average after any None gap."""
    out = [None] * len(col)
    avg_g = avg_l = prev = None
    gains, losses = [], []
    for i, v in enumerate(col):
        if v is None:
            avg_g = avg_l = prev = None
            gains, losses = [], []
            continue
        if prev is None:
            prev = v
            continue
        chg = v - prev
        prev = v
        g, l = max(chg, 0.0), max(-chg, 0.0)
        if avg_g is None:
            gains.append(g)
            losses.append(l)
            if len(gains) >= n:
                avg_g, avg_l = sum(gains) / n, sum(losses) / n
        else:
            avg_g, avg_l = (avg_g * (n - 1) + g) / n, (avg_l * (n - 1) + l) / n
        if avg_g is not None:
            out[i] = 100.0 if avg_l == 0 else 100 - 100 / (1 + avg_g / avg_l)
    return out


def obv(px, vol):
    """On-balance volume: cumulative volume signed by the day's price direction."""
    out = [None] * len(px)
    cum = 0.0
    for i in range(len(px)):
        if px[i] is None or vol[i] is None:
            continue
        if i > 0 and px[i - 1] is not None:
            if px[i] > px[i - 1]:
                cum += vol[i]
            elif px[i] < px[i - 1]:
                cum -= vol[i]
        out[i] = cum
    return out


def rel_vol(vol, n=20):
    """Today's volume vs its trailing n-session average."""
    avg = sma(vol, n)
    return [None if v is None or a in (None, 0) else v / a for v, a in zip(vol, avg)]


def up_down_vol(universe, vol, n=20):
    """Universe-wide up/down volume ratio over n sessions."""
    length = len(next(iter(universe.values())))
    upv, dnv = [0.0] * length, [0.0] * length
    for t in universe:
        p, v = universe[t], vol.get(t)
        if not v:
            continue
        for i in range(1, length):
            if p[i] is None or p[i - 1] is None or v[i] is None:
                continue
            if p[i] > p[i - 1]:
                upv[i] += v[i]
            elif p[i] < p[i - 1]:
                dnv[i] += v[i]
    out = [None] * length
    for i in range(n, length):
        u, d = sum(upv[i - n + 1 : i + 1]), sum(dnv[i - n + 1 : i + 1])
        if d > 0:
            out[i] = u / d
    return out


def dist_accum_days(comp, tot_vol, win=25):
    """Distribution vs accumulation day counts on the composite over `win` sessions."""
    n = len(comp)
    dist, accum = [None] * n, [None] * n
    for i in range(win, n):
        d = a = 0
        for k in range(i - win + 1, i + 1):
            if comp[k] is None or comp[k - 1] is None or tot_vol[k] is None or tot_vol[k - 1] is None:
                continue
            chg = comp[k] / comp[k - 1] - 1
            if chg <= -0.005 and tot_vol[k] > tot_vol[k - 1]:
                d += 1
            elif chg >= 0.005 and tot_vol[k] > tot_vol[k - 1]:
                a += 1
        dist[i], accum[i] = d, a
    return dist, accum


def rolling_z(series, window=20):
    """z-score of series[i] vs the trailing `window` values (requires a full window)."""
    out = [None] * len(series)
    for i in range(len(series)):
        if series[i] is None:
            continue
        w = [v for v in series[max(0, i - window + 1) : i + 1] if v is not None]
        if len(w) < window:
            continue
        mean = sum(w) / len(w)
        var = sum((x - mean) ** 2 for x in w) / (len(w) - 1)
        sd = var ** 0.5
        if sd > 0:
            out[i] = (series[i] - mean) / sd
    return out


Z_WINDOWS = [21, 40, 50, 70]


def build_stock_panel(universe, vol, mas20, mas50, comp, bench, n):
    """Per-ticker series for the individual-stock panel: absolute price + 20/50-dma,
    price relative to a chosen benchmark (EW basket / SMH / SPY, base 100) + 20/50-dma,
    rolling z-scores of daily returns (absolute and vs the basket) across Z_WINDOWS,
    MACD(12,26,9) and RSI(14) on price, and volume with its 20-session average."""
    comp_ret = daily_ret(comp)

    def rel_to(px, base, first_i):
        out = [None] * n
        base_px, base_b = px[first_i], base[first_i]
        if base_b in (None, 0):
            return out
        for i in range(first_i, n):
            if px[i] is not None and base[i] not in (None, 0):
                out[i] = (px[i] / base_px) / (base[i] / base_b) * 100
        return out

    panel = {}
    for t, px in universe.items():
        first_i = next((i for i in range(n) if px[i] is not None), None)
        if first_i is None:
            continue
        rel = rel_to(px, comp, first_i)
        ret = daily_ret(px)
        rel_ret = [None] * n
        for i in range(1, n):
            if ret[i] is not None and comp_ret[i] is not None:
                rel_ret[i] = (1 + ret[i]) / (1 + comp_ret[i]) - 1

        rel_by_bench = {"EW basket": {
            "v": [r2(v) for v in rel],
            "d20": [r2(v) for v in sma(rel, 20)],
            "d50": [r2(v) for v in sma(rel, 50)],
        }}
        for bt, bcol in bench.items():
            br = rel_to(px, bcol, first_i)
            rel_by_bench[bt] = {
                "v": [r2(v) for v in br],
                "d20": [r2(v) for v in sma(br, 20)],
                "d50": [r2(v) for v in sma(br, 50)],
            }

        ml, sl, hi = macd(px)
        vcol = vol.get(t)
        panel[t] = {
            "px": [r2(v) for v in px],
            "dma20": [r2(v) for v in mas20[t]],
            "dma50": [r2(v) for v in mas50[t]],
            "rel": rel_by_bench,
            "macd": {"line": [r2(v) for v in ml], "signal": [r2(v) for v in sl],
                     "hist": [r2(v) for v in hi]},
            "rsi": [r2(v) for v in rsi(px)],
            "vol": None if not vcol else [None if v is None else round(v) for v in vcol],
            "volAvg20": None if not vcol else [r2(v) for v in sma(vcol, 20)],
            "zAbs": {str(w): [r2(v) for v in rolling_z(ret, w)] for w in Z_WINDOWS},
            "zRel": {str(w): [r2(v) for v in rolling_z(rel_ret, w)] for w in Z_WINDOWS},
        }
    return panel


def r1(x):
    return None if x is None else round(x, 1)


def r2(x):
    return None if x is None else round(x, 2)


def main():
    dates, raw, vol, bench, dropped = load_prices()
    n = len(dates)

    # ticker classification
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

    # ---- equal-weight composite (full-history tickers only) ----
    comp = []
    for i in range(n):
        vals = [full[t][i] / full[t][0] * 100 for t in full if full[t][i] is not None]
        comp.append(sum(vals) / len(vals))
    comp50 = sma(comp, 50)
    comp20 = sma(comp, 20)
    comp_roc65 = roc(comp, 65)

    peak_i = comp.index(max(comp))
    post_min_i = min(range(peak_i, n), key=lambda i: comp[i])

    # first crack: first 5-day drop of >=8% after the peak
    crack1_i = next(
        (
            i
            for i in range(peak_i + 1, n)
            if comp[i] / comp[max(peak_i, i - 5)] - 1 <= -0.08
        ),
        None,
    )

    # failed retest (lower high): highest close after the first crack
    retest_i = crack1_low_i = None
    if crack1_i is not None and crack1_i < n - 1:
        cand = max(range(crack1_i, n), key=lambda i: comp[i])
        lo = min(range(peak_i, cand + 1), key=lambda i: comp[i])
        if comp[cand] > comp[lo] * 1.05 and cand > crack1_i:
            retest_i, crack1_low_i = cand, lo
    if crack1_low_i is None and crack1_i is not None:
        crack1_low_i = min(range(peak_i, crack1_i + 1), key=lambda i: comp[i])

    # climax: worst 5-day drop after the retest (or after the peak)
    start = retest_i if retest_i is not None else peak_i
    climax_i, climax_chg = None, 0.0
    for i in range(start + 5, n):
        chg = comp[i] / comp[i - 5] - 1
        if chg < climax_chg:
            climax_i, climax_chg = i, chg

    # best oversold bounce after the climax
    bounce_i = None
    if climax_i is not None and climax_i < n - 1:
        bounce_i = max(range(climax_i, n), key=lambda i: comp[i])

    # first close below the 50-dma after the peak
    ma_break_i = next(
        (i for i in range(peak_i, n) if comp50[i] is not None and comp[i] < comp50[i]),
        None,
    )

    # ---- breadth: % above 20/50-dma ----
    mas20 = {t: sma(universe[t], 20) for t in universe}
    mas50 = {t: sma(universe[t], 50) for t in universe}

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
                out[i] = 100 * cnt / tot
        return out

    b20, b50 = breadth(mas20), breadth(mas50)
    stock_panel = build_stock_panel(universe, vol, mas20, mas50, comp, bench, n)
    b20_valid = [(i, v) for i, v in enumerate(b20) if v is not None]
    b20_min_pre = min((x for x in b20_valid if x[0] < peak_i), key=lambda x: x[1])
    b20_min_post = min((x for x in b20_valid if x[0] >= peak_i), key=lambda x: x[1])

    # ---- momentum quintile spread (top - bottom quintile mean 65d ROC) ----
    rocs = {t: roc(universe[t], 65) for t in universe}
    spread = [None] * n
    for i in range(65, n):
        xs = sorted(rocs[t][i] for t in universe if rocs[t][i] is not None)
        if len(xs) < 25:
            continue
        q = len(xs) // 5
        spread[i] = sum(xs[-q:]) / q - sum(xs[:q]) / q
    spread_valid = [(i, v) for i, v in enumerate(spread) if v is not None]
    spread_max = max(spread_valid, key=lambda x: x[1])

    # ---- new-low expansion ----
    # period lows (expanding window, the 52-wk-low proxy) + 3-month (63d) lows
    newlows = [None] * n
    lows63 = [None] * n
    for i in range(60, n):
        lo = lo63 = 0
        for t in universe:
            col = universe[t]
            if col[i] is None:
                continue
            w = [v for v in col[: i + 1] if v is not None]
            if len(w) < 60:
                continue
            lo += col[i] <= min(w)
            w63 = [v for v in col[max(0, i - 62) : i + 1] if v is not None]
            lo63 += col[i] <= min(w63)
        newlows[i], lows63[i] = lo, lo63

    # ---- volume-based technical metrics (new with this workbook) ----
    tot_vol = [None] * n
    for i in range(n):
        s = [vol[t][i] for t in full if vol.get(t) and vol[t][i] is not None]
        tot_vol[i] = sum(s) if s else None
    tot_vol50 = sma(tot_vol, 50)
    up_down = up_down_vol(universe, vol, 20)
    dist_days, accum_days = dist_accum_days(comp, tot_vol, 25)
    comp_obv = obv(comp, tot_vol)

    # ---- composite momentum indicators ----
    comp_macd_line, comp_macd_signal, comp_macd_hist = macd(comp)
    comp_rsi = rsi(comp)

    # ---- benchmark comparison: SMH / SPY, rebased to 100 at the window start ----
    bench_rebased = {}
    for bt, bcol in bench.items():
        base = bcol[0]
        bench_rebased[bt] = [None if v is None or base in (None, 0) else v / base * 100 for v in bcol]
    bench_rel = {
        bt: [None if comp[i] is None or brc[i] in (None, 0) else comp[i] / brc[i] * 100 for i in range(n)]
        for bt, brc in bench_rebased.items()
    }

    # ---- per-stock table ----
    stocks = []
    doubled = []
    for t in sorted(universe):
        col = universe[t]
        first_i = next(i for i in range(n) if col[i] is not None)
        last_i = max(i for i in range(n) if col[i] is not None)
        last = col[last_i]
        valid = [(i, v) for i, v in enumerate(col) if v is not None]
        hi_i, hi_v = max(valid, key=lambda x: x[1])
        ret = (last / col[first_i] - 1) * 100
        is_doubled = t in full and last / col[first_i] >= 2
        if is_doubled:
            doubled.append(t)
        at_low = last <= min(v for _, v in valid) * 1.001 and len(valid) >= 60
        vv = [v for v in (vol.get(t) or [])[max(0, last_i - 19) : last_i + 1] if v is not None]
        avg_vol20 = sum(vv) / len(vv) if vv else None
        last_vol = (vol.get(t) or [None] * n)[last_i]
        stocks.append(
            {
                "t": t,
                "px": r2(last),
                "ret": r1(ret),
                "offHi": r1((last / hi_v - 1) * 100),
                "hiDate": dates[hi_i],
                "dSinceHi": last_i - hi_i,
                "a20": None if mas20[t][last_i] is None else col[last_i] > mas20[t][last_i],
                "a50": None if mas50[t][last_i] is None else col[last_i] > mas50[t][last_i],
                "roc": r1(rocs[t][last_i]),
                "dbl": is_doubled,
                "low": bool(at_low),
                "bell": t in BELLWETHERS,
                "part": t in partial,
                "avgVol": r1(avg_vol20 / 1e6) if avg_vol20 else None,
                "relVol": r2(last_vol / avg_vol20) if last_vol is not None and avg_vol20 else None,
            }
        )

    # ---- inflection events ----
    def ev(i, title, detail, kind):
        return {"date": dates[i], "i": i, "title": title, "detail": detail, "kind": kind}

    events = [
        ev(
            b20_min_pre[0],
            "Mid-cycle breadth washout — the dip that got bought",
            f"Only {b20_min_pre[1]:.0f}% of stocks above their 20-dma — an oversold flush "
            "inside the uptrend. The dip was bought and the advance resumed: bull-market "
            "behavior, and the template FOMO buyers extrapolated into 2026.",
            "info",
        ),
        ev(
            peak_i,
            "Composite peak — the structural top",
            f"Equal-weight composite tops at {comp[peak_i]:.0f} (+{comp[peak_i]-100:.0f}% in "
            "10 months), inside RenMac's 3–6-month topping window after the April bubble "
            "signal fired.",
            "critical",
        ),
    ]
    if crack1_i is not None:
        events.append(
            ev(
                crack1_i,
                "First crack — parabolic trend broken",
                f"Sudden {(comp[crack1_i]/comp[max(peak_i, crack1_i-5)]-1)*100:.0f}% drop in a "
                f"week, taking the composite {(comp[crack1_low_i]/comp[peak_i]-1)*100:.0f}% "
                "off the peak. RenMac's 'shot across the bow' — structural momentum is damaged.",
                "serious",
            )
        )
    if retest_i is not None:
        events.append(
            ev(
                retest_i,
                "Failed retest — the lower high",
                f"Oversold bounce recovers to {comp[retest_i]:.0f}, stalling "
                f"{abs((comp[retest_i]/comp[peak_i]-1)*100):.1f}% below the May high before "
                "rolling over. The right side of the topping pattern begins: good news "
                "(Samsung blowout, hyperscaler capex) no longer lifts prices.",
                "serious",
            )
        )
    if ma_break_i is not None:
        events.append(
            ev(
                ma_break_i,
                "50-dma breakdown",
                "First close below the 50-day moving average since the peak — trend support "
                "gives way and trapped overhead supply starts capping every rally.",
                "serious",
            )
        )
    if climax_i is not None:
        climax_detail = (
            f"Worst 5-day drop of the period: {climax_chg*100:.1f}% in a week as the "
            "momentum trade liquidates. Breadth collapses into RenMac's 2–15% oversold zone."
        )
        # a bounce right on the heels of the climax is a dead cat, not a shoulder
        if bounce_i is not None and bounce_i - climax_i <= 5:
            climax_detail += (
                f" The reflex bounce to {comp[bounce_i]:.0f} on {dates[bounce_i]} "
                f"({(comp[bounce_i]/comp[peak_i]-1)*100:.0f}% below the peak) fades within days."
            )
        events.append(ev(climax_i, "Climax of the unwind", climax_detail, "critical"))
    if bounce_i is not None and post_min_i > bounce_i and bounce_i - climax_i > 5:
        events.append(
            ev(
                bounce_i,
                "Right-shoulder bounce fails",
                f"Best post-climax rally reaches only {comp[bounce_i]:.0f} "
                f"({(comp[bounce_i]/comp[peak_i]-1)*100:.0f}% below the peak) and fades — "
                "the failed right shoulder of the head-and-shoulders top.",
                "serious",
            )
        )
    events.append(
        ev(
            b20_min_post[0],
            "Post-peak breadth washout",
            f"Breadth hits {b20_min_post[1]:.0f}% above the 20-dma. Unlike November's washout, "
            "these oversold readings are producing bounces that fail — distribution, not "
            "accumulation.",
            "serious",
        )
    )
    events.append(
        ev(
            post_min_i,
            "Closing at the lows",
            f"Composite ends the period at {comp[post_min_i]:.0f}, "
            f"{(comp[post_min_i]/comp[peak_i]-1)*100:.0f}% off the peak — no support level "
            "has held yet, and new-low expansion says distribution continues beneath the surface.",
            "critical",
        )
    )
    events.sort(key=lambda e: e["i"])

    # ---- pillar scorecard ----
    last_i = n - 1
    lows63_now = lows63[last_i] or 0
    roc_max = max(v for v in comp_roc65 if v is not None)
    topping_bits = [f"Peak {dates[peak_i]}"]
    if crack1_i is not None:
        topping_bits.append(
            f"first crack ({(comp[crack1_low_i]/comp[peak_i]-1)*100:.0f}% by "
            f"{dates[crack1_low_i]})"
        )
    if retest_i is not None:
        topping_bits.append(
            f"failed retest {abs((comp[retest_i]/comp[peak_i]-1)*100):.1f}% under the high "
            f"({dates[retest_i]})"
        )
    if climax_i is not None:
        topping_bits.append(f"{climax_chg*100:.0f}% climax week ({dates[climax_i]})")
    topping_bits.append(
        f"period ends at the post-peak low, {(comp[last_i]/comp[peak_i]-1)*100:.0f}% off"
        if post_min_i == last_i
        else f"now {(comp[last_i]/comp[peak_i]-1)*100:.0f}% off the peak"
    )
    pillars = [
        {
            "name": "1 · Bubble signal",
            "status": "confirmed",
            "headline": f"{len(doubled)} of {len(full)} stocks doubled in 12 months",
            "detail": "RenMac's rule is a double within TWO years; "
            f"{len(doubled)} names ({len(doubled)/len(full)*100:.0f}% of the full-history "
            "universe) cleared it in just one — a stricter screen than the rule itself.",
        },
        {
            "name": "2 · Topping structure",
            "status": "confirmed",
            "headline": "Peak → crack → lower high → new lows: full sequence present",
            "detail": " → ".join(topping_bits) + ". The multi-phase unwind RenMac "
            "describes is fully in place through the failed right shoulder.",
        },
        {
            "name": "3 · Momentum unwind",
            "status": "confirmed",
            "headline": f"65-day ROC {comp_roc65[last_i]:+.0f}% (was {roc_max:+.0f}% at the extreme)",
            "detail": f"Composite 65d ROC has swung {roc_max - comp_roc65[last_i]:.0f} pts off "
            f"its high. The top-minus-bottom momentum-quintile spread hit {spread_max[1]:.0f} "
            f"pts on {dates[spread_max[0]]} and has collapsed to {spread[last_i]:.0f} pts — "
            "high-momentum leaders are unwinding fastest (RenMac flagged an 84% momentum-"
            "spread extreme before the break).",
        },
        {
            "name": "4 · Breadth & new lows",
            "status": "confirmed",
            "headline": f"{b20[last_i]:.0f}% above 20-dma · {lows63_now} stocks at 3-mo lows",
            "detail": f"Breadth sits inside the 2–15% oversold zone while {lows63_now} of "
            f"{len(universe)} names close at 3-month lows — new-low expansion during "
            "weakness is the distribution signature RenMac watches. (True 52-wk lows are "
            "unmeasurable with 1 year of data; most stocks bottomed at the window start.)",
        },
        {
            "name": "5 · Sentiment / flows",
            "status": "not-testable",
            "headline": f"Fund-flow sentiment still qualitative — up/down volume "
            f"{r2(up_down[last_i]) if up_down[last_i] is not None else '–'} is the closest proxy",
            "detail": "RenMac: SMH inflows in the 90th percentile despite drawdowns; Samsung blowout "
            "earnings and hyperscaler capex failed to lift prices — that flow/sentiment claim itself "
            "is still unverifiable from this file. What volume now adds is a partial proxy: the "
            f"universe-wide up/down volume ratio and {dist_days[last_i] or 0} distribution vs "
            f"{accum_days[last_i] or 0} accumulation days (25d) — see the Volume section below.",
        },
    ]

    verdict = {
        "peakDate": dates[peak_i],
        "peakVal": r1(comp[peak_i]),
        "lastVal": r1(comp[last_i]),
        "lastDate": dates[last_i],
        "drawdown": r1((comp[last_i] / comp[peak_i] - 1) * 100),
        "ret12m": r1(comp[last_i] - 100),
        "atLow": post_min_i == last_i,
    }

    def slim(series):
        return [r2(v) for v in series]

    data = {
        "dates": dates,
        "comp": slim(comp),
        "comp50": slim(comp50),
        "b20": slim(b20),
        "b50": slim(b50),
        "roc65": slim(comp_roc65),
        "spread": slim(spread),
        "newlows": newlows,
        "lows63": lows63,
        "events": events,
        "pillars": pillars,
        "verdict": verdict,
        "stocks": stocks,
        "doubled": doubled,
        "stockPanel": {
            "tickers": sorted(stock_panel),
            "bellwethers": sorted(BELLWETHERS & set(stock_panel)),
            "series": stock_panel,
            "zWindows": Z_WINDOWS,
        },
        "compMacd": {"line": slim(comp_macd_line), "signal": slim(comp_macd_signal), "hist": slim(comp_macd_hist)},
        "compRsi": slim(comp_rsi),
        "totVol": [None if v is None else round(v / 1e6, 1) for v in tot_vol],
        "totVol50": [None if v is None else round(v / 1e6, 1) for v in tot_vol50],
        "upDownVol": slim(up_down),
        "distDays": dist_days,
        "accumDays": accum_days,
        "obv": [None if v is None else round(v / 1e6, 1) for v in comp_obv],
        "bench": {bt: slim(c) for bt, c in bench_rebased.items()},
        "benchRel": {bt: slim(c) for bt, c in bench_rel.items()},
        "meta": {
            "nFull": len(full),
            "nPartial": len(partial),
            "dropped": dropped,
            "partial": sorted(partial),
            "built": dates[last_i],
            "benchmarks": sorted(bench),
        },
    }

    with open(TEMPLATE, encoding="utf-8") as f:
        html = f.read()
    marker = "/*__DATA__*/"
    if marker not in html:
        sys.exit("marker not found in template")
    html = html.replace(marker, "const DATA = " + json.dumps(data, separators=(",", ":")) + ";")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"OK -> {OUT}")
    print(f"  universe: {len(full)} full + {len(partial)} partial, dropped {dropped}")
    print(f"  peak {verdict['peakDate']} @ {verdict['peakVal']} | last {verdict['lastVal']} ({verdict['drawdown']}% off peak)")
    print(f"  breadth20 last {b20[last_i]:.0f}% | spread max {spread_max[1]:.0f} on {dates[spread_max[0]]} -> now {spread[last_i]:.0f}")
    print(f"  doubled: {len(doubled)} | 3-mo lows today: {lows63_now} | period lows today: {newlows[last_i]}")
    print(f"  events: {[(e['date'], e['title']) for e in events]}")
    print(f"  benchmarks: {sorted(bench)} | up/down vol {up_down[last_i]} | dist/accum days {dist_days[last_i]}/{accum_days[last_i]}")
    print(f"  composite RSI(14) {comp_rsi[last_i]} | MACD hist {comp_macd_hist[last_i]}")


if __name__ == "__main__":
    main()
