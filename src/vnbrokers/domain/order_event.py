from dataclasses import dataclass

from vnbrokers.domain.enums import OrderStatus
from vnbrokers.domain.raw import RawPayload


@dataclass(frozen=True)
class OrderEvent:
    broker: str
    account_id: str | None
    order_id: str
    symbol: str | None
    status: OrderStatus
    raw_status: str | None
    filled_quantity: str | None
    received_at: str | None
    raw: RawPayload
