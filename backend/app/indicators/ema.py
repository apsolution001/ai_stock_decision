import numpy as np
import pandas as pd


def ema(values: pd.Series, period: int) -> pd.Series:
    """EMA seeded with the SMA of the first `period` values (TA-Lib convention); NaN before that."""
    if period < 1:
        raise ValueError(f"period must be >= 1, got {period}")
    arr = values.to_numpy(dtype=float)
    out = np.full(len(arr), np.nan)
    if len(arr) >= period:
        alpha = 2.0 / (period + 1)
        out[period - 1] = arr[:period].mean()
        for i in range(period, len(arr)):
            out[i] = alpha * arr[i] + (1 - alpha) * out[i - 1]
    return pd.Series(out, index=values.index, name=f"ema_{period}")
