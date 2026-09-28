import pandas as pd

from app.core.clock import IST


def require_ist_index(candles: pd.DataFrame) -> pd.DatetimeIndex:
    """Session maths groups by calendar day, which is only correct on an IST index."""
    index = candles.index
    if not isinstance(index, pd.DatetimeIndex) or str(index.tz) != str(IST):
        raise ValueError("candles must have a tz-aware Asia/Kolkata DatetimeIndex")
    return index
