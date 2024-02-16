import asyncio

from pytoncenter import get_client
from pytoncenter.v3.models import *

"""
Take this transaction as example:
https://testnet.tonviewer.com/transaction/84b7c9467a0a24e7a59a5e224e9ef8803563621f4710fe8536ae7803fe245d61

The output transactions should be:
1. ae4bf0c6a14506c6440e063d779768d464cabc87b5f552ba04ed31e9d79d9f93
2. 754ae0725ab41d3c627e8ca992e250cbc3db239e82d02d93a7b4aebba55ba358
"""


async def main():
    client = get_client(version="v3", network="testnet")
    tx = await client.get_transactions(GetTransactionByHashRequest(hash="84b7c9467a0a24e7a59a5e224e9ef8803563621f4710fe8536ae7803fe245d61"))
    assert tx is not None
    for out_msg in tx.out_msgs:
        txs = await client.get_transaction_by_message(GetTransactionByMessageRequest(direction="in", msg_hash=out_msg.hash))
        for _tx in txs:
            print("Out Msg Hash", out_msg.hash, " -> Transaction hash", _tx.hash)


if __name__ == "__main__":
    asyncio.run(main())
