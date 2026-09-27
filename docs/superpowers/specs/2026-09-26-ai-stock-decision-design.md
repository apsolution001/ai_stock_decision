# AI Stock Decision — Design Spec

> **SUPERSEDED (2026-09-27):** the project changed to an auto-trading system on the INDstocks API. See `docs/research/07-decisions-log.md`. Kept for history; the Laya facts in the spec (§2) are still valid.

- **Date:** 2026-09-26
- **Status:** Approved (brainstorming)
- **Market:** Indian equities (NSE / BSE)
- **Decision engine:** [Laya](https://laya-ai.com/guides/install-laya) — open-source, non-autoregressive typed-decision model (Apache 2.0)

> Decision-support tool only. Outputs are not investment advice.

## 1. Goal

Produce auditable, confidence-gated **Buy / Hold / Sell** signals for Indian stocks by combining:

1. **News & sentiment signals** — headlines classified per ticker.
2. **Technical signals** — indicators computed from OHLCV data.
3. **Decision fusion** — Laya judges a compact text summary of both.
4. **Portfolio / watchlist scanner** — scheduled scans producing a ranked leaderboard.

Success criteria:

- `GET /stocks/{symbol}/analysis` returns a decision with per-component evidence in < 3 s on CPU for a cached symbol.
- A NIFTY 50 scan completes in < 10 min on CPU (auto-detect GPU when present).
- Every stored signal records its inputs (snapshot text, headlines, model id, package version) for audit.
- Evaluation harness reports accuracy / coverage-at-threshold on a labeled golden set.

## 2. Laya facts that shape the design

| Fact | Consequence |
|---|---|
| Question types: `choice` (≤ ~20 options), `score` (ordinal), `noul` (P(yes)) | All decisions modeled as these three types. |
| Output includes `probabilities`, `answer_confidence` | Gate on `answer_confidence`; below threshold → **"No call / review"**. |
| English `laya` reads 512 tokens; `laya-multilingual` 1024+ | States must be compact text summaries (one headline, or one indicator snapshot). |
| Base checkpoints near chance zero-shot on typed decisions (~0.36) | Fine-tuning + evaluation is a first-class phase, not optional. |
| Text only; no math, no data fetching | Indicators computed in code; Laya only judges text. |
| Devices: `cpu`, `cuda`, `mps`; ~808 MB checkpoint downloaded on first load; `HF_HUB_OFFLINE=1` supported | Auto-detect device; preload at worker start; cache checkpoint in a Docker volume. |
| Avoid boolean labels in `choice` questions | Use `noul` for yes/no. |

## 3. Tech stack

- **Backend:** Python 3.11, FastAPI, Pydantic v2, SQLAlchemy 2 + Alembic, PostgreSQL 16, Redis 7, Celery (worker + beat).
- **ML / data:** `laya`, `pandas`, `pandas-ta`, `yfinance`, `feedparser`, `httpx`.
- **Frontend:** Next.js (App Router, TypeScript), Tailwind CSS + shadcn/ui, TanStack Query, TradingView Lightweight Charts.
- **Tooling:** `uv` (Python deps), `pnpm` (web), ruff, mypy, pytest, Vitest, pre-commit, Docker Compose, GitHub Actions CI.

## 4. Architecture

```
            ┌──────────────┐      ┌──────────────┐
            │  data/prices │      │  data/news   │
            │  (yfinance)  │      │ (RSS feeds)  │
            └──────┬───────┘      └──────┬───────┘
                   ▼                     ▼
            ┌──────────────┐      ┌──────────────┐
            │  technical/  │      │  sentiment/  │
            │ indicators → │      │ Laya/headline│
            │ text snapshot│      │              │
            └──────┬───────┘      └──────┬───────┘
                   └─────────┬───────────┘
                             ▼
                     ┌──────────────┐
                     │  decision/   │  Laya fusion + confidence gate
                     └──────┬───────┘
                            ▼
              ┌─────────────┴─────────────┐
              ▼                           ▼
       ┌─────────────┐             ┌─────────────┐
       │  scanner/   │  Celery     │    api/     │  FastAPI
       │ (watchlist) │  beat       │             │
       └──────┬──────┘             └──────┬──────┘
              └──────────► Postgres ◄─────┘
                                  ▲
                            web/ (Next.js)
```

### Repository layout

```
backend/
  app/
    core/        config (pydantic-settings), logging, device detection
    data/        PriceProvider, NewsProvider protocols + adapters
    technical/   indicators, snapshot renderer
    engine/      DecisionEngine protocol, LayaEngine, FakeEngine
    sentiment/   headline question set + aggregation
    decision/    fusion question set + gating
    scanner/     watchlist scan orchestration, Celery tasks
    db/          SQLAlchemy models, repositories, Alembic
    api/         FastAPI routers, schemas
  tests/
  eval/          golden datasets, evaluation + fine-tune scripts
web/             Next.js app
docker-compose.yml
.github/workflows/ci.yml
```

## 5. Components

### 5.1 Data layer (`data/`)
- `PriceProvider.get_ohlcv(symbol, period, interval) -> DataFrame`; default `YFinancePriceProvider` using `.NS` / `.BO` suffixes.
- `NewsProvider.get_headlines(symbol, since) -> list[Headline]`; `RssNewsProvider` over Moneycontrol, ET Markets and Google News RSS (query = company name + symbol). Dedup by normalized title hash.
- Symbol master: CSV of NSE symbols → company names / sector (seeded with NIFTY 50).
- Results cached in Redis (prices 15 min, news 10 min).

### 5.2 Technical engine (`technical/`)
- Indicators: RSI(14), MACD(12,26,9), EMA 20/50/200, Bollinger(20,2), ATR(14), 20-day volume ratio, 52-week high/low distance.
- Derived facts (deterministic, code): trend (EMA stack), crossovers in last 5 sessions, overbought/oversold.
- `render_snapshot(facts) -> str` — ≤ ~300 tokens, fixed template, e.g. `"RELIANCE: close 2,941 (+1.2%). Trend: up (EMA20>EMA50>EMA200). RSI 68 (near overbought). MACD bullish crossover 2 days ago. Volume 1.8x 20d avg."`

### 5.3 Engine abstraction (`engine/`)
- `DecisionEngine.predict(state, questions) -> Answers` and `predict_batch(...)`.
- `LayaEngine`: wraps `laya.Router(preload=True)` or `laya.load(model_id)`; device auto-detected (`cuda` → `mps` → `cpu`); model id & version pinned via config.
- `FakeEngine`: deterministic, for tests and CI (no checkpoint download).

### 5.4 Sentiment engine (`sentiment/`)
Per headline questions:
- `sentiment` — `score`: `["very bearish","bearish","neutral","bullish","very bullish"]`
- `event_type` — `choice`: `earnings`, `mergers_acquisitions`, `regulatory_legal`, `management_change`, `order_win_contract`, `macro_sector`, `other`
- `relevance` — `noul`: "Is this headline primarily about {company}?"
- `risk_flag` — `noul`: "Does this headline report fraud, lawsuit, default, raid or regulatory penalty?"

Aggregation: drop headlines with relevance < 0.5; recency-weighted (half-life 3 days) mean sentiment; any risk_flag ≥ 0.7 surfaces a red flag.

### 5.5 Decision fusion (`decision/`)
State = technical snapshot + news summary line (`"News (7d): 6 relevant, avg sentiment bullish, events: earnings, order_win. Risk flags: none."`).
Questions:
- `action` — `choice`: `buy` ("strong uptrend with supportive news"), `hold` ("mixed or sideways"), `sell` ("downtrend or negative news/risk")
- `conviction` — `score`: `["low","medium","high"]`

Gating: `answer_confidence(action) < THRESHOLD` (default 0.7, configurable, tuned via eval) → `NO_CALL`. Risk flag present → cap action at `hold` and mark `review_required`.

### 5.6 Scanner (`scanner/`)
- Watchlists stored in DB (default: NIFTY 50).
- Celery beat: scan at 09:30 and 15:45 IST on trading days; manual trigger via API.
- Batches Laya calls with `predict_batch`; persists `Signal` rows; ranks by action then conviction × confidence.

### 5.7 API (`api/`)
- `GET  /health`
- `GET  /stocks/{symbol}/analysis` — fresh or cached decision + evidence
- `GET  /stocks/{symbol}/signals` — history
- `POST /scans` / `GET /scans/{id}` — trigger and poll a watchlist scan
- `GET  /scans/latest` — ranked leaderboard
- `CRUD /watchlists`

### 5.8 Web (`web/`)
- **Scanner page:** leaderboard table (symbol, action, conviction, confidence, sentiment, risk badge), filters.
- **Stock page:** candlestick chart with EMAs, indicator panel, tagged headlines, decision card showing the exact Laya state + probabilities.
- **Watchlists page.** Persistent disclaimer banner.

### 5.9 Data model
`Stock(symbol, exchange, name, sector)`, `Watchlist`, `WatchlistItem`, `Headline(id, symbol, title, source, url, published_at, hash)`, `HeadlineAnalysis(headline_id, sentiment, event_type, relevance, risk, model_id)`, `Signal(id, symbol, action, conviction, confidence, status[OK|NO_CALL|DEGRADED], review_required, technical_snapshot, news_summary, probabilities JSON, model_id, laya_version, created_at)`, `Scan(id, watchlist_id, status, started_at, finished_at)`.

## 6. Error handling
- Missing / stale price data → `DEGRADED` signal, technical section omitted, reason recorded.
- No news → decision on technicals only; noted in evidence.
- Laya load/inference failure → `NO_CALL` with error; worker retries with backoff; API never 500s on engine failure.
- External fetch failures retried (tenacity, 3 attempts), per-symbol isolation during scans.

## 7. Testing & evaluation
- Unit: indicators vs known values, snapshot renderer token budget, aggregation math, gating rules.
- API: FastAPI TestClient with `FakeEngine` and fixture providers.
- Integration (marked, opt-in): real Laya on CPU with a handful of cases.
- Eval (`eval/`): labeled Indian financial headlines (sentiment/event) and historical snapshots labeled by forward 10-day return; report accuracy and coverage-at-threshold; backtest simple long-only strategy vs NIFTY 50.
- Fine-tuning per Laya's fine-tune guide once a ≥ 1–2k labeled set exists; compare against base checkpoints.

## 8. Phases
0. Repo scaffold, tooling, CI, Docker Compose.
1. Data layer (prices, news, symbol master, cache).
2. Technical engine + snapshot.
3. Engine abstraction + Laya sentiment.
4. Decision fusion + gating.
5. Persistence, scanner, API.
6. Next.js dashboard.
7. Evaluation, threshold tuning, fine-tuning.

## 9. Out of scope (for now)
Order execution / broker integration, intraday tick data, options/F&O analytics, user auth beyond single-user.
