# Session handoff — Brass Price Foresight for Castle Hardware

**Last updated:** 2026-11-12
**Project folder:** `/mnt/c/Users/Abuza/OneDrive/Documents/Brass`
**Supersedes:** `archive/brass_session_handoff_2026-10-01.md` (the original research-only brief; keep it for history, do not follow its "do not build a model" instruction — that phase is over).

> **How to use this document:** paste the whole file into a new session as the first message. Then read the authoritative machine files before trusting any prose here: `output/tree.json`, `output/edges.json`, `output/claim_ledger.csv`, `output/quarantine.csv`, `data/baseline_metrics.json`, `data/tournament_dexinus.json`, `data/decisions_demo.json`. Where this document and those files disagree, the files win and this document is wrong and must be corrected.

---

## 0. TL;DR — where the project stands

| Area | State |
|---|---|
| Driver research | **Done.** 72-node MECE tree, 9 evidenced cross-links, two independent verification rounds, 14 numeric claims quarantined. |
| Interactive graph | **Done.** `brass_graph.html` — 3 tabs, 72 nodes, search, expand/collapse, sourced detail panels, watchlist in grey. |
| Owner-facing story | **Done.** `Brass_Story.html` — premium editorial layout, logo header, 8 questions at top, 8 folios, weekly rhythm, verified clean render. |
| Course proof (DTPS) | **Done.** `DTPS_Dossier.html` maps the work to the syllabus frameworks. |
| Technical spec | **Done.** `PRD.md` / `PRD.docx` (72 node cards, 9 rendered flowcharts). |
| Free data spine | **Done and live.** 7 FRED series + ECB + CFTC, full history backfilled, 2,789-row weekly feature table, daily collector at 10/11 feeds. |
| Baseline + model harness | **Done.** Naive bar established; Ridge tournament run; naive wins — by design, this is the honest bar. |
| Decision engine | **Demo only.** Runs on public legs; real brass signal needs owner labels. |
| Owner labels | **Partially unblocked (2026-11-12).** 6 of 8 answers received verbatim in `data/owner_answers.md`. Q6 price formula and Q5 quote-validity days still missing. |
| Manual collection | **Templates ready, mostly empty.** One LME day + one MCX bhavcopy captured. |
| Automation | **Partial.** Cron entry exists but daemon will not start in this WSL without admin; data drifted one month until manually refreshed on 2026-11-11. |

**One-line status:** the public-data half of the system is built, tested and current. The Castle-specific half — the part that makes it a brass model rather than an FX/copper model — is waiting on eight answers.

---

## 1. Project and client

- **Client:** Castle Hardwares, Aligarh. Established 1965. Brass, aluminium and iron builder hardware; PVD finishes; exports to 40+ countries; also a UAE scaffolding/fencing line. Site: `castlehardwares.com`.
- **Problem being solved:** brass is the dominant raw-material cost and its price moves weekly, but export quotes are fixed for roughly 30 days. A quote can be won and then lose money when metal moves before purchase. The business needs a defensible weekly view of the brass price range, plus a quote floor, without hiring a trading desk.
- **Double purpose:** the same work is the user's MBA Design Thinking & Problem Solving (DTPS) live project. Frameworks must be applied visibly and honestly, not name-dropped.
- **End state:** a weekly brass price band (low / middle / high), a buying signal, and a quote-floor rule — each traceable to a driver, a source and a backtest.
- **Explicit non-goals:** no promise of a live public website, no single-point price prediction, no fabricated precision, no asking the owner for bills or documents.

---

## 2. The core insight the whole system rests on

**There is no brass futures contract.** Verified against LME, MCX and COMEX product lists: LME lists copper (25 t contract) but no brass; MCX launched a brass contract in 2018 but it is absent from the live 2026 product list; COMEX has copper, not brass. So brass cannot be "forecast" as a single traded price. It has to be **reconstructed as an identity**:

```
P_INR/kg = wCu · LME_Cu · FX
         + wZn · LME_Zn · FX
         + premium
         − scrap discount
         + conversion
         + margin
         + transport (always extra — owner, 2026-11-12)
         + net duties
```

Consequences that drive every design decision:

1. Model the **three moving legs** first — LME copper, LME zinc, USD/INR — because they explain most of the variance.
2. Then model the **slow spreads** — dealer premium, mandi premium, scrap discount, conversion charge, inventory carry, duty wedges. These are Castle-specific and mostly owner data.
3. Output **bands, not a number**: low / middle / high, derived from model error and spread uncertainty.
4. The same forecast serves **two decisions**: when to buy metal, and what quote floor to set. That is why the selling/quote-guard section belongs in a raw-material (buying) project: the loss is realised on the sell side, after the fixed quote meets moved metal.

**Illustrative arithmetic used in the owner story (clearly labelled illustrative, not live):** a 100 kg order with ₹85,000 of metal; 60/40 rod ≈ ₹850/kg at Cu $13,500/t, Zn $3,500/t, ₹95/USD; quote guard ₹905 + ₹28 = ₹933, plus 5% (₹47) = ₹980 floor; bands ₹892 / ₹905 / ₹918; quote floor ₹940. **Do not present these as current market levels.** They exist to explain the mechanism.

---

## 3. Deliverables map

| File | Audience | What it is | State |
|---|---|---|---|
| `Brass_Story.html` | Owner / Castle team | Premium editorial story: logo header, 8 questions at top, problem, recipe, range charts, system diagram, quote guard explained line by line, honest ending. Weekly wording only. | Final, clean render |
| `brass_graph.html` | User / technical reviewer / DTPS assessor | Self-contained interactive graph. Tabs: Driver Graph, DTPS Steps, Owner Input. 72 nodes, 9 edges, search, expand/collapse, JSON export, watchlist grey badges, sourced detail panels. | Final |
| `Castle_Discovery_Questions.html` | Owner | The 8 questions, printable, no bills requested, US/Europe/Australia/UAE scope. | Final |
| `DTPS_Dossier.html` | Course assessor | Syllabus-mapped proof: MECE, verification, stakeholder work, iteration, reflection. | Final |
| `PRD.md` / `PRD.docx` | Technical team / future analyst | Full spec: price identity, 72 node cards, 9 flowcharts, model tournament, backtest and acceptance rules. | Final |
| `Executive_Summary.docx` | Non-technical sponsor | Short summary of problem, method, deliverables, next steps. | Final |
| `output/tree.json` | Machine source of truth | 72 nodes with definition, inclusion, exclusion, split criterion, status, sources. | Authoritative |
| `output/edges.json` | Machine source of truth | 9 evidenced cross-links with type, sign, lag, evidence, status. | Authoritative |
| `output/claim_ledger.csv` | Audit trail | 61 claim rows: claim, source, publisher, URL, date, retrieved, tier, status, note. | Authoritative |
| `output/data_catalogue.csv` | ML planning | 38 dataset rows: variable, unit, frequency, access, source, history, lag, quality issues. | Authoritative |
| `output/quarantine.csv` | Audit trail | 14 excluded numeric claims with reason and action. Never silently deleted. | Authoritative |
| `output/verification_round1.md`, `round2.md` | Audit trail | Independent verification logs. | Authoritative |
| `output/checkpoint_summary.md` | Audit trail | Timeline, counts, corrections, reconciliation. | Historical |
| `output/README.md` | Audit trail | Method, assumptions, known corrections. | Historical |
| `output/PROPRIETARY_PLAN.md` | Internal | Fresh primary-source intel and the owner-independent plan. | Current |
| `data/*.py` | Pipeline | Collector, backfill, feature builder, baseline, tournament, decision demo. | Working |
| `data/MANUAL_GUIDE.md` | User | Exact manual collection routine with source pages and column headers. | Current |
| `data/manual/*.csv` | Data | Pre-headed manual templates. | Mostly empty |
| `data/owner_answers.md` | Owner | Stub for the 8 answers, one section each. | Empty |

---

## 4. Research foundation (the 72-driver map)

### 4.1 Method

- 8 research subagents in parallel: Supply, Demand, Macro/Finance, Policy/Trade, Conversion/Commercial, Market structure, Cross-links, Data availability.
- Two independent verification rounds: 3 checkers in round 1, 3 different checkers in round 2, plus an adversarial counter-evidence hunt.
- Status rule applied strictly: **Verified** only when both rounds agree; **Disputed** when rounds disagree (reasons kept); **Unverified** for watchlist hypotheses with no evidence yet; numeric claims that failed verification go to **quarantine**, never into the graph.
- MECE tests at every level, plus an independent collective-exhaustiveness check via the price identity above.
- Cross-links live in a separate edge layer so they cannot break the tree.

### 4.2 Structure and counts (current)

| First-level branch | Nodes | Verified | Disputed | Unverified |
|---|---:|---:|---:|---:|
| Root (`ROOT`, Castle brass price) | 1 | 1 | 0 | 0 |
| Supply / metal benchmarks (`SUP`) | 15 | 9 | 6 | 0 |
| Demand pull (`DEM`) | 9 | 0 | 9 | 0 |
| Macro & finance (`MAC`) | 9 | 8 | 1 | 0 |
| Policy & trade wedges (`POL`) | 14 | 5 | 9 | 0 |
| Conversion & commercial (`CONV`) | 9 | 3 | 6 | 0 |
| Watchlist (`WATCH`) | 15 | 0 | 0 | 15 |
| **Total** | **72** | **26** | **31** | **15** |

- **9 edges:** 4 Verified, 5 Disputed.
  1. `F1 → M_CU` — FX to copper price, causal, negative, Disputed.
  2. `S2 → SUP_UP` — smelter tightness to upstream supply, causal, positive, Verified.
  3. `M_CU → S4` — copper price to scrap availability, feedback loop, negative, Disputed.
  4. `P3 → S5` — US market access to visible inventories, causal, positive, Verified.
  5. `F5 → D1` — energy/fuel to India demand, causal, positive, Disputed.
  6. `M_CU → D3` — copper price to substitution, substitution, negative, Verified.
  7. `M_CU → C1` — copper price to metal-value anchor, causal, positive, Verified.
  8. `F2 → D1` — cost of money to India demand, causal, negative, Disputed.
  9. `F5 → C4` — energy to commercial/logistics overlay, causal, positive, Disputed.
- **61 claim-ledger rows**, **38 dataset rows**, **14 quarantined claims**.

### 4.3 Verified facts worth carrying forward

These survived both rounds; still re-check any live number before using it in a document.

- LME copper contract is 25 tonnes; **no LME brass contract**.
- MCX brass launched in 2018 but is **not on the live 2026 product list** — do not treat it as a hedge.
- IS 319: Gr-I 56–59% Cu, Gr-II 60–63% Cu. C360 nominal 61.5% is a midpoint; spec is a range plus lead.
- US Section 232 copper measure: **50% on copper semi-finished content only**, effective 1 Aug 2025; ores, cathodes and scrap excluded; no drawback. Interacts with, and does not simply stack on, the IEEPA India baseline.
- EU CBAM definitive from **1 Jan 2026**, six sectors; brass is out of scope.
- UK CBAM from **1 Jan 2027**.
- UK–India CETA live **15 Jul 2026**; 99% of Indian goods duty-free.
- Australia ECTA: 100% of Indian imports duty-free from **1 Jan 2026**.
- UAE CEPA in force since **May 2022**.
- Fed funds 3.75–4.00% after the Sep 2026 hike; ECB 2.50%; US CPI +3.4% y/y (Aug 2026). These are vintage-stamped facts, not live.
- HS 74032100 brass unwrought: **BCD 5 + SWS 10 + IGST 18, policy Free** (EximGuru mirror of CBIC; marked Disputed until cross-checked directly with CBIC).
- HCL Q1 FY27 mined copper 6,075 MT (+16.65% y/y); Q4 FY26 8,413 MT (+34.01%); MIC sales Q1 FY27 6,619 MT (+21.47%); CC-rod output thin at 2,602 MT.
- IBM publishes Average Sale Prices, Mining & Mineral Statistics and the Indian Minerals Yearbook — official domestic anchors, monthly pull.
- HCL publishes monthly cathode/CC-rod base-price circulars and runs spot booking.

### 4.4 What is deliberately still Disputed

Do not “clean these up” by assertion. They are Disputed because the rounds disagreed or the number had one source:

- ICSG copper balance figures (direction kept, kt numbers quarantined).
- India >90% concentrate import dependence.
- HZL mined vs refined splits; zinc-only vs zinc+lead denominators.
- ICA FY25 1,878 kt and its sector splits.
- Jamnagar cluster shares (denominators conflict between 2018 and 2026 sources).
- MCX brass as a live hedge.
- Billet ratio and conversion-cost magnitudes.
- BCD / RoDTEP vintage / QCO active status / EPR / safeguard / US–India 18% interaction.
- USD beta, energy-to-zinc elasticity, scrap elasticity magnitudes.
- All demand-branch mechanisms (they are plausible but not jointly evidenced).

### 4.5 The watchlist (15 grey nodes)

These are kept visible on purpose — the user insisted nothing be excluded. They are hypotheses awaiting evidence, not findings:

`W_MGN` dealer margins/premia · `W_CONV` live conversion ₹/kg · `W_MND` mandi rod premium · `W_HNY` honey discount · `W_CARRY` inventory carry · `W_PWR` foundry power tariff · `W_MON` monsoon magnitude · `W_EUCOM` EU import volumes · `W_MEDEM` Gulf demand series · `W_AUDEM` Australia demand detail · `W_PB` lead-free cost delta · `W_GST` GST schedule check · `W_BETA` quantified USD beta · `W_ELAS` quantified scrap elasticity.

Upgrade a watchlist node only when a retrievable source is added to the ledger. Never turn grey to coloured by opinion.

### 4.6 Quarantine (14 rows, visible in `output/quarantine.csv`)

Examples: India brass rod $9,511/MT (single vendor, conflicting proxy); conversion scrap-to-billet ₹14–18/kg (2018 anecdote); dealer margins, spot premia, carry rate (no citable source); CZ121 ₹500–600/kg vendor FAQ; ICA 1,878 kt numbers; ICSG kt balances; HZL splits; methodology details (FBIL window, LME VWAP, COMEX specs, BDI weights); single-round rate prints; CD A ratios; dead URLs; quantified edge elasticities; QCO/RoDTEP/drawback/FTZ claims; SHFE/ICSG/ILZSG/IBM/BigMint detailed tables behind paywalls.

**Rule:** quarantine is a holding area, not a bin. A row leaves only with a stronger source, and the move is logged.

---

## 5. Data stack

### 5.1 Automated feeds

`data/backfill_fred.py` pulls full history; `data/collect_daily.py` appends the latest observation each run.

| Series | Meaning | Rows | Coverage | Frequency |
|---|---|---:|---|---|
| `DEXINUS` | USD per INR (FRED H.10) | 13,497 | 1973-01-02 → 2026-11-06 | daily |
| `DEXUSEU` | USD per EUR | 6,984 | 1999-01-04 → 2026-11-06 | daily |
| `PCOPPUSDM` | IMF copper, USD/t | 417 | 1992-01-01 → 2026-09-01 | monthly |
| `PZINCUSDM` | IMF zinc, USD/t | 417 | 1992-01-01 → 2026-09-01 | monthly |
| `DCOILBRENTEU` | Brent, USD/bbl | 9,122 | 1987-05-20 → 2026-11-03 | daily |
| `HOUST` | US housing starts, k | 813 | 1959-01-01 → 2026-09-01 | monthly |
| `TTLCONS` | US construction spend, $M | 405 | 1993-01-01 → 2026-09-01 | monthly |
| ECB euro ref | USD/EUR and INR/EUR | 2 rows per pair | 2026-10-09 and 2026-11-11 snapshots | daily snapshot |
| CFTC `6dca-aqww` | COMEX copper legacy COT | 1 row | 2026-11-03 report (bad 2026-10-06 row removed after parser fix) | weekly snapshot |

**Latest collector run (2026-11-11):** `collected=10 missed=1`. The only miss is MCX bhavcopy, which returns HTTPError to bots. That is expected and recorded, not hidden.

**Important:** `collect_daily.py` captures only the latest observation. It does not fill history. FRED history comes from `backfill_fred.py`. ECB and CFTC currently have a gap between the 2026-10-11 snapshot and 2026-11-11 because the cron job did not run; neither is used in the feature table yet. If they are promoted into features, backfill them first (CFTC API supports history; ECB publishes `eurofxref-hist.zip`).

### 5.2 Weekly feature table

`data/make_features.py` builds `data/features_weekly.csv`:

- **2,789 Friday-anchored rows**, 1973-01-05 → 2026-11-06.
- **31 columns:** `week` + 5 series × (level, lag 1, lag 2, lag 4, lag 8, 4-week momentum).
- Monthly series are carried forward to the latest available observation on or before each Friday.
- No leakage correction is applied here; that is the model's job via `data/LEAK_MAP.md`.

`data/LEAK_MAP.md` records publication lags (FRED H.10 weekly, IMF monthly, CFTC Friday 15:30 ET, ECB ~16:00 CET, MCX manual). Use it when building backtests or the model will see the future.

### 5.3 Manual collection

`data/MANUAL_GUIDE.md` is the routine: 10 min/day, 20 min/week, 30 min/month. Templates are pre-headed in `data/manual/`.

Current contents:

| File | Rows | Note |
|---|---:|---|
| `manual/lme_daily.csv` | 1 | 2026-10-09: Cu cash 14,688.5, Cu 3M 14,567.5, Zn cash 3,839.5, Zn 3M 3,781.25; stocks blank |
| `manual/lme_official_2026-10-09.xlsx` | — | Full LME official table + computed mids + source stamp |
| `mcx_manual/BhavCopyDateWise_09102026.xls` | — | **UNUSABLE.** HTML frameset shell pointing to a missing `sheet001.htm`; no prices. Retained as evidence, not as data. Re-download required. |
| `manual/rbi_ref_rates.csv` | 0 | waiting |
| `manual/freight_weekly.csv` | 0 | waiting |
| `manual/cotr_weekly.csv` | 0 | waiting |
| `manual/mandi_quotes.csv` | 0 | **highest-value manual series** |
| `manual/pmi_monthly.csv` | 0 | waiting |
| `manual/opec_monthly.csv` | 0 | waiting |
| `manual/au_monthly.csv` | 0 | waiting |
| `manual/ppac_fuel.csv` | 0 | waiting |

Rules: append only, never rewrite old rows; a missed day stays a gap; no screenshots as data; no invented numbers.

### 5.4 Paid / gated data (do not fake, do not bypass)

- LME daily history and warehouse detail — bot-walled, paid datasets (~$85/dataset/year is the only purchase worth considering pre-model).
- Fastmarkets / Platts / CRU / Wood Mackenzie premia and scrap spreads — paid seats.
- ICSG / ILZSG / WBMS books — paid or gated.
- SHFE history, BigMint scrap, Comext, MEED — gated.
- Moneycontrol, Zauba, MCX bhavcopy, LME detail — 403 to automated probes; manual browser only.
- IBM ASP, HCL circulars, EximGuru notifications — free but manual/monthly; wire them next.

---

## 6. Models, baselines and the honest result

### 6.1 The bar every model must beat

Walk-forward, `data/baseline.py`, target USD/INR weekly close:

| Setup | n | MAE | RMSE | Direction hit |
|---|---:|---:|---:|---:|
| 1-week naive (carry forward) | 2,728 | **0.2128** | 0.3832 | n/a by construction |
| 1-week seasonal-52 | 2,728 | 2.4057 | 3.3987 | 0.397 |
| 4-week naive | 2,725 | **0.4625** | 0.7965 | 0.450 |
| 4-week seasonal-52 | 2,725 | 2.5111 | 3.5093 | 0.399 |

### 6.2 Challenger tournament

`data/train.py`: expanding-window walk-forward (step 4 weeks), Ridge alphas 0.1/1/10, feature-family ablations (no levels / no lags / no momentum), Diebold–Mariano against naive. n = 671 forecasts per setup.

| Horizon | Best Ridge | MAE | RMSE | DM vs naive |
|---|---|---:|---:|---:|
| 1 week | `ridge0.1_no_levels` | 0.2930 | 0.4900 | +4.893 |
| 4 weeks | `ridge0.1_no_levels` | 0.5131 | 0.8712 | +2.703 |

**Naive wins at both horizons, and the DM statistic is significant in naive's favour.** This is the single most important modelling finding so far, and it is not a failure:

- A random walk is very hard to beat on a liquid currency pair.
- Any claim that a model can reliably out-predict USD/INR week-ahead should be treated as suspect.
- The project's edge is therefore **structural**: the price identity, the spreads, the regime rules and Castle's own labels — not directional FX betting.
- The harness is now proven and will accept the real brass target unchanged.

### 6.3 Decision-engine demo

`data/decide.py` produces a labelled demo, not advice:

- 1,805 weekly signal points; 546 BUY; 30.2% buy rate.
- Average next-week copper move after a BUY: −0.16% (no edge demonstrated).
- Latest: week 2026-11-06, copper $14,473/t, USD/INR 93.91, signal **WAIT**.
- Output: `data/decisions_demo.json`; message text says explicitly that the real message needs the brass target and spreads.

**Do not send this demo message to the owner.** It is a plumbing test.

### 6.4 Model roadmap (unchanged, now sequenced)

1. **Naive bar** — done.
2. **Ridge / elastic-net challenger** — done, loses honestly.
3. **LightGBM direct multi-horizon** — next, on the same walk-forward splits with embargo; only if it beats naive on the real target.
4. **Deep models** — only with 3+ years of clean weekly brass data; CPU is sufficient on Kaggle free tier for the earlier stages.
5. **Champion selection** — tournament + ablations + rupee-saved backtest, not a single accuracy number.
6. **Production rule** — low/middle/high band + quote floor + buy signal, with a kill switch when the band width explodes.

Candidate target file when labels exist: `data/brass_target.csv` with columns `week,true_inr_kg`. `train.py --target BRASS` already looks for it and refuses cleanly if absent.

---

## 7. Owner inputs — partially received (2026-11-12)

`data/owner_answers.md` now holds the founder's verbatim answers dated 2026-11-12. **Answered:** Q1 suppliers, Q2 items/grades, Q3 weekly cadence, Q4 planning horizon, Q5 markets (partial), Q7 scrap share, Q8 volumes. **Still missing:** Q6 price formula (no premium/conversion/scrap/duty breakdown, no quotation) and Q5 quote-validity days. These two numbers gate the spread layer and the quote floor.

What the answers establish: brass is bought as **bartan/gittu scrap** from local traders (no brass ingot/rod grade named); buying is **almost weekly, hand-to-mouth, no bulk**; **Europe and the Middle East carry most orders**; **scrap is ~70% of raw material**, melted in-house; brass volume **~5–6 t/month** (aluminium ~10 t, iron ~10 t); the founder **cannot act same-day** and needs a **~1-month forward projection** to plan. Follow-up on the price mechanism (2026-11-12): **LME governs most of it, MCX also governs the price, and transport is always extra**.

| # | Section | What it unlocks |
|---|---|---|
| Q1 | Suppliers / customers | Bargaining structure, pass-through, who absorbs moves |
| Q2 | Items, sizes, grades | Alloy weights (Cu/Zn/Pb), correct benchmark and conversion route |
| Q3 | Order rhythm / load | Weekly seasonality, inventory cycle, signal horizon |
| Q4 | Reaction speed | Lag from metal move to purchase/quote; the sticky-spread parameter |
| Q5 | Markets / quote validity | Export legs (US, Europe, Australia, UAE), quote windows, currency |
| Q6 | Price formula | Dealer premium, conversion charge, scrap treatment, duty pass-through |
| Q7 | Scrap | Scrap share, discount, whether scrap price anchors the buy |
| Q8 | Monthly kilos | Optional ballpark volume, to translate % moves into rupees |

**Do not ask for bills, invoices or documents.** If the owner volunteers them, log them in `data/invoice_log_template.csv`; otherwise proceed on ballpark answers.

Until Q4 and Q6 land, the spread layer cannot be estimated and the brass target cannot be built. That is not a modelling excuse; it is the actual dependency.

---

## 8. How to run everything

### 8.1 Environment

- Python 3 with `numpy`, `pandas`, `openpyxl` available. `scikit-learn` and `lightgbm` are **not** installed in this WSL; `train.py` deliberately falls back to a numpy Ridge. Install them on Kaggle or locally when moving to LightGBM.
- `Brass/.env` holds `FRED_API_KEY=...`. It is git-ignored. **Never print, commit or paste the key.**
- The collector reads `.env` automatically.

### 8.2 Run order

```bash
cd "/mnt/c/Users/Abuza/OneDrive/Documents/Brass/data"

python3 backfill_fred.py      # full FRED history -> data/history/
python3 collect_daily.py      # latest FRED + ECB + CFTC + MCX probe -> data/*.csv
python3 make_features.py      # -> data/features_weekly.csv
python3 baseline.py           # -> data/baseline_metrics.json
python3 train.py              # -> data/tournament_dexinus.json
python3 decide.py             # -> data/decisions_demo.json (demo only)
```

Every script fails closed: if its input is missing it prints `STOP` and writes nothing. That is intentional.

### 8.3 Sanity checks after a refresh

```bash
# counts and date range
python3 -c "import csv;r=list(csv.DictReader(open('features_weekly.csv')));print(len(r),r[0]['week'],r[-1]['week'],len(r[0]))"
# baseline present
python3 -c "import json;print(json.load(open('baseline_metrics.json')))"
# collector honesty
python3 collect_daily.py | tail -3
```

Expected as of 2026-11-11: 2,789 weekly rows, 1973-01-05 → 2026-11-06, 31 columns, collector 10 collected / 1 missed.

### 8.4 Cron / scheduling

A crontab entry exists:

```
0 8 * * * cd /mnt/c/Users/Abuza/OneDrive/Documents/Brass/data && python3 collect_daily.py >> collect.log 2>&1 # brass-collect
```

But `service cron start` fails in this WSL without interactive admin authentication. Options:

1. Run `sudo service cron start` once (then the entry works while WSL is running).
2. Use Windows Task Scheduler to run the same command at 08:00.
3. Run `collect_daily.py` manually each morning — 10 seconds.

Until one of these is done, **assume no automation**. The 2026-10-11 → 2026-11-11 gap is exactly this failure mode.

---

## 9. Blockers, risks and honest gaps

| Rank | Blocker | Impact | Unblock |
|---:|---|---|---|
| 1 | Owner's 8 answers absent | Cannot build brass target, spread layer, quote floor, or rupee-saved backtest | Owner conversation; log verbatim in `data/owner_answers.md` |
| 2 | Manual series mostly empty | Mandi premium and LME stocks are the strongest slow drivers; absent | 10 min/day routine in `MANUAL_GUIDE.md` |
| 3 | Cron not running | Raw ECB/CFTC logs have a one-month hole; FRED history backfilled so features are current | `sudo service cron start`, Task Scheduler, or manual run |
| 4 | MCX bhavcopy bot-blocked | No automated Indian exchange leg | Manual download into `data/mcx_manual/` |
| 5 | LME daily detail bot-blocked | No free automated LME cash/3M/stocks | Manual LME page entry; consider paid history only if model justifies |
| 6 | Paid premia/scrap seats absent | Cannot validate dealer premium against a market benchmark | Owner quotes first; buy a seat only if the free+manual model fails |
| 7 | No git repository | No version history; OneDrive only | `git init` + first commit if the user wants it |
| 8 | Date drift | Prose/docs can go stale within weeks | Always re-run the pipeline and update the "last updated" line |

**Data-quality warnings:**

- IMF copper/zinc are monthly and lag ~2 months. They are regime features, not weekly triggers.
- FRED H.10 can revise. Backtests should use vintage awareness where possible.
- LME manual rows are typed by hand. One typo is invisible without a range check.
- The 2026-10-09 LME row has blank stocks. Do not treat blank as zero.
- The illustrative story numbers are not current market data.
- Fed/ECB/CPI figures are Sep-2026 vintage; re-check before quoting in a new document.

---

## 10. Next steps, in priority order

### P0 — Owner (partially cleared 2026-11-12)

1. ~~Get the 8 answers~~ — 6 of 8 received verbatim on 2026-11-12.
2. Still needed: (a) **Q6 price formula** — one recent brass purchase quotation showing scrap ₹/kg + charges + delivery; (b) **Q5 quote-validity days** for Europe and the Middle East; (c) **8–12 weeks of actual brass scrap purchase prices** (or one mandi quote per week) to build `data/brass_target.csv`.
3. If offered, log purchase prices in `data/invoice_log_template.csv`; never demand bills.

**Acceptance:** Q6 formula + Q5 validity days written down; brass price history long enough to fit a target; spread parameters (premium, conversion, scrap discount, reaction lag) sourced to the owner interview/quotation.

### P1 — Keep the public spine alive (user, 10 min/day)

4. Start the daily manual routine: RBI rates, LME cash/3M + stocks, MCX bhavcopy.
5. One mandi quote per week in `manual/mandi_quotes.csv` — the single highest-value habit.
6. Fix scheduling (`sudo service cron start` or Task Scheduler).

**Acceptance:** seven consecutive days of RBI + LME rows; one mandi row per week; collector log shows 10/11 or better.

### P2 — Backfill the month gap (user/analyst)

7. Backfill ECB history from `eurofxref-hist.zip`.
8. Backfill CFTC copper COT from the Socrata API (`6dca-aqww`) for the missing weeks.
9. Add HCL MIC y/y and IBM ASP as monthly features; add the HS 74032100 duty stack as event constants.
10. Add EximGuru/CBIC notification events as policy dummies.

**Acceptance:** no raw series used by the model has an unexplained gap; every new feature has a row in `data_catalogue.csv` and a leak rule in `LEAK_MAP.md`.

### P3 — Model promotion (analyst)

11. Install `scikit-learn` + `lightgbm` on Kaggle; run the baseline notebook `data/kaggle_baseline.ipynb`.
12. Build LightGBM direct multi-horizon with walk-forward + embargo.
13. Run the tournament on the real brass target once it exists; compare against naive and Ridge.
14. Add the rupee-saved backtest: does following the signal beat buying every week?
15. Only then wire the weekly message and quote-floor rule.

**Acceptance:** champion beats naive on MAE **and** survives the rupee-saved backtest; otherwise ship the naive band and say so.

### P4 — Only if justified

16. Buy LME history (~$85/dataset/year) if the free model is blocked specifically by LME granularity.
17. Buy one premia/scrap seat if the owner quotes cannot anchor the spread.
18. Kill rule: if a paid feed does not beat free+manual in a backtest within a month, cancel it.

---

## 11. Owner-facing design rules (do not regress)

These were hard-won across several iterations. Treat them as acceptance criteria for any future edit to `Brass_Story.html`.

- **Premium, bespoke, editorial.** Not a template, not an AI-looking dashboard. Ruled-paper / ledger feel, restrained palette, strong typography.
- **Plain English.** No jargon, no consultant-speak, no AI-slop phrases. If a sentence could appear in any generic report, cut it.
- **Every element must earn its place.** No decorative filler, no generic stock imagery, no meaningless icons.
- **Weekly rhythm only.** Say "weekly"; do not say Monday/Friday, and do not promise a live website.
- **Header:** project name + Castle logo + one-line weekly rhythm statement.
- **8 questions near the top, physically separate from the summary.** The owner should see them before any analysis.
- **Keep the selling / quote-guard section**, and explain why it belongs in a raw-material volatility project: a fixed export quote meets moved metal after ~30 days, so the same forecast sets both the buy trigger and the quote floor.
- **No bills / documents request.** Ballpark monthly kilos only, and only if comfortable.
- **Honest ending.** State what is known, what is assumed, and what is still missing. No triumphalism.
- **Logo:** `castle_logo.png` (258×56 RGBA), downloaded from `castlehardwares.com`.

---

## 12. Integrity rules (non-negotiable)

1. **No guessing.** Every claim, URL and figure traces to a retrieved source. Memory is a hypothesis, not a source.
2. **Two independent verification rounds** for research claims. One round = Disputed at best.
3. **MECE at every level**, with the splitting criterion stated in one line per split.
4. **Never fabricate** a source, URL, figure, author or quote. If it cannot be retrieved, write "not retrievable" and move on.
5. **Quarantine, never delete.** Failed claims stay visible in `quarantine.csv` with a reason and action.
6. **Watchlist stays visible.** No silencing an inconvenient factor by removing it; grey it and state what evidence is needed.
7. **Paid data is listed, not bypassed.** Respect site terms; no paywall circumvention, no leaked material.
8. **The naive bar stands.** No model ships unless it beats naive on the metric that matters and survives the rupee-saved backtest.
9. **Label illustrative numbers.** Story arithmetic is illustrative; market data is sourced and dated.
10. **Append-only manual data.** Mistakes get a correcting row, never a silent rewrite.

---

## 13. Full file inventory

```
Brass/
├── .env                         # FRED key — secret, git-ignored, never share
├── .gitignore                   # .env, __pycache__/
├── Brass_Story.html             # owner-facing premium story (current deliverable)
├── Castle_Discovery_Questions.html  # printable 8 questions
├── DTPS_Dossier.html            # syllabus/framework proof
├── Executive_Summary.docx       # non-technical summary
├── PRD.md / PRD.docx            # full technical spec + 72 node cards + flowcharts
├── brass_graph.html             # interactive 72-node graph, 3 tabs
├── brass_session_handoff.md     # this file (canonical handoff)
├── castle_logo.png              # 258×56 RGBA logo from castlehardwares.com
├── archive/
│   └── brass_session_handoff_2026-10-01.md   # original research brief (ARCHIVED — banner says do not follow)
├── output/
│   ├── tree.json                # 72 nodes — authoritative
│   ├── edges.json               # 9 edges — authoritative
│   ├── claim_ledger.csv         # 61 claim rows
│   ├── data_catalogue.csv       # 38 dataset rows
│   ├── quarantine.csv           # 14 excluded claims
│   ├── verification_round1.md
│   ├── verification_round2.md
│   ├── checkpoint_summary.md    # historical timeline (sections 1-3 stale by design)
│   ├── NEXT_STEPS.md            # live action list: human + agent side
│   ├── README.md
│   ├── PROPRIETARY_PLAN.md      # fresh primary-source intel + plan
│   └── FOLLOWUP_TO_FOUNDER.md   # draft message: quotation, transport, validity days, weekly prices
├── data/
│   ├── LEAK_MAP.md              # publication lags for backtests
│   ├── MANUAL_GUIDE.md          # 10 min/day collection routine
│   ├── backfill_fred.py         # full FRED history
│   ├── collect_daily.py         # daily FRED + ECB + CFTC + MCX probe
│   ├── make_features.py         # weekly features
│   ├── baseline.py              # naive / seasonal-52 bar
│   ├── train.py                 # Ridge tournament + DM test
│   ├── decide.py                # decision demo (public legs only)
│   ├── kaggle_baseline.ipynb    # validated notebook scaffold
│   ├── check_mcx.py             # fails closed on the MCX frameset trap
│   ├── invoice_log_template.csv # purchase-price log
│   ├── owner_answers.md         # founder's verbatim answers 2026-11-12 (6/8) + gaps
│   ├── baseline_metrics.json    # current bar
│   ├── tournament_dexinus.json  # current tournament results
│   ├── decisions_demo.json      # demo output
│   ├── features_weekly.csv      # 2,789 × 31 weekly features
│   ├── history/                 # 7 FRED series, full history
│   ├── manual/                  # 9 pre-headed templates + LME xlsx
│   └── mcx_manual/              # MCX bhavcopy — current file is a frameset SHELL, no prices
└── New folder/                  # empty; ignore
```

---

## 14. Corrections and fixes log

| Date | Issue | Fix | Evidence |
|---|---|---|---|
| 2026-11-11 | CFTC collector wrote wrong fields | Fixed-width offsets in `deafut.txt` were misread (OI read as date, NC_L read as legacy code). Replaced with Socrata API `6dca-aqww` named fields: `open_interest_all`, `noncomm_positions_long_all`, etc. Bad row removed and replaced; fix recorded here. | Live API check: latest report 2026-11-03, OI 327,850; NC_L 85,660; NC_S 47,950; spread 99,560; C_L 126,082; C_S 168,005. |
| 2026-11-11 | One-month data drift | Cron daemon never started; raw ECB/CFTC logs had a gap. Re-ran backfill + collector + features + baseline + tournament. | DEXINUS now through 2026-11-06; features 2,789 rows. |
| 2026-10-12 | Story edits risked duplicated/truncated HTML | Machine-verified node counts, folio order, `node --check`, headless Chromium render after every edit. | Zero console errors; 8 folios; 8 questions; counts match. |
| 2026-10-02 | Graph node click swallowed | Pointer-capture bug fixed; deep links added; selftest 72/9. | Headless Chromium selftest. |
| 2026-10-02 | US-only source tilt | Added UAE/Australia/UK/Middle East nodes; 15-node watchlist restored. | Branch counts. |
| 2026-10-01 | Research phase required two rounds | Round 1 + round 2 + reconciliation; disputed items kept with reasons. | `verification_round*.md`. |
| 2026-11-12 | Owner answers received (6/8) | Founder reply recorded verbatim in `data/owner_answers.md`: brass is scrap-based (bartan/gittu), bought almost weekly hand-to-mouth, ~5–6 t/month; Europe + Middle East dominate; ~70% of raw material is scrap; needs ~1-month forward projection. Q6 formula + Q5 validity days still missing. | `data/owner_answers.md` |
| 2026-11-12 | Owner follow-up on price mechanism | Founder: "LME governs most of it but in India we have MCX which is metal trading which also governs the price, plus the transportation is always extra." Identity updated with an MCX reference leg and a transport line. | `data/owner_answers.md` |
| 2026-11-12 | MCX re-capture probed and blocked | `mcxindia.com` returns HTTP 403 on home, Market Data and the bhavcopy endpoint with a normal browser UA. MCX stays manual-browser only; no automated route exists without circumventing the block, which we will not do. | Direct probe 2026-11-12: 3/3 endpoints 403. |
| 2026-11-12 | Guard added for the MCX frameset trap | `data/check_mcx.py` fails closed if a saved bhavcopy has no price table. Current file fails, as expected. `MANUAL_GUIDE.md` now documents the trap and the check. | `python3 check_mcx.py` -> FAIL on the 2026-10-09 file. |

---

## 15. Gotchas for the next session

- **The Windows path is the real path.** Work in `/mnt/c/Users/Abuza/OneDrive/Documents/Brass`. `/home/abuzar/Brass` is a wrong-path trap that already caused one misfiled file.
- **Do not trust prose over JSON.** Counts in old markdown (47 nodes, 51 nodes, 28 ledger rows) are historical. Current tree is 72 nodes / 61 ledger rows / 38 catalogue rows.
- **`output/checkpoint_summary.md` is a timeline, not current state.** It contains earlier counts. Use it for “what happened”, not “what is true now”.
- **Generators:** `brass_graph.html` and `PRD.docx` were produced by scripts in `/tmp/opencode/build_brass.py` and `/tmp/opencode/build_prd.py`. `/tmp` may be wiped. If a rebuild is needed, regenerate the script from the current JSON rather than hand-editing the 84 KB HTML.
- **Headless verification:** `/home/abuzar/chrome4testing/chrome-linux64/chrome` with `--no-sandbox --disable-gpu`. Pillow is available for screenshot crops. Always check console errors and counts after an HTML edit.
- **Mermaid:** `~/.npm/_npx/668c188756b835f3/node_modules/.bin/mmdc` with `-p /tmp/opencode/pup.json`.
- **No git.** There is no repo; do not assume `git diff` works. If version control is wanted, `git init` first and commit before large edits.
- **`collect_daily.py` has no same-day de-dupe.** Running it twice in one day appends two rows for the same observation. Downstream joins must de-dupe on `obs_date`/`series` or the raw log will double-count.
- **OneDrive + WSL:** file mode bits show as 777; that is normal on the Windows mount, not a security finding.
- **Numbers can move.** FRED revises; IMF is monthly with a lag; LME manual entries are hand-typed. Re-run the pipeline before quoting a number in a new document.
- **MCX capture is manual only.** `mcxindia.com` 403s every automated request (verified again 2026-11-12 on 3 endpoints). `data/check_mcx.py` fails closed on the frameset shell that the 2026-10-09 capture turned out to be.
- **`output/FOLLOWUP_TO_FOUNDER.md` is a draft**, not sent. It asks for one costed purchase, the transport rate, quote-validity days and a weekly price note. Do not add requests for bills or documents to it.
- **The `.env` key is live.** Never echo it, never include it in a screenshot, never commit it.

---

## 16. Key figures cheat sheet

**Current data (as of 2026-11-11):**

- Weekly feature rows: 2,789 (1973-01-05 → 2026-11-06), 31 columns.
- USD/INR latest: 93.91 (week 2026-11-06, IMF/FRED-derived feature).
- Copper latest feature: $14,473/t (week 2026-11-06, IMF monthly carried forward).
- LME official 2026-10-09 (manual): Cu cash 14,688.5, Cu 3M 14,567.5, Zn cash 3,839.5, Zn 3M 3,781.25 USD/t.
- Collector: 10 collected / 1 missed (MCX).
- Naive bar: 1w MAE ₹0.2128; 4w MAE ₹0.4625.
- Best Ridge: 1w MAE 0.2930 (loses); 4w MAE 0.5131 (loses).
- Owner follow-up drafted: `output/FOLLOWUP_TO_FOUNDER.md` (4 asks: costed purchase, transport rate, validity days, weekly brass price note).
- Demo signal: WAIT; 30.2% historical buy rate; no demonstrated edge.
- Owner volumes (2026-11-12): brass ~5–6 t/month (~1.2–1.4 t/week); aluminium ~10 t/month; iron ~10 t/month.

**Research counts:**

- 72 nodes: 26 Verified / 31 Disputed / 15 Unverified watchlist.
- 9 edges: 4 Verified / 5 Disputed.
- 61 claim rows; 38 dataset rows; 14 quarantined claims.
- Branches: SUP 15, DEM 9, MAC 9, POL 14, CONV 9, WATCH 15, ROOT 1.

**Illustrative story numbers (not market data):**

- 100 kg order, ₹85,000 metal.
- 60/40 rod ≈ ₹850/kg at Cu $13,500, Zn $3,500, ₹95.
- Quote guard: ₹905 + ₹28 = ₹933; +5% (₹47) = ₹980 floor.
- Bands: ₹892 / ₹905 / ₹918. Quote floor: ₹940.

---

## 17. Open assumptions (still unconfirmed)

- **A1 alloys:** owner names brass **bartan scrap and gittu scrap** only — no brass ingot/rod grade given. CW614N/C36000/C260/Muntz are not confirmed for this client. Lock via a recent quotation or CoA.
- **A2 geography:** buy raw material in India (INR); owner says **Europe and the Middle East carry most orders** (US/Australia unmentioned, assumed minor). Currency legs shift to EUR + AED; confirm quote currency and validity.
- **A3 contracts:** owner buys **almost weekly, hand-to-mouth, no bulk**; needs a **~1-month forward projection** to plan (cannot act same-day). Reaction lag still unquantified — Q4 gave planning horizon, not order lag.
- **A4 hedging:** none. Confirm.
- **A5 horizon:** weekly 1–8 week lags plus monthly regimes.
- **A6 MCX leg:** owner says MCX also governs the price. There is no MCX brass contract (research), so this means MCX copper/zinc futures are the domestic reference. No usable MCX data yet — the captured bhavcopy is a frameset shell. Confirm with a working bhavcopy.

Every assumption must be marked as an assumption in any owner-facing document. Do not let one harden into a fact because it was repeated.

---

## 18. Glossary

- **MECE:** mutually exclusive, collectively exhaustive. No factor in two branches; children cover the parent.
- **Price identity:** brass price rebuilt from copper + zinc + FX + spreads + duties, because no brass futures exist.
- **Basis / spread:** difference between a quoted physical price and the exchange benchmark.
- **Backwardation:** nearby price above forward price; signals tight prompt supply.
- **Contango:** forward above nearby; signals ample supply / carry.
- **TC/RC:** treatment and refining charges paid to smelters; a smelter-margin signal.
- **COT / COTR:** commitments of traders; positioning data (CFTC weekly, LME COTR).
- **Walk-forward:** retrain on past data only, predict the next block, roll forward. No look-ahead.
- **Embargo:** gap between train and test to respect publication lags.
- **Diebold–Mariano:** statistical test of whether two forecast error series differ significantly.
- **Naive bar:** carry-forward forecast; the minimum any model must beat.
- **Quote floor:** minimum price for a fixed-validity export quote that still covers expected metal moves.
- **Watchlist:** visible grey node with a hypothesis but no evidence yet.
- **Quarantine:** failed claim held visibly with a reason; not deleted, not used.

---

## 19. First five actions for the next session

1. Read `output/tree.json`, `output/edges.json`, `output/quarantine.csv`, `data/baseline_metrics.json`. Do not re-research what is already verified.
2. Check whether `data/owner_answers.md` has content. If yes, convert answers into spread parameters and start `data/brass_target.csv`. If no, do not invent labels.
3. Run the pipeline once to confirm the environment still works: `backfill_fred.py → collect_daily.py → make_features.py → baseline.py`.
4. Check `data/manual/` for new rows. Any new mandi/LME/RBI rows should be validated for units and dates before use.
5. Pick the next owner-independent task from P2 (ECB/CFTC gap backfill, HCL/IBM features, duty-event dummies) and log every new claim in `claim_ledger.csv`.

---

## 20. Do-not-do list

- Do not build a brass target from guessed spreads.
- Do not claim a model beats naive when it does not.
- Do not send the demo decision message to the owner.
- Do not delete quarantine rows or hide watchlist nodes.
- Do not ask the owner for bills or documents.
- Do not say Monday/Friday in owner-facing copy; say weekly.
- Do not promise a live website or real-time prices.
- Do not paste the FRED key anywhere.
- Do not treat old markdown counts (47/51/28) as current.
- Do not edit `brass_graph.html` by hand without a count/render check.
- Do not present illustrative story numbers as market data.
- Do not buy a paid data seat before the free+manual model proves the gap.

---

*End of handoff. Last verified against the live files on 2026-11-11.*
