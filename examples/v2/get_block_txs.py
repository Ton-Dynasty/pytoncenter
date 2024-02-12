from pytoncenter.v2.api import AsyncTonCenterClientV2
import asyncio
from pprint import pprint


async def main():
    client = AsyncTonCenterClientV2(network="testnet")
    info = await client.get_masterchain_info()
    seqno = info["last"]["seqno"]
    shards = await client.get_shards(seqno)
    basechain = shards["shards"][0]
    txs = await client.get_block_transactions(workchain=basechain["workchain"], shard=basechain["shard"], seqno=basechain["seqno"])
    pprint(txs, width=120)


if __name__ == "__main__":
    asyncio.run(main())
