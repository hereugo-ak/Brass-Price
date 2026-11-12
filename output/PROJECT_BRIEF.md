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

1. **There is no brass futures contract.** Verified against LME, MCX and COMEX product lists. LME lists copper, not brass. MCX launched a brass contract in 2018 but it is not on the live 2026 product list. COMEX has copper. So brass cannot simply be forecast as a traded price.
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
| Claim ledger (`output/claim_ledger.csv`) | **62 rows** | every claim with URL, date, tier, status |
| Dataset catalogue (`output/data_catalogue.csv`) | **39 rows** | variable, unit, frequency, access, lag, quality |
| Quarantined claims (`output/quarantine.csv`) | **16 rows** | visible, never deleted |
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

Built into **`data/features_weekly.csv` — 2,789 weekly rows, 1973-01-05 → 2026-11-06, 31 columns**, with publication lags mapped in `data/LEAK_MAP.md`.

### 2.3 Domestic Indian brass price index — the key find

**Source:** Office of the Economic Adviser (DPIIT), Government of India — `eaindustry.nic.in`, WPI commodity **1314090011 "Brass metal/sheet/coils"** (row 596 of the monthly workbook).

| Property | Value |
|---|---|
| Base | 2011-12 = 100 |
| Frequency | monthly |
| Coverage | **169 months, 2012-04 → 2026-04** |
| Cost | free, official, no paywall |
| Saved to | `data/manual/wpi_brass_monthly.csv` |

This is the first genuine **domestic Indian brass** price series in the project. It is an **index**, not ₹/kg. One real price anchors it to a 169-month ₹/kg history:

```
price(month) = price_anchor × index(month) / index(anchor_month)
```

### 2.4 Brass scrap retail rates — collected, verified, level quarantined

**Source:** `scrapratetoday.com` — national brass scrap ₹419.93/kg (12 Nov 2026); five cities (Delhi, Mumbai, Jamnagar, Ahmedabad, Pune); **235 daily observations, 47 dates, 2026-09-27 → 2026-11-12**, which form **8 weekly points**. Saved to `data/manual/scrapratetoday_brass_90d.csv`. A 90-day history endpoint was found and pulled.

**Verification result — two parts:**

| Check | Result |
|---|---|
| Transcription against source | **PASS** — ₹419.93 national and ₹429 Delhi match the live pages exactly |
| Physical consistency of the level | **FAIL** — see below |

The ₹419.93 figure is only **43% of the computed metal content** of brass (₹981/kg at Cu $14,473/t, Zn $4,021/t, ₹93.91/USD) and **49% of its own copper content alone**. Anchoring the WPI index to it would imply a 2011-12 brass price of **₹194/kg**, when the metal cost alone that year was **₹287/kg** — impossible.

Additional flag: the series barely moves — standard deviation ₹3.2–4.8 across 47 days on a ~₹425 mean (~1%). That is consistent with a slowly-adjusted indicative rate card, not transacted prices.

**Decision:** the level is **quarantined** (logged in `output/quarantine.csv`, never deleted). The data is kept and may serve as a **directional cross-check only**. It is not used as Castle's price, not used to anchor the WPI index, and not used to estimate volatility.

### 2.5 Owner intelligence — 6 of 8 questions answered

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

What this changed in the design: the modelled target became the **domestic brass scrap price in ₹/kg, delivered, GST inclusive**, not an exchange brass number; the horizon became **four weeks**; the quote shield is built for **Europe and the Gulf**; **transport** entered the price identity; and the **transport cost is inside the target**, not added later.

### 2.6 Models built and results so far

| Model | Target | Result |
|---|---|---|
| Naive / seasonal-52 (`baseline.py`) | USD/INR weekly | naive 1w MAE **0.2128**, 4w **0.4625** |
| Ridge tournament + Diebold–Mariano (`train.py`) | USD/INR weekly | best Ridge 1w **0.2930**, 4w **0.5131** — **naive wins** |
| Metal-leg model (`brass_model.py`) | Cu+Zn×FX, ₹/kg, 4-week | naive MAE **₹27.31/kg**; **all challengers lose at every alloy weight** |
| `drift12` on the WPI brass index | domestic brass index, 1–4 months | **beats naive in all 12 configurations by 2.7–7.5%** — but DM +0.56…+1.22, not significant, and the edge exists only post-2020 |

**Findings that matter:**

- **Naive is very hard to beat** on FX and on the metal leg. That is the honest bar, not a failure.
- **The 4-week band is asymmetric:** at 80% confidence, −₹33.84 / **+₹60.71** ₹/kg. Upside risk is ~1.8× downside. A symmetric band would systematically *under-cushion* the quote floor — the exact failure the project exists to prevent.
- **First genuine challenge to naive:** `drift12` on the real domestic brass index. Suggestive, not established.
- **Metal leg explains only ~19% of monthly domestic brass movement** (R² ≈ 0.19). Copper alone (+0.455) beats the weighted leg (+0.435); USD/INR is essentially uncorrelated at monthly frequency (−0.046) — consistent with the owner's description of a slow, dealer-mediated price.

### 2.7 Tools and deliverables built

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
| `output/WPI_BRASS_FINDING.md` | the index discovery and its four tests | current |
| `output/BAND_REPORT.md` | metal-leg results, band, quote-floor grid | current |

---

## 3. What we are going to do

### 3.1 Method — the four-layer chain

```
Layer 0  identity       ₹/kg = metal leg + spreads + transport + duties
Layer 1  metal leg      Cu, Zn, USD/INR — public, 53 years, forecastable
Layer 2  spread layer   dealer premium, scrap discount, conversion, transport
Layer 3  output         low / middle / high band for 4 weeks + quote floor
```

Layer 1 is **done and tested**. Layer 2 is the only missing piece, and it cannot be estimated from public data because it is a bilateral dealer spread.

### 3.2 The anchor plan — how one price unlocks 14 years

```
price ₹/kg (any month) ──anchors──► WPI brass index (169 months) ──► 169-month ₹/kg history
```

One actual Castle brass price fixes the level; the index supplies the history and the movement. This is the single highest-value next step.

**Blocker, stated plainly:** the anchor must be a real Castle or trader price. The one candidate we have (the retail rate site) **fails the physical consistency test** and was quarantined. It cannot be used.

### 3.3 Sequence

| # | Step | Status |
|---:|---|---|
| 1 | Research the 72-driver map, two verification rounds | done |
| 2 | Build the public data spine and weekly feature table | done |
| 3 | Establish the naive bar on FX | done — naive wins |
| 4 | Build the metal-leg model and 4-week band | done — naive wins, band asymmetric |
| 5 | Find an official domestic brass series | **done** — WPI 1314090011, 169 months |
| 6 | Verify collected brass rate data against source and against physics | **done** — transcription passes, level quarantined |
| 7 | Obtain one real brass price to anchor the index | **open — awaiting Castle** |
| 8 | Build the calibrated ₹/kg series and re-run the tournament on it | blocked on 7 |
| 9 | Rupee-saved backtest: does following the signal beat buying every week | blocked on 8 |
| 10 | Wire the weekly message and quote-floor rule | blocked on 8 |

### 3.4 Automated collection

`data/backfill_fred.py` → `collect_daily.py` → `make_features.py` → `baseline.py` runs end to end. Latest run: **8 feeds collected, 2 missed** — ECB (network) and MCX (HTTP 403 to all automated requests; manual browser only). Misses are recorded, never hidden.

The WPI brass index is purchasable-free but **monthly and manual**; it is added to `LEAK_MAP.md` with its ~14-day publication lag.

---

## 4. What is still missing — and why it cannot be invented

| # | Missing | Why it matters | What resolves it |
|---:|---|---|---|
| 1 | **One actual brass purchase price (₹/kg, with month)** | anchors the 169-month WPI index to ₹/kg — converts an index into a price history | one number from Castle or a trader |
| 2 | Weekly brass price series | calibrates the spread and enables the rupee-saved backtest | one figure a week; 8 rows to start, 30 to be usable, 100+ to fit |
| 3 | Quote-validity days per market | sets the quote-floor horizon precisely | owner; 30 days assumed and stress-tested at 15 and 7 |
| 4 | Spread numbers (premium, transport ₹/kg, conversion, scrap discount) | the ±₹80/kg column in the quote-floor grid | owner's itemised purchase, or the anchored series |
| 5 | LME cash/3M daily history | best metal granularity | paid dataset (~$85) or manual daily entry |

**Why these are not estimated:** the spread uncertainty is ~1.8× the entire 4-week forecast error. Guessing it would make the model 1.8× more fiction than fact, with no way to tell which part was invented. Every output instead carries the spread as a **labelled parameter** with a range.

---

## 5. Honest limitations

1. **No model has beaten naive on a Castle-specific target.** Naive loses on FX and on the metal leg. `drift12` beats naive on the domestic brass index but is not statistically significant and depends on the post-2020 regime.
2. **The project's edge is structural, not predictive** — the identity, the spreads, the asymmetric band, and the quote-floor rule.
3. **The metal leg explains only ~19% of domestic brass movement.** The rest is spread, dealer behaviour and pass-through. That is the part the owner data must supply.
4. **Domestic brass rose 2.14× since 2012 while metal content rose 2.83×.** Unresolved — could be index methodology, margin compression, or basket differences. Not presented as a conclusion.
5. **The one public brass rate source found fails physical plausibility** and is quarantined as a level.
6. **Owner answers are memory-based, not documents.** They are recorded verbatim and dated, and every derived assumption is labelled.

---

## 6. Position at submission (2026-11-15)

**Delivered:** a verified 72-node driver map, a live public data spine with 53 years of history, an honest naive bar, a working metal-leg model with an asymmetric 4-week band and a quote-floor grid, an official 169-month domestic brass index, a verified-and-quarantined retail rate check, a browser capture tool, and owner-facing documents re-scoped to the owner's actual answers.

**Not delivered, and not claimed:** a model that beats naive on Castle's real price, a rupee-saved backtest, or a calibrated ₹/kg history.

**The gap is one number.** Every remaining step is blocked on a single actual brass price. That is a data dependency, not a modelling difficulty, and stating it plainly is the honest result.

---

*Compiled 2026-11-12 from the committed files. Counts are reproducible: `tree.json` 72 nodes, `edges.json` 9, `claim_ledger.csv` 62, `data_catalogue.csv` 39, `quarantine.csv` 16, `features_weekly.csv` 2,789 × 31, `wpi_brass_monthly.csv` 169, `scrapratetoday_brass_90d.csv` 235.*
