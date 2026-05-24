import asyncio
import os

from vnbrokers.brokers.dnse import DnseBroker, DnseConfig
from vnbrokers.trading.realtime import SubscribeOrdersRequest


async def main() -> None:
    stream_encoding = os.getenv("DNSE_STREAM_ENCODING", "msgpack")
    broker = DnseBroker(
        DnseConfig(
            api_key=os.getenv("DNSE_API_KEY"),
            api_secret=os.getenv("DNSE_API_SECRET"),
            stream_encoding=stream_encoding,
        )
    )
    request = SubscribeOrdersRequest(
        account_id=os.getenv("DNSE_ACCOUNT_ID", ""),
        market_type=os.getenv("DNSE_MARKET_TYPE", "STOCK"),
    )

    print(f"Subscribing orders with DNSE stream encoding={stream_encoding}")
    async with await broker.trading.realtime.subscribe_orders(request) as subscription:
        async for event in subscription.events():
            print(event.order_id, event.status.value)


if __name__ == "__main__":
    asyncio.run(main())
