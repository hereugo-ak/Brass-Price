# PRD — Brass Guard

**Product:** Brass Guard · **Client:** Castle Hardwares, Aligarh
**Document version:** 2.0 · **Date:** 2026-11-12 · **Status:** DRAFT — awaiting sign-off
**Author:** Product lead (DTPS live project, AMU MBA-506)
**Supersedes:** `PRD.md` (research-phase technical spec, 72 node cards)

---

## 0. Document control

| Section | Owner | Status |
|---|---|---|
| Problem, personas, metrics | Product | draft |
| Feature scope & priorities | Product | draft |
| Data & ingestion | Product + analyst | draft |
| Architecture | Engineering | agreed (`ARCHITECTURE_PLAN.md`) |
| Model results | Data | **final — negative** |
| UX direction | Design | agreed (editorial system) |

**Sign-off required before build:** product scope (§5), non-goals (§4.2), success metrics (§4.3).

---

## 1. Problem

Castle buys brass almost every week and quotes export customers at a price that is fixed the moment
it is given. Metal is bought over the following weeks. When brass moves in between, the difference
comes out of margin — and there is no way to know how much cushion a quote needs.

**Evidence from the owner interview (2026-11-12):**

| Finding | Owner's words |
|---|---|
| Weekly, hand-to-mouth buying | *"We almost buy every week… we don't buy in bulk because of the uncertainty in price and availability."* |
| Cannot act on an alert | *"You cannot expect one sudden morning that price is going to go high today."* |
| Needs a month's view | *"We need at least a projection for a month to plan for delivery."* |
| Price is computable | *"LME governs most of it but in India we have MCX… plus the transportation is always extra."* |
| Quotes are same-day | *"Quote is valid till no price change in market — usually that day only."* |
| 70% scrap, melted in-house | *"Scrap is melted into cast and then finished, almost 70% of our raw material share."* |
| Volume | *Brass ~5–6 tonnes/month.* |
| Markets | *Europe and the Middle East.* |

**The problem statement:**

> Castle cannot set a defensible floor for a fixed-price export quote, because it has no view of the
> brass price it will actually pay over the delivery period — and the segment it buys from publishes
> no forward price.

---

## 2. What we already know (evidence ledger)

This PRD is written **after** the research and modelling, so the scope is constrained by measurement,
not optimism.

| Finding | Result | Consequence |
|---|---|---|
| No brass futures contract exists | LME/MCX/COMEX verified | price must be **reconstructed** |
| Metal leg validated | MCX brass 2019 settled at **0.977×** our computed metal content | level can be trusted |
| Two metal routes agree | LME×FX ₹987.77 vs MCX ₹983.65 = **0.42%** | no single-source dependency |
| Brass/metal ratio measured | **0.876 ± 0.039** (bartan+honey+purja, n=16); 0.977 (2019) → 0.910 (2023) → 0.876 (2026) | spread layer is *measured*, not assumed |
| Band cross-check | band mid ₹871 vs actual board ₹870 | level confirmed externally |
| **Prediction** | **8 models, 17 drivers, 155 months: all lose to naive** (DM −5.6 to −10.2) | **forecasting is out of scope** |
| Buy-timing signal | loses **₹0.11/kg (−0.045%)** vs buying every week | **signal is out of scope** |
| Quote exposure | quoting at the band mid costs **~₹29,500 per 5,500 kg order** expected | **the floor is the product** |

**Therefore the product is a floor, a record, and a weekly ritual — not a forecast.**

---

## 3. Vision

> **A brass quote should never be given without a floor under it.**

One number, at the moment of quoting, backed by a measured model, a public data spine, and a
record of every quote so the claim can be audited in rupees after a quarter.

---

## 4. Goals

### 4.1 Goals

1. **Prevent below-floor quotes.** The single job.
2. **Deliver a weekly ritual** the owner actually opens — one message, three numbers.
3. **Record every quote** so rupees saved can be proven, not asserted.
4. **Make data upkeep honest** — show which feeds are stale or blocked, never silently reuse.
5. **Stay operable by one analyst**, under 30 minutes a week.

### 4.2 Non-goals — explicit and evidence-backed

| Non-goal | Why |
|---|---|
| **Price forecasting** | 8 models lost to a random walk. Re-test quarterly; do not ship. |
| **Buy/wait signal** | Loses ₹0.11/kg. Withdrawn on its own acceptance test. |
| Trading / hedging execution | No brass futures exist; MCX 2019 contract had zero volume |
| Being a marketplace | Owner has trader relationships. Do not insert ourselves. |
| Replacing the owner's judgement | It informs a decision; it does not make one |
| Live/real-time prices | Feeds are daily at best; MCX is manual |
| Multi-tenant SaaS (initially) | One client, one workflow. Prove it first. |

### 4.3 Success metrics

| Metric | Definition | Target | Baseline today |
|---|---|---|---|
| **Below-floor quotes** | quotes logged below floor ÷ total quotes | **→ 0** | unknown (not recorded) |
| **Recorded quotes** | quotes logged per month | **≥ 4** | 0 |
| **Rupees saved** | Σ(quotes below floor corrected × kg) | **> 0, provable** | not measurable |
| **Floor coverage** | 4-week price stays below floor | **≥ 80%** | 80% band by construction |
| **Note engagement** | weeks the note is opened | **≥ 75%** | not measurable |
| **Data freshness** | feeds updated within their lag | **100%** | manual, unverified |
| Time to check a quote | input → verdict | **< 10 s** | n/a |

**Anti-metrics — deliberately not tracked:** prediction accuracy, R², directional hit rate. Chasing
these produced the project's biggest dead end.

---

## 5. Scope and priorities

MoSCoW against the product's job.

### MVP — the pilot (must)

| # | Feature | Acceptance |
|---|---|---|
| F1 | **This week's floor** — band + floor for same-day / 15 / 30-day cover, with the input values shown | a user can read the floor in under 5 seconds |
| F2 | **Check a quote** — enter price, get safe/thin/risky/stop + gap in ₹ on 100 kg and on 5,500 kg | verdict returns in < 300 ms |
| F3 | **Quote log** — every check stored with `model_version`, floor at the time, cover period | rows survive reload; exportable CSV |
| F4 | **Sync All** — one button runs every automatable feed; shows per-feed OK / stale / blocked | completes < 60 s; never silently succeeds on a failure |
| F5 | **Manual upload** — drop a CSV/XLSX for any manual feed; parsed, validated, previewed, committed | bad rows rejected with a reason; nothing written on error |
| F6 | **Guide** — 3-step onboarding + contextual help per feed ("MCX blocks automation — save the bhavcopy and upload it") | a non-technical user completes a manual upload unaided |
| F7 | **Weekly note** — generated text, copy/share, and a record of what was sent | note matches displayed numbers exactly |

### v1 — after the pilot (should)

| # | Feature | Notes |
|---|---|---|
| F8 | History & rupee-saved report | floor vs actual, quotes vs corrections, monthly rupee figure |
| F9 | WhatsApp delivery | via Business API; ~₹1/conversation |
| F10 | Multi-market validity | Europe vs Middle East cover periods, once owner confirms a difference |
| F11 | Ratio recalibration workflow | owner uploads a purchase price → ratio updates with a dated version |
| F12 | Print rate card | one-page PDF for the factory wall |
| F13 | Roles | owner (read/check) vs analyst (upload/config) |

### v2 — only if justified (could)

F14 multi-client (other brass units) · F15 MCX bhavcopy parser (if a permitted route appears) ·
F16 supplier quote comparison · F17 quarterly model re-test harness as a scheduled job ·
F18 mobile app shell / PWA install.

### Won't

Price prediction · buy signal · inventory optimisation · hedging · marketplace · anything requiring
a paid data bypass.

---

## 6. Personas and jobs

| Persona | Context | Job to be done | Today |
|---|---|---|---|
| **Owner** (decision maker, ~60s attention) | phone, WhatsApp, factory floor | *"Tell me the lowest safe price before I send this quote."* | memory + trader calls |
| **Purchase man** | dealer calls, notebook | *"What did brass cost this week?"* | memory |
| **Analyst** (us) | laptop, weekly | *"Keep the numbers current and honest."* | scripts + manual discipline |

**Design constraint from persona 1:** he is not technical, will not learn software, and the tool must
work in under ten seconds with one thumb.

---

## 7. Information architecture

```
Brass Guard
├── 1  This week            floor · band · gauge · inputs · freshness stamp
├── 2  Check a quote        entry · cover period · verdict · log
├── 3  Weekly note          generated text · copy · send · history of sent notes
├── 4  Data                 sync status per feed · upload · guide
│      ├ 4a  Auto feeds     FRED · ECB · CFTC  (one button)
│      └ 4b  Manual feeds   MCX · WPI · board prices · transport · owner rate
├── 5  History              floors vs actual · quotes · rupees saved
└── 6  Settings             ratio · transport · margin · model_version · export
```

Seven screens. Nothing else. **No dashboard, no charts beyond the gauge.**

---

## 8. Feature specifications

### F1 · This week

- Renders band (low / mid / high) and floor for the active cover period.
- Shows the three input values in plain words: metal ₹/kg, ratio, transport ₹/kg.
- **Freshness stamp**: "metal 11 Nov · ratio 12 Nov". If any input is older than its lag, the stamp
  turns amber and names the stale feed.
- Guard rail: if the metal input is older than 7 days, the floor is shown but marked **PROVISIONAL**.

### F2 · Check a quote

- Input: price (₹/kg), cover period (same-day default), optional customer/market.
- Output: verdict + gap in ₹/kg and ₹ on 100 kg / 5,500 kg + the exact floor used.
- On verdict `stop`, offer the one-tap fix: "raise to ₹X".
- Every check writes to the quote log **before** the verdict renders (no loss on crash).

### F3 · Quote log

- Columns: `quoted_at, price, cover_days, floor_at_time, verdict, model_version, market, note`.
- Append-only. Corrections are new rows.
- CSV export; the table is the rupee-saved report's only source.

### F4 · Sync All

- Runs: FRED backfill, collector, features, engine inputs, board extraction.
- Per-feed status: **OK · STALE · BLOCKED(403) · FAILED(network)** — never a generic "done".
- Blocked feeds are expected (MCX, WPI), so they are shown as **action needed**, with a link to the
  upload screen.
- A run log with timestamps is retained and visible.

### F5 · Manual upload

- Accepts `.csv` / `.xlsx` for: MCX bhavcopy, WPI monthly, board prices, weekly brass rate,
  transport bill, owner purchase price.
- **Preview → validate → commit** in three steps:

| Step | Behaviour |
|---|---|
| Preview | show parsed rows, detected columns, date range, row count |
| Validate | units, dates not in the future, price within a sane band, duplicates flagged |
| Commit | refused if any blocking error; otherwise appended with `source`, `retrieved_at` |

- Reuses the existing `check_mcx.py` logic: a frameset shell is rejected with the real reason.

### F6 · Guide

- **First run:** three screens — what the floor is; how to check a quote; when the note arrives.
- **Per feed:** a short "how to get this" panel, including the honest line for MCX: *"This site
  blocks automation. Open it in your browser, select the table, paste into Excel, save as CSV, then
  upload here."*
- **Failure help:** each error state links to the exact remedy, not a generic "contact support".
- Written at a reading level a factory owner can follow: short sentences, no jargon, no AI voice.

### F7 · Weekly note

- Generated from the same values as F1 — the product is forbidden from having two sources of truth.
- Copy, share (Web Share API), and later WhatsApp.
- A record of each sent note is kept, so "did he receive it" is answerable.

---

## 9. Data and ingestion

| Feed | Mode | Frequency | Lag | Owner of failure |
|---|---|---|---|---|
| FRED ×7 | auto | daily | T+1 | analyst |
| ECB | auto | daily | same day | analyst |
| CFTC | auto | weekly | Fri | analyst |
| **MCX copper + zinc** | **manual upload** | daily | T+0 | analyst |
| **WPI brass index** | **manual upload** | monthly | ~14d | analyst |
| **Board prices** | **manual upload** | weekly | same day | analyst |
| **Transport rate** | manual entry | quarterly | n/a | owner |
| **Owner brass rate** | manual entry | weekly (optional) | n/a | purchase man |

**Honesty requirement:** the product must never present a number as current when its feed is stale.
That is the highest-severity defect this product can have.

---

## 10. Architecture (summary)

`output/ARCHITECTURE_PLAN.md` holds the full version. Key decisions:

- **Frozen engine** — `data/engine.py`, `MODEL_VERSION`, one pure function. No ML in the request path.
- **Every stored output carries `model_version`.**
- Postgres (SQLite for the pilot) with `series`, `observation`, `model_input`, `quote`, `note`.
- FastAPI: `/week`, `/quote`, `/history`, `/config`, `/sync`, `/upload`.
- Hosting ~₹1,000/month; no paid data required for the MVP.

---

## 11. Non-functional requirements

| Area | Requirement |
|---|---|
| Speed | check a quote < 300 ms; first paint < 1 s on 4G |
| Offline | the floor and checker work offline (PWA cache); sync requires network |
| Accessibility | WCAG AA contrast; keyboard operable; respects `prefers-reduced-motion` |
| Data safety | quote log append-only; CSV export always available |
| Privacy | no customer names required; no PII stored beyond an optional market label |
| Auditability | any displayed number reproducible from `series` rows + `model_version` |
| Failure behaviour | fail loudly; never write a partial or guessed value |

---

## 12. Analytics

Events: `quote_checked` (price, cover, verdict, floor), `note_copied`, `sync_run` (per-feed outcome),
`upload_attempted` (feed, rows, accepted/rejected), `guide_opened`.

**Deliberately not tracked:** anything identifying the customer, or any prediction accuracy claim.

---

## 13. Risks

| # | Risk | Impact | Mitigation |
|---|---|---|---|
| R1 | Analyst stops uploading MCX/WPI | floors go stale | staleness stamp + amber state + weekly reminder |
| R2 | Ratio drifts (−1.5%/yr) | floor slowly wrong | quarterly recalibration; version the ratio |
| R3 | Transport rate never verified | floor off by ₹1–4/kg | mark as assumption in UI; ask for one bill |
| R4 | Owner ignores the floor | no value delivered | show rupees on a real order size; log adherence |
| R5 | We ship a forecast because it is interesting | credibility loss | §4.2 non-goal is binding |
| R6 | Scope creep to multi-tenant/SaaS | nothing ships | MVP is single-client, seven screens |
| R7 | Owner's "same-day" validity was approximate | cover period wrong | keep 15/30-day views visible; re-confirm |
| R8 | Data licence / terms | legal exposure | MCX stays manual; no bypass, no scraping at scale |

---

## 14. Release plan

### Phase 0 — before 2026-11-15 (submission)

Engine frozen · quote log · weekly note generator · print rate card · architecture diagram ·
this PRD. **No hosted backend.**

### Phase 1 — pilot, weeks 1–4

Seven screens live on a single laptop + phone. Sync All and Manual Upload working. Owner checks real
quotes; every check is logged. **Exit criteria:** ≥ 4 quotes logged, ≥ 1 below-floor quote corrected.

### Phase 2 — v1, months 2–3

History + rupee-saved report. WhatsApp delivery. Ratio recalibration from his weekly rate.
**Exit criteria:** a rupee figure the owner accepts as real.

### Phase 3 — v2, only if Phase 2 shows value

Print card, roles, PWA install, quarterly model re-test job.

---

## 15. Open questions

| # | Question | Blocks | Owner |
|---|---|---|---|
| Q1 | Transport: distance and ₹/km, or one freight bill | floor accuracy | owner |
| Q2 | Which source markets are actually used | transport default | owner |
| Q3 | Is transport already inside the trader's quote | the toggle's correct default | owner |
| Q4 | One purchase invoice (₹/kg, month, grade) | ratio calibration ±₹38 → ±₹17 | owner |
| Q5 | Does quote validity differ by market | multi-market floors (F10) | owner |
| Q6 | Cu/Zn split of bartan and gittu | metal leg precision | owner / CoA |

---

## 16. Product-manager note — why this PRD looks like this

Three things a PM should take from this document:

1. **The non-goals are longer than usual and each one cites evidence.** Killing the forecast was the
   highest-value decision in the project; it came from 94 walk-forward forecasts and an ablation,
   not from a feeling.
2. **The riskiest dependency is a human, not a server.** MCX and the WPI index cannot be automated.
   The product is therefore designed to *fail visibly* and to make manual upload trivially easy.
3. **Every metric is a rupee or a behaviour, none is an accuracy score.** Accuracy metrics are what
   led this project into its dead end; adherence, freshness and rupees saved are what make it useful.

---

*Appendices: `ARCHITECTURE_PLAN.md` (build detail), `PROCUREMENT_BACKTEST.md` (why prediction was
rejected), `DRIVER_MODEL_RESULTS.md` (the 8 models), `PRODUCT_DESIGN.md` (journey, tiers, syllabus).*
