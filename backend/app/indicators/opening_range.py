from datetime import time

import pandas as pd

from app.indicators.frame import require_ist_index


def opening_range(
    candles: pd.DataFrame, start: time = time(9, 15), end: time = time(9, 30)
) -> pd.DataFrame:
    """Per-day high/low of bars whose start time is in [start, end) (research/03, candidate 1)."""
    index = require_ist_index(candles)
    bar_times = index.time
    in_window = (bar_times >= start) & (bar_times < end)
    window = candles[in_window]
    result: pd.DataFrame = window.groupby(index[in_window].date).agg(
        or_high=("high", "max"), or_low=("low", "min")
    )
    return result
