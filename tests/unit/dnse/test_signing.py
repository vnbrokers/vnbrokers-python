from datetime import datetime, timezone

from vnbrokers.brokers.dnse.auth import DnseSigner
from vnbrokers.transport.http import HttpRequest


def test_dnse_signer_adds_hmac_signature_headers() -> None:
    signer = DnseSigner(
        api_key="key",
        api_secret="secret",
        now=lambda: datetime(2024, 10, 2, 7, 44, 2, tzinfo=timezone.utc),
        nonce=lambda: "abc123",
    )
    request = HttpRequest(
        method="POST", url="https://api.dnse.example/accounts/orders?marketType=DERIVATIVE"
    )

    signed = signer.sign(request)

    assert signed.headers["X-API-Key"] == "key"
    assert signed.headers["X-Aux-Date"] == "Wed, 02 Oct 2024 07:44:02 +0000"
    assert signed.headers["X-Signature"] == (
        'Signature keyId="key",algorithm="hmac-sha256",'
        'headers="(request-target) x-aux-date",'
        'signature="TGoPDEvWPw8PKV8Ev8hTQcrCls%2FFZ7eWdx5uwc0oIMg%3D",'
        'nonce="abc123"'
    )
