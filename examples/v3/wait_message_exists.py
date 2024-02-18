import asyncio

from pytoncenter import get_client
from pytoncenter.utils import format_trace
from pytoncenter.v3.models import *


async def main():
    client = get_client(version="v3", network="testnet")
    
    # sent_message = await client.send_message(ExternalMessage())
    # msg_hash = sent_message.message_hash
    # Take msg_hash = "82CBB53717ACE80D7A1263243F7CA4085C6C0B65A05ABBC41C7BA38D435507DF" as example

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
