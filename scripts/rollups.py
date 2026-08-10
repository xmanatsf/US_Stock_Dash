"""Sector and industry-group rollups for the market-internals tab.

Ported from build_sp100_dashboard.py (group_rollup / classify_regime / quartile_buckets) and
generalised so the level (sector, industryGroup, industry) is config.

The n>=3 rule is the important part and it is enforced HERE, server-side: a group with fewer than
three full-history members gets comp=None, regime='insufficient-sample' and a human-readable note
instead of a fabricated composite. That is the "never fabricate" rule in miniature -- the client
renders the note, it does not decide.

The group regime vocabulary is deliberately BIDIRECTIONAL. 'Positive inflection / bottoming' and
'Uptrend continuation' are first-class states, not an afterthought to a bearish read.
"""

from __future__ import annotations

import indicators as I


def classify_group_regime(comp, b20, roc65, hi65, lo65, i, params):
    """Coarse per-group regime, distinct from the 8-state RenMac ladder.

    Four inputs, exactly as the playbook's pre-narrative check prescribes: where the window
    extremum sits relative to now, the breadth trend, the ROC direction, and which of new highs
    or new lows is actually expanding. The last is usually the cleanest tell.
    """
    if comp is None or comp[i] is None:
        return "insufficient-sample", []

    win = min(i + 1, params["windows"]["STRUCT_WIN"])
    lo_i = i - win + 1
    w = [(j, comp[j]) for j in range(max(0, lo_i), i + 1) if comp[j] is not None]
    if len(w) < 30:
        return "insufficient-sample", []

    peak_i, peak_v = max(w, key=lambda kv: kv[1])
    trough_i, trough_v = min(w, key=lambda kv: kv[1])
    cur = comp[i]
    off_peak = (cur / peak_v - 1) * 100 if peak_v else None
    up_trough = (cur / trough_v - 1) * 100 if trough_v else None
    anchor = "peak" if peak_i > trough_i else "trough"

    bslope = I.slope(b20, i, 21) if b20 else None
    r = roc65[i] if roc65 else None
    rslope = I.slope(roc65, i, 21) if roc65 else None
    h, l = (hi65[i] if hi65 else None), (lo65[i] if lo65 else None)

    signals = [
        f"{off_peak:.1f}% from the {win}-session high" if off_peak is not None else "",
        f"{up_trough:.1f}% above the {win}-session low" if up_trough is not None else "",
        f"breadth 21-session change {bslope:+.1f} pts" if bslope is not None else "",
        f"65-day ROC {r:+.1f}%" if r is not None else "",
        f"new highs {h:.1f}% vs new lows {l:.1f}%" if h is not None and l is not None else "",
    ]
    signals = [s for s in signals if s]

    expanding_highs = h is not None and l is not None and h > l
    expanding_lows = h is not None and l is not None and l > h

    # "Near the high" is -5%, not -3%. At -3% a group sitting 3.2% off its high with +18% momentum
    # and 79% of members above their 20-dma fell through to "Mixed", which is not a reading anyone
    # can act on -- the same failure the main ladder fixes by relaxing its divergence gate.
    near_high = off_peak is not None and off_peak > -5
    near_low = up_trough is not None and up_trough < 5

    if anchor == "peak" and near_high:
        if (bslope or 0) < -5 or expanding_lows:
            return "Topping / deteriorating", signals
        return "Uptrend continuation", signals
    if anchor == "trough" and near_low:
        if (bslope or 0) > 5 or expanding_highs:
            return "Positive inflection / bottoming", signals
        return "Downtrend continuation", signals
    if anchor == "peak":
        if (r or 0) < 0 and (bslope or 0) < 0 and expanding_lows:
            return "Downtrend continuation", signals
        if (r or 0) < 0 and (bslope or 0) < -5:
            return "Topping / deteriorating", signals
        # momentum positive and breadth not deteriorating, but off the high: still a trend
        if (r or 0) > 0 and (bslope or 0) >= -5:
            return "Uptrend continuation", signals
    else:
        if (r or 0) > 0 and (bslope or 0) > 0 and expanding_highs:
            return "Uptrend continuation", signals
        if (bslope or 0) > 5 and (rslope or 0) > 0:
            return "Positive inflection / bottoming", signals
        if (r or 0) < 0 and (bslope or 0) < 0:
            return "Downtrend continuation", signals
    return "Mixed / no clear signal", signals


def build_group_rollups(universe, vol, coverage, mapping, dates, params, sectors_cfg, level):
    """One rollup record per group at the requested taxonomy level."""
    n = len(dates)
    last = n - 1
    cfg = sectors_cfg["rollup"]
    min_members = cfg["minMembers"]
    quorum = cfg["breadthQuorum"]
    yr = params["windows"]["YR"]

    groups: dict[str, list] = {}
    unmapped = []
    for t in universe:
        rec = mapping.get(t)
        g = (rec or {}).get(level)
        if not g:
            unmapped.append(t)
            continue
        groups.setdefault(g, []).append(t)

    out = []
    for g, members in sorted(groups.items()):
        full = [t for t in members if coverage.get(t, {}).get("cls") == "full"]
        rec = {"name": g, "level": level, "n": len(members), "nFull": len(full),
               "members": sorted(members)}
        if len(full) < min_members:
            rec.update({
                "comp": None, "regime": cfg["insufficientSampleLabel"], "signals": [],
                "note": f"{len(full)} full-history member(s), below the {min_members}-name minimum "
                        f"— no composite is computed rather than showing a fabricated one",
                "ret": None, "ret1y": None, "offHi": None, "pctAbove20": None, "atLows": None,
            })
            out.append(rec)
            continue

        cols = [universe[t] for t in full]
        comp = I.ew(cols, n)
        mas20 = {t: I.sma(universe[t], 20) for t in full}
        sub = {t: universe[t] for t in full}
        b20 = I.breadth(sub, mas20, n, min(quorum, max(3, len(full) // 2)))
        hl = I.highs_minus_lows(sub, n, 65, params["stats"]["min65dBars"],
                                min(quorum, max(3, len(full) // 2)))
        roc65 = I.roc(comp, params["windows"]["ROC"])
        regime, signals = classify_group_regime(comp, b20, roc65, hl["hi"], hl["lo"], last, params)

        hi_v = max((v for v in comp if v is not None), default=None)
        j1 = max(0, last - yr)
        above20 = [t for t in full if universe[t][last] is not None and mas20[t][last] is not None
                   and universe[t][last] > mas20[t][last]]
        rets = []
        for t in full:
            c = universe[t]
            i0 = coverage[t].get("i0") or 0
            if c[last] is not None and c[i0]:
                rets.append((t, (c[last] / c[i0] - 1) * 100))
        rets.sort(key=lambda kv: -kv[1])

        rec.update({
            "comp": [None if v is None else round(v, 2) for v in comp],
            "b20": [None if v is None else round(v, 1) for v in b20],
            "roc65": [None if v is None else round(v, 2) for v in roc65],
            "regime": regime,
            "signals": signals,
            "note": None,
            "ret": I.r1(comp[last] - 100) if comp[last] is not None else None,
            "ret1y": I.r1((comp[last] / comp[j1] - 1) * 100) if comp[j1] else None,
            "offHi": I.r1((comp[last] / hi_v - 1) * 100) if hi_v else None,
            "roc65Last": I.r1(roc65[last]),
            "b20Last": I.r1(b20[last]),
            "b20MonthAgo": I.r1(b20[max(0, last - 21)]),
            "pctAbove20": I.r1(100.0 * len(above20) / len(full)) if full else None,
            "top": [{"t": t, "ret": I.r1(r)} for t, r in rets[:cfg["topBottomN"]]],
            "bottom": [{"t": t, "ret": I.r1(r)} for t, r in rets[-cfg["topBottomN"]:][::-1]],
        })
        out.append(rec)

    out.sort(key=lambda r: (r["ret"] is None, -(r["ret"] or 0)))
    return out, unmapped


def quartile_buckets(rows, key, label, n_buckets=4):
    """Split tickers into quantile buckets by `key` and report each bucket's average return.

    Bucket edges and averages are computed here; the client only scales the diverging bar.
    """
    vals = [r for r in rows if r.get(key) is not None and r.get("ret") is not None]
    if len(vals) < n_buckets * 3:
        return []
    vals.sort(key=lambda r: r[key])
    size = len(vals) // n_buckets
    out = []
    names = ["Q1 (lowest)", "Q2", "Q3", "Q4 (highest)"]
    for b in range(n_buckets):
        lo = b * size
        hi = (b + 1) * size if b < n_buckets - 1 else len(vals)
        chunk = vals[lo:hi]
        if not chunk:
            continue
        rets = [c["ret"] for c in chunk]
        out.append({
            "bucket": names[b] if b < len(names) else f"Q{b+1}",
            "metric": label,
            "n": len(chunk),
            "lo": round(chunk[0][key], 3),
            "hi": round(chunk[-1][key], 3),
            "avgRet": round(sum(rets) / len(rets), 1),
            "tickers": [c["t"] for c in chunk][:40],
        })
    return out


def composite_split(rollups, parent_level_map):
    """Find sectors whose industry groups disagree most -- the distortion guard, generalised.

    'Check for a composite-distorting subgroup before trusting one blended number', in code and
    as a first-class UI element rather than something buried in a sortable table.
    """
    by_parent: dict[str, list] = {}
    for r in rollups:
        p = parent_level_map.get(r["name"])
        if p and r.get("ret") is not None:
            by_parent.setdefault(p, []).append(r)
    out = []
    for parent, rows in by_parent.items():
        if len(rows) < 2:
            continue
        rows = sorted(rows, key=lambda r: r["ret"])
        lo, hi = rows[0], rows[-1]
        spread = hi["ret"] - lo["ret"]
        if spread < 50:
            continue
        out.append({
            "parent": parent, "spread": round(spread, 1),
            "hiGroup": hi["name"], "hiRet": hi["ret"], "hiRegime": hi["regime"],
            "loGroup": lo["name"], "loRet": lo["ret"], "loRegime": lo["regime"],
        })
    out.sort(key=lambda r: -r["spread"])
    return out
