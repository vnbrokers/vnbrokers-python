from enum import Enum


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP = "STOP"
    UNKNOWN = "UNKNOWN"


class TimeInForce(str, Enum):
    DAY = "DAY"
    IOC = "IOC"
    FOK = "FOK"
    UNKNOWN = "UNKNOWN"


class OrderStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
