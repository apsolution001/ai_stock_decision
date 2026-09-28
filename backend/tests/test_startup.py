"""I1 (safety rules §2): the app must refuse to start on an invalid config."""

import pytest
from pydantic import ValidationError

from app.main import create_app


def test_create_app_refuses_live_mode_without_confirm(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TRADING_MODE", "live")
    with pytest.raises(ValidationError):
        create_app()


def test_create_app_refuses_risk_per_trade_over_capital(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RISK_PER_TRADE", "25000")
    with pytest.raises(ValidationError):
        create_app()
