from typing import Protocol

from vnbrokers.domain.quote import Quote
from vnbrokers.domain.raw import RawPayload


class MarketDataQuotesService(Protocol):
    async def get_quote(self, symbol: str, *, board_id: str | None = None) -> Quote:
        raise NotImplementedError

    async def get_price_trades(
        self,
        symbol: str,
        *,
        from_time: int,
        to_time: int,
        board_id: str | None = None,
        limit: int | None = None,
    ) -> RawPayload:
        raise NotImplementedError

    async def get_close_price(self, symbol: str, *, board_id: str | None = None) -> RawPayload:
        raise NotImplementedError
