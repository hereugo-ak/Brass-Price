"""What is automated vs manual vs missing — the collection-provision audit."""
import pathlib, json, subprocess, csv
H = pathlib.Path('.')
auto = {
 'backfill_fred.py': 'full FRED history, 7 series',
 'collect_daily.py': 'daily FRED + ECB + CFTC + MCX probe',
 'make_features.py': 'weekly feature table (2,789 rows)',
 'baseline.py': 'naive bar refresh',
 'brass_model.py': 'metal-leg band refresh',
 'brass_target_from_board.py': 'workbook extraction + ratio anchors',
 'brass_price_calculator.py': 'current price + floor',
 'backtest_procurement.py': 'acceptance backtest',
 'train_drivers.py': 'driver model training',
 'check_mcx.py': 'validates a manual MCX download',
}
manual = {
 'manual/mandi_quotes.csv': 'weekly brass rate — 0 rows',
 'manual/lme_daily.csv': 'LME cash/3M — 1 row',
 'mcx_manual/': 'MCX bhavcopy — file is a frameset shell',
 'manual/rbi_ref_rates.csv': 'RBI ref — 0 rows',
 'manual/freight_weekly.csv': 'Drewry WCI — 0 rows',
 'manual/pmi_monthly.csv': 'PMI — 0 rows',
 'manual/opec_monthly.csv': 'OPEC MOMR — 0 rows',
 'manual/au_monthly.csv': 'ABS/RBA — 0 rows',
 'manual/ppac_fuel.csv': 'PPAC — 0 rows',
 'manual/cotr_weekly.csv': 'LME COTR — 0 rows',
}
print('AUTOMATED (run by command):')
for k,v in auto.items():
    ok = (H/'data'/k).exists()
    print(f'  {"OK " if ok else "MISS"} data/{k:32} {v}')
print('\nMANUAL ONLY (browser, 403 to bots):')
for k,v in manual.items():
    p = H/'data'/k
    n = 0
    if p.is_file():
        try: n = sum(1 for _ in open(p, encoding='utf-8', errors='ignore'))-1
        except Exception: n = 0
    print(f'  {"has data" if n>2 else "EMPTY   "} data/{k:32} {v}')
print('\nMISSING FEEDS (catalogue entry, no file): 18')
print('  LME official/stocks · LME COTR · SHFE · PMI · freight · TC/RC · USGS')
print('  · HCL output · IBM ASP · CBAM price · policy rates · CPI · OPEC · ABS · RBA')
print('\nSCHEDULING: cron daemon does not start in this WSL without admin.')
print('  -> Windows Task Scheduler entry for collect_daily.py is the working option.')
