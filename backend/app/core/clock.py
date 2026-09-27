"""The only place allowed to read the wall clock.

Everything else calls `now()` so tests can inject time.
"""

from datetime import datetime, timedelta
from typing import Protocol
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")


class Clock(Protocol):
    def now(self) -> datetime: ...


def to_ist(dt: datetime) -> datetime:
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError(f"naive datetime not allowed: {dt!r}")
    return dt.astimezone(IST)


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(IST)


class FixedClock:
    def __init__(self, at: datetime) -> None:
        self._at = to_ist(at)

    def now(self) -> datetime:
        return self._at

    def advance(self, delta: timedelta) -> None:
        self._at = self._at + delta


_clock: Clock = SystemClock()


def set_clock(clock: Clock) -> None:
    global _clock
    _clock = clock


def now() -> datetime:
    return _clock.now()
