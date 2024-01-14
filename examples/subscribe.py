from pytoncenter import AsyncTonCenterClient
import asyncio


async def main():
    client = AsyncTonCenterClient(network="testnet")
    async for tx in client.subscribeTx("kQA_NyEP4fSvLS7hzr2z7SKL5NGa67JrykHJjOrvS6XwtoXa", interval=1):
        print(tx["transaction_id"])

if __name__ == "__main__":
    asyncio.run(main())