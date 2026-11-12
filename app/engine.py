"""Frozen pricing engine — the single source of truth for every number the
product displays.

MODEL_VERSION changes only when the formula changes. Every stored output keeps
the version that produced it, so any historical floor can be reproduced.

No model training lives here, by design. See output/DRIVER_MODEL_RESULTS.md:
eight models were trained and all lost to a naive random walk.
"""
from __future__ import annotations

MODEL_VERSION = '2026-11-12.1'

# Empirical constants from the backtest (data/procurement_backtest.json):
# 4-week brass price change, p95 upside and the thinner downside tail.
RISK_P95_30D = 25.8
DOWN_FACTOR = 0.72


def band(metal: float, ratio: float, sd: float, transport: float,
         cover_days: int = 1, margin: float = 0.05,
         risk_p95_30d: float = RISK_P95_30D,
         down_factor: float = DOWN_FACTOR) -> dict:
    """Return low / mid / high / floor in INR per kg.

    metal       INR/kg, 0.615*MCX copper + 0.385*MCX zinc
    ratio       measured brass-to-metal ratio
    sd          standard deviation of that ratio
    transport   INR/kg, 0 when already inside the trader's delivered quote
    cover_days  how long the price is exposed (delivery lead time)
    margin      required margin, e.g. 0.05
    """
    if metal <= 0:
        raise ValueError('metal must be positive')
    if ratio <= 0:
        raise ValueError('ratio must be positive')
    if cover_days < 0:
        raise ValueError('cover_days cannot be negative')

    k = (max(cover_days, 1) / 30.0) ** 0.5
    brass = metal * ratio
    up = metal * sd + risk_p95_30d * k
    down = metal * sd + risk_p95_30d * down_factor * k

    return {
        'model_version': MODEL_VERSION,
        'cover_days': cover_days,
        'metal': round(metal, 2),
        'transport': round(transport, 2),
        'low': round(brass - down + transport, 2),
        'mid': round(brass + transport, 2),
        'high': round(brass + up + transport, 2),
        'floor': round((brass + up + transport) * (1 + margin), 2),
        'inputs': {
            'metal': round(metal, 2), 'ratio': ratio, 'sd': sd,
            'transport': round(transport, 2), 'margin': margin,
        },
    }


def verdict(price: float, b: dict) -> str:
    """One of: safe | thin | risky | stop."""
    if price >= b['floor']:
        return 'safe'
    if price >= b['high']:
        return 'thin'
    if price >= b['mid']:
        return 'risky'
    return 'stop'


VERDICT_COPY = {
    'safe': 'Covers a normal metal move over the cover period.',
    'thin': 'Above the expected high but below the floor: one sharp move eats the margin.',
    'risky': 'Near the expected metal value. Prices rose in 57 of the last 100 four-week periods.',
    'stop': 'Below the expected metal value: metal would be bought at a loss.',
}


def transport_inr_kg(km: float, rate_per_t_km: float) -> float:
    """km x INR/tonne-km = INR/tonne; /1000 = INR/kg."""
    if km < 0 or rate_per_t_km < 0:
        raise ValueError('km and rate must be non-negative')
    return km * rate_per_t_km / 1000.0


def metal_from_mcx(cu_inr_kg: float, zn_inr_kg: float, w_cu: float = 0.615) -> float:
    return w_cu * cu_inr_kg + (1 - w_cu) * zn_inr_kg


def metal_from_lme(cu_usd_t: float, zn_usd_t: float, usdinr: float,
                   w_cu: float = 0.615) -> float:
    return (w_cu * cu_usd_t + (1 - w_cu) * zn_usd_t) * usdinr / 1000.0
