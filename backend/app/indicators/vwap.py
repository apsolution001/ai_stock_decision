import numpy as np
import pandas as pd

from app.indicators.frame import require_ist_index


def session_vwap(candles: pd.DataFrame) -> pd.Series:
    """Typical-price VWAP, cumulative within each IST trading day (research/03)."""
    index = require_ist_index(candles)
    typical = (candles["high"] + candles["low"] + candles["close"]) / 3.0
    volume = candles["volume"].astype(float)
    day = index.date
    cum_pv = (typical * volume).groupby(day).cumsum()
    cum_volume = volume.groupby(day).cumsum()
    return (cum_pv / cum_volume.replace(0.0, np.nan)).rename("vwap")
