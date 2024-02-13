from pytoncenter.v2.api import AsyncTonCenterClientV2
from pytoncenter.address import Address
import asyncio
import json
from pytoncenter.v2.tools import pretty_print_trace_tx, create_named_mapping_func


"""
# Subscribe Address
https://testnet.tonviewer.com/kQAreQ23eabjRO5glLCbhZ4KxQ9SOIjtw2eM2PuEXXhIZeh3

# Get Jetton Mint Transaction
https://testnet.tonviewer.com/transaction/0f8d6b47a00d4914cb447b34cbce42e9e40c1d188e99ab76f56b0685b3532365
"""


async def main():
    # Query transaction
    client = AsyncTonCenterClientV2(network="testnet")
    txs = await client.get_transactions(
        address="kQAreQ23eabjRO5glLCbhZ4KxQ9SOIjtw2eM2PuEXXhIZeh3",
        limit=1,
        hash="Lomkyzxh1WBkxvxZ3cJNS2bAYIPC7dPZA67wDomGM4U=",
    )
    tx = txs[0]
    with open("tx.json", "w") as f:
        json.dump(tx, f, indent=2)

    # Get transaction trace
    result = await client.trace_tx(tx)
    with open("tx_trace.json", "w") as f:
        json.dump(result, f, indent=2)

    # Pretty print transaction trace with any formed of address mapping
    named_func = create_named_mapping_func(
        {
            Address("EQC8zFHM8LCMp9Xs--w3g9wmf7RwuDgJcQtV-oHZRSCqQZ__"): "Alan WalletV4R2",
            Address("0:2b790db779a6e344ee6094b09b859e0ac50f523888edc3678cd8fb845d784865"): "Jetton Master",
            Address("kQC40ScRg9_1ob5sjWsdScltrCGu0HARsUnOYQ1esc12588C"): "Jetton Wallet",
        },
        truncate_address=True,
    )
    pretty_print_trace_tx(result, named_func=named_func)


if __name__ == "__main__":
    asyncio.run(main())
