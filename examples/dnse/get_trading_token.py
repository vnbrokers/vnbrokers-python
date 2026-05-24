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
    payload = await broker.auth.get_trading_token(
        otp_type=os.getenv("DNSE_OTP_TYPE", "email_otp"),
        passcode=os.getenv("DNSE_PASSCODE", ""),
    )
    print(payload.data)


if __name__ == "__main__":
    asyncio.run(main())
