from decimal import Decimal

import pytest

from vnbrokers.brokers.dnse import DnseBroker, DnseConfig
from vnbrokers.domain.enums import OrderSide, OrderStatus, OrderType
from vnbrokers.domain.order import PlaceOrderRequest
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
async def test_place_order_builds_signed_dnse_request() -> None:
    transport = FakeTransport(
        [
            HttpResponse(
                status_code=200,
                headers={"Content-Type": "application/json"},
                body={
                    "id": 116,
                    "symbol": "VN30F2506",
                    "side": "NB",
                    "orderType": "LO",
                    "orderStatus": "FILLED",
                    "price": 1200.5,
                    "quantity": 2,
                    "accountNo": "000123",
                    "marketType": "DERIVATIVE",
                    "orderCategory": "NORMAL",
                },
            )
        ]
    )
    broker = DnseBroker(
        DnseConfig(
            base_url="https://api.dnse.example",
            api_key="key",
            api_secret="secret",
            trading_token="trade-token",
            loan_package_id=1775,
        ),
        http_transport=transport,
    )

    response = await broker.trading.orders.place_order(
        PlaceOrderRequest(
            account_id="000123",
            symbol="VN30F2506",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("2"),
            price=Decimal("1200.5"),
        )
    )

    sent = transport.requests[0]
    assert sent.method == "POST"
    assert (
        sent.url
        == "https://api.dnse.example/accounts/orders?marketType=DERIVATIVE&orderCategory=NORMAL"
    )
    assert sent.headers["X-API-Key"] == "key"
    assert sent.headers["trading-token"] == "trade-token"
    assert sent.json == {
        "accountNo": "000123",
        "loanPackageId": 1775,
        "orderType": "LO",
        "price": 1200.5,
        "quantity": 2,
        "side": "NB",
        "symbol": "VN30F2506",
    }
    assert response.order_id == "116"
    assert response.status == OrderStatus.FILLED


@pytest.mark.asyncio
async def test_get_order_maps_dnse_response() -> None:
    transport = FakeTransport(
        [
            HttpResponse(
                status_code=200,
                headers={},
                body={
                    "id": 116,
                    "side": "NS",
                    "accountNo": "000123",
                    "symbol": "VN30F2506",
                    "price": 1201.0,
                    "quantity": 1,
                    "orderType": "LO",
                    "orderStatus": "PENDING",
                },
            )
        ]
    )
    broker = DnseBroker(
        DnseConfig(base_url="https://api.dnse.example", api_key="key"), http_transport=transport
    )

    order = await broker.trading.orders.get_order("000123", "116")

    assert transport.requests[0].method == "GET"
    assert transport.requests[0].url == (
        "https://api.dnse.example/accounts/000123/orders/116?marketType=DERIVATIVE&orderCategory=NORMAL"
    )
    assert order.order_id == "116"
    assert order.side == OrderSide.SELL


@pytest.mark.asyncio
async def test_cancel_order_raises_broker_rejected_error() -> None:
    transport = FakeTransport(
        [
            HttpResponse(
                status_code=400,
                headers={},
                body={"code": "OA-003", "message": "Thong tin nhap khong hop le", "status": 400},
            )
        ]
    )
    broker = DnseBroker(
        DnseConfig(
            base_url="https://api.dnse.example",
            api_key="key",
            api_secret="secret",
            trading_token="trade-token",
        ),
        http_transport=transport,
    )

    with pytest.raises(BrokerRejectedError) as exc:
        await broker.trading.orders.cancel_order("000123", "116")

    assert exc.value.broker == "dnse"
    assert exc.value.code == "OA-003"
