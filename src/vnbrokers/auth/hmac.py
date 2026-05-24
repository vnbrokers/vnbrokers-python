from dataclasses import dataclass

from vnbrokers.auth.signer import Signer
from vnbrokers.transport.http import HttpRequest


@dataclass(frozen=True)
class HmacSigner(Signer):
    api_key: str
    api_secret: str

    def sign(self, request: HttpRequest) -> HttpRequest:
        headers = dict(request.headers)
        headers["X-API-Key"] = self.api_key
        return HttpRequest(
            method=request.method,
            url=request.url,
            headers=headers,
            json=request.json,
        )
