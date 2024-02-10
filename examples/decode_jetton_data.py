from pytoncenter import AsyncTonCenterClient
from pytoncenter.decoder import JettonDataDecoder
import asyncio
from pprint import pprint


async def main():
    client = AsyncTonCenterClient(network="testnet")
    result = await client.run_get_method("kQBqSpvo4S87mX9tjHaG4zhYZeORhVhMapBJpnMZ64jhrP-A", "get_jetton_data", {})
    output = JettonDataDecoder.decode(result)
    pprint(output, width=120)


if __name__ == "__main__":
    asyncio.run(main())
