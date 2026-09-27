# Laya — Role in the System

Laya: open-source, typed-decision model ([install guide](https://laya-ai.com/guides/install-laya), Apache 2.0). The facts below come from the original design spec (`docs/superpowers/specs/2026-09-26-ai-stock-decision-design.md`, §2).

## Facts that constrain its use

| Fact | Consequence |
|---|---|
| Question types: `choice`, `score` (ordinal), `noul` (P(yes)) | The veto is a `noul` question; news risk is a `noul`; sentiment is a `score` |
| Outputs `probabilities` + `answer_confidence` | Gate on confidence; low confidence counts as **no veto** (fail-open) and is logged |
| English model reads **512 tokens** | The state is a compact text snapshot (≤ ~300 tokens) |
| **Zero-shot accuracy ≈ 0.36** on typed decisions, near chance | Laya **cannot originate trades**. It is only a veto or filter until fine-tuned and measured. |
| Text only: no maths, no data fetching | All indicators are computed in Python; Laya only reads rendered text |
| ~808 MB checkpoint, CPU / CUDA / MPS | Preload at startup; never load it inside the trading loop |

## Where Laya is used

1. **News risk filter (pre-market).** For each headline:
   - `relevance` (`noul`): "Is this headline primarily about {company}?"
   - `risk_flag` (`noul`): "Does this headline report fraud, lawsuit, default, raid, or regulatory penalty?"
   - `sentiment` (`score`): very bearish … very bullish

   If relevance ≥ 0.5 **and** risk ≥ 0.7, the stock is excluded for the day.
2. **Trade veto (live).** The state is the rendered setup snapshot plus the news summary.
   - `take_trade` (`noul`): "Given this setup, should a long intraday trade be taken now?"
   - If P(yes) < `LAYA_VETO_THRESHOLD`, the trade is **vetoed**.

## Measuring whether Laya helps

During paper trading, every signal is logged with the Laya answer and **both** outcomes are simulated:
- **Rules-only P&L**: every signal taken.
- **Rules + Laya P&L**: vetoed signals skipped.

After the test period, Laya's veto stays **on** only if Rules+Laya has **higher net P&L and a lower max drawdown** than rules-only. Otherwise Laya goes to log-only mode.

## Latency and safety rules

- Laya inference must never block the price loop. Run it in a worker thread, with a timeout of `LAYA_TIMEOUT_S` (default 2 s).
- **Timeout or error means no veto (fail-open) for the entry decision.** Hard risk rules still apply. The event is logged. Reason: Laya is an optional filter, and the risk manager is the real safety layer.
- **Exits never wait for Laya.** Stops and targets are pure code.

## Future

- Fine-tune on our own labeled data: signals labeled by actual trade outcome, per Laya's fine-tune guide. It can be promoted from veto to signal scorer only after measured accuracy beats rules-only on out-of-sample data.
