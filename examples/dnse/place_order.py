import asyncio
import os
from decimal import Decimal

from vnbrokers.brokers.dnse import DnseBroker, DnseConfig
from vnbrokers.domain.enums import OrderSide, OrderType
from vnbrokers.domain.order import PlaceOrderRequest

from _common import require_env


async def main() -> None:
    loan_package_id = os.getenv("DNSE_LOAN_PACKAGE_ID")
    broker = DnseBroker(
        DnseConfig(
            api_key=os.getenv("DNSE_API_KEY"),
            api_secret=os.getenv("DNSE_API_SECRET"),
            trading_token=os.getenv("DNSE_TRADING_TOKEN"),
            market_type=os.getenv("DNSE_MARKET_TYPE", "STOCK"),
            loan_package_id=int(loan_package_id) if loan_package_id else None,
        )
    )
    request = PlaceOrderRequest(
        account_id=require_env("DNSE_ACCOUNT_ID"),
        symbol=os.getenv("DNSE_SYMBOL", "HPG"),
        side=OrderSide(os.getenv("DNSE_ORDER_SIDE", "BUY")),
        order_type=OrderType.LIMIT,
        quantity=Decimal(os.getenv("DNSE_ORDER_QUANTITY", "100")),
        price=Decimal(os.getenv("DNSE_ORDER_PRICE", "1000")),
    )
    response = await broker.trading.orders.place_order(request)
    print(response.order_id)


if __name__ == "__main__":
    asyncio.run(main())
