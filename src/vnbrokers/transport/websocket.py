from collections.abc import AsyncIterator
from collections.abc import Awaitable, Callable
from typing import Any, Protocol

import websockets

WebSocketMessage = str | bytes


class WebSocketTransport(Protocol):
    async def send_text(self, message: WebSocketMessage) -> None:
        raise NotImplementedError

    def receive_text(self) -> AsyncIterator[WebSocketMessage]:
        raise NotImplementedError

    async def close(self) -> None:
        raise NotImplementedError


WebSocketTransportFactory = Callable[[str], Awaitable[WebSocketTransport]]


class WebsocketsTransport:
    def __init__(self, connection: Any) -> None:
        self._connection = connection

    @classmethod
    async def connect(cls, url: str) -> WebSocketTransport:
        return cls(await websockets.connect(url))

    async def send_text(self, message: WebSocketMessage) -> None:
        await self._connection.send(message)

    async def receive_text(self) -> AsyncIterator[WebSocketMessage]:
        async for message in self._connection:
            if isinstance(message, bytes):
                yield message
            else:
                yield str(message)

    async def close(self) -> None:
        await self._connection.close()
