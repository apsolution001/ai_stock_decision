# AI Stock Decision

A personal, rules-based trading system for Indian equities (NSE/BSE) on the INDmoney **INDstocks API**:
- a technical + fundamental + news rules engine finds trades
- [Laya](https://laya-ai.com/guides/install-laya) can veto a trade
- hard risk limits: max 3 trades/day, +1.5% / −1% daily stops
- paper trading first, and a live real-time UI

> ⚠️ Trading involves risk of loss. No daily profit is guaranteed. Paper mode is the default.

## Status

Design phase. Start here:

- Central guide: [`CLAUDE.md`](CLAUDE.md)
- Decisions: [`docs/research/07-decisions-log.md`](docs/research/07-decisions-log.md)
- Research: [`docs/research/`](docs/research/README.md)
- Standards and safety rules: [`docs/standards/`](docs/standards/)
- Original (superseded) signal-only design: [`docs/superpowers/specs/`](docs/superpowers/specs/)

## Stack

Python · FastAPI (async) · SQLite · INDstocks REST/WebSocket · pyotp · pandas · Laya · React + Vite · WebSocket live UI
