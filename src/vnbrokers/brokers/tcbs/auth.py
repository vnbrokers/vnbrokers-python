from dataclasses import dataclass

from vnbrokers.brokers.tcbs.config import TcbsConfig


@dataclass(frozen=True)
class TcbsAuth:
    config: TcbsConfig
