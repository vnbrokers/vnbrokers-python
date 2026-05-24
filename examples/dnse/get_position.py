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
    position = await broker.trading.positions.get_position(require_env("DNSE_POSITION_ID"))
    print(position)


if __name__ == "__main__":
    asyncio.run(main())
