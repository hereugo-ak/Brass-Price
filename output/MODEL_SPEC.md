# Model specification — decisions locked

**Date:** 2026-11-12
**Owner of these decisions:** analyst (you), based on founder interview 2026-11-12
**Purpose:** this file records every choice made about the target variable, so the work is
auditable and can be shown to the examiner, the founder, or a future session. Nothing here is a
guess that was quietly made — each line says what was decided and why.

---

## 1. The target variable — `data/brass_target.csv`

```
week,true_inr_kg
```

One row per week. `true_inr_kg` = the price Castle paid for brass scrap, in rupees per kilo.

### 1.1 Delivery basis — **DELIVERED to works** (decided 2026-11-12)

The price **includes** the transport from the trader to Castle's works. It is the full landed
cost of metal sitting in the yard, not a trader's ex-godown quote.

**Why this basis:** the founder said transport is *always* extra, and it is a real cash cost of
every purchase. Recording it inside the target means the series measures what the business
actually pays for metal. If we had recorded ex-godown prices, transport would have to be added
back later from an estimate — and we have no sourced transport rate, so that estimate would be
invented. Recording delivered removes an unknown instead of creating one.

**Consequence:** if any past or future figure is quoted ex-godown, it **must be flagged and
converted**, not appended silently. A mixed series is not a time series.

### 1.2 GST — **INCLUSIVE** (decided 2026-11-12)

The recorded price includes GST.

**Known risk, recorded deliberately:** GST rates can change by law. Under an inclusive basis, a
rate change shows up as a price move and cannot be separated afterwards. The clean alternative
was GST-exclusive; it was considered and the inclusive basis was chosen anyway. Therefore:

- Any week where the applicable GST rate changes must carry a note in that row.
- Before fitting a model, check the series for a step change at any GST change date.

### 1.3 Grades — **three parallel series** (decided 2026-11-12)

The founder buys two brass scrap types. Both are recorded separately, plus a blend:

| Column | Meaning |
|---|---|
| `bartan_inr_kg` | bartan (household vessel) scrap price |
| `gittu_inr_kg` | gittu scrap price |
| `blend50_inr_kg` | 50-50 blend, for a single headline number |
| `true_inr_kg` | **the modelled target** — whichever series is primary that week, stated in a `basis` column |

**Working assumption to confirm from data:** the blend is a straight 50-50 of the two recorded
prices. If the founder's actual purchase mix is not 50-50, the blend is wrong and must be
re-weighted from his stated monthly split. Mark this as an assumption in any document.

**Why all three:** two grades may price differently and move differently. Recording both costs
nothing once a weekly note exists, and it allows testing whether the blend or a single grade is
the better modelling target.

### 1.4 Observation weekday — **MONDAY** (decided 2026-11-12)

Prices are observed on Monday and dated to that Monday. If a Monday is a market/bank holiday, the
next trading day is used **and the actual observation date is written in the row**, not backdated.

**Why one fixed day:** metal moves daily. If observations drift across weekdays, part of every
week-to-week change is just which day someone looked. A fixed day removes that noise.

**UI requirement:** any collection tool must offer a **weekday dropdown**, defaulting to Monday,
so the observer can change it without touching code. Internal rule only — owner-facing documents
never name a weekday.

---

## 2. Quote validity — **30 days baseline**, adjustable (approved 2026-11-12)

An export quote stays price-fixed for a number of days. That number sets the horizon the quote
floor must cover.

| Setting | Value | Use |
|---|---|---|
| Baseline | **30 days** | the assumption used in documents |
| Stress A | **15 days** | shorter validity, smaller cushion needed |
| Stress B | **7 days** | shortest, minimum cushion |

**Source status:** 30 days is **owner-derived, not invented**. The founder said: *"we need at least
a projection for a month to plan for delivery."* A one-month planning requirement means quoting
must be open roughly that long.

**Known gap:** he did not give per-market values. Europe and the Middle East may differ. Until he
does, 30 days is applied to both and the 15/7-day cases are reported alongside, so the assumption
can never do quiet damage.

---

## 3. Scrap composition — **IS 319 range swept, not asserted** (decided 2026-11-12)

Brass price depends heavily on the copper share:

| Cu share | Metal leg (Cu $14,473/t, Zn $4,021/t, ₹93.91/USD) |
|---|---:|
| 58% | ₹947/kg |
| 60% | ₹967/kg |
| 61.5% | ₹981/kg |
| 63% | ₹996/kg |

**Decision:** use **IS 319 Grade-II, 60–63% Cu**, and **sweep the band** rather than pick a point.
Every output reports the range across 58/60/61.5/63% Cu.

**Why:** "bartan scrap" and "gittu scrap" are old household vessels. No retrieved source states
their exact composition, and asserting one would be fabrication. IS 319 is a citable standard; the
sweep keeps the honest uncertainty visible. It costs one extra column in the output.

---

## 4. Historical brass price data — **NOT AVAILABLE**, retrieval documented

The question asked was: can a reliable public weekly series of Indian brass scrap ₹/kg be found
on the internet? **No.** Recorded so nobody repeats the search blindly.

### 4.1 Retrieval attempts (2026-11-12)

| Source | Result |
|---|---|
| MCX India (brass + copper) | **HTTP 403** — bot-walled |
| BigMint | **HTTP 403** — paid/gated |
| SteelMint | HTTP 200 but **no brass content in response** (JS-rendered) |
| metal.com | HTTP 200, 430 KB, **zero brass mentions** in the payload |
| ScrapMonster India | HTTP 404 |
| RecycleInMe | HTTP 404 |
| IndiaMART brass scrap | HTTP 200 but **no brass listing content** in response |

### 4.2 Structural reasons no such series exists

1. **There is no brass futures contract** anywhere (LME/MCX/COMEX verified in the research phase),
   so there is no exchange settlement series to download.
2. **Indian brass scrap is a physical, local, dealer-quoted market.** Prices are bilateral between
   trader and factory. No exchange, no regulator and no trade body publishes a weekly ₹/kg series.
3. The commercial providers who do track it (**BigMint, SteelMint, Fastmarkets, Platts, CRU**) put
   it behind a paid seat. Per the project's integrity rule, paid data is **listed, not bypassed** —
   no paywall circumvention was attempted.
4. Vendor listing pages (IndiaMART and similar) are **advertisements**, not transacted prices, and
   they carry no usable history. They would be a fabricated series wearing a URL.

### 4.3 Consequence

The public half of the model (copper, zinc, USD/INR, Brent) has **53 years** of retrievable history
and is already built. The Castle-specific half — the price he actually pays — **can only come from
Castle**. There is no shortcut, and stating that plainly is the finding.

**What is done instead:** the metal leg is modelled and forecast on real history; the spread layer
is carried as an explicit unknown with a sensitivity range; the two are combined into a band. When
real prices arrive they calibrate the spread rather than replace the model.

---

## 5. Deadline

**Submission:** 2026-11-15 (stated 2026-11-12 — three days).

This sets the build order: a defensible metal-leg band plus quote-floor calculator with the spread
labelled unknown ships first. The full brass-target model follows once weekly prices exist, and is
reported as the next stage, not claimed as done.

---

## 6. Version control

Repository: `https://github.com/hereugo-ak/Brass-Price.git`

`.env` is git-ignored and must never be committed. The FRED key stays local.

---

## 7. Open items awaiting the founder

| # | Item | Blocks |
|---|---|---|
| 1 | First weekly price row (any of the three series) | the real brass target |
| 2 | Which day he can realistically note the price | collection reliability |
| 3 | Per-market quote validity, Europe vs Middle East | quote-floor precision |
| 4 | Whether his bartan:gittu purchase mix is 50-50 | blend weighting |
| 5 | Transport as a share of delivered price | splitting delivered vs ex-godown in analysis |

None of these are guessed anywhere in the build. Each is carried as a labelled assumption or a
sensitivity range until answered.

---

*Recorded 2026-11-12. Every decision above is referenced by the code that implements it.*
