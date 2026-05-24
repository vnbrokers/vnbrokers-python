from dataclasses import dataclass

from vnbrokers.core.config import BrokerConfig


@dataclass(frozen=True)
class DnseConfig(BrokerConfig):
    base_url: str | None = "https://openapi.dnse.com.vn"
    stream_url: str | None = "wss://ws-openapi.dnse.com.vn/v1/stream?encoding=json"
    api_key: str | None = None
    api_secret: str | None = None
    access_token: str | None = None
    trading_token: str | None = None
    stream_encoding: str = "json"
    market_type: str = "DERIVATIVE"
    order_category: str = "NORMAL"
    loan_package_id: int | None = None
    positions_page_size: int = 20
    market_data_symbol_limit: int = 1000
    market_data_board_id: str = "G1"
    candle_market_type: str = "STOCK"
    candle_lookback_seconds: int = 86400
