import { useCallback, useEffect, useRef, useState } from 'react'
import type { Band } from './api/types'
import { api, cacheWeeks, cachedWeeks, DEFAULT_BACKEND, getBackendUrl, setBackendUrl } from './api/client'
import { ageDays, fmt } from './lib/format'
import { DataScreen } from './screens/DataScreen'
import { FloorScreen } from './screens/FloorScreen'
import { HistoryScreen } from './screens/HistoryScreen'
import { NoteScreen } from './screens/NoteScreen'
import { ToastProvider, useToast } from './components/Toast'

type Conn = 'connecting' | 'live' | 'off'
type Tab = 'floor' | 'note' | 'history' | 'data'

const TABS: { id: Tab; label: string }[] = [
  { id: 'floor', label: 'Floor' },
  { id: 'note', label: 'Weekly note' },
  { id: 'history', label: 'History' },
  { id: 'data', label: 'Data' },
]

function Mark() {
  return (
    <svg className="brand-mark" viewBox="0 0 32 32" aria-hidden="true">
      <rect width="32" height="32" rx="7" fill="var(--bg-2)" stroke="var(--line-2)" />
      <path d="M16 5.5 25 11v10l-9 5.5L7 21V11z" fill="none" stroke="var(--brass)" strokeWidth="1.8" />
      <path d="M16 10.5v11M11.5 13.2l9 5.6M20.5 13.2l-9 5.6" stroke="var(--brass)" strokeWidth="1.1" opacity=".55" />
    </svg>
  )
}

function Shell() {
  const toast = useToast()
  const [tab, setTab] = useState<Tab>('floor')
  const [conn, setConn] = useState<Conn>('connecting')
  const [modelVersion, setModelVersion] = useState<string>('')
  const [weeks, setWeeks] = useState<Partial<Record<number, Band>>>({})
  const [cover, setCover] = useState(1)
  const [settings, setSettings] = useState(false)
  const [everConnected, setEverConnected] = useState(false)
  const aliveRef = useRef(true)

  useEffect(() => () => void (aliveRef.current = false), [])

  // ---- connection: poll health, then load the three covers ----
  const connect = useCallback(
    async (announce = false) => {
      setConn('connecting')
      try {
        const h = await api.health()
        if (!aliveRef.current) return
        setModelVersion(h.model_version)
        const bands = await Promise.all(
          [1, 15, 30].map((d) => api.week(d).then((b) => [d, b] as const)),
        )
        if (!aliveRef.current) return
        const map: Partial<Record<number, Band>> = {}
        for (const [d, b] of bands) {
          map[d] = b
        }
        setWeeks(map)
        cacheWeeks(map)
        setWeeks(map)
        setConn('live')
        setEverConnected(true)
        if (announce) toast('ok', 'Connected to the Brass Guard API.')
      } catch {
        if (!aliveRef.current) return
        setConn('off')
      }
    },
    [toast],
  )

  useEffect(() => {
    connect(false)
    const iv = setInterval(() => {
      connect(false)
    }, 25000)
    return () => clearInterval(iv)
  }, [connect])

  const offline = conn !== 'live'
  const cached = offline ? cachedWeeks() : null
  // live weeks win; the cache fills the gaps so an offline reload still reads
  const merged: Partial<Record<number, Band>> = { ...(cached?.bands ?? {}), ...weeks }
  const shown: Band | null = merged[cover] ?? merged[1] ?? null

  const navAux =
    shown && shown.provenance
      ? `metal ${shown.provenance.metal_source} · ${ageDays(shown.provenance.metal_age_days)}`
      : ''

  return (
    <div className="shell">
      {/* ---- masthead ---- */}
      <header className="masthead">
        <div className="mast-row">
          <div className="wordmark">
            <Mark />
            <div>
              <h1>Brass Guard</h1>
              <div className="est">Castle Hardwares · Aligarh · Est. 1965</div>
            </div>
          </div>
          <div className="mast-meta">
            <span className="hide-m">{modelVersion ? `model ${modelVersion}` : ''}</span>
            <button
              className={`conn ${conn === 'live' ? 'live' : conn === 'off' ? 'off' : ''}`}
              onClick={() => setSettings(true)}
              title="Backend connection"
            >
              <span className="dot" />
              {conn === 'live' ? 'live' : conn === 'connecting' ? 'connecting' : 'offline'}
            </button>
          </div>
        </div>
        <div className="mast-rules" />
      </header>

      {/* ---- section index ---- */}
      <nav className="index" aria-label="Sections">
        {TABS.map((t, i) => (
          <button key={t.id} className={tab === t.id ? 'on' : ''} onClick={() => setTab(t.id)}>
            <span className="no">0{i + 1}</span>
            {t.label}
          </button>
        ))}
        <span className="indextail">{navAux}</span>
      </nav>

      {/* ---- price strip ---- */}
      {shown && (
        <div className="strip" role="status">
          <div className="cell">
            <span className="k">Metal</span>
            <span className="v">{fmt(shown.metal)}</span>
            <span className="meta">{shown.provenance?.metal_source}</span>
          </div>
          <div className="cell">
            <span className="k">Low</span>
            <span className="v">{fmt(shown.low)}</span>
          </div>
          <div className="cell">
            <span className="k">Mid</span>
            <span className="v">{fmt(shown.mid)}</span>
          </div>
          <div className="cell">
            <span className="k">High</span>
            <span className="v">{fmt(shown.high)}</span>
          </div>
          {weeks[1] && (
            <div className="cell">
              <span className="k">Floor · same day</span>
              <span className="v lead">{fmt(weeks[1].floor)}</span>
            </div>
          )}
          {weeks[15] && (
            <div className="cell">
              <span className="k">15 d</span>
              <span className="v">{fmt(weeks[15].floor)}</span>
            </div>
          )}
          {weeks[30] && (
            <div className="cell">
              <span className="k">30 d</span>
              <span className="v">{fmt(weeks[30].floor)}</span>
            </div>
          )}
          <div className="cell" style={{ borderRight: 0 }}>
            <span className="k">Transport</span>
            <span className="v">{fmt(shown.transport)}</span>
            <span className="meta">{shown.provenance?.transport_source}</span>
          </div>
        </div>
      )}

      {/* ---- offline banner ---- */}
      {offline && (
        <div className="offline-note">
          <div className="notice err">
            <span className="glyph">OFFLINE</span>
            <div>
              <b>The backend is not reachable.</b>
              {shown
                ? ' Showing the last synced floor from cache. Verdicts and logging are disabled until the connection returns.'
                : ' Start the API with start_local.bat, or set the backend address in connection settings.'}
            </div>
          </div>
        </div>
      )}

      {/* ---- first run ---- */}
      {conn === 'off' && !everConnected && !shown && (
        <div className="sheet">
          <div className="firstrun">
            <h3>Three steps to the first floor</h3>
            <ol>
              <li>
                Start the API: <code>python -m app.cli serve</code> — or double-click{' '}
                <code>start_local.bat</code> on Windows.
              </li>
              <li>
                Point this app at it: default is <code>{DEFAULT_BACKEND}</code> — change it in
                connection settings.
              </li>
              <li>
                Run <b>Data → Sync all feeds</b>, then upload the manual feeds (MCX bhavcopy)
                so the metal input is current.
              </li>
            </ol>
            <div style={{ marginTop: 18 }}>
              <button className="btn" onClick={() => setSettings(true)}>
                Connection settings
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ---- screens ---- */}
      {!(conn === 'off' && !everConnected && !shown) && (
        <main className="sheet" key={tab}>
          {tab === 'floor' && (
            <FloorScreen
              weeks={merged}
              offline={offline}
              cover={cover}
              setCover={setCover}
              reloadWeeks={() => connect(false)}
            />
          )}
          {tab === 'note' && <NoteScreen offline={offline} />}
          {tab === 'history' && <HistoryScreen offline={offline} />}
          {tab === 'data' && (
            <DataScreen offline={offline} onSynced={() => connect(false)} />
          )}
        </main>
      )}

      {settings && (
        <SettingsModal
          onClose={() => setSettings(false)}
          onSaved={(ok) => {
            setSettings(false)
            if (ok) connect(true)
          }}
        />
      )}
    </div>
  )
}

function SettingsModal({
  onClose,
  onSaved,
}: {
  onClose: () => void
  onSaved: (connected: boolean) => void
}) {
  const [url, setUrl] = useState(getBackendUrl())
  const [testing, setTesting] = useState(false)
  const [msg, setMsg] = useState<string | null>(null)

  async function save() {
    const clean = url.trim().replace(/\/+$/, '')
    setBackendUrl(clean || DEFAULT_BACKEND)
    setTesting(true)
    setMsg(null)
    try {
      const h = await api.health()
      onSaved(true)
      setMsg(`Connected · model ${h.model_version} · ${h.observations} observations`)
    } catch (e) {
      setTesting(false)
      setMsg((e as Error).message)
    }
  }

  return (
    <div className="overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
        <h3>Connection</h3>
        <div className="sub">Where the Brass Guard API is listening. Never served over file://.</div>
        <div className="row">
          <label className="flabel">Backend URL</label>
          <input
            className="select"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && save()}
            placeholder={DEFAULT_BACKEND}
            spellCheck={false}
          />
        </div>
        {msg && (
          <div className="notice" style={{ marginTop: 14 }}>
            <span className="glyph">·</span>
            <div>{msg}</div>
          </div>
        )}
        <div className="foot">
          <button className="btn ghost" onClick={onClose}>
            Close
          </button>
          <button className="btn primary" onClick={save} disabled={testing}>
            {testing ? 'Testing…' : 'Save & connect'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <ToastProvider>
      <Shell />
    </ToastProvider>
  )
}
