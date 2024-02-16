import asyncio

from pytoncenter import get_client
from pytoncenter.v3.models import *


async def main():
    client = get_client(version="v3", network="testnet")
    my_address = "0QC8zFHM8LCMp9Xs--w3g9wmf7RwuDgJcQtV-oHZRSCqQXmw"
    account = await client.get_account(GetAccountRequest(address=my_address))
    jetton_wallets = await client.get_jetton_wallets(GetJettonWalletsRequest(owner_address=my_address, limit=10))
    masters = await client.multicall({w.address: client.get_jetton_masters(w.jetton) for w in jetton_wallets})
    print("=== Account Info ===")
    print(" -", "Symbol", "TON", "Balance:", account.balance / 1e9)
    print("=== Jetton Wallets ===")
    for wallet in jetton_wallets:
        jetton = masters.get(wallet.address, None)
        if jetton is None:
            continue
        content = jetton.jetton_content
        symbol = content.symbol if content else "unknown"
        decimals = (content.decimals if content else 0) or 9
        print(" -", "Symbol", symbol, "Balance", wallet.balance / 10**decimals)


if __name__ == "__main__":
    asyncio.run(main())
