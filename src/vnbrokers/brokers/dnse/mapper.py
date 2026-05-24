from decimal import Decimal
from typing import Any

from vnbrokers.brokers.dnse.dto import DnseOrderDTO, DnseOrderEventDTO
from vnbrokers.domain.account import Account
from vnbrokers.domain.balance import Balance
from vnbrokers.domain.candle import Candle
from vnbrokers.domain.enums import OrderSide, OrderStatus, OrderType
from vnbrokers.domain.order import Order, PlaceOrderResponse
from vnbrokers.domain.order_event import OrderEvent
from vnbrokers.domain.position import Position
from vnbrokers.domain.quote import Quote
from vnbrokers.domain.raw import RawPayload
from vnbrokers.domain.symbol import Symbol

_ORDER_STATUS_MAP = {
    "PENDING": OrderStatus.PENDING,
    "NEW": OrderStatus.ACCEPTED,
    "ACCEPTED": OrderStatus.ACCEPTED,
    "PARTIALLY_FILLED": OrderStatus.PARTIALLY_FILLED,
    "FILLED": OrderStatus.FILLED,
    "CANCELLED": OrderStatus.CANCELLED,
    "CANCELED": OrderStatus.CANCELLED,
    "REJECTED": OrderStatus.REJECTED,
}


def map_side(raw_side: str | None) -> OrderSide:
    if raw_side == "NB":
        return OrderSide.BUY
    if raw_side == "NS":
        return OrderSide.SELL
    raise ValueError(f"Unsupported DNSE order side: {raw_side}")


def map_order_type(raw_type: str | None) -> OrderType:
    if raw_type == "LO":
        return OrderType.LIMIT
    if raw_type in {"MP", "MTL", "MOK", "MAK"}:
        return OrderType.MARKET
    return OrderType.UNKNOWN


def map_order_status(raw_status: str | None) -> OrderStatus:
    if raw_status is None:
        return OrderStatus.UNKNOWN
    return _ORDER_STATUS_MAP.get(raw_status.upper(), OrderStatus.UNKNOWN)


def _decimal(value: Any) -> Decimal:
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


def _optional_decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    return _decimal(value)


def order_dto_from_payload(payload: dict[str, Any]) -> DnseOrderDTO:
    return DnseOrderDTO(
        id=payload.get("id", ""),
        account_no=str(payload.get("accountNo", "")),
        symbol=str(payload.get("symbol", "")),
        side=payload.get("side"),
        order_type=payload.get("orderType"),
        order_status=payload.get("orderStatus"),
        quantity=payload.get("quantity"),
        price=payload.get("price"),
        raw=payload,
    )


def map_order(payload: dict[str, Any]) -> Order:
    dto = order_dto_from_payload(payload)
    return Order(
        broker="dnse",
        account_id=dto.account_no,
        order_id=str(dto.id),
        symbol=dto.symbol,
        side=map_side(dto.side),
        order_type=map_order_type(dto.order_type),
        quantity=_decimal(dto.quantity),
        status=map_order_status(dto.order_status),
        price=_decimal(dto.price) if dto.price is not None else None,
        raw=RawPayload(source="dnse", data=dto.raw),
    )


def map_orders(payload: dict[str, Any]) -> list[Order]:
    raw_orders = payload.get("orders")
    if not isinstance(raw_orders, list):
        return []
    return [map_order(raw_order) for raw_order in raw_orders if isinstance(raw_order, dict)]


def map_order_history(payload: dict[str, Any]) -> list[Order]:
    raw_orders = payload.get("data")
    if not isinstance(raw_orders, list):
        return []
    return [map_order(raw_order) for raw_order in raw_orders if isinstance(raw_order, dict)]


def map_place_order_response(payload: dict[str, Any]) -> PlaceOrderResponse:
    return PlaceOrderResponse(
        order_id=str(payload.get("id", "")),
        status=map_order_status(payload.get("orderStatus")),
        raw=RawPayload(source="dnse", data=payload),
    )


def map_order_event(dto: DnseOrderEventDTO) -> OrderEvent:
    return OrderEvent(
        broker="dnse",
        account_id=dto.account_id,
        order_id=dto.order_id,
        symbol=dto.symbol,
        status=map_order_status(dto.status),
        raw_status=dto.status,
        filled_quantity=dto.filled_quantity,
        received_at=dto.received_at,
        raw=RawPayload(source="dnse", data=dto.raw),
    )


def map_accounts(payload: dict[str, Any]) -> list[Account]:
    raw_accounts = payload.get("accounts")
    if not isinstance(raw_accounts, list):
        return []

    display_name = str(payload["name"]) if payload.get("name") is not None else None
    accounts: list[Account] = []
    for raw_account in raw_accounts:
        if not isinstance(raw_account, dict):
            continue
        account_id = raw_account.get("id")
        if account_id is None:
            continue
        raw = dict(payload)
        raw["account"] = raw_account
        accounts.append(
            Account(
                account_id=str(account_id),
                broker="dnse",
                display_name=display_name,
                raw=RawPayload(source="dnse", data=raw),
            )
        )
    return accounts


def map_balance(account_id: str, payload: dict[str, Any]) -> Balance:
    stock = payload.get("stock")
    stock_payload = stock if isinstance(stock, dict) else {}
    available_cash = _optional_decimal(stock_payload.get("availableCash"))
    return Balance(
        account_id=account_id,
        cash_available=available_cash,
        cash_total=_optional_decimal(stock_payload.get("totalCash")),
        buying_power=available_cash,
        currency="VND",
        raw=RawPayload(source="dnse", data=payload),
    )


def map_positions(payload: dict[str, Any]) -> list[Position]:
    raw_positions = payload.get("positions")
    if not isinstance(raw_positions, list):
        return []

    positions: list[Position] = []
    for raw_position in raw_positions:
        if not isinstance(raw_position, dict):
            continue
        account_id = raw_position.get("accountNo")
        symbol = raw_position.get("symbol")
        if account_id is None or symbol is None:
            continue
        quantity = _decimal(
            raw_position.get("openQuantity")
            if raw_position.get("openQuantity") is not None
            else raw_position.get("tradeQuantity")
        )
        market_price = _optional_decimal(raw_position.get("marketPrice"))
        positions.append(
            Position(
                account_id=str(account_id),
                symbol=str(symbol),
                quantity=quantity,
                available_quantity=quantity,
                average_price=_optional_decimal(raw_position.get("costPrice")),
                market_value=quantity * market_price if market_price is not None else None,
                raw=RawPayload(source="dnse", data=raw_position),
            )
        )
    return positions


def map_position(payload: dict[str, Any]) -> Position:
    data = payload.get("data")
    if isinstance(data, dict):
        payload = data
    account_id = payload.get("accountNo")
    symbol = payload.get("symbol")
    if account_id is None or symbol is None:
        raise ValueError("DNSE position payload must include accountNo and symbol")
    quantity = _decimal(
        payload.get("openQuantity")
        if payload.get("openQuantity") is not None
        else payload.get("tradeQuantity")
    )
    market_price = _optional_decimal(payload.get("marketPrice"))
    return Position(
        account_id=str(account_id),
        symbol=str(symbol),
        quantity=quantity,
        available_quantity=quantity,
        average_price=_optional_decimal(
            payload.get("averageCostPrice") or payload.get("costPrice")
        ),
        market_value=quantity * market_price if market_price is not None else None,
        raw=RawPayload(source="dnse", data=payload),
    )


def map_symbols(payload: dict[str, Any]) -> list[Symbol]:
    data = payload.get("data")
    if not isinstance(data, list):
        return []

    symbols: list[Symbol] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        symbol = item.get("symbol")
        if symbol is None:
            continue
        display_name = item.get("name") or item.get("shortName")
        symbols.append(
            Symbol(
                symbol=str(symbol),
                exchange=str(item["marketId"]) if item.get("marketId") is not None else None,
                display_name=str(display_name) if display_name is not None else None,
                raw=RawPayload(source="dnse", data=item),
            )
        )
    return symbols


def map_quote(symbol: str, payload: dict[str, Any]) -> Quote:
    trades = payload.get("trades")
    first_trade = trades[0] if isinstance(trades, list) and trades else {}
    trade = first_trade if isinstance(first_trade, dict) else {}
    time_value = trade.get("time")
    return Quote(
        symbol=symbol,
        last_price=_optional_decimal(trade.get("price")),
        received_at=str(time_value) if time_value is not None else None,
        raw=RawPayload(source="dnse", data=payload),
    )


def map_candles(symbol: str, interval: str, payload: dict[str, Any]) -> list[Candle]:
    timestamps = payload.get("t")
    opens = payload.get("o")
    highs = payload.get("h")
    lows = payload.get("l")
    closes = payload.get("c")
    volumes = payload.get("v")
    if not isinstance(timestamps, list):
        return []
    if not isinstance(opens, list):
        return []
    if not isinstance(highs, list):
        return []
    if not isinstance(lows, list):
        return []
    if not isinstance(closes, list):
        return []
    if not isinstance(volumes, list):
        return []

    candles: list[Candle] = []
    for opened_at, open_, high, low, close, volume in zip(
        timestamps, opens, highs, lows, closes, volumes, strict=False
    ):
        candles.append(
            Candle(
                symbol=symbol,
                interval=interval,
                opened_at=str(opened_at),
                open=_decimal(open_),
                high=_decimal(high),
                low=_decimal(low),
                close=_decimal(close),
                volume=_decimal(volume),
                raw=RawPayload(source="dnse", data=payload),
            )
        )
    return candles
