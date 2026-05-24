from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from vnbrokers.domain.candle import Candle
from vnbrokers.domain.raw import RawPayload
from vnbrokers.domain.tick import Tick
from vnbrokers.domain.top_price import TopPrice
from vnbrokers.realtime.subscription import Subscription


@dataclass(frozen=True)
class SubscribeSymbolRequest:
    symbol: str | None = None
    symbols: Sequence[str] = ()

    def __post_init__(self) -> None:
        if self.symbol is not None and self.symbols:
            raise ValueError("Use either symbol or symbols, not both")

    @classmethod
    def all(cls) -> "SubscribeSymbolRequest":
        return cls()

    def symbol_list(self) -> list[str] | None:
        if self.symbol is not None:
            return [self.symbol]
        if self.symbols:
            return list(self.symbols)
        return None


class MarketDataRealtimeService(Protocol):
    async def subscribe_ticks(self, request: SubscribeSymbolRequest) -> Subscription[Tick]:
        raise NotImplementedError

    async def subscribe_top_price(self, request: SubscribeSymbolRequest) -> Subscription[TopPrice]:
        raise NotImplementedError

    async def subscribe_candles(
        self,
        request: SubscribeSymbolRequest,
        interval: str,
    ) -> Subscription[Candle]:
        raise NotImplementedError

    async def subscribe_closed_candles(
        self,
        request: SubscribeSymbolRequest,
        interval: str,
    ) -> Subscription[Candle]:
        raise NotImplementedError

    async def subscribe_tick_extra(
        self,
        request: SubscribeSymbolRequest,
    ) -> Subscription[RawPayload]:
        raise NotImplementedError

    async def subscribe_expected_price(
        self,
        request: SubscribeSymbolRequest,
    ) -> Subscription[RawPayload]:
        raise NotImplementedError

    async def subscribe_foreign(
        self,
        request: SubscribeSymbolRequest,
    ) -> Subscription[RawPayload]:
        raise NotImplementedError

    async def subscribe_security_definition(
        self,
        request: SubscribeSymbolRequest,
    ) -> Subscription[RawPayload]:
        raise NotImplementedError

    async def subscribe_market_index(self, index_name: str) -> Subscription[RawPayload]:
        raise NotImplementedError
