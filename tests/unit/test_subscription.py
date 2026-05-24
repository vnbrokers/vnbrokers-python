import pytest

from vnbrokers.realtime.status import ConnectionStatus
from vnbrokers.realtime.subscription import QueueSubscription


@pytest.mark.asyncio
async def test_queue_subscription_yields_events_and_closes() -> None:
    subscription = QueueSubscription[int]()

    subscription.publish_event(1)
    subscription.publish_status(ConnectionStatus.SUBSCRIBED)

    events = subscription.events()
    statuses = subscription.status()

    assert await anext(events) == 1
    assert await anext(statuses) == ConnectionStatus.SUBSCRIBED

    await subscription.close()

    assert subscription.closed
