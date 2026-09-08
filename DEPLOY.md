# DEPLOY

Static site, no backend, no build step at serve time. All computation happens in the Python
pipeline under `scripts/` ahead of commit; the browser fetches plain JSON.

## Requirements

Python 3.14 with `openpyxl` (the only third-party dependency of the build).
`playwright` is needed for the render test but not for the build.

## Local testing

**You cannot open the site from `file://`.** It uses ES modules and `fetch`, which browsers block
on the `file://` scheme for security. This is the one way it differs from the old single-file
dashboards, which inlined everything. GitHub Pages serves over HTTP, so local testing needs a
static server:

```
python -m http.server 8000 --directory site
# then open http://127.0.0.1:8000/
```

## Refreshing the data

**What exists today.** Steps 1–3, 5, 6, 8 and 9 below are live. Steps 4 and 7, and the
*Benchmark volume* bullet under *What to check*, describe the analysis modules
(`institutional`, `screener`) from `CLAUDE.md → Analysis modules` — spec steps 9–11, which are
**not implemented**: there is no `institutional` block in `config/parameters.json`, no
`test_institutional.py` or `test_screener.py`, and `benchmarks.json` carries `series` without
`volume` for that reason rather than as a stale artefact. They are kept here so the routine is
complete when they land; until then they are no-ops, not failures.

1. **Copy** the new `.xlsx` into `data/raw/` — copy, never move or replace. Keep the date stamp in
   the filename; file resolution picks the newest match for an **anchored** stem, so
   `US software stocks 5y price and volume 20260816.xlsx` is selected and the older
   `US software stocks 20260804.xlsx` is not. A loose glob would pick the wrong one.
   **Do not delete old vintages.** `US semi stocks 5y price and volume 20260807.xlsx` is pinned as
   the input to the regression gate and the build will tell you so if it goes missing.
2. `python scripts/validate_all.py` — read the report before building anything.
3. Re-measure `config/parameters.json → calendar.expected` against what the report printed
   (`tradingDays`, `firstDate`, `lastDate`) and update it. The CapIQ 5-year window **rolls**: both
   ends of the grid move on every refresh, so carrying the old expectation forward turns a real
   check into permanent noise.
4. **Not built yet — skip on a refresh today.** Re-check `config/parameters.json →
   institutional.indexSeries`. Each entry's `available` flag
   describes **this export**, not the framework: `QQQ` is `available: false` today because no
   workbook carries a Nasdaq series, and it flips the moment one does. A stale flag either hides a
   series you now have or promises one you do not. The rest of the `institutional` block is
   framework-level and does not move on a refresh; every key in it is defined once, in
   `CLAUDE.md → Analysis modules`, and nowhere else.
5. `python scripts/build_all.py` — writes `data/processed/**`, builds the fab5 and news pages last,
   rewrites `index.json`, and copies everything to `site/data/**`.
6. `python scripts/tests/test_regression_semis.py` (must stay 131 PASS / 0 FAIL — it runs on the
   pinned vintage and a refresh must not move it) and `python scripts/tests/test_cross_tab.py`.
7. **Not built yet — skip on a refresh today.** `python scripts/tests/test_institutional.py` and
   `python scripts/tests/test_screener.py` — the
   analysis-module gates. The first checks the up/down ratio, weekly bars and volume-at-price levels
   against hand-worked values on the pinned vintage; the second checks that every screener row's
   components reproduce from that ticker's shard and that the ordering matches `screenerRank`.
8. `python scripts/tests/test_render.py` (add `--shots` to save screenshots). This also asserts the
   fab5 page's ticker strip still agrees with the universe payload, and that the new module hosts
   and both infographics render without a `pageerror`.
9. `python scripts/tests/test_regime_history.py` — a comparison, not a gate. It runs on the date
   intersection with the golden, so it survives the window roll.
10. Commit `data/processed/**`, `site/data/**` and any config change. Push.

Excel lock files (`~$*.xlsx`) are ignored by the resolver and by git, so a workbook open in Excel
does not break a build.

## What to check on every refresh

The validation report is not decoration. Re-read it each time, because a corrected file can
relocate bad data rather than fix it.

- **`DUPLICATED_SOURCE`** is fatal and means a workbook contains another workbook's numbers under
  different headers. This has already happened once here: a hardware export shipped with
  `#PEND` / `SPGRANGEV` in its label row and 34 of 36 columns byte-identical to the semiconductor
  file, so "AAPL" carried AMD's price. Re-export with the CapIQ plugin connected.
- **`CONSTANT_SERIES`** is fatal. A column with one distinct value is not a price.
- **`TERMINAL_FLATLINE`** is a warning and genuinely ambiguous: a real acquisition pinned at deal
  terms looks identical to a dead feed on every price and volume statistic. Each is named. Confirm
  before trusting or excluding.
- **`EXCLUDED_BY_CONFIG`** lists tickers dropped at load time with a written reason in
  `config/universes.json`. Re-check these on a new vintage — they may have been fixed.
- **Benchmark volume** *(applies once the analysis modules land; not built today)*.
  `benchmarks.json` must carry a `volume` object beside `series`.
  `pipeline.build_benchmarks` reads the `Volume` sheet for SPY/SMH as well as the `Price` sheet,
  because the index-level distribution-day rule compares each session's volume against the prior
  session's. A payload with `series` but no `volume` is a stale artefact from before that change:
  the build says so and the index leg renders unavailable. It is never silently skipped.
- **Standing request: ask for `QQQ` on the next CapIQ export.** No workbook carries a Nasdaq
  series — verified by header scan through the 20260907 vintage, which has `SPY` and `SMH` in the
  semi and hardware exports and no benchmark column at all in the S&P export. Until one arrives the
  Nasdaq leg of the distribution-day rule renders as unavailable rather than substituting a proxy.
  Adding a `QQQ` column to the semi export is the whole fix; flipping `available` in
  `institutional.indexSeries` is the only config change it needs.

## GitHub Pages

One-time:

1. Create the repo and push.
2. `Settings → Pages → Build and deployment → Deploy from a branch`.
3. Branch `main`, folder `/site` (or move `site/*` to the repo root and choose `/root`).

Cache-busting is already handled: the manifest is the only `no-store` fetch, and every summary
and shard is requested with `?v=<version>`, where the version changes only when the data changes.
A redeploy is visible immediately without any client action, and an unchanged rebuild does not
needlessly bust caches.

### Repository size

The per-ticker shards are the bulk of the repo:

| Tab | Shards | Size |
|---|---|---|
| Market internals | 495 | ~42 MB |
| Software | 119 | ~15 MB |
| Semiconductors | 65 | ~8 MB |
| Hardware & networking | 34 | ~4 MB |

About 70 MB total, comfortably inside GitHub's limits but a slow first push. Two levers already
applied, both in config rather than code:

- Moving averages are **not** shipped. `dma20`, `dma50`, `volAvg20` and the relative 20/50-dma are
  plain SMAs of series already in the shard, so `stock-panel.js` derives them. This halved the
  payload. Genuinely heavy computation — regime, breadth, beta, the pillars — stays server-side.
- `market_internals` sets `shardZWindows: [21]`, shipping one z-score window instead of four. The
  focused tabs carry all four because their universes are 34–120 names.

If the repo needs to shrink further, reduce `shardZWindows` on the other tabs or drop `obv` from
the shard (it is a running sum of `vol`, so it is also derivable).

**The analysis modules do not grow the shards.** The screener adds one `screener` array to each
universe's `summary.json` — scalars only, at most ~120 rows of ~30 numbers, a few hundred KB across
all four tabs. Every per-ticker series the modules chart (the 50-day up/down ratio, the weekly
bars, the volume-at-price bins, the support/resistance levels) is **derived client-side** from the
`px` and `vol` already in the shard, exactly as the moving averages are. Do not reach for shipping
a new per-ticker series to make a module easier to write: 724 shards multiply everything, and a
client that fetches 495 of them to rank one sector is the failure this rule exists to prevent.

## Adding a fifth universe

By design this is config plus two thin files, and nothing in `loaders.py`, `validators.py`,
`indicators.py`, `interpretation.py`, `pipeline.py` or `charts.js` changes:

1. An entry in `config/universes.json`.
2. A sub-basket entry in `config/parameters.json` (or `null`).
3. `scripts/build_<name>.py` — a 6-line copy of an existing one.
4. `site/tabs/<tab>.html` — a copy of an existing tab with one string changed.

## Adding a page (not a universe)

A *page* has no workbook, no composite and no regime. There are two — `fab5` (cross-source read)
and `news` (news intelligence). A page lives in `index.json`'s `pages` section rather than
`universes`, so it gets a nav link but no validation glyph and no verdict row on the landing page.
To add another:

1. A hand-maintained content file under `data/insights/`.
2. `scripts/build_<page>.py` exposing `build()`, `emit()`, `index_entry()` and `print_console()`.
3. Three lines in `build_all.main()` calling it after the universe loop and assigning
   `index["pages"][<key>]`. **Never write `index.json` from the page's own script** — `build_all`
   owns that file and rewrites it every run.
4. `site/tabs/<page>.html` plus a render module; call the exported `initNav` for the shared nav.

`build_all` treats a page failure as non-fatal to the dashboards: the four universe payloads are
already on disk, so the page is reported and omitted from the nav rather than taking the build down.
That is per page — a broken `news` build does not take `fab5` off the nav.

## Refreshing a page's content

Adding a page and refreshing one are different jobs, and only the first was written down before.
A content refresh is:

1. Drop a new dated file into `data/insights/` — `fab5_<date>.json` or `news_<date>.json`. Keep the
   old one; page inputs are versioned the same way workbook vintages are.
2. Update `asOf`, `sourceDoc` and `priorBaseline` inside it. `priorBaseline` is what the
   what-changed banner and every `insights[].priorRun` verdict are measured against, so a stale
   value silently mislabels which claims are new.
3. For `news`, also refresh the copy of `narrative_dashboard_source_audit.json` — the Index and
   Sources sections and every count are generated from it, so an old audit file means an old index
   under new prose.
4. `python scripts/build_all.py`, then read `print_console`. For `fab5` confirm the joined /
   external ticker split is what you expect: an unresolved non-external ticker is a **fatal** build
   error by design, not a warning. For `news` confirm the article, brief and citation counts match
   the audit file.
5. `python scripts/tests/test_render.py` — this is what re-asserts that the fab5 ticker strip is
   still a verbatim copy of the universe payload rather than a second source of prices.

The fab5 content is now the Run 6 synthesis — `fab5_20260906.json` at schemaVersion 2, authored
from `Fab5_Cross_Source_Synthesis_20260905.md` and its 6 September addendum. `build_fab5.py`
resolves the newest `fab5_<date>.json` rather than a pinned filename, so the next refresh really is
just a file drop. The news page follows the same rule with `news_<date>.json`, and additionally
needs its `narrative_dashboard_source_audit.json` refreshed in the same step — an old audit file
means an old index and old counts sitting under new prose.

## Validating an infographic

Both infographics are **claim surfaces**, so the gate is provenance rather than arithmetic. There is
no recomputation to check — there is only whether each figure came from somewhere.

- Every figure must resolve to a generated count (from the audit JSON, or from the page payload's
  own arrays) or to an explicitly sourced hand-authored field. The page's build script **fails** on
  anything else, the same way `build_fab5.py` already fails on an unresolved non-external ticker.
- A missing prior window renders as "no prior window". It never renders as zero, which a reader
  would correctly interpret as a collapse to nothing.
- `test_render.py` asserts both `#infographic` hosts render with no `pageerror`.
- To confirm the gate is live rather than merely written down, remove the `sources` from one `stat`
  and check that the build fails instead of rendering it.

**Reserved-token hazard, if anything is ever authored back upstream.**
`WSJ/build_narrative_dashboard.mjs` counts `data-st=`, `class="ev"`, `class="ev big"` and
`class="cf"` with **global regexes over the entire document** and exits 1 when a count drifts from
the pinned number. A new section reusing any of those strings fails that build even from a different
panel. New infographic markup uses `ig-`-prefixed classes for this reason.

## Upstream: the News reference

`Cowork Playground/WSJ/` owns the reference dashboard. Its build is two steps run from that folder:

```
sh tpl/assemble.sh          # cats tpl/*.html -> narrative_dashboard_template.html
                            # then runs the generator
```

`assemble.sh` overwrites the assembled template from the section files, and the generator overwrites
the output HTML — so **edit `tpl/` section files, never the assembled template or the built page**.

The copy of that HTML sitting in this repo is downstream and exists as a design reference. The
`news` page consumes extracted JSON under `data/insights/`, never the assembled HTML. Editing the
local copy is orphaned work: it is neither the source nor the deployed artefact.

## Layout

```
config/          universes, sectors, parameters, charts — all thresholds live here,
                 including the `institutional` block the analysis modules read
data/raw/        source workbooks, unmodified
data/insights/   hand-maintained PAGE inputs (fab5_<date>.json, news_<date>.json,
                 narrative_dashboard_source_audit.json). Sibling to raw/, never processed/ —
                 these are inputs a human writes, not build output.
data/processed/  generated JSON, never hand-edited
scripts/         the build pipeline and its tests
site/            what deploys: index.html, tabs/, assets/, data/
reference/       harvested templates and the golden baselines used by the regression gate
```
