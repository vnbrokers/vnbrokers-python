from typing import Any

from vnbrokers.brokers.dnse.config import DnseConfig
from vnbrokers.core.broker import BrokerBase
from vnbrokers.core.capability import Capability
from vnbrokers.brokers.dnse.dto import DnseOrderEventDTO
from vnbrokers.brokers.dnse.mapper import map_order_event, map_position
from vnbrokers.brokers.dnse import realtime as dnse_realtime
from vnbrokers.domain.order_event import OrderEvent
from vnbrokers.domain.position import Position
from vnbrokers.realtime.subscription import QueueSubscription, Subscription
from vnbrokers.trading.realtime import SubscribeOrdersRequest, SubscribePositionsRequest
from vnbrokers.transport.websocket import WebSocketTransportFactory


class DnseTradingRealtimeService:
    def __init__(
        self,
        broker: BrokerBase,
        config: DnseConfig,
        websocket_transport_factory: WebSocketTransportFactory,
    ) -> None:
        self._broker = broker
        self._config = config
        self._websocket_transport_factory = websocket_transport_factory

    async def subscribe_orders(
        self,
        request: SubscribeOrdersRequest,
    ) -> Subscription[OrderEvent]:
        self._broker.require_capability(Capability.TRADING_REALTIME_ORDERS)
        return dnse_realtime.start_dnse_realtime_subscription(
            config=self._config,
            websocket_transport_factory=self._websocket_transport_factory,
            subscribe_message=build_stream_subscribe_orders_message(
                market_type=request.market_type,
                encoding=self._config.stream_encoding,
            ),
            publisher=publish_order_stream_message,
            should_publish=_is_trading_stream_payload,
        )

    async def subscribe_positions(
        self,
        request: SubscribePositionsRequest,
    ) -> Subscription[Position]:
        self._broker.require_capability(Capability.TRADING_REALTIME_POSITIONS)
        return dnse_realtime.start_dnse_realtime_subscription(
            config=self._config,
            websocket_transport_factory=self._websocket_transport_factory,
            subscribe_message=build_stream_subscribe_positions_message(
                market_type=request.market_type,
                encoding=self._config.stream_encoding,
            ),
            publisher=publish_position_stream_message,
            should_publish=_is_trading_stream_payload,
        )


def build_stream_subscribe_orders_message(
    market_type: str = "STOCK",
    encoding: str = "json",
) -> dict[str, object]:
    return {
        "action": "subscribe",
        "channels": [{"name": f"order.{market_type}.{encoding}", "symbols": []}],
    }


def build_stream_auth_message(
    *,
    api_key: str,
    api_secret: str,
    timestamp: int | None = None,
    nonce: str | None = None,
) -> dict[str, object]:
    return dnse_realtime.build_stream_auth_message(
        api_key=api_key,
        api_secret=api_secret,
        timestamp=timestamp,
        nonce=nonce,
    )


def build_stream_subscribe_positions_message(
    market_type: str = "STOCK",
    encoding: str = "json",
) -> dict[str, object]:
    return {
        "action": "subscribe",
        "channels": [{"name": f"position.{market_type}.{encoding}", "symbols": []}],
    }


def decode_order_stream_message(message: dict[str, Any]) -> OrderEvent:
    data = _message_data(message)
    dto = DnseOrderEventDTO(
        account_id=_optional_str(data.get("accountNo")),
        order_id=str(data.get("id") or data.get("orderId") or ""),
        symbol=_optional_str(data.get("symbol")),
        status=_optional_str(data.get("orderStatus")),
        filled_quantity=_optional_str(data.get("fillQuantity")),
        received_at=_optional_str(data.get("createdDate") or data.get("modifiedDate")),
        raw=message,
    )
    return map_order_event(dto)


def decode_position_stream_message(message: dict[str, Any]) -> Position:
    return map_position(_message_data(message))


def publish_order_stream_message(
    subscription: QueueSubscription[OrderEvent],
    message: dict[str, Any],
) -> None:
    subscription.publish_event(decode_order_stream_message(message))


def publish_position_stream_message(
    subscription: QueueSubscription[Position],
    message: dict[str, Any],
) -> None:
    subscription.publish_event(decode_position_stream_message(message))


def _message_data(message: dict[str, Any]) -> dict[str, Any]:
    data = message.get("data")
    if isinstance(data, dict):
        return data
    event_type = message.get("T")
    if event_type == "eo":
        order = message.get("order")
        if isinstance(order, dict):
            return order
    if event_type == "ep":
        position = message.get("position")
        if isinstance(position, dict):
            return position
    order = message.get("order")
    if isinstance(order, dict):
        return order
    position = message.get("position")
    if isinstance(position, dict):
        return position
    return message


def _is_trading_stream_payload(message: dict[str, Any]) -> bool:
    event_type = message.get("T")
    if event_type == "eo":
        return isinstance(message.get("order"), dict)
    if event_type == "ep":
        return isinstance(message.get("position"), dict)
    data = _message_data(message)
    return "accountNo" in data and ("id" in data or "orderId" in data or "symbol" in data)


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    return str(value)
