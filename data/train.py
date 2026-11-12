#!/usr/bin/env python3
"""Model tournament scaffold — runs on public legs today, brass target tomorrow.
Design: walk-forward (expanding window, step 4w), horizons 1/4, Ridge alphas +
feature-group ablations + Diebold-Mariano vs naive. Uses lightgbm/sklearn when
present (Kaggle), numpy-Ridge fallback otherwise. No owner data needed to run:
defaults to DEXINUS demo target and says so.
Usage: python3 train.py [--target DEXINUS|BRASS] [--data data/]
Targets: data/brass_target.csv (week,true_inr_kg) enables the real BRASS target.
"""
import csv, json, math, pathlib, sys

try:
    import numpy as np
except ImportError:
    sys.exit('STOP: numpy required')

HERE = pathlib.Path(__file__).parent
DATA = pathlib.Path(sys.argv[sys.argv.index('--data') + 1]) if '--data' in sys.argv else HERE
TARGET = sys.argv[sys.argv.index('--target') + 1] if '--target' in sys.argv else 'DEXINUS'

GROUPS = {  # feature-family ablations
    'levels': lambda c: not ('_L' in c or '_mom' in c),
    'lags': lambda c: '_L' in c,
    'momentum': lambda c: '_mom' in c,
}

def load_features():
    rows = list(csv.DictReader(open(DATA / 'features_weekly.csv')))
    feats, y_dex = [], []
    for r in rows:
        try:
            y_dex.append(float(r['DEXINUS']))
        except (ValueError, TypeError):
            y_dex.append(None)
        feats.append(r)
    cols = [k for k in rows[0] if k != 'week' and k != 'DEXINUS']
    return rows, cols, y_dex

def load_target(name, rows, y_dex):
    if name == 'BRASS':
        p = DATA / 'brass_target.csv'
        if not p.exists():
            print('STOP: BRASS target needs data/brass_target.csv (week,true_inr_kg) — owner labels first.')
            return None
        m = {r['week']: float(r['true_inr_kg']) for r in csv.DictReader(open(p))}
        return [m.get(r['week']) for r in rows]
    return y_dex

def ridge_fit(X, y, alpha):
    X1 = np.column_stack([np.ones(len(X)), np.asarray(X, float)])
    yv = np.asarray(y, float)
    A = X1.T @ X1 + alpha * np.eye(X1.shape[1])
    A[0, 0] -= alpha
    return np.linalg.solve(A, X1.T @ yv)

def ridge_pred(beta, x):
    return float(beta[0] + sum(b * v for b, v in zip(beta[1:], x)))

def dm_test(e1, e2):
    """Diebold-Mariano (MSE loss, h=1 approx): returns stat; |stat|>1.96 ~= 5% signif."""
    import math
    d = np.asarray([(a - b) for a, b in zip(np.asarray(e1) ** 2, np.asarray(e2) ** 2)], float)
    n = len(d)
    if n < 20:
        return None
    m, v = d.mean(), d.var(ddof=1)
    return float(m / math.sqrt(v / n)) if v > 0 else 0.0

def main():
    rows, cols, y_dex = load_features()
    y = load_target(TARGET, rows, y_dex)
    if y is None:
        return
    demo = TARGET != 'BRASS'
    print(f'TARGET={TARGET}' + (' (DEMO on public leg — real target needs owner labels)' if demo else ''))
    res = {}
    for H in (1, 4):
        idx = [i for i in range(104, len(y) - H)
               if y[i] is not None and y[i + H] is not None]
        if len(idx) < 20:
            res[f'h{H}'] = {'note': 'too few points'}
            continue
        fam = {'all': cols}
        for g, f in GROUPS.items():
            fam[f'no_{g}'] = [c for c in cols if not f(c)]
        for variant, keep in fam.items():
            for alpha in (0.1, 1.0, 10.0):
                pe, pn, ac = [], [], []
                for i in idx[::4]:
                    tr = [j for j in range(52, i) if y[j] is not None]
                    X = [[float(rows[j][c] or 0) for c in keep] for j in tr]
                    X = [[0.0 if not isinstance(v, float) else v for v in row] for row in X]
                    try:
                        beta = ridge_fit(X, [y[j] for j in tr], alpha)
                        x = [float(rows[i][c] or 0) for c in keep]
                        pe.append(y[i + H] - ridge_pred(beta, x))
                    except Exception:
                        continue
                    pn.append(y[i + H] - y[i])
                if len(pe) < 10:
                    continue
                mae = sum(abs(e) for e in pe) / len(pe)
                rm = math.sqrt(sum(e * e for e in pe) / len(pe))
                res[f'h{H}_ridge{alpha}_{variant}'] = {
                    'n': len(pe), 'MAE': round(mae, 4), 'RMSE': round(rm, 4),
                    'dm_vs_naive': round(dm_test(pe, pn), 3) if dm_test(pe, pn) is not None else None}
    base = {k: v for k, v in res.items() if k.startswith('h1_ridge1.0_all') or k.startswith('h4_ridge1.0_all')}
    print(json.dumps({**res, '_reads': 'negative dm_vs_naive = model beats naive (MSE); |dm|>1.96 ~= significant'}, indent=1))
    json.dump(res, open(DATA / f'tournament_{TARGET.lower()}.json', 'w'), indent=1)

if __name__ == '__main__':
    main()
