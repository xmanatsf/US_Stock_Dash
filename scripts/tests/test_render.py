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
    failures = []
    os.makedirs(SHOTS, exist_ok=True)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=not args.headed)
        for name in ["index"] + tabs:
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

            if name != "index":
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
