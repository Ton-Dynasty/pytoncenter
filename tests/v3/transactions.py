import pytest

from pytoncenter import AsyncTonCenterClientV3, get_client
from pytoncenter.address import Address
from pytoncenter.utils import create_address_mapping, format_trace
from pytoncenter.v3.models import *

pytest_plugins = ("pytest_asyncio",)


class TestDecoder:
    client: AsyncTonCenterClientV3

    def setup_method(self):
        self.client = get_client(version="v3", network="testnet")

    @pytest.mark.asyncio
    async def test_multicall_masterchain(self):
        client = get_client(version="v3", network="testnet")
        # test not throwing exceptions
        info = await client.get_masterchain_info()
        assert not isinstance(info, Exception)
        state = client.get_masterchain_block_shard_state(GetMasterchainBlockShardStateRequest(seqno=10))
        assert not isinstance(state, Exception)
        shards = client.get_masterchain_block_shards(GetMasterchainBlockShardsRequest(seqno=10, include_mc_block=True))
        assert not isinstance(shards, Exception)

    @pytest.mark.asyncio
    async def test_get_trace_alternative(self):
        trace = await self.client.get_trace_alternative(GetTransactionTraceRequest(hash="84b7c9467a0a24e7a59a5e224e9ef8803563621f4710fe8536ae7803fe245d61", sort="asc"))
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
        assert output

    @pytest.mark.asyncio
    async def test_get_address_book(self):
        book = await self.client.get_address_book(
            GetAddressBookRequest(
                address=[
                    "0QApdUMEOUuHnBo-RSdbikkZZ3qWItZLdXjyff9lN_eS5Zib",
                    "kQCQ1B7B7-CrvxjsqgYT90s7weLV-IJB2w08DBslDdrIXucv",
                    "kQDO_0Z0SuVpqpaNE0dPxUiFCNDpdR4ODW9KQAwgQGwc5wiB",
                    "kQCpk40ub48fvx89vSUjOTRy0vOEEZ4crOPPfLEvg88q1EeH",
                    "kQA0FY6YIacA0MgDlKN_qMQuXVZqL3qStyyaNkVB-svHQqsJ",
                ]
            )
        )
        print(book)
        assert len(book) == 5
