# CLAUDE.md — AI Stock Decision (Indian equity auto-trader)

## What this project is

A personal trading system for **Indian equity stocks (NSE/BSE)** using the **INDmoney INDstocks API**.
- **Rules engine** (technical + fundamental + news filters) finds trades.
- **Laya** can **veto** a trade but never starts one.
- **RiskManager** enforces hard limits.
- A **React UI** shows everything live over WebSocket.

**Real money is involved. Correctness over speed. Never guess. Verify, then state facts with evidence.**

## Current phase

Brainstorming / design. Decisions are in `docs/research/07-decisions-log.md`. Design sections 2+ are pending owner approval, then the spec, then the implementation plan.

Rollout: **Step 1** backtest 3 strategies → **Step 2** live engine + paper + UI (first 3 days observe-only) → **Step 3** 2–4 weeks paper → **Step 4** live (static IP).

Foundation (scaffold, IST clock, charges, validated config, indicators, CI) is built per `docs/superpowers/plans/2026-09-27-01-foundation.md`.

## Key numbers (from the decisions log)

| Setting | Value |
|---|---|
| Capital | ₹25,000 |
| Trades/day | max 3 |
| Day profit stop | +1.5% net |
| Day loss stop | −1% net |
| Risk/trade | ₹100 |
| Entry window | 09:30–14:30 IST |
| Intraday exit | 15:15 IST |
| Direction | Long only (MVP) |
| Holding | Intraday by default; swing only when strict rules pass (max 1 open, broker GTT stop) |

## Must-read before working

- Safety (non-negotiable): @docs/standards/trading-safety-rules.md
- Coding: @docs/standards/coding-standards.md
- Testing: @docs/standards/testing-standards.md
- Backtest pass bar: @docs/standards/backtest-standards.md
- Git: @docs/standards/git-workflow.md
- Research index: `docs/research/README.md`. Broker facts: `docs/research/01-indstocks-api.md`

## Hard rules for Claude

1. **Never set `TRADING_MODE=live`**, never write `LIVE_CONFIRM`, and never place a real order, in code, tests or commands. Only the owner does that.
2. **Never read, print or commit `.env` or any secret** (MPIN, TOTP secret, tokens).
3. **Broker behaviour must be verified.** If it isn't in `docs/research/01-indstocks-api.md`, use the `verify-api-fact` skill first.
4. **Every order goes through `RiskManager.approve()`.** No bypasses.
5. **No strategy trades** (paper or live) without a PASS result under `docs/research/strategy-results/`.
6. Money is `Decimal`; time is tz-aware IST; strategies are pure and shared by backtest, paper and live.
7. Report outcomes truthfully: failing tests, unverified facts and skipped steps are stated plainly.

## Agents (`.claude/agents/`)

| Agent | Use for |
|---|---|
| `sr-coder` | Architecture, task breakdown, reviews, and the risky core (risk, broker, order flow, backtest core) |
| `coder` | Implementing clearly specified tasks test-first (indicators, strategies, data, API, UI wiring) |
| `strategy-researcher` | Designing or researching strategies |
| `backtest-validator` | Running or reviewing backtests against the pass bar |
| `risk-safety-auditor` | **Required review** for changes to risk/, broker/, engine/, config |
| `indstocks-api-specialist` | Broker REST/WS/auth code |
| `ui-realtime-builder` | React live UI |

## Skills (`.claude/skills/`)

`add-strategy` · `backtest-strategy` · `verify-api-fact` · `daily-review` · `pre-live-checklist`

## Commands (once scaffolded)

On Windows, one script wraps all of these: `.\run.ps1 setup | check | fix | test | serve` (run `.\run.ps1 help`).

```bash
uv sync                                        # install deps (Python 3.11 via .python-version)
uv run pytest                                  # unit + safety tests
uv run ruff format . && uv run ruff check . && uv run mypy backend/app
uv run uvicorn app.main:app --app-dir backend  # backend
pnpm --dir web dev                             # UI (later)
```
