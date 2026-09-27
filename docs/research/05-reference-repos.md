# Reference Repositories & Libraries

- **Checked:** 2026-09-27.
- **Rule:** **study** these for design ideas and **use** only the libraries marked "use". Check licenses before copying any code. We do **not** copy AGPL code into this repo.

## Indian-market / broker related

| Repo | What it is | How we use it |
|---|---|---|
| [marketcalls/openalgo](https://github.com/marketcalls/openalgo) | Open-source self-hosted algo platform for Indian brokers (Flask + React), 30+ broker plugins, unified API. **AGPL-3.0** | **Study only**: broker-adapter abstraction, order-state handling, risk and UI ideas. Do not copy code (license). |
| [Arnavshah22/indstocks-mcp](https://github.com/Arnavshah22/indstocks-mcp) | Unofficial MCP server over the official INDstocks REST API (TypeScript, MIT). **Read-only; no order placement by design.** | **Study**: real INDstocks endpoint usage, auth and WebSocket handling notes. Small repo (few commits), so cross-check against the official docs. |
| [INDstocks API docs](https://api-docs.indstocks.com/) | Official API reference | **Source of truth.** See [01-indstocks-api.md](01-indstocks-api.md). |

## Backtesting

| Repo | Notes | Decision |
|---|---|---|
| [kernc/backtesting.py](https://github.com/kernc/backtesting.py) | Simple, fast, well documented. One instrument per run. | Study the API design. |
| [polakowo/vectorbt](https://github.com/polakowo/vectorbt) | Vectorized, very fast parameter sweeps | Study. It's heavy, and the advanced features are in a paid "PRO" version. |
| [mementum/backtrader](https://github.com/mementum/backtrader) | Event-driven classic, largely unmaintained | Study only. |
| [nautechsystems/nautilus_trader](https://github.com/nautechsystems/nautilus_trader) | Production-grade event-driven engine where backtest and live use the same code | Study the architecture idea: **the same strategy code runs in backtest, paper and live**. |
| [freqtrade/freqtrade](https://github.com/freqtrade/freqtrade) | Mature crypto bot: dry-run mode, risk protections, Web UI | Study the **dry-run (paper) mode, "protections" (stop after N losses), and UI**. The concepts transfer. |

**Decision: build our own small event-driven backtester.** Reasons:
- Our rules are few and specific: 3 trades/day, day-level stops, cost model, 5-min bars.
- **One strategy code path** has to run unchanged in backtest, paper and live. Adapting a framework to INDstocks and to our day-level risk rules would take more code than writing the loop.
- A small codebase is fully testable and auditable, which matters when real money is involved.

## Indicators

| Library | Status | Decision |
|---|---|---|
| [pandas-ta](https://pypi.org/project/pandas-ta/) | Maintainer announced it may be **archived after 1 July 2026** unless funded; licensing moved toward paid releases | **Do not depend on it** |
| [TA-Lib/ta-lib-python](https://github.com/TA-Lib/ta-lib-python) | Mature C library; needs a native build on Windows | Use **only as a test reference** (optional) |
| Own implementation (pandas/numpy) | We need only VWAP, EMA, RSI, ATR, volume ratio, opening range | **Use**: ~150 lines, unit-tested against known values |

## Runtime libraries (planned)

| Library | Purpose |
|---|---|
| `fastapi` + `uvicorn` | API and WebSocket push to the UI |
| `websockets` / `httpx` | INDstocks WebSocket and REST clients |
| `pyotp` ([pyauth/pyotp](https://github.com/pyauth/pyotp)) | TOTP code generation for daily auto-login |
| `pydantic-settings` | `.env` config |
| `sqlite3` / SQLAlchemy | Trade log, signals, daily P&L |
| `pandas`, `numpy` | Indicators and backtest |
| `yfinance` | Weekly fundamentals (unofficial; swappable) |
| `feedparser` | RSS news for the risk filter |
| `laya` | Veto and news risk |
| React + Vite + TypeScript | Live UI; lightweight-charts for charts |
