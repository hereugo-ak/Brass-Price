# Leak map — publication lags (no feature may use data before it was public)

| Series | Publisher | Frequency | Usable from (lag) | Collector |
|---|---|---|---|---|
| LME Cu/Zn official + stocks | LME | daily | T+1 evening | manual/delayed page until history bought |
| USD-INR (DEXINUS) | FRED (H.10) | daily | T+1 | collect_daily.py |
| IMF Cu/Zn monthly | FRED/IMF | monthly | ~1 month | collect_daily.py |
| Brent spot | FRED/EIA | daily | T+1 | collect_daily.py |
| US housing starts / construction | Census via FRED | monthly | ~3 weeks / ~1 month | collect_daily.py |
| RBI ref rates | RBI/FBIL | daily | ~13:30 IST same day | manual Excel until scraped |
| MCX Cu/Zn bhavcopy | MCX | daily | T+0 evening | data/mcx_manual/ (bot-blocked) |
| PMI (IN/US/EU) | S&P/ISM | monthly | flash ~1wk, final month-start | manual headline |
| CFTC COT / LME COTR | CFTC/LME | weekly | Fri (Tue positions) | manual |
| Drewry WCI | Drewry | weekly Thu | same day | manual headline |
| ABS approvals / RBA rate | ABS/RBA | monthly/event | ~5wk / same day | manual |
| OPEC MOMR | OPEC | monthly | ~2 weeks | manual |
| Own invoices | Castle | per purchase | same day | invoice_log_template.csv |

Rule: any backtest row dated D may only use values published on or before D.
| ECB euro ref (USD+INR/EUR) | ECB | daily | ~16:00 CET same day | collect_daily.py |
| CFTC COMEX copper COT | CFTC | weekly (Tue/Fri) | Fri 15:30 ET | collect_daily.py |
| WPI brass index (1314090011) | OEA / DPIIT | monthly | ~14 days after month end | manual: eaindustry.nic.in -> monthly_index file |
