// Floor vs realised cost, week by week. The only chart in the product:
// did the floor hold against what the metal actually cost afterwards?

import type { SeriesPoint } from '../api/types'
import { day, fmt } from '../lib/format'

const W = 1000
const H = 250
const PADL = 16
const PADR = 64
const PADT = 22
const PADB = 34

interface Props {
  series: SeriesPoint[]
}

export function TrendChart({ series }: Props) {
  const pts = series.filter((p) => p.realised !== null)
  if (pts.length < 2) {
    return (
      <div className="chart-empty">
        coverage chart appears once quotes are logged and realised costs arrive
      </div>
    )
  }

  const values = pts.flatMap((p) => [p.floor, p.realised as number])
  let min = Math.min(...values)
  let max = Math.max(...values)
  const span = Math.max(max - min, 20)
  min -= span * 0.1
  max += span * 0.1

  const x = (i: number) => PADL + (i / (pts.length - 1)) * (W - PADL - PADR)
  const y = (v: number) => PADT + (1 - (v - min) / (max - min)) * (H - PADT - PADB)

  const path = (get: (p: SeriesPoint) => number) =>
    pts.map((p, i) => `${i === 0 ? 'M' : 'L'}${x(i).toFixed(1)},${y(get(p)).toFixed(1)}`).join(' ')

  // y grid: 4 hairlines
  const gridY = [0, 1 / 3, 2 / 3, 1].map((t) => min + t * (max - min))

  return (
    <svg className="chart-svg" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Floor versus realised cost">
      {gridY.map((v) => (
        <g key={v}>
          <line className="grid" x1={PADL} y1={y(v)} x2={W - PADR} y2={y(v)} />
          <text className="lbl" x={W - PADR + 8} y={y(v) + 3.5}>
            {fmt(v, 0)}
          </text>
        </g>
      ))}

      <path className="real-line" d={path((p) => p.realised as number)} />
      <path className="floor-line" d={path((p) => p.floor)} />
      {pts.map((p, i) =>
        p.realised !== null ? (
          <circle key={i} className="real-dot" cx={x(i)} cy={y(p.realised)} r={2.4} />
        ) : null,
      )}

      <text className="lbl" x={PADL} y={H - 12}>
        {day(pts[0].at)}
      </text>
      <text className="lbl" x={W - PADR} y={H - 12} textAnchor="end">
        {day(pts[pts.length - 1].at)}
      </text>

      <g transform={`translate(${PADL}, ${14})`}>
        <line x1={0} y1={-4} x2={22} y2={-4} className="floor-line" />
        <text className="legend" x={30} y={0}>floor</text>
        <line x1={78} y1={-4} x2={100} y2={-4} className="real-line" />
        <text className="legend" x={108} y={0}>realised</text>
      </g>
    </svg>
  )
}
