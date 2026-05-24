import asyncio
import json
from collections.abc import AsyncIterator

import msgpack
import pytest

from vnbrokers.brokers.dnse import DnseBroker, DnseConfig
from vnbrokers.brokers.dnse.market_data_realtime import build_market_data_channel
from vnbrokers.market_data.realtime import SubscribeSymbolRequest
from vnbrokers.realtime.subscription import Subscription

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
async def test_subscribe_top_price_authenticates_subscribes_and_publishes_events() -> None:
    websocket = FakeWebSocketTransport(
        [
            {"action": "auth", "status": "ok"},
            {
                "T": "q",
                "symbol": "HPG",
                "bid": [{"price": 27.25, "qtty": 100}],
                "offer": [{"price": 27.3, "qtty": 200}],
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

    subscription = await broker.market_data.realtime.subscribe_top_price(
        SubscribeSymbolRequest(symbols=("HPG", "SSI"))
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
        "channels": [{"name": "top_price.G1.json", "symbols": ["HPG", "SSI"]}],
    }
    assert event.symbol == "HPG"
    assert str(event.bid_price) == "27.25"
    assert str(event.ask_price) == "27.3"
    assert websocket.closed


@pytest.mark.asyncio
async def test_subscribe_top_price_supports_msgpack_encoding() -> None:
    websocket = FakeWebSocketTransport(
        [
            msgpack.packb({"action": "auth", "status": "ok"}, use_bin_type=True),
            msgpack.packb(
                {
                    "T": "q",
                    "symbol": "HPG",
                    "bid": [{"price": 27.25, "qtty": 100}],
                    "offer": [{"price": 27.3, "qtty": 200}],
                },
                use_bin_type=True,
            ),
        ]
    )
    factory = FakeWebSocketFactory(websocket)
    broker = DnseBroker(
        DnseConfig(
            stream_url="wss://stream.dnse.example/v1/stream?foo=bar&encoding=json",
            stream_encoding="msgpack",
            api_key="key",
            api_secret="secret",
        ),
        websocket_transport_factory=factory,
    )

    subscription = await broker.market_data.realtime.subscribe_top_price(
        SubscribeSymbolRequest(symbol="HPG")
    )
    event = await asyncio.wait_for(anext(subscription.events()), timeout=1)
    await subscription.close()

    sent = [msgpack.unpackb(message, raw=False) for message in websocket.sent]
    assert factory.urls == ["wss://stream.dnse.example/v1/stream?foo=bar&encoding=msgpack"]
    assert sent[0]["action"] == "auth"
    assert sent[0]["api_key"] == "key"
    assert sent[1] == {
        "action": "subscribe",
        "channels": [{"name": "top_price.G1.msgpack", "symbols": ["HPG"]}],
    }
    assert event.symbol == "HPG"
    assert str(event.bid_price) == "27.25"


@pytest.mark.asyncio
async def test_subscribe_ticks_all_symbols_omits_symbols_field() -> None:
    websocket = FakeWebSocketTransport(
        [
            {"T": "t", "symbol": "HPG", "matchPrice": 27.3, "matchQtty": 10},
        ]
    )
    factory = FakeWebSocketFactory(websocket)
    broker = DnseBroker(
        DnseConfig(api_key="key", api_secret="secret"),
        websocket_transport_factory=factory,
    )

    subscription = await broker.market_data.realtime.subscribe_ticks(SubscribeSymbolRequest.all())
    event = await asyncio.wait_for(anext(subscription.events()), timeout=1)
    await subscription.close()

    sent = [json.loads(message) for message in websocket.sent]
    assert sent[1] == {
        "action": "subscribe",
        "channels": [{"name": "tick.G1.json"}],
    }
    assert event.symbol == "HPG"
    assert str(event.price) == "27.3"


@pytest.mark.asyncio
async def test_subscribe_candles_uses_ohlc_resolution_channel() -> None:
    websocket = FakeWebSocketTransport(
        [
            {
                "T": "b",
                "symbol": "HPG",
                "resolution": "1",
                "time": 1778472960,
                "open": 27.25,
                "high": 27.3,
                "low": 27.25,
                "close": 27.25,
                "volume": 2400,
            },
        ]
    )
    factory = FakeWebSocketFactory(websocket)
    broker = DnseBroker(
        DnseConfig(api_key="key", api_secret="secret"),
        websocket_transport_factory=factory,
    )

    subscription = await broker.market_data.realtime.subscribe_candles(
        SubscribeSymbolRequest(symbol="HPG"),
        interval="1",
    )
    event = await asyncio.wait_for(anext(subscription.events()), timeout=1)
    await subscription.close()

    sent = [json.loads(message) for message in websocket.sent]
    assert sent[1] == {
        "action": "subscribe",
        "channels": [{"name": "ohlc.1.json", "symbols": ["HPG"]}],
    }
    assert event.symbol == "HPG"
    assert event.interval == "1"


@pytest.mark.parametrize(
    ("method_name", "method_args", "incoming", "expected_channel"),
    [
        (
            "subscribe_tick_extra",
            (SubscribeSymbolRequest(symbol="HPG"),),
            {"symbol": "HPG", "price": 27.3, "avgPrice": 27.25},
            {"name": "tick_extra.G1.json", "symbols": ["HPG"]},
        ),
        (
            "subscribe_expected_price",
            (SubscribeSymbolRequest(symbol="HPG"),),
            {"symbol": "HPG", "expectedTradePrice": 27.3, "expectedTradeQuantity": 1000},
            {"name": "expected_price.G1.json", "symbols": ["HPG"]},
        ),
        (
            "subscribe_foreign",
            (SubscribeSymbolRequest(symbol="HPG"),),
            {"symbol": "HPG", "buyVolume": 1000, "sellVolume": 500},
            {"name": "foreign.G1.json", "symbols": ["HPG"]},
        ),
        (
            "subscribe_security_definition",
            (SubscribeSymbolRequest(symbol="HPG"),),
            {"symbol": "HPG", "basicPrice": 27.0, "ceilingPrice": 28.8},
            {"name": "security_definition.G1.json", "symbols": ["HPG"]},
        ),
        (
            "subscribe_market_index",
            ("VN30",),
            {"T": "mi", "indexName": "VN30", "valueIndexes": 1669.38},
            {"name": "market_index.VN30.json"},
        ),
    ],
)
@pytest.mark.asyncio
async def test_subscribe_remaining_dnse_v2_raw_market_data_streams(
    method_name: str,
    method_args: tuple[object, ...],
    incoming: dict[str, object],
    expected_channel: dict[str, object],
) -> None:
    websocket = FakeWebSocketTransport([incoming])
    factory = FakeWebSocketFactory(websocket)
    broker = DnseBroker(
        DnseConfig(api_key="key", api_secret="secret"),
        websocket_transport_factory=factory,
    )

    method = getattr(broker.market_data.realtime, method_name)
    subscription: Subscription = await method(*method_args)
    event = await asyncio.wait_for(anext(subscription.events()), timeout=1)
    await subscription.close()

    sent = [json.loads(message) for message in websocket.sent]
    assert sent[1] == {
        "action": "subscribe",
        "channels": [expected_channel],
    }
    assert event.source == "dnse"
    assert event.data == incoming


@pytest.mark.asyncio
async def test_subscribe_closed_candles_uses_ohlc_closed_resolution_channel() -> None:
    websocket = FakeWebSocketTransport(
        [
            {
                "symbol": "HPG",
                "resolution": "15",
                "time": 1757992500,
                "open": 30.4,
                "high": 30.4,
                "low": 30.25,
                "close": 30.3,
                "volume": 1398200,
            },
        ]
    )
    factory = FakeWebSocketFactory(websocket)
    broker = DnseBroker(
        DnseConfig(api_key="key", api_secret="secret"),
        websocket_transport_factory=factory,
    )

    subscription = await broker.market_data.realtime.subscribe_closed_candles(
        SubscribeSymbolRequest(symbol="HPG"),
        interval="15",
    )
    event = await asyncio.wait_for(anext(subscription.events()), timeout=1)
    await subscription.close()

    sent = [json.loads(message) for message in websocket.sent]
    assert sent[1] == {
        "action": "subscribe",
        "channels": [{"name": "ohlc_closed.15.json", "symbols": ["HPG"]}],
    }
    assert event.symbol == "HPG"
    assert event.interval == "15"
    assert str(event.close) == "30.3"


@pytest.mark.asyncio
async def test_subscribe_raw_channel_covers_other_market_data_streams() -> None:
    websocket = FakeWebSocketTransport(
        [
            {"T": "mi", "indexName": "VNINDEX", "valueIndexes": 1669.38},
        ]
    )
    factory = FakeWebSocketFactory(websocket)
    broker = DnseBroker(
        DnseConfig(api_key="key", api_secret="secret"),
        websocket_transport_factory=factory,
    )

    subscription = await broker.market_data.realtime.subscribe_raw_channel(
        build_market_data_channel("market_index", index_name="VN30")
    )
    event = await asyncio.wait_for(anext(subscription.events()), timeout=1)
    await subscription.close()

    sent = [json.loads(message) for message in websocket.sent]
    assert sent[1] == {
        "action": "subscribe",
        "channels": [{"name": "market_index.VN30.json"}],
    }
    assert event.source == "dnse"
    assert event.data["indexName"] == "VNINDEX"
