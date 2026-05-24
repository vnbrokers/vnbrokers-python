from dataclasses import dataclass
from decimal import Decimal

from vnbrokers.domain.raw import RawPayload


@dataclass(frozen=True)
class Tick:
    symbol: str
    price: Decimal
    quantity: Decimal | None = None
    received_at: str | None = None
    raw: RawPayload | None = None
