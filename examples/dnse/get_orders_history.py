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
        )
    )
    orders = await broker.trading.accounts.list_order_history(
        require_env("DNSE_ACCOUNT_ID"),
        from_date=os.getenv("DNSE_FROM_DATE", "2026-01-01"),
        to_date=os.getenv("DNSE_TO_DATE", "2026-12-31"),
        page_index=int(os.getenv("DNSE_PAGE_INDEX", "0")),
    )
    for order in orders:
        print(order)


if __name__ == "__main__":
    asyncio.run(main())
