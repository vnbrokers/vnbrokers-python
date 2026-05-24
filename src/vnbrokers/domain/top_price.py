from dataclasses import dataclass
from decimal import Decimal

from vnbrokers.domain.raw import RawPayload


@dataclass(frozen=True)
class TopPrice:
    symbol: str
    bid_price: Decimal | None = None
    bid_quantity: Decimal | None = None
    ask_price: Decimal | None = None
    ask_quantity: Decimal | None = None
    received_at: str | None = None
    raw: RawPayload | None = None
