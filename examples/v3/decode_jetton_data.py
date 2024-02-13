import asyncio
from pprint import pprint

from pytoncenter import get_client
from pytoncenter.decoder import AutoDecoder, JettonDataDecoder
from pytoncenter.v3.models import *


async def main():
    client = get_client(version="v3", network="testnet")
    req = GetAccountRequest(address="kQBqSpvo4S87mX9tjHaG4zhYZeORhVhMapBJpnMZ64jhrP-A")
    account_info = await client.get_account(req)

    # Check account status is active
    if account_info.status == "active":
        print("Account is active")
    else:
        raise Exception("Account is not active")

    print("=====================================")

    req = RunGetMethodRequest(address="kQBqSpvo4S87mX9tjHaG4zhYZeORhVhMapBJpnMZ64jhrP-A", method="get_jetton_data", stack=[])
    result = await client.run_get_method(req)
    print(result)

    print("===============Jetton Decoder======================")
    decoder = JettonDataDecoder()
    jetton_data = decoder.decode(result)
    pprint(jetton_data, width=120)

    print("===============Auto Decoder======================")
    decoder = AutoDecoder()
    jetton_data = decoder.decode(result)
    pprint(jetton_data, width=120)


if __name__ == "__main__":
    asyncio.run(main())
