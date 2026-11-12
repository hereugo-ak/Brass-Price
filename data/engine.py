#!/usr/bin/env python3
"""Frozen pricing engine. ONE pure function, ONE version string.

Every number this project publishes must be reproducible from here. If the
formula changes, the version changes, and old rows keep their old version.
This module contains NO model training on purpose — see
output/DRIVER_MODEL_RESULTS.md for why prediction was rejected.
"""
MODEL_VERSION = "2026-11-12.1"


def band(metal, ratio, sd, transport, cover_days=1, margin=0.05,
         risk_p95_30d=25.8, down_factor=0.72):
    """Return the week's band and quote floor, all in Rs per kg.

    metal        Rs/kg = 0.615 * MCX copper + 0.385 * MCX zinc
    ratio        measured brass-to-metal ratio (0.876)
    sd           standard deviation of that ratio (0.039)
    transport    Rs/kg, 0 when already inside the trader's delivered quote
    cover_days   how long the price is exposed (delivery lead time, not quote validity)
    margin       required margin, e.g. 0.05
    """
    k = (max(cover_days, 1) / 30.0) ** 0.5
    brass = metal * ratio
    up = metal * sd + risk_p95_30d * k
    down = metal * sd + risk_p95_30d * down_factor * k
    return {
        "model_version": MODEL_VERSION,
        "cover_days": cover_days,
        "low": round(brass - down + transport, 2),
        "mid": round(brass + transport, 2),
        "high": round(brass + up + transport, 2),
        "floor": round((brass + up + transport) * (1 + margin), 2),
        "inputs": {"metal": metal, "ratio": ratio, "sd": sd,
                   "transport": transport, "margin": margin},
    }


def verdict(price, b):
    """safe / thin / risky / stop — the four states the product shows."""
    if price >= b["floor"]:
        return "safe"
    if price >= b["high"]:
        return "thin"
    if price >= b["mid"]:
        return "risky"
    return "stop"


def transport_inr_kg(km, rate_per_t_km=3.0):
    """km x Rs/tonne-km = Rs/tonne; /1000 = Rs/kg. Rate is an ASSUMPTION."""
    return km * rate_per_t_km / 1000.0


if __name__ == "__main__":
    import json
    b = band(983.65, 0.876, 0.039, transport_inr_kg(130), cover_days=1)
    print(json.dumps(b, indent=1))
    for days in (1, 15, 30):
        bb = band(983.65, 0.876, 0.039, transport_inr_kg(130), cover_days=days)
        print(f'{days:>2}d  low {bb["low"]:7.2f}  mid {bb["mid"]:7.2f}  '
              f'high {bb["high"]:7.2f}  floor {bb["floor"]:7.2f}')
