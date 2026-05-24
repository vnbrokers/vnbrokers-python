from vnbrokers.brokers.ssi.capabilities import SSI_CAPABILITIES
from vnbrokers.brokers.ssi.config import SsiConfig
from vnbrokers.core.broker import BrokerBase
from vnbrokers.core.capability import Capability


class SsiBroker(BrokerBase):
    _name = "ssi"
    _capabilities: tuple[Capability, ...] = SSI_CAPABILITIES

    def __init__(self, config: SsiConfig) -> None:
        self.config = config
