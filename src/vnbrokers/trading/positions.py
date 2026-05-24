from typing import Protocol

from vnbrokers.domain.position import Position
from vnbrokers.domain.raw import RawPayload


class TradingPositionsService(Protocol):
    async def list_positions(self, account_id: str) -> list[Position]:
        raise NotImplementedError

    async def get_position(self, position_id: str) -> Position:
        raise NotImplementedError

    async def close_position(self, position_id: str) -> RawPayload:
        raise NotImplementedError
