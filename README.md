# Pytoncenter

## Introduction

Pytoncenter is a [TON Center](https://toncenter.com/) client with type hints that introduces advanced features such as **address subscriptions**, **obtaining transaction flows** similar to TON Viewer, **parallel processing of multiple calls**, and **robust debug tools**. Developers can use this package to create TON data analysis platforms, Dapp backends, and other services with enhanced functionality and efficiency.

## Quick Start

### 1. Install the package

To get started, install Pytoncenter using pip:

```bash
pip3 install pytoncenter
```

### 2. Obtain a Transaction Flow

The following example demonstrates how to obtain the transaction flow for a specified transaction. This transaction is associated with a contract deployed using the [TON Dynasty Contract Jetton Template](https://github.com/Ton-Dynasty/tondynasty-contracts/blob/main/contracts/jetton_example.tact).

- Contract Address on [Testnet TON Viewer](https://testnet.tonviewer.com/kQAreQ23eabjRO5glLCbhZ4KxQ9SOIjtw2eM2PuEXXhIZeh3)
- JettonMint Message Transaction on [Testnet TON Viewer](https://testnet.tonviewer.com/transaction/0f8d6b47a00d4914cb447b34cbce42e9e40c1d188e99ab76f56b0685b3532365)

```python
from pytoncenter import AsyncTonCenterClient, Address
import asyncio
import json
from pytoncenter.debug import pretty_print_trace_tx, create_named_mapping_func

async def main():
    # Initialize the client and query a transaction
    client = AsyncTonCenterClient(network="testnet")
    txs = await client.get_transactions(address="kQAreQ23eabjRO5glLCbhZ4KxQ9SOIjtw2eM2PuEXXhIZeh3", hash="Lomkyzxh1WBkxvxZ3cJNS2bAYIPC7dPZA67wDomGM4U=", limit=1)
    tx = txs[0]
    result = await client.trace_tx(tx)
    # Pretty print the transaction trace with name mapping for addresses
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
```

You may get the following output in the console:

```bash
Alan WalletV4R2 -> Jetton Master (Mint:1) [1.0 TON]
└── Jetton Master -> Jetton Wallet (0x178d4519) [0.955002 TON]
    └── Jetton Wallet -> Alan WalletV4R2 (0xd53276db) [0.853806 TON]
```


## Full Examples
1. [Get Transaction Flows](./examples/transaction_flows.py)
2. [Decode Jetton Get Method Result](./examples/decode_jetton_data.py)
3. [Decode Custom Get Method Result](./examples/decode_custom_data.py)
4. [Execute Parallelly](./examples/execute_many.py)
5. [Subscribe transactions for address](./examples/subscribe.py)
6. [Address Parser](./examples/address.py)