"""Objective measurement in, labelled conclusion out. Never touches a workbook.

Ported from renmac_score.py (the seven pillars) and build_renmac_dashboard.py (structure_series,
score_at, classify). Where they disagreed, build_renmac_dashboard wins -- each divergence was a
deliberate fix and the reason is recorded at the function.

THERE IS NO PILLAR D. Weights are A:10 B:25 C:10 E:15 F:20 G:15 H:5 = 100. Pillar D
(fundamental / earnings-cycle inflection) is deliberately unscorable: price leads EPS revisions
by roughly two quarters, so a revision trigger is structurally two quarters late at tops and
late the other way at bottoms. Its price-side substitute is the "failure on good news" test,
which lives in pillar H. Do not close this gap.

The narrative rule: every string a user reads is either (a) a measured fact formatted into a
template from config, or (b) a conclusion explicitly labelled as one. There is no template for
an external sourced claim, so one cannot be emitted. This replaces ~170 lines of hardcoded
semiconductor prose in build_dashboard.py:534-702 which, copied to another sector, would have
asserted confident falsehoods.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

import indicators as I


@dataclass
class Pillar:
    key: str
    name: str
    score: float | None
    direction: str = "neutral"          # bullish | bearish | neutral | not-testable
    status: str = "weak"                # confirmed | weak | not-confirmed | not-testable
    signals: list = field(default_factory=list)   # measured, rendered as objective
    conclusion: str = ""                          # interpreted, rendered as prose
    covered: bool = True

    def to_dict(self) -> dict:
        return {
            "key": self.key, "name": self.name, "score": self.score,
            "direction": self.direction, "status": self.status,
            "signals": self.signals, "conclusion": self.conclusion, "covered": self.covered,
        }


def _status_from_score(s):
    """Three-way chip status, in BOTH directions. Real data rarely lands cleanly on one side."""
    if s is None:
        return "not-testable", "not-testable"
    if s >= 1:
        return "confirmed", "bullish"
    if s <= -1:
        return "confirmed", "bearish"
    if s == 0:
        return "weak", "neutral"
    return "weak", "bullish" if s > 0 else "bearish"


# ---------------------------------------------------------------- structure


def structure_series(comp, comp50, n, win=252, p=None):
    """Per-index structure state read off a TRAILING window.

    Searching from an all-time anchor makes every event flag permanent: a thrust and 50-dma
    breakout from Nov-2022 stayed 'true' for four years, so the bottoming gate matched forever
    and the classifier reported early recovery in the middle of a crash. The sequence must
    describe the tape NOW.

    Topping and bottoming are the SAME algorithm mirrored -- max/min swapped, the crack/thrust
    threshold sign flipped, and 'retest stays below the high' swapped for 'retest holds above
    the low'. Resist inventing separate bottoming logic.
    """
    p = p or {}
    crack_pct = p.get("crackPct", -0.08)
    thrust_pct = p.get("thrustPct", 0.08)
    cw = p.get("crackWindow", 5)
    retest_above = p.get("retestAbovePct", 0.05)
    at_low_min = p.get("atLowMinBars", 5)
    at_low_tol = p.get("atLowTol", 1.001)

    out = [None] * n
    for i in range(n):
        lo_i = max(0, i - win + 1)
        w = [(j, comp[j]) for j in range(lo_i, i + 1) if comp[j] is not None]
        if len(w) < 30:
            continue
        peak_i, peak_v = max(w, key=lambda kv: kv[1])
        trough_i, trough_v = min(w, key=lambda kv: kv[1])
        cur = comp[i]
        if cur is None:
            continue

        # The more recent extremum owns the narrative.
        anchor = "peak" if peak_i > trough_i else "trough"

        crack_i = thrust_i = retest_i = held_i = ma_break_i = climax_i = None

        if anchor == "peak":
            for j in range(peak_i + 1, i + 1):
                k = j - cw
                if k < 0 or comp[j] is None or comp[k] in (None, 0):
                    continue
                if comp[j] / comp[k] - 1 <= crack_pct:
                    crack_i = j
                    break
            if crack_i is not None:
                post = [(j, comp[j]) for j in range(crack_i, i + 1) if comp[j] is not None]
                if post:
                    low_j, low_v = min(post, key=lambda kv: kv[1])
                    cands = [(j, comp[j]) for j in range(low_j + 1, i + 1) if comp[j] is not None]
                    if cands:
                        hi_j, hi_v = max(cands, key=lambda kv: kv[1])
                        # a real failed retest rallies off the low AND stays below the peak
                        if hi_v > low_v * (1 + retest_above) and hi_v < peak_v:
                            retest_i = hi_j
            if comp50[i] is not None and cur < comp50[i]:
                for j in range(peak_i + 1, i + 1):
                    if comp[j] is not None and comp50[j] is not None and comp[j] < comp50[j]:
                        ma_break_i = j
                        break
        else:
            for j in range(trough_i + 1, i + 1):
                k = j - cw
                if k < 0 or comp[j] is None or comp[k] in (None, 0):
                    continue
                if comp[j] / comp[k] - 1 >= thrust_pct:
                    thrust_i = j
                    break
            if thrust_i is not None:
                post = [(j, comp[j]) for j in range(thrust_i, i + 1) if comp[j] is not None]
                if post:
                    hi_j, hi_v = max(post, key=lambda kv: kv[1])
                    cands = [(j, comp[j]) for j in range(hi_j + 1, i + 1) if comp[j] is not None]
                    if cands:
                        lo_j, lo_v = min(cands, key=lambda kv: kv[1])
                        held_i = lo_j if lo_v > trough_v else None

        # worst 5-day drop in the window
        worst, worst_i = 0.0, None
        for j in range(lo_i + cw, i + 1):
            a, b = comp[j], comp[j - cw]
            if a is None or b in (None, 0):
                continue
            ch = a / b - 1
            if ch < worst:
                worst, worst_i = ch, j
        if worst <= p.get("climaxPct", -0.10):
            climax_i = worst_i

        post_peak = [comp[j] for j in range(peak_i, i + 1) if comp[j] is not None]
        at_low = bool(post_peak) and (i - peak_i) >= at_low_min and cur <= min(post_peak) * at_low_tol

        ma_up = None
        if comp50[i] is not None:
            s = I.slope(comp50, i, 10)
            ma_up = (s is not None and s > 0)

        out[i] = {
            "anchor": anchor,
            "peak_i": peak_i, "peak_v": peak_v, "trough_i": trough_i, "trough_v": trough_v,
            "crack_i": crack_i, "thrust_i": thrust_i, "retest_i": retest_i, "held_i": held_i,
            "ma_break_i": ma_break_i, "climax_i": climax_i,
            "off_peak": (cur / peak_v - 1) if peak_v else None,
            "up_from_trough": (cur / trough_v - 1) if trough_v else None,
            "at_low_since_peak": at_low,
            "ma50_rising": ma_up,
            "worst5d": worst,
            "breakout": bool(ma_up and comp50[i] is not None and cur > comp50[i] and anchor == "trough"),
        }
    return out


def top_confirmed(s) -> bool:
    """A distribution top actually formed: peak anchor + a crack + (failed retest OR 50-dma break).

    This single boolean decides whether a washout is buyable or a bull trap, so it is the most
    consequential expression in the framework.
    """
    return bool(s and s["anchor"] == "peak" and s["crack_i"] is not None
                and (s["retest_i"] is not None or s["ma_break_i"] is not None))


# ---------------------------------------------------------------- measures


def build_measures(universe, vol, comp, benches, dates, params, baskets=None, coverage=None):
    """The ~25 series every pillar reads. Config-injected; no globals."""
    n = len(dates)
    W = params["windows"]
    q = params["breadth"]["quorum"]
    yr = W["YR"]

    # A pinned price (M&A deal terms or a dead feed) reads as 'unchanged and above its MA'.
    # Keep those names out of breadth and momentum, which is where the distortion lands.
    pinned = {t for t, c in (coverage or {}).items() if c.get("pinned")}
    mom = {t: c for t, c in universe.items() if t not in pinned}

    mas = {w: {t: I.sma(c, w) for t, c in mom.items()} for w in W["MA"]}
    M = {
        "comp": comp,
        "comp20": I.sma(comp, 20),
        "comp50": I.sma(comp, 50),
        "comp200": I.sma(comp, 200),
        "b20": I.breadth(mom, mas[20], n, q),
        "b50": I.breadth(mom, mas[50], n, q),
        "b200": I.breadth(mom, mas[200], n, q),
        "x2065": I.pct_short_above_long(mom, mas[20], mas[65], n, q),
        "roc65": I.roc(comp, W["ROC"]),
        "spread": I.momentum_spread(mom, n, W["ROC"], params["stats"]["momentumSpreadMinNames"]),
        "doubled2y": I.pct_doubled(mom, n, yr, params["structure"]["bubbleDoubleYears"]),
    }
    hl65 = I.highs_minus_lows(mom, n, 65, params["stats"]["min65dBars"], q)
    M["hi65"], M["lo65"], M["hml65"] = hl65["hi"], hl65["lo"], hl65["hml"]
    hl52 = I.highs_minus_lows(mom, n, yr, int(yr * params["stats"]["min52wBars"]), q)
    M["hi52"], M["lo52"], M["hml52"] = hl52["hi"], hl52["lo"], hl52["hml"]
    M["obos"] = I.overbought_minus_oversold(mom, n, params["stochastic"]["n"],
                                            params["stochastic"]["ob"], params["stochastic"]["os"], q)

    va = params["zscore"]["volAlert"]
    alerts = I.vol_alerts(mom, n, va["window"], va["abs"], va["trailing"])
    M["volAlertPos"], M["volAlertNeg"] = alerts["pos"], alerts["neg"]

    cret = I.daily_ret(comp)
    M["sharpe"] = I.rolling_sharpe(cret, params["stats"]["rollingSharpeWin"],
                                   params["stats"]["rollingSharpeMinValid"], yr)
    M["sharpePct"] = I.expanding_pct(M["sharpe"], params["stats"]["expandingPctWarm"])
    M["spreadPct"] = I.expanding_pct(M["spread"], params["stats"]["expandingPctWarm"])

    # beta spread: top vs bottom quintile by beta to the composite
    betas = {}
    minp = params["stats"]["betaMinPairs"]["native5y"]
    for t, c in mom.items():
        b = I.beta(I.daily_ret(c), cret, minp)
        if b is not None:
            betas[t] = b
    M["_betas"] = betas
    if len(betas) >= 10:
        ranked = sorted(betas, key=lambda t: betas[t])
        k = max(params["stats"]["betaBasketQuintileMin"], len(ranked) // 5)
        lo_b, hi_b = ranked[:k], ranked[-k:]
        M["_hiBeta"], M["_loBeta"] = hi_b, lo_b
        hi_c = I.ew([mom[t] for t in hi_b], n)
        lo_c = I.ew([mom[t] for t in lo_b], n)
        M["betaSpread"] = [None if a is None or b in (None, 0) else a / b * 100
                           for a, b in zip(hi_c, lo_c)]
    else:
        M["_hiBeta"], M["_loBeta"] = [], []
        M["betaSpread"] = [None] * n
    M["betaPct"] = I.expanding_pct(M["betaSpread"], params["stats"]["expandingPctWarm"])

    # volume aggregates: full-coverage names only, so a mid-window entrant reads as composition
    # change rather than a surge in activity
    fullt = [t for t, c in (coverage or {}).items() if c.get("cls") == "full" and t in universe]
    tv = [None] * n
    for i in range(n):
        s = [vol[t][i] for t in fullt if vol.get(t) and vol[t][i] is not None]
        tv[i] = sum(s) if s else None
    M["totVol"] = tv
    M["totVol50"] = I.sma(tv, 50)
    M["upDownVol"] = I.up_down_vol({t: universe[t] for t in fullt}, vol, n,
                                   params["volume"]["upDownVolWindow"])
    da = I.dist_accum_days(comp, tv, n, params["volume"]["distAccumWindow"],
                           params["volume"]["distAccumThreshold"])
    M["distDays"], M["accumDays"] = da["dist"], da["accum"]

    ob = [None] * n
    cum = 0.0
    for i in range(1, n):
        if comp[i] is None or comp[i - 1] is None or tv[i] is None:
            continue
        cum += tv[i] if comp[i] > comp[i - 1] else (-tv[i] if comp[i] < comp[i - 1] else 0)
        ob[i] = cum / 1e6
    M["obv"] = ob

    cm = I.macd(comp, params["macd"]["fast"], params["macd"]["slow"], params["macd"]["signal"])
    M["macdLine"], M["macdSignal"], M["macdHist"] = cm["line"], cm["signal"], cm["hist"]
    M["rsi"] = I.rsi(comp, params["rsi"]["n"])

    # sub-baskets and their relative performance -- rotation is what dates the cycle
    M["baskets"] = {}
    if baskets:
        for name, members in (baskets.get("baskets") or {}).items():
            cols = [universe[t] for t in members if t in universe]
            if len(cols) < baskets.get("minMembers", 3):
                M["baskets"][name] = {"n": len(cols), "comp": None, "rel": None, "scored": False,
                                      "note": f"n={len(cols)} member(s) present, below the "
                                              f"{baskets.get('minMembers', 3)}-name minimum"}
                continue
            bc = I.ew(cols, n)
            rel = [None if a is None or b in (None, 0) else a / b * 100 for a, b in zip(bc, comp)]
            M["baskets"][name] = {
                "n": len(cols), "comp": bc, "rel": rel,
                "scored": name in (baskets.get("scored") or []),
                "roc65": I.roc(bc, W["ROC"]),
            }

    # bellwether concentration proxy for leadership breadth
    M["bellRel"] = [None] * n
    return M


def add_bellwether_relative(M, universe, bellwethers, comp, n):
    cols = [universe[t] for t in bellwethers if t in universe]
    if len(cols) >= 3:
        bc = I.ew(cols, n)
        M["bellRel"] = [None if a is None or b in (None, 0) else a / b * 100 for a, b in zip(bc, comp)]
    return M


# ---------------------------------------------------------------- pillars

def _fmt(x, d=1, suffix=""):
    return "n/a" if x is None else f"{x:.{d}f}{suffix}"


def pillar_A(M, i, p, vocab):
    """Positioning & extension. Sizes the book; it does not direct it.

    Rule 4 in code: an extension LEVEL at an extreme scores nothing. Only a gauge that is
    extreme AND rolling over scores negative. Penalising the level pinned this pillar at -2 for
    years, which is exactly the false signal the framework warns about.
    """
    bp, sp = M["betaPct"][i], M["sharpePct"][i]
    bslope = I.slope(M["betaPct"], i, p["stats"]["slopeLookbacks"]["breadth"])
    sig = [f"high/low-beta spread percentile {_fmt(bp, 0)}",
           f"21-session change {_fmt(bslope, 1, ' pts')}",
           f"rolling 3y Sharpe percentile {_fmt(sp, 0)}"]
    if bp is None:
        return Pillar("A", "Positioning & extension", None, "not-testable", "not-testable", sig,
                      "Insufficient history to measure extension.", covered=False)

    rising = (bslope or 0) > 0
    if bp >= 90:
        score, concl = (-1, "Extension is at an extreme but still rising — a long fuse. Stay long, sized.") \
            if rising else (-2, "Extension is at an extreme and contracting — the mean-reversion setup.")
    elif bp >= 70:
        score, concl = (0, "Extension is elevated and still rising.") if rising else \
            (-1, "Extension is elevated and rolling over.")
    elif bp <= 20:
        score, concl = (2, "Beta is reviving from a washed-out base — the early-recovery signature.") \
            if rising else (-1, "Beta is dead and getting deader; risk appetite is still contracting.")
    else:
        score, concl = (1, "Extension is mid-range with beta improving — not exhaustive.") if rising else \
            (0, "Extension is mid-range and drifting.")

    if sp is not None:
        sslope = I.slope(M["sharpePct"], i, p["stats"]["slopeLookbacks"]["breadth"])
        if sp >= 90 and (sslope or 0) < 0:
            score -= 1
            sig.append("Sharpe percentile >=90 and rolling over")
        elif sp <= 15 and (sslope or 0) > 0:
            score += 1
            sig.append("Sharpe percentile <=15 and turning up")

    d2 = M["doubled2y"][i]
    if d2 is not None:
        sig.append(f"{_fmt(d2, 0, '%')} of {vocab['memberNoun']} doubled within two years")
        if d2 >= 25 and (I.slope(M["doubled2y"], i, 21) or 0) < 0:
            score -= 1
            sig.append("the doubled cohort is shrinking — the bubble signal is deflating")

    score = max(-2, min(2, score))
    st, dr = _status_from_score(score)
    return Pillar("A", "Positioning & extension", score, dr, st, sig, concl)


def pillar_B(M, i, p, vocab):
    """Breadth, trend & relative strength. Weight 25 -- the primary read. Direction over level."""
    b20, b50, b200 = M["b20"][i], M["b50"][i], M["b200"][i]
    x = M["x2065"][i]
    hml = M["hml65"][i]
    obos = M["obos"][i]
    sl = I.slope(M["b20"], i, p["stats"]["slopeLookbacks"]["breadth"])
    sig = [f"{_fmt(b20, 0, '%')} above the 20-dma", f"{_fmt(b50, 0, '%')} above the 50-dma",
           f"{_fmt(b200, 0, '%')} above the 200-dma",
           f"{_fmt(x, 0, '%')} with a 20-dma above their 65-dma",
           f"65-day highs minus lows {_fmt(hml, 1, ' pts')}",
           f"overbought minus oversold {_fmt(obos, 0, ' pts')}",
           f"21-session breadth change {_fmt(sl, 1, ' pts')}"]
    if b20 is None:
        return Pillar("B", "Breadth, trend & relative strength", None, "not-testable",
                      "not-testable", sig, "Breadth quorum not met.", covered=False)

    score = I.band(b20, p["breadth"]["bands"])
    if b50 is not None and b50 < 25:
        score = min(score, -1)
    if x is not None and b50 is not None and x > 65 and b50 > 55:
        score = max(score, 1)
    if hml is not None:
        score += 1 if hml > 10 else (-1 if hml < -10 else 0)
    if sl is not None:
        score += 1 if sl > 20 else (-1 if sl < -20 else 0)

    udv = M["upDownVol"][i]
    if udv is not None:
        score += 1 if udv > 1.4 else (-1 if udv < 0.75 else 0)
        sig.append(f"up/down volume {_fmt(udv, 2)}")
    dd, ad = M["distDays"][i], M["accumDays"][i]
    if dd is not None and ad is not None:
        sig.append(f"{dd} distribution vs {ad} accumulation days")
        if dd >= 6 and dd > ad:
            score -= 1

    score = max(-2, min(2, score))
    zone = p["breadth"]["oversoldZonePct"]
    if b20 < zone[0] or b20 <= zone[1]:
        base = f"Breadth is inside the {zone[0]}-{zone[1]}% oversold zone"
        concl = base + (", and rising out of it — the thrust that starts new legs."
                        if (sl or 0) > 0 else ", and stuck there — distribution, not a bottom.")
    elif b20 >= 80:
        concl = ("Breadth above 80% and still expanding — momentum expansion."
                 if (sl or 0) > 0 else "Breadth above 80% and rolling over — the first warning.")
    else:
        concl = (f"Breadth is mid-range and improving." if (sl or 0) > 0
                 else "Breadth is mid-range and deteriorating.")
    st, dr = _status_from_score(score)
    return Pillar("B", "Breadth, trend & relative strength", score, dr, st, sig, concl)


def pillar_C(M, i, p, vocab):
    """Sentiment & crowding. A seller's panic scores ZERO, not bullish.

    A crash is raw material for a base, not a base. It matters only through the capitulation
    gate, and then only when no confirmed top precedes it.
    """
    pos, neg = M["volAlertPos"][i], M["volAlertNeg"][i]
    bell = M["bellRel"][i]
    bslope = I.slope(M["bellRel"], i, p["stats"]["slopeLookbacks"]["leadership"])
    sp = M["spreadPct"][i]
    sig = [f"{_fmt(pos, 0, '%')} of {vocab['memberNoun']} firing positive volatility alerts",
           f"{_fmt(neg, 0, '%')} firing negative alerts",
           f"bellwether-vs-equal-weight 65-session change {_fmt(bslope, 1, ' pts')}",
           f"momentum-spread percentile {_fmt(sp, 0)}"]
    if pos is None:
        return Pillar("C", "Sentiment & crowding", None, "not-testable", "not-testable", sig,
                      "No volatility-alert coverage.", covered=False)

    score = 0
    bits = []
    if pos >= 20 and (neg or 0) < 10:
        score += 1
        bits.append("a buyer's panic, which associates with escape velocity rather than tops")
    if neg is not None and neg >= 20:
        bits.append("a seller's panic, which marks a low being made but not that it will hold")
    if bslope is not None:
        if bslope > 2:
            score -= 1
            bits.append("leadership is narrowing into the bellwethers")
        elif bslope < -2:
            score += 1
            bits.append("leadership is broadening")
    if sp is not None and sp >= 85 and (I.slope(M["spreadPct"], i, 21) or 0) < 0:
        score -= 1
        bits.append("a crowded momentum cohort is starting to unwind")

    score = max(-2, min(2, score))
    st, dr = _status_from_score(score)
    concl = ("Crowding and sentiment read: " + "; ".join(bits) + ".") if bits else \
        "Nothing extreme in crowding or sentiment."
    return Pillar("C", "Sentiment & crowding", score, dr, st, sig, concl)


def pillar_E(M, i, p, vocab):
    """Cycle position from sub-basket ROTATION, not absolute performance.

    Absolute tells you what happened; relative tells you what is being rotated into, and
    rotation is what dates the cycle. In a broad drawdown every basket falls and the only usable
    information is which falls least. A 65-day ROC can read positive well into a drawdown.
    """
    baskets = M.get("baskets") or {}
    scored = {k: v for k, v in baskets.items() if v.get("scored") and v.get("rel")}
    sig = []
    for k, v in baskets.items():
        if not v.get("rel"):
            sig.append(f"{k}: {v.get('note', 'not scored')}")
        else:
            r = v["rel"][i]
            base = 100.0
            sig.append(f"{k} ({v['n']} names) relative {_fmt((r - base) if r else None, 1, ' pts')}")
    if not scored:
        return Pillar("E", "Cycle position", None, "not-testable", "not-testable", sig,
                      "No sub-basket has enough members to score.", covered=False)

    rels = {k: (v["rel"][i] - 100.0) for k, v in scored.items() if v["rel"][i] is not None}
    if not rels:
        return Pillar("E", "Cycle position", None, "not-testable", "not-testable", sig,
                      "Sub-basket relatives unavailable at this date.", covered=False)

    lead = vocab.get("leadGroup", "")
    lead_key = next((k for k in rels if k.lower().startswith(lead.split("/")[0].lower()[:4])), None)
    narrowing = vocab.get("narrowingGroup", "")
    narrow_key = next((k for k in rels if k.lower().startswith(narrowing.split("/")[0].lower()[:4])), None)

    c50 = M["comp50"][i]
    tape_down = (c50 is not None and M["comp"][i] is not None and M["comp"][i] < c50
                 and (I.slope(M["comp50"], i, 21) or 0) < 0)
    leader = max(rels, key=lambda k: rels[k])
    npos = sum(1 for v in rels.values() if v > 0)

    if tape_down:
        lv = rels.get(lead_key) if lead_key else None
        if lv is not None and lv > 5:
            score = 1
            concl = f"{lead_key} is outperforming into a weak tape — the first constructive tell at a bottom."
        elif lv is not None and lv < -2:
            score = -2
            concl = f"{lead_key} is lagging into a weak tape — the cycle is rolling over, not turning up."
        else:
            score = -1
            concl = "The tape is down and no basket is leading it out yet."
    elif npos == len(rels) and lead_key and leader in (lead_key, vocab.get("confirmGroup")):
        score = 2
        concl = f"Every scored basket is positive and {leader} is leading — a broad, durable advance."
    elif npos >= len(rels) - 1:
        if narrow_key and leader == narrow_key:
            score = 0
            concl = f"{leader} is leading while the rest lag — watch for narrowing."
        else:
            score = 1
            concl = f"Most baskets are positive with {leader} leading."
    elif npos <= 1:
        score = -2
        concl = "Only one basket is holding up — the cycle has split."
    else:
        score = -1
        concl = "The cycle is splitting; leadership is not confirming."

    st, dr = _status_from_score(score)
    return Pillar("E", "Cycle position", score, dr, st, sig, concl)


def pillar_F(M, i, p, S, dates, vocab):
    """Structure. Weight 20 -- this is what dates the turn."""
    s = S[i]
    if not s:
        return Pillar("F", "Structure", None, "not-testable", "not-testable", [],
                      "Insufficient trailing window to read structure.", covered=False)
    sig = [f"trailing-{p['windows']['STRUCT_WIN']}-session anchor: {s['anchor']}",
           f"peak {dates[s['peak_i']]} at {s['peak_v']:.1f}",
           f"trough {dates[s['trough_i']]} at {s['trough_v']:.1f}",
           f"{_fmt((s['off_peak'] or 0) * 100, 1, '%')} from the peak",
           f"{_fmt((s['up_from_trough'] or 0) * 100, 1, '%')} above the trough"]
    score = 0
    bits = []
    if s["anchor"] == "peak":
        if s["crack_i"] is not None:
            score -= 1
            sig.append(f"first crack {dates[s['crack_i']]}")
            bits.append("a first crack has printed")
        if s["retest_i"] is not None:
            score -= 1
            sig.append(f"failed retest {dates[s['retest_i']]}")
            bits.append("the retest failed at a lower high")
        if s["ma_break_i"] is not None:
            sig.append(f"50-dma break {dates[s['ma_break_i']]}")
            bits.append("the 50-dma has broken")
        if s["at_low_since_peak"]:
            score -= 1
            bits.append("it is closing at the post-peak low")
    else:
        if s["thrust_i"] is not None:
            score += 1
            sig.append(f"thrust {dates[s['thrust_i']]}")
            bits.append("a thrust off the low has printed")
        if s["held_i"] is not None:
            score += 1
            sig.append(f"retest held {dates[s['held_i']]}")
            bits.append("the retest held above the trough")
        if s["breakout"]:
            score += 1
            bits.append("it has broken out above a rising 50-dma")
    if s["climax_i"] is not None:
        sig.append(f"worst 5-day drop {_fmt(s['worst5d'] * 100, 1, '%')} into {dates[s['climax_i']]}")

    score = max(-2, min(2, score))
    st, dr = _status_from_score(score)
    seq = "topping" if s["anchor"] == "peak" else "bottoming"
    concl = (f"The {seq} sequence is live: " + "; ".join(bits) + ".") if bits else \
        f"The {seq} anchor is set but no sequence step has triggered — the trend is simply continuing."
    return Pillar("F", "Structure", score, dr, st, sig, concl)


def pillar_G(M, i, p, S, vocab):
    """Divergences. The early-warning layer. Count them -- one is noise, two is a regime signal."""
    s = S[i]
    comp, b20, roc65 = M["comp"][i], M["b20"][i], M["roc65"][i]
    sig, neg, pos = [], 0, 0
    if s and comp is not None:
        near_high = comp >= s["peak_v"] * 0.97
        near_low = comp <= s["trough_v"] * 1.03
        bslope = I.slope(M["b20"], i, p["stats"]["slopeLookbacks"]["breadth"])
        sig.append(f"composite {_fmt((s['off_peak'] or 0) * 100, 1, '%')} from its window peak")
        sig.append(f"21-session breadth change {_fmt(bslope, 1, ' pts')}")
        if near_high and bslope is not None and bslope < -10:
            neg += 1
            sig.append("price near its high on materially deteriorating breadth")
        if near_low and bslope is not None and bslope > 10:
            pos += 1
            sig.append("price near its low on improving breadth")
        if roc65 is not None and roc65 > 0 and bslope is not None and bslope < -20:
            neg += 1
            sig.append("positive 65-day momentum while breadth collapses — a shrinking group "
                       "holding the index up")
        if roc65 is not None and roc65 < 0 and bslope is not None and bslope > 20:
            pos += 1
            sig.append("negative momentum while breadth improves — accumulation under the surface")
        lo, hi = M["lo65"][i], M["hi65"][i]
        if lo is not None and hi is not None:
            sig.append(f"65-day highs {_fmt(hi, 1, '%')} vs lows {_fmt(lo, 1, '%')}")
            if roc65 is not None and roc65 > 0 and lo > hi:
                neg += 1
                sig.append("new lows expanding while the composite advances — distribution")
            if roc65 is not None and roc65 < 0 and hi > lo:
                pos += 1
                sig.append("new highs expanding while the composite declines — accumulation")

    score = max(-2, min(2, pos - neg))
    st, dr = _status_from_score(score)
    if neg >= 2:
        concl = f"{neg} active negative divergences with breadth deteriorating — a regime signal. Reduce incrementally; do not reverse."
    elif neg == 1:
        concl = "One negative divergence. Narrow leadership is a condition, not a trigger — never act on it alone."
    elif pos >= 2:
        concl = f"{pos} active positive divergences — accumulation under a weak surface."
    elif pos == 1:
        concl = "One positive divergence; not yet corroborated."
    else:
        concl = "No active divergences."
    return Pillar("G", "Divergences", score, dr, st, sig or ["no divergence inputs available"], concl)


def pillar_H(M, i, p, dates, vocab):
    """Catalyst, risk & confirmation. Weight 5. NEVER initiate on this pillar.

    Carries pillar D's price-side substitute: the failure-on-good-news test.
    """
    c20, c50 = M["comp20"][i], M["comp50"][i]
    sig = []
    score = 0
    if c20 is not None and c50 is not None:
        up = c20 > c50
        score = 1 if up else -1
        sig.append(f"20-dma is {'above' if up else 'below'} the 50-dma")
    lo = max(1, i - p["windows"]["STRUCT_WIN"] + 1)
    crosses = 0
    for j in range(lo + 1, i + 1):
        a1, a2 = M["comp20"][j], M["comp50"][j]
        b1, b2 = M["comp20"][j - 1], M["comp50"][j - 1]
        if None in (a1, a2, b1, b2):
            continue
        if (a1 > a2) != (b1 > b2):
            crosses += 1
    sig.append(f"{crosses} 20/50-dma crosses in the trailing window")

    # failure on good news: the best up-day of the last 60 sessions, checked 10 sessions later
    comp = M["comp"]
    best_j, best_r = None, 0.0
    for j in range(max(1, i - 59), i + 1):
        if comp[j] is None or comp[j - 1] in (None, 0):
            continue
        r = comp[j] / comp[j - 1] - 1
        if r > best_r:
            best_r, best_j = r, j
    if best_j is not None and i - best_j >= 3:
        k = min(best_j + 10, i)
        start = comp[best_j - 1]
        if start and comp[k] is not None:
            held = comp[k] > start
            sig.append(f"best up-day {dates[best_j]} (+{best_r*100:.1f}%); "
                       f"{'still above' if held else 'fully retraced below'} its starting level "
                       f"{k - best_j} sessions later")
            if held and score > 0:
                score += 1
            elif not held:
                score -= 1

    if crosses >= p["structure"]["whipsawCrosses"] and score > 0:
        score = 0
        sig.append("whipsaw neutraliser active — the trend system's signal is treated as noise")

    score = max(-2, min(2, score))
    st, dr = _status_from_score(score)
    concl = ("The trend system and the news test agree." if abs(score) >= 2 else
             "Confirmation is mixed; this pillar raises or lowers conviction, it never initiates.")
    return Pillar("H", "Catalyst & confirmation", score, dr, st, sig, concl)


# ---------------------------------------------------------------- scoring


def score_at(M, S, i, params, vocab, dates):
    """Evaluate all seven pillars and combine.

    Missing pillars are DROPPED and the remaining weights RENORMALISED -- never zeroed. A
    zeroed pillar silently votes 'neutral'; a dropped one is honestly absent, and the printed
    coverage percentage says so.
    """
    ps = [
        pillar_A(M, i, params, vocab),
        pillar_B(M, i, params, vocab),
        pillar_C(M, i, params, vocab),
        pillar_E(M, i, params, vocab),
        pillar_F(M, i, params, S, dates, vocab),
        pillar_G(M, i, params, S, vocab),
        pillar_H(M, i, params, dates, vocab),
    ]
    W = {k: v for k, v in params["weights"].items() if isinstance(v, (int, float))}
    tot = sum(W[p.key] for p in ps if p.score is not None)
    num = sum(p.score * W[p.key] for p in ps if p.score is not None)
    score = (num / (2 * tot) * 100) if tot else None
    coverage = 100.0 * tot / sum(W.values())
    return {"pillars": ps, "score": score, "coveragePct": round(coverage, 1)}


def classify(M, S, i, score, params):
    """The regime ladder. Evaluated IN ORDER; FIRST MATCH WINS.

    Score bands alone are insufficient: capitulation and breakdown both score deeply negative,
    and a top can form while the score is still high. Every rung therefore carries a structural
    gate. Late-cycle topping is checked LAST precisely because it can fire at a high composite
    score -- a pure band lookup would have classified April 2026 as momentum expansion.
    """
    s = S[i]
    if score is None or not s:
        return "Indeterminate"

    b20, b50 = M["b20"][i], M["b50"][i]
    roc = M["roc65"][i]
    neg_panic = (M["volAlertNeg"][i] or 0) >= 20
    off_peak = s["off_peak"]
    near_high = off_peak is not None and off_peak > params["structure"]["nearHighOffPeak"]
    bslope = I.slope(M["b20"], i, params["stats"]["slopeLookbacks"]["breadth"])

    # count active negative divergences the same way pillar G does
    neg_div = 0
    comp = M["comp"][i]
    if comp is not None:
        if comp >= s["peak_v"] * 0.97 and bslope is not None and bslope < -10:
            neg_div += 1
        if roc is not None and roc > 0 and bslope is not None and bslope < -20:
            neg_div += 1
        lo, hi = M["lo65"][i], M["hi65"][i]
        if lo is not None and hi is not None and roc is not None and roc > 0 and lo > hi:
            neg_div += 1

    washed = (b20 is not None and b20 <= 15) or (b50 is not None and b50 <= 10)
    climax_recent = s["climax_i"] is not None and (i - s["climax_i"]) <= params["structure"]["climaxLookback"]

    # 1 capitulation -- splits on whether a distribution top preceded it
    if score <= -45 and washed and (climax_recent or neg_panic):
        return "Capitulation inside a confirmed top" if top_confirmed(s) else "Capitulation / washout"
    # 2 breakdown
    if score <= -25 and s["at_low_since_peak"] and roc is not None and roc < 0 \
            and (I.slope(M["roc65"], i, 21) or 0) < 0:
        return "Breakdown"
    # 3 bottoming
    if -25 < score <= -5 and s["anchor"] == "trough" and s["held_i"] is not None \
            and (bslope or 0) > 0:
        return "Bottoming / base"
    # 4 early recovery -- requires the trough to be the LIVE anchor, else a stale thrust matches
    #   in the middle of a decline
    if -5 < score <= 20 and s["anchor"] == "trough" and s["thrust_i"] is not None and s["breakout"]:
        return "Early recovery"
    # 5 momentum expansion
    if score >= 50 and b20 is not None and b20 > 80 and neg_div == 0 and near_high:
        return "Momentum expansion"
    # 6 confirmed uptrend -- neg <= 1, not neg == 0. One divergence is noise, and demanding zero
    #   left healthy advances with a single narrowing tell falling through to 'indeterminate'.
    if 20 <= score < 50 and b20 is not None and b20 > 50 and roc is not None and roc > 0 \
            and neg_div <= 1 and near_high:
        return "Confirmed uptrend"
    # 7 late-cycle topping -- LAST, because it can fire at a high score
    if (s["anchor"] == "peak" and s["crack_i"] is not None
            and (s["retest_i"] is not None or s["ma_break_i"] is not None)):
        return "Late-cycle topping"
    if neg_div >= 2 and (bslope or 0) < 0:
        return "Late-cycle topping"
    # fall-throughs
    if score <= -25:
        return "Breakdown"
    if score >= 20 and near_high:
        return "Confirmed uptrend"
    return "Indeterminate"


def debounce_labels(raw, warmup, dwell=10):
    """Debounce the LABEL, never the score.

    Stacking a score average on top of hysteresis cost about four weeks of lag and reported
    'indeterminate' straight through a break. The structural gates are already persistent;
    smooth the label only.

    And debounce by MAJORITY over the dissent window, not by consecutive days of one candidate:
    when the raw signal alternates between two adjacent bearish regimes neither ever accumulates,
    and the held regime sticks through a crash.
    """
    out = [None] * len(raw)
    held, dissent = None, []
    for i in range(len(raw)):
        r = raw[i]
        if i < warmup or r is None:
            out[i] = None
            continue
        if r == held:
            dissent = []
        else:
            dissent.append(r)
            if len(dissent) >= dwell:
                held = Counter(dissent).most_common(1)[0][0]
                dissent = []
        out[i] = held or r
    return out


def compress_runs(labels, dates):
    runs = []
    for i, lab in enumerate(labels):
        if lab is None:
            continue
        if runs and runs[-1]["label"] == lab:
            runs[-1]["end"] = dates[i]
            runs[-1]["endIdx"] = i
        else:
            runs.append({"label": lab, "start": dates[i], "end": dates[i],
                         "startIdx": i, "endIdx": i})
    return runs


# ---------------------------------------------------------------- events & playbook


def detect_events(M, S, dates, params, vocab, universe_label):
    """Emit only what the engine measured, formatted through config templates.

    There is deliberately no template for an external sourced claim, so the engine cannot assert
    one. This is what makes the same code safe to run on four different universes.
    """
    tpl = params["interpretation"]["eventTemplates"]
    n = len(dates)
    last = n - 1
    s = S[last]
    ev = []

    def emit(kind, idx, **facts):
        t = tpl.get(kind)
        if not t or idx is None:
            return
        facts.setdefault("universeLabel", universe_label)
        facts.setdefault("date", dates[idx])
        try:
            ev.append({"i": idx, "date": dates[idx], "kind": t["kind"],
                       "title": t["title"].format(**facts), "detail": t["detail"].format(**facts)})
        except (KeyError, IndexError):
            pass

    if not s:
        return ev
    emit("peak", s["peak_i"], value=f"{s['peak_v']:.1f}", offPeak=f"{(s['off_peak'] or 0)*100:.1f}")
    emit("trough", s["trough_i"], value=f"{s['trough_v']:.1f}",
         upFromTrough=f"{(s['up_from_trough'] or 0)*100:.1f}")

    cw = params["structure"]["crackWindow"]
    if s["crack_i"] is not None:
        j = s["crack_i"]
        pct = (M["comp"][j] / M["comp"][j - cw] - 1) * 100 if M["comp"][j - cw] else 0
        emit("crack", j, pct=f"{pct:.1f}", threshold=f"{abs(params['structure']['crackPct'])*100:.0f}")
    if s["thrust_i"] is not None:
        j = s["thrust_i"]
        pct = (M["comp"][j] / M["comp"][j - cw] - 1) * 100 if M["comp"][j - cw] else 0
        emit("thrust", j, pct=f"{pct:.1f}", b20=f"{M['b20'][j] or 0:.0f}")
    if s["retest_i"] is not None:
        j = s["retest_i"]
        post = [(k, M["comp"][k]) for k in range(s["crack_i"] or 0, j) if M["comp"][k] is not None]
        low_k, low_v = min(post, key=lambda kv: kv[1]) if post else (j, M["comp"][j])
        emit("retest", j, pct=f"{(M['comp'][j]/low_v-1)*100:.1f}", lowDate=dates[low_k],
             offPeak=f"{(M['comp'][j]/s['peak_v']-1)*100:.1f}")
    if s["ma_break_i"] is not None:
        emit("ma_break", s["ma_break_i"], ma=50, sinceDays=s["ma_break_i"] - (s["peak_i"] or 0))
    if s["climax_i"] is not None:
        j = s["climax_i"]
        emit("climax", j, pct=f"{s['worst5d']*100:.1f}", b20=f"{M['b20'][j] or 0:.0f}")

    b20 = M["b20"]
    zone = params["breadth"]["oversoldZonePct"]
    wash = next((j for j in range(n - 1, max(0, n - 253), -1)
                 if b20[j] is not None and b20[j] <= zone[1]), None)
    if wash is not None:
        emit("washout", wash, b20=f"{b20[wash]:.0f}", b50=f"{M['b50'][wash] or 0:.0f}")

    d2 = M["doubled2y"][last]
    if d2 is not None and d2 >= 25:
        tot = len([1 for _ in (M.get("_betas") or {})]) or 0
        emit("bubble", last, count=f"{d2:.0f}%", total="the universe")

    crosses = sum(1 for j in range(max(1, n - 252), n)
                  if None not in (M["comp20"][j], M["comp50"][j], M["comp20"][j-1], M["comp50"][j-1])
                  and (M["comp20"][j] > M["comp50"][j]) != (M["comp20"][j-1] > M["comp50"][j-1]))
    if crosses >= params["structure"]["whipsawCrosses"]:
        emit("whipsaw", last, crosses=crosses, window=252)

    ev.sort(key=lambda e: e["i"])
    return ev


def render_playbook(regime, params, universe_key):
    pb = params.get("regimePlaybook", {})
    shared = dict(pb.get("_shared", {}).get(regime, {}))
    uni = pb.get(universe_key, {}).get(regime, {})
    shared.update(uni)
    return shared
