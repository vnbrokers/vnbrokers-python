from decimal import Decimal
from typing import Any

import pytest

from vnbrokers.brokers.dnse import DnseBroker
from vnbrokers.domain.enums import OrderSide, OrderType
from vnbrokers.domain.order import PlaceOrderRequest


@pytest.mark.integration
@pytest.mark.asyncio
async def test_trading_order_and_position_endpoints_accept_200_responses(
    dnse_broker: DnseBroker, dnse_server: Any
) -> None:
    assert (await dnse_broker.trading.positions.list_positions("0001179019"))[0].symbol == (
        "VN30F2506"
    )
    assert (
        await dnse_broker.trading.positions.get_position("177796763592657")
    ).account_id == "0001179019"
    assert (await dnse_broker.trading.positions.close_position("177796763592657")).source == "dnse"
    assert (
        await dnse_broker.trading.orders.place_order(
            PlaceOrderRequest(
                account_id="0001179019",
                symbol="VN30F2506",
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                quantity=Decimal("1"),
                price=Decimal("1200.5"),
            )
        )
    ).order_id == "116"
    assert (await dnse_broker.trading.orders.get_order("0001179019", "42")).broker == "dnse"
    assert (
        await dnse_broker.trading.orders.update_order(
            "0001179019", "42", price=Decimal("1201"), quantity=1
        )
    ).source == "dnse"
    assert await dnse_broker.trading.orders.cancel_order("0001179019", "42") is None

    dnse_server.assert_200_responses(7)
