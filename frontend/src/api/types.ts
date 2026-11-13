// Types mirroring app/api.py responses exactly. The backend is the single
// source of truth; nothing on this side recomputes verdicts or band maths.

export type Verdict = 'safe' | 'thin' | 'risky' | 'stop'
export type FeedStatus = 'OK' | 'STALE' | 'BLOCKED' | 'FAILED' | 'MANUAL'

export interface BandInputs {
  metal: number
  ratio: number
  sd: number
  transport: number
  margin: number
}

export interface Provenance {
  metal_source: 'mcx' | 'lme' | 'default'
  metal_age_days: number | null
  transport_source: 'owner' | 'assumed'
  as_of: string | null
  model_version: string
}

export interface Band {
  model_version: string
  cover_days: number
  metal: number
  transport: number
  low: number
  mid: number
  high: number
  floor: number
  inputs: BandInputs
  provenance?: Provenance
  warnings?: string[]
  stale?: boolean
}

export interface WeekResponse extends Band {
  cover_days: number
}

export interface QuoteResponse {
  quote_id: number
  price: number
  cover_days: number
  verdict: Verdict
  floor: number
  high: number
  mid: number
  gap_per_kg: number
  gap_100kg: number
  gap_5500kg: number
  band: Band
  quoted_at: string
  model_version: string
  verdict_copy: string
}

export interface QuoteRow {
  id: number
  quoted_at: string
  price: number
  cover_days: number
  floor_at_time: number
  high_at_time: number
  gap: number
  verdict: Verdict
  market: string
  note: string
  model_version: string
}

export interface HistoryResponse {
  total_quotes: number
  below_floor: number
  below_floor_rate: number | null
  quotes: QuoteRow[]
}

export interface ReportQuote {
  id: number
  quoted_at: string
  price: number
  cover_days: number
  floor: number
  verdict: Verdict
  gap_per_kg: number
  model_version: string
  realised_cost: number | null
  realised_source: 'mcx' | 'lme' | null
  covered: boolean | null
  realised_gap?: number
  loss_if_quoted_100kg?: number
}

export interface SeriesPoint {
  at: string
  floor: number
  realised: number | null
}

export interface ReportResponse {
  total_quotes: number
  scored_quotes: number
  unscored_quotes: number
  below_floor_quotes: number
  below_floor_rate: number | null
  floor_coverage_rate: number | null
  floor_coverage_target: number
  exposure_flagged_per_100kg: number
  loss_if_all_quoted_per_100kg: number
  order_kg: number
  quotes: ReportQuote[]
  series: SeriesPoint[]
}

export interface SyncFeedResult {
  series: string
  label: string
  mode: string
  status: FeedStatus
  rows_added: number
  age_days: number | null
  http_status: number | null
  message: string
  action: string
}

export interface SyncResponse {
  run_id: number
  started_at: string
  finished_at: string
  trigger: string
  feeds: SyncFeedResult[]
  counts: Record<string, number>
  action_required: SyncFeedResult[]
}

export interface SyncLastRunItem {
  run_id: number
  series: string
  status: FeedStatus
  rows: number
  http_status: number | null
  message: string
  duration_ms: number
}

export interface SyncLastResponse {
  run: {
    run_id: number
    started_at: string
    finished_at: string
    trigger: string
    feeds: SyncLastRunItem[]
  } | null
  message?: string
}

export interface ManualFeed {
  series: string
  label: string
  freq: string
  unit: string
  template: string[]
  note: string
  source: string
}

export interface UploadPreview {
  series: string
  label: string
  filename: string
  template: string[]
  note: string
  total_rows: number
  accepted_count: number
  rejected_count: number
  rejected: { row: number; reason: string }[]
  date_range: [string, string] | null
  sample: { date: string; value: number }[]
  blocking: string | null
}

export interface UploadCommit {
  series: string
  filename: string
  rows_in_file: number
  accepted: number
  added: number
  rejected: number
  date_range: [string, string] | null
  message: string
}

export interface NoteResponse {
  week_start: string
  body: string
  floors: { same_day: number; d15: number; d30: number }
  band: { low: number; mid: number; high: number }
  model_version: string
  provisional: boolean
  missing_feeds: string[]
  warnings: string[]
}

export interface NoteSendResponse {
  channel: string
  ok: boolean
  path?: string
  message: string
  note_id?: number
  week_start?: string
  provisional?: boolean
  dry_run?: boolean
  note?: NoteResponse
  would_send_via?: string
}

export interface NoteHistoryResponse {
  notes: { id: number; week_start: string; channel: string; sent_at: string | null; chars: number }[]
  total: number
}

export interface ConfigFeed {
  key: string
  label: string
  mode: 'auto' | 'manual'
  freq: string
  lag_days: number
  unit: string
  source: string
}

export interface ConfigResponse {
  model_version: string
  db_path: string
  feeds: ConfigFeed[]
  verdicts: Record<Verdict, string>
}

export interface HealthResponse {
  status: string
  model_version: string
  observations: number
  quotes: number
}
