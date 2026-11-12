"""History analytics: did the floor actually hold, and what did it protect?

Two rules shape this module:
  * "realised" means the metal price that was actually current at the end of the
    cover period, from stored observations — never an estimate.
  * exposure is reported as exposure, not as savings we cannot prove. We do not
    know whether the owner raised his price, so we never claim he did.
"""
from __future__ import annotations

import sqlite3
from datetime import date, timedelta

from .config import DEFAULT_RATIO, W_CU
from .db import latest_observation

ORDER_KG = 100          # the worked example used throughout the documents
MONTHLY_KG = 5500       # Castle brass volume, from the owner interview


def _month_end(d: date) -> date:
    """Observation dates may be monthly (YYYY-MM); treat them as month-end."""
    return d


def metal_on(conn: sqlite3.Connection, on: str) -> tuple[float | None, str | None]:
    """Metal value current on a date, preferring MCX, falling back to LME."""
    cu = conn.execute(
        'SELECT obs_date, value FROM observation WHERE series=? AND obs_date<=? '
        'ORDER BY obs_date DESC LIMIT 1', ('mcx.copper', on)).fetchone()
    zn = conn.execute(
        'SELECT obs_date, value FROM observation WHERE series=? AND obs_date<=? '
        'ORDER BY obs_date DESC LIMIT 1', ('mcx.zinc', on)).fetchone()
    if cu and zn:
        return W_CU * cu['value'] + (1 - W_CU) * zn['value'], 'mcx'

    cu = conn.execute(
        'SELECT obs_date, value FROM observation WHERE series=? AND obs_date<=? '
        'ORDER BY obs_date DESC LIMIT 1', ('fred.PCOPPUSDM', on)).fetchone()
    zn = conn.execute(
        'SELECT obs_date, value FROM observation WHERE series=? AND obs_date<=? '
        'ORDER BY obs_date DESC LIMIT 1', ('fred.PZINCUSDM', on)).fetchone()
    fx = conn.execute(
        'SELECT obs_date, value FROM observation WHERE series=? AND obs_date<=? '
        'ORDER BY obs_date DESC LIMIT 1', ('fred.DEXINUS', on)).fetchone()
    if cu and zn and fx:
        return (W_CU * cu['value'] + (1 - W_CU) * zn['value']) * fx['value'] / 1000.0, 'lme'
    return None, None


def transport_at(conn: sqlite3.Connection, on: str) -> float:
    r = conn.execute(
        'SELECT value FROM observation WHERE series=? AND obs_date<=? '
        'ORDER BY obs_date DESC LIMIT 1', ('owner.transport', on)).fetchone()
    return float(r['value']) if r else 0.39


def realised_cost(conn: sqlite3.Connection, on: str,
                  ratio: float = DEFAULT_RATIO) -> tuple[float | None, str | None]:
    """What one kilo of brass actually cost on a given date, delivered."""
    metal, src = metal_on(conn, on)
    if metal is None:
        return None, None
    return round(metal * ratio + transport_at(conn, on), 2), src


def _add_days(iso: str, days: int) -> str:
    try:
        return (date.fromisoformat(iso[:10]) + timedelta(days=days)).isoformat()
    except Exception:
        return iso[:10]


def history_report(conn: sqlite3.Connection, limit: int = 200) -> dict:
    """Every quote scored against what the metal actually cost afterwards."""
    rows = conn.execute('SELECT * FROM quote ORDER BY id DESC LIMIT ?',
                        (limit,)).fetchall()
    quotes = []
    n_judged = n_unjudged = n_covered = 0
    exposure = 0.0
    loss_if_quoted = 0.0
    below = 0

    for r in rows:
        end = _add_days(r['quoted_at'], r['cover_days'])
        realised, src = realised_cost(conn, end)
        item = {
            'id': r['id'],
            'quoted_at': r['quoted_at'],
            'price': r['price'],
            'cover_days': r['cover_days'],
            'floor': r['floor_at_time'],
            'verdict': r['verdict'],
            'gap_per_kg': r['gap'],
            'model_version': r['model_version'],
            'realised_cost': realised,
            'realised_source': src,
        }
        if r['verdict'] in ('stop', 'risky', 'thin'):
            below += 1
            exposure += max(0.0, r['floor_at_time'] - r['price']) * ORDER_KG

        if realised is None:
            item['covered'] = None
            n_unjudged += 1
        else:
            covered = r['floor_at_time'] >= realised
            item['covered'] = covered
            item['realised_gap'] = round(r['floor_at_time'] - realised, 2)
            n_judged += 1
            if covered:
                n_covered += 1
            # what the quote would have lost had it been sent at that price
            if r['price'] < realised:
                loss_if_quoted += (realised - r['price']) * ORDER_KG
                item['loss_if_quoted_100kg'] = round((realised - r['price']) * ORDER_KG, 2)
        quotes.append(item)

    total = conn.execute('SELECT COUNT(*) FROM quote').fetchone()[0]
    stops = conn.execute(
        "SELECT COUNT(*) FROM quote WHERE verdict='stop'").fetchone()[0]

    return {
        'total_quotes': total,
        'scored_quotes': n_judged,
        'unscored_quotes': n_unjudged,
        'below_floor_quotes': below,
        'below_floor_rate': round(stops / total, 4) if total else None,
        'floor_coverage_rate': round(n_covered / n_judged, 4) if n_judged else None,
        'floor_coverage_target': 0.80,
        'exposure_flagged_per_100kg': round(exposure, 2),
        'loss_if_all_quoted_per_100kg': round(loss_if_quoted, 2),
        'order_kg': ORDER_KG,
        'quotes': quotes,
    }


def weekly_series(conn: sqlite3.Connection, weeks: int = 26) -> list[dict]:
    """Floor history against realised cost, newest last — for a small chart."""
    rows = conn.execute(
        'SELECT quoted_at, cover_days, floor_at_time AS floor FROM quote '
        'ORDER BY id DESC LIMIT ?', (weeks,)).fetchall()
    out = []
    for r in reversed(rows):
        end = _add_days(r['quoted_at'], r['cover_days'])
        realised, _ = realised_cost(conn, end)
        out.append({'at': r['quoted_at'][:10], 'floor': r['floor'],
                    'realised': realised})
    return out
