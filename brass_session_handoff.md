# Brass Guard — session handoff

**Project:** Castle Hardwares brass price floor · **Also:** DTPS live project (MBA-506, AMU)
**Last updated:** 2026-11-13 · **Supersedes:** every earlier handoff, including `archive/brass_session_handoff_2026-10-01.md`
**Model version in production:** `2026-11-12.1`

> **How to use this document.** Read it top to bottom once. Then treat the machine files as
> authoritative where they disagree with this prose: `output/tree.json`, `output/edges.json`,
> `output/claim_ledger.csv`, `output/data_catalogue.csv`, `output/quarantine.csv`,
> `data/drivers_results.json`, `data/procurement_backtest.json`, `data/brass_ratio_anchors.json`,
> `app/engine.py`. If this document and a machine file disagree, **the file wins and this document
> is wrong and must be corrected.**

---

## 0. TL;DR — the honest state

| Area | State |
|---|---|
| Problem definition | ✅ fixed, in the owner's own words |
| Owner intelligence | ✅ 8/8 answered, recorded verbatim, with a Q6 and Q5 follow-up |
| Driver research | ✅ 72 nodes (26 Verified / 31 Disputed / 15 Unverified), 9 edges, 65 claims, 44 catalogue rows, 19 quarantined |
| Public data spine | ✅ 2,789 weekly feature rows, 1973 → 2026, 31 columns |
| MCX domestic data | ✅ 955 daily copper/zinc closes, 2025-01 → 2026-11 |
| Brass/metal ratio | ✅ **measured**: 0.876 ± 0.039, anchored at 2019 / 2023 / 2026 |
| Predictive models | ⛔ **8 trained, all lost to naive**, DM −5.6 to −10.2 — closed |
| Buy/wait signal | ⛔ **built, tested, rejected** (−₹0.11/kg) — withdrawn |
| Band width | ⚠️ one constant (25.8) proven wrong in both directions; regime buckets validated, **not yet implemented** |
| Backend | ✅ 12 modules, 14 endpoints, 8 tables, 47 tests passing |
| Frontend | ✅ **two UIs**: React 19 + Vite + TypeScript in `frontend/` (the product, 4 screens, instrument-panel design, builds clean, calls the API for every number) **and** `Castle_Quote_Checker.html` (one file, no build, offline fallback) |
| Deployed | ⛔ localhost only, no auth, nothing hosted |
| GitHub | ⛔ **20 commits local, never pushed** |
| The one missing number | ⛔ **one Castle invoice** (₹/kg, month, grade) |

**One sentence:** the price *level* is validated two independent ways, the *forecast* was tested and
rejected, the *spread layer* was measured, and a working product exists — but one owner-supplied
number still separates "the market's brass price" from "what Castle actually pays".

---

## 1. Client and problem

**Castle Hardwares, Aligarh.** Founded 1965. Brass, aluminium and iron builder hardware. Export
markets are **Europe and the Middle East**. Also a UAE scaffolding/fencing line.

### 1.1 Problem statement (canonical, do not reword casually)

> **Castle cannot set a defensible floor for a fixed-price export quote, because it has no view of
> the brass price it will actually pay over the delivery period — and the segment it buys from
> publishes no forward price.**

The owner's own words, which are the source for every design decision:

> *"We almost buy every week as per our requirement… we don't buy in bulk now because of the
> uncertainty in price and availability."*

> *"Even if you tell me in morning price may climb we will have to contact our vendor to exactly
> know what price are they giving… we need at least a projection for a month to plan for delivery."*

> *"LME governs most of it but in India we have MCX which is metal trading which also governs the
> price, plus the transportation is always extra."*

> *"Quote is valid till no price change in market — usually that day only valid till that day."*

### 1.2 Promised outputs vs delivered

| Promised | Delivered | Status |
|---|---|---|
| Weekly band (low / middle / high) | same-day / 15-day / 30-day bands | ✅ |
| Quote floor | ₹950.40 same-day, ₹964.61 15-day, ₹972.54 30-day | ✅ |
| **Buying signal** | built, backtested, **lost ₹0.11/kg vs buying every week** | ⛔ **withdrawn on evidence** |
| "The price it will actually pay" | market tier × measured ratio | ⚠️ estimate, not an invoice |

**The single biggest deviation from the original brief is the buy signal.** It was not dropped
because it was hard; it was dropped because it lost money in a 1,592-week test. That substitution is
defensible and must be *stated*, not hidden.

### 1.3 Non-goals (binding)

Price forecasting · buy/wait signal · hedging execution · marketplace · real-time prices ·
multi-tenant SaaS (until one client works) · anything requiring a paywall bypass.

---

## 2. The core insight everything rests on

**There is no brass futures contract.** Verified against LME, MCX and COMEX product lists. LME lists
copper, not brass. MCX launched a brass contract in 2018 but it is absent from the live 2026 product
list, and the 2019 contract that exists traded with **zero volume and zero open interest** — it is a
settlement price of an illiquid contract, not a market.

Therefore brass price is **reconstructed, never looked up**:

```
price ₹/kg = wCu·Cu·FX + wZn·Zn·FX + premium − scrap discount
             + conversion + margin + transport + net duties
```

**IMPORTANT — the identity was later collapsed in code.** See §7.4. The code computes
`metal × ratio + transport`, where the ratio absorbs premium, scrap discount, conversion and duties.
This is a deliberate engineering choice and it **must be described accurately** in any document:
the six-term identity above is the theory; the one-ratio form is what runs.

---

## 3. Owner intelligence — complete record

Recorded verbatim in `data/owner_answers.md`. Consolidated analysis in `output/OWNER_INPUT.md`
(+ `.docx`). **All 8 questions answered, plus two follow-ups.**

| # | Question | Answer (abridged) | What it changed |
|---|---|---|---|
| Q1 | Suppliers | brass from **local traders/vendors**; Al scrap local; Al sheet/extrusion from Hindalco, Alum, MM Metacraft; iron from Tata/Jindal vendors; SS from Mumbai | fixed the price tier (trader, not mill; not exchange) |
| Q2 | Items | scrap, ingots, rods, extrusions, tubes, sheet. **Brass bartan scrap, Gittu scrap.** No brass ingot/rod grade named | target became brass **scrap**, not IS 319 rod |
| Q3 | Rhythm | "almost every week… don't buy in bulk because of the uncertainty" | weekly cadence, no inventory carry to model |
| Q4 | Reaction | cannot act on a same-morning warning; **needs a month's projection** | horizon = 4 weeks |
| Q5 | Markets | **Europe and the Middle East** | all owner-facing copy re-scoped |
| Q5+ | Validity | **same-day only** | risk is the *delivery window*, not the quote ageing |
| Q6 | Price formula | **"LME governs most of it… MCX also governs… transportation is always extra"** | the price is **computable**; two metal routes built |
| Q7 | Scrap | melted into cast then finished; **~70% of raw material is scrap** | target = brass scrap price |
| Q8 | Volumes | brass **5–6 t/month**; Al ~10 t; iron ~10 t | every ₹/kg gets a monthly rupee value |

Q6 was later **half-confirmed from a company source**: Hindustan Copper sets its base price as
**(LME + premium)**, premium **USD 100/t cathode**, **USD 180/t 8 mm CC rod**. Status: Disputed
(single company source). See `output/claim_ledger.csv`.

**Still missing from the owner:** the transport rate in ₹/tonne-km, and one purchase invoice.

---

## 4. Research foundation (closed — do not redo)

| Asset | Count | Notes |
|---|---:|---|
| Driver tree `output/tree.json` | **72 nodes** | 26 Verified / 31 Disputed / 15 Unverified watchlist |
| Cross-link edges `output/edges.json` | **9** | 4 Verified / 5 Disputed |
| Claim ledger `output/claim_ledger.csv` | **65** | claim, source, publisher, URL, date, tier, status |
| Dataset catalogue `output/data_catalogue.csv` | **44** | variable, unit, freq, access, source, lag, quality |
| Quarantined `output/quarantine.csv` | **19** | visible, never deleted |
| Verification rounds | 2 | `output/verification_round1.md`, `round2.md` |

Branches: `SUP` 14 · `DEM` 8 · `MAC` 8 · `POL` 13 · `CONV` 8 · `WATCH` 14 · `ROOT` 1.

**Verified facts worth carrying forward** (re-check before quoting in a new document):
LME copper 25 t, no LME brass · MCX brass launched 2018, absent from the 2026 list · IS 319 Gr-I 56–59% Cu, Gr-II 60–63% Cu · US Section 232 copper 50% on semi-finished content only, effective 1 Aug 2025, ores/cathode/scrap excluded · EU CBAM definitive 1 Jan 2026, brass out of scope · UK CBAM 1 Jan 2027 · UK–India CETA live 15 Jul 2026 · Australia ECTA 100% duty-free from 1 Jan 2026 · UAE CEPA in force since May 2022 · HS 74032100 = BCD 5 + SWS 10 + IGST 18, policy Free.

**Deliberately still Disputed — do not "clean up" by assertion:** ICSG balances · India >90% concentrate import dependence · HZL splits · ICA FY25 1,878 kt · Jamnagar cluster shares · MCX brass as a live hedge · billet ratio · BCD/RoDTEP vintage · QCO status · all demand-branch mechanisms.

---

## 5. Data we actually hold

### 5.1 Series with real data (verified by row count)

| File | Rows | What |
|---|---:|---|
| `data/history/DEXINUS.csv` | 13,497 | USD/INR daily, 1973 → 2026-11 |
| `data/history/DCOILBRENTEU.csv` | 9,122 | Brent daily |
| `data/history/DEXUSEU.csv` | 6,984 | USD/EUR daily |
| `data/manual/mcx_copper_zinc_daily.csv` | 955 | MCX copper + zinc daily closes, 2025-01 → 2026-11-11 |
| `data/history/HOUST.csv` | 813 | US housing starts |
| `data/history/PCOPPUSDM.csv` | 417 | IMF copper monthly, 1992 → 2026-09 |
| `data/history/PZINCUSDM.csv` | 417 | IMF zinc monthly |
| `data/history/TTLCONS.csv` | 405 | US construction spend |
| `data/manual/scrapratetoday_brass_90d.csv` | 235 | retail kabadi brass, 5 cities, 47 days |
| `data/manual/wpi_brass_monthly.csv` | 169 | **WPI brass index, official, 2012-04 → 2026-04** |
| `data/manual/mcx_brass_2019.csv` | 107 | MCX BRASSPHY 2019, zero-volume settlements |
| `data/manual/comtrade_brass_unit_values.csv` | 50 | UN Comtrade HS 740321/740721 unit values |
| `data/manual/wpi_brass_newbase.csv` | 42 | WPI brass, base 2022-23 |
| `data/manual/brass_board_prices.csv` | 27 | dated domestic board quotes, 11 sources |

`data/features_weekly.csv` — **2,789 weekly rows, 1973-01-05 → 2026-11-06, 31 columns.**
Database `brass.db`: 13 series, **31,580 observations**, 74 model_input rows, 5 quotes, 3 notes, 6 sync runs.

### 5.2 Empty templates — nine of them

`au_monthly` · `cotr_weekly` · `freight_weekly` · `lme_daily` · `mandi_quotes` · `opec_monthly` · `pmi_monthly` · `ppac_fuel` · `rbi_ref_rates`

### 5.3 Not collected at all — 18 catalogue entries have no file

LME official/3M/stocks · LME COTR · SHFE stocks · India + US PMI · ocean freight · copper TC/RC · USGS · HCL output · IBM ASP · CBAM certificate price · policy rates · CPI · OPEC MOMR · ABS approvals · RBA · and more.

**Any claim that "all the data is collected" is FALSE.** What is collected is the metal complex, US demand proxies, MCX daily, the WPI brass index, board prices and Comtrade. Audit: `python data/collection_audit.py`.

---

## 6. The two price tiers — resolved contradiction

Indian brass scrap quotes split into two clearly separated markets. Confusing them cost a full day.

Metal content at 2026-09 = **₹998/kg** (`0.615·Cu + 0.385·Zn` at IMF prices and FRED FX).

| Tier | ₹/kg | % of metal content | Who trades |
|---|---:|---:|---|
| Household / kabadi pickup | 402–519 | **40–52%** | a household selling a broken utensil |
| **Foundry board / wholesale** | **810–1000** | **82–100%** | a factory buying tonnes from a trader |

**Castle buys from traders, so its tier is the board.** Sources in the board tier: MTLEXS, AajBazar,
Steel-Baba, ShreeMetalPrices, PTI via News18, SMM, National Recycling, Adinath — eleven independent
sources agreeing within 0.82–1.00 of metal content.

`scrapratetoday.com` and `scrapmonster.com` publish the **household** tier. Their ₹419.93 was
correctly quarantined as a level, but for the *right* reason: it is a real market, just not Castle's.
See `output/quarantine.csv`.

---

## 7. Modelling — everything that was tried, and what it proved

### 7.1 The naive bar (USD/INR)

| Setup | n | MAE | RMSE |
|---|---:|---:|---:|
| 1-week naive | 2,728 | **0.2128** | 0.3832 |
| 1-week seasonal-52 | 2,728 | 2.4057 | 3.3987 |
| 4-week naive | 2,725 | **0.4625** | 0.7965 |

Ridge tournament (3 alphas × 4 ablations, DM tests): best 1w **0.2930**, best 4w **0.5131** —
**naive wins, significantly.** `output/BAND_REPORT.md`.

### 7.2 Metal-leg model (₹/kg, 4-week)

`data/brass_model.py` — inputs shifted for publication lag (copper/zinc 56 days, FX 7 days).

| wCu | naive MAE | best challenger |
|---:|---:|---:|
| 0.580 | 26.45 | 26.74 (drift26) |
| 0.600 | 26.94 | 27.26 |
| **0.615** | **27.31** | 27.65 |
| 0.630 | 27.68 | 28.03 |

**Naive wins at every alloy weight.** The band is **asymmetric**: 80% −₹33.84 / **+₹60.71**;
90% −₹45.98 / **+₹83.03**. Upside risk ≈ 1.8× downside. A symmetric band would systematically
under-cushion the floor — the exact failure the project exists to prevent.

### 7.3 Driver models on the WPI brass index — 8 models, all lost

`data/train_drivers.py` → `data/drivers_results.json`. Target: **WPI brass index 1314090011**,
155 usable months 2013-06 → 2026-04, **94 walk-forward forecasts**, 17 leakage-controlled features.

| h | naive | best ML | drift12 | drift12 DM |
|---|---:|---:|---:|---:|
| 1 | **2.45** | 3.90 (lasso) | 2.31 | +1.04 |
| 2 | **4.26** | 5.39 (ridge) | 4.09 | +0.74 |
| 3 | **5.77** | 6.66 (ridge) | 5.51 | +0.80 |

Every ML model loses with **DM −5.6 to −10.2** — significantly worse, not marginally.
`ridge100` had the *best* direction hit (0.809) and near-worst MAE (6.67): the overfit signature.

**Ablation — the most important table in the project:**

| Feature family | Features | Ridge MAE | vs naive |
|---|---:|---:|---:|
| **naive** | 0 | **2.45** | — |
| index lags only | 5 | 4.19 | +1.74 |
| index + momentum | 8 | 4.17 | +1.72 |
| **metal only** (Cu, Zn, FX) | 5 | **5.54** | **+3.09** |
| **macro only** (Brent, housing, construction, EUR) | 4 | **9.22** | **+6.77** |
| all 17 drivers | 17 | 3.95 | +1.50 |

**Adding features makes it worse.** Metal drivers are noisier than the target's own history; macro
drivers are 3.8× worse than doing nothing. **Brass is structurally explainable but not statistically
forecastable** at 1–3 months.

### 7.4 How many of the 72 nodes are trainable? Six.

| Node | Series | History |
|---|---|---:|
| `M_CU` | IMF copper | 417 months |
| `M_ZN` | IMF zinc | 417 months |
| `F1_INR` | USD/INR | 13,497 days |
| `F1_EUR` | USD/EUR | 6,984 days |
| `F5_EN` | Brent | 9,122 days |
| `D2_US` | US housing + construction | 813 / 405 |

**66 are not trainable:** 57 have no data at all, 1 is too short (CFTC COT, 6 rows), 8 are organising
parents that cannot be variables. By branch: SUP 2/14, DEM 1/8, MAC 3/8, **POL 0/13, CONV 0/8,
WATCH 0/14**.

**Every Castle-specific node is untrainable.** And `D2_US` is the wrong geography — Castle sells to
Europe and the Middle East.

### 7.5 Rupee-saved backtest — the buy/wait signal was rejected

`data/backtest_procurement.py` → `output/PROCUREMENT_BACKTEST.md`. **1,592 decision weeks, 1992 → 2026.**

| | Result |
|---|---:|
| Buy every week (baseline) | ₹249.02/kg |
| Defer when forecast says cheaper | ₹249.13/kg |
| **Difference** | **−₹0.11/kg (−0.045%)** |
| Weeks deferred | 30.5% |
| Monthly impact, 5,500 kg | **−₹612** |

**The signal loses. It was withdrawn, not shipped.** This is the acceptance rule doing its job.

**Cost of delay** (why the owner's weekly rhythm is rational): brass was higher than today in
**52.6% of 1-week, 57.5% of 4-week, 59.6% of 8-week** periods — but the expected cost of waiting is
only **+₹2.38/kg metal per 4 weeks (+0.24%)**. Small on average, one-sided in the tail.

**Quote exposure** — where the money actually is: quoting at the band's middle carries an expected
metal cost of **₹5.37/kg ≈ ₹29,558 per 5,500 kg order**, worst observed ₹77.7/kg.

### 7.6 The ratio — the measured breakthrough

`data/brass_target_from_board.py` → `data/brass_ratio_anchors.json` → `output/BRASS_RATIO_FINDING.md`

```
brass ₹/kg ≈ ratio × metal_leg ₹/kg
```

| Period | Source family | n | Ratio |
|---|---|---:|---:|
| 2019-08 → 2019-12 | MCX BRASSPHY futures, 107 closes | 5 months | **0.977** |
| 2023-01 | MTLEXS Mumbai (honey, sheet) | 6 | **0.910** |
| 2026-11 | eleven Indian boards | 27 | **0.897** |

By grade in 2026: honey **0.888** (sd 0.017) · bartan/utensil **0.872** · purja/mixed **0.866** ·
sheet/chadri **0.963**. Yellow brass (0.701) and gun metal (1.049) are different alloys and are
**excluded, not averaged in**.

**Castle's grades — bartan + honey + purja — pool to ratio 0.876, sd 0.039, n = 16.**

Ratio drifts down roughly **−1.5%/year**. A constant ratio will be wrong in either direction over time.

### 7.7 Two independent metal routes agree to 0.42%

| Route | Construction | Metal value |
|---|---|---:|
| A — LME × FX | 0.615 × Cu $14,473/t × ₹94.53 + 0.385 × Zn $4,021/t × ₹94.53 | ₹987.77/kg |
| B — MCX domestic | 0.615 × ₹1,341.85 + 0.385 × ₹411.45 (already ₹/kg) | ₹983.65/kg |
| | **difference** | **−₹4.12/kg (−0.42%)** |

B embeds FX, import duty and the domestic premium, so this is a genuine cross-check, not a tautology.

**External validation:** MCX BRASSPHY 2019 settled at **0.977×** our computed metal content — an
actual Indian exchange settlement reproduced to 2.3%. Domestic copper: MTLEXS cathode ₹1,410 vs our
IMF-derived ₹1,359 (3.8% gap, consistent with an import premium).

### 7.8 What the floor actually is, term by term

Traced live from `app/engine.py` + the database. **This is the whole model.**

```
metal  = 0.615 × MCX copper + 0.385 × MCX zinc                    = 983.65 ₹/kg   (observed)
brass  = metal × 0.876                                            = 861.68 ₹/kg   (ratio measured)
up     = metal × 0.039 + 25.8 × sqrt(cover_days/30)                              (both measured)
floor  = (brass + up + transport) × 1.05                          = 950.40 ₹/kg   (margin chosen)
verdict = price >= floor ? safe : price >= high ? thin
        : price >= mid ? risky : stop
```

| Term | Value | Source | Status |
|---|---:|---|---|
| metal | 983.65 | MCX bhavcopy | **verified**, 2 days old |
| ratio | 0.876 | 11 boards, n=16 | **measured** |
| ratio sd | 0.039 → ±₹38.36/kg | 16 board readings | **measured** |
| price risk p95 | 25.8 ₹/kg @30d | 1,543 four-week changes | **measured** |
| down/up factor | 0.72 | p05 18.7 ÷ p95 25.8 | **measured** |
| transport | 0.39 ₹/kg | 130 km × ₹3/t-km | **ASSUMED rate** |
| margin | 5% | policy | **CHOSEN** |

**Five of eight inputs are estimated from history.** Two are assumed/chosen. One is a spec (0.615).

Bands: same-day **₹820.31 / ₹862.07 / ₹905.14**, floor **₹950.40** · 15-day floor ₹964.61 ·
30-day floor ₹972.54. Verify: `python -m app.cli week --cover 1`.

**The verdict is not a prediction.** It is a comparison between the number you typed and a computed
threshold. There is no forecast anywhere in the suggestion.

### 7.9 The band width is one constant — and that constant is wrong

`data/quantile_band.py` → `output/QUANTILE_BAND_FINDING.md`

1,543 weeks bucketed by trailing 26-week volatility:

| Regime | weeks | p05 | **p95** |
|---|---:|---:|---:|
| Calm (<6) | 775 | −10.0 | **+13.5** |
| Normal (6–10) | 458 | −22.5 | **+30.0** |
| Elevated (10–14) | 183 | −38.8 | **+45.3** |
| High (≥14) | 127 | −25.3 | **+59.3** |
| **What we ship** | — | — | **+29.74** |

**One constant, wrong in both directions:** 2.2× too wide when calm (floor too high → uncompetitive),
2× too narrow when volatile (breached in **17% of high-volatility weeks** → losses).

Learned width was tested (356 walk-forward origins, pinball loss):

| Model | pinball ↓ | coverage | width |
|---|---:|---:|---:|
| Shipped constant | 4.153 | 0.944 | 51.35 |
| **Linear quantile regression** | **3.292** | 0.928 | 47.25 |
| Gradient boosting quantile | 2.398 | 0.911 | 34.47 (only 28 forecasts — not trusted) |

Linear quantile regression wins in **both** sample halves (2.23 vs 3.33; 4.35 vs 4.98) — **the first
positive modelling result in the project.** But it **overshoots at extremes** (+79.6 vs empirical
+59.3) because the true relationship is concave and the fit is linear.

**Recommendation: regime buckets, not a fitted line.** Floor becomes ₹958 / ₹973 / ₹988 / ₹1,000 by
regime instead of a flat ₹973 — a ₹42/kg spread ≈ **₹2.3 lakh/month** at 5,500 kg.
**NOT YET IMPLEMENTED in `app/engine.py`.**

---

## 8. The product (frontends)

**There are two, and they serve different jobs.**

### 8.1 `frontend/` — the product UI (React 19 + Vite + TypeScript)

Currently the better interface. Dark instrument-panel design: a fixed data strip (metal · low · mid ·
high · floor same-day/15/30 · transport), a large serif floor figure, cover-period selector, a price
sheet card (metal, metal age, ratio ± sd, transport, margin, status), the low/middle/high trio, a
horizontal gauge with **STOP / RISKY / THIN / SAFE** zones and a needle placed on the quoted price,
and a derivation strip showing `metal × ratio + transport = expected + cushion × margin → floor`.

Four screens: `FloorScreen`, `NoteScreen`, `HistoryScreen`, `DataScreen`, plus `Gauge`,
`TrendChart`, `Toast`. **`src/api/client.ts` is the only API client and it deliberately never
recomputes the verdict or the band** — when the backend is unreachable it shows the last cached week,
clearly marked, and disables actions that need the engine. This is the correct architecture and it
fixes the duplication found in the HTML version.

```bash
cd frontend && npm install && npm run dev     # :8080, expects the API on :8000
npm run build                                  # → frontend/dist/ (654 KB, committed)
```

### 8.2 `Castle_Quote_Checker.html` — the field UI

One file, no build step, no npm. Set in the paper/ledger system of `Brass_Story.html`. Four tabs
(Check · Note · History · Data), live API wiring, and an offline fallback to built-in numbers with an
explicit warning. Useful where a laptop cannot run a dev server.

**Known flaw in this one, stated honestly:** it duplicates the verdict thresholds and the note text
between client and server. The React UI does not. If only one UI is maintained, maintain the React one.

### 8.3 Shared behaviour (both)


**`frontend/` — Vite + React 19 + TypeScript app, "Price Sheet" design system (v2).** Built
2026-11-14. Replaces the single-file `Castle_Quote_Checker.html` UI (kept for reference).
The screen is composed as a machined engineering price-sheet of the floor — not a dashboard:
no app shell, no cards, no rounded boxes. A broadsheet masthead with heavy-over-hair rules and a
numbered section index (01 FLOOR / 02 WEEKLY NOTE / 03 HISTORY / 04 DATA); a full-bleed price
strip; the floor as a ~168px Fraunces numeral with a dimension line; an engineering **title
block** (METAL / METAL AGE / RATIO / TRANSPORT / MARGIN 5% ×1.05 / STATUS) carrying the
provenance; a hatched machinist's-rule gauge (verdict zones drawn as diagonal hatch patterns,
tick scale above the ruler, leader-line callouts, dimension line broken around its label); the
whole model shown as a one-line equation; the verdict rendered as a die-cut stamp plate pressed
at −1.8°. Fonts self-hosted via @fontsource (Fraunces Variable, Instrument Sans Variable, IBM
Plex Mono). Four tabs with full parity. Offline shows the cache explicitly marked; every
failure surfaces. Run: `python -m app.cli serve` + `npm run dev` in `frontend/` (README there).
A prebuilt `dist/` ships in the repo. (v1 "Foundry" dashboard composition was rejected as
generic and fully re-composed; screenshots of the review pass live in the build workspace.)

**Architectural fix, stated:** the old client duplicated the verdict thresholds and note text.
The new client **never recomputes verdicts or band maths** — verdicts come only from `POST /quote`;
offline it shows the last synced week from localStorage cache, explicitly marked, with checking
and logging disabled. Nothing is silently estimated.

`Castle_Quote_Checker.html` — **previous product, kept as reference.** Single file, no build step,
4 tabs, offline fallback with built-in numbers. Superseded by `frontend/`.

---

## 9. The backend

```
app/
  config.py    settings + the 13-feed registry (key, mode, freq, lag, template, note)
  db.py        schema, connection, idempotent observation upsert
  engine.py    THE frozen maths: band, verdict, transport, metal routes. MODEL_VERSION.
  feeds.py     FRED (JSON API) / ECB / CFTC fetchers; every failure becomes a status
  sync.py      Sync All, staleness by feed lag, run log
  upload.py    preview → validate → commit, per-feed validators
  pricing.py   inputs + provenance + warnings, week(), quote log, history
  analytics.py realised cost, floor coverage, exposure, weekly series
  notes.py     build / save / deliver the weekly note (file + SMTP)
  api.py       FastAPI surface
  cli.py       the same operations from the terminal
```

**14 endpoints** (OpenAPI 3.1.0 at `/docs`, 5 pydantic schemas):

```
GET  /health              GET  /week?cover_days      POST /quote
GET  /history             GET  /report               GET  /config
POST /sync                GET  /sync/last
GET  /upload/templates    POST /upload/preview       POST /upload/commit
GET  /note                POST /note/send            GET  /note/history
```

**8 tables:** `series`, `observation`, `model_input`, `quote`, `note`, `feed_run`, `feed_run_item`,
`upload`. The **quote log is append-only** and every row carries `floor_at_time` and `model_version`,
so any historical verdict can be reproduced.

**Provenance is surfaced, not hidden.** Every `/week` response carries `metal_source`
(`mcx`/`lme`/`default`), `metal_age_days`, `transport_source`, and a `warnings[]` list. If the metal
input is older than 7 days the floor is marked **PROVISIONAL**.

**Feed status semantics:** `OK` · `STALE` · `BLOCKED` (403) · `FAILED` · `MANUAL`. First real run:
**4 OK / 3 STALE / 6 MANUAL**. MCX and WPI are `MANUAL` because those sites block automation —
recorded as fact, never worked around.

**Upload guards (all tested):** HTML-frameset-saved-as-`.xls` refused with the real reason · prices
outside a sane range rejected per-row with the number quoted back · future dates rejected · headerless
and empty files refused · zero valid rows is blocking · re-upload is idempotent (0 new rows) · auto
feeds cannot be uploaded · duplicate board quotes on one date averaged, never overwritten.

**CLI:**

```bash
python -m app.cli init                      # create brass.db, seed 13 feeds
python -m app.cli sync                      # Sync All, per-feed status
python -m app.cli week --cover 1            # band + floor + provenance + warnings
python -m app.cli quote 1000 --cover 1      # verdict, logged
python -m app.cli report                    # coverage, exposure, per-quote scoring
python -m app.cli note                      # build the weekly note
python -m app.cli note --send --channel file
python -m app.cli upload mcx.copper file.csv [--commit]
python -m app.cli serve                     # uvicorn on :8000
```

---

## 10. Running it on localhost

**Windows, one click:** double-click **`start_local.bat`** → API on :8000, page on :8080, browser opens.
Stop with **`stop_local.bat`**. Full guide: `RUN_LOCAL.md`.

**The new frontend (recommended):**

```bat
:: API (project root)
python -m app.cli serve
:: frontend (separate terminal, in frontend\)
npm install   :: first time only
npm run dev   :: opens the UI on http://127.0.0.1:8080
```

**Manual (old UI):**

```bat
python -m uvicorn app.api:app --host 127.0.0.1 --port 8000
python -m http.server 8080 --bind 127.0.0.1
:: then open http://127.0.0.1:8080/Castle_Quote_Checker.html
```

**Never open the HTML with `file://`** — it cannot call the API and silently falls back to the offline
numbers. It must be served over `http://`.

**WSL / Linux:** `./start_local.sh` (Ctrl-C stops both).

Dependencies (installed on both WSL and the Windows interpreter):
`fastapi uvicorn[standard] python-multipart httpx pytest openpyxl xlrd numpy scikit-learn`

---

## 11. Tests and the bugs they caught

**`python -m pytest tests -q` → 47 passing.**

| File | Tests | Covers |
|---|---:|---|
| `tests/test_engine_upload.py` | 15 | engine maths, asymmetry, transport, verdicts, frameset rejection, range/future/empty guards, idempotency, board averaging |
| `tests/test_api.py` | 18 | health, week validation, quote logging, history, report, sync, note endpoints, upload preview/commit, CORS-independent behaviour |
| `tests/test_analytics_notes.py` | 14 | realised cost, coverage, exposure, unmeasured handling, note build, file delivery, SMTP failure honesty, dry run |

**Bugs found and fixed — each of these was real:**

| Bug | How it was caught | Lesson |
|---|---|---|
| `/report` returned **HTTP 500** — `weekly_series()` selected `floor_at_time AS floor` then read `r['floor_at_time']` | browser test against the live server | unit tests were all green while an endpoint was broken; **click-through testing earns its keep** |
| **Data tab had no click handler at all** — the pane could never open | screenshotting the page | assertions checked elements *existed*, not that the pane was *visible* |
| Entrance animations used `opacity: 0 → 1`; when the animation did not run the **section stayed invisible** | first render of the rebuilt UI was half blank | **never gate visibility on an animation** — use transform-only |
| The guide overlay used an opacity animation → rendered **invisible** | screenshot | same class of bug as above |
| DB path was resolved at **import time**, so all 13 API tests shared the real database | test failures with 6 quotes instead of 2 | resolve config at call time |
| `timeout /t` in the `.bat` was shadowed by Git Bash's Unix `timeout` | running the launcher from a shell | use `ping -n` for waits in batch files |
| Dependencies existed only in WSL → 18 API tests errored on Windows | running the suite on both interpreters | verify on every interpreter you support |
| Counter animation never landed a value when `requestAnimationFrame` did not fire | headless test | set the final value first, animate second |
| Verdict stamp reserved ~120 px of blank paper when hidden | screenshot | collapse with `display`, not `max-height` transitions |
| A file was written with a literal Windows path as its filename | `git status` | the write tool's cwd is **not** the project root |

---

## 12. Environment gotchas — read this before running anything

1. **The shell context switches between WSL and Windows Git Bash.**
   - WSL paths: `/mnt/c/Users/Abuza/OneDrive/Documents/Brass`
   - Git Bash paths: `/c/Users/Abuza/OneDrive/Documents/Brass`
   - If a `cd` fails with "No such file or directory", you are in the other one. Check `pwd` first.
2. **Two interpreters.** `python3` in WSL, `python` on Windows. Both now have the dependencies. Run
   the test suite on whichever you are using.
3. **Headless Chrome differs.**
   - WSL: `/home/abuzar/chrome4testing/chrome-linux64/chrome --headless`
   - Windows: `"/c/Program Files/Google/Chrome/Application/chrome.exe" --headless=new`
   - Write screenshot/dump output to a **relative** path; Windows Python cannot read `/tmp`.
4. **The file-writing tool's working directory is the user's home, not the project.** Files written
   with a relative path may land in the wrong place; files written with a Windows absolute path can be
   created with a literal backslash name. Always verify with `ls` afterwards.
5. **Long heredocs get truncated.** Write large files in chunks of ~4 KB and verify line counts.
6. **`.env` holds `FRED_API_KEY`.** Never print, commit or paste it. It is git-ignored — verified.
7. **`brass.db` is git-ignored** (runtime state). Delete it and re-run `init` for a clean start.
8. **FRED's `fredgraph.csv` endpoint times out** from this network. `app/feeds.py` uses the JSON API
   with the key instead.
9. **OneDrive + WSL** shows file mode 777; that is normal, not a security finding.

---

## 13. What is blocked, and what would unblock it

| # | Missing | Blocks | Resolver |
|---:|---|---|---|
| 1 | **One Castle invoice** (₹/kg, month, grade) | ratio ±₹38 → ±₹17/kg; ±₹2.1 lakh → ±₹92k/month | owner, ~5 minutes |
| 2 | **Transport rate** ₹/tonne-km | the only assumed number in the floor | one freight bill |
| 3 | **Weekly brass rate** | turns the ratio into a tracked series; enables drift correction | purchase man, 30 s/week |
| 4 | **Source markets actually used** | transport default | owner |
| 5 | Bartan/gittu Cu/Zn split | the 0.872 bartan ratio rests on **one** observation | owner or CoA |
| 6 | **GitHub push** | nothing is backed up | your credentials |
| 7 | Auth + hosting | product is localhost-only | not started, deliberately |
| 8 | WhatsApp delivery | note is file/email only | Business API account |

---

## 14. Next steps, in priority order

1. **Push the repo.** 20 commits are local. One OneDrive accident loses the backend.
2. **Get one invoice.** Halves the floor's width; confirms 0.876 is Castle's number, not the market's.
3. **Implement the regime band** in `app/engine.py` (§7.9), bump `MODEL_VERSION`, add stored regime
   table, re-run `data/quantile_band.py` quarterly as a standing test.
4. **Remove the client/server duplication** (§8): have the UI fetch the verdict and the note from the
   API instead of recomputing them.
5. **Log quotes for four weeks**, then read `/report` — that is the rupee proof.
6. **Transport rate** from one freight bill; then distance-based defaults become real.
7. Only then: auth, hosting, scheduler, WhatsApp.

**Do not** reopen forecasting. It is closed with 8 models and an ablation. Reopen only with genuinely
new data (a weekly brass series), and even then expect naive to win.

---

## 15. Do-not-do list

- Do not build a brass target from guessed spreads.
- Do not claim a model beats naive when it does not.
- Do not send the demo signal to the owner.
- Do not delete quarantine rows or hide watchlist nodes.
- Do not ask the owner for bills or documents.
- Do not say a weekday name in owner-facing copy — say "weekly".
- Do not promise a live website or real-time prices.
- Do not paste the FRED key anywhere.
- Do not treat old markdown counts (47/51/28 nodes) as current — the tree is 72.
- Do not present illustrative story numbers (₹850/kg, ₹940 floor) as market data.
- Do not interpolate the monthly WPI index to weekly and call it weekly data.
- Do not use the WPI **old-base** index as a price level — it understates the market by 1.49×.
- Do not treat the ₹420 tier as Castle's price — that is household/kabadi, not the board tier.
- Do not buy a paid data seat before free + manual proves the gap.
- Do not gate visibility on an opacity animation.

---

## 16. File inventory

**Root:** `frontend/` (**the product** — Vite + React + TS, see §8) · `Castle_Quote_Checker.html`
(previous single-file product, kept as reference) · `Brass_Story.html` (owner story) ·
`brass_graph.html` (72-node graph) · `DTPS_Dossier.html` · `Castle_Discovery_Questions.html` ·
`Brass_Weekly_Input.html` · `PRD.md` · `PRD_v2.md` · `BACKEND.md` · `RUN_LOCAL.md` ·
`brass_session_handoff.md` · `HANDOFF_PROMPT.md` · `start_local.bat` · `stop_local.bat` ·
`start_local.sh` · `castle_logo.png` · `DTPS_syllabus_screenshot_2026-11-12.png`


**`.docx` companions:** `PRD.docx` · `PRD_v2.docx` · `PROJECT_BRIEF.docx` · `PRODUCT_DESIGN.docx` · `ARCHITECTURE_PLAN.docx` · `OWNER_INPUT.docx` · `DRIVER_MODEL_RESULTS.docx` · `TODO.docx` · `RUN_LOCAL.docx` · `Executive_Summary.docx`

**`app/`** — the backend (§9). **`tests/`** — 47 tests.

**`data/`** — pipeline: `backfill_fred`, `collect_daily`, `make_features`, `baseline`, `train`, `brass_model`, `brass_target_from_board`, `brass_price_calculator`, `backtest_procurement`, `train_drivers`, `quantile_band`, `check_mcx`, `collection_audit`, `md_to_docx`, `engine`, `decide`. Plus `history/` (7 FRED series), `manual/` (16 files, 9 empty), `outbox/` (generated notes).

**`output/`** — `tree.json` · `edges.json` · `claim_ledger.csv` · `data_catalogue.csv` · `quarantine.csv` · `verification_round1/2.md` · `PROJECT_BRIEF.md` · `PRD_v2.md` · `TODO.md` · `MODEL_SPEC.md` · `OWNER_INPUT.md` · `PRODUCT_DESIGN.md` · `ARCHITECTURE_PLAN.md` · `DRIVER_MODEL_RESULTS.md` · `BRASS_RATIO_FINDING.md` · `QUANTILE_BAND_FINDING.md` · `PROCUREMENT_BACKTEST.md` · `WPI_BRASS_FINDING.md` · `BAND_REPORT.md` · `WHERE_TO_FIND_BRASS_PRICE.md` · `FOLLOWUP_TO_FOUNDER.md` · `NEXT_STEPS.md` · `Brass_Prices_Combined_v3_2026-11-12.xlsx`

**Archive:** `archive/brass_session_handoff_2026-10-01.md` — the original research brief, **frozen**, banner says do not follow.

---

## 17. Commands cheat sheet

```bash
# run
start_local.bat                  # Windows, one click
./start_local.sh                 # WSL / Linux
python -m app.cli serve          # API only, :8000

# verify
python -m pytest tests -q        # 47 tests
python -m app.cli week           # floor + provenance + warnings
python -m app.cli sync           # per-feed status
python -m app.cli report         # coverage + exposure

# data
python -m app.cli upload mcx.copper f.csv --commit
python data/quantile_band.py     # regime / band-width test
python data/train_drivers.py     # the 8 models (all lose)
python data/collection_audit.py  # what is still empty

# docs
python data/md_to_docx.py output/PROJECT_BRIEF.md PROJECT_BRIEF.docx "Title" "Subtitle"
```

---

*End of handoff. Consistent with the machine files as of 2026-11-13. 20 commits, unpushed.*
