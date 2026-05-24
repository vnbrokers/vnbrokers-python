from typing import Any

import pytest

from vnbrokers.brokers.dnse import DnseBroker


@pytest.mark.integration
@pytest.mark.asyncio
async def test_brokerage_endpoints_accept_200_responses(
    dnse_broker: DnseBroker, dnse_server: Any
) -> None:
    payload = await dnse_broker.brokerage.get_care_by_accounts()

    assert payload.source == "dnse"
    dnse_server.assert_200_responses(1)
