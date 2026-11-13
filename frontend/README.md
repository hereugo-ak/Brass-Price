# Brass Guard — Frontend

Premium frontend for the Castle Hardwares brass price-floor product.
Vite + React 19 + TypeScript, no UI framework — a hand-rolled design system
("Foundry": warm dark ink, hairlines, brass accent, Fraunces display numerals).
All fonts self-hosted; the UI never recomputes verdicts or band maths — the
FastAPI backend in `../app/` is the single source of truth.

## Run it (development)

```bash
# 1. start the API (from the project root)
python -m app.cli serve          # http://127.0.0.1:8000
#    …or double-click ..\start_local.bat on Windows

# 2. start the frontend (here)
npm install                      # first time only
npm run dev                      # http://127.0.0.1:8080
```

The frontend talks to `http://127.0.0.1:8000` by default. Change it via the
connection pill in the top-right (stored in localStorage).

## Production build

```bash
npm run build                    # outputs dist/
npm run preview                  # serves dist/ on :8080
```

`dist/` is fully static — it can be served by `python -m http.server`, nginx,
or wired into the FastAPI app as static files later. A prebuilt `dist/` ships
with the repo, so the UI runs without installing anything.

## Screens

| Tab | What it does | Endpoints |
|---|---|---|
| **Floor** | band + floor, cover-period switch, machinist's-rule gauge, quote check → verdict stamp (logged), full model equation | `/week`, `/quote`, `/history` |
| **Weekly note** | backend-composed note, copy / write-to-file / email, note history | `/note`, `/note/send`, `/note/history` |
| **History** | floor coverage vs 80% target, exposure, floor-vs-realised chart, scored quote ledger | `/report` |
| **Data** | Sync All, per-feed status chips with honest failure messages, manual upload preview → commit | `/sync`, `/sync/last`, `/upload/*`, `/config` |

## Behaviour rules carried over from the project

- **No client-side verdict re-computation.** Offline shows the last synced week
  from cache, clearly marked, with checking/logging disabled.
- **Provenance surfaces:** metal source (mcx/lme/default), age, transport source,
  model version, warnings, PROVISIONAL state when the metal input is >7 days old.
- **Honesty in data:** feed statuses surface `OK / STALE / BLOCKED / FAILED /
  MANUAL` verbatim, including failure messages.
- `prefers-reduced-motion` respected; visibility never gated on opacity.

## Structure

```
src/
  api/        typed client + types mirroring app/api.py
  components/ Gauge (the rule), TrendChart, Toast
  screens/    FloorScreen · NoteScreen · HistoryScreen · DataScreen
  lib/        format (₹, en-IN), hooks, feed labels
  styles/     tokens.css (design tokens) · app.css (components)
```
