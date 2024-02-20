import asyncio

import pytest

from pytoncenter import AsyncTonCenterClientV3, get_client
from pytoncenter.address import Address
from pytoncenter.decoder import AutoDecoder, Decoder, JettonDataDecoder, Types
from pytoncenter.v3.models import GetDNSRecordRequest, RunGetMethodRequest

pytest_plugins = ("pytest_asyncio",)


class TestDecoder:
    client: AsyncTonCenterClientV3

    def setup_method(self):
        self.client = get_client(version="v3", network="testnet")

    @pytest.mark.asyncio
    async def test_get_jetton_data(self):
        req = RunGetMethodRequest(address="kQBqSpvo4S87mX9tjHaG4zhYZeORhVhMapBJpnMZ64jhrP-A", method="get_jetton_data", stack=[])
        result = await self.client.run_get_method(req)
        decoder = JettonDataDecoder()
        output = decoder.decode(result)
        assert output["mintable"] == True
        assert output["admin_address"] == Address("0:bccc51ccf0b08ca7d5ecfbec3783dc267fb470b83809710b55fa81d94520aa41")

    @pytest.mark.asyncio
    async def test_get_custom_data(self):
        req = RunGetMethodRequest(address="kQCpk40ub48fvx89vSUjOTRy0vOEEZ4crOPPfLEvg88q1EeH", method="getOracleData", stack=[])
        result = await self.client.run_get_method(req)
        OracleMetaDataDecoder = Decoder(
            Types.Address("base_asset_address"),
            Types.Address("quote_asset_address"),
            Types.Number("base_asset_decimals"),
            Types.Number("quote_asset_decimals"),
            Types.Number("min_base_asset_threshold"),
            Types.Address("base_asset_wallet_address"),
            Types.Address("quote_asset_wallet_address"),
            Types.Bool("is_initialized"),
            Types.Number("latestBaseAssetPrice"),
            Types.Number("latestTimestamp"),
        )
        output = OracleMetaDataDecoder.decode(result)
        assert output["base_asset_address"] == Address("0:0000000000000000000000000000000000000000000000000000000000000000")
        assert output["base_asset_decimals"] == 9
        assert output["is_initialized"] == True
        assert output["min_base_asset_threshold"] == 1000000000

    @pytest.mark.asyncio
    async def test_auto_decoder(self):
        req = RunGetMethodRequest(address="kQCpk40ub48fvx89vSUjOTRy0vOEEZ4crOPPfLEvg88q1EeH", method="getOracleData", stack=[])
        result = await self.client.run_get_method(req)
        OracleMetaDataDecoder = AutoDecoder()
        output = OracleMetaDataDecoder.decode(result)
        print(output)
        assert output["idx_0"] == Address("0:0000000000000000000000000000000000000000000000000000000000000000")
        assert output["idx_2"] == 9
        assert output["idx_7"] == -1  # True, because auto decoder does not know the type of the field
        assert output["idx_4"] == 1000000000

    @pytest.mark.asyncio
    async def test_get_dns_record(self):
        await asyncio.sleep(0.5)
        client = get_client(version="v3", network="mainnet", api_key="")
        dns_name = "doge.ton"
        record = await client.get_dns_record(
            GetDNSRecordRequest(
                dns_name=dns_name,
                category="wallet",
            )
        )
        assert record.address == Address("EQDVjQWmoS6xrPqPJ5vEFBPZdBnY075ydcoEEqpVWjJXZ9RE")
