> **HISTORICAL TIMELINE — NOT CURRENT STATE.** Sections 1–3 are the 2026-10-01 checkpoint and
> their counts (47 nodes / 28 ledger / 22 catalogue) are stale. For what is true *now*, use
> `../brass_session_handoff.md`, `../HANDOFF_PROMPT.md` and the machine files in `output/` and
> `data/`. Use this file for "what happened", never for "what is true".

# Checkpoint — STOP, wait for go-ahead before HTML (handoff section 7)
Date: 2026-10-01. Run time: start 2026-10-01T18:10:48Z (end stamped in section 7; 30-40 min minimum required). Files validated: tree 47 nodes depth 4, edges 9, ledger 28 rows, catalogue 22 rows, quarantine 14 rows.

## 1. Run time and agents used
8 research (supply, demand, macro, policy, conversion, market-structure, cross-links, data) + 6 verification (R1 x3, R2 x3 different + adversarial). Logs: verification_round1.md / verification_round2.md.

## 2. Structure outline
47 nodes, 5 deep (max depth 4), with splitting criterion stated per parent in tree.json. Splitting criterion stated per parent in tree.json. CE check: P_INR identity (no LME brass leg). MECE: naive trees failed both rounds (triple-counts, geography x mechanism x time mixing, rates/FX/COT overlap); fixed with tonne-once / rupee-once / time-as-feature / positioning-overlay rules + inclusion/exclusion per node + edge-only cross-links. Remaining overlaps kept as Disputed with interaction notes.

## 3. Counts (validated)
Nodes 47: Verified 24 / Disputed 23 / Quarantined 14 rows (excluded). Edges in graph 9: Verified 4 (TC->cuts; tariff->spread diversion; Cu/Al substitution; FX->INR identity) + Disputed 5 (USD->Cu directional; price->scrap feedback; China PMI directional; rates->demand; freight pass-through). Quarantined edges (quantified betas without joint evidence) in quarantine.csv.
Top VERIFIED: LME 25t/no-brass; IS319 ranges; Sterlite-date 28-May-2018; Kutch 28-Mar-2024 Phase-1; TC $0/t 2026; US 232 content-only + exclusions; CBAM 1-Jan-2026 brass-out; Fed 3.75-4% + ECB 2.50% 16-Sep-2026; CPI +3.4%; CFTC Tue/Fri; CDA/USGS vintage ranges; C260 70/30.
Top DISPUTED (rounds disagree, reasons in tree/ledger): ICSG kt; India >90% import; HZL split; ICA 1878kt; CSEP 3.24Mt (R2-only); Jamnagar shares; MCX-live; billet ratio; lag; BCD/RoDTEP-vintage/QCO-active/EPR/safeguard/US-India-18% (R2-primary vs R1-quarantine - strict Disputed); USD-beta/energy-Zn/scrap-elasticity magnitudes.
Gaps: MCX continuous brass; Indian honey-scrap series; ocean-freight legs (WCI URL); paid premia seat; ICSG/ILZSG/WBMS/IBM tables; SHFE history; BIS current QCO list; DGFT line-level RoDTEP; EUR-Lex vs EC-news tie-breaks already pulled for steel - reuse pattern.

## 4. Data availability for ML (summary)
Weekly layer READY (free): LME cash/3M (XML/free-delayed) + RBI/FBIL + FRED/ECB FX + EIA fuels + PPAC basket/RSP + PMI headlines + diesel-as-freight proxy. Long-term READY: IMF monthly Cu/Zn/Brent/gas + World Bank FX annual + LME stocks/COTR trends. GAPS (paid/subscribe): 1 paid premia/scrap seat (Fastmarkets/Platts/CRU/WoodMac - costs not retrievable free); MCX brass continuous (verify listing); BigMint scrap; Drewry/Freightos/Baltic legs (re-verify URLs); ICSG/ILZSG/WBMS detail. See data_catalogue.csv (22 rows).

## 5. Open questions and assumptions
A1-A5 in README. Cluster shares, dealer premia, carry rates: no citable source - estimate from mandi spread post-go-ahead, do NOT hard-code. Alloy weights per SKU (62/38 vs 60/40 vs 70/30) must be inputs, not constants.

## 6. Reconciliation statement
Every R1 vs R2 disagreement reconciled with evidence (see tree status_notes + ledger status_note). Rule applied strictly: Verified only if both rounds agree (or R1 + different-R2 agent agree on TC/US-232); else Disputed with reasons; numbers without second-round fetch quarantined even if plausible. No unverified item presented as fact.

AWAITING explicit instruction before building HTML (handoff rule 7).

## 7. Late fixes (reported per working-style rule)
- Edge source F_FX_USD -> F1 (unknown endpoint caught by validation, fixed 18:35Z, re-validated 0 bad endpoints).
- Direct tie-breakers (lead, ~18:34-18:37Z): FRED DEXINUS 95.81 (25-Sep-2026 H.10); RBI archive+Excel live (upd Oct 01 2026); Fed FOMC 16-Sep-2026 hike to 3.75-4% 12-0; ECB eurofxref USD table Sep-2026 (~1.135-1.165); WH copper proclamation full text (50% eff 1-Aug-2025, content-only, CBP penalties, no drawback, 90-day inclusion, refined review by 30-Jun-2026, DPA sales, UK coordination); EC CBAM definitive 1-Jan-2026 + 6 sectors. LME + MCX direct 403 bot-block noted (not counter-evidence).
- End: stamped at 30-min mark below. No HTML built (awaiting go-ahead).
- End: 2026-10-01T18:40:49Z (~30 min wall from 18:10:48Z; 14 subagents + lead tie-breakers; minimum met).

## 8. Post-checkpoint expansion (2026-10-02, user-requested)
- 4 drivers added (51 nodes): UK CBAM 2027 P4_UK (Verified: R2-flag + GOV.UK), Ocean freight WCI C4_FRT (Disputed, Drewry), Energy & fuel F5_EN (Verified: data-agent + R1), Spreads & premiums M_SPR (Disputed, paid levels noted).
- Ledger 28->35 rows (HOUST/TTLCONS FRED direct; WCI; UK CBAM; energy; COMEX-LME spread CNBC/ING; SHFE weekly), data catalogue 22->31 rows (HOUST/TTLCONS/WCI/CBAM-price/TC-RC/SHFE/USGS/rates/CPI). New nodes single-round = Disputed except P4_UK/F5_EN (two-round).
- Full source coverage enforced: builder asserts every node has >=1 claim (headless selftest noSourceNodes:[]).
- HTML rebuilt as Brass/brass_graph.html; verified via headless Chromium: zero JS errors, selftest ok (51/9 resolve, links render, search+detail pass), desktop+mobile screenshots reviewed.

## 9. India-rebalance + watchlist expansion (2026-10-02, user challenge)
- Source audit on 35 rows: GLOBAL/exchange 14, INDIA 11, USA 9, other 1. US tilt confined to FX/macro (LME trades in USD; FRED/BLS/Fed) — conceded gap was export legs: ME 0 nodes, AU 0 nodes, EU thin.
- Added (verified where fetched): P_ME (UAE CEPA May-2022), P_AU (ECTA 100% from 1-Jan-2026, DFAT+PIB), P_UKFTA (CETA live 15-Jul-2026, 99% IN goods duty-free, GOV.UK), P4_PB (EU DWD lead 5ug/L by 2036 + 31/12/2026 conformity), D2_ME (OPEC MOMR), D2_AU (ABS approvals + RBA 4.60%), GST-18% row (commercial, CBIC check noted).
- Watchlist branch (15 nodes, grey Unverified): all 14 previously excluded/quarantined hypotheses restored visible, each with evidence-needed note. Nothing hidden anymore.
- Click bug fixed (pointer capture ate node clicks); deep links ?select=&links=&search=; selftest ok in headless Chromium (72 nodes, 15 watch).

## 10. Phase-1b owner-independent build (2026-10-12)
- decide.py: decision-engine DEMO on public legs (1800 weekly signals, 30% buy rate, labeled demo; real message needs brass target + spreads).
- kaggle_baseline.ipynb: validated notebook scaffold (CPU-sufficient, GPU optional).
- Cron job registered (daily 08:00 collect_daily.py) BUT daemon won't start in this WSL without privileges — run `sudo service cron start` once, or use Windows Task Scheduler, or run manually.
- LME direct fetch still bot-blocked; MCX manual-only. Both recorded, not worked around.

## 11. Refresh + data correction (2026-11-11)
- Re-ran backfill_fred.py: full history now DEXINUS 13,497 rows (to 2026-11-06), DEXUSEU 6,984, IMF Cu/Zn 417 each (to 2026-09-01), Brent 9,122, HOUST 813, TTLCONS 405.
- features_weekly.csv rebuilt: 2,789 Friday rows (1973-01-05..2026-11-06), 31 columns.
- Baseline refreshed: h1 naive MAE 0.2128 (n 2,728), h4 naive MAE 0.4625 (n 2,725). Ridge still loses: best h1 0.2930, h4 0.5131 (DM favours naive).
- CFTC collector bug found and fixed: deafut.txt fixed-width offsets were misread (OI/date/positions shifted). Replaced with Socrata API 6dca-aqww named fields. Bad row removed; latest verified report 2026-11-03 (OI 327,850; NC_L 85,660; NC_S 47,950; spread 99,560; C_L 126,082; C_S 168,005).
- One-month drift explained: cron daemon never started in this WSL. Raw ECB/CFTC logs have a gap Oct 11..Nov 11; FRED history backfilled so features are current. ECB/CFTC are not yet model features.
- Full current handoff: ../brass_session_handoff.md.

## 12. Owner answers received + MCX reality check (2026-11-12)

### 12.1 Founder answered 6 of 8 questions (verbatim in `data/owner_answers.md`)
Recorded unparaphrased, dated 2026-11-12. This is the first owner data in the project's life.

- **Q1 suppliers:** brass from local traders/vendors; aluminium scrap local; Al extrusions/sheet Hindalco, Alum and MM Metacraft; iron sheet from local Tata/Jindal vendors; SS from Mumbai.
- **Q2 items/grades:** scrap, ingots, rods, extrusions, tubes, sheet, many sizes — Al 6063, Al ADC12, SS304, Tata CR/HR, SS202, **Brass bartan scrap, Gittu scrap**. No brass ingot/rod grade named.
- **Q3 rhythm:** buys **almost weekly as required, no bulk**, because of price and availability uncertainty.
- **Q4 reaction:** cannot act on a same-day warning — must call the vendor for the actual price. Needs **at least a 1-month projection** to plan delivery.
- **Q5 markets (partial):** **Europe and Middle East** have most orders. Quote-validity days **not answered**.
- **Q6 price formula (partial):** follow-up — "**LME governs most of it but in India we have MCX** which is metal trading which also governs the price, **plus the transportation is always extra**." No numbers given.
- **Q7 scrap:** melted into cast then finished; **~70% of raw material share**.
- **Q8 volumes:** brass **~5–6 t/month**, aluminium **~10 t/month**, iron **~10 t/month**.

**Consequences recorded:** the model target is the **domestic brass scrap price in ₹/kg**, not an exchange brass number. Horizon is **~4 weeks**, not 1. Currency legs shift toward EUR + AED. The identity gained an explicit **transport** line. Q6 numbers and Q5 validity days remain the gating unknowns.

### 12.2 MCX re-capture attempted and blocked
- Re-probed `mcxindia.com` on three endpoints (home, `/market-data/bhavcopy`, `/backpage.aspx/GetDateWiseBhavCopy`) with a normal browser UA: **403 on all three**. Consistent with the 2026-10-11 note; no automated route without circumventing the block, which was not attempted.
- **The previously "captured" bhavcopy is not data.** `data/mcx_manual/BhavCopyDateWise_09102026.xls` is an HTML frameset shell referencing a missing `sheet001.htm`. It has a plausible `.xls` name and 9,991 bytes, and holds zero prices. Root cause: browser "save page" on MCX's frameset page.
- **Guard added:** `data/check_mcx.py` fails closed on a bhavcopy with no price table. Current result: `FAIL` on the 2026-10-09 file, as expected. `MANUAL_GUIDE.md` documents the trap and the check next to the MCX row.
- **No MCX feature was added.** Building one from a proven-empty file would have created a permanently blank column.

### 12.3 Collector run and duplicate-row note
- `collect_daily.py` on 2026-11-12: **collected=8 missed=2**. Misses are ECB (URLError, network) and MCX (403) — both expected and recorded.
- The known no-same-day-de-dupe behaviour reproduced: `fred_inr_per_usd.csv` now carries two rows for obs 2026-11-06, `cftc_copper_cmx.csv` two for 2026-11-03. Raw logs left append-only per the integrity rule; downstream must de-dupe on `(obs_date, series)`. Features unaffected — they are built from `data/history/`.
- Pipeline re-verified after the run: 2,789 weekly rows (1973-01-05 → 2026-11-06, 31 cols), baseline unchanged (naive 0.2128 / 0.4625).

### 12.4 New files this session
- `output/FOLLOWUP_TO_FOUNDER.md` — draft owner message, 4 asks: one costed purchase (scrap ₹/kg + transport), the transport rate, quote-validity days for Europe and the Middle East, and a **weekly brass price note**. Checked: no weekday names, no website/live-price promise, no request for bills or documents.
- `output/NEXT_STEPS.md` — the live action list, human-side and agent-side.
- `data/check_mcx.py` — the frameset guard described above.

### 12.5 What is now the single blocker
Everything Castle-specific waits on the founder's reply: the **numbers** (premium, transport ₹/kg, conversion, scrap discount), the **quote-validity days**, and ideally **8–12 weeks of actual brass scrap prices**. Research, deliverables and the public data spine are done. No further analyst work can substitute for those numbers, and none will be invented.
