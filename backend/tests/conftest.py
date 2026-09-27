from collections.abc import Iterator
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _hermetic(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    # Run every test from an empty directory so a real .env (secrets, live mode) is never loaded.
    monkeypatch.chdir(tmp_path)
    yield
