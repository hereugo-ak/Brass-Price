# Brass Guard — product design and DTPS mapping

**Client:** Castle Hardwares, Aligarh · **Course:** DTPS (MBA-506), AMU · **Date:** 2026-11-12
**Built artefact:** `Castle_Quote_Checker.html` — a working, single-file product (no login, no server, works offline on a phone)

---

## 1. The pain, in the owner's own words

> *"We almost buy every week as per our requirement… we don't buy in bulk now because of the
> uncertainty in price and availability."*

> *"Even if you tell me in morning price may climb we will have to contact our vendor to exactly
> know what price are they giving… we need at least a projection for a month to plan for delivery."*

> *"LME governs most of it but in India we have MCX which is metal trading which also governs the
> price, plus the transportation is always extra."*

The pain is **not** "we cannot predict brass." It is:

> **We commit to a price for weeks, and we buy metal later. When metal moves in between, the loss
> lands on us, and we have no way to know how much cushion a quote needs.**

---

## 2. Stated need vs latent need

This distinction drove every product decision.

| | Stated (what he said) | Latent (what he actually needs) | Product consequence |
|---|---|---|---|
| 1 | "A projection for a month" | A **range** he can quote against, not a forecast — a single number would be false precision and he knows it | Ship a low/middle/high **band**, never a point |
| 2 | "Tell me if prices may climb" | He **cannot act same-day** — the warning is useless as an alert. It is only useful as a *cushion decision made days earlier* | The output is a **floor to quote against**, delivered at the start of the week, not a trigger to buy |
| 3 | "LME + MCX + transport" | He needs the **brass scrap** number, not the copper number — 70% of his material is scrap, melted in-house | Model brass directly via the **measured ratio**, not LME copper |
| 4 | (not stated) | He is **not technical** and will not learn software | **Zero-install, zero-login, one screen, one number in** |
| 5 | "We don't buy in bulk" | He does not want a buying strategy — he wants to stop **losing on quotes** | The money is on the **sell** side; the backtest proved it |
| 6 | (not stated) | He is **time-poor and family-run**; anything needing daily input will be abandoned | **He does no data entry.** The system collects publicly |
| 7 | (not stated) | He trusts **his trader, not a website** | We never ask him to switch supplier or trade |

**The single most important latent need:** he said "a projection for a month." What he actually
described was *"I need to know how much room to leave in a quote."* Those are different products.

---

## 3. Did we build around the stated problem? — an honest audit

| Stated problem | Did we address it? | Evidence |
|---|---|---|
| Brass price is volatile | ✅ | Measured: 4-week change sd ₹14/kg, p95 +₹25.8/kg |
| Quotes are fixed for weeks | ✅ | Validity model at 30 / 15 / 7 days |
| No forward view | ✅ | Band in ₹/kg: **₹843 / ₹882 / ₹920**, floor **₹966** |
| Cannot act same-day | ✅ | Output is a weekly cushion, not a daily alarm |
| No hedging available | ✅ | Confirmed: no brass futures; MCX 2019 contract had **zero volume** |

**Where we initially went wrong — and corrected:**

We first built a **buy/wait signal**. It was tested on 1,592 weeks and **lost ₹0.11/kg against
buying every week**. We withdrew it. The founder never asked for a buying strategy; he asked for a
month's projection to plan delivery. We had over-indexed on prediction because prediction is the
interesting problem, not the valuable one.

**Corrected emphasis:** the product is a **quote guard**, not a crystal ball. That is what the
evidence supports, and it is what the money is made of — quoting at the band's middle carries an
expected metal cost of about **₹29,500 per 5,500 kg order**.

This correction is the strongest part of the submission: the prototype was tested, failed on its
own criteria, and was iterated. That is Unit V.

---

## 4. The product

**Brass Guard** — one page, one number in, one verdict out.

```
Owner types the price he is about to quote   →   gets PASS / THIN / RISKY / STOP
                                                  plus the minimum safe price
```

Nothing else. No login. No install. Works on a phone, offline, from a shared link or a saved file.

**What it is built from:**
```
price = metal value (MCX copper + zinc) × brass ratio + transport
floor = (high band + transport) × 1.05
```
Metal ₹983.65/kg · ratio 0.876 (measured) · transport ₹20/kg → **floor ₹966/kg for a 30-day quote.**

---

## 5. How they collect data — the answer is "they don't"

This was the decisive design question. A tool that needs daily input from a family-run factory will
be abandoned in a fortnight.

| Data | Who supplies it | Effort |
|---|---|---|
| MCX copper + zinc closes | **the system** | none |
| Metal benchmark, FX | **the system** | none |
| Brass/metal ratio | **the system** (measured from 11 board sources) | none |
| Transport charge | owner, **once** | one number |
| Quote-validity days | owner, **once** | one number |
| Weekly brass rate *(optional)* | purchase man — *"aaj peetal ka kya bhaav hai?"* | one figure a week, 30 seconds |
| One invoice *(optional)* | owner, whenever convenient | once |

**Total owner effort: two numbers, once. Then zero.**
Everything else is collected automatically or measured from public sources.

The optional weekly figure matters: it turns the ratio into a tracked series. If he never sends it,
the product still works — it just uses the market ratio instead of his own.

---

## 6. One-step or multi-step? — the decision

**Recommended: one step.** The weekly message *is* the product; the checker lives behind a link
inside it.

| Design | Owner effort | Accuracy | Verdict |
|---|---|---|---|
| **One step — weekly note + link to checker** | open one message, occasionally tap one number | good | ✅ **Recommended** |
| Two steps — note + separate login dashboard | sign in, navigate | same | ❌ friction without benefit |
| Continuous monitoring app | daily attention | slightly better | ❌ abandoned in weeks |
| Alert-only (SMS on price move) | none | poor | ❌ he cannot act same-day; alerts are noise for him |

**Reasoning:** his revealed behaviour — buying almost weekly in small lots, planning a month out,
never bulk — describes someone who wants **one ritual**, not a tool to operate. A daily alert would
fight his own stated constraint.

---

## 7. Options to give the owner — three tiers

The trade-off offered is **accuracy versus effort**, and it is his to choose.

| | **Tier 1 — The Note** | **Tier 2 — Note + Guard** | **Tier 3 — Calibrated** |
|---|---|---|---|
| **What he gets** | weekly WhatsApp message: low/mid/high + floor | + the checker page | + the ratio calibrated to **his** purchases |
| **His effort** | none | tap one number when quoting | one figure a week |
| **Data used** | public metal + market ratio | same | + his own scrap rates |
| **Uncertainty** | ±₹38/kg (ratio sd) | ±₹38/kg | ±₹17/kg (honey-grade sd) |
| **Cost of being wrong** | ~₹2.1 lakh/month | ~₹2.1 lakh/month | ~₹0.9 lakh/month |
| **Starts** | day 1 | day 1 | week 4 |
| **Abandon risk** | very low | low | moderate |

**Recommendation to the owner:** start at **Tier 2**, and treat Tier 3 as an upgrade he can opt into
once he has seen the note be right a few times. Tier 3 asks for a habit; habits must be earned.

---

## 8. Customer journey

| Stage | What happens | Owner sees | What we need to have built |
|---|---|---|---|
| **0 · Awareness** | we show him the band for last week and what actually happened | one page, one number | the band |
| **1 · First use** | he checks a quote he is about to send | PASS / THIN / RISKY / STOP | the checker |
| **2 · First week** | the weekly note arrives at the start of the week | three numbers + floor + one line of meaning | note generator |
| **3 · First surprise** | a quote that would have lost money gets raised | a rupee figure saved | the gap-in-rupees line |
| **4 · Fourth week** | he starts planning delivery against the middle number | the band as a planning input | nothing new |
| **5 · Month 2** | he asks for validity per market (Europe vs Gulf) | floors at 30/15/7 days | validity model |
| **6 · Month 3** | the ratio is recalibrated on his invoices | the floor tightens | Tier 3 |
| **7 · Quarter 1** | review: rupees saved vs quoting at the middle | a single before/after number | the backtest |

**Moment of truth:** stage 3. The product earns its place the first time it stops a quote that
would have bled. Nothing before that matters.

---

## 9. What they actually touch

`Castle_Quote_Checker.html` — built and tested (13/13 headless behavioural tests pass).

- **Tab 1 · Check a quote** — one big number field, three validity chips, one verdict
  - `Safe to quote.` / `Allowed, but thin.` / `Risky.` / `Do not quote this.`
  - shows the gap in ₹/kg **and in rupees on a 100 kg order**
- **Tab 2 · This week's note** — the WhatsApp text, ready to copy or share
- **Collapsed panel** — the four inputs, for whoever maintains the file weekly
- Defaults are pre-filled and correct; an untrained user never has to open that panel

---

## 10. Mapping to the DTPS syllabus

| Unit | Topic | Where it appears in this project |
|---|---|---|
| **I** | Design thinking models, applications | Problem framed from the owner's words, not a textbook problem |
| **I** | **Business Model Innovation** | The three tiers in §7 — accuracy sold as an upgrade, not a feature list |
| **I** | Visualisation Tool | `brass_graph.html` — 72-node driver map |
| **II** | **Mind Preparation** | Reading the market structure before theorising: no brass futures, scrap-led buying |
| **II** | **Storytelling** | `Brass_Story.html` — the 100-kilo order narrative |
| **II** | **Idea Generation Process** | 6 ideas → 3 kept (LME tracker ✔, weekly signal ✔, quote bands ✔; hedging ✘ no facility, black-box picker ✘ unexplainable, daily trader ✘ cannot act) |
| **II** | **Mind Mapping** | The 72-node tree, MECE-tested per level |
| **II** | **Launch Tool** | The three tiers + the journey in §8 |
| **II** | **Strategic Opportunities** | Europe + Middle East confirmed; UK CETA, UAE CEPA, EU lead rules |
| **III** | **Opportunity Finding** | The latent need in §2 — "a month's projection" really meant "how much room in a quote" |
| **III** | **Osborne–Parnes CPS** | Fact-finding (72 nodes, 65 claims) → problem-finding (the identity) → idea-finding (6) → solution-finding (tiers) → acceptance-finding (owner interview, 8 questions) |
| **III** | **Brainstorming** | The three-kept-of-six shortlist |
| **III** | **Attribute Listing** | A usable forecast must be: weekly · ranged · grade-aware · explainable · cheaper than one bad purchase |
| **III** | **Morphological Analysis** | Horizons (weekly buying × quarterly budget) × decisions (buy/quote/budget) × markets (Europe, Middle East) = **2×3×2 = 12 cells** |
| **IV** | **Influence Diagrams** | `output/edges.json` — 9 evidenced cross-links with sign and lag |
| **IV** | **Interpretive Structure Modelling** | The 72-node hierarchy, one criterion per split |
| **IV** | **Scenario Building** | Low / middle / high band across four alloy weights and three validity horizons |
| **IV** | **Flexibility** | Every unknown carried as a **parameter or a range**, never a guess |
| **V** | **Rapid Prototyping** | `brass_model.py` → `brass_price_calculator.py` → `Castle_Quote_Checker.html` in one day |
| **V** | **Synthesis** | Metal model + measured ratio + transport + validity → one floor |
| **V** | **Iteration** | 20+ logged corrections in `brass_session_handoff.md` §14 |
| **V** | **Formative Feedback** | The founder's 8 answers, verbatim and dated; they changed the target, the horizon and the markets |
| **V** | **Action Planning** | The P0–P7 TODO with acceptance criteria |
| **V** | **Launch Tools** | This document — journey, tiers, moment of truth |

---

## 11. Success measures

| Measure | Target | Source |
|---|---|---|
| Quote floor coverage | ≥ 80% of 4-week periods stay below the floor | backtest |
| Rupees saved vs quoting at the middle | ~₹29,500 per 5,500 kg order, expected | quote-exposure model |
| Owner effort | two numbers once, then zero | design |
| Ratio calibration error | ±₹38/kg → ±₹17/kg | Tier 3 |
| Abandonment | note still opened in week 8 | the real test |

---

## 12. Failure modes, and what we do about them

| Failure | Why it would happen | Mitigation |
|---|---|---|
| The note stops arriving | no automation; cron never ran in WSL | Windows Task Scheduler, or a 10-second manual run |
| Owner ignores the floor | no consequence attached | show the rupee gap on a real order size |
| Ratio drifts | −1.5%/yr | recalibrate quarterly, or Tier 3 |
| Prices spike beyond the band | 4-week p95 is +₹25.8/kg | band is a range by design; the floor is the conservative line |
| Over-trust in the middle number | it looks precise | wording: "plan on the middle, treat the gap as cushion" |
| We ship a signal that does not work | it looked clever | **the backtest already rejected it** |

---

## 13. Rollout

1. **Week 1** — send the note once, by hand. Watch whether he opens it.
2. **Week 2–4** — note + the checker link. Ask him to check one live quote and tell us the verdict he got.
3. **Month 2** — ask for validity days per market; split the floors.
4. **Month 3** — ask for one invoice; recalibrate to Tier 3.
5. **Quarter 1** — review rupees saved against the middle-number policy.

**Do not** promise a website, live prices, or a profit. The product's claim is narrow and provable:
*here is a floor, and here is what it costs you to quote below it.*

---

*Artefact: `Castle_Quote_Checker.html`. Method: `output/PROJECT_BRIEF.md`. Limits: `output/PROCUREMENT_BACKTEST.md`.*
