# Strategy Research

- **Status:** candidates chosen and not yet backtested. **No strategy trades, paper or live, until it passes [backtest-standards](../standards/backtest-standards.md).**
- **Honest baseline:** no strategy is "the best" in advance. Professional desks find edges by testing many ideas on historical data, keeping only what survives costs and unseen data, and re-checking continuously. We follow the same method.

## Selection criteria (why these three)

A strategy is a candidate only if it:

1. uses **only data we have**: INDstocks OHLCV, live ticks, the index feed;
2. trades **≤ 3 times/day** with a clear stop, which fits the ₹100 risk per trade;
3. works on **liquid NIFTY stocks**, where slippage is small;
4. is **long-only** for the MVP (shorting is Step 2);
5. has a **mechanical definition**, with no discretion, so it can be backtested exactly.

---

## Candidate 1 — Opening Range Breakout (ORB) + VWAP

**Idea.** The first 15 minutes (09:15–09:30) set the day's opening range. A break above it with volume shows buyers in control. VWAP (the volume-weighted average price) confirms that the average participant is in profit on the long side.

**Why it can work**
- Opening auctions and institutional orders cluster early, and breakouts from that range often trend.
- Widely studied on intraday equity and index data. Simple, with few parameters, so there is less room for overfitting.

**Rules (v0, parameters are tuned only on training data)**
- Stock passed the pre-market filter.
- A 5-min candle **closes above the opening range high**, between 09:30 and 14:30.
- Close **> VWAP**.
- Candle volume **≥ 1.5×** the average volume of the same time slot over the last 20 days.
- 5-min RSI(14) **between 55 and 75**.
- NIFTY 50 index **> its VWAP**.
- Entry at the next candle open. Stop at the **nearer of** the opening range low or entry − 1×ATR(14, 5-min). Target **2R** (twice the risk). Move the stop to breakeven at **1R**. Exit everything at **15:15**.

**Known failure modes**
- **Fake breakouts** on range-bound days: price pokes above the high and falls back. This is the most common loss.
- **Wide opening range** on gap days. The stop is far away, so the quantity becomes tiny and the trade is not worth the costs.
- **Late-day breakouts** have no time to reach the target.

**Mitigations to test (one at a time, then keep only what helps out-of-sample)**
- Skip if the opening range is **> 1.5×** the stock's 20-day average range.
- Require a **close** above the high, not just a wick.
- No new entries after **13:30** (test against 14:30).

---

## Candidate 2 — VWAP Pullback in Trend

**Idea.** On a trending day, price pulls back to VWAP and bounces. Buying the bounce gives a tighter stop than chasing a breakout.

**Why it can work**
- VWAP is a real execution benchmark for institutions, so buying often appears near it on trend days.
- Better risk/reward than breakouts, because the stop sits just below VWAP.

**Rules (v0)**
- Trend filter: price > VWAP for most of the session so far, and EMA(20, 5-min) rising.
- Price touches or dips within **0.2%** of VWAP, then a 5-min candle **closes back above** VWAP.
- NIFTY > its VWAP.
- Stop below the pullback low (min 0.3%). Target 2R, or the day's high if that is nearer and still ≥ 1.5R. Exit 15:15.

**Known failure modes**
- **Trend reversal**: the "pullback" is actually the start of a downtrend. Price cuts through VWAP.
- **Choppy days** with many VWAP crosses, where every signal is noise.

**Mitigations:** maximum 1 attempt per stock per day; require the NIFTY trend filter; skip if VWAP has been crossed > 3 times already.

---

## Candidate 3 — Previous Day High (PDH) Breakout

**Idea.** Stocks that closed strong yesterday (near their high, on high volume) and break **yesterday's high** today show continuing momentum.

**Why it can work**
- Short-term momentum (continuation over 1–5 days) is one of the most documented effects in equity markets.
- A natural fit for the **swing upgrade**: if daily-trend filters pass, the same trade can be held as CNC.

**Rules (v0)**
- Yesterday: close in the top 25% of the day's range, volume ≥ 1.5× 20-day average, close > EMA(20, daily).
- Today: price breaks yesterday's high after 09:30 with volume confirmation; NIFTY > its VWAP.
- Stop: the nearer of yesterday's close or 1×ATR(14, 5-min). Target 2R intraday.
- Swing variant: CNC, stop 1×ATR(14, daily), target 2R, max hold 5 days, stop and target placed as a broker **Smart Order (GTT)**.

**Known failure modes**
- **Gap-up opens above PDH**, so there is no clean breakout. Rule: skip if the open is > PDH.
- **Overnight gaps against swing trades** (news, global markets). Mitigation: the GTT stop plus the news risk filter, and only one swing position at a time.

---

## Ideas rejected for the MVP, and why

| Idea | Why rejected (for now) |
|---|---|
| **Scalping** (many small trades) | Costs are ~₹32 per round trip on a ₹25k position (see [06](06-costs-and-math.md)). Scalping profits are smaller than costs. It also breaks the 3-trade cap. |
| **RSI mean reversion intraday** (buy oversold) | Catches falling knives on trend days. Poor fit with a hard −1% day stop. Can be revisited in Step 2 as a range-day strategy. |
| **Gap fade** | Needs shorting to be useful (Step 2) and has high tail risk on news gaps. |
| **News-speed trading** (react to headlines) | Free RSS news arrives minutes late. Professionals get it in milliseconds, so we would always be last. News is used only as a **risk filter**. |
| **ML price prediction** (LSTM etc. on candles) | Very easy to overfit; accuracy on unseen data is usually near chance. Complexity is too high for an MVP. |
| **Options / F&O** | Out of scope. Equity only, by decision. |

---

## Process: what we do, and what happens if it fails

```
1. Download data      NIFTY 50 + NIFTY index, 1-min, max history available
2. Split              TRAIN 2019-01 → 2023-12   |   TEST 2024-01 → today (untouched)
3. Tune on TRAIN      small parameter grid only; prefer stable regions, not the single best point
4. Test on TEST       run once, with costs + slippage + all risk rules
5. Judge              pass bar in backtest-standards.md
6. Walk-forward       rolling 1-year train / 3-month test windows must be mostly positive
7. Paper trade        2–4 weeks live-paper; results must track the backtest
8. Live small         static IP, real money, same rules
```

| If this happens… | …we do this |
|---|---|
| A strategy fails the pass bar | Reject it. Record why in `docs/research/strategy-results/`. Never loosen the bar to pass it. |
| **All 3 fail** | The system stays in **observe-only**. Research the next ideas (range-day mean reversion, sector-relative strength, shorting). The system still logs signals every day. |
| Passes on TRAIN, fails on TEST | This is overfitting. Reject it and simplify (fewer rules and parameters). |
| Passes backtest, but paper-trading P&L is much worse | Check fills: are slippage, latency or missed signals being modelled correctly? Fix the model. Do not tweak the strategy to fit 2 weeks of data. |
| A live strategy degrades (20-trade rolling profit factor < 1.0) | Auto-pause the strategy, drop back to paper, and investigate. |
| Laya veto makes results worse on paper | Turn the veto off. The rules engine runs alone, and Laya stays in log-only mode. |

## Combining strategies

If two or more candidates pass, run them together under the **same global limits**: 3 trades/day, +1.5% / −1% day stops, ₹100 risk per trade. If two signals fire at once, take the one with the higher backtested expectancy (average profit per trade).
