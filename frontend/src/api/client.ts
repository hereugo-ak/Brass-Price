// Connection to the Brass Guard API. The client never recomputes verdicts or
// band maths — when the backend is unreachable it shows the last cached week,
// clearly marked, and disables actions that require the engine.

import type {
  Band,
  ConfigResponse,
  HealthResponse,
  HistoryResponse,
  NoteHistoryResponse,
  NoteResponse,
  NoteSendResponse,
  QuoteResponse,
  ReportResponse,
  SyncLastResponse,
  SyncResponse,
  UploadCommit,
  UploadPreview,
} from './types'

const URL_KEY = 'brassguard.backend_url'
const WEEK_CACHE_KEY = 'brassguard.cached_week'

export const DEFAULT_BACKEND = 'http://127.0.0.1:8000'

export function getBackendUrl(): string {
  try {
    return localStorage.getItem(URL_KEY) || DEFAULT_BACKEND
  } catch {
    return DEFAULT_BACKEND
  }
}

export function setBackendUrl(url: string) {
  try {
    localStorage.setItem(URL_KEY, url.replace(/\/+$/, ''))
  } catch {
    /* private mode: session-only */
  }
}

export class ApiError extends Error {
  status: number
  detail: string
  constructor(status: number, detail: string) {
    super(detail)
    this.status = status
    this.detail = detail
  }
}

async function call<T>(path: string, init?: RequestInit): Promise<T> {
  const base = getBackendUrl()
  let res: Response
  try {
    res = await fetch(base + path, {
      ...init,
      headers: { 'Content-Type': 'application/json', ...init?.headers },
    })
  } catch (e) {
    throw new ApiError(0, 'The backend is unreachable. Start it with start_local.bat or python -m app.cli serve.')
  }
  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`
    try {
      const body = await res.json()
      if (body?.detail) detail = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail)
    } catch {
      /* non-JSON error body */
    }
    throw new ApiError(res.status, detail)
  }
  return res.json() as Promise<T>
}

export const api = {
  health: () => call<HealthResponse>('/health'),
  week: (coverDays: number) => call<Band>(`/week?cover_days=${coverDays}`),
  quote: (price: number, coverDays: number, market = '', note = '') =>
    call<QuoteResponse>('/quote', {
      method: 'POST',
      body: JSON.stringify({ price, cover_days: coverDays, market, note }),
    }),
  history: (limit = 100) => call<HistoryResponse>(`/history?limit=${limit}`),
  report: (limit = 200) => call<ReportResponse>(`/report?limit=${limit}`),
  config: () => call<ConfigResponse>('/config'),
  sync: (includeManual = true) =>
    call<SyncResponse>(`/sync?include_manual=${includeManual}`, { method: 'POST' }),
  syncLast: () => call<SyncLastResponse>('/sync/last'),
  uploadTemplates: () =>
    call<{ feeds: import('./types').ManualFeed[] }>('/upload/templates'),
  uploadPreview: (series: string, file: File) => {
    const form = new FormData()
    form.append('file', file)
    return fetch(`${getBackendUrl()}/upload/preview?series=${encodeURIComponent(series)}`, {
      method: 'POST',
      body: form,
    }).then(async (res) => {
      if (!res.ok) {
        const body = await res.json().catch(() => null)
        throw new ApiError(res.status, body?.detail || `${res.status} ${res.statusText}`)
      }
      return (await res.json()) as UploadPreview
    })
  },
  uploadCommit: (series: string, filename: string, file: File) =>
    new Promise<UploadCommit>((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => {
        const dataB64 = (reader.result as string).split(',')[1]
        call<UploadCommit>('/upload/commit', {
          method: 'POST',
          body: JSON.stringify({ series, filename, data_b64: dataB64 }),
        }).then(resolve, reject)
      }
      reader.onerror = () => reject(new ApiError(0, 'Could not read the file.'))
      reader.readAsDataURL(file)
    }),
  note: () => call<NoteResponse>('/note'),
  noteSend: (channel: string) =>
    call<NoteSendResponse>(`/note/send?channel=${encodeURIComponent(channel)}`, {
      method: 'POST',
    }),
  noteHistory: () => call<NoteHistoryResponse>('/note/history?limit=20'),
}

// ---- offline cache: the last good /week, shown with an explicit banner ----

export function cacheWeeks(bands: Partial<Record<number, Band>>) {
  try {
    localStorage.setItem(WEEK_CACHE_KEY, JSON.stringify({ at: Date.now(), bands }))
  } catch {
    /* ignore */
  }
}

export function cachedWeeks(): { at: number; bands: Partial<Record<number, Band>> } | null {
  try {
    const raw = localStorage.getItem(WEEK_CACHE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}
