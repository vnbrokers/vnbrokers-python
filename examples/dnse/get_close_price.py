import asyncio
import os

from vnbrokers.brokers.dnse import DnseBroker, DnseConfig


async def main() -> None:
    symbol = os.getenv("DNSE_SYMBOL", "HPG")
    board_id = os.getenv("DNSE_BOARD_ID", "G1")
    broker = DnseBroker(
        DnseConfig(
            api_key=os.getenv("DNSE_API_KEY"),
            api_secret=os.getenv("DNSE_API_SECRET"),
        )
    )

    payload = await broker.market_data.quotes.get_close_price(symbol, board_id=board_id)
    print(payload.data)


if __name__ == "__main__":
    asyncio.run(main())
