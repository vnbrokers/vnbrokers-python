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
            positions_page_size=int(os.getenv("DNSE_POSITIONS_PAGE_SIZE", "20")),
        )
    )
    positions = await broker.trading.positions.list_positions(require_env("DNSE_ACCOUNT_NO"))
    for position in positions:
        print(position)


if __name__ == "__main__":
    asyncio.run(main())
