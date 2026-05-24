from dataclasses import dataclass
from decimal import Decimal

from vnbrokers.domain.raw import RawPayload


@dataclass(frozen=True)
class Candle:
    symbol: str
    interval: str
    opened_at: str
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    raw: RawPayload | None = None
