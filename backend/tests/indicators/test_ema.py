import math

import pandas as pd
import pytest

from app.indicators.ema import ema


def test_ema_seeded_with_sma() -> None:
    out = ema(pd.Series([1.0, 2, 3, 4, 5, 6]), 3)
    assert math.isnan(out.iloc[0]) and math.isnan(out.iloc[1])
    assert out.iloc[2:].tolist() == pytest.approx([2.0, 3.0, 4.0, 5.0])


def test_ema_hand_values() -> None:
    out = ema(pd.Series([10.0, 20, 30, 10]), 2)
    assert out.iloc[1:].tolist() == pytest.approx([15.0, 25.0, 15.0])


def test_ema_short_input_is_all_nan() -> None:
    assert ema(pd.Series([1.0, 2]), 3).isna().all()


def test_ema_keeps_index() -> None:
    s = pd.Series([1.0, 2, 3], index=[10, 20, 30])
    assert list(ema(s, 2).index) == [10, 20, 30]


def test_ema_no_look_ahead() -> None:
    base = pd.Series([1.0, 2, 3, 4, 5, 6])
    changed = base.copy()
    changed.iloc[5] = 100.0
    pd.testing.assert_series_equal(ema(base, 3).iloc[:5], ema(changed, 3).iloc[:5])


def test_ema_rejects_bad_period() -> None:
    with pytest.raises(ValueError, match="period"):
        ema(pd.Series([1.0]), 0)
