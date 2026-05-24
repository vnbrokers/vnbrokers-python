from dataclasses import dataclass
from decimal import Decimal

from vnbrokers.domain.raw import RawPayload


@dataclass(frozen=True)
class Balance:
    account_id: str
    cash_available: Decimal | None = None
    cash_total: Decimal | None = None
    buying_power: Decimal | None = None
    currency: str = "VND"
    raw: RawPayload | None = None
