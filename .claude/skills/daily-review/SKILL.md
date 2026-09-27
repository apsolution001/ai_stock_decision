---
name: daily-review
description: Use after market close (after 15:30 IST) on a paper or live trading day to review the day's signals, trades and P&L, check every risk limit was respected, compare rules-only vs rules+Laya, flag anomalies, and append the paper-log entry.
---

# Daily Review

Output: `docs/research/paper-log/YYYY-MM-DD.md` (one file per trading day).

## Checklist

1. **Collect the day's data** (from the SQLite DB via repositories or the API)
   - [ ] Mode (`paper`/`live`) and whether it was an observe-only day (first 3 days)
   - [ ] All signals: time, symbol, strategy, entry, stop, target, Laya P(yes), vetoed or not
   - [ ] All orders and fills, with requested vs filled price
   - [ ] Closed and open positions; realized P&L; open MTM (swing)
   - [ ] Charges per trade (the model's figure) and net P&L
   - [ ] State events: `HALTED`, feed staleness, reconnects, token issues, kill-switch use

2. **Verify the risk limits** (`docs/standards/trading-safety-rules.md` §2)
   - [ ] ≤ 3 new trades
   - [ ] No entries after the +1.5% or −1% day stop fired
   - [ ] All entries inside 09:30–14:30; intraday flat by 15:15
   - [ ] Risk per trade ≤ ₹100; ≤ 1 open swing, with a broker GTT stop in place
   - [ ] Every order had a stop before entry
   - [ ] **Any violation is a critical bug.** Report it to the owner at the top of the log and recommend `HALTED` until it's fixed.

3. **Laya comparison** (`docs/research/04-laya-role.md`)
   - [ ] Rules-only net P&L vs rules+Laya net P&L for the day, and cumulative
   - [ ] Count of vetoes, and how vetoed trades would have ended
   - [ ] Laya timeouts or errors

4. **Anomalies vs backtest**
   - [ ] Slippage: average fill vs model (0.05%); flag if worse
   - [ ] Missed signals: backtest logic replayed on today's candles vs signals actually raised
   - [ ] Win rate and average R vs the backtest result file (cumulative)

5. **Write the log file**, with these sections:
   - Summary: mode, trades, net P&L (₹ and %), day-stop hit?
   - Limits check (pass/fail per rule)
   - Trades table
   - Laya comparison
   - Anomalies and actions
   - Cumulative: days, net P&L, max drawdown, profit factor

6. **Report to the owner**: a 3–5 line summary and any critical issue. Don't change strategy parameters based on one day.
