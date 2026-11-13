<p align="center">
  <img src="castle_logo_readme.png" alt="Castle Hardwares" width="360">
</p>

<h1 align="center">Brass Guard</h1>

<p align="center">
  <em>A weekly price floor for a brass exporter whose quotes are fixed while metal is still moving.</em>
</p>

<p align="center">
  <code>model 2026-11-12.1</code> &nbsp;·&nbsp;
  <code>47 tests passing</code> &nbsp;·&nbsp;
  <code>72-node driver map</code> &nbsp;·&nbsp;
  <code>no forecast, by design</code>
</p>

---

## The problem

Castle Hardwares, Aligarh — builder hardware since 1965, exporting to Europe and the Middle East — buys brass **almost every week** and quotes at a price that is fixed the moment it is given. Metal is bought over the following weeks. When brass moves in between, the difference comes out of margin.

> *"You cannot expect one sudden morning that price is going to go high today… we need at least a projection for a month to plan for delivery."* — the founder

**Brass Guard answers one question, in under ten seconds:**

> **What is the lowest price this quote can safely carry?**

---

## The honest result, first

This project tested the obvious idea and rejected it.

| What was tried | Outcome |
|---|---|
| 8 predictive models on 155 months of real domestic brass data | **all lost to a random walk** — DM −5.6 to −10.2 |
| A weekly buy/wait signal, 1,592 weeks backtested | **lost ₹0.11/kg** vs simply buying every week |
| Adding all 17 available drivers | **61% worse** than doing nothing |

So there is no forecast here. What survives is the part the evidence supports: **a measured price level, a band, and a quote floor.**

That is the finding, and it is worth more than a fitted model with a fabricated edge.

---

## How the number is built

No black box. Every term, and where it comes from:

```
metal  = 0.615 × MCX copper + 0.385 × MCX zinc          ₹983.65/kg   observed
brass  = metal × 0.876                                  ₹861.68/kg   measured ratio
up     = metal × 0.039 + 25.8 × √(cover_days / 30)                   measured
floor  = (brass + up + transport) × 1.05                ₹950.40/kg   + margin

verdict = price ≥ floor ? safe
        : price ≥ high  ? thin
        : price ≥ mid   ? risky
        :                 stop
```

| Term | Value | Source | Status |
|---|---:|---|---|
| metal | ₹983.65/kg | MCX bhavcopy | **verified** |
| brass/metal ratio | 0.876 | 11 Indian boards, n=16 | **measured** |
| ratio dispersion | ±₹38.36/kg | same 16 readings | **measured** |
| 4-week price risk | ₹25.8/kg | 1,543 historical moves | **measured** |
| asymmetry | 0.72 | p05 ÷ p95 | **measured** |
| transport | ₹0.39/kg | 130 km × ₹3/t-km | **assumed** |
| margin | 5% | policy | **chosen** |

**Five of eight inputs are estimated from history. Two are assumed. None are invented.**

### The level is cross-checked two ways

| Route | Construction | Result |
|---|---|---:|
| LME × FX | 0.615 × Cu $14,473/t × ₹94.53 + 0.385 × Zn $4,021/t × ₹94.53 | ₹987.77/kg |
| MCX domestic | 0.615 × ₹1,341.85 + 0.385 × ₹411.45 | ₹983.65/kg |
| | **agreement** | **0.42%** |

And externally: MCX's 2019 brass contract settled at **0.977×** this same computed metal content — an actual Indian exchange price reproduced to 2.3%.

---

## What is built

| Layer | Detail |
|---|---|
| **Backend** | FastAPI + SQLite · 14 endpoints · 8 tables · append-only quote log · `model_version` on every stored row |
| **Product UI** | React 19 + Vite + TypeScript · 4 screens · instrument-panel design · calls the API for every number |
| **Engine** | one frozen pure function — the only place a floor is computed |
| **Field UI** | one self-contained HTML file · same API · works with no build step and no network |
| **Data** | 7 FRED series (1973→2026) · 955 MCX daily closes · WPI brass index (169 months) · 11 board sources · UN Comtrade |
| **Tests** | 47 backend · 23 browser integration |
| **Sync** | per-feed `OK / STALE / BLOCKED / MANUAL / FAILED` — never silently succeeds |
| **Upload** | preview → validate → commit · refuses the HTML-frameset-saved-as-xls trap · idempotent |

```
  public data                                                 daily sync
  FRED · MCX · WPI · boards · Comtrade                              │
        │                                                           ▼
        └──────────────►  INGEST  ──────────►  STORE  ──────────────┐
                          fetch, validate      series · observation │
                          status per feed      quote · note         │
                                               model_input         │
                                                                   ▼
                                                             ENGINE
                                                     band() · verdict()
                                                       MODEL_VERSION
                                                               │
                                        ┌──────────────────────┴──────────┐
                                        ▼                                 ▼
                                   API  FastAPI                       NOTE
                                   14 endpoints                   file · email
                                        │
                        ┌───────────────┴────────────────┐
                        ▼                                ▼
                 React product UI                 field UI (one file)
                 Floor · Note ·                      offline-capable
                 History · Data                      paper-ledger
```

---

## Quick start

**Windows — one click**

```
start_local.bat
```

Starts the API on `127.0.0.1:8000`, serves the page on `8080`, opens the browser.
Stop with `stop_local.bat`.

**The product UI — React + Vite**

```bash
# terminal 1 — backend
python -m uvicorn app.api:app --host 127.0.0.1 --port 8000

# terminal 2 — product UI
cd frontend
npm install        # first time only
npm run dev        # http://127.0.0.1:8080
```

`npm run build` produces a static bundle in `frontend/dist/` that any static host can serve. A
pre-built copy is committed, so it also runs with `python -m http.server 8080 --directory frontend/dist`.

> The React dev server and `start_local.bat` both default to port **8080**. Run one at a time, or
> change the port in `frontend/vite.config.ts`.

**The field UI — one HTML file, no build step**

```bash
python -m http.server 8081 --bind 127.0.0.1
# open http://127.0.0.1:8081/Castle_Quote_Checker.html
```

> Do not open either page with `file://` — it cannot call the API and silently drops to offline numbers.

**CLI**

```bash
python -m app.cli init                     # create the database
python -m app.cli sync                     # Sync All, per-feed status
python -m app.cli week --cover 1           # floor + provenance + warnings
python -m app.cli quote 1000               # verdict, logged
python -m app.cli report                   # coverage + exposure
python -m app.cli note --send --channel file
python -m app.cli upload mcx.copper f.csv --commit
python -m pytest tests -q                  # 47 tests
```

---

## Honesty rules the code enforces

These are not aspirations. Each is covered by a test.

- **A quote is logged before the response returns** — the audit trail cannot miss a check.
- **Every stored output carries `model_version`** — any historical floor is reproducible.
- **A blocked feed is reported, not hidden.** MCX returns HTTP 403 to automation, so it is `MANUAL`. Nothing is bypassed.
- **Stale data is labelled.** If the metal input is older than 7 days the floor is marked **PROVISIONAL**.
- **A failed email is never reported as sent.** Without SMTP configuration the note reports the exact missing variables and leaves `sent_at` null.
- **Unmeasurable quotes are shown as unmeasured**, never guessed.
- **Exposure is reported as exposure, not as savings** — we cannot prove the owner raised his price.
- **Re-uploading the same file adds zero rows.**
- **The product UI never recomputes the maths.** It asks the engine. A client-side verdict that drifts from the server is how quote tools start disagreeing with themselves.
- **Quarantined claims stay visible** in `output/quarantine.csv`. Nothing is deleted.

---

## The data, and what is missing

| Held | Count |
|---|---:|
| USD/INR daily | 13,497 |
| Brent daily | 9,122 |
| USD/EUR daily | 6,984 |
| MCX copper + zinc daily | 955 |
| US housing starts / construction | 813 / 405 |
| IMF copper / zinc monthly | 417 each |
| WPI brass index (official, India) | 169 months |
| MCX brass 2019 settlements | 107 |
| UN Comtrade unit values | 50 |
| Domestic board quotes | 27 |
| **Weekly feature table** | **2,789 rows × 31 columns** |

**Not collected:** LME official/stocks · SHFE · PMI · ocean freight · TC/RC · USGS · HCL output · IBM ASP · CBAM price · policy rates · CPI · OPEC · ABS/RBA — 18 catalogue entries have no data file, and 9 manual templates are empty. Saying otherwise would be the biggest lie in the project.

**The one number that would change everything:** a single Castle purchase invoice (₹/kg, month, grade). It halves the floor's width from ±₹38 to ±₹17/kg and confirms the ratio is *theirs*, not just the market's.

---

## Repository map

```
app/                     backend — config · db · engine · feeds · sync · upload
                         pricing · analytics · notes · api · cli
frontend/                product UI — React 19 · Vite · TypeScript
  src/screens/             Floor · Weekly Note · History · Data
  src/components/          Gauge · TrendChart · Toast
  src/api/client.ts        single API client; never recomputes the maths
tests/                   47 tests (engine, upload, api, analytics, notes)
data/                    pipeline scripts · history/ · manual/ · outbox/
output/                  research artefacts, findings, PRD, brief, TODO
Castle_Quote_Checker.html   field UI — one file, no build step
Brass_Story.html            owner-facing editorial story
brass_graph.html            interactive 72-node driver map
DTPS_Dossier.html           syllabus-mapped course proof
brass_session_handoff.md    full narrative handoff
HANDOFF_PROMPT.md           paste-ready cold start
BACKEND.md  RUN_LOCAL.md    run and operate
start_local.bat / .sh       one-click localhost launcher
```

---

## Further reading

| Document | What it covers |
|---|---|
| [`brass_session_handoff.md`](brass_session_handoff.md) | the full narrative: everything tried, every number |
| [`output/DRIVER_MODEL_RESULTS.md`](output/DRIVER_MODEL_RESULTS.md) | the 8 models that lost, and the ablation |
| [`output/PROCUREMENT_BACKTEST.md`](output/PROCUREMENT_BACKTEST.md) | why the buy signal was withdrawn |
| [`output/BRASS_RATIO_FINDING.md`](output/BRASS_RATIO_FINDING.md) | the measured spread layer |
| [`output/QUANTILE_BAND_FINDING.md`](output/QUANTILE_BAND_FINDING.md) | why one band width cannot be right |
| [`output/PRD_v2.md`](output/PRD_v2.md) | scope, non-goals, success metrics |
| [`BACKEND.md`](BACKEND.md) | API, feeds, guards, known gaps |

---

<p align="center"><sub>
Castle Hardwares, Aligarh · brass, aluminium and iron builder hardware since 1965<br>
Built as a DTPS live project · Department of Business Administration, Aligarh Muslim University
</sub></p>
