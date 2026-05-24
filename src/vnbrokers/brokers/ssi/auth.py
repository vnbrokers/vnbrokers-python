from dataclasses import dataclass

from vnbrokers.brokers.ssi.config import SsiConfig


@dataclass(frozen=True)
class SsiAuth:
    config: SsiConfig
