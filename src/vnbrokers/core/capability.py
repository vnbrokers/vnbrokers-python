from enum import Enum


class Capability(str, Enum):
    TRADING_ACCOUNTS_LIST = "trading.accounts.list"
    TRADING_ORDERS_PLACE = "trading.orders.place"
    TRADING_ORDERS_CANCEL = "trading.orders.cancel"
    TRADING_POSITIONS_LIST = "trading.positions.list"
    TRADING_REALTIME_ORDERS = "trading.realtime.orders"
    TRADING_REALTIME_POSITIONS = "trading.realtime.positions"
    BROKERAGE_CARE_BY = "brokerage.accounts.care_by"
    MARKETDATA_SYMBOLS_LIST = "marketdata.symbols.list"
    MARKETDATA_QUOTES = "marketdata.quotes.snapshot"
    MARKETDATA_CANDLES = "marketdata.candles.history"
    MARKETDATA_REALTIME_TICKS = "marketdata.realtime.ticks"
    MARKETDATA_REALTIME_TOP_PRICE = "marketdata.realtime.top_price"
    MARKETDATA_REALTIME_CANDLES = "marketdata.realtime.candles"
    MARKETDATA_REALTIME_RAW = "marketdata.realtime.raw"
