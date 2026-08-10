"""Indicator math. Pure functions, no I/O, no config reads, no globals.

Ported one-for-one from build_dashboard.py (primitives), build_renmac_dashboard.py (the 5-year
measures) and renmac_score.py (cross-sectional helpers). Where the three disagreed, the
build_renmac_dashboard version wins -- each of those divergences was a deliberate bug fix and
the reason is recorded at the function.

Two unit conventions that look like bugs and are not:
  * `roc()` returns PERCENT, `daily_ret()` returns a FRACTION.
  * `rolling_z` uses the SAMPLE standard deviation (n-1) and requires a FULL window.
Unifying either silently changes every z-score and every breadth threshold downstream.

Gap semantics, also deliberate and load-bearing:
  * STRICT windows (`sma`, `rolling_z`) return None unless the whole window is present.
  * TOLERANT windows (`stochastic`, 52w hi/lo, avg volume) drop Nones and apply a min count.
  * PATH indicators (`ema_from`, `rsi`) RESET their running state on any None.
  * `obv` SKIPS gaps without resetting, so the cumulative carries across.
"""

from __future__ import annotations

import math

# ---------------------------------------------------------------- rounding helpers


def r1(x):
    return None if x is None else round(x, 1)


def r2(x):
    return None if x is None else round(x, 2)


def rn(x, d):
    return None if x is None else round(x, d)


# ---------------------------------------------------------------- primitives


def sma(col, n):
    """Simple moving average. STRICT: one None in the window kills the value."""
    out = [None] * len(col)
    for i in range(n - 1, len(col)):
        w = col[i - n + 1:i + 1]
        if all(v is not None for v in w):
            out[i] = sum(w) / n
    return out


def roc(col, n):
    """n-session rate of change, in PERCENT."""
    out = [None] * len(col)
    for i in range(n, len(col)):
        if col[i] is not None and col[i - n] not in (None, 0):
            out[i] = (col[i] / col[i - n] - 1) * 100
    return out


def daily_ret(col):
    """Simple daily return as a FRACTION (not percent)."""
    out = [None] * len(col)
    for i in range(1, len(col)):
        if col[i] is not None and col[i - 1] not in (None, 0):
            out[i] = col[i] / col[i - 1] - 1
    return out


def ema_from(col, n):
    """EMA seeded with the SMA of the first n non-None values, k = 2/(n+1).

    Resets hard on any None: the run buffer clears and it re-seeds from scratch. This is why
    the MACD signal line needs 9 consecutive valid MACD values, so the first histogram value
    lands around index 35 on clean data and later after any gap.
    """
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
    ef, es = ema_from(col, fast), ema_from(col, slow)
    line = [None if a is None or b is None else a - b for a, b in zip(ef, es)]
    sig = ema_from(line, signal)
    hist = [None if a is None or b is None else a - b for a, b in zip(line, sig)]
    return {"line": line, "signal": sig, "hist": hist}


def rsi(col, n=14):
    """Wilder RSI: (avg*(n-1) + x)/n, seeded with the simple mean of the first n changes.

    NOT the 2/(n+1) smoothing used by ema_from. Resets on any None. Returns 100.0 when the
    average loss is zero, which avoids a divide-by-zero on an unbroken advance.
    """
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
            avg_g = (avg_g * (n - 1) + g) / n
            avg_l = (avg_l * (n - 1) + l) / n
        if avg_g is not None:
            out[i] = 100.0 if avg_l == 0 else 100 - 100 / (1 + avg_g / avg_l)
    return out


def obv(px, vol):
    """On-balance volume. Starts at 0.0; gaps SKIP rather than reset. Flat days add nothing."""
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
    avg = sma(vol, n)
    return [None if v is None or a in (None, 0) else v / a for v, a in zip(vol, avg)]


def rolling_z(series, window=20):
    """Trailing z-score. SAMPLE stdev (n-1). Requires a FULL window of non-None values.

    The current value is included in its own mean and stdev, matching the original.

    Implementation note: the obvious version rebuilds the window list at every index, which is
    O(n*w) with a large constant and dominated the 500-ticker build (8 calls per ticker). This
    tracks a run of consecutive non-None values and recomputes mean/variance over an explicit
    window slice only where the window is complete. Exactness is preserved -- the regression
    suite compares every z-window against the shipped dashboard at 1e-9 and still passes.
    """
    n = len(series)
    out = [None] * n
    if window < 2:
        return out
    run_start = None  # index where the current unbroken non-None run began
    s1 = s2 = None    # running sum and sum of squares over the current window
    for i in range(n):
        v = series[i]
        if v is None:
            run_start = None
            s1 = s2 = None
            continue
        if run_start is None:
            run_start = i
            s1 = s2 = None
        if i - run_start + 1 < window:
            continue
        lo = i - window + 1
        if lo == run_start or s1 is None:
            # first full window of this run: seed the running sums exactly
            w = series[lo:i + 1]
            s1 = sum(w)
            s2 = sum(x * x for x in w)
        else:
            drop = series[lo - 1]
            s1 += v - drop
            s2 += v * v - drop * drop
        mean = s1 / window
        var = (s2 - s1 * mean) / (window - 1)
        if var > 0:
            out[i] = (v - mean) / (var ** 0.5)
    return out


def stochastic(col, n=14):
    """14-day %K. TOLERANT: drops Nones, needs at least half the window."""
    out = [None] * len(col)
    for i in range(len(col)):
        if col[i] is None:
            continue
        w = [v for v in col[max(0, i - n + 1):i + 1] if v is not None]
        if len(w) < max(2, n // 2):
            continue
        lo, hi = min(w), max(w)
        if hi > lo:
            out[i] = (col[i] - lo) / (hi - lo) * 100
    return out


def slope(series, i, lookback):
    """Level change over `lookback` sessions. Used to turn every level into a direction."""
    j = i - lookback
    if j < 0 or i >= len(series):
        return None
    a, b = series[i], series[j]
    return None if a is None or b is None else a - b


def band(x, cuts):
    """Map a value onto a 5-level score (-2..+2) given 4 ascending cut points."""
    if x is None:
        return 0
    lo, mlo, mhi, hi = cuts
    if x < lo:
        return -2
    if x < mlo:
        return -1
    if x < mhi:
        return 0
    if x < hi:
        return 1
    return 2


# ---------------------------------------------------------------- composites


def ew(cols, n):
    """Daily-rebalanced equal-weight index, base 100.

    Chains the cross-sectional mean of daily returns. THIS is the composite to use -- the
    base-date version (average of prices rebased to a common start) is fine over 12 months and
    fails over five: by 2026 a name up 20x dominates an index still labelled 'equal-weight',
    which silently reintroduces the exact concentration this framework exists to detect, and it
    moved the detected composite peak by a month.

    Chaining returns also keeps late-listing tickers from jolting the index on the day they
    enter -- a name only contributes once it has two consecutive prints.
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


def ew_composite(cols, n):
    """Base-date-normalised equal weight. LEGACY-PARITY ONLY.

    Retained solely so the regression harness can reproduce the 1-year dashboard bit-for-bit.
    Never use it for a 5-year series -- see `ew`.
    """
    out = []
    for i in range(n):
        vals = [c[i] / c[0] * 100 for c in cols if c[i] is not None and c[0]]
        out.append(sum(vals) / len(vals) if vals else None)
    return out


def rel_to(px, base, first_i, n=None):
    """Price relative to a benchmark, base 100, rebased at the TICKER's own first print.

    Rebasing at the ticker's first valid date rather than the window start is what lets a late
    IPO still show a meaningful relative series from wherever its data begins.
    """
    n = n if n is not None else len(px)
    out = [None] * n
    if first_i is None or first_i >= n:
        return out
    base_px, base_b = px[first_i], base[first_i]
    if base_px in (None, 0) or base_b in (None, 0):
        return out
    for i in range(first_i, n):
        if px[i] is not None and base[i] not in (None, 0):
            out[i] = (px[i] / base_px) / (base[i] / base_b) * 100
    return out


def rel_ret(ret, bench_ret):
    """Geometric excess return, (1+r)/(1+b)-1 -- not a subtraction. Feeds zRel."""
    out = [None] * len(ret)
    for i in range(1, len(ret)):
        if ret[i] is not None and bench_ret[i] is not None and bench_ret[i] != -1:
            out[i] = (1 + ret[i]) / (1 + bench_ret[i]) - 1
    return out


# ---------------------------------------------------------------- percentiles


def pct_rank_insample(series, i, min_valid=30):
    """Whole-window percentile. IN-SAMPLE: it can see the future.

    Named explicitly so it cannot be used by accident. Valid only for an as-of-today
    cross-sectional ranking, NEVER for a historical series -- see `expanding_pct`.
    """
    if i >= len(series) or series[i] is None:
        return None
    vals = [v for v in series if v is not None]
    if len(vals) < min_valid:
        return None
    return 100.0 * sum(1 for v in vals if v <= series[i]) / len(vals)


def expanding_pct(series, warm=252):
    """Causal expanding-window percentile: at every index it uses only data up to that index.

    This is the only percentile valid inside a regime HISTORY. The in-sample version leaks
    future information into past readings and makes a backtested regime look prescient.
    """
    out = [None] * len(series)
    seen = []
    for i, v in enumerate(series):
        if v is not None:
            seen.append(v)
        if v is None or len(seen) < warm:
            continue
        out[i] = 100.0 * sum(1 for x in seen if x <= v) / len(seen)
    return out


def rolling_sharpe(rets, win=756, min_valid=0.90, ann=252):
    out = [None] * len(rets)
    for i in range(len(rets)):
        w = [v for v in rets[max(0, i - win + 1):i + 1] if v is not None]
        if len(w) < win * min_valid:
            continue
        m = sum(w) / len(w)
        var = sum((x - m) ** 2 for x in w) / (len(w) - 1) if len(w) > 1 else 0
        sd = var ** 0.5
        if sd > 0:
            out[i] = m / sd * math.sqrt(ann)
    return out


def beta(a_ret, b_ret, min_pairs=100):
    """OLS beta of a on b over paired non-None returns."""
    xs = [(x, y) for x, y in zip(a_ret, b_ret) if x is not None and y is not None]
    if len(xs) < min_pairs:
        return None
    mx = sum(p[1] for p in xs) / len(xs)
    my = sum(p[0] for p in xs) / len(xs)
    cov = sum((p[1] - mx) * (p[0] - my) for p in xs)
    var = sum((p[1] - mx) ** 2 for p in xs)
    return cov / var if var > 0 else None


def pearson(xs, ys):
    ps = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    if len(ps) < 3:
        return None
    n = len(ps)
    mx = sum(p[0] for p in ps) / n
    my = sum(p[1] for p in ps) / n
    num = sum((p[0] - mx) * (p[1] - my) for p in ps)
    dx = sum((p[0] - mx) ** 2 for p in ps) ** 0.5
    dy = sum((p[1] - my) ** 2 for p in ps) ** 0.5
    return num / (dx * dy) if dx > 0 and dy > 0 else None


# ---------------------------------------------------------------- breadth family


def breadth(universe, mas, n, quorum=25):
    """% of the universe trading above a given moving average.

    `quorum` is the minimum number of names with both a price and an MA on that bar. Prior art
    drifted 30 -> 25 undocumented; it is a config value now.
    """
    out = [None] * n
    for i in range(n):
        cnt = tot = 0
        for t, col in universe.items():
            m = mas.get(t)
            if m is None:
                continue
            p, mv = col[i], m[i]
            if p is None or mv is None:
                continue
            tot += 1
            cnt += p > mv
        if tot >= quorum:
            out[i] = 100.0 * cnt / tot
    return out


def pct_short_above_long(universe, short_mas, long_mas, n, quorum=25):
    """% of issues whose short MA is above their long MA (RenMac's 20-vs-65 measure).

    Less noisy than raw price-vs-MA because it compares two smoothed series.
    """
    out = [None] * n
    for i in range(n):
        cnt = tot = 0
        for t in universe:
            s, l = short_mas.get(t), long_mas.get(t)
            if s is None or l is None or s[i] is None or l[i] is None:
                continue
            tot += 1
            cnt += s[i] > l[i]
        if tot >= quorum:
            out[i] = 100.0 * cnt / tot
    return out


def highs_minus_lows(universe, n, win=65, min_bars=50, quorum=25):
    """New highs minus new lows over a trailing window, as % of issues.

    The playbook calls the 65-day version the cleanest single tell in the framework.
    """
    hi = [None] * n
    lo = [None] * n
    hml = [None] * n
    for i in range(n):
        h = l = tot = 0
        for t, col in universe.items():
            w = [v for v in col[max(0, i - win + 1):i + 1] if v is not None]
            if len(w) < min_bars or col[i] is None:
                continue
            tot += 1
            if col[i] >= max(w):
                h += 1
            elif col[i] <= min(w):
                l += 1
        if tot >= quorum:
            hi[i] = 100.0 * h / tot
            lo[i] = 100.0 * l / tot
            hml[i] = hi[i] - lo[i]
    return {"hi": hi, "lo": lo, "hml": hml}


def overbought_minus_oversold(universe, n, k=14, ob=80, os_=20, quorum=25):
    stos = {t: stochastic(col, k) for t, col in universe.items()}
    out = [None] * n
    for i in range(n):
        o = u = tot = 0
        for t in universe:
            v = stos[t][i]
            if v is None:
                continue
            tot += 1
            if v >= ob:
                o += 1
            elif v <= os_:
                u += 1
        if tot >= quorum:
            out[i] = 100.0 * (o - u) / tot
    return out


def momentum_spread(universe, n, win=65, min_names=25):
    """Top-quintile minus bottom-quintile mean 65-day ROC. A dispersion/crowding gauge."""
    rocs = {t: roc(col, win) for t, col in universe.items()}
    out = [None] * n
    for i in range(win, n):
        xs = sorted(v for t in universe if (v := rocs[t][i]) is not None)
        if len(xs) < min_names:
            continue
        q = len(xs) // 5
        if q == 0:
            continue
        out[i] = sum(xs[-q:]) / q - sum(xs[:q]) / q
    return out


def pct_doubled(universe, n, yr=252, years=2):
    """% of the universe that doubled inside `years` -- RenMac's bubble/extension flag."""
    lb = yr * years
    out = [None] * n
    for i in range(n):
        c = tot = 0
        for col in universe.values():
            j = i - lb
            if j < 0 or col[i] is None or col[j] in (None, 0):
                continue
            tot += 1
            c += col[i] / col[j] >= 2
        if tot:
            out[i] = 100.0 * c / tot
    return out


def up_down_vol(universe, vol, n, win=20):
    """Ratio of volume on up days to volume on down days over a trailing window."""
    out = [None] * n
    up = [0.0] * n
    dn = [0.0] * n
    for t, col in universe.items():
        v = vol.get(t)
        if v is None:
            continue
        for i in range(1, n):
            if col[i] is None or col[i - 1] is None or v[i] is None:
                continue
            if col[i] > col[i - 1]:
                up[i] += v[i]
            elif col[i] < col[i - 1]:
                dn[i] += v[i]
    for i in range(n):
        a = sum(up[max(0, i - win + 1):i + 1])
        b = sum(dn[max(0, i - win + 1):i + 1])
        if b > 0:
            out[i] = a / b
    return out


def dist_accum_days(comp, tot_vol, n, win=25, thr=0.005):
    """Distribution / accumulation day counts over a trailing window.

    Distribution = a >=thr down day on higher total volume; accumulation is the mirror.
    """
    dist = [None] * n
    accum = [None] * n
    dflag = [0] * n
    aflag = [0] * n
    for i in range(1, n):
        if comp[i] is None or comp[i - 1] in (None, 0):
            continue
        if tot_vol[i] is None or tot_vol[i - 1] is None:
            continue
        chg = comp[i] / comp[i - 1] - 1
        higher = tot_vol[i] > tot_vol[i - 1]
        if chg <= -thr and higher:
            dflag[i] = 1
        elif chg >= thr and higher:
            aflag[i] = 1
    for i in range(n):
        lo = max(0, i - win + 1)
        dist[i] = sum(dflag[lo:i + 1])
        accum[i] = sum(aflag[lo:i + 1])
    return {"dist": dist, "accum": accum}


def vol_alerts(universe, n, window=65, abs_z=2.5, trailing=5):
    """Share of the universe firing an outsized-move alert, split by direction.

    >20% firing POSITIVE is a buyer's panic and is counter-intuitively bullish -- the source
    material notes these associate with escape velocity, not tops. A seller's panic is NOT
    treated as a bullish contrarian signal: a crash is raw material for a base, not a base.
    """
    zs = {t: rolling_z(daily_ret(col), window) for t, col in universe.items()}
    pos = [None] * n
    neg = [None] * n
    for i in range(n):
        p = q = tot = 0
        for t in universe:
            w = [v for v in zs[t][max(0, i - trailing + 1):i + 1] if v is not None]
            if not w:
                continue
            tot += 1
            if any(v >= abs_z for v in w):
                p += 1
            if any(v <= -abs_z for v in w):
                q += 1
        if tot:
            pos[i] = 100.0 * p / tot
            neg[i] = 100.0 * q / tot
    return {"pos": pos, "neg": neg}


# ---------------------------------------------------------------- per-ticker panel


def build_stock_panel(ticker, px, vol, benches, n, params, first_i=None):
    """Everything the per-ticker panel renders, date-aligned to the universe grid.

    `benches` maps a display name ('SPY', 'SMH', 'EW basket') to that benchmark's level series.
    Adds OBV, which the reference dashboard computed only at composite level.
    """
    z_windows = params["zscore"]["windows"]
    m = params["macd"]
    if first_i is None:
        first_i = next((i for i, v in enumerate(px) if v is not None), None)

    ret = daily_ret(px)
    out = {
        "px": px,
        "dma20": sma(px, 20),
        "dma50": sma(px, 50),
        "macd": macd(px, m["fast"], m["slow"], m["signal"]),
        "rsi": rsi(px, params["rsi"]["n"]),
        "vol": vol,
        "volAvg20": sma(vol, params["volume"]["relVolWindow"]) if vol else None,
        "obv": obv(px, vol) if vol else None,
        "rel": {},
        "zAbs": {},
        "zRel": {},
    }
    for w in z_windows:
        out["zAbs"][str(w)] = rolling_z(ret, w)

    for name, series in benches.items():
        v = rel_to(px, series, first_i, n)
        out["rel"][name] = {"v": v, "d20": sma(v, 20), "d50": sma(v, 50)}

    primary = params.get("_relZBenchmark") or next(iter(benches), None)
    if primary and primary in benches:
        rr = rel_ret(ret, daily_ret(benches[primary]))
        for w in z_windows:
            out["zRel"][str(w)] = rolling_z(rr, w)
    return out


def horizon_slice(dates, horizon, yr=252):
    """Return the start index for a named horizon. Client slices; server ships the full series."""
    n = len(dates)
    bars = {"1m": 21, "3m": 63, "6m": 126, "1y": yr, "2y": yr * 2, "3y": yr * 3, "5y": yr * 5}
    b = bars.get(horizon)
    return 0 if b is None else max(0, n - b)
