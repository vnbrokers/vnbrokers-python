from vnbrokers.core.broker import Broker
from vnbrokers.core.capability import Capability


def assert_broker_declares_capabilities(
    broker: Broker,
    expected: tuple[Capability, ...],
) -> None:
    for capability in expected:
        assert broker.supports(capability)
