import os

import pytest

from vnbrokers.brokers.dnse import DnseBroker, DnseConfig


pytestmark = pytest.mark.skipif(
    os.getenv("VNBROKERS_LIVE") != "1",
    reason="set VNBROKERS_LIVE=1 to run DNSE live read tests",
)


def _broker() -> DnseBroker:
    api_key = os.getenv("DNSE_API_KEY")
    if not api_key:
        pytest.skip("DNSE_API_KEY is required for DNSE live read tests")
    return DnseBroker(
        DnseConfig(
            base_url=os.getenv("DNSE_BASE_URL") or "https://openapi.dnse.com.vn",
            api_key=api_key,
            api_secret=os.getenv("DNSE_API_SECRET"),
            market_type=os.getenv("DNSE_MARKET_TYPE") or "DERIVATIVE",
        )
    )


async def _account_id(broker: DnseBroker) -> str:
    configured = os.getenv("DNSE_ACCOUNT_NO")
    if configured:
        return configured
    accounts = await broker.trading.accounts.list_accounts()
    if not accounts:
        pytest.skip("DNSE live account list returned no accounts")
    return accounts[0].account_id


@pytest.mark.asyncio
async def test_dnse_live_lists_accounts() -> None:
    broker = _broker()

    accounts = await broker.trading.accounts.list_accounts()

    assert accounts
    assert accounts[0].broker == "dnse"
    assert accounts[0].account_id


@pytest.mark.asyncio
async def test_dnse_live_reads_balance() -> None:
    broker = _broker()
    account_id = await _account_id(broker)

    balance = await broker.trading.accounts.get_balance(account_id)

    assert balance.account_id == account_id
    assert balance.currency == "VND"
    assert balance.raw is not None


@pytest.mark.asyncio
async def test_dnse_live_lists_positions() -> None:
    broker = _broker()
    account_id = await _account_id(broker)

    positions = await broker.trading.positions.list_positions(account_id)

    for position in positions:
        assert position.account_id
        assert position.symbol
        assert position.raw is not None
