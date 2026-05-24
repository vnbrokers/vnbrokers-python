from typing import Any


class VnBrokerError(Exception):
    def __init__(
        self,
        message: str,
        *,
        broker: str | None = None,
        raw: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.broker = broker
        self.raw = raw
