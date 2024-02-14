import asyncio
from typing import Any, Coroutine, Dict, Iterable, List, TypeVar, overload

T = TypeVar("T")
K = TypeVar("K")


class Multicallable:
    @overload
    async def multicall(self, *coros: Coroutine[Any, Any, T]) -> List[T]: ...

    @overload
    async def multicall(self, coros: Dict[K, Coroutine[Any, Any, T]]) -> Dict[K, T]: ...

    @overload
    async def multicall(self, coros: List[Coroutine[Any, Any, T]]) -> List[T]: ...

    async def multicall(self, *args, **kwargs) -> Any:
        """
        With multicall, you can execute multiple async function calls by this method.
        This function will return a list of results or a dictionary of results if you pass a dictionary of coroutines.


        Code Snippet
        ------------
        ```python
        client = get_client("v2 or v3", network="testnet or mainnet")
        result = await client.multicall(
            any_asnyc_func1(param1, param2...),
            any_asnyc_func2(param1, param2...),
            any_asnyc_func3(param1, param2...),
        )
        print(result)
        ```

        Example1
        -------
        ```python
        client = get_client("v2", network="testnet")
        result = await client.multicall([
            client.get_address_information("address1"),
            client.get_address_information("address2"),
        ])
        print(result)
        ```

        Example2
        -------
        ```python
        client = get_client("v2", network="testnet")
        result = await client.multicall(
            client.get_address_balance("address1"),
            client.run_get_method("kQBqSpvo4S87mX9tjHaG4zhYZeORhVhMapBJpnMZ64jhrP-A", "get_jetton_data", {})
        )
        print(result)
        ```

        Example3
        -------
        ```python
        client = get_client("v2", network="testnet")
        result = await client.multicall({
            "task1": client.get_address_balance("address1"),
            "task2": client.run_get_method("kQBqSpvo4S87mX9tjHaG4zhYZeORhVhMapBJpnMZ64jhrP-A", "get_jetton_data", {})
        })
        print(result)
        ```
        """

        if len(args) == 1 and isinstance(args[0], (dict, list)):
            coros = args[0]
        else:
            # check if the arguments are coroutines
            assert all([asyncio.iscoroutine(coro) for coro in args]), "All element should be Coroutines"
            coros = args

        if isinstance(coros, dict):
            tasks = {name: asyncio.create_task(coro) for name, coro in coros.items()}
            results = await asyncio.gather(*tasks.values(), return_exceptions=True)
            return {name: result for name, result in zip(tasks.keys(), results)}
        elif isinstance(coros, Iterable):
            tasks = [asyncio.create_task(coro) for coro in coros]
            return await asyncio.gather(*tasks, return_exceptions=True)
        else:
            raise ValueError("Invalid argument type")
