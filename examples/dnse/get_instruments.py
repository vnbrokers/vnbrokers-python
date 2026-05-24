import asyncio
import os

from vnbrokers.brokers.dnse import DnseBroker, DnseConfig


async def main() -> None:
    broker = DnseBroker(
        DnseConfig(
            api_key=os.getenv("DNSE_API_KEY"),
            api_secret=os.getenv("DNSE_API_SECRET"),
            market_data_symbol_limit=int(os.getenv("DNSE_LIMIT", "1000")),
        )
    )
    symbols = await broker.market_data.symbols.list_symbols(symbol=os.getenv("DNSE_SYMBOLS"))
    for symbol in symbols:
        print(symbol)


if __name__ == "__main__":
    asyncio.run(main())
