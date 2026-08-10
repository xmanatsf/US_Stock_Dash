# RenMac Semiconductor Market-Timing Framework

Derived from the Renaissance Macro (Jeff deGraaf) research in `Renmac Notes/` — two TMT
Deep Dives (4-May-2023, 13-Jul-2023), ten deGraaf's Dailies (Mar–Aug 2023), the 2-Jun-2020
Weekly Survival Guide, and the "Anatomy of a Chip Top" note (Jul-2026).

Companion to `DASHBOARD_PLAYBOOK.md`: **the playbook is how to build, this is how to read.**
Implemented by `renmac_score.py` — every threshold below is in that file.

---

## Why this document exists

`DASHBOARD_PLAYBOOK.md` was written from one source — the 2026 chip-top note — and correctly
warns that its pillar language came out bearish-first because that's what semis happened to
be doing. The broader source set shows why that warning matters. The **same toolkit** produced
three opposite calls:

| Date | Call | The evidence used |
|---|---|---|
| 4-May-2023 | "Semis are now tactically oversold and positioned for a bounce. We're dip buyers in AMAT, ADI, LSCC, OLED." | 65-day lows spiked, oversold condition — "historically supports a tactical bounce" |
| 13-Jul-2023 | "Strength in Semis Not Exhaustive… stay overweight." | Rolling 3-yr Sharpe not at extremes; semi ETF flows near the 50th percentile; 65-day *highs* spiking; >80% above the 20-dma |
| Jul-2026 | "Anatomy of a chip top." | Bubble signal fired Apr-2026; peak → crack → failed retest; breadth stuck at 2–15%; flows in the 90th percentile |

Ten weeks apart, deGraaf went from "buy this dip" to "this isn't exhausted yet" using
identical instruments. A framework built to detect only one of those states is miscalibrated.
Everything below is **symmetric by construction**.

---

## Section 0 — Six operating principles

These override the individual indicators. When an indicator and a principle disagree, the
principle wins.

**1. Peaks and contractions beat levels.**
> "We get uneasy when factor performance reaches the top 5%… in late 2020 beta performance
> reached the top 90th percentile and then persisted to create historical exceptions, peaking
> in April but staying in the +90th percentile for the entire year. **Peaks and contractions
> are better signals than levels**, so we'll be on guard for a peak in high beta performance
> as an indication of shifting sentiment." — 20-Jul-2023

An indicator *at* an extreme tells you conditions are stretched. An indicator *rolling over
from* an extreme tells you to act. This is why `renmac_score.py` pairs a percentile with a
21-session slope for every extension measure, and why the 96th percentile on 20-Jul was a
"be on guard," not a sell.

**2. Price leads fundamentals by about two quarters.**
Semiconductor prices peak roughly two quarters before analysts start cutting EPS. Waiting for
the estimate cut means selling two quarters late. (Chip-top note, 2000 precedent.)

**3. Direction beats level.**
> "Inflation matters, but direction is more important than level, and the market has been
> discounting this improvement for a year now." — 13-Jul-2023

Applies to macro data, breadth, momentum and estimates alike.

**4. Fade the narrative, follow the trend.**
> "Fade don't follow S&P strategist forecasts… Bear market bottoms tend to be marked by
> 'Strategist capitulation' and a reduction of price targets en masse, while consolidations
> or the end of the 'easy money phase' are marked by a type of 'Strategists' Frenzy'."
> — 26-Jul-2023

Same logic on macro: ISM new orders and the Conference Board LEI in the **bottom** decile are
*bullish* for forward returns — a negative, statistically significant t-stat (21-Jul-2023,
2-Aug-2023). The 2020 Weekly Survival Guide states it flatly: "PMI/PPI are CONTRARIAN
Indications."

**5. Rank conflicting signals explicitly.**
> "Our market cycle clock is in a bullish zone… while our yield impact model has spiked into
> the bearish decile… which one should take precedence? There are several techniques… one
> being the 'hot-hand' or asking which has been getting better at predicting more recently…
> Another is regime analysis. When both are present simultaneously, which one is more
> influential? In this case both answers are the market cycle clock." — 12-Jul-2023

Never average conflicting signals. Ask which has been right lately, and which historically
dominates when both fire.

**6. Bottoms are built from panic; tops are built from FOMO.**
Enthusiastic dip-buying into a first break is a **top** signature. Capitulation, redemptions
and disgust are **bottom** signatures. (Chip-top note; and its inverse in the 26-Jul-2023
observation that prominent bears capitulating marks the *end* of the easy-money phase.)

---

## Section 1 — The eight components

Each component follows the same seven-part structure: logic → what to monitor → bull/bear
read → leading vs. confirming → false signals → positioning → worked example.

---

### A. Market and investor positioning

**1. Logic.** A trend can only run as far as there is capital left to commit to it. RenMac
doesn't ask "is this expensive" but "is this *exhausted*" — and treats that as a measurable
question, not a judgement call. deGraaf stayed bullish through July 2023 explicitly *because*
extension gauges were mid-range.

**2. What to monitor.**
- Rolling 3-year Sharpe ratio of the group, percentile-ranked. *(RenMac-native; needs 3 yrs
  of data — currently `insufficient-history`.)*
- High-beta vs. low-beta basket performance, percentile-ranked, **with its slope**.
- Momentum-quintile dispersion (top quintile 65-day ROC minus bottom quintile).
- *(Non-price, documented but not scored: CFTC commercials z-score, ETF flow percentile,
  SERM positioning.)*

**3. Bull / bear.** Mid-range extension with beta improving = "long runway for excess
returns," stay long. Extension in the top decile **and contracting** = mean-reversion setup,
reduce. Extension washed out at the bottom decile and *turning up* = the early-recovery
signature. Extension washed out and still falling = risk appetite still contracting, not a
buy.

**4. Leading vs. confirming.** **Leading** at tops (positioning saturates before price rolls).
**Confirming** at bottoms (beta revives after price has already turned).

**5. False signals.** The big one: extremes persist. Beta performance sat above the 90th
percentile for all of 2021 without mean-reverting. This is why the level alone is never a
signal — only the peak-and-contraction. Also note that with one year of data every percentile
in `renmac_score.py` is **in-sample**: it ranks today against the same twelve months it was
computed from. Read them as "where does today sit in the past year," not as RenMac's
multi-decade percentiles.

**6. Positioning.** This pillar sizes, it doesn't direct. Mid-range extension → full size in
whatever direction the other pillars point. Top-decile-and-contracting → cut size even if
breadth and trend are still fine.

**7. Example.** 13-Jul-2023: *"Despite concerns that Tech is overly extended, risk-adjusted
returns measured by Sharpe Ratios are nowhere near extremes, suggesting a long runway for
excess returns… CFTC data for Commercials also shows that positioning is not yet in the 10th
percentile."* And for semis specifically: *"Risk adjusted returns for Semis and Semi Equipment
are not at extremes… ETF flows are also not at exhaustion levels and are near the 50th
percentile."* Contrast Jul-2026, where SMH inflows sat in the 90th percentile *during* a
drawdown.

---

### B. Price, volume, breadth and relative strength

**1. Logic.** The primary read. Every Deep Dive leads with breadth. An index is an average;
breadth tells you whether the average is describing the population or hiding it.

**2. What to monitor.**
- % of issues above the 20-dma (short-term), 50-dma (intermediate), 200-dma (long-term).
- % of issues with the **20-dma above the 65-dma** — RenMac's short-vs-intermediate trend
  measure, less noisy than raw price-vs-MA.
- 20-day and 65-day highs minus lows, as % of issues.
- Overbought minus oversold, 14-day stochastic (%K ≥ 80 vs. ≤ 20).
- Composite vs. its own 20/50-dma; golden/dark cross state.
- Relative strength vs. the equal-weight composite, and — now that SMH/SPY ride along as
  benchmark columns in the workbook — absolute and relative-strength comparison against the
  sector ETF and the broad market (see `build_renmac_dashboard.py`'s "Benchmark comparison"
  section). Not yet wired into the seven-pillar score itself; RenMac's "three relative
  conditions" framing is still a manual read off those two charts.

**3. Bull / bear.** Breadth rising out of the 2–15% oversold zone and **holding** above it,
with 65-day highs expanding, is the breadth-thrust that starts new legs. Breadth falling into
that zone and getting *stuck* there, with new lows expanding on rallies, is distribution.
Above 80% and rising is momentum expansion; above 80% and rolling over is the first warning.

**4. Leading vs. confirming.** Breadth **leads** price at both ends. The 65-day-high/low
expansion is the cleanest single tell in the whole framework — it's the one measure that
answers "which way is this actually going" without interpretation.

**5. False signals.** An oversold reading inside a *downtrend* is an exit, not an entry —
RenMac repeatedly says to "use any tactical bounces to exit weakness" and "use bounces off the
oversold condition to rotate out of relative laggards" (13-Jul-2023, on Telecom). The
20/50-dma cross earns "+A in our efficacy/simplicity score" but is "subject to the occasional
whipsaw, which we saw with the sell signal in April" — two R2K golden crosses in 2023 alone
(13-Jul-2023). `renmac_score.py` counts crosses in the window and neutralises the signal at
four or more. Finally, a 200-dma breadth *level* can be perfectly valid while its *trend* is
unknowable — after a large advance, 74% of stocks can sit above a 200-dma that is far below
current price, which says nothing about direction.

**6. Positioning.** This pillar sets direction and gross exposure. It carries the largest
weight (25) for that reason.

**7. Example.** 4-May-2023, on the bullish side of an oversold read: *"65-day lows have spiked
in semis while generating an oversold condition. Historically, this supports a tactical bounce
following these internal conditions."* Ten weeks later, the same instrument reading the other
way: *"Tech saw several recent spikes in 65-day highs, which is historically associated with
bullish 3-month and 6-month forward returns"* and *"the percentage of issues trading above the
20-DMA remains firm, back above 80% after some consolidation off the overbought condition."*

---

### C. Sentiment, expectations and crowding

**1. Logic.** Sentiment matters at the extremes and is noise in between. RenMac is unusually
blunt about how weak it is as a timing tool — and unusually specific about the one sentiment
measure that *does* work.

**2. What to monitor.**
- **Volatility alerts** — an outsized daily move relative to trailing volatility. The share of
  the universe firing positive vs. negative alerts. This is RenMac-native and appears
  throughout the Dailies ("(+) vol alert in NFLX", "negative vol alert in MO").
- **Leadership concentration** — cap-weight vs. equal-weight (proxied here by a bellwether
  basket vs. the equal-weight composite).
- **Momentum-quintile spread** as a crowding gauge: wide and widening = healthy dispersion;
  wide and compressing = the unwind.
- *(Non-price, documented but not scored: AAII, put/call, ETF flows, strategist targets.)*

**3. Bull / bear.** More than 20% of names firing **positive** vol alerts is a buyer's panic —
counter-intuitively bullish. Leadership broadening (equal-weight gaining on cap-weight) is
constructive; narrowing is late-cycle. A crowded momentum cohort that starts compressing is
the unwind beginning.

**4. Leading vs. confirming.** Crowding **leads** at tops. Vol-alert clusters are roughly
coincident. Panic-side extremes are **confirming** at bottoms — they tell you a low is being
made, not that it will hold.

**5. False signals.** This is where RenMac is most scathing:
> "AAII investor sentiment reading this week shows bulls in the upper 40s or the top 10th
> percentile of readings historically. It has made some good calls in the past, but it carries
> a weak t-stat of −.18 and equally as horrific trading stats (shorts are right 22% of the
> time when shorting the SPX in this zone). **In short, the data sucks at calling tops, we
> encourage abstinence.**" — 13-Jul-2023

And on the vol-alert measure specifically, the natural misreading is to treat a burst of big
up-days as blow-off exhaustion:
> "Technology had more than 20% of names with positive volatility alerts last week; a buyer's
> panic. **They don't tend to associate themselves with tops, but escape velocity.**"
> — 30-May-2023

Because of this, `renmac_score.py` scores a *seller's* panic as **zero**, not as a bullish
contrarian signal — a crash is raw material for a base, not a base. It only matters via the
capitulation gate, and then only when no confirmed top precedes it.

**6. Positioning.** Sizing input, like pillar A. Never trade on it alone.

**7. Example.** 4-May-2023: *"Put/Call data has yet to spike, suggesting to us that the acute
fear is siloed and not yet present in the broad market. Positioning is still favorable for the
bulls."* And 30-Jul-2023: *"Sentiment does not yet represent a problem in our view, as Wall St
strategist 12m targets remain below current SPX levels."*

---

### D. Fundamental and earnings-cycle inflection

**This component is deliberately not scored.** That is the finding, not an omission.

**1. Logic.** RenMac's own position is that fundamentals are not a timing input. Semiconductor
prices peak roughly **two quarters before** analysts begin cutting EPS. An earnings-revision
signal, used as a trigger, is structurally two quarters late — and at the bottom it is late in
the opposite direction, since estimates trough after price does.

**2. What to monitor instead — the "failure on good news" test.** The price-side substitute is
to watch what the tape does with *unambiguously* good news. A tape that cannot rally on a
blowout print has already discounted it. `renmac_score.py` implements this mechanically: take
the largest single-day advance of the last 60 sessions and check whether the composite is
still above that day's starting level ten sessions later.

**3. Bull / bear.** Good news that holds → expectations are not yet fully discounted. Good news
fully retraced within two weeks → fully discounted; the marginal buyer is gone.

**4. Leading vs. confirming.** The failure-on-good-news test is **coincident-to-leading**. EPS
revisions are **confirming only** — useful for dating a cycle in hindsight, never for timing.

**5. False signals.** A single failed rally is noise; it's the *pattern* of repeated failures
that matters. And the test is only meaningful when the up-day was actually news-driven — a
mechanical short-covering bounce off a washout will fail the test without carrying any
information about expectations.

**6. Positioning.** Never initiate on this. Use it to *raise conviction* in a signal the other
pillars have already given.

**7. Example.** Chip-top note, Jul-2026: Samsung's blow-out earnings and large hyperscaler AI
capex announcements both failed to produce sustained upside. On the 2023 data, the same test
fires on the 25-Jul file: the best up-day of the prior 60 sessions was +9.0% on 21-Jul-2026,
and three sessions later the composite was already back below where that day began.

---

### E. Semiconductor-cycle position

**1. Logic.** "Semis" is not one trade. The sub-groups lead and lag each other in a stable
order, so *which part* of the complex is leading dates the cycle more precisely than the
composite can. RenMac runs this at industry-group and sub-industry level throughout both Deep
Dives; the sub-basket construction here is the extension of that idea inside a single sector.

**2. What to monitor.** Equal-weight sub-baskets and their relative performance vs. the
universe composite. **Full membership, cycle roles and known gaps: `SUBBASKETS.md`.**
Defined once in `renmac_score.py` (`SUBBASKETS`) and imported everywhere else.

| Basket | Cycle role |
|---|---|
| **WFE / equipment** | Turns **first** in both directions — up out of a trough, down into a top |
| **Memory** | High-beta cycle expression; leads on price, lags on breadth |
| **AI / compute** | Secular overlay; carries the composite alone in late-cycle narrowing |
| **Analog / MCU / industrial** | Broadest, latest — joining late is what makes a recovery *durable* |
| **Thematic** (solar, quantum) | Own drivers; reported, not scored |

The dashboard charts each basket **absolute and relative to the equal-weight universe**, both
rebased to 100 at the start of a selectable window (1m / 3m / 6m / 1y / 2y / 3y / 5y), with a
sortable return table underneath. Read the **relative** panel for the cycle: absolute tells you
what happened, relative tells you what is being rotated into, and rotation is what dates the
cycle. In a broad drawdown every basket falls and the only usable information is which falls
least. The 65-day ROC that pillar E actually scores sits between the 3m and 6m views — the
1m and 3m windows are tactical and noisy.

**3. Bull / bear.** Equipment outperforming into a weak tape is the first constructive tell at
a bottom. Analog joining an advance is what turns a bounce into a cycle. AI/compute leading
while everything else lags is narrowing — late-cycle. Equipment *lagging* into a weak tape
means the cycle is rolling over, not turning up.

**4. Leading vs. confirming.** Equipment relative strength **leads**. Analog participation
**confirms**.

**5. False signals.** Two, both caught the hard way in the build:
- **A 65-day ROC can read positive well into a drawdown.** On the 31-Jul-2026 file, all four
  cycle baskets showed positive 65-day ROC while the composite sat 31% below its peak with 5%
  of names above their 50-dma. "All baskets up" meant nothing. The scorer therefore checks
  whether the composite is below a falling 50-dma *first*, and reads the basket numbers as a
  rolling cycle when it is.
- **A two-name basket is not a basket.** Memory (MU, RMBS) posted +42.8% and would have been
  named "leadership" on the strength of essentially one stock. Baskets need three names to be
  scored; thinner ones are reported and flagged `[thin, not scored]`.

**6. Positioning.** This pillar decides *which names*, not how much. It maps directly to the
tilt column in the regime table.

**7. Example.** 4-May-2023, on rotation within the sector: *"Semis & Semi Equipment are now
among the laggards, with Utes, Banks, and Energy as the only groups with worse trends"* — and
in the same report, *"Semi Materials & Equipment are the most undervalued group within Tech,
but in a neutral trend."* By 13-Jul-2023 the whole complex had turned: *"Semis and semi
materials & equipment, tech hardware… and software are all at new absolute highs, a testament
to the broad-based strength in the sector."* Broadening is what made it durable.

---

### F. Accumulation, breakout, distribution and topping structure

**1. Logic.** Tops and bottoms are *processes*, not points. Both run a recognisable multi-step
sequence, and the sequence is what dates the turn.

**2. What to monitor.** The two mirror sequences:

| Topping | Bottoming |
|---|---|
| Peak | Trough |
| **First crack** — ≥8% drop in 5 sessions | **Thrust** — ≥8% rally in 5 sessions |
| **Failed retest** — a lower high | **Held retest** — a higher low that doesn't undercut the trough |
| 50-dma break | Breakout above a **rising** 50-dma |
| **Climax** — the worst 5-day drop | Follow-through with new highs expanding |
| Failed bounce → new lows | |

**3. Bull / bear.** Read the sequence, not the score. The critical step is deciding **which
anchor is live** — the playbook's "where does the extremum sit relative to now" test. The more
recent extremum owns the narrative.

**4. Leading vs. confirming.** The first crack **leads** — it's the shot across the bow. The
failed retest and 50-dma break **confirm**. The climax is coincident.

**5. False signals.** A "failed retest" only 0.5% below the high (the 31-Jul-2026 reading) is
really a double top — technically a lower high, but marginal enough that it needs the 50-dma
break to corroborate. And a bounce arriving within five sessions of the climax is a dead-cat
reflex, not a right shoulder; `build_dashboard.py` already distinguishes these.

**6. Positioning.** This pillar sets *timing*. It carries the second-largest weight (20).

**7. Example.** The chip-top note's sequence — bubble signal Apr-2026, first crack early June,
right-shoulder construction in July — reproduces exactly from price data: peak 26-May-2026 →
first crack 29-May → failed retest 15-Jun (0.5% under the high) → 50-dma break 2-Jul → climax
week 29-Jul (−22%). The scorer and the shipped dashboard agree on every one of those dates.

---

### G. Divergences

**1. Logic.** A divergence is the market telling you the index is no longer representative of
its constituents. It is the earliest available warning and the least reliable in isolation.

**2. What to monitor.**
- Price near its high on materially lower breadth than at the prior high (and its mirror).
- Price near an extreme with 65-day ROC well short of its own prior extreme.
- **New lows expanding while the composite advances** — distribution beneath the surface. And
  the mirror: new highs expanding while the composite declines — accumulation.
- **Positive 65-day ROC while breadth collapses** — a shrinking group holding the index up.
  This is the one that fires in the *middle* of the range, where extremum-anchored tests are
  silent, and it is the divergence that caught the 31-Jul-2026 tape.
- Cap-weight vs. equal-weight; large-cap vs. small-cap.

**3. Bull / bear.** Negative divergences cluster at tops, positive ones at bottoms. Count them
— one is noise, two or more with deteriorating breadth is a regime signal in its own right.

**4. Leading vs. confirming.** The earliest-leading pillar in the framework, and the one most
prone to firing early.

**5. False signals.** Divergences can persist for many months — narrow leadership is a
*condition*, not a trigger. Cap-weight tech was making new highs vs. equal-weight tech in
May-2023 (a textbook narrowing divergence), and the sector then rallied to new highs into
July. Never act on a divergence alone; require breadth to be deteriorating too, which is why
the gate ladder pairs `neg >= 2` with a falling 21-session breadth slope.

**6. Positioning.** Reduce incrementally; don't reverse. Divergences justify trimming, not
shorting.

**7. Example.** May-2023: *"Cap-Weight Tech is breaking out to new highs vs. Equal-Weight
Tech"* alongside *"Small vs. Large Tech at Multi-Year Lows"* — narrowing on two measures at
once, and the correct response was selectivity ("stay selective," "focus longs on relative
leadership"), not exit.

---

### H. Catalysts, risks and confirmation

**1. Logic.** The lowest-weight pillar (5) because it confirms more often than it leads — but
it's where a signal is either validated or exposed as a whipsaw.

**2. What to monitor.** Trend-system state (20-dma vs. 50-dma; 50/200 golden or dark cross
where history permits); the **number of crosses in the window** as a whipsaw gauge; the
failure-on-good-news test from component D; seasonality *(needs multi-year history)*; credit
spreads and volatility regime *(external, documented not scored)*.

**3. Bull / bear.** Trend up with good news holding = confirmed. Trend down with good news
failing = confirmed the other way. Four or more crosses in a window = the system is
whipsawing; treat its signal as noise regardless of direction.

**4. Leading vs. confirming.** Confirming, by construction.

**5. False signals.** The whipsaw problem is the whole story. RenMac grades the golden cross
"+A in our efficacy/simplicity score" *and* notes it produced a failed sell signal in April
2023 followed by a second buy in July — two crosses in seven months on the same index.

**6. Positioning.** Never initiate on this pillar. It raises or lowers conviction in what the
other seven already said.

**7. Example.** RenMac's broader risk overlay from the 2020 Weekly Survival Guide — "Credit
and Volatility Inexorably Linked," "Contractions in Vol = Beta Outperformance" — is the
external version of this pillar. On 23-Jul-2023: *"The trends remain bullish, as do BBB
spreads and our market cycle clock, all of which suggest that weakness and oversold conditions
are buyable in these names."* Credit confirming the trend is what made the dip buyable.

---

## Section 2 — Scoring

Seven scored pillars, each **−2 … +2**, weighted to a composite of **−100 … +100**. Component
D is a rule, not a score.

| Pillar | Weight | Why |
|---|---|---|
| B — Breadth, trend, relative strength | 25 | The primary read in every Deep Dive |
| F — Structure | 20 | What dates the turn |
| G — Divergences | 15 | The early-warning layer |
| E — Cycle position | 15 | Semi-specific; tells you *which* names |
| C — Sentiment / crowding | 10 | Sizing input |
| A — Positioning / extension | 10 | The "not exhaustive" test |
| H — Catalyst / confirmation | 5 | Confirms, rarely leads |

**Missing data is dropped, never zeroed.** A pillar that can't be computed returns
`insufficient-history`, is removed from the weighted average, and the remaining weights are
renormalised. The scorer prints coverage ("scored on 90% of full pillar weight") so a partial
read is never mistaken for a complete one.

---

## Section 3 — Regime classification

**Score bands alone are insufficient.** Capitulation and breakdown both score deeply negative;
a top can form while the score is still high. Each regime therefore carries a structural gate,
and the ladder is evaluated in order — **first match wins**.

| # | Regime | Score | Gate |
|---|---|---|---|
| 1 | **Capitulation** | ≤ −45 | Breadth washed out (≤15% above 20-dma **or** ≤10% above 50-dma) **and** a ≥10% five-day drop within 15 sessions, or a seller's panic |
| 2 | **Breakdown** | ≤ −25 | Closing at the post-peak low, 65-day ROC negative *and* falling |
| 3 | **Bottoming / base** | −25 … −5 | Trough is the live anchor, retest held above it, breadth rising |
| 4 | **Early recovery** | −5 … +20 | Thrust present **and** breakout above a rising 50-dma |
| 5 | **Momentum expansion** | ≥ +50 | Breadth >80%, zero active negative divergences |
| 6 | **Confirmed uptrend** | +20 … +50 | Breadth >50%, ROC positive, zero negative divergences |
| 7 | **Late-cycle topping** | any | Peak anchor + first crack + (failed retest **or** 50-dma break); **or** ≥2 negative divergences with breadth falling |
| 8 | **Indeterminate** | — | Nothing above matched — say so, don't force a call |

### The capitulation split — the framework's most important rule

Gate 1 resolves to **two different regimes** depending on whether a topping sequence preceded
it:

- **Capitulation / washout** (no confirmed top) — a washout inside an ongoing uptrend, or at
  the end of a decline that never had a distribution top. Buyable, scale in.
- **Capitulation inside a confirmed top** — identical measurements, opposite instruction.

The distinction comes straight from the chip-top note: in a confirmed topping structure the
oversold bounces *fail*, and the base case is 18–24 months of malaise rather than a V-shaped
recovery. `build_dashboard.py` says the same thing in its own event text — "unlike November's
washout, these oversold readings are producing bounces that fail — distribution, not
accumulation." A framework that labelled the 31-Jul-2026 tape "capitulation, scale in" would
be giving precisely the advice the source material warns against.

**Late-cycle topping is checked last** because it can fire at a high composite score. A pure
band lookup would have classified April 2026 as momentum expansion.

---

## Section 4 — Positioning by regime

| Regime | Exposure | Tilt | Confirms if | Invalidated by |
|---|---|---|---|---|
| **Capitulation / washout** | 30–50%, scaling in | Highest-beta and equipment first | Held retest, breadth >30%, 3-month lows contracting | A lower low on expanding new lows |
| **Capitulation inside a confirmed top** | 15–35%, **do not scale in** | Sell strength into the bounce; cut relative laggards; rotate to value/cyclical | Only a held retest **plus** breadth >30% makes this a buyable base | A thrust holding on retest with 65-day highs expanding |
| **Breakdown** | 0–25% | Quality over beta, large over small; sell oversold bounces | Nothing yet — wait for a climax and a held retest | A thrust off a trough that holds |
| **Bottoming / base** | 40–60% | Equipment first, memory second; leave analog for later | Reclaim of a rising 50-dma; 65-day highs expanding | Undercut of the trough; breadth back under 20% |
| **Early recovery** | 60–80% | Add cyclically — equipment → memory → analog as it broadens | Breadth >55% holding; analog joining; dispersion widening | Breadth back under 35%; close below the 50-dma |
| **Confirmed uptrend** | 80–100% | Buy pullbacks in names still in uptrends; large over small | 65-day-high spikes; breadth >80% | A first crack; two active negative divergences |
| **Momentum expansion** | 90–100%, **stop adding** | Stay with leadership; monitor extension percentiles daily | Extension mid-range = "not exhaustive," stay long | Extension percentile peaking and contracting; breadth diverging |
| **Late-cycle topping** | 25–50% and falling | Sell strength; cut relative laggards; rotate to quality/value | Failed retest and 50-dma break confirm | A breadth thrust >80% with new highs expanding |

The **large-over-small** tilt runs through every one of these. It is the most persistent single
recommendation in the source set — repeated in both Deep Dives and stated flatly in the
4-May-2023 Daily as *"Short the Russell 2000, Long the S&P 100."*

---

## Section 5 — False signals and known limits

**From the source material:**

- **Sentiment surveys don't call tops.** AAII bulls in the top decile: t-stat −0.18, shorts
  right 22% of the time. "The data sucks at calling tops, we encourage abstinence."
- **Trend systems whipsaw.** Two R2K golden crosses in 2023; the April sell signal failed.
- **Extremes persist.** Beta performance held above the 90th percentile for a full year in
  2021. Peaks and contractions, never levels.
- **Oversold in a downtrend is an exit.** "Use any bounces off the oversold condition to
  rotate out of relative laggards."
- **Overbought in a downtrend is a short.** 23-Jul-2023 on banks: *"continue to look
  vulnerable, particularly those overbought and below their 200-day moving average."*
- **Narrowing divergences persist for months.** Cap-weight beat equal-weight from May-2023 and
  the sector still rallied to new highs in July.
- **Cheap without momentum is a value trap.** *"Momentum and value are a powerful combination,
  the former being the missing ingredient to these charts… it's the trend and momentum that
  gives us the confidence to be long"* (26-Jul-2023). Also 23-Jul-2023: "No Cheap Uptrends
  Present."

**From this implementation:**

- **Percentiles are in-sample.** With one year of data, every percentile ranks today against
  the same twelve months it was computed from. Not comparable to RenMac's multi-decade ranks.
- **65-day ROC survives a drawdown.** All four cycle baskets read positive with the composite
  31% off its peak. Always check the tape's own trend first.
- **Thin baskets lie.** A two-name basket produced the largest "leadership" reading in the
  universe. Three-name minimum to score.
- **A valid level with no trend.** 200-dma breadth reads 74% on 49 sessions of history — the
  level is real, its direction is unknowable.
- **Volume is proxied, not measured, in this (1-year) file.** The 1-year price file has no
  volume column, so volume confirmation is substituted with volatility alerts. RenMac-native,
  but a different measure. The 5-year `build_renmac_dashboard.py` file carries real volume —
  up/down volume ratio, distribution/accumulation days, on-balance volume — see below.
- **No external benchmark scored into the pillars.** SMH/SPY are now available as columns (see
  below) and rendered as a standalone benchmark-comparison section, but relative strength
  *inside the seven-pillar score* is still measured within the universe only. The framework
  sees rotation *inside* semis; semis-vs-market is a chart to read alongside the score, not yet
  an input to it.

---

## Section 6 — Running it

```
python renmac_score.py                                          # current file
python renmac_score.py --xlsx "US semi stocks price 20260725.xlsx"
python renmac_score.py --json                                   # machine-readable
```

The scorer imports its price-handling helpers from `build_dashboard.py` and transcribes that
file's event-sequence logic verbatim, so the two agree on peak/crack/retest/climax dates by
construction. Verified against the shipped dashboard's embedded data blob.

### The 5-year price + volume dataset — `build_renmac_dashboard.py`

`US semi stocks 5y price and volume 20260807.xlsx` (sheets `Price`, `Volume`, 2021-08 →
2026-08, plus SMH/SPY benchmark columns) lifts most of the history gates. Build with:

```
python build_renmac_dashboard.py     ->  US_Semi_RenMac_Regime_Dashboard.html
```

Now measurable, where the one-year file returned `insufficient-history`:

| Measure | Status |
|---|---|
| Bubble signal | RenMac's **actual** rule — a double within *two* years — instead of the stricter 12-month screen |
| 52-week highs / lows | True, not expanding-window period-low proxies |
| 200-dma breadth | Level **and** trend |
| Rolling 3-yr Sharpe percentile | The "not exhaustive" test |
| Percentiles | Causal expanding-window, no longer in-sample |
| Volume | Up/down volume ratio, distribution/accumulation days, and on-balance volume replace the vol-alert proxy |
| Momentum | Composite MACD(12,26,9) and RSI(14), shaded by regime |
| **Regime history** | The framework runs on every session since Aug-2022 using only data available at the time |
| **Sub-basket performance** | Absolute and relative-to-universe, over any window from 1m to 5y (see component E) |
| **Benchmark comparison** | SMH/SPY absolute (rebased) and relative-strength charts, over any window from 1m to 5y — RenMac's semis-vs-market read, previously unavailable |

Still outstanding: **static market caps** for a true cap-weight vs. equal-weight concentration
measure (remains proxied), and wiring the SMH/SPY relative-strength read into the seven-pillar
score itself rather than leaving it as a standalone chart — RenMac's "three relative
conditions" framing is still a manual read, not a scored input.

### Four implementation rules the 5-year build forced

These are not cosmetic — each one produced a materially wrong answer first.

1. **Rebalance the composite.** Averaging prices normalised to a base date works over a year
   and fails over five: by 2026 a stock up 20× dominates an index still labelled
   "equal-weight," reintroducing the exact concentration distortion this framework exists to
   detect. Chain daily cross-sectional mean returns instead.
2. **Read structure off a trailing window (252 sessions).** Searching from an all-time anchor
   makes every event flag permanent — a thrust and 50-dma breakout from Nov-2022 stayed "true"
   for four years, so the bottoming gate matched forever and the classifier reported
   *early recovery in the middle of a crash*. The sequence describes the tape **now**.
3. **Debounce the label, never the score.** Stacking a 21-session score average on top of
   10-session hysteresis cost about four weeks of lag and reported "indeterminate" straight
   through the June–July 2026 break. The structural gates are already persistent; smooth the
   *label* only. And debounce by **majority over the dissent window**, not by consecutive days
   of one candidate — when the raw signal alternates between two adjacent bearish regimes,
   neither ever accumulates and the held regime sticks through a crash.
4. **Apply "peaks beat levels" to the code, not just the prose.** Penalising extension
   *levels* pinned the positioning pillar at −2 for years — precisely the false signal
   principle 1 warns about. Only a gauge that is extreme **and rolling over** scores negative.

### Reading a calendar-day file

The 5-year workbook ships **calendar days**, with weekends and market holidays carrying the
prior close *and the prior volume* forward. Left in, a "20-day" average spans roughly 14
trading days and every weekend counts Friday's volume three times. The builder drops weekends
plus any weekday where >95% of the universe repeats the prior row's price *and* volume — which
recovered exactly the 50 real US market holidays over five years, leaving 251 sessions/yr.
Always check `rows / years` before trusting any moving average on a new file.

---

*Sources: `Renmac Notes/` — TMT Deep Dive 4-May-2023 and 13-Jul-2023; deGraaf's Daily
23-Mar, 4-May, 30-May, 12-Jul, 13-Jul, 20-Jul, 21-Jul, 23-Jul, 26-Jul, 30-Jul, 2-Aug-2023;
deGraaf's Weekly Survival Guide 2-Jun-2020; "Renmac Technical Setup on Semiconductor stocks"
(Jul-2026). Jeff deGraaf, Michail Adzhiashvili, Kevin Dempter, Jillian Tarlowe.*
