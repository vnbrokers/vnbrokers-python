from vnbrokers.errors.base import VnBrokerError


class RateLimitError(VnBrokerError):
    retry_after_seconds: float | None

    def __init__(
        self,
        message: str,
        *,
        broker: str | None = None,
        retry_after_seconds: float | None = None,
    ) -> None:
        super().__init__(message, broker=broker)
        self.retry_after_seconds = retry_after_seconds
