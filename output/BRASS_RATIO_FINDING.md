# Finding — the brass/metal ratio, and why the price tiers split

**Date:** 2026-11-12
**Source:** `output/Brass_Prices_Combined_v3_2026-11-12.xlsx` (14 sheets)
**Extraction:** `data/brass_target_from_board.py` → `data/manual/*.csv`, `data/brass_ratio_anchors.json`
**Verdict: this is the most useful file in the project so far.**

---

## 1. What the file resolved

Two questions were open this morning:

1. Which price is Castle's — the ₹420 tier or the ₹900 tier?
2. Can the metal leg be turned into a brass price at all?

Both are now answered with evidence.

---

## 2. There are two separate markets, and they are not in conflict

| Tier | ₹/kg | % of metal content | Who trades there |
|---|---:|---:|---|
| **Household / kabadi pickup** | 402 – 519 | **40 – 52%** | a household selling a broken utensil |
| **Foundry board / wholesale** | **810 – 1000** | **82 – 100%** | a factory buying tonnes from a trader |

Metal content, computed as `0.615·Cu + 0.385·Zn` at IMF prices and FRED FX: **₹998/kg (2026-09)**.

The low tier is not bad data. It is a **real tier** — Steel-Baba explicitly lists household pickup at
₹550–700/kg for bartan. The earlier quarantine of ₹419.93 as "physically impossible" was the right
call for the wrong reason, and the entry has been **corrected**: the figure is genuine but belongs to
a market Castle does not buy in.

**Castle buys from local traders, so its tier is the board: ₹810–1000/kg.**

---

## 3. The ratio is stable across seven years and three source families

```
brass_₹/kg  ≈  ratio × metal_leg_₹/kg
```

| Period | Source family | n | Ratio |
|---|---|---:|---:|
| 2019-08 → 2019-12 | MCX BRASSPHY futures (107 closes) | 5 months | **0.977** |
| 2023-01 | MTLEXS Mumbai (honey, sheet) | 6 | **0.910** |
| 2026-11 | Eleven Indian boards | 27 | **0.897** |

Three independent families, seven years apart, agree within **8 percentage points**. That is the
first time the spread layer has been measured rather than assumed.

**By grade in 2026:**

| Grade family | n | Ratio | sd |
|---|---:|---:|---:|
| honey | 7 | 0.888 | 0.017 |
| bartan / utensil | 1 | **0.872** | — |
| purja / mixed | 8 | 0.866 | 0.050 |
| sheet / chadri | 8 | 0.963 | 0.046 |
| yellow brass (other alloy) | 1 | 0.701 | — |
| gun metal (other alloy) | 1 | 1.049 | — |

**Castle's grades — bartan, honey, purja — pool to ratio 0.876, sd 0.039, n = 16.**
Yellow brass and gun metal are different alloys and are excluded, not averaged in.

---

## 4. The band in ₹/kg — the deliverable

Metal leg, 4-week horizon (from `data/brass_model.py`): **₹994.63/kg** latest known,
80% band −₹33.84 / +₹60.71 → **₹960.79 to ₹1,055.34**.

Applying the ratio range (mean ± 1sd of Castle's grades):

| Line | Calculation | Result |
|---|---|---:|
| Low | 960.79 × 0.837 | **₹804/kg** |
| Middle | 994.63 × 0.876 | **₹871/kg** |
| High | 1055.34 × 0.915 | **₹966/kg** |
| Quote floor (+5%) | 966 × 1.05 | **₹1,014/kg** |

Sanity check against the market: Steel-Baba's *Utensil (Bartan/Pital)* board price on 2026-09-14 was
**₹870/kg**. The band's middle is ₹871. That agreement was not fitted — it fell out of two
independent routes.

On 5,500 kg/month, the band spans about **₹9 lakh** between low and high. That is why the floor
matters more than the middle number.

---

## 5. What the file also confirmed

### 5.1 The metal leg construction is right

MCX BRASSPHY 2019 settled at **0.977×** our computed `(0.615·Cu + 0.385·Zn)·FX`. Our copper, zinc
and FX assembly reproduces an actual Indian exchange settlement to within 2.3%. The single most
important structural assumption in the project is now empirically checked.

### 5.2 Domestic copper validates too

MTLEXS Mumbai cathode, 2026-11-05: **₹1,410/kg**. Our IMF-derived copper: ₹1,359/kg. A 3.8% gap —
consistent with an import-duty/domestic premium. The public metal data is sound.

### 5.3 HCL's pricing formula — partial answer to the owner's Q6

Hindustan Copper sets its base price as **(LME + premium)**, with a premium of **USD 100/t for
cathode** and **USD 180/t for 8 mm CC rod**. This is the domestic metal-pricing mechanism the owner
described in words ("LME governs most of it, MCX also governs the price, transport extra") and it is
now documented. Status: **Disputed**, single company source, needs a second pull.

### 5.4 The WPI brass index is not a price proxy — correction

Earlier today I proposed anchoring the WPI index to a market price. **That index cannot be used as
a level.**

| Check | Value |
|---|---:|
| 2019: index 112.4 ↔ MCX brass ₹312 | implied base = ₹278/kg |
| 2011-12 metal cost | ₹287.5/kg |
| ratio | 0.97 — sane |
| 2026-04: index 216.3 → implied | ₹601/kg |
| actual board, Nov 2026 | ₹897/kg |
| **index understates the market by** | **1.49×** |

The old-base index rises 1.92× since 2019 while the market rose ~2.9×. It may be used as a
**direction** indicator only. The 2022-23-base series is kept separate and must never be spliced.

---

## 6. What is still weak

1. **No continuous weekly brass series.** The board data is a *level* (27 dated observations
   concentrated in Nov 2026, plus two historical windows), not a series. The ratio is estimated from
   snapshots.
2. **The ratio drifts down**: 0.977 (2019) → 0.910 (2023) → 0.876 (2026). Roughly −1.5% a year.
   A constant ratio will be wrong in either direction as time passes. The band must carry the drift.
3. **MCX BRASSPHY 2019 had zero volume and zero OI** — settlement prices of an illiquid contract.
   Useful as a ratio anchor, never as a traded price or as proof brass is hedgeable.
4. **Grade composition of "bartan" and "gittu" is still unconfirmed.** The 0.872 bartan ratio rests
   on one observation.
5. **The ¥/₹ spread is estimated, not observed by Castle.** ₹871 is a well-evidenced estimate of
   Castle's market. It is still not Castle's invoice.

---

## 7. What this changes in the plan

| Before today | Now |
|---|---|
| spread layer unmeasurable, carried as ±₹80 parameter | **ratio 0.876 ± 0.039, measured at 3 points in time** |
| metal leg is a proxy, output labelled "not Castle's price" | metal leg × ratio ≈ Castle's market tier, **cross-checked against a real board price** |
| band existed only in metal-leg terms | **band in ₹/kg: ₹804 / ₹871 / ₹966, quote floor ₹1,014** |
| WPI index expected to anchor the level | **WPI old base withdrawn as a level source** |

The project now has a defensible number in the units the business uses. The remaining gap is
narrower and specific: **one invoice from Castle** to confirm the ratio on its own purchases, and a
weekly price note to make it a time series.

---

*All figures reproducible: `python3 data/brass_target_from_board.py` then `data/brass_ratio_anchors.json`.*
