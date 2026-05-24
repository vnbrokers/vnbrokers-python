from dataclasses import dataclass


@dataclass(frozen=True)
class LoggingMiddleware:
    logger_name: str = "vnbrokers"
