from decimal import Decimal
from typing import Any

import pytest

from vnbrokers.brokers.dnse import DnseBroker


@pytest.mark.integration
@pytest.mark.asyncio
async def test_trading_account_endpoints_accept_200_responses(
    dnse_broker: DnseBroker, dnse_server: Any
) -> None:
    assert (await dnse_broker.trading.accounts.list_accounts())[0].broker == "dnse"
    assert (await dnse_broker.trading.accounts.get_balance("0001179019")).account_id == (
        "0001179019"
    )
    assert (await dnse_broker.trading.accounts.list_orders("0001179019"))[0].broker == "dnse"
    assert (
        await dnse_broker.trading.accounts.list_order_history(
            "0001179019", from_date="2026-05-01", to_date="2026-05-23"
        )
    )[0].broker == "dnse"
    assert (await dnse_broker.trading.accounts.get_executions("0001179019", "42")).source == "dnse"
    assert (
        await dnse_broker.trading.accounts.get_ppse(
            "0001179019", symbol="ACB", price=Decimal("23000"), loan_package_id=1769
        )
    ).source == "dnse"
    assert (
        await dnse_broker.trading.accounts.get_loan_packages("0001179019", symbol="ACB")
    ).source == "dnse"

    dnse_server.assert_200_responses(7)
