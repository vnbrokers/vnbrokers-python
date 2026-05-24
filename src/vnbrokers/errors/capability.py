from vnbrokers.core.capability import Capability
from vnbrokers.errors.base import VnBrokerError


class UnsupportedCapabilityError(VnBrokerError):
    def __init__(self, broker: str, capability: Capability) -> None:
        super().__init__(
            f"Broker '{broker}' does not support capability '{capability.value}'",
            broker=broker,
        )
        self.capability = capability
