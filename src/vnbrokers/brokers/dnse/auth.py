import base64
import hashlib
import hmac
import secrets
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import quote, urlsplit

from vnbrokers.auth.hmac import HmacSigner
from vnbrokers.brokers.dnse.config import DnseConfig
from vnbrokers.domain.raw import RawPayload
from vnbrokers.errors.broker_rejected import BrokerRejectedError
from vnbrokers.transport.http import HttpRequest, HttpResponse, HttpTransport


def _default_now() -> datetime:
    return datetime.now(timezone.utc)


def _default_nonce() -> str:
    return secrets.token_hex(16)


@dataclass(frozen=True)
class DnseSigner:
    api_key: str
    api_secret: str
    now: Callable[[], datetime] = _default_now
    nonce: Callable[[], str] = _default_nonce

    def sign(self, request: HttpRequest) -> HttpRequest:
        date = self.now().astimezone(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
        nonce = self.nonce()
        path = urlsplit(request.url).path or "/"
        signing_string = (
            f"(request-target): {request.method.lower()} {path}\nx-aux-date: {date}\nnonce: {nonce}"
        )
        digest = hmac.new(
            self.api_secret.encode("utf-8"),
            signing_string.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        signature = quote(base64.b64encode(digest).decode("ascii"), safe="")
        headers = dict(request.headers)
        headers["X-API-Key"] = self.api_key
        headers["X-Aux-Date"] = date
        headers["X-Signature"] = (
            f'Signature keyId="{self.api_key}",algorithm="hmac-sha256",'
            f'headers="(request-target) x-aux-date",signature="{signature}",nonce="{nonce}"'
        )
        return HttpRequest(
            method=request.method, url=request.url, headers=headers, json=request.json
        )


@dataclass(frozen=True)
class DnseAuth:
    config: DnseConfig

    def legacy_signer(self) -> HmacSigner | None:
        if self.config.api_key is None or self.config.api_secret is None:
            return None
        return HmacSigner(api_key=self.config.api_key, api_secret=self.config.api_secret)

    def signer(self) -> DnseSigner | None:
        if self.config.api_key is None or self.config.api_secret is None:
            return None
        return DnseSigner(api_key=self.config.api_key, api_secret=self.config.api_secret)


class DnseAuthService:
    def __init__(self, config: DnseConfig, transport: HttpTransport) -> None:
        self._config = config
        self._transport = transport

    async def send_email_otp(self) -> RawPayload:
        response = await self._send(
            HttpRequest(
                method="POST",
                url=f"{self._base_url()}/registration/send-email-otp",
                headers=self._headers(),
            )
        )
        return RawPayload(source="dnse", data=_expect_object(response.body))

    async def get_trading_token(self, *, otp_type: str, passcode: str) -> RawPayload:
        response = await self._send(
            HttpRequest(
                method="POST",
                url=f"{self._base_url()}/registration/trading-token",
                headers=self._headers(include_content_type=True),
                json={"otpType": otp_type, "passcode": passcode},
            )
        )
        return RawPayload(source="dnse", data=_expect_object(response.body))

    def _base_url(self) -> str:
        return (self._config.base_url or "https://openapi.dnse.com.vn").rstrip("/")

    def _headers(self, *, include_content_type: bool = False) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self._config.api_key:
            headers["X-API-Key"] = self._config.api_key
        if include_content_type:
            headers["Content-Type"] = "application/json"
        return headers

    async def _send(self, request: HttpRequest) -> HttpResponse:
        signer = DnseAuth(self._config).signer()
        if signer is not None:
            request = signer.sign(request)
        response = await self._transport.send(request)
        if response.status_code >= 400:
            body = response.body if isinstance(response.body, dict) else {}
            raise BrokerRejectedError(
                str(
                    body.get("message") or f"DNSE request failed with status {response.status_code}"
                ),
                broker="dnse",
                code=str(body.get("code")) if body.get("code") is not None else None,
                raw=response.body,
            )
        return response


def _expect_object(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise TypeError("Expected DNSE response body to be a JSON object")
    return value
