from __future__ import annotations

from typing import Protocol

from vnbrokers.core.capability import Capability
from vnbrokers.errors.capability import UnsupportedCapabilityError


class Broker(Protocol):
    @property
    def name(self) -> str:
        raise NotImplementedError

    @property
    def capabilities(self) -> tuple[Capability, ...]:
        raise NotImplementedError

    def supports(self, capability: Capability) -> bool:
        raise NotImplementedError

    def require_capability(self, capability: Capability) -> None:
        raise NotImplementedError


class BrokerBase:
    _name: str
    _capabilities: tuple[Capability, ...]

    @property
    def name(self) -> str:
        return self._name

    @property
    def capabilities(self) -> tuple[Capability, ...]:
        return self._capabilities

    def supports(self, capability: Capability) -> bool:
        return capability in self._capabilities

    def require_capability(self, capability: Capability) -> None:
        if not self.supports(capability):
            raise UnsupportedCapabilityError(self.name, capability)
