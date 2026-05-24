import json
from decimal import Decimal
from pathlib import Path

from vnbrokers.brokers.dnse.mapper import map_accounts, map_balance, map_positions


FIXTURE_DIR = Path(__file__).parents[2] / "fixtures" / "dnse"


def _load_fixture(name: str) -> dict[str, object]:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_map_accounts_preserves_customer_context_and_raw_payload() -> None:
    accounts = map_accounts(_load_fixture("get_accounts_200.json"))

    assert [account.account_id for account in accounts] == ["000123", "000123D"]
    assert accounts[0].broker == "dnse"
    assert accounts[0].display_name == "Nguyen Van A"
    assert accounts[0].raw is not None
    assert accounts[0].raw.source == "dnse"
    assert accounts[0].raw.data["custodyCode"] == "064C000123"


def test_map_balance_uses_stock_cash_fields_for_normalized_values() -> None:
    balance = map_balance("000123", _load_fixture("get_balances_200.json"))

    assert balance.account_id == "000123"
    assert balance.cash_available == Decimal("12500000")
    assert balance.cash_total == Decimal("15000000")
    assert balance.buying_power == Decimal("12500000")
    assert balance.currency == "VND"
    assert balance.raw is not None
    assert balance.raw.data["derivative"]["remainSecure"] == 3000000


def test_map_positions_uses_open_quantity_and_market_price() -> None:
    positions = map_positions(_load_fixture("get_positions_200.json"))

    assert len(positions) == 1
    position = positions[0]
    assert position.account_id == "000123D"
    assert position.symbol == "VN30F2506"
    assert position.quantity == Decimal("3")
    assert position.available_quantity == Decimal("3")
    assert position.average_price == Decimal("1200.5")
    assert position.market_value == Decimal("3630")
    assert position.raw is not None
    assert position.raw.data["marketType"] == "DERIVATIVE"
