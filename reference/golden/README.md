# Golden baselines

Captured **before** any porting work, from the shipped dashboards. These are the numeric ground
truth for the regression gate. If a ported indicator disagrees with these, fix the port — never
edit the golden.

| File | Source | Window | Composite |
|---|---|---|---|
| `semi_data.json` | `US_Stk_Dash/US_Semi_Chip_Top_Dashboard.html` | 252 days (1y tail) | base-date `ew_composite` |
| `semi_renmac_data.json` | `US_Semi_Stock/US_Semi_RenMac_Regime_Dashboard.html` | 1,255 days (full 5y) | daily-rebalanced `ew` |

## Two-mode regression

The new engine is 5y + daily-rebalanced `ew`, so it **cannot** reproduce `semi_data.json`'s
composite figures. Run the harness in two modes:

- **legacy-parity mode** (1y window, `ew_composite`) → must match `semi_data.json`
- **native mode** (5y, `ew`) → must match `semi_renmac_data.json`

Path-independent indicators (`dma20`, `dma50`, `rsi`, `macd`, `obv`, `rel_vol`, z-scores) must match
in both modes on the overlapping date range.

## Verified assertions

From `semi_renmac_data.json.meta` — independently confirmed by direct openpyxl probe of the
workbook:

```
rawRows      1827
holidays     50
tradingDays  1255
dates        2021-08-09 .. 2026-08-07
```

Coverage differs by window, and both are correct:

| Build | nFull | nPartial | partial | dropped |
|---|---|---|---|---|
| 1y (`semi_data.json`) | 64 | 2 | CBRS, WOLF | — |
| 5y (`semi_renmac_data.json`) | 61 | 4 | ALAB, AMBQ, GFS, WOLF | CBRS |

The 5y build classifies ALAB/AMBQ/GFS as partial because their leading-NA runs (956 / 1,453 / 82)
fall inside the 5y window but outside the 1y tail. CBRS (1,741 leading NAs) drops entirely at 5y.

## Intentional deltas — these must NOT match

Three series are deliberately different in the new engine. If they match the 1y golden, the port
silently kept the inferior version:

1. `ew` daily-rebalanced vs `ew_composite` base-date
2. `expanding_pct` causal vs `pct_rank` in-sample
3. `structure_series` trailing-252 vs `structure` global-anchor

## Spot values (NVDA, last session 2026-08-07)

```
px      [..., 206.64, 211.94, 219.22, 218.99, 223.96]
dma20   [..., 205.36, 206.17, 206.82]
rsi     [..., 61.6, 61.37, 64.41]
```

## Note

The legacy build scripts were deliberately **not executed** to produce these. Running them would
overwrite the shipped dashboards in `US_Semi_Stock/`, which are themselves the ground truth. The
embedded `DATA` blob is richer than the console summary anyway.

## Known divergence: the regime HISTORY, not the final read

`scripts/tests/test_regime_history.py` diffs all 1,255 sessions against the shipped RenMac
dashboard. Result as of the 2026-08-09 build:

| Measure | Result |
|---|---|
| Final verdict (regime, score, coverage, composite, peak date/value, drawdown) | **all 7 fields identical** |
| Label agreement across 1,003 comparable sessions | 63.2% |
| Score delta (ours − golden) | median **−5.0**, mean −4.9, same sign on 89.9% |
| Regime runs | golden 30, ours 38 |
| Capitulation-inside-a-confirmed-top days | golden Nov–Dec 2025, ours Aug 2024 — **zero overlap** |

The composite itself is not the cause: it matches to 0.01 (352.9), as do the peak date and
drawdown. `pillar_A`'s ladder and both 5-year overlays were checked line-for-line against
`build_renmac_dashboard.py:540-585` and are identical.

The residual is in the measure inputs the pillars read — most likely the beta-basket construction
(quintile size, minimum paired returns) and percentile warm-up, which were rebuilt to the
documented specification rather than line-ported. A −5.0 median on a composite defined as
`Σ(score·w)/2` is arithmetically one weight-10 pillar scoring 1 lower, which is consistent with a
single input series being shifted rather than a structural error.

**Do not treat the current history as reconciled.** The final-day read is verified; the
day-by-day history is close but not equivalent, and the capitulation split — the framework's most
consequential rule, since it flips the instruction on identical measurements — fires in a
different year. Reconciling `build_measures` against `build_renmac_dashboard.py:226-470`
line-by-line is the outstanding work.
