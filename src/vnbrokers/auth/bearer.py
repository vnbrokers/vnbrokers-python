from dataclasses import dataclass

from vnbrokers.auth.token_provider import TokenProvider
from vnbrokers.transport.http import HttpRequest


@dataclass(frozen=True)
class BearerTokenAuth:
    token_provider: TokenProvider

    async def authorize(self, request: HttpRequest) -> HttpRequest:
        headers = dict(request.headers)
        headers["Authorization"] = f"Bearer {await self.token_provider.get_token()}"
        return HttpRequest(
            method=request.method,
            url=request.url,
            headers=headers,
            json=request.json,
        )
