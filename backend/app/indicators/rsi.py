import numpy as np
import pandas as pd


def _rsi_value(avg_gain: float, avg_loss: float) -> float:
    if avg_loss == 0:
        return 50.0 if avg_gain == 0 else 100.0
    return 100.0 - 100.0 / (1.0 + avg_gain / avg_loss)


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """Wilder's RSI. The first value is at index `period` (needs `period` price changes)."""
    if period < 1:
        raise ValueError(f"period must be >= 1, got {period}")
    arr = close.to_numpy(dtype=float)
    out = np.full(len(arr), np.nan)
    if len(arr) > period:
        delta = np.diff(arr)
        gains = np.clip(delta, 0.0, None)
        losses = np.clip(-delta, 0.0, None)
        avg_gain = float(gains[:period].mean())
        avg_loss = float(losses[:period].mean())
        out[period] = _rsi_value(avg_gain, avg_loss)
        for i in range(period + 1, len(arr)):
            avg_gain = (avg_gain * (period - 1) + float(gains[i - 1])) / period
            avg_loss = (avg_loss * (period - 1) + float(losses[i - 1])) / period
            out[i] = _rsi_value(avg_gain, avg_loss)
    return pd.Series(out, index=close.index, name=f"rsi_{period}")
