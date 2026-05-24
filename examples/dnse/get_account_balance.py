import asyncio
import os

from vnbrokers.brokers.dnse import DnseBroker, DnseConfig

from _common import require_env


async def main() -> None:
    broker = DnseBroker(
        DnseConfig(
            api_key=os.getenv("DNSE_API_KEY"),
            api_secret=os.getenv("DNSE_API_SECRET"),
        )
    )
    balance = await broker.trading.accounts.get_balance(require_env("DNSE_ACCOUNT_ID"))
    print(balance)


if __name__ == "__main__":
    asyncio.run(main())
