import { createContext, useCallback, useContext, useRef, useState } from 'react'
import type { ReactNode } from 'react'

interface Toast {
  id: number
  kind: 'ok' | 'err' | 'info'
  text: string
}

const ToastCtx = createContext<(kind: Toast['kind'], text: string) => void>(() => {})

export function useToast() {
  return useContext(ToastCtx)
}

let seq = 0

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])
  const timers = useRef<ReturnType<typeof setTimeout>[]>([])

  const push = useCallback((kind: Toast['kind'], text: string) => {
    const id = ++seq
    setToasts((t) => [...t.slice(-3), { id, kind, text }])
    const timer = setTimeout(() => {
      setToasts((t) => t.filter((x) => x.id !== id))
    }, 4200)
    timers.current.push(timer)
  }, [])

  return (
    <ToastCtx.Provider value={push}>
      {children}
      <div className="toasts" role="status" aria-live="polite">
        {toasts.map((t) => (
          <div key={t.id} className={`toast ${t.kind === 'info' ? '' : t.kind}`}>
            {t.text}
          </div>
        ))}
      </div>
    </ToastCtx.Provider>
  )
}
