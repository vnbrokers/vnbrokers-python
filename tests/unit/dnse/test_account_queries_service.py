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
async def test_list_accounts_builds_signed_dnse_request() -> None:
    transport = FakeTransport(
        [
            HttpResponse(
                status_code=200,
                headers={},
                body={
                    "name": "Nguyen Van A",
                    "custodyCode": "064C000123",
                    "investorId": "INV123",
                    "accounts": [{"id": "000123"}],
                },
            )
        ]
    )
    broker = DnseBroker(
        DnseConfig(base_url="https://api.dnse.example", api_key="key", api_secret="secret"),
        http_transport=transport,
    )

    accounts = await broker.trading.accounts.list_accounts()

    sent = transport.requests[0]
    assert sent.method == "GET"
    assert sent.url == "https://api.dnse.example/accounts"
    assert sent.headers["X-API-Key"] == "key"
    assert "X-Aux-Date" in sent.headers
    assert "X-Signature" in sent.headers
    assert accounts[0].account_id == "000123"


@pytest.mark.asyncio
async def test_get_balance_maps_dnse_response() -> None:
    transport = FakeTransport(
        [
            HttpResponse(
                status_code=200,
                headers={},
                body={"stock": {"totalCash": 1000, "availableCash": 700}},
            )
        ]
    )
    broker = DnseBroker(
        DnseConfig(base_url="https://api.dnse.example", api_key="key"), http_transport=transport
    )

    balance = await broker.trading.accounts.get_balance("000 123")

    assert transport.requests[0].method == "GET"
    assert transport.requests[0].url == "https://api.dnse.example/accounts/000%20123/balances"
    assert balance.account_id == "000 123"
    assert str(balance.cash_available) == "700"


@pytest.mark.asyncio
async def test_list_positions_uses_market_type_and_page_size() -> None:
    transport = FakeTransport(
        [
            HttpResponse(
                status_code=200,
                headers={},
                body={
                    "positions": [
                        {
                            "accountNo": "000123D",
                            "symbol": "VN30F2506",
                            "openQuantity": 2,
                            "costPrice": 1200,
                            "marketPrice": 1210,
                        }
                    ],
                    "total": 1,
                },
            )
        ]
    )
    broker = DnseBroker(
        DnseConfig(
            base_url="https://api.dnse.example",
            api_key="key",
            market_type="STOCK",
            positions_page_size=50,
        ),
        http_transport=transport,
    )

    positions = await broker.trading.positions.list_positions("000123D")

    assert transport.requests[0].method == "GET"
    assert transport.requests[0].url == (
        "https://api.dnse.example/accounts/000123D/positions?marketType=STOCK&pageSize=50"
    )
    assert positions[0].symbol == "VN30F2506"


@pytest.mark.asyncio
async def test_account_query_raises_broker_rejected_error() -> None:
    transport = FakeTransport(
        [
            HttpResponse(
                status_code=403,
                headers={},
                body={"code": "AUTH-001", "message": "Forbidden"},
            )
        ]
    )
    broker = DnseBroker(
        DnseConfig(base_url="https://api.dnse.example", api_key="key"), http_transport=transport
    )

    with pytest.raises(BrokerRejectedError) as exc:
        await broker.trading.accounts.list_accounts()

    assert exc.value.broker == "dnse"
    assert exc.value.code == "AUTH-001"
