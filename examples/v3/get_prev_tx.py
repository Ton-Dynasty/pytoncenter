import asyncio

from pytoncenter import get_client
from pytoncenter.v3.models import *

"""
Take this transaction as example:
https://testnet.tonviewer.com/transaction/84b7c9467a0a24e7a59a5e224e9ef8803563621f4710fe8536ae7803fe245d61

The output transactions should be:
https://testnet.tonviewer.com/transaction/f5333b49b754376ff96b0d299dc38142b8b5ca1b046f41704a4814b51700c89d
"""


async def main():
    client = get_client(version="v3", network="testnet")
    tx = await client.get_transactions(GetTransactionByHashRequest(hash="84b7c9467a0a24e7a59a5e224e9ef8803563621f4710fe8536ae7803fe245d61"))
    assert tx is not None
    txs = await client.get_transaction_by_message(GetTransactionByMessageRequest(direction="out", msg_hash=tx.in_msg.hash))
    for _tx in txs:
        print("Prev Transaction hash", _tx.hash)


if __name__ == "__main__":
    asyncio.run(main())
