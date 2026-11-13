// Formatting helpers. Indian rupee grouping, consistent tabular figures.

const inrFull = new Intl.NumberFormat('en-IN', {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
})

const inrRound = new Intl.NumberFormat('en-IN', {
  maximumFractionDigits: 0,
})

export function fmt(v: number | null | undefined, dp = 2): string {
  if (v === null || v === undefined || Number.isNaN(v)) return '—'
  return dp === 0 ? inrRound.format(v) : inrFull.format(v)
}

/** ₹950.40 — negatives carry the sign before the mark: −₹90.40 */
export function rs(v: number | null | undefined, dp = 2): string {
  return v === null || v === undefined || Number.isNaN(v) ? '—' : `${v < 0 ? '−' : ''}₹${fmt(Math.abs(v), dp)}`
}

/** ₹29,558 — big sums get no decimals and Indian grouping (2,30,000) */
export function rsSum(v: number | null | undefined): string {
  return v === null || v === undefined || Number.isNaN(v) ? '—' : `${v < 0 ? '−' : ''}₹${fmt(Math.abs(v), 0)}`
}

export function pct(v: number | null | undefined): string {
  if (v === null || v === undefined || Number.isNaN(v)) return '—'
  return `${(v * 100).toFixed(1)}%`
}

export function day(iso: string | null | undefined): string {
  if (!iso) return '—'
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso.slice(0, 10)
  return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short' })
}

export function dayFull(iso: string | null | undefined): string {
  if (!iso) return '—'
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso.slice(0, 10)
  return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
}

export function hm(iso: string | null | undefined): string {
  if (!iso) return '—'
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso
  return d.toLocaleString('en-IN', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit', hour12: false })
}

export function ageDays(n: number | null | undefined): string {
  if (n === null || n === undefined) return 'age unknown'
  if (n <= 0) return 'today'
  if (n === 1) return '1 day old'
  return `${n} days old`
}

export const VERDICT_LABEL: Record<string, string> = {
  safe: 'SAFE',
  thin: 'THIN',
  risky: 'RISKY',
  stop: 'STOP',
}

export const VERDICT_COLOR: Record<string, string> = {
  safe: 'var(--safe)',
  thin: 'var(--thin)',
  risky: 'var(--risky)',
  stop: 'var(--stop)',
}
