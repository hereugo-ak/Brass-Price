"""Analytics (did the floor hold) and weekly note delivery."""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import analytics, db, notes  # noqa: E402


@pytest.fixture()
def conn(tmp_path):
    c = db.init(tmp_path / 'a.db')
    yield c
    c.close()


def _seed_metal(conn, series, rows):
    db.upsert_observations(conn, series, rows, '2026-11-12T00:00:00+00:00')
    conn.commit()


def _quote(conn, quoted_at, price, cover, floor, verdict):
    conn.execute(
        """INSERT INTO quote(quoted_at, price, cover_days, floor_at_time,
                             high_at_time, gap, verdict, model_version)
           VALUES(?,?,?,?,?,?,?,'test')""",
        (quoted_at, price, cover, floor, floor + 5, price - floor, verdict))
    conn.commit()


# ------------------------------------------------------------------ analytics
def test_report_is_empty_and_honest_before_any_quotes(conn):
    r = analytics.history_report(conn)
    assert r['total_quotes'] == 0
    assert r['floor_coverage_rate'] is None, 'no quotes means no coverage claim'
    assert r['exposure_flagged_per_100kg'] == 0


def test_floor_that_held_is_counted_as_covered(conn):
    # metal on the quote day and 7 days later is unchanged
    _seed_metal(conn, 'mcx.copper', [('2026-11-01', 1341.85), ('2026-11-08', 1341.85)])
    _seed_metal(conn, 'mcx.zinc', [('2026-11-01', 411.45), ('2026-11-08', 411.45)])
    _quote(conn, '2026-11-01T09:00:00+00:00', 1000, 7, 960.0, 'safe')
    r = analytics.history_report(conn)
    assert r['scored_quotes'] == 1
    assert r['quotes'][0]['covered'] is True
    assert r['floor_coverage_rate'] == 1.0


def test_floor_that_failed_is_counted_and_loss_valued(conn):
    # metal jumped 30% between the quote and the end of the cover period
    _seed_metal(conn, 'mcx.copper', [('2026-11-01', 1341.85), ('2026-11-08', 1800.0)])
    _seed_metal(conn, 'mcx.zinc', [('2026-11-01', 411.45), ('2026-11-08', 411.45)])
    _quote(conn, '2026-11-01T09:00:00+00:00', 700, 7, 960.0, 'stop')
    r = analytics.history_report(conn)
    q = r['quotes'][0]
    assert q['covered'] is False
    assert r['floor_coverage_rate'] == 0.0
    assert q['loss_if_quoted_100kg'] > 0
    assert r['loss_if_all_quoted_per_100kg'] > 0


def test_unmeasurable_quotes_are_excluded_not_guessed(conn):
    _quote(conn, '2026-11-01T09:00:00+00:00', 900, 7, 950.0, 'risky')
    r = analytics.history_report(conn)     # no observations stored at all
    assert r['unscored_quotes'] == 1
    assert r['scored_quotes'] == 0
    assert r['floor_coverage_rate'] is None
    assert r['quotes'][0]['covered'] is None


def test_exposure_is_reported_as_exposure_not_savings(conn):
    _seed_metal(conn, 'mcx.copper', [('2026-11-01', 1341.85)])
    _seed_metal(conn, 'mcx.zinc', [('2026-11-01', 411.45)])
    _quote(conn, '2026-11-01T09:00:00+00:00', 900, 1, 950.0, 'risky')
    r = analytics.history_report(conn)
    # 50/kg gap x 100 kg order
    assert r['exposure_flagged_per_100kg'] == pytest.approx(5000.0)


def test_metal_falls_back_from_mcx_to_lme(conn):
    _seed_metal(conn, 'fred.PCOPPUSDM', [('2026-10-01', 14473)])
    _seed_metal(conn, 'fred.PZINCUSDM', [('2026-10-01', 4021)])
    _seed_metal(conn, 'fred.DEXINUS', [('2026-10-01', 94.53)])
    metal, src = analytics.metal_on(conn, '2026-11-01')
    assert src == 'lme'
    assert metal == pytest.approx(987.8, abs=1.0)


# ------------------------------------------------------------------------ note
def test_note_contains_every_floor_and_warns_about_missing_feeds(conn):
    n = notes.build(conn)
    for needle in ('Quotation floor', 'same day', '15 days', '30 days',
                   'Range this month', 'ASSUMED'):
        assert needle in n['body'], needle
    assert n['missing_feeds'], 'un-uploaded manual feeds must be named'
    assert n['model_version']


def test_note_reflects_a_freight_bill_when_one_exists(conn):
    _seed_metal(conn, 'owner.transport', [('2026-11-01', 3.81)])
    n = notes.build(conn)
    assert 'from a freight bill' in n['body']
    assert 'ASSUMED' not in n['body']


def test_file_delivery_writes_and_marks_sent(conn, tmp_path, monkeypatch):
    monkeypatch.setattr(notes, 'OUTBOX', tmp_path / 'outbox')
    res = notes.deliver(conn, channel='file')
    assert res['ok'] is True
    p = pathlib.Path(res['path'])
    assert p.exists() and p.read_text(encoding='utf-8').startswith('BRASS GUARD')
    row = conn.execute('SELECT channel, sent_at FROM note WHERE id=?',
                       (res['note_id'],)).fetchone()
    assert row['channel'] == 'file'
    assert row['sent_at'], 'a delivered note must be stamped'


def test_email_without_configuration_never_claims_success(conn, monkeypatch):
    for k in notes.SMTP_ENV:
        monkeypatch.delenv(k, raising=False)
    res = notes.deliver(conn, channel='email')
    assert res['ok'] is False
    assert 'not configured' in res['message'].lower()
    assert 'SMTP_HOST' in res['message']
    row = conn.execute('SELECT sent_at FROM note WHERE id=?',
                       (res['note_id'],)).fetchone()
    assert row['sent_at'] is None, 'a failed send must not be stamped as sent'


def test_dry_run_writes_nothing(conn):
    before = conn.execute('SELECT COUNT(*) FROM note').fetchone()[0]
    res = notes.deliver(conn, channel='file', dry_run=True)
    assert res['dry_run'] is True
    assert conn.execute('SELECT COUNT(*) FROM note').fetchone()[0] == before


def test_unknown_channel_is_rejected(conn):
    with pytest.raises(ValueError):
        notes.deliver(conn, channel='telegram')


def test_note_history_lists_previous_notes(conn, tmp_path, monkeypatch):
    monkeypatch.setattr(notes, 'OUTBOX', tmp_path / 'outbox')
    notes.deliver(conn, channel='file')
    h = notes.history(conn)
    assert h['total'] == 1
    assert h['notes'][0]['channel'] == 'file'
    assert h['notes'][0]['chars'] > 100


def test_weekly_series_runs_and_returns_one_row_per_quote(conn):
    """Regression: this endpoint returned 500 because of a mismatched column."""
    _seed_metal(conn, 'mcx.copper', [('2026-11-01', 1341.85)])
    _seed_metal(conn, 'mcx.zinc', [('2026-11-01', 411.45)])
    _quote(conn, '2026-11-01T09:00:00+00:00', 1000, 1, 950.0, 'safe')
    _quote(conn, '2026-11-02T09:00:00+00:00', 960, 1, 951.0, 'thin')
    s = analytics.weekly_series(conn, 26)
    assert len(s) == 2
    assert s[0]['floor'] == pytest.approx(950.0)
    assert s[-1]['floor'] == pytest.approx(951.0)
    assert s[-1]['realised'] is not None
