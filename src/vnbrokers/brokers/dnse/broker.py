from dataclasses import dataclass

from vnbrokers.brokers.dnse.auth import DnseAuthService
from vnbrokers.brokers.dnse.brokerage import DnseBrokerageService
from vnbrokers.brokers.dnse.capabilities import DNSE_CAPABILITIES
from vnbrokers.brokers.dnse.config import DnseConfig
from vnbrokers.brokers.dnse.market_data import (
    DnseMarketDataCandlesService,
    DnseMarketDataQuotesService,
    DnseMarketDataSymbolsService,
)
from vnbrokers.brokers.dnse.market_data_realtime import DnseMarketDataRealtimeService
from vnbrokers.brokers.dnse.trading import (
    DnseTradingAccountsService,
    DnseTradingOrdersService,
    DnseTradingPositionsService,
)
from vnbrokers.brokers.dnse.trading_realtime import DnseTradingRealtimeService
from vnbrokers.core.broker import BrokerBase
from vnbrokers.core.capability import Capability
from vnbrokers.transport.http import HttpTransport, HttpxTransport
from vnbrokers.transport.websocket import WebsocketsTransport, WebSocketTransportFactory


@dataclass(frozen=True)
class DnseTradingService:
    accounts: DnseTradingAccountsService
    orders: DnseTradingOrdersService
    positions: DnseTradingPositionsService
    realtime: DnseTradingRealtimeService


@dataclass(frozen=True)
class DnseMarketDataService:
    symbols: DnseMarketDataSymbolsService
    quotes: DnseMarketDataQuotesService
    candles: DnseMarketDataCandlesService
    realtime: DnseMarketDataRealtimeService


class DnseBroker(BrokerBase):
    _name = "dnse"
    _capabilities: tuple[Capability, ...] = DNSE_CAPABILITIES

    def __init__(
        self,
        config: DnseConfig,
        http_transport: HttpTransport | None = None,
        websocket_transport_factory: WebSocketTransportFactory | None = None,
    ) -> None:
        self.config = config
        self.http_transport = http_transport or HttpxTransport()
        factory: WebSocketTransportFactory = (
            websocket_transport_factory or WebsocketsTransport.connect
        )
        self.websocket_transport_factory = factory
        self.auth = DnseAuthService(config, self.http_transport)
        self.brokerage = DnseBrokerageService(self, config, self.http_transport)
        self.trading = DnseTradingService(
            accounts=DnseTradingAccountsService(self, config, self.http_transport),
            orders=DnseTradingOrdersService(self, config, self.http_transport),
            positions=DnseTradingPositionsService(self, config, self.http_transport),
            realtime=DnseTradingRealtimeService(
                self,
                config,
                self.websocket_transport_factory,
            ),
        )
        self.market_data = DnseMarketDataService(
            symbols=DnseMarketDataSymbolsService(self, config, self.http_transport),
            quotes=DnseMarketDataQuotesService(self, config, self.http_transport),
            candles=DnseMarketDataCandlesService(self, config, self.http_transport),
            realtime=DnseMarketDataRealtimeService(
                self,
                config,
                self.websocket_transport_factory,
            ),
        )
