from dataclasses import dataclass


@dataclass(frozen=True)
class TracingMiddleware:
    service_name: str = "vnbrokers"
