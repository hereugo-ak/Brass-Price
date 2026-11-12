"""The weekly note: build it from the same numbers the screen shows, store it,
and deliver it.

Delivery is deliberately conservative. There is no pretend sending: if SMTP is
not configured, the email channel says exactly that instead of reporting success.
"""
from __future__ import annotations

import os
import pathlib
import smtplib
import sqlite3
from datetime import date, datetime, timedelta, timezone
from email.message import EmailMessage

from . import pricing
from .config import MANUAL_FEEDS, SETTINGS

OUTBOX = SETTINGS.data_dir / 'outbox'


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def week_start(d: date | None = None) -> str:
    d = d or date.today()
    return (d - timedelta(days=d.weekday())).isoformat()


def _money(v: float) -> str:
    return f'Rs {round(v)}'


def build(conn: sqlite3.Connection, start: str | None = None) -> dict:
    """Compose the note from live engine outputs. One source of truth."""
    start = start or week_start()
    b1 = pricing.week(conn, cover_days=1, persist=False)
    b15 = pricing.week(conn, cover_days=15, persist=False)
    b30 = pricing.week(conn, cover_days=30, persist=False)

    stale = [f for f in MANUAL_FEEDS
             if not conn.execute(
                 'SELECT 1 FROM observation WHERE series=? LIMIT 1',
                 (f.key,)).fetchone()]
    tsrc = b1['provenance']['transport_source']
    transport_line = (f"Transport  {b1['transport']:.2f}/kg "
                      f"({'from a freight bill' if tsrc == 'owner' else 'ASSUMED rate'})")

    lines = [
        f'BRASS GUARD — week of {start}',
        '',
        'Range this month (Rs/kg)',
        f"  low      {_money(b1['low'])}",
        f"  middle   {_money(b1['mid'])}",
        f"  high     {_money(b1['high'])}",
        '',
        'Quotation floor (Rs/kg)',
        f"  same day {_money(b1['floor'])}",
        f"  15 days  {_money(b15['floor'])}",
        f"  30 days  {_money(b30['floor'])}",
        '',
        transport_line,
        f"Metal     {_money(b1['metal'])}/kg from {b1['provenance']['metal_source']}"
        + (f" ({b1['provenance']['metal_age_days']} days old)"
           if b1['provenance']['metal_age_days'] is not None else ''),
        '',
        'Read it like this: plan on the middle, treat the gap to the high as',
        'your cushion, and never quote below the floor for the period you are',
        'holding the price.',
    ]
    if b1['stale']:
        lines += ['', 'Status: PROVISIONAL — the metal input is older than 7 days.']
    if stale:
        lines += ['', 'Missing data: ' + ', '.join(f.label for f in stale) +
                  '. Figures may be less precise until these are uploaded.']

    body = '\n'.join(lines)
    return {
        'week_start': start,
        'body': body,
        'floors': {'same_day': b1['floor'], 'd15': b15['floor'], 'd30': b30['floor']},
        'band': {'low': b1['low'], 'mid': b1['mid'], 'high': b1['high']},
        'model_version': b1['model_version'],
        'provisional': b1['stale'],
        'missing_feeds': [f.key for f in stale],
        'warnings': b1['warnings'],
    }


def save(conn: sqlite3.Connection, note: dict, channel: str = 'manual') -> int:
    cur = conn.execute(
        'INSERT INTO note(week_start, body, channel, sent_at) VALUES(?,?,?,?)',
        (note['week_start'], note['body'], channel, None))
    conn.commit()
    return cur.lastrowid


def mark_sent(conn: sqlite3.Connection, note_id: int, channel: str) -> None:
    conn.execute('UPDATE note SET channel=?, sent_at=? WHERE id=?',
                 (channel, _now(), note_id))
    conn.commit()


# ------------------------------------------------------------------ channels
def deliver_file(conn: sqlite3.Connection, note: dict,
                 note_id: int | None = None) -> dict:
    OUTBOX.mkdir(parents=True, exist_ok=True)
    p = OUTBOX / f"brass-guard-{note['week_start']}.txt"
    p.write_text(note['body'], encoding='utf-8')
    if note_id:
        mark_sent(conn, note_id, 'file')
    return {'channel': 'file', 'ok': True, 'path': str(p),
            'message': f'Written to {p.name}'}


SMTP_ENV = ('SMTP_HOST', 'SMTP_PORT', 'SMTP_USER', 'SMTP_PASS',
            'SMTP_FROM', 'SMTP_TO')


def email_configured() -> tuple[bool, list[str]]:
    missing = [k for k in SMTP_ENV if not os.environ.get(k)]
    return (not missing), missing


def deliver_email(conn: sqlite3.Connection, note: dict,
                  note_id: int | None = None) -> dict:
    ok, missing = email_configured()
    if not ok:
        return {'channel': 'email', 'ok': False,
                'message': 'Email is not configured. Missing environment '
                           'variables: ' + ', '.join(missing) +
                           '. The note was saved but not sent — nothing is '
                           'reported as delivered when it was not.'}
    msg = EmailMessage()
    msg['Subject'] = f"Brass Guard — week of {note['week_start']}"
    msg['From'] = os.environ['SMTP_FROM']
    msg['To'] = os.environ['SMTP_TO']
    msg.set_content(note['body'])
    try:
        with smtplib.SMTP(os.environ['SMTP_HOST'],
                          int(os.environ.get('SMTP_PORT', 587)), timeout=20) as s:
            s.starttls()
            s.login(os.environ['SMTP_USER'], os.environ['SMTP_PASS'])
            s.send_message(msg)
    except Exception as e:
        return {'channel': 'email', 'ok': False,
                'message': f'SMTP failed: {type(e).__name__}: {str(e)[:120]}'}
    if note_id:
        mark_sent(conn, note_id, 'email')
    return {'channel': 'email', 'ok': True,
            'message': f"Sent to {os.environ['SMTP_TO']}"}


CHANNELS = {'file': deliver_file, 'email': deliver_email}


def deliver(conn: sqlite3.Connection, channel: str = 'file',
            start: str | None = None, dry_run: bool = False) -> dict:
    if channel not in CHANNELS:
        raise ValueError(f'Unknown channel "{channel}". Use one of: '
                         + ', '.join(CHANNELS))
    note = build(conn, start)
    if dry_run:
        return {'dry_run': True, 'note': note,
                'would_send_via': channel}
    note_id = save(conn, note, channel)
    result = CHANNELS[channel](conn, note, note_id)
    result.update({'note_id': note_id, 'week_start': note['week_start'],
                   'provisional': note['provisional']})
    return result


def history(conn: sqlite3.Connection, limit: int = 20) -> dict:
    rows = conn.execute(
        'SELECT id, week_start, channel, sent_at, LENGTH(body) AS chars '
        'FROM note ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
    return {'notes': [dict(r) for r in rows],
            'total': conn.execute('SELECT COUNT(*) FROM note').fetchone()[0]}
