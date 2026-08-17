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
4. `python scripts/build_all.py` — writes `data/processed/**`, builds the fab5 page last, rewrites
   `index.json`, and copies everything to `site/data/**`.
5. `python scripts/tests/test_regression_semis.py` (must stay 131 PASS / 0 FAIL — it runs on the
   pinned vintage and a refresh must not move it) and `python scripts/tests/test_cross_tab.py`.
6. `python scripts/tests/test_render.py` (add `--shots` to save screenshots). This also asserts the
   fab5 page's ticker strip still agrees with the universe payload.
7. `python scripts/tests/test_regime_history.py` — a comparison, not a gate. It runs on the date
   intersection with the golden, so it survives the window roll.
8. Commit `data/processed/**`, `site/data/**` and any config change. Push.

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

## Adding a fifth universe

By design this is config plus two thin files, and nothing in `loaders.py`, `validators.py`,
`indicators.py`, `interpretation.py`, `pipeline.py` or `charts.js` changes:

1. An entry in `config/universes.json`.
2. A sub-basket entry in `config/parameters.json` (or `null`).
3. `scripts/build_<name>.py` — a 6-line copy of an existing one.
4. `site/tabs/<tab>.html` — a copy of an existing tab with one string changed.

## Adding a page (not a universe)

A *page* has no workbook, no composite and no regime — `fab5` is the first. It lives in
`index.json`'s `pages` section rather than `universes`, so it gets a nav link but no validation
glyph and no verdict row on the landing page. To add another:

1. A hand-maintained content file under `data/insights/`.
2. `scripts/build_<page>.py` exposing `build()`, `emit()`, `index_entry()` and `print_console()`.
3. Three lines in `build_all.main()` calling it after the universe loop and assigning
   `index["pages"][<key>]`. **Never write `index.json` from the page's own script** — `build_all`
   owns that file and rewrites it every run.
4. `site/tabs/<page>.html` plus a render module; call the exported `initNav` for the shared nav.

`build_all` treats a page failure as non-fatal to the dashboards: the four universe payloads are
already on disk, so the page is reported and omitted from the nav rather than taking the build down.

## Layout

```
config/       universes, sectors, parameters, charts — all thresholds live here
data/raw/     source workbooks, unmodified
data/processed/  generated JSON, never hand-edited
scripts/      the build pipeline and its tests
site/         what deploys: index.html, tabs/, assets/, data/
reference/    harvested templates and the golden baselines used by the regression gate
```
