#!/usr/bin/env python3
"""Validate a manually downloaded MCX bhavcopy before it is treated as captured.
Usage: python3 check_mcx.py [path]

Why this exists: the 2026-10-09 capture recorded in the handoff is an HTML
frameset shell that points to a missing sheet001.htm. It has a .xls filename
and a plausible byte size, so it looked captured while containing zero prices.
This check fails closed so that cannot happen silently again.
"""
import pathlib
import re
import sys

MIN_PRICE_TOKENS = 6  # a real bhavcopy has dozens; a shell has none

def main():
    root = pathlib.Path(__file__).resolve().parent
    targets = [pathlib.Path(sys.argv[1])] if len(sys.argv) > 1 else sorted(
        (root / 'mcx_manual').glob('*')
    )
    targets = [p for p in targets if p.is_file() and p.suffix.lower() in ('.xls', '.xlsx', '.csv', '.htm', '.html')]
    if not targets:
        print('STOP: no bhavcopy files in data/mcx_manual/')
        return

    bad = 0
    for p in targets:
        raw = p.read_bytes()
        size = len(raw)
        kind = 'binary' if raw[:4] in (b'\xd0\xcf\x11\xe0', b'PK\x03\x04') else 'text'
        text = '' if kind == 'binary' else raw.decode('utf-8', 'ignore')

        is_frameset = 'frameset' in text.lower() and 'sheet001.htm' in text.lower()
        # numeric tokens long enough to be a price or a quantity
        prices = re.findall(r'\b\d{4,7}(?:\.\d{1,2})?\b', text) if kind == 'text' else []
        has_header = any(k in text.lower() for k in ('symbol', 'expiry', 'close', 'settle', 'open', 'high', 'low'))

        if kind == 'binary':
            verdict, note = 'OK', 'binary workbook — open with openpyxl/xlrd to confirm rows'
        elif is_frameset:
            verdict, note = 'FAIL', 'HTML frameset shell: points to missing sheet001.htm, contains no prices'
        elif not has_header or len(prices) < MIN_PRICE_TOKENS:
            verdict, note = 'FAIL', f'no bhavcopy table found (price_tokens={len(prices)}, header={has_header})'
        else:
            verdict, note = 'OK', f'bhavcopy table present (price_tokens={len(prices)})'

        if verdict == 'FAIL':
            bad += 1
        print(f'[{verdict}] {p.name} size={size} kind={kind} :: {note}')

    if bad:
        print(f'\nSTOP: {bad} file(s) unusable. Re-download the bhavcopy from mcxindia.com')
        print('-> Market Data -> Bhavcopy, and keep the whole dated download.')
        print('The browser saves a frameset + "_files/" folder; save the actual sheet,')
        print('or copy the visible table into a CSV. Do not mark MCX as captured until this passes.')
    else:
        print(f'\nOK: {len(targets)} file(s) passed the bhavcopy check.')

if __name__ == '__main__':
    main()
