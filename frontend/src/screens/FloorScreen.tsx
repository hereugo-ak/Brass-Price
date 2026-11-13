// The operate core: read the floor, place a price on the rule, get a verdict.
// Every check is logged by the backend — that is the quote ledger.
// The hero is drawn like an engineering price-sheet: a dimensioned number,
// a title block carrying the provenance, and a hatched band rule.

import { useMemo, useState } from 'react'
import type { Band, QuoteResponse, Verdict } from '../api/types'
import { Gauge } from '../components/Gauge'
import { api } from '../api/client'
import { ageDays, fmt, rs, rsSum, VERDICT_LABEL } from '../lib/format'
import { useAsync } from '../lib/hooks'

interface Props {
  weeks: Partial<Record<number, Band>>
  offline: boolean
  cover: number
  setCover: (d: number) => void
  reloadWeeks: () => void
}

const COVERS = [
  { d: 1, label: 'Same day' },
  { d: 15, label: '15 days' },
  { d: 30, label: '30 days' },
]

export function FloorScreen({ weeks, offline, cover, setCover, reloadWeeks }: Props) {
  const band = weeks[cover] ?? weeks[1] ?? null
  const [price, setPrice] = useState('')
  const [market, setMarket] = useState('')
  const [result, setResult] = useState<QuoteResponse | null>(null)
  const [checking, setChecking] = useState(false)
  const [quoteErr, setQuoteErr] = useState<string | null>(null)

  const history = useAsync(() => api.history(5), [offline])

  const priceNum = useMemo(() => {
    const n = parseFloat(price.replace(/,/g, ''))
    return Number.isFinite(n) && n > 0 ? n : null
  }, [price])

  async function check() {
    if (!priceNum) return
    setChecking(true)
    setQuoteErr(null)
    try {
      const res = await api.quote(priceNum, cover, market)
      setResult(res)
      history.reload()
      reloadWeeks()
    } catch (e) {
      setQuoteErr((e as Error).message)
    } finally {
      setChecking(false)
    }
  }

  const stampColor: Record<Verdict, string> = {
    safe: 'safe',
    thin: 'thin',
    risky: 'risky',
    stop: 'stop',
  }

  return (
    <div className="sheet-in">
      {/* ---- hero: the floor, drawn ---- */}
      <div className="hero">
        <div className="floor-display">
          <span className="k">Quotation floor · {COVERS.find((c) => c.d === cover)?.label}</span>
          {band ? (
            <>
              <div className="floor-num">
                <span className="rs">₹</span>
                {fmt(band.floor)}
              </div>
              <div className="dimension">
                <div className="dim-line" />
                <div className="lbl">
                  hold <b>{cover === 1 ? 'the day' : `${cover} days`}</b>
                  {' '}· model <b>{band.model_version}</b>
                  {band.stale ? ' · provisional' : ''}
                </div>
              </div>
            </>
          ) : (
            <div className="floor-num skel">₹950.40</div>
          )}

          <div className="bandrow">
            <div>
              <div className="k">Low</div>
              <div className="v">{band ? fmt(band.low) : '—'}</div>
              <div className="s">bad month · p05 side</div>
            </div>
            <div>
              <div className="k">Middle</div>
              <div className="v">{band ? fmt(band.mid) : '—'}</div>
              <div className="s">expected</div>
            </div>
            <div>
              <div className="k">High</div>
              <div className="v up">{band ? fmt(band.high) : '—'}</div>
              <div className="s">upside risk · p95 side</div>
            </div>
          </div>
        </div>

        <div>
          <span className="seg-label">Cover period</span>
          <div className="seg" role="tablist" aria-label="Cover period">
            {COVERS.map((c) => (
              <button
                key={c.d}
                className={cover === c.d ? 'on' : ''}
                onClick={() => setCover(c.d)}
                aria-pressed={cover === c.d}
              >
                {c.label}
              </button>
            ))}
          </div>

          {/* title block — provenance as drawing cells */}
          <div className="titleblock" style={{ marginTop: 18 }}>
            <div className="tb-name">
              <span>Price sheet</span>
              <span className="doc">DRG BG-01 · {band ? band.model_version : '—'}</span>
            </div>
            <div className="cell">
              <span className="k">Metal</span>
              <span className="v">
                {band ? fmt(band.metal) : '—'}
                {band && (
                  <span className={`src-tag ${band.provenance?.metal_source === 'mcx' ? 'hot' : ''}`}>
                    {band.provenance?.metal_source}
                  </span>
                )}
              </span>
            </div>
            <div className="cell">
              <span className="k">Metal age</span>
              <span className={`v ${(band?.provenance?.metal_age_days ?? 99) > 7 ? 'warn' : ''}`}>
                {band ? ageDays(band.provenance?.metal_age_days) : '—'}
              </span>
            </div>
            <div className="cell">
              <span className="k">Ratio</span>
              <span className="v">
                {band ? <>{band.inputs.ratio} <small>± {band.inputs.sd}</small></> : '—'}
              </span>
            </div>
            <div className="cell">
              <span className="k">Transport</span>
              <span className="v">
                {band ? (
                  <>
                    {rs(band.transport)}
                    <span className={`src-tag ${band.provenance?.transport_source === 'owner' ? 'owner' : 'warn'}`}>
                      {band.provenance?.transport_source}
                    </span>
                  </>
                ) : '—'}
              </span>
            </div>
            <div className="cell">
              <span className="k">Margin</span>
              <span className="v">
                {band ? <>5% <small>× 1.05</small></> : '—'}
              </span>
            </div>
            <div className="cell">
              <span className="k">Status</span>
              <span className="v">
                {band ? (
                  <span className={`src-tag ${band.stale ? 'warn' : 'owner'}`}>
                    {band.stale ? 'provisional' : 'current'}
                  </span>
                ) : '—'}
              </span>
            </div>
          </div>

          {band && band.warnings && band.warnings.length > 0 && (
            <div className="notice">
              <span className="glyph">NOTE</span>
              <div>
                <ul>
                  {band.warnings.map((w, i) => (
                    <li key={i}>{w}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ---- the rule ---- */}
      {band && (
        <div className="rule-wrap">
          <Gauge band={band} price={priceNum} />
        </div>
      )}

      {/* ---- the formula: the whole model, one line ---- */}
      {band && (
        <div className="formula" aria-label="How the floor is built">
          <div className="f-term">
            <div className="k">Metal</div>
            <div className="v">{fmt(band.metal)}<small>{band.provenance?.metal_source}</small></div>
          </div>
          <div className="f-op">×</div>
          <div className="f-term">
            <div className="k">Ratio</div>
            <div className="v">{band.inputs.ratio}<small>measured</small></div>
          </div>
          <div className="f-op">+</div>
          <div className="f-term">
            <div className="k">Transport</div>
            <div className="v">{fmt(band.transport)}<small>{band.provenance?.transport_source}</small></div>
          </div>
          <div className="f-op">=</div>
          <div className="f-term">
            <div className="k">Expected</div>
            <div className="v">{fmt(band.mid)}</div>
          </div>
          <div className="f-op">+</div>
          <div className="f-term">
            <div className="k">Cushion</div>
            <div className="v">{fmt(band.high - band.mid)}<small>p95 risk</small></div>
          </div>
          <div className="f-op">×</div>
          <div className="f-term">
            <div className="k">Margin</div>
            <div className="v">1.05</div>
          </div>
          <div className="f-op">→</div>
          <div className="f-term">
            <div className="k">Floor</div>
            <div className="v serif">{fmt(band.floor)}</div>
          </div>
        </div>
      )}

      {/* ---- quote check ---- */}
      <hr className="secrule heavy" style={{ marginTop: 42 }} />
      <div className="check-grid">
        <div>
          <div className="entry">
            <label className="lab" htmlFor="qprice">Price you were quoted</label>
            <div className="entry-box">
              <span className="rs">₹</span>
              <input
                id="qprice"
                type="number"
                inputMode="decimal"
                step="0.01"
                min="0"
                placeholder="0.00"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && check()}
                disabled={offline}
              />
              <span className="unit">/ kg</span>
            </div>
            <div className="entry-hint">
              Compare against the {COVERS.find((c) => c.d === cover)?.label.toLowerCase()} floor.
              Every check is logged.
            </div>
          </div>
          <div className="entry text" style={{ marginTop: 22 }}>
            <label className="lab" htmlFor="qmarket">
              Market <span className="opt">— optional</span>
            </label>
            <div className="entry-box">
              <input
                id="qmarket"
                type="text"
                placeholder="e.g. Europe"
                value={market}
                onChange={(e) => setMarket(e.target.value)}
                maxLength={40}
                disabled={offline}
              />
            </div>
          </div>
          <div style={{ marginTop: 24 }}>
            <button className="btn primary" onClick={check} disabled={!priceNum || checking || offline}>
              {checking ? 'Checking…' : 'Check & log quote'}
            </button>
          </div>
          {quoteErr && (
            <div className="notice err">
              <span className="glyph">ERROR</span>
              <div>{quoteErr}</div>
            </div>
          )}
        </div>

        <div>
          {result ? (
            <div className={`stamp ${stampColor[result.verdict]}`}>
              <div className="head">
                {VERDICT_LABEL[result.verdict]}
                <span className="mk">no. {result.quote_id}</span>
                <span className="mk">{result.cover_days === 1 ? 'same day' : `${result.cover_days} d`}</span>
              </div>
              <div className="copy">{result.verdict_copy}</div>
              <div className="math">
                <span>floor <b>{rs(result.floor)}</b></span>
                <span>gap <b>{result.gap_per_kg >= 0 ? '+' : ''}{rs(result.gap_per_kg)}/kg</b></span>
                <span>on 100 kg <b>{result.gap_100kg >= 0 ? '+' : ''}{rsSum(result.gap_100kg)}</b></span>
                <span>on 5,500 kg <b>{result.gap_5500kg >= 0 ? '+' : ''}{rsSum(result.gap_5500kg)}</b></span>
              </div>
              <div className="meta">logged {new Date(result.quoted_at).toLocaleString('en-IN', { hour12: false })}</div>
            </div>
          ) : (
            <div className="empty">
              <b>The verdict appears here.</b>
              <p>Type a quoted price and place it on the rule. The stamp compares it against
              the computed floor — it is not a prediction.</p>
            </div>
          )}
          {history.data && history.data.quotes.length > 0 && (
            <table className="dtable" style={{ marginTop: 20 }}>
              <thead>
                <tr>
                  <th>Logged</th>
                  <th className="r">Price</th>
                  <th className="r">Floor</th>
                  <th>Verdict</th>
                </tr>
              </thead>
              <tbody>
                {history.data.quotes.map((q) => (
                  <tr key={q.id}>
                    <td className="dim">{new Date(q.quoted_at).toLocaleString('en-IN', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit', hour12: false })}</td>
                    <td className="num r">{fmt(q.price)}</td>
                    <td className="num r dim">{fmt(q.floor_at_time)}</td>
                    <td>
                      <span className="vdot">
                        <span className="d" style={{ background: `var(--${q.verdict})` }} />
                        <span style={{ color: `var(--${q.verdict})` }}>{q.verdict.toUpperCase()}</span>
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  )
}
