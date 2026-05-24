from dataclasses import dataclass


@dataclass(frozen=True)
class MetricsMiddleware:
    namespace: str = "vnbrokers"
