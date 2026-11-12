"""Database: schema, connection, migrations.

Append-only by design where it matters. The quote log is never updated in
place — a correction is a new row — because it is the only evidence that can
prove the floor saved money.
"""
from __future__ import annotations

import os
import pathlib
import sqlite3
from contextlib import contextmanager

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS series (
    key         TEXT PRIMARY KEY,
    label       TEXT NOT NULL,
    unit        TEXT NOT NULL,
    freq        TEXT NOT NULL,
    mode        TEXT NOT NULL,          -- auto | manual
    lag_days    INTEGER NOT NULL,
    source      TEXT NOT NULL,
    note        TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS observation (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    series      TEXT NOT NULL REFERENCES series(key),
    obs_date    TEXT NOT NULL,          -- ISO date or YYYY-MM
    value       REAL NOT NULL,
    retrieved_at TEXT NOT NULL,
    vintage     TEXT NOT NULL DEFAULT 'first-seen',
    UNIQUE(series, obs_date, vintage)
);
CREATE INDEX IF NOT EXISTS obs_series_date ON observation(series, obs_date DESC);

CREATE TABLE IF NOT EXISTS model_input (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    as_of       TEXT NOT NULL,          -- ISO date the inputs describe
    metal       REAL NOT NULL,
    metal_source TEXT NOT NULL,         -- mcx | lme | default
    ratio       REAL NOT NULL,
    ratio_sd    REAL NOT NULL,
    transport   REAL NOT NULL,
    margin      REAL NOT NULL,
    model_version TEXT NOT NULL,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS quote (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    quoted_at   TEXT NOT NULL,
    price       REAL NOT NULL,
    cover_days  INTEGER NOT NULL,
    floor_at_time REAL NOT NULL,
    high_at_time REAL NOT NULL,
    gap         REAL NOT NULL,
    verdict     TEXT NOT NULL,
    market      TEXT DEFAULT '',
    note        TEXT DEFAULT '',
    model_version TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS quote_time ON quote(quoted_at DESC);

CREATE TABLE IF NOT EXISTS note (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    week_start  TEXT NOT NULL,
    body        TEXT NOT NULL,
    channel     TEXT NOT NULL DEFAULT 'manual',
    sent_at     TEXT
);

CREATE TABLE IF NOT EXISTS feed_run (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at  TEXT NOT NULL,
    finished_at TEXT,
    trigger     TEXT NOT NULL DEFAULT 'manual'
);

CREATE TABLE IF NOT EXISTS feed_run_item (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id      INTEGER NOT NULL REFERENCES feed_run(id) ON DELETE CASCADE,
    series      TEXT NOT NULL,
    status      TEXT NOT NULL,          -- OK|STALE|BLOCKED|MANUAL|FAILED
    rows        INTEGER DEFAULT 0,
    http_status INTEGER,
    message     TEXT DEFAULT '',
    duration_ms INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS upload (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    series      TEXT NOT NULL,
    filename    TEXT NOT NULL,
    accepted    INTEGER NOT NULL DEFAULT 0,
    rejected    INTEGER NOT NULL DEFAULT 0,
    uploaded_at TEXT NOT NULL,
    note        TEXT DEFAULT ''
);
"""


def connect(path: pathlib.Path | str | None = None) -> sqlite3.Connection:
    """Resolve the database path at call time so tests and deployments can
    point BRASS_DB somewhere else without re-importing the package."""
    from .config import SETTINGS
    p = pathlib.Path(path or os.environ.get('BRASS_DB') or SETTINGS.db_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(p), detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys=ON')
    return conn


def init(path: pathlib.Path | str | None = None, seed: bool = True) -> sqlite3.Connection:
    conn = connect(path)
    conn.executescript(SCHEMA)
    if seed:
        seed_series(conn)
    conn.commit()
    return conn


def seed_series(conn: sqlite3.Connection) -> None:
    from .config import FEEDS
    for f in FEEDS:
        conn.execute(
            """INSERT INTO series(key,label,unit,freq,mode,lag_days,source,note)
               VALUES(?,?,?,?,?,?,?,?)
               ON CONFLICT(key) DO UPDATE SET
                 label=excluded.label, unit=excluded.unit, freq=excluded.freq,
                 mode=excluded.mode, lag_days=excluded.lag_days,
                 source=excluded.source, note=excluded.note""",
            (f.key, f.label, f.unit, f.freq, f.mode, f.lag_days, f.source, f.note))


@contextmanager
def session(path: pathlib.Path | str | None = None):
    conn = init(path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def latest_observation(conn: sqlite3.Connection, series: str):
    return conn.execute(
        'SELECT obs_date, value, retrieved_at FROM observation '
        'WHERE series=? ORDER BY obs_date DESC LIMIT 1', (series,)).fetchone()


def upsert_observations(conn: sqlite3.Connection, series: str,
                        rows: list[tuple[str, float]], retrieved_at: str) -> int:
    """Insert (obs_date, value) pairs; ignore duplicates. Returns rows added."""
    before = conn.execute('SELECT COUNT(*) FROM observation WHERE series=?',
                          (series,)).fetchone()[0]
    conn.executemany(
        """INSERT INTO observation(series, obs_date, value, retrieved_at)
           VALUES(?,?,?,?)
           ON CONFLICT(series, obs_date, vintage) DO NOTHING""",
        [(series, d, v, retrieved_at) for d, v in rows])
    after = conn.execute('SELECT COUNT(*) FROM observation WHERE series=?',
                         (series,)).fetchone()[0]
    return after - before
