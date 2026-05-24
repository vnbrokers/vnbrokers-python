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
    quote = await broker.market_data.quotes.get_quote(
        os.getenv("DNSE_SYMBOL", "HPG"),
        board_id=os.getenv("DNSE_BOARD_ID", "G1"),
    )
    print(quote)


if __name__ == "__main__":
    asyncio.run(main())
