// The proof screen: did the floor actually hold?
// Realised cost means the metal price current at the end of the cover period,
// from stored observations — never an estimate.

import type { ReportResponse } from '../api/types'
import { api } from '../api/client'
import { TrendChart } from '../components/TrendChart'
import { fmt, hm, pct, rs, rsSum } from '../lib/format'
import { useAsync } from '../lib/hooks'

export function HistoryScreen({ offline }: { offline: boolean }) {
  const report = useAsync(() => api.report(200), [offline])
  const data: ReportResponse | null = report.data

  return (
    <div className="screen-in">
      <div className="sec-head">
        <span className="sec-kicker">Report</span>
        <h2>Did the floor hold?</h2>
        <span className="aux">{data ? `${data.scored_quotes} of ${data.total_quotes} quotes scored` : ''}</span>
      </div>

      {report.error && (
        <div className="notice err">
          <span className="glyph">✕</span>
          <div>{report.error}</div>
        </div>
      )}

      {report.loading && (
        <div className="statband">
          {['', '', '', ''].map((_, i) => (
            <div key={i}>
              <div className="k skel">k</div>
              <div className="v skel">000</div>
            </div>
          ))}
        </div>
      )}

      {data && (
        <>
          <div className="statband">
            <div>
              <div className="k">Quotes logged</div>
              <div className="v">{data.total_quotes}</div>
              <div className="s">{data.unscored_quotes} awaiting realised cost</div>
            </div>
            <div>
              <div className="k">Floor coverage</div>
              <div
                className={`v ${
                  data.floor_coverage_rate === null
                    ? 'mute'
                    : data.floor_coverage_rate >= data.floor_coverage_target
                      ? 'good'
                      : 'bad'
                }`}
              >
                {pct(data.floor_coverage_rate)}
              </div>
              <div className="s">
                target <b>{pct(data.floor_coverage_target)}</b> · higher is better
              </div>
            </div>
            <div>
              <div className="k">Below floor</div>
              <div className={`v ${data.below_floor_quotes > 0 ? 'bad' : 'mute'}`}>
                {data.below_floor_quotes}
              </div>
              <div className="s">would have bought at a loss</div>
            </div>
            <div>
              <div className="k">Exposure flagged</div>
              <div className={`v ${data.exposure_flagged_per_100kg > 0 ? 'warn' : 'mute'}`}>
                {rsSum(data.exposure_flagged_per_100kg)}
              </div>
              <div className="s">per {data.order_kg} kg order</div>
            </div>
          </div>

          <div className="chart-panel">
            <div className="chart-cap">
              <span>Fig. 1 — floor vs realised cost</span>
              <span>₹/kg</span>
            </div>
            <TrendChart series={data.series} />
          </div>

          <div className="sec-head" style={{ marginTop: 36 }}>
            <span className="sec-kicker">Ledger</span>
            <h2>Every quote, scored</h2>
          </div>

          {data.quotes.length === 0 ? (
            <div className="empty">
              <b>No quotes logged yet.</b>
              Check a quote in Floor — every check lands here and is scored against the
              realised metal cost once its cover period ends.
            </div>
          ) : (
            <table className="dtable">
              <thead>
                <tr>
                  <th>Quoted</th>
                  <th className="r">Price</th>
                  <th className="r">Floor at time</th>
                  <th className="r">Gap</th>
                  <th>Verdict</th>
                  <th className="r">Realised</th>
                  <th>Covered</th>
                </tr>
              </thead>
              <tbody>
                {data.quotes.map((q) => (
                  <tr key={q.id}>
                    <td className="dim">{hm(q.quoted_at)}</td>
                    <td className="num r">{fmt(q.price)}</td>
                    <td className="num r dim">{fmt(q.floor)}</td>
                    <td className={`num r ${q.gap_per_kg < 0 ? '' : 'dim'}`}
                        style={q.gap_per_kg < 0 ? { color: 'var(--stop)' } : undefined}>
                      {q.gap_per_kg >= 0 ? '+' : ''}{fmt(q.gap_per_kg)}
                    </td>
                    <td>
                      <span className="vdot">
                        <span className="d" style={{ background: `var(--${q.verdict})` }} />
                        <span style={{ color: `var(--${q.verdict})` }}>{q.verdict.toUpperCase()}</span>
                      </span>
                    </td>
                    <td className="num r dim">{q.realised_cost !== null ? fmt(q.realised_cost) : '—'}</td>
                    <td>
                      {q.covered === null ? (
                        <span className="dim" style={{ font: '400 11px var(--mono)' }}>pending</span>
                      ) : q.covered ? (
                        <span style={{ color: 'var(--safe)', font: '500 11px var(--mono)' }}>held ✓</span>
                      ) : (
                        <span style={{ color: 'var(--stop)', font: '500 11px var(--mono)' }}>
                          missed{q.loss_if_quoted_100kg ? ` · ${rs(q.loss_if_quoted_100kg, 0)}` : ''}
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          {data.scored_quotes > 0 && data.loss_if_all_quoted_per_100kg > 0 && (
            <div className="notice" style={{ marginTop: 18 }}>
              <span className="glyph">Σ</span>
              <div>
                Had every logged quote been sent at its quoted price, the metal cost it
                missed totals <b>{rs(data.loss_if_all_quoted_per_100kg)}</b> per {data.order_kg} kg.
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
