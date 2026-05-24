from collections.abc import Callable
from decimal import Decimal
from typing import Any, TypeVar

from vnbrokers.brokers.dnse.config import DnseConfig
from vnbrokers.brokers.dnse.realtime import start_dnse_realtime_subscription
from vnbrokers.core.broker import BrokerBase
from vnbrokers.core.capability import Capability
from vnbrokers.domain.candle import Candle
from vnbrokers.domain.raw import RawPayload
from vnbrokers.domain.tick import Tick
from vnbrokers.domain.top_price import TopPrice
from vnbrokers.market_data.realtime import SubscribeSymbolRequest
from vnbrokers.realtime.subscription import QueueSubscription, Subscription
from vnbrokers.transport.websocket import WebSocketTransportFactory

_T = TypeVar("_T")


class DnseMarketDataRealtimeService:
    def __init__(
        self,
        broker: BrokerBase,
        config: DnseConfig,
        websocket_transport_factory: WebSocketTransportFactory,
    ) -> None:
        self._broker = broker
        self._config = config
        self._websocket_transport_factory = websocket_transport_factory

    async def subscribe_ticks(self, request: SubscribeSymbolRequest) -> Subscription[Tick]:
        self._broker.require_capability(Capability.MARKETDATA_REALTIME_TICKS)
        return _start_market_data_subscription(
            config=self._config,
            websocket_transport_factory=self._websocket_transport_factory,
            channel=build_market_data_channel(
                "tick",
                board_id=self._config.market_data_board_id,
                encoding=self._config.stream_encoding,
            ),
            symbols=request.symbol_list(),
            publisher=publish_tick_stream_message,
        )

    async def subscribe_top_price(self, request: SubscribeSymbolRequest) -> Subscription[TopPrice]:
        self._broker.require_capability(Capability.MARKETDATA_REALTIME_TOP_PRICE)
        return _start_market_data_subscription(
            config=self._config,
            websocket_transport_factory=self._websocket_transport_factory,
            channel=build_market_data_channel(
                "top_price",
                board_id=self._config.market_data_board_id,
                encoding=self._config.stream_encoding,
            ),
            symbols=request.symbol_list(),
            publisher=publish_top_price_stream_message,
        )

    async def subscribe_candles(
        self,
        request: SubscribeSymbolRequest,
        interval: str,
    ) -> Subscription[Candle]:
        self._broker.require_capability(Capability.MARKETDATA_REALTIME_CANDLES)
        return _start_market_data_subscription(
            config=self._config,
            websocket_transport_factory=self._websocket_transport_factory,
            channel=build_market_data_channel(
                "ohlc",
                resolution=interval,
                encoding=self._config.stream_encoding,
            ),
            symbols=request.symbol_list(),
            publisher=publish_candle_stream_message,
        )

    async def subscribe_closed_candles(
        self,
        request: SubscribeSymbolRequest,
        interval: str,
    ) -> Subscription[Candle]:
        self._broker.require_capability(Capability.MARKETDATA_REALTIME_CANDLES)
        return _start_market_data_subscription(
            config=self._config,
            websocket_transport_factory=self._websocket_transport_factory,
            channel=build_market_data_channel(
                "ohlc_closed",
                resolution=interval,
                encoding=self._config.stream_encoding,
            ),
            symbols=request.symbol_list(),
            publisher=publish_candle_stream_message,
        )

    async def subscribe_tick_extra(
        self,
        request: SubscribeSymbolRequest,
    ) -> Subscription[RawPayload]:
        return self._subscribe_board_raw("tick_extra", request)

    async def subscribe_expected_price(
        self,
        request: SubscribeSymbolRequest,
    ) -> Subscription[RawPayload]:
        return self._subscribe_board_raw("expected_price", request)

    async def subscribe_foreign(
        self,
        request: SubscribeSymbolRequest,
    ) -> Subscription[RawPayload]:
        return self._subscribe_board_raw("foreign", request)

    async def subscribe_security_definition(
        self,
        request: SubscribeSymbolRequest,
    ) -> Subscription[RawPayload]:
        return self._subscribe_board_raw("security_definition", request)

    async def subscribe_market_index(self, index_name: str) -> Subscription[RawPayload]:
        self._broker.require_capability(Capability.MARKETDATA_REALTIME_RAW)
        return _start_market_data_subscription(
            config=self._config,
            websocket_transport_factory=self._websocket_transport_factory,
            channel=build_market_data_channel(
                "market_index",
                index_name=index_name,
                encoding=self._config.stream_encoding,
            ),
            symbols=None,
            publisher=publish_raw_stream_message,
        )

    async def subscribe_raw_channel(
        self,
        channel: str,
        symbols: list[str] | None = None,
    ) -> Subscription[RawPayload]:
        self._broker.require_capability(Capability.MARKETDATA_REALTIME_RAW)
        return _start_market_data_subscription(
            config=self._config,
            websocket_transport_factory=self._websocket_transport_factory,
            channel=channel,
            symbols=symbols,
            publisher=publish_raw_stream_message,
        )

    def _subscribe_board_raw(
        self,
        kind: str,
        request: SubscribeSymbolRequest,
    ) -> Subscription[RawPayload]:
        self._broker.require_capability(Capability.MARKETDATA_REALTIME_RAW)
        return _start_market_data_subscription(
            config=self._config,
            websocket_transport_factory=self._websocket_transport_factory,
            channel=build_market_data_channel(
                kind,
                board_id=self._config.market_data_board_id,
                encoding=self._config.stream_encoding,
            ),
            symbols=request.symbol_list(),
            publisher=publish_raw_stream_message,
        )


def build_market_data_channel(
    kind: str,
    *,
    board_id: str | None = None,
    resolution: str | None = None,
    index_name: str | None = None,
    encoding: str = "json",
) -> str:
    if kind in {
        "tick",
        "tick_extra",
        "top_price",
        "expected_price",
        "security_definition",
        "foreign",
    }:
        return f"{kind}.{board_id or 'G1'}.{encoding}"
    if kind in {"ohlc", "ohlc_closed"}:
        if resolution is None:
            raise ValueError(f"{kind} channel requires resolution")
        return f"{kind}.{resolution}.{encoding}"
    if kind == "market_index":
        if index_name is None:
            raise ValueError("market_index channel requires index_name")
        return f"market_index.{index_name}.{encoding}"
    raise ValueError(f"Unsupported DNSE market data stream channel kind: {kind}")


def build_market_data_subscribe_message(
    channel: str, symbols: list[str] | None = None
) -> dict[str, object]:
    return _market_data_subscription_message("subscribe", channel, symbols)


def build_market_data_unsubscribe_message(
    channel: str, symbols: list[str] | None = None
) -> dict[str, object]:
    return _market_data_subscription_message("unsubscribe", channel, symbols)


def build_stream_ping_message() -> dict[str, str]:
    return {"action": "ping"}


def decode_tick_stream_message(message: dict[str, Any]) -> Tick:
    data = _message_data(message)
    return Tick(
        symbol=_required_str(data.get("symbol"), "symbol"),
        price=_decimal(data.get("matchPrice")),
        quantity=_optional_decimal(data.get("matchQtty")),
        received_at=_optional_str(data.get("sendingTime") or data.get("multicastReceiveTime")),
        raw=RawPayload(source="dnse", data=message),
    )


def decode_top_price_stream_message(message: dict[str, Any]) -> TopPrice:
    data = _message_data(message)
    bid = _first_price_level(data.get("bid"))
    offer = _first_price_level(data.get("offer"))
    return TopPrice(
        symbol=_required_str(data.get("symbol"), "symbol"),
        bid_price=_optional_decimal(bid.get("price")),
        bid_quantity=_optional_decimal(bid.get("qtty")),
        ask_price=_optional_decimal(offer.get("price")),
        ask_quantity=_optional_decimal(offer.get("qtty")),
        received_at=_optional_str(data.get("sendingTime") or data.get("multicastReceiveTime")),
        raw=RawPayload(source="dnse", data=message),
    )


def decode_candle_stream_message(message: dict[str, Any]) -> Candle:
    data = _message_data(message)
    return Candle(
        symbol=_required_str(data.get("symbol"), "symbol"),
        interval=_required_str(data.get("resolution"), "resolution"),
        opened_at=str(data.get("time") or ""),
        open=_decimal(data.get("open")),
        high=_decimal(data.get("high")),
        low=_decimal(data.get("low")),
        close=_decimal(data.get("close")),
        volume=_decimal(data.get("volume")),
        raw=RawPayload(source="dnse", data=message),
    )


def decode_market_data_raw_message(message: dict[str, Any]) -> RawPayload:
    return RawPayload(source="dnse", data=message)


def publish_tick_stream_message(
    subscription: QueueSubscription[Tick],
    message: dict[str, Any],
) -> None:
    subscription.publish_event(decode_tick_stream_message(message))


def publish_top_price_stream_message(
    subscription: QueueSubscription[TopPrice],
    message: dict[str, Any],
) -> None:
    subscription.publish_event(decode_top_price_stream_message(message))


def publish_candle_stream_message(
    subscription: QueueSubscription[Candle],
    message: dict[str, Any],
) -> None:
    subscription.publish_event(decode_candle_stream_message(message))


def publish_raw_stream_message(
    subscription: QueueSubscription[RawPayload],
    message: dict[str, Any],
) -> None:
    subscription.publish_event(decode_market_data_raw_message(message))


def _start_market_data_subscription(
    *,
    config: DnseConfig,
    websocket_transport_factory: WebSocketTransportFactory,
    channel: str,
    symbols: list[str] | None,
    publisher: Callable[[QueueSubscription[_T], dict[str, Any]], None],
) -> Subscription[_T]:
    return start_dnse_realtime_subscription(
        config=config,
        websocket_transport_factory=websocket_transport_factory,
        subscribe_message=build_market_data_subscribe_message(channel, symbols),
        publisher=publisher,
        should_publish=_is_market_data_payload,
    )


def _is_market_data_payload(message: dict[str, Any]) -> bool:
    data = message.get("data")
    if isinstance(data, dict):
        return "T" in data or "symbol" in data
    return "T" in message or "symbol" in message


def _market_data_subscription_message(
    action: str, channel: str, symbols: list[str] | None
) -> dict[str, object]:
    channel_payload: dict[str, object] = {"name": channel}
    if symbols is not None:
        channel_payload["symbols"] = symbols
    return {"action": action, "channels": [channel_payload]}


def _message_data(message: dict[str, Any]) -> dict[str, Any]:
    data = message.get("data")
    if isinstance(data, dict):
        return data
    return message


def _first_price_level(value: Any) -> dict[str, Any]:
    if isinstance(value, list) and value and isinstance(value[0], dict):
        return value[0]
    return {}


def _decimal(value: Any) -> Decimal:
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


def _optional_decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    return _decimal(value)


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _required_str(value: Any, name: str) -> str:
    if value is None:
        raise ValueError(f"DNSE market data stream payload must include {name}")
    return str(value)
