# Where to find Indian brass prices — manual hunt list

**Date:** 2026-11-12
**Why this file:** the automated probes found no free brass series (MCX 403, BigMint 403, SteelMint/
metal.com carry no brass in payload, ScrapMonster/RecycleInMe 404). These are the manual routes left,
in priority order, with the exact queries to run.

**Rule:** every figure you keep needs `date · value · unit · source name · URL · retrieved date`.
A number without a URL is not data. Vendor listing pages are advertisements, not prices.

---

## TIER 1 — the only realistic FREE route to a *historical series*

### 1. UN Comtrade — official customs unit values (free)
`https://comtradeplus.un.org/` — free account, monthly data, no paywall.

Search India (reporter = 344 India) for these HS codes:

| HS code | Meaning | Use |
|---|---|---|
| **740321** | Copper-zinc base alloys (brass), unwrought | closest official brass price proxy |
| **740721** | Copper-zinc base alloys (brass), bars/rods/profiles | your product form |
| 740311 | Refined copper cathodes | copper leg cross-check |
| 7901 | Unwrought zinc | zinc leg cross-check |

Request: **trade value ÷ net weight → USD/kg → × INR/USD → ₹/kg, monthly.**

This is the single best free substitute for a brass price series: it is official, monthly, and has
years of history. It is an **import/export unit value**, not Castle's price — label it a proxy, never
Castle's number.

### 2. Ministry of Commerce — TradeStat India (free)
`https://tradestat.commerce.gov.in/` — HS-wise India trade, monthly. Same unit-value trick.
Useful to cross-check Comtrade, which sometimes lags.

---

## TIER 2 — Indian domestic market, free

### 3. MCX India — copper (browser only)
`https://www.mcxindia.com/market-data/commodity/COPPER` — **403 to bots, fine in a browser.**
MCX copper in ₹/kg is the domestic anchor the founder named. **There is no MCX brass contract**, so
copper + zinc are what you record.

### 4. Indian Bureau of Mines — Average Sale Price
`https://ibm.gov.in/` — official ASP series, monthly, free.
Covers copper/zinc minerals. **Not brass scrap** — it is an upstream anchor. Free and citable.

### 5. Hindustan Copper — price circulars
`https://www.hindustancopper.com/HindiPage/PriceCircular` — domestic cathode / CC-rod base prices.
Mechanism verified in research; circulars are monthly. Copper only.

### 6. EximGuru — HS 74032100 duty + notification feed
`https://www.eximguru.com/indian-customs-duty/74032100-copper-alloys-copper-zinc-base.aspx`
Duty stack (BCD 5 + SWS 10 + IGST 18) and policy-change events. Not a price — a cost wedge.

---

## TIER 3 — paid, but sometimes previewable

### 7. BigMint (ex-SteelMint) — `https://www.bigmint.co/`
The Indian scrap price publisher. 403 to bots; the site works in a browser. Free tier sometimes
shows one headline price. **Do not circumvent the paywall** — if it is gated, record "gated" and
move on. A paid seat is ~₹/month and is a legitimate purchase decision, not a workaround.

### 8. Price reporting agencies — Fastmarkets / Platts / CRU / Wood Mackenzie
Paid seats for premia and scrap spreads. Listed, not bypassed.

---

## TIER 4 — physical market, the honest local route

Brass scrap in India is a **bilateral dealer market**. The cheapest reliable route is a phone call,
not a website.

| Place | Why |
|---|---|
| **Moradabad (UP)** | India's brass city; the reference market for brass scrap and bartan scrap |
| **Aligarh (UP)** | Castle's own market; local traders are the primary source |
| **Jamnagar (Gujarat)** | largest brass manufacturing/trade cluster (source in ledger, Disputed on shares) |
| **Mumbai / Delhi metal markets** | secondary reference |

Ask a scrap dealer, or Castle's own purchase man, for the weekly rate. That is the target series.

---

## TIER 5 — company disclosures (free, real ₹/kg)

Brass and copper-alloy manufacturers disclose raw-material consumption in ₹ and in tonnes.
Divide one by the other and you get **₹/kg actually paid**, by year, from an audited source.

Search annual reports for: `raw material consumed` + `quantity` + `brass`.

Companies to try: listed copper/brass wire, rod and hardware makers; Hindustan Copper; and
architectural-hardware exporters. Treat anything you find as an **annual average**, not a weekly
price, and cite the filing page.

---

## TIER 6 — government scrap auctions (free, occasional)

| Source | URL |
|---|---|
| MSTC e-auction | `https://www.mstcindia.co.in/` |
| GeM (scrap lots) | `https://gem.gov.in/` |

Brass scrap lots appear occasionally. Winning bids are real transacted prices. Sparse and
irregular — useful as cross-checks, not as a series.

---

## SEARCH PROMPTS — copy and paste

### Goal A: today's Indian brass scrap rate
```
brass scrap price per kg India today
```
```
"brass scrap" "per kg" India rate 2026
```
```
brass scrap rate Aligarh
```
```
brass scrap rate Moradabad
```
```
पीतल स्क्रैप भाव आज
```
```
peetal bhangaar rate per kg
```
```
brass bartan scrap price per kg
```
```
brass utensil scrap rate India today
```

### Goal B: the publisher indexes (paid)
```
bigmint brass scrap price India
```
```
site:bigmint.co brass scrap
```
```
steelmint brass scrap price index India
```
```
"brass scrap" index price India monthly
```

### Goal C: official / customs series
```
UN Comtrade India HS 740321 brass unwrought
```
```
site:tradestat.commerce.gov.in 740321
```
```
India import unit value brass 740321 USD per kg
```
```
customs import data copper zinc alloy unwrought India unit price
```

### Goal D: exchange anchors (copper + zinc)
```
MCX copper price today per kg
```
```
LME copper cash settlement official price today
```
```
LME zinc official price today
```
```
MCX copper closing price history download
```

### Goal E: RBI / FX
```
RBI reference rate USD INR archive
```
```
FBIL reference rate USD INR historical
```

### Goal F: company ₹/kg from filings
```
annual report "raw material consumed" brass quantity tonnes India
```
```
brass rod manufacturer annual report raw material cost per kg
```
```
architectural hardware exporter annual report brass consumption
```

### Goal G: auctions
```
MSTC brass scrap auction result
```
```
GeM brass scrap lot bid price
```

### Goal H: the local term (may fail — record if so)
```
"gittu" brass scrap
```
```
gittu scrap rate
```
```
brass gittu price per kg
```
Note: "gittu" is a trade/local term. If searches return nothing, that is a finding — record
"no public usage found" and rely on the founder for that grade.

---

## WHAT TO DO WITH EACH FINDING

Append to `data/manual/mandi_quotes.csv`:

```
date,item,spec,price_inr_kg,source
2026-11-16,brass scrap,bartan,560,<dealer/Moradabad>
```

And if it is a series (Comtrade etc.), note it in `output/data_catalogue.csv` with frequency,
lag and quality issues. Anything gated or unverifiable goes to `output/quarantine.csv` with the
reason — never deleted.

---

## WHAT NOT TO USE

| Not a price | Why |
|---|---|
| IndiaMART / Justdial listings | advertisements, asking prices, no history |
| Social media "rate today" posts | unverifiable, often stale |
| Any figure without a URL | not data |
| Screenshots as the only record | no audit trail |
| Paywall-bypassed content | breach of the project's integrity rule |

---

## REALISTIC EXPECTATION

Comtrade (Tier 1) can give you a **monthly brass unit-value series** today, free. That is enough to
build and backtest a proxy model honestly.

It is **not** Castle's price and cannot be presented as such — it is official customs unit value,
which differs from a local scrap deal by premium, transport, scrap discount and duty. Label it
`brass_import_unit_value_proxy` everywhere.

Only Castle can give you Castle's number.
