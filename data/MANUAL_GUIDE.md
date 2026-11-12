# Manual collection guide — 10 min/day, 20 min/week, 30 min/month

Everything lands in `Brass/data/manual/`. One row per observation, newest at bottom.
Date format everywhere: YYYY-MM-DD. Numbers plain (no ₹, $, commas).

## DAILY (morning, ~10 min)
| # | What | Exact source | Save to | Columns |
|---|---|---|---|---|
| 1 | RBI ref rates USD, EUR | rbi.org.in → Reference Rate Archive → download Excel | `manual/rbi_ref_rates.csv` | date,usd_inr,eur_inr |
| 2 | LME copper+zinc cash/3M + stocks | lme.com → Official Prices + Warehouse & stock reports | `manual/lme_daily.csv` | date,cu_cash,cu_3m,zn_cash,zn_3m,cu_stocks_t,zn_stocks_t |
| 3 | MCX copper/zinc settle | mcxindia.com → Market Data → Bhavcopy | `mcx_manual/` (keep original dated file, don't rename) | — |

**MCX check:** after saving, run `python3 check_mcx.py`. It fails closed on the frameset trap below.

> **Known trap (2026-11-12):** a browser "save" of the MCX bhavcopy often stores an HTML
> frameset that points to a `_files/sheet001.htm` that was never saved. The file has an `.xls`
> name and looks fine, but holds no prices. The 2026-10-09 capture is exactly this. Save the
> visible table itself (or copy it into `mcx_daily.csv`), then re-run `check_mcx.py`.
> MCX returns HTTP 403 to all automated requests — manual browser download only.

## WEEKLY (Thursday/Friday, ~20 min)
| # | What | Exact source | Save to | Columns |
|---|---|---|---|---|
| 4 | Drewry WCI + Shanghai–Rotterdam/Genoa legs | drewry.co.uk → World Container Index (Thursday) | `manual/freight_weekly.csv` | date,wci_40ft,sh_rtm,sh_genoa |
| 5 | LME COTR copper positioning | lme.com → Commitments of Traders | `manual/cotr_weekly.csv` | date,inv_fund_net_cu_lots,commercial_net_cu_lots |
| 6 | Mandi/dealer quote (THE valuable one) | your supplier call/WhatsApp | `manual/mandi_quotes.csv` | date,item,spec,price_inr_kg,source |

## MONTHLY (~30 min)
| # | What | Exact source | Save to | Columns |
|---|---|---|---|---|
| 7 | PMI headlines IN/US/EU | S&P Global / ISM / HCOB releases | `manual/pmi_monthly.csv` | date,india_mfg,us_ism,eu_hcob |
| 8 | OPEC demand + ORB price | publications.opec.org/momr | `manual/opec_monthly.csv` | date,demand_growth_mbd,orb_usd_bbl |
| 9 | ABS approvals + RBA rate | abs.gov.au / rba.gov.au cash-rate page | `manual/au_monthly.csv` | date,approvals_no,rba_cash_rate |
| 10 | PPAC Indian basket + Delhi RSP | ppac.gov.in → prices | `manual/ppac_fuel.csv` | date,indian_basket_usd_bbl,petrol_inr_l,diesel_inr_l |

## WHENEVER IT ARRIVES
- Owner's 8 answers → `data/owner_answers.md` (Q + answer + date, exact words)
- Owner's price mechanism / transport detail → same file, under Q6
- Purchase bills → `data/invoice_log_template.csv` (one row per bill; only if volunteered)
- Anything paid/gated → note it in `quarantine.csv`, don't fake it

## Rules
1. Never edit old rows — append only. Mistakes get a correcting row, never a rewrite.
2. If a source is down, skip the day and note it. Gaps are honest; invented numbers kill models.
3._templates below already have headers — just add rows.
