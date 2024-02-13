import asyncio
from pprint import pprint

from pytoncenter import get_client
from pytoncenter.v3.models import *


async def A():
    return "A"


async def B():
    return 2


async def C():
    return ["c"]


async def main():
    client = get_client(version="v3", network="testnet")
    results = await client.multicall(
        {
            "A": A(),
            "B": B(),
            "C": C(),
        }
    )
    pprint(results)

    print("=========================================")

    results = await client.multicall(
        [
            A(),
            B(),
            C(),
        ]
    )
    pprint(results)

    print("=========================================")

    results = await client.multicall(
        {
            "get_account": client.get_account(GetAccountRequest(address="kQA_NyEP4fSvLS7hzr2z7SKL5NGa67JrykHJjOrvS6XwtoXa")),
            "get_jetton_wallet": client.get_jetton_wallets(GetJettonWalletsRequest(address="kQA_NyEP4fSvLS7hzr2z7SKL5NGa67JrykHJjOrvS6XwtoXa")),
            "get_jetton_master": client.get_jetton_masters(GetJettonMastersRequest(address="kQBqSpvo4S87mX9tjHaG4zhYZeORhVhMapBJpnMZ64jhrP-A")),
            "get_adjacent_txs": client.get_adjacent_transactions(GetAdjacentTransactionsRequest(hash="d3c52b311b1e2a317521ed4cc9b60ebcb48fcca1477fc5c336d2b626a341fd84")),
        }
    )

    pprint(results, width=88)

    print("=========================================")


if __name__ == "__main__":
    asyncio.run(main())
