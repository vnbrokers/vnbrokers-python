from dataclasses import dataclass


@dataclass(frozen=True)
class ReconnectPolicy:
    enabled: bool = False
    max_attempts: int = 3
    initial_delay_seconds: float = 1.0
    max_delay_seconds: float = 30.0
