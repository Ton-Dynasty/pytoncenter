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
    async def test_get_next_transaction_by_message(self):
        """
        Take this transaction as example:
        https://testnet.tonviewer.com/transaction/84b7c9467a0a24e7a59a5e224e9ef8803563621f4710fe8536ae7803fe245d61

        The output transactions should be:
        1. ae4bf0c6a14506c6440e063d779768d464cabc87b5f552ba04ed31e9d79d9f93
        2. 754ae0725ab41d3c627e8ca992e250cbc3db239e82d02d93a7b4aebba55ba358
        """
        client = get_client(version="v3", network="testnet")
        tx = await client.get_transactions(GetTransactionByHashRequest(hash="84b7c9467a0a24e7a59a5e224e9ef8803563621f4710fe8536ae7803fe245d61"))
        assert tx is not None
        txhashes = set()
        for out_msg in tx.out_msgs:
            txs = await client.get_transaction_by_message(GetTransactionByMessageRequest(direction="in", msg_hash=out_msg.hash))
            assert len(txs) == 1
            txhashes.add(txs[0].hash.lower())
        assert txhashes == {"ae4bf0c6a14506c6440e063d779768d464cabc87b5f552ba04ed31e9d79d9f93", "754ae0725ab41d3c627e8ca992e250cbc3db239e82d02d93a7b4aebba55ba358"}

    @pytest.mark.asyncio
    async def test_get_prev_transaction_by_message(self):
        """
        Take this transaction as example:
        https://testnet.tonviewer.com/transaction/84b7c9467a0a24e7a59a5e224e9ef8803563621f4710fe8536ae7803fe245d61

        The output transactions should be:
        https://testnet.tonviewer.com/transaction/f5333b49b754376ff96b0d299dc38142b8b5ca1b046f41704a4814b51700c89d
        """
        tx = await self.client.get_transactions(GetTransactionByHashRequest(hash="84b7c9467a0a24e7a59a5e224e9ef8803563621f4710fe8536ae7803fe245d61"))
        assert tx is not None
        txs = await self.client.get_transaction_by_message(GetTransactionByMessageRequest(direction="out", msg_hash=tx.in_msg.hash))
        assert len(txs) == 1
        assert txs[0].hash.lower() == "f5333b49b754376ff96b0d299dc38142b8b5ca1b046f41704a4814b51700c89d"

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
