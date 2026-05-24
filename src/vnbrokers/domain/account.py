from dataclasses import dataclass

from vnbrokers.domain.raw import RawPayload


@dataclass(frozen=True)
class Account:
    account_id: str
    broker: str
    display_name: str | None = None
    raw: RawPayload | None = None
