# Run Brass Guard on your machine

Two pieces run side by side:

| Piece | What it is | Address |
|---|---|---|
| **Backend** | Python API + database | `http://127.0.0.1:8000` |
| **Frontend** | One HTML page | `http://127.0.0.1:8080/Castle_Quote_Checker.html` |

The page must be opened at that `http://` address. **Do not double-click the HTML file** — a
`file://` page is not allowed to call the API, and the screen will fall back to its offline copy.

---

## Windows — the easy way

1. Open the `Brass` folder.
2. Double-click **`start_local.bat`**.

Two black windows open (backend and page), then your browser opens on the page.

Keep the two black windows open while you use it. To stop, close them, or double-click
**`stop_local.bat`**.

---

## Windows — manual way

Open **two** terminals in the `Brass` folder (Shift + right-click → *Open PowerShell here*).

**Terminal 1 — backend**

```bat
python -m uvicorn app.api:app --host 127.0.0.1 --port 8000
```

**Terminal 2 — page**

```bat
python -m http.server 8080 --bind 127.0.0.1
```

Then open: <http://127.0.0.1:8080/Castle_Quote_Checker.html>

---

## WSL / Linux / macOS

```bash
cd ~/Brass            # or wherever the folder is
./start_local.sh      # Ctrl-C to stop both
```

Manual equivalent:

```bash
python3 -m uvicorn app.api:app --host 127.0.0.1 --port 8000 &
python3 -m http.server 8080 --bind 127.0.0.1 &
# then open http://127.0.0.1:8080/Castle_Quote_Checker.html
```

---

## First-time setup

Only needed once, and only if `brass.db` is missing:

```bash
python -m app.cli init          # create the database and the feed registry
python -m app.cli sync          # fetch everything that can be fetched
```

Load the manual feeds (MCX, WPI, board prices) from the **Data** tab, or:

```bash
python -m app.cli upload mcx.copper data/manual/mcx_copper.csv --commit
```

---

## What you should see

**On the page** — a small badge in the top right:

| Badge | Meaning |
|---|---|
| **LIVE** | talking to the backend. Numbers are real. |
| **OFFLINE** | backend not running. The page still shows its last built-in numbers and says so. |

Click the badge to change the backend address (e.g. if the API is on another port).

**Backend checks** — open these in a browser:

- <http://127.0.0.1:8000/health> — should return `{"status":"ok", ...}`
- <http://127.0.0.1:8000/docs> — the interactive API documentation

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Badge says **OFFLINE** | backend not running, or on a different port | start it, or click the badge and set the URL |
| Page is blank | opened via `file://` | open `http://127.0.0.1:8080/...` instead |
| `No module named fastapi` | dependencies missing | `python -m pip install --user fastapi "uvicorn[standard]" python-multipart httpx openpyxl xlrd` |
| `python` not recognised | not on PATH | install Python 3.11+ from python.org and tick *Add Python to PATH*, or use `py` |
| Port already in use | an old run is still alive | run `stop_local.bat`, or start on another port: `--port 8011` |
| Sync shows `BLOCKED` | publisher refuses automated requests (MCX) | expected — upload that feed from the Data tab |
| Floors look `PROVISIONAL` | metal input older than 7 days | upload a recent MCX bhavcopy |

---

## Ports used

```
8000   backend API
8080   the page
```

If either is taken, change it in the command **and** set the backend URL by clicking the LIVE/OFFLINE
badge on the page.

---

## Tests

```bash
python -m pytest tests -q        # 47 tests
```

---

## Notes

- The backend binds to `127.0.0.1` only — it is not reachable from other machines on the network.
  That is deliberate for the pilot: there is no authentication yet.
- The database is `brass.db` in the project folder. Delete it and re-run `init` to start clean.
- Generated weekly notes go to `data/outbox/`.
