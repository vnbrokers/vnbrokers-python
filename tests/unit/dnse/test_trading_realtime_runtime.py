import asyncio
import json
from collections.abc import AsyncIterator

import msgpack
import pytest

from vnbrokers.brokers.dnse import DnseBroker, DnseConfig
from vnbrokers.domain.enums import OrderStatus
from vnbrokers.trading.realtime import SubscribeOrdersRequest, SubscribePositionsRequest

StreamPayload = dict[str, object] | str | bytes


class FakeWebSocketTransport:
    def __init__(self, incoming: list[StreamPayload]) -> None:
        self.incoming = incoming
        self.sent: list[str | bytes] = []
        self.closed = False

    async def send_text(self, message: str | bytes) -> None:
        self.sent.append(message)

    async def receive_text(self) -> AsyncIterator[str | bytes]:
        for message in self.incoming:
            if isinstance(message, dict):
                yield json.dumps(message)
            else:
                yield message

    async def close(self) -> None:
        self.closed = True


class FakeWebSocketFactory:
    def __init__(self, transport: FakeWebSocketTransport) -> None:
        self.transport = transport
        self.urls: list[str] = []

    async def __call__(self, url: str) -> FakeWebSocketTransport:
        self.urls.append(url)
        return self.transport


@pytest.mark.asyncio
async def test_subscribe_orders_authenticates_subscribes_and_publishes_events() -> None:
    websocket = FakeWebSocketTransport(
        [
            {"action": "auth", "status": "ok"},
            {
                "T": "eo",
                "action": "order_update",
                "event": "canceled",
                "order": {
                    "id": 596,
                    "accountNo": "0001179019",
                    "symbol": "41I1G5000",
                    "orderStatus": "Canceled",
                    "fillQuantity": 0,
                    "createdDate": "2026-04-13T04:24:05.274Z",
                },
                "sequence": 8,
            },
        ]
    )
    factory = FakeWebSocketFactory(websocket)
    broker = DnseBroker(
        DnseConfig(
            stream_url="wss://stream.dnse.example/v1/stream?encoding=json",
            api_key="key",
            api_secret="secret",
        ),
        websocket_transport_factory=factory,
    )

    subscription = await broker.trading.realtime.subscribe_orders(
        SubscribeOrdersRequest(account_id="0001179019", market_type="STOCK")
    )
    event = await asyncio.wait_for(anext(subscription.events()), timeout=1)
    await subscription.close()

    sent = [json.loads(message) for message in websocket.sent]
    assert factory.urls == ["wss://stream.dnse.example/v1/stream?encoding=json"]
    assert sent[0]["action"] == "auth"
    assert sent[0]["api_key"] == "key"
    assert "signature" in sent[0]
    assert sent[1] == {
        "action": "subscribe",
        "channels": [{"name": "order.STOCK.json", "symbols": []}],
    }
    assert event.account_id == "0001179019"
    assert event.order_id == "596"
    assert event.status == OrderStatus.CANCELLED
    assert websocket.closed


@pytest.mark.asyncio
async def test_subscribe_orders_supports_msgpack_encoding() -> None:
    websocket = FakeWebSocketTransport(
        [
            msgpack.packb({"action": "auth", "status": "ok"}, use_bin_type=True),
            msgpack.packb(
                {
                    "T": "eo",
                    "action": "order_update",
                    "order": {
                        "id": 596,
                        "accountNo": "0001179019",
                        "symbol": "41I1G5000",
                        "orderStatus": "Canceled",
                        "fillQuantity": 0,
                    },
                },
                use_bin_type=True,
            ),
        ]
    )
    factory = FakeWebSocketFactory(websocket)
    broker = DnseBroker(
        DnseConfig(
            stream_url="wss://stream.dnse.example/v1/stream?encoding=json",
            stream_encoding="msgpack",
            api_key="key",
            api_secret="secret",
        ),
        websocket_transport_factory=factory,
    )

    subscription = await broker.trading.realtime.subscribe_orders(
        SubscribeOrdersRequest(account_id="0001179019", market_type="STOCK")
    )
    event = await asyncio.wait_for(anext(subscription.events()), timeout=1)
    await subscription.close()

    sent = [msgpack.unpackb(message, raw=False) for message in websocket.sent]
    assert factory.urls == ["wss://stream.dnse.example/v1/stream?encoding=msgpack"]
    assert sent[0]["action"] == "auth"
    assert sent[1] == {
        "action": "subscribe",
        "channels": [{"name": "order.STOCK.msgpack", "symbols": []}],
    }
    assert event.account_id == "0001179019"
    assert event.status == OrderStatus.CANCELLED


@pytest.mark.asyncio
async def test_subscribe_positions_uses_position_market_type_channel() -> None:
    websocket = FakeWebSocketTransport(
        [
            {
                "id": 177796763592657,
                "marketType": "DERIVATIVE",
                "symbol": "41I1G5000",
                "accountNo": "0001179019",
                "openQuantity": 23,
                "costPrice": 2036.78986,
                "marketPrice": 1915.8,
            },
        ]
    )
    factory = FakeWebSocketFactory(websocket)
    broker = DnseBroker(
        DnseConfig(api_key="key", api_secret="secret"),
        websocket_transport_factory=factory,
    )

    subscription = await broker.trading.realtime.subscribe_positions(
        SubscribePositionsRequest(account_id="0001179019", market_type="DERIVATIVE")
    )
    event = await asyncio.wait_for(anext(subscription.events()), timeout=1)
    await subscription.close()

    sent = [json.loads(message) for message in websocket.sent]
    assert sent[1] == {
        "action": "subscribe",
        "channels": [{"name": "position.DERIVATIVE.json", "symbols": []}],
    }
    assert event.account_id == "0001179019"
    assert event.symbol == "41I1G5000"
