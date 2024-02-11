import pytest
from pytoncenter.address import Address
from pytoncenter.api import AsyncTonCenterClient
from pytoncenter.debug import pretty_print_trace_tx, create_named_mapping_func

pytest_plugins = ("pytest_asyncio",)


class TestDebug:
    client: AsyncTonCenterClient

    @pytest.mark.asyncio
    async def test_print_trace(self, capsys):
        client = AsyncTonCenterClient(network="testnet")
        txs = await client.get_transactions(
            address="kQAreQ23eabjRO5glLCbhZ4KxQ9SOIjtw2eM2PuEXXhIZeh3",
            limit=1,
            hash="Lomkyzxh1WBkxvxZ3cJNS2bAYIPC7dPZA67wDomGM4U=",
        )
        # Get transaction trace
        result = await client.trace_tx(txs[0])
        # Pretty print transaction trace with any formed of address mapping
        named_func = create_named_mapping_func(
            {
                Address("EQC8zFHM8LCMp9Xs--w3g9wmf7RwuDgJcQtV-oHZRSCqQZ__"): "Alan WalletV4R2",
                Address("0:2b790db779a6e344ee6094b09b859e0ac50f523888edc3678cd8fb845d784865"): "Jetton Master",
                Address("kQC40ScRg9_1ob5sjWsdScltrCGu0HARsUnOYQ1esc12588C"): "Jetton Wallet",
            },
            truncate_address=True,
        )
        pretty_print_trace_tx(result, named_func=named_func)
        captured = capsys.readouterr()
        assert captured.out
        assert not captured.err
