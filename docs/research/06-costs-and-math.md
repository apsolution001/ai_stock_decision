# Costs & Target Math (₹25,000 capital)

- **Status:** brokerage is verified (₹10/order, [INDstocks FAQ](https://api-docs.indstocks.com/faq/)). Statutory charges below are the **standard NSE equity rates as we understand them**. ⚠️ Verify every rate against INDstocks' official charges page before live mode, and put them in config, never hard-coded.

## Charges per order (NSE equity)

| Charge | Intraday | Delivery (CNC) |
|---|---|---|
| Brokerage | ₹10 / order | ₹10 / order |
| STT | 0.025% on **sell** | 0.1% on **buy and sell** |
| Exchange transaction (NSE) | ~0.00297% of turnover | ~0.00297% |
| SEBI fee | ₹10 per crore | ₹10 per crore |
| Stamp duty | 0.003% on **buy** | 0.015% on **buy** |
| GST | 18% on (brokerage + exchange + SEBI) | same |
| DP charge | — | per sell scrip ⚠️ unknown for INDstocks |

## Example: one intraday round trip, ₹25,000 position

| Item | ₹ |
|---|---|
| Brokerage 2 × ₹10 | 20.00 |
| STT 0.025% × 25,000 | 6.25 |
| Exchange 0.00297% × 50,000 | 1.49 |
| Stamp 0.003% × 25,000 | 0.75 |
| GST 18% × (20 + 1.49) | 3.87 |
| **Total** | **≈ 32.4** |

3 trades/day comes to ≈ ₹97, which is **0.39% of capital per day in costs**.

## What this does to the risk rules

The plan risks ₹100 per trade with a 2R target:

| Outcome | Gross | Costs | **Net** |
|---|---|---|---|
| Win (2R) | +200 | −32 | **+168** |
| Loss (1R) | −100 | −32 | **−132** |

**Break-even win rate = 132 / (168 + 132) = 44%.** Any strategy must win more than 44% of the time at 2R, or have a larger average win.

**Implication:** costs are about ⅓ of the per-trade risk. The backtest must model them exactly. A strategy that looks profitable before costs can be a loser after them.

## Daily target reality

| Day | Net |
|---|---|
| 1 win | +₹168 (+0.67%) |
| 2 wins | +₹336 (+1.34%), so the +1.5% day-stop is not yet hit; a 3rd trade is allowed |
| 2 wins + 1 loss | +₹204 (+0.82%) |
| 2 losses | −₹264 (−1.06%). The **−1% day-stop triggers after the 2nd loss**. |

Real outcome: some days +1–2%, many days smaller, some days −1%. The goal is a **positive monthly** result, not a guaranteed daily one.

## Open decision

With these numbers, **₹100 risk per trade is tight relative to costs**. The backtest will compare ₹100 vs ₹125 per trade. Note that ₹125 × 2 losses = ₹250 plus costs, which is just over the −1% stop. The trade-off will be decided from data, not opinion.
