from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Generic, TypeVar, cast

from vnbrokers.realtime.status import ConnectionStatus

T = TypeVar("T")
_SENTINEL = object()


class Subscription(Generic[T]):
    def events(self) -> AsyncIterator[T]:
        raise NotImplementedError

    def errors(self) -> AsyncIterator[Exception]:
        raise NotImplementedError

    def status(self) -> AsyncIterator[ConnectionStatus]:
        raise NotImplementedError

    async def close(self) -> None:
        raise NotImplementedError

    async def __aenter__(self) -> "Subscription[T]":
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        await self.close()


class QueueSubscription(Subscription[T]):
    def __init__(self, max_queue_size: int = 1024) -> None:
        self._events: asyncio.Queue[T | object] = asyncio.Queue(maxsize=max_queue_size)
        self._errors: asyncio.Queue[Exception | object] = asyncio.Queue(maxsize=max_queue_size)
        self._status: asyncio.Queue[ConnectionStatus | object] = asyncio.Queue(
            maxsize=max_queue_size
        )
        self._closed = False

    @property
    def closed(self) -> bool:
        return self._closed

    def publish_event(self, event: T) -> None:
        self._events.put_nowait(event)

    def publish_error(self, error: Exception) -> None:
        self._errors.put_nowait(error)

    def publish_status(self, status: ConnectionStatus) -> None:
        self._status.put_nowait(status)

    async def events(self) -> AsyncIterator[T]:
        while True:
            item = await self._events.get()
            if item is _SENTINEL:
                return
            yield cast(T, item)

    async def errors(self) -> AsyncIterator[Exception]:
        while True:
            item = await self._errors.get()
            if item is _SENTINEL:
                return
            if not isinstance(item, Exception):
                continue
            yield item

    async def status(self) -> AsyncIterator[ConnectionStatus]:
        while True:
            item = await self._status.get()
            if item is _SENTINEL:
                return
            if not isinstance(item, ConnectionStatus):
                continue
            yield item

    async def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._events.put_nowait(_SENTINEL)
        self._errors.put_nowait(_SENTINEL)
        self._status.put_nowait(ConnectionStatus.CLOSED)
        self._status.put_nowait(_SENTINEL)
