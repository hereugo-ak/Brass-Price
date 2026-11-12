#!/usr/bin/env python3
"""Naive baselines on DEXINUS weekly closes (walk-forward, the bar every model must beat).
Metrics: MAE, RMSE, directional hit-rate for 1-week and 4-week horizons.
Usage: python3 baseline.py
"""
import csv, json, math, pathlib

HERE = pathlib.Path(__file__).parent

def main():
    p = HERE / 'features_weekly.csv'
    if not p.exists():
        print('STOP: run make_features.py first.')
        return
    rows = list(csv.DictReader(open(p)))
    y = []
    for r in rows:
        try:
            y.append(float(r['DEXINUS']))
        except (ValueError, TypeError):
            y.append(None)
    out = {}
    for H in (1, 4):
        preds_n, preds_s, actuals = [], [], []
        for i in range(60, len(y) - H):
            if y[i] is None or y[i + H] is None:
                continue
            preds_n.append(y[i])
            preds_s.append(y[i - 51] if i >= 51 and y[i - 51] is not None else y[i])
            actuals.append(y[i + H])
        if len(actuals) < 20:
            out[f'h{H}'] = {'n': len(actuals), 'note': 'too few points — more history needed'}
            continue
        for tag, pr in (('naive', preds_n), ('seasonal52', preds_s)):
            err = [a - x for a, x in zip(actuals, pr)]
            mae = sum(abs(e) for e in err) / len(err)
            rmse = math.sqrt(sum(e * e for e in err) / len(err))
            scored = [(actuals[k] - actuals[k - 1]) * (pr[k] - actuals[k - 1])
                      for k in range(1, len(actuals)) if pr[k] != actuals[k - 1]]
            hits = sum(1 for v in scored if v > 0)
            out[f'h{H}_{tag}'] = {'n': len(actuals), 'MAE': round(mae, 4),
                                  'RMSE': round(rmse, 4),
                                  'dir_hit': round(hits / len(scored), 3) if scored else None,
                                  'dir_note': '1-step naive has no direction by construction' if not scored else ''}
    json.dump(out, open(HERE / 'baseline_metrics.json', 'w'), indent=1)
    print(json.dumps(out, indent=1))
    print('Write this down: every future model must beat naive MAE above, or it ships nothing.')

if __name__ == '__main__':
    main()
