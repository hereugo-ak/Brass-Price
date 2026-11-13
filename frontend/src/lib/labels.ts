// Feed keys are internal; the UI speaks in labels ("Castle brass rate",
// not "owner.brass_rate"). One cached lookup, shared by every screen.

import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { ConfigResponse } from '../api/types'

let cache: ConfigResponse | null = null
let pending: Promise<ConfigResponse> | null = null

function load(): Promise<ConfigResponse> {
  if (cache) return Promise.resolve(cache)
  if (!pending) {
    pending = api
      .config()
      .then((c) => {
        cache = c
        return c
      })
      .catch(() => {
        pending = null
        throw new Error('config unavailable')
      })
  }
  return pending
}

export function useFeedLabels(): Map<string, string> {
  const [map, setMap] = useState<Map<string, string>>(new Map())
  useEffect(() => {
    let alive = true
    load()
      .then((c) => {
        if (alive) setMap(new Map(c.feeds.map((f) => [f.key, f.label])))
      })
      .catch(() => {})
    return () => {
      alive = false
    }
  }, [])
  return map
}
