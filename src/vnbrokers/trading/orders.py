from decimal import Decimal
from typing import Protocol

from vnbrokers.domain.order import Order, PlaceOrderRequest, PlaceOrderResponse
from vnbrokers.domain.raw import RawPayload


class TradingOrdersService(Protocol):
    async def place_order(self, request: PlaceOrderRequest) -> PlaceOrderResponse:
        raise NotImplementedError

    async def cancel_order(self, account_id: str, order_id: str) -> None:
        raise NotImplementedError

    async def get_order(self, account_id: str, order_id: str) -> Order:
        raise NotImplementedError

    async def update_order(
        self,
        account_id: str,
        order_id: str,
        *,
        price: Decimal,
        quantity: int,
    ) -> RawPayload:
        raise NotImplementedError
