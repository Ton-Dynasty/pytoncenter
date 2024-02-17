import asyncio

from pytoncenter import get_client
from pytoncenter.utils import format_trace
from pytoncenter.v3.models import *

"""
Take this transaction as example:
https://testnet.tonviewer.com/transaction/84b7c9467a0a24e7a59a5e224e9ef8803563621f4710fe8536ae7803fe245d61

The output transactions should be:
https://testnet.tonviewer.com/transaction/f5333b49b754376ff96b0d299dc38142b8b5ca1b046f41704a4814b51700c89d
"""


async def main():
    client = get_client(version="v3", network="testnet")
    generator = client.wait_message_exists(
        WaitMessageExistsRequest(
            msg_hash="82CBB53717ACE80D7A1263243F7CA4085C6C0B65A05ABBC41C7BA38D435507DF",
        )
    )
    tx = await anext(generator)
    print("Transaction found", tx.hash)
    trace = await client.get_trace_alternative(GetTransactionTraceRequest(hash=tx.hash))
    fmt_trace = format_trace(trace)
    print(fmt_trace)

    print("================Retry Will Raise 429 Error At Limit=====================")
    # Non-existent message
    generator = client.wait_message_exists(
        WaitMessageExistsRequest(
            msg_hash="82CBB53717",
            max_retry=1,
        )
    )
    try:
        tx = await anext(generator)
        print("Transaction found", tx.hash)
    except Exception as e:
        print("It will raise an error", e)


if __name__ == "__main__":
    asyncio.run(main())
