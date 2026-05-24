from dataclasses import dataclass


@dataclass(frozen=True)
class RateLimitMiddleware:
    requests_per_second: float
