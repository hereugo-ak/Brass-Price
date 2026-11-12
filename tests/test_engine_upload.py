"""Engine and upload tests. Run: python3 -m pytest tests -q"""
from __future__ import annotations

import csv
import io
import sys
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import db, engine, upload  # noqa: E402


# ------------------------------------------------------------------- engine
def test_band_matches_the_product():
    """The number the UI shows must come from here and nowhere else."""
    b = engine.band(983.65, 0.876, 0.039, 0.39, cover_days=1)
    assert b['floor'] == pytest.approx(950.40, abs=0.05)
    assert b['mid'] == pytest.approx(862.07, abs=0.05)
    assert b['model_version'] == engine.MODEL_VERSION


def test_cover_period_widens_the_band():
    f = [engine.band(983.65, 0.876, 0.039, 0.39, cover_days=d)['floor']
         for d in (1, 15, 30)]
    assert f[0] < f[1] < f[2]
    assert f[2] - f[0] < 60      # sensible increment, not a wild swing


def test_band_is_asymmetric():
    b = engine.band(983.65, 0.876, 0.039, 0.39, cover_days=30)
    up = b['high'] - b['mid']
    down = b['mid'] - b['low']
    assert up > down, 'upside risk must exceed downside (measured in the backtest)'


def test_engine_rejects_nonsense():
    with pytest.raises(ValueError):
        engine.band(0, 0.876, 0.039, 0)
    with pytest.raises(ValueError):
        engine.band(983, -1, 0.039, 0)
    with pytest.raises(ValueError):
        engine.transport_inr_kg(-5, 3)


def test_transport_maths():
    assert engine.transport_inr_kg(130, 3) == pytest.approx(0.39)
    assert engine.transport_inr_kg(1270, 3) == pytest.approx(3.81)


def test_metal_routes():
    mcx = engine.metal_from_mcx(1341.85, 411.45)
    lme = engine.metal_from_lme(14473, 4021, 94.53)
    assert mcx == pytest.approx(983.65, abs=0.05)
    # the two independent routes agree to well under 1%
    assert abs(mcx - lme) / lme < 0.01


def test_verdicts():
    b = engine.band(983.65, 0.876, 0.039, 0.39, cover_days=1)
    assert engine.verdict(b['floor'] + 1, b) == 'safe'
    assert engine.verdict(b['high'] + 0.1, b) == 'thin'
    assert engine.verdict(b['mid'] + 0.1, b) == 'risky'
    assert engine.verdict(b['mid'] - 1, b) == 'stop'


# ------------------------------------------------------------------- upload
@pytest.fixture()
def conn(tmp_path):
    c = db.init(tmp_path / 'test.db')
    yield c
    c.close()


def _csv(rows: list[list]) -> bytes:
    buf = io.StringIO()
    csv.writer(buf).writerows(rows)
    return buf.getvalue().encode()


def test_frameset_shell_is_rejected_with_the_real_reason():
    """The exact trap that cost this project a month of empty data."""
    html = b'<html xmlns:x="urn:schemas"><head><title>x</title></head>' \
           b'<frameset><frame src="sheet001.htm"></frameset></html>'
    with pytest.raises(upload.UploadError) as e:
        upload.read_table(html, 'bhavcopy.xls')
    assert 'frameset' in str(e.value).lower()


def test_empty_and_headerless_files_are_rejected():
    with pytest.raises(upload.UploadError):
        upload.read_table(b'', 'x.csv')
    with pytest.raises(upload.UploadError):
        upload.read_table(b'1,2,3\n4,5,6\n', 'x.csv')


def test_valid_rows_are_accepted_and_bad_rows_carry_a_reason():
    data = _csv([
        ['date', 'close_inr'],
        ['2026-11-11', '1341.85'],
        ['2026-11-11', '99999'],       # out of range
        ['2099-01-01', '1300'],        # future
        ['not-a-date', 'abc'],         # unreadable
    ])
    rows = upload.read_table(data, 'mcx.csv')
    res = upload.validate('mcx.copper', rows)
    assert res['accepted_count'] == 1
    assert res['rejected_count'] == 3
    reasons = ' '.join(r['reason'] for r in res['rejected'])
    assert 'outside the sane range' in reasons
    assert 'future' in reasons
    assert 'unreadable' in reasons


def test_no_accepted_rows_is_blocking():
    data = _csv([['date', 'close_inr'], ['bad', 'bad']])
    res = upload.validate('mcx.copper', upload.read_table(data, 'x.csv'))
    assert res['blocking'], 'a file with zero valid rows must be refused'
    with pytest.raises(upload.UploadError):
        upload.commit_upload(object(), 'mcx.copper', 'x.csv', res)


def test_auto_feeds_cannot_be_uploaded(conn):
    with pytest.raises(upload.UploadError) as e:
        upload.validate('fred.DEXINUS', [{'date': '2026-11-11', 'value': 93}])
    assert 'Sync All' in str(e.value)


def test_upload_is_idempotent(conn):
    data = _csv([['date', 'close_inr'], ['2026-11-11', '1341.85'],
                 ['2026-11-12', '1345.00']])
    rows = upload.read_table(data, 'mcx.csv')
    res = upload.validate('mcx.copper', rows)
    first = upload.commit_upload(conn, 'mcx.copper', 'mcx.csv', res)
    assert first['added'] == 2
    second = upload.commit_upload(conn, 'mcx.copper', 'mcx.csv', res)
    assert second['added'] == 0, 're-uploading the same file must add nothing'


def test_transport_upload_converts_to_inr_per_kg(conn):
    data = _csv([['km', 'rate_inr_per_t_km'], ['1270', '3']])
    res = upload.validate('owner.transport', upload.read_table(data, 't.csv'))
    assert res['accepted_count'] == 1
    assert res['accepted'][0][1] == pytest.approx(3.81)


def test_board_prices_are_averaged_per_date(conn):
    data = _csv([
        ['date', 'price_inr_kg', 'grade'],
        ['2026-11-11', '870', 'bartan'],
        ['2026-11-11', '910', 'honey'],
    ])
    res = upload.validate('board.brass_prices', upload.read_table(data, 'b.csv'))
    assert res['accepted_count'] == 1, 'two quotes on one date must reduce to one value'
    assert res['accepted'][0][1] == pytest.approx(890.0)
