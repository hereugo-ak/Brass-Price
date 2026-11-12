# Finding — an official Indian brass price index exists

**Date:** 2026-11-12
**Source:** Office of the Economic Adviser (DPIIT), Government of India — `eaindustry.nic.in`
**Files:** `cal_year_index.xls`, `monthly_index_202606.xls` (row 596 in both)
**Extracted series:** `data/manual/wpi_brass_monthly.csv`

---

## 1. What row 596 actually is

| Field | Value |
|---|---|
| Commodity | **Brass metal/sheet/coils** |
| Code | **1314090011** |
| WPI weight | 0.01026% |
| Base | 2011-12 = 100 |
| Frequency | monthly |
| Coverage | **2012-04 → 2026-04 = 169 observations** |
| Cost | free, official, no paywall |

It sits in the WPI non-ferrous metals group, alongside copper metal (1314090001), zinc metal
(1314090002) and copper bars/rods/strips (1314090006) — all extracted to the same CSV for
cross-checking.

**Answer to the question asked: yes, this is useful.** It is the first genuine *domestic Indian
brass price series* this project has found. Weekly ₹/kg still does not exist publicly, but a
monthly domestic brass **index** does, with 14 years of history.

---

## 2. Correction to an earlier claim in this session

Earlier I told the user that no free public brass series could be found, based on seven failed
retrievals (MCX 403, BigMint 403, SteelMint/metal.com empty, ScrapMonster/RecycleInMe 404,
IndiaMART empty).

**That was too strong.** It was true for *weekly ₹/kg transacted prices*. It was wrong as a blanket
statement — an official **monthly index** exists and was missed. The corrected position:

| Wanted | Exists publicly? |
|---|---|
| Weekly ₹/kg brass scrap | **No** |
| Monthly ₹/kg brass scrap | **No** |
| **Monthly brass price INDEX** | **Yes** — this file |
| Monthly brass customs unit value | Yes — UN Comtrade (not yet pulled) |

The retrieval failure was real for what I searched; the conclusion drawn from it was too wide.

---

## 3. What the series says

Brass index, annual averages (base 2011-12 = 100):

| Year | Index | y/y |
|---|---:|---:|
| 2012 | 102.3 | — |
| 2013 | 104.2 | +1.8% |
| 2014 | 109.4 | +5.1% |
| 2015 | 105.7 | −3.4% |
| 2016 | 98.6 | −6.7% |
| 2017 | 109.2 | +10.7% |
| 2018 | 117.1 | +7.2% |
| 2019 | 112.4 | −4.0% |
| 2020 | 114.4 | +1.8% |
| 2021 | 150.2 | +31.3% |
| 2022 | 161.0 | +7.2% |
| 2023 | 161.6 | +0.4% |
| 2024 | 170.5 | +5.5% |
| 2025 | 178.9 | +4.9% |
| 2026 (to Apr) | 212.9 | +19.0% |

Monthly change: mean +0.47%, median +0.49%, sd 1.98%. Largest single month +7.5%, largest −3.8%.

---

## 4. The three tests that matter

### 4.1 Does our copper+zinc+FX metal leg explain it? Partly.

Correlation of monthly % changes, 169 months:

| Compared with brass % change | Correlation |
|---|---:|
| copper alone | **+0.455** |
| metal leg (Cu+Zn)×FX | +0.435 |
| zinc alone | +0.362 |
| USD/INR alone | −0.046 |

So the metal leg explains roughly **R² ≈ 0.19** of monthly brass movement. Real, but weak.
Two notable points:

- **Copper alone correlates better than the weighted leg.** The zinc weight is mostly noise at
  monthly frequency.
- **USD/INR is essentially uncorrelated** (−0.05). Domestic brass quotes do not reprice with the
  rupee month to month — consistent with the founder's own description of a slow, dealer-mediated
  price ("we need at least a month to plan").

### 4.2 Does the index track the metal leg in level? No — it lags badly.

| Series | First month (2012-04) | Latest (2026-04) | Rise |
|---|---:|---:|---:|
| Brass index | 101.1 | 216.3 | **2.14×** |
| Metal leg ₹/kg | 308.88 | 875.00 | **2.83×** |

Domestic brass prices rose **2.14×** while the metal content rose **2.83×**. Either the index
methodology smooths and lags, or domestic margins compressed, or the basket specification differs.
**This is not resolved and must not be presented as a conclusion.** It does mean the index cannot be
scaled to the metal leg without an explicit bridge.

### 4.3 Does anything beat naive on this real target? Yes — for the first time in the project.

`drift12`: last index plus the average 12-month change, projected forward.

| h (months) | start | n | naive MAE | drift12 MAE | gap | DM |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 36 | 132 | 2.20 | 2.10 | −4.7% | +1.07 |
| 1 | 96 | 72 | 2.72 | 2.53 | −7.2% | +1.21 |
| 3 | 36 | 130 | 5.04 | 4.78 | −5.2% | +1.06 |
| 3 | 96 | 70 | 6.63 | 6.13 | −7.5% | +1.22 |
| 4 | 36 | 129 | 6.00 | 5.83 | −2.7% | +0.56 |

**Drift beats naive in all 12 configurations tested** — every horizon, every start point, by 2.7% to
7.5%. This is the **first time any challenger has beaten naive** anywhere in this project (Ridge lost
on FX, all four challengers lost on the metal leg).

**But it is not statistically established:**

- The Diebold–Mariano statistic ranges **+0.56 to +1.22**. Significance needs **> 1.96**. Never
  reached.
- Split sample: **2013–2019 naive is better** (−0.109); **2020–2026 drift is better** (+0.439).
  The entire edge comes from the post-2020 trending period.

**Honest verdict:** a suggestive, consistent, period-dependent edge. Not a proven one. It is worth
one line in the submission and it is *not* grounds to ship a signal.

---

## 5. Why this is still worth a lot — the anchor trick

The index has **no ₹/kg level**, only relatives. But one real price converts the whole series:

```
price_₹kg(month) = price_anchor × index(month) / index(anchor_month)
```

One brass price from Castle for any single month gives a **169-month ₹/kg history** back to
April 2012.

Worked example (illustrative arithmetic, not market data): if a recent price were **₹560/kg** at
index 216.3, the implied 2011-12 base would be ₹560 × 100/216.3 ≈ **₹259/kg** — a plausible level
for brass scrap in that year, which is a sanity check on the method, not a validation.

**Caveats that must travel with any calibrated series:**
1. WPI commodity weights are tiny here (0.01026%), so the basket is thin and noisy.
2. WPI will rebase to 2022-23 at some point; that breaks the ratio across the base change.
3. It is an administered index of selected quotations, not Castle's transaction price.
4. Given the 2.14× vs 2.83× gap in §4.2, a single anchor may not hold across 14 years. Anchoring
   near the estimation window is safer than anchoring at the base year.

---

## 6. What to do next with it

| Use | Status |
|---|---|
| Register as a dataset and a claim | **Done** — `data_catalogue.csv` (39 rows), `claim_ledger.csv` (62 rows) |
| Add to the leakage map (14-day WPI lag) | **Done** — `LEAK_MAP.md` |
| Use as a monthly validation series for the metal leg | Ready now |
| Convert to ₹/kg with one Castle anchor | **Blocked on one real price** |
| Monthly model at 1–3 month horizon | Tested above; drift is suggestive |
| Weekly model | **Not possible** — monthly source, and interpolating to weeks would invent data |

**Do not** interpolate this index to weekly and present it as weekly brass data. That is exactly the
fabrication the project forbids. It is a monthly series and stays monthly.

---

## 7. Reproduce

```
python3 -c "import xlrd; ..."   # extraction is in this session's log; CSV is committed
data/manual/wpi_brass_monthly.csv   # 169 rows: month, brass_index, copper_shapes, zinc_metal, copper_metal
```

Source page: `https://www.eaindustry.nic.in/download_data_1112.asp`
Row 596 in both `monthly_index_202606.xls` and `cal_year_index.xls`.

---

*Logged 2026-11-12. Every figure above is reproducible from the committed CSV and the FRED history
files.*
