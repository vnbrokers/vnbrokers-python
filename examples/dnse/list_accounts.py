import asyncio
import os

from vnbrokers.brokers.dnse import DnseBroker, DnseConfig


async def main() -> None:
    broker = DnseBroker(
        DnseConfig(
            api_key=os.getenv("DNSE_API_KEY"),
            api_secret=os.getenv("DNSE_API_SECRET"),
        )
    )
    accounts = await broker.trading.accounts.list_accounts()
    for account in accounts:
        print(account.account_id)


if __name__ == "__main__":
    asyncio.run(main())
