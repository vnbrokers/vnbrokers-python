import asyncio
import os

from vnbrokers.brokers.dnse import DnseBroker, DnseConfig

from _common import require_env


async def main() -> None:
    broker = DnseBroker(
        DnseConfig(
            api_key=os.getenv("DNSE_API_KEY"),
            api_secret=os.getenv("DNSE_API_SECRET"),
            market_type=os.getenv("DNSE_MARKET_TYPE", "STOCK"),
            order_category=os.getenv("DNSE_ORDER_CATEGORY", "NORMAL"),
        )
    )
    payload = await broker.trading.accounts.get_executions(
        require_env("DNSE_ACCOUNT_ID"),
        require_env("DNSE_ORDER_ID"),
    )
    print(payload.data)


if __name__ == "__main__":
    asyncio.run(main())
