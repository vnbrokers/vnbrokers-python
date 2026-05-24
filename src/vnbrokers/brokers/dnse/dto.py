from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DnseOrderDTO:
    id: int | str
    account_no: str
    symbol: str
    side: str | None
    order_type: str | None
    order_status: str | None
    quantity: int | float | str | None
    price: int | float | str | None
    raw: Any


@dataclass(frozen=True)
class DnseOrderEventDTO:
    account_id: str | None
    order_id: str
    symbol: str | None
    status: str | None
    filled_quantity: str | None
    received_at: str | None
    raw: Any
