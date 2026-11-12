"""API, pricing and sync integration tests. Run: python3 -m pytest tests -q"""
from __future__ import annotations

import base64
import csv
import io
import os
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """Fresh database per test; the API resolves its connection at call time."""
    monkeypatch.setenv('BRASS_DB', str(tmp_path / 'api.db'))
    from fastapi.testclient import TestClient
    from app import db
    db.init(tmp_path / 'api.db')
    import app.api as api
    return TestClient(api.app)


def _csv_bytes(rows):
    buf = io.StringIO()
    csv.writer(buf).writerows(rows)
    return buf.getvalue().encode()


def test_health(client):
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json()['status'] == 'ok'


def test_week_without_data_warns_but_still_answers(client):
    r = client.get('/week?cover_days=1')
    assert r.status_code == 200
    b = r.json()
    assert b['floor'] > 0
    assert b['warnings'], 'an empty database must produce an explicit warning'
    assert b['provenance']['metal_source'] in ('default', 'lme', 'mcx')


def test_week_rejects_absurd_cover(client):
    assert client.get('/week?cover_days=-1').status_code == 400
    assert client.get('/week?cover_days=500').status_code == 400


def test_quote_is_logged_before_the_response(client):
    r = client.post('/quote', json={'price': 1000, 'cover_days': 1,
                                    'market': 'europe'})
    assert r.status_code == 200
    body = r.json()
    assert body['quote_id'] >= 1
    assert body['verdict'] in ('safe', 'thin', 'risky', 'stop')
    assert body['model_version']
    h = client.get('/history').json()
    assert h['total_quotes'] == 1
    assert h['quotes'][0]['price'] == 1000


def test_quote_validation(client):
    assert client.post('/quote', json={'price': 0}).status_code == 422
    assert client.post('/quote', json={'price': -5}).status_code == 422


def test_history_counts_below_floor(client):
    client.post('/quote', json={'price': 1000})
    client.post('/quote', json={'price': 100})     # surely below any floor
    h = client.get('/history').json()
    assert h['total_quotes'] == 2
    assert h['below_floor'] == 1


def test_upload_preview_then_commit(client):
    data = _csv_bytes([['date', 'close_inr'], ['2026-11-11', '1341.85']])
    files = {'file': ('mcx.csv', data, 'text/csv')}
    p = client.post('/upload/preview?series=mcx.copper', files=files)
    assert p.status_code == 200, p.text
    body = p.json()
    assert body['accepted_count'] == 1
    assert '_result' not in body, 'server-side carry must not leak to the client'

    c = client.post('/upload/commit', json={
        'series': 'mcx.copper', 'filename': 'mcx.csv',
        'data_b64': base64.b64encode(data).decode()})
    assert c.status_code == 200, c.text
    assert c.json()['added'] == 1


def test_upload_rejects_frameset_over_the_api(client):
    html = b'<html><frameset><frame src="sheet001.htm"></frameset></html>'
    r = client.post('/upload/preview?series=mcx.copper',
                    files={'file': ('bhav.xls', html, 'application/vnd.ms-excel')})
    assert r.status_code == 422
    assert 'frameset' in r.text.lower()


def test_upload_rejects_auto_feed(client):
    data = _csv_bytes([['date', 'value'], ['2026-11-11', '93']])
    r = client.post('/upload/preview?series=fred.DEXINUS',
                    files={'file': ('x.csv', data, 'text/csv')})
    assert r.status_code == 422


def test_templates_list_manual_feeds(client):
    r = client.get('/upload/templates')
    assert r.status_code == 200
    keys = {f['series'] for f in r.json()['feeds']}
    assert 'mcx.copper' in keys and 'owner.transport' in keys
    assert 'fred.DEXINUS' not in keys


def test_config_exposes_model_version(client):
    r = client.get('/config')
    assert r.status_code == 200
    assert r.json()['model_version']


def test_sync_reports_every_feed_and_never_raises(client, monkeypatch):
    """Network is stubbed out: the point is that every feed gets a status."""
    from app import feeds
    monkeypatch.setattr(feeds, 'AUTO_FETCHERS', {})   # force all auto feeds to fail
    r = client.post('/sync?include_manual=true')
    assert r.status_code == 200, r.text
    body = r.json()
    assert len(body['feeds']) >= 10
    for f in body['feeds']:
        assert f['status'] in ('OK', 'STALE', 'BLOCKED', 'FAILED', 'MANUAL')
    assert body['counts']


def test_last_sync_is_recorded(client, monkeypatch):
    from app import feeds
    monkeypatch.setattr(feeds, 'AUTO_FETCHERS', {})
    client.post('/sync')
    r = client.get('/sync/last')
    assert r.status_code == 200
    assert r.json()['run'] is not None
