"""The shared build spine. Every tab runs through this exact function.

That is the point: `build_hw_networking.py` is structurally identical to `build_semis.py` and
differs only by a config key. The validation-banner path is ONE branch in shared code, so a tab
whose workbook fails validation still emits a payload describing why, and a tab whose workbook
is clean lights up with no code change.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil

import indicators as I
import interpretation as T
import loaders as L
import rollups as R
import validators as V


# ---------------------------------------------------------------- helpers


def slim(series, d=2):
    return [None if v is None else round(v, d) for v in series]


def _version(source_name: str, payload_bits: list) -> str:
    stamp = "".join(ch for ch in source_name if ch.isdigit())[-8:] or "00000000"
    h = hashlib.sha1("".join(payload_bits).encode()).hexdigest()[:7]
    return f"{stamp}-{h}"


def envelope(universe_key, label, status, report, dates, built_at, version, source, **rest):
    out = {
        "schemaVersion": 1,
        "universe": universe_key,
        "label": label,
        "status": status,
        "builtAt": built_at,
        "version": version,
        "source": source,
        "validation": report.to_dict() if report else {"findings": []},
        "dates": dates,
    }
    out.update(rest)
    return out


# ---------------------------------------------------------------- benchmarks


def build_benchmarks(cfg, books) -> dict:
    """Extract SPY/SMH ONCE, from the configured source universe, before any tab build.

    Doing this per-tab would invite four subtly different date grids. One extraction makes the
    cross-workbook alignment structural rather than lucky.
    """
    bs = cfg.universes["benchmarkSource"]
    book = books[bs["universe"]][0]
    series = {}
    for t in bs["tickers"]:
        if t in book.px:
            series[t] = slim(book.px[t], 4)
    # Sector ETFs that exist in only one workbook (XBI in biotech, XLV in pharma). Same rule as
    # the primary source: joined only when the trading grid is IDENTICAL, never date-matched
    # loosely -- a differing grid is reported and the series left out, not realigned.
    sources, skipped = {os.path.basename(book.path): list(series)}, []
    for ex in bs.get("extra", []):
        if ex["universe"] not in books:
            continue
        xb = books[ex["universe"]][0]
        if xb.dates != book.dates:
            skipped.append({"universe": ex["universe"], "tickers": ex["tickers"],
                            "reason": "trading grid differs from the primary benchmark source"})
            continue
        got = [t for t in ex["tickers"] if t in xb.px and t not in series]
        for t in got:
            series[t] = slim(xb.px[t], 4)
        sources[os.path.basename(xb.path)] = got
    return {"schemaVersion": 1, "dates": book.dates, "series": series,
            "source": os.path.basename(book.path), "sources": sources, "skipped": skipped}


# ---------------------------------------------------------------- main build


def build_universe_payload(cfg, key, books, benchmarks, built_at, mapping=None):
    """Load -> validate -> measure -> interpret -> emit. Returns (payload, shards, report)."""
    u = cfg.universe(key)
    par = cfg.parameters
    label = u["label"]
    book, load_findings, path = books[key]
    source = os.path.basename(path)

    rep = V.Report(key)
    rep.add(load_findings)
    exp = par["calendar"]["expected"]
    rep.add(V.check_date_grid(book.dates, exp.get("tradingDays"), exp.get("lastDate")))
    for other in u.get("crossCheckAgainst", []):
        if other in books and books[other][0].dates:
            rep.add(V.cross_workbook_identity(book, books[other][0], key, other))

    skip = set(u.get("excludeFromUniverse", [])) | {e["ticker"] for e in u.get("excludeTickers", [])}
    flat = V.scan_flatlines(book.px, book.vol, book.dates,
                            tickers=[t for t in book.tickers if t not in skip])
    rep.add(flat)
    pinned = next((list(f.tickers) for f in flat if f.code == "TERMINAL_FLATLINE"), [])

    universe, coverage, cov_f = V.build_universe(
        book, par, exclude=u.get("excludeFromUniverse", []),
        exclude_tickers=u.get("excludeTickers", []), pinned=pinned)
    rep.add(cov_f)
    rep.add(V.scan_gaps(universe))
    rep.add(V.check_extreme_returns(universe))

    sb = cfg.sub_baskets(key)
    if sb:
        rep.add(V.check_basket_membership(sb.get("baskets"), universe.keys()))

    version = _version(source, [source, str(len(book.dates)), str(sorted(universe))])

    # THE Tab-4 mechanism: one branch, in shared code.
    if rep.status != "ok":
        return envelope(key, label, "validation_failed", rep, book.dates, built_at, version,
                        source, tickers=sorted(universe)), {}, rep

    n = len(book.dates)
    par = dict(par)

    # benchmark levels, RAW -- the client rebases per selected horizon. Rebasing server-side
    # would hardcode one horizon and make the 1-month view meaningless.
    bench_series = {}
    for b in u.get("benchmarks", []):
        if b in benchmarks["series"]:
            bench_series[b] = [None if v is None else float(v) for v in benchmarks["series"][b]]

    full_t = [t for t, c in coverage.items() if c.get("cls") == "full" and t in universe]
    comp = I.ew([universe[t] for t in full_t], n)
    bench_series["EW basket"] = comp

    # split composites (software's crypto sleeve): never ship one blended number
    splits = {}
    for sp in u.get("splits", []):
        members = set((sb or {}).get("baskets", {}).get(sp["basket"], []))
        inc = [t for t in full_t if t in members]
        exc = [t for t in full_t if t not in members]
        if len(inc) >= 3 and len(exc) >= 3:
            # `members` counts only FULL-history names, because that is what the composite is
            # built from -- the same rule the universe composite uses. State both counts so a
            # basket of 10 showing a 6-name composite is explicit rather than a silent mismatch.
            partial_members = sorted(m for m in members if m in universe and m not in set(inc))
            splits[sp["id"]] = {
                "label": sp["label"], "badge": sp.get("badge"),
                "members": sorted(inc),
                "memberCount": len(inc),
                "basketCount": len([m for m in members if m in universe]),
                "partialExcluded": partial_members,
                "comp": slim(I.ew([universe[t] for t in inc], n), 2),
                "compEx": slim(I.ew([universe[t] for t in exc], n), 2),
                "exCount": len(exc),
                "note": sp.get("note", ""),
            }
            if "EW ex-crypto" in u.get("benchmarks", []):
                bench_series["EW ex-crypto"] = I.ew([universe[t] for t in exc], n)

    vocab = par["vocabulary"][u["narrative"]["vocabulary"]]

    # Sector / industry-group rollups (market internals). Built BEFORE build_measures so the
    # sector composites can serve as this universe's sub-baskets -- the spec's point is that
    # market internals has no static basket list, its baskets ARE the GICS groups. Without this
    # pillar E is dropped and the read runs on 85% of the pillar weight.
    rollup_payload, sector_baskets = {}, None
    if mapping and u.get("sectorMap"):
        levels = cfg.sectors.get("levels", ["sector", "industryGroup"])
        for lvl in levels:
            if lvl == "industry":
                continue
            rows, unmapped = R.build_group_rollups(
                universe, book.vol, coverage, mapping, book.dates, par, cfg.sectors, lvl)
            rollup_payload[lvl] = rows
            if unmapped:
                rep.add([V.Finding("UNMAPPED_IN_ROLLUP", "warn",
                                   f"{len(unmapped)} ticker(s) have no {lvl} and are excluded "
                                   f"from that rollup", tickers=sorted(unmapped),
                                   count=len(unmapped))])
        sec_rows = rollup_payload.get("sector") or []
        scored = [r["name"] for r in sec_rows if r.get("comp")]
        if len(scored) >= 3:
            sector_baskets = {
                "baskets": {r["name"]: r["members"] for r in sec_rows if r.get("comp")},
                "scored": scored,
                "cycleBaskets": scored,
                "minMembers": cfg.sectors["rollup"]["minMembers"],
            }
            sb = sector_baskets

    M = T.build_measures(universe, book.vol, comp, bench_series, book.dates, par, sb, coverage)
    M = T.add_bellwether_relative(M, universe, u.get("bellwethers", []), comp, n)
    S = T.structure_series(comp, M["comp50"], n, par["windows"]["STRUCT_WIN"], par["structure"])

    warm = par["windows"]["WARMUP"]
    raw_reg, scores = [None] * n, [None] * n
    for i in range(n):
        if i < warm or S[i] is None:
            continue
        sc = T.score_at(M, S, i, par, vocab, book.dates)
        scores[i] = sc["score"]
        raw_reg[i] = T.classify(M, S, i, sc["score"], par)
    regimes = T.debounce_labels(raw_reg, warm, par["windows"]["DWELL"])
    runs = T.compress_runs(regimes, book.dates)

    # chart-only smoothing. Deliberately computed AFTER gating so it cannot reach a gate.
    sm = par["windows"]["SCORE_SMOOTH_CHART_ONLY"]
    scores_smooth = [None] * n
    for i in range(n):
        w = [v for v in scores[max(0, i - sm + 1):i + 1] if v is not None]
        if len(w) >= sm // 2:
            scores_smooth[i] = sum(w) / len(w)

    last = n - 1
    final = T.score_at(M, S, last, par, vocab, book.dates)
    regime = regimes[last] or "Indeterminate"
    events = T.detect_events(M, S, book.dates, par, vocab, label)
    s = S[last] or {}

    verdict = {
        "regime": regime,
        "score": I.r1(final["score"]),
        "coverage": final["coveragePct"],
        "lastDate": book.dates[last],
        "comp": I.r1(comp[last]),
        "peakDate": book.dates[s["peak_i"]] if s.get("peak_i") is not None else None,
        "peakVal": I.r1(s.get("peak_v")),
        "troughDate": book.dates[s["trough_i"]] if s.get("trough_i") is not None else None,
        "troughVal": I.r1(s.get("trough_v")),
        "drawdown": I.r1((s.get("off_peak") or 0) * 100),
        "upFromTrough": I.r1((s.get("up_from_trough") or 0) * 100),
        "topConfirmed": T.top_confirmed(s),
        "playbook": T.render_playbook(regime, par, u["narrative"]["playbook"]),
    }

    # ---- per-ticker table
    yr = par["windows"]["YR"]
    bell = set(u.get("bellwethers", []))
    stocks = []
    for t, col in universe.items():
        i0 = coverage[t]["i0"] or 0
        px_last = col[last]
        if px_last is None:
            continue
        hi_v, hi_i = None, None
        for j in range(i0, n):
            if col[j] is not None and (hi_v is None or col[j] >= hi_v):
                hi_v, hi_i = col[j], j
        base = col[i0]
        j1 = max(i0, last - yr)
        v20, v50 = I.sma(col, 20)[last], I.sma(col, 50)[last]
        vv = [x for x in (book.vol.get(t) or [])[max(0, last - 19):last + 1] if x is not None]
        avg20 = sum(vv) / len(vv) if vv else None
        lastv = (book.vol.get(t) or [None] * n)[last]
        stocks.append({
            "t": t,
            "px": I.r2(px_last),
            "ret": I.r1((px_last / base - 1) * 100) if base else None,
            "ret1y": I.r1((px_last / col[j1] - 1) * 100) if col[j1] else None,
            "offHi": I.r1((px_last / hi_v - 1) * 100) if hi_v else None,
            "hiDate": book.dates[hi_i] if hi_i is not None else None,
            "dSinceHi": (last - hi_i) if hi_i is not None else None,
            "a20": (px_last > v20) if v20 is not None else None,
            "a50": (px_last > v50) if v50 is not None else None,
            "roc": I.r1(I.roc(col, par["windows"]["ROC"])[last]),
            "bell": t in bell,
            "part": coverage[t]["cls"] == "partial",
            "pinned": bool(coverage[t].get("pinned")),
            "avgVol": I.r1(avg20 / 1e6) if avg20 else None,
            "relVol": I.r2(lastv / avg20) if (avg20 and lastv) else None,
        })
    stocks.sort(key=lambda r: (r["ret"] is None, -(r["ret"] or 0)))

    # ---- per-ticker shards
    # Shard contents. Moving averages are NOT shipped: dma20/dma50, volAvg20 and the relative
    # 20/50-dma are plain SMAs of series already in the shard, so stock-panel.js derives them on
    # load. That is presentation arithmetic, not the "heavy calc" the architecture keeps
    # server-side (regime, breadth, beta, pillars all stay here). It cuts the payload roughly in
    # half -- Tab 1 alone was 105 MB of shards, which is a real problem in a git repo -- and it
    # keeps the two tabs that share a ticker deriving identical values from identical inputs.
    par_panel = dict(par)
    par_panel["_relZBenchmark"] = u.get("defaultBenchmark", "EW basket")
    zsh = [str(w) for w in (u.get("shardZWindows") or par["zscore"]["windows"])]
    shards = {}
    for t, col in universe.items():
        i0 = coverage[t]["i0"] or 0
        p = I.build_stock_panel(t, col, book.vol.get(t), bench_series, n, par_panel, i0)
        rec = {
            "t": t, "v": version, "i0": i0,
            "px": slim(p["px"], 2)[i0:],
            "macd": {k: slim(v, 3)[i0:] for k, v in p["macd"].items()},
            "rsi": slim(p["rsi"], 1)[i0:],
            "vol": ([None if v is None else int(v) for v in p["vol"]][i0:]) if p["vol"] else None,
            "obv": ([None if v is None else round(v / 1e6, 2) for v in p["obv"]][i0:]) if p["obv"] else None,
            "rel": {b: slim(d["v"], 2)[i0:] for b, d in p["rel"].items()},
            "zAbs": {w: slim(v, 2)[i0:] for w, v in p["zAbs"].items() if w in zsh},
            "zRel": {w: slim(v, 2)[i0:] for w, v in p["zRel"].items() if w in zsh},
            # `last`, NOT `last - i0`: build_stock_panel returns FULL-grid arrays and the shard
            # slicing happens below. Offsetting here read into the leading-None run for every
            # partial-history ticker (ALAB at i0=657 read index 597) and silently shipped an
            # empty signal summary for all 27 of them.
            "signals": technical_signals(p, par, last),
        }
        shards[t] = rec

    # cross-sectional views (quartile buckets + scatter), computed server-side; the client only
    # scales the diverging bar and plots the points
    quart, scatter, csplit = [], [], []
    if rollup_payload:
        for row in stocks:
            row_roc = row.get("roc")
            if row_roc is not None and row.get("ret") is not None:
                scatter.append({"t": row["t"], "x": row_roc, "y": row["ret"],
                                "bell": row.get("bell", False),
                                "group": (mapping.get(row["t"], {}) or {}).get("sector")})
        quart = R.quartile_buckets(
            [{"t": r["t"], "roc": r["roc"], "ret": r["ret"]} for r in stocks],
            "roc", "65-day ROC")
        parent = {}
        for t, rec in (mapping or {}).items():
            if rec.get("industryGroup") and rec.get("sector"):
                parent[rec["industryGroup"]] = rec["sector"]
        csplit = R.composite_split(rollup_payload.get("industryGroup") or [], parent)

    summary = envelope(
        key, label, "ok", rep, book.dates, built_at, version, source,
        comp=slim(comp, 2),
        comp20=slim(M["comp20"], 2), comp50=slim(M["comp50"], 2), comp200=slim(M["comp200"], 2),
        b20=slim(M["b20"], 1), b50=slim(M["b50"], 1), b200=slim(M["b200"], 1),
        x2065=slim(M["x2065"], 1), hml65=slim(M["hml65"], 2), hi65=slim(M["hi65"], 2),
        lo65=slim(M["lo65"], 2), hml52=slim(M["hml52"], 2), obos=slim(M["obos"], 1),
        roc65=slim(M["roc65"], 2), spread=slim(M["spread"], 2), doubled2y=slim(M["doubled2y"], 1),
        volAlertPos=slim(M["volAlertPos"], 1), volAlertNeg=slim(M["volAlertNeg"], 1),
        sharpe=slim(M["sharpe"], 3), sharpePct=slim(M["sharpePct"], 1),
        betaSpread=slim(M["betaSpread"], 2), betaPct=slim(M["betaPct"], 1),
        upDownVol=slim(M["upDownVol"], 3), distDays=M["distDays"], accumDays=M["accumDays"],
        totVol=[None if v is None else round(v / 1e6, 2) for v in M["totVol"]],
        totVol50=[None if v is None else round(v / 1e6, 2) for v in M["totVol50"]],
        obv=slim(M["obv"], 2), bellRel=slim(M["bellRel"], 2),
        macdLine=slim(M["macdLine"], 3), macdSignal=slim(M["macdSignal"], 3),
        macdHist=slim(M["macdHist"], 3), rsi=slim(M["rsi"], 2),
        bench={b: slim(v, 4) for b, v in bench_series.items()},
        baskets={k: {"n": v["n"], "scored": v["scored"], "note": v.get("note"),
                     "comp": slim(v["comp"], 2) if v.get("comp") else None,
                     "rel": slim(v["rel"], 2) if v.get("rel") else None}
                 for k, v in (M.get("baskets") or {}).items()},
        splits=splits,
        rollups=rollup_payload,
        quartiles=quart,
        scatter=scatter,
        compositeSplit=csplit,
        scores=slim(scores, 2), scoresSmooth=slim(scores_smooth, 2),
        regimes=regimes, runs=runs,
        pillars=[p.to_dict() for p in final["pillars"]],
        verdict=verdict, events=events, stocks=stocks,
        meta={
            "nFull": len(full_t),
            "nPartial": sum(1 for c in coverage.values() if c.get("cls") == "partial"),
            "dropped": sorted(t for t, c in coverage.items() if c.get("cls") == "drop"),
            "partial": sorted(t for t, c in coverage.items() if c.get("cls") == "partial"),
            "excluded": {t: c.get("reason") for t, c in coverage.items() if c.get("cls") == "excluded"},
            "pinned": sorted(pinned),
            "bellwethers": sorted(bell),
            "benchmarks": sorted(bench_series),
            "defaultBenchmark": u.get("defaultBenchmark"),
            "defaultTicker": u.get("defaultTicker"),
            "zWindows": par["zscore"]["windows"],
            "horizons": par["horizons"],
            "calendar": book.calendar,
            "vocabulary": vocab,
        },
    )
    return summary, shards, rep


def technical_signals(panel, params, i):
    """Per-ticker signal summary. Objective statements only -- each is a stated test.

    This did not exist in either reference dashboard; CLAUDE.md lists it as an existing
    capability but a grep of both files finds nothing. It is net-new.
    """
    out = []

    def at(series, k=i):
        return series[k] if series and 0 <= k < len(series) else None

    px, d20, d50 = at(panel["px"]), at(panel["dma20"]), at(panel["dma50"])
    if px is not None and d20 is not None:
        out.append({"test": "Price vs 20-dma",
                    "value": f"{(px/d20-1)*100:+.1f}%",
                    "state": "above" if px > d20 else "below"})
    if px is not None and d50 is not None:
        out.append({"test": "Price vs 50-dma",
                    "value": f"{(px/d50-1)*100:+.1f}%",
                    "state": "above" if px > d50 else "below"})
    if d20 is not None and d50 is not None:
        out.append({"test": "20-dma vs 50-dma",
                    "value": f"{(d20/d50-1)*100:+.1f}%",
                    "state": "uptrend" if d20 > d50 else "downtrend"})
    r = at(panel["rsi"])
    if r is not None:
        st = "overbought" if r >= params["rsi"]["ob"] else ("oversold" if r <= params["rsi"]["os"] else "neutral")
        out.append({"test": f"RSI ({params['rsi']['n']})", "value": f"{r:.1f}", "state": st})
    h = at(panel["macd"]["hist"])
    if h is not None:
        out.append({"test": "MACD histogram", "value": f"{h:+.2f}",
                    "state": "positive" if h > 0 else "negative"})
    v, va = at(panel["vol"]), at(panel["volAvg20"])
    if v is not None and va:
        out.append({"test": "Relative volume", "value": f"{v/va:.2f}x",
                    "state": "elevated" if v / va > 1.5 else "routine"})
    ob = panel.get("obv")
    if ob:
        prev = at(ob, max(0, i - 21))
        cur = at(ob)
        if prev is not None and cur is not None:
            out.append({"test": "OBV 21-session change", "value": f"{(cur-prev)/1e6:+.1f}M",
                        "state": "accumulation" if cur > prev else "distribution"})
    return out


# ---------------------------------------------------------------- emit


def emit(cfg, key, summary, shards, out_root) -> dict:
    """Write summary + per-ticker shards + manifest. Returns the manifest."""
    u = cfg.universe(key)
    d = os.path.join(out_root, key)
    tdir = os.path.join(d, "tickers")
    os.makedirs(tdir, exist_ok=True)

    manifest = {
        "schemaVersion": 1, "universe": key, "label": summary["label"],
        "status": summary["status"], "version": summary["version"],
        "builtAt": summary["builtAt"], "source": summary["source"],
        "dateCount": len(summary.get("dates") or []),
        "firstDate": (summary.get("dates") or [None])[0],
        "lastDate": (summary.get("dates") or [None])[-1],
        "validation": summary["validation"],
    }

    if summary["status"] != "ok":
        manifest["tickers"] = {}
        _write(os.path.join(d, "manifest.json"), manifest)
        return manifest

    meta = summary["meta"]
    manifest.update({
        "summaryFile": "summary.json", "shardDir": "tickers",
        "zWindows": meta["zWindows"], "horizons": meta["horizons"],
        "benchmarks": meta["benchmarks"], "defaultBenchmark": meta["defaultBenchmark"],
        "defaultTicker": meta["defaultTicker"],
    })
    tick = {}
    total = 0
    for t, rec in shards.items():
        fn = f"tickers/{t.replace('/', '_')}.json"
        p = os.path.join(d, fn)
        b = _write(p, rec)
        total += b
        cvg = next((s for s in summary["stocks"] if s["t"] == t), {})
        tick[t] = {"f": fn, "b": b, "i0": rec["i0"],
                   "bell": cvg.get("bell", False), "part": cvg.get("part", False),
                   "pinned": cvg.get("pinned", False)}
    manifest["tickers"] = tick
    manifest["shardBytes"] = total

    _write(os.path.join(d, "summary.json"), summary)
    _write(os.path.join(d, "manifest.json"), manifest)
    manifest["_summaryBytes"] = os.path.getsize(os.path.join(d, "summary.json"))
    return manifest


def _write(path, obj) -> int:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, separators=(",", ":"), allow_nan=False)
    return os.path.getsize(path)


def copy_to_site(processed_dir, site_dir):
    if os.path.abspath(processed_dir) == os.path.abspath(site_dir):
        return
    os.makedirs(site_dir, exist_ok=True)
    for name in os.listdir(processed_dir):
        src = os.path.join(processed_dir, name)
        dst = os.path.join(site_dir, name)
        if os.path.isdir(src):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        elif name.endswith(".json"):
            shutil.copy2(src, dst)
