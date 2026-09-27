# INDstocks API — Verified Facts

- **Verified on:** 2026-09-27 against the official docs at <https://api-docs.indstocks.com/>
- **Rule:** anything not in this file is **unverified**. Check the docs before coding against it and add it here with its source.

## Basics

| Item | Value | Source |
|---|---|---|
| Base URL | `https://api.indstocks.com` | [Conventions](https://api-docs.indstocks.com/conventions/) |
| Format | JSON; timestamps are Unix epoch **milliseconds** (IST) | Conventions |
| Auth header | `Authorization: <token>` (no `Bearer`) | Conventions |
| Cost | API free; brokerage **₹10 flat per order** | [FAQ](https://api-docs.indstocks.com/faq/) |
| Sandbox | **None.** Test in live with small qty, so we build our own paper broker | FAQ |
| Error body | `{"status":"error","message":"...","error_code":"INVALID_INPUT"}` | Conventions |

## Authentication (TOTP, unattended)

Source: [Access Tokens & Profile](https://api-docs.indstocks.com/Users/)

1. One-time setup: indstocks.com, then **Access tokens**, then **Setup TOTP**. Scan the QR and confirm one code within 5 minutes.
2. The TOTP **secret is shown exactly once** and can never be retrieved. Save it into `.env` as `INDSTOCKS_TOTP_SECRET`.
3. The dashboard shows the **Client ID**. It is the static `x-api-key`.

```
POST /generate/token
Headers: x-api-key: <CLIENT_ID>, Content-Type: application/json
Body:    {"mpin": "<MPIN>", "totp": "<6-digit code from pyotp>"}
Response: {"token": "..."}        # field is `token`, not `access_token`
```

| Rule | Consequence for our code |
|---|---|
| Token valid **24 h** | Generate a new token every morning at 08:30 IST |
| **Only one token active**; a new one invalidates the old | The bot owns token generation; never generate one manually while the bot runs |
| **1 token / 60 s** | Never retry faster than 60 s |
| **5 wrong TOTP → 15 min lockout**; 3 lockouts/hour → 1 h lockout + email | Stop after **1** failure and alert; no retry loops |
| No static IP needed for this endpoint | Token generation works from a home PC |

## Rate limits

Source: Conventions

| Category | Per second | Per day |
|---|---|---|
| Order APIs | 10 | — |
| Data APIs | 5 | 100,000 |
| Quote APIs | 5 | 100,000 |
| Non-trading APIs | 15 | 100,000 |
| Token generation | 1 / minute | — |
| WebSocket | max **3 connections** per user, **3,000 instruments** per connection | |

Exceeding a limit returns `429`. The client must have a per-category token-bucket limiter.

## Orders

Source: [API Overview](https://api-docs.indstocks.com/api-overview/)

- `POST /order`, `POST /order/modify`, `POST /order/cancel`, `GET /order-book`, `GET /trades/{order_id}`, `GET /trade-book`
- Product: `CNC` (delivery), `INTRADAY`, `MARGIN`
- Order types: **`LIMIT`, `MARKET` only.** A plain stop-loss order type is not listed.
- Stop-loss and target come from **Smart Orders (GTT)**: `POST /smart/order`, `/smart/order/modify`, `/smart/order/cancel`. These support automated SL/target and OCO (one-cancels-other).
- Validity: `DAY`. Exchanges: `NSE`, `BSE`.
- **Static IP whitelisting is required for order placement** (NSE circular NSE/INVG/67858, 5 May 2025). There are 2 slots (primary and secondary) and they can change **once per calendar week**.
- ⚠️ No endpoint was found for converting a position between INTRADAY and CNC. **Intraday vs swing is decided at entry.**

## Market data

- REST: `GET /market/quotes/full`, `/market/quotes/ltp`, `/market/quotes/mkt` (depth), `GET /market/instruments` (CSV master)
- Historical: `GET /market/historical/{interval}?scrip-codes=...&start_time=<ms>&end_time=<ms>` ([docs](https://api-docs.indstocks.com/historicalData/))

| Interval values | Max range per request |
|---|---|
| `1minute` … `5minute`, `10minute`, `15minute`, `30minute` | **7 days** |
| `60minute` … `240minute` | 15 days |
| `1day`, `1week`, `1month` | 1 year |

- Max **5 scrip codes per request**. There are no continuation tokens, so the downloader loops over date windows.
- Candle: `ts` (open time, **epoch seconds**), `o`, `h`, `l`, `c`, `v`. The request uses ms and the response uses s. Watch for this.
- Intraday candles align to the **09:15 IST** session open.
- Response uses a `"success"` boolean, and instruments with no data are simply missing from the response.
- The FAQ claims "10+ years" of history. ⚠️ **Unverified for 1-minute data.** Probe the earliest available date per interval before relying on it.

**Download budget:** NIFTY 50 × 1-minute × ~7 years ≈ 365 windows × 10 batches ≈ 3,650 requests. At 5 req/s that is about 15 minutes, well under the 100k/day cap.

## WebSockets

Source: [WebSockets](https://api-docs.indstocks.com/Websockets/)

| Stream | URL |
|---|---|
| Prices | `wss://ws-prices.indstocks.com/api/v1/ws/prices` |
| Order updates | `wss://ws-order-updates.indstocks.com/api/v1/ws/trades` |

- Auth: `Authorization: <token>` header on the handshake.
- Subscribe prices: `{"action":"subscribe","mode":"ltp"|"quote","instruments":["NSE:2885"]}`
- Subscribe orders: `{"action":"subscribe","mode":"order_update"}`
- Instrument format `SEGMENT:TOKEN`: `NSE:2885`, `BSE:500325`, `NIDX:26000` (index), `NFO:…`, `BFO:…`
- Order status codes: `R, P, S, F, C, RJ, PF, PFC`. ⚠️ Exact meanings are not yet documented here; verify before mapping them.
- Order updates **omit fields that are at their default value**, so check a field is present before reading it.
- Order events by envelope `timestamp` (epoch ms, UTC).
- Heartbeats: the FAQ says to ping every 30 s, and the WS page says the server sends heartbeats. Implement both a client ping and a staleness watchdog.

## Open questions (verify before live trading)

- [ ] Meaning of each order status code (`R, P, S, F, C, RJ, PF, PFC`)
- [ ] Smart Order (GTT) request schema and whether it works for `INTRADAY` as well as `CNC`
- [ ] Broker auto square-off time for `INTRADAY` positions
- [ ] Intraday margin (leverage) for NIFTY 50 stocks
- [ ] Earliest date of `1minute` history
- [ ] Full charges sheet (see [06-costs-and-math.md](06-costs-and-math.md))
- [ ] Algo-ID / strategy registration needs for a personal API bot (see [02-regulation.md](02-regulation.md))
