import math

import pandas as pd
import pytest

from app.indicators.rsi import rsi


def test_rsi_wilder_hand_values() -> None:
    # deltas 1, 1, -1, 2, -1; period 3 -> first avg gain 2/3, avg loss 1/3
    out = rsi(pd.Series([10.0, 11, 12, 11, 13, 12]), 3)
    assert all(math.isnan(v) for v in out.iloc[:3])
    assert out.iloc[3:].tolist() == pytest.approx([200 / 3, 250 / 3, 100 - 1300 / 33])


def test_rsi_only_gains_is_100() -> None:
    assert rsi(pd.Series([1.0, 2, 3, 4, 5]), 3).iloc[-1] == pytest.approx(100.0)


def test_rsi_flat_is_50() -> None:
    assert rsi(pd.Series([5.0] * 6), 3).iloc[-1] == pytest.approx(50.0)


def test_rsi_short_input_is_all_nan() -> None:
    assert rsi(pd.Series([1.0, 2, 3]), 3).isna().all()


def test_rsi_no_look_ahead() -> None:
    base = pd.Series([10.0, 11, 12, 11, 13, 12])
    changed = base.copy()
    changed.iloc[5] = 1.0
    assert rsi(base, 3).iloc[3:5].tolist() == rsi(changed, 3).iloc[3:5].tolist()


def test_rsi_rejects_bad_period() -> None:
    with pytest.raises(ValueError, match="period"):
        rsi(pd.Series([1.0]), 0)
