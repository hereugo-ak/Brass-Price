"""Feed fetchers. Each returns a FeedResult and never raises for a network or
HTTP problem — a blocked feed is a fact the product must display, not a crash.
"""
from __future__ import annotations

import csv
import io
import json
import pathlib
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone

from .config import BLOCKED, FAILED, MANUAL, OK, Feed

UA = {'User-Agent': 'BrassGuard/1.0 (Castle Hardwares price floor; contact: analyst)'}
TIMEOUT = 45


@dataclass
class FeedResult:
    series: str
    status: str
    rows: list[tuple[str, float]] = field(default_factory=list)
    http_status: int | None = None
    message: str = ''
    duration_ms: int = 0

    @property
    def added(self) -> int:
        return len(self.rows)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def _get(url: str) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.status, r.read()


# --------------------------------------------------------------------- FRED
# The public CSV endpoint (fredgraph.csv) times out reliably from this network,
# so the documented JSON API is used with the project's key. The key is read
# from .env and is never logged.
FRED_API = ('https://api.stlouisfed.org/fred/series/observations'
            '?series_id={sid}&api_key={key}&file_type=json')


def _fred_key() -> str | None:
    import os
    k = os.environ.get('FRED_API_KEY')
    if k:
        return k.strip()
    env = None
    for base in (pathlib.Path(__file__).resolve().parent.parent,):
        p = base / '.env'
        if p.exists():
            env = p
            break
    if env is None:
        return None
    for line in env.read_text(encoding='utf-8', errors='ignore').splitlines():
        line = line.strip()
        if line.startswith('FRED_API_KEY'):
            return line.split('=', 1)[1].strip().strip('"').strip("'")
    return None


def fetch_fred(feed: Feed) -> FeedResult:
    sid = feed.key.split('.', 1)[1]
    t0 = time.time()
    key = _fred_key()
    if not key:
        return FeedResult(feed.key, FAILED,
                          message='FRED_API_KEY not found in the environment or .env',
                          duration_ms=int((time.time() - t0) * 1000))
    url = FRED_API.format(sid=sid, key=key)
    try:
        status, body = _get(url)
    except urllib.error.HTTPError as e:
        return FeedResult(feed.key, BLOCKED, http_status=e.code,
                          message=f'FRED returned HTTP {e.code}',
                          duration_ms=int((time.time() - t0) * 1000))
    except Exception as e:  # network, DNS, timeout
        return FeedResult(feed.key, FAILED,
                          message=f'{type(e).__name__}: {str(e)[:120]}',
                          duration_ms=int((time.time() - t0) * 1000))

    rows: list[tuple[str, float]] = []
    try:
        payload = json.loads(body)
        for o in payload.get('observations', []):
            d, v = str(o.get('date', ''))[:10], str(o.get('value', ''))
            if not d or v in ('', '.'):
                continue
            try:
                rows.append((d, float(v)))
            except ValueError:
                continue
    except Exception as e:
        return FeedResult(feed.key, FAILED, message=f'parse: {e}',
                          duration_ms=int((time.time() - t0) * 1000))

    if not rows:
        return FeedResult(feed.key, FAILED, message='no observations returned',
                          duration_ms=int((time.time() - t0) * 1000))
    return FeedResult(feed.key, OK, rows=rows, http_status=status,
                      message=f'{len(rows)} observations',
                      duration_ms=int((time.time() - t0) * 1000))


# --------------------------------------------------------------------- ECB
ECB_DAILY = 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'


def fetch_ecb(feed: Feed) -> FeedResult:
    t0 = time.time()
    try:
        status, body = _get(ECB_DAILY)
    except urllib.error.HTTPError as e:
        return FeedResult(feed.key, BLOCKED, http_status=e.code,
                          message=f'ECB returned HTTP {e.code}',
                          duration_ms=int((time.time() - t0) * 1000))
    except Exception as e:
        return FeedResult(feed.key, FAILED, message=f'{type(e).__name__}: {str(e)[:120]}',
                          duration_ms=int((time.time() - t0) * 1000))

    import re
    text = body.decode('utf-8', 'ignore')
    m_date = re.search(r'time=[\'"](\d{4}-\d{2}-\d{2})[\'"]', text)
    m_usd = re.search(r'currency=[\'"]USD[\'"][^>]*rate=[\'"]([\d.]+)[\'"]', text)
    if not (m_date and m_usd):
        return FeedResult(feed.key, FAILED, message='ECB payload shape changed',
                          duration_ms=int((time.time() - t0) * 1000))
    return FeedResult(feed.key, OK, rows=[(m_date.group(1), float(m_usd.group(1)))],
                      http_status=status, message='1 rate',
                      duration_ms=int((time.time() - t0) * 1000))


# --------------------------------------------------------------------- CFTC
CFTC_API = ('https://publicreporting.cftc.gov/resource/6dca-aqww.json'
            '?$limit=6&$order=report_date_as_yyyy_mm_dd%20DESC')


def fetch_cftc(feed: Feed) -> FeedResult:
    """Net non-commercial position is the single value stored per week."""
    t0 = time.time()
    try:
        status, body = _get(CFTC_API)
    except urllib.error.HTTPError as e:
        return FeedResult(feed.key, BLOCKED, http_status=e.code,
                          message=f'CFTC returned HTTP {e.code}',
                          duration_ms=int((time.time() - t0) * 1000))
    except Exception as e:
        return FeedResult(feed.key, FAILED, message=f'{type(e).__name__}: {str(e)[:120]}',
                          duration_ms=int((time.time() - t0) * 1000))

    rows = []
    try:
        for rec in json.loads(body):
            d = str(rec.get('report_date_as_yyyy_mm_dd', ''))[:10]
            try:
                net = float(rec['noncomm_positions_long_all']) - \
                      float(rec['noncomm_positions_short_all'])
            except (KeyError, TypeError, ValueError):
                continue
            if d:
                rows.append((d, net))
    except Exception as e:
        return FeedResult(feed.key, FAILED, message=f'parse: {e}',
                          duration_ms=int((time.time() - t0) * 1000))
    if not rows:
        return FeedResult(feed.key, FAILED, message='no usable rows',
                          duration_ms=int((time.time() - t0) * 1000))
    return FeedResult(feed.key, OK, rows=rows, http_status=status,
                      message=f'{len(rows)} weekly positions',
                      duration_ms=int((time.time() - t0) * 1000))


AUTO_FETCHERS = {
    'fred': fetch_fred,
    'ecb': fetch_ecb,
    'cftc': fetch_cftc,
}


def run_feed(feed: Feed) -> FeedResult:
    """Dispatch one feed. Manual feeds are never attempted."""
    if feed.mode == 'manual':
        return FeedResult(feed.key, MANUAL,
                          message=f'Needs an upload from {feed.source}')
    prefix = feed.key.split('.', 1)[0]
    fn = AUTO_FETCHERS.get(prefix)
    if fn is None:
        return FeedResult(feed.key, FAILED, message=f'no fetcher for {prefix}')
    try:
        return fn(feed)
    except Exception as e:  # absolute safety net
        return FeedResult(feed.key, FAILED, message=f'unexpected: {type(e).__name__}')
