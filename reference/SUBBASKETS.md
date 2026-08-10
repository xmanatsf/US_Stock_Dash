# Semiconductor sub-baskets

The cycle-position component (pillar E) of `RENMAC_TIMING_FRAMEWORK.md`. "Semis" is not one
trade — the sub-groups lead and lag each other in a stable order, so *which part* of the
complex is leading dates the cycle more precisely than the composite can.

Defined once in `renmac_score.py` (`SUBBASKETS`, `CYCLE_BASKETS`) and imported by
`build_renmac_dashboard.py`. **Edit them there, not here** — this file documents the roster,
it does not drive it.

Membership below is as resolved against `US semi stocks price and volume 5y 20260731.xlsx`
(65 tickers with usable history).

---

## The baskets

### WFE / equipment — 18 names · **scored**
Wafer-fab equipment, materials, test, and OSAT.

`AMAT, LRCX, KLAC, ONTO, ACLS, ENTG, MKSI, UCTT, ICHR, TER, AMKR, PLAB, FORM, AEHR, VECO, COHU, ACMR, SKYT`

**Cycle role — turns first, in both directions.** Equipment leads out of a trough and rolls
over first into a top, because capex decisions are made before the shipments they fund. Its
relative strength is the single most informative cycle signal in the framework, which is why
pillar E weights it above the raw count of baskets that happen to be positive: equipment
outperforming into a weak tape is the first constructive tell at a bottom, and equipment
lagging into a weak tape means the cycle is rolling rather than turning.

*Defined but absent from this file: `RTEC` (Rudolph/Onto legacy line) — present in the older
one-year universe, dropped from the five-year pull.*

### AI / compute — 8 names · **scored**
Datacenter compute, accelerators, networking silicon, and foundry.

`NVDA, AVGO, AMD, MRVL, ALAB, GFS, INTC, QCOM`

**Cycle role — secular overlay, not a cycle read.** This basket can run on an AI capex cycle
that is largely decoupled from the traditional chip cycle. Its diagnostic value is in
*narrowing*: when AI/compute carries the composite while equipment and analog lag, leadership
has concentrated and the tape is late-cycle. Pillar E therefore scores "broad advance led by
AI/compute" lower than the same breadth led by the cycle-sensitive end.

### Analog / MCU / industrial — 24 names · **scored**
Analog, mixed-signal, microcontrollers, RF, connectivity, timing.

`ADI, TXN, MCHP, ON, MPWR, POWI, DIOD, ALGM, SLAB, SWKS, QRVO, SMTC, AOSL, SYNA, MXL, CRUS, PI, MTSI, CEVA, LSCC, INDI, NVTS, AMBA, SITM`

**Cycle role — broadest and latest.** Tied to autos, industrial and handset end-markets, which
recover after the capex and memory cycles have already turned. Analog *joining* an advance is
what converts a bounce into a durable, broad recovery; an advance that never reaches analog
has not broadened.

*Defined but absent from this file: `MBLY` (Mobileye).*

### Memory — 2 names · **thin, reported but NOT scored**
`MU, RMBS`

**Cycle role — high-beta cycle expression.** Memory leads on price and lags on breadth, and is
the most violent expression of the cycle. It is excluded from scoring here only because a
two-name basket is not a basket: on the 31-Jul-2026 build it posted the strongest 65-day ROC
of any group (+18%) on essentially one stock, which would have been named "leadership" off a
single name's move. Pillar E requires **three or more names** for a cycle basket to score.

### Thematic — 8 names · reported only, never scored
`ENPH, FSLR, RGTI, KOPN, NVEC, OLED, AXTI, WOLF`

Solar, quantum, display materials, compound semis. These sit in the semiconductor GICS bucket
but trade on their own drivers — panel oversupply, funding cycles, single-customer design wins
— not the chip cycle. Charted for context and deliberately excluded from the cycle read, the
same treatment the playbook prescribes for the software dashboard's crypto-miner subgroup.

---

## Unassigned names

Five tickers in the universe belong to no basket. They still contribute to the composite,
breadth, momentum and every other pillar — they are invisible only to the **cycle** read.

| Ticker | What it is | Natural home |
|---|---|---|
| `MRAM` | Everspin — MRAM memory | Memory |
| `PENG` | Penguin Solutions — memory modules + AI infrastructure | Memory |
| `AMBQ` | Ambiq Micro — ultra-low-power MCU/SoC | Analog/MCU |
| `PDFS` | PDF Solutions — fab yield analytics | none; it is software, not equipment |
| `TE` | unidentified at a $0.95–16.08 price range (not TE Connectivity) | unresolved — do not guess |

**Known improvement, deliberately not applied.** Adding `MRAM` and `PENG` to Memory would take
it from two names to four and make it **scorable**, which matters — memory is a genuine cycle
signal currently being measured and then discarded. Adding `AMBQ` to Analog/MCU is equally
clear-cut. This was left alone because changing basket membership shifts pillar E and therefore
the whole regime history, so it needs a rebuild and re-verification rather than a quiet edit.

---

## Reading the performance section

The dashboard charts each basket two ways over a user-selected window (1m through 5y):

- **Absolute** — each basket rebased to 100 at the start of the window.
- **Relative** — each basket divided by the equal-weight universe composite over the same
  window, also rebased to 100. A rising line means the basket is *gaining* on the universe,
  regardless of whether it is up or down in absolute terms.

Relative is the one that carries the cycle signal. Absolute tells you what happened; relative
tells you what is being rotated into, and rotation is what dates the cycle. In a broad
drawdown every basket falls, and the only usable information is which is falling least.

Short windows (1m, 3m) read tactically and are noisy. The 65-day ROC that pillar E actually
scores sits between the 3m and 6m views.
