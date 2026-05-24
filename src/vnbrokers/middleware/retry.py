from dataclasses import dataclass


@dataclass(frozen=True)
class RetryMiddleware:
    max_attempts: int = 3
