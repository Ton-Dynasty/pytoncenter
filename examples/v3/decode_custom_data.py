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

    quote_token = await client.get_jetton_masters(GetJettonMastersRequest(address=output["quote_asset_address"]))
    pprint(quote_token, width=120)

    print("====================================")

    # call get method with parameters
    # contract address: kQBO50OJlbegG9CNOeIL8v85Z0sGTJY1YwiOQ-1MtxRv8hz7 (alarm contract)
    # new price: 1 TON for 4 USDT
    # get fun getEstimate(buyNum: Int, newBaseAssetPrice: Int)
    req = RunGetMethodRequest(
        address="kQBO50OJlbegG9CNOeIL8v85Z0sGTJY1YwiOQ-1MtxRv8hz7",
        method="getEstimate",
        stack=[
            GetMethodParameterInput(type="num", value=1),
            GetMethodParameterInput(type="num", value=int(0.004 * 2**64)),
        ],
    )
    result = await client.run_get_method(req)

    EstimateResultDecoder = Decoder(
        Types.Bool("canBuy"),
        Types.Number("needBaseAssetAmount"),
        Types.Number("needQuoteAssetAmount"),
    )
    output = EstimateResultDecoder.decode(result)
    print("canBuy:", output["canBuy"])
    print("needBaseAssetAmount:", output["needBaseAssetAmount"] / 10**9, "TON")
    print("needQuoteAssetAmount:", output["needQuoteAssetAmount"] / 10**6, "USDT")

    print("====================================")

    # Use a simple way
    req = RunGetMethodRequest(
        address="kQBO50OJlbegG9CNOeIL8v85Z0sGTJY1YwiOQ-1MtxRv8hz7",
        method="getEstimate",
        stack=[
            {"type": "num", "value": 1},
            {"type": "num", "value": int(0.004 * 2**64)},
        ],
    )
    result = await client.run_get_method(req)
    output = EstimateResultDecoder.decode(result)
    print("canBuy:", output["canBuy"])
    print("needBaseAssetAmount:", output["needBaseAssetAmount"] / 10**9, "TON")
    print("needQuoteAssetAmount:", output["needQuoteAssetAmount"] / 10**6, "USDT")


if __name__ == "__main__":
    asyncio.run(main())
