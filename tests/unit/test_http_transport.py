from typing import Any

import pytest

from vnbrokers.transport.http import HttpRequest, HttpxTransport


class FakeResponse:
    status_code = 200
    headers = {"Content-Type": "application/json"}

    def json(self) -> dict[str, str]:
        return {"ok": "true"}


@pytest.mark.asyncio
async def test_httpx_transport_follows_redirects(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, Any]] = []

    class FakeAsyncClient:
        async def __aenter__(self) -> "FakeAsyncClient":
            return self

        async def __aexit__(self, *args: object) -> None:
            return None

        async def request(self, *args: object, **kwargs: Any) -> FakeResponse:
            calls.append(kwargs)
            return FakeResponse()

    import httpx

    monkeypatch.setattr(httpx, "AsyncClient", FakeAsyncClient)

    response = await HttpxTransport().send(HttpRequest(method="GET", url="https://example.test"))

    assert response.status_code == 200
    assert calls[0]["follow_redirects"] is True
