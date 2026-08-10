# US_Stk_Dash — Stock Analytics Dashboard

Build a modular, multi-tab, static stock analytics dashboard deployable on GitHub Pages. It applies the RenMac breadth/momentum/regime framework (and future frameworks) across four stock universes: broad S&P 500 market internals, semiconductors, software, and hardware/networking.

## Read before building

1. `DASHBOARD_PLAYBOOK.md` — how the existing single-sector dashboards (`US_Semi_Chip_Top_Dashboard.html`, `SP100_Sector_Dashboard.html`, `build_dashboard.py`, `build_renmac_dashboard.py`, `renmac_score.py`) were built, and every data/charting gotcha hit so far. This is prior art for this project, not a different codebase — port its patterns (loaders, MACD/RSI/OBV/z-score helpers, stock-detail panel, regime classifier) into the new modular structure rather than reinventing them.
2. `RENMAC_TIMING_FRAMEWORK.md` — the seven-pillar scoring/regime model (extension, structural turn, momentum, breadth, sentiment, +2 quantitative pillars) and its four implementation rules (rebalance the composite, read structure off a trailing window, debounce the label not the score, "peaks beat levels"). Primary framework, not the only one — the calc engine must let new frameworks/indicators plug in alongside it.
3. `Renmac Technical Setup on Semiconductor stocks.txt` — the narrative source for pillar language (topping direction). `DASHBOARD_PLAYBOOK.md` already documents the mirror-image bullish/bottoming reading of every pillar — implement both directions from day one, never bearish-only.
4. `US_Semi_Chip_Top_Dashboard.html` — the reference layout/chart suite for **every individual-stock panel** in this project (Tabs 1–4): price + 20/50-dma, relative-to-benchmark price + its own 20/50-dma, MACD, RSI, OBV/volume, 20-day rolling z-score (absolute + relative), benchmark selector, technical-signal summary. Treat this as the canonical per-ticker template — semis, software, and hardware/networking tabs all reuse it identically.
5. `SP100_Sector_Dashboard.html` — the reference for sector/industry-group rollups: per-group regime classification, breadth, quartile buckets, cross-sectional scatter. Basis for Tab 1's sector/industry-group views.

## Input data (as of 2026-08-09)

| File | Sheets | Shape | Notes / known issues |
|---|---|---|---|
| `SP500 5y price and volume 20260809.xlsx` | `Price`, `Volume` (+ `__snloffice` cache sheet — ignore) | 501 tickers × 1,829 rows | **Two header rows**: ticker symbols on row 1, `"Day Close Price"`/`"Volume"` label on row 2 — take row 1 unconditionally as header, never filter on col-A-is-None before splitting header from data. 1,829 rows over 5y ≈ 365/yr → almost certainly **calendar days** with weekend/holiday rows forward-filled; verify via the `rows/years` and repeated-row-across->95%-of-universe checks in `DASHBOARD_PLAYBOOK.md` before computing any moving average. No embedded SPY/benchmark column — SPY must be sourced from a file that has one (semi/hw workbooks below) or added as its own small reference series. |
| `SP500 industry groups.xlsx` | `Sheet1` | 505 rows × 7 cols | CapIQ mapping export. **CORRECTED 2026-08-09:** the layout is blank row 1, human header row 2 (`Entity Name`, `Entity ID`, `Ticker`, `Sector`, `Industry Group`, `Industry`, `Primary Industry`), CapIQ field codes row 3, blank rows 4–5, **data from row 6** (1-based). An earlier version of this file said "data from row 4" — that was wrong. `build_sp100_dashboard.py:68` uses yet another offset for `SP100.xlsx`, so the offset is per-source config (`config/sectors.json`), never a shared constant. Verified 500/500 priced tickers map, to 11 sectors and 25 industry groups. |
| `US semi stocks 5y price and volume 20260807.xlsx` | `Price`, `Volume` | 68 tickers × 1,829 rows | Same two-header-row and calendar-day shape as above. Carries `SMH` and `SPY` as extra ticker-like columns — treat as benchmarks, not universe members. `WOLF`'s price/volume show `'NA'` strings (delisted/halted) — coerce non-numeric to `None`, don't let it crash numeric ops. |
| `US software stocks 5y price and volume 20260809.xlsx` | `Price`, `Volume` | 120 tickers × 1,829 rows | Same shape. **No SMH/SPY columns** — benchmark series must be joined in from another workbook, date-aligned. Per `DASHBOARD_PLAYBOOK.md`, eyeball for a composite-distorting subgroup (prior build found ~10 crypto-treasury tickers riding in this GICS bucket) before trusting a single blended return. |
| `US hw networking stocks 5y price and volume 20260809.xlsx` | `Price`, `Volume` | 36 tickers × 1,827 data rows | **RESOLVED 2026-08-09.** The first delivery of this file was a corrupt CapIQ export: row-2 header `"#PEND"`/`"SPGRANGEV"` (unresolved formulas) and **34 of 36 columns byte-identical to the semiconductor workbook** — the save had cached the previous query's values under hardware headers, so "AAPL" carried AMD's $110.11. Re-exported by the user and re-verified clean: correct prices (AAPL $146.09 on 2021-08-09), zero column matches against any other workbook, identical 1,255-day grid, and it also carries `SPY` and `SMH`. 34 universe tickers; only DBD, INFQ and SNDK have leading NAs. The detector that caught it (`validators.cross_workbook_identity`) is now a permanent check on every build, because this failure mode recurs whenever CapIQ formulas fail to resolve before a save. `US network and hw stocks.xlsx` (market-cap + industry mapping) is a companion for bellwether/industry curation, not a price source. |

General rule for all price/volume files: sanity-check header row, date range, row count vs. trading-day count, and NA/placeholder strings on every load — never assume a workbook is clean because a prior one with the same layout was.

### Verified facts about the 2026-08-09 vintage (measured, not assumed)

- **All four price workbooks are calendar-day grids** carrying 1,827 data rows: 522 weekend rows forward-filled from the prior close *and prior volume*, plus 50 US market holidays. Dropping weekends first, then any weekday row repeating the prior surviving row across >95% of the universe on **price AND volume**, leaves **1,255 real trading days** (`2021-08-09 .. 2026-08-07`) — identical across all four files. Exact whole-row equality is not a sufficient holiday test: it finds 11 holidays in the software file instead of 50.
- **Every `'NA'` run is leading-edge only.** Zero interior gaps, zero trailing NAs, universe-wide. `NA` means "not listed yet", so the rule is to truncate at first print. `WOLF` is a re-listing with short history, not a delisting.
- **SPY and SMH live only in the semiconductor and hardware workbooks.** They are extracted once, before any tab build, and joined into every universe — which is sound precisely because the grids are identical.
- **Three S&P columns are not prices at all** and are excluded at load time with written reasons in `config/universes.json`: `D` (Dominion, a constant 15 for all 1,255 sessions), `COR` (Cencora, 0.024 → 0.0018 while the stock trades near $250), `BNY` (BNY Mellon, 15.36 → 10.2 while the stock trades near $70–100; already flagged in `DASHBOARD_PLAYBOOK.md`).
- **Eight software names are pinned at M&A deal terms** (Informatica $24.79, Couchbase $24.51, Olo $10.26, MeridianLink $20.01, Verint $20.51, PROS $23.25, Jamf $13.05, Confluent $30.99). This is correct data about a real situation, so they are kept and named — but excluded from breadth, momentum and z-score measures, where an unchanged price otherwise reads as strength. A dead feed is indistinguishable from this on every price/volume statistic, so it is reported rather than auto-classified.
- **The software universe carries 10 crypto/BTC-proxy names** (MARA, RIOT, CLSK, CORZ, HUT, WULF, CIFR, MSTR, CRCL, BMNR). Mean return is +27% against a **median of −21%** — the composite is shipped three ways (all / ex-crypto / crypto-only), never blended.

## Tabs

1. **Market Internals** — `SP500 5y price and volume 20260809.xlsx` + `SP500 industry groups.xlsx`, styled after `SP100_Sector_Dashboard.html`. Sector/industry-group performance, breadth/leadership/participation/momentum/relative-strength trends, top/bottom performers per group, absolute + relative performance across configurable horizons, SPY as default benchmark, a stock selector reproducing the full `US_Semi_Chip_Top_Dashboard.html` per-ticker panel for any S&P 500 name.
2. **Semiconductor Stock Dynamics** — `US semi stocks 5y price and volume 20260807.xlsx`, direct port of `US_Semi_Chip_Top_Dashboard.html` (layout, charts, indicators, signals, conclusions). Ticker + benchmark selector, SPY default.
3. **Software Stock Dynamics** — `US software stocks 5y price and volume 20260809.xlsx`, same per-stock framework/chart suite as Tab 2. Ticker + benchmark selector, SPY default, technical-signal summaries, relative-performance analysis.
4. **Hardware & Networking Stock Dynamics** — `US hw networking stocks 5y price and volume 20260809.xlsx` (validate first — see table above), same per-stock framework as Tab 2. Ticker + benchmark selector, SPY default, technical-signal summaries, relative-performance analysis.

All four tabs share one calculation engine, one chart component library, and one interpretation layer — a tab is a config (which workbook(s), which universe, which sector-mapping file if any) plus a thin page assembling shared components, not a fork of the code.

## Architecture

Static, zero-backend, GitHub Pages–deployable, following the lightweight model in [xmanatsf/stk-dashboard](https://github.com/xmanatsf/stk-dashboard) (single `index.html` reading a pre-built data file from the same repo, a Python script that regenerates that data file, a one-click push routine, `Settings → Pages → Deploy from branch`). This project extends that model to four tabs sharing one codebase instead of one page reading one CSV.

```
US_Stk_Dash/
  data/
    raw/                        # source .xlsx files (as delivered, unmodified)
    processed/                  # generated per-tab JSON, built from raw/ — never hand-edited
  config/
    universes.json              # per-tab: workbook path(s), sheet names, ticker universe, benchmark tickers
    sectors.json                # sector/industry-group classification source + mapping-sheet layout (header row offset etc.)
    parameters.json              # MA windows, ROC window, RSI/MACD params, breadth thresholds, oversold zone, z-score window, default horizons
    charts.json                  # chart definitions shared by all tabs (which series, colors, panel layout) keyed by chart type
  scripts/                       # Python build pipeline (mirrors build_dashboard.py's pattern, generalized)
    loaders.py                   # xlsx → typed price/volume/mapping frames; header-row + calendar-day + NA/placeholder handling
    validators.py                # date/ticker/duplicate/missing-value/price-volume/benchmark-alignment/sector-mapping checks; returns a report, never silently drops data
    indicators.py                # daily_ret, rolling_z, ema/macd/rsi, obv, rel_vol, breadth, ROC, regime classifier — ported from build_dashboard.py / renmac_score.py
    interpretation.py            # pillar/regime narrative generation, kept separate from indicators.py: objective signal → labeled conclusion, both directions (bearish/bullish)
    build_market_internals.py    # Tab 1 data build → data/processed/market_internals.json
    build_semis.py               # Tab 2 build
    build_software.py            # Tab 3 build
    build_hw_networking.py       # Tab 4 build
    build_all.py                 # runs all four + validation report
  site/                          # what actually deploys to GitHub Pages
    index.html                   # tab shell / nav
    tabs/
      market-internals.html
      semis.html
      software.html
      hw-networking.html
    assets/
      js/
        charts.js                # shared inline-SVG chart renderer (port of dashboard_template.html's chart()/render(), incl. the bipolar-bar-height fix)
        indicators-client.js     # any client-side derived display logic (the heavy calc stays server-side in scripts/)
        interpret.js             # renders interpretation.py's output; keeps objective signals visually distinct from conclusions
        stock-panel.js           # the shared per-ticker panel (ticker + benchmark selectors, all charts) used by Tabs 1–4
        tabs.js                  # tab navigation, shared date-range control, loading/error states
      css/
        dashboard.css
    data/                        # copy (or symlink at build time) of data/processed/*.json — what the browser actually fetches
  DEPLOY.md                      # setup, local-testing, data-refresh, GitHub Pages steps
  CLAUDE.md
  DASHBOARD_PLAYBOOK.md
  RENMAC_TIMING_FRAMEWORK.md
  Renmac Technical Setup on Semiconductor stocks.txt
```

Config-driven means: adding a fifth universe/tab, a new indicator, or a new sector taxonomy should require new entries in `config/*.json` plus one `build_<tab>.py` and one `tabs/<tab>.html`, not edits scattered across `charts.js` or `indicators.py`.

## Data validation (run in `validators.py` before any indicator is computed)

- Dates: monotonic, no duplicates, calendar-day rows detected and dropped (see `SP500 5y...xlsx` note above), trading-day count sane for the window.
- Tickers: header row confirmed to contain ticker strings (not numeric data mistaken for a header — see the two-header-row gotcha), duplicate columns flagged.
- Missing values: distinguish "no data yet" (partial-history/IPO) from "gap" from delisting; volume is never forward-filled, price gaps get bounded forward-fill only.
- Placeholder strings: `'NA'`, `'NM'`, `'#PEND'`, or any non-numeric value in a price/volume cell coerced to `None` with a logged count, not silently treated as 0.
- Flatline/anomaly scan: runs of identical price+volume across >95% of the universe (calendar-day artifact) and single-ticker flatline-then-jump patterns (bad data, e.g. the `WAL`/HW-file style cases) both flagged before use.
- Benchmark alignment: benchmark series (SPY, and SMH where relevant) date-joined to the universe on trading days actually present in both; missing benchmark coverage reported per tab, not assumed.
- Sector mapping: every priced ticker either resolves to a sector/industry group or is explicitly reported as unmapped — no silent drops from breadth/leadership rollups.
- Every validation run produces a report (counts, tickers affected, reasons) surfaced in the build log and, for anything unresolved, as a visible dashboard banner — never fabricate or interpolate around a validation failure.

## Development sequence

1. `config/` schemas + `scripts/loaders.py` + `scripts/validators.py`, run against all five input files, fix data issues found (especially the Tab 4 file) before writing any indicator code.
2. `scripts/indicators.py` (port from `build_dashboard.py`/`build_renmac_dashboard.py`/`renmac_score.py`) + `scripts/interpretation.py`, unit-checked against the existing dashboards' printed console summaries for the semis file as a regression check.
3. `assets/js/charts.js` + `stock-panel.js`, built once against Tab 2 (semis) since `US_Semi_Chip_Top_Dashboard.html` is the reference to match pixel-for-pixel in capability.
4. Tab 2 (Semiconductors) end-to-end — this is the template every other tab must match.
5. Tab 3 (Software) and Tab 4 (Hardware/Networking) by reusing Tabs/scripts from step 4 via config only.
6. Tab 1 (Market Internals) — sector/industry-group rollup logic ported from the SP100 reference, plus the shared stock-panel component from step 3 for individual names.
7. `index.html` shell, shared nav, synchronized date-range control, loading/error states across all tabs.
8. `DEPLOY.md` + GitHub Pages wiring + data-refresh routine.

## Testing / QA criteria

- Each `build_<tab>.py` prints a console summary (coverage %, date range, peak/trough, breadth, regime call per pillar) that a human can sanity-check against the raw data before trusting the output — mirror the existing scripts' pattern.
- Headless render check per tab (Playwright against the `file://` or deployed URL): page loads, no `pageerror`s, embedded/fetched JSON parses, ticker/benchmark selector switch re-renders without leaking listeners or throwing.
- Cross-tab consistency check: same indicator (e.g., 20-dma, RSI) computed on the same ticker if it appears in more than one universe file must agree; shared chart component must render identically across tabs.
- Validation report from `validators.py` reviewed and either clean or explicitly annotated as a known/accepted limitation in the relevant tab's footer — this is the mechanism for "don't fabricate when data is missing."
- Interpretation text spot-checked against the objective numbers it's describing (peak/trough dates, thresholds crossed) to confirm the objective-signal vs. conclusion distinction actually holds in the copy, not just in code structure.

## GitHub Pages deployment

Static `site/` deploys directly — no build step required at serve time (all heavy computation happens in the Python `scripts/` pipeline ahead of commit, output is plain JSON `fetch()`ed by the browser, same approach as `US_Semi_Chip_Top_Dashboard.html`'s embedded-`DATA`-blob pattern, generalized to fetched files instead of inlined). `DEPLOY.md` should specify: one-time repo creation and `Settings → Pages → Deploy from branch (main, /site or /root)`; local testing via any static file server (or `file://`, since the reference dashboards already work that way) pointed at `site/`; the data-refresh routine (drop new `.xlsx` in `data/raw/`, run `python scripts/build_all.py`, review the validation report, commit `data/processed/*.json` + `site/data/*.json`, push); and cache-busting on fetch so a refreshed deploy is visible without special client action.

## Non-negotiables

- No backend services, no build-time framework/bundler dependency — vanilla JS + inline SVG charts, matching the existing dashboards. **One deliberate deviation from the reference dashboards:** because the site is modular (ES modules + `fetch`ed JSON) it cannot be opened from `file://` — browsers block module imports and fetches on that scheme. Local testing needs `python -m http.server 8000 --directory site`. GitHub Pages serves over HTTP, so production is unaffected. This was the price of "a tab is a config entry, not a fork".
- Three capabilities the spec assumed already existed do **not** exist in either reference dashboard and were built new: the per-ticker technical-signal summary, the shared date-range/horizon control, and per-ticker OBV (the references compute OBV only at composite level). Grep both files before assuming a capability is available to port.
- Every capability already in `US_Semi_Chip_Top_Dashboard.html` and `SP100_Sector_Dashboard.html` must be present somewhere in the new dashboard unless explicitly replaced by a documented improvement — this is a supersede, not a downgrade.
- Frameworks and indicators beyond RenMac's must be addable without restructuring — new pillar/indicator = new function in `indicators.py` + new entry in `config/parameters.json`, not a rewrite.
- Never fabricate a conclusion the data doesn't support; when a file (e.g., the current HW/networking workbook) fails validation, say so in the UI rather than shipping a plausible-looking but ungrounded chart.
