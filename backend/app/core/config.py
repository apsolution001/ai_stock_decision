"""All thresholds live here.

Defaults: docs/research/07-decisions-log.md and docs/standards/trading-safety-rules.md.
An invalid config refuses to load, so the app refuses to start.
"""

from dataclasses import fields
from datetime import time
from decimal import Decimal
from functools import lru_cache
from typing import Literal, Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.risk.charges import ChargeRates

LIVE_CONFIRM_PHRASE = "I_UNDERSTAND_REAL_MONEY"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", frozen=True)

    # Mode (safety rules §1). Live is only ever set by the owner in .env.
    trading_mode: Literal["paper", "live"] = "paper"
    live_confirm: str = ""
    observe_only_days: int = Field(default=3, ge=0)

    # Hard risk limits (safety rules §2, decisions D4-D9).
    capital: Decimal = Field(default=Decimal("25000"), gt=0)
    max_trades_per_day: int = Field(default=3, ge=1)
    daily_profit_stop_pct: Decimal = Field(default=Decimal("1.5"), gt=0)
    daily_loss_stop_pct: Decimal = Field(default=Decimal("-1"), lt=0)
    risk_per_trade: Decimal = Field(default=Decimal("100"), gt=0)
    max_swing_positions: int = Field(default=1, ge=0)
    max_position_value: Decimal = Field(default=Decimal("25000"), gt=0)
    # Own cap; the broker allows 10/s.
    max_orders_per_second: int = Field(default=2, ge=1, le=10)
    entry_window_start: time = time(9, 30)
    entry_window_end: time = time(14, 30)
    intraday_squareoff: time = time(15, 15)

    # Charges (research/06). Verify against INDstocks' official page before live.
    brokerage_per_order: Decimal = Field(default=Decimal("10"), ge=0)
    stt_intraday_sell_pct: Decimal = Field(default=Decimal("0.025"), ge=0)
    stt_delivery_pct: Decimal = Field(default=Decimal("0.1"), ge=0)
    exchange_txn_pct: Decimal = Field(default=Decimal("0.00297"), ge=0)
    sebi_per_crore: Decimal = Field(default=Decimal("10"), ge=0)
    stamp_intraday_buy_pct: Decimal = Field(default=Decimal("0.003"), ge=0)
    stamp_delivery_buy_pct: Decimal = Field(default=Decimal("0.015"), ge=0)
    gst_pct: Decimal = Field(default=Decimal("18"), ge=0)
    dp_charge_per_sell: Decimal = Field(default=Decimal("0"), ge=0)

    @model_validator(mode="after")
    def _check_consistency(self) -> Self:
        if self.trading_mode == "live" and self.live_confirm != LIVE_CONFIRM_PHRASE:
            raise ValueError("live mode requires LIVE_CONFIRM to be set by the owner in .env")
        if not (self.entry_window_start < self.entry_window_end < self.intraday_squareoff):
            raise ValueError("entry window must satisfy start < end < intraday squareoff")
        if self.risk_per_trade >= self.capital:
            raise ValueError("risk_per_trade must be smaller than capital")
        return self

    def charge_rates(self) -> ChargeRates:
        return ChargeRates(**{f.name: getattr(self, f.name) for f in fields(ChargeRates)})


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
