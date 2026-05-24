import json
from decimal import Decimal
from pathlib import Path

from vnbrokers.brokers.dnse.mapper import map_order, map_place_order_response
from vnbrokers.domain.enums import OrderSide, OrderStatus, OrderType


def load_fixture(name: str) -> dict[str, object]:
    return json.loads(Path("tests/fixtures/dnse", name).read_text(encoding="utf-8"))


def test_map_place_order_response_preserves_raw_payload() -> None:
    raw = load_fixture("place_order_200.json")

    response = map_place_order_response(raw)

    assert response.order_id == "116"
    assert response.status == OrderStatus.FILLED
    assert response.raw is not None
    assert response.raw.source == "dnse"
    assert response.raw.data is raw


def test_map_order_maps_dnse_side_type_status_and_decimal_values() -> None:
    raw = load_fixture("get_order_200.json")

    order = map_order(raw)

    assert order.broker == "dnse"
    assert order.account_id == "000123"
    assert order.order_id == "116"
    assert order.symbol == "VN30F2506"
    assert order.side == OrderSide.SELL
    assert order.order_type == OrderType.LIMIT
    assert order.status == OrderStatus.PENDING
    assert order.quantity == Decimal("1")
    assert order.price == Decimal("1201.0")
    assert order.raw is not None
    assert order.raw.data is raw
