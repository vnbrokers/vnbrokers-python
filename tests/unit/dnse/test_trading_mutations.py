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
async def test_send_email_otp_builds_dnse_registration_request() -> None:
    transport = FakeTransport([HttpResponse(status_code=200, headers={}, body={})])
    broker = DnseBroker(
        DnseConfig(base_url="https://api.dnse.example", api_key="key", api_secret="secret"),
        http_transport=transport,
    )

    payload = await broker.auth.send_email_otp()

    sent = transport.requests[0]
    assert sent.method == "POST"
    assert sent.url == "https://api.dnse.example/registration/send-email-otp"
    assert sent.headers["X-API-Key"] == "key"
    assert "X-Signature" in sent.headers
    assert payload.source == "dnse"
    assert payload.data == {}


@pytest.mark.asyncio
async def test_get_trading_token_posts_otp_credentials() -> None:
    transport = FakeTransport(
        [
            HttpResponse(
                status_code=200,
                headers={},
                body={"tradingToken": "dnse-trading-token"},
            )
        ]
    )
    broker = DnseBroker(
        DnseConfig(base_url="https://api.dnse.example", api_key="key"), http_transport=transport
    )

    payload = await broker.auth.get_trading_token(otp_type="EMAIL", passcode="123456")

    sent = transport.requests[0]
    assert sent.method == "POST"
    assert sent.url == "https://api.dnse.example/registration/trading-token"
    assert sent.headers["Content-Type"] == "application/json"
    assert sent.json == {"otpType": "EMAIL", "passcode": "123456"}
    assert payload.data["tradingToken"] == "dnse-trading-token"


@pytest.mark.asyncio
async def test_update_order_builds_put_request_with_trading_token() -> None:
    transport = FakeTransport(
        [
            HttpResponse(
                status_code=200,
                headers={},
                body={"id": 42, "accountNo": "0001179019", "price": 23100, "quantity": 200},
            )
        ]
    )
    broker = DnseBroker(
        DnseConfig(
            base_url="https://api.dnse.example",
            api_key="key",
            trading_token="trade-token",
            market_type="STOCK",
        ),
        http_transport=transport,
    )

    payload = await broker.trading.orders.update_order(
        "0001179019", "42", price=Decimal("23100"), quantity=200
    )

    sent = transport.requests[0]
    assert sent.method == "PUT"
    assert sent.url == (
        "https://api.dnse.example/accounts/0001179019/orders/42"
        "?marketType=STOCK&orderCategory=NORMAL"
    )
    assert sent.headers["trading-token"] == "trade-token"
    assert sent.headers["Content-Type"] == "application/json"
    assert sent.json == {"price": 23100, "quantity": 200}
    assert payload.data["quantity"] == 200


@pytest.mark.asyncio
async def test_close_position_builds_post_request_with_trading_token() -> None:
    transport = FakeTransport(
        [
            HttpResponse(
                status_code=200,
                headers={},
                body={"id": 42, "symbol": "VN30F2505", "quantity": 10},
            )
        ]
    )
    broker = DnseBroker(
        DnseConfig(
            base_url="https://api.dnse.example",
            api_key="key",
            trading_token="trade-token",
        ),
        http_transport=transport,
    )

    payload = await broker.trading.positions.close_position("2183078")

    sent = transport.requests[0]
    assert sent.method == "POST"
    assert sent.url == (
        "https://api.dnse.example/accounts/positions/2183078/close?marketType=DERIVATIVE"
    )
    assert sent.headers["trading-token"] == "trade-token"
    assert payload.data["symbol"] == "VN30F2505"


@pytest.mark.asyncio
async def test_trading_mutation_raises_broker_rejected_error() -> None:
    transport = FakeTransport(
        [
            HttpResponse(
                status_code=400,
                headers={},
                body={"code": "TR-001", "message": "Bad trading request"},
            )
        ]
    )
    broker = DnseBroker(
        DnseConfig(base_url="https://api.dnse.example", api_key="key"), http_transport=transport
    )

    with pytest.raises(BrokerRejectedError) as exc:
        await broker.auth.send_email_otp()

    assert exc.value.broker == "dnse"
    assert exc.value.code == "TR-001"
