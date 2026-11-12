#!/usr/bin/env python3
"""Extract the combined price workbook and build the brass/metal ratio model.

WHY
    `output/Brass_Prices_Combined_v3_2026-11-12.xlsx` holds 14 sheets gathered on
    2026-11-12. Two price tiers exist in it and they must never be mixed:
      - HIGH tier (foundry board / wholesale): Rs 750-1000/kg  <- the factory tier
      - LOW  tier (household pickup / kabadi): Rs 375-520/kg  <- what a household gets
    Castle buys from local traders, so only the HIGH tier is its market.

THE MODEL
    brass_inr_kg  ~=  ratio x metal_leg_inr_kg
    with ratio estimated at three independent points in time and reported as a
    range, never a single number.

OUTPUTS
    data/manual/brass_board_prices.csv        dated HIGH-tier observations
    data/manual/mcx_copper_zinc_daily.csv     domestic exchange anchor (daily)
    data/manual/mcx_brass_2019.csv            historical brass futures, 2019
    data/manual/comtrade_brass_unit_values.csv
    data/manual/wpi_brass_newbase.csv
    data/brass_ratio_anchors.json             ratio estimates + band inputs

Usage: python3 brass_target_from_board.py
"""
import collections
import csv
import json
import pathlib
from statistics import mean

import openpyxl

HERE = pathlib.Path(__file__).parent
BOOK = HERE.parent / 'output' / 'Brass_Prices_Combined_v3_2026-11-12.xlsx'
MANUAL = HERE / 'manual'

PRIMARY_W = 0.615
# series that belong to the household/kabadi tier and must never enter a board average
LOW_TIER_SOURCES = {'ScrapRateToday (90d file)', 'ScrapRateToday (city page, weekly xlsx)',
                    'ScrapRates.in', 'GetScrapRate', 'ScrapXtrade', 'ScrapMonster'}
# rows in the high cluster that are NOT brass (alloy-leg comparators)
NON_BRASS_GRADES = {'cathode', 'cc rod'}


def load_history(sid):
    out = {}
    p = HERE / 'history' / f'{sid}.csv'
    with open(p) as f:
        for r in csv.DictReader(f):
            try:
                out[r['date'][:7]] = float(r['value'])
            except ValueError:
                pass
    return out


def build_leg():
    cu = load_history('PCOPPUSDM')
    zn = load_history('PZINCUSDM')
    _f = collections.defaultdict(list)
    for r in csv.DictReader(open(HERE / 'history' / 'DEXINUS.csv')):
        _f[r['date'][:7]].append(float(r['value']))
    fx = {k: mean(v) for k, v in _f.items()}

    def leg(month, w=PRIMARY_W):
        if month in cu and month in zn and month in fx:
            return (w * cu[month] + (1 - w) * zn[month]) * fx[month] / 1000.0
        return None
    return leg


def find_header_row(wb, name, key, scan=6):
    """Locate the header row by looking for a expected column name."""
    sh = wb[name]
    for r in range(1, min(scan, sh.max_row) + 1):
        for c in range(1, sh.max_column + 1):
            v = sh.cell(r, c).value
            if v is not None and str(v).strip().lower() == key.lower():
                return r
    return None


def sheet_rows(wb, name, key='Date'):
    hr = find_header_row(wb, name, key)
    if hr is None:
        print(f'  !! {name}: header row with "{key}" not found')
        return []
    sh = wb[name]
    hdr = [sh.cell(hr, c).value for c in range(1, sh.max_column + 1)]
    out = []
    for r in range(hr + 1, sh.max_row + 1):
        vals = [sh.cell(r, c).value for c in range(1, sh.max_column + 1)]
        if not any(v is not None for v in vals):
            continue
        out.append(dict(zip(hdr, vals)))
    return out


def write_csv(path, header, rows):
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f'  -> {path.relative_to(HERE.parent)}  ({len(rows)} rows)')


def main():
    if not BOOK.exists():
        print(f'STOP: workbook not found at {BOOK}')
        return
    wb = openpyxl.load_workbook(BOOK, data_only=True)
    leg = build_leg()
    MANUAL.mkdir(exist_ok=True)

    # ---------------------------------------------------------- 1. board prices
    spot = sheet_rows(wb, 'Daily_Spot_INRkg', 'Date')
    board, low, excluded = [], [], []
    for d in spot:
        src = d.get('Source_Name')
        grade = str(d.get('Grade_Spec') or '').lower()
        try:
            mid = float(d.get('Mid_INR_kg'))
        except (TypeError, ValueError):
            continue
        row = {'date': str(d.get('Date'))[:10], 'city': d.get('Geography'),
               'grade': d.get('Grade_Spec'), 'price': mid,
               'basis': d.get('Basis'), 'source': src, 'url': d.get('Source_URL')}
        if grade in NON_BRASS_GRADES:
            excluded.append((row, 'alloy-leg comparator (copper), not brass'))
        elif src in LOW_TIER_SOURCES:
            low.append(row)
        elif mid > 600:
            board.append(row)
        else:
            excluded.append((row, f'below high-tier floor ({mid})'))
    write_csv(MANUAL / 'brass_board_prices.csv',
              ['date', 'city', 'grade', 'price_inr_kg', 'basis', 'source', 'url'],
              [[r['date'], r['city'], r['grade'], r['price'], r['basis'], r['source'], r['url']]
               for r in sorted(board, key=lambda x: x['date'])])
    print(f'     high tier {len(board)} | low tier (excluded) {len(low)} '
          f'| other excluded {len(excluded)}')

    # ---------------------------------------------------------- 2. MCX daily
    mcx = sheet_rows(wb, 'MCX_Daily_Cu_Zn', 'Date')
    rows = []
    for d in mcx:
        try:
            rows.append([str(d.get('Date'))[:10], d.get('Symbol'), d.get('Expiry'),
                         d.get('Close_INR'), d.get('Vol_Lots')])
        except Exception:
            continue
    write_csv(MANUAL / 'mcx_copper_zinc_daily.csv',
              ['date', 'symbol', 'expiry', 'close_inr', 'vol_lots'], rows)

    # ---------------------------------------------------------- 3. MCX brass 2019
    br = sheet_rows(wb, 'MCX_Brass_Futures_2019', 'Date')
    rows = []
    for d in br:
        try:
            rows.append([str(d.get('Date'))[:10], float(d.get('Close_INR_kg')),
                         d.get('Vol_Lots'), d.get('OI_Lots')])
        except (TypeError, ValueError):
            continue
    write_csv(MANUAL / 'mcx_brass_2019.csv',
              ['date', 'close_inr_kg', 'vol_lots', 'oi_lots'], rows)

    # ---------------------------------------------------------- 4. Comtrade
    ct = sheet_rows(wb, 'Comtrade_UnitValues', 'Period')
    rows = []
    for d in ct:
        if d.get('Period') is None:
            continue
        rows.append([d.get('Period'), d.get('Flow'), d.get('HS_Code'),
                     d.get('UnitValue_USD_kg'), d.get('UnitValue_INR_kg'),
                     d.get('Qty_kg'), d.get('Value_USD')])
    write_csv(MANUAL / 'comtrade_brass_unit_values.csv',
              ['period', 'flow', 'hs_code', 'unit_value_usd_kg', 'unit_value_inr_kg',
               'qty_kg', 'value_usd'], rows)

    # ---------------------------------------------------------- 5. WPI new base
    nb = sheet_rows(wb, 'WPI_NewBase_Monthly', 'Month')
    rows = []
    for d in nb:
        if d.get('Month') is None:
            continue
        rows.append([d.get('Month'), d.get('Brass_Metal_Sheet_Coils_2022_23_100'),
                     d.get('YoY_pct'), d.get('Brass_Tubes_Pipes_2022_23_100')])
    write_csv(MANUAL / 'wpi_brass_newbase.csv',
              ['month', 'brass_sheet_2022_23_100', 'yoy_pct', 'brass_tubes_2022_23_100'], rows)

    # ---------------------------------------------------------- 6. ratio anchors
    anchors = []

    # (a) MCX brass futures 2019 — 107 daily closes
    by_month = collections.defaultdict(list)
    for d in br:
        try:
            by_month[str(d.get('Date'))[:7]].append(float(d.get('Close_INR_kg')))
        except (TypeError, ValueError):
            continue
    for m in sorted(by_month):
        L = leg(m)
        if L:
            anchors.append({'anchor': 'MCX BRASSPHY futures (zero-volume settlement)',
                            'period': m, 'brass_inr_kg': round(mean(by_month[m]), 1),
                            'metal_leg_inr_kg': round(L, 1),
                            'ratio': round(mean(by_month[m]) / L, 3), 'n': len(by_month[m])})

    # (b) MTLEXS Mumbai Jan 2023 — brass honey + sheet scrap
    for d in sheet_rows(wb, 'MTLEXS_Jan2023_Window', 'Date'):
        it = str(d.get('Item') or '')
        if 'Brass' in it and 'Shell' not in it:
            try:
                v = float(d.get('Price_INR_kg'))
            except (TypeError, ValueError):
                continue
            m = str(d.get('Date'))[:7]
            L = leg(m)
            if L:
                anchors.append({'anchor': f'MTLEXS Mumbai ({it})', 'period': m,
                                'brass_inr_kg': v, 'metal_leg_inr_kg': round(L, 1),
                                'ratio': round(v / L, 3), 'n': 1})

    # (c) current board, weighted by month
    cur_leg = leg('2026-09')
    for r in board:
        m = r['date'][:7]
        L = leg(m) or cur_leg
        if L:
            anchors.append({'anchor': f"{r['source']} ({r['grade']})", 'period': m,
                            'brass_inr_kg': r['price'], 'metal_leg_inr_kg': round(L, 1),
                            'ratio': round(r['price'] / L, 3), 'n': 1})

    ratios = [a['ratio'] for a in anchors]
    groups = collections.defaultdict(list)
    for a in anchors:
        key = a['period'][:4]
        groups[key].append(a['ratio'])
    by_year = {y: round(mean(v), 3) for y, v in sorted(groups.items())}

    out = {
        'model': 'brass_inr_kg = ratio x metal_leg_inr_kg',
        'primary_weight_cu': PRIMARY_W,
        'ratio_by_year': by_year,
        'ratio_overall_mean': round(mean(ratios), 3),
        'ratio_overall_min': min(ratios),
        'ratio_overall_max': max(ratios),
        'n_anchors': len(anchors),
        'anchors': anchors,
        'caveats': [
            'MCX BRASSPHY 2019 had zero volume and zero OI: those are settlement '
            'prices of an illiquid contract, not traded prints.',
            'MTLEXS 2023 covers three days in one city (Mumbai).',
            'The 2026 board is concentrated in November; it is a level, not a series.',
            'The ratio drifts downward over time; a single constant will be wrong '
            'in either direction. Report the range.',
            'Low-tier sources (household/kabadi) are excluded by construction.',
        ],
    }
    (HERE / 'brass_ratio_anchors.json').write_text(json.dumps(out, indent=1), encoding='utf-8')

    # ---------------------------------------------------------- report
    print('\n=== BRASS / METAL-LEG RATIO ANCHORS ===')
    for y, r in by_year.items():
        n = sum(1 for a in anchors if a['period'][:4] == y)
        print(f'  {y}  ratio {r:.3f}  (n={n})')
    print(f'  overall mean {out["ratio_overall_mean"]:.3f}  '
          f'range {out["ratio_overall_min"]:.3f}-{out["ratio_overall_max"]:.3f}  '
          f'n={out["n_anchors"]}')
    L = leg('2026-09')
    print(f'\nmetal leg 2026-09 = Rs {L:.0f}/kg')
    for q, label in [(out['ratio_overall_min'], 'low anchor'),
                     (out['ratio_overall_mean'], 'mean'),
                     (out['ratio_overall_max'], 'high anchor')]:
        print(f'  x {q:.3f} ({label:11}) -> brass Rs {L*q:.0f}/kg')
    print('\n-> data/brass_ratio_anchors.json')


if __name__ == '__main__':
    main()
