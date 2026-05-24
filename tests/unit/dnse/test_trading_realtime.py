from vnbrokers.brokers.dnse.trading_realtime import (
    build_stream_auth_message,
    build_stream_subscribe_orders_message,
    build_stream_subscribe_positions_message,
    decode_order_stream_message,
    decode_position_stream_message,
    publish_position_stream_message,
)
from vnbrokers.domain.enums import OrderStatus
from vnbrokers.realtime.subscription import QueueSubscription


def test_build_stream_auth_message_uses_hmac_sha256_hex_signature() -> None:
    message = build_stream_auth_message(
        api_key="key",
        api_secret="secret",
        timestamp=1710000000,
        nonce="nonce-1",
    )

    assert message == {
        "action": "auth",
        "api_key": "key",
        "signature": "1c828afbb19b0490a2615f637f6c08e103adf1d8c2b82bd5415432f8fefb329b",
        "timestamp": 1710000000,
        "nonce": "nonce-1",
    }


def test_build_stream_subscribe_orders_message_uses_empty_symbols_list() -> None:
    assert build_stream_subscribe_orders_message(market_type="STOCK") == {
        "action": "subscribe",
        "channels": [{"name": "order.STOCK.json", "symbols": []}],
    }


def test_build_stream_subscribe_orders_message_supports_msgpack_encoding() -> None:
    assert build_stream_subscribe_orders_message(market_type="STOCK", encoding="msgpack") == {
        "action": "subscribe",
        "channels": [{"name": "order.STOCK.msgpack", "symbols": []}],
    }


def test_build_stream_subscribe_positions_message_uses_market_type_channel() -> None:
    assert build_stream_subscribe_positions_message(market_type="STOCK") == {
        "action": "subscribe",
        "channels": [{"name": "position.STOCK.json", "symbols": []}],
    }


def test_build_stream_subscribe_positions_message_supports_msgpack_encoding() -> None:
    assert build_stream_subscribe_positions_message(
        market_type="DERIVATIVE", encoding="msgpack"
    ) == {
        "action": "subscribe",
        "channels": [{"name": "position.DERIVATIVE.msgpack", "symbols": []}],
    }


def test_decode_order_stream_message_preserves_raw_payload() -> None:
    raw = {
        "action": "data",
        "type": "order",
        "channel": "orders",
        "data": {
            "accountNo": "000123",
            "id": 116,
            "symbol": "VN30F2506",
            "orderStatus": "FILLED",
            "fillQuantity": 2,
            "createdDate": "2026-05-23T09:15:00Z",
        },
    }

    event = decode_order_stream_message(raw)

    assert event.account_id == "000123"
    assert event.order_id == "116"
    assert event.symbol == "VN30F2506"
    assert event.status == OrderStatus.FILLED
    assert event.filled_quantity == "2"
    assert event.raw.data is raw


def test_decode_order_stream_message_maps_live_order_update_envelope() -> None:
    raw = {
        "T": "eo",
        "action": "order_update",
        "event": "canceled",
        "order": {
            "accountNo": "0001179019",
            "averagePrice": 0,
            "canceledQuantity": 1,
            "createdDate": "2026-05-23T14:19:56.529Z",
            "fillQuantity": 0,
            "id": "16701",
            "investorId": "1001700768",
            "leaveQuantity": 0,
            "loanPackageId": 1775,
            "marketType": "STOCK",
            "modifiedDate": "2026-05-23T14:37:42.719Z",
            "orderStatus": "Canceled",
            "orderType": "LO",
            "price": 21300,
            "priceSecure": 21300,
            "quantity": 1,
            "side": "NB",
            "symbol": "ACB",
            "transDate": "2026-05-25T00:00:00Z",
        },
        "sequence": 8,
        "timestamp": 1779547062728,
    }

    event = decode_order_stream_message(raw)

    assert event.account_id == "0001179019"
    assert event.order_id == "16701"
    assert event.symbol == "ACB"
    assert event.status == OrderStatus.CANCELLED
    assert event.filled_quantity == "0"
    assert event.received_at == "2026-05-23T14:19:56.529Z"
    assert event.raw.data is raw


def test_decode_position_stream_message_maps_dnse_payload() -> None:
    raw = {
        "id": 177796763592657,
        "marketType": "DERIVATIVE",
        "symbol": "41I1G5000",
        "accountNo": "0001179019",
        "status": "OPEN",
        "loanPackageId": 2278,
        "side": "NB",
        "accumulateQuantity": 259,
        "tradeQuantity": 23,
        "closedQuantity": 236,
        "openQuantity": 23,
        "overNightQuantity": 0,
        "costPrice": 2036.78986,
        "marketPrice": 1915.8,
        "breakEvenPrice": 2037.28116,
        "averageClosePrice": 2094.28941,
        "createdDate": "2026-05-05T09:17:50.457893Z",
        "modifiedDate": "2026-05-08T06:51:04.755263Z",
    }

    position = decode_position_stream_message(raw)

    assert position.account_id == "0001179019"
    assert position.symbol == "41I1G5000"
    assert str(position.quantity) == "23"
    assert str(position.average_price) == "2036.78986"
    assert str(position.market_value) == "44063.4"
    assert position.raw is not None
    assert position.raw.data is raw


def test_publish_position_stream_message_to_queue_subscription() -> None:
    subscription: QueueSubscription = QueueSubscription()

    publish_position_stream_message(
        subscription,
        {
            "symbol": "41I1G5000",
            "accountNo": "0001179019",
            "openQuantity": 23,
            "costPrice": 2036.78986,
            "marketPrice": 1915.8,
        },
    )

    assert not subscription.closed
