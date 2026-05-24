from collections.abc import AsyncIterator
from typing import Protocol


class MqttTransport(Protocol):
    async def publish(self, topic: str, payload: bytes) -> None:
        raise NotImplementedError

    async def subscribe(self, topic: str) -> AsyncIterator[bytes]:
        raise NotImplementedError
