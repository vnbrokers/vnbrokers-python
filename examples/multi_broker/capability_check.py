from vnbrokers.brokers.dnse import DnseBroker, DnseConfig
from vnbrokers.core.capability import Capability


def main() -> None:
    broker = DnseBroker(DnseConfig())
    if broker.supports(Capability.TRADING_REALTIME_ORDERS):
        print("DNSE order stream is available")
    else:
        print("DNSE order stream is unavailable")


if __name__ == "__main__":
    main()
