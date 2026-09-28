from collections.abc import Iterator
from pathlib import Path

import pytest

from app.core.clock import SystemClock, set_clock
from app.core.config import Settings, get_settings


@pytest.fixture(autouse=True)
def _hermetic(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    # Run every test from an empty directory so a real .env (secrets, live mode) is never loaded,
    # and drop any config the developer's shell exports (e.g. TRADING_MODE).
    monkeypatch.chdir(tmp_path)
    for name in Settings.model_fields:
        monkeypatch.delenv(name.upper(), raising=False)
    get_settings.cache_clear()
    # M2: reset the global clock on both sides so one test's injected FixedClock can never
    # leak into the next test, regardless of which test forgets to reset it itself.
    set_clock(SystemClock())
    yield
    set_clock(SystemClock())
    get_settings.cache_clear()
