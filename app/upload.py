"""Manual upload: preview -> validate -> commit.

Three deliberate properties:
  1. Nothing is written unless the file parses and at least one row validates.
  2. Every rejected row carries a reason a non-technical user can act on.
  3. A browser-saved "xls" that is really an HTML frameset is rejected with the
     real cause, because that exact trap cost this project a month of empty data.
"""
from __future__ import annotations

import csv
import io
import pathlib
import re
import sqlite3
from datetime import date, datetime, timezone

from .config import FEED_BY_KEY, MANUAL
from .db import upsert_observations
from .engine import transport_inr_kg

MAX_DATE_FUTURE_DAYS = 1


class UploadError(Exception):
    """Blocking problem: nothing may be written."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


# ------------------------------------------------------------------ reading
def is_html(data: bytes) -> bool:
    head = data[:400].lower()
    return b'<html' in head or b'frameset' in head or b'<?xml' in head[:50]


def read_table(data: bytes, filename: str) -> list[dict]:
    """Return rows as dicts with lowercased, stripped column names."""
    name = (filename or '').lower()

    if is_html(data):
        if b'frameset' in data[:2000].lower():
            raise UploadError(
                'This file is an HTML frameset, not a spreadsheet — the browser '
                'saved the page wrapper and the actual table was never saved. '
                'Open the source page, select the table, paste it into Excel, '
                'then save as CSV.')
        raise UploadError(
            'This file is HTML, not a spreadsheet. Save it as .csv or .xlsx first.')

    if name.endswith('.xlsx') or data[:2] == b'PK':
        try:
            import openpyxl
        except ImportError as e:
            raise UploadError(f'xlsx reader unavailable: {e}')
        wb = openpyxl.load_workbook(io.BytesIO(data), data_only=True)
        sh = wb[wb.sheetnames[0]]
        rows = list(sh.values)
        return _to_dicts(rows)

    if name.endswith('.xls') or data[:4] == b'\xd0\xcf\x11\xe0':
        try:
            import xlrd
        except ImportError as e:
            raise UploadError(f'xls reader unavailable: {e}')
        wb = xlrd.open_workbook(file_contents=data)
        sh = wb.sheet_by_index(0)
        rows = [[sh.cell_value(r, c) for c in range(sh.ncols)]
                for r in range(sh.nrows)]
        return _to_dicts(rows)

    # CSV / TSV
    text = data.decode('utf-8-sig', 'ignore')
    if not text.strip():
        raise UploadError('The file is empty.')
    sample = text[:2000]
    delim = '\t' if sample.count('\t') > sample.count(',') else ','
    rdr = csv.reader(io.StringIO(text), delimiter=delim)
    rows = [r for r in rdr if any(str(c).strip() for c in r)]
    return _to_dicts(rows)


def _to_dicts(rows: list) -> list[dict]:
    if not rows:
        raise UploadError('The file has no rows.')
    header_idx = None
    for i, r in enumerate(rows[:10]):
        cells = [str(c).strip().lower() for c in (r or []) if c is not None]
        if any(k in cells for k in ('date', 'month', 'week', 'km')):
            header_idx = i
            break
    if header_idx is None:
        raise UploadError(
            'No header row found. The first row must name the columns, '
            'for example: date, close_inr')
    header = [re.sub(r'[^a-z0-9_]', '_', str(c).strip().lower())
              for c in rows[header_idx]]
    out = []
    for r in rows[header_idx + 1:]:
        if not any(str(c).strip() for c in (r or []) if c is not None):
            continue
        out.append({header[i]: r[i] for i in range(min(len(header), len(r)))
                    if header[i]})
    return out


# ------------------------------------------------------------------ validating
def _as_float(v) -> float | None:
    if v is None:
        return None
    s = str(v).strip().replace(',', '').replace('₹', '').replace('$', '')
    if not s or s in ('-', '—', 'NA', 'N/A', 'null', 'None'):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _as_date(v) -> str | None:
    if v is None:
        return None
    if isinstance(v, (datetime, date)):
        return v.date().isoformat() if isinstance(v, datetime) else v.isoformat()
    s = str(v).strip()
    if not s:
        return None
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', s):
        return s
    if re.fullmatch(r'\d{4}-\d{2}', s):
        return s
    for fmt in ('%d/%m/%Y', '%d-%m-%Y', '%d %B %Y', '%d %b %Y', '%Y/%m/%d',
                '%d-%b-%Y', '%b-%y', '%d-%m-%y'):
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _future(d: str) -> bool:
    try:
        s = d if len(d) == 10 else d + '-01'
        return (date.fromisoformat(s) - date.today()).days > MAX_DATE_FUTURE_DAYS
    except Exception:
        return False


SPECS = {
    'mcx.copper': {'date': ('date',), 'value': ('close_inr', 'close', 'price_inr_kg'),
                   'lo': 100, 'hi': 5000},
    'mcx.zinc': {'date': ('date',), 'value': ('close_inr', 'close', 'price_inr_kg'),
                 'lo': 50, 'hi': 2000},
    'wpi.brass_index': {'date': ('month', 'date'),
                        'value': ('brass_index', 'index', 'value'),
                        'lo': 20, 'hi': 2000},
    'board.brass_prices': {'date': ('date',), 'value': ('price_inr_kg', 'price', 'mid'),
                           'lo': 200, 'hi': 3000},
    'owner.brass_rate': {'date': ('week', 'date'), 'value': ('price_inr_kg', 'price'),
                         'lo': 200, 'hi': 3000},
}


def _pick(row: dict, keys: tuple[str, ...]):
    for k in keys:
        if k in row and str(row[k]).strip() != '':
            return row[k]
    return None


def validate(feed_key: str, rows: list[dict]) -> dict:
    """Return {accepted, rejected, blocking, summary}. Never writes."""
    feed = FEED_BY_KEY.get(feed_key)
    if feed is None:
        raise UploadError(f'Unknown feed "{feed_key}".')
    if feed.mode != 'manual':
        raise UploadError(
            f'"{feed.label}" is fetched automatically — use Sync All instead of uploading.')

    accepted: list[tuple[str, float]] = []
    rejected: list[dict] = []

    if feed_key == 'owner.transport':
        # km + rate -> a single transport figure in INR/kg
        for i, row in enumerate(rows, start=1):
            km = _as_float(row.get('km'))
            rate = _as_float(row.get('rate_inr_per_t_km') or row.get('rate'))
            if km is None or rate is None:
                rejected.append({'row': i, 'reason': 'needs km and rate_inr_per_t_km'})
                continue
            if not (0 < km < 5000):
                rejected.append({'row': i, 'reason': f'km {km} outside 0–5000'})
                continue
            if not (0 < rate < 50):
                rejected.append({'row': i, 'reason': f'rate {rate} outside 0–50'})
                continue
            accepted.append((date.today().isoformat(), round(transport_inr_kg(km, rate), 4)))
        return _validation_result(accepted, rejected, rows)

    spec = SPECS.get(feed_key)
    if spec is None:
        raise UploadError(f'No validator is defined for "{feed_key}" yet.')

    for i, row in enumerate(rows, start=1):
        d = _as_date(_pick(row, spec['date']))
        v = _as_float(_pick(row, spec['value']))
        if d is None:
            rejected.append({'row': i, 'reason': 'date/month missing or unreadable'})
            continue
        if _future(d):
            rejected.append({'row': i, 'reason': f'{d} is in the future'})
            continue
        if v is None:
            rejected.append({'row': i, 'reason': 'price missing or not a number'})
            continue
        if not (spec['lo'] <= v <= spec['hi']):
            rejected.append({'row': i,
                             'reason': f'{v} outside the sane range '
                                       f'{spec["lo"]}–{spec["hi"]} {feed.unit}'})
            continue
        accepted.append((d, v))

    # one value per date: average duplicates rather than silently overwrite
    if feed_key == 'board.brass_prices' and accepted:
        from collections import defaultdict
        by_date: dict[str, list[float]] = defaultdict(list)
        for d, v in accepted:
            by_date[d].append(v)
        accepted = [(d, round(sum(vs) / len(vs), 2)) for d, vs in sorted(by_date.items())]

    return _validation_result(accepted, rejected, rows)


def _validation_result(accepted, rejected, rows) -> dict:
    dates = [d for d, _ in accepted]
    blocking = None
    if not accepted:
        blocking = ('No row could be accepted. Check the column names against the '
                    'template and the value ranges.')
    return {
        'total_rows': len(rows),
        'accepted': accepted,
        'accepted_count': len(accepted),
        'rejected': rejected[:50],
        'rejected_count': len(rejected),
        'date_range': [min(dates), max(dates)] if dates else None,
        'blocking': blocking,
    }


# ------------------------------------------------------------------ committing
def commit_upload(conn: sqlite3.Connection, feed_key: str, filename: str,
                  result: dict) -> dict:
    if result.get('blocking'):
        raise UploadError(result['blocking'])
    added = upsert_observations(conn, feed_key, result['accepted'], _now())
    conn.execute(
        """INSERT INTO upload(series, filename, accepted, rejected, uploaded_at, note)
           VALUES(?,?,?,?,?,?)""",
        (feed_key, filename, result['accepted_count'], result['rejected_count'],
         _now(), '; '.join(r['reason'] for r in result['rejected'][:5])))
    conn.commit()
    return {'series': feed_key, 'filename': filename, 'rows_in_file': result['total_rows'],
            'accepted': result['accepted_count'], 'added': added,
            'rejected': result['rejected_count'],
            'date_range': result['date_range']}


def preview(conn: sqlite3.Connection, feed_key: str, filename: str,
            data: bytes) -> dict:
    """Parse and validate without writing."""
    rows = read_table(data, filename)
    result = validate(feed_key, rows)
    feed = FEED_BY_KEY[feed_key]
    return {
        'series': feed_key,
        'label': feed.label,
        'filename': filename,
        'template': list(feed.template),
        'note': feed.note,
        'total_rows': result['total_rows'],
        'accepted_count': result['accepted_count'],
        'rejected_count': result['rejected_count'],
        'rejected': result['rejected'],
        'date_range': result['date_range'],
        'sample': [{'date': d, 'value': v} for d, v in result['accepted'][:5]],
        'blocking': result['blocking'],
        '_result': result,      # carried server-side into commit
    }


def read_upload(path: pathlib.Path) -> bytes:
    return pathlib.Path(path).read_bytes()
