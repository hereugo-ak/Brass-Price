#!/usr/bin/env python3
"""Procurement backtest on the ratio-derived brass target.

WHY
    The project's acceptance rule has two halves:
       1. beat naive on MAE                        -> tested (naive wins)
       2. survive the rupee-saved backtest          -> NEVER tested until now
    This runs half 2.

TARGET (and its honest label)
    target_brass(t) = metal_leg_actual(t) x ratio
    ratio = 0.876 (bartan+honey+purja, 2026, sd 0.039)
    This is a SYNTHETIC target: a well-evidenced estimate of Castle's market
    tier, not Castle's invoice. Because the ratio is a constant multiplier,
    rupee savings computed in metal-leg units scale exactly; both are reported.

WHAT IS TESTED
    A. Cost of delay      - what does waiting k weeks cost per kg?
    B. Buy-timing signal  - does deferring when the forecast says "cheaper
                            next week" beat simply buying every week?

OUTPUTS
    data/procurement_backtest.json
    output/PROCUREMENT_BACKTEST.md

Usage: python3 backtest_procurement.py
"""
import collections
import csv
import json
import pathlib
from statistics import mean

HERE = pathlib.Path(__file__).parent
PRIMARY_W = 0.615
RATIO = 0.876
RATIO_SD = 0.039
MONTHLY_KG = 5500
LAG_CU_ZN = 56     # days, per LEAK_MAP
LAG_FX = 7


def load(sid):
    out = {}
    with open(HERE / 'history' / f'{sid}.csv') as f:
        for r in csv.DictReader(f):
            try:
                out[r['date'][:10]] = float(r['value'])
            except ValueError:
                pass
    return out


def known_at(series, cutoff):
    past = [k for k in series if k <= cutoff]
    return series[max(past)] if past else None


def build():
    """Weekly frame: date, actual brass Rs/kg, known brass Rs/kg (lagged)."""
    cu, zn, fx = load('PCOPPUSDM'), load('PZINCUSDM'), load('DEXINUS')
    days = sorted(fx)
    weeks = [d for d in days if _dow(d) == 0]
    rows = []
    for w in weeks:
        cut = _shift(w, -LAG_CU_ZN)
        cut_fx = _shift(w, -LAG_FX)
        c, z, f = known_at(cu, cut), known_at(zn, cut), known_at(fx, cut_fx)
        ca, za, fa = known_at(cu, w), known_at(zn, w), known_at(fx, w)
        if None in (c, z, f, ca, za, fa):
            continue
        known = (PRIMARY_W * c + (1 - PRIMARY_W) * z) * f / 1000
        actual = (PRIMARY_W * ca + (1 - PRIMARY_W) * za) * fa / 1000
        rows.append({'week': w, 'known': known, 'actual': actual})
    return rows


def _dow(d):
    import datetime
    return datetime.date.fromisoformat(d).weekday()


def _shift(d, n):
    import datetime
    return (datetime.date.fromisoformat(d) + datetime.timedelta(days=n)).isoformat()


# ---------------------------------------------------------------- A. cost of delay
def cost_of_delay(rows):
    out = {}
    for k in (1, 2, 3, 4, 8):
        diffs = [rows[i + k]['actual'] - rows[i]['actual']
                 for i in range(len(rows) - k)]
        out[k] = {
            'n': len(diffs),
            'mean_inr_kg': round(mean(diffs), 2),
            'pct_up': round(sum(1 for d in diffs if d > 0) / len(diffs) * 100, 1),
        }
    return out


# ---------------------------------------------------------------- B. signal backtest
def signal_backtest(rows, max_stack=2):
    """Each week one unit is due. Defer if the forecast says next week is cheaper."""
    def run(policy):
        cost = 0.0
        kg = 0.0
        owed = 0
        deferred = 0
        for i in range(len(rows) - 1):
            owed += 1
            price = rows[i]['actual']
            if policy == 'always' or owed >= max_stack:
                cost += owed * price
                kg += owed
                owed = 0
            else:
                # forecast next week's known leg vs this week's known leg
                if rows[i + 1]['known'] < rows[i]['known']:
                    deferred += 1      # expect cheaper next week -> wait
                else:
                    cost += owed * price
                    kg += owed
                    owed = 0
        if owed:                        # settle any tail at the last price
            cost += owed * rows[-1]['actual']
            kg += owed
        return cost, kg, deferred

    base_cost, base_kg, _ = run('always')
    sig_cost, sig_kg, deferred = run('signal')
    base_avg = base_cost / base_kg
    sig_avg = sig_cost / sig_kg
    saved_per_kg = base_avg - sig_avg
    return {
        'weeks': len(rows) - 1,
        'baseline_avg_inr_kg': round(base_avg, 2),
        'signal_avg_inr_kg': round(sig_avg, 2),
        'saved_inr_kg': round(saved_per_kg, 2),
        'saved_pct': round(saved_per_kg / base_avg * 100, 3),
        'times_deferred': deferred,
        'defer_rate_pct': round(deferred / (len(rows) - 1) * 100, 1),
        'saved_inr_per_month': round(saved_per_kg * MONTHLY_KG, 0),
    }


def main():
    rows = build()
    if len(rows) < 100:
        print(f'STOP: only {len(rows)} usable weeks')
        return
    print(f'weekly frame: {len(rows)} weeks, {rows[0]["week"]} -> {rows[-1]["week"]}')
    print(f'target = metal leg x {RATIO} (SYNTHETIC: estimate of Castle tier, not invoice)')

    cd = cost_of_delay(rows)
    print('\n=== A. cost of delay (metal leg Rs/kg, and brass at ratio) ===')
    print(f'{"delay":>6} {"n":>5} {"mean Rs/kg":>12} {"% weeks higher":>15} {"brass Rs/kg":>12}')
    for k, v in cd.items():
        print(f'{k:>5}w {v["n"]:>5} {v["mean_inr_kg"]:>12.2f} {v["pct_up"]:>14.1f}% '
              f'{v["mean_inr_kg"]*RATIO:>12.2f}')

    sb = signal_backtest(rows)
    print('\n=== B. buy-timing signal vs buy every week ===')
    print(f'  weeks                 {sb["weeks"]}')
    print(f'  baseline avg          Rs {sb["baseline_avg_inr_kg"]}/kg')
    print(f'  signal avg            Rs {sb["signal_avg_inr_kg"]}/kg')
    print(f'  saved                 Rs {sb["saved_inr_kg"]}/kg  ({sb["saved_pct"]}%)')
    print(f'  deferred on            {sb["defer_rate_pct"]}% of weeks')
    print(f'  -> per month (5,500kg) Rs {sb["saved_inr_per_month"]:,.0f}')

    out = {
        'label': 'SYNTHETIC TARGET: metal leg x ratio, not Castle invoice',
        'ratio': RATIO, 'ratio_sd': RATIO_SD,
        'weekly_frame': {'n': len(rows), 'first': rows[0]['week'], 'last': rows[-1]['week']},
        'cost_of_delay': cd,
        'signal_backtest': sb,
        'latest': {'week': rows[-1]['week'],
                   'metal_leg_known': round(rows[-1]['known'], 2),
                   'brass_estimate_inr_kg': round(rows[-1]['known'] * RATIO, 2)},
    }
    (HERE / 'procurement_backtest.json').write_text(json.dumps(out, indent=1), encoding='utf-8')
    print('\n-> data/procurement_backtest.json')


if __name__ == '__main__':
    main()
