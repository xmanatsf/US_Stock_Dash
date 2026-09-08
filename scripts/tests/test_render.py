"""Headless render check for every tab.

Asserts what a screenshot cannot: zero pageerrors, zero console.error (this is what catches the
negative-SVG-height regression, which paints nothing but looks merely 'empty'), fetched JSON
parses, every chart actually emitted an <svg>, and the selector switch does not leak chart
registrations.

Served over HTTP, not file:// -- the site uses ES modules and fetch, which browsers block on
file:// for security. GitHub Pages serves over HTTP so this matches production.

    python scripts/tests/test_render.py [--headed] [--shots]
"""

from __future__ import annotations

import argparse
import functools
import http.server
import os
import socketserver
import sys
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SITE = os.path.join(ROOT, "site")
SHOTS = os.path.join(ROOT, "reference", "shots")


def check_strip_agreement(failures):
    """The fab5 page's live strip must be READ from the universe payload, never recomputed.

    A page that quotes a price is a second source of prices, and a second source of prices is a
    source of disagreement. This asserts field-by-field that it is a copy: same last price, same
    RSI tail, same off-high, same regime as the tab the link points at. Returns the number of
    tickers checked, or None if it failed.
    """
    import json
    data = os.path.join(ROOT, "data", "processed")
    fp = os.path.join(data, "insights", "fab5.json")
    if not os.path.exists(fp):
        failures.append("fab5: data/processed/insights/fab5.json is missing")
        print("  FAIL fab5 payload not built")
        return None
    with open(fp, encoding="utf-8") as f:
        doc = json.load(f)

    bad, checked = [], 0
    summaries, manifests = {}, {}
    for imp in doc["implications"]:
        live = imp.get("live")
        if not live:
            continue
        uni, t = live["universe"], imp["ticker"]
        if uni not in summaries:
            with open(os.path.join(data, uni, "summary.json"), encoding="utf-8") as f:
                summaries[uni] = json.load(f)
            with open(os.path.join(data, uni, "manifest.json"), encoding="utf-8") as f:
                manifests[uni] = json.load(f)
        summ, man = summaries[uni], manifests[uni]
        row = next((r for r in summ["stocks"] if r["t"] == t), None)
        if row is None:
            bad.append(f"{t}: not in {uni} summary.stocks")
            continue
        with open(os.path.join(data, uni, man["tickers"][t]["f"]), encoding="utf-8") as f:
            shard = json.load(f)
        rsi = next((v for v in reversed(shard["rsi"]) if v is not None), None)

        for field, expect in (("px", row["px"]), ("ret1y", row["ret1y"]),
                              ("offHi", row["offHi"]), ("roc", row["roc"]),
                              ("a20", row["a20"]), ("a50", row["a50"]),
                              ("relVol", row["relVol"]), ("rsi", rsi),
                              ("regime", summ["verdict"]["regime"]),
                              ("asOf", man["lastDate"])):
            if live.get(field) != expect:
                bad.append(f"{t}.{field}: page={live.get(field)!r} payload={expect!r}")
        checked += 1

    if bad:
        failures.append(f"fab5: live strip disagrees with the universe payload: {bad[:5]}")
        print(f"  FAIL strip disagreement ({len(bad)}): {bad[:5]}")
        return None
    return checked


def serve(directory):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=directory)
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, httpd.server_address[1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--headed", action="store_true")
    ap.add_argument("--shots", action="store_true")
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright

    httpd, port = serve(SITE)
    base = f"http://127.0.0.1:{port}"
    tabs = ["market-internals", "semis", "software", "hw-networking"]
    # fab5 is a PAGE, not a universe: no charts, no horizon control, no stock selector. It gets
    # its own assertions below rather than being run through the chart battery.
    pages = ["fab5"]
    failures = []
    os.makedirs(SHOTS, exist_ok=True)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=not args.headed)
        for name in ["index"] + tabs + pages:
            page = browser.new_page(viewport={"width": 1280, "height": 1000})
            errors, console_errors = [], []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.on("console", lambda m: console_errors.append(m.text)
                    if m.type == "error" else None)
            url = f"{base}/index.html" if name == "index" else f"{base}/tabs/{name}.html"
            print(f"\n=== {name}")
            page.goto(url, wait_until="networkidle")
            page.wait_for_timeout(1200)

            if errors:
                failures.append(f"{name}: {len(errors)} pageerror(s): {errors[:3]}")
                print(f"  FAIL pageerrors: {errors[:3]}")
            else:
                print("  PASS no pageerrors")
            if console_errors:
                failures.append(f"{name}: console.error: {console_errors[:3]}")
                print(f"  FAIL console errors: {console_errors[:3]}")
            else:
                print("  PASS no console errors")

            if name in pages:
                # 1. the page rendered its sections rather than the error banner
                counts = page.evaluate("""() => ({
                    insights: document.querySelectorAll('#insightList .insight').length,
                    agree: document.querySelectorAll('.card.conv').length,
                    disputes: document.querySelectorAll('.card.disp').length,
                    checklist: document.querySelectorAll('.ckTbl tbody tr').length,
                    imps: document.querySelectorAll('.imp').length,
                    fatal: document.querySelectorAll('.banner.fatal').length,
                })""")
                print(f"  sections: {counts}")
                if counts["fatal"]:
                    failures.append(f"{name}: rendered a fatal banner")
                    print("  FAIL fatal banner on the page")
                for k, minimum in (("insights", 5), ("agree", 3), ("disputes", 3),
                                   ("checklist", 3), ("imps", 5)):
                    if counts[k] < minimum:
                        failures.append(f"{name}: only {counts[k]} {k} rendered (expected >= {minimum})")
                        print(f"  FAIL {k}: {counts[k]} < {minimum}")
                if all(counts[k] >= m for k, m in (("insights", 5), ("agree", 3),
                                                   ("disputes", 3), ("checklist", 3), ("imps", 5))):
                    print("  PASS every section rendered content")

                # 2. deep links must point at a tab that exists and carry a ticker
                links = page.eval_on_selector_all(
                    ".impGo[href]", "a => a.map(x => x.getAttribute('href'))")
                bad = []
                for h in links:
                    tab = h.split("/")[-1].split("?")[0].replace(".html", "")
                    if tab not in tabs or "?t=" not in h:
                        bad.append(h)
                print(f"  deep links: {len(links)} ticker links into the universe tabs")
                if not links:
                    failures.append(f"{name}: no ticker deep links rendered at all")
                    print("  FAIL no deep links")
                elif bad:
                    failures.append(f"{name}: deep links pointing nowhere: {bad[:3]}")
                    print(f"  FAIL bad deep links: {bad[:3]}")
                else:
                    print("  PASS every deep link targets an existing tab with a ticker")

                # 3. THE assertion that matters: the strip must agree with the universe payload.
                # If this page ever computes its own numbers it becomes a second, quietly
                # divergent source of prices -- which is the one failure mode worth a test.
                mismatches = check_strip_agreement(failures)
                if mismatches is not None:
                    print(f"  PASS live strip agrees with the universe payload "
                          f"({mismatches} tickers checked)")

                # 4. filters must actually filter
                before = page.eval_on_selector_all(".imp", "e => e.length")
                page.click('.impFilter[data-dir="bull"]')
                page.wait_for_timeout(200)
                after = page.eval_on_selector_all(".imp", "e => e.length")
                page.click('.impFilter[data-dir="all"]')
                page.wait_for_timeout(200)
                restored = page.eval_on_selector_all(".imp", "e => e.length")
                print(f"  direction filter: {before} -> {after} -> {restored}")
                if not (0 < after < before and restored == before):
                    failures.append(f"{name}: direction filter is a no-op "
                                    f"({before} -> {after} -> {restored})")
                    print("  FAIL direction filter did not filter")
                else:
                    print("  PASS direction filter narrows and restores")

                # 5. the infographic. It renders six bands off arrays that already exist in the
                # payload, so an empty band means a renamed key silently dropped a whole
                # category rather than throwing -- which no pageerror check would catch.
                ig = page.evaluate("""() => ({
                    bands: document.querySelectorAll('#infographic .ig-band').length,
                    stats: document.querySelectorAll('#infographic .ig-stat').length,
                    themes: document.querySelectorAll('#infographic .ig-theme').length,
                    scens: document.querySelectorAll('#infographic .ig-scen').length,
                    cal: document.querySelectorAll('#infographic .ig-cal li').length,
                    sides: document.querySelectorAll('#infographic .ig-side').length,
                    counts: document.querySelectorAll('#infographic .ig-count').length,
                    tks: document.querySelectorAll('#infographic .ig-tk').length,
                })""")
                print(f"  infographic: {ig}")
                empty = [k for k, v in ig.items() if not v]
                if empty:
                    failures.append(f"{name}: infographic band(s) rendered empty: {empty}")
                    print(f"  FAIL empty infographic bands: {empty}")
                elif ig["bands"] != 6:
                    failures.append(f"{name}: infographic has {ig['bands']} bands, expected 6")
                    print(f"  FAIL {ig['bands']} bands, expected 6")
                else:
                    print("  PASS all six infographic bands rendered content")

                # 6. the signal-board status filter, same contract as the direction filter
                ck_before = page.eval_on_selector_all(".ckTbl tbody tr", "e => e.length")
                page.click('.ckFilter[data-st="bad"]')
                page.wait_for_timeout(200)
                ck_after = page.eval_on_selector_all(".ckTbl tbody tr", "e => e.length")
                page.click('.ckFilter[data-st="all"]')
                page.wait_for_timeout(200)
                ck_restored = page.eval_on_selector_all(".ckTbl tbody tr", "e => e.length")
                print(f"  status filter: {ck_before} -> {ck_after} -> {ck_restored}")
                if not (0 < ck_after < ck_before and ck_restored == ck_before):
                    failures.append(f"{name}: signal-board status filter is a no-op "
                                    f"({ck_before} -> {ck_after} -> {ck_restored})")
                    print("  FAIL status filter did not filter")
                else:
                    print("  PASS status filter narrows and restores")

            elif name != "index":
                charts = page.eval_on_selector_all(
                    "[data-chart]", "els => els.map(e => ({id: e.id, svg: !!e.querySelector('svg'),"
                    " empty: !!e.querySelector('.emptyNote')}))")
                if not charts:
                    failures.append(f"{name}: no [data-chart] containers in the DOM at all "
                                    f"(initTab probably threw and the page replaced #app)")
                    print("  FAIL zero chart containers -- the app was replaced by an error state")
                blank = [c["id"] for c in charts if not c["svg"] and not c["empty"]]
                print(f"  charts: {len(charts)} containers, "
                      f"{sum(1 for c in charts if c['svg'])} rendered, "
                      f"{sum(1 for c in charts if c['empty'])} explicitly empty")
                if blank:
                    failures.append(f"{name}: blank chart containers {blank}")
                    print(f"  FAIL blank containers: {blank}")
                else:
                    print("  PASS every chart container has an svg or a stated reason")

                # negative SVG height would be logged as a console error above; also assert none
                negs = page.eval_on_selector_all(
                    "rect", "els => els.filter(e => parseFloat(e.getAttribute('height')) < 0).length")
                if negs:
                    failures.append(f"{name}: {negs} rect(s) with negative height")
                    print(f"  FAIL {negs} negative-height rects")
                else:
                    print("  PASS no negative-height rects (bipolar bar fix holds)")

                # selector churn must not leak chart registrations
                sel = page.query_selector("#stockSel")
                if sel:
                    opts = page.eval_on_selector_all("#stockSel option", "o => o.map(x => x.value)")
                    before = page.evaluate(
                        "import('/assets/js/charts.js').then(m => m.liveChartCount())")
                    for t in opts[1:11]:
                        page.select_option("#stockSel", t)
                        page.wait_for_timeout(120)
                    page.wait_for_timeout(600)
                    after = page.evaluate(
                        "import('/assets/js/charts.js').then(m => m.liveChartCount())")
                    print(f"  live chart registrations: {before} -> {after} after 10 switches")
                    if after > before + 2:
                        failures.append(f"{name}: chart registry grew {before} -> {after}")
                        print("  FAIL registry grew")
                    else:
                        print("  PASS no listener/registry leak")
                    if errors:
                        failures.append(f"{name}: error during selector switching")

                    # benchmark + z-window switches
                    for sid in ("#benchSel", "#zWinSel"):
                        vals = page.eval_on_selector_all(f"{sid} option", "o => o.map(x => x.value)")
                        for v in vals:
                            page.select_option(sid, v)
                            page.wait_for_timeout(100)
                    print(f"  PASS benchmark and z-window switching")

                # horizon control must actually CHANGE THE WINDOW, not just the active button.
                # Asserting "no errors" would pass on a no-op, which is exactly how this shipped
                # broken the first time. Compare the first x-axis label across horizons.
                def first_x_label():
                    return page.evaluate("""() => {
                        const el = document.querySelector('#chComp svg');
                        if (!el) return null;
                        const t = [...el.querySelectorAll('text')]
                          .filter(x => x.getAttribute('text-anchor') === 'middle');
                        return t.length ? t[0].textContent : null;
                    }""")
                seen = {}
                for h in ("5y", "1y", "3m", "1m"):
                    b = page.query_selector(f'.hBtn[data-h="{h}"]')
                    if b:
                        b.click()
                        page.wait_for_timeout(350)
                        seen[h] = first_x_label()
                distinct = len({v for v in seen.values() if v})
                print(f"  horizon -> first x-axis label: {seen}")
                if distinct >= 3:
                    print("  PASS horizon actually re-windows the charts")
                else:
                    failures.append(f"{name}: horizon control is a no-op, labels={seen}")
                    print("  FAIL horizon control did not change the rendered window")

            if args.shots:
                page.screenshot(path=os.path.join(SHOTS, f"{name}.png"), full_page=False)
            if errors:
                failures.append(f"{name}: post-interaction pageerrors {errors[:2]}")
            page.close()
        browser.close()
    httpd.shutdown()

    print("\n" + "=" * 60)
    if failures:
        print(f"FAILED ({len(failures)})")
        for f in failures:
            print("  -", f)
        return 1
    print("ALL RENDER CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
