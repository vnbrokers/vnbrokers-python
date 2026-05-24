from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class HttpRequest:
    method: str
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    json: Any = None


@dataclass(frozen=True)
class HttpResponse:
    status_code: int
    headers: dict[str, str]
    body: Any


class HttpTransport(Protocol):
    async def send(self, request: HttpRequest) -> HttpResponse:
        raise NotImplementedError


class HttpxTransport:
    async def send(self, request: HttpRequest) -> HttpResponse:
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.request(
                request.method,
                request.url,
                headers=request.headers,
                json=request.json,
                follow_redirects=True,
            )
        try:
            body = response.json()
        except ValueError:
            body = response.text
        return HttpResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            body=body,
        )
