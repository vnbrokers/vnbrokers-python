from typing import Any

from vnbrokers.errors.base import VnBrokerError


class BrokerRejectedError(VnBrokerError):
    def __init__(
        self,
        message: str,
        *,
        broker: str | None = None,
        code: str | None = None,
        raw: Any = None,
    ) -> None:
        super().__init__(message, broker=broker, raw=raw)
        self.code = code
