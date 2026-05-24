from typing import Protocol

from vnbrokers.transport.http import HttpRequest


class Signer(Protocol):
    def sign(self, request: HttpRequest) -> HttpRequest:
        raise NotImplementedError
