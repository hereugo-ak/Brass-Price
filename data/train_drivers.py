#!/usr/bin/env python3
"""Train real models on the 72-driver map — using only series we actually hold.

TARGET
    WPI brass index, commodity 1314090011 (base 2011-12=100), monthly,
    169 observations 2012-04 -> 2026-04. Real domestic Indian brass.

DRIVERS ACTUALLY AVAILABLE (from output/data_catalogue.csv → data files)
    IMF copper, IMF zinc, USD/INR, USD/EUR, Brent, US housing starts,
    US construction spend, MCX copper, MCX zinc  (monthly aggregated)

DRIVERS IDENTIFIED BUT NOT COLLECTED (so NOT used, and that is recorded):
    LME official/3M/stocks, LME COTR, SHFE stocks, PMI, ocean freight,
    TC/RC, USGS, HBM/HCL output, IBM ASP, CBAM price, policy rates, CPI,
    OPEC MOMR, ABS approvals, RBA. 18 catalogue entries have no data file.

LEAKAGE
    index at t-1 (WPI publishes ~14 days after month end)
    metals/macro at t-2 (IMF monthly publishes ~2 months late)
    verified in data/LEAK_MAP.md

Usage: python3 train_drivers.py
"""
import collections
import csv
import json
import math
import pathlib
from statistics import mean

import numpy as np

HERE = pathlib.Path(__file__).parent

HORIZONS = (1, 2, 3)
MIN_TRAIN = 60
LAG_INDEX = 1
LAG_MACRO = 2


def load_monthly(sid, agg='last'):
    by = collections.defaultdict(list)
    with open(HERE / 'history' / f'{sid}.csv') as f:
        for r in csv.DictReader(f):
            try:
                by[r['date'][:7]].append(float(r['value']))
            except ValueError:
                pass
    if agg == 'mean':
        return {k: mean(v) for k, v in by.items()}
    return {k: v[-1] for k, v in by.items()}


def load_manual_monthly(path, col):
    by = collections.defaultdict(list)
    p = HERE / 'manual' / path
    if not p.exists():
        return {}
    with open(p) as f:
        for r in csv.DictReader(f):
            try:
                by[r['date'][:7]].append(float(r[col]))
            except (ValueError, KeyError):
                pass
    return {k: mean(v) for k, v in by.items()}


def build():
    target = {}
    with open(HERE / 'manual' / 'wpi_brass_monthly.csv') as f:
        for r in csv.DictReader(f):
            try:
                target[r['month']] = float(r['brass_index'])
            except (TypeError, ValueError):
                pass

    cu = load_monthly('PCOPPUSDM')
    zn = load_monthly('PZINCUSDM')
    fx = load_monthly('DEXINUS', 'mean')
    eu = load_monthly('DEXUSEU', 'mean')
    br = load_monthly('DCOILBRENTEU', 'mean')
    hs = load_monthly('HOUST')
    tc = load_monthly('TTLCONS')
    mcu = load_manual_monthly('mcx_copper_zinc_daily.csv', 'close_inr')
    mzn = collections.defaultdict(list)
    with open(HERE / 'manual' / 'mcx_copper_zinc_daily.csv') as f:
        for r in csv.DictReader(f):
            if r.get('symbol') == 'ZINC':
                try:
                    mzn[r['date'][:7]].append(float(r['close_inr']))
                except (ValueError, KeyError):
                    pass
    mzn = {k: mean(v) for k, v in mzn.items()}

    months = sorted(target)
    rows = []
    for i, m in enumerate(months):
        if i < 14:
            continue
        # ---- availability
        mi = months[i - LAG_INDEX]                      # index lag 1
        mm = months[i - LAG_MACRO]                      # macro lag 2
        f = {'month': m}
        if mi not in target or mm not in cu or mm not in zn or mm not in fx:
            continue
        f['idx_lag1'] = target[mi]
        for L in (2, 3, 6, 12):
            if i - LAG_INDEX - L + 1 >= 0:
                src = months[i - LAG_INDEX - L + 1]
                if src in target:
                    f[f'idx_lag{L}'] = target[src]
        for L in (3, 6, 12):
            k = f'idx_lag{L}'
            if k in f:
                f[f'mom{L}'] = f['idx_lag1'] / f[k] - 1
        f['cu'] = cu[mm]
        f['zn'] = zn[mm]
        f['fx'] = fx[mm]
        f['metal'] = (0.615 * cu[mm] + 0.385 * zn[mm]) * fx[mm] / 1000.0
        if mm in br:
            f['brent'] = br[mm]
        if mm in hs:
            f['houst'] = hs[mm]
        if mm in tc:
            f['ttlcons'] = tc[mm]
        if mm in eu:
            f['eur'] = eu[mm]
        if mm in mcu:
            f['mcx_cu'] = mcu[mm]
        if mm in mzn:
            f['mcx_zn'] = mzn[mm]
        # momentum of the metal leg
        m2 = months[i - LAG_MACRO - 3] if i - LAG_MACRO - 3 >= 0 else None
        if m2 and m2 in cu and m2 in zn and m2 in fx:
            prev = (0.615 * cu[m2] + 0.385 * zn[m2]) * fx[m2] / 1000.0
            f['metal_mom3'] = f['metal'] / prev - 1
        f['y'] = target[m]
        rows.append(f)
    return rows


FEATURES = ['idx_lag1', 'idx_lag2', 'idx_lag3', 'idx_lag6', 'idx_lag12',
            'mom3', 'mom6', 'mom12', 'cu', 'zn', 'fx', 'metal', 'metal_mom3',
            'brent', 'houst', 'ttlcons', 'eur', 'mcx_cu', 'mcx_zn']


def matrix(rows, feats):
    out = []
    for r in rows:
        if any(k not in r for k in feats):
            return None, None
        out.append([r[k] for k in feats])
    y = [r['y'] for r in rows]
    return np.array(out, dtype=float), np.array(y, dtype=float)


def naive_pred(vals, i, h):
    return vals[i]


def drift_pred(vals, i, h):
    if i < 12:
        return vals[i]
    return vals[i] + (vals[i] - vals[i - 12]) / 12.0 * h


def dm_test(e1, e2):
    """Diebold-Mariano on absolute errors. Positive => model 2 better."""
    d = [abs(a) - abs(b) for a, b in zip(e1, e2)]
    n = len(d)
    m = mean(d)
    sd = (sum((x - m) ** 2 for x in d) / (n - 1)) ** 0.5
    return m / (sd / math.sqrt(n)) if sd else 0.0


def run_sklearn(rows, h, feats):
    from sklearn.linear_model import Ridge, Lasso
    from sklearn.ensemble import (RandomForestRegressor, GradientBoostingRegressor,
                                  HistGradientBoostingRegressor)
    X, y = matrix(rows, feats)
    if X is None:
        return None
    vals = [r['y'] for r in rows]
    n = len(rows)
    models = {
        'ridge0.1': lambda: Ridge(alpha=0.1),
        'ridge1': lambda: Ridge(alpha=1.0),
        'ridge10': lambda: Ridge(alpha=10.0),
        'ridge100': lambda: Ridge(alpha=100.0),
        'lasso0.01': lambda: Lasso(alpha=0.01, max_iter=5000),
        'rf': lambda: RandomForestRegressor(n_estimators=300, max_depth=4,
                                            min_samples_leaf=3, random_state=7),
        'gbr': lambda: GradientBoostingRegressor(n_estimators=200, learning_rate=0.05,
                                                 max_depth=3, random_state=7),
        'hgb': lambda: HistGradientBoostingRegressor(max_iter=200, learning_rate=0.05,
                                                     max_depth=3, random_state=7),
    }
    errs = collections.defaultdict(list)
    errs['naive'] = []
    errs['drift12'] = []
    preds = collections.defaultdict(list)
    for i in range(MIN_TRAIN, n - h):
        tr = slice(0, i)
        target = y[i + h]
        errs['naive'].append(target - naive_pred(vals, i, h))
        errs['drift12'].append(target - drift_pred(vals, i, h))
        for name, mk in models.items():
            mu = X[tr].mean(axis=0)
            sd = X[tr].std(axis=0)
            sd[sd == 0] = 1.0
            Xtr = (X[tr] - mu) / sd
            Xte = (X[i:i + 1] - mu) / sd
            try:
                mdl = mk()
                mdl.fit(Xtr, y[tr])
                p = float(mdl.predict(Xte)[0])
            except Exception:
                p = vals[i]
            errs[name].append(target - p)
            preds[name].append((rows[i]['month'], p, target))
    return errs, preds, n - h - MIN_TRAIN


def score(e):
    a = [abs(x) for x in e]
    return {'n': len(e), 'MAE': round(mean(a), 2),
            'RMSE': round((mean([x * x for x in a])) ** 0.5, 2),
            'dir_hit': round(sum(1 for x in e if x > 0) / len(e), 3)}


def main():
    rows = build()
    print(f'target: WPI brass index · {len(rows)} usable months '
          f'({rows[0]["month"]} -> {rows[-1]["month"]})')
    have = [f for f in FEATURES if all(f in r for r in rows)]
    print(f'features actually available: {len(have)} -> {have}')
    print(f'features dropped (not collected): '
          f'{[f for f in FEATURES if f not in have]}\n')

    out = {'target': 'WPI brass index 1314090011', 'rows': len(rows),
           'features_used': have,
           'features_missing_because_not_collected':
               [f for f in FEATURES if f not in have],
           'horizons': {}}

    for h in HORIZONS:
        res = run_sklearn(rows, h, have)
        if not res:
            continue
        errs, preds, nf = res
        print(f'--- horizon {h} month(s), {nf} walk-forward forecasts ---')
        print(f'{"model":>12} {"n":>5} {"MAE":>8} {"RMSE":>8} {"dir":>6} {"DM vs naive":>12}')
        base = errs['naive']
        table = {}
        for name in ['naive', 'drift12', 'ridge0.1', 'ridge1', 'ridge10', 'ridge100',
                     'lasso0.01', 'rf', 'gbr', 'hgb']:
            if name not in errs:
                continue
            s = score(errs[name])
            dm = None if name == 'naive' else round(dm_test(base, errs[name]), 2)
            s['dm_vs_naive'] = dm
            table[name] = s
            print(f'{name:>12} {s["n"]:>5} {s["MAE"]:>8.2f} {s["RMSE"]:>8.2f} '
                  f'{s["dir_hit"]:>6.3f} {("" if dm is None else f"{dm:+.2f}"):>12}')
        best = min((v['MAE'], k) for k, v in table.items() if k != 'naive')
        print(f'  best challenger: {best[1]} MAE {best[0]:.2f} '
              f'vs naive {table["naive"]["MAE"]:.2f} -> '
              f'{"BEATS naive" if best[0] < table["naive"]["MAE"] else "naive WINS"}\n')
        out['horizons'][h] = {'n_forecasts': nf, 'scores': table,
                              'best': best[1]}

    (HERE / 'drivers_results.json').write_text(json.dumps(out, indent=1), encoding='utf-8')
    print('-> data/drivers_results.json')


if __name__ == '__main__':
    main()
