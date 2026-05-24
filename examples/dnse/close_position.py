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
            market_type=os.getenv("DNSE_MARKET_TYPE", "DERIVATIVE"),
        )
    )
    payload = await broker.trading.positions.close_position(require_env("DNSE_POSITION_ID"))
    print(payload.data)


if __name__ == "__main__":
    asyncio.run(main())
