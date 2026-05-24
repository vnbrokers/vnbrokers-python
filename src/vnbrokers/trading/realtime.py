from dataclasses import dataclass
from typing import Protocol

from vnbrokers.domain.order_event import OrderEvent
from vnbrokers.domain.position import Position
from vnbrokers.realtime.subscription import Subscription


@dataclass(frozen=True)
class SubscribeOrdersRequest:
    account_id: str
    market_type: str = "STOCK"


@dataclass(frozen=True)
class SubscribePositionsRequest:
    account_id: str
    market_type: str = "STOCK"


class TradingRealtimeService(Protocol):
    async def subscribe_orders(
        self,
        request: SubscribeOrdersRequest,
    ) -> Subscription[OrderEvent]:
        raise NotImplementedError

    async def subscribe_positions(
        self,
        request: SubscribePositionsRequest,
    ) -> Subscription[Position]:
        raise NotImplementedError
