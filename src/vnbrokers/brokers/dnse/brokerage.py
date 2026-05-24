from vnbrokers.brokers.dnse.config import DnseConfig
from vnbrokers.brokers.dnse.trading import _api_headers, _base_url, _expect_object, _send_request
from vnbrokers.core.broker import BrokerBase
from vnbrokers.core.capability import Capability
from vnbrokers.domain.raw import RawPayload
from vnbrokers.transport.http import HttpRequest, HttpTransport


class DnseBrokerageService:
    def __init__(self, broker: BrokerBase, config: DnseConfig, transport: HttpTransport) -> None:
        self._broker = broker
        self._config = config
        self._transport = transport

    async def get_care_by_accounts(self, *, version: str = "2026-05-07") -> RawPayload:
        self._broker.require_capability(Capability.BROKERAGE_CARE_BY)
        headers = _api_headers(self._config)
        headers["version"] = version
        response = await _send_request(
            self._config,
            self._transport,
            HttpRequest(
                method="GET",
                url=f"{_base_url(self._config)}/brokers/accounts/care-by",
                headers=headers,
            ),
        )
        return RawPayload(source="dnse", data=_expect_object(response.body))
