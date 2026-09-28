import math
from datetime import date, datetime

import pandas as pd
import pytest

from app.core.clock import IST
from app.indicators.opening_range import opening_range
from app.indicators.volume import slot_volume_ratio
from app.indicators.vwap import session_vwap


def _frame(rows: list[tuple[datetime, float, float, float, float]]) -> pd.DataFrame:
    """rows: (start, high, low, close, volume)."""
    index = pd.DatetimeIndex([r[0] for r in rows])
    return pd.DataFrame(
        {
            "open": [r[3] for r in rows],
            "high": [r[1] for r in rows],
            "low": [r[2] for r in rows],
            "close": [r[3] for r in rows],
            "volume": [r[4] for r in rows],
        },
        index=index,
    )


def _at(day: int, hour: int, minute: int) -> datetime:
    return datetime(2026, 9, day, hour, minute, tzinfo=IST)


def _two_days() -> pd.DataFrame:
    return _frame(
        [
            (_at(28, 9, 15), 11, 9, 10, 100),  # typical 10
            (_at(28, 9, 20), 12, 10, 11, 200),  # typical 11
            (_at(28, 9, 25), 13, 11, 12, 100),  # typical 12
            (_at(29, 9, 15), 21, 19, 20, 50),  # new day: typical 20
        ]
    )


def test_vwap_hand_values_and_daily_reset() -> None:
    out = session_vwap(_two_days())
    assert out.tolist() == pytest.approx([10.0, 3200 / 300, 11.0, 20.0])


def test_vwap_zero_volume_is_nan_not_inf() -> None:
    candles = _frame([(_at(28, 9, 15), 11, 9, 10, 0), (_at(28, 9, 20), 12, 10, 11, 100)])
    out = session_vwap(candles)
    assert math.isnan(out.iloc[0])
    assert out.iloc[1] == pytest.approx(11.0)


def test_vwap_no_look_ahead() -> None:
    base = _two_days()
    changed = base.copy()
    changed.iloc[2, changed.columns.get_loc("volume")] = 10_000
    assert session_vwap(base).iloc[:2].tolist() == session_vwap(changed).iloc[:2].tolist()


def test_opening_range_excludes_0930_bar() -> None:
    candles = _frame(
        [
            (_at(28, 9, 15), 101, 99, 100, 10),
            (_at(28, 9, 20), 103, 100, 102, 10),
            (_at(28, 9, 25), 102, 98, 101, 10),
            (_at(28, 9, 30), 110, 97, 105, 10),
        ]
    )
    out = opening_range(candles)
    assert list(out.index) == [date(2026, 9, 28)]
    assert out.loc[date(2026, 9, 28), "or_high"] == 103
    assert out.loc[date(2026, 9, 28), "or_low"] == 98


def test_slot_volume_ratio_uses_only_previous_days() -> None:
    rows = []
    for day, v915, v920 in [(28, 100, 50), (29, 300, 50), (30, 400, 25)]:
        rows.append((_at(day, 9, 15), 11.0, 9.0, 10.0, float(v915)))
        rows.append((_at(day, 9, 20), 11.0, 9.0, 10.0, float(v920)))
    out = slot_volume_ratio(_frame(rows), lookback=2)
    assert out.iloc[:4].isna().all()
    assert out.iloc[4] == pytest.approx(400 / 200)
    assert out.iloc[5] == pytest.approx(25 / 50)


def test_slot_volume_ratio_zero_average_is_nan() -> None:
    rows = [
        (_at(28, 9, 15), 11.0, 9.0, 10.0, 0.0),
        (_at(29, 9, 15), 11.0, 9.0, 10.0, 100.0),
    ]
    out = slot_volume_ratio(_frame(rows), lookback=1)
    assert math.isnan(out.iloc[1])


@pytest.mark.parametrize("tz", [None, "UTC"])
def test_session_indicators_reject_non_ist_index(tz: str | None) -> None:
    candles = _two_days()
    candles.index = pd.DatetimeIndex([ts.replace(tzinfo=None) for ts in candles.index])
    if tz is not None:
        candles.index = candles.index.tz_localize(tz)
    for fn in (session_vwap, opening_range, slot_volume_ratio):
        with pytest.raises(ValueError, match="Asia/Kolkata"):
            fn(candles)
