from decimal import Decimal

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
async def test_list_orders_builds_account_orders_request() -> None:
    transport = FakeTransport(
        [
            HttpResponse(
                status_code=200,
                headers={},
                body={
                    "orders": [
                        {
                            "id": 42,
                            "side": "NB",
                            "accountNo": "0001179019",
                            "symbol": "VN30F2505",
                            "price": 1300.5,
                            "quantity": 10,
                            "orderType": "LO",
                            "orderStatus": "PARTIALLY_FILLED",
                        }
                    ]
                },
            )
        ]
    )
    broker = DnseBroker(
        DnseConfig(base_url="https://api.dnse.example", api_key="key", api_secret="secret"),
        http_transport=transport,
    )

    orders = await broker.trading.accounts.list_orders("0001179019")

    sent = transport.requests[0]
    assert sent.method == "GET"
    assert sent.url == (
        "https://api.dnse.example/accounts/0001179019/orders"
        "?marketType=DERIVATIVE&orderCategory=NORMAL"
    )
    assert sent.headers["X-API-Key"] == "key"
    assert "X-Signature" in sent.headers
    assert orders[0].order_id == "42"


@pytest.mark.asyncio
async def test_list_order_history_builds_history_request() -> None:
    transport = FakeTransport(
        [
            HttpResponse(
                status_code=200,
                headers={},
                body={
                    "data": [
                        {
                            "id": "42",
                            "side": "NB",
                            "accountNo": "0001179019",
                            "symbol": "VN30F2505",
                            "quantity": 10,
                            "orderType": "LO",
                            "orderStatus": "FILLED",
                        }
                    ]
                },
            )
        ]
    )
    broker = DnseBroker(
        DnseConfig(base_url="https://api.dnse.example", api_key="key"), http_transport=transport
    )

    orders = await broker.trading.accounts.list_order_history(
        "0001179019", from_date="2026-05-01", to_date="2026-05-23", page_index=1
    )

    assert transport.requests[0].method == "GET"
    assert transport.requests[0].url == (
        "https://api.dnse.example/accounts/0001179019/orders/history"
        "?marketType=DERIVATIVE&from=2026-05-01&to=2026-05-23&pageIndex=1"
    )
    assert orders[0].order_id == "42"


@pytest.mark.asyncio
async def test_get_executions_returns_raw_payload() -> None:
    transport = FakeTransport(
        [
            HttpResponse(
                status_code=200,
                headers={},
                body={"id": 42, "reports": [{"execId": "E1"}]},
            )
        ]
    )
    broker = DnseBroker(
        DnseConfig(base_url="https://api.dnse.example", api_key="key"), http_transport=transport
    )

    payload = await broker.trading.accounts.get_executions("0001179019", "42")

    assert transport.requests[0].url == (
        "https://api.dnse.example/accounts/0001179019/executions/42"
        "?marketType=DERIVATIVE&orderCategory=NORMAL"
    )
    assert payload.source == "dnse"
    assert payload.data["reports"][0]["execId"] == "E1"


@pytest.mark.asyncio
async def test_get_ppse_and_loan_packages_return_raw_payloads() -> None:
    transport = FakeTransport(
        [
            HttpResponse(
                status_code=200,
                headers={},
                body={"qmaxBuy": 1209, "qmaxSell": 700, "price": 23000},
            ),
            HttpResponse(
                status_code=200,
                headers={},
                body={"symbol": "ACB", "marketType": "STOCK", "loanPackages": [{"id": 1769}]},
            ),
        ]
    )
    broker = DnseBroker(
        DnseConfig(base_url="https://api.dnse.example", api_key="key", market_type="STOCK"),
        http_transport=transport,
    )

    ppse = await broker.trading.accounts.get_ppse(
        "0001179019", symbol="ACB", price=Decimal("23000"), loan_package_id=1769
    )
    loan_packages = await broker.trading.accounts.get_loan_packages("0001179019", symbol="ACB")

    assert transport.requests[0].url == (
        "https://api.dnse.example/accounts/0001179019/ppse"
        "?marketType=STOCK&symbol=ACB&loanPackageId=1769&price=23000"
    )
    assert ppse.data["qmaxBuy"] == 1209
    assert transport.requests[1].url == (
        "https://api.dnse.example/accounts/0001179019/loan-packages?marketType=STOCK&symbol=ACB"
    )
    assert loan_packages.data["loanPackages"][0]["id"] == 1769


@pytest.mark.asyncio
async def test_get_position_builds_position_by_id_request() -> None:
    transport = FakeTransport(
        [
            HttpResponse(
                status_code=200,
                headers={},
                body={
                    "id": 177796763592657,
                    "symbol": "41I1G5000",
                    "accountNo": "0001179019",
                    "openQuantity": 23,
                    "costPrice": 2036.78986,
                    "marketPrice": 1915.8,
                },
            )
        ]
    )
    broker = DnseBroker(
        DnseConfig(base_url="https://api.dnse.example", api_key="key"), http_transport=transport
    )

    position = await broker.trading.positions.get_position("177796763592657")

    assert transport.requests[0].method == "GET"
    assert transport.requests[0].url == (
        "https://api.dnse.example/accounts/positions/177796763592657?marketType=DERIVATIVE"
    )
    assert position.symbol == "41I1G5000"


@pytest.mark.asyncio
async def test_get_position_unwraps_data_response() -> None:
    transport = FakeTransport(
        [
            HttpResponse(
                status_code=200,
                headers={},
                body={
                    "data": {
                        "id": 177410795472387,
                        "symbol": "41I1G4000",
                        "accountNo": "0001179019",
                        "openQuantity": 1,
                        "averageCostPrice": 1834.5,
                        "marketPrice": 1706.1,
                    }
                },
            )
        ]
    )
    broker = DnseBroker(
        DnseConfig(base_url="https://api.dnse.example", api_key="key"), http_transport=transport
    )

    position = await broker.trading.positions.get_position("177410795472387")

    assert transport.requests[0].url == (
        "https://api.dnse.example/accounts/positions/177410795472387?marketType=DERIVATIVE"
    )
    assert position.account_id == "0001179019"
    assert position.symbol == "41I1G4000"
    assert str(position.average_price) == "1834.5"


@pytest.mark.asyncio
async def test_account_auxiliary_query_raises_broker_rejected_error() -> None:
    transport = FakeTransport(
        [
            HttpResponse(
                status_code=400,
                headers={},
                body={"code": "ACC-001", "message": "Bad account query"},
            )
        ]
    )
    broker = DnseBroker(
        DnseConfig(base_url="https://api.dnse.example", api_key="key"), http_transport=transport
    )

    with pytest.raises(BrokerRejectedError) as exc:
        await broker.trading.accounts.list_orders("0001179019")

    assert exc.value.broker == "dnse"
    assert exc.value.code == "ACC-001"
