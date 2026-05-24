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
    orders = await broker.trading.accounts.list_orders(require_env("DNSE_ACCOUNT_ID"))
    for order in orders:
        print(order)


if __name__ == "__main__":
    asyncio.run(main())
