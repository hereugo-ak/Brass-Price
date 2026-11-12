# Full model + backend build plan

**Date:** 2026-11-12 · **Deadline context:** DTPS submission 2026-11-15
**Question this answers:** what does it take to turn the current single-page tool into a real product,
and what can honestly be built before Sunday.

---

## 0. Where we are, stated plainly

| Layer | Today | State |
|---|---|---|
| Data collection | 10 scripts, 7 FRED series, 955 MCX closes, WPI index, board prices, Comtrade | ✅ works, **no scheduler** |
| Identity | metal → brass via measured ratio 0.876 ± 0.039 | ✅ validated (MCX 2019 at 0.977×) |
| Price level | two routes (LME×FX, MCX) agree to 0.42% | ✅ |
| Band | same-day / 15 / 30-day floors: ₹950 / ₹965 / ₹973 | ✅ |
| Prediction | 8 models trained, **all lose to naive**; buy signal rejected | ⛔ dead end, documented |
| Product surface | one HTML file, 19/19 behavioural tests | ✅ but single-device, no data retained |
| Backend | **none** | ⛔ |
| Delivery | none — the note is copy-pasted by hand | ⛔ |
| Retention | localStorage only | ⛔ |

The maths is finished. What is missing is **plumbing**: scheduling, storage, delivery, and a record of
what was quoted so the thing can be audited and improved.

---

## 1. The honest scope decision

There are two products hiding here. They must be separated or the build will sprawl.

| | **Product A — Quote Guard** | **Product B — Price Forecaster** |
|---|---|---|
| Job | stop quoting below a safe floor | tell you what brass will cost in 4 weeks |
| Evidence | ✅ validated | ⛔ **tested and failed** (8 models, naive wins) |
| Build risk | low | very high |
| Sell it? | yes | **no** |

**Build A. Keep B in the drawer with its negative result on file.** Every architecture choice below
serves A. B stays as a research artefact and a quarterly re-test.

---

## 2. Target architecture

```
                 ┌──────────────────────────────────────────┐
   public data → │  INGEST      FRED · MCX · WPI · boards    │  cron / task scheduler
                 └───────────────┬──────────────────────────┘
                                 ↓
                 ┌──────────────────────────────────────────┐
                 │  STORE       Postgres (or SQLite→PG)      │
                 │  series · observations · model_inputs     │
                 └───────────────┬──────────────────────────┘
                                 ↓
                 ┌──────────────────────────────────────────┐
                 │  ENGINE      metal leg · ratio · band     │  one pure function
                 │              floor = f(inputs, cover)     │  versioned
                 └───────────────┬──────────────────────────┘
                    ┌────────────┴────────────┐
                    ↓                         ↓
        ┌───────────────────┐     ┌────────────────────────┐
        │  API  (FastAPI)   │     │  SCHEDULER             │
        │  /week /quote     │     │  weekly note fan-out   │
        │  /history /config │     │  daily data refresh    │
        └─────────┬─────────┘     └───────────┬────────────┘
                  ↓                           ↓
        ┌───────────────────┐     ┌────────────────────────┐
        │  WEB APP          │     │  DELIVERY              │
        │  quote guard      │     │  WhatsApp Business API │
        │  weekly note      │     │  or email fallback     │
        │  history + export │     └────────────────────────┘
        └───────────────────┘
```

**One rule that keeps this sane:** the engine is a **pure function** with an explicit
`model_version`. Every stored row records which version produced it. Without that, in six months
nobody can tell why a floor was ₹950 — and an auditable floor is the entire product.

---

## 3. Components, with real choices

### 3.1 Ingest

| Feed | Method | Frequency | Reality |
|---|---|---|---|
| FRED (7 series) | API | daily | ✅ automated today |
| ECB / CFTC | API | daily / weekly | ✅ automated |
| **MCX copper + zinc** | manual bhavcopy | daily | ⛔ **403 to bots — stays manual** |
| **WPI brass index** | manual download | monthly | ⛔ manual |
| **Board prices** (11 sources) | manual / scrape-with-permission | weekly | ⛔ manual |
| Transport rate | owner bill | quarterly | ⛔ manual |

**Design consequence:** this product is **manual-assist, not fully automated**. Pretending otherwise
would be the single biggest lie in the build. The scheduler must therefore *remind* a human, not
silently fail.

### 3.2 Store

Start `SQLite`, migrate to Postgres when there is a second user. Tables:

```
series(id, name, unit, freq, source, lag_days)
observation(series_id, obs_date, value, retrieved_at, vintage)
model_input(id, as_of, metal, ratio, ratio_sd, transport, margin, model_version)
quote(id, quoted_at, price_inr_kg, cover_days, floor_at_time, verdict, model_version)
note(id, week_start, body, sent_at, channel)
```

`quote` is the one that matters most: it is the record that lets us prove, after a quarter, whether
the floor saved money. It is also the only "training data" this product will ever have.

### 3.3 Engine

A single module, ~80 lines, already written three times in this project. Freeze it:

```python
def band(metal, ratio, sd, transport, cover_days, margin) -> dict
```

Versioned as `model_version = "2026-11-12.1"`. **No model training in this path.** No ML. The
evidence says ML makes it worse.

### 3.4 API

FastAPI, four endpoints:

| Endpoint | Returns |
|---|---|
| `GET /week?cover=1` | band + floor + inputs + model_version |
| `POST /quote` | verdict for a price, stores the check |
| `GET /history?from=` | past floors, verdicts, and what happened |
| `GET /config` | editable parameters (transport rate, ratio, margin) |

### 3.5 Delivery

The product is a **weekly message**, so delivery is the product.

| Channel | Cost | Reality |
|---|---|---|
| **WhatsApp Business API** | ~₹0.60–1.00 per conversation | the right answer; the owner lives in WhatsApp |
| Email | free | acceptable fallback |
| SMS | ~₹0.20 | overkill |
| **Manual copy-paste** | free | what we have; works, does not scale |

**Recommendation:** keep manual copy for the pilot (it also proves whether he opens it), then move to
WhatsApp Business once there is evidence anyone reads it.

### 3.6 Web app

Two screens only: **Check a quote** and **This week's note**, plus **history**. No dashboards. No
charts beyond the gauge. The prose-lite, print-like design already built is the right direction —
it matches the document the owner was given, which is why it reads as a considered product rather
than a template.

---

## 4. What the owner must supply, and when

| Ask | Why | Blocks |
|---|---|---|
| **Transport: distance + ₹/km, or one freight bill** | the only unverified number in the model | floor accuracy ±₹4 |
| **Source markets actually used** | drives distance, hence transport | the transport panel default |
| **Whether transport is already inside his trader's quote** | toggle position | whether transport should be added at all |
| **One invoice** | confirms the ratio is Castle's, not the market's | calibration ±₹38 → ±₹17 |
| **Weekly brass rate** | turns the ratio into a tracked series | drift correction |

**The transport toggle you suggested is the right call** and is already built: if his trader quotes
delivered prices, he switches it off and the floor drops by the transport term. The backend simply
stores that flag alongside the quote.

---

## 5. Build order, and what is realistically deliverable

### Before 2026-11-15 (the submission) — 2 days

| # | Item | Effort | Why |
|---|---|---|---|
| 1 | Freeze engine into `engine.py` with `model_version` | 2h | makes everything else honest |
| 2 | `quotes.sqlite` + a `POST /quote`-equivalent CLI | 2h | starts the audit trail |
| 3 | Weekly note generator that writes a dated file | 1h | delivery without infrastructure |
| 4 | Transport toggle + distance model (done) | — | ✅ |
| 5 | Print-ready one-page rate card (PDF) | 2h | the artefact the factory actually pins up |
| 6 | Architecture diagram in the brief | 1h | shows the plan is real |

**Not before the deadline:** hosted API, WhatsApp integration, user accounts, history UI.

### Weeks 1–4 after

- Host the API + web app (Fly.io / Railway, ~₹500/month)
- Postgres, daily cron with **failure alerts to the analyst**, not silent gaps
- Weekly note by email, then WhatsApp
- History view: floor vs actual, rupees saved

### Months 2–3

- Owner's weekly rate feed → ratio drift series
- Recalibrate ratio quarterly; re-run the model tournament as a standing test
- Quote log → real rupee-saved reporting

---

## 6. Non-negotiables for the backend

1. **`model_version` on every stored output.** No exceptions.
2. **Manual feeds fail loudly.** If MCX is not uploaded, the note must say so, not silently reuse
   last week's number.
3. **No fabricated fill.** A missing week stays a gap in the record.
4. **Vintage history.** FRED revises; store what we saw, not just the latest.
5. **The forecast stays out of production** until it beats naive on a live target. It has not.
6. **Every number traceable** to a series row and a model version.
7. **No paid data bypass.** MCX stays manual because it 403s, not because we found a workaround.

---

## 7. Cost estimate

| Item | Monthly |
|---|---:|
| Hosting (API + web) | ₹500 |
| Postgres (small) | ₹400 |
| WhatsApp Business (≈8 messages/month) | ₹10 |
| Domain | ₹100 |
| **Total** | **~₹1,000/month** |

No paid data seats are needed for Product A. LME history (~$85 once) is only worth it if the metal
leg needs finer granularity — it does not, because prediction has already failed on monthly data.

---

## 8. The one sentence that should govern the build

> The maths is done and it says **do not predict**. Build the plumbing that delivers a defensible
> floor every week, records what was quoted, and proves after a quarter whether the floor saved money.
> Anything that adds prediction to this product is adding risk, not value.

---

*Related: `output/PROCUREMENT_BACKTEST.md` (why prediction was rejected), `output/PRODUCT_DESIGN.md`
(journey, tiers, syllabus mapping), `output/DRIVER_MODEL_RESULTS.md` (the 8 models that lost).*
