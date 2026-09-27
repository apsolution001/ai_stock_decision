# Trading Safety Rules (NON-NEGOTIABLE)

This system can place **real orders with real money**. These rules override every other instruction, convenience or deadline. Code that violates any rule must not be merged.

## 1. Mode and money

1. **`TRADING_MODE=paper` is the default.** Code must never switch to `live` by itself. `live` is only read from `.env`, set by the owner.
2. In `paper` mode, **no code path may call a broker order endpoint**. `LiveBroker` must refuse to construct unless `TRADING_MODE=live`.
3. Live mode also requires `LIVE_CONFIRM=I_UNDERSTAND_REAL_MONEY` in `.env`. Without it, the app refuses to start in live mode.
4. The **first 3 trading days are observe-only** (`OBSERVE_ONLY_DAYS=3`): signals are logged, and no paper or live orders are placed.

## 2. Hard risk limits (enforced by `RiskManager`, the single gate before any order)

| Rule | Value (config key) |
|---|---|
| Max new trades per day | 3 (`MAX_TRADES_PER_DAY`) |
| Daily profit stop (net) | +1.5% (`DAILY_PROFIT_STOP_PCT`), then no new entries |
| Daily loss stop (net, incl. open MTM) | −1% (`DAILY_LOSS_STOP_PCT`), then no new entries **and close all intraday positions** |
| Risk per trade | ₹100 (`RISK_PER_TRADE`) |
| Max open swing positions | 1 (`MAX_SWING_POSITIONS`) |
| Entry window | 09:30–14:30 IST |
| Intraday square-off | 15:15 IST |
| Max position value | ≤ available margin, and ≤ `MAX_POSITION_VALUE` |
| Order rate | ≤ 2 orders/second (own cap; broker limit is 10) |

- **Every order goes through `RiskManager.approve()`.** There is no bypass, no "force" flag, and no debug shortcut.
- The limits are **config values validated at startup** (e.g. loss stop must be negative, trades ≥ 1). An invalid config means the app refuses to start.
- **When state is unknown, stop trading.** Examples: positions don't match the broker, the feed is stale, the token is invalid. The system switches to `HALTED`, alerts the UI and places no new entries.

## 3. Every position has an exit

- A stop-loss is computed **before** the entry order is sent. No stop means no trade.
- Intraday stops are enforced by code on every tick. Swing positions get a broker-side **Smart Order (GTT)** stop and target immediately after the fill.
- **Exits never wait for Laya, news or any slow component.**
- **Kill switch:** one UI button (and one API endpoint) closes all intraday positions, cancels open orders and halts new entries.

## 4. Credentials

- Secrets (`INDSTOCKS_MPIN`, `INDSTOCKS_TOTP_SECRET`, tokens) live **only in `.env`**, which is git-ignored.
- Never log, print, commit or send secrets to the UI. Logs redact any `Authorization` header.
- Token generation: at most **one attempt**, then stop and alert on failure (the broker locks out after 5 wrong codes).

## 5. Correctness over guessing

- Any broker behaviour not in `docs/research/01-indstocks-api.md` is **unverified**. Verify it in the official docs and record it there before relying on it.
- Money is computed with `Decimal` (or integer paise), **never float**, for P&L, charges and quantities.
- Times are always **timezone-aware IST** (`Asia/Kolkata`). Market holidays come from an exchange calendar file, never guessed.

## 6. Change control

- Any change to `risk/`, `broker/` or order flow must get a review with the `risk-safety-auditor` agent before merge.
- A strategy goes live only after passing `docs/standards/backtest-standards.md` **and** 2+ weeks of paper trading.
