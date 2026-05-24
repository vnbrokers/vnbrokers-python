from dataclasses import dataclass
from decimal import Decimal

from vnbrokers.domain.enums import OrderSide, OrderStatus, OrderType, TimeInForce
from vnbrokers.domain.raw import RawPayload


@dataclass(frozen=True)
class Order:
    broker: str
    account_id: str
    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    status: OrderStatus
    price: Decimal | None = None
    raw: RawPayload | None = None


@dataclass(frozen=True)
class PlaceOrderRequest:
    account_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    price: Decimal | None = None
    time_in_force: TimeInForce = TimeInForce.DAY


@dataclass(frozen=True)
class PlaceOrderResponse:
    order_id: str
    status: OrderStatus
    raw: RawPayload | None = None
