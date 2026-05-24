from vnbrokers.brokers.tcbs.capabilities import TCBS_CAPABILITIES
from vnbrokers.brokers.tcbs.config import TcbsConfig
from vnbrokers.core.broker import BrokerBase
from vnbrokers.core.capability import Capability


class TcbsBroker(BrokerBase):
    _name = "tcbs"
    _capabilities: tuple[Capability, ...] = TCBS_CAPABILITIES

    def __init__(self, config: TcbsConfig) -> None:
        self.config = config
