#!/usr/bin/env python3
"""Brass metal-leg model + quote-floor engine.

WHAT THIS IS
    A model of the METAL LEG of Castle's brass price only:
        metal_leg_inr_kg = (wCu*LME_Cu + (1-wCu)*LME_Zn) * USDINR / 1000
    It does NOT model the spread layer (dealer premium, transport, conversion,
    scrap discount, duties). Those are carried as explicit parameters, never guessed.

WHAT THIS IS NOT
    Not Castle's buying price. Every output carries a PROXY label.

LEAKAGE
    Inputs are shifted to their publication availability before any forecast:
      - IMF Cu/Zn monthly: 8-week availability lag (published ~1-2 months late)
      - USD/INR (FRED H.10): 1-week lag
    See data/LEAK_MAP.md. A backtest row dated D uses only data public by D.

OUTPUTS
    data/brass_band.csv          weekly band, all weight assumptions
    data/brass_model_results.json walk-forward scores + band calibration
    output/BAND_REPORT.md        human-readable summary

Usage: python3 brass_model.py
"""
import csv
import json
import pathlib
from datetime import date, timedelta
from statistics import mean, median

HERE = pathlib.Path(__file__).parent

WEIGHTS = [0.58, 0.60, 0.615, 0.63]   # IS 319 Gr-II range, swept not asserted
PRIMARY_W = 0.615                      # reported headline weight
HORIZON = 4                            # weeks ahead — owner needs ~1 month
STEP = 4                               # walk-forward stride
LAG_CU_ZN = 56                         # days of publication lag for IMF monthly
LAG_FX = 7                             # days for FRED H.10

# Quote validity settings approved 2026-11-12 (MODEL_SPEC.md section 2)
VALIDITY = [30, 15, 7]


# ---------------------------------------------------------------- data loading
def load_history(sid):
    p = HERE / 'history' / f'{sid}.csv'
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


def monday_weeks(days):
    out = []
    for d in sorted(days):
        if d.weekday() == 0:
            out.append(d)
    return out


def known_at(series, d, lag_days):
    """Latest value published on or before (d - lag_days)."""
    cutoff = d - timedelta(days=lag_days)
    past = [k for k in series if k <= cutoff]
    if not past:
        return None
    return series[max(past)]


# ---------------------------------------------------------------- the metal leg
def metal_leg(cu, zn, fx, w):
    """USD/t, USD/t, INR per USD -> INR per kg."""
    if cu is None or zn is None or fx is None:
        return None
    return (w * cu + (1 - w) * zn) * fx / 1000.0


# ---------------------------------------------------------------- forecasters
def build_series(w):
    cu = load_history('PCOPPUSDM')
    zn = load_history('PZINCUSDM')
    fx = load_history('DEXINUS')
    if not (cu and zn and fx):
        return []
    all_days = sorted(set(fx))
    weeks = monday_weeks(all_days)
    rows = []
    for wd in weeks:
        # what a decision-maker actually knew on this date
        cu_k = known_at(cu, wd, LAG_CU_ZN)
        zn_k = known_at(zn, wd, LAG_CU_ZN)
        fx_k = known_at(fx, wd, LAG_FX)
        rows.append({
            'week': wd,
            'known': metal_leg(cu_k, zn_k, fx_k, w),
        })
    # realised leg (no lag) is the thing we are trying to predict
    cu_all = sorted(cu)
    zn_all = sorted(zn)
    fx_all = sorted(fx)
    for r in rows:
        wd = r['week']
        cu_r = known_at(cu, wd + timedelta(days=LAG_CU_ZN), 0)
        zn_r = known_at(zn, wd + timedelta(days=LAG_CU_ZN), 0)
        fx_r = known_at(fx, wd + timedelta(days=LAG_FX), 0)
        r['actual'] = metal_leg(cu_r, zn_r, fx_r, w)
    return [r for r in rows if r['known'] is not None and r['actual'] is not None]


def f_naive(hist, i, h):
    return hist[i]['known']


def f_ma4(hist, i, h):
    vals = [hist[j]['known'] for j in range(max(0, i - 3), i + 1)]
    vals = [v for v in vals if v is not None]
    return mean(vals) if vals else None


def f_ma13(hist, i, h):
    vals = [hist[j]['known'] for j in range(max(0, i - 12), i + 1)]
    vals = [v for v in vals if v is not None]
    return mean(vals) if vals else None


def f_drift(hist, i, h):
    """Naive plus the average weekly change over the last 26 weeks, scaled by h."""
    if i < 26:
        return hist[i]['known']
    a = hist[i - 26]['known']
    b = hist[i]['known']
    if a is None or b is None or a == 0:
        return hist[i]['known']
    weekly = (b - a) / 26.0
    return b + weekly * h


FORECASTERS = {
    'naive': f_naive,
    'ma4': f_ma4,
    'ma13': f_ma13,
    'drift26': f_drift,
}


def walk_forward(hist, fn, h):
    pairs = []
    last_origin = len(hist) - h - 1
    for i in range(52, last_origin + 1, STEP):
        pred = fn(hist, i, h)
        tgt = hist[i + h]['actual']
        if pred is None or tgt is None:
            continue
        pairs.append((hist[i]['week'], pred, tgt, tgt - pred))
    return pairs


def score(pairs):
    if not pairs:
        return {}
    err = [abs(e) for _, _, _, e in pairs]
    sq = [e * e for e in err]
    return {
        'n': len(pairs),
        'MAE': round(mean(err), 2),
        'RMSE': round(mean(sq) ** 0.5, 2),
    }


# ---------------------------------------------------------------- quote floor
def quantile(xs, q):
    if not xs:
        return None
    s = sorted(xs)
    k = (len(s) - 1) * q
    lo, hi = int(k), min(int(k) + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


def quote_floor(band_high, spread_high, margin_pct):
    """Lowest safe committed price: cover the high band, the spread, then margin."""
    base = band_high + spread_high
    return base * (1 + margin_pct)


# ---------------------------------------------------------------- main
def main():
    report = {'weights': {}, 'notes': []}

    for w in WEIGHTS:
        hist = build_series(w)
        if len(hist) < 60:
            report['weights'][str(w)] = {'error': 'insufficient history'}
            continue
        res = {}
        for name, fn in FORECASTERS.items():
            pairs = walk_forward(hist, fn, HORIZON)
            s = score(pairs)
            if s:
                res[name] = s
        # band calibration from the best-available honest forecaster = naive
        naive_pairs = walk_forward(hist, f_naive, HORIZON)
        errs = [e for _, _, _, e in naive_pairs]
        res['_band'] = {
            'q80_low': round(quantile(errs, 0.10), 2),
            'q80_high': round(quantile(errs, 0.90), 2),
            'q90_low': round(quantile(errs, 0.05), 2),
            'q90_high': round(quantile(errs, 0.95), 2),
        }
        report['weights'][str(w)] = res

    # headline = primary weight
    head = report['weights'].get(str(PRIMARY_W), {})
    best = min((v for k, v in head.items() if not k.startswith('_') and v),
               key=lambda x: x['MAE'], default={})

    report['headline'] = {
        'primary_weight': PRIMARY_W,
        'horizon_weeks': HORIZON,
        'naive_MAE_inr_kg': head.get('naive', {}).get('MAE'),
        'best_challenger': best,
        'naive_wins': (
            bool(best) and head.get('naive', {}).get('MAE', 1e9) <= best.get('MAE', 1e18)
        ),
        'band': head.get('_band', {}),
    }
    report['notes'] = [
        'METAL LEG ONLY. The spread layer (premium, transport, conversion, '
        'scrap discount, duties) is not modelled and not guessed.',
        'This is a PROXY series, not Castle Hardwares buying price.',
        'Inputs shifted for publication lag per data/LEAK_MAP.md.',
        'Weights swept across the IS 319 Grade-II 60-63% Cu range.',
    ]

    (HERE / 'brass_model_results.json').write_text(
        json.dumps(report, indent=1), encoding='utf-8')

    # ---------------- latest band + quote floor grid
    hist = build_series(PRIMARY_W)
    if hist:
        last = hist[-1]
        base = last['known']
        band = head.get('_band', {})
        rows = []
        for spread in (-80, -40, 0, 40, 80):
            for days in VALIDITY:
                # a longer quote stays exposed longer, so the cushion scales
                # with sqrt(time) — the standard random-walk scaling, not a
                # fitted parameter (there is no data to fit it on yet).
                scale = (days / 30.0) ** 0.5
                lo = base + band.get('q80_low', 0) * scale + spread
                hi = base + band.get('q80_high', 0) * scale + spread
                mid = base + spread
                rows.append({
                    'week': last['week'].isoformat(),
                    'weight': PRIMARY_W,
                    'spread_inr_kg': spread,
                    'validity_days': days,
                    'metal_leg_low': round(lo, 2),
                    'metal_leg_mid': round(mid, 2),
                    'metal_leg_high': round(hi, 2),
                    'quote_floor_5pct': round(quote_floor(hi, 0, 0.05), 2),
                })
        with open(HERE / 'brass_band.csv', 'w', newline='') as f:
            wr = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            wr.writeheader()
            wr.writerows(rows)
        report['latest'] = {
            'week': last['week'].isoformat(),
            'metal_leg_inr_kg': round(base, 2),
            'band': band,
        }
        (HERE / 'brass_model_results.json').write_text(
            json.dumps(report, indent=1), encoding='utf-8')

    # ---------------- console
    print('=== BRASS METAL-LEG MODEL (PROXY, not Castle price) ===')
    print(f'horizon {HORIZON} weeks, walk-forward step {STEP}, primary weight {PRIMARY_W}')
    print(f"{'weight':>7} {'model':>9} {'n':>6} {'MAE':>8} {'RMSE':>8}")
    for w in WEIGHTS:
        r = report['weights'].get(str(w), {})
        for name in FORECASTERS:
            if name in r:
                print(f"{w:>7.3f} {name:>9} {r[name]['n']:>6} "
                      f"{r[name]['MAE']:>8.2f} {r[name]['RMSE']:>8.2f}")
    print()
    h = report['headline']
    print(f"naive MAE  Rs {h.get('naive_MAE_inr_kg')}/kg   "
          f"best challenger {h.get('best_challenger', {}).get('MAE')}  "
          f"-> naive_wins={h.get('naive_wins')}")
    if 'latest' in report:
        b = report['latest']['band']
        print(f"latest known metal leg: Rs {report['latest']['metal_leg_inr_kg']}/kg "
              f"({report['latest']['week']})")
        print(f"4-week band 80%: {b.get('q80_low')} .. +{b.get('q80_high')}  "
              f"(asymmetric: upside {b.get('q80_high')} vs downside {abs(b.get('q80_low'))})")
    print('-> data/brass_model_results.json, data/brass_band.csv')


if __name__ == '__main__':
    main()
