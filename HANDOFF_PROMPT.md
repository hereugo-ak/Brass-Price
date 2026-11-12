# Copy-paste handoff prompt

Paste the block below as the first message in a new session.

---

You are continuing the **Brass Price Foresight** project for **Castle Hardwares, Aligarh** — a brass architectural-hardware exporter exposed to weekly brass price moves while its export quotes stay fixed for roughly 30 days. The same work is the user's MBA Design Thinking & Problem Solving (DTPS) live project.

**Working directory:** `/mnt/c/Users/Abuza/OneDrive/Documents/Brass` (Windows: `C:\Users\Abuza\OneDrive\Documents\Brass`). `/home/abuzar/Brass` is a wrong-path trap that has already caused one misfiled file.

**Read these first, in this order, before doing anything:**
1. `brass_session_handoff.md` — the full current handoff (authoritative narrative)
2. `output/NEXT_STEPS.md` — the live action list, human-side and agent-side
3. `output/tree.json`, `output/edges.json`, `output/quarantine.csv` — authoritative driver map
4. `data/owner_answers.md` — the founder's verbatim answers (2026-11-12) **and** what is still missing
5. `data/baseline_metrics.json`, `data/tournament_dexinus.json`, `data/decisions_demo.json` — current model reality
6. `data/MANUAL_GUIDE.md` — the collection routine

**Core insight, do not re-litigate:** there is no brass futures contract (LME/MCX/COMEX verified). Brass price is reconstructed as an identity:

```
wCu·LME_Cu·FX + wZn·LME_Zn·FX + premium − scrap + conversion + margin + transport + net duties
```

The **transport line is owner-confirmed** (2026-11-12: "the transportation is always extra"). Model the three moving legs first, add slow spreads second, output low/middle/high bands — never a single-point prediction.

**Owner intelligence (2026-11-12, verbatim in `data/owner_answers.md`) — treat as established fact, do not re-ask:**
- Brass is bought as **bartan scrap and gittu scrap** from local traders. No brass ingot/rod grade was named. Do not assume C360/CW614N for this client.
- **Scrap is ~70% of raw material**, melted in-house into cast then finished. So the price to model is the **domestic brass scrap buying price in ₹/kg**, not an exchange brass number.
- Buying is **almost weekly, hand-to-mouth, no bulk** — explicitly because of price and availability uncertainty.
- The founder **cannot act same-day** ("you cannot expect one sudden morning that price is going to go high today"). He needs a **~1-month forward projection** to plan delivery.
- Most orders come from **Europe and the Middle East**. US/Australia unmentioned.
- Price mechanism: **LME governs most of it, MCX in India also governs the price, transport is always extra.**
- Volumes: brass **~5–6 t/month**, aluminium ~10 t/month, iron ~10 t/month.
- **Still missing:** the actual numbers — premium over benchmark, transport ₹/kg, conversion, scrap discount, and **quote-validity days by market**. Q6 and Q5 are only partly answered.

**Current state (as of 2026-11-12):**
- Research done and closed: 72 nodes (26 Verified / 31 Disputed / 15 visible watchlist), 9 edges (4 Verified / 5 Disputed), 61 claim rows, 38 dataset rows, 14 quarantined claims. Do not re-research.
- Owner deliverables done: `Brass_Story.html`, `brass_graph.html`, `Castle_Discovery_Questions.html`, `DTPS_Dossier.html`, `PRD.md/.docx`, `Executive_Summary.docx`. Owner-facing copy was re-scoped on 2026-11-12 to the founder's answers: Europe + Middle East markets, scrap-led economics (bartan/gittu, ~70% scrap), delivered + transport basis, and a "what you told us" answers band in the story and the dossier. Weekday names were purged from all owner-facing copy (weekly wording only).
- Data spine live: 7 FRED series backfilled (DEXINUS through 2026-11-06), 2,789 weekly feature rows (1973-01-05 → 2026-11-06, 31 columns), ECB + CFTC snapshots.
- Model bar: naive 1-week MAE ₹0.2128, 4-week ₹0.4625. Best Ridge loses (0.2930 / 0.5131); Diebold–Mariano favours naive. This is the honest finding, not a bug.
- Decision engine is **demo only**; it is not advice and must not be sent to the owner.
- **MCX is blocked and has no usable data.** `mcxindia.com` returns HTTP 403 on every endpoint (home, Market Data, bhavcopy) to automated requests — re-verified 2026-11-12, 3/3. Manual browser only; do not attempt to circumvent. The stored file `data/mcx_manual/BhavCopyDateWise_09102026.xls` is an **HTML frameset shell** pointing to a missing `sheet001.htm` — it contains **no prices**. `data/check_mcx.py` fails closed on it; run that check before MCX is ever counted as captured.
- Manual series are **almost entirely empty**: only one LME day captured. `manual/mandi_quotes.csv` has 0 rows — the highest-value missing series.
- `output/FOLLOWUP_TO_FOUNDER.md` is a **draft, not sent**. It asks for one costed purchase, the transport rate, quote-validity days, and a weekly brass price note.

**Non-negotiable rules:**
- No guessing. Every claim, URL and figure traces to a retrieved source; memory is a hypothesis.
- Verified only when two independent rounds agree; otherwise Disputed or quarantined. Quarantine is visible, never deleted. Watchlist nodes stay visible in grey.
- Never fabricate a source or number. If it cannot be retrieved, say so.
- Paid data is listed, not bypassed. No paywall circumvention — MCX's 403 is recorded, not worked around.
- No model ships unless it beats the naive bar and survives the rupee-saved backtest.
- **No brass target from assumed spreads.** Not until real prices exist.
- Owner-facing copy: plain English, premium bespoke design, no template/AI-slop feel, weekly wording only (no Monday/Friday), no promise of a live website, no request for bills or documents.
- `.env` contains the FRED key. Never print, commit or paste it.

**Immediate next actions, in order:**
1. Run the pipeline once to confirm the environment: `cd data && python3 backfill_fred.py && python3 collect_daily.py && python3 make_features.py && python3 baseline.py`. Expect ~2,789 weekly rows and collector misses only on ECB (network) and MCX (403).
2. Read `output/NEXT_STEPS.md` and confirm which human actions are still outstanding (send founder message, one MCX bhavcopy, first mandi quote).
3. Owner-independent work remaining: backfill the ECB/CFTC month gap (Oct 11 → Nov 11), add HCL MIC y/y + IBM ASP + HS 74032100 duty events as features, rerun the tournament. Do **not** add an MCX feature until a real bhavcopy passes `check_mcx.py`.
4. Check `data/manual/` for new rows; validate units and dates before use. One mandi quote per week is the whole ballgame.
5. If the founder has replied, record it **verbatim with the date** in `data/owner_answers.md`, then derive spread parameters — each sourced to his message and date.
6. Log every new claim in `output/claim_ledger.csv`, every new dataset in `output/data_catalogue.csv`, and update `brass_session_handoff.md` before ending the session.

**Do not:** redo completed research; re-ask the founder questions he has already answered; build a brass target from guessed spreads; add MCX to the features from the known-bad file; trust old markdown counts (47/51/28); hand-edit `brass_graph.html` without a count/render check; treat illustrative story numbers as market data; or send the demo signal to the owner.

**Reply style:** concise, direct, evidence-first. Report blockers early. If something is unknown, say "unknown" and state exactly what would resolve it.
