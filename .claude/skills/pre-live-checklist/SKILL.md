---
name: pre-live-checklist
description: Use when the owner asks about going live, switching TRADING_MODE to live, or trading with real money — checks every gate and reports status. Claude never switches to live mode itself.
---

# Pre-Live Checklist

**Hard rule:** Claude **never** sets `TRADING_MODE=live` or `LIVE_CONFIRM`, and never edits `.env` for them. Claude only checks each item and **reports** the status to the owner. The owner makes the switch personally.

## Checklist (every item must be ✅ with evidence)

**Strategy**
- [ ] A **PASS** result file exists in `docs/research/strategy-results/` for each strategy to be enabled
- [ ] `backtest-validator` agent review of that result is clean
- [ ] **≥ 2 weeks of paper trading** logged in `docs/research/paper-log/`
- [ ] Paper results **track the backtest**: win rate, average R, slippage within tolerance; no unexplained gaps
- [ ] Laya decision made (veto on or off) from the paper comparison (`docs/research/04-laya-role.md`)

**Broker and regulation**
- [ ] All "Open questions" in `docs/research/01-indstocks-api.md` resolved, with sources
- [ ] All "Must confirm" items in `docs/research/02-regulation.md` answered, with date and source
- [ ] **Static IP whitelisted** on INDstocks, and the bot's machine actually uses that IP
- [ ] Charges in config verified against INDstocks' official charges page (`docs/research/06-costs-and-math.md`)
- [ ] Funds in the account ≥ configured capital

**Safety**
- [ ] `uv run pytest` passes, including every safety test in `docs/standards/testing-standards.md` §8
- [ ] `risk-safety-auditor` agent review of `risk/`, `broker/`, order flow: no open findings
- [ ] **Kill switch tested** in paper mode: closes intraday, cancels orders, halts entries
- [ ] Unknown state → `HALTED` tested (stale feed, position mismatch, invalid token)
- [ ] Limits in config match `docs/research/07-decisions-log.md`: 3 trades, +1.5%, −1%, ₹100 risk, 1 swing

**Owner actions** (the owner does these personally, never Claude)
- [ ] Owner sets `TRADING_MODE=live` in `.env`
- [ ] Owner sets `LIVE_CONFIRM=I_UNDERSTAND_REAL_MONEY` in `.env`
- [ ] Owner agrees the first live week uses the same ₹25,000 capital and the same limits

## Report format

Present a table with one row per item: ✅ / ❌ / ⚠️, evidence (file path, test output, date). If anything is ❌ or ⚠️, state clearly: **"Not ready for live."** List what's missing. Do not offer workarounds that skip a gate.
