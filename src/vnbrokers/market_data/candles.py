from typing import Protocol

from vnbrokers.domain.candle import Candle


class MarketDataCandlesService(Protocol):
    async def get_candles(
        self,
        symbol: str,
        interval: str,
        *,
        from_time: int | None = None,
        to_time: int | None = None,
        market_type: str | None = None,
    ) -> list[Candle]:
        raise NotImplementedError
