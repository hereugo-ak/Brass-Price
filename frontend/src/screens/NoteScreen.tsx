// The weekly note: the same numbers as the screen, in prose the owner can
// forward. Built by the backend; this screen never edits the text.

import type { NoteResponse, NoteSendResponse } from '../api/types'
import { api } from '../api/client'
import { fmt } from '../lib/format'
import { useFeedLabels } from '../lib/labels'
import { useAsync, useCopy } from '../lib/hooks'
import { useToast } from '../components/Toast'
import { useState } from 'react'

export function NoteScreen({ offline }: { offline: boolean }) {
  const note = useAsync(() => api.note(), [offline])
  const history = useAsync(() => api.noteHistory(), [])
  const labels = useFeedLabels()
  const toast = useToast()
  const [copied, copy] = useCopy()
  const [sending, setSending] = useState(false)

  async function writeFile() {
    setSending(true)
    try {
      const res: NoteSendResponse = await api.noteSend('file')
      if (res.ok) toast('ok', res.message)
      else toast('err', res.message)
      history.reload()
    } catch (e) {
      toast('err', (e as Error).message)
    } finally {
      setSending(false)
    }
  }

  async function tryEmail() {
    setSending(true)
    try {
      const res = await api.noteSend('email')
      // the backend is honest: if SMTP is not configured it says so
      if (res.ok) toast('ok', res.message)
      else toast('err', res.message)
      history.reload()
    } catch (e) {
      toast('err', (e as Error).message)
    } finally {
      setSending(false)
    }
  }

  const data: NoteResponse | null = note.data

  return (
    <div className="screen-in">
      <div className="sec-head">
        <span className="sec-kicker">Weekly note</span>
        <h2>Built from the same numbers as the screen</h2>
        <span className="aux">
          {data ? `week of ${data.week_start}` : ''}
        </span>
      </div>

      {note.error && (
        <div className="notice err">
          <span className="glyph">✕</span>
          <div>{note.error}</div>
        </div>
      )}

      {note.loading && <div className="memo skel" style={{ minHeight: 260 }}>loading</div>}

      {data && (
        <>
          {data.provisional && (
            <div className="notice">
              <span className="glyph">NOTE</span>
              <div>The metal input is stale — the note is marked <b>provisional</b> in its own text.</div>
            </div>
          )}
          {data.missing_feeds.length > 0 && (
            <div className="notice">
              <span className="glyph">NOTE</span>
              <div>
                Missing manual feeds: <b>{data.missing_feeds.map((k) => labels.get(k) ?? k).join(', ')}</b>. Upload them in
                Data for a tighter floor.
              </div>
            </div>
          )}

          <div className="memo" style={{ marginTop: 20 }}>
            <strong>{data.body.split('\n')[0]}</strong>
            {'\n' + data.body.split('\n').slice(1).join('\n')}
          </div>

          <div className="note-actions">
            <button className="btn" onClick={() => copy(data.body)}>
              {copied ? 'Copied ✓' : 'Copy text'}
            </button>
            <button className="btn ghost" onClick={writeFile} disabled={sending || offline}>
              Write to file
            </button>
            <button className="btn ghost" onClick={tryEmail} disabled={sending || offline}>
              Send by email
            </button>
          </div>

          <div className="floorsline">
            <div>
              <div className="k">Same day</div>
              <div className="v">{fmt(data.floors.same_day)}</div>
            </div>
            <div>
              <div className="k">15 days</div>
              <div className="v">{fmt(data.floors.d15)}</div>
            </div>
            <div>
              <div className="k">30 days</div>
              <div className="v">{fmt(data.floors.d30)}</div>
            </div>
          </div>
        </>
      )}

      <div className="sec-head" style={{ marginTop: 40 }}>
        <span className="sec-kicker">History</span>
        <h2>Notes kept on record</h2>
      </div>

      {history.data && history.data.notes.length > 0 ? (
        <table className="dtable">
          <thead>
            <tr>
              <th>Week of</th>
              <th>Channel</th>
              <th>Sent</th>
              <th className="r">Length</th>
            </tr>
          </thead>
          <tbody>
            {history.data.notes.map((n) => (
              <tr key={n.id}>
                <td className="num">{n.week_start}</td>
                <td className="dim">{n.channel}</td>
                <td className="dim">{n.sent_at ? n.sent_at.slice(0, 16).replace('T', ' ') : 'not sent'}</td>
                <td className="num r">{n.chars} chars</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <div className="empty">
          <b>No notes yet.</b>
          "Write to file" saves this week's note into data/outbox and records it here.
        </div>
      )}
    </div>
  )
}
