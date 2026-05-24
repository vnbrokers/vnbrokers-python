from typing import Any

import pytest

from vnbrokers.brokers.dnse import DnseBroker


@pytest.mark.integration
@pytest.mark.asyncio
async def test_auth_endpoints_accept_200_responses(
    dnse_broker: DnseBroker, dnse_server: Any
) -> None:
    assert (await dnse_broker.auth.send_email_otp()).source == "dnse"
    assert (
        await dnse_broker.auth.get_trading_token(otp_type="EMAIL", passcode="123456")
    ).source == "dnse"

    dnse_server.assert_200_responses(2)
