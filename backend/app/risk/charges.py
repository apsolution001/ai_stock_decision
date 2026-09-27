"""Per-order NSE equity charges. Rates: docs/research/06-costs-and-math.md.

Default rates are the standard NSE rates as understood in research/06 and MUST be verified against
INDstocks' official charges page before live mode; the live values come from config (Settings).
"""

from dataclasses import dataclass, fields
from decimal import ROUND_HALF_UP, Decimal
from enum import StrEnum

PAISE = Decimal("0.01")
HUNDRED = Decimal("100")
CRORE = Decimal("10000000")


class Side(StrEnum):
    BUY = "BUY"
    SELL = "SELL"


class Product(StrEnum):
    INTRADAY = "INTRADAY"
    DELIVERY = "DELIVERY"


@dataclass(frozen=True)
class ChargeRates:
    brokerage_per_order: Decimal = Decimal("10")
    stt_intraday_sell_pct: Decimal = Decimal("0.025")
    stt_delivery_pct: Decimal = Decimal("0.1")
    exchange_txn_pct: Decimal = Decimal("0.00297")
    sebi_per_crore: Decimal = Decimal("10")
    stamp_intraday_buy_pct: Decimal = Decimal("0.003")
    stamp_delivery_buy_pct: Decimal = Decimal("0.015")
    gst_pct: Decimal = Decimal("18")
    # INDstocks DP charge is unknown (research/06); 0 understates swing costs until verified.
    dp_charge_per_sell: Decimal = Decimal("0")


@dataclass(frozen=True)
class ChargeBreakdown:
    brokerage: Decimal
    stt: Decimal
    exchange_txn: Decimal
    sebi: Decimal
    stamp: Decimal
    gst: Decimal
    dp: Decimal

    @property
    def total(self) -> Decimal:
        return sum((getattr(self, f.name) for f in fields(self)), Decimal("0"))

    def __add__(self, other: "ChargeBreakdown") -> "ChargeBreakdown":
        return ChargeBreakdown(
            **{f.name: getattr(self, f.name) + getattr(other, f.name) for f in fields(self)}
        )


def _paise(amount: Decimal) -> Decimal:
    return amount.quantize(PAISE, rounding=ROUND_HALF_UP)


def order_charges(
    side: Side, product: Product, price: Decimal, quantity: int, rates: ChargeRates
) -> ChargeBreakdown:
    if not isinstance(price, Decimal):
        raise TypeError(f"price must be Decimal, got {type(price).__name__}")
    if price <= 0:
        raise ValueError(f"price must be positive, got {price}")
    if quantity <= 0:
        raise ValueError(f"quantity must be positive, got {quantity}")

    turnover = price * quantity
    is_buy = side is Side.BUY
    intraday = product is Product.INTRADAY

    if intraday:
        stt_pct = Decimal("0") if is_buy else rates.stt_intraday_sell_pct
        stamp_pct = rates.stamp_intraday_buy_pct if is_buy else Decimal("0")
    else:
        stt_pct = rates.stt_delivery_pct
        stamp_pct = rates.stamp_delivery_buy_pct if is_buy else Decimal("0")

    brokerage = rates.brokerage_per_order
    exchange_txn = turnover * rates.exchange_txn_pct / HUNDRED
    sebi = turnover * rates.sebi_per_crore / CRORE
    # GST is levied on the unrounded service components, then the result is rounded once.
    gst = (brokerage + exchange_txn + sebi) * rates.gst_pct / HUNDRED
    dp = rates.dp_charge_per_sell if (not intraday and not is_buy) else Decimal("0")

    return ChargeBreakdown(
        brokerage=_paise(brokerage),
        stt=_paise(turnover * stt_pct / HUNDRED),
        exchange_txn=_paise(exchange_txn),
        sebi=_paise(sebi),
        stamp=_paise(turnover * stamp_pct / HUNDRED),
        gst=_paise(gst),
        dp=_paise(dp),
    )


def round_trip_charges(
    product: Product,
    entry_price: Decimal,
    exit_price: Decimal,
    quantity: int,
    rates: ChargeRates,
) -> ChargeBreakdown:
    """Long-only round trip (D10): BUY at entry, SELL at exit."""
    buy = order_charges(Side.BUY, product, entry_price, quantity, rates)
    sell = order_charges(Side.SELL, product, exit_price, quantity, rates)
    return buy + sell
