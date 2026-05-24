import json
from decimal import Decimal
from pathlib import Path

from vnbrokers.brokers.dnse.mapper import map_candles, map_quote, map_symbols


FIXTURE_DIR = Path(__file__).parents[2] / "fixtures" / "dnse"


def _load_fixture(name: str) -> dict[str, object]:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_map_symbols_maps_dnse_instruments_to_domain_symbols() -> None:
    symbols = map_symbols(_load_fixture("get_instruments_200.json"))

    assert len(symbols) == 1
    assert symbols[0].symbol == "ACB"
    assert symbols[0].exchange == "STO"
    assert symbols[0].display_name == "Ngan hang TMCP A Chau"
    assert symbols[0].raw is not None
    assert symbols[0].raw.data["securityGroupId"] == "ST"


def test_map_quote_uses_first_latest_trade() -> None:
    quote = map_quote("ACB", _load_fixture("get_latest_price_trades_200.json"))

    assert quote.symbol == "ACB"
    assert quote.last_price == Decimal("23000")
    assert quote.received_at == "1773183637"
    assert quote.raw is not None
    assert quote.raw.data["trades"][0]["quantity"] == 1000


def test_map_candles_maps_parallel_ohlc_arrays() -> None:
    candles = map_candles("ACB", "15", _load_fixture("get_ohlc_200.json"))

    assert len(candles) == 1
    candle = candles[0]
    assert candle.symbol == "ACB"
    assert candle.interval == "15"
    assert candle.opened_at == "1773657310"
    assert candle.open == Decimal("23000")
    assert candle.high == Decimal("23200")
    assert candle.low == Decimal("22900")
    assert candle.close == Decimal("23100")
    assert candle.volume == Decimal("100000")
    assert candle.raw is not None
    assert candle.raw.data["nextTime"] == 1773831010
