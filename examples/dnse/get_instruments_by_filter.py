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
    symbols = await broker.market_data.symbols.list_symbols(
        symbol=os.getenv("DNSE_SYMBOLS", "SSI,SHS,ACB,HUT,DSE"),
        market_id=os.getenv("DNSE_MARKET_ID") or None,
        security_group_id=os.getenv("DNSE_SECURITY_GROUP_ID") or None,
        index_name=os.getenv("DNSE_INDEX_NAME") or None,
        limit=int(os.getenv("DNSE_LIMIT", "10")),
        page=int(os.getenv("DNSE_PAGE", "1")),
    )
    for symbol in symbols:
        print(symbol)


if __name__ == "__main__":
    asyncio.run(main())
