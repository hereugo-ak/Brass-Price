"""Command line: the same operations as the API, for the analyst's laptop.

  python3 -m app.cli init
  python3 -m app.cli sync
  python3 -m app.cli week --cover 1
  python3 -m app.cli quote 1000 --cover 1
  python3 -m app.cli history
  python3 -m app.cli upload mcx.copper path/to/file.csv
  python3 -m app.cli serve
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

from . import db, pricing, sync, upload
from .config import MANUAL_FEEDS, SETTINGS
from .engine import MODEL_VERSION


def _print(obj):
    print(json.dumps(obj, indent=2, default=str))


def cmd_init(a):
    conn = db.init()
    n = conn.execute('SELECT COUNT(*) FROM series').fetchone()[0]
    conn.close()
    _print({'ok': True, 'db': str(SETTINGS.db_path), 'series_seeded': n,
            'model_version': MODEL_VERSION})


def cmd_sync(a):
    conn = db.init()
    try:
        res = sync.sync_all(conn, trigger='cli')
    finally:
        conn.close()
    print(f"Sync All — run {res['run_id']} ({res['trigger']})")
    print(f"{'feed':34} {'mode':7} {'status':8} {'+rows':>6} {'age':>5}  note")
    for f in res['feeds']:
        age = '' if f['age_days'] is None else f"{f['age_days']}d"
        note = f['action'] or f['message']
        print(f"{f['series']:34} {f['mode']:7} {f['status']:8} "
              f"{f['rows_added']:>6} {age:>5}  {note[:60]}")
    print('\ncounts:', res['counts'])
    if res['action_required']:
        print(f"\nAction required on {len(res['action_required'])} feed(s):")
        for f in res['action_required']:
            print(f"  - {f['series']}: {f['action'] or f['status']}")


def cmd_week(a):
    conn = db.init()
    try:
        b = pricing.week(conn, cover_days=a.cover)
    finally:
        conn.close()
    print(f"Band for {a.cover}-day cover   [model {b['model_version']}]")
    print(f"  low    {b['low']:>8.2f}")
    print(f"  mid    {b['mid']:>8.2f}")
    print(f"  high   {b['high']:>8.2f}")
    print(f"  FLOOR  {b['floor']:>8.2f}  INR/kg")
    prov = b['provenance']
    print(f"\n  metal {b['inputs']['metal']} from {prov['metal_source']} "
          f"({prov['metal_age_days']} days old)")
    print(f"  transport {b['inputs']['transport']} from {prov['transport_source']}")
    if b['warnings']:
        print('\n  warnings:')
        for w in b['warnings']:
            print(f'   - {w}')


def cmd_quote(a):
    conn = db.init()
    try:
        r = pricing.check_quote(conn, a.price, a.cover, a.market, a.note)
    finally:
        conn.close()
    print(f"Quote {r['price']:.2f} for {r['cover_days']}-day cover -> "
          f"{r['verdict'].upper()}")
    print(f"  floor {r['floor']:.2f}   gap {r['gap_per_kg']:+.2f}/kg "
          f"({r['gap_100kg']:+.0f} on 100 kg)")
    print(f"  logged as quote #{r['quote_id']} [model {r['model_version']}]")


def cmd_history(a):
    conn = db.init()
    try:
        h = pricing.history(conn, a.limit)
    finally:
        conn.close()
    print(f"quotes: {h['total_quotes']}   below floor: {h['below_floor']}"
          f"   rate: {h['below_floor_rate']}")
    for q in h['quotes'][:a.limit]:
        print(f"  {q['quoted_at'][:19]}  {q['price']:>8.2f}  "
              f"{q['cover_days']:>3}d  {q['verdict']:>5}  floor {q['floor_at_time']:.2f}")


def cmd_upload(a):
    p = pathlib.Path(a.path)
    if not p.exists():
        sys.exit(f'No such file: {p}')
    data = p.read_bytes()
    conn = db.init()
    try:
        prev = upload.preview(conn, a.series, p.name, data)
        result = prev.pop('_result')
        print(f"Preview — {prev['label']} ({a.series})")
        print(f"  rows {prev['total_rows']}  accepted {prev['accepted_count']}  "
              f"rejected {prev['rejected_count']}")
        if prev['date_range']:
            print(f"  range {prev['date_range'][0]} .. {prev['date_range'][1]}")
        for r in prev['rejected'][:8]:
            print(f"  rejected row {r['row']}: {r['reason']}")
        if prev['blocking']:
            sys.exit(f"\nREFUSED: {prev['blocking']}")
        if not a.commit:
            print('\nDry run. Re-run with --commit to write.')
            return
        saved = upload.commit_upload(conn, a.series, p.name, result)
    except upload.UploadError as e:
        sys.exit(f'REFUSED: {e}')
    finally:
        conn.close()
    print(f"\nCommitted: {saved['accepted']} accepted, {saved['rejected']} rejected, "
          f"{saved['added']} new rows.")


def cmd_feeds(a):
    for f in MANUAL_FEEDS:
        print(f'{f.key:26} {f.freq:8} {f.unit:20} template: {", ".join(f.template)}')
        if f.note:
            print(f'{"":26} {f.note}')


def cmd_serve(a):
    from .api import serve
    serve(a.host, a.port)


def main(argv=None):
    p = argparse.ArgumentParser(prog='brassguard', description='Brass Guard backend CLI')
    sub = p.add_subparsers(dest='cmd', required=True)

    sub.add_parser('init', help='create the database and seed the feed registry'
                   ).set_defaults(fn=cmd_init)

    s = sub.add_parser('sync', help='run every automatable feed (Sync All)')
    s.set_defaults(fn=cmd_sync)

    s = sub.add_parser('week', help="this week's band and floor")
    s.add_argument('--cover', type=int, default=1, help='cover days (default 1)')
    s.set_defaults(fn=cmd_week)

    s = sub.add_parser('quote', help='check a price and log it')
    s.add_argument('price', type=float)
    s.add_argument('--cover', type=int, default=1)
    s.add_argument('--market', default='')
    s.add_argument('--note', default='')
    s.set_defaults(fn=cmd_quote)

    s = sub.add_parser('history', help='recent quotes')
    s.add_argument('--limit', type=int, default=20)
    s.set_defaults(fn=cmd_history)

    s = sub.add_parser('upload', help='preview or commit a manual feed file')
    s.add_argument('series')
    s.add_argument('path')
    s.add_argument('--commit', action='store_true')
    s.set_defaults(fn=cmd_upload)

    sub.add_parser('feeds', help='list feeds that need manual upload'
                   ).set_defaults(fn=cmd_feeds)

    s = sub.add_parser('serve', help='run the API')
    s.add_argument('--host', default='127.0.0.1')
    s.add_argument('--port', type=int, default=8000)
    s.set_defaults(fn=cmd_serve)

    a = p.parse_args(argv)
    a.fn(a)


if __name__ == '__main__':
    main()
