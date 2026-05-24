from vnbrokers.core.capability import Capability

DNSE_CAPABILITIES: tuple[Capability, ...] = (
    Capability.TRADING_ACCOUNTS_LIST,
    Capability.TRADING_ORDERS_PLACE,
    Capability.TRADING_ORDERS_CANCEL,
    Capability.TRADING_POSITIONS_LIST,
    Capability.TRADING_REALTIME_ORDERS,
    Capability.TRADING_REALTIME_POSITIONS,
    Capability.BROKERAGE_CARE_BY,
    Capability.MARKETDATA_SYMBOLS_LIST,
    Capability.MARKETDATA_QUOTES,
    Capability.MARKETDATA_CANDLES,
    Capability.MARKETDATA_REALTIME_TICKS,
    Capability.MARKETDATA_REALTIME_TOP_PRICE,
    Capability.MARKETDATA_REALTIME_CANDLES,
    Capability.MARKETDATA_REALTIME_RAW,
)
