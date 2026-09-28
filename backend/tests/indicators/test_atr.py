import math

import pandas as pd
import pytest

from app.indicators.atr import atr, true_range


def _candles() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "open": [9.0, 9, 10, 12, 12],
            "high": [10.0, 11, 13, 12, 14],
            "low": [8.0, 9, 10, 11, 12],
            "close": [9.0, 10, 12, 11, 13],
            "volume": [100, 100, 100, 100, 100],
        }
    )


def test_true_range_uses_previous_close() -> None:
    tr = true_range(_candles())
    assert math.isnan(tr.iloc[0])
    # bar 4 gaps: high 14 - prev close 11 = 3 > high-low 2
    assert tr.iloc[1:].tolist() == pytest.approx([2.0, 3.0, 1.0, 3.0])


def test_atr_wilder_hand_values() -> None:
    out = atr(_candles(), 2)
    assert math.isnan(out.iloc[0]) and math.isnan(out.iloc[1])
    assert out.iloc[2:].tolist() == pytest.approx([2.5, 1.75, 2.375])


def test_atr_short_input_is_all_nan() -> None:
    assert atr(_candles().iloc[:2], 2).isna().all()


def test_atr_no_look_ahead() -> None:
    base = _candles()
    changed = base.copy()
    changed.loc[4, "high"] = 50.0
    pd.testing.assert_series_equal(atr(base, 2).iloc[:4], atr(changed, 2).iloc[:4])


def test_atr_rejects_bad_period() -> None:
    with pytest.raises(ValueError, match="period"):
        atr(_candles(), 0)
