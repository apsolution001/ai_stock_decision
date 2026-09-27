---
name: backtest-strategy
description: Use when evaluating whether a strategy may be paper-traded — runs the TRAIN/TEST/walk-forward backtest with full costs and slippage, writes the result file, and judges PASS/FAIL against docs/standards/backtest-standards.md.
---

# Backtest a Strategy

Source of truth for the pass bar: `docs/standards/backtest-standards.md`. Costs come from `docs/research/06-costs-and-math.md`.

## Checklist

1. **Data**
   - [ ] Use cached data under `data/` (git-ignored) if present; otherwise download it with the historical downloader. Respect `docs/research/01-indstocks-api.md` limits: max 5 scrips per request, 7-day windows for 1-minute data, 5 req/s, request in ms and response `ts` in seconds.
   - [ ] Include the NIFTY index (`NIDX:26000`) for the market filter.
   - [ ] Record the actual earliest date available. If it's later than 2019-01-01, note it in the result.
   - [ ] Record universe survivorship bias if the universe is not point-in-time.

2. **Realism** (all required)
   - [ ] Same strategy + `RiskManager` + charges code as live.
   - [ ] Full charges; slippage 0.05% against us; stops filled at the bar open if the price gapped through.
   - [ ] Completed candles only (no look-ahead); exchange holiday calendar.
   - [ ] Day rules: 3 trades/day, +1.5% / −1% day stops, entry window 09:30–14:30, 15:15 square-off.

3. **TRAIN (2019-01-01 → 2023-12-31)**
   - [ ] Small parameter grid **on TRAIN only**.
   - [ ] Choose from a **stable region**, where neighbouring values are also profitable, not the single best point.
   - [ ] Freeze the parameters and write them down **before** touching TEST.

4. **TEST (2024-01-01 → latest)**
   - [ ] Run **once** with the frozen parameters. No tuning after looking. If you re-run with changes, it's a new run and must be reported as such.

5. **Walk-forward**
   - [ ] Rolling 12-month train / 3-month test windows. Count the positive windows.

6. **Judge** against the pass bar (TEST, after costs):
   - [ ] ≥ 200 trades · profit factor > 1.3 · max drawdown < 10% · ≥ 60% positive months · ≥ 60% walk-forward windows positive · win rate above break-even · parameters stable

7. **Write the result file**: `docs/research/strategy-results/YYYY-MM-DD-<strategy>-<run>.md`
   - [ ] Strategy version, parameters, data range, git commit hash
   - [ ] All metrics, equity-curve summary, monthly table, walk-forward table
   - [ ] **PASS / FAIL** with the reason; known biases and limitations

8. **Review**
   - [ ] Ask the `backtest-validator` agent to review the code and result file for look-ahead, cost or slippage mistakes and overfitting.
   - [ ] Fix any issue it finds and re-run as a **new** run.

9. **On FAIL**
   - [ ] Follow the "what happens if it fails" table in `docs/research/03-strategies.md`. **Never loosen the bar.**
