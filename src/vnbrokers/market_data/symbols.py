from typing import Protocol

from vnbrokers.domain.raw import RawPayload
from vnbrokers.domain.symbol import Symbol


class MarketDataSymbolsService(Protocol):
    async def list_symbols(
        self,
        symbol: str | None = None,
        *,
        market_id: str | None = None,
        security_group_id: str | None = None,
        index_name: str | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> list[Symbol]:
        raise NotImplementedError

    async def get_security_definition(
        self, symbol: str, *, board_id: str | None = None
    ) -> RawPayload:
        raise NotImplementedError

    async def get_working_dates(self) -> RawPayload:
        raise NotImplementedError
