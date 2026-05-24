from dataclasses import dataclass

from vnbrokers.core.config import BrokerConfig


@dataclass(frozen=True)
class TcbsConfig(BrokerConfig):
    token: str | None = None
