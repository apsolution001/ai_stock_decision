# Coding Standards

## Stack

- **Backend:** Python 3.11+, `uv` for deps, FastAPI (async), pydantic v2 + pydantic-settings, SQLite (via SQLAlchemy 2), `httpx`, `websockets`, `pyotp`, pandas/numpy.
- **Frontend:** React + Vite + TypeScript, lightweight-charts, a native WebSocket client.
- **Tooling:** `ruff` (lint + format), `mypy --strict` on `backend/app`, `pytest`, Vitest, pre-commit.

## Layout (planned)

```
backend/app/
  core/        config, logging, clock (IST), market calendar
  broker/      Broker protocol, IndstocksClient (REST+WS+auth), PaperBroker, LiveBroker
  data/        historical downloader, candle builder (ticks → 1m/5m), instruments
  indicators/  vwap, ema, rsi, atr, opening range, volume ratio (pure functions)
  strategies/  Strategy protocol + one module per strategy (pure, no I/O)
  risk/        RiskManager, charges model, position sizing
  engine/      live loop: feed → candles → strategies → risk → broker
  filters/     fundamentals, news (Laya), universe/categories
  laya/        LayaVeto adapter + FakeLaya for tests
  backtest/    event-driven backtester reusing strategies/ + risk/ + charges
  api/         REST + /ws push to UI
  db/          models, repositories
backend/tests/
web/           React UI
```

## Rules

1. **Same strategy code runs in backtest, paper and live.** Strategies are pure: `on_candle(state) -> Signal | None`. No I/O, no clock reads, no broker calls inside strategies.
2. **Pure core, thin I/O shell.** Indicators, strategies, risk and charges are pure functions or classes, testable without a network.
3. **One responsibility per file**, and a file should stay under ~300 lines. If it grows, split it.
4. **Types everywhere.** Public functions are fully typed. Use pydantic models at the boundaries (API, broker payloads, config).
5. **Money is `Decimal`**, prices come from the broker as strings/decimals, quantities are `int`. Floats only inside indicator maths.
6. **Time is IST, tz-aware.** Use `core.clock.now()` (injectable for tests). Never call `datetime.now()` directly.
7. **No silent failures.** Catch only specific exceptions. Log with context (symbol, order id, mode). Unknown state → `HALTED`.
8. **Async discipline:** never block the event loop. CPU-heavy work (Laya, backtests) runs in threads/processes, with timeouts.
9. **Config over constants.** Every threshold is in `core/config.py` with the default from the decisions log.
10. **Comments explain *why*, not *what*.** Every strategy rule cites `docs/research/03-strategies.md`.
11. **Match the surrounding code.** Follow existing naming, patterns and idioms.
