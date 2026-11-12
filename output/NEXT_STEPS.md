# What to do now — action list

**Date:** 2026-11-12
**Situation:** research is done, the data spine runs, 6 of 8 owner answers are in. The project is
now waiting on **numbers**, not on analysis. Nothing below requires you to code.

---

## TODAY (~30 minutes total)

### 1. Send the founder message — 5 min
Open `output/FOLLOWUP_TO_FOUNDER.md`. Copy between the two `---` lines. Send on WhatsApp or email.
Change nothing except his name and your sign-off. It asks for four things; if he only does one,
push the weekly price note.

**Why first:** every remaining blocker on this project is behind that message. Nothing I build
moves the needle until one of those four answers comes back.

### 2. Try one MCX bhavcopy — 10 min
1. Open `mcxindia.com` in your own browser (not automated — it 403s everything else).
2. Market Data → Bhavcopy → pick the latest date.
3. Save the **table itself**, not the page. Easiest reliable way: select the table, paste into
   Excel, save as `data/mcx_manual/mcx_YYYY-MM-DD.csv` with a header row.
4. Run:
   ```bash
   cd "C:\Users\Abuza\OneDrive\Documents\Brass\data"
   python check_mcx.py
   ```
5. Green `OK` = done. `FAIL` = the file is a shell, try the paste-into-Excel route instead.

**Why:** MCX is the domestic anchor the founder named. We currently have zero usable MCX rows.

### 3. First mandi quote — 5 min
Message your purchase contact: *"what is brass scrap going for per kilo today?"*
Then add one line to `data/manual/mandi_quotes.csv`:

```
date,item,spec,price_inr_kg,source
2026-11-12,brass scrap,bartan,<price>,<supplier name>
```

**Why:** this is the single highest-value habit in the project. One quote a week for 8–12 weeks
is literally what becomes `data/brass_target.csv`. Without it there is no brass model — only a
copper-and-FX model wearing a brass label.

---

## THIS WEEK

### 4. Start the daily 10-minute routine
`data/MANUAL_GUIDE.md`, the DAILY table: RBI reference rates + LME copper/zinc cash/3M.
Ten minutes, once a day. Seven days in a row is the acceptance test.

### 5. Decide on automation — 5 min, once
Cron does not work in this WSL without admin. Pick one:
- **Windows Task Scheduler** running `python3 collect_daily.py` at 08:00 daily (recommended), or
- run `collect_daily.py` manually each morning (10 seconds), or
- `sudo service cron start` once.

Until one is done, assume no automation and expect data gaps.

### 6. Optional, 2 min: put it in git
There is no repo. One bad edit to an 84 KB HTML file is unrecoverable.
```bash
cd "C:\Users\Abuza\OneDrive\Documents\Brass"
git init && git add . && git commit -m "baseline before owner data"
```
`.gitignore` already excludes `.env`. Never commit that key.

---

## I DO THESE (owner-independent, no input needed)

7. Backfill the ECB + CFTC month gap (Oct 11 → Nov 11) from the official history endpoints.
8. Add HCL MIC y/y, IBM ASP and the HS 74032100 duty stack as features, with catalogue rows and
   leak rules.
9. Rerun the tournament on the expanded feature set; report whether naive is still unbeaten.
10. Wire a weekly-updated "what changed" note so you can see the data is alive.

---

## WHEN THE FOUNDER REPLIES

11. Paste his reply to me verbatim. I record it in `data/owner_answers.md` with the date — no
    paraphrasing into certainty.
12. I convert the costed purchase into **spread parameters**: premium over benchmark, transport
    ₹/kg, conversion, scrap discount. Each one sourced to his message and date.
13. Quote-validity days become the **horizon** for the quote floor.
14. Weekly price notes accumulate → after 8–12 rows, `data/brass_target.csv` exists → the real
    tournament runs.

---

## WHAT NOT TO DO

- Do not send the demo signal (`data/decisions_demo.json`) to the founder. It is plumbing.
- Do not build a brass target from assumed spreads. That is the one shortcut that ruins the work.
- Do not buy LME/Fastmarkets/LightGBM seats yet. Free + manual must fail first.
- Do not ask the founder for bills or documents. Ballpark only.
- Do not re-research the 72 nodes. That phase closed.
- Do not quote the illustrative story numbers as market prices.

---

## The one-line version

Send the message, grab one MCX file, start one weekly price note. Everything else is mine.
