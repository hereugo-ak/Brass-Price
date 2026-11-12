# Brass Price Foresight — project brief

**Client:** Castle Hardwares, Aligarh (est. 1965) — brass, aluminium and iron builder hardware; exports to 40+ countries; also a UAE scaffolding/fencing line.
**Author:** DTPS live project (MBA, Design Thinking & Problem Solving)
**Status date:** 2026-11-12 · **Submission:** 2026-11-15

---

## 1. Problem statement

Castle buys brass almost every week and quotes export customers at a price that stays fixed for weeks. Brass is the dominant raw-material cost. When metal moves between the day a quote is promised and the day the metal is actually bought, the difference comes straight out of margin — and the owner has no forward view to plan against.

The owner's own words: *"you cannot expect one sudden morning that price is going to go high today… we need at least a projection for a month to plan for delivery."*

Formally:

> **Castle cannot time spot metal purchases, or set a safe export quote floor, because it has no weekly forward view of the price it will actually pay for brass scrap — and the market segment it buys from publishes no such view.**

Three constraints make this harder than an ordinary price forecast:

1. **There is no brass futures contract.** Verified against LME, MCX and COMEX product lists. LME lists copper, not brass. MCX launched a brass contract in 2018 but it is absent from the live 2026 product list, and the 2019 contract that does exist traded with **zero volume and zero open interest**. COMEX has copper. Brass cannot simply be forecast as a traded price.
2. **Castle's brass is scrap.** Roughly 70% of raw material is bartan and gittu scrap bought from local traders and melted in-house. The relevant price is a dealer price in rupees, not an exchange settlement.
3. **The price is a bilateral quote, not a market tick.** It moves slowly, depends on the trader, and includes transport.

Consequence for the method: brass price must be **reconstructed**, not looked up.

```
price ₹/kg = wCu·Cu·FX  +  wZn·Zn·FX  +  premium − scrap discount
             + conversion + margin + transport + net duties
```

Output must be a **low / middle / high band for the coming weeks**, plus a quote floor — never a single-point prediction.

---

## 2. What has been collected

### 2.1 Driver research — complete and closed

| Asset | Count | State |
|---|---:|---|
| Driver tree (`output/tree.json`) | **72 nodes** | 26 Verified / 31 Disputed / 15 visible watchlist |
| Cross-link edges (`output/edges.json`) | **9 edges** | 4 Verified / 5 Disputed |
| Claim ledger (`output/claim_ledger.csv`) | **65 rows** | every claim with URL, date, tier, status |
| Dataset catalogue (`output/data_catalogue.csv`) | **44 rows** | variable, unit, frequency, access, lag, quality |
| Quarantined claims (`output/quarantine.csv`) | **19 rows** | visible, never deleted |
| Verification logs | 2 rounds | round 1 + round 2, independent agents |

Method: MECE tree with a stated splitting criterion per level, two independent verification rounds, quarantined numerics, and an independent collective-exhaustiveness check against the price identity above.

### 2.2 Public price data — live and current

| Series | Source | Coverage |
|---|---|---|
| USD/INR (DEXINUS) | FRED H.10 | 13,497 days, 1973 → 2026-11-06 |
| USD/EUR | FRED H.10 | 6,984 days, 1999 → |
| IMF copper, USD/t | FRED / IMF | 417 months, 1992 → 2026-09 |
| IMF zinc, USD/t | FRED / IMF | 417 months, 1992 → 2026-09 |
| Brent crude | FRED / EIA | 9,122 days |
| US housing starts, construction spend | FRED / Census | 813 and 405 months |
| ECB euro reference | ECB | daily snapshots |
| CFTC COMEX copper COT | CFTC Socrata | weekly |
| **MCX copper + zinc futures closes** | MCX bhavcopy (manual) | **955 daily rows, 2025-01-01 → 2026-11-11** |

Built into **`data/features_weekly.csv` — 2,789 weekly rows, 1973-01-05 → 2026-11-06, 31 columns**, with publication lags mapped in `data/LEAK_MAP.md`.

The MCX series matters most: the owner named MCX as the Indian anchor, and it is now captured daily in rupees per kilo.

### 2.3 The domestic price tiers — two markets, not one conflict

Indian brass scrap quotes split into two clearly separated tiers. This resolved a contradiction that had blocked the project all day.

Metal content, computed as `0.615·Cu + 0.385·Zn` at IMF prices and FRED FX: **₹998/kg (2026-09)**.

| Tier | ₹/kg | % of metal content | Who trades there |
|---|---:|---:|---|
| **Household / kabadi pickup** | 402 – 519 | **40 – 52%** | a household selling a broken utensil |
| **Foundry board / wholesale** | **810 – 1000** | **82 – 100%** | a factory buying tonnes from a trader |

Castle buys from local traders, so **its tier is the board: ₹810–1000/kg**. The low tier is a real market, simply not Castle's. Sources in the board tier: MTLEXS, AajBazar, Steel-Baba, ShreeMetalPrices, PTI via News18, SMM, National Recycling, Adinath — **eleven independent sources agreeing within 0.82–1.00 of metal content.**

**27 dated board observations** are extracted to `data/manual/brass_board_prices.csv`. They are a **level**, not a series.

### 2.4 The brass/metal ratio — the spread layer, measured

```
brass ₹/kg  ≈  ratio × metal_leg ₹/kg
```

| Period | Source family | n | Ratio |
|---|---|---:|---:|
| 2019-08 → 2019-12 | MCX BRASSPHY futures, 107 closes | 5 months | **0.977** |
| 2023-01 | MTLEXS Mumbai (honey, sheet) | 6 | **0.910** |
| 2026-11 | Eleven Indian boards | 27 | **0.897** |

Three independent source families, seven years apart, agreeing within **8 percentage points**. This is the first time the spread layer has been **measured** rather than assumed.

By grade in 2026: honey **0.888** (sd 0.017), bartan/utensil **0.872**, purja/mixed **0.866** (sd 0.050), sheet/chadri **0.963** (sd 0.046). Yellow brass (0.701) and gun metal (1.049) are different alloys and are **excluded, not averaged in**.

**Castle's grades — bartan, honey, purja — pool to ratio 0.876, sd 0.039, n = 16.**

### 2.5 The band, in the units the business uses

Metal leg, 4-week horizon (from `data/brass_model.py`): **₹994.63/kg**, 80% band −₹33.84 / +₹60.71.

| Line | Calculation | Result |
|---|---|---:|
| Low | ₹960.79 × 0.837 | **₹804/kg** |
| Middle | ₹994.63 × 0.876 | **₹871/kg** |
| High | ₹1,055.34 × 0.915 | **₹966/kg** |
| **Quote floor (+5%)** | ₹966 × 1.05 | **₹1,014/kg** |

**Independent cross-check:** Steel-Baba's *Utensil (Bartan/Pital)* board price on 2026-09-14 was **₹870/kg**. The band's middle is ₹871. That agreement was not fitted — it fell out of two separate routes.

On 5,500 kg/month the band spans roughly **₹9 lakh** between low and high. That is why the floor matters more than the middle number.

### 2.6 The price is calculated, not looked up

The owner described the mechanism himself: *"LME governs most of it but in India we have MCX which is metal trading which also governs the price, plus the transportation is always extra."*

That is an instruction to **calculate**, and the calculation now runs two independent ways:

```
price = ratio × metal_value + transport
```

| Route | Construction | Metal value |
|---|---|---:|
| **A — LME × FX** | 0.615 × Cu $14,473/t × ₹94.53 + 0.385 × Zn $4,021/t × ₹94.53 | **₹987.77/kg** |
| **B — MCX domestic** | 0.615 × ₹1,341.85 + 0.385 × ₹411.45 (INR/kg already) | **₹983.65/kg** |
| | **difference** | **−₹4.12/kg (−0.42%)** |

Route B embeds FX, import duty and the domestic premium, so the agreement between A and B is a genuine cross-check rather than a tautology. Two different data sources, two different constructions, same answer to within 0.42%.

**Current calculated price (12 Nov 2026, transport taken as ₹20/kg):**

| Line | Metal | × ratio | Brass | + transport |
|---|---:|---:|---:|---:|
| Low (mean − 1sd) | 983.65 | 0.837 | 823.31 | **₹843/kg** |
| Central | 983.65 | 0.876 | 861.67 | **₹882/kg** |
| High (mean + 1sd) | 983.65 | 0.915 | 900.04 | **₹920/kg** |
| Quote floor (+5%) | | | | **₹966/kg** |

**No invoice was used to produce these numbers.** They follow from public metal prices, the domestic exchange, a measured ratio and a transport parameter.

**What an invoice would and would not do.** It is **not** a prerequisite for the calculation — that claim was made earlier and is withdrawn. It would narrow the ratio from the *market board* value (sd 0.039 → ±₹38/kg) toward Castle's *own* value. The honey grade alone already carries sd 0.017 (±₹17/kg), so the remaining uncertainty is bounded and modest. An invoice improves precision; it does not unlock anything.

### 2.7 Owner intelligence — 6 of 8 questions answered

Recorded verbatim in `data/owner_answers.md`, dated 2026-11-12:

| Question | Answer |
|---|---|
| Q1 suppliers | brass from local traders/vendors; aluminium scrap local; Al sheet/extrusion from Hindalco, Alum and MM Metacraft; iron sheet from Tata/Jindal vendors; SS from Mumbai |
| Q2 items | scrap, ingots, rods, extrusions, tubes, sheet — many sizes. **Brass bartan scrap and gittu scrap.** No brass ingot/rod grade named |
| Q3 rhythm | *"almost every week as per our requirement… we don't buy in bulk now because of the uncertainty in price and availability"* |
| Q4 reaction | cannot act on a same-morning warning; **needs at least a month's projection** |
| Q5 markets | **Europe and the Middle East** carry most orders. Quote-validity days **not given** |
| Q6 price mechanism | *"LME governs most of it but in India we have MCX which is metal trading which also governs the price, plus the transportation is always extra"*. Numbers **not given** |
| Q7 scrap | melted into cast then finished; **~70% of raw-material share** |
| Q8 volumes | brass **~5–6 t/month**; aluminium ~10 t; iron ~10 t |

**Q6 is now half-answered from a company source:** Hindustan Copper sets its domestic base price as **(LME + premium)**, with **USD 100/t premium on cathode** and **USD 180/t on 8 mm CC rod**. That is the domestic metal-pricing mechanism the owner described in words. Status: Disputed — one company source, needs a second pull.

What the answers changed in the design: the target became the **domestic brass scrap price in ₹/kg, delivered, GST inclusive**; the horizon became **four weeks**; the quote shield is built for **Europe and the Gulf**; **transport** entered the price identity and sits inside the target, not added later.

### 2.8 Models built and results

| Model | Target | Result |
|---|---|---|
| Naive / seasonal-52 (`baseline.py`) | USD/INR weekly | naive 1w MAE **0.2128**, 4w **0.4625** |
| Ridge tournament + Diebold–Mariano (`train.py`) | USD/INR weekly | best Ridge 1w **0.2930**, 4w **0.5131** — **naive wins** |
| Metal-leg model (`brass_model.py`) | Cu+Zn×FX, ₹/kg, 4-week | naive MAE **₹27.31/kg**; **all challengers lose at every alloy weight** |
| `drift12` on the WPI brass index | domestic brass index, 1–4 months | **beats naive in all 12 configurations by 2.7–7.5%** — but DM +0.56…+1.22, not significant, and the edge exists only post-2020 |
| **Ratio model (`brass_target_from_board.py`)** | brass ₹/kg = ratio × metal leg | **ratio 0.876 ± 0.039**, band ₹804 / ₹871 / ₹966 |
| **Procurement backtest (`backtest_procurement.py`)** | synthetic brass, 1,593 weeks | **buy-timing signal FAILS**: −₹0.11/kg vs buying every week. Quote floor is what survives. |
| **Price calculator (`brass_price_calculator.py`)** | brass ₹/kg from MCX + LME + transport | **₹823 / ₹862 / ₹900 + transport**, quote floor ₹966. LME route and MCX route agree to **0.42%**. |

**Findings that matter:**

- **Naive is very hard to beat** on FX and on the metal leg. That is the honest bar, not a failure.
- **The 4-week band is asymmetric:** −₹33.84 / **+₹60.71**. Upside risk is ~1.8× downside. A symmetric band would systematically *under-cushion* the quote floor — the exact failure the project exists to prevent.
- **First genuine challenge to naive:** `drift12` on the real domestic brass index. Suggestive, not established.
- **The metal leg construction is validated:** MCX BRASSPHY 2019 settled at **0.977×** our computed metal content. An actual Indian exchange settlement is reproduced to within 2.3%.
- **Domestic copper validates too:** MTLEXS Mumbai cathode ₹1,410/kg vs our IMF-derived ₹1,359/kg — a 3.8% gap consistent with an import premium.
- **The buy/wait signal was rejected by its own acceptance test.** Deferring when the forecast says "cheaper next week" loses **₹0.11/kg (−0.045%)** against buying every week, on 1,592 decision weeks and 30.5% deferrals. Per the project rule, it does not ship. The honest finding is that the value is on the **sell** side.
- **The asymmetry is confirmed in time, not only in spread:** brass was higher than today in **52.6% of 1-week periods, 57.5% of 4-week periods and 59.6% of 8-week periods**. The expected cost of delay is small (+0.24% over four weeks) — the owner's weekly rhythm is rational — but the tail is one-sided, which is exactly what the quote floor covers.
- **Quoting at the band's middle carries an expected metal cost of ₹5.37/kg = ~₹29,500 per 5,500 kg order**, worst case ₹77.7/kg. Quoting at the band high removes that risk but prices ~11% above the middle. That trade-off is the decision the floor rule encodes.

### 2.9 Tools and deliverables built

| File | Purpose | State |
|---|---|---|
| `Brass_Story.html` | owner-facing editorial story, 8 questions, 8 folios, answers band | final, render-verified |
| `brass_graph.html` | interactive 72-node driver graph | final |
| `DTPS_Dossier.html` | syllabus-mapped proof for the course assessor | final, answers recorded |
| `Castle_Discovery_Questions.html` | printable 8 questions | final |
| `PRD.md` / `PRD.docx` | full technical specification | final |
| `Executive_Summary.docx` | non-technical summary | final |
| `Brass_Weekly_Input.html` | weekly price capture tool, weekday dropdown, CSV export | built, 11/11 headless tests pass |
| `output/MODEL_SPEC.md` | every target decision, with reasons | current |
| `output/BRASS_RATIO_FINDING.md` | the ratio discovery, tiers and validation | current |
| `output/WPI_BRASS_FINDING.md` | the WPI index discovery and its four tests | current |
| `output/BAND_REPORT.md` | metal-leg results, band, quote-floor grid | current |
| `output/PROCUREMENT_BACKTEST.md` | acceptance test: cost of delay, signal rejection, quote exposure | current |
| `data/brass_price_calculator.py` | the working calculation, two routes, transport as a parameter | current |

---

## 3. What we are going to do

### 3.1 Method — the four-layer chain

```
Layer 0  identity       ₹/kg = metal leg + spreads + transport + duties
Layer 1  metal leg      Cu, Zn, USD/INR — public, 53 years, forecastable
Layer 2  ratio          brass ≈ 0.876 × metal leg — now measured at 3 points in time
Layer 3  output         low / middle / high band for 4 weeks + quote floor
```

Layers 1 and 2 are **done and tested**. What remains is confirmation on Castle's own purchases and a series to track the ratio's drift.

### 3.2 Sequence

| # | Step | Status |
|---:|---|---|
| 1 | Research the 72-driver map, two verification rounds | done |
| 2 | Build the public data spine and weekly feature table | done |
| 3 | Establish the naive bar on FX | done — naive wins |
| 4 | Build the metal-leg model and 4-week band | done — naive wins, band asymmetric |
| 5 | Find an official domestic brass series | done — WPI 1314090011, 169 months |
| 6 | Verify collected brass rate data against source and physics | done — **two price tiers identified** |
| 7 | Measure the brass/metal ratio from board and exchange data | **done — 0.876 ± 0.039** |
| 8 | Produce the band in ₹/kg with a quote floor | **done — ₹804 / ₹871 / ₹966, floor ₹1,014** |
| 9 | Confirm the ratio on Castle's own invoice | **open — one number needed** |
| 10 | **Rupee-saved backtest** | **done — buy signal fails and is withdrawn; floor survives** |
| 11 | Weekly price note → ratio drift series, live floor | **open — needs a series** |

### 3.3 Automated collection

`data/backfill_fred.py` → `collect_daily.py` → `make_features.py` → `baseline.py` runs end to end. Latest run: **8 feeds collected, 2 missed** — ECB (network) and MCX (**HTTP 403** to all automated requests; manual browser only). Misses are recorded, never hidden.

MCX data therefore arrives by manual bhavcopy. It is now captured: 955 daily copper/zinc closes, 2025-01 → 2026-11.

---

## 4. What is still missing — and why it cannot be invented

| # | Missing | Why it matters | What resolves it |
|---:|---|---|---|
| 1 | **One Castle invoice — ₹/kg, month, grade** *(optional, not a blocker)* | narrows the ratio from the market board value (±₹38/kg) to Castle's own value, and confirms the transport charge | one figure from the owner — the calculation already runs without it |
| 2 | Weekly brass price series | turns the ratio into a tracked series and enables the rupee-saved backtest | one figure a week: 8 rows to start, 30 to be usable, 100+ to fit |
| 3 | Quote-validity days per market | sets the quote-floor horizon precisely | owner; 30 days assumed, stress-tested at 15 and 7 |
| 4 | Bartan/gittu alloy composition | the 0.872 bartan ratio rests on one observation; composition sets the metal leg | owner, or a CoA/IS 319 grade confirmation |
| 5 | LME cash/3M daily history | best metal granularity | paid dataset (~$85) or manual daily entry |

**What is no longer missing:** the spread layer. It was the project's main dependency this morning and is now a measured ratio with a standard deviation.

**Why the remainder is not estimated:** the ratio is measured, but a ratio is not an invoice. Applying an industry ratio to Castle's buying is an assumption; confirming it with one invoice removes the assumption.

---

## 5. Honest limitations

1. **No model has beaten naive on a Castle-specific target, and the buy-timing signal has now been tested and rejected** (−₹0.11/kg against buying every week). Naive wins on FX and on the metal leg. `drift12` beats naive on the domestic brass index but is not statistically significant and depends on the post-2020 regime.
2. **The project's edge is structural, not predictive** — the identity, the measured ratio, the asymmetric band, and the quote-floor rule.
3. **The ratio drifts down**: 0.977 (2019) → 0.910 (2023) → 0.876 (2026), about −1.5% a year. A constant ratio will be wrong in either direction; the band must carry the drift.
4. **MCX BRASSPHY 2019 had zero volume and zero open interest** — settlement prices of an illiquid contract. Usable as a ratio anchor, never as a traded price or as proof brass is hedgeable.
5. **The WPI brass index cannot be used as a level.** Anchored at 2019 it implies ₹601/kg at index 216.3, while the board actually quotes ₹897 — it **understates the market by 1.49×**. Direction only; the 2022-23 base must never be spliced to the 2011-12 base.
6. **The board data is a level, not a series** — 27 dated observations concentrated in November 2026, plus two historical windows.
7. **Owner answers are memory-based, not documents.** Recorded verbatim and dated; every derived assumption is labelled.

---

## 6. Position at submission (2026-11-15)

**Delivered:** a verified 72-node driver map; a live public data spine with 53 years of history plus 955 daily MCX closes; an honest naive bar; a metal-leg model with an asymmetric 4-week band; **a measured brass/metal ratio validated across three source families and seven years**; **a ₹/kg band of ₹804 / ₹871 / ₹966 with a ₹1,014 quote floor, cross-checked against a real board price of ₹870**; a two-tier market structure that explains the price contradiction; a browser capture tool; and owner-facing documents re-scoped to the owner's actual answers.

**Also delivered — a negative result, honestly reported:** the rupee-saved backtest now exists, and it **rejects the buy-timing signal** (−₹0.11/kg). The quote floor is what survives it. This is the acceptance rule doing its job.

**Not delivered, and not claimed:** a model that beats naive on Castle's real price, a profitable timing signal, or a calibrated continuous ₹/kg history.

**The calculation runs today.** Two independent metal routes agree to 0.42%, the ratio is measured, and the output is a ₹/kg band with a quote floor. What remains is refinement — a weekly series to track the ratio's drift, and one invoice to confirm it is Castle's number and not just the market's.

---

*Compiled 2026-11-12 from the committed files. Counts reproducible: `tree.json` 72 nodes, `edges.json` 9, `claim_ledger.csv` 65, `data_catalogue.csv` 44, `quarantine.csv` 19, `features_weekly.csv` 2,789 × 31, `wpi_brass_monthly.csv` 169, `brass_board_prices.csv` 27, `mcx_copper_zinc_daily.csv` 955, `mcx_brass_2019.csv` 107, `comtrade_brass_unit_values.csv` 50, `wpi_brass_newbase.csv` 42.*
