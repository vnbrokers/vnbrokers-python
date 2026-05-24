import asyncio
import os

from vnbrokers.brokers.dnse import DnseBroker, DnseConfig
from vnbrokers.market_data.realtime import SubscribeSymbolRequest


async def main() -> None:
    stream_encoding = os.getenv("DNSE_STREAM_ENCODING", "msgpack")
    broker = DnseBroker(
        DnseConfig(
            api_key=os.getenv("DNSE_API_KEY"),
            api_secret=os.getenv("DNSE_API_SECRET"),
            stream_encoding=stream_encoding,
        )
    )
    request = SubscribeSymbolRequest(symbols=("FPT", "HPG"))

    print(f"Subscribing top price with DNSE stream encoding={stream_encoding}")
    async with await broker.market_data.realtime.subscribe_top_price(request) as subscription:
        async for top_price in subscription.events():
            print(top_price.symbol, top_price.bid_price, top_price.ask_price)


if __name__ == "__main__":
    asyncio.run(main())
