import numpy as np
import pandas as pd


def true_range(candles: pd.DataFrame) -> pd.Series:
    """True range; the first bar has no previous close, so it is NaN."""
    prev_close = candles["close"].shift(1)
    ranges = pd.concat(
        [
            candles["high"] - candles["low"],
            (candles["high"] - prev_close).abs(),
            (candles["low"] - prev_close).abs(),
        ],
        axis=1,
    )
    return ranges.max(axis=1, skipna=False).rename("true_range")


def atr(candles: pd.DataFrame, period: int = 14) -> pd.Series:
    """Wilder's ATR (TA-Lib convention): first value at index `period` = mean of TR[1..period].

    A NaN anywhere in `candles` propagates to every later value (ATR is recursive), so callers
    must fill or split data gaps before calling this.
    """
    if period < 1:
        raise ValueError(f"period must be >= 1, got {period}")
    tr = true_range(candles).to_numpy(dtype=float)
    out = np.full(len(tr), np.nan)
    if len(tr) > period:
        out[period] = tr[1 : period + 1].mean()
        for i in range(period + 1, len(tr)):
            out[i] = (out[i - 1] * (period - 1) + tr[i]) / period
    return pd.Series(out, index=candles.index, name=f"atr_{period}")
