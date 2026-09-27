# Testing Standards

## Rules

1. **Test-first for all logic** (indicators, strategies, risk, charges, sizing, candle builder): write a failing test, then the code.
2. **No network in unit tests.** Use `FakeBroker`, recorded INDstocks payload fixtures, `FakeLaya` and an injected clock.
3. **Indicators** are tested against hand-computed or reference values (TA-Lib optional) on fixed fixtures.
4. **RiskManager has 100% branch coverage**: every limit is hit, every boundary tested (exactly 3 trades, exactly −1%, 14:30:00 vs 14:30:01, 15:15 square-off).
5. **Charges model** is tested against worked examples in `docs/research/06-costs-and-math.md`.
6. **Backtester** is tested with synthetic candle series whose correct trades and P&L are known by hand.
7. **Paper/live parity:** the same signal sequence through `PaperBroker` and a mocked `LiveBroker` produces identical decisions.
8. **Safety tests** (must always exist and pass):
   - `paper` mode can never reach a live order endpoint
   - live mode refuses to start without `LIVE_CONFIRM`
   - no order without a stop-loss
   - a stale feed or unknown position state switches to `HALTED`
   - token generation makes one attempt only on failure
   - secrets never appear in logs
9. **Integration tests** against the real INDstocks API are marked `@pytest.mark.live_api`, are read-only (data/quotes only), and are opt-in. **Tests never place real orders.**

## Commands

```bash
uv run pytest                 # unit + safety tests
uv run pytest -m live_api     # opt-in, read-only API checks
uv run ruff check . && uv run mypy backend/app
```

## Definition of done

The tests pass, lint and types are clean, and the change has been **verified by running it**, with actual output shown, not assumed.
