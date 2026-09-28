from datetime import time
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.core.config import Settings, get_settings
from app.risk.charges import ChargeRates


def test_defaults_match_decisions_log() -> None:
    s = Settings()
    assert s.trading_mode == "paper"
    assert s.observe_only_days == 3
    assert s.capital == Decimal("25000")
    assert s.max_trades_per_day == 3
    assert s.daily_profit_stop_pct == Decimal("1.5")
    assert s.daily_loss_stop_pct == Decimal("-1")
    assert s.risk_per_trade == Decimal("100")
    assert s.max_swing_positions == 1
    assert s.max_orders_per_second == 2
    assert s.entry_window_start == time(9, 30)
    assert s.entry_window_end == time(14, 30)
    assert s.intraday_squareoff == time(15, 15)


def test_money_fields_are_decimal() -> None:
    s = Settings()
    assert isinstance(s.capital, Decimal)
    assert isinstance(s.risk_per_trade, Decimal)


def test_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MAX_TRADES_PER_DAY", "2")
    monkeypatch.setenv("RISK_PER_TRADE", "125")
    s = Settings()
    assert s.max_trades_per_day == 2
    assert s.risk_per_trade == Decimal("125")


def test_live_mode_refused_without_confirm(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TRADING_MODE", "live")
    with pytest.raises(ValidationError, match="LIVE_CONFIRM"):
        Settings()


def test_live_mode_refused_with_wrong_confirm(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TRADING_MODE", "live")
    monkeypatch.setenv("LIVE_CONFIRM", "yes")
    with pytest.raises(ValidationError, match="LIVE_CONFIRM"):
        Settings()


def test_unknown_mode_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TRADING_MODE", "LIVE ")
    with pytest.raises(ValidationError):
        Settings()


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("MAX_TRADES_PER_DAY", "0"),
        ("DAILY_LOSS_STOP_PCT", "1"),
        ("DAILY_LOSS_STOP_PCT", "0"),
        ("DAILY_PROFIT_STOP_PCT", "-1"),
        ("RISK_PER_TRADE", "0"),
        ("RISK_PER_TRADE", "25000"),
        ("CAPITAL", "0"),
        ("MAX_ORDERS_PER_SECOND", "11"),
        ("MAX_SWING_POSITIONS", "-1"),
        ("STT_INTRADAY_SELL_PCT", "-0.1"),
    ],
)
def test_invalid_limits_refused(monkeypatch: pytest.MonkeyPatch, name: str, value: str) -> None:
    monkeypatch.setenv(name, value)
    with pytest.raises(ValidationError):
        Settings()


def test_entry_window_must_be_ordered(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENTRY_WINDOW_END", "15:30")
    with pytest.raises(ValidationError, match="entry window"):
        Settings()


def test_entry_window_start_before_market_open_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENTRY_WINDOW_START", "09:00")
    with pytest.raises(ValidationError, match="entry window"):
        Settings()


def test_intraday_squareoff_after_market_close_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INTRADAY_SQUAREOFF", "15:45")
    with pytest.raises(ValidationError, match="entry window"):
        Settings()


def test_validation_error_does_not_echo_live_confirm(monkeypatch: pytest.MonkeyPatch) -> None:
    # I2 (safety rules §4): a raised ValidationError must never leak secret-shaped input back out.
    monkeypatch.setenv("TRADING_MODE", "live")
    monkeypatch.setenv("LIVE_CONFIRM", "sentinel-secret-7731")
    with pytest.raises(ValidationError) as excinfo:
        Settings()
    assert "sentinel-secret-7731" not in str(excinfo.value)


def test_charge_rates_from_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    assert Settings().charge_rates() == ChargeRates()
    monkeypatch.setenv("BROKERAGE_PER_ORDER", "20")
    assert Settings().charge_rates().brokerage_per_order == Decimal("20")


def test_get_settings_is_cached() -> None:
    assert get_settings() is get_settings()
