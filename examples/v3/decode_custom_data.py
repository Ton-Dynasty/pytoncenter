import asyncio
from pprint import pprint

from pytoncenter import get_client
from pytoncenter.decoder import Decoder, Types
from pytoncenter.v3.models import *


async def main():
    client = get_client("v3", network="testnet")
    req = RunGetMethodRequest(address="kQCpk40ub48fvx89vSUjOTRy0vOEEZ4crOPPfLEvg88q1EeH", method="getOracleData", stack=[])
    result = await client.run_get_method(req)
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
