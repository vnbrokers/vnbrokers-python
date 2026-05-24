import pytest

from vnbrokers.brokers.dnse import DnseBroker, DnseConfig
from vnbrokers.core.broker import BrokerBase
from vnbrokers.core.capability import Capability
from vnbrokers.errors.capability import UnsupportedCapabilityError


class MinimalBroker(BrokerBase):
    _name = "minimal"
    _capabilities = (Capability.TRADING_ACCOUNTS_LIST,)


def test_dnse_declares_supported_capabilities() -> None:
    broker = DnseBroker(DnseConfig())

    assert broker.name == "dnse"
    assert broker.supports(Capability.TRADING_ACCOUNTS_LIST)
    assert broker.supports(Capability.TRADING_ORDERS_PLACE)
    assert broker.supports(Capability.TRADING_POSITIONS_LIST)
    assert broker.supports(Capability.TRADING_REALTIME_ORDERS)
    assert broker.supports(Capability.TRADING_REALTIME_POSITIONS)
    assert broker.supports(Capability.BROKERAGE_CARE_BY)
    assert broker.supports(Capability.MARKETDATA_SYMBOLS_LIST)
    assert broker.supports(Capability.MARKETDATA_QUOTES)
    assert broker.supports(Capability.MARKETDATA_CANDLES)
    assert broker.supports(Capability.MARKETDATA_REALTIME_TICKS)
    assert broker.supports(Capability.MARKETDATA_REALTIME_TOP_PRICE)
    assert broker.supports(Capability.MARKETDATA_REALTIME_CANDLES)
    assert broker.supports(Capability.MARKETDATA_REALTIME_RAW)


def test_require_capability_raises_typed_error_for_unsupported_feature() -> None:
    broker = MinimalBroker()

    with pytest.raises(UnsupportedCapabilityError) as exc:
        broker.require_capability(Capability.MARKETDATA_QUOTES)

    assert exc.value.broker == "minimal"
    assert exc.value.capability == Capability.MARKETDATA_QUOTES
