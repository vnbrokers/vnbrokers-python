from typing import Protocol


class TokenProvider(Protocol):
    async def get_token(self) -> str:
        raise NotImplementedError
