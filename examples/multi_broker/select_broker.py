from vnbrokers import create_broker
from vnbrokers.core.broker import Broker


def select_broker(name: str) -> Broker:
    return create_broker(name)


if __name__ == "__main__":
    broker = select_broker("dnse")
    print(broker.name)
