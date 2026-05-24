from typing import Any

import pytest

from vnbrokers.brokers.dnse import DnseBroker


@pytest.mark.integration
@pytest.mark.asyncio
async def test_market_data_endpoints_accept_200_responses(
    dnse_broker: DnseBroker, dnse_server: Any
) -> None:
    assert (await dnse_broker.market_data.symbols.list_symbols(symbol="ACB"))[0].symbol == "ACB"
    assert (
        await dnse_broker.market_data.symbols.get_security_definition("HPG", board_id="G1")
    ).source == "dnse"
    assert (await dnse_broker.market_data.symbols.get_working_dates()).source == "dnse"
    assert (await dnse_broker.market_data.quotes.get_quote("ACB", board_id="G1")).symbol == "ACB"
    assert (
        await dnse_broker.market_data.quotes.get_price_trades(
            "ACB", from_time=1773182637, to_time=1773183637, board_id="G1"
        )
    ).source == "dnse"
    assert (
        await dnse_broker.market_data.quotes.get_close_price("HPG", board_id="G1")
    ).source == "dnse"
    assert (
        await dnse_broker.market_data.candles.get_candles(
            "ACB", "15", from_time=1773657310, to_time=1773830110, market_type="STOCK"
        )
    )[0].symbol == "ACB"

    dnse_server.assert_200_responses(7)
