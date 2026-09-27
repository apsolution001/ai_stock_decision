# Backtest Standards (pass bar for any strategy)

A strategy may be paper-traded **only** if it meets every item below. **Never loosen the bar to make a strategy pass.**

## Realism requirements

- [ ] Uses the **same strategy + RiskManager + charges code** as live
- [ ] Full **charges model** (brokerage, STT, exchange, SEBI, stamp, GST)
- [ ] **Slippage:** entries and exits filled at the next bar open ± 0.05% against us (stop exits: at the stop price −0.05%, or at the bar open if it gapped through the stop)
- [ ] Signals use **only completed candles**. No look-ahead (an indicator at bar *t* uses data ≤ *t*).
- [ ] Day rules applied: 3 trades/day, +1.5% / −1% day stops, entry window, 15:15 square-off
- [ ] Universe is **point-in-time** where possible. If not, the survivorship bias is documented in the result.
- [ ] Holidays and half-days from the exchange calendar

## Data split

- **TRAIN:** 2019-01-01 → 2023-12-31 (tuning allowed)
- **TEST:** 2024-01-01 → latest (**run once**; no tuning after looking)
- **Walk-forward:** rolling 12-month train / 3-month test windows

## Pass bar (all measured on TEST, after costs)

| Metric | Required |
|---|---|
| Number of trades | ≥ 200 |
| Profit factor (gross profit ÷ gross loss) | > 1.3 |
| Max drawdown | < 10% of capital |
| Positive months | ≥ 60% |
| Walk-forward windows positive | ≥ 60% |
| Win rate at 2R | > break-even (~44%, see research/06) |
| Parameter stability | Neighbouring parameter values are also profitable (no single "lucky" point) |

## Reporting

Each run writes `docs/research/strategy-results/YYYY-MM-DD-<strategy>-<run>.md` with:
- strategy version, parameters, data range, git commit
- all metrics above, an equity-curve summary, monthly table
- **PASS / FAIL**, with the reason
- known biases or limitations of this run
