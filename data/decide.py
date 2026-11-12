#!/usr/bin/env python3
"""Decision-engine DEMO on public legs (no owner data needed).
Rule: BUY signal when copper 4wk momentum < -1% (dip) and INR 4wk move > -1%
(no rupee shock); range = last close +/- rolling naive-error bands.
Outputs data/decisions_demo.json + prints a sample Monday message.
Labeled DEMO until brass target + spreads plug in.
"""
import csv, json, math, pathlib

HERE = pathlib.Path(__file__).parent

def main():
    rows = list(csv.DictReader(open(HERE / 'features_weekly.csv')))
    cu = [float(r['PCOPPUSDM']) if r['PCOPPUSDM'] != '' else None for r in rows]
    fx = [float(r['DEXINUS']) if r['DEXINUS'] != '' else None for r in rows]
    sigs = []
    for i in range(60, len(rows)):
        if cu[i] is None or fx[i] is None or cu[i - 4] is None or fx[i - 4] is None:
            continue
        cm = cu[i] / cu[i - 4] - 1
        fm = fx[i] / fx[i - 4] - 1
        sigs.append({'week': rows[i]['week'], 'cu': cu[i], 'fx': fx[i],
                     'signal': 'BUY' if (cm < -0.01 and fm > -0.01) else 'WAIT'})
    # how did copper move the week after BUY signals? (informational only)
    fwd = []
    by_wk = {s['week']: s for s in sigs}
    for k in range(len(sigs) - 1):
        if sigs[k]['signal'] == 'BUY':
            w0, w1 = sigs[k]['cu'], sigs[k + 1]['cu']
            if w0 and w1:
                fwd.append(w1 / w0 - 1)
    n_buy = sum(1 for s in sigs if s['signal'] == 'BUY')
    out = {'mode': 'DEMO-public-legs', 'signals': len(sigs), 'buy_signals': n_buy,
           'buy_rate': round(n_buy / max(1, len(sigs)), 3),
           'avg_nextwk_move_after_buy': round(sum(fwd) / len(fwd), 4) if fwd else None,
           'last': sigs[-1] if sigs else None,
           'message': (f"DEMO Monday note ({sigs[-1]['week']}): copper ${sigs[-1]['cu']:,.0f}/t, "
                       f"INR {sigs[-1]['fx']:.2f} — signal {sigs[-1]['signal']}. "
                       f"Real message needs brass target + spreads.") if sigs else 'no data'}
    json.dump(out, open(HERE / 'decisions_demo.json', 'w'), indent=1)
    print(json.dumps(out, indent=1))

if __name__ == '__main__':
    main()
