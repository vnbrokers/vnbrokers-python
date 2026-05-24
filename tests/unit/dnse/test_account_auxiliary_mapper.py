import json
from decimal import Decimal
from pathlib import Path

from vnbrokers.brokers.dnse.mapper import map_order_history, map_orders, map_position
from vnbrokers.domain.enums import OrderStatus


FIXTURE_DIR = Path(__file__).parents[2] / "fixtures" / "dnse"


def _load_fixture(name: str) -> dict[str, object]:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_map_orders_maps_current_account_orders() -> None:
    orders = map_orders(_load_fixture("get_orders_200.json"))

    assert len(orders) == 1
    assert orders[0].order_id == "42"
    assert orders[0].account_id == "0001179019"
    assert orders[0].status == OrderStatus.PARTIALLY_FILLED
    assert orders[0].raw is not None
    assert orders[0].raw.data["leaveQuantity"] == 7


def test_map_order_history_maps_history_data_items() -> None:
    orders = map_order_history(_load_fixture("get_orders_history_200.json"))

    assert len(orders) == 1
    assert orders[0].order_id == "42"
    assert orders[0].status == OrderStatus.FILLED
    assert orders[0].raw is not None
    assert orders[0].raw.data["fillQuantity"] == 10


def test_map_position_maps_single_position_payload() -> None:
    position = map_position(_load_fixture("get_position_200.json"))

    assert position.account_id == "0001179019"
    assert position.symbol == "41I1G5000"
    assert position.quantity == Decimal("23")
    assert position.average_price == Decimal("2036.78986")
    assert position.market_value == Decimal("44063.4")
    assert position.raw is not None
    assert position.raw.data["loanPackageId"] == 2278
