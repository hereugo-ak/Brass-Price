"""FastAPI surface for Brass Guard.

Six endpoints. Anything that changes state says exactly what it changed.
"""
from __future__ import annotations

import base64
from typing import Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from . import db, pricing, sync, upload
from .config import FEEDS, MANUAL_FEEDS, SETTINGS
from .engine import MODEL_VERSION, VERDICT_COPY

app = FastAPI(
    title='Brass Guard API',
    version=MODEL_VERSION,
    description='Quote-floor service for Castle Hardwares. No forecasting by design.',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],           # pilot: the static UI is served from file://
    allow_methods=['*'],
    allow_headers=['*'],
)


def _conn():
    return db.init()


@app.get('/health')
def health():
    conn = _conn()
    try:
        n = conn.execute('SELECT COUNT(*) FROM observation').fetchone()[0]
        q = conn.execute('SELECT COUNT(*) FROM quote').fetchone()[0]
    finally:
        conn.close()
    return {'status': 'ok', 'model_version': MODEL_VERSION,
            'observations': n, 'quotes': q}


# --------------------------------------------------------------------- week
@app.get('/week')
def get_week(cover_days: int = 1):
    if cover_days < 0 or cover_days > 180:
        raise HTTPException(400, 'cover_days must be between 0 and 180')
    conn = _conn()
    try:
        b = pricing.week(conn, cover_days=cover_days)
    finally:
        conn.close()
    b['cover_days'] = cover_days
    return b


# --------------------------------------------------------------------- quote
class QuoteIn(BaseModel):
    price: float = Field(..., gt=0, description='INR per kg')
    cover_days: int = Field(1, ge=0, le=180)
    market: str = ''
    note: str = ''


@app.post('/quote')
def post_quote(q: QuoteIn):
    conn = _conn()
    try:
        res = pricing.check_quote(conn, q.price, q.cover_days, q.market, q.note)
    finally:
        conn.close()
    res['verdict_copy'] = VERDICT_COPY.get(res['verdict'], '')
    return res


@app.get('/history')
def get_history(limit: int = 100):
    if limit < 1 or limit > 1000:
        raise HTTPException(400, 'limit must be 1..1000')
    conn = _conn()
    try:
        return pricing.history(conn, limit)
    finally:
        conn.close()


# --------------------------------------------------------------------- sync
@app.post('/sync')
def post_sync(include_manual: bool = True, trigger: str = 'api'):
    conn = _conn()
    try:
        return sync.sync_all(conn, trigger=trigger, include_manual=include_manual)
    finally:
        conn.close()


@app.get('/sync/last')
def get_sync_last():
    conn = _conn()
    try:
        run = sync.last_run(conn)
    finally:
        conn.close()
    if run is None:
        return {'run': None, 'message': 'Sync All has never been run.'}
    return {'run': run}


# --------------------------------------------------------------------- upload
@app.get('/upload/templates')
def upload_templates():
    return {'feeds': [
        {'series': f.key, 'label': f.label, 'freq': f.freq, 'unit': f.unit,
         'template': list(f.template), 'note': f.note, 'source': f.source}
        for f in MANUAL_FEEDS]}


@app.post('/upload/preview')
async def upload_preview(series: str, file: UploadFile = File(...)):
    data = await file.read()
    if not data:
        raise HTTPException(400, 'Empty file')
    if len(data) > 12 * 1024 * 1024:
        raise HTTPException(413, 'File larger than 12 MB')
    conn = _conn()
    try:
        out = upload.preview(conn, series, file.filename or 'upload', data)
    except upload.UploadError as e:
        raise HTTPException(422, str(e))
    finally:
        conn.close()
    out.pop('_result', None)
    return out


class CommitIn(BaseModel):
    series: str
    filename: str
    data_b64: str


@app.post('/upload/commit')
def upload_commit(body: CommitIn):
    try:
        data = base64.b64decode(body.data_b64)
    except Exception:
        raise HTTPException(400, 'data_b64 is not valid base64')
    conn = _conn()
    try:
        prev = upload.preview(conn, body.series, body.filename, data)
        result = prev.pop('_result')
        saved = upload.commit_upload(conn, body.series, body.filename, result)
    except upload.UploadError as e:
        raise HTTPException(422, str(e))
    finally:
        conn.close()
    saved['message'] = (f'{saved["accepted"]} row(s) accepted, '
                        f'{saved["rejected"]} rejected, {saved["added"]} new.')
    return saved


# --------------------------------------------------------------------- config
@app.get('/config')
def get_config():
    return {
        'model_version': MODEL_VERSION,
        'db_path': str(SETTINGS.db_path),
        'feeds': [{'key': f.key, 'label': f.label, 'mode': f.mode,
                   'freq': f.freq, 'lag_days': f.lag_days, 'unit': f.unit,
                   'source': f.source} for f in FEEDS],
        'verdicts': VERDICT_COPY,
    }


def serve(host: str = '127.0.0.1', port: int = 8000):
    import uvicorn
    uvicorn.run('app.api:app', host=host, port=port, reload=False)
