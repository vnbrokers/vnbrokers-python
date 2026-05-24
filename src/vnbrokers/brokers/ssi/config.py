from dataclasses import dataclass

from vnbrokers.core.config import BrokerConfig


@dataclass(frozen=True)
class SsiConfig(BrokerConfig):
    api_key: str | None = None
    api_secret: str | None = None
