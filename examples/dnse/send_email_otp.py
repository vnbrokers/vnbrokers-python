import asyncio
import os

from vnbrokers.brokers.dnse import DnseBroker, DnseConfig


async def main() -> None:
    broker = DnseBroker(
        DnseConfig(
            api_key=os.getenv("DNSE_API_KEY"),
            api_secret=os.getenv("DNSE_API_SECRET"),
        )
    )
    payload = await broker.auth.send_email_otp()
    print(payload.data)


if __name__ == "__main__":
    asyncio.run(main())
