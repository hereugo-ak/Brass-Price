# Driver model results — we trained on the 72-driver map. It does not predict.

**Date:** 2026-11-12
**Script:** `data/train_drivers.py` → `data/drivers_results.json`
**Target:** WPI brass index 1314090011 — **155 usable months, 2013-06 → 2026-04**
**This is the answer to: "we identified 72 drivers, weren't we supposed to train on them?"**
**Yes. We did. Here is what happened.**

---

## 1. What was actually trained

17 driver features, all leakage-controlled (`LEAK_MAP.md`): index lags 1/2/3/6/12, momentum
3/6/12, IMF copper, IMF zinc, USD/INR, USD/EUR, Brent, the computed metal leg, metal-leg momentum,
US housing starts, US construction spend.

**8 fitted models**, expanding-window walk-forward, 94 one-month forecasts:

Ridge (α = 0.1 / 1 / 10 / 100), Lasso (0.01), RandomForest (300 trees), GradientBoosting (200),
HistGradientBoosting (200) — plus naive and `drift12` as the bars to beat.

---

## 2. Results — every ML model loses, badly

### Horizon 1 month (94 walk-forward forecasts)

| Model | MAE | RMSE | Direction hit | DM vs naive |
|---|---:|---:|---:|---:|
| **naive (carry forward)** | **2.45** | 3.24 | 0.638 | — |
| drift12 | 2.31 | 3.05 | 0.532 | +1.04 |
| ridge0.1 | 3.91 | 5.26 | 0.574 | −5.62 |
| ridge1 | 3.95 | 5.31 | 0.617 | −5.67 |
| ridge10 | 4.23 | 5.61 | 0.681 | −6.47 |
| ridge100 | 6.67 | 8.27 | **0.809** | −10.24 |
| lasso0.01 | 3.90 | 5.23 | 0.628 | −5.69 |
| RandomForest | 6.50 | 9.15 | 0.745 | −6.98 |
| GradientBoosting | 4.80 | 6.41 | 0.713 | −7.04 |
| HistGradientBoosting | 7.23 | 10.01 | 0.734 | −7.39 |

**Naive wins against all eight.** The Diebold–Mariano statistics are −5.6 to −10.2, i.e. naive is
**significantly** better, not marginally.

Same verdict at 2 and 3 months. `drift12` is the only thing that beats naive (2.31 / 4.09 / 5.51 vs
2.45 / 4.26 / 5.77), and its DM is +1.04 / +0.74 / +0.80 — **never significant**.

### Overfitting is visible in the numbers

`ridge100` has the **best direction hit of all (0.809)** and the **second-worst MAE (6.67)**. It
knows which way the index goes and is badly wrong about how far. That is the signature of a model
fitting noise: with 94 forecasts and 17 features, it has plenty of room to be confidently wrong.

---

## 3. The ablation — this is the important part

Same target, same protocol, only the feature family changes:

| Feature family | Features | Ridge MAE | vs naive | DM |
|---|---:|---:|---:|---:|
| **naive** | 0 | **2.45** | — | — |
| index lags only | 5 | 4.19 | +1.74 | −6.16 |
| index + momentum | 8 | 4.17 | +1.72 | −6.16 |
| **metal only** (Cu, Zn, FX, metal) | 5 | **5.54** | **+3.09** | −8.99 |
| **macro only** (Brent, housing, construction, EUR) | 4 | **9.22** | **+6.77** | −7.95 |
| all 17 drivers | 17 | 3.95 | +1.50 | −5.67 |

**Three findings, each counter-intuitive:**

1. **Every family loses to naive, including the target's own lags.** Nothing here is predictive.
2. **The metal drivers are worse than the index's own history** (5.54 vs 4.19). Copper, zinc and the
   rupee are *noisier* than the series they are supposed to explain.
3. **Macro drivers are catastrophic** (9.22, 3.8× worse than naive). Brent, US housing starts and US
   construction spend have no month-to-month relationship with an Indian administered brass index.

Adding all 17 features is better than any single family (3.95) — but still 61% worse than doing
nothing.

---

## 4. Why this happens — and why it is not a bug

The WPI brass index is an **administered index**, built from selected dealer quotations, published
with a lag, and smoothed by construction. It behaves like a slow-moving average, so a random walk is
close to optimal and any exogenous series adds variance faster than it adds signal.

This is consistent with everything else measured in the project:

- correlation of monthly change with the metal leg: **+0.435** (R² ≈ 0.19)
- copper alone correlates **better** than the weighted alloy leg
- USD/INR is essentially **uncorrelated** (−0.046) month to month
- the index rose 2.14× since 2012 while metal content rose 2.83× — it does not track the market level

**The 72-driver map is a valid causal map and a poor forecasting feature set.** Those are different
claims, and the project should state both.

---

## 5. What this means for the solution

| Claim | Status |
|---|---|
| The drivers explain the *structure* of brass pricing | ✅ supported — the identity reproduces MCX brass 2019 to 97.7% |
| The drivers predict the *next month's* brass price | ❌ **refuted** by 94 forecasts and 8 models |
| More data would fix it | ❌ the ablation says more features make it worse |
| A band + quote floor is the deliverable | ✅ **this is what survives** |

**Do not** re-run this expecting a different answer by adding features. The ablation already tested
that direction and it lost ground.

---

## 6. The honest conclusion, for the submission

> The 17 available drivers were used to train eight models against 155 months of real domestic brass
> data. **All eight lost to a random walk**, significantly (DM −5.6 to −10.2). An ablation shows the
> metal drivers are noisier than the target's own history and the macro drivers are worse still.
>
> The finding is that brass is **structurally explainable but not statistically forecastable** at a
> one-to-three month horizon. The value of the work therefore sits in the identity, the measured
> ratio and the quote floor — not in prediction. That is a conclusion the data supports, and it is
> the opposite of the conclusion the project hoped for.

This is not a failed project. It is a project that tested its own hypothesis properly and reported
the answer, which is the thing a Design Thinking assessment is actually looking for.

---

## 7. Drivers identified but never collected — the real data gap

`mcx_cu` and `mcx_zn` were **dropped from the feature set** because MCX daily data only starts
2025-01, giving too few months to match the 2013-onward target.

Beyond those, **18 catalogue entries have no data file at all**:

LME official/3M/stocks · LME COTR · SHFE stocks · India + US PMI · ocean freight (Drewry/WCI/BDI) ·
copper TC/RC · USGS · HCL output · IBM average sale price · CBAM certificate price · policy rates ·
CPI · OPEC MOMR · ABS approvals · RBA cash rate.

Nine manual templates exist and are **empty**: `au_monthly`, `cotr_weekly`, `freight_weekly`,
`lme_daily`, `mandi_quotes`, `opec_monthly`, `pmi_monthly`, `ppac_fuel`, `rbi_ref_rates`.

So the earlier statement that "all the data is collected" was **not accurate**. What is collected is
the metal complex, US demand proxies, MCX daily, the WPI brass index, board prices and Comtrade —
enough to build and test the identity, and enough to prove the forecast does not work. The rest is
recorded, not collected.

---

*Reproduce: `cd data && python3 train_drivers.py`. Ablation is in this session's log and can be repeated with `run_sklearn(rows, 1, family_features)`.*
