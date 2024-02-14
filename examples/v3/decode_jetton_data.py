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

    print("===============Easier way get jetton data======================")
    jettons = await client.get_jetton_masters(GetJettonMastersRequest(address="kQBqSpvo4S87mX9tjHaG4zhYZeORhVhMapBJpnMZ64jhrP-A"))
    jetton = jettons[0]
    print("Total Supply: ", jetton.total_supply)
    print("Mintable: ", jetton.mintable)
    print("last transaction lt: ", jetton.last_transaction_lt)
    if jetton.jetton_content is not None:
        print("Jetton content - Symbol: ", jetton.jetton_content.symbol)
        print("Jetton content - Name: ", jetton.jetton_content.name)
        print("Jetton content - Decimals: ", jetton.jetton_content.decimals)
        print("Jetton content - Image: ", jetton.jetton_content.image)


if __name__ == "__main__":
    asyncio.run(main())
