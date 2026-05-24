import asyncio
import os
from decimal import Decimal

from vnbrokers.brokers.dnse import DnseBroker, DnseConfig

from _common import require_env


async def main() -> None:
    broker = DnseBroker(
        DnseConfig(
            api_key=os.getenv("DNSE_API_KEY"),
            api_secret=os.getenv("DNSE_API_SECRET"),
            market_type=os.getenv("DNSE_MARKET_TYPE", "STOCK"),
        )
    )
    payload = await broker.trading.accounts.get_ppse(
        require_env("DNSE_ACCOUNT_ID"),
        symbol=os.getenv("DNSE_SYMBOL", "HPG"),
        price=Decimal(os.getenv("DNSE_PRICE", "1000")),
        loan_package_id=int(os.getenv("DNSE_LOAN_PACKAGE_ID", "0")),
    )
    print(payload.data)


if __name__ == "__main__":
    asyncio.run(main())
