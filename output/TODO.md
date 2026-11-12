# TODO — Brass Price Foresight

**Updated:** 2026-11-12 · **Submission:** 2026-11-15
**Rule:** nothing ships unless it beats naive on MAE **and** survives the rupee-saved backtest.

---

## Status snapshot — what is already done

| Area | State |
|---|---|
| Driver research | ✅ done — 72 nodes, 9 edges, 65 claims, 44 catalogue rows, 19 quarantined |
| Public data spine | ✅ done — 7 FRED series, 2,789 weekly feature rows, 1973 → 2026 |
| MCX daily copper + zinc | ✅ done — 955 rows, 2025-01-01 → 2026-11-11 |
| Board price tier | ✅ done — 27 dated observations from 11 sources |
| Brass/metal ratio | ✅ measured — 0.977 (2019) / 0.910 (2023) / 0.876 (2026) |
| Price calculator | ✅ working — two routes agree to 0.42%; band ₹843 / ₹882 / ₹920, floor ₹966 |
| Rupee-saved backtest | ✅ run — **buy signal rejected** (−₹0.11/kg) |
| **Trained model on brass** | ❌ **NONE. This is P1.** |
| Weekly brass series | ❌ missing — needs Castle |
| GitHub push | ❌ blocked — needs your login |

---

# P0 — Unblock the repo (5 minutes, yours)

**Why:** 12 commits are local only. Nothing is backed up.

```bash
cd C:\Users\Abuza\OneDrive\Documents\Brass
git push -u origin main
```

**Acceptance:** `git ls-remote origin` shows a `main` ref.

---

# P1 — Train a real model on the WPI brass index  ⭐ START HERE

**Why this is priority 1:** it is the only target in the project with enough history for a genuine
fitted model — **169 monthly observations, 2012-04 → 2026-04, real domestic Indian brass**. And a
mere hand-written rule (`drift12`) already beat naive on it by 2.7–7.5%. A trained model has a real
chance here, which it has nowhere else.

## 1.1 Data and target

| Item | Detail |
|---|---|
| Target | `brass_index` — WPI 1314090011, base 2011-12 = 100 |
| File | `data/manual/wpi_brass_monthly.csv` (169 rows) |
| Frequency | monthly |

## 1.2 Feature construction — leakage rules are mandatory

| Feature group | Columns | Availability at origin month `t` |
|---|---|---|
| Own lags | index at `t-1, t-2, t-3, t-6, t-12` | use `t-1` minimum (WPI publishes ~14 days after month end) |
| Momentum | 3-, 6-, 12-month changes | from lags only |
| Metal leg | `(0.615·Cu + 0.385·Zn)·FX/1000` | **lag 2 months** (IMF series publish ~2 months late) |
| Metal legs separately | Cu, Zn, FX levels and 3-month changes | lag 2 months |
| Ratio | measured 0.876 ± 0.039 | constant, or the anchor-year value |

**Hard rule:** every feature at origin `t` must be available at `t`. If in doubt, lag it more.
Violating this is the single easiest way to fake a result.

## 1.3 Models to fit

| Model | Notes |
|---|---|
| naive (carry forward) | the bar to beat |
| `drift12` | existing rule baseline — already slightly beats naive |
| Ridge | alphas 0.1 / 1 / 10 / 100 |
| Lasso | alphas 0.01 / 0.1 / 1 |
| RandomForest | 300 trees, max_depth tuned on a validation slice only |
| GradientBoosting | 200 estimators, learning_rate 0.05, max_depth 3 |
| HistGradientBoosting | sklearn's faster variant, same setup |

`scikit-learn 1.9.1` is installed (user site). `numpy 2.5.3`, `pandas 3.0.6` available.

## 1.4 Evaluation protocol

1. **Expanding-window walk-forward**, step 1 month, minimum 60 months of training history.
2. Horizons **1, 2, 3 months** (the owner needs ~1 month, so 1 is the headline).
3. **Diebold–Mariano** against naive for every challenger.
4. **Split sample**: 2013–2019 vs 2020–2026. A model that only wins after 2020 has not won.
5. Report **MAE, RMSE, direction hit, DM statistic** — all of them.
6. Feature-importance check: if the model leans on one lag, say so.

## 1.5 Acceptance criteria

| Outcome | Action |
|---|---|
| Beats naive **and** DM > +1.96 **and** holds in both split samples | **Promote.** This is the project's first validated model. |
| Beats naive but DM < 1.96 | Report as suggestive only. Do not ship a signal. |
| Loses to naive | **Record honestly.** Naive then has won 13 contests; state it plainly. |

**In every branch the result is reported.** A negative result here is still a complete deliverable.

## 1.6 Deliverables

- `data/train_brass_index.py`
- `data/brass_index_results.json`
- `output/BRASS_INDEX_MODEL.md` — the honest write-up, all four scenarios covered
- Rows added to `claim_ledger.csv` / `data_catalogue.csv` if new sources appear

---

# P2 — Train GBM on the weekly metal leg

**Why second:** 2,789 weekly rows is plenty of data, but naive has already beaten every rule at
all four alloy weights. A GBM *might* find non-linearity the rules miss — but this is a lower
probability bet than P1.

- Target: metal leg ₹/kg, weekly, horizon 4 weeks
- Features: lagged Cu/Zn/FX levels, lags 1/2/4/8, momentum, Brent, housing starts, construction
- Models: GradientBoosting, HistGradientBoosting, RandomForest, Ridge
- Walk-forward step 4 weeks, **embargo 2 weeks** to respect publication lag
- DM test vs naive at each alloy weight (0.58 / 0.60 / 0.615 / 0.63)
- **Acceptance:** same three-way rule as P1.

**Deliverables:** `data/train_metal_leg.py`, `data/metal_leg_gbm.json`, report section.

---

# P3 — Model the ratio drift

**Why third:** the ratio falls 0.977 (2019) → 0.910 (2023) → 0.876 (2026), about −1.5%/year. A
constant ratio will be wrong in either direction as time passes.

- Only **3 anchor points**, so a 2-parameter trend is the honest ceiling. Anything richer is
  over-fitting three numbers.
- Fit: `ratio(t) = a + b·t`, report the residual on each anchor.
- Test: does a drifting ratio improve the level check against the 2026 board? (₹871 vs ₹870)
- **Acceptance:** must be justified on out-of-sample anchors, or it stays a stated caveat, not a model.

**Deliverables:** short section in `output/BRASS_RATIO_FINDING.md`; no separate model ships unless it passes.

---

# P4 — Train on MCX copper/zinc daily

**Why fourth:** 955 daily rows, and MCX is the anchor the owner named — but it is the same random
walk in a different currency. Expect naive to win.

- Target: MCX copper ₹/kg, horizons 5 and 20 trading days
- Compare against naive and against the LME-implied value
- Useful by-product: quantify the **domestic premium** over LME over time (currently 0.42% on the alloy, 4% on copper)

**Deliverables:** `data/train_mcx.py`; premium series saved to `data/manual/mcx_premium.csv`.

---

# P5 — Fallback: ship the calculator, train nothing more

**Why keep it on the list:** if P1 and P2 both lose, this is the honest end state and it is already
built and working.

- Band ₹843 / ₹882 / ₹920 delivered; quote floor ₹966/kg
- Two independent metal routes agreeing to 0.42%
- Buy signal withdrawn on evidence
- **This is a defensible submission on its own.** The trained models are upside, not a prerequisite.

---

# P6 — Data that would actually improve the result

| # | Item | Impact | Owner |
|---|---|---|---|
| 6.1 | **One Castle invoice** — ₹/kg, month, grade | narrows ratio ±₹38 → Castle's own value | you / founder |
| 6.2 | **Weekly brass price note** | turns the ratio into a tracked series; enables a real weekly backtest | you / purchase man |
| 6.3 | **Transport charge** ₹/kg, delivered vs ex-yard | currently a ₹0–40/kg assumption driving ~₹2 lakh/month | founder |
| 6.4 | **Quote-validity days**, Europe vs Middle East | pinpoints the floor horizon (30 assumed, stress-tested at 15 and 7) | founder |
| 6.5 | **Bartan vs gittu composition** (Cu/Zn) | the 0.872 bartan ratio rests on **one** observation | founder or CoA |
| 6.6 | LME cash/3M daily history | better metal granularity than IMF monthly | ~$85 paid, or manual daily entry |

**None of these block P1–P5.** 6.1 and 6.2 improve precision; the rest improve calibration.

---

# P7 — Submission packing

- [ ] Regenerate `PROJECT_BRIEF.docx` if the brief changes (`python3 data/md_to_docx.py …`)
- [ ] Fold the P1 result into `PROJECT_BRIEF.md` §2.8 and §5
- [ ] Update `brass_session_handoff.md` correction log
- [ ] Decide on the `Brass_Story.html` line *"Six weeks out of ten"* — unsupported accuracy claim
- [ ] Final `python3 check_mcx.py` and count verification pass
- [ ] Print / export PDF of the brief for the assessor

---

## Honest expectation, recorded in advance

Naive has won **12 of 12** contests so far: FX weekly, FX 4-week, Ridge × 2, metal leg × 4 weights,
plus every rule tested. `drift12` on the WPI index is the single marginal exception and it is not
statistically significant.

So P1 is a genuine attempt, not a likely win. If a GBM beats naive on the WPI brass index with
DM > 1.96 and both split samples agreeing, that is a real result. If not, the project's honest
finding stands: **brass 4 weeks out is close to a random walk, and the value is in the band and the
quote floor, not in prediction.**

That finding is worth more to an examiner than a fitted model with a fake edge.
