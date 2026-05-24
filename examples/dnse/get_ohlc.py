import asyncio
import os

from vnbrokers.brokers.dnse import DnseBroker, DnseConfig


async def main() -> None:
    broker = DnseBroker(
        DnseConfig(
            api_key=os.getenv("DNSE_API_KEY"),
            api_secret=os.getenv("DNSE_API_SECRET"),
            candle_market_type=os.getenv("DNSE_MARKET_TYPE", "STOCK"),
        )
    )
    candles = await broker.market_data.candles.get_candles(
        os.getenv("DNSE_SYMBOL", "HPG"),
        os.getenv("DNSE_CANDLE_INTERVAL", "15"),
        from_time=int(os.getenv("DNSE_FROM_TIME", "1773657310")),
        to_time=int(os.getenv("DNSE_TO_TIME", "1773830110")),
    )
    for candle in candles:
        print(candle)


if __name__ == "__main__":
    asyncio.run(main())
