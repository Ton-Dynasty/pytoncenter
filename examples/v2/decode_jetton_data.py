from pytoncenter.v2.api import AsyncTonCenterClientV2
from pytoncenter.decoder import JettonDataDecoder
import asyncio
from pprint import pprint


async def main():
    client = AsyncTonCenterClientV2(network="testnet")
    result = await client.run_get_method("kQBqSpvo4S87mX9tjHaG4zhYZeORhVhMapBJpnMZ64jhrP-A", "get_jetton_data", {})
    decoder = JettonDataDecoder()
    output = decoder.decode(result)
    pprint(output, width=120)


if __name__ == "__main__":
    asyncio.run(main())
