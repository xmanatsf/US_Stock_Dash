# Stock-Level Detail Table — Explained

*Refers to the "Stock-level detail" section of `US_Semi_Chip_Top_Dashboard.html` (screenshot: `dash screenshot1.png`). Data through 2026-07-24.*

This table shows one row per stock, sorted in the screenshot by the **>20-dma** column (▲ arrow on that header, so ✗ rows sort first).

## Column definitions

| Column | Meaning |
|---|---|
| **Ticker** | The stock. Green **2×** chip = at least doubled over the 12-month window (bubble-signal roster). Bold = bellwether (NVDA, AVGO, AMD, MU, AMAT, LRCX, KLAC, TXN, MRVL, INTC). |
| **Last** | Closing price on 2026-07-24, the latest date in the file. |
| **12-mo %** | Total return since the window start (2025-07-30). Green = positive. |
| **Off high %** | Distance below the stock's highest close of the period. |
| **High date / Days since** | When that high was set, and how many trading days ago. |
| **65d ROC %** | 65-trading-day rate of change — RenMac's momentum gauge. |
| **Avg vol (m)** | Average daily volume over the trailing 20 sessions, in millions of shares. |
| **Rel vol** | Latest session's volume ÷ its own 20-session average. Above ~1.5 flags an unusually active print (news, index rebalance, capitulation/climax day); near 1.0 is a routine session. |
| **>20-dma / >50-dma** | Whether the last close is above its 20-day / 50-day moving average. ✓ green = above, ✗ red = below. |
| **LOW flag** | Stock closing at a *period* low. Rare in this file — most stocks bottomed at the window start (July 2025), so a period low means the entire 12-month gain has round-tripped. |

Individual-stock detail charts (above the table) also carry MACD(12,26,9), RSI(14), and a
volume bar with its 20-session average, plus a "Compare vs" selector (EW basket / SMH / SPY)
for the relative-price and its moving averages — added when the workbook picked up SMH/SPY
benchmark columns and per-ticker volume.

## What the visible rows are telling you

The classic top signature, stock by stock:

- **Still up big, but far off the highs.** All five rows show strong 12-month returns — AEHR +328%, ACMR +163%, ALAB +126% — yet every one is 16–40% below its high.
- **Highs are clustered in June 2026** (6/04 to 6/30), i.e., set during the topping window, 17–34 trading days ago. Nothing is making new highs.
- **Everything is below trend.** All five trade below both their 20- and 50-day moving averages — which is why they sort to the top with ✗ first.
- **Trapped overhead supply.** ACMR (+64.7%) and ALAB (+51.9%) still show strongly positive trailing 65-day momentum despite trading below trend — everyone who bought in the last quarter is underwater at higher prices, capping every rally (RenMac's overhead-supply dynamic). ADI and ACLS, with ROC near zero, have already round-tripped their entire spring run.
