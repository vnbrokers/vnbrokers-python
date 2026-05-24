import asyncio
import os

from vnbrokers.brokers.dnse import DnseBroker, DnseConfig


async def main() -> None:
    stream_encoding = os.getenv("DNSE_STREAM_ENCODING", "msgpack")
    index_name = os.getenv("DNSE_MARKET_INDEX", "VN30")
    broker = DnseBroker(
        DnseConfig(
            api_key=os.getenv("DNSE_API_KEY"),
            api_secret=os.getenv("DNSE_API_SECRET"),
            stream_encoding=stream_encoding,
        )
    )

    print(f"Subscribing market index {index_name} with DNSE stream encoding={stream_encoding}")
    async with await broker.market_data.realtime.subscribe_market_index(index_name) as subscription:
        async for payload in subscription.events():
            print(payload.data)


if __name__ == "__main__":
    asyncio.run(main())
