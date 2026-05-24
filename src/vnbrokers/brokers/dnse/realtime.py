import asyncio
import hashlib
import hmac
import json
import time
from collections.abc import Callable
from contextlib import suppress
from typing import Any, TypeVar, cast
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import msgpack  # type: ignore[import-untyped]

from vnbrokers.brokers.dnse.config import DnseConfig
from vnbrokers.errors.auth import AuthError
from vnbrokers.errors.decode import DecodeError
from vnbrokers.realtime.status import ConnectionStatus
from vnbrokers.realtime.subscription import QueueSubscription, Subscription
from vnbrokers.transport.websocket import (
    WebSocketMessage,
    WebSocketTransport,
    WebSocketTransportFactory,
)

_T = TypeVar("_T")
_DEFAULT_STREAM_URL = "wss://ws-openapi.dnse.com.vn/v1/stream?encoding=json"
_SUPPORTED_STREAM_ENCODINGS = {"json", "msgpack"}


def build_stream_auth_message(
    *,
    api_key: str,
    api_secret: str,
    timestamp: int | None = None,
    nonce: str | None = None,
) -> dict[str, object]:
    timestamp = int(time.time()) if timestamp is None else timestamp
    nonce = str(time.time_ns()) if nonce is None else nonce
    message = f"{api_key}:{timestamp}:{nonce}"
    signature = hmac.new(api_secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    return {
        "action": "auth",
        "api_key": api_key,
        "signature": signature,
        "timestamp": timestamp,
        "nonce": nonce,
    }


def start_dnse_realtime_subscription(
    *,
    config: DnseConfig,
    websocket_transport_factory: WebSocketTransportFactory,
    subscribe_message: dict[str, object],
    publisher: Callable[[QueueSubscription[_T], dict[str, Any]], None],
    should_publish: Callable[[dict[str, Any]], bool],
) -> Subscription[_T]:
    subscription = ManagedRealtimeSubscription[_T]()
    task = asyncio.create_task(
        _run_dnse_realtime_subscription(
            subscription=subscription,
            config=config,
            websocket_transport_factory=websocket_transport_factory,
            subscribe_message=subscribe_message,
            publisher=publisher,
            should_publish=should_publish,
        )
    )
    subscription.attach_task(task)
    return subscription


async def _run_dnse_realtime_subscription(
    *,
    subscription: "ManagedRealtimeSubscription[_T]",
    config: DnseConfig,
    websocket_transport_factory: WebSocketTransportFactory,
    subscribe_message: dict[str, object],
    publisher: Callable[[QueueSubscription[_T], dict[str, Any]], None],
    should_publish: Callable[[dict[str, Any]], bool],
) -> None:
    try:
        if config.api_key is None or config.api_secret is None:
            raise AuthError("DNSE realtime stream requires api_key and api_secret", broker="dnse")
        encoding = _stream_encoding(config)
        stream_url = _stream_url(config)
        subscription.publish_status(ConnectionStatus.CONNECTING)
        transport = await websocket_transport_factory(stream_url)
        subscription.attach_transport(transport)
        subscription.publish_status(ConnectionStatus.CONNECTED)
        subscription.publish_status(ConnectionStatus.AUTHENTICATING)
        await transport.send_text(
            _encode_stream_message(
                build_stream_auth_message(api_key=config.api_key, api_secret=config.api_secret),
                encoding,
            )
        )
        await transport.send_text(_encode_stream_message(subscribe_message, encoding))
        subscription.publish_status(ConnectionStatus.SUBSCRIBED)
        async for message_text in transport.receive_text():
            message = _decode_stream_message(message_text, encoding)
            if not isinstance(message, dict) or not should_publish(message):
                continue
            try:
                publisher(subscription, message)
            except Exception as exc:
                subscription.publish_error(
                    DecodeError(
                        f"Failed to decode DNSE realtime stream message: {exc}",
                        broker="dnse",
                        raw=message,
                    )
                )
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        subscription.publish_status(ConnectionStatus.FAILED)
        subscription.publish_error(exc)
    finally:
        await subscription.close()


class ManagedRealtimeSubscription(QueueSubscription[_T]):
    def __init__(self) -> None:
        super().__init__()
        self._task: asyncio.Task[None] | None = None
        self._transport: WebSocketTransport | None = None

    def attach_task(self, task: asyncio.Task[None]) -> None:
        self._task = task

    def attach_transport(self, transport: WebSocketTransport) -> None:
        self._transport = transport

    async def close(self) -> None:
        task = self._task
        if task is not None and task is not asyncio.current_task() and not task.done():
            task.cancel()
        if self._transport is not None:
            await self._transport.close()
        await super().close()
        if task is not None and task is not asyncio.current_task():
            with suppress(asyncio.CancelledError):
                await task


def _stream_encoding(config: DnseConfig) -> str:
    encoding = config.stream_encoding.strip().lower()
    if encoding not in _SUPPORTED_STREAM_ENCODINGS:
        supported = ", ".join(sorted(_SUPPORTED_STREAM_ENCODINGS))
        raise ValueError(
            f"Unsupported DNSE stream encoding: {config.stream_encoding}. Use {supported}."
        )
    return encoding


def _stream_url(config: DnseConfig) -> str:
    stream_url = config.stream_url or _DEFAULT_STREAM_URL
    encoding = _stream_encoding(config)
    parts = urlsplit(stream_url)
    query_items = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if key != "encoding"
    ]
    query_items.append(("encoding", encoding))
    return urlunsplit(
        (parts.scheme, parts.netloc, parts.path, urlencode(query_items), parts.fragment)
    )


def _encode_stream_message(message: dict[str, object], encoding: str) -> WebSocketMessage:
    if encoding == "json":
        return json.dumps(message)
    return cast(bytes, msgpack.packb(message, use_bin_type=True))


def _decode_stream_message(message: WebSocketMessage, encoding: str) -> Any:
    if encoding == "json":
        if isinstance(message, bytes):
            message = message.decode()
        return json.loads(message)
    payload = message if isinstance(message, bytes) else message.encode()
    return msgpack.unpackb(payload, raw=False)
