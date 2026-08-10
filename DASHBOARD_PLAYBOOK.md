# Sector Inflection Dashboard Playbook (RenMac Breadth/Momentum Framework)

How the dashboards in this folder are built, how to refresh them with new
data, and how to spin up a new one for a different stock universe. Written
after building `US_Semi_Chip_Top_Dashboard.html` (semiconductors) and
`US_Software_Top_Dashboard.html` (software) — read this before touching
either.

**This is a two-sided framework, not a top-calling tool.** RenMac's original
note frames it as "Anatomy of a Chip Top" because that's the call semis
happened to be set up for. The underlying toolkit — breadth, moving-average
positioning, rate-of-change, new-high/new-low expansion — is symmetric: the
exact same metrics that flag a sector topping out (falling breadth, rolling
momentum, expanding new lows) flag a sector turning up when read in mirror
image (rising breadth, troughing-then-rising momentum, expanding new highs).
A sector showing more stocks reclaiming their 20/50-dma, breadth climbing out
of an oversold zone, and ROC troughing and turning positive is showing a
**positive inflection** — the bullish twin of everything below, not a
different framework.

## What exists

| Sector | Price file | Build script | Template | Output | Stock-detail panel |
|---|---|---|---|---|---|
| Semis | `US semi stocks 5y price and volume <date>.xlsx` — `Price` + `Volume` sheets, trimmed to the trailing ~1yr window (SMH/SPY benchmark columns — see Gotchas) | `build_dashboard.py` | `dashboard_template.html` | `US_Semi_Chip_Top_Dashboard.html` | Yes |
| Software | `US software stocks <date>.xlsx` | `build_software_dashboard.py` | `dashboard_template_software.html` | `US_Software_Top_Dashboard.html` | Not yet |
| US Banks | `US bank stocks <date>.xlsx` | `build_bank_dashboard.py` | `dashboard_template_bank.html` | `US_Bank_Stock_Dashboard.html` | Not yet |
| CHN Semis | `CHN semi stocks price <date>.xlsx` + `CHN Semi stock mapping.xlsx` (ticker resolution — see Gotchas) | `build_chn_semi_dashboard.py` | `dashboard_template_chn_semi.html` | `CHN_Semi_Stock_Dashboard.html` | Not yet |
| SP100 (broad market) | `SP100.xlsx` — `Price` sheet (one column per ticker) + `Mapping` sheet (Sector/Industry Group/Beta/Fwd PE, CapIQ export — see Gotchas) | `build_sp100_dashboard.py` | `dashboard_template_sp100.html` | `SP100_Sector_Dashboard.html` | Yes |
| Semis, 5-yr regime | `US semi stocks 5y price and volume <date>.xlsx` — `Price` + `Volume` sheets (calendar days, SMH/SPY benchmark columns — see Gotchas) | `build_renmac_dashboard.py` | `dashboard_template_renmac.html` | `US_Semi_RenMac_Regime_Dashboard.html` | Not yet |

Both semis dashboards now share the same source workbook (`US semi stocks 5y price and volume
<date>.xlsx`) — the 1-yr chip-top build trims it to a tail window, the 5-yr regime build uses
it whole. Both also carry, as of the 20260807 refresh: composite MACD(12,26,9) and RSI(14),
on-balance volume, and an SMH/SPY benchmark-comparison section (absolute rebased + relative
strength). The chip-top per-stock panel additionally carries per-ticker MACD/RSI/volume and a
"Compare vs" selector (EW basket / SMH / SPY) for the relative-price chart.

**The 5-yr semi dashboard is the analytical successor to the 1-yr chip-top one.** It scores
the seven weighted pillars of `RENMAC_TIMING_FRAMEWORK.md` (read that file first — it is the
"how to read" companion to this "how to build" one), adds volume, and classifies a **regime
history** across every session since Aug-2022 rather than only the latest tape. The four
implementation rules it had to learn the hard way — rebalance the composite, read structure
off a trailing window, debounce the label not the score, and apply "peaks beat levels" in the
code — are written up in that file's implementation section.

**SP100 extends the framework two ways** a single-sector file can't: it runs the
regime check (see below) independently on each GICS sector and industry group
via `group_rollup()`/`classify_regime()` (building each group's own equal-weight
sub-composite, gated on ≥3 full-history members), and it cross-cuts the universe
by 1-yr beta and forward P/E (quartile buckets + scatter + Pearson correlation
against 12-mo return) using the Mapping sheet's fundamentals columns. When a
new universe's workbook ships a Mapping/fundamentals sheet, prefer copying
`build_sp100_dashboard.py`'s `group_rollup`/`classify_regime`/`quartile_buckets`
pattern over `build_bank_dashboard.py`'s (sector-blind) one.

Each is a standalone, zero-dependency HTML file: the build script computes
everything in Python, serializes it to one `const DATA = {...}` blob, and
injects it into the template at the `/*__DATA__*/` marker. All charts are
inline SVG drawn by vanilla JS in the template — no chart libraries, no
network calls, works from `file://`.

Both existing dashboards happened to land in topping/deteriorating territory,
so their pillar language and event-detection code (`crack1_i`, `retest_i`,
`climax_i`...) are written bearish-first. That's a fact about semis and
software in this window, not a property of the framework — see below before
assuming a new sector will look the same.

## The framework, both directions

Source: `Renmac Technical Setup on Semiconductor stocks.txt` — Jeff DeGraaf /
RenMac's five-pillar structure. Below, each pillar's original (bearish/
topping) reading is paired with its mirror-image (bullish/bottoming) reading.
Both are the same computation; only the direction of the extremum and the
sign of the threshold flip.

| # | Pillar | Bearish reading (topping) | Bullish reading (positive inflection) |
|---|---|---|---|
| 1 | Extension / capitulation | Stocks/sector doubling within ~2 years — late-cycle excess | A large share of stocks near/at multi-month lows, sharply down over the window — capitulation-level excess to the downside, the fuel for a base |
| 2 | Structural turn | Peak → first crack (≥8% drop in 5 days) → failed retest (lower high) → climax (worst 5-day drop) → failed bounce → new lows | Trough → first thrust (≥8% rally in 5 days) → successful retest (higher low holds, doesn't undercut the trough) → breakout above the down-trendline/50-dma → follow-through with new highs expanding |
| 3 | Momentum | Composite 65-day ROC rolling over from a positive extreme; momentum-quintile spread compressing from a wide extreme | 65-day ROC troughing from a negative extreme and crossing back above zero; quintile spread *widening* again as leadership differentiates on the way up (early-cycle dispersion, not distribution) |
| 4 | Breadth | % of stocks above 20/50-dma falling into (and getting stuck in) RenMac's 2–15% oversold zone; new/period lows expanding on "rallies" = distribution | % above 20/50-dma rising out of an oversold zone and holding above it, with new/period highs expanding = accumulation — the breadth-thrust pattern that historically marks the start of a new leg |
| 5 | Sentiment / flows | ETF inflows in a top percentile despite drawdowns = FOMO dip-buying | Outflows/redemptions at a bottom percentile despite the sector holding up = capitulation by holders, contrarian-bullish | Not testable from a price-only file either way — always mark `not-testable` unless flow data is actually present. |

The code changes needed to detect the bullish sequence are small and
mechanical: swap `max`→`min` (peak→trough), flip the sign on the crack/thrust
threshold (`-8%` → `+8%`), and swap "retest stays below the high" for "retest
holds above the low." It is *not* a different algorithm — resist the urge to
invent new logic; mirror the existing functions in `build_dashboard.py`
(`peak_i`/`crack1_i`/`retest_i`/`climax_i`/`bounce_i`/`ma_break_i`) rather
than writing bespoke bottoming detection from scratch.

## Determine the regime before writing any narrative

Don't decide in advance whether a new sector is "topping" or "bottoming" —
check what the data actually shows first:

1. **Where does the composite's extremum in the window sit relative to now?**
   A high behind it → possible topping setup. A low behind it → possible
   bottoming setup. Neither (still grinding toward one) → say so, don't force
   an inflection story onto a trend that's just continuing.
2. **Breadth trend over the trailing 4–8 weeks** — climbing out of an
   oversold zone (improving) vs. falling into or stuck in one
   (deteriorating).
3. **ROC direction** — crossing up through zero (improving momentum) vs.
   rolling over from an extreme (deteriorating).
4. **New-highs vs. new-lows** — which one is actually expanding right now?
   This is usually the cleanest tell.

That gives four possible regimes — use whichever the numbers support, not
whichever is more dramatic:

- **Uptrend continuation** — near/above prior highs, breadth healthy, ROC
  positive and stable. No inflection signal either direction; report that
  plainly instead of manufacturing a top or bottom call.
- **Topping** — peak behind, crack/retest/climax sequence present, breadth
  falling, ROC rolling over. (What semis and software both showed as of
  25-Jul-26.)
- **Positive inflection / bottoming** — trough behind, thrust/retest/breakout
  sequence present, breadth rising out of oversold, ROC troughing and turning
  up. Flag this explicitly as the constructive mirror case — don't bury a
  genuine breadth-expansion story under top-calling pillar names.
- **Downtrend continuation** — lower lows, breadth weak and falling, ROC
  negative and falling. Still deteriorating, no basing signature yet.

## Refreshing an existing dashboard with new data

1. Drop the new `.xlsx` in this folder (same column layout: `Date` + one
   column per ticker, one row per trading day).
2. **Before rerunning the script, sanity-check the file** — this bit us once
   (see Gotchas below):
   ```python
   import openpyxl, hashlib
   wb = openpyxl.load_workbook("<new file>.xlsx", read_only=True, data_only=True)
   rows = list(wb.worksheets[0].iter_rows(values_only=True))
   print(rows[0])       # header — do the tickers match the sector you expect?
   print(rows[1], rows[-1])   # first/last row — sane dates and prices?
   ```
   If the ticker list doesn't match the sector (e.g. semis tickers in a file
   named "software"), stop and flag it — don't build on it.
3. Update the `XLSX = ...` filename constant at the top of the relevant
   `build_*.py` if the filename changed.
4. Run `python build_dashboard.py` or `python build_software_dashboard.py`.
5. Read the console summary (peak/trough date/value, drawdown or rally %,
   breadth, doubled count, pillar statuses) and sanity-check it against what
   you'd expect before treating the output as done. Check whether the regime
   itself has flipped since the last build (e.g. a former topping candidate
   now showing breadth expansion) — the pillar language may need to flip with
   it, not just the numbers.
6. Open the output HTML in a browser (or headless-screenshot it, see
   Verification below) — don't just trust that the script exited 0.

## Adding the individual-stock detail panel

`build_dashboard.py` / `dashboard_template.html` (semis) carry a "Individual
stock detail" section: a ticker dropdown driving four charts per stock —
absolute price with 20/50-dma, price relative to the equal-weight basket
(base 100) with its own 20/50-dma, and 20-day rolling z-scores of daily
returns (absolute, and relative to the basket). Port this to another
dashboard (software, banks, CHN semis) when asked, rather than reinventing it:

**Build script side** (`build_<sector>_dashboard.py`):
1. Copy the helpers from `build_dashboard.py` verbatim: `daily_ret`,
   `rolling_z` (20-day trailing window, requires a *full* window of 20 valid
   points, sample std with `len(w)-1` denominator, `None` when std is 0 or
   the window is short), `ema_from`/`macd`/`rsi`/`obv`/`rel_vol` (the
   MACD/RSI/volume technicals — restart their running state on any `None`
   gap rather than carrying a stale average across missing data), and
   `build_stock_panel(universe, vol, mas20, mas50, comp, bench, n)`.
2. Call `build_stock_panel(...)` right after `mas20`/`mas50` (the per-ticker
   20/50-dma dicts used for breadth) and `comp` (the equal-weight composite)
   already exist — it needs those plus `universe` (full+partial price dict),
   `vol` (per-ticker volume dict, `{}` if the sector's workbook has no Volume
   sheet — `build_stock_panel` degrades gracefully, per-stock `vol`/`volAvg20`
   come back `None`), `bench` (benchmark price dict, `{}` if the workbook has
   none — the per-stock `rel` dict then only carries the "EW basket" key) and
   `n` (day count). Every dashboard's build script already computes
   `universe`/`mas20`/`mas50`/`comp` for the breadth/composite sections, so
   this is a same-shape addition, not new plumbing.
3. Add `"stockPanel": {"tickers": sorted(stock_panel), "bellwethers":
   sorted(BELLWETHERS & set(stock_panel)), "series": stock_panel}` to the
   `data` dict. Reuse each dashboard's existing `BELLWETHERS` set for the
   dropdown's default selection (falls back to the first ticker
   alphabetically if none of the bellwethers made it into the universe).
4. Relative price (`rel_to()` inside `build_stock_panel`) is `(px/px_first) /
   (base/base_first) * 100` for each benchmark in `{"EW basket": comp,
   **bench}` — rebased to 100 at *that stock's* first valid date, not the
   benchmark's start date, so partial-history tickers (late IPOs, etc.) still
   get a meaningful relative series from wherever their data begins. Each
   entry in the per-ticker `rel` dict carries its own `v`/`d20`/`d50`
   (20/50-dma of the ratio) so the front end can switch benchmarks without a
   rebuild.

**Template side** (`dashboard_template_<sector>.html`):
1. Add the `.stockSelWrap` CSS block (dropdown row) — copy from
   `dashboard_template.html`.
2. Add the HTML section: a `<select id="stockSel">` (+ `<select id="benchSel">`
   if the workbook has benchmark columns) inside a `.card stockSelWrap`, then
   a `.grid2` with `.card.chartCard` divs — `chStockAbs`, `chStockRel`,
   `chStockZAbs`, `chStockZRel` at minimum, plus `chStockMacd`, `chStockRsi`,
   and a full-width `chStockVol` (`style="grid-column:1/-1"`) if the sector's
   workbook carries volume. Place it wherever it reads best next to that
   dashboard's other per-stock content (semis put it right before "What the
   playbook implies next").
3. **Patch `chart()`'s resize listener before reusing it for a
   re-renderable panel**, if the template's copy doesn't already have this:
   the original `chart()` added a fresh `addEventListener("resize", ...)`
   on every call. That's harmless when each chart element is only ever
   rendered once, but the stock panel calls `chart()` again on every
   dropdown change against the *same* four elements, so the un-patched
   version leaks one resize listener per switch. Guard it:
   ```js
   function chart(el, cfg){
     el.__cfg = cfg; el.__render = () => render(el, cfg); el.__render();
     if(!el.__hasResize){
       el.__hasResize = true;
       addEventListener("resize", debounce(() => el.__render(), 150));
     }
   }
   ```
4. Copy the "individual stock panel" IIFE from `dashboard_template.html`'s
   script block: populate `#stockSel` from `DATA.stockPanel.tickers`
   (star-mark bellwethers) and `#benchSel` from `Object.keys(firstSeries.rel)`,
   define `renderStock(t)` calling `chart()` on each div with `s.px/dma20/
   dma50`, `s.rel[bk].v/d20/d50` (`bk` = the selected benchmark), `s.zAbs`,
   `s.zRel`, `s.macd.line/signal/hist`, `s.rsi`, and — guarded on `s.vol`
   truthiness, since a partial-coverage ticker's volume column can be empty —
   `s.vol`/`s.volAvg20`. Default the ticker to a bellwether (`NVDA` in semis —
   swap for that sector's flagship name) or `tickers[0]`, and wire `onchange`
   on both selects.
5. Rebuild and verify per the standard Verification section below — the
   dropdown switch is the one interaction worth explicitly re-screenshotting
   (see `check_stockpanel.py`-style Playwright script: load, screenshot,
   `select_option`, wait, screenshot again, assert no `pageerror`s), since
   it's the only place in these dashboards where a chart is re-rendered
   against a live DOM element rather than drawn once at load.

## Building a new dashboard for a different universe

1. **Get a ticker universe.** A market-cap file (name/cap/ticker, possibly
   with many exchange-listing variants per company — dedupe by name, keep
   max cap) is useful for picking bellwethers but is *not* a substitute for
   an actual daily-close price file with one column per ticker.
2. **Copy, don't rewrite from scratch**: `cp build_dashboard.py
   build_<sector>_dashboard.py` and `cp dashboard_template.html
   dashboard_template_<sector>.html`, then adapt:
   - `XLSX`, `TEMPLATE`, `OUT` constants.
   - `BELLWETHERS` — 8–10 of the largest/most-representative names. If a
     market-cap file only covers a subset of the universe (e.g. it was
     curated for a sub-theme like security software), don't force bellwether
     selection through it — use general knowledge of the sector's largest
     public names and just verify each ticker exists in the price header.
3. **Run the regime check (above) before choosing pillar logic or wording.**
   Don't assume any prior dashboard's conclusion carries over, in either
   direction. Compute each pillar's status from thresholds (see
   `p1_status`..`p4_status` in `build_software_dashboard.py` for the
   pattern), and make sure the thresholds are checked in *both* directions —
   e.g. pillar 4's status shouldn't only ever test "is breadth in the
   oversold zone," it should also recognize "breadth just broke out of the
   oversold zone and is climbing," and label that constructively rather than
   defaulting to `not-confirmed`. Use a middle `weak` chip status (amber)
   between `confirmed` and `not-confirmed` — real data rarely lands cleanly
   on one side, in either regime.
4. **Generalize the event/pillar prose, and match its polarity to the
   regime.** Don't copy specific factual claims from another sector's
   narrative (e.g. "Samsung's blowout earnings", "SMH inflows in the 90th
   percentile") into a new sector's dashboard — those are specific, sourced
   claims about semis, not generic framework language. Keep event text
   limited to what the price data itself shows, and only cite a companion
   sector's numbers explicitly for contrast (e.g. "-13% vs semis' -31%
   drawdown"), sourced from that dashboard's own verdict. If the new sector
   is actually showing a positive inflection, the event timeline and pillar
   headlines should read that way (trough / thrust / breakout / breadth
   expansion) — don't leave bearish pillar names ("Bubble signal", "Topping
   structure") on a dashboard whose data shows the opposite.
5. **Look for a composite-distorting subgroup.** The most valuable insight in
   the software build wasn't the RenMac pillars — it was noticing the
   equal-weight composite was flattered by 10 crypto-miner/treasury tickers
   that sit in the sector's GICS bucket but trade on bitcoin, not the
   sector's fundamentals. Stripping them out revealed the other ~90% of the
   universe was down double digits on average. Always eyeball the
   stock-level table sorted by return for this kind of bimodal split — in
   either direction (a handful of names driving an otherwise-flat composite
   up just as easily as down) — before shipping a single composite number as
   "the" story. If you find one, split it out explicitly (see `split`
   computation + the `cry` flag / crypto badge in
   `build_software_dashboard.py` and its template) rather than leaving it
   buried in a sortable table.
6. Wire the new file into `dashboard_template_<sector>.html`'s footer/source
   line and cross-link it to any companion dashboard.

## Gotchas hit so far

- **Mislabeled source file.** `US software stocks 20260725.xlsx` was
  originally byte-identical to the semi price file (wrong data under the
  right filename). Caught by hashing/diffing against the semi file before
  building. Always spot-check headers, don't trust filenames.
- **Excel serial dates leaking through.** One row's date cell came through as
  a raw int (`46227`) instead of a `datetime` (last trading day, apparently a
  formatting-only cell). `openpyxl`'s `r[0].strftime(...)` crashes on this.
  Fix: convert defensively — `datetime(1899,12,30) + timedelta(days=v)` if
  the cell is numeric instead of a `datetime`.
- **Trailing blank rows.** The xlsx had a handful of fully-`None` rows after
  the last real trading day. Filter with `[r for r in rows[1:] if r[0] is
  not None]` before doing anything date-based, rather than assuming every
  row past the header is real data.
- **Mid-period delistings (M&A / going-private).** Several tickers (e.g.
  Informatica, Olo, Couchbase in the software file) stop returning values
  partway through the window because they were acquired. These land in the
  existing `full`/`partial`/`dropped` coverage-threshold buckets naturally —
  they get excluded from the full-history composite (correctly) but still
  show up in the stock table with their last traded price. No special
  handling needed beyond leaving the existing coverage-based classification
  alone; don't be alarmed by <95% coverage on names you don't recognize —
  check if they were acquired before assuming bad data.
- **Anchoring a correction/washout event to the wrong local extremum.** When
  pairing a breadth-washout date with "the price low it coincided with," search
  a small window *around* the washout date for the local composite minimum —
  don't scan the whole post-trough range for the global min. The global min
  over a long range can land on an unrelated earlier dip that has nothing to
  do with the washout, producing a nonsensical pairing (e.g. citing a November
  price low next to a March breadth washout). Hit this building the bank
  dashboard; caught it via the screenshot-verification step before shipping,
  not by inspection of the code.
- **A "corrected" file can relocate bad data instead of fixing it.** After
  flagging bad-data tickers and asking for a fix, don't assume the fix worked
  and move on — re-run the full anomaly scan (low distinct-value count,
  >100% single-name return) on the new file and diff the flagged list against
  the prior build's. In one case the previously-bad tickers got real data,
  but the *exact same* corrupted value blocks reappeared one column over
  under different (previously clean) tickers — a column-shift/paste artifact
  in the source pipeline, not a clean re-pull. Net corruption count was
  unchanged, just moved. Also re-check sheet order and ticker-list membership
  on any refresh of a "same-named" file — both drifted between builds here
  (an add-in cache sheet reordered ahead of the data sheet; one ticker was
  dropped and another added). Read the sheet by name, not `worksheets[0]`.
- **Bad data disguised as a real outlier.** One ticker (`WAL` in the bank
  price file) flatlined at round numbers for months at a time then jumped
  ~10x, producing a fake "+900% return, doubled" bubble signal that would
  have distorted both the composite level and the pillar-1 bubble-signal
  count. Not a real trading pattern -- real daily closes don't sit on exact
  round numbers for weeks. Eyeball the top of the sorted-by-return stock table
  for this before trusting a "doubled" or extreme-return roster; exclude the
  ticker at load time (with a documented reason) rather than letting it flow
  through silently.
- **A CapIQ Mapping/fundamentals sheet sits behind extra header rows, same as
  the price gotcha below but worse.** `SP100.xlsx`'s `Mapping` sheet has a
  blank row 0, the human-readable header on row 1, CapIQ's internal field
  codes (`SP_ENTITY_NAME`, `IQ_SECTOR`, `SP_BETA1YR`, ...) on row 2, and a
  units row (`Current`, `NTM`, ...) on row 3 -- real data starts row 4. Always
  print the first several rows before assuming row 1 is the last header row.
- **CapIQ "NA"/"NM" placeholders leak through as literal strings, not None.**
  Beta and forward-PE columns can contain the Python string `'NA'` (e.g. a
  same-year spinoff with no 1-yr beta yet) or `'NM'` ("not meaningful", e.g.
  negative-earnings forward PE) sitting in an otherwise-numeric column.
  `isinstance(v, (int, float))` before using the value, or arithmetic/sort
  ops throw `TypeError` comparing `str` to `int`.
- **A ticker's price feed can go stale mid-window without being a delistling.**
  Two SP100 names (`HONA` -- Honeywell's 2026 aerospace spinoff entity, and
  `BNY` -- Bank of New York Mellon, a decades-old NYSE listing) both stop
  returning values partway through the year (HONA after ~6 weeks, BNY around
  Feb 2026) despite being live, actively-traded stocks -- confirmed by the
  anomaly scan below finding no flatline/round-number pattern, just real
  prints that stop. This is a stale/incomplete data pull, not a corporate
  action; it still falls into the existing partial-coverage bucket
  correctly, but call it out by name in the footer (`STALE_DATA` dict in
  `build_sp100_dashboard.py`) rather than let a reader assume the ticker
  delisted.
- **A price file can be CALENDAR days, not trading days.** `US semi stocks price and volume
  5y 20260731.xlsx` ships 1,827 rows for 5 years (365/yr, not 252/yr): weekends and market
  holidays are present with the prior close *and the prior volume* forward-filled. Every
  window in these dashboards is defined in trading days, so left uncorrected a "20-dma" spans
  ~14 real sessions, a "200-dma" ~138, and each weekend counts Friday's volume three times.
  Detect and drop them by flagging rows where >95% of the universe repeats the prior row's
  price **and** volume — on this file that recovered exactly the 522 weekend rows plus the 50
  genuine US market holidays (Labor Day, Thanksgiving, Good Friday, Juneteenth, ...), leaving
  1,255 rows = 251/yr. Sanity-check `rows / years` on any new file before trusting an MA.
- **Volume must not be forward-filled.** `ffill_small_gaps` is right for price and wrong for
  volume: a filled volume print fabricates activity that never happened. Treat missing as
  missing. Zero is real data (a halt, or a thin name that didn't trade) and is not the same
  as `None`.
- **Normalised-price composites drift away from equal weight over multi-year windows.**
  `build_dashboard.py`'s `ew`-style composite (average of prices rebased to a common start)
  is fine over 12 months. Over 5 years a name up 20x comes to dominate an index still called
  "equal-weight" — which silently reintroduces the concentration the framework is supposed to
  detect, and moved the detected composite peak by a month. For any window beyond ~18 months
  use a daily-rebalanced index (chain the cross-sectional mean of daily returns) as in
  `build_renmac_dashboard.py`.
- **Windows console encoding.** `print()`-ing em dashes / non-ASCII through
  `cmd`'s default `cp1252` codepage raises `UnicodeEncodeError` or prints
  `�`. Doesn't affect the written file (opened with `encoding="utf-8"`),
  only console output — don't mistake a garbled `print` for a broken file;
  verify the actual file content if it matters (`open(..., encoding="utf-8")`
  read-back, or `PYTHONIOENCODING=utf-8` on the command).

- **Header row holds raw vendor IDs instead of tickers.** The CHN semi price
  file's header row (and even its shared-strings table) contained no ticker
  or company text at all -- just numeric S&P Capital IQ entity IDs (e.g.
  `5264740`), confirmed via the workbook's `IQ_*` defined names (the CapIQ
  Excel add-in). This happens when a CapIQ/FactSet-linked sheet gets pasted
  as values and the row that normally shows the resolved name/ticker (sitting
  above the raw ID row) doesn't come along. Don't guess company identities
  from price patterns -- ask for a mapping file (Entity Name / Entity ID /
  Ticker) and join on the ID. Watch for an extra field-code row in CapIQ
  mapping exports (e.g. `SP_ENTITY_NAME`, `SP_ENTITY_ID`) sitting between the
  human-readable header and the actual data -- skip it explicitly, don't
  assume data starts at row 2.
- **A GICS/RBICS industry bucket can smuggle in an unrelated sub-sector.**
  9 of 162 names in the CHN semi mapping file's "Semiconductors and
  Semiconductor Equipment" bucket were actually solar/polysilicon companies
  (JA Solar, GCL Technology/System Integration, Tongwei, LONGi, Trina, Xinyi
  Solar, Flat Glass) -- makes sense given polysilicon refining is
  upstream of both chip-grade and solar-grade silicon, but they trade on
  panel oversupply/ASPs, not the chip cycle. Same playbook-step-5 check as
  the software build's crypto-miner subgroup, but the *opposite* direction:
  those 9 names average -30% for the year with zero doublings, so including
  them drags the composite DOWN rather than flattering it up. Don't assume a
  composite-distorting subgroup always inflates the story -- check both ways.
- **±20% single-day moves on STAR Market/ChiNext names are real, not bad
  data.** Several CHN semi tickers showed repeated exact +20.0% (and -20%ish)
  daily jumps. On US boards that pattern would be the WAL-style flatline-then-
  jump red flag; here it's the daily price-limit band on STAR Market (688xxx)
  and ChiNext (300xxx) listings (±20%, vs. ±10% on the mainboard and no limit
  in Hong Kong). Distinguish the two by checking the *distinct-value count*
  over the window -- real limit-up days still produce a high number of
  distinct daily closes (low-to-mid 200s out of ~238 trading days here);
  a flatline artifact collapses that count sharply.
- **A sheet can carry TWO header rows, both with a blank column A — filtering
  on `r[0] is not None` before splitting off the header drops the header
  itself.** The 20260807 semis refresh added a "Day Close Price"/"Volume"
  sub-header row directly under the ticker row; both rows have `None` in
  column A (same as every weekend/holiday-none blank-row filter elsewhere in
  this codebase). `build_dashboard.py`'s old `load_prices()` did
  `rows = [r for r in ws.iter_rows(...) if r[0] is not None]; hdr = rows[0]`
  — filtering the None-first-cell rows *before* taking the header meant
  `hdr` silently became the first *data* row (prices), and every downstream
  "ticker" was actually a float. `build_renmac_dashboard.py`'s `grab()`
  already had the robust pattern — take `rows[0]` unconditionally as the
  header, filter only `rows[1:]` on a non-None first cell — because it was
  written for a CapIQ export that already had this shape. Always mirror that
  pattern for a new sheet, and print `hdr` (not just `rows[0]`) after any
  loader change to confirm it's ticker strings, not numbers.
- **A bipolar bar series (values crossing zero, e.g. a MACD histogram) needs
  `min(baseY, valueY)` / `abs(baseY - valueY)` for its SVG `y`/`height`, not
  `Y(value)` / `Y(baseline) - Y(value)`.** The chart engine's original
  positive-only bar code (`y:Y(v), height:Y(max(lo,0))-Y(v)`, used for
  `chLows`'s always-nonnegative counts) emits a **negative** `height`
  attribute for any bar below the baseline — an invalid SVG attribute that
  Chromium logs as a console error and silently fails to paint. Caught via
  the Playwright console-error check in Verification, not by eyeballing the
  screenshot (the missing bars didn't visually register as "wrong" at a
  glance). Fix once in the shared `render()` bar block, not per-chart.

## Verification before calling it done

Static HTML, no build step, so "done" means actually rendering it:

```python
# via the webapp-testing skill's Playwright pattern, file:// URL is fine
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 1000})
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto("file:///" + r"<path to output html>".replace("\\", "/"))
    page.wait_for_load_state("networkidle")
    page.screenshot(path="check.png", full_page=False)
    print(errors or "no JS errors")
```

Also parse the embedded `DATA` blob back out with `json.loads` on the
generated file to confirm the marker was actually replaced and the JSON is
valid, before screenshotting.
