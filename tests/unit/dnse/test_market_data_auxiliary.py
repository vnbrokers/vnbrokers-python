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
async def test_get_security_definition_builds_secdef_request() -> None:
    transport = FakeTransport(
        [
            HttpResponse(
                status_code=200,
                headers={},
                body=[
                    {
                        "marketId": "STO",
                        "boardId": "G1",
                        "symbol": "HPG",
                        "listingDate": "2007-11-15",
                    }
                ],
            )
        ]
    )
    broker = DnseBroker(
        DnseConfig(base_url="https://api.dnse.example", api_key="key", api_secret="secret"),
        http_transport=transport,
    )

    payload = await broker.market_data.symbols.get_security_definition("HPG", board_id="G1")

    sent = transport.requests[0]
    assert sent.method == "GET"
    assert sent.url == "https://api.dnse.example/price/HPG/secdef?boardId=G1"
    assert sent.headers["X-API-Key"] == "key"
    assert "X-Signature" in sent.headers
    assert payload.source == "dnse"
    assert payload.data[0]["symbol"] == "HPG"


@pytest.mark.asyncio
async def test_get_price_trades_builds_trades_request() -> None:
    transport = FakeTransport(
        [
            HttpResponse(
                status_code=200,
                headers={},
                body={"trades": [{"price": 23000}], "nextPageToken": "next-token"},
            )
        ]
    )
    broker = DnseBroker(
        DnseConfig(base_url="https://api.dnse.example", api_key="key"), http_transport=transport
    )

    payload = await broker.market_data.quotes.get_price_trades(
        "ACB", from_time=1773182637, to_time=1773183637, board_id="G1", limit=1000
    )

    assert transport.requests[0].method == "GET"
    assert transport.requests[0].url == (
        "https://api.dnse.example/price/ACB/trades"
        "?boardId=G1&from=1773182637&to=1773183637&limit=1000"
    )
    assert payload.data["nextPageToken"] == "next-token"


@pytest.mark.asyncio
async def test_get_close_price_builds_close_price_request() -> None:
    transport = FakeTransport(
        [
            HttpResponse(
                status_code=200,
                headers={},
                body={
                    "prices": [
                        {
                            "marketId": "STO",
                            "boardId": "G1",
                            "symbol": "HPG",
                            "closePrice": 26.8,
                            "time": "2026-04-08 02:14:59",
                        }
                    ]
                },
            )
        ]
    )
    broker = DnseBroker(
        DnseConfig(base_url="https://api.dnse.example", api_key="key"), http_transport=transport
    )

    payload = await broker.market_data.quotes.get_close_price("HPG", board_id="G1")

    assert transport.requests[0].method == "GET"
    assert transport.requests[0].url == "https://api.dnse.example/price/HPG/close?boardId=G1"
    assert payload.source == "dnse"
    assert payload.data["prices"][0]["closePrice"] == 26.8


@pytest.mark.asyncio
async def test_get_working_dates_builds_market_request() -> None:
    transport = FakeTransport(
        [
            HttpResponse(
                status_code=200,
                headers={},
                body={"workingDates": ["2026-04-16"]},
            )
        ]
    )
    broker = DnseBroker(
        DnseConfig(base_url="https://api.dnse.example", api_key="key"), http_transport=transport
    )

    payload = await broker.market_data.symbols.get_working_dates()

    assert transport.requests[0].method == "GET"
    assert transport.requests[0].url == "https://api.dnse.example/market/working-dates"
    assert payload.data["workingDates"] == ["2026-04-16"]


@pytest.mark.asyncio
async def test_market_data_auxiliary_raises_broker_rejected_error() -> None:
    transport = FakeTransport(
        [
            HttpResponse(
                status_code=400,
                headers={},
                body={"code": "MD-002", "message": "Bad market data request"},
            )
        ]
    )
    broker = DnseBroker(
        DnseConfig(base_url="https://api.dnse.example", api_key="key"), http_transport=transport
    )

    with pytest.raises(BrokerRejectedError) as exc:
        await broker.market_data.symbols.get_working_dates()

    assert exc.value.broker == "dnse"
    assert exc.value.code == "MD-002"
