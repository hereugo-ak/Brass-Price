// The honesty screen: what came in, what couldn't, and what must be uploaded
// by hand. Failures are surfaced, never smoothed over.

import { useRef, useState } from 'react'
import type { ManualFeed, SyncResponse, UploadPreview } from '../api/types'
import { api } from '../api/client'
import { hm } from '../lib/format'
import { useFeedLabels } from '../lib/labels'
import { useAsync } from '../lib/hooks'
import { useToast } from '../components/Toast'

export function DataScreen({ offline, onSynced }: { offline: boolean; onSynced: () => void }) {
  const toast = useToast()
  const labels = useFeedLabels()
  const templates = useAsync(() => api.uploadTemplates(), [offline])
  const last = useAsync(() => api.syncLast(), [offline])
  const [syncing, setSyncing] = useState(false)
  const [syncResult, setSyncResult] = useState<SyncResponse | null>(null)

  // upload state
  const [feedKey, setFeedKey] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<UploadPreview | null>(null)
  const [busy, setBusy] = useState<'preview' | 'commit' | null>(null)

  const fileRef = useRef<HTMLInputElement>(null)
  const feeds: ManualFeed[] = templates.data?.feeds ?? []
  const chosen = feeds.find((f) => f.series === feedKey) ?? null

  async function syncAll() {
    setSyncing(true)
    try {
      const res = await api.sync(true)
      setSyncResult(res)
      last.reload()
      onSynced()
      const ok = res.counts.OK ?? 0
      const issues = res.action_required.length
      toast(
        issues > 0 ? 'info' : 'ok',
        `Sync finished: ${ok} OK${issues ? `, ${issues} need attention` : ''}.`,
      )
    } catch (e) {
      toast('err', (e as Error).message)
    } finally {
      setSyncing(false)
    }
  }

  async function doPreview() {
    if (!feedKey || !file) return
    setBusy('preview')
    setPreview(null)
    try {
      const res = await api.uploadPreview(feedKey, file)
      setPreview(res)
    } catch (e) {
      toast('err', (e as Error).message)
    } finally {
      setBusy(null)
    }
  }

  async function doCommit() {
    if (!preview || !file) return
    setBusy('commit')
    try {
      const res = await api.uploadCommit(preview.series, preview.filename, file)
      toast('ok', res.message)
      setPreview(null)
      setFile(null)
      if (fileRef.current) fileRef.current.value = ''
      onSynced()
    } catch (e) {
      toast('err', (e as Error).message)
    } finally {
      setBusy(null)
    }
  }

  // feed status grid, preferring a fresh sync result over the stored last run
  type FeedDisp = { series: string; label?: string; status: string; message?: string; rows?: number }
  let feedRows: FeedDisp[] = []
  let runInfo: { started_at: string; trigger: string } | null = null
  if (syncResult) {
    feedRows = syncResult.feeds.map((f) => ({
      series: f.series,
      label: f.label,
      status: f.status,
      message: f.message || f.action,
      rows: f.rows_added,
    }))
    runInfo = { started_at: syncResult.started_at, trigger: syncResult.trigger }
  } else if (last.data?.run) {
    feedRows = last.data.run.feeds.map((f) => ({
      series: f.series,
      status: f.status,
      message: f.message,
      rows: f.rows,
    }))
    runInfo = { started_at: last.data.run.started_at, trigger: last.data.run.trigger }
  }

  return (
    <div className="screen-in">
      <div className="sec-head">
        <span className="sec-kicker">Data</span>
        <h2>Feeds, sync, and manual uploads</h2>
        {runInfo && (
          <span className="aux">
            last run {hm(runInfo.started_at)} · {runInfo.trigger}
          </span>
        )}
      </div>

      <div
        style={{
          display: 'flex', alignItems: 'center', gap: 18, flexWrap: 'wrap',
          borderTop: '2px solid var(--tx-0)', borderBottom: '1px solid var(--line-2)',
          padding: '14px 0', marginTop: 18,
        }}
      >
        <button className="btn primary" onClick={syncAll} disabled={syncing || offline}>
          {syncing ? 'Syncing…' : 'Sync all feeds'}
        </button>
        <div style={{ font: '400 12px/1.6 var(--sans)', color: 'var(--tx-2)', flex: 1, minWidth: 240 }}>
          Runs every automatable feed. Sites that block automation report{' '}
          <span className="chip MANUAL">MANUAL</span> and wait for an upload — nothing is
          guessed to fill the gap.
        </div>
      </div>

          {feedRows.length > 0 && (
            <div className="feedgrid">
              {feedRows.map((f) => (
            <div className="feedrow" key={f.series}>
              <div style={{ minWidth: 0 }}>
                <div className="nm">{labels.get(f.series) ?? f.label ?? f.series}</div>
                <div className="sub">{f.series}{f.rows ? ` · +${f.rows} rows` : ''}</div>
              </div>
              <div className="right">
                <span className={`chip ${f.status}`}>{f.status}</span>
                {f.message && (
                  <div className="sub" style={{ maxWidth: 260, marginTop: 4, whiteSpace: 'normal' }}>
                    {f.message}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {!offline && !syncResult && last.data?.message && (
        <div className="empty" style={{ marginTop: 14 }}>
          <b>Sync All has never been run.</b>
          {last.data.message}
        </div>
      )}

      {/* ---- manual upload ---- */}
      <div className="sec-head" style={{ marginTop: 42 }}>
        <span className="sec-kicker">Manual upload</span>
        <h2>For the feeds that block automation</h2>
      </div>

      {offline ? (
        <div className="empty"><b>Offline.</b> Connect to the backend to upload.</div>
      ) : (
        <div className="up-grid" style={{ marginTop: 8 }}>
          <div>
            <div>
              <label className="flabel">Feed</label>
              <select
                className="select"
                value={feedKey}
                onChange={(e) => {
                  setFeedKey(e.target.value)
                  setPreview(null)
                  setFile(null)
                }}
              >
                <option value="">Choose a manual feed…</option>
                {feeds.map((f) => (
                  <option key={f.series} value={f.series}>
                    {f.label} — {f.freq}
                  </option>
                ))}
              </select>

              {chosen && (
                <>
                  <div className="tmpl">
                    columns: {chosen.template.map((t, i) => (
                      <span key={t}>
                        <code>{t}</code>
                        {i < chosen.template.length - 1 ? ' ' : ''}
                      </span>
                    ))}
                  </div>
                  {chosen.note && <div className="help">{chosen.note}</div>}
                </>
              )}

              <div style={{ marginTop: 14 }}>
                <label className="flabel">File — CSV or XLSX</label>
                <input
                  ref={fileRef}
                  type="file"
                  className="filein"
                  accept=".csv,.xlsx,.xls,.tsv"
                  onChange={(e) => {
                    setFile(e.target.files?.[0] ?? null)
                    setPreview(null)
                  }}
                />
              </div>

              <button
                className="btn wide"
                style={{ marginTop: 14 }}
                onClick={doPreview}
                disabled={!feedKey || !file || !!busy}
              >
                {busy === 'preview' ? 'Reading…' : 'Preview & validate'}
              </button>
            </div>
          </div>

          <div>
            {!preview && (
              <div className="empty">
                <b>Preview first, commit second.</b>
                <p>Nothing is written until the file parses and at least one row validates.
                Rejected rows carry a reason you can act on.</p>
              </div>
            )}

            {preview && (
              <>
                {preview.blocking ? (
                  <div className="notice err">
                    <span className="glyph">✕</span>
                    <div>{preview.blocking}</div>
                  </div>
                ) : (
                  <div className="checkrow">
                    <div>
                      <div className="k">Accepted</div>
                      <div className="v" style={{ color: 'var(--safe)' }}>{preview.accepted_count}</div>
                    </div>
                    <div>
                      <div className="k">Rejected</div>
                      <div className="v" style={{ color: preview.rejected_count ? 'var(--thin)' : 'var(--tx-2)' }}>
                        {preview.rejected_count}
                      </div>
                    </div>
                    <div>
                      <div className="k">Range</div>
                      <div className="v" style={{ font: '400 13px var(--mono)', color: 'var(--tx-1)' }}>
                        {preview.date_range ? `${preview.date_range[0]} → ${preview.date_range[1]}` : '—'}
                      </div>
                    </div>
                  </div>
                )}

                {preview.sample.length > 0 && (
                  <table className="dtable" style={{ marginTop: 12 }}>
                    <thead>
                      <tr>
                        <th>Date</th>
                        <th className="r">Value</th>
                      </tr>
                    </thead>
                    <tbody>
                      {preview.sample.map((s, i) => (
                        <tr key={i}>
                          <td className="num">{s.date}</td>
                          <td className="num r">{s.value}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}

                {preview.rejected.length > 0 && (
                  <div className="rej">
                    <div className="k">Rejected rows</div>
                    <ul>
                      {preview.rejected.slice(0, 8).map((r, i) => (
                        <li key={i}>
                          row {r.row}: {r.reason}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <button
                  className="btn primary wide"
                  style={{ marginTop: 14 }}
                  onClick={doCommit}
                  disabled={!!preview.blocking || !!busy}
                >
                  {busy === 'commit' ? 'Committing…' : `Commit ${preview.accepted_count} row(s)`}
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
