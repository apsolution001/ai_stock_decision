from datetime import UTC, datetime, timedelta

import pytest

from app.core import clock
from app.core.clock import IST, FixedClock, SystemClock, set_clock, to_ist


def test_system_clock_is_ist_aware() -> None:
    assert SystemClock().now().tzinfo == IST


def test_to_ist_converts_utc() -> None:
    utc = datetime(2026, 9, 28, 4, 0, tzinfo=UTC)
    assert to_ist(utc) == datetime(2026, 9, 28, 9, 30, tzinfo=IST)
    assert to_ist(utc).tzinfo == IST


def test_to_ist_rejects_naive() -> None:
    with pytest.raises(ValueError, match="naive"):
        to_ist(datetime(2026, 9, 28, 9, 30))


def test_fixed_clock_rejects_naive() -> None:
    with pytest.raises(ValueError, match="naive"):
        FixedClock(datetime(2026, 9, 28, 9, 30))


def test_fixed_clock_returns_ist_and_advances() -> None:
    fixed = FixedClock(datetime(2026, 9, 28, 4, 0, tzinfo=UTC))
    assert fixed.now() == datetime(2026, 9, 28, 9, 30, tzinfo=IST)
    assert fixed.now().tzinfo == IST
    fixed.advance(timedelta(minutes=5))
    assert fixed.now() == datetime(2026, 9, 28, 9, 35, tzinfo=IST)


def test_module_now_uses_injected_clock() -> None:
    at = datetime(2026, 9, 28, 14, 30, tzinfo=IST)
    set_clock(FixedClock(at))
    assert clock.now() == at
