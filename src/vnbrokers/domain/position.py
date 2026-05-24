from dataclasses import dataclass
from decimal import Decimal

from vnbrokers.domain.raw import RawPayload


@dataclass(frozen=True)
class Position:
    account_id: str
    symbol: str
    quantity: Decimal
    available_quantity: Decimal | None = None
    average_price: Decimal | None = None
    market_value: Decimal | None = None
    raw: RawPayload | None = None
