# Stage 1 — metal-leg band and quote floor

**Date:** 2026-11-12
**Status:** working engine, honest limits. **This is not Castle's buying price.**
**Run:** `cd data && python3 brass_model.py`

---

## 1. What was built

`data/brass_model.py` models the **metal leg only**:

```
metal_leg_inr_kg = (wCu · Cu_USD_t + (1 − wCu) · Zn_USD_t) × INR_per_USD / 1000
```

| Piece | Implementation |
|---|---|
| Inputs | IMF copper/zinc (monthly), USD/INR (FRED H.10) |
| Leakage control | copper/zinc shifted 56 days, FX shifted 7 days, per `LEAK_MAP.md` |
| Horizon | **4 weeks** — matched to the founder's "projection for a month" |
| Walk-forward | step 4 weeks, origins from week 52 |
| Weights | swept 58 / 60 / 61.5 / 63% Cu (IS 319 Gr-II range) |
| Band | empirical error quantiles, not an assumed distribution |

**Not modelled, not guessed:** dealer premium, mandi premium, transport, conversion charge, scrap
discount, duties. These are parameters with a stated range, never a point pick.

---

## 2. Result — naive wins again

Primary weight 61.5% Cu, 385 walk-forward forecasts per model:

| Model | MAE ₹/kg | RMSE ₹/kg |
|---|---:|---:|
| **naive (carry forward)** | **27.31** | 41.63 |
| drift26 | 27.65 | 41.30 |
| ma4 | 28.03 | 43.29 |
| ma13 | 30.51 | 48.05 |

Same verdict at every weight:

| wCu | naive MAE | best challenger |
|---:|---:|---:|
| 0.580 | 26.45 | 26.74 (drift26) |
| 0.600 | 26.94 | 27.26 (drift26) |
| **0.615** | **27.31** | 27.65 (drift26) |
| 0.630 | 27.68 | 28.03 (drift26) |

**No challenger beats naive at any weight assumption.** This is consistent with the FX result
(naive 0.2128 vs Ridge 0.2930) and with the broader finding: metal prices 4 weeks out are close to
a random walk, and every extra moving part adds error rather than removing it.

**Do not treat this as a failure to fix.** It is the bar. It also means the project's value is
structural — the identity, the spreads, the quote-floor rule — not directional prediction.

---

## 3. The band is asymmetric — a real finding

Latest known metal leg: **₹994.63/kg** (week 2026-11-02).

| Range | Downside | Upside |
|---|---:|---:|
| 80% band | −₹33.84 | **+₹60.71** |
| 90% band | −₹45.98 | **+₹83.03** |

Upside risk is **~1.8× the downside** at both levels. Brass prices in this sample move up faster
than they fall.

**Practical consequence:** a symmetric ± band would systematically *under-cushion* the quote floor.
That bias runs straight into the business problem — a quote that is too low loses money when metal
rises, which is exactly the failure the project exists to prevent. The asymmetric band is therefore
a required part of the output, not a cosmetic detail.

80% band width = ₹94.55/kg = **9.5% of the metal leg**. That is the honest 4-week uncertainty on the
metal alone.

---

## 4. Quote floor grid

`data/brass_band.csv` — 5 spread assumptions × 3 validity settings.

| Spread assumed | Metals band 80% (30d) | Quote floor +5% |
|---|---:|---:|
| −₹80/kg | ₹960.79 – ₹1,055.34 | ₹1,108.10 |
| ₹0 | ₹1,040.79 – ₹1,135.34 | ₹1,192.10 |
| +₹80/kg | ₹1,120.79 – ₹1,215.34 | ₹1,276.10 |

Validity scaling: cushion scales with √(days/30) — standard random-walk scaling, **not fitted**
(there is no data to fit it on yet). 7-day and 15-day floors are in the CSV.

The spread column is the honest part: it ranges ±₹80 because **nobody has told us the real value.**

---

## 5. Correction to an earlier claim in this session

Earlier I said the unknown spread (±₹50/kg) was **12× the forecast error**. **That was wrong.**

It compared ±₹50 against ₹4.1/kg, which was the **FX-only** error, not the metal-leg error. Once
copper and zinc are modelled properly at a 4-week horizon, the real error is **₹27.31/kg**.

Corrected statement:

> The unknown spread (±₹50/kg) is about **1.8×** the 4-week metal-leg forecast error (₹27.31/kg).

Still material — the spread matters about twice as much as forecast skill does — but it is not the
12× gulf I claimed. The corrected ratio is used everywhere from here on.

---

## 6. What this can and cannot support

**Can support:**
- a weekly band on the metal leg, with honest asymmetry
- a quote-floor grid across spread and validity assumptions
- a defensible "Stage 1, proxy only" deliverable for the 2026-11-15 submission
- the claim that naive is the bar, demonstrated twice on two different targets

**Cannot support:**
- any statement about Castle's actual buying price
- a rupee-saved backtest (no real target)
- a claim that the band is calibrated to Castle's market

**The gap, stated once:** the metal leg is ₹994.63/kg and the delivered scrap price is that plus an
unknown spread. Every output above is that metal leg plus a labelled parameter grid. It becomes
Castle's number only when real prices calibrate the spread.

---

## 7. Next stage, triggered by data

| Weekly rows | What unlocks |
|---:|---|
| 8 | constant spread estimate + error bar |
| 12 | band calibrated against Castle's own prices |
| 30 | spread with confidence interval; usable quote floor |
| 100+ | fitted lags, full tournament, rupee-saved backtest |

Until row 1 exists, Stage 1 is the honest ceiling.

---

*Generated by `data/brass_model.py`. Numbers in `data/brass_model_results.json`.*
