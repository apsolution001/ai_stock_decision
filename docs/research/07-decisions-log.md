# Decisions Log

These decisions were agreed with the owner during brainstorming (2026-09-27). **Each one is binding until changed here, with a date.**

| # | Decision | Value |
|---|---|---|
| D1 | Instruments | **Equity stocks only** (NSE/BSE). No F&O. |
| D2 | Broker | **INDmoney INDstocks API** (free API, ₹10/order) |
| D3 | Auth | Daily auto token via **TOTP** (`pyotp`) + MPIN + Client ID, stored in `.env` |
| D4 | Capital (paper and first live) | **₹25,000** |
| D5 | Max trades | **3 new trades per day** |
| D6 | Daily profit stop | Stop new trades at **≥ +1.5%** net (target band 1–2%) |
| D7 | Daily loss stop | **−1% (₹250)**. Stop new trades and close intraday positions. |
| D8 | Risk per trade | **₹100** (0.4%); ₹125 is to be evaluated in the backtest |
| D9 | Holding | **Intraday + swing, chosen per trade by rules at entry**. Default intraday (exit 15:15). Swing needs daily trend up + good fundamentals + clean news + no Laya veto; max 1 open swing; max hold 3–5 days; broker GTT stop/target. |
| D10 | Direction | **Long only** for the MVP; shorting in Step 2 |
| D11 | Universe | Categories: **NIFTY 50, NIFTY 100, NIFTY 200, My Watchlist**, then pre-market filter, then daily shortlist. MVP: NIFTY 50 + Watchlist. Sector categories in Step 3. |
| D12 | Laya role | **Veto only** (and news risk filter). Never originates trades. Kept only if it measurably improves paper P&L. |
| D13 | Architecture | **Option A**: single async FastAPI process + SQLite + React/Vite UI via WebSocket push. No Celery, Redis or Docker for the MVP. |
| D14 | Real-time UI | Live updates without page reload (WebSocket) |
| D15 | Rollout | Step 1 backtest and choose strategy → Step 2 live engine + paper + UI (**first 3 days observe-only**) → Step 3 2–4 weeks paper → Step 4 live (static IP) |
| D16 | Strategy choice | Backtest 3 candidates (ORB+VWAP, VWAP pullback, PDH breakout) on unseen data; only pass-bar strategies trade |
| D17 | Mode switch | `TRADING_MODE=paper` by default; `live` requires an explicit change |

## Supersedes

The original design (`docs/superpowers/specs/2026-09-26-ai-stock-decision-design.md`) was a signal-only tool with no broker. Its §9 "Out of scope: order execution" **no longer applies**. Its Laya facts (§2) are still valid.

## Still open

- Design sections 2+ (components, data flow, error handling, testing, UI) are **pending owner approval**. The final spec will be written after that.
- ₹100 vs ₹125 risk per trade (to be decided by the backtest)
- Broker confirmations listed in [01](01-indstocks-api.md) and [02](02-regulation.md)
