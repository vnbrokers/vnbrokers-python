import asyncio
import os

from vnbrokers.brokers.dnse import DnseBroker, DnseConfig

from _common import require_env


async def main() -> None:
    broker = DnseBroker(
        DnseConfig(
            api_key=os.getenv("DNSE_API_KEY"),
            api_secret=os.getenv("DNSE_API_SECRET"),
            trading_token=os.getenv("DNSE_TRADING_TOKEN"),
            market_type=os.getenv("DNSE_MARKET_TYPE", "STOCK"),
            order_category=os.getenv("DNSE_ORDER_CATEGORY", "NORMAL"),
        )
    )
    await broker.trading.orders.cancel_order(
        require_env("DNSE_ACCOUNT_ID"),
        require_env("DNSE_ORDER_ID"),
    )
    print("cancel requested")


if __name__ == "__main__":
    asyncio.run(main())
