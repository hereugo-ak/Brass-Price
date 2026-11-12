# Owner input — verbatim record and what each answer changed

**Source:** founder, Castle Hardwares, Aligarh
**Received:** 2026-11-12 · **Recorded verbatim, not paraphrased**
**Files:** `data/owner_answers.md` (raw), this file (consolidated + consequences)

---

## The record

### Q1 — Suppliers and customers

> We source brass from local traders and vendors, aluminium scrap from local vendors, Aluminium
> extrusions and sheet from Hindalco, Alum and MM metacraft, iron sheet from local Tata/ Jindal
> steel vendors, and SS from Mumbai.

**What this changed:** brass comes from **local traders**, not an exchange and not a mill. That
settled the question of which price tier Castle lives in — the trader/board tier, not the
household kabadi tier. It also confirmed the buying point is bilateral, which is why no public
brass price series exists.

**Still missing:** which city/mandi, and who the buyers are country by country.

---

### Q2 — Items, sizes, grades

> We buy scrap, ingots, rods, extrusions, tubes, sheet, a lot of different sizes, and grades-
> Aluminium 6063, Aluminium ADC12, SS304, Tata CR/HR sheet, SS202, Brass bartan scrap, Gittu scrap

**What this changed:** the only brass named is **bartan scrap and gittu scrap**. No brass ingot or
rod grade was specified. So the modelled commodity became brass **scrap**, not IS 319 rod — which
invalidated the earlier CW614N/C360 assumption in the documents.

**Still missing:** Cu/Zn split for bartan and gittu. The bartan ratio (0.872) currently rests on a
**single** board observation.

---

### Q3 — Order rhythm and load

> We almost buy every week as per our requirement we don't buy in bulk now because of the
> uncertainty in price and availability.

**What this changed:** buying is **weekly and hand-to-mouth**, deliberately not bulk. This killed
the idea of a bulk-buying strategy and made the quote side the place where money is made. It also
means there is no inventory carry to model.

**Still missing:** what one full load is, in kilos.

---

### Q4 — Reaction speed

> Even if you tell me in morning price may climb we will have to contact our vendor to exactly know
> what price are they giving you cannot expect one sudden morning that price is going to go high
> today and hence we need to buy immediately we need atleast a projection for a month to plan for
> delivery.

**What this changed:** the single most consequential answer. It ruled out same-day alerts and fixed
the horizon at **four weeks**. It also revealed the real product requirement: not a prediction, but
**how much room to leave in a quote**.

**Still missing:** the actual lag in days between a warning and placing an order.

---

### Q5 — Markets and quote validity

> Europe and Middle east has most orders

**What this changed:** owner-facing copy was re-scoped from "US, Europe, Australia, UAE" to
**Europe and the Middle East**. The quote shield is now built for a European and a Gulf quote.

**Follow-up (2026-11-12):** *"quote is valid till no price change in market (usually that day only
valid till that day)"*

**Resolved — a quotation is valid same-day only.** This changes the model's exposure window. The
risk is not the quote ageing; it is that the price is fixed today while metal is **bought over the
following weeks**. So the cover period is the **delivery lead time (~1 month, from Q4)**, not the
validity of the quote. The floor is shown for same-day, 15-day and 30-day cover so the difference
is visible.

---

### Q6 — How the buying price is set

Asked: *"How is your buying price set — daily market rate, monthly average, or world price plus
extra charges? One recent quotation answers this fully."*

> **LME governs most of it but in India we have MCX which is metal trading which also governs the
> price, plus the transportation is always extra**

**What this changed: everything about how the price is computed.** It is a **computable formula**,
not a mystery:

```
price = metal (LME-led, MCX domestic reference) + transport + charges
```

This is why the price is **calculated rather than looked up**, and why two independent metal routes
are built:

| Route | Construction | Result (2026-11-12) |
|---|---|---:|
| A — LME × FX | 0.615 × Cu $14,473/t × ₹94.53 + 0.385 × Zn $4,021/t × ₹94.53 | ₹987.77/kg |
| B — MCX domestic | 0.615 × ₹1,341.85 + 0.385 × ₹411.45 | ₹983.65/kg |
| | **agreement** | **−0.42%** |

**Follow-up (2026-11-12):** *"transport varies"* — it depends on distance, i.e. on which city the
metal comes from.

**Transport is now a distance model:** `km × ₹/tonne-km ÷ 1,000`. Delhi 130 km → ₹0.39/kg at
₹3/tonne-km; Jamnagar 1,270 km → ₹3.81/kg. **This corrects an earlier error:** the ₹20/kg figure
used in the first draft was a placeholder and about 50× too high for a short haul. Transport is a
**minor** term — under 0.5% of the price — not a major one.

**Still missing:** the actual ₹/tonne-km rate. All four freight-rate sources probed (IndiaFilings,
Vahak, Porter, BlackBuck) returned **404**, so ₹3/tonne-km is a labelled assumption, editable in the
product. Every ₹1/tonne-km moves the floor by about ₹0.13/kg at 130 km.

---

### Q7 — Scrap

> Scrap is melted into cast and then finished, it makes up almost 70% of our raw material share

**What this changed:** raw material is **70% scrap, melted in-house**. The target became the
domestic brass scrap price, not a mill product. It also means conversion is largely internal, so
power cost matters and a purchased conversion charge largely does not.

**Still missing:** the scrap discount relative to the metal content, and whether scrap price anchors
the buy.

---

### Q8 — Volumes

> Brass almost 5-6tonn · Aluminium almost 10 ton · Iron approx 10 ton

**What this changed:** gives every ₹/kg figure a monthly rupee value. Brass **5–6 t/month** ≈
1.2–1.4 t/week. A ₹10/kg move is **₹55,000/month**; the quote-floor gap of ₹84/kg (middle to floor)
is about **₹4.6 lakh/month**.

---

## Summary: what we asked, what we got

| # | Question | Answered? | Used in |
|---|---|---|---|
| 1 | Suppliers / customers | ✅ partly | tier selection |
| 2 | Items, sizes, grades | ✅ | target = brass **scrap** |
| 3 | Order rhythm | ✅ | weekly cadence, no bulk |
| 4 | Reaction speed | ✅ | **4-week horizon** |
| 5 | Markets / quote validity | ✅ **same-day validity** | Europe + Middle East; same-day cover |
| 6 | Price formula | ✅ mechanism, ❌ numbers | **the calculator + ratio** |
| 7 | Scrap share | ✅ | 70% scrap, in-house melt |
| 8 | Monthly kilos | ✅ | rupee translation |

**All 8 answered.** One thing still open: the **transport rate in ₹/tonne-km** (all freight
sources returned 404, so it is an editable assumption).

---

## Where these words appear in the code

| Answer | Implemented in |
|---|---|
| Q4 — 4-week horizon | `brass_model.py` (`HORIZON = 4`) |
| Q6 — LME + MCX + transport | `brass_price_calculator.py` (two metal routes, transport parameter) |
| Q6 — MCX governs in India | `mcx_copper_zinc_daily.csv` (955 daily closes) feeding the calculator |
| Q7 — scrap, in-house melt | ratio model (0.876) rather than a mill-product price |
| Q8 — 5–6 t/month | `MONTHLY_KG = 5500` in `backtest_procurement.py` |
| Q5 — Europe + Middle East | owner-facing documents, quote-floor framing |

---

*Verbatim source of record: `data/owner_answers.md`. This file summarises and tracks consequences; where the two disagree, the verbatim file wins.*
