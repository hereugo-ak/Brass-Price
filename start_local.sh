#!/usr/bin/env bash
# =============================================================================
#  Brass Guard — start backend and frontend on localhost (WSL / Linux / macOS)
#  Usage:  ./start_local.sh          stop with Ctrl-C
# =============================================================================
set -euo pipefail
cd "$(dirname "$0")"

PY=python3
command -v "$PY" >/dev/null 2>&1 || PY=python

if [ ! -f brass.db ]; then
  echo "First run: creating the database..."
  "$PY" -m app.cli init
fi

echo "Starting backend on http://127.0.0.1:8000"
"$PY" -m uvicorn app.api:app --host 127.0.0.1 --port 8000 --log-level warning &
API_PID=$!

echo "Starting page on http://127.0.0.1:8080"
"$PY" -m http.server 8080 --bind 127.0.0.1 >/dev/null 2>&1 &
WEB_PID=$!

cleanup() {
  echo ""
  echo "Stopping..."
  kill "$API_PID" "$WEB_PID" 2>/dev/null || true
  wait 2>/dev/null || true
  exit 0
}
trap cleanup INT TERM

sleep 3
echo ""
echo "  Backend  : http://127.0.0.1:8000        (API docs at /docs)"
echo "  Frontend : http://127.0.0.1:8080/Castle_Quote_Checker.html"
echo ""
echo "  Open the frontend link in your browser. Ctrl-C here to stop both."
wait
