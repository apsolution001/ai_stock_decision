from decimal import Decimal

import pytest

from app.risk.charges import (
    ChargeBreakdown,
    ChargeRates,
    Product,
    Side,
    order_charges,
    round_trip_charges,
)

RATES = ChargeRates()
D = Decimal


def test_intraday_buy_25000() -> None:
    c = order_charges(Side.BUY, Product.INTRADAY, D("250"), 100, RATES)
    assert c == ChargeBreakdown(
        brokerage=D("10.00"),
        stt=D("0.00"),
        exchange_txn=D("0.74"),
        sebi=D("0.03"),
        stamp=D("0.75"),
        gst=D("1.94"),
        dp=D("0.00"),
    )
    assert c.total == D("13.46")


def test_intraday_sell_25000() -> None:
    c = order_charges(Side.SELL, Product.INTRADAY, D("250"), 100, RATES)
    assert c.stt == D("6.25")
    assert c.stamp == D("0.00")
    assert c.total == D("18.96")


def test_intraday_round_trip_matches_research_example() -> None:
    # docs/research/06: one intraday round trip on a 25,000 position costs about 32.4.
    assert round_trip_charges(Product.INTRADAY, D("250"), D("250"), 100, RATES).total == D("32.42")


def test_intraday_round_trip_with_different_exit_price() -> None:
    c = round_trip_charges(Product.INTRADAY, D("250"), D("255"), 100, RATES)
    assert c.stt == D("6.38")
    assert c.total == D("32.57")


def test_delivery_round_trip() -> None:
    buy = order_charges(Side.BUY, Product.DELIVERY, D("250"), 100, RATES)
    sell = order_charges(Side.SELL, Product.DELIVERY, D("250"), 100, RATES)
    assert buy.stt == D("25.00")
    assert buy.stamp == D("3.75")
    assert buy.total == D("41.46")
    assert sell.total == D("37.71")
    assert round_trip_charges(Product.DELIVERY, D("250"), D("250"), 100, RATES).total == D("79.17")


def test_dp_charge_only_on_delivery_sell() -> None:
    rates = ChargeRates(dp_charge_per_sell=D("15.93"))
    assert order_charges(Side.SELL, Product.DELIVERY, D("250"), 100, rates).dp == D("15.93")
    assert order_charges(Side.BUY, Product.DELIVERY, D("250"), 100, rates).dp == D("0.00")
    assert order_charges(Side.SELL, Product.INTRADAY, D("250"), 100, rates).dp == D("0.00")


def test_breakdown_addition() -> None:
    a = order_charges(Side.BUY, Product.INTRADAY, D("250"), 100, RATES)
    b = order_charges(Side.SELL, Product.INTRADAY, D("250"), 100, RATES)
    assert (a + b).total == a.total + b.total


def test_float_price_rejected() -> None:
    with pytest.raises(TypeError, match="Decimal"):
        order_charges(Side.BUY, Product.INTRADAY, 250.0, 100, RATES)  # type: ignore[arg-type]


@pytest.mark.parametrize("price", [D("0"), D("-1")])
def test_non_positive_price_rejected(price: Decimal) -> None:
    with pytest.raises(ValueError, match="price"):
        order_charges(Side.BUY, Product.INTRADAY, price, 100, RATES)


@pytest.mark.parametrize("quantity", [0, -5])
def test_non_positive_quantity_rejected(quantity: int) -> None:
    with pytest.raises(ValueError, match="quantity"):
        order_charges(Side.BUY, Product.INTRADAY, D("250"), quantity, RATES)
