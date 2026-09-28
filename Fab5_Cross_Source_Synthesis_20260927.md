# Fab5 Cross-Source Synthesis — Run 7

**Date:** 27 September 2026
**Window covered:** 7 – 27 September 2026 (underlying notes 28 August – 27 September)
**Sources consumed:** 42 reports across seven houses (UBS 7, NSR 2, ISI 6, MS 1, JPM 2, Red-Ring 13, TMTB 11)
**Supersedes:** `Fab5_Cross_Source_Synthesis_20260905.md` (Run 6, with its 6 September addendum)

---

## TLDR

Every macro bear trigger Run 6 wrote for September fired, and the AI complex made new highs anyway. The Fed hiked unanimously on 16 September with hawkish dots. The 10-year went through 5% and the 5-year closed above 5% for the first time since 2004. Brent went through $100, and diesel set records above $6. Yet the Nasdaq-100 closed at a record on 21–22 September and the SOX is up ~79% YTD. **The reason is that the washout happened a week earlier and for a different reason.** On 14 September the "pace the frontier" episode took semis down 5.5% in a day and momentum down 6%. Within a week the same story was re-priced as "safety is additive compute", and CTAs re-levered from the 13th to the 37th percentile. **The run's two real findings sit under that tape.** First, the credit discrimination Run 6 predicted is now visible and wide. CoreWeave CDS is at 811bp, +259bp this quarter, while hyperscaler CDS averages ~88bp. Oracle served force majeure on its 2.45GW Jupiter campus, and a lender sold Jupiter project debt below 90 cents. Credit and the channel led again, and the equity research followed: three houses were bullish on CoreWeave's equity while its CDS was blowing out (UBS initiated at Buy, JPM upgraded, ISI held Outperform). Second, the AI price structure has split in two. **Compute rents are inflating:** B200 rents rose 50% from June to September, and short-dated capacity trades at ~$40m/MW, about three times long-term rates. **Tokens are deflating:** OpenAI's average paid price fell 62%, GPT-6 is 50% cheaper and Opus 5.5 40% cheaper. Value is flowing to whoever owns scarce, energised, contracted capacity, and it is being squeezed out of the model layer and out of anything that must be refinanced. The memory conflict is now **resolved on mechanism.** September spot DRAM and NAND turned negative, monthly DDR contract increases collapsed from +18–19% to +2–3% (ISI), double-ordering appeared, and two buyers called the NAND peak. Meanwhile the contracted tier firmed: CSPs agreed to pay more for DRAM in 1Q27, and HBM4 prices are set to rise 80–100% in 2027. **The Fed has also named AI financing as a driver of long yields.** Warsh cited "competition for capital from hyperscaler debt issuance", and Barr named the AI investment surge as an inflation source. **The recommendation sharpens rather than reverses: own contracted, self-funded scarcity; underweight whatever must be refinanced or re-priced; and hedge with options, not bonds.** That last clause is a correction. Run 6's long-duration hedge lost money because the stock–bond correlation turned positive.

---

## §1 — What changed since 6 September

**The sequencing worth recording first.** Credit and physical-channel signals again arrived before the research frameworks, the same pattern as Run 6's AVGO CDS in August:
- **Jupiter.** Barclays flagged the air-permit and gas-pipeline risk on 9 September (TMTB relay). Oracle served force majeure on 24 September. A lender sold the project debt below 90 cents on the 25th–26th (WSJ, via TMTB and Red-Ring).
- **Kyber.** An anonymous rack expert said the all-copper NVL144 had been removed from the 2027 plan on 9 September (Red-Ring, grade c). UBS put the 800VDC/Kyber slip at 2028 on 13 September, TMTB corrected it to "Kyber only, not all of Rubin Ultra" on the 15th, and ISI's Virgo wrote "Rubin/Kyber delays" on the 21st.
- **CoreWeave.** CDS widened 259bp QTD to 811bp (UBS Debt Monitor, 21 Sep) **before** UBS initiated at Buy (22 Sep), JPM upgraded to OW (24 Sep) and BNP upgraded NBIS (24 Sep).

In each case the frameworks followed the price, not the other way round.

**6–11 September — oil through $100 and the Iran war widens, then half-reverses.** On 8 September Houthi attacks shut part of Saudi Arabia's southern facilities. On 9 September US forces sank five Iranian tankers and Brent went through $100 (TMTB; ISI Guha re-marked "Brent above $100", ending a stale mark carried since 1 September). On 10 September the WSJ reported Trump's advisers telling him the Iran conflict could last to the end of his term, and Iran fired missiles at a US base in Jordan. On 11 September oil fell 3% on news of a GCC–Iran meeting in Oman, the first since the war began. The same day **core CPI printed +0.3% m/m against +0.2% expected** and US diesel crossed $6 a gallon for the first time. Two ISI data points frame the inflation read: ISI's three-wave model now expects the AI wave (memory and component costs) to peak in 4Q26 or early 1Q27, and Red-Ring's August CPI table shows fuel oil +52%, gasoline +27% and airfares +23% y/y.

**8–11 September — the capex clock and the demand proofs.** MS put hyperscaler capex at ~+60% in 2027 (~+$550bn), falling to ~+12% in 2028 ("2027 boom, 2028 brake"), with ASICs taking 66% of new capacity (TMTB). **Oracle's FQ1 was the cleanest demand proof of the run:**
- OCI +121%, RPO $664bn, 850MW and >300k GPUs delivered in the quarter.
- **100% of GPU capacity up for renewal was renewed or resold at a 20% premium, most of it four years old or more, at 97.9% utilisation** (ISI; JPM; UBS).

**It was also the cleanest financing warning:**
- OCF of $23.1bn included $11.4bn of customer prepayments; capex was $28.5bn.
- FCF was −$5.4bn, or roughly −$16.8bn excluding prepayments. Management gave no date for consolidated FCF turning positive and said it was considering up to $20bn more FY27 financing (TMTB).
- The 10-Q showed unconditional purchase obligations up 2.6x q/q to $34.2bn (ISI).

On 11 September Bloomberg reported Altman telling staff OpenAI might slow frontier development, possibly alongside other labs, and that some model development had been paused on safety grounds.

**12–15 September — "pace the frontier", the sell-off, and the rapid reversal.** Amodei's 12 September essay proposed pacing. Altman and Musk broadly agreed; Nadella stressed human control; Trump replied that "whoever wins AI wins everything." Per Gavin Baker via TMTB, **the only tangible new fact was that OpenAI and Anthropic will embed third-party evaluators such as METR.** On 14 September:
- Semis −5.5%, optical −7%, memory −6%, neoclouds −7%, TMT momentum −6%.
- KOSPI −3%, SoftBank −11%, Hynix −7%.
- Software +1.6% and cybersecurity +4%.
- **Yields rose 1–2bp during the sell-off**, so this was an intra-equity narrative re-pricing rather than macro risk-off (TMTB; Red-Ring).

UBS and Bernstein both said no capex plan had changed. UBS added that semis estimates already require ~380GW of new AI capacity over 2026–30. NSR's point settled the argument: **~80% of "training" compute already sits outside pre-training (reinforcement learning, alignment, evaluation), which is exactly the work pacing requires.** By 18 September Jefferies' bus tour (ANET, NVDA, AVGO, ALAB) had turned "safety" into a compute-additive line. Anthropic disclosed that Claude now does 26% of its internal AI R&D, up from 1% in March, with ~30,000 concurrent agents whose every action is screened before execution. Ross later wrote that "Amodei marked the low day for Semis/AI." **A narrative that could have been bearish for the whole complex was fully reversed in six trading days.**

**16 September — the Warsh Fed's first hike.**
- **Decision:** +25bp to 3.75–4.00%, **unanimous** (ISI had forecast a 10–2 split).
- **Dots:** the September SEP median is 4.1% for both 2026 and 2027, a hold in 2027 "but only just." Only two dots show no further 2026 hike; four show a third; eight show three hikes in total by 2027. The statement dropped the language attributing inflation to energy supply shocks.
- **Framework:** Warsh called it "removing a dose of accommodation," dismissed neutral as academic and pointed to private-sector financial conditions as the benchmark. Taken literally, he could keep hiking until financial conditions stop supporting growth.
- **AI named:** **Warsh attributed higher long yields partly to "competition for capital from hyperscaler debt issuance"** (ISI).
- **House responses:** ISI moved its house view toward the Fed: a December hike, then a single 2027 cut, and by 24–25 September the 2027 cut was no longer being restated. **The Run 6 rate fracture is resolved: the GS and ISI hike readings were right, and TMTB's "~60% odds of a 35bp+ cut" was the mis-specified side.** TMTB was still printing "~70% September cut" on 11 September against 85–92% hike pricing elsewhere.

**17–22 September — the credit tape discriminates, the equity tape ignores it.**
- **17 Sep, CoreWeave's 8-K:** 3–6 month contracts at ~$40m/MW annualised, July prices +25% across SKUs, ~70% of 2Q deals with customer prepayments. The same day it launched a $3.0bn 2033 convertible and a 35m-share ATM (Red-Ring).
- **18 Sep, rates and inventory:** the 10-year closed at 5.01% and the 2-year at 4.76% (ISI). Wolfe put semi-customer inventory at ~58 days, +52% y/y and up for a second quarter, with two of its three stated causes price-driven (TMTB).
- **18 Sep, capacity and memory:** JPM put the CoWoS supply gap at only ~10%; **advanced-node wafers and substrates are now the larger bottleneck**. RBC put the DRAM upcycle in its 14th quarter with ~5 more to run and 2027 HBM contract prices +80–100%.
- **21 Sep, credit:** UBS's Debt Monitor showed **CoreWeave CDS at 811bp (+259bp QTD)**, Alphabet's August bonds ~40% wider than February's at matched maturities, and ZENARC high-yield paper +138bp on a permit denial against QTS −84bp.
- **21 Sep, equities:** the Nasdaq closed at a record (+2.26%), SOX +4.3% and META +11% on Muse. Trump had reportedly called off Houthi strikes at the last minute.
- **21 Sep, frontier-lab funding:** FT published OpenAI's plan: −$278bn cumulative FCF over 2026–30, $856bn of compute, and March's $122bn raise "could be exhausted in 2028." SoftBank came to market with a $10bn + €1bn bond to fund its OpenAI contribution, with an expected Fitch rating of **BB+**. Rothschild initiated NBIS and CRWV at Sell.
- **22 Sep:** UBS initiated CRWV at Buy and published its first DC delay tracker (7.0GW of US capacity currently affected). The Ornn indices showed the token-versus-rent scissor.

**23–27 September — the rates shock, force majeure and the memory turn.**
- **23 Sep, rates:** the 5-year closed above 5% for the first time since 2004 after a 3.1bp tail. The composite PMI hit a five-year high. Fed Governor Barr: "further policy tightening will likely be needed," **citing the AI investment surge.** Markets priced ~95bp of hikes through October 2027 (UBS). UBS credit strategy went Underweight Tech in IG and HY, citing "AI-related investment needs."
- **23 Sep, trade:** the US–China truce was extended by only two months, to 10 January.
- **24 Sep, Jupiter and tokens:** Oracle served force majeure on Jupiter. GPT-6 and Opus 5.5 cut prices 40–50%. Raspberry Pi's CEO said memory prices were "past the steep phase" and that it is "not premature" to call the NAND peak.
- **25 Sep, memory:** **Lipacis told ISI's whole client base that semis are in the "late innings":** September DDR5 spot −1.8%, DDR4 −3.2%, NAND TLC spot −5.0%, DDR contract increases down from +18–19% in August to +2–3% in September, early double-ordering, and OEM inventory 70% above trend.
- **25 Sep, compute:** Akamai signed a $11.6bn, seven-year, **all-CPU** compute contract with Anthropic (8-K, grade a).
- **25 Sep, Texas and policy:** Texas halted state data-center permits pending the ERCOT and water audits. Four senators introduced a bill to keep InnoLight and Eoptolink transceivers out of US national-security systems. Iran proposed restoring the June MOU within seven days, and yields eased.
- **27 Sep, MS batch:** MS called memory 53% of 2027 cloud capex, moved NVDA credit to Neutral on ~$170bn of off-balance-sheet exposure, and **cut AMAT and CAMT targets while raising their estimates.**

---

## §2 — The four-layer read

### Layer 1 — Operational fundamentals: demand intact, the constraint has become deliverability, and the price structure has split

**Demand did not weaken anywhere this run looked.**
- **Backlog:** cloud TTM bookings hit $1.4tn in the June quarter, +191% y/y (ISI). AWS, Azure and GCP commitments/RPO total ~$1.69tn (+152%), including non-cloud items (GS via Red-Ring). Aggregate US cloud backlog now exceeds 100% of sales, up from ~50% last autumn (UBS).
- **Capacity sold forward:** Azure grew 43%, guided to 45%. AWS says "the lion's share of capacity in 2027 is largely reserved… quite a bit already reserved for 2028" (NSR).
- **Supply chain:** TSMC's August sales were +53% y/y. Taiwan's ODMs grew 50–178% in August (Red-Ring).
- **Semis cycle:** UBS's cycle model has semis revenue at $1.63tn (2026E, +118%) and $2.43tn (2027E, +49%). Memory is expected to reach ~68% of semis revenue in 2027.
- **Top-down capex:** unchanged at UBS's top-12 perimeter: $1.01tn / $1.45tn / $1.62tn for 2026/27/28.

**What binds is converting that demand into energised racks, and the binding points moved again.**

- **GPUs are "Balanced":** 30–40 weeks, which is equilibrium for GPUs. DRAM (20 weeks), HDD (50 weeks) and ABF (48–56 weeks) are "Very Tight"; eSSD and MLCC are "Tight" (TrendForce radar via Red-Ring).
- **CoWoS is loosening:** the gap is down to ~10%, and **OSATs supply 58% of the 2028 increment** (JPM). End-2027 CoWoS is 270kwpm per the UBS Taipei team and 260kwpm per the US team.
- **N3 wafers are now the binding logic constraint:** 107%/106% utilisation in 2026/27, and **cloud AI takes N3 from 36% to 73% of wafers.** NVIDIA's N3 share goes from 11% to 31%; Apple's falls from 38% to 14% (UBS Asia Semis). TSMC raises wafer prices 3–6% from January 2027 (DigiTimes, via TMTB and Red-Ring). Samsung's 4nm is full because **HBM4 base dies consume more than half of it**, and Samsung raised 4nm prices 10–15% for US and Chinese customers (DigiTimes via TMTB).
- **Upstream shortages:** InP substrate: Sumitomo and AXT control ~85% of supply, meaningful 6-inch relief is not before 2028, and 2Q contract prices rose 50–60% (Mizuho via TMTB; Red-Ring grade c). Lumentum's EML/CW demand exceeds supply by >30%, with a backlog of more than two years (Globlex via TMTB). 12-inch wafer 2027 LTAs are +15–25% (Commercial Times via Red-Ring). Analog lead times are 30–50+ weeks with prices up 10–30% YTD (Cantor via TMTB).
- **Physical delivery is the binding layer.** UBS's first delay tracker shows 7.0GW of US capacity affected, 12% of the operational base, "direction warrants monitoring". Texas froze new grid connections after large-load requests passed 474GW, then on 25 September also froze state data-center permits. **Chip supply implies ~51GW of AI capacity additions in 2027 against 30–50GW a year of deployable powered shell** (UBS). Rubin's full-rack yield is ~80% against a 90% target, and only ~60% of the ~80k racks in 2027 demand is firm (Red-Ring, anonymous industry Q&A, c). Labs are renting 20–30MW stopgap sites because gigawatt campuses are late (ISI). Turbine lead times are "as much as seven years" (Ceres via ISI).

**The one-line version (TMTB): GPUs deliver in weeks; energised megawatts take years.**

**The price structure has split, and this is the most important new fact in Layer 1.**

*Compute is inflating:*
- Ornn: B200 rents +50% and H200 +28% from June to September; the B200 settlement index was $7.77/GPU-hr on 22 September (official index, grade b).
- CoreWeave: July prices +25% across SKUs; short-dated capacity ~$40m/MW, about three times long-term rates (8-K via Red-Ring; JPM).
- Nebius: 1–3-year contracts at about twice hyperscaler rates and 3–6-month contracts at about four times (BofA via TMTB). It posted a further 16–20% on-demand increase effective 1 October (social-media relay, grade d; cite the direction only).
- Residual values: Silicon Data puts B200 residual value at 158% of purchase price on observed leases (Red-Ring, c).

*Tokens are deflating:*
- Ornn: OpenAI's average paid token price −62%, DeepSeek −51%, Google −29% and Anthropic −11% over the same June–September window.
- New list prices: GPT-6 Sol/Luna −50% against the prior tier; Opus 5.5 −20% per token and ~−40% per workload.
- The LLM Token Expenditure Index is −21.9% YTD at $0.97/Mtok (Red-Ring; ISI; TMTB).
- Buyers are holding spend flat: Uber's AI token spend was flat for 3–4 months despite broader usage, and EY says only one enterprise in ten can show AI ROI in its P&L (TMTB).

**What the scissor does:**
- **It explains the vertical-integration moves:** Anthropic's 1GW direct lease talks with Stream, with a possible Google credit guarantee; the Akamai CPU contract; OpenAI's 8GW SB Energy lease.
- **It explains why the model layer's margin argument is getting harder** even as its revenue grows.
- **Three counterweights:**
  - DeepSeek *raised* prices 2.3–4.5x in August without losing customers and runs an 82.9% API gross margin (TMTB), so price cuts are a competitive choice, not a cost floor.
  - Latency is becoming a priced tier: the rumoured $500 ChatGPT Pro Max, possibly on Cerebras.
  - Enterprise spend at the top is not deflating: one UBS customer went from $1m to $10m a month in 8–9 months.

**The CPU renaissance became a contract, and the contract is really about memory.**
- **The contract:** Akamai–Anthropic is $11.6bn over seven years, entirely CPU, with a ~$9bn option. It carries ~$5.5bn of capex, ~95–105MW, a run-rate of ~$1.7bn by end-2028, and a warrant over up to ~5% of Akamai (8-K, grade a).
- **The hardware:** the fleet runs AMD EPYC, with NVIDIA Vera planned. **Jabil holds ~$1.7bn of Akamai memory on consignment, more than the ~$1.0–1.4bn of CPU spend** (TMTB, from the 8-K).
- **The Vera question:** every OEM's dedicated agentic tier (Dell, HPE, SMCI) runs on NVIDIA Vera, which is Arm-based (ISI). The "x86 CY27 super-cycle" (+48% revenue, +34% ASP, mostly memory-driven) may therefore accrue partly to NVIDIA/TSMC rather than to AMD/Intel.
- **The CPU counts:** Mercury's 2Q26 server CPU units are +27% y/y and ASPs +44%. Intel's unit share is 54% (−1,005bp), AMD's 28% (+445bp), Arm's 18% (+560bp) (ISI, correcting its own prior conflation).

**Memory-cost inflation reached the P&L in more end-markets:**
- **Apple:** the December-quarter gross margin is ~46.2%, 50bp below consensus; memory is ~$150 of the ~$168 y/y BOM increase on a 256GB iPhone 18 Pro Max (Bernstein via TMTB).
- **Consoles and telecom:** Nintendo cut its FY28 unit target (BNP), and Ericsson warned of memory-driven gross-margin pressure building through 2H26–2027 (NSR).
- **PCs:** 2H PC shipments are tracking −26% y/y (MS via TMTB).
- **Smartphones:** UBS cut 2027 smartphone units to −3%. Memory is now 35–37% of a flagship BOM and 55–57% of a low-end BOM.
- **Run 6's downstream FCF channel (ZS, IOT) now has a consumer-hardware leg with a named mega-cap.**

### Layer 2 — Market structure: a narrative flush did the washout, and the complex re-levered into a rates shock

**The tape did not break when the macro triggers fired, for reasons that are all in the data:**
1. **The 14 September pacing flush** (semis −5.5%, momentum −6%) cleared positioning a week before the FOMC.
2. **The post-FOMC selling was brief.** A −$62bn excess-sell burst lasted about 30 minutes before reversing. Retail bought the dip for a seventh time that month and later at the 97th percentile (UBS desk, grade d).
3. **Systematic re-levering:** CTA equity exposure rose from the 13th to the 37th percentile. September Nasdaq excess flow was +$115bn and target-date funds added +$78bn (UBS desk, d).
4. **Positioning cuts both ways:** mutual-fund cash is only 1.2% (GS via Red-Ring), which limits fuel as much as it limits selling. **Hedge-fund Tech net leverage is at the 100th percentile** and QQQ put/call at the 10th percentile over five years (UBS desk, d).

**What makes this regime fragile:**
- **Bonds no longer hedge.** Stock–bond correlation is positive at +28–60% (UBS desk). ISI's CIO breakfast was unanimous that fixed income no longer hedges equities.
- **Bond CTAs are max short:** 1st percentile over five years and 100% short USTs, LQD and HYG (UBS desk). A rally to a 4.80% 10-year would trigger short-covering that lifts equities too, so it works as a second long, not a hedge.
- **Leverage in semis:** leveraged semis ETFs hold $98.7bn of notional, and rebalancing reaches ~20% of ADV.
- **Household equity is 49% of financial assets, above the 45% tech-bubble peak** (UBS desk).
- **Narrow breadth:** only 49% of the S&P was above its 200-day average while the index sat near highs (Krinsky via Red-Ring). Only 19% of semis are at all-time highs against 39% of IT (ISI).
- **ISI's own "Not Dotcom" barometer** is still 4 of 10, but its internals worsened. Hyperscaler forward FCF went from −$38bn to −$83bn, and the equity risk premium compressed from 40bp to 20bp against a zero flag level.
- **Two of Emanuel's four top-calling conditions are now met** (a 5%+ 10-year and a hiking Fed). Recession and genuine FOMO are not.

**Dispersion is rotating, and the market is starting to price the scissor.** The equity market is paying for the contracted and allocation tiers of memory: the Memory Exposed basket is +165% YTD and led every bounce, and Hynix, Kioxia and Samsung rose 6%, 9% and 3% on 18 September. It is also paying for optics, the first sub-sector to re-rate on ECOC.

**Multiples are being cut while earnings rise, now written into the models:**
- MU's price target is unchanged but the multiple fell from 11x to 8x because UBS now uses a 5.00% 10-year in its cost of equity.
- MS cut AMAT's target from $642 to $563 and CAMT's from $165 to $152 while raising EPS on both.
- Stifel upgraded MSFT while cutting FY28 estimates.
- Wells' +24% META target raise is entirely multiple.
- The KOSPI target was cut from 8,800 to 8,000 on rising EPS.

**This is Run 6's #29 regime generalised from semis to the whole AI complex.** The "AI losers" factor also became tradeable: UBS's Consumer Friction basket fell 10% in about a week on Muse, OTAs fell 5–10%, and GOOGL fell 4% on one day. MS moved ABNB to EW and EXPE to UW.

**Korea is the transmission test.**
- **Target and drivers:** the KOSPI target was cut to 8,000, on a stronger won (+11% since June), two BOK hikes and oil above $100.
- **Earnings sensitivity:** each 1% of won appreciation costs ~1.1% of KOSPI EPS, and UBS says FX is "not fully incorporated."
- **Flows:** foreigners have sold Won 198.9tn of Korean tech YTD. Samsung and Hynix are 64% of MSCI Korea, close to the 67% peak that triggers rebalancing (GS via Red-Ring).
- **Returns catalysts:** SK hynix's October shareholder-return package and Samsung's January board.

### Layer 3 — Financing and credit: discrimination is confirmed, the borrower tier is priced as distressed, and the guarantor is now visible

The numbers first, by scope:

| Measure | Reading | Scope / grade |
|---|---|---|
| CoreWeave 5Y CDS | **811bp, +259bp QTD**; June notes T+530 → ~T+850 | UBS Debt Monitor 21 Sep / CRWV initiation 22 Sep (b) |
| Hyperscaler CDS | ~88bp average, from ~60bp in January; ORCL 189bp widest IG; MSFT 44bp | UBS (b) |
| NVDA 5Y CDS | +80bp, +36bp QTD; '56 bond at +111bp, "like an A1" despite Aa1/AA | MS 9 Sep (b) — roughly flat to Run 6's 86.7bp all-time wide |
| US IG tech issuance | $321bn YTD vs $113bn a year ago; 2026F $450bn; US IG running at a $1.97tn annualised pace; books 3–5x | UBS (b) |
| Repeat-issuer concession | Alphabet August deal ~40% wider than February at matched maturities; Dell ~26% wider | UBS (b) |
| Deal-level dispersion | QTS (IG, Blackstone) −84bp; ZENARC (HY) +138bp on a permit denial | UBS (b) |
| Jupiter project debt | Sold below 90 cents by at least one lender | WSJ via TMTB/Red-Ring (b) |
| HY OAS | ~305–315bp, still tight | ISI chart-read (c) |
| Private-credit tech maturities | $54bn 2028, $65bn 2029, against ~$3bn a year of issuance | UBS credit (b) |
| US HY CCC | 923bp, 100th percentile for 2026 | UBS credit (b) |

**Run 6's discrimination thesis is confirmed.** The credit market charges by tenant quality, project stage and permitting, and the gap is now wide. CoreWeave trades roughly 720bp over the hyperscaler average; Run 6 cited a 5.9–6.5% versus 8–9% YTW split. UBS's framing holds: AI financing is constrained by *price, not capacity*. Books are 3–5x covered and issuance is at records. UBS also notes that hyperscaler CDS stayed stable while hyperscaler equities drifted: **credit is not confirming a solvency problem in the AI winners, and it is pricing distress in the borrower tier.**

**The observable precursor Run 6 named has fired at the neocloud tier.** Run 6 wrote that the break would not be a bankruptcy: *"it is spread widening in IG Tech while equities are still making highs."* IG Tech OAS against its March peak has no print in this batch (see the note below). But the same divergence appeared one rung down: CoreWeave's CDS went out 259bp in the quarter while the Nasdaq closed at records. **The equity research went the other way on the same name the same week:**

| House | Action | Basis |
|---|---|---|
| UBS | Initiated Buy, $120 | Pricing +25%, $15bn+/GW by end-2027, NVIDIA's obligation to buy unsold capacity through April 2032 |
| JPM | Upgraded to OW, $125 | Short-dated $40m/MW, contribution margin +5–10pt |
| ISI | OP, $150 | GPU life ~10 years vs 6 in the accounts |
| BNP | Upgraded NBIS to Outperform, $399 ("The Price of Scarcity") | |
| Rothschild | Initiated Sell on NBIS and CRWV | "demand more circular than it appears" |
| Bernstein | Underperform on CRWV, $74 | |

JPM's own model shows why credit disagrees:

| JPM CRWV model | FY26E | FY27E | FY28E |
|---|---:|---:|---:|
| Capex | $36.3bn | $54.3bn | $75.3bn |
| Adjusted FCFF | −$28.7bn | −$34.4bn | −$36.8bn |
| Net debt | $46bn | $78bn | $115bn |
| Net interest | | | **$7.84bn** |
| Adjusted EBIT | | | **$8.79bn** |

Share count rises from ~550m to ~663m over the period. ISI's CRWV deep dive puts take-or-pay project ROIC at only ~8–10%, close to a high-yield cost of debt with the 10-year at ~5.1%. **The equity case rests on years 7–10 of GPU life and on CY27 recontracting at spot premia. Credit is pricing the opposite: that the recontracting happens into a world where token prices have halved.**

**Vendor financing is now quantified and visible in NVIDIA's own credit:**
- **Scale:** NSR counts **>$1.4tn of NVIDIA- and Broadcom-architected facilities** and ~$128bn of disclosed hyperscaler neocloud backstops: Google $76bn, Meta $41bn, Amazon $8bn, Microsoft $3bn.
- **NVIDIA's exposure:** NVIDIA's identified backstops of ~$300bn sit just above its ~$260bn annualised EBITDA (NSR). MS models ~$200bn of all-in credit exposure by end-CY28, ~$170bn of it off funded debt: ~$40bn of lease adjustments, ~$65bn of residual-value support and ~$65bn of revenue-share floors. That includes a **$2.12/hr GPU backstop floor**, and DSO has risen from 45 to 60 days on extended terms.
- **Credit rating:** MS moved NVDA credit to Neutral/"Sidelined" while keeping the equity at OW, and put it plainly: **the same facts carry opposite signs by asset class.**
- **Broadcom scope:** NSR has the first >1GW Anthropic deal on Broadcom's AI XPV platform raising $35bn, $30bn of it backstopped by Broadcom, inside a >20GW (~$650bn implied) programme. Run 6's "~$100bn raise ($60bn senior + $30bn sub)" is the same platform at a different perimeter. **No pricing print for the raise appeared in this batch.**

**The buyers' funding runway now has dates:**
- **OpenAI:** the FT deck (not guidance, grade b/c) shows −$278bn of cumulative FCF over 2026–30, $856bn of compute against ~$840bn of revenue, and March's $122bn raise "could be exhausted in 2028." The FT names NVIDIA and Oracle as suppliers dependent on that financing.
- **SoftBank:** funding its OpenAI contribution in the bond market at an expected BB+.
- **Anthropic funding:** in talks for a 1GW direct lease from Apollo-backed Stream, developer-estimated at ≥$40bn of capital per GW, with a possible **Google credit guarantee** (The Information, via ISI and Red-Ring). It has raised $95bn of equity this year: $30bn at a $380bn valuation and $65bn at $965bn. It also has a $35bn Apollo/Blackstone compute SPV.
- **Anthropic IPO:** now targeted for November rather than October, at ~$2tn and raising up to $100bn (WSJ/NYT, expectations only). ISI's CIOs treat it as a macro variable: if it prices before year-end, positive; if it slips into a stressed 2027, it "could catalyze hyperscaler issuance woes."
- **Hyperscalers:** their own FCF turns negative in 2027: META ~−$45–48bn, GOOG ~−$30–37bn, AMZN ~−$20bn, MSFT ~+$10–12bn (ISI, chart-read). Capex runs at ~105% of OCF in 2026E (UBS). NSR's trough is −$486bn in 2028 on its wider perimeter.

**The bull case on financing is still strong and still has to be carried.**
- **NSR's restated waterfall:** $16.5tn of 2026–30 DC capex, a $3.7tn net financing need and $8tn of hyperscaler OCF. Its conclusion: "a large trillion-dollar problem, but an easy one."
- **Customer prepayments:** Oracle's prepayments and CoreWeave's ~70% prepaid deals show buyers funding capacity directly.
- **Renewal pricing:** Oracle's +20% renewal pricing on four-year-old GPUs is company-reported evidence that residual value is real.
- **Credit discrimination runs both ways:** QTS tightened 84bp after pricing.
- **Spillover:** non-AI consumer credit shows no spillover (Run 6's AFRM point stands).

**Run 6's break condition for its recommendation — IG Tech tightening through 100bp while the tenant spread compresses — did not fire. The opposite happened.**

*A "no new data" note, stated plainly:* ISI's formal fourth bear trigger (IG Tech OAS against March's peak) and Run 6's AVGO CDS level (126.2bp) have no print in this batch. The proxies above are graded and used as proxies. The trigger status is not claimed either way.

### Layer 4 — Macro and policy: the gate resolved hawkish, and AI entered the Fed's reaction function by name

**The facts:**
- **Policy:** a unanimous 25bp hike to 3.75–4.00% on 16 September. The market prices ~72–80% odds of another hike at the 28 October meeting, +36bp for the rest of 2026 and +55–95bp through 2027 depending on the day (ISI; TMTB; UBS).
- **Yields:** the 10-year is at 4.96% (13 Sep), 5.01% (18 Sep), ~5.11% (23 Sep) and ~5.2% (24–26 Sep, chart-read) — the level of its 19-year quarterly closing high. **The 5-year closed above 5% for the first time since 2004.** The 30-year was at 5.355% (11 Sep, GS via TMTB) and ~5.40% (JPM, 14 Sep).
- **Curve:** it has bear-flattened YTD, led by real front-end yields (2-year +130bp, 10-year +75bp): a real-rate shock, the most damaging kind for long-duration equity (UBS).
- **Energy:** Brent was $103.9 and WTI $100.3 on 18 September. Brent is +97.5% YTD and heating oil +147%. EIA diesel was $5.97 on 23 September, +58% y/y, and is the benchmark; ISI's $6.30 and $6.50 prints are chart-read or policy-desk figures. **Three ISI desks now identify refined products, not crude, as the binding inflation channel:** AAL has taken ~$1bn of extra 4Q fuel cost and LUV has roughly halved planned 2026 capacity growth.

**The escalation to record, the one this project has been building toward since Run 6:**
- **Run 6's baseline:** ISI's three-wave model counted the AI wave as memory-chip costs, about 2pp of the diffusion index.
- **Now the Fed says it directly.** The Chair attributes higher long yields partly to "competition for capital from hyperscaler debt issuance." Barr lists the AI investment surge alongside tariffs and wars as a reason for more tightening. ISI's Guha notes the Fed now treats AI demand as inflationary in "some sectors" through "dual-use inputs," and that bank C&I loan growth has risen 230bp since April, plausibly on AI and data-center financing.
- **The loop.** UBS spells it out: hyperscaler capex (~$1.45tn in 2027) adds to inflation. That keeps the Fed hiking and term premium high, which raises the funding cost of the same capex. **This is the macro mechanism behind the Layer 3 discrimination: the rates shock and the credit discrimination are one process.**

**Two structural traps sit underneath:**
- **Warsh's benchmark is itself an AI variable.** His "policy is as policy does" benchmark of private-sector financial conditions puts the terminal rate partly in the hands of asset prices, and the AI trade is the largest component of US financial conditions. An AI rally loosens conditions and, on his framework, argues for more hikes (ISI). The only dovish offset is Guha's new finding that *credit* conditions are "much less accommodative than wider FCIs," so Warsh "may not have as far to go."
- **The balance sheet and the long end.** The Fed's balance-sheet review points to a shorter SOMA duration, "a Fed less willing to backstop long-end yields"; Treasury has tripled its long-end buybacks as the partial offset (UBS). **The debt ceiling becomes binding in 1Q27** and the TGA rebuild afterwards is the scarcity tail. Run 6's 1H27 collision is on schedule.

**Houses are split on 2027:**

| House | 2027 Fed path |
|---|---|
| UBS | Cuts: about −25bp, as CPI peaks at ~3.6–3.9% in Sep–Oct 2026 and core PCE falls to 2.2–2.5% by late 2027. UBS calls this its most important macro call for long-duration tech |
| ISI | Has stopped restating its 2027 cut in four consecutive notes |
| Market | Prices hikes |
| Emanuel (ISI strategy) | Floats a "rip the bandaid" 50bp October scenario |

**The policy surface widened on three fronts at once:**
- **State level.** Texas froze state data-center permits and will ask the Legislature to remove data-center incentives. ISI concedes "onsite generation… does not eliminate state environmental permitting." That dents the Run 6 inverted read that restriction is bullish for behind-the-meter power (§6 #31). ERCOT 2027 forwards have round-tripped to pre-AI levels (~$38–39/MWh) while PJM 2028 makes new highs (~$69) (ISI, chart-read). **The market is pricing Texas policy into ERCOT power before the research does.**
- **Federal and international.** The transceiver bill names InnoLight and Eoptolink for national-security systems, with a five-year transition: a proposal, not law, and not a commercial ban. The US–China truce was extended only to 10 January. Taiwan appears "sidelined" in the summit readout (ISI Wang), and an AI incident channel was agreed "far short of any coordination to slow AI."
- **Social licence.**
  - **Public opinion:** 73% of US adults worry AI firms do not guard against serious harm, 55% support slowing development, and negative views rose from 36% to 39% (Reuters/Ipsos via TMTB). Moratoria stand at 374 active against 92 in June (Wells Fargo via Red-Ring).
  - **State and legal:** Newsom's executive order mandates onsite verifiers and a frontier-model kill switch, and an antitrust class action names Anthropic, OpenAI, SpaceXAI and Google (ISI Bianchi).
  - **Elections:** Polymarket puts a Democratic clean sweep at 65% (UBS desk). ISI's policy desk calls post-midterm investigations into big tech the broadest risk.

---

## §3 — Cross-source agreement and disagreement

### Where all seven houses agree

1. **Demand is not the constraint; deliverability and financing are.** UBS ("power, permits and financing"), ISI ("timing, not demand"), NSR ("supply rather than demand as the binding constraint"), MS (power shortfall 33GW net for 2026–28, 72GW by 2029), JPM ("system delivery and capital return"), Red-Ring ("the deliverable system") and TMTB ("GPUs deliver in weeks, energised MW take years") all say it, in their own words.
2. **The GPU is no longer the tightest input.** Memory, N3 wafers, substrates, InP, turbines and permits are. No house argued that GPU supply binds 2027.
3. **Compute pricing is rising at the margin.** CoreWeave (+25%), Nebius, Oracle renewals (+20%), H100 spot (+20–40%), Ornn B200 (+50%). No house found GPU rental pricing under pressure this run (ISI states this explicitly).
4. **The contracted memory tier is tight into 2027.** HBM4 2027 +80–100% (RBC), DRAM fulfilment ~60% (UBS, Samsung NDR), DRAM sufficiency −15% to −17% (MS), CSPs agreeing higher 1Q27 DRAM ASPs (BofA), NAND contract +21/+17/+15% into 1Q27 (TrendForce). Every house that models memory has the allocated tier tight.
5. **Agentic AI broadens hardware beyond GPUs.** CPUs (AKAM contract; Mercury +27% units), memory (the AKAM consignment; Vera's SOCAMM2 costing more than the GPU's HBM4 at $10,160 vs $9,976 per UBS), storage (eSSD demand ~2x prior), bandwidth (Cisco: +450% per agent task), identity and observability (OKTA, DDOG).
6. **The Fed is now an AI variable.** UBS, ISI and TMTB all record Warsh's hyperscaler-issuance remark and Barr's AI citation. No house argues that rates are irrelevant to AI valuation.

### The conflict registry — twelve live or newly resolved items

**① The memory cycle top — RESOLVED ON MECHANISM, OPEN ON TIMING. [was Run 6's top unresolved item]**

Run 6 left this as "contracted versus un-contracted," with only Red-Ring's channel-inventory build (~1.5 → ~4 months) on the bear side and one balanced source "half for" the trim. This run supplied **price evidence for the split from a second house**, plus buyer-side confirmation:

*The channel and spot tier is turning:*
- ISI's September series: DDR5 16GB spot +7.9% (Jul) / +2.0% (Aug) / **−1.8% (Sep)**; DDR4 16Gb +10.2 / +5.8 / **−3.2%**; DDR4 8Gb **−6.1%**; NAND TLC 512Gb spot **−5.0%**; **DDR contract +18–19% in August to +2–3% in September**; NAND contract 0.0%.
- The 80-source checks show early double-ordering (OEMs ordering the same programmes through distributors *and* brokers), a DRAM inventory build with brokers discounting to franchise distributors, and OEM inventory **70% above trend**, a 10-year high.
- Wolfe: semi-customer inventory ~58 days, +52% y/y, with two of three causes price-driven.
- Daishin: a single customer declared 2028 HBM demand above the entire 2026 world supply, and admitted customers over-report in shortages (Red-Ring, c/d).
- **Buyers:** Raspberry Pi — "past the steep phase," "not premature to say NAND is near peak" (grade c). Acer's chairman expects average memory cost to *fall* next year (c).
- **Supply:** CXMT's G5 lifts dies per wafer ≥50%. Its ~15% of wafer capacity yields only ~11% of bits, so G5 alone could add ~5% to global DRAM bit supply without a new wafer (Commercial Times via TMTB). CXMT's purchase commitments tripled to RMB52.4bn (Red-Ring).

*The contracted and allocated tier is firm:*
- CSPs agreed to pay a higher DRAM ASP in 1Q27 than in 4Q26 (BofA via Red-Ring).
- NAND contract guidance was *raised* to +21% / +17% / +15% q/q for 3Q26 / 4Q26 / 1Q27, from +18% / +2% / 0%. Hyperscaler NAND inventory is heading below its ~15-week norm (TrendForce via TMTB and Red-Ring).
- 2027 HBM contract prices +80–100% (RBC). SK hynix has >50% of capacity under LTAs (JPM).
- SanDisk has 65% of FY28 output under new business-model agreements with eight customers (Rosenblatt via TMTB).

**Adjudication.** The two sides are not contradictory; they describe different markets, and the equity market is currently paying for the allocated one. ISI's own synthesis reached the same split independently: "the memory cycle is splitting, not topping." The unit trap matters: ISI's September contract print is a *monthly* series, while the 4Q guides from UBS (+7–9%), MS (+5–10%) and Arcuri (+7%) are *quarterly q/q*. So the correct statement is that **monthly contract momentum decelerated sharply while quarterly 4Q guides still sit at or above Run 6's +3–8% band**.

**Timing, now dated by the sources themselves:**

| Source | Call |
|---|---|
| Citi | Memory price increases decelerate over the next four quarters and **may peak in 2Q27**; ~60% of commodity DRAM bits are not under LTAs |
| UBS Gaudois (APAC v3) | **Memory stocks peak around 4CQ27**, two quarters before the memory profit peak in 2CQ28; DRAM upcycle to ~2Q28, NAND to ~4Q27 |
| UBS Arcuri | Micron's q/q blended DRAM ASP goes +23% (CQ3'26) → +7% → +6/+6/+5/+5 (2027) → 0/0 (1H28). Under the house heuristic that the shares peak with q/q ASP momentum, **the momentum is peaking now** |
| MS | Rotates semis leadership away from "pricing-leverage" memory (MU, SNDK) while holding memory earnings above the Street; notes that the 2028 arithmetic (capex +12% while 2.5D capacity +50%) *requires* memory prices to moderate in 2028 |
| Industry revenue chart (Red-Ring) | DRAM revenue +147% in 2026, then +25% / +17% / +3% / +3% |

*Status:* **Resolved on mechanism; open on timing, with the window now dated to 2Q–4Q27 by three houses.** The Run 6 un-contracted-tier trim is vindicated on mechanism: spot turned and buyers called it. It remains an *exposure* rather than a ticker list. See §7 for how Micron, a net-cash self-funder whose earnings are roughly half contracted but whose stock trades on pricing leverage, is handled. **Resolving evidence:** Micron's 30 September print and its commentary on SCA/LTA coverage; whether the 4Q contract settles at the quarterly guides or at September's monthly run-rate; Samsung's and SK hynix's October–January capital-return decisions.

**② The rate-reading fracture — RESOLVED. [Run 6 item ②]**

GS (~60% hike) and ISI ("under 50%" before hardening to a high-conviction hike call on 14 September) were right on direction. ISI was wrong on the vote (unanimous, not 10–2) and on the dots (a 2027 hold, not cuts). **TMTB's "~60% odds of a 35bp+ cut" was the mis-specified side**, and TMTB was still printing "~70% September cut" on 11 September. Logged as a source quirk.

*Replaced by ②′ — the 2027 Fed path.* UBS models ~−25bp of cuts in 2027 and calls this its single most important macro assumption for long-duration tech. ISI has stopped restating its 2027 cut. The market prices hikes: +55bp to +95bp through 2027 depending on the day. Emanuel floats a 50bp October "rip the band-aid" scenario. *Status:* **LIVE.** **Resolving evidence:** ISM (~1 October), September payrolls (2 October), the 28 October FOMC, and September CPI (which UBS expects to mark the peak).

**③ and ④** were retired in Run 6 and stay retired. The CoWoS question was answered again this run in the same direction and further: the gap narrowed to ~10%, and N3 and substrates took over as the bottleneck.

**⑤ Whether AI monetisation is real, and where it accrues. [ADVANCING — the scissor adds a price dimension]**

*Bullish:*
- **Enterprise spend at the top:** one UBS customer went from $1m to $10m a month in 8–9 months; AI budgets +20–25% in 2026 and +30–40% in 2027 (UBS partner).
- **Adoption:** daily tokens rose from ~1trn in January to ~18trn in September (UBS APAC); OpenRouter agentic tokens are up 14x in seven months (ISI). OpenAI's enterprise mix crossed 50/50, ads run at $1bn, and Codex went from ~100k to ~25m users (ISI).
- **Lab economics:** Anthropic reported positive adjusted operating profit for a second quarter at >80% gross margin before training and partner share (FT via Red-Ring and TMTB).

*Bearish:*
- **Buyers:** Uber's token spend is flat on broader usage; EY says only one in ten enterprises can show ROI.
- **Prices:** list prices were cut 40–50%.
- **Seats:** Copilot discounts of 30–50% for large enterprises; Agentforce deployment success at one large partner was only ~8% (Jefferies).

*The open-model sub-dispute (Run 6) resolves contextually, as Run 6 predicted:*
- ISI measures open-source token share at ~30% → ~80% from June to September.
- Replit uses *less* open-source since OpenAI cut prices.
- Regulated banks bar Chinese open models but adopt open-weight ones for cost (Nemotron may now be the top enterprise open-weight model).
- At one bank, Anthropic holds 60–70% of token spend and Gemini under 5% (UBS).
- NSR's revised profit pool: frontier models take 35% of tokens and ~80% of gross profit, and leading-edge models earn ~20x the profit per token of open-weight.

*Status:* **UNRESOLVED, but the question has changed.** It is no longer "is there revenue" but **"does usage grow faster than price falls, net of rising compute rents."** Labs "need usage to grow faster than prices fall" (ISI Mahaney). **Resolving evidence:** Anthropic's S-1 (now November); OpenAI DevDay (29 September); CY27 neocloud recontracting prices.

**⑥ The valuation-horizon split — ESCALATED from "PTs are a corrupted signal" to "earnings up, multiples down written into models."**

Run 6's ISI example (AVGO held on CY28 EPS discounted two years; CIEN cut a third while estimates rose 24%) now has company:
- **Micron (UBS):** PT unchanged at $1,625 while C2029 EPS rose from $165 to $219; the multiple fell from 11x to 8x on a 5.00% 10-year in the cost of equity.
- **AMAT and CAMT (MS):** targets cut while EPS was raised.
- **MSFT (Stifel):** upgraded with FY28 estimates cut.
- **META (Wells):** PT +24%, all multiple.
- **CIEN (ISI):** upgraded to $550 on *undiscounted* FY29 EPS, ~32x CY28E; the analyst's own slide shorthand implies $500.
- **CRDO (Mizuho):** PT $290 → $245 on peer multiples, with the fundamental checks positive.

*Status:* **LIVE and broader.** The rule from Run 6 stands: read the EPS revision and the stated horizon, never the headline PT. There is a new corollary. **Rates, not unit pricing, are now the input most likely to move memory PTs next:** on UBS's own framework, another 50bp on the 10-year at unchanged EPS implies a Micron PT cut.

**⑦ Vendor financing — additive capital or relocated leverage? [ADVANCING — both sides now quantified, discrimination confirmed]**

- **Additive (NSR):** the guarantors are named and sized (>$1.4tn of facilities; ~$128bn of hyperscaler backstops), and guarantor EBITDA can carry it. NVIDIA's ~$300bn of backstops sit against ~$260bn of EBITDA and net cash.
- **Relocated (MS credit):** ~$170bn of NVIDIA contingent exposure is Neutral-rated, "sidelined". NVIDIA CDS +36bp QTD. The "same facts, opposite signs by asset class" framing is MS's own.
- **The price signal:** it discriminates, and the gap is widening. CoreWeave is at 811bp against hyperscalers at ~88bp; QTS −84bp against ZENARC +138bp; Jupiter debt is below 90 cents.

*Status:* **LIVE, and the answer is "both, by tier."** Guarantor balance sheets make the aggregate additive. The concentration of residual-value, revenue-floor and lease-guarantee exposure on a few guarantors relocates the tail. **Resolving evidence:** NVIDIA's next 10-Q contingent-commitment disclosure; CoreWeave CDS direction; the Anthropic–Stream guarantee terms.

**⑧ The un-repriced 52% OpenAI backstop cut — PARTIALLY PRICED, through credit rather than equity.**

Run 6 called this the cleanest live test because the market was visibly not watching. It is now being priced, just not where Run 6 looked:
- NVIDIA CDS is +36bp QTD, and MS moved NVDA credit to Neutral.
- The FT names NVIDIA and Oracle as suppliers dependent on OpenAI's financing.
- Rothschild's Sell initiation on the neocloud tier is built on "circular" demand.
- NVIDIA *equity* still trades at ~19x NTM (ISI) with the backstop invisible in the multiple.

*Status:* **The "was it load-bearing?" question is answering "partly yes"**: the credit market is treating NVIDIA's guarantees as real exposure. **Resolving evidence:** NVIDIA's 10-Q backstop drawn balance (only ~$35bn of the $125bn cap was drawn at Run 5); a formal credit-desk downgrade.

**⑨ Bloom versus PowerGen LCOE — LIVE, now with a live test case.**

- **UBS supports Bloom on method:** its "delivered cost of electricity" framing counts grid transmission, congestion and reliability costs, so on-site SOFC compares better than on headline LCOE. UBS's own Bloom EPS nonetheless sits *below* the Street ($2.95 / $5.56 vs $4.90 / $7.74).
- **The live test:** Oracle's Jupiter is a 2.45GW single Bloom-powered microgrid whose gas pipeline route has been rejected twice. ISI's defence moved from "committed COD" (24 Sep) to "economics tied to delivery to financiers" (25 Sep), and ISI concedes Bloom has disclosed no Jupiter-specific MW. MS calls the force-majeure notice a contractual protection: 1.2GW of 2027–28 contracts is worth ~$1.25bn of EBITDA and is redeployable.
- **Competition:** Ceres warns licensed SOFC capacity "could… pressure pricing" from 2028. BE's NTM EV/EBITDA fell ~40 turns QTD, to 66.5x.

*Status:* **LIVE.** **Resolving evidence:** whether the Jupiter volumes sit in the firm 1.2GW or in the 1.2 → 2.8GW upside; the air permit; the gas route.

**⑩ Neocloud equity versus neocloud credit — NEW, and the run's sharpest two-asset-class disagreement.**

Four equity houses are bullish on scarcity pricing (UBS, JPM, ISI on CRWV; BNP on NBIS). Two are bearish (Rothschild: "a credit-cycle contest"; Bernstein Underperform $74). Credit is priced as distressed (811bp; notes at T+850). On JPM's own model, net interest nearly equals adjusted EBIT in FY28. Run 6's framing of neoclouds as "the AI that has to borrow" is not contradicted by the upgrades. The upgrades are a bet that **short-dated price inflation outruns the cost of the debt that funds it**, and in the same week ISI documented token prices halving. *Status:* **LIVE.** **Single flip test:** CY27 recontracting prices (ISI: "high-single to low-double-digit % of revenue comes off first 5-year contracts in CY27"; ~10% renewing at a ~100% spot premium would lift CY27 revenue +8% and EBIT +33%) and the direction of CoreWeave's CDS. CoreWeave's AI Cloud Conference on 30 September should show the lab versus non-lab backlog mix.

**⑪ Safety pacing — demand-negative or compute-additive? — NEW, and resolved within the window toward additive.**

- **The bear leg (11–14 Sep):** Altman's slowdown remarks, Amodei's pacing essay, a departing researcher ("gambling with all our lives", WSJ), and a −5.5% semis day.
- **The resolution (by 18 Sep):**
  - NSR: ~80% of training compute is already non-pretraining, and pacing *raises* compute.
  - Jefferies: trust and safety requirements drive more compute.
  - Anthropic: ~30,000 agents, every action screened, and the screening itself consumes inference.
  - Accenture: evaluators embedded at Anthropic, a ≥$1bn joint commitment. ACN rose 5% three days after being downgraded with its PT removed.
- **Who stayed bearish:** only Kass (ex-OpenAI, via an AI-generated readout, grade d) holds a coordinated slowdown as his base case.

*Status:* **RESOLVED as a demand question. OPEN as a political tail.** The social-licence and regulatory numbers in Layer 4 are rising in the same weeks consumer agents took off.

**⑫ Late innings versus infinite demand — NEW, a split inside ISI and between houses.**

- **Lipacis (ISI) — late innings:** the September quarter is peak industry growth (~70% y/y, fading toward ~40% by late 2027); semis NTM earnings are +316% over 34 months, about 4x a median cycle; the SOX's relative run is a 25-year record at +195% over 15 months; OEM inventory is +70% and double-ordering has started. He is still long, through dispersion: low-P/E NVDA and AVGO, plus turnarounds.
- **Against, in the same week:** Ross (ISI) targets the S&P at 8,300 and calls semis his "highest conviction"; UBS writes "no signs of AI demand abating"; MS puts memory at 53% of 2027 capex.
- **The tape sides with neither camp:** it rewards the high-multiple CPU names (INTC +232% YTD, AMD +193%) over Lipacis's low-P/E picks (NVDA +20%, AVGO +2%).

*Status:* **LIVE.** This is the #4 clock (ISI's September 2026 – January 2027 mid-cycle window) now argued from inside ISI with price data behind it.

**⑬ Muse and agentic value capture — NEW.**

*Evidence of scale:*
- ~3m US downloads by about day 15–20, a steeper curve than ChatGPT's. Global DAU went from ~70k to ~710k in 10 days (Similarweb via TMTB).
- META +11% on 21 September, its second-largest non-earnings move.

*Evidence of economics:*
- MS: ~$10 per user per year (>$1bn per 100m users). StoneX: subscriptions mostly cover the VM, browser and compute cost, deepening rather than resolving META's AI ROIC debate.
- Oppenheimer: only 8% of US consumers would trust Meta with passwords, against 30% for Google.
- Amazon blocked Muse from shopping, citing credential capture, while opening an official Claude seller plugin.

*Evidence of redistribution:*
- The Consumer Friction basket fell 10% and OTAs fell 5–10%; EXPE app MAU is −11% y/y.
- SHOP was reclassified as an "integrated" winner (Shop Pay inside Muse). TWLO split: TD Cowen raised to $300, while HSBC cut to Reduce at $211 because Meta's own voice stack captures the value.

*Status:* **LIVE. The adoption is proven; monetisation is unquantified.** The usable rule (ISI; TMTB): **the winners are the non-bypassable billing nodes** (EDA consumption, traces, identity, payment rails, CPUs and memory). The losers are intermediaries whose value was the customer relationship.

**⑭ UBS's intra-house 2029 memory split — NEW.**

- **Arcuri (US):** Micron's C2029 EPS is 36% *above* consensus, because LTA floors plus buybacks (~$100bn in F27 and ~$190bn in F28 once the CHIPS limits lapse on 9 December; share count −32% by F30) protect *per-share* earnings through a revenue decline.
- **Gaudois (Seoul):** Samsung and SK hynix 2029 operating profit 22–26% *below* consensus, with 2029 DRAM ASP −26%. CXMT is the first UBS model to show an outright 2029 revenue decline (−31%).

Both teams keep the DRAM upcycle to ~2Q28. *Status:* **LIVE.** It is a disagreement about whether capital-return structure beats the cycle. Per the standing rule that intra-house splits are signal, track which team revises first.

### Retired from the Run 6 registry

- **② The rate-reading fracture:** resolved by the 16 September decision (above) and replaced by ②′.
- **Nothing else is retired.** ③ and ④ were retired in Run 6.

---

## §4 — Near-term outlook (weeks: 28 September – mid-November)

**Why nothing broke, and why that matters for the next six weeks.** Run 6 expected the macro gate to decide September. It did decide it, hawkishly, but by then the market had already washed out on a different story. The 14 September pacing flush did the de-grossing. Semis fell 5.5% in a day and TMT momentum fell 6%, with yields *rising*, so it was a positioning event rather than a macro one (TMTB; Red-Ring). By the time the 5-year went through 5% on 23 September, the complex was rebuilding exposure rather than cutting it.

**Positioning says** the cushion that absorbed September has been used up:
- **Flows (UBS desk, grade d):** CTAs re-levered from the 13th to the 37th percentile, and retail bought the dip at the 97th percentile, for the 7th time in September.
- **Leverage and hedging:** hedge-fund tech net leverage is at the 100th percentile (UBS desk, d); mutual-fund cash is 1.2% (GS via Red-Ring); the QQQ put/call ratio is at the 10th percentile (UBS desk, d).
- **Breadth:** only 49% of the S&P trades above its 200-day with the index near highs (Krinsky via Red-Ring).
- **Where the two ISI voices land:** Emanuel's CIO panel reports that "nobody is shorting." Two of his four top conditions (10Y above 5%, a hiking Fed) are now met, against none on 6 September. His posture is "long-term offense, near-term defence," and his 7,750 target has gone unrestated three times. Ross (technicals) targets 8,300 with semis as his highest conviction.

**Fundamentals say** there is no estimate problem in the next six weeks:
- **Guides:** 84% of semis guided above the Street (UBS). Micron's 30 September print is modelled above guidance: UBS has $52.4bn and $32.50 EPS against a $50bn guide.
- **Capex:** hyperscaler capex plans are unchanged, and the contracted tier of every bottleneck is tightening.
- **The one live fundamental risk inside the window** is the un-contracted memory tier (see ①), and the market is already pricing it: Micron trades at 7x NTM (ISI).

**Base case (~50%) — choppy, rates-led range; dispersion rather than direction.** The NDX holds within ~5–8% of its 22 September high (30,771) while the 10-year stays at 5.0–5.3%. Two rotations continue under the index:
- *Contracted over spot:* the allocated memory tier, N3 and optics rise while the commodity channel and PC/phone OEMs lag.
- *Billing nodes over intermediaries:* Muse-exposed rails (SHOP, CPUs, observability, EDA consumption) rise while OTAs and consumer-friction names lag.

Credit keeps widening at the borrower tier without contaminating the guarantor tier. **Named triggers that keep it here:**
- Micron guides FQ1 in the $57–59bn range with SCA/LTA commentary that supports the contracted tier (30 Sep).
- ISM (~1 Oct) and payrolls (2 Oct) do not force an October hike (72–80% priced).
- CoreWeave's 30 September conference shows a non-lab backlog share that stabilises the name.

**Bull case (~20%) — a relief rally led by long yields.** The 10-year falls back toward ~4.80%, which the UBS desk calls the level that forces short-covering: bond CTAs are 100% short and at the 1st percentile over five years. Two events could do it: Iran's MOU proposal turning into a Hormuz reopening (Brent below $95), or a soft ISM and payrolls pair that takes October off the table. With CTA equity exposure only at the 37th percentile and a record short in bonds, **a bond rally now works as a second long on AI equities, not a hedge**, because the stock–bond correlation is +28–60%. **Named triggers:** Brent below $95 *and* WTI below $95 (Emanuel's de-hedge level); the 10-year below 4.85%; a priced October hike falling below 40%; Anthropic confirming a November pricing date.

**Bear case (~30%) — the rates shock meets a crowded tape, and the borrower tier cracks.** The 10-year pushes toward 5.4–5.5% on a hot ISM or payrolls print or on an oil spike: Iran has threatened to extend the war to the Indian Ocean, and global oil inventories sit in their bottom decile since 1990. The Fed hikes on 28 October, and on Warsh's "policy is as policy does" framework he says more is coming. With HF leverage at the 100th percentile and QQQ put/call at the 10th, the drawdown resembles Emanuel's macro-correction set (average −12.9%, 2018 Q4 analogue −20%). It is also consistent with Lipacis's ~−25% index-terms consolidation.

The **first place it shows is credit**, not equity: CRWV CDS above 1,000bp, a second hyperscale-campus markdown after Jupiter, or a failed or sharply repriced AI-infra deal. **Named triggers:**
- The 10-year closes above 5.3% and the 30-year above 5.5% (BofA's 30Y band broken).
- CRWV CDS goes through 1,000bp, or HY OAS moves above 350bp (from ~305–315bp).
- The SOX takes out its 14 September pacing low, which is Emanuel's bull-invalidation level ("Situational Awareness lows").
- Micron guides below $55bn, or reports a contract-price q/q in single digits for 4Q.

**The calendar that decides it:**

| Date | Event | What it tests |
|---|---|---|
| 29 Sep | OpenAI DevDay; MDB investor day | Token pricing/tiering ($500 Pro Max rumour, grade d); seat-to-consumption transition (#30) |
| 30 Sep | **Micron FQ4**; SNPS investor day; CRWV AI Cloud Conference; BEA PCE revision; HPE Networking day | ①, #7, #9, #19; #10 EDA consumption; ⑩ lab mix; #26 |
| ~1 Oct | ISM manufacturing | October hike odds (ISI Guha's condition) |
| 1 Oct | Nebius on-demand price increases take effect; SoftBank's $10bn OpenAI contribution due | #6, #32; #33 |
| 2 Oct | September payrolls | #26 |
| 5 Oct | CME / Silicon Data compute futures launch | #6, #32: first exchange price for compute rent |
| 6 Oct | MRVL and ZS investor days | #15; #30 (non-seat ACV share) |
| 9 Oct | Micron Taiwan board; possible union action | MU supply risk (low) |
| ~Mid-Oct | TSMC 3Q print; SK hynix shareholder-return package | #1; #3 |
| 13 Oct | Bank earnings | C&I loan growth (AI/DC financing) |
| 19 Oct | Texas TCEQ update on the permit halt | #31 |
| 28 Oct | **FOMC** (hike 72–80% priced); ORCL investor day | #26; ⑦/⑧, Jupiter |
| 3 Nov | US midterms | #31, AI-safety legislative tail |
| ~5 Nov | SPCX lock-up (~1.3bn shares, ~$196bn) | #16 equity supply |
| November | **Anthropic IPO** (target); APEC Shenzhen; US–China AI dialogue #2 | #33; Layer 4 |

---

## §5 — Medium-term outlook (quarters: 4Q26 – 3Q27)

**Fundamentals say** 2027 is supply-capped rather than demand-capped, and the cap sits in more places than it did three weeks ago:
- **Chips and materials:** N3 at 106–113% utilisation (UBS); DRAM fulfilment ~60%; ABF 48–56-week lead times; HDD 50 weeks (TrendForce); InP prices +50–60% (Red-Ring, c); turbines with up to 7-year lead times (ISI/Ceres).
- **Sites:** permits (Texas halt); energised shells, with 7.0GW of US capacity delayed (UBS).
- **Capex:** estimates for 2027 are firm: top-12 hyperscaler capex $1.45tn (UBS), $1.39tn (MS), $1.4–1.45tn (ISI).
- **The real 2027 question is deliverability.** UBS's semis estimates imply ~51GW of 2027 AI capacity additions against a market that can deploy 30–50GW a year, so **chip supply may outrun powered shell in 2027–28**. If digestion comes, it arrives through sites, power and financing, not through demand.

**Positioning and valuation say** multiples are compressing into rising earnings, and that is now written into the models (⑥):
- Micron's multiple has been cut from 11x to 8x (UBS); AMAT and CAMT targets were cut on raised EPS (MS).
- ISI has SOX NTM P/E compressing from the mid-30s to ~20x.
- The medium-term equity return is EPS growth minus de-rating. Over the past year, S&P EPS rose 36% while its P/E fell 16%; for IT, EPS rose 85% and P/E fell 32% (ISI).

**Base case (~55%) — "2027 boom, 2028 brake"; earnings up, multiples down; the borrower tier refinances at a price.**
- **Capex:** hyperscaler capex grows ~+45–60% in 2027 and ~+12–14% in 2028 (MS; ISI).
- **Memory:** contract prices decelerate through 1H27 and peak around 2Q27 (Citi); memory equities peak around 4CQ27, ahead of the 2CQ28 profit peak (UBS Gaudois).
- **Neoclouds:** they keep refinancing at 10–13% all-in, so CY27 recontracting has to clear a take-or-pay ROIC of ~8–10%, which is about the HY cost of debt (ISI).
- **Frontier labs:** Anthropic's IPO prices, whether before YE or in 1Q27, and OpenAI is funded through 2027. The token-versus-rent scissor narrows slowly as new capacity lands in 2H27.
- **Leadership:** migrates from pricing-leverage names to contracted-content and trough-multiple names (MS AI 6.0 rotation; Lipacis dispersion).
- **Named triggers that confirm it:** TSMC's 2027 capex at $74–80bn with 1Q27 price increases holding; 1Q27 DRAM contracts settling above 4Q26 (BofA's CSP agreement); CRWV's first 5-year contract roll in CY27 clearing at a premium to installed pricing; hyperscaler IG spreads holding within ~100bp of the 88bp CDS average.

**Bull case (~20%) — adoption outruns deflation, and the capital markets underwrite the borrower tier.** Agentic usage grows fast enough that lab revenue closes the capex gap early:
- **Adoption:** daily tokens have gone from ~1trn in January to ~18trn; OpenRouter agentic tokens are up 14x in seven months; Muse reached ~3m US downloads in about 20 days.
- **Lab revenue:** Altimeter's "what has to be true" is ~$1tn of 2029 lab ARR against $1.3tn of hyperscaler capex. Anthropic's IPO prices at or above ~$2tn and re-opens equity for the borrower tier.
- **Macro:** the Fed reaches its terminal rate in December and cuts from mid-2027 (the UBS path).
- **What gets bought:** everything scarce re-rates, and the borrower tier re-rates most.
- **Named triggers:** CRWV CDS back below ~550bp (its pre-QTD level) *while* the HY tech wall refinances; the Anthropic S-1 showing positive operating margin at scale; CY27 recontracting at or above 50% premiums; the 10-year back below 4.7% with the 30-year below 5.3% (BofA's band).

**Bear case (~25%) — the financing channel breaks before demand does.** The Fed keeps hiking into 2027 on AI-driven inflation, which is the Barr and Warsh reaction function taken literally. Long yields reach 5.5–6%. Four things then fail in sequence:
1. **The borrower tier cannot refinance.** CRWV's ~$102bn 2027–30 funding gap (UBS) meets the $119bn private-credit tech wall of 2028–29 (UBS credit), and a neocloud or campus SPV defaults or restructures.
2. **Guarantor exposure becomes the story.** NVIDIA's ~$170bn of contingent exposure (MS) and Google's lease guarantees (NSR) move from footnote to headline, and NVDA credit and equity re-price together.
3. **Frontier-lab funding stalls.** The Anthropic IPO slips into a stressed 2027, which Emanuel says could catalyse "hyperscaler issuance woes." OpenAI's runway is shorter than the $122bn raise implies.
4. **The un-contracted memory tier rolls into the contracted tier.** 2027 recontracting happens at lower prices, CXMT's G5 adds ~5% of global bits (Commercial Times via TMTB), and the Lipacis correction plays out (historical average −38% over 13 months).

**Named triggers:** a second hyperscale-campus force majeure or a markdown below 80 cents; NVIDIA disclosing a drawn backstop above ~$50bn or a rating-agency outlook change; the Anthropic IPO withdrawn or priced below its $965bn Series H mark; 1Q27 DRAM contracts settling below 4Q26; hyperscaler 2027 capex guides *cut* in January (none has been cut to date).

**Break condition for the whole stance (see §7).** Drop the underweight on the borrower tier and go long outright only if all three of these happen: CRWV CDS falls back below ~550bp, the Anthropic IPO prices before year-end, and CY27 recontracting clears at a premium to installed rates. Each alone is noise. Together they mean the capital markets have decided to underwrite the borrower tier, and Run 6's "credit is binding" thesis would be wrong.

---

## §6 — Monitoring checklist

Run 6 carried 30 live indicators (#1–#11 and #13–#31; #12 was retired on 14 July 2026). **No indicator is retired this run, and two are added: #32 and #33.** Row count reconciles: **30 − 0 retired + 2 added = 32.** One *source* is retired: the Humanoid workstation, which has now been silent for five consecutive runs since 12 July. Indicator #23 stays live and is served by UBS, MS and IFR (see the row).

**How triggers were handled.** Where a Run 6 trigger fired, the row is marked **FIRED** and given a *fresh* trigger pair; the old pair is not left standing. Fired this run:
- **Bear side:** #8, #21, #22, #25, #26 (all three legs) and #31.
- **Bull side:** #10, #20 and #24.
- **Partially:** #30.
- **The duration hedge in #17 is marked Contradicted.**

| # | Indicator | Status | Updated baseline | Bullish trigger | Bearish trigger | Next checkpoint |
|---|---|---|---|---|---|---|
| 1 | TSMC / CoWoS / 2027 capex | **Confirmed — the bottleneck has moved from CoWoS to N3 and substrates** | CoWoS end-2027 260k wpm (UBS SEMICON) / 270k (UBS Lin: TSMC 180k, ASE 70k from 20k, Amkor 20k); TSMC share 81% → 67% 4Q26–4Q27. JPM puts the CoWoS supply gap at only ~10%; **N3 utilisation 106–113% (UBS)**, with Cloud AI at 73% of 2027 N3 and NVDA its largest client at 31%. TSMC capex $63/80/95bn 2026–28E (UBS) vs $56 → $74bn (ISI; bull case $80bn). **2027 wafer prices +3–6% from January** (DigiTimes, grade c). TSMC trades at 17x/12x 2027/28E vs the SOX at 29x/20x (UBS) | The October print frames 2027 capex at or above $74–80bn and confirms 1Q27 price increases; N5/N4-to-N3 tool conversion is on schedule | 2027 capex framed below $70bn, or the 1Q27 increases are withdrawn — either would say TSMC sees AI wafer demand rolling; N3 relief arriving before 2H27 | **TSMC 3Q print, mid-October** |
| 2 | Hyperscaler capex + monetisation | **Confirmed, and capex now exceeds operating cash flow** | Top-12 capex $1.01tn/$1.45tn/$1.62tn 2026–28E (UBS, ~unchanged); MS $861bn → $1,390bn → $1,591bn (hyperscalers + neoclouds). **Aggregate US cloud backlog >100% of total sales, from ~50% last autumn (UBS)**; cloud TTM bookings $1.4tn, +191% (ISI). Azure +43%, GCP +82%, AWS "lion's share of 2027 capacity reserved" (NSR). **Hyperscaler capex ~105% of OCF in 2026E, the first time above OCF (UBS)**, and FCF negative in 2027 for everyone except MSFT (ISI). ~60% of the 2026 capex increase is memory cost, not volume (UBS) | October prints raise 2027 capex with backlog growth outpacing capex growth; the non-lab share of backlog increments holds (MSFT's +$51bn Q4 RPO was all enterprise, per GS) | Backlog cover falls below ~3x; a hyperscaler cuts 2027 capex for reasons other than memory; capex/OCF moves above ~110% without a named financing bridge | **Late-October hyperscaler prints.** Keep tracking incremental GW rather than incremental dollars, because memory inflation is flattering the dollar series |
| 3 | Korea flows + capital returns | **Split — capital returns confirmed, flows contradicted** | UBS cut its KOSPI 12-month target from 8,800 to 8,000 on rates, KRW +11% and oil above $100. Foreigners sold Won33.2tn/22.2tn/12.1tn of Tech in Jul/Aug/Sep-MTD (Won198.9tn YTD); Tech is −28.6% over 3 months, and ISI puts the Jun–Jul blow-off at −44%. **Returns:** Samsung 2027E FCF Won448tn, UBS 2027E dividend yield 12.4%; SK hynix's shareholder-return package is due in **October** at >50% of FCF; JPM has SKH ~42% TSR 2026–28. Samsung + SKH are 64% of MSCI Korea (prior peak 67%). BOK has hiked to 3.0%, with December +25bp expected | SKH's October package lands above 50% of FCF and Samsung's January board extends the programme; foreign Tech flows turn net positive for a month | The package disappoints; foreign selling continues through a memory beat; BOK hikes beyond December | **SK hynix October package; Samsung board late January 2027** |
| 4 | SOX mid-cycle correction clock | **Live — the window is open and now argued from inside ISI** | Lipacis (25 Sep, all-client webinar): industry revenue growth **peaks in the Sep-26 quarter at ~70% y/y**, fading to ~40% by mid/late 2027. Semis NTM earnings +316% over 34 months (~4x a median cycle); SOX relative performance +195% over 15 months, a 25-year record; implied index-level consolidation ~−25%. The **June–September −22% SOX drawdown (UBS) was a first leg**; the pacing low on 14 September was retested and held, and the SOX is +79% YTD (ISI Ross). Emanuel: **2 of 4 top conditions now met** (10Y >5%, a hiking Fed), against 0 on 6 September | The SOX holds above its 14 September low through the end of January and the Sep-quarter industry print does not confirm a peak | The SOX takes out the 14 September pacing low (Emanuel's "Situational Awareness" invalidation); the Sep-quarter SIA data confirms the second-derivative peak; a third Emanuel top condition appears | **SIA September data (early November); the window closes end-January 2027** |
| 5 | Leverage / crowding | **Contradicted — the September washout re-crowded within two weeks** | HF tech net leverage at the **100th percentile**; CTA equity exposure re-levered from the 13th to the 37th percentile; QQQ put/call at the 10th percentile; household equity 49% of financial assets, above the 45% tech-bubble peak (all UBS desk, grade d). MF cash 1.2% and fundamental L/S gross/net at 207%/49.8% (GS via Red-Ring). Margin debt $1.5tn → $1.4tn (ISI). Only 49% of S&P names above the 200-day with the index near highs (Krinsky). Retail bought the dip at the 97th percentile | Breadth broadens (>60% of S&P above the 200-day) while HF leverage eases from the 100th percentile without a price shock | The SPX breaks 7,237 (June low) and then 7,157 (200-day; ISI) with HF leverage still at the 100th percentile; a third "risk-parity everything" sell-off after 10 and 14 September | **SPX 7,237 / 7,157; the 28 October FOMC** |
| 6 | GPU rental / neocloud unit economics | **Confirmed, bull side — rents are inflating across every tenor** | CRWV 8-K: 3–6-month contracts ~$40m/MW annualised (~3x long-term), July prices +25% across SKUs, ~70% of 2Q deals with prepayments. Nebius on-demand prices rise from 1 October (direction only; screenshot bases differ, grade d), with preemptible +26–72% (ISI). **Ornn B200 index $7.77/GPU-hr (+67.7% y/y)**; H100 spot +20–40% (ISI). Silicon Data lease-implied residuals: H100 58%, **B200 158% of purchase price.** Oracle renewals at a +20% premium at 97.9% utilisation. **But ISI puts take-or-pay project ROIC at only ~8–10%, roughly the HY cost of debt** | The 5 October CME compute futures clear consistent with Silicon Data marks; Nebius's 1 October increases stick through November; CY27 5-year rolls reprice upward | Short-dated premiums compress toward long-term rates; any month of falling H100 rents; CME futures print below the Silicon Data marks | **1 October (Nebius), 5 October (CME launch), 30 September CRWV conference** |
| 7 | DRAM / NAND contract prints | **Split — quarterly contract firm, monthly contract and spot rolling** | **Quarterly:** 3Q DRAM +20–30% q/q (BofA), UBS DDR +22–27%; **4Q guides +7–9% (UBS), +5–10% (MS), +7% (Arcuri), above Run 6's +3–8% band**; NAND contract +21/+17/+15% for 3Q26/4Q26/1Q27, raised (TrendForce); **CSPs agreed a higher 1Q27 DRAM ASP than 4Q26 (BofA)**. **Monthly and spot (ISI):** DDR contract +18–19% in August → **+2–3% in September**; NAND contract 0.0%; DDR5 16GB spot −1.8%, DDR4 16Gb −3.2%, NAND TLC −5.0%. **Unit warning: ISI's monthly series is not comparable with the quarterly q/q guides** | 4Q settles at the quarterly guides and 1Q27 settles above 4Q26, as BofA's CSP agreement implies | October monthly contract prints negative; 1Q27 settles at or below 4Q26; spot weakness reaches server RDIMM | **Micron, 30 September; TrendForce October contract; the 1Q27 settlement in December** |
| 8 | Memory de-spec + demand destruction | **Bear trigger FIRED: the ZS/IOT channel spread to a third, fourth and fifth sector** | Beyond ZS/IOT: **Apple** Dec-quarter GM ~−50bp vs consensus, with the 256GB iPhone 18 Pro Max BOM up ~$168 y/y, ~90% of it memory (Bernstein); **Ericsson** CFO sees memory-driven GM pressure through 2H26–2027 (NSR); **Nintendo** cut its Switch 2 FY28 unit target (BNP); **PCs** 2H shipments tracking −26% y/y, with HP giving no FY27 guide (MS); **Infineon's** auto customers are running "escalation calls" (UBS). Smartphones 2027E 1.11bn (−3%), with memory 35–37% of the flagship BOM (UBS). *Data-centre side:* Rubin Ultra HBM cut from 768GB to 512/384GB (UBS), read as volume-positive; SemiAnalysis argues 4-Hi wins inference | *(fresh)* 1Q27 device guides stabilise units while HBM de-spec keeps coexisting with rising aggregate bit demand | *(fresh)* A hyperscaler or NVIDIA cites memory cost as a reason to cut **unit volume**, not just margin; 2027 PC or phone unit forecasts cut by >10% | **Apple late October; HP FY27 guide (November)** |
| 9 | Micron / memory valuation frameworks | **Advancing — "earnings up, multiple down" is written into the model** | UBS $1,625 unchanged while C2029 EPS rose from $165 to $219, **on a multiple cut from 11x to 8x (cost of equity 12.2% at a 5.00% 10Y)**. Citi bull/base/bear $1,500/$1,300/$700; NSR $1,250; RBC OP $1,500 (strategic customer agreements ~half of revenue); MS CY27 EPS $180.48 (+12% vs Street). MU trades at 7x NTM (ISI). **CHIPS buyback limits lapse on 9 December**; UBS models ~$20bn a quarter from FQ2:27, rising to $40–50bn. SanDisk: Rosenblatt $2,400 on ~8x FY30 EPS | Micron confirms SCA/LTA coverage and a post-9-December buyback framework; a house raises a memory PT on rising EPS *without* cutting the multiple | On UBS's own framework, another +50bp on the 10Y at unchanged EPS forces a PT cut; a Micron beat is sold (#29 applied to memory) | **30 September print; 9 October board; 9 December CHIPS lapse** |
| 10 | Meta agent productivity | **Bull trigger FIRED — launched and adopted; monetisation unquantified** | *Mapping (inference): Muse is treated as the product this row tracked as "Hatch/PSI"; no source states the equivalence.* ~3m US downloads by about day 15–20, steeper than ChatGPT (Sensor Tower via Red-Ring and TMTB); global DAU ~70k → ~710k in 10 days (Similarweb); **META +11% on 21 September**, its second-largest non-earnings move. Power $20 / Max $100 tiers. MS: ~$10 per user per year. Oppenheimer: only 8% trust Meta with passwords. **Amazon blocked Muse shopping**; Watermelon at 70% odds by 31 October (Polymarket, d) | *(fresh)* The Q3 call quantifies paid conversion or Muse revenue; Watermelon ships by 31 October; merchant connectors keep expanding (Shopify, Walmart, Best Buy, Expedia) | *(fresh)* DAU plateaus below ~1m globally; merchant blocking spreads beyond Amazon; a credential or trust incident | **META Q3 print (late October); Watermelon by 31 October** |
| 11 | Enterprise token economics | **Advancing — now paired with the price scissor (#32)** | Token prices: Red-Ring index $0.97/Mtok (−21.9% YTD); ISI index ~$2 → ~$1; Opus 5.5 −40% per workload, GPT-6 Sol −50%. Usage: one UBS customer went from $1m to $10m a month; AI budgets +20–25% in 2026 and +30–40% in 2027 (UBS partner); daily tokens ~1trn → ~18trn (UBS). Against: Uber's token spend is flat on broader usage, and EY finds 1 in 10 enterprises can show ROI. Anthropic holds 60–70% of token spend at one bank; Yipit (d) has Anthropic's top 1% of customers at 46% of spend. **Anthropic ARR is quoted at four vintages — do not average them: $65bn (July, FT), ~$70bn (Yipit, d), >$100bn (September, second-hand table), >$110bn (a YE expectation)** | The Anthropic S-1 shows revenue growth outrunning price cuts with GM above 70%; DeepSeek-style price *rises* stick (ARR ~$1bn after raising prices 2.3–4.5x) | The S-1 shows GM compression from price cuts; a second large customer reports flat token spend on rising usage | **OpenAI DevDay (29 September); the Anthropic S-1 (November); Gemini 3.8 Flash's price doubling on 1 January 2027** |
| 13 | 2027 capex consensus vs buy-side bar (WFE) | **Confirmed — raised again, with ISI's own contradiction attached** | ISI raised 2026/27 WFE to $155bn/$215bn (bull case $225bn); memory capex $104bn → $194bn (+86%). **UBS's 2027 WFE ranges from $198bn (Lin) to $226bn (Arcuri) because the two desks define WFE differently**; JPM $159/$205/$237bn. ASML is exploring >110 EUV systems for 2028. MS: "DRAM the fastest-growing WFE segment in 2026, the slowest in 2027." **ISI's flag: memory makers accelerating capex (Samsung +75%, SKH +64%, MU +110%) just as spot turns is the classic memory-top pattern** | October semicap prints guide 2027 above $215bn while memory capex acceleration coexists with firm contract pricing | A memory maker raises capex while 1Q27 contract settles flat or lower (ISI's top pattern confirmed); any volume capex cut | **LRCX/KLAC/ASML October prints; Samsung and SK hynix capex plans in January** |
| 14 | Hyperscaler FCF / financing | **Confirmed — but no new data on either named trigger** | **No source updated IG Tech OAS against the March peak, or AVGO CDS against 126.2bp.** Proxies: hyperscaler CDS average 88bp (from ~60bp in January); ORCL 189bp, the widest IG name; MSFT 44bp. Alphabet's August deal came ~40% wider than February's at matched maturities, but books were still 3–5x. US IG tech issuance $321bn YTD vs $113bn a year ago; US IG pace $1.97tn annualised (UBS). UBS credit strategy went Underweight Tech (IG and HY). NSR restated hyperscaler FCF to trough at −$486bn in 2028 ("a large trillion-dollar problem, but an easy one") | Hyperscaler CDS average back toward ~60bp; new-issue concessions compress; jumbo books stay above 3x | Hyperscaler CDS average above ~120bp; a hyperscaler deal with books below 2x; the 10Y holds above UBS's 5% credit-headwind threshold into year-end | **The next hyperscaler jumbo deal; the 1Q27 debt-ceiling window** |
| 15 | ALAB / Trainium / custom silicon | **Advancing — the XPU field widened and reshuffled** | **QCOM–AWS $60bn, 10-year custom silicon + optical deal, with AWS warrants for up to 25m QCOM shares**: a third credible XPU entrant (UBS; ISI). **UBS Lin cut Marvell's 2027 Trainium units from 686k to 85k (Alchip 3.08m), while UBS's Arcuri keeps MRVL at Buy $310: an intra-UBS tension.** MS: ASIC units are 1.7x GPU units in 2027, and MS's base case puts the $120bn Marvell warrant at $85.6bn cumulative from FY29. Google TPU runs a dual track (AVGO v8i / MTK v8t). **AVGO 2027 revenue cut 6.7% to $193.4bn (ISI); MS has AVGO CY27 5% below the Street.** TorchTPU open-source due mid-October | Marvell on 6 October reaffirms FY28 $18bn and names a Trainium successor socket; Broadcom reaffirms FY27 AI revenue of ~$115bn | Marvell's Trainium loss is confirmed with no replacement; Broadcom's FY27 AI guide is cut; TorchTPU erodes CUDA lock-in faster than modelled | **MRVL investor day, 6 October; AVGO December print** |
| 16 | Leveraged / thematic ETF flows + equity supply | **Re-leveraging, with an equity-supply overhang now dated** | Leveraged semis ETFs $36.8bn AUM / $98.7bn notional, rebalancing up to 20% of ADV (UBS desk, d). Nasdaq September excess flow +$115bn; the first foreign ETF outflow since April (−$1.6bn). Korean 2x single-stock ETFs ~$6bn vs a $21bn peak (GS). **Equity supply:** SPCX lock-up of ~1.3bn shares (~$196bn) around 5 November; Anthropic raising up to $100bn; three AI IPOs worth more than 45 years of tech IPOs (TMTB, d) | Flows broaden beyond leveraged vehicles; the SPCX lock-up and Anthropic IPO are absorbed without SOX underperformance | Leveraged-ETF rebalancing amplifies a >3% semis day into a second-day flush; equity supply meets foreign ETF outflows | **~5 November SPCX lock-up; Anthropic pricing** |
| 17 | CTA / positioning triggers | **CONTRADICTED on the hedge: long duration lost money** | **Run 6 called long duration "the cleanest hedge." In the window the 10Y went from ~4.8% to ~5.2%, and the stock–bond correlation turned positive (+28–60%, UBS desk).** Bond CTAs are at the 1st percentile over five years and 100% short UST/LQD/HYG; equity CTAs rose from the 13th to the 37th percentile; post-FOMC CTA sell triggers "largely exhausted." "Fixed income no longer a hedge" (ISI CIO panel) | The 10Y rallies to ~4.80%, UBS's short-covering level, which lifts bonds *and* equities: a second long, not a hedge | The correlation stays positive and a rates-led drawdown hits both legs, a third risk-parity sell-off | **10Y 4.80% / 5.30%; the 28 October FOMC** |
| 18 | NeoCloud economics + frontier-lab buyers | **Split — pricing power up, balance sheets worse, labs bypassing** | CRWV backlog $104bn ($129bn including early 3Q); ~72% of revenue from three customers; ND/EBITDA 5.7x in 2026E; interest ~25% of revenue; external funding gap ~$102bn over 2027–30 (UBS). **JPM's own model: FY28 net interest $7.84bn against adjusted EBIT of $8.79bn.** **Nscale's S-1: ~$103bn signed backlog against ~$2.6bn active TCV (~2.5%).** Labs are bypassing neoclouds: OpenAI's 8GW SB Energy lease, Anthropic–Stream 1GW, and the Akamai CPU deal. SPCX's three compute contracts are cancellable on 90 days' notice, and Google's GPU-delivery deadline is 30 September | The CRWV conference shows a non-lab backlog share above ~40%; the first CY27 5-year rolls reprice at a premium (ISI: ~10% at a ~100% premium → CY27 revenue +8%, EBIT +33%) | A lab exercises a 90-day cancel or moves volume to self-build; a second neocloud shows an Nscale-style backlog-to-active gap | **30 September CRWV conference; SPCX's 30 September Google deadline** |
| 19 | DRAM cycle-top clock | **RESOLVED ON MECHANISM, and the timing is now dated (see §3 ①)** | Citi: prices peak **2Q27**, with ~60% of commodity DRAM bits outside LTAs. UBS Gaudois: memory **stocks peak 4CQ27**, profits 2CQ28. Arcuri: q/q DRAM momentum is peaking now. OEM inventory +70% vs trend; early double-ordering (ISI checks); Wolfe customer inventory 58 days (+52% y/y), mostly price-driven. Buyers: Raspberry Pi and Acer (grade c). Supply: CXMT's G5 ≈ +5% of global bits without new wafers; CXMT commitments at RMB52.4bn (+206%). *Run 6's decisive trigger ("channel inventory past four months") got no direct update to Red-Ring's month series; the proxies point to a build* | Micron confirms 2027 HBM4 pricing (+80–100%, RBC) and LTA coverage above 50%; bit-denominated (not dollar) inventory stays flat | 1Q27 contract settles below 4Q26; spot declines reach allocated server DRAM; channel inventory past four months confirmed in bits | **30 September; October spot series; December 1Q27 settlement** |
| 20 | ABF / substrate / packaging → upstream | **Bull trigger FIRED — tightness persists through expansion; NPO partly corroborated** | InP delivered prices +50–60% (Red-Ring, c); Sumitomo/AXT hold ~85% of supply; InP capacity +81%/+32% in 2026/27, with no meaningful 6" relief before 2028 (Mizuho). **Lumentum prepaid AXTI $43.5m to reserve supply to 2031**; Coherent's 6" InP reaches 75% of output by end-2027. **COHR: scale-up CPO/NPO in 2H27, a partial second-vendor corroboration of LITE's NPO pull-forward (grade c)**; MS ECOC has first-gen NPO trials in 2028. ABF 48–56-week lead times; ABF laminator lead time 6 months → 2 years; 12" wafer LTAs +15–25%; Samsung 4nm +10–15% on HBM4 base-die demand | *(fresh)* 6" InP ramps in 2027 *without* price declines (LTAs hold the price); COHR/LITE confirm NPO revenue in 2H27 | *(fresh)* Equipment over-booking unwinds (PCB tool orders to 2028, a possible double-book); ABF lead times fall below ~30 weeks; InP prices fall on the 6" ramp | **COHR/LITE early-November prints; OFC, March 2027** |
| 21 | Hyperscaler credit spreads / SPV pricing | **Bear trigger FIRED at the neocloud tier** | **CRWV CDS 811bp (+259bp QTD); notes from T+530 → ~T+850**, so the tenant spread over the ~88bp hyperscaler average is ~720bp against Run 6's ~250bp threshold. **Jupiter project debt was sold below 90 cents.** ZENARC HY +138bp on a permit denial vs QTS (IG) −84bp; HY DC paper +55bp since issue; DC ABS BBB +17bp since August (UBS). **SoftBank's OpenAI-funding bond expected at BB+.** NVDA CDS +36bp QTD, now trading like A1 (MS) | *(fresh)* CRWV CDS back below ~550bp; Jupiter debt recovers above 95 cents | *(fresh)* CRWV CDS above 1,000bp; a second hyperscale-campus markdown below 80 cents; hyperscaler CDS average above ~120bp (contagion into the guarantor tier) | **30 September CRWV conference; ORCL investor day, 28 October** |
| 22 | Rubin / Kyber delivery | **Bear trigger FIRED — the Kyber slip is formalised** | **Kyber NVL144 slips to 2028**: 800VDC sidecar to 2028 HVM (UBS); all-copper NVL144 removed from the 2027 plan (Red-Ring rack expert, c); TMTB's correction that this is Kyber only, not all of Rubin Ultra; ISI's Virgo "Rubin/Kyber delays". The 2027 mainline is NVL72 plus NVL576 (8 racks via CPO/NPO). Rubin ships 2.0m units in 2H26 after a redesign; the compute board slipped 6–8 months (expert, c); Dec-26 tray output ~45k; rack yield ~80% against a 90% target; 2027 rack demand ~80k, ~60% firm (c). MLPerf: VR200 ~2x GB300 per rack | *(fresh)* NVL576 on schedule for 2H27; December compute-tray output at or above ~45k; rack yield reaches 90% | *(fresh)* A second slip that touches VR200 NVL72 volume in 1H27; rack yield stuck below 85% | **NVDA November print; monthly ODM revenue** |
| 23 | Humanoid | **SOURCE RETIRED (5th silent run); indicator kept, served by UBS, MS and IFR** | UBS raised humanoid units by 73–123%: 51.9k in 2026E, 94.4k in 2027E, 305.9k in 2030E; "no EV moment" before 2030; 45% of 2025 units went to research and data collection. IFR/Reuters: ~7,000 units sold globally in 2025. **The perimeter differs from MS's 50k for 2026e; do not compare the two.** Optimus revenue has slipped to ~2029; the Unitree IPO went 151 → 1,100 → 530 yuan (ISI) | Repeat commercial orders at scale; a second-quarter unit print confirms UBS's raised path | Valuation deflation spreads beyond Unitree (−52% from peak); a component ASP war | **Tesla Q3 (October); UBS APAC humanoid update** |
| 24 | Server CPU / agentic | **Bull trigger FIRED — the first frontier-lab CPU contract** | **Akamai–Anthropic $11.6bn, 7-year, all-CPU (8-K, grade a)**, ~95–105MW, ~$22m/MW/yr. **Jabil holds ~$1.7bn of Akamai *memory* on consignment, more than the CPU spend**, so "a CPU contract is a memory contract." Mercury: server CPU units +27% y/y, AMD 28% (+445bp), Arm 18% (+560bp). CPUs are up to 90.6% of agentic latency; every OEM's agentic tier runs on NVIDIA Vera (ISI). MSFT: CPU now exceeds GPU in short-lived capex. *Counter (d):* M Science has AMD new-CPU deployments in 1H September negative y/y | *(fresh)* A second frontier-lab CPU contract; AMD or Intel raise server-CPU guides in October | *(fresh)* M Science deployments stay negative y/y through October; CPU tightness turns into price-driven double-ordering, as in memory | **AMD / INTC late-October prints** |
| 25 | Optical transceiver gap + regulatory | **Bear trigger FIRED (proposal only, NSS-scoped); demand side confirmed** | **Senate bill of 25 September (McCormick/Gallego/Cornyn/Fetterman) would bar InnoLight and Eoptolink transceivers from federal national-security systems, with a 5-year transition. It is a proposal, not law, and not a commercial DC ban.** Demand: CIEN upgraded to $550, backlog >$10bn, high-single-digit to 20% price increases including on existing backlog, "not balanced before 2028"; LITE EML/CW demand exceeds supply by >30% with a >2-year backlog; OCS >$1bn in 2027 (Globlex, c). GS cut 2026 CPO shipments 33%; CPO mass production 2028–29 | *(fresh)* The bill stays NSS-scoped or dies; LITE/COHR confirm NPO revenue in 2H27 | *(fresh)* Scope expands to commercial data centres or hyperscaler procurement (e.g., an entity listing); CPO/NPO slips to 2029 | **Senate committee action; COHR/LITE prints; OFC March 2027** |
| 26 | Macro gate (Warsh / oil / rates) → **②′ the 2027 Fed path** | **All three bear triggers FIRED** | **Hike on 16 September, unanimous, to 3.75–4.00%**; median dot 4.1% for 2026 and 2027. **10Y ~5.2%** (5.197% on 25 Sep; Red-Ring); the 5Y closed above 5% for the first time since 2004; 30Y ~5.36–5.40%. Brent $100–104; WTI ~$100. Diesel: **EIA $5.97 (+58% y/y)** is the benchmark (other series $6.30–6.50). Core CPI +0.3% m/m. **Warsh and Barr both named AI financing and investment.** Market pricing ~95bp of hikes through October 2027 (UBS), with October at 72–80% | *(fresh)* The 10Y falls below 4.85% with Brent below $95 and October hike odds under 40%; the BEA revision lowers core PCE ~20bp | *(fresh)* The 10Y above 5.3% and the 30Y above 5.5%; on 28 October the Fed signals hikes into 2027; Brent above $110 | **30 Sep BEA; ~1 Oct ISM; 2 Oct payrolls; 28 Oct FOMC; 1Q27 debt ceiling** |
| 27 | Power / speed-to-power | **Confirmed — the shortfall is revised up and delays are now tracked** | MS: 2026–28 US DC demand 68GW → **97GW**; gross shortfall 57GW, **net 33GW**; 2029 net shortfall 72GW. **UBS's DC delay tracker: 7.0GW currently affected in the US (16.9GW ultimately)**, with the curve steepening since March. Turbine lead times up to 7 years (ISI/Ceres); planned gas capacity pushed to 2029–30 (EIA). GS raised 2030 BTM to 67GW from 40GW; Generac–Amazon deal up to $8bn. ERCOT 2027 forward ~$38–39/MWh (down); PJM 2028 ~$69 | UBS's delay curve flattens; BTM deployments (Bloom 1.2GW, Generac) land on time | UBS-tracked affected capacity above ~10GW; a second hyperscale-campus force majeure | **UBS monthly tracker; 19 October Texas update** |
| 28 | AI financing circularity / contingent liabilities | **Escalated — "load-bearing" is now being priced, in credit** | MS: NVIDIA's all-in contingent exposure ~$200bn by end-CY28, **~$170bn off funded debt**; credit Neutral, "sidelined"; DSO 45 → 60 days. NSR: **>$1.4tn of NVDA/AVGO-architected facilities; ~$128bn of hyperscaler backstops; NVDA ~$300bn of backstops vs ~$260bn EBITDA; SB Energy $170bn guarantee.** **Broadcom's first XPV deal raised $35bn, $30bn of it Broadcom-backstopped (NSR). That is a different perimeter from Run 6's ~$100bn programme figure, not a contradiction.** NVIDIA is obliged to buy CRWV's unsold capacity through April 2032 (UBS). The FT names NVIDIA and Oracle as dependent on OpenAI's financing | NVIDIA's 10-Q shows the drawn backstop balance flat; NVDA CDS retraces the +36bp QTD | A formal rating action on NVIDIA or any guarantor; a guarantee is called; the Anthropic–Stream Google guarantee is formalised at scale | **NVIDIA November 10-Q** |
| 29 | Beat-and-raise, hold/cut the target | **Confirmed — now in the models, with the escape valve still working** | **84% of semis guided above the Street, against 97% a quarter ago; "earnings up, multiples down" (UBS).** MU multiple cut from 11x to 8x; AMAT $642 → $563 and CAMT $165 → $152 while EPS rose (MS); Stifel upgraded MSFT while cutting FY28; Wells' META target +24%, all of it multiple; CRDO cut to $245 by Mizuho and $292 by ISI. UBS Parker: ~5% of earnings-driven performance is offset by 60–90bp of discount-rate increase. **The escape valve held: a quantified AI contract moved AKAM +19.7%, and an adoption shock moved META +11%** | October prints move PTs up on EPS without multiple cuts | Rates add another 50bp and PTs get cut systematically; a Micron beat is sold on 30 September | **October earnings season** |
| 30 | Seats vs tokens | **PARTIALLY FIRED — the first seat-price discounting at the largest vendor** | **MSFT Copilot discounts of 30–50% for large enterprises (The Information), with Cowork, Code and Autopilot billed on usage (ISI).** CRM Agentforce pricing at $50/$125/$550, with partners resisting a 10–15% uplift (ISI); ~8% deployment success at one partner (Jefferies). TEAM moves to usage pricing on 3 December; SNPS moves EDA from seats to consumption; OKTA per-agent pricing is coming, but "no standard way to count agents." ACN organic growth <1%; ~70% of INTU's revenue is growing ~1.4%. *No vendor has yet reported a seat-count decline attributable to agents* | ZS on 6 October holds a ~30% non-seat share of new ACV with ARR steady; MSFT's usage-billed products show acceleration | A vendor reports a seat-count decline attributable to agents; Copilot discounts spread into E5/E7 renewal pricing | **ZS analyst day, 6 October; MSFT late October; TEAM, 3 December** |
| 31 | State data-centre politics | **Bear trigger FIRED — and the behind-the-meter exemption is dented** | **Texas halted state data-centre permits pending the ERCOT interconnection and TWDB water audits (update due 19 October)**, with >470GW of large loads in the ERCOT queue; Abbott will ask the Legislature to remove DC incentives. **ISI concedes that "onsite generation… does not eliminate state environmental permitting"**, so BTM now carries a permitting asterisk (Jupiter's air permit is the template). Wells Fargo: cumulative moratoria 530, 374 active (vs 182/92 in June). Newsom EO: on-site verifiers and a frontier-model kill switch. Ipsos: 55% support slowing AI; ~70% oppose a nearby DC | *(fresh)* The 19 October update lifts the halt with conditions; the 10 December audit ends without capacity loss | *(fresh)* The halt extends past the December audit or the Legislature strips incentives; a second large state halts permits; BTM projects are denied air permits | **19 October; 3 November midterms; 10 December audit; April 2027 ERCOT Batch Zero** |
| **32** | **Compute-rent vs token-price scissor** *(NEW)* | **Added — distinct from #6 (rent level) and #11 (enterprise token economics); this row tracks the *spread* that decides who captures value** | **Ornn, June → September: average paid token prices OpenAI −62%, DeepSeek −51%, Google −29%, Anthropic −11%; over the same period GPU rents B200 +50%, H200 +28%, H100 +9% (Red-Ring).** ISI: token index ~$2 → ~$1/Mtok while short-dated compute trades at ~$40m/MW. The consequence is vertical integration: Anthropic's 1GW Stream lease, the AKAM CPU deal, OpenAI's SB Energy lease. The counter-signals are tiering, not cuts: DeepSeek *raised* prices 2.3–4.5x and ARR rose to ~$1bn; ChatGPT Pro Max at $500 is rumoured (d) | The scissor narrows because token prices stabilise (premium tiers stick) while rents hold, so lab margins survive and the demand chain stays financeable | The scissor widens for another quarter (token prices −30% or more while rents rise +20% or more), squeezing lab margins into #33 and the CY27 recontracting test (⑩) | **OpenAI DevDay (29 September); CME compute futures (5 October); Ornn monthly** |
| **33** | **Frontier-lab funding runway + hyperscaler lease guarantees** *(NEW)* | **Added — distinct from #18 (the neocloud seller side) and #28 (vendor-architected guarantees); this row tracks the ultimate buyer's own funding** | **Anthropic:** IPO targeted for November at ~$2tn, raising up to $100bn (WSJ/NYT); $95bn of equity raised in 2026 ($380bn → $965bn); a $35bn compute SPV; the 1GW Stream lease with a possible Google credit guarantee; ≥14.8GW / ~$517bn of multi-year compute commitments. **OpenAI (FT, plan not guidance):** −$278bn cumulative FCF 2026–30, $856bn of compute, the March $122bn raise "could be exhausted in 2028"; >$1.2tn raise talks. **SoftBank's OpenAI-funding bond expected at BB+.** Emanuel: the IPO pricing before 31 December is positive; a slip into a stressed 2027 could catalyse "hyperscaler issuance woes" | Anthropic prices before year-end at or above the $965bn Series H mark; OpenAI closes its raise; SoftBank's 1 October contribution settles cleanly | The IPO slips into 2027 or prices below the Series H mark; SoftBank funding stress; hyperscaler guarantees of lab leases spread, transferring lab credit onto hyperscaler balance sheets | **1 October SoftBank contribution; the November IPO window** |

**Row count:** 30 carried + 2 added (#32, #33) − 0 retired = **32 live indicators** (#1–#11, #13–#33). **Status tally:**
- **Fired, bear side (fresh triggers written):** 6 (#8, #21, #22, #25, #26, #31).
- **Fired, bull side (fresh triggers written):** 3 (#10, #20, #24).
- **Partially fired:** 1 (#30).
- **Contradicted:** 2 (#5, #17).
- **Resolved on mechanism:** 1 (#19).
- **Split:** 3 (#3, #7, #18).
- **Confirmed, advancing or live:** 14.
- **New:** 2.

---

## §7 — One strong recommendation

**Own contracted, self-funded scarcity; underweight whatever must be refinanced or re-priced — and hedge with options, not bonds.**

This is one stance and a refinement of Run 6, not a reversal. Each clause answers something the last three weeks taught.

**First, what Run 6 got wrong, stated plainly.**
- **The break condition did not fire. The opposite happened.** Run 6 would have dropped the discrimination if IG Tech spreads tightened through 100bp while the tenant-quality spread compressed. Instead the tenant spread blew out: CoreWeave went to 811bp against ~88bp for hyperscalers, a ~720bp gap against Run 6's ~250bp watch level. The discrimination paid.
- **The long-duration hedge lost money.** The 10-year went from ~4.8% to ~5.2% during the window, and the stock–bond correlation turned positive (+28–60%, UBS desk). Bond CTAs now sit at the 1st percentile and 100% short, so a bond rally from here works as a *second long* on AI equities, not as insurance. **That is why the hedge is now options.** Specifically: index or SOX downside (Emanuel's IWM puts and SPY straddles were bought at mid-teens VIX), or payer structures on the neocloud credit where they are available. Not duration.

**Why "contracted" is now the operative word, not just "self-funded."** Run 6 sorted by who funds themselves. That still matters, but this run showed a second axis cutting through the same names: **whether today's price is contracted or has to be re-struck.** The run's evidence splits every market along that line:
- **Memory:** CSPs agreed to pay higher 1Q27 DRAM prices while September spot turned negative.
- **Compute:** B200 rents are up 50% while paid token prices fell 11–62%.
- **Seat software:** priced per seat, and now discounted 30–50% at the largest vendor.
- **Neoclouds:** priced for scarcity, but must refinance at 10–13%, and their first 5-year contracts roll in CY27.

In each case value accrues to the side that has locked in the price, the volume or the funding, and is squeezed out of the side that has to go back to market.

**Own:**
- **NVDA and AVGO.** Both are net cash or low-leverage self-funders with contracted, supply-locked 2027–28 revenue, and they are Lipacis's low-P/E dispersion picks at ~19–20x NTM. **One qualification on NVDA:** its credit is now priced for its guarantor role (~$170bn of contingent exposure, CDS +36bp QTD). Watch NVDA CDS as the early warning for this leg.
- **TSMC.** N3 runs at >100% utilisation, prices rise 3–6% in January (grade c), and it trades at 17x/12x 2027/28 against the SOX at 29x/20x.
- **Contracted HBM and server memory through Samsung and SK hynix.** Samsung is gaining HBM share in 2027 (UBS, MS), and SK hynix has >50% of capacity under LTAs and >50% FCF returns.
- **The optical laser layer (LITE, COHR).** InP is sold out, prepaid to 2031, and repriced +50–60%.
- **Energised hyperscaler capacity.**

**Hold Micron as an exposure, sized to its contract share, not as a pure-play name.** It is a net-cash self-funder with roughly half its revenue under strategic agreements (RBC). The 9 December CHIPS lapse opens a buyback UBS models at ~$20bn a quarter rising to $40–50bn (share count −32% by F30). **But the stock trades on pricing leverage, and on UBS's own heuristic the q/q ASP momentum is peaking now.** Micron is the name where both clauses of this stance collide. Size it to the contracted half.

**Underweight:**
- **Neoclouds (CRWV, NBIS, IREN, Nscale).** Four equity houses are bullish on borrower equity this run (UBS initiating and JPM upgrading CRWV, ISI holding Outperform; BNP upgrading NBIS), and two initiated or kept Sell (Rothschild; Bernstein). **The credit market is on the Sell side's side at 811bp.** State the asymmetry honestly: this underweight runs against the majority of equity research, and it is justified only by the credit tape. **The flip test is specific: the CY27 recontracting price and the direction of CRWV CDS.**
- **Lab-dependent, vendor-financed structures, with Oracle the clearest case.** Oracle served force majeure on Jupiter; FCF is −$16.8bn excluding prepayments; the FT names it as dependent on OpenAI's financing; its CDS is 189bp, the widest in IG.
- **The un-contracted memory tier:** spot and channel DRAM, consumer NAND, and the Nanya-overlap DRAM that CXMT's G5 targets. *This is an exposure, not a ticker list.*
- **Seat-priced application software facing agent-era discounting.** This does not include the non-bypassable billing nodes (identity, observability, payment rails, EDA consumption), which belong on the long side.

**What this recommendation is not.**
- **It is not a call to cut gross AI exposure.** The fundamentals strengthened again: backlog exceeds sales, 84% of semis guided above the Street, and the contracted tier tightened. Cutting exposure would be trading the September tape rather than the evidence.
- **It is not a call on the direction of rates.** The options hedge exists precisely because the rate path is now a two-sided tail (②′).

**The single thing that would break it.** Drop the underweight and go long the borrower tier outright only if **all three** of the following happen:
1. CRWV CDS falls back below ~550bp, its pre-QTD level.
2. The Anthropic IPO prices before year-end.
3. CY27 recontracting clears at a premium to installed rates.

Together those would mean the capital markets have decided to underwrite the borrower tier's cost of capital, and that credit is no longer the binding constraint. Any one alone is noise.

---

## §8 — Source inventory

**42 reports, 7 – 27 September 2026.** All seven standing sources reported. The Humanoid adjunct is **retired as a source** this run after five consecutive silent runs (last output 12 July 2026); indicator #23 continues from UBS, MS and IFR.

| Source | n | Files | Notes |
|---|---|---|---|
| UBS | 7 | `UBS_Research_Report_2026{0910, 0913, 0916, 0917, 0920, 0922, 0924}` | Batches span older underlying notes (4–24 Sep); desk notes graded (d). Intra-house splits carried: Arcuri vs Gaudois on 2029 memory (⑭); Lin vs Arcuri on MRVL Trainium; HOLT vs Top Picks on PLTR |
| NSR | 2 | `NSR_Research_Report_2026{0912, 0924}` | The 4-part "Financing the AI Buildout" series and a 46pp Gen AI deep dive (financing restated up to $3.7tn). Internal inconsistency: open-weight token share 80% (Pacing note) vs 65% (Gen AI deck) |
| ISI / Evercore | 6 | `ISI_Research_Report_2026{0910, 0916, 0920, 0924, 0925, 0926}` | 87 PDFs in total; the richest set again. The Lipacis late-innings webinar and the September memory price series are the run's key new data |
| MS / Morgan Stanley | 1 | `MS_Research_Report_20260927` | 21 reports, 28 Aug – 27 Sep; NVDA "Balance Sheet-as-a-Service" credit note; memory-as-value-capture across five teams |
| JPM | 2 | `JPM_Research_Report_2026{0917, 0924}` | 0924 carries only one new PDF (the CRWV upgrade); the rest are historical or duplicate |
| Red-Ring | 13 | `Red_Ring_Market_Synthesis_2026{0906, 0907, 0909, 0912, 0915, 0916, 0917, 0920, 0921, 0922, 0923, 0924, 0926}` | 【直接事实】/【渠道信息】/【分析推论】 tagging honoured. **0906 is not a hole:** it was published after the Run 6 addendum cut-off |
| TMTB | 11 | `TMTB晨间综述_深度解析_20260908`, `TMTB晨间综述_20260909_主题集群分析`, `TMTB_20260910_晨报分析`, `TMTB_晨报_20260911_主题聚类分析`, `综合研究报告_20260911`, `TMTB_Morning_Wrap_20260914_analysis`, `综合研究报告_20260918`, `综合研究报告_20260921`, `TMTB_Morning_Wrap_20260922_深度分析`, `TMTB_Morning_Wrap_20260924_深度分析`, `TMTB_Morning_Wrap_20260925_深度分析` | **11 unique files after hash-dedupe of 14 candidates** (three were byte-identical copies under `Claude outputs/`). GS-sourced numbers graded (b) |

### Evidence grades

- **(a) — official disclosure.**
  - Company filings and releases: the Akamai–Anthropic 8-K, IR deck and contract terms; the CoreWeave 8-K of 17 September; Oracle's FQ1'27 print and 10-Q; NVIDIA's Hugging Face acquisition blog (3 Sep, which moves the item off Red-Ring's unverified list); TSMC's August revenue.
  - Policy and legislation: the FOMC statement and SEP of 16 September; the Senate transceiver bill text; the Texas TCEQ directive.
- **(b) — named research and contract data.**
  - Every named analyst estimate and target across the seven houses.
  - Market data: CRWV CDS and the UBS Debt Monitor spreads; the Jupiter <90c sale (WSJ/FT/Reuters, multi-outlet).
  - Price indices: the Ornn token and GPU indices; Silicon Data residuals; TrendForce contract guides; BofA's memory weekly.
  - Graded **(b/c):** ISI's September memory price series (a named series whose provenance is not fully specified) and FT's reporting of the OpenAI plan (a plan, not guidance).
- **(c) — expert and channel checks, corroborated.**
  - Buyer-side peak calls: Raspberry Pi and Acer.
  - Rubin/Kyber: the Rubin compute-tray and rack-yield Q&A and the Red-Ring rack expert on Kyber. **Kyber's slip itself is (b) via UBS and ISI; the expert detail is (c).**
  - Optical: InP delivered prices; the COHR ECOC notes as partial NPO corroboration.
  - Other: the Edgewater Anthropic DRAM demand; the TSMC January price increase (DigiTimes); Samsung's 4nm HBM base-die pricing.
  - Graded **(c/d):** Daishin's HBM over-reporting admission.
- **(d) — desk colour, screenshots and single unverified claims. None drives a conclusion here.**
  - Desk and positioning colour: all UBS Neo/desk positioning figures (CTA percentiles, HF leverage, QQQ put/call, retail dip-buying); Polymarket odds; Rich Ross's technical targets.
  - Revenue and pricing claims: Nebius price-list screenshots (**cite direction only**; two different bases circulate); Yipit Anthropic/OpenAI ARR; the rumoured $500 ChatGPT Pro Max.
  - Unverified narratives: Kass's AI-generated readout (the "Chernobyl moment" containment claim); OpenAI's "solved Navier–Stokes" claim; the Jon Ma Anthropic net-ARR screenshot (contains a definitional error).

### Figures quoted at multiple perimeters — reconciliation

- **Anthropic ARR — four vintages; never average them.** $65bn (end-July, FT) / ~$70bn (Yipit, d, mid-September) / >$100bn (September, second-hand table) / >$110bn (a YE *expectation*, WSJ/NYT). Yipit's +$5bn a month cannot reach $110bn by YE (that needs ~$11.8bn a month), so either the run-rate definitions differ or the expectation is aggressive. Q2 revenue $11.5bn remains grade (c).
- **2027 WFE — $198–226bn depending on definition.** UBS alone spans $198bn (Lin, APAC) to $226bn (Arcuri, US); ISI $215bn; JPM $205bn. Different perimeters, not disagreement.
- **Broadcom's financing — two perimeters, one programme.** Run 6's ~$100bn ($60bn senior + $30bn sub) was the XPV programme scale. NSR's **$35bn raised in the first >1GW Anthropic deal, $30bn Broadcom-backstopped**, is the first draw. The XPV targets >20GW through 2028 (~$650bn implied).
- **Diesel.** EIA **$5.97** (+58% y/y) is the benchmark; ISI and TMTB also quote $6.30 and $6.50 from other series and dates.
- **Memory contract: monthly vs quarterly.** ISI's September DDR contract +2–3% is *month-over-month*. The 4Q guides (+5–10%) are *quarter-over-quarter*. They do not contradict each other; they describe a deceleration.
- **NVIDIA CDS.** Run 6 carried 86.7bp (24 Aug, ATW). MS reports 5Y at ~80bp, +36bp QTD, at a different date and tenor convention. Read as flat-to-wider, not tighter.
- **Revenue per MW — tenor-dependent.** CRWV installed ~$10.5–12.5bn/GW; long-term take-or-pay ~$13bn/GW (NSR); AKAM ~$20–22m/MW/yr; short-dated ~$37–43bn/GW (UBS); SPCX/lab deals $30–50m/MW. Never quote one without its tenor.

### Known gaps and flags

1. **`00_Resources/voice-principles.md` still does not exist anywhere on disk.** This is the fifth consecutive flag. This run again used the Cowork Playground CLAUDE.md Preferences section as the voice specification. It should be written or the reference removed.
2. **The Micron buyback contradiction is closed.** Parker's ~$460bn figure (≈40% of S&P LTM buybacks) was forward-looking. Arcuri's FQ4 preview supplies the schedule: CHIPS limits lapse on **9 December 2026**; buybacks run ~$20bn a quarter from FQ2:27, rising to $40–50bn a quarter; $100.5bn in F27 and $192.5bn in F28; share count −32% by F30. The two claims were never in conflict. They described different dates. Retired from this list.
3. **The Humanoid source is retired** (see #23). The indicator remains.
4. **Red-Ring files carry long source and company directories after §9–10.** The substantive §1–9 were read in full; the directory tails were skimmed. This is a method disclosure and does not affect any conclusion.
5. **TMTB's rate-reading quirk.** TMTB printed "market pricing ~70% September rate CUT" on 11 September, while hike pricing elsewhere was 85–92%. It was the mis-specified side of the Run 6 fracture. TMTB rate-probability statements should be cross-checked against GS or ISI before use.
6. **No new data on two named Run 6 triggers:** IG Tech OAS against the March peak, and AVGO CDS against 126.2bp. Proxies are used in #14 and #21. A future batch should be asked for both directly.
7. **Red-Ring's channel-inventory month series (Run 6's decisive #19 bear trigger) was not updated.** ISI's OEM inventory (+70% vs trend) and Wolfe's customer inventory days are dollar-denominated and contaminated by price. A bit-denominated series is needed to resolve #19's timing.
8. **Intra-house splits carried unresolved:** UBS Arcuri vs Gaudois (2029 memory); UBS Lin vs Arcuri (MRVL Trainium); NSR's internal open-weight share (80% vs 65%); MS's memory "half of capex" vs its 2028 bridge that requires memory to moderate.
9. **MS vs UBS on AMD 2027 CoWoS:** MS 345k wafers (cut from 530k) vs UBS 475k (3.7x). Unresolved; relevant to #15 and to AMD's 2027 GPU volume.

---
