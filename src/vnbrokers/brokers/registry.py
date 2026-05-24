from vnbrokers.brokers.dnse import DnseBroker, DnseConfig
from vnbrokers.brokers.ssi import SsiBroker, SsiConfig
from vnbrokers.brokers.tcbs import TcbsBroker, TcbsConfig
from vnbrokers.core.broker import Broker
from vnbrokers.core.config import BrokerConfig
from vnbrokers.core.factory import BrokerFactory, BrokerRegistration

BUILTIN_BROKERS: tuple[BrokerRegistration[BrokerConfig, Broker], ...] = (
    BrokerRegistration("dnse", DnseBroker, DnseConfig),
    BrokerRegistration("ssi", SsiBroker, SsiConfig),
    BrokerRegistration("tcbs", TcbsBroker, TcbsConfig),
)

DEFAULT_BROKER_FACTORY = BrokerFactory(list(BUILTIN_BROKERS))


def create_broker(
    name: str,
    config: BrokerConfig | None = None,
    **config_kwargs: object,
) -> Broker:
    return DEFAULT_BROKER_FACTORY.create_broker(name, config, **config_kwargs)


def list_brokers() -> tuple[str, ...]:
    return DEFAULT_BROKER_FACTORY.list_brokers()


def get_broker_registration(name: str) -> BrokerRegistration[BrokerConfig, Broker]:
    return DEFAULT_BROKER_FACTORY.get_registration(name)
