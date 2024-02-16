import asyncio

from pytoncenter import get_client
from pytoncenter.address import Address
from pytoncenter.utils import create_address_mapping, format_trace
from pytoncenter.v3.models import *

"""
Take this transaction as example:
https://testnet.tonviewer.com/transaction/84b7c9467a0a24e7a59a5e224e9ef8803563621f4710fe8536ae7803fe245d61

The output transactions should be the whole trace of the transaction. The source transaction hash is
https://testnet.tonviewer.com/transaction/dc40feab455e86fa0736508febed224891c965ef6cbf55f5ec309247e8d38664
"""


async def main():
    client = get_client(version="v3", network="testnet")
    trace = await client.get_trace_alternative(GetTransactionTraceRequest(hash="84b7c9467a0a24e7a59a5e224e9ef8803563621f4710fe8536ae7803fe245d61", sort="asc"))
    addr_mapping = create_address_mapping(
        {
            Address("0QApdUMEOUuHnBo-RSdbikkZZ3qWItZLdXjyff9lN_eS5Zib"): "Alan Wallet V4",
            Address("kQCQ1B7B7-CrvxjsqgYT90s7weLV-IJB2w08DBslDdrIXucv"): "Alan USD Jetton Wallet",
            Address("kQDO_0Z0SuVpqpaNE0dPxUiFCNDpdR4ODW9KQAwgQGwc5wiB"): "Oracle Jetton Wallet",
            Address("kQCpk40ub48fvx89vSUjOTRy0vOEEZ4crOPPfLEvg88q1EeH"): "Oracle",
            Address("kQA0FY6YIacA0MgDlKN_qMQuXVZqL3qStyyaNkVB-svHQqsJ"): "New Alarm",
        }
    )
    output = format_trace(trace, address_mapping=addr_mapping)
    print(output)


if __name__ == "__main__":
    asyncio.run(main())
