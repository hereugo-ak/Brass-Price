# Finding — the band width should not be one number

**Date:** 2026-11-13 · **Script:** `data/quantile_band.py` → `data/quantile_band_results.json`, `data/quantile_split.json`
**Target:** metal-leg 4-week change in ₹/kg · **Sample:** 1,543 weekly observations, 1992 → 2026

---

## 1. What we ship today

The band half-width is **one constant**:

```
risk_p95_30d = 25.8 ₹/kg        (brass; equals 29.74 on the metal leg)
scaled by sqrt(cover_days / 30)
```

That number is the p95 of *all* historical 4-week moves, applied identically in every market
condition. This document tests whether that is defensible.

**It is not.**

---

## 2. The proof — the tail depends on the regime

All 1,543 weeks bucketed by trailing 26-week volatility, then the realised 4-week change measured
inside each bucket:

| Volatility regime | weeks | p05 | median | **p95** | band width |
|---|---:|---:|---:|---:|---:|
| Calm (< 6) | 775 | −10.0 | +0.6 | **+13.5** | 23.5 |
| Normal (6–10) | 458 | −22.5 | +2.7 | **+30.0** | 52.5 |
| Elevated (10–14) | 183 | −38.8 | +2.5 | **+45.3** | 84.2 |
| High (≥ 14) | 127 | −25.3 | +6.6 | **+59.3** | 84.6 |
| **What we ship** | — | — | — | **+29.74** | — |

**One constant is wrong in both directions at once:**

- In **calm** weeks it is **2.2× too wide**. The floor sits too high, quotes look expensive, orders
  are lost to competitors who priced nearer the market.
- In **high** weeks it is **2× too narrow**. Measured: the constant was **breached in 17% of
  high-volatility weeks** — a one-in-six chance of an underpriced quote becoming a loss.

This is not a modelling opinion. It is a count.

---

## 3. Can the width be learned? Yes — measured

356 walk-forward origins, expanding window, quantile regression at τ = 0.05 and 0.95.
Scored with **pinball loss** (the proper scoring rule for a quantile), plus coverage and width.

| Model | pinball ↓ | coverage (target 95%) | band width ₹/kg |
|---|---:|---:|---:|
| **Shipped constant** (baseline) | 4.153 | 0.944 | 51.35 |
| Expanding empirical quantile | 4.337 | 0.869 | — |
| **Linear quantile regression** | **3.292** | 0.928 | 47.25 |
| Gradient-boosting quantile | 2.398 | 0.911 | 34.47 |

**Linear quantile regression: 21% better pinball loss, narrower band, coverage 92.8%.**

Split-sample check — it must win in both halves to be believable:

| Model | early half | late half |
|---|---|---|
| Shipped constant | 3.33 / cov 0.97 | 4.98 / cov 0.92 |
| Linear quantile reg. | **2.23** / cov 0.91 | **4.35** / cov 0.94 |
| Gradient boosting | 1.02 / cov 0.89 | 3.78 / cov 0.93 |

It wins in both halves. **This is the first genuinely positive modelling result in the project.**

**Caveat, stated plainly:** the gradient-boosting model only produced **28 forecasts** (it runs every
13th origin for cost reasons). 28 points is not enough to claim anything. Only the linear model
(356 forecasts) is trustworthy.

---

## 4. The catch — the fitted model overshoots at extremes

At the latest origin (week 2026-09-28) trailing volatility is **14.22**, the **92nd percentile** —
inside history (max 22.91, 123 comparable weeks), so not an extrapolation.

| Estimate | p95 prediction | implied floor |
|---|---:|---:|
| Normal approximation (1.645 × vol × 2) | +46.8 | ₹995 |
| **Linear quantile regression** | **+79.6** | **₹1,019** |
| **Empirical high-regime p95** | **+59.3** | **₹1,000** |
| Shipped constant | +29.7 | ₹973 |

The linear model overshoots the empirical answer by ~34% because the true relationship between
volatility and tail width is **concave**, and a linear fit extrapolates it as if it were straight.

For a product, an over-wide band means an over-high floor, which loses orders. So the fitted model is
**statistically better on average and commercially riskier at the extremes.**

Log-transforming the volatility features tempers it only slightly (+79.6 → +75.4). Regularisation
does not help either. The problem is the functional form, not the fit.

---

## 5. What is actually recommended — regime buckets

Use the table in §2 directly. Bucket the current volatility, look up the historical quantile for that
bucket. No extrapolation, fully auditable, and it captures the effect.

| Regime today | p95 used | Resulting floor |
|---|---:|---:|
| Calm | +13.5 | **₹958** |
| Normal | +30.0 | ₹973 |
| Elevated | +45.3 | ₹988 |
| **High (current)** | **+59.3** | **₹1,000** |
| *Shipped constant* | *+29.7* | *₹973* |

**Spread across regimes: ₹958 → ₹1,000 = ₹42/kg = ₹2.3 lakh/month on 5,500 kg.**

This is still learning from history — conditional estimation rather than a fitted predictor. It is
also impossible to make it produce a silly number, which the linear model can.

---

## 6. What this does and does not fix

| | Effect |
|---|---|
| Does it improve the forecast? | **No.** Direction remains unpredictable; that is closed. |
| Does it improve the band? | **Yes** — 21% better pinball, coverage held, both halves |
| Does it change the floor? | **Yes**, ₹958–₹1,000 instead of a flat ₹973 |
| Rupee value | ~₹42/kg spread = **₹2.3 lakh/month** at 5,500 kg |
| Bigger lever still available | the ratio (±₹38/kg = ±₹2.1 lakh/month). One invoice outranks this. |

---

## 7. Honest verdict

**Positive result, worth shipping — as regime buckets, not as a fitted model.**

It is the first time a learned component beats the incumbent on a proper scoring rule in this
project. Everything before it failed: 8 predictive models on the brass index (all lost with
DM −5.6 to −10.2), and the buy/wait signal (−₹0.11/kg).

The distinction to keep straight:

- **Predicting direction** — tested, failed, closed.
- **Estimating how wide the uncertainty is** — tested, **works**, and is what a floor actually needs.

---

## 8. If this is implemented

1. Add the regime table to `app/engine.py` with a `MODEL_VERSION` bump.
2. Keep the constant as the fallback if volatility cannot be computed.
3. Cap the regime p95 at the historical high-regime value — never extrapolate.
4. Re-run `data/quantile_band.py` quarterly as a standing test; if regime buckets stop beating the
   constant, retire them.
5. Document the regime in the product UI so a user can see *why* the floor moved.

*Reproduce: `cd data && python quantile_band.py`*
