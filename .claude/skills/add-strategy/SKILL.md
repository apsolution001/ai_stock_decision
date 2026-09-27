---
name: add-strategy
description: Use when adding a new trading strategy (or a new variant of an existing one) to backend/app/strategies/. Covers research entry first, pure Strategy module, TDD with synthetic candles, registration, and the backtest gate before any paper/live use.
---

# Add a Strategy

A strategy is **pure logic**. It never trades by itself. It is only enabled for paper or live after a backtest **PASS**.

## Checklist

1. **Research entry first**
   - [ ] Add a section to `docs/research/03-strategies.md` covering: idea, why it can work, exact v0 rules, known failure modes, mitigations to test.
   - [ ] Confirm it fits the selection criteria in that file: uses only data we have, ≤ 3 trades/day, clear stop, liquid stocks, long-only for the MVP, mechanical.
   - [ ] If it needs any INDstocks behaviour not already recorded, run the `verify-api-fact` skill first.

2. **Write failing tests (TDD)**, in `backend/tests/strategies/test_<name>.py`
   - [ ] Build **synthetic candle series** where the correct signal (or no signal) is known by hand.
   - [ ] Cover: a clear entry, each rule failing on its own (one test per rule), entry-window edges (09:30, 14:30), no look-ahead (a signal uses only completed candles).
   - [ ] Verify each stop and target price exactly.
   - [ ] Run `uv run pytest backend/tests/strategies/test_<name>.py` and **confirm the tests fail** for the right reason.

3. **Implement the pure module**, `backend/app/strategies/<name>.py`
   - [ ] Implements the Strategy protocol: `on_candle(state) -> Signal | None`.
   - [ ] **No I/O**: no network, DB, clock reads (`datetime.now`), broker or Laya calls.
   - [ ] Parameters are a typed pydantic/dataclass config with defaults from the research doc.
   - [ ] Every returned `Signal` includes the stop-loss and target. **No stop means no signal.**
   - [ ] Comments cite `docs/research/03-strategies.md` for the *why* of each rule.
   - [ ] Indicators come from `backend/app/indicators/`. Don't re-implement them inline.
   - [ ] Follow `docs/standards/coding-standards.md` (types, file < ~300 lines).

4. **Make the tests pass**
   - [ ] `uv run pytest`, `uv run ruff check .`, `uv run mypy backend/app` are all clean.

5. **Register it, disabled**
   - [ ] Add it to the strategy registry with `enabled_paper=False`, `enabled_live=False`.
   - [ ] Registration must not change the behaviour of any currently enabled strategy.

6. **Backtest**
   - [ ] Run the `backtest-strategy` skill for this strategy.
   - [ ] Only on **PASS** (result file in `docs/research/strategy-results/`) can it be enabled for **paper**, and only after the owner agrees.
   - [ ] Live enablement only through the `pre-live-checklist` skill.

## Never

- Enable a strategy for paper or live without a PASS result file.
- Loosen `docs/standards/backtest-standards.md` to make it pass.
- Put risk limits inside the strategy. Limits live only in `RiskManager` (`docs/standards/trading-safety-rules.md`).
