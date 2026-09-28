# US_Stk_Dash — Stock Analytics Dashboard

Build a modular, multi-tab, static stock analytics dashboard deployable on GitHub Pages. It applies the RenMac breadth/momentum/regime framework (and future frameworks) across four stock universes: broad S&P 500 market internals, semiconductors, software, and hardware/networking.

## Read before building

1. `DASHBOARD_PLAYBOOK.md` — how the existing single-sector dashboards (`US_Semi_Chip_Top_Dashboard.html`, `SP100_Sector_Dashboard.html`, `build_dashboard.py`, `build_renmac_dashboard.py`, `renmac_score.py`) were built, and every data/charting gotcha hit so far. This is prior art for this project, not a different codebase — port its patterns (loaders, MACD/RSI/OBV/z-score helpers, stock-detail panel, regime classifier) into the new modular structure rather than reinventing them.
2. `RENMAC_TIMING_FRAMEWORK.md` — the seven-pillar scoring/regime model (extension, structural turn, momentum, breadth, sentiment, +2 quantitative pillars) and its four implementation rules (rebalance the composite, read structure off a trailing window, debounce the label not the score, "peaks beat levels"). Primary framework, not the only one — the calc engine must let new frameworks/indicators plug in alongside it.
3. `Renmac Technical Setup on Semiconductor stocks.txt` — the narrative source for pillar language (topping direction). `DASHBOARD_PLAYBOOK.md` already documents the mirror-image bullish/bottoming reading of every pillar — implement both directions from day one, never bearish-only.
4. `US_Semi_Chip_Top_Dashboard.html` — the reference layout/chart suite for **every individual-stock panel** in this project (Tabs 1–4): price + 20/50-dma, relative-to-benchmark price + its own 20/50-dma, MACD, RSI, OBV/volume, 20-day rolling z-score (absolute + relative), benchmark selector, technical-signal summary. Treat this as the canonical per-ticker template — semis, software, and hardware/networking tabs all reuse it identically.
5. `SP100_Sector_Dashboard.html` — the reference for sector/industry-group rollups: per-group regime classification, breadth, quartile buckets, cross-sectional scatter. Basis for Tab 1's sector/industry-group views.
6. `Fab5 Market Dashboard 20260906.html` — the reference for the **fab5 page infographic**. Hand-authored, no generator, no data model: read it for its *organisation* (stat tiles, delta banner, layered theme read, per-house attribution, scenario probabilities), not its markup. Its CSS collides with `dashboard.css` on `.chip`, `.call`, `.src` and `.stat`, and `--s1`/`--s2` hold different values in each — see *Page infographics*.
7. `narrative_dashboard_2026-08-31_to_09-05.html` — the reference for **Tab 6**. This copy is downstream; `Cowork Playground/WSJ/` owns the build and overwrites it. Read the generator (`WSJ/build_narrative_dashboard.mjs`) alongside it: its citation resolution and its pinned-count invariants are the parts worth porting, and its global-regex count checks are the hazard worth knowing about.

## Current vintage: 20260927 (measured 2026-09-27)

`data/raw` holds every vintage ever delivered and `loaders.resolve_input` takes the newest
date-stamped file per **anchored** stem, so a refresh is a file copy, not a config edit. Old
vintages are never deleted — `US semi stocks 5y price and volume 20260807.xlsx` is load-bearing
for the regression gate (see below).

**The 5-year window rolls; it does not extend.** This is the single most important thing to know
about a refresh here. Vintages so far: 20260807/09 = 1,255 days over `2021-08-09 .. 2026-08-07`;
20260816 = 1,254 over `2021-08-17 .. 2026-08-14`; 20260907 = 1,255 over `2021-09-07 .. 2026-09-04`;
**20260927 = 1,255 over `2021-09-27 .. 2026-09-25`**. Both ends move every time. Any test or golden
that pins a date or a grid length is therefore vintage-locked by construction.

Measured on the 20260927 files, identically across all **six** workbooks:

```
raw rows      1827
- weekends    -522
- holidays    -50
= trading     1255        (251.3/yr)  2021-09-27 .. 2026-09-25
```

**The export was taken on Sunday 2026-09-27.** The grid's last two calendar rows are Saturday
09-26 and Sunday 09-27, so the weekend drop alone removes them, `lastDate` is Friday 09-25 and the
holiday count stays at **50**. **If a future refresh ever produces a `lastDate` equal to the
export's own weekend or holiday stamp, that placeholder survived and the build is wrong.** The
expectation is asserted in `config/parameters.json → calendar.expected`, which must be re-measured
on every refresh rather than carried forward.

What moved on this refresh, all reported by `validate_all.py` rather than inferred:

- **`CVX` is newly broken in the S&P export** — a constant 27.375 for all 1,255 sessions with
  volume pinned at 416,100 (`CONSTANT_SERIES`, fatal), where the 20260907 export carried a normal
  97 → 208 series. Excluded in `config/universes.json` with that reason; drop the exclusion once a
  vintage prints a real series again.
- **`BNY` is fixed** — 52.63 → 150.15 with normal volume — so its wrong-metric exclusion was
  removed. `D` (constant 15) and `COR` (0.0018) are still wrong-metric and stay excluded. The S&P
  universe is 495 scored names either way (one out, one in).
- The ten terminal flatlines are unchanged (eight software deal-pinned names + `SKYT` + `IPEU`),
  as are `COVERAGE_DROPPED` (`FDXF`, `HONA`, `CBRS`, `OCTV`) and `BASKET_MEMBER_ABSENT` (`CBRS`,
  `MBLY`, `RTEC`). `AVB`'s row-2 label now reads `#INVALID COMPANY ID` — cosmetic, data passes.
- **Two new universes, first delivery** — Biotech (`US Biotech stocks 5y price and volume`, 117
  scored) and Pharma (`US pharma stocks 5y price and volume`, 48 scored). See *Tabs* 5–6.

Regime calls on this vintage: all six universes read **Late-cycle topping** — market internals
−60.0 (b20 29.7%), semis −5.0 (b20 90.6% — the label is debounced, the score has recovered),
software −65.0, hardware & networking −5.0, biotech −70.0, pharma −37.5.

## Input data (original delivery, as of 2026-08-09 — historical record, not the current inputs)

The dated filenames below are the files **as first delivered**, kept because the notes column
records what was wrong with each one and how it was resolved. They are not the tab inputs: those are
resolved by anchored stem to the newest vintage in `data/raw` (see *Tabs*). Every shape, gotcha and
exclusion in this table is re-checked on each refresh rather than carried forward.

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

Tab inputs are named below by their **anchored file stem**, never by a dated filename.
`loaders.resolve_input` selects the newest date-stamped file matching the stem, so a refresh is a
file copy rather than a config edit. (The dated filenames in the *Input data* table above are the
historical record of the original delivery, not the current inputs.)

1. **Market Internals** — `SP500 5y price and volume` + `SP500 industry groups.xlsx`, styled after `SP100_Sector_Dashboard.html`. Sector/industry-group performance, breadth/leadership/participation/momentum/relative-strength trends, top/bottom performers per group, absolute + relative performance across configurable horizons, SPY as default benchmark, a stock selector reproducing the full `US_Semi_Chip_Top_Dashboard.html` per-ticker panel for any S&P 500 name.
2. **Semiconductor Stock Dynamics** — `US semi stocks 5y price and volume`, direct port of `US_Semi_Chip_Top_Dashboard.html` (layout, charts, indicators, signals, conclusions). Ticker + benchmark selector, SPY default.
3. **Software Stock Dynamics** — `US software stocks 5y price and volume`, same per-stock framework/chart suite as Tab 2. Ticker + benchmark selector, SPY default, technical-signal summaries, relative-performance analysis.
4. **Hardware & Networking Stock Dynamics** — `US hw networking stocks 5y price and volume` (validate first — see table above), same per-stock framework as Tab 2. Ticker + benchmark selector, SPY default, technical-signal summaries, relative-performance analysis.

5. **Biotech Stock Dynamics** — `US Biotech stocks 5y price and volume` (added 20260927), same per-stock framework as Tab 2. The workbook carries **XBI** as an extra column, used as the default benchmark (not a member). `A950160` (Kolon TissueGene's KOSDAQ listing, priced in won on the Korean calendar) is excluded at load time. Sub-baskets are an editorial modality split — Genetic medicine (lead), Oncology (confirm), Large-cap commercial (narrowing), plus unscored Tools & diagnostics, Vaccines & infectious, Metabolic & cardio; ~48 names sit in no basket (`BASKET_UNASSIGNED`, a warning by design). Real one-day binary-event moves (MDGL, JANX, SMMT, SRRK, KOD, AMLX, AVTX, OBX…) are kept — they are data, not errors.
6. **Pharma Stock Dynamics** — `US pharma stocks 5y price and volume` (added 20260927). **XLV, IHE, XHE** ride as extra columns and are benchmarks (XLV default). `GTII` is excluded: a sub-penny OTC quote (0.0001 low, 44 single-day moves beyond +200%/−80%) that would wreck the daily-chained EW composite by ~240 points in a single session. Baskets: Clinical-stage (lead), Specialty & generics (confirm), Big pharma (narrowing — in practice one GLP-1 name), Animal health, Royalty.

**Sector-ETF benchmarks.** `universes.json → benchmarkSource.extra` pulls XBI from the biotech workbook and XLV/IHE/XHE from the pharma workbook into `benchmarks.json`, joined **only when that workbook's trading grid is identical** to the primary (semis) source; a differing grid lands in `benchmarks.json → skipped` rather than being realigned. `validators.cross_workbook_identity` treats those ETFs as benchmarks, like SPY/SMH.

All six tabs share one calculation engine, one chart component library, and one interpretation layer — a tab is a config (which workbook(s), which universe, which sector-mapping file if any) plus a thin page assembling shared components, not a fork of the code.

7. **Fab5 Cross-Source Read** — a **page**, not a universe. There is no workbook, no composite and
   no regime. It renders a hand-authored reading of `Fab5_Cross_Source_Synthesis_20260927.md` —
   **Run 7**, 42 reports across 7 research houses, 7 – 27 Sep: the recommendation (“own contracted,
   self-funded scarcity; underweight whatever must be refinanced or re-priced; hedge with options,
   not bonds”) and its three instructions, twelve reads grouped by the four-layer read (each
   measured against what Run 6 predicted: 5 confirmed, 3 contradicted, 1 unresolved, 3 new),
   cross-source agreement beside the twelve-item conflict registry, the full 32-row signal board
   (#32 compute-rent vs token-price scissor and #33 frontier-lab funding added), near- and
   medium-term scenarios, the dated calendar, and 45 ticker lines (36 joined live, 9 external).

   **The distinction that governs its design:** every other tab renders *measurements*, this one
   renders *claims*. So the chip means something different here — it carries the **source house and
   an evidence grade (a–d)**, not a test result, and the claim text stays plain prose. The only
   measured content on the page is the live technical strip on each named ticker, and that is
   **read verbatim** from the same `data/processed/<universe>/` payload the four dashboard tabs
   render, joined at build time. `test_render.py::check_strip_agreement` asserts field-by-field that
   it is a copy, because a page that computes its own prices is a second and quietly divergent
   source of prices.

   Content lives in `data/insights/fab5_<date>.json` — a **hand-maintained input**, sibling to
   `data/raw`, never in `data/processed`. `build_fab5.py` resolves the **newest** one, so a content
   refresh is a file drop rather than a code edit; the current file is `fab5_20260927.json` at
   schemaVersion 2 (Run 6's `fab5_20260906.json` is kept beside it). The source markdown is prose and cannot be honestly parsed. Every number in the
   JSON must trace to a line in the source document.

   The page also carries a **top-of-page infographic** modelled on
   `Fab5 Market Dashboard 20260906.html` — see *Page infographics* below. The claim/evidence-grade
   content model, the direction tag and the live ticker strip are unchanged by it.

8. **News Intelligence** — a **page**, not a universe, ported from
   `narrative_dashboard_2026-08-31_to_09-05.html`. Like fab5 it renders **claims, not
   measurements**: the six sections (Key insights, Timeline, Conflicts, Signals, Action, Index),
   the citation convention, the signal-board and index filter chips, the `<details>` table views
   and the print rules are all preserved. The sections are built up-front and toggled with
   `[hidden]` behind a section nav, so a control has to be brought on screen before it can be
   clicked — which is why `test_render.py` switches sections before exercising a filter.

   **What is authored and what is generated.** The Key insights, Timeline, Conflicts, Signals and
   Action prose is hand-maintained in `data/insights/news_<date>.json`. The **Index and Sources
   sections are generated in full**, as are every article / publication / theme / citation count,
   from a copy of `narrative_dashboard_source_audit.json` placed under `data/insights/` — its
   `articles[]` records are already structured (`id`, `date`, `publication`, `title`, `url`,
   `bullets`, `theme`) and its `citations` object is keyed, so the 108 index rows are never
   hand-typed. This preserves the upstream generator's own contract: *the template carries every
   analytical claim; this script carries every number and every link.*

   **`Cowork Playground/WSJ/` is the source of truth for the reference.** That folder owns the
   briefs, `tpl/`, and the build (`sh tpl/assemble.sh` → `node build_narrative_dashboard.mjs`), and
   that build overwrites the assembled HTML. The copy sitting in this repo is downstream. The
   `news` page therefore consumes extracted JSON, **never the assembled HTML** — editing the local
   copy is orphaned work.

   The page carries a top-of-page infographic — see *Page infographics* below.

9. **September News Intelligence** (`monthly` page, `tabs/news-monthly.html`, added 2026-09-27) —
   a **sibling** of the weekly News page, not a replacement, transcribed from the 7-board
   `September News Intelligence.html` design canvas (a bundled export: its boards are gzip+base64
   pages inside a `__bundler/manifest`; the timeline and heatmap rows live in each board's
   `text/x-dc` component script). Sections: Overview, Timeline (six stories × four weeks, theme
   filter), Economy & rates, Geopolitics & energy, AI & tech, Business & finance, Intersections &
   outlook (flow diagram, ranking, exposure table, Q4 storylines, market-implied odds, catalyst
   calendar, 13-row source-conflict log).

   **Its citation contract differs from the weekly page's, deliberately.** The canvas cites by
   *outlet and date* (“WSJ · 25 Sep”) and has no per-article audit, so `build_monthly.py` fails on
   any Reported, Analysis or market-implied item that does not name a publication **and** a date,
   on a market-implied figure that does not name its market (CME, swaps, Kalshi…), and on any
   probability attached to an Our-read or Scenario item. Every claim renders with the canvas's kind
   chip (Reported / Analysis / Our read / Scenario / Market-implied).

   **Counts are generated, never typed.** `scripts/census_briefs.py --from 2026-09-04 --to
   2026-09-25` counts the brief files in `Cowork Playground/WSJ/` (each brief = one `# ` title +
   one `**Source:**` line) into `data/insights/monthly_census_20260925.json`: 558 briefs, 41 files,
   15 file dates, WSJ 258 / Bloomberg 158 / Barron's 141 / Reuters 1 — exactly the canvas's
   figures. `{{count:*}}` tokens in the content are filled from it, and the heatmap's
   briefs-per-day row is asserted against it. The heatmap's theme *shares* are the canvas's own
   keyword pass and are carried, not recomputed. Content: `data/insights/monthly_<date>.json`
   (newest wins); run the census in the same step as dropping a new month.

The three pages share the nav, the theme control and the design tokens with the six stock tabs, and
nothing else: they render claims, so they have no workbook, no composite and no regime.

## Analysis modules (all four stock tabs)

Two modules sit on every stock tab, between the individual-stock panel and the stock table. They
apply the WSJ reading of institutional footprints — support, resistance, up/down volume, and
accumulation/distribution — and they are **layered on** the RenMac engine, not a replacement for it.
Nothing here feeds the seven pillars, the composite or the regime ladder.

### (a) Institutional accumulation / distribution analysis

**Selector.** One control with three levels — Stock | Sector | Industry group. The level source
differs by tab and is the only per-tab difference:

| Tab | Sector / industry-group source |
|---|---|
| `market_internals` | `config/sectors.json` levels — `sector` (11), `industryGroup` (25), `industry` |
| `semis`, `software`, `hw_networking` | `config/parameters.json → subBaskets.<key>.baskets` — the cycle baskets are this universe's industry groups |

Group-level analysis runs the identical legs on the group's equal-weight composite and its summed
volume — so the group path is a different input series, not a different calculation.

**The composite exists; the volume series does not yet.** `summary.baskets[<group>]` ships
`n, scored, note, comp, rel`, and `summary.rollups[<level>][]` ships `comp` among its per-group
fields — neither carries volume, and `rollups` is `{}` on the three focused tabs, which group by
sub-basket rather than by sector map. So each group gains **one summed-volume array** in
`summary.json`, alongside the composite it already has: ~4–6 arrays per focused tab and ~36 on
`market_internals` (11 sectors + 25 industry groups). These are group-level series, not per-ticker
ones, so the payload rule below still holds — nothing is added to the 724 shards.

**Data definitions.** The workbooks carry `Day Close Price` and `Volume` and nothing else — **there
is no intraday high or low anywhere in this project**. Every definition below is therefore stated on
closes, and where the classical formulation uses a true range this is a documented proxy rather than
an approximation left unsaid.

| Term | Definition |
|---|---|
| Weekly bar | ISO week, Mon–Fri. `wkHigh` / `wkLow` = max / min of that week's daily **closes**; `wkClose` = the week's last close; `wkVol` = summed volume. Weeks truncated by the window edge are kept and flagged `partialWeek: true`. |
| Weekly close position | `wcp = (wkClose − wkLow) / (wkHigh − wkLow)`; `null` when `wkHigh == wkLow`. |
| Accumulation week | `wcp >= institutional.closeHighPct` **and** `wkVol >= institutional.volMult × avg(wkVol, institutional.wkVolWindow)` — a close near the top of the weekly range on above-average volume. |
| Distribution week | `wcp <= institutional.closeLowPct` and the same volume condition — a close near the bottom of the range on heavy volume. |
| Up/down volume ratio | `Σ vol[i] where ret[i] > 0` ÷ `Σ vol[i] where ret[i] < 0` over the trailing `institutional.upDownWindow` (50) **trading** sessions. Sessions with `ret == 0` join neither leg and are reported as `flatSessions`. Returns `null` below `institutional.minSessions` valid sessions. When down-volume is zero the value is reported as `>= institutional.ratioCap`, never as infinity. |
| Up/down bands | Four bands, exhaustive and non-overlapping, because `ratioBand` is a screener column and a rank key — a gap or an overlap would leave an implementer inventing one. `< 1 − neutralBand` **selling pressure** · `[1 − neutralBand, 1 + neutralBand]` **neutral churn** · `(1 + neutralBand, ratioStrong)` **moderate buying** · `>= ratioStrong` **strong buying**. With the defaults: `< 0.85` / `0.85–1.15` / `1.15–2.0` / `>= 2.0`. |
| Support / resistance | Close-based **volume-at-price**: bin the window's closes into `institutional.priceBins` equal-width bins across `[min close, max close]` and accumulate each session's volume into its bin. Bins above `institutional.hvnPercentile` of binned volume are high-volume nodes — **support** below the last close, **resistance** above it. Separately, close swing pivots (a local extreme over `institutional.pivotWin` sessions either side) recurring within `institutional.pivotTolPct` are emitted as tested levels. Every level ships `price`, `kind`, `volumeShare`, `tests`, `lastTouch`, `distancePct`. |
| Index distribution day | For a registered index series: `close[i]/close[i−1] − 1 <= −institutional.indexDropPct` (0.2%) **and** `vol[i] > vol[i−1]`. The accumulation mirror is computed and reported but never scored. A day expires after `institutional.expireSessions`, or when the index closes `institutional.expireGainPct` above its close on that day (`institutional.expireOnGain`, default true). |
| Cluster warning | `>= institutional.clusterCount` **live** distribution days inside `institutional.clusterWindow` sessions raises a broad-market warning banner on every tab, using the same banner mechanism as a validation finding. |

**Registered index series** — `institutional.indexSeries`, and it registers only what exists:

- `SPY` — the S&P 500 leg. Read from `benchmarks.json`, which must carry **volume as well as
  price**; see the build requirement below.
- `SMH` — the semiconductor complex, same treatment.
- Each universe's own `comp` + `totVol` from its `summary.json`, as the complex-level analogue of
  an index. Note that `totVol` is a summed **share count**, not dollar volume — that is the series
  as shipped and it is a stated choice, not an oversight.
- `QQQ` is registered with `available: false`. **No Nasdaq series exists in any of the four
  workbooks** — verified by header scan on the 20260907 vintage, which carries `SPY` and `SMH` in
  the semi and hardware exports and no benchmark at all in the S&P export. The page renders an
  explicit "no Nasdaq series in this export" state. It does not substitute a proxy and call it the
  index.

**Build requirement.** `pipeline.build_benchmarks` currently extracts price only, so
`benchmarks.json` has `series.SPY` / `series.SMH` and no volume. It must be extended to read the
`Volume` sheet for the same tickers and emit a `volume` object beside `series`. A benchmarks payload
without `volume` is a stale artefact: say so in the build log and render the index leg unavailable —
do not silently skip it.

**Signal card.** Five fields, in this order, for the selected stock or group:

| Field | Definition |
|---|---|
| `signal` | `Accumulation` / `Distribution` / `Neutral — churn` / `Insufficient data`, from the first-match ladder below. |
| `evidence` | The measured facts that fired the rung — ratio value and band, accumulation vs distribution week counts over `institutional.weekLookback`, nearest support and resistance with distance %, live index distribution-day count. Numbers only. |
| `trend` | Direction of the 50-day ratio over `institutional.trendLookback` sessions, plus the change in the accumulation/distribution week balance against the prior equal window. |
| `confidence` | `high` / `medium` / `low`, **with its reasons listed**. Inputs: history coverage, volume-data quality (no `NA` runs, not price-pinned at deal terms), sample size against `minSessions`, and whether the three legs agree. Never a percentage — a graded label carrying its own justification. |
| `implication` | Rendered **only** from `institutional.implicationTemplates`, keyed `signal × regime` and formatted with facts the engine measured. This is the same rule that governs `interpretation.eventTemplates`: prose comes from templates, so a claim the data does not support cannot be emitted. |

**Signal ladder** (`institutional.ladder`) — evaluated in order, first match wins, exactly like
`regime.ladder`. Never a weighted score. The default, config-editable:

| Rung | Gate |
|---|---|
| `Insufficient data` | any leg null — ratio below `minSessions`, no valid weekly bars, or coverage below `coverage.full` |
| `Distribution` | `ratio < 1.0` **and** `distWeeks > accumWeeks` over `weekLookback`; **or** a live index cluster on the tab's primary series |
| `Accumulation` | `ratio >= ratioStrong` **and** `accumWeeks > distWeeks` **and** no live cluster |
| `Neutral — churn` | everything else |

The ladder tests the ratio against `1.0` and `ratioStrong` **directly**, not against the four
display bands — so a ratio of 1.10 is "neutral churn" as a band and still fails the `Distribution`
rung. That is deliberate: the bands label a reading, the ladder decides a signal.

**"The tab's primary series"** is `vocabulary.<universe>.primaryBench`, which already exists in
`config/parameters.json` — `SMH` for semis, `SPY` for software, hardware and market internals. The
cluster gate reads that series' distribution-day count, so the same key drives the benchmark and the
index leg rather than a second, quietly divergent notion of "the index for this tab".

`institutional.implicationTemplates` carries at least one template per `signal × regime` cell. The
`Indeterminate` regime column defaults to the playbook's own wording — *"no regime signal — do not
force a trade"*.

**Charts** — all through the existing `charts.js` `render()` / `chart()`. No new library:

- Price with support/resistance bands overlaid (the `--band` token).
- Volume-at-price histogram beside it.
- 50-day up/down volume ratio, with reference lines at 2.0 and 1.0.
- Weekly accumulation/distribution markers as bipolar bars — note the bipolar-bar-height fix already
  documented in `charts.js`.
- Volume with **abnormal-volume markers**, driven by the existing `zscore.volAlert` (65-session,
  `abs: 2.5`, `trailing: 5`) and `relVol`. Reuse those thresholds; do not introduce a second
  definition of "abnormal".
- Index distribution-day count over `clusterWindow`, with the cluster threshold drawn.

**DOM hosts** — one block in each of the four `site/tabs/*.html`, between `Individual stock` and
`Stock table`: `<h2>Institutional footprint</h2>` containing `#instSel`, `#instSignal`, and the
chart divs `#chInstPrice`, `#chInstVap`, `#chInstUdv`, `#chInstWeekly`, `#chInstVolAlert`,
`#chInstIndexDist`.

### (b) Sector and industry stock screener

Ranks the members of the selected sector, industry group or basket on the module-(a) metrics, most
to least attractive.

**It is not a black-box score.** Every column that decides the ordering is on screen: `signal`,
50-day up/down `ratio` and its `ratioBand`, `accumWeeks` and `distWeeks` over `weekLookback`,
`netAccumWeeks` (= `accumWeeks − distWeeks` over the same window), latest `wcp`,
`distToSupportPct` and `distToResistancePct`, `relVol`, 65-day ROC, RSI, regime, and `confidence`.

**Rank definition.** An ordered lexicographic comparison over `institutional.screenerRank` — a
configured list of `(metric, direction)` pairs where each metric is **bucketed into bands first**,
so a reader can see which band decided a row's position. A `rankWhy` cell names the deciding band.
There is no hidden weight vector. The shipped default, config-editable:

```
screenerRank: [ [signal, desc], [ratioBand, desc], [netAccumWeeks, desc],
                [distToSupportPct, asc], [relVol, desc] ]
```

Band edges are reused from the same `institutional.*` keys rather than restated. Any tie surviving
the whole list breaks **alphabetically by ticker**, so the ordering is reproducible run to run.

**Filters** — signal, confidence, band, minimum average volume, and an exclude toggle for
price-pinned and partial-history names. Columns are sortable. Extend the existing `#stockTable`
pattern in `tabs.js` rather than writing a second table renderer.

**Payload rule.** The screener is computed **server-side** and emitted as one `screener` array per
universe inside that universe's `summary.json` — scalars only, at most ~120 rows of ~30 numbers.
Per-ticker chart series stay **client-derived** from the shard's `px` and `vol`. This is the same
lever `DEPLOY.md` already applies to moving averages, and it is the reason the client never fetches
495 shards to rank a sector.

**DOM host** — `<h2>Sector screener</h2>` containing `#screenerCtl` and `#screenerTable`.

### Config: the `institutional` namespace

All thresholds live in `config/parameters.json` under a **new `institutional` key**, never in code:

```
institutional: {
  upDownWindow: 50, minSessions: 40, ratioStrong: 2.0, neutralBand: 0.15, ratioCap: 10,
  closeHighPct: 0.75, closeLowPct: 0.25, volMult: 1.25, wkVolWindow: 10, weekLookback: 13,
  priceBins: 40, hvnPercentile: 85, pivotWin: 10, pivotTolPct: 0.015,
  indexDropPct: 0.002, clusterCount: 4, clusterWindow: 25,
  expireSessions: 25, expireGainPct: 0.05, expireOnGain: true,
  trendLookback: 21,
  indexSeries: [ { key: "SPY", label: "S&P 500 (SPY)", available: true },
                 { key: "SMH", label: "Semis (SMH)",   available: true },
                 { key: "QQQ", label: "Nasdaq (QQQ)",  available: false,
                   reason: "No Nasdaq series in any workbook - verified on the 20260907 vintage." } ],
  ladder: [ ... ], implicationTemplates: { ... }, screenerRank: [ ... ]
}
```

**Do not retune the existing `volume` block to serve this module.** `volume.upDownVolWindow` (20)
and `volume.distAccumThreshold` (0.005) feed `interpretation.build_measures` → pillar B → the pinned
131-check `test_regression_semis` gate, and `indicators.up_down_vol` / `dist_accum_days` are
**composite-level** measures over different windows. The module's per-ticker functions live beside
them in `indicators.py` and share no state. If a change here moves the regression gate, the change
touched shared state and is wrong.

## Page infographics

Both pages carry a top-of-page infographic. Both are **claim surfaces**, so their gate is
provenance rather than arithmetic: every figure must resolve either to a generated count or to an
explicitly sourced hand-authored field, and the page's build script **fails** on a figure with
neither — the same mechanism `build_fab5.py` already applies to an unresolved non-external ticker.

### One styling rule, for both

The reference dashboards are Georgia serif on a gold/teal palette; this site is the `dashboard.css`
sans stack on blue/orange. Worse, `.chip`, `.call`, `.src` and `.stat` already mean different things
in each, and `--s1` / `--s2` hold different values. So: **adopt `dashboard.css` tokens, typography,
nav and theme toggle**, and re-express the references' *layout* patterns — stat tiles, a section
heading with a kicker, figure plus `<details>` table view, filter chips, status tags, print rules —
in site tokens. New classes take an `ig-` prefix.

"Preserve valuable existing functionality and styling" means preserving what the references *do* and
how they are *organised*. Transplanting their stylesheets would give the site two visual languages
and four colliding class names.

### News page infographic

A `#infographic` host at the top of `site/tabs/news.html`, **above** the section nav so it is
visible whichever section is open. Five rows:

1. **The narratives** — the week's thesis sentence plus the top N reads, each one sentence with its
   source. **Hand-authored and cited**, because this is the one row counts cannot produce: article
   counts measure *coverage volume*, which is not the same thing as which narrative mattered. This
   is the reference's `h1` + "Eight reads" compressed to a scannable band, and it is the row a
   reader should be able to stop at.
2. **KPI tiles** — article entries, briefs, distinct brief dates, houses, distinct citations
   resolved. All from the audit JSON's `counts` and `citations`.
3. **Coverage map** — themes as bars sized by `counts.byTheme`, each carrying a momentum arrow:
   this window's count against the prior window's count for the same theme. With no prior audit
   JSON present, render "no prior window" — **never a zero**, which would read as a real collapse.
4. **Cross-theme relationships** — theme × publication from `counts.byThemeAndPublication`, plus
   hand-authored theme-to-theme links, each carrying its source reference.
5. **Momentum row** — chips counting the signal board's statuses as `new` / `escalated` / `faded` /
   `unchanged`.

Rows 1 and 4's links are authored; rows 2, 3 and 5 are generated. That split is the same one the
upstream generator draws, and it is what keeps the page honest: a count is never dressed up as a
judgement, and a judgement always carries a source.

**Reserved-token hazard.** If any of this is ever authored back into the upstream template,
`build_narrative_dashboard.mjs` counts `data-st=`, `class="ev"`, `class="ev big"` and `class="cf"`
with **global regexes over the whole document** and exits 1 on a mismatch — a new section reusing
any of them fails the build even from a different panel. The `ig-` prefix avoids this by
construction.

### Fab5 page infographic

A `#infographic` host in `site/tabs/fab5.html`, **before** `#focus`, rendered by
`renderInfographic()` in `fab5.js`. Six bands, one per category the page must summarise:

| Band | Source |
|---|---|
| Key themes | `layers[].summary` — already authored, but today invisible behind the click-gated `#layerNote` |
| KPI stat strip | `stats[]` |
| Major company developments | `implications[]` filtered to `scope: "name"`, joined with `calendar[]` for dated catalysts; each carries its source chips and evidence grade |
| Competitive dynamics | `disputes[].sides[].house` plus `agreement` — who is on which side |
| Market implications | `scenarios[]`, with probabilities |
| Momentum / what changed | the `whatChanged` delta banner plus a row counting `insights[].priorRun.verdict` |

This needs `data/insights/fab5_<date>.json` at **schemaVersion 2**, adding:

| Key | Shape |
|---|---|
| `stats[]` | `{ kicker, num, lab, sources[], grade }` |
| `whatChanged` | `{ priorBaseline, bullets[], stanceRefinement }` |
| `insights[].priorRun` | `{ predicted, outcome, verdict }`, `verdict ∈ confirmed \| contradicted \| unresolved \| new` |
| `checklist[].status` | `ok \| warn \| bad \| new` — what lets the checklist gain filter chips |
| `disputes[].sides[]` | gains `house`, so a side is attributable |
| `scenarios[]` | `{ name, pct, body, triggers[] }` |
| `calendar[]` | `{ date, body, sources[] }` |

`build_fab5.py` validates the new arrays and fails on an unsourced `stat` or an unknown `verdict`,
exactly as it already fails on an unresolved non-external ticker.

## Architecture

Static, zero-backend, GitHub Pages–deployable, following the lightweight model in [xmanatsf/stk-dashboard](https://github.com/xmanatsf/stk-dashboard) (single `index.html` reading a pre-built data file from the same repo, a Python script that regenerates that data file, a one-click push routine, `Settings → Pages → Deploy from branch`). This project extends that model to four tabs sharing one codebase instead of one page reading one CSV.

```
US_Stk_Dash/
  data/
    raw/                        # source .xlsx files (as delivered, unmodified)
    insights/                   # hand-maintained PAGE inputs (fab5_<date>.json, news_<date>.json,
                                #   narrative_dashboard_source_audit.json) — sibling to raw/, never processed/
    processed/                  # generated JSON, built from raw/ + insights/ — never hand-edited
      <universe>/summary.json   #   composite, breadth, pillars, regime, baskets, rollups, screener
      <universe>/manifest.json  #   ticker list, version, lastDate
      <universe>/tickers/*.json #   per-ticker shards
      insights/                 #   built page payloads (fab5.json, news.json)
      index.json                #   the nav — universes + pages; OWNED BY build_all.py
  config/
    universes.json              # per-tab: workbook stem(s), sheet names, ticker universe, benchmark tickers
    sectors.json                # sector/industry-group classification source + mapping-sheet layout (header row offset etc.)
    parameters.json             # MA windows, ROC window, RSI/MACD params, breadth thresholds, oversold zone,
                                #   z-score windows, horizons, regime ladder, sub-baskets, and `institutional`
    charts.json                 # chart definitions shared by all tabs (which series, colors, panel layout) keyed by chart type
  scripts/                      # Python build pipeline (mirrors build_dashboard.py's pattern, generalized)
    config.py                   # loads config/*.json; the single accessor for every threshold
    loaders.py                  # xlsx → typed price/volume/mapping frames; header-row + calendar-day + NA/placeholder handling
    validators.py               # date/ticker/duplicate/missing-value/price-volume/benchmark-alignment/sector-mapping checks; returns a report, never silently drops data
    indicators.py               # daily_ret, rolling_z, ema/macd/rsi, obv, rel_vol, breadth, ROC, up_down_vol,
                                #   dist_accum_days, and the per-ticker `institutional` family
    interpretation.py           # pillar/regime narrative generation, kept separate from indicators.py: objective signal → labeled conclusion, both directions (bearish/bullish)
    rollups.py                  # sector/industry-group regime classification, breadth, quartiles, scatter
    pipeline.py                 # load → validate → measure → interpret → emit; benchmarks, shards, site copy
    build_market_internals.py   # Tab 1 data build
    build_semis.py              # Tab 2 build
    build_software.py           # Tab 3 build
    build_hw_networking.py      # Tab 4 build
    build_fab5.py               # Tab 5 page build  -> data/processed/insights/fab5.json
    build_news.py               # Tab 6 page build  -> data/processed/insights/news.json
    build_all.py                # runs all four + both pages + validation report; OWNS index.json
    validate_all.py             # validation report only, no build — run this first on a refresh
    tests/                      # test_regression_semis.py, test_cross_tab.py, test_render.py,
                                #   test_regime_history.py, test_institutional.py, test_screener.py
  site/                         # what actually deploys to GitHub Pages
    index.html                  # landing page / nav
    tabs/
      market-internals.html
      semis.html
      software.html
      hw-networking.html
      fab5.html
      news.html
    assets/
      js/
        charts.js               # shared inline-SVG chart renderer (port of dashboard_template.html's chart()/render(), incl. the bipolar-bar-height fix)
        data-client.js          # manifest/summary/shard fetching and cache-busting
        interpret.js            # renders interpretation.py's output; keeps objective signals visually distinct from conclusions
        regimes.js              # regime colors and label helpers shared by tabs and pages
        stock-panel.js          # the shared per-ticker panel (ticker + benchmark selectors, all charts) used by Tabs 1–4
        institutional.js        # analysis module (a) — imported by initTab
        screener.js             # analysis module (b) — imported by initTab
        tabs.js                 # tab navigation, shared horizon control, loading/error states; hosts + render calls only
        fab5.js                 # the fab5 page renderer, incl. renderInfographic()
        news.js                 # the news page renderer, incl. renderInfographic()
      css/
        dashboard.css
    data/                       # copy of data/processed/** — what the browser actually fetches
  DEPLOY.md                     # setup, local-testing, data-refresh, GitHub Pages steps
  CLAUDE.md
  DASHBOARD_PLAYBOOK.md
  RENMAC_TIMING_FRAMEWORK.md
  Renmac Technical Setup on Semiconductor stocks.txt
```

`institutional.js` and `screener.js` are **new ES modules imported by `initTab`**. `tabs.js` gains
the two hosts and the two render calls, not the module bodies, so it stays the size it is.

Config-driven means: adding a fifth universe/tab, a new indicator, or a new sector taxonomy should require new entries in `config/*.json` plus one `build_<tab>.py` and one `tabs/<tab>.html`, not edits scattered across `charts.js` or `indicators.py`.

**`index.json` is the only source of the nav and `build_all.py` owns it exclusively.** It has two
sections: `universes` (workbook-backed, carry a validation `status`, get a verdict row on the
landing page) and `pages` (no workbook, no status, no verdict row — `fab5` and `news`). Anything
that writes `index.json` outside `build_all` gets silently overwritten on the next build, which is
why `build_fab5.py` returns an index entry rather than patching the file. `build_all --only <x>`
seeds the index from the file already on disk before overwriting the rebuilt universe, so a partial
build no longer deletes the other tabs from the nav.

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

The analysis modules and the two page infographics come after the above and in this order, because
each step's output is the next step's input:

9. Extend `pipeline.build_benchmarks` to emit SPY/SMH **volume** beside price, and add the
   `institutional` block to `config/parameters.json`. Nothing downstream works without both.
10. The per-ticker `institutional` family in `indicators.py` (weekly bars, up/down ratio,
    volume-at-price, index distribution days), unit-checked by `test_institutional.py` against
    hand-worked values on the pinned 20260807 vintage. **Re-run `test_regression_semis.py` here** —
    it must still be 131 PASS / 0 FAIL, which is what proves the new functions did not disturb the
    composite-level measures they sit beside.
11. The `screener` array in `pipeline.emit`, then `site/assets/js/institutional.js` and
    `screener.js`, built once against Tab 2 and reused by config on Tabs 1, 3 and 4.
12. Fab5 page: `fab5_<date>.json` to schemaVersion 2, `build_fab5.py` validation for the new
    arrays, then `renderInfographic()`.
13. News page: the `data/insights/` inputs, `scripts/build_news.py`, `site/tabs/news.html` and
    `news.js`, three lines in `build_all.main()`, then its infographic.

## Testing / QA criteria

### Two tests are vintage-locked on purpose

- **`test_regression_semis.py` is pinned** to `US semi stocks 5y price and volume 20260807.xlsx`
  via a `GOLDEN_WORKBOOK` constant, not `resolve_input`. It measures **engine parity against the
  shipped dashboards**, and the input workbook is part of the golden capture exactly as
  `reference/golden/semi_data.json` is. Letting it follow the newest vintage would silently
  redefine the baseline the golden README forbids editing, and every date and price assertion
  would fail for a reason unrelated to the engine. It must stay at **131 PASS / 0 FAIL** through
  any refresh. Never delete the 20260807 workbook from `data/raw`.
- **`test_regime_history.py` compares on the date intersection.** Since the window rolls, its grid
  and the golden's will never be identical again. It intersects the two date lists and runs the
  label / score / run / capitulation comparisons over the overlap, printing both non-overlapping
  tails. The final-verdict block now compares two *different* sessions and says so — the seven-field
  match was verified on the 20260807 vintage and is not re-assertable after a refresh. Exit 1 only
  if the grids do not overlap at all. Post-refresh reading on the 20260927 vintage: **1,221-session
  overlap** (2021-09-27 .. 2026-08-07), **63.2% label agreement** over 969 comparable sessions,
  mean |Δ| 11.9 points, and both builds' last regime run starting 2026-07-14. The reconciliation
  described in `reference/golden/README.md` is still outstanding. The script also reconfigures
  stdout to UTF-8: it prints a Greek delta, and a Windows console defaults to cp1252, which used to
  kill a diagnostic that had nothing wrong with it.

### QA criteria

- Each `build_<tab>.py` prints a console summary (coverage %, date range, peak/trough, breadth, regime call per pillar) that a human can sanity-check against the raw data before trusting the output — mirror the existing scripts' pattern.
- Headless render check per tab (Playwright against the `file://` or deployed URL): page loads, no `pageerror`s, embedded/fetched JSON parses, ticker/benchmark selector switch re-renders without leaking listeners or throwing.
- Cross-tab consistency check: same indicator (e.g., 20-dma, RSI) computed on the same ticker if it appears in more than one universe file must agree; shared chart component must render identically across tabs.
- Validation report from `validators.py` reviewed and either clean or explicitly annotated as a known/accepted limitation in the relevant tab's footer — this is the mechanism for "don't fabricate when data is missing."
- Interpretation text spot-checked against the objective numbers it's describing (peak/trough dates, thresholds crossed) to confirm the objective-signal vs. conclusion distinction actually holds in the copy, not just in code structure.

### QA criteria for the analysis modules and infographics

- **`test_institutional.py`** — the up/down ratio, the weekly bars and the volume-at-price levels
  reproduce hand-worked values on the pinned 20260807 vintage. Cover the edge cases explicitly:
  zero down-volume (must report `>= ratioCap`, never infinity), a flat week (`wcp` must be `null`,
  not 0.5), a partial week at the window edge, and a series below `minSessions`.
- **`test_screener.py`** — every screener row's component values reproduce from that ticker's shard,
  and the rank ordering matches `screenerRank` applied by hand to three sampled groups. This is the
  test that keeps the ranking inspectable rather than merely claimed to be.
- **`test_regression_semis.py` must stay 131 PASS / 0 FAIL** through all of this. The module shares
  `indicators.py` with the pillars but shares no state; if the gate moves, it did.
- **`test_render.py`** extended to the new DOM hosts on all four tabs, plus `news.html` and the fab5
  `#infographic` — page loads, no `pageerror`, selectors re-render without leaking chart listeners.
- **Infographic provenance** — the build fails on a figure that resolves to neither a generated
  count nor a sourced hand-authored field. Spot-check that a deliberately unsourced `stat` actually
  fails the build rather than rendering.
- **Signal-card copy** spot-checked the same way as the pillar copy: `evidence` is numbers,
  `implication` came from a template, and `confidence` lists its reasons rather than asserting a
  grade.

## GitHub Pages deployment

Static `site/` deploys directly — no build step required at serve time (all heavy computation happens in the Python `scripts/` pipeline ahead of commit, output is plain JSON `fetch()`ed by the browser, same approach as `US_Semi_Chip_Top_Dashboard.html`'s embedded-`DATA`-blob pattern, generalized to fetched files instead of inlined). `DEPLOY.md` specifies: one-time repo creation and `Settings → Pages → Deploy from branch (main, /site or /root)`; local testing via `python -m http.server 8000 --directory site` — **not `file://`**, which browsers block for ES modules and `fetch` (see Non-negotiables below); the data-refresh routine (drop new `.xlsx` in `data/raw/`, run `python scripts/build_all.py`, review the validation report, commit `data/processed/**` + `site/data/**`, push); and cache-busting on fetch so a refreshed deploy is visible without special client action.

## Non-negotiables

- No backend services, no build-time framework/bundler dependency — vanilla JS + inline SVG charts, matching the existing dashboards. **One deliberate deviation from the reference dashboards:** because the site is modular (ES modules + `fetch`ed JSON) it cannot be opened from `file://` — browsers block module imports and fetches on that scheme. Local testing needs `python -m http.server 8000 --directory site`. GitHub Pages serves over HTTP, so production is unaffected. This was the price of "a tab is a config entry, not a fork".
- Three capabilities the spec assumed already existed do **not** exist in either reference dashboard and were built new: the per-ticker technical-signal summary, the shared date-range/horizon control, and per-ticker OBV (the references compute OBV only at composite level). Grep both files before assuming a capability is available to port.
- Every capability already in `US_Semi_Chip_Top_Dashboard.html` and `SP100_Sector_Dashboard.html` must be present somewhere in the new dashboard unless explicitly replaced by a documented improvement — this is a supersede, not a downgrade.
- Frameworks and indicators beyond RenMac's must be addable without restructuring — new pillar/indicator = new function in `indicators.py` + new entry in `config/parameters.json`, not a rewrite.
- Never fabricate a conclusion the data doesn't support; when a file (e.g., the current HW/networking workbook) fails validation, say so in the UI rather than shipping a plausible-looking but ungrounded chart.
- **The analysis modules never emit a signal from an unbuilt or insufficient series.** `Insufficient data` is a first-class value of `signal`, not a gap to be filled, and an index leg with no series renders as unavailable rather than substituting a proxy. Same rule as above, applied to the new surfaces.
- **Infographic figures are sourced or they are not shipped.** Every number on either page's infographic resolves to a generated count or to an explicitly sourced hand-authored field; the page's build script fails on anything else. A missing prior window renders as "no prior window", never as zero.
