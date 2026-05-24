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

    print(f"Subscribing security definition with DNSE stream encoding={stream_encoding}")
    async with await broker.market_data.realtime.subscribe_security_definition(
        request
    ) as subscription:
        async for payload in subscription.events():
            print(payload.data)


if __name__ == "__main__":
    asyncio.run(main())
