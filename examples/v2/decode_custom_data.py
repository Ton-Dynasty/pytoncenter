import asyncio
from pprint import pprint

from pytoncenter.decoder import Decoder, Types
from pytoncenter.v2.api import AsyncTonCenterClientV2


async def main():
    client = AsyncTonCenterClientV2(network="testnet")
    result = await client.run_get_method("kQCpk40ub48fvx89vSUjOTRy0vOEEZ4crOPPfLEvg88q1EeH", "getOracleData")
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
    pprint(output, width=120)


if __name__ == "__main__":
    asyncio.run(main())
