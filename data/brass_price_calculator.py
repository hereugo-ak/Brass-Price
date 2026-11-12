#!/usr/bin/env python3
"""Brass price calculator — implements the owner's own description.

OWNER (2026-11-12):
    "LME governs most of it but in India we have MCX which is metal trading
     which also governs the price, plus the transportation is always extra"

So the price is calculated, not looked up:

    price = ratio x metal_value + transport

and the metal value is computed TWO independent ways:

    route A (LME): 0.615*Cu_USD_t*FX/1000 + 0.385*Zn_USD_t*FX/1000
    route B (MCX): 0.615*MCX_Cu_INR_kg      + 0.385*MCX_Zn_INR_kg

Route B already embeds FX, import duty and the domestic premium, so the two
routes agreeing is a real cross-check, not a tautology.

NO INVOICE IS NEEDED TO PRODUCE A NUMBER. The invoice is a validation of the
ratio, not a prerequisite for the calculation.

Usage: python3 brass_price_calculator.py [transport_inr_kg]
"""
import collections
import csv
import json
import pathlib
import sys
from statistics import mean

HERE = pathlib.Path(__file__).parent

W_CU = 0.615            # IS 319 Gr-II midpoint, swept elsewhere
RATIO = 0.876           # bartan+honey+purja, 2026, n=16
RATIO_SD = 0.039
RATIO_PRIOR_YEARS = {'2019': 0.977, '2023': 0.910, '2026': 0.897}


def load_monthly(sid):
    out = {}
    with open(HERE / 'history' / f'{sid}.csv') as f:
        for r in csv.DictReader(f):
            try:
                out[r['date'][:7]] = float(r['value'])
            except ValueError:
                pass
    return out


def latest_monthly(series):
    m = max(series)
    return m, series[m]


def weekly_fx_latest():
    """Latest weekly-averaged USDINR."""
    by = collections.defaultdict(list)
    with open(HERE / 'history' / 'DEXINUS.csv') as f:
        for r in csv.DictReader(f):
            try:
                by[r['date'][:7]].append(float(r['value']))
            except ValueError:
                pass
    m = max(by)
    return m, mean(by[m])


def mcx_latest():
    """Most recent daily close per symbol, in INR per kg."""
    by = collections.defaultdict(lambda: collections.defaultdict(list))
    path = HERE / 'manual' / 'mcx_copper_zinc_daily.csv'
    with open(path) as f:
        for r in csv.DictReader(f):
            try:
                by[r['symbol']][r['date'][:10]].append(float(r['close_inr']))
            except (TypeError, ValueError):
                pass
    out = {}
    for sym, days in by.items():
        d = max(days)
        out[sym] = {'date': d, 'inr_kg': mean(days[d])}
    return out


def main():
    transport = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0

    cu_m, cu_v = latest_monthly(load_monthly('PCOPPUSDM'))
    zn_m, zn_v = latest_monthly(load_monthly('PZINCUSDM'))
    fx_m, fx_v = weekly_fx_latest()
    mcx = mcx_latest()

    # ---- route A: LME x FX
    leg_a = (W_CU * cu_v + (1 - W_CU) * zn_v) * fx_v / 1000.0
    # ---- route B: MCX domestic, already INR/kg
    cu_d = mcx.get('COPPER', {}).get('inr_kg')
    zn_d = mcx.get('ZINC', {}).get('inr_kg')
    leg_b = (W_CU * cu_d + (1 - W_CU) * zn_d) if (cu_d and zn_d) else None

    print('=' * 66)
    print('BRASS PRICE — CALCULATED, NOT LOOKED UP')
    print('=' * 66)
    print(f'\nINPUTS')
    print(f'  LME/IMF copper   {cu_v:>9.0f} USD/t   ({cu_m})')
    print(f'  LME/IMF zinc     {zn_v:>9.0f} USD/t   ({zn_m})')
    print(f'  USD/INR          {fx_v:>9.2f}          ({fx_m})')
    if cu_d:
        print(f'  MCX copper       {cu_d:>9.2f} INR/kg  ({mcx["COPPER"]["date"]})')
    if zn_d:
        print(f'  MCX zinc         {zn_d:>9.2f} INR/kg  ({mcx["ZINC"]["date"]})')
    print(f'  alloy            {W_CU:.3f} Cu / {1-W_CU:.3f} Zn (IS 319 Gr-II)')

    print(f'\nROUTE A — LME x FX')
    print(f'  {W_CU:.3f} x {cu_v*fx_v/1000:8.2f}  +  {1-W_CU:.3f} x {zn_v*fx_v/1000:8.2f}')
    print(f'  metal value = Rs {leg_a:.2f}/kg')

    if leg_b:
        print(f'\nROUTE B — MCX domestic (embeds FX + duty + local premium)')
        print(f'  {W_CU:.3f} x {cu_d:8.2f}  +  {1-W_CU:.3f} x {zn_d:8.2f}')
        print(f'  metal value = Rs {leg_b:.2f}/kg')
        gap = (leg_b - leg_a) / leg_a * 100
        print(f'\n  A vs B difference: Rs {leg_b-leg_a:+.2f}/kg  ({gap:+.2f}%)')
        print(f'  -> the two independent routes {"AGREE" if abs(gap)<2 else "DIVERGE"}')

    leg = leg_b if leg_b else leg_a
    print(f'\nPRICE = ratio x metal + transport')
    print(f'{"":22}{"metal":>10}{"x ratio":>10}{"brass":>10}{"+transport":>12}{"delivered":>11}')
    for label, r in [('low  (mean-1sd)', RATIO - RATIO_SD),
                     ('central', RATIO),
                     ('high (mean+1sd)', RATIO + RATIO_SD)]:
        brass = leg * r
        print(f'  {label:20}{leg:>10.2f}{r:>10.3f}{brass:>10.2f}'
              f'{transport:>12.2f}{brass+transport:>11.2f}')

    print(f'\n  NB the ratio is the MARKET board ratio, not Castle\'s own. '
          f'1sd = +/-Rs{leg*RATIO_SD:.0f}/kg')

    # what the owner's own numbers say: MCX-led
    out = {
        'label': 'calculated price, no invoice used',
        'inputs': {
            'lme_cu_usd_t': cu_v, 'lme_zn_usd_t': zn_v, 'usdinr': round(fx_v, 2),
            'mcx_cu_inr_kg': round(cu_d, 2) if cu_d else None,
            'mcx_zn_inr_kg': round(zn_d, 2) if zn_d else None,
            'mcx_date': mcx.get('COPPER', {}).get('date'),
            'w_cu': W_CU,
        },
        'metal_value': {'route_a_lme': round(leg_a, 2),
                        'route_b_mcx': round(leg_b, 2) if leg_b else None,
                        'gap_pct': round((leg_b - leg_a) / leg_a * 100, 2) if leg_b else None},
        'ratio': {'central': RATIO, 'sd': RATIO_SD, 'prior_years': RATIO_PRIOR_YEARS},
        'transport_inr_kg': transport,
        'price_inr_kg': {
            'low': round(leg * (RATIO - RATIO_SD) + transport, 2),
            'mid': round(leg * RATIO + transport, 2),
            'high': round(leg * (RATIO + RATIO_SD) + transport, 2),
        },
        'quote_floor_5pct': round((leg * (RATIO + RATIO_SD) + transport) * 1.05, 2),
    }
    (HERE / 'brass_price_calculated.json').write_text(json.dumps(out, indent=1), encoding='utf-8')
    print(f'\n  QUOTE FLOOR (+5%) = Rs {out["quote_floor_5pct"]:.0f}/kg')
    print(f'\n-> data/brass_price_calculated.json')


if __name__ == '__main__':
    main()
