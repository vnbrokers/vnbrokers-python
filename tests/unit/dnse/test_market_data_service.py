import pytest

from vnbrokers.brokers.dnse import DnseBroker, DnseConfig
from vnbrokers.errors.broker_rejected import BrokerRejectedError
from vnbrokers.transport.http import HttpRequest, HttpResponse


class FakeTransport:
    def __init__(self, responses: list[HttpResponse]) -> None:
        self.responses = responses
        self.requests: list[HttpRequest] = []

    async def send(self, request: HttpRequest) -> HttpResponse:
        self.requests.append(request)
        return self.responses.pop(0)


@pytest.mark.asyncio
async def test_list_symbols_builds_signed_instruments_request() -> None:
    transport = FakeTransport(
        [
            HttpResponse(
                status_code=200,
                headers={},
                body={
                    "data": [{"symbol": "ACB", "marketId": "STO", "name": "Ngan hang TMCP A Chau"}],
                    "total": 1,
                    "page": 1,
                    "pageSize": 10,
                },
            )
        ]
    )
    broker = DnseBroker(
        DnseConfig(base_url="https://api.dnse.example", api_key="key", api_secret="secret"),
        http_transport=transport,
    )

    symbols = await broker.market_data.symbols.list_symbols(symbol="ACB", limit=10)

    sent = transport.requests[0]
    assert sent.method == "GET"
    assert sent.url == "https://api.dnse.example/instruments?symbol=ACB&limit=10"
    assert sent.headers["X-API-Key"] == "key"
    assert "X-Aux-Date" in sent.headers
    assert "X-Signature" in sent.headers
    assert symbols[0].symbol == "ACB"


@pytest.mark.asyncio
async def test_get_quote_builds_latest_trade_request() -> None:
    transport = FakeTransport(
        [
            HttpResponse(
                status_code=200,
                headers={},
                body={"trades": [{"price": 23000, "quantity": 1000, "time": 1773183637}]},
            )
        ]
    )
    broker = DnseBroker(
        DnseConfig(base_url="https://api.dnse.example", api_key="key"), http_transport=transport
    )

    quote = await broker.market_data.quotes.get_quote("ACB", board_id="G1")

    assert transport.requests[0].method == "GET"
    assert (
        transport.requests[0].url == "https://api.dnse.example/price/ACB/trades/latest?boardId=G1"
    )
    assert quote.symbol == "ACB"
    assert str(quote.last_price) == "23000"


@pytest.mark.asyncio
async def test_get_candles_builds_ohlc_request_with_explicit_range() -> None:
    transport = FakeTransport(
        [
            HttpResponse(
                status_code=200,
                headers={},
                body={
                    "t": [1773657310],
                    "o": [23000],
                    "h": [23200],
                    "l": [22900],
                    "c": [23100],
                    "v": [100000],
                    "nextTime": 1773831010,
                },
            )
        ]
    )
    broker = DnseBroker(
        DnseConfig(base_url="https://api.dnse.example", api_key="key"), http_transport=transport
    )

    candles = await broker.market_data.candles.get_candles(
        "ACB", "15", from_time=1773657310, to_time=1773830110, market_type="STOCK"
    )

    assert transport.requests[0].method == "GET"
    assert transport.requests[0].url == (
        "https://api.dnse.example/price/ohlc?symbol=ACB&type=STOCK&resolution=15"
        "&from=1773657310&to=1773830110"
    )
    assert candles[0].close == 23100


@pytest.mark.asyncio
async def test_market_data_query_raises_broker_rejected_error() -> None:
    transport = FakeTransport(
        [
            HttpResponse(
                status_code=400,
                headers={},
                body={"code": "MD-001", "message": "Bad market data request"},
            )
        ]
    )
    broker = DnseBroker(
        DnseConfig(base_url="https://api.dnse.example", api_key="key"), http_transport=transport
    )

    with pytest.raises(BrokerRejectedError) as exc:
        await broker.market_data.symbols.list_symbols(symbol="BAD")

    assert exc.value.broker == "dnse"
    assert exc.value.code == "MD-001"
