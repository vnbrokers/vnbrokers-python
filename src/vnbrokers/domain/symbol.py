from dataclasses import dataclass

from vnbrokers.domain.raw import RawPayload


@dataclass(frozen=True)
class Symbol:
    symbol: str
    exchange: str | None = None
    display_name: str | None = None
    raw: RawPayload | None = None
