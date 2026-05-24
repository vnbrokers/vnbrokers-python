import pytest

from vnbrokers.brokers.dnse import DnseBroker, DnseConfig
from vnbrokers.errors.broker_rejected import BrokerRejectedError
from vnbrokers.transport.http import HttpRequest, HttpResponse


class FakeTransport:
    def __init__(self, responses: list[HttpResponse]) -> None:
        self.responses = responses
        self.requests: list[HttpRequest] = []

    async def send(self, request: HttpRequest) -> HttpResponse:
        self.requests.append(request)
        return self.responses.pop(0)


@pytest.mark.asyncio
async def test_get_care_by_accounts_builds_brokerage_request() -> None:
    transport = FakeTransport(
        [
            HttpResponse(
                status_code=200,
                headers={},
                body={
                    "careBy": [
                        {
                            "accountNo": "0335000633",
                            "fullName": "Hoang Tu Mai",
                            "totalNav": 54134802357,
                        }
                    ],
                    "total": 1,
                },
            )
        ]
    )
    broker = DnseBroker(
        DnseConfig(base_url="https://api.dnse.example", api_key="key", api_secret="secret"),
        http_transport=transport,
    )

    payload = await broker.brokerage.get_care_by_accounts()

    sent = transport.requests[0]
    assert sent.method == "GET"
    assert sent.url == "https://api.dnse.example/brokers/accounts/care-by"
    assert sent.headers["X-API-Key"] == "key"
    assert sent.headers["version"] == "2026-05-07"
    assert "X-Signature" in sent.headers
    assert payload.source == "dnse"
    assert payload.data["careBy"][0]["accountNo"] == "0335000633"


@pytest.mark.asyncio
async def test_get_care_by_accounts_allows_version_override() -> None:
    transport = FakeTransport([HttpResponse(status_code=200, headers={}, body={"careBy": []})])
    broker = DnseBroker(
        DnseConfig(base_url="https://api.dnse.example", api_key="key"), http_transport=transport
    )

    await broker.brokerage.get_care_by_accounts(version="2026-05-23")

    assert transport.requests[0].headers["version"] == "2026-05-23"


@pytest.mark.asyncio
async def test_get_care_by_accounts_raises_broker_rejected_error() -> None:
    transport = FakeTransport(
        [
            HttpResponse(
                status_code=400,
                headers={},
                body={"code": "BR-001", "message": "Bad broker request"},
            )
        ]
    )
    broker = DnseBroker(
        DnseConfig(base_url="https://api.dnse.example", api_key="key"), http_transport=transport
    )

    with pytest.raises(BrokerRejectedError) as exc:
        await broker.brokerage.get_care_by_accounts()

    assert exc.value.broker == "dnse"
    assert exc.value.code == "BR-001"
