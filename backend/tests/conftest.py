from collections.abc import Iterator
from pathlib import Path

import pytest

from app.core.config import Settings, get_settings


@pytest.fixture(autouse=True)
def _hermetic(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    # Run every test from an empty directory so a real .env (secrets, live mode) is never loaded,
    # and drop any config the developer's shell exports (e.g. TRADING_MODE).
    monkeypatch.chdir(tmp_path)
    for name in Settings.model_fields:
        monkeypatch.delenv(name.upper(), raising=False)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
