from pytoncenter import get_client
from pytoncenter.v3.models import *
from pytoncenter.decoder import JettonDataDecoder, AutoDecoder
import asyncio
from pprint import pprint


async def main():
    client = get_client(version="v3", network="testnet")
    req = GetAccountRequest(address="kQBqSpvo4S87mX9tjHaG4zhYZeORhVhMapBJpnMZ64jhrP-A")
    account_info = await client.get_account(req)

    # Check account status is active
    if account_info.status == AccountStatus.active:
        print("Account is active")
    else:
        raise Exception("Account is not active")

    print("=====================================")

    req = RunGetMethodRequest(address="kQBqSpvo4S87mX9tjHaG4zhYZeORhVhMapBJpnMZ64jhrP-A", method="get_jetton_data", stack=[])
    result = await client.run_get_method(req)
    print(result)

    print("=====================================")
    decoder = JettonDataDecoder()
    jetton_data = decoder.decode(result)
    pprint(jetton_data, width=120)

    print("=====================================")
    decoder = AutoDecoder()
    jetton_data = decoder.decode(result)
    pprint(jetton_data, width=120)


if __name__ == "__main__":
    asyncio.run(main())
