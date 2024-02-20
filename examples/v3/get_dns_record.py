import asyncio

from pytoncenter import get_client
from pytoncenter.v3.models import *


async def main():
    # DNS only supports mainnet, so you have to use mainnet api key here
    # We set it to empty string to request without api key
    client = get_client(version="v3", network="mainnet", api_key="")
    dns_name = "doge.ton"
    record = await client.get_dns_record(
        GetDNSRecordRequest(
            dns_name=dns_name,
            category="wallet",
        )
    )
    print(f"DNS record for {dns_name} is https://tonviewer.com/{record.address}")


if __name__ == "__main__":
    asyncio.run(main())
