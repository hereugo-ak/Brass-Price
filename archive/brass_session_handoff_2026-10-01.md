> **ARCHIVED — HISTORICAL DOCUMENT. DO NOT FOLLOW AS INSTRUCTIONS.**
>
> This is the original 2026-10-01 research brief, kept for history only. Several of its rules are
> now **wrong** for the project:
> - Section 1's "**Do not build any model**" is **obsolete**. The model phase began 2026-10-12.
>   The harness, baseline and tournament already exist and run.
> - Section 3's five questions were asked and largely answered — see `data/owner_answers.md`.
> - Section 7's "wait for go-ahead before HTML" checkpoint is long passed; the HTML was built
>   and verified.
> - The research here had not yet produced the final tree. It was later rebuilt to **72 nodes /
>   9 edges / 61 claim rows / 38 catalogue rows / 14 quarantined**, not the 47/28/22 quoted below.
>
> **Current authority:** `brass_session_handoff.md` (narrative) and `HANDOFF_PROMPT.md` (paste
> prompt), plus the machine files `output/tree.json`, `output/edges.json`, `output/claim_ledger.csv`,
> `output/quarantine.csv`. See the state appendix at the end of this file.

# Session handoff: brass price driver system for Castle Hardware

Paste this whole document into the new session as the first message.

## 1. Context

- Client: Castle Hardware, a hardware manufacturer.
- Problem: the price of brass, a key raw material, is highly volatile and hurts cost planning.
- End goal: a forecasting system for brass price. The order of work is (1) a verified, MECE driver map, (2) an interactive HTML node graph of it, (3) later, a machine learning model built on those drivers.
- This session covers steps 1 and 2 only. Do not build any model.
- An earlier, unverified draft split the drivers into five groups: Supply, Demand, Macro and finance, Policy and trade, Conversion and commercial. Treat this only as a hypothesis. Re-derive the structure independently. Keep, change or discard it based on evidence and the MECE tests below.

## 2. Non-negotiable rules

1. No guessing. Every node, definition, relationship and data claim must trace to a retrieved, citable source. Your own memory is a hypothesis to be checked, never a source.
2. Two independent verification rounds are mandatory (section 6).
3. MECE at every level of the tree (section 4).
4. Never fabricate a source, URL, figure, author or quote. If you cannot retrieve something, record "not retrievable" and move on.
5. Anything that fails verification goes to a quarantine list. It does not appear in the graph and it is not silently deleted.
6. Stay within the law and site terms. "Proprietary information" here means authoritative, industry-specific and primary data: exchange and statistical agency data, trade bodies, company filings, customs data, standards, academic and industry research, licensed datasets. Do not access confidential, leaked or paywall-bypassed material. If a valuable dataset is paid, list it with cost and access route and let me decide.
7. Do not build the HTML until I give the go-ahead after the checkpoint (section 7).

## 3. Questions to ask me before starting

Ask these in one message, then proceed with whatever I answer. Mark unanswered items as assumptions and list them.

- Which brass alloys and product forms does Castle buy (for example rod, strip, forgings, castings), and which grades?
- Where does Castle buy and sell (country and region), and in which currency?
- How are supplier contracts priced (formula, reference price, lag, fixed or floating)?
- Approximate volumes, and any existing hedging or inventory policy.
- Forecast horizon the business needs (weeks, months, quarters).

## 4. Structure requirements (MECE)

- Build a tree at least four levels deep. Go deeper wherever the evidence supports it.
- Every split must state its splitting criterion in one line (for example "by stage of the supply chain" or "by cost component"). Use one criterion per split.
- Each node needs a definition and an explicit inclusion and exclusion note.
- Mutually exclusive test: no factor may fit under two siblings. If it does, redefine the siblings or move the factor. Each node has exactly one parent in the tree.
- Collectively exhaustive test: for every parent, show that the children cover it completely. Verify this using an independent decomposition (for example a price identity or cost build-up) derived separately from the tree, and report any gap.
- Connections between nodes are NOT allowed to break the tree. They live in a separate edge layer (section 5).

## 5. Cross-links between nodes

Many factors influence each other across different branches and levels. Capture this separately from the tree.

Edge record fields:
- source node, target node
- type: causal, substitution, common driver, feedback loop, correlation only
- direction and sign (positive, negative, ambiguous), with the mechanism in one sentence
- typical lag, if documented
- evidence: sources and a strength note (mechanism documented vs statistical only)
- scope: same-level (parallel) or cross-level
- verification status

An edge enters the graph only if a source supports the relationship itself, not just each node separately. Flag feedback loops explicitly. Do not infer plausible links without evidence; send them to quarantine.

## 6. Multi-agent research and verification plan

Research phase (minimum 30 to 40 minutes of real working time):
- Spawn multiple agents in parallel, at least one per top-level branch plus agents for: cross-link discovery, data availability, and brass-specific market structure (how brass is actually priced and traded).
- Log start and end timestamps. Do not stop early. If the minimum time is reached but coverage is thin, keep going and tell me.
- Each agent writes to a shared claim ledger: claim, source title, publisher, URL, date published, date retrieved, source tier (primary, official statistics, industry body, peer-reviewed, reputable press, other).
- Prefer primary and official sources. Every node needs at least two independent sources where possible.

Verification round 1:
- New agents who did not write the claims check each ledger entry. Confirm the source was actually opened and truly says what is claimed. Check dates and units.
- Test MECE per level. Test each edge.

Verification round 2:
- A second, different set of agents, who have not seen round 1 conclusions, re-verify independently using different sources where possible. Add an adversarial pass: try to find counter-evidence and missing branches.
- Reconcile every disagreement between rounds with evidence.

Status labels: Verified (both rounds), Disputed (rounds disagree, shown with reasons), Unverified (quarantined).

## 7. Checkpoint (stop here and wait for me)

When research and both verification rounds are done, report back with:
- run time and agents used
- structure outline (levels and node counts), MECE test results, and gaps
- counts of verified, disputed and quarantined nodes and edges
- data availability summary for ML (section 9)
- open questions and assumptions

Then wait for my explicit instruction before building the HTML.

## 8. HTML deliverable (after my go-ahead)

One self-contained HTML file, usable on a phone and a laptop, data stored as a JSON block separate from the rendering code.

- Interactive node graph showing the hierarchy: expand and collapse, expand all, collapse all, pan and zoom, search.
- Cross-link layer OFF by default. A master toggle turns all cross-links on and off. Separate toggles per edge type and for same-level vs cross-level links.
- Selecting a node highlights its parent chain, children and linked nodes, and opens a detail panel: definition, inclusion and exclusion, sources with dates, verification status, data availability, and its connections with sign and lag.
- Visual distinction for edge types and signs, feedback loops marked clearly, and a legend.
- Show verification status as a badge. Disputed items visible with reasons. Quarantined items are not shown in the graph (listed in the files below).
- Export of the tree and edges as JSON.

## 9. ML-readiness catalogue (research only, no modelling)

For each leaf node record only verified facts: candidate variable, unit, frequency, public or paid source, history length, licensing, publication lag, and known data quality issues. Mark gaps clearly. This feeds the next stage, where we will design the machine learning model.

## 10. Files to produce

- tree.json, edges.json
- claim_ledger.csv with sources
- verification_round1 and verification_round2 logs
- quarantine list with reasons
- data_catalogue.csv
- README with method, run time, assumptions
- the HTML graph, only after my go-ahead

## 11. Working style

Be concise in status updates. Report problems early (blocked sources, paywalls, conflicts). Never present an unverified item as fact.

---

## Appendix — project state as of 2026-11-12 (added retroactively; not part of the original brief)

Recorded so this archive cannot mislead a future session. The original text above is left untouched.

### Where the project actually stands
- **Research:** closed. 72 nodes (26 Verified / 31 Disputed / 15 watchlist), 9 edges (4 Verified / 5 Disputed), 61 claim rows, 38 dataset rows, 14 quarantined.
- **Deliverables:** `Brass_Story.html`, `brass_graph.html`, `Castle_Discovery_Questions.html`, `DTPS_Dossier.html`, `PRD.md/.docx`, `Executive_Summary.docx` — all built and verified.
- **Data spine:** 7 FRED series backfilled; 2,789 weekly feature rows (1973-01-05 → 2026-11-06, 31 columns).
- **Model:** naive bar 1-week MAE ₹0.2128 / 4-week ₹0.4625. Best Ridge loses (0.2930 / 0.5131); Diebold–Mariano favours naive. Honest finding, not a bug.
- **Decision engine:** demo only, not advice, must not reach the owner.

### What the original brief got wrong or left open
- "Do not build any model" (section 1) — superseded 2026-10-12. The model phase is active.
- The five-question list (section 3) was asked; **6 of 8 answers** arrived 2026-11-12, verbatim in `data/owner_answers.md`.
- The HTML go-ahead gate (section 7) is passed.
- The 47-node / 28-ledger / 22-catalogue counts here are historical. Current: 72 / 61 / 38.

### Owner facts established 2026-11-12
- Brass is **scrap-based**: bartan scrap and gittu scrap from local traders; **~70% of raw material is scrap**, melted in-house. No brass ingot/rod grade was named.
- Buying is **almost weekly, hand-to-mouth, no bulk**.
- Founder needs a **~1-month forward projection**; he cannot act same-day.
- Most orders: **Europe and the Middle East**.
- Price mechanism: **LME leads, MCX is the Indian reference, transport is always extra.**
- Volumes: brass ~5–6 t/month; aluminium ~10 t/month; iron ~10 t/month.
- **Still missing:** premium over benchmark, transport ₹/kg, conversion, scrap discount, quote-validity days by market, and any brass price history.

### Blockers
- **MCX:** no usable data. `mcxindia.com` 403s all automated requests (3/3 endpoints, 2026-11-12). The stored bhavcopy is an HTML frameset shell with no prices; `data/check_mcx.py` fails closed on it.
- **Manual series:** essentially empty. `manual/mandi_quotes.csv` has 0 rows — the highest-value gap.
- **Owner numbers:** only behind `output/FOLLOWUP_TO_FOUNDER.md` (draft, not sent).

---

*End of archive. For current instructions use `HANDOFF_PROMPT.md`.*
