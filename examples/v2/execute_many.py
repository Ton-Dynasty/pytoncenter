from pytoncenter.v2.api import AsyncTonCenterClientV2
from tonpy import begin_cell
import asyncio


async def main():
    client = AsyncTonCenterClientV2(network="testnet")
    result = await client.multicall(
        client.get_address_information("kQA_NyEP4fSvLS7hzr2z7SKL5NGa67JrykHJjOrvS6XwtoXa"),
        client.get_address_balance("kQA_NyEP4fSvLS7hzr2z7SKL5NGa67JrykHJjOrvS6XwtoXa"),
    )
    print(result)

    result1 = await client.multicall(
        [
            client.run_get_method("kQBqSpvo4S87mX9tjHaG4zhYZeORhVhMapBJpnMZ64jhrP-A", "get_jetton_data", {}),
            client.get_address_state("kQBqSpvo4S87mX9tjHaG4zhYZeORhVhMapBJpnMZ64jhrP-A"),
            client.get_token_data("kQC_7JzoE_WZItHepEyfSvtKFLqDq-nu886YjX4gI6h3qBbn"),
        ]
    )
    print(result1)

    result2 = await client.multicall(
        {
            "task_detect_address": client.detect_address("kQC_7JzoE_WZItHepEyfSvtKFLqDq-nu886YjX4gI6h3qBbn"),
            "task_estimate_fee": client.estimate_fee("kQBqSpvo4S87mX9tjHaG4zhYZeORhVhMapBJpnMZ64jhrP-A", begin_cell().store_string("hello").end_cell(), "", "", True),
            "task_get_txs": client.get_transactions("kQA_NyEP4fSvLS7hzr2z7SKL5NGa67JrykHJjOrvS6XwtoXa"),
        }
    )
    print(result2)


if __name__ == "__main__":
    asyncio.run(main())
