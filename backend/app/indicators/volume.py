import numpy as np
import pandas as pd

from app.indicators.frame import require_ist_index


def slot_volume_ratio(candles: pd.DataFrame, lookback: int = 20) -> pd.Series:
    """Volume vs the same time slot's mean over the previous `lookback` days (research/03).

    shift(1) inside each slot excludes the current day, so there is no look-ahead.
    """
    if lookback < 1:
        raise ValueError(f"lookback must be >= 1, got {lookback}")
    index = require_ist_index(candles)
    volume = candles["volume"].astype(float)
    slot_mean = volume.groupby(index.time).transform(
        lambda s: s.shift(1).rolling(lookback, min_periods=lookback).mean()
    )
    return (volume / slot_mean.replace(0.0, np.nan)).rename("slot_volume_ratio")
