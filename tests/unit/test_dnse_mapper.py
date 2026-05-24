from vnbrokers.brokers.dnse.dto import DnseOrderEventDTO
from vnbrokers.brokers.dnse.mapper import map_order_event
from vnbrokers.domain.enums import OrderStatus


def test_dnse_order_event_mapper_preserves_unknown_status_and_raw_payload() -> None:
    raw = {"orderId": "OID001", "orderStatus": "BROKER_NEW_STATUS"}
    dto = DnseOrderEventDTO(
        account_id="ACC001",
        order_id="OID001",
        symbol="FPT",
        status="BROKER_NEW_STATUS",
        filled_quantity="10",
        received_at="2026-05-23T00:00:00Z",
        raw=raw,
    )

    event = map_order_event(dto)

    assert event.broker == "dnse"
    assert event.status == OrderStatus.UNKNOWN
    assert event.raw_status == "BROKER_NEW_STATUS"
    assert event.raw.source == "dnse"
    assert event.raw.data is raw
