import asyncio

from tonpy import begin_cell

from pytoncenter.v2.api import AsyncTonCenterClientV2

pytest_plugins = ("pytest_asyncio",)


class TestDebug:
    client: AsyncTonCenterClientV2

    def test_parallel_tasks(self):
        """
        NOT TO USE @pytest.mark.asyncio decorator, since the python gc will collect the client object before the async function completes.

        You will get an error like this:
        Task was destroyed but it is pending!

        Instead, we use the asyncio.run to prevent the it occurs.
        """

        async def test_multicall():
            client = AsyncTonCenterClientV2(network="testnet")

            result = await client.multicall(
                client.get_address_information("kQA_NyEP4fSvLS7hzr2z7SKL5NGa67JrykHJjOrvS6XwtoXa"),
                client.get_address_balance("kQA_NyEP4fSvLS7hzr2z7SKL5NGa67JrykHJjOrvS6XwtoXa"),
            )
            assert len(result) == 2
            assert isinstance(result, list)
            await asyncio.sleep(1)

            result1 = await client.multicall(
                [
                    client.get_address_state("kQBqSpvo4S87mX9tjHaG4zhYZeORhVhMapBJpnMZ64jhrP-A"),
                    client.get_token_data("kQC_7JzoE_WZItHepEyfSvtKFLqDq-nu886YjX4gI6h3qBbn"),
                    client.pack_address("kQBqSpvo4S87mX9tjHaG4zhYZeORhVhMapBJpnMZ64jhrP-A"),
                ]
            )
            assert len(result1) == 3
            assert isinstance(result1, list)
            await asyncio.sleep(1)

            result2 = await client.multicall(
                {
                    "task_detect_address": client.detect_address("kQC_7JzoE_WZItHepEyfSvtKFLqDq-nu886YjX4gI6h3qBbn"),
                    "task_estimate_fee": client.estimate_fee("kQBqSpvo4S87mX9tjHaG4zhYZeORhVhMapBJpnMZ64jhrP-A", begin_cell().store_string("hello").end_cell(), "", "", True),
                    "task_get_txs": client.get_transactions("kQA_NyEP4fSvLS7hzr2z7SKL5NGa67JrykHJjOrvS6XwtoXa"),
                }
            )
            assert len(result2) == 3
            assert isinstance(result2, dict)
            await asyncio.sleep(1)

        asyncio.run(test_multicall())
