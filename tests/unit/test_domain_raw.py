from vnbrokers.domain.enums import OrderStatus
from vnbrokers.domain.order_event import OrderEvent
from vnbrokers.domain.raw import RawPayload


def test_order_event_preserves_raw_payload() -> None:
    raw_data = {"orderStatus": "BROKER_NEW_STATUS"}
    raw = RawPayload(source="dnse", data=raw_data)

    event = OrderEvent(
        broker="dnse",
        account_id="ACC001",
        order_id="OID001",
        symbol="FPT",
        status=OrderStatus.UNKNOWN,
        raw_status="BROKER_NEW_STATUS",
        filled_quantity="0",
        received_at="2026-05-23T00:00:00Z",
        raw=raw,
    )

    assert event.raw is raw
    assert event.raw.data is raw_data
    assert event.raw_status == "BROKER_NEW_STATUS"
