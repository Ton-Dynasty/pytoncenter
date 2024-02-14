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

### Example 1. Decode Jetton Get Method Result (V3)

Here is an example for decoding get method by declaring the decoder and Type of the field explicitly. Decoder will decode the result based on the type of the field. If you are not sure about the type of the field, you can use AutoDecoder to decode the result.

```python
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
    assert account_info.status == "active", "Account is not active"

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


if __name__ == "__main__":
    asyncio.run(main())
```

You may get the following jetton data in the console:

```bash
OrderedDict([('total_supply', 5000000000),
             ('mintable', True),
             ('admin_address', EQC8zFHM8LCMp9Xs--w3g9wmf7RwuDgJcQtV-oHZRSCqQZ__),
             ('jetton_content', <CellSlice [9] bits, [1] refs, [A21FCFE4756B6AD7A1E88E65483CCDAB3BBBD9F8AEF5F5060C5FC8A36737AC36] hash>),
             ('jetton_wallet_code', 'b5ee9c7241022501000a......'),])
```

If you use AutoDecoder, you may get the following result:

```bash
OrderedDict([('idx_0', 5000000000),
             ('idx_1', -1), # Because auto decoder does not know the type, it will decode the result as number
             ('idx_2', EQC8zFHM8LCMp9Xs--w3g9wmf7RwuDgJcQtV-oHZRSCqQZ__), # Address field will automatically decode to Address object
             ('idx_3', 'b5ee9c7241022501000a......'), # Cell and Slice will apply b64decode to hex string
             ('idx_4', 'b5ee9c7241022501000a......'),])
```

However, for jetton data, there is a more efficient way to retreive the result by V3 API.

```python
client = get_client(version="v3", network="testnet")
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
```

The output will be:

```bash
Total Supply:  5000000000
Mintable:  True
last transaction lt:  19051958000005
Jetton content - Symbol:  USDT
Jetton content - Name:  USDT
Jetton content - Decimals:  6
Jetton content - Image:  https://coinhere.io/wp-content/uploads/2020/08/Tether-USDT-icon-1.png
```

### Example 2. Obtain a Transaction Flow (V2)

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
