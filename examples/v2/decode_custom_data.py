from pytoncenter.v2.api import AsyncTonCenterClientV2
from pytoncenter.decoder import Decoder, Field
import asyncio
from pprint import pprint


async def main():
    client = AsyncTonCenterClientV2(network="testnet")
    result = await client.run_get_method("kQCpk40ub48fvx89vSUjOTRy0vOEEZ4crOPPfLEvg88q1EeH", "getOracleData", {})
    OracleMetaDataDecoder = Decoder(
        Field.Address("base_asset_address"),
        Field.Address("quote_asset_address"),
        Field.Number("base_asset_decimals"),
        Field.Number("quote_asset_decimals"),
        Field.Number("min_base_asset_threshold"),
        Field.Address("base_asset_wallet_address"),
        Field.Address("quote_asset_wallet_address"),
        Field.Bool("is_initialized"),
        Field.Number("latestBaseAssetPrice"),
        Field.Number("latestTimestamp"),
    )
    output = OracleMetaDataDecoder.decode(result)
    pprint(output, width=120)


if __name__ == "__main__":
    asyncio.run(main())
