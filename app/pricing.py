"""Pricing service: build the week's inputs, produce the band, and log quotes.

Provenance matters as much as the number. Every band returned here says which
metal source was used and how old each input is, so the product can warn when a
floor is being computed from stale data.
"""
from __future__ import annotations

import sqlite3
from datetime import date, datetime, timezone

from .config import (DEFAULT_MARGIN, DEFAULT_METAL_INR_KG, DEFAULT_RATIO,
                     DEFAULT_RATIO_SD, DEFAULT_RATE_INR_PER_T_KM,
                     DEFAULT_TRANSPORT_INR_KG, W_CU)
from .db import latest_observation
from .engine import (MODEL_VERSION, band as engine_band, metal_from_lme,
                     metal_from_mcx, transport_inr_kg, verdict)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def _age_days(obs_date: str | None) -> int | None:
    if not obs_date:
        return None
    try:
        s = obs_date[:10]
        if len(s) == 7:
            s = s + '-01'
        return (date.today() - date.fromisoformat(s)).days
    except Exception:
        return None


def current_inputs(conn: sqlite3.Connection) -> dict:
    """Resolve the engine inputs from stored observations, with provenance."""
    warnings: list[str] = []

    mcx_cu = latest_observation(conn, 'mcx.copper')
    mcx_zn = latest_observation(conn, 'mcx.zinc')
    imf_cu = latest_observation(conn, 'fred.PCOPPUSDM')
    imf_zn = latest_observation(conn, 'fred.PZINCUSDM')
    fx = latest_observation(conn, 'fred.DEXINUS')
    transport_row = latest_observation(conn, 'owner.transport')

    metal = None
    source = 'default'
    as_of = None

    if mcx_cu and mcx_zn:
        metal = metal_from_mcx(mcx_cu['value'], mcx_zn['value'], W_CU)
        source = 'mcx'
        as_of = min(mcx_cu['obs_date'], mcx_zn['obs_date'])
    elif imf_cu and imf_zn and fx:
        metal = metal_from_lme(imf_cu['value'], imf_zn['value'], fx['value'], W_CU)
        source = 'lme'
        as_of = min(imf_cu['obs_date'], imf_zn['obs_date'])
        warnings.append('MCX copper/zinc not uploaded: metal value is derived from '
                        'IMF monthly copper and zinc, which lag the market by up to '
                        'two months.')
    else:
        metal = DEFAULT_METAL_INR_KG
        as_of = date.today().isoformat()
        warnings.append('No metal observations stored: using the default metal value. '
                        'Run a sync or upload an MCX bhavcopy.')

    if transport_row:
        transport = transport_row['value']
        transport_source = 'owner'
    else:
        transport = transport_inr_kg(130, DEFAULT_RATE_INR_PER_T_KM)
        transport_source = 'assumed'
        warnings.append('Transport rate not supplied by Castle: using the assumed '
                        'INR 3 per tonne-km over 130 km. One freight bill replaces this.')

    return {
        'as_of': as_of,
        'metal': round(metal, 2),
        'metal_source': source,
        'metal_age_days': _age_days(as_of),
        'ratio': DEFAULT_RATIO,
        'ratio_sd': DEFAULT_RATIO_SD,
        'transport': round(transport, 2),
        'transport_source': transport_source,
        'margin': DEFAULT_MARGIN,
        'model_version': MODEL_VERSION,
        'warnings': warnings,
    }


def persist_inputs(conn: sqlite3.Connection, inp: dict) -> int:
    cur = conn.execute(
        """INSERT INTO model_input
           (as_of, metal, metal_source, ratio, ratio_sd, transport, margin,
            model_version, created_at)
           VALUES(?,?,?,?,?,?,?,?,?)""",
        (inp['as_of'], inp['metal'], inp['metal_source'], inp['ratio'],
         inp['ratio_sd'], inp['transport'], inp['margin'],
         inp['model_version'], _now()))
    return cur.lastrowid


def week(conn: sqlite3.Connection, cover_days: int = 1,
         persist: bool = True) -> dict:
    """The week's band and floor, with provenance and warnings."""
    inp = current_inputs(conn)
    b = engine_band(inp['metal'], inp['ratio'], inp['ratio_sd'],
                    inp['transport'], cover_days=cover_days, margin=inp['margin'])
    b['provenance'] = {
        'metal_source': inp['metal_source'],
        'metal_age_days': inp['metal_age_days'],
        'transport_source': inp['transport_source'],
        'as_of': inp['as_of'],
        'model_version': inp['model_version'],
    }
    b['warnings'] = inp['warnings']
    b['stale'] = bool(inp['metal_age_days'] is not None and inp['metal_age_days'] > 7)
    if b['stale']:
        b['warnings'].append(
            f"Metal input is {inp['metal_age_days']} days old: this floor is PROVISIONAL.")
    if persist:
        persist_inputs(conn, inp)
        conn.commit()
    return b


def check_quote(conn: sqlite3.Connection, price: float, cover_days: int = 1,
                market: str = '', note: str = '') -> dict:
    """Verdict for a price, written to the quote log before it is returned."""
    if price <= 0:
        raise ValueError('price must be positive')
    b = week(conn, cover_days=cover_days, persist=True)
    v = verdict(price, b)
    gap = round(price - b['floor'], 2)
    cur = conn.execute(
        """INSERT INTO quote
           (quoted_at, price, cover_days, floor_at_time, high_at_time, gap,
            verdict, market, note, model_version)
           VALUES(?,?,?,?,?,?,?,?,?,?)""",
        (_now(), price, cover_days, b['floor'], b['high'], gap, v,
         market, note, b['model_version']))
    conn.commit()
    return {
        'quote_id': cur.lastrowid,
        'price': price,
        'cover_days': cover_days,
        'verdict': v,
        'floor': b['floor'],
        'high': b['high'],
        'mid': b['mid'],
        'gap_per_kg': gap,
        'gap_100kg': round(gap * 100, 2),
        'gap_5500kg': round(gap * 5500, 2),
        'band': b,
        'quoted_at': _now(),
        'model_version': b['model_version'],
    }


def history(conn: sqlite3.Connection, limit: int = 100) -> dict:
    rows = conn.execute(
        'SELECT * FROM quote ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
    quotes = [dict(r) for r in rows]
    total = conn.execute('SELECT COUNT(*) FROM quote').fetchone()[0]
    below = conn.execute(
        "SELECT COUNT(*) FROM quote WHERE verdict='stop'").fetchone()[0]
    return {
        'total_quotes': total,
        'below_floor': below,
        'below_floor_rate': round(below / total, 4) if total else None,
        'quotes': quotes,
    }
