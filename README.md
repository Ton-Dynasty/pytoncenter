# Pytoncenter
[![codecov](https://codecov.io/gh/alan890104/pytoncenter/graph/badge.svg?token=EjDfnQmBiE)](https://codecov.io/gh/alan890104/pytoncenter)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pytoncenter?style=flat)
![GitHub Repo stars](https://img.shields.io/github/stars/alan890104/pytoncenter?style=flat)


## Introduction

Pytoncenter is a [TON Center](https://toncenter.com/) client with type hints that introduces advanced features such as **address subscriptions**, **obtaining transaction flows** similar to TON Viewer, **parallel processing of multiple calls**, and **robust debug tools**. Developers can use this package to create TON data analysis platforms, Dapp backends, and other services with enhanced functionality and efficiency.

## Quick Start

### 1. Install the package

To get started, install Pytoncenter using pip:

```bash
pip3 install pytoncenter
```

### 2. Export the TONCENTER_API_KEY

To use the TON Center API, you need to obtain an API key from the [TON Center](https://toncenter.com/). After obtaining the API key from [@tonapibot](https://t.me/tonapibot), export it as an environment variable:

```bash
export TONCENTER_API_KEY=your_api_key
```

### 2. Obtain a Transaction Flow

The following example demonstrates how to obtain the transaction flow for a specified transaction. This transaction is associated with a contract deployed using the [TON Dynasty Contract Jetton Template](https://github.com/Ton-Dynasty/tondynasty-contracts/blob/main/contracts/jetton_example.tact).

- Contract Address on [Testnet TON Viewer](https://testnet.tonviewer.com/kQAreQ23eabjRO5glLCbhZ4KxQ9SOIjtw2eM2PuEXXhIZeh3)
- JettonMint Message Transaction on [Testnet TON Viewer](https://testnet.tonviewer.com/transaction/0f8d6b47a00d4914cb447b34cbce42e9e40c1d188e99ab76f56b0685b3532365)

```python
from pytoncenter import get_client
from pytoncenter.v2.tools import pretty_print_trace_tx, create_named_mapping_func
from pytoncenter.address import Address
import asyncio
import json

async def main():
    # Initialize the client and query a transaction
    client = get_client(version="v2", network="testnet")
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

## Examples (V3)
1. [Get Transaction Traces] - Waiting for TONCENTER to fix their api
2. [Decode Jetton Get Method Result](./examples/v3/decode_jetton_data.py)
3. [Decode Custom Get Method Result](./examples/v3/decode_custom_data.py)
4. [Multicall](./examples/v3/multicall.py)
5. [Subscribe transactions for address](./examples/v3/subscribe_jetton_wallet.py)

## Examples (V2)
1. [Get Transaction Traces](./examples/v2/transaction_trace.py)
2. [Decode Jetton Get Method Result](./examples/v2/decode_jetton_data.py)
3. [Decode Custom Get Method Result](./examples/v2/decode_custom_data.py)
4. [Execute Parallelly](./examples/v2/multicall.py)
5. [Subscribe transactions for address](./examples/v2/subscribe_jetton_wallet.py)

## Examples (Address)
1. [Address Parser](./examples/v2/address.py)


## Development Guide

Please refer to the [Development Guide](./docs/dev.md) for more information on how to contribute to this project.
