import pytest

from vnbrokers import create_broker, get_broker_registration, list_brokers
from vnbrokers.brokers.dnse import DnseBroker, DnseConfig
from vnbrokers.brokers.ssi import SsiBroker, SsiConfig
from vnbrokers.brokers.tcbs import TcbsBroker


def test_list_brokers_returns_builtin_names() -> None:
    assert list_brokers() == ("dnse", "ssi", "tcbs")


def test_create_broker_accepts_explicit_config() -> None:
    broker = create_broker("dnse", DnseConfig(api_key="key"))

    assert isinstance(broker, DnseBroker)
    assert broker.config.api_key == "key"


def test_create_broker_builds_config_from_keyword_arguments() -> None:
    broker = create_broker("ssi", api_key="key", api_secret="secret")

    assert isinstance(broker, SsiBroker)
    assert broker.config == SsiConfig(api_key="key", api_secret="secret")


def test_create_broker_normalizes_broker_name() -> None:
    broker = create_broker(" TCBS ")

    assert isinstance(broker, TcbsBroker)


def test_get_broker_registration_returns_registered_types() -> None:
    registration = get_broker_registration("dnse")

    assert registration.name == "dnse"
    assert registration.broker_type is DnseBroker
    assert registration.config_type is DnseConfig


def test_create_broker_rejects_unknown_broker() -> None:
    with pytest.raises(ValueError, match="Unsupported broker: unknown"):
        create_broker("unknown")


def test_create_broker_rejects_config_and_keyword_arguments_together() -> None:
    with pytest.raises(TypeError, match="Pass either config or config keyword arguments"):
        create_broker("dnse", DnseConfig(), api_key="key")


