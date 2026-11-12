"""Sync All — run every automatable feed, record the run, and be honest about
what could not be fetched.

The product must never present stale data as current, so staleness is computed
here and surfaced with the run, not left to the caller.
"""
from __future__ import annotations

import sqlite3
from datetime import date, datetime, timezone

from .config import AUTO_FEEDS, FEED_BY_KEY, MANUAL, OK, STALE, Feed
from .db import latest_observation, upsert_observations
from .feeds import FeedResult, run_feed


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def _days_old(obs_date: str) -> int | None:
    try:
        if len(obs_date) == 7:                      # YYYY-MM monthly series
            y, m = int(obs_date[:4]), int(obs_date[5:7])
            d = date(y + (m == 12), 1 if m == 12 else m + 1, 1)
            return (date.today() - d).days + 1
        return (date.today() - date.fromisoformat(obs_date[:10])).days
    except Exception:
        return None


def staleness(conn: sqlite3.Connection, feed: Feed) -> tuple[str, int | None]:
    """Return (status, age_days) for a feed based on what is stored."""
    row = latest_observation(conn, feed.key)
    if row is None:
        return STALE, None
    age = _days_old(row['obs_date'])
    if age is None:
        return STALE, None
    return (OK if age <= feed.lag_days else STALE), age


def sync_all(conn: sqlite3.Connection, trigger: str = 'manual',
             include_manual: bool = True) -> dict:
    """Run every auto feed, store what arrives, log the run. Never raises."""
    started = _now()
    cur = conn.execute('INSERT INTO feed_run(started_at, trigger) VALUES(?,?)',
                       (started, trigger))
    run_id = cur.lastrowid
    conn.commit()

    results: list[dict] = []
    checked: list[Feed] = list(AUTO_FEEDS)
    if include_manual:
        from .config import MANUAL_FEEDS
        checked.extend(MANUAL_FEEDS)

    for feed in checked:
        res: FeedResult = run_feed(feed)
        added = 0
        if res.status == OK and res.rows:
            added = upsert_observations(conn, feed.key, res.rows, _now())
        status_after, age = staleness(conn, feed)
        # a successful fetch can still be stale if the publisher lags
        final_status = res.status if res.status != OK else status_after

        conn.execute(
            """INSERT INTO feed_run_item
               (run_id, series, status, rows, http_status, message, duration_ms)
               VALUES(?,?,?,?,?,?,?)""",
            (run_id, feed.key, final_status, added, res.http_status,
             res.message, res.duration_ms))
        results.append({
            'series': feed.key,
            'label': feed.label,
            'mode': feed.mode,
            'status': final_status,
            'rows_added': added,
            'age_days': age,
            'http_status': res.http_status,
            'message': res.message,
            'action': _action_for(feed, final_status),
        })
        conn.commit()

    finished = _now()
    conn.execute('UPDATE feed_run SET finished_at=? WHERE id=?', (finished, run_id))
    conn.commit()

    summary = {
        'run_id': run_id,
        'started_at': started,
        'finished_at': finished,
        'trigger': trigger,
        'feeds': results,
        'counts': _count_by_status(results),
        'action_required': [r for r in results
                            if r['status'] in (STALE, 'BLOCKED', 'FAILED', MANUAL)],
    }
    return summary


def _count_by_status(results: list[dict]) -> dict:
    out: dict[str, int] = {}
    for r in results:
        out[r['status']] = out.get(r['status'], 0) + 1
    return out


def _action_for(feed: Feed, status: str) -> str:
    if status == OK:
        return ''
    if feed.mode == 'manual':
        return f'Upload: {feed.label}'
    if status == 'BLOCKED':
        return f'{feed.source} refused the request; retry or check terms'
    if status == 'FAILED':
        return f'{feed.label}: fetch failed, see message'
    if status == STALE:
        return f'{feed.label} is older than {feed.lag_days} days'
    return ''


def last_run(conn: sqlite3.Connection) -> dict | None:
    row = conn.execute('SELECT * FROM feed_run ORDER BY id DESC LIMIT 1').fetchone()
    if not row:
        return None
    items = conn.execute(
        'SELECT * FROM feed_run_item WHERE run_id=? ORDER BY id', (row['id'],)).fetchall()
    return {
        'run_id': row['id'],
        'started_at': row['started_at'],
        'finished_at': row['finished_at'],
        'trigger': row['trigger'],
        'feeds': [dict(i) for i in items],
    }
