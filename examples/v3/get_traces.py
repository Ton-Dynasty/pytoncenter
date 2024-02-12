from pytoncenter import get_client
from pytoncenter.v3.models import *
import asyncio
from datetime import datetime
from pytoncenter.address import Address


async def main():
    client = get_client(version="v3", network="testnet")
    req = GetAccountRequest(address="kQCpk40ub48fvx89vSUjOTRy0vOEEZ4crOPPfLEvg88q1EeH")
    account_info = await client.get_account(req)
    print(account_info.status)


if __name__ == "__main__":
    asyncio.run(main())
