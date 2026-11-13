# Copy-paste handoff prompt

Paste the block below as the first message in a new session.

---

You are continuing **Brass Guard** for **Castle Hardwares, Aligarh** — a brass price *floor* product, and also the user's DTPS live project (MBA-506, AMU). Established 1965; brass/aluminium/iron builder hardware; **exports mostly to Europe and the Middle East**.

**Working directory** — check `pwd` first, the shell may be in either context:
- WSL: `/mnt/c/Users/Abuza/OneDrive/Documents/Brass`
- Git Bash: `/c/Users/Abuza/OneDrive/Documents/Brass`

**Read these before doing anything, in this order:**
1. `brass_session_handoff.md` — the authoritative narrative (17 sections, everything that was tried)
2. `app/engine.py` — the *only* place a floor is computed; carries `MODEL_VERSION`
3. `output/QUANTILE_BAND_FINDING.md` — the newest result, and what is not yet implemented
4. `output/DRIVER_MODEL_RESULTS.md` — the 8 models that lost, and the ablation
5. `output/BRASS_RATIO_FINDING.md` — the measured spread layer
6. `output/PROCUREMENT_BACKTEST.md` — why the buy signal was withdrawn
7. `output/PRD_v2.md` — scope, non-goals, success metrics
8. Machine files (authoritative): `output/tree.json`, `output/edges.json`, `output/claim_ledger.csv`, `output/data_catalogue.csv`, `output/quarantine.csv`

Where this prompt and a machine file disagree, **the file wins**.

---

## The problem (canonical — do not reword casually)

> **Castle cannot set a defensible floor for a fixed-price export quote, because it has no view of the brass price it will actually pay over the delivery period — and the segment it buys from publishes no forward price.**

**The core insight, do not re-litigate: there is no brass futures contract.** LME lists copper; MCX's 2018 brass contract is absent from the 2026 list and the 2019 one traded at **zero volume and zero OI**; COMEX has no brass. So brass is **reconstructed**:

```
price ₹/kg = wCu·Cu·FX + wZn·Zn·FX + premium − scrap + conversion + margin + transport + duties
```

**But the code collapses this.** `app/engine.py` computes `metal × 0.876 + transport`, where the ratio absorbs premium, scrap discount, conversion and duties. That is deliberate — describe it accurately, do not present the six-term form as what runs.

---

## Current state — honest

| Area | State |
|---|---|
| Owner intelligence | ✅ 8/8 answered verbatim + Q5/Q6 follow-ups (`data/owner_answers.md`) |
| Driver research | ✅ 72 nodes (26 Verified / 31 Disputed / 15 Unverified), 9 edges, 65 claims, 44 catalogue, 19 quarantined |
| Public data | ✅ 2,789 weekly rows 1973→2026 · 955 MCX daily closes · 31,580 DB observations |
| Brass/metal ratio | ✅ **measured** 0.876 ± 0.039; anchors 0.977 (2019) / 0.910 (2023) / 0.897 (2026) |
| Two metal routes | ✅ LME×FX ₹987.77 vs MCX ₹983.65 — agree to **0.42%** |
| Predictive models | ⛔ **8 trained, all lost to naive**, DM −5.6 to −10.2 — **closed** |
| Buy/wait signal | ⛔ **built, tested, rejected** (−₹0.11/kg) — **withdrawn** |
| Fluid floor | ✅ `(brass + up + transport) × 1.05` = **₹950.40** same-day / ₹964.61 15d / ₹972.54 30d |
| Band width | ⚠️ one constant 25.8 proven **wrong in both directions**; regime buckets validated, **not implemented** |
| Backend | ✅ 12 modules, 14 endpoints, 8 tables, **47 tests passing** |
| Frontend | ✅ single HTML, 4 tabs, wired to the API, offline fallback |
| Deployed | ⛔ localhost only; no auth, no hosting, no scheduler |
| GitHub | ⛔ **20 commits local, never pushed** |
| **The one missing number** | ⛔ **one Castle invoice** (₹/kg, month, grade) |

---

## What has been proven — do not repeat these experiments

**1. Naive is very hard to beat.**
FX weekly: naive 0.2128 vs best Ridge 0.2930. Metal leg 4-week: naive ₹27.31 vs best 27.65, at all four alloy weights. Band is **asymmetric**: 80% −₹33.84 / **+₹60.71**.

**2. Driving on the 72 nodes makes prediction worse.**

| Feature family | MAE | vs naive 2.45 |
|---|---:|---:|
| naive | **2.45** | — |
| metal only | 5.54 | +126% |
| macro only | 9.22 | +276% |
| all 17 | 3.95 | +61% |

155 months of real domestic brass, 94 walk-forward forecasts, 8 fitted models. **All lost, DM −5.6 to −10.2.** More features = worse. Forecasting is **closed**; reopen only with genuinely new data.

**3. Only 6 of the 72 nodes are trainable** (M_CU, M_ZN, F1_INR, F1_EUR, F5_EN, D2_US). 57 have no data, 1 is too short, 8 are organising parents. **POL, CONV and WATCH are 0/n** — every Castle-specific node is untrainable, and `D2_US` is the wrong geography anyway.

**4. The buy/wait signal loses.** 1,592 weeks: −₹0.11/kg (−0.045%), 30.5% deferrals, −₹612/month. Withdrawn per the acceptance rule. **Cost of delay is small** (+0.24%/4wk) — the owner's weekly rhythm is rational; the risk is one-sided in the tail.

**5. The money is on the sell side.** Quoting at the band's middle carries an expected metal cost of **₹5.37/kg ≈ ₹29,558 per 5,500 kg order**.

**6. The band width is one constant and it is wrong.** Bucketed by trailing volatility, the 4-week p95 is +13.5 (calm) to +59.3 (high) — but we ship **+29.74 everywhere**: 2.2× too wide when calm, 2× too narrow when volatile (breached in **17% of high-vol weeks**). Linear quantile regression beats the constant on pinball loss (3.292 vs 4.153) in both sample halves — the first positive modelling result — but overshoots at extremes (+79.6 vs empirical +59.3). **Recommendation: regime buckets (floor ₹958/₹973/₹988/₹1,000), not a fitted line. Not yet implemented.**

---

## Owner facts — do not re-ask

- Brass is **bartan scrap + gittu scrap** from local traders. No brass ingot/rod grade named.
- **~70% of raw material is scrap**, melted in-house into cast.
- Buys **almost every week, hand-to-mouth, no bulk** — deliberately.
- **Cannot act on a same-morning warning**; needs **a month's projection**.
- Quotes are **valid same-day only** — so the risk is the **delivery window**, not the quote ageing.
- Price mechanism: **"LME governs most of it… MCX also governs… transportation is always extra."**
- **Europe and the Middle East** carry most orders.
- Volumes: brass **5–6 t/month**; aluminium ~10 t; iron ~10 t.
- **Still open:** transport ₹/tonne-km · one purchase invoice · which source markets · bartan/gittu Cu-Zn split.

---

## How to run it

```bash
start_local.bat                  # Windows: API :8000 + page :8080 + browser
./start_local.sh                 # WSL / Linux, Ctrl-C stops both
python -m pytest tests -q        # 47 tests
```

**Never open the HTML via `file://`** — it cannot call the API and silently drops to offline numbers. Serve it over `http://`. Full guide: `RUN_LOCAL.md`.
---

## Immediate next actions, in order

1. **Push the repo.** 20 commits are local; nothing is backed up. `git push -u origin main` (needs the user's GitHub login).
2. **Get one Castle invoice** — ₹/kg, month, grade. Halves the floor width (±₹38 → ±₹17/kg) and confirms 0.876 is Castle's number, not the market's.
3. **Implement the regime band** in `app/engine.py`, bump `MODEL_VERSION`, store the regime table, keep the constant as fallback, never extrapolate.
4. **Remove client/server duplication** — the verdict thresholds and the note text are computed in both `app/engine.py` / `app/notes.py` and in `Castle_Quote_Checker.html`. Make the client ask the API.
5. **Log quotes for four weeks**, then read `GET /report` — that produces the rupee proof.
6. Only then: auth, hosting, scheduler, WhatsApp.

**Do not** reopen forecasting. It is closed with 8 models and an ablation that shows the direction is worse, not better.

---

## Operating rules (non-negotiable)

- **No guessing.** Every figure traces to a retrieved source. Memory is a hypothesis.
- **Quarantine, never delete.** Failed claims stay visible in `output/quarantine.csv`.
- **Watchlist stays visible** — grey, never removed.
- **No model ships** unless it beats naive *and* survives the rupee-saved backtest. The buy signal did not; it was withdrawn.
- **Every stored output carries `model_version`.** A floor must be reproducible from stored rows.
- **Failures are surfaced, not hidden.** Feeds report `OK / STALE / BLOCKED / MANUAL / FAILED`. Nothing is ever filled in or guessed.
- **No paywall bypass.** MCX and WPI are manual because those sites block automation — that is recorded as fact, not worked around.
- **Owner-facing copy:** plain English, weekly wording only, no weekday names, no promise of a live website, no request for bills.
- **`.env` holds `FRED_API_KEY`.** Never print, commit or paste it.

---

## Environment traps that will waste your time

1. **The shell switches between WSL and Git Bash.** If `cd` fails, check `pwd` — the other path root applies.
2. **Two interpreters:** `python3` in WSL, `python` on Windows. Both have the dependencies.
3. **Headless Chrome differs:** WSL `/home/abuzar/chrome4testing/...`; Windows `"/c/Program Files/Google/Chrome/Application/chrome.exe" --headless=new`. Write screenshots to **relative** paths; Windows Python cannot read `/tmp`.
4. **The file-writing tool's cwd is the user's home, not the project.** Verify every file with `ls` after writing.
5. **Long heredocs get truncated** at ~4–6 KB. Write big files in chunks and check line counts.
6. **Never gate visibility on an opacity animation.** Under headless, and sometimes in real browsers, the animation does not run and the section stays invisible. Use transform-only, or `display`.
7. **Test click-through, not just unit tests.** `/report` returned HTTP 500 and the Data tab had no click handler at all — both while 47 unit tests were green.

---

## Do not

- Build a brass target from guessed spreads.
- Claim a model beats naive when it does not.
- Send any demo signal to the owner.
- Delete quarantine rows or hide watchlist nodes.
- Ask the owner for bills or documents.
- Say Monday/Friday in owner-facing copy; say weekly.
- Promise a live website or real-time prices.
- Paste the FRED key anywhere.
- Treat old counts (47/51/28 nodes) as current — the tree is **72**.
- Present illustrative story numbers (₹850/kg, ₹940 floor) as market data.
- Interpolate the monthly WPI index to weekly and call it weekly data.
- Use the WPI **old-base** index as a price level — it understates the market by 1.49×.
- Treat the ₹420/kg tier as Castle's price — that is household kabadi, not the board tier (₹810–1000).
- Buy a paid data seat before free + manual proves the gap.

---

## Reply style

Concise, direct, evidence-first. Report blockers early. If something is unknown, say **"unknown"** and state exactly what would resolve it. Distinguish **measured** from **assumed** from **chosen** — the user will ask, and conflating them destroys trust.
