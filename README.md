# AI Stock Decision

Confidence-gated **Buy / Hold / Sell** decision support for Indian equities (NSE/BSE), combining news sentiment, technical indicators and a watchlist scanner. Decisions are made with [Laya](https://laya-ai.com/guides/install-laya), an open-source typed-decision model.

> ⚠️ Decision-support tool only. Not investment advice.

## Status

Planning. See:

- Design spec: [`docs/superpowers/specs/2026-09-26-ai-stock-decision-design.md`](docs/superpowers/specs/2026-09-26-ai-stock-decision-design.md)
- Implementation plan: [`docs/superpowers/plans/`](docs/superpowers/plans/)

## Stack

FastAPI · PostgreSQL · Redis · Celery · Laya · pandas-ta · yfinance · Next.js · Tailwind/shadcn · Docker Compose · GitHub Actions
