from datetime import datetime, timezone
from urllib.parse import quote, urlencode

from vnbrokers.brokers.dnse.config import DnseConfig
from vnbrokers.brokers.dnse.mapper import map_candles, map_quote, map_symbols
from vnbrokers.brokers.dnse.trading import _api_headers, _base_url, _expect_object, _send_request
from vnbrokers.core.broker import BrokerBase
from vnbrokers.core.capability import Capability
from vnbrokers.domain.candle import Candle
from vnbrokers.domain.quote import Quote
from vnbrokers.domain.raw import RawPayload
from vnbrokers.domain.symbol import Symbol
from vnbrokers.transport.http import HttpRequest, HttpTransport


class DnseMarketDataSymbolsService:
    def __init__(self, broker: BrokerBase, config: DnseConfig, transport: HttpTransport) -> None:
        self._broker = broker
        self._config = config
        self._transport = transport

    async def list_symbols(
        self,
        symbol: str | None = None,
        *,
        market_id: str | None = None,
        security_group_id: str | None = None,
        index_name: str | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> list[Symbol]:
        self._broker.require_capability(Capability.MARKETDATA_SYMBOLS_LIST)
        params: dict[str, object] = {}
        if symbol is not None:
            params["symbol"] = symbol
        if market_id is not None:
            params["marketId"] = market_id
        if security_group_id is not None:
            params["securityGroupId"] = security_group_id
        if index_name is not None:
            params["indexName"] = index_name
        params["limit"] = limit if limit is not None else self._config.market_data_symbol_limit
        if page is not None:
            params["page"] = page

        response = await _send_request(
            self._config,
            self._transport,
            HttpRequest(
                method="GET",
                url=f"{_base_url(self._config)}/instruments?{urlencode(params)}",
                headers=_api_headers(self._config),
            ),
        )
        return map_symbols(_expect_object(response.body))

    async def get_security_definition(
        self, symbol: str, *, board_id: str | None = None
    ) -> RawPayload:
        self._broker.require_capability(Capability.MARKETDATA_SYMBOLS_LIST)
        params = urlencode({"boardId": board_id or self._config.market_data_board_id})
        response = await _send_request(
            self._config,
            self._transport,
            HttpRequest(
                method="GET",
                url=f"{_base_url(self._config)}/price/{quote(symbol, safe='')}/secdef?{params}",
                headers=_api_headers(self._config),
            ),
        )
        return RawPayload(source="dnse", data=response.body)

    async def get_working_dates(self) -> RawPayload:
        self._broker.require_capability(Capability.MARKETDATA_SYMBOLS_LIST)
        response = await _send_request(
            self._config,
            self._transport,
            HttpRequest(
                method="GET",
                url=f"{_base_url(self._config)}/market/working-dates",
                headers=_api_headers(self._config),
            ),
        )
        return RawPayload(source="dnse", data=response.body)


class DnseMarketDataQuotesService:
    def __init__(self, broker: BrokerBase, config: DnseConfig, transport: HttpTransport) -> None:
        self._broker = broker
        self._config = config
        self._transport = transport

    async def get_quote(self, symbol: str, *, board_id: str | None = None) -> Quote:
        self._broker.require_capability(Capability.MARKETDATA_QUOTES)
        params = urlencode({"boardId": board_id or self._config.market_data_board_id})
        response = await _send_request(
            self._config,
            self._transport,
            HttpRequest(
                method="GET",
                url=(
                    f"{_base_url(self._config)}/price/{quote(symbol, safe='')}"
                    f"/trades/latest?{params}"
                ),
                headers=_api_headers(self._config),
            ),
        )
        return map_quote(symbol, _expect_object(response.body))

    async def get_price_trades(
        self,
        symbol: str,
        *,
        from_time: int,
        to_time: int,
        board_id: str | None = None,
        limit: int | None = None,
    ) -> RawPayload:
        self._broker.require_capability(Capability.MARKETDATA_QUOTES)
        params: dict[str, object] = {
            "boardId": board_id or self._config.market_data_board_id,
            "from": from_time,
            "to": to_time,
        }
        if limit is not None:
            params["limit"] = limit
        response = await _send_request(
            self._config,
            self._transport,
            HttpRequest(
                method="GET",
                url=(
                    f"{_base_url(self._config)}/price/{quote(symbol, safe='')}"
                    f"/trades?{urlencode(params)}"
                ),
                headers=_api_headers(self._config),
            ),
        )
        return RawPayload(source="dnse", data=response.body)

    async def get_close_price(self, symbol: str, *, board_id: str | None = None) -> RawPayload:
        self._broker.require_capability(Capability.MARKETDATA_QUOTES)
        params = urlencode({"boardId": board_id or self._config.market_data_board_id})
        response = await _send_request(
            self._config,
            self._transport,
            HttpRequest(
                method="GET",
                url=f"{_base_url(self._config)}/price/{quote(symbol, safe='')}/close?{params}",
                headers=_api_headers(self._config),
            ),
        )
        return RawPayload(source="dnse", data=response.body)


class DnseMarketDataCandlesService:
    def __init__(self, broker: BrokerBase, config: DnseConfig, transport: HttpTransport) -> None:
        self._broker = broker
        self._config = config
        self._transport = transport

    async def get_candles(
        self,
        symbol: str,
        interval: str,
        *,
        from_time: int | None = None,
        to_time: int | None = None,
        market_type: str | None = None,
    ) -> list[Candle]:
        self._broker.require_capability(Capability.MARKETDATA_CANDLES)
        to_value = to_time if to_time is not None else int(datetime.now(timezone.utc).timestamp())
        from_value = (
            from_time if from_time is not None else to_value - self._config.candle_lookback_seconds
        )
        params = urlencode(
            {
                "symbol": symbol,
                "type": market_type or self._config.candle_market_type,
                "resolution": interval,
                "from": from_value,
                "to": to_value,
            }
        )
        response = await _send_request(
            self._config,
            self._transport,
            HttpRequest(
                method="GET",
                url=f"{_base_url(self._config)}/price/ohlc?{params}",
                headers=_api_headers(self._config),
            ),
        )
        return map_candles(symbol, interval, _expect_object(response.body))
