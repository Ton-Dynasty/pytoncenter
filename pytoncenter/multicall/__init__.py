from typing import List, Dict, Coroutine, Any, Union, overload, Iterable
import asyncio


class Multicallable:
    @overload
    async def multicall(self, *coros: Coroutine[Any, Any, Any]) -> List[Any]: ...

    @overload
    async def multicall(self, *coros: Dict[str, Coroutine[Any, Any, Any]]) -> Dict[str, Any]: ...

    @overload
    async def multicall(self, *coros: List[Coroutine[Any, Any, Any]]) -> List[Any]: ...

    async def multicall(self, *coros: Union[Coroutine[Any, Any, Any], List[Coroutine[Any, Any, Any]], Dict[str, Coroutine[Any, Any, Any]]]):
        """
        Example1
        -------
        ```
        client = AsyncTonCenterClient(network="testnet")
        result = await client.execute([
            client.get_address_information("address1"),
            client.get_address_information("address2"),
        ])
        print(result)
        ```

        Example2
        -------
        ```
        client = AsyncTonCenterClient(network="testnet")
        result = await client.execute(
            client.get_address_balance("address1"),
            client.run_get_method("kQBqSpvo4S87mX9tjHaG4zhYZeORhVhMapBJpnMZ64jhrP-A", "get_jetton_data", {})
        )
        print(result)
        ```

        Example3
        -------
        ```
        client = AsyncTonCenterClient(network="testnet")
        result = await client.execute({
            "task1": client.get_address_balance("address1"),
            "task2": client.run_get_method("kQBqSpvo4S87mX9tjHaG4zhYZeORhVhMapBJpnMZ64jhrP-A", "get_jetton_data", {})
        })
        print(result)
        ```
        """

        assert isinstance(coros, dict) or isinstance(coros, Iterable) or isinstance(coros, Coroutine), "Invalid argument type"
        if not coros:
            return []

        if isinstance(coros[0], dict):
            tasks = [asyncio.create_task(coro, name=name) for name, coro in coros[0].items()]  # type: ignore
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return {task.get_name(): result for task, result in zip(tasks, results)}
        if isinstance(coros[0], Iterable):
            tasks = [asyncio.create_task(coro) for coro in coros[0]]  # type: ignore
            return await asyncio.gather(*tasks, return_exceptions=True)
        else:
            tasks = [asyncio.create_task(coro) for coro in coros]  # type: ignore
            return await asyncio.gather(*tasks, return_exceptions=True)
