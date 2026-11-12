# PROPRIETARY intel brief + best-possible plan — Brass Price Foresight
Date: 2026-10-11. Method: 15+ min targeted digging, primary sources only, every URL opened.

## A. Fresh proprietary-grade intel (all retrieved today)

1. **HCL mine output is surging (domestic supply signal).** HCL Production Report: Q1 FY27 MIC 6,075 MT (+16.65% y/y); Q4 FY26 MIC 8,413 MT (+34.01%); Q3 FY26 MIC 6,962 MT (+9.81%). Sales Volume page: Q1 FY27 MIC sales 6,619 MT (+21.47%); Q3 FY26 6,021 MT (+55.10%). CC-rod output thin (2,602 MT Q1 FY27). tradable form: HCL MIC y/y% as an India-supply feature. Source: hindustancopper.com ProductionReport/SalesVolume (primary-company, 2026-10-11).
2. **HCL runs monthly price circulars + spot booking.** Price Circular archive (cathode/CC-rod base prices, 2017–2020 visible) + Spot Booking login + Marketing Policy pages. Mechanism confirmed: domestic base-price circulars exist — next step is pulling the current circular monthly. Source: hindustancopper.com (primary-company).
3. **Exact brass duty stack nailed: HS 74032100 = BCD 5 + SWS 10 + IGST 18, policy Free.** Full duty history back to 2006 + live customs-notification feed on the same page. This hard-codes the P1 landed-cost math — no estimates. Source: eximguru.com HS 74032100 (trade-primary mirror of CBIC; cross-check CBIC notifications).
4. **IBM publishes Average Sale Prices + Yearbook + mineral statistics.** IBM portal (ibm.gov.in) has an Average Sale Price series, Mining & Mineral Statistics division, Indian Minerals Yearbook, and a new Mineral Exchange registration notice. ASP = official domestic price anchor to pull monthly. Source: ibm.gov.in (primary-official).
5. **Bot-walled (manual-or-paid, confirmed by direct probe):** Moneycontrol 403, Zauba 403, BigMint unreachable, MCX bhavcopy 403, LME detail 403. These stay manual-browser or paid — recorded, not guessed.

## B. What this changes in the model
- New features (free): HCL MIC y/y% (quarterly, from HCL reports), duty stack constants (5/10/18 for 74032100), IBM ASP (monthly, to wire), EximGuru notification feed (event dummies for BCD/tariff-value changes).
- Node upgrades: S1/S2_IN cite HCL reports directly; P1 cites the exact stack; data catalogue gains 4 rows.

## C. Best-possible plan (owner-independent work first)
- **Phase 0 (done):** collector + backfill + features + naive bar (MAE h1 ₹0.21 / h4 ₹0.46) + leak map + manual kit.
- **Phase 1 (now, no owner needed):** model tournament scaffold on public legs (train.py — Ridge alphas + ablations + Diebold-Mariano vs naive, walk-forward). Proves the harness on USD-INR before brass labels exist.
- **Phase 2 (monthly manual pulls):** HCL MIC%, IBM ASP, EximGuru notifications, LME delayed closes, mandi quotes. Each pull hardens one spread.
- **Phase 3 (owner answers land):** brass target series → same harness, real target → quote-floor + budget-band rules live.
- **Phase 4 (only if justified):** LME history purchase, one Fastmarkets seat. Kill rule: if a paid feed doesn't beat free+manual in backtest within a month, cancel it.

## D. Integrity rules (unchanged)
No invented numbers, quarantine stays visible, every new claim needs a retrievable source, naive bar must fall before anything ships.
