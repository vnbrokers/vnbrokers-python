from dataclasses import dataclass
from decimal import Decimal

from vnbrokers.domain.raw import RawPayload


@dataclass(frozen=True)
class Quote:
    symbol: str
    last_price: Decimal | None = None
    bid_price: Decimal | None = None
    ask_price: Decimal | None = None
    received_at: str | None = None
    raw: RawPayload | None = None
