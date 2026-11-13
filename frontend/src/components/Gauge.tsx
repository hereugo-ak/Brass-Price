// The signature instrument: a dimensioned engineering scale of the band.
// Verdict zones are hatched like a technical drawing — cross-hatch for the
// downside, line-hatch for the upside — so the needle's position reads as a
// drawing annotation, not a UI state. Callouts carry the three thresholds;
// the tick scale runs above the ruler so nothing collides with the hatch.

import type { Band } from '../api/types'

const W = 1200
const H = 172
const PAD = 30
const RULER_Y = 88
const ZONE_H = 30
const DIM_Y = RULER_Y + 3 + ZONE_H + 18

const ZONE_NAMES = ['STOP', 'RISKY', 'THIN', 'SAFE']
const ZONE_COLORS = ['var(--stop)', 'var(--risky)', 'var(--thin)', 'var(--safe)']
const ZONE_ANGLES = [45, 135, 45, 135]

interface Props {
  band: Band | null
  price: number | null
}

function HatchDefs() {
  return (
    <defs>
      {ZONE_COLORS.map((c, i) => (
        <pattern
          key={i}
          id={`hatch${i}`}
          patternUnits="userSpaceOnUse"
          width={7}
          height={7}
          patternTransform={`rotate(${ZONE_ANGLES[i]})`}
        >
          <line x1={0} y1={0} x2={0} y2={7} stroke={c} strokeWidth={1} opacity={0.34} />
        </pattern>
      ))}
    </defs>
  )
}

export function Gauge({ band, price }: Props) {
  if (!band) return null

  const { low, mid, high, floor } = band
  const lo = Math.min(low, price ?? Infinity)
  const hi = Math.max(floor, price ?? -Infinity)
  const span = Math.max(hi - lo, 60)
  const pad = span * 0.14
  const min = lo - pad
  const max = hi + pad

  const x = (v: number) => PAD + ((v - min) / (max - min)) * (W - 2 * PAD)

  const ticks: { v: number; major: boolean }[] = []
  for (let v = Math.ceil(min / 10) * 10; v <= max; v += 10) {
    ticks.push({ v, major: v % 50 === 0 })
  }

  const zones = [
    { from: min, to: mid },
    { from: mid, to: high },
    { from: high, to: floor },
    { from: floor, to: max },
  ].filter((z) => z.to > z.from + 1)

  // threshold callouts sit above the scale; major ticks that would label the
  // same spot are left unlabelled so the two never print over each other
  const callouts = [
    { v: mid, lbl: 'MID' },
    { v: high, lbl: 'HIGH' },
    { v: floor, lbl: 'FLOOR' },
  ]
  const nearCallout = (v: number) => callouts.some((m) => Math.abs(x(v) - x(m.v)) < 15)

  // needle value must be inside the drawn domain
  const px = price !== null ? Math.min(Math.max(price, min), max) : null

  return (
    <svg
      className="rule-svg"
      viewBox={`0 0 ${W} ${H}`}
      role="img"
      aria-label={`Price rule from ${Math.round(min)} to ${Math.round(max)} rupees per kg`}
    >
      <HatchDefs />

      {/* threshold callouts — leader lines down to the ruler */}
      {callouts.map((m) => (
        <g key={m.lbl}>
          <line
            x1={x(m.v)}
            y1={38}
            x2={x(m.v)}
            y2={RULER_Y}
            stroke="var(--line-3)"
            strokeWidth={1}
            strokeDasharray="2 4"
          />
          <text className="callout-lbl" x={x(m.v)} y={20} textAnchor="middle">
            {m.lbl}
          </text>
          <text className="callout-val" x={x(m.v)} y={33} textAnchor="middle">
            {Math.round(m.v)}
          </text>
        </g>
      ))}

      {/* the ruler */}
      <line className="ruler" x1={PAD - 8} y1={RULER_Y} x2={W - PAD + 8} y2={RULER_Y} />

      {/* hatched verdict zones below the ruler */}
      {zones.map((z, i) => {
        const x0 = x(z.from)
        const x1 = x(z.to)
        const w = Math.max(x1 - x0, 1)
        return (
          <g key={i}>
            <rect className="hatch" x={x0} y={RULER_Y + 3} width={w} height={ZONE_H} fill={`url(#hatch${i})`} />
            <rect x={x0} y={RULER_Y + 3} width={w} height={ZONE_H} fill="none" stroke={ZONE_COLORS[i]} strokeWidth={1} opacity={0.5} />
            {w > 60 && (
              <text className="zone-lbl" x={(x0 + x1) / 2} y={RULER_Y + 3 + ZONE_H / 2 + 3.5} textAnchor="middle" fill={ZONE_COLORS[i]}>
                {ZONE_NAMES[i]}
              </text>
            )}
          </g>
        )
      })}

      {/* ticks above the ruler, like a machinist's scale */}
      {ticks.map((t) => (
        <g key={t.v}>
          <line
            className={t.major ? 'tick-major' : 'tick-minor'}
            x1={x(t.v)}
            y1={RULER_Y}
            x2={x(t.v)}
            y2={RULER_Y - (t.major ? 12 : 6)}
          />
          {t.major && !nearCallout(t.v) && (
            <text className="tick-lbl" x={x(t.v)} y={RULER_Y - 18} textAnchor="middle">
              {Math.round(t.v)}
            </text>
          )}
        </g>
      ))}

      {/* dimension line with arrows — the label sits in a gap in the line */}
      <g>
        <line className="dim-line" x1={PAD} y1={DIM_Y} x2={W / 2 - 96} y2={DIM_Y} />
        <line className="dim-line" x1={W / 2 + 96} y1={DIM_Y} x2={W - PAD} y2={DIM_Y} />
        <path className="dim-arrow" d={`M${PAD},${DIM_Y} l7,-3.5 v7 z`} />
        <path className="dim-arrow" d={`M${W - PAD},${DIM_Y} l-7,-3.5 v7 z`} />
        <text className="dim-lbl" x={W / 2} y={DIM_Y + 3.5} textAnchor="middle">
          indicative range · ₹/kg
        </text>
      </g>

      {/* the quoted price needle */}
      {px !== null ? (
        <g className="needle" style={{ transform: `translateX(${x(px)}px)` }}>
          <line className="needle-line" x1={0} y1={44} x2={0} y2={RULER_Y + ZONE_H + 3} />
          <rect className="needle-cap" x={-31} y={26} width={62} height={20} rx={2} />
          <text className="needle-lbl" x={0} y={40} textAnchor="middle">
            ₹{Math.round(price ?? 0)}
          </text>
        </g>
      ) : (
        <text className="no-price" x={W / 2} y={DIM_Y + 22} textAnchor="middle">
          enter a quoted price — the needle is placed on the rule
        </text>
      )}
    </svg>
  )
}
