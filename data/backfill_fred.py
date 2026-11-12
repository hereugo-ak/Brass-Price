#!/usr/bin/env python3
"""Pull FULL history for each FRED series into data/history/. Needs FRED_API_KEY in ../.env.
Usage: python3 backfill_fred.py
"""
import csv, json, os, pathlib, urllib.request, urllib.parse

HERE = pathlib.Path(__file__).parent
HIST = HERE / 'history'
HIST.mkdir(exist_ok=True)

def load_dotenv():
    p = HERE.parent / '.env'
    if p.exists():
        for line in p.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())

SERIES = ['DEXINUS', 'DEXUSEU', 'PCOPPUSDM', 'PZINCUSDM', 'DCOILBRENTEU', 'HOUST', 'TTLCONS']

def main():
    load_dotenv()
    key = os.environ.get('FRED_API_KEY', '')
    if not key or key == 'PASTE_YOUR_FREE_KEY_HERE':
        print('STOP: put your free key in Brass/.env first (FRED_API_KEY=...). No calls made.')
        return
    for sid in SERIES:
        q = urllib.parse.urlencode({'series_id': sid, 'api_key': key, 'file_type': 'json'})
        try:
            req = urllib.request.Request('https://api.stlouisfed.org/fred/series/observations?' + q,
                                         headers={'User-Agent': 'brass-foresight/1.0'})
            with urllib.request.urlopen(req, timeout=60) as r:
                obs = json.load(r)['observations']
            rows = [(o['date'], o['value']) for o in obs if o['value'] != '.']
            with open(HIST / f'{sid}.csv', 'w', newline='') as f:
                w = csv.writer(f); w.writerow(['date', 'value']); w.writerows(rows)
            print(f'{sid}: {len(rows)} rows ({rows[0][0]}..{rows[-1][0]})')
        except Exception as e:
            print(f'{sid}: FAILED ({type(e).__name__}) — retry later, nothing half-written')

if __name__ == '__main__':
    main()
