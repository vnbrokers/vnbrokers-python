from dataclasses import dataclass


@dataclass(frozen=True)
class BrokerConfig:
    base_url: str | None = None
    stream_url: str | None = None
    timeout_seconds: float = 30.0
