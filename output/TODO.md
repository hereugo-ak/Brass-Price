# TODO — Brass Price Foresight / Brass Guard

**Updated:** 2026-11-12 · **Submission:** 2026-11-15 · **Status:** AWAITING SCOPE SIGN-OFF
**Governing rule:** nothing ships unless it beats naive **and** survives the rupee-saved backtest.
The forecaster did not, and has been withdrawn.

---

## Where we stand

| Area | State |
|---|---|
| Driver research | ✅ 72 nodes, 9 edges, 65 claims, 44 catalogue rows, 19 quarantined |
| Public data spine | ✅ 7 FRED series, 2,789 weekly rows, 1973→2026 |
| MCX copper + zinc daily | ✅ 955 rows, 2025-01-01 → 2026-11-11 |
| Board price tier | ✅ 27 dated observations, 11 sources |
| Brass/metal ratio | ✅ measured 0.876 ± 0.039 (0.977 / 0.910 / 0.876 across 2019/2023/2026) |
| Price calculator | ✅ two routes agree to 0.42% |
| Engine frozen | ✅ `data/engine.py`, `MODEL_VERSION 2026-11-12.1`, matches product to ₹0.01 |
| Rupee-saved backtest | ✅ run — **buy signal rejected** (−₹0.11/kg) |
| **Model training** | ⛔ **DONE AND NEGATIVE** — 8 models, 17 drivers, 155 months, all lose (DM −5.6 to −10.2) |
| Product UI | ✅ v3, editorial system, 19/19 headless tests |
| Quote log | ✅ **live** — every check stored with `model_version`, floor at time, verdict |
| Backend / API | ✅ **BUILT & TESTED** — FastAPI + SQLite, 28/28 pytest, verified on a live server |
| Sync All | ✅ built — per-feed `OK / STALE / BLOCKED / MANUAL / FAILED`, never crashes |
| Manual upload | ✅ built — preview → validate → commit, with tested guards |
| Guide (owner-facing) | ⛔ not built (P2) |
| Delivery (weekly note) | ⛔ not built (P3) |
| Push to GitHub | ⛔ blocked on your login |

---

## P0 — Unblock (yours, 5 min)

- [ ] `git push -u origin main` — 18 commits are local only
- [ ] Confirm PRD scope: `output/PRD_v2.md` §4.2 non-goals and §5 priorities

---

## P1 — Backend foundation ✅ DONE 2026-11-12

- [x] Database: SQLite `brass.db` — `series`, `observation`, `model_input`, `quote`, `note`, `feed_run`, `feed_run_item`, `upload`
- [x] Engine at `app/engine.py`, `MODEL_VERSION 2026-11-12.1`, matches UI to ₹0.01
- [x] **Sync All** `app/sync.py` — FRED ×5, ECB, CFTC live; 4 OK / 3 STALE / 6 MANUAL on first run
- [x] **Manual upload** `app/upload.py` — 5 feeds, frameset trap rejected, idempotent, per-row reasons
- [x] Quote log writer — rows written before the response is returned
- [x] FastAPI: `/health`, `/week`, `/quote`, `/history`, `/sync`, `/sync/last`, `/upload/*`, `/config`
- [x] Run log (`feed_run` + `feed_run_item`) — every run and every feed outcome retained

**Acceptance:** one command brings every feed current, refuses bad uploads with a reason, and every
displayed number is reproducible from stored rows + `model_version`.

---

## P2 — Guide and onboarding

- [ ] 3-screen first-run guide: what the floor is, how to check, when the note arrives
- [ ] Per-feed "how to get this" panels, including the honest MCX instruction
- [ ] Error states that name the fix (not "contact support")
- [ ] Written for a factory owner: short sentences, no jargon

**Acceptance:** a non-technical user completes a manual MCX upload without help.

---

## P3 — Weekly note delivery

- [ ] Note generator writing a dated file (already prototyped in the UI)
- [ ] Record of notes sent
- [ ] Email delivery (free) → WhatsApp Business later (~₹1/conversation)

**Acceptance:** the note can be delivered without a human copying text.

---

## P4 — History and the rupee-saved report

- [ ] Floor vs actual over time
- [ ] Quotes vs corrections, adherence rate
- [ ] Rupee-saved figure the owner accepts as real

**Acceptance:** a single number the owner believes, derived only from the quote log.

---

## P5 — Model work: only what the evidence supports

- [ ] **Quarterly re-test** of the 8-model tournament as a scheduled job (not a build task)
- [ ] Ratio recalibration workflow from the owner's weekly price (F11)
- [ ] Transport rate verification once one bill exists
- [ ] ~~Forecasting~~ — **closed.** 8 models lost. Re-open only with new data (e.g. a weekly brass series)

**Do not** add features to the forecaster. The ablation shows more features make it worse.

---

## P6 — Data still not collected (18 catalogue entries)

| Priority | Feed | Why it matters | Mode |
|---|---|---|---|
| 1 | **Transport rate** | only unverified number in the floor | ask owner |
| 2 | **Weekly brass rate** | turns the ratio into a tracked series | owner, 30 s/week |
| 3 | **Owner invoice** | ratio ±₹38 → ±₹17 | owner, once |
| 4 | MCX bhavcopy (clean) | domestic anchor | manual upload |
| 5 | WPI brass monthly | real domestic target | manual upload |
| 6 | LME official/stocks | better metal granularity | paid (~$85) or manual |
| 7 | PMI · freight · OPEC · ABS/RBA · CPI · policy rates · SHFE · USGS · HCL · IBM ASP · CBAM · TC/RC | driver coverage | mixed; **none improve prediction** |

**Note:** item 7 is a coverage exercise, not a value exercise — the ablation already showed extra
drivers reduce accuracy. It is listed for completeness, not as a priority.

---

## P7 — Submission packing

- [ ] Regenerate `PROJECT_BRIEF.docx`, `PRD_v2.docx`, `ARCHITECTURE_PLAN.docx`
- [ ] Fold model results into the brief (§2.8, §5)
- [ ] Decide on *"Six weeks out of ten"* in `Brass_Story.html` — unsupported accuracy claim
- [ ] Update `brass_session_handoff.md` correction log
- [ ] Final count verification + print/PDF export

---

## Blocked or waiting

| Item | Blocked on |
|---|---|
| GitHub push | your credentials |
| Transport rate | owner |
| Weekly brass rate | owner / purchase man |
| Ratio calibration | one invoice |
| Multi-market floors | owner confirming validity differs by market |
| WhatsApp delivery | Business API account + pilot evidence |

---

## The one-line priority order

**Sign off the PRD → build the backend foundation (P1) → guide + upload (P2) → delivery (P3) →
history (P4).** No model work, no forecasting, no UI polish until P1–P3 exist.
