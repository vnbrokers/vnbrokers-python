from collections.abc import AsyncIterator
from typing import Any, Protocol


class SignalRTransport(Protocol):
    async def invoke(self, method: str, *args: Any) -> Any:
        raise NotImplementedError

    async def stream(self, method: str, *args: Any) -> AsyncIterator[Any]:
        raise NotImplementedError
