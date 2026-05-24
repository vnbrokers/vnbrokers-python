import asyncio
import os

from vnbrokers.brokers.dnse import DnseBroker, DnseConfig


async def main() -> None:
    broker = DnseBroker(
        DnseConfig(
            api_key=os.getenv("DNSE_API_KEY"),
            api_secret=os.getenv("DNSE_API_SECRET"),
        )
    )
    payload = await broker.market_data.quotes.get_price_trades(
        os.getenv("DNSE_SYMBOL", "HPG"),
        from_time=int(os.getenv("DNSE_FROM_TIME", "1773182637")),
        to_time=int(os.getenv("DNSE_TO_TIME", "1773183637")),
        board_id=os.getenv("DNSE_BOARD_ID", "G1"),
        limit=int(os.getenv("DNSE_LIMIT", "1000")),
    )
    print(payload.data)


if __name__ == "__main__":
    asyncio.run(main())
