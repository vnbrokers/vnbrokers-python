from decimal import Decimal
from typing import Any
from urllib.parse import quote, urlencode

from vnbrokers.brokers.dnse.auth import DnseAuth
from vnbrokers.brokers.dnse.config import DnseConfig
from vnbrokers.brokers.dnse.mapper import (
    map_accounts,
    map_balance,
    map_order,
    map_order_history,
    map_orders,
    map_place_order_response,
    map_position,
    map_positions,
)
from vnbrokers.core.broker import BrokerBase
from vnbrokers.core.capability import Capability
from vnbrokers.domain.account import Account
from vnbrokers.domain.balance import Balance
from vnbrokers.domain.enums import OrderSide, OrderType
from vnbrokers.domain.order import Order, PlaceOrderRequest, PlaceOrderResponse
from vnbrokers.domain.position import Position
from vnbrokers.domain.raw import RawPayload
from vnbrokers.errors.broker_rejected import BrokerRejectedError
from vnbrokers.transport.http import HttpRequest, HttpResponse, HttpTransport


class DnseTradingAccountsService:
    def __init__(
        self,
        broker: BrokerBase,
        config: DnseConfig,
        transport: HttpTransport,
    ) -> None:
        self._broker = broker
        self._config = config
        self._transport = transport

    async def list_accounts(self) -> list[Account]:
        self._broker.require_capability(Capability.TRADING_ACCOUNTS_LIST)
        response = await _send_request(
            self._config,
            self._transport,
            HttpRequest(
                method="GET",
                url=f"{_base_url(self._config)}/accounts",
                headers=_api_headers(self._config),
            ),
        )
        return map_accounts(_expect_object(response.body))

    async def get_balance(self, account_id: str) -> Balance:
        self._broker.require_capability(Capability.TRADING_ACCOUNTS_LIST)
        response = await _send_request(
            self._config,
            self._transport,
            HttpRequest(
                method="GET",
                url=f"{_base_url(self._config)}/accounts/{quote(account_id, safe='')}/balances",
                headers=_api_headers(self._config),
            ),
        )
        return map_balance(account_id, _expect_object(response.body))

    async def list_orders(self, account_id: str) -> list[Order]:
        self._broker.require_capability(Capability.TRADING_ORDERS_PLACE)
        response = await _send_request(
            self._config,
            self._transport,
            HttpRequest(
                method="GET",
                url=f"{_base_url(self._config)}/accounts/{quote(account_id, safe='')}/orders?{_market_order_query(self._config)}",
                headers=_api_headers(self._config),
            ),
        )
        return map_orders(_expect_object(response.body))

    async def list_order_history(
        self,
        account_id: str,
        *,
        from_date: str,
        to_date: str,
        page_index: int = 0,
    ) -> list[Order]:
        self._broker.require_capability(Capability.TRADING_ORDERS_PLACE)
        params = urlencode(
            {
                "marketType": self._config.market_type,
                "from": from_date,
                "to": to_date,
                "pageIndex": page_index,
            }
        )
        response = await _send_request(
            self._config,
            self._transport,
            HttpRequest(
                method="GET",
                url=f"{_base_url(self._config)}/accounts/{quote(account_id, safe='')}/orders/history?{params}",
                headers=_api_headers(self._config),
            ),
        )
        return map_order_history(_expect_object(response.body))

    async def get_executions(self, account_id: str, order_id: str) -> RawPayload:
        self._broker.require_capability(Capability.TRADING_ORDERS_PLACE)
        response = await _send_request(
            self._config,
            self._transport,
            HttpRequest(
                method="GET",
                url=(
                    f"{_base_url(self._config)}/accounts/{quote(account_id, safe='')}"
                    f"/executions/{quote(order_id, safe='')}?{_market_order_query(self._config)}"
                ),
                headers=_api_headers(self._config),
            ),
        )
        return RawPayload(source="dnse", data=_expect_object(response.body))

    async def get_ppse(
        self,
        account_id: str,
        *,
        symbol: str,
        price: Decimal,
        loan_package_id: int | None = None,
    ) -> RawPayload:
        self._broker.require_capability(Capability.TRADING_ACCOUNTS_LIST)
        params = urlencode(
            {
                "marketType": self._config.market_type,
                "symbol": symbol,
                "loanPackageId": (
                    loan_package_id
                    if loan_package_id is not None
                    else self._config.loan_package_id or 0
                ),
                "price": _number(price),
            }
        )
        response = await _send_request(
            self._config,
            self._transport,
            HttpRequest(
                method="GET",
                url=f"{_base_url(self._config)}/accounts/{quote(account_id, safe='')}/ppse?{params}",
                headers=_api_headers(self._config),
            ),
        )
        return RawPayload(source="dnse", data=_expect_object(response.body))

    async def get_loan_packages(self, account_id: str, *, symbol: str) -> RawPayload:
        self._broker.require_capability(Capability.TRADING_ACCOUNTS_LIST)
        params = urlencode({"marketType": self._config.market_type, "symbol": symbol})
        response = await _send_request(
            self._config,
            self._transport,
            HttpRequest(
                method="GET",
                url=(
                    f"{_base_url(self._config)}/accounts/{quote(account_id, safe='')}"
                    f"/loan-packages?{params}"
                ),
                headers=_api_headers(self._config),
            ),
        )
        return RawPayload(source="dnse", data=_expect_object(response.body))


class DnseTradingPositionsService:
    def __init__(
        self,
        broker: BrokerBase,
        config: DnseConfig,
        transport: HttpTransport,
    ) -> None:
        self._broker = broker
        self._config = config
        self._transport = transport

    async def list_positions(self, account_id: str) -> list[Position]:
        self._broker.require_capability(Capability.TRADING_POSITIONS_LIST)
        params = urlencode(
            {"marketType": self._config.market_type, "pageSize": self._config.positions_page_size}
        )
        response = await _send_request(
            self._config,
            self._transport,
            HttpRequest(
                method="GET",
                url=(
                    f"{_base_url(self._config)}/accounts/{quote(account_id, safe='')}"
                    f"/positions?{params}"
                ),
                headers=_api_headers(self._config),
            ),
        )
        return map_positions(_expect_object(response.body))

    async def get_position(self, position_id: str) -> Position:
        self._broker.require_capability(Capability.TRADING_POSITIONS_LIST)
        params = urlencode({"marketType": self._config.market_type})
        response = await _send_request(
            self._config,
            self._transport,
            HttpRequest(
                method="GET",
                url=(
                    f"{_base_url(self._config)}/accounts/positions/"
                    f"{quote(position_id, safe='')}?{params}"
                ),
                headers=_api_headers(self._config),
            ),
        )
        return map_position(_expect_object(response.body))

    async def close_position(self, position_id: str) -> RawPayload:
        self._broker.require_capability(Capability.TRADING_ORDERS_PLACE)
        params = urlencode({"marketType": self._config.market_type})
        response = await _send_request(
            self._config,
            self._transport,
            HttpRequest(
                method="POST",
                url=(
                    f"{_base_url(self._config)}/accounts/positions/"
                    f"{quote(position_id, safe='')}/close?{params}"
                ),
                headers=_trading_headers(self._config, include_trading_token=True),
            ),
        )
        return RawPayload(source="dnse", data=_expect_object(response.body))


class DnseTradingOrdersService:
    def __init__(
        self,
        broker: BrokerBase,
        config: DnseConfig,
        transport: HttpTransport,
    ) -> None:
        self._broker = broker
        self._config = config
        self._transport = transport

    async def place_order(self, request: PlaceOrderRequest) -> PlaceOrderResponse:
        self._broker.require_capability(Capability.TRADING_ORDERS_PLACE)
        response = await self._send(
            HttpRequest(
                method="POST",
                url=self._url("/accounts/orders", include_order_category=True),
                headers=self._headers(include_trading_token=True, include_content_type=True),
                json=self._place_order_body(request),
            )
        )
        return map_place_order_response(_expect_object(response.body))

    async def cancel_order(self, account_id: str, order_id: str) -> None:
        self._broker.require_capability(Capability.TRADING_ORDERS_CANCEL)
        await self._send(
            HttpRequest(
                method="DELETE",
                url=self._order_url(account_id, order_id),
                headers=self._headers(include_trading_token=True),
            )
        )

    async def get_order(self, account_id: str, order_id: str) -> Order:
        self._broker.require_capability(Capability.TRADING_ORDERS_PLACE)
        response = await self._send(
            HttpRequest(
                method="GET",
                url=self._order_url(account_id, order_id),
                headers=self._headers(include_trading_token=False),
            )
        )
        return map_order(_expect_object(response.body))

    async def update_order(
        self,
        account_id: str,
        order_id: str,
        *,
        price: Decimal,
        quantity: int,
    ) -> RawPayload:
        self._broker.require_capability(Capability.TRADING_ORDERS_PLACE)
        response = await self._send(
            HttpRequest(
                method="PUT",
                url=self._order_url(account_id, order_id),
                headers=self._headers(include_trading_token=True, include_content_type=True),
                json={"price": _number(price), "quantity": quantity},
            )
        )
        return RawPayload(source="dnse", data=_expect_object(response.body))

    def _url(self, path: str, *, include_order_category: bool) -> str:
        params = {"marketType": self._config.market_type}
        if include_order_category:
            params["orderCategory"] = self._config.order_category
        return f"{self._base_url()}{path}?{urlencode(params)}"

    def _order_url(self, account_id: str, order_id: str) -> str:
        path = f"/accounts/{quote(account_id, safe='')}/orders/{quote(order_id, safe='')}"
        return self._url(path, include_order_category=True)

    def _base_url(self) -> str:
        return _base_url(self._config)

    def _headers(
        self, *, include_trading_token: bool, include_content_type: bool = False
    ) -> dict[str, str]:
        headers = _api_headers(self._config)
        if include_trading_token and self._config.trading_token:
            headers["trading-token"] = self._config.trading_token
        if include_content_type:
            headers["Content-Type"] = "application/json"
        return headers

    def _place_order_body(self, request: PlaceOrderRequest) -> dict[str, object]:
        body: dict[str, object] = {
            "accountNo": request.account_id,
            "orderType": _dnse_order_type(request.order_type),
            "price": _number(request.price),
            "quantity": int(request.quantity),
            "side": _dnse_side(request.side),
            "symbol": request.symbol,
        }
        if self._config.loan_package_id is not None:
            body["loanPackageId"] = self._config.loan_package_id
        return body

    async def _send(self, request: HttpRequest) -> HttpResponse:
        return await _send_request(self._config, self._transport, request)


def _base_url(config: DnseConfig) -> str:
    return (config.base_url or "https://openapi.dnse.com.vn").rstrip("/")


def _api_headers(config: DnseConfig) -> dict[str, str]:
    headers: dict[str, str] = {}
    if config.api_key:
        headers["X-API-Key"] = config.api_key
    return headers


def _trading_headers(
    config: DnseConfig,
    *,
    include_trading_token: bool,
    include_content_type: bool = False,
) -> dict[str, str]:
    headers = _api_headers(config)
    if include_trading_token and config.trading_token:
        headers["trading-token"] = config.trading_token
    if include_content_type:
        headers["Content-Type"] = "application/json"
    return headers


def _market_order_query(config: DnseConfig) -> str:
    return urlencode({"marketType": config.market_type, "orderCategory": config.order_category})


async def _send_request(
    config: DnseConfig, transport: HttpTransport, request: HttpRequest
) -> HttpResponse:
    signer = DnseAuth(config).signer()
    if signer is not None:
        request = signer.sign(request)
    response = await transport.send(request)
    if response.status_code >= 400:
        body = response.body if isinstance(response.body, dict) else {}
        raise BrokerRejectedError(
            str(body.get("message") or f"DNSE request failed with status {response.status_code}"),
            broker="dnse",
            code=str(body.get("code")) if body.get("code") is not None else None,
            raw=response.body,
        )
    return response


def _expect_object(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError("Expected DNSE response body to be a JSON object")
    return value


def _dnse_side(side: OrderSide) -> str:
    if side == OrderSide.BUY:
        return "NB"
    if side == OrderSide.SELL:
        return "NS"
    raise ValueError(f"Unsupported order side: {side}")


def _dnse_order_type(order_type: OrderType) -> str:
    if order_type == OrderType.LIMIT:
        return "LO"
    if order_type == OrderType.MARKET:
        return "MTL"
    raise ValueError(f"Unsupported order type: {order_type}")


def _number(value: Decimal | None) -> int | float | None:
    if value is None:
        return None
    if value == value.to_integral_value():
        return int(value)
    return float(value)
