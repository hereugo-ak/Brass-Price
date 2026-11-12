#!/usr/bin/env python3
"""Build weekly feature table from data/history/*.csv -> data/features_weekly.csv
Features per series: level, lags 1/2/4/8 weeks, 4-week momentum. Friday-anchored.
Usage: python3 make_features.py
"""
import csv, pathlib
from datetime import date

HERE = pathlib.Path(__file__).parent
HIST = HERE / 'history'

def load(sid):
    p = HIST / f'{sid}.csv'
    if not p.exists():
        return {}
    out = {}
    with open(p) as f:
        for r in csv.DictReader(f):
            try:
                out[date.fromisoformat(r['date'])] = float(r['value'])
            except ValueError:
                pass
    return out

def fridays(days):
    return sorted(d for d in days if d.weekday() == 4)

def main():
    if not HIST.exists() or not any(HIST.glob('*.csv')):
        print('STOP: no history yet — run backfill_fred.py with a key first.')
        return
    series = {s: load(s) for s in ['DEXINUS', 'DEXUSEU', 'PCOPPUSDM', 'PZINCUSDM', 'DCOILBRENTEU']}
    all_days = sorted(set().union(*[set(v) for v in series.values()]))
    weeks = fridays(all_days)
    if len(weeks) < 12:
        print(f'STOP: only {len(weeks)} Fridays — need 12+ for lags. More history required.')
        return
    # last observation carried forward within each week is approximated by Friday value
    rows = []
    for i, w in enumerate(weeks):
        row = {'week': w.isoformat()}
        for sid, vals in series.items():
            v = vals.get(w)
            if v is None:  # monthly series: use latest available on/before Friday
                past = [d for d in vals if d <= w]
                v = vals[max(past)] if past else ''
            row[sid] = v
            for L in (1, 2, 4, 8):
                pv = ''
                if i >= L:
                    pv = rows[i - L][sid] if isinstance(rows[i - L][sid], float) else ''
                row[f'{sid}_L{L}'] = pv
            try:
                row[f'{sid}_mom4'] = round(float(v) / float(rows[i - 4][sid]) - 1, 6) if i >= 4 and rows[i - 4][sid] != '' else ''
            except (ValueError, ZeroDivisionError, TypeError):
                row[f'{sid}_mom4'] = ''
        rows.append(row)
    cols = ['week'] + [k for k in rows[0] if k != 'week']
    with open(HERE / 'features_weekly.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    print(f'OK: {len(rows)} weekly rows -> data/features_weekly.csv')

if __name__ == '__main__':
    main()
