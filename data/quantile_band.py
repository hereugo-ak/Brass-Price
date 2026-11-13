#!/usr/bin/env python3
"""Can we learn the WIDTH of the band instead of hard-coding it?

Today the band half-width is a single constant:
    risk_p95_30d = 25.8 INR/kg   (unconditional p95 of 4-week brass moves)
scaled by sqrt(cover/30).

A quantile regression replaces that constant with a conditional estimate:
    Q_tau(y_t+4 | X_t)  where X_t is what was known at t
so the band widens when the market is genuinely volatile and narrows when it is calm.

This script measures whether that is actually better. It does not assume it is.

Scoring
  pinball loss   proper scoring rule for a quantile (lower = better)
  coverage       share of outcomes inside the bound (target = 1 - alpha)
  width          average band width (narrower at equal coverage = better)

Baseline is the expanding empirical quantile — i.e. exactly what the product does
now. If the models cannot beat that, the constant stays.
"""
from __future__ import annotations

import collections
import csv
import json
import math
import pathlib
from statistics import mean

import numpy as np

HERE = pathlib.Path(__file__).parent
HORIZON = 4          # weeks, matches the product's 30-day cover
TAUS = (0.05, 0.95)
MIN_TRAIN = 120      # weeks before the first forecast
STEP = 4             # origin stride (every 4 weeks) — keeps the walk-forward affordable
GBR_STRIDE = 13      # the boosting model runs every 13th origin only


def load(sid, agg_mean=False):
    by = collections.defaultdict(list)
    with open(HERE / 'history' / f'{sid}.csv') as f:
        for r in csv.DictReader(f):
            try:
                by[r['date'][:10]].append(float(r['value']))
            except ValueError:
                pass
    return {k: (mean(v) if agg_mean else v[-1]) for k, v in by.items()}


def build():
    cu, zn, fx = load('PCOPPUSDM'), load('PZINCUSDM'), load('DEXINUS', True)
    import datetime
    days = sorted(fx)
    weeks = [d for d in days if datetime.date.fromisoformat(d).weekday() == 0]

    def on_or_before(s, d):
        past = [k for k in s if k <= d]
        return s[max(past)] if past else None

    leg, fxw = [], []
    for w in weeks:
        c, z, f = on_or_before(cu, w), on_or_before(zn, w), on_or_before(fx, w)
        if None in (c, z, f):
            continue
        leg.append((w, (0.615 * c + 0.385 * z) * f / 1000.0, f))

    rows = []
    for i in range(len(leg)):
        w, m, f = leg[i]
        rows.append({'week': w, 'leg': m, 'fx': f})

    # features known at t
    def changes(series, a, b):
        return [series[j] - series[j - 1] for j in range(max(1, a), b + 1)]

    out = []
    legs = [r['leg'] for r in rows]
    fxr = [r['fx'] for r in rows]
    for i in range(52, len(rows) - HORIZON):
        c26 = changes(legs, i - 25, i)
        c52 = changes(legs, i - 51, i)
        cfx = changes(fxr, i - 25, i)
        if len(c26) < 6 or len(c52) < 6:
            continue
        out.append({
            'week': rows[i]['week'],
            'leg': legs[i],
            'y': legs[i + HORIZON] - legs[i],
            # trailing state — nothing from the future
            'vol26': float(np.std(c26)),
            'vol52': float(np.std(c52)),
            'absmove4': abs(legs[i] - legs[i - 4]),
            'mom13': legs[i] / legs[i - 13] - 1 if i >= 13 and legs[i - 13] else 0.0,
            'mom26': legs[i] / legs[i - 26] - 1 if i >= 26 and legs[i - 26] else 0.0,
            'fxvol26': float(np.std(cfx)),
            'level': legs[i],
        })
    return out


FEATURES = ['vol26', 'vol52', 'absmove4', 'mom13', 'mom26', 'fxvol26', 'level']


def pinball(y, pred, tau):
    d = np.asarray(y) - np.asarray(pred)
    return float(np.mean(np.maximum(tau * d, (tau - 1) * d)))


def run(rows, h_label='metal-leg 4-week change (INR/kg)'):
    y = np.array([r['y'] for r in rows])
    X = np.array([[r[f] for f in FEATURES] for r in rows])
    n = len(rows)
    print(f'target      : {h_label}')
    print(f'observations: {n}   features: {len(FEATURES)}   horizon: {HORIZON} weeks\n')

    from sklearn.linear_model import QuantileRegressor
    from sklearn.ensemble import GradientBoostingRegressor

    results = {t: {m: {'pinball': [], 'cov': [], 'width': []}
                   for m in ('unconditional', 'qreg', 'gbr')} for t in TAUS}

    for k, i in enumerate(range(MIN_TRAIN, n, STEP)):
        tr = slice(0, i)
        mu, sd = X[tr].mean(0), X[tr].std(0)
        sd[sd == 0] = 1.0
        Xtr = (X[tr] - mu) / sd
        Xte = ((X[i] - mu) / sd).reshape(1, -1)
        ytr, yte = y[tr], y[i]

        for tau in TAUS:
            # baseline: exactly what the product does now
            p_base = float(np.quantile(ytr, tau))
            preds = {'unconditional': p_base}

            # linear quantile regression
            try:
                qr = QuantileRegressor(quantile=tau, alpha=0.0, solver='highs')
                qr.fit(Xtr, ytr)
                preds['qreg'] = float(qr.predict(Xte)[0])
            except Exception:
                preds['qreg'] = p_base

            # gradient boosting on the quantile loss (costly: every Nth origin)
            if k % GBR_STRIDE == 0:
                try:
                    gb = GradientBoostingRegressor(loss='quantile', alpha=tau,
                                                   n_estimators=60, learning_rate=0.08,
                                                   max_depth=2, random_state=7)
                    gb.fit(Xtr, ytr)
                    preds['gbr'] = float(gb.predict(Xte)[0])
                except Exception:
                    preds['gbr'] = p_base

            for name, p in preds.items():
                if name == 'gbr' and k % GBR_STRIDE != 0:
                    continue
                results[tau][name]['pinball'].append(pinball([yte], [p], tau))
                results[tau][name]['cov'].append(bool(yte <= p) if tau > 0.5
                                                 else bool(yte >= p))
                # width contributed by this tail
                results[tau][name]['width'].append(abs(p))

    print(f"{'tau':>5} {'model':>15} {'pinball':>9} {'coverage':>9} {'target':>7} {'mean |q|':>9}")
    summary = {}
    for tau in TAUS:
        for name in ('unconditional', 'qreg', 'gbr'):
            r = results[tau][name]
            pb = mean(r['pinball'])
            cov = sum(r['cov']) / len(r['cov'])
            w = mean(r['width'])
            summary[f'{tau}:{name}'] = {'pinball': round(pb, 3),
                                        'coverage': round(cov, 4),
                                        'mean_abs_quantile': round(w, 2),
                                        'n': len(r['pinball'])}
            print(f'{tau:>5} {name:>15} {pb:>9.3f} {cov:>9.3f} {tau if tau>0.5 else 1-tau:>7.2f} {w:>9.2f}')

    # combined band for the two tails
    print(f"\n{'model':>15} {'total pinball':>14} {'band width':>12} {'coverage 90%':>13}")
    comb = {}
    for name in ('unconditional', 'qreg', 'gbr'):
        pb = summary[f'0.05:{name}']['pinball'] + summary[f'0.95:{name}']['pinball']
        width = summary[f'0.05:{name}']['mean_abs_quantile'] + summary[f'0.95:{name}']['mean_abs_quantile']
        cov = (summary[f'0.05:{name}']['coverage'] + summary[f'0.95:{name}']['coverage']) / 2
        comb[name] = {'pinball': round(pb, 3), 'width': round(width, 2),
                      'coverage': round(cov, 4)}
        print(f'{name:>15} {pb:>14.3f} {width:>12.2f} {cov:>13.3f}')

    base = comb['unconditional']
    best = min((v['pinball'], k) for k, v in comb.items() if k != 'unconditional')
    verdict = 'BEATS' if best[0] < base['pinball'] else 'LOSES TO'
    print(f"\nbest challenger: {best[1]}  pinball {best[0]:.3f} vs unconditional "
          f"{base['pinball']:.3f}  -> {verdict} the baseline")
    summary['_combined'] = comb
    summary['_verdict'] = {'best': best[1], 'beats_baseline': best[0] < base['pinball']}
    return summary


if __name__ == '__main__':
    rows = build()
    s = run(rows)
    (HERE / 'quantile_band_results.json').write_text(json.dumps(s, indent=1),
                                                     encoding='utf-8')
    print('\n-> data/quantile_band_results.json')
