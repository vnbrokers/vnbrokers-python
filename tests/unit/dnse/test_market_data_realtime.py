from decimal import Decimal

import pytest

from vnbrokers.brokers.dnse.market_data_realtime import (
    build_market_data_channel,
    build_market_data_subscribe_message,
    build_market_data_unsubscribe_message,
    build_stream_ping_message,
    decode_candle_stream_message,
    decode_market_data_raw_message,
    decode_tick_stream_message,
    decode_top_price_stream_message,
    publish_candle_stream_message,
    publish_tick_stream_message,
    publish_top_price_stream_message,
)
from vnbrokers.market_data.realtime import SubscribeSymbolRequest
from vnbrokers.realtime.subscription import QueueSubscription


def test_build_market_data_channels_match_names() -> None:
    assert build_market_data_channel("tick", board_id="G1") == "tick.G1.json"
    assert build_market_data_channel("tick_extra", board_id="G1") == "tick_extra.G1.json"
    assert build_market_data_channel("top_price", board_id="G1") == "top_price.G1.json"
    assert build_market_data_channel("expected_price", board_id="G1") == "expected_price.G1.json"
    assert build_market_data_channel("security_definition", board_id="G1") == (
        "security_definition.G1.json"
    )
    assert build_market_data_channel("foreign", board_id="G1") == "foreign.G1.json"
    assert build_market_data_channel("ohlc", resolution="1") == "ohlc.1.json"
    assert build_market_data_channel("ohlc_closed", resolution="1") == "ohlc_closed.1.json"
    assert build_market_data_channel("market_index", index_name="VN30") == "market_index.VN30.json"


def test_build_market_data_channels_support_msgpack_encoding() -> None:
    assert (
        build_market_data_channel("top_price", board_id="G1", encoding="msgpack")
        == "top_price.G1.msgpack"
    )
    assert build_market_data_channel("ohlc", resolution="1", encoding="msgpack") == (
        "ohlc.1.msgpack"
    )
    assert (
        build_market_data_channel("market_index", index_name="VN30", encoding="msgpack")
        == "market_index.VN30.msgpack"
    )


def test_build_market_data_stream_messages_match_collection_shape() -> None:
    assert build_market_data_subscribe_message("tick.G1.json", ["HPG"]) == {
        "action": "subscribe",
        "channels": [{"name": "tick.G1.json", "symbols": ["HPG"]}],
    }
    assert build_market_data_subscribe_message("tick.G1.json", ["HPG", "SSI"]) == {
        "action": "subscribe",
        "channels": [{"name": "tick.G1.json", "symbols": ["HPG", "SSI"]}],
    }
    assert build_market_data_unsubscribe_message("tick.G1.json", ["HPG"]) == {
        "action": "unsubscribe",
        "channels": [{"name": "tick.G1.json", "symbols": ["HPG"]}],
    }
    assert build_market_data_subscribe_message("security_definition.G1.json", None) == {
        "action": "subscribe",
        "channels": [{"name": "security_definition.G1.json"}],
    }
    assert build_market_data_subscribe_message("market_index.VN30.json") == {
        "action": "subscribe",
        "channels": [{"name": "market_index.VN30.json"}],
    }
    assert build_stream_ping_message() == {"action": "ping"}


def test_subscribe_symbol_request_supports_single_multiple_and_all_symbols() -> None:
    assert SubscribeSymbolRequest(symbol="HPG").symbol_list() == ["HPG"]
    assert SubscribeSymbolRequest(symbols=("HPG", "SSI")).symbol_list() == ["HPG", "SSI"]
    assert SubscribeSymbolRequest.all().symbol_list() is None


def test_subscribe_symbol_request_rejects_ambiguous_symbol_inputs() -> None:
    with pytest.raises(ValueError, match="Use either symbol or symbols"):
        SubscribeSymbolRequest(symbol="HPG", symbols=("SSI",))


def test_decode_tick_stream_message_maps_trade_payload() -> None:
    raw = {
        "T": "t",
        "symbol": "HPG",
        "matchPrice": 27.3,
        "matchQtty": 10,
        "sendingTime": "2026-05-11T02:59:34.989Z",
    }

    tick = decode_tick_stream_message(raw)

    assert tick.symbol == "HPG"
    assert tick.price == Decimal("27.3")
    assert tick.quantity == Decimal("10")
    assert tick.received_at == "2026-05-11T02:59:34.989Z"
    assert tick.raw is not None
    assert tick.raw.data is raw


def test_decode_top_price_stream_message_maps_first_bid_and_offer() -> None:
    raw = {
        "T": "q",
        "symbol": "HPG",
        "bid": [{"price": 27.25, "qtty": 39440}],
        "offer": [{"price": 27.3, "qtty": 14230}],
        "sendingTime": "2026-05-11T03:26:11.100Z",
    }

    top_price = decode_top_price_stream_message(raw)

    assert top_price.symbol == "HPG"
    assert top_price.bid_price == Decimal("27.25")
    assert top_price.bid_quantity == Decimal("39440")
    assert top_price.ask_price == Decimal("27.3")
    assert top_price.ask_quantity == Decimal("14230")
    assert top_price.received_at == "2026-05-11T03:26:11.100Z"


def test_decode_candle_stream_message_maps_ohlc_payload() -> None:
    raw = {
        "T": "b",
        "symbol": "HPG",
        "resolution": "1",
        "time": 1778472960,
        "open": 27.25,
        "high": 27.3,
        "low": 27.25,
        "close": 27.25,
        "volume": 2400,
    }

    candle = decode_candle_stream_message(raw)

    assert candle.symbol == "HPG"
    assert candle.interval == "1"
    assert candle.opened_at == "1778472960"
    assert candle.open == Decimal("27.25")
    assert candle.high == Decimal("27.3")
    assert candle.low == Decimal("27.25")
    assert candle.close == Decimal("27.25")
    assert candle.volume == Decimal("2400")


def test_decode_market_data_raw_message_preserves_payload() -> None:
    raw = {"T": "mi", "indexName": "VNINDEX", "valueIndexes": 1669.38}

    payload = decode_market_data_raw_message(raw)

    assert payload.source == "dnse"
    assert payload.data is raw


def test_publish_market_data_messages_to_queue_subscriptions() -> None:
    tick_subscription: QueueSubscription = QueueSubscription()
    top_price_subscription: QueueSubscription = QueueSubscription()
    candle_subscription: QueueSubscription = QueueSubscription()

    publish_tick_stream_message(
        tick_subscription, {"symbol": "HPG", "matchPrice": 27.3, "matchQtty": 10}
    )
    publish_top_price_stream_message(
        top_price_subscription,
        {"symbol": "HPG", "bid": [{"price": 27.25}], "offer": [{"price": 27.3}]},
    )
    publish_candle_stream_message(
        candle_subscription,
        {
            "symbol": "HPG",
            "resolution": "1",
            "time": 1778472960,
            "open": 27.25,
            "high": 27.3,
            "low": 27.25,
            "close": 27.25,
            "volume": 2400,
        },
    )

    assert not tick_subscription.closed
    assert not top_price_subscription.closed
    assert not candle_subscription.closed
