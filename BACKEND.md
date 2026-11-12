# Brass Guard — backend

Working backend for the quote-floor product. **No forecasting** — see
`output/DRIVER_MODEL_RESULTS.md`: eight models were trained and all lost to a naive random walk.

---

## Run it

```bash
cd /mnt/c/Users/Abuza/OneDrive/Documents/Brass

python3 -m app.cli init          # create brass.db and seed the feed registry
python3 -m app.cli sync          # Sync All — every automatable feed
python3 -m app.cli week          # this week's band and floor
python3 -m app.cli quote 1000    # check a price, log it
python3 -m app.cli history       # recent quotes

python3 -m app.cli serve         # http://127.0.0.1:8000/docs
```

Tests: `python3 -m pytest tests -q` → **28 passing**.

---

## What is automated and what is not

`sync` runs every feed and reports a status. It never crashes and never invents a value.

| Status | Meaning |
|---|---|
| `OK` | fetched and fresh |
| `STALE` | stored, but older than the feed's lag |
| `BLOCKED` | the publisher refused (HTTP 403) |
| `FAILED` | network or unexpected error |
| `MANUAL` | cannot be automated; needs an upload |

| Feed | Mode | Why |
|---|---|---|
| FRED × 5 (USD/INR, USD/EUR, IMF Cu, IMF Zn, Brent) | auto | free API |
| ECB euro reference | auto | public XML |
| CFTC copper COT | auto | Socrata API |
| **MCX copper / zinc** | **manual** | MCX returns HTTP 403 to all automated requests |
| **WPI brass index** | **manual** | monthly workbook download |
| **Board prices** | **manual** | eleven domestic rate pages |
| **Castle brass rate** | **manual** | owner supplies one figure a week |
| **Transport rate** | **manual** | owner supplies one freight bill |

**This is manual-assist by design.** Pretending otherwise would be the biggest lie in the build.

---

## Uploading a manual feed

Three steps — the file is never written on a dry run.

```bash
# 1. preview (validates, writes nothing)
python3 -m app.cli upload mcx.copper data/manual/mcx_copper.csv

# 2. inspect what was rejected and why
# 3. commit
python3 -m app.cli upload mcx.copper data/manual/mcx_copper.csv --commit
```

Templates: `python3 -m app.cli feeds`

| Feed | Columns |
|---|---|
| `mcx.copper`, `mcx.zinc` | `date, close_inr` |
| `wpi.brass_index` | `month, brass_index` |
| `board.brass_prices` | `date, grade, price_inr_kg, source` |
| `owner.brass_rate` | `week, price_inr_kg` |
| `owner.transport` | `km, rate_inr_per_t_km` |

**Guards that are tested, not aspirational:**

- an HTML **frameset** saved as `.xls` is refused with the real reason (this exact trap cost the
  project a month of empty data)
- prices outside a sane range are rejected per row, with the number quoted back
- future dates rejected
- a file with zero valid rows is refused outright
- re-uploading the same file adds **zero** rows
- auto feeds cannot be uploaded — the error tells you to use Sync All
- two quotes on one date are averaged into one observation, never overwritten

---

## API

Start with `python3 -m app.cli serve`, then open `/docs`.

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | model version, row counts |
| GET | `/week?cover_days=1` | band + floor + provenance + warnings |
| POST | `/quote` | verdict for a price, **logged before the response is returned** |
| GET | `/history?limit=100` | quotes, below-floor count and rate |
| POST | `/sync` | Sync All; per-feed status |
| GET | `/sync/last` | the last run and every feed outcome |
| GET | `/upload/templates` | what each manual feed expects |
| POST | `/upload/preview` | parse + validate, writes nothing |
| POST | `/upload/commit` | write the accepted rows |
| GET | `/config` | feeds, model version, verdict copy |

---

## The rule that makes this auditable

`app/engine.py` is the **only** place a floor is calculated, and it carries `MODEL_VERSION`.
Every `quote` row stores the floor that was shown, the cover period and the model version. That means
any historical verdict can be reproduced exactly — and after a quarter, "did the floor save money"
becomes a query rather than an opinion.

```
MODEL_VERSION = '2026-11-12.1'
floor = (brass + ratio_sd·metal + metal_risk(cover) + transport) × (1 + margin)
brass = metal × 0.876     metal = 0.615·MCX_Cu + 0.385·MCX_Zn
```

Verified against the product UI to ₹0.01: **floor ₹950.40** for a same-day quote at
metal ₹983.65, transport ₹0.39, margin 5%.

---

## Layout

```
app/
  config.py    settings + the 13-feed registry (mode, lag, template, note)
  db.py        schema, connection, idempotent observation upsert
  engine.py    frozen maths: band, verdict, transport, metal routes
  feeds.py     FRED / ECB / CFTC fetchers; every failure becomes a status
  sync.py      Sync All, staleness, run log
  upload.py    preview -> validate -> commit, per-feed validators
  pricing.py   inputs + provenance, week(), quote log, history
  api.py       FastAPI surface
  cli.py       the same operations from the terminal
tests/
  test_engine_upload.py   15 tests
  test_api.py             13 tests
```

---

## Known gaps, stated

| Gap | Effect |
|---|---|
| No scheduler | `sync` is run by hand or by Task Scheduler; nothing fires on its own |
| No auth | pilot runs on localhost only |
| Ratio is a constant | 0.876 from eleven boards; Castle's own invoice would move it ±₹38 → ±₹17 |
| Transport rate assumed | ₹3/tonne-km; one freight bill replaces it |
| No delivery | the weekly note is generated but not sent by this service yet |

Each of these is a deliberate pilot-stage choice, recorded in `output/PRD_v2.md` §4.2 and
`output/TODO.md`.
