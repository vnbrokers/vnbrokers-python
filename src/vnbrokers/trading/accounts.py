from decimal import Decimal
from typing import Protocol

from vnbrokers.domain.account import Account
from vnbrokers.domain.balance import Balance
from vnbrokers.domain.order import Order
from vnbrokers.domain.raw import RawPayload


class TradingAccountsService(Protocol):
    async def list_accounts(self) -> list[Account]:
        raise NotImplementedError

    async def get_balance(self, account_id: str) -> Balance:
        raise NotImplementedError

    async def list_orders(self, account_id: str) -> list[Order]:
        raise NotImplementedError

    async def list_order_history(
        self,
        account_id: str,
        *,
        from_date: str,
        to_date: str,
        page_index: int = 0,
    ) -> list[Order]:
        raise NotImplementedError

    async def get_executions(self, account_id: str, order_id: str) -> RawPayload:
        raise NotImplementedError

    async def get_ppse(
        self,
        account_id: str,
        *,
        symbol: str,
        price: Decimal,
        loan_package_id: int | None = None,
    ) -> RawPayload:
        raise NotImplementedError

    async def get_loan_packages(self, account_id: str, *, symbol: str) -> RawPayload:
        raise NotImplementedError
