#!/usr/bin/env python3
"""Daily free-data collector for Brass Price Foresight (stdlib only).
Pulls: FRED series (needs free FRED_API_KEY in ../.env), ECB euro reference
rates, CFTC COMEX copper COT (Socrata 6dca-aqww), MCX bhavcopy (best effort).
Appends one row per series/day into Brass/data/*.csv. Never crashes on a miss.
Usage: python3 collect_daily.py   (reads Brass/.env automatically)
"""
import csv, json, os, pathlib, urllib.request, urllib.parse, datetime

HERE = pathlib.Path(__file__).parent
HERE.mkdir(exist_ok=True)
TODAY = datetime.date.today().isoformat()
def _load_dotenv():
    p = HERE.parent / '.env'
    if p.exists():
        for line in p.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())

_load_dotenv()
FRED_KEY = os.environ.get('FRED_API_KEY', '').strip()
if FRED_KEY == 'PASTE_YOUR_FREE_KEY_HERE':
    FRED_KEY = ''

FRED_SERIES = {
    'DEXINUS':  'inr_per_usd',
    'DEXUSEU':  'usd_per_eur',
    'PCOPPUSDM': 'imf_copper_usd_t',
    'PZINCUSDM': 'imf_zinc_usd_t',
    'DCOILBRENTEU': 'brent_usd_bbl',
    'HOUST':    'us_housing_starts_k',
    'TTLCONS':  'us_construction_spend_musd',
}
LOG = []

def log(msg):
    LOG.append(msg); print(msg)

def fred_latest(series):
    if not FRED_KEY:
        return None, 'no-key'
    q = urllib.parse.urlencode({'series_id': series, 'api_key': FRED_KEY,
                                'file_type': 'json', 'sort_order': 'desc', 'limit': 1})
    try:
        req = urllib.request.Request('https://api.stlouisfed.org/fred/series/observations?' + q,
                                     headers={'User-Agent': 'brass-foresight/1.0'})
        with urllib.request.urlopen(req, timeout=30) as r:
            obs = json.load(r)['observations'][0]
        return (obs['date'], obs['value']), 'ok'
    except Exception as e:
        return None, f'fetch-fail: {type(e).__name__}'

def append_csv(path, row):
    new = not path.exists()
    with open(path, 'a', newline='') as f:
        w = csv.writer(f)
        if new:
            w.writerow(['retrieved', 'obs_date', 'series', 'value', 'status'])
        w.writerow(row)

def main():
    got, missed = 0, 0
    for sid, name in FRED_SERIES.items():
        (val, status) = fred_latest(sid)
        if val:
            append_csv(HERE / f'fred_{name}.csv', [TODAY, val[0], sid, val[1], status])
            got += 1
        else:
            append_csv(HERE / f'fred_{name}.csv', [TODAY, '', sid, '', status])
            missed += 1
    # ECB euro reference rates (free XML, no key): USD + INR per EUR
    try:
        import re as _re
        req = urllib.request.Request('https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml',
                                     headers={'User-Agent': 'brass-foresight/1.0'})
        with urllib.request.urlopen(req, timeout=30) as r:
            x = r.read().decode()
        day = _re.search(r"time='([\d-]+)'", x).group(1)
        got_ecb = 0
        for cur in ('USD', 'INR'):
            m = _re.search(r"currency='" + cur + r"' rate='([\d.]+)'", x)
            if m:
                append_csv(HERE / f'ecb_{cur.lower()}_per_eur.csv', [TODAY, day, 'ECB', m.group(1), 'ok'])
                got_ecb += 1
        got += got_ecb
        log(f'ECB ref rates {day}: captured {got_ecb}/2 (USD+INR per EUR)')
    except Exception as e:
        log(f'ECB ref rates failed ({type(e).__name__})')
        missed += 1
    # CFTC legacy COT via Socrata JSON (dataset 6dca-aqww = legacy, futures only).
    # Named fields beat the fixed-width deafut.txt, whose column offsets are ambiguous.
    try:
        url = ('https://publicreporting.cftc.gov/resource/6dca-aqww.json'
               '?$limit=1&$order=report_date_as_yyyy_mm_dd%20DESC'
               '&contract_market_name=COPPER-%20%231')
        req = urllib.request.Request(url, headers={'User-Agent': 'brass-foresight/1.0'})
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.load(r)
        if d:
            x = d[0]
            obs = x['report_date_as_yyyy_mm_dd'][:10]
            append_csv(HERE / 'cftc_copper_cmx.csv',
                       [TODAY, obs, '085692-CMX',
                        'OI={} NC_L={} NC_S={} SPR={} C_L={} C_S={}'.format(
                            x['open_interest_all'], x['noncomm_positions_long_all'],
                            x['noncomm_positions_short_all'], x['noncomm_postions_spread_all'],
                            x['comm_positions_long_all'], x['comm_positions_short_all']),
                        'ok'])
            got += 1
            log(f'CFTC COMEX copper COT captured ({obs})')
        else:
            missed += 1
            log('CFTC API returned no copper row — needs eyes')
    except Exception as e:
        log(f'CFTC COT failed ({type(e).__name__})')
        missed += 1
    # MCX bhavcopy: best effort (often bot-blocked); record outcome honestly
    try:
        req = urllib.request.Request('https://www.mcxindia.com/market-data/bhavcopy',
                                     headers={'User-Agent': 'brass-foresight/1.0'})
        with urllib.request.urlopen(req, timeout=30) as r:
            log(f'MCX bhavcopy page reachable (HTTP {r.status}); automated CSV parse not wired — manual download goes to data/mcx_manual/')
            got += 1
    except Exception as e:
        log(f'MCX bhavcopy blocked ({type(e).__name__}) — use manual download into data/mcx_manual/')
        missed += 1
    (HERE / 'mcx_manual').mkdir(exist_ok=True)
    log(f'DONE collected={got} missed={missed} (misses are retried tomorrow; nothing crashes)')

if __name__ == '__main__':
    main()
