# Brass driver map — README (Castle Hardware)
Date: 2026-10-01. Session: Brass (C:\Users\Abuza\OneDrive\Documents\Brass).

> **Historical document.** Counts below (47 nodes, 28 ledger rows, 22 catalogue rows) describe the 2026-10-01 checkpoint, not the current system. Current authoritative counts: 72 nodes (26 Verified / 31 Disputed / 15 Unverified), 9 edges, 61 claim rows, 38 catalogue rows, 14 quarantined. See `../brass_session_handoff.md` and `tree.json`.

## 1. What was done (handoff steps 1 only, no model, no HTML yet)
- Asked 5 intake questions in one message (tool). Answers used:
  - Alloys: unknown → assume typical hardware brass (free-cutting rod CW614N/C36000 ~60-63% Cu + Pb, forging CW617N, cartridge C260 70/30, Muntz 60/40) — grades to lock via CoA/EN 12164/12165 + BIS IS 319 before modelling. IS 319:2007 Gr-I/II ranges VERIFIED via BIS text.
  - Geography: buy raw India (INR), export finished US/EU (USD/EUR). FX legs: USD/INR (RBI/FBIL + FRED DEXINUS), EUR/USD (ECB/FRED).
  - Contracts: spot/mixed → weekly buy-timing exposure 100%, no hedge.
  - Hedging: none → full variance passes through.
  - Horizon: weekly + long-term → dual-layer features (weekly lags + monthly regimes).
- Research phase: 8 parallel agents (Supply, Demand, Macro/Finance, Policy/Trade, Conversion/Commercial, Market-structure, Cross-links, Data-availability). Start 2026-10-01T18:10:48Z.
- Verification R1: 3 independent checkers (supply+structure / demand+macro / policy+edges+data). R2: 3 different checkers, different sources where possible + adversarial counter-evidence hunt.
- Reconciliation: disagreements resolved with evidence below; statuses Verified (both rounds agree), Disputed (rounds disagree, shown with reasons), Unverified-quarantined (excluded from graph).

## 2. Run time and agents
- Start: 2026-10-01T18:10:48Z. Research complete ~18:16Z. R1 complete ~18:22Z. R2 complete ~18:28Z. Synthesis + validation + tie-breakers to 30-min mark (end stamped in checkpoint_summary).
- Agents: 8 research + 6 verification = 14 subagent runs. Start 2026-10-01T18:10:48Z, files validated ~18:35Z (depth 4 met).

## 3. Structure (MECE)
- Root: Castle INR delivered brass cost + export margin.
- L1 split criterion: disjoint causal stage (benchmarks | currency translation | upstream tonnes | India spreads | policy wedges | demand pull | expectations). Implemented as 5 branches per hypothesis, redefined to be disjoint (see tree.json split_criterion per parent).
- Price identity (independent CE check, market-structure agent): P_INR = wCu*LME_Cu*FX + wZn*LME_Zn*FX + premium - scrap_discount + conversion + margin + net_duties. No LME brass contract (VERIFIED: LME list + 25t Cu spec); MCX brass launched 2018 1t (VERIFIED historical) but absent from 2026 product list (DISPUTED as live hedge). Brass has no exogenous future leg → model as identity, not root node.
- Levels: 5 deep (root-L1-L2-L3-L4, max depth 4 verified). Node counts: 47 total (24 Verified, 23 Disputed; quarantined 14 excluded from graph). All have definition + inclusion/exclusion + single parent. Cross-effects live ONLY in edges.json.
- MECE tests: R1+R2 both found naive trees NOT MECE (TC vs refined vs imports triple-count; scrap vs secondary; stocks level vs shocks; geography×mechanism×time mixing; rates/FX/COT overlap). Fixed by: tonnes counted once (conc vs refined vs scrap vs stock), rupees once (metal vs spread vs tax), time as feature not branch, positioning as overlay. Remaining overlaps documented as Disputed nodes with interaction notes (US 232 content vs reciprocal non-content; CBAM vs steel safeguard on steel-containing goods; RoDTEP vintage).

## 4. Counts (validated)
- Nodes: 47 total — Verified 24 / Disputed 23 / Quarantined 14 rows (excluded from graph, in quarantine.csv). Edges in graph: 9 (Verified 4 + Disputed 5). Ledger: claim_ledger.csv 28 rows. Catalogue: data_catalogue.csv 22 rows.
- See checkpoint_summary.md for full tables.

## 5. Assumptions (unanswered intake)
A1 alloys per above; A2 INR buy + USD/EUR sell; A3 spot/mixed = LME+FX pass-through with 1-2wk stickiness (DISPUTED single trade source, model as lag to estimate); A4 no hedge; A5 weekly lags 1-8W + monthly regimes. Cluster: Jamnagar industrial rod/parts vs Moradabad decor — shares DISPUTED (denominators conflict), keep as flag not factor.

## 6. Key corrections from verification
- Hindu BusinessLine 2018 "60% zinc" inverted — do NOT cite for composition; use BIS/ASTM.
- "No MCX brass ever" false — launched 2018, now illiquid/absent. Time-qualify.
- Jamnagar "80% sold in India" (2018) vs "80% of exports" (2026) different denominators — do not conflate.
- C360 nominal 61.5% is midpoint, spec is 60-63% Cu + 2.5-3.7% Pb — use ranges.
- ICSG kt balances, HZL splits, ICA 1878kt, rod $9511, Rs14-18/kg, billet 62.5-63.5% — single-source or stale → Disputed/Quarantined, not modelling facts.
- LME COTR + PPAC deep URLs as cited 404 — replaced in data_catalogue.
- QCO 2023 withdrawn Nov-2025; 2024 status ambiguous — check current BIS list before use. RoDTEP must be vintage-stamped (Feb-2026 cut + Mar-2026 restore). US 232 vs IEEPA 18% do not stack — interact with copper-weight share.

## 7. Files
tree.json, edges.json, claim_ledger.csv, data_catalogue.csv, quarantine.csv, verification_round1.md, verification_round2.md, checkpoint_summary.md, README.md (this file). HTML only after go-ahead.
