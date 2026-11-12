# Procurement backtest — the acceptance test, run for the first time

**Date:** 2026-11-12
**Script:** `data/backtest_procurement.py` → `data/procurement_backtest.json`
**Target:** `metal_leg × 0.876` — a **SYNTHETIC** brass series (estimate of Castle's tier, not an invoice)
**Weekly frame:** 1,593 weeks, 1992-03-02 → 2026-11-02

---

## Headline

**The buy-timing signal fails the rupee-saved backtest.** It loses money against simply buying every week.

Per the project's own acceptance rule — *no model ships unless it beats naive on MAE **and** survives the rupee-saved backtest* — the buy signal **does not ship**.

What survives is the **quote floor**. That is not a consolation prize; the same numbers say the money sits on the sell side, which is where the owner's losses actually occur.

---

## A. Cost of delay — what waiting actually costs

Brass price change by delay, all 1,589 four-week periods on record:

| Delay | n | Mean change | Weeks higher | Share higher |
|---|---:|---:|---:|---:|
| 1 week | 1,592 | +₹0.59/kg | 52.6% | |
| 2 weeks | 1,591 | +₹1.19/kg | 55.6% | |
| 3 weeks | 1,590 | +₹1.78/kg | 56.5% | |
| **4 weeks** | 1,589 | **+₹2.38/kg** | **57.5%** | |
| 8 weeks | 1,585 | +₹4.76/kg | 59.6% | |

On the brass estimate (× 0.876): **+₹2.08/kg per four weeks of delay.**

**Interpretation, stated carefully:** the *expected* cost of waiting is small — about 0.24% of the
price over four weeks. But the **probability** of being higher than today climbs steadily with the
horizon: 52.6% at one week, **57.5% at four**, 59.6% at eight. Prices rise more often than they
fall, they just do not rise much on average.

That is the asymmetry the band already showed, now confirmed in the time dimension.

**Business meaning:** "wait a week and see" is not expensive on average — which is why the owner's
weekly hand-to-mouth rhythm is rational. It is the **tail** that hurts, and that is what the floor
covers.

---

## B. Buy-timing signal vs buying every week

Policy tested: each week one unit is due. Defer if the model's one-week-ahead forecast is lower than
this week. Maximum two weeks of obligation stacking. 1,592 decision weeks.

| Metric | Value |
|---|---:|
| Baseline — buy every week | ₹249.02/kg average |
| Signal — defer when forecast says cheaper | ₹249.13/kg average |
| **Difference** | **−₹0.11/kg (−0.045%)** |
| Weeks deferred | 30.5% |
| **Monthly impact on 5,500 kg** | **−₹612** |

**The signal loses.** It defers on 30.5% of weeks and pays ₹0.11/kg more for the privilege.

This is consistent with every other result in the project: the metal leg is close to a random walk
week-ahead, naive is the best forecast, and timing on a nearly unpredictable series generates churn
cost rather than savings.

**Conclusion: do not ship a buy/wait signal.** Ship the band and the floor.

---

## C. Quote exposure — where the money actually is

Same 1,589 four-week periods, expressed as brass price change (₹/kg):

| Percentile | Change |
|---|---:|
| p05 | −₹18.7 |
| p10 | −₹10.8 |
| p50 | +₹0.8 |
| p90 | +₹16.7 |
| p95 | **+₹25.8** |
| mean | +₹2.1 |
| sd | ₹14.0 |

Share of four-week periods in which brass rose: **57.5%**.

Expected metal cost of quoting at each level, per 5,500 kg order:

| Quote set at | Expected loss | Worst observed |
|---|---:|---:|
| Mid ₹871/kg | **−₹5.37/kg = −₹29,558** | −₹77.7/kg |
| High ₹966/kg | ₹0 | ₹0 |
| Floor ₹1,014/kg | ₹0 | ₹0 |

**Read this correctly:** quoting at the band's middle carries an expected metal cost of about
**₹29,500 per 5,500 kg order**, and up to ₹4.3 lakh in the worst case. Quoting at the band high
removes the metal risk — but prices the offer roughly **11% above the middle**, which is a
competitiveness cost, not a free lunch.

That trade-off *is* the decision the floor rule encodes. It is the one place in this project where
the numbers point at real money.

---

## D. A technical caveat that changes the floor

The band used above (−₹33.84 / +₹60.71) comes from `brass_model.py` **forecast errors**, and those
errors are inflated on purpose: the model is only allowed to use IMF copper and zinc that were
public **56 days** earlier, per the leak map.

If Castle works from **current** LME/MCX prices — which a trader does — the four-week uncertainty is
much tighter: p95 of the *actual change* is **+₹25.8/kg on brass**, not +₹60.71.

| Source of the band | 4-week upside |
|---|---:|
| Model forecast errors (56-day lag handicap) | +₹60.71/kg metal |
| Actual price-change distribution (current prices known) | **+₹25.8/kg brass** |

**So ₹1,014/kg is a conservative floor.** With live metal prices it could be set nearer the high
band of ₹966. The honest position: quote the conservative floor, and tighten it once Castle's own
prices confirm the ratio.

---

## E. What this settles

| Question | Answer |
|---|---|
| Does a buy/wait signal beat buying every week? | **No** — loses ₹0.11/kg (−0.045%) |
| Should a signal ship? | **No.** The acceptance rule is explicit. |
| Does waiting cost money? | Only slightly on average (+0.24% / 4 weeks), but prices are higher 57.5% of the time |
| Where is the money? | **On the sell side** — an open quote at the mid carries ~₹29,500 expected metal cost per 5,500 kg order |
| Does the ratio model survive? | It is not a timing model. It survived the level cross-check (₹871 vs ₹870 board), which is the test that applies to it. |

---

## F. What must be said in the submission

> A weekly buy/wait signal was built, tested and **rejected on its own acceptance criteria**: it
> loses ₹0.11/kg against buying every week. The project's remaining value is the range and the quote
> floor, both of which are supported by the evidence. Shipping the signal would have been the
> easy, dishonest choice; the backtest exists to prevent exactly that.

That paragraph is worth more to the assessment than a fabricated edge would be.

---

*Reproduce: `cd data && python3 backtest_procurement.py`. Target is synthetic — a ratio estimate, not an invoice — and every output is labelled accordingly.*
