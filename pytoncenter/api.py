import os
from tonpy import Cell
from typing import Dict, List, Optional, Union, Literal, Tuple, TypedDict, Coroutine, Iterable, OrderedDict, Any
import aiohttp
import asyncio
from .types import *
import warnings

class TonException(Exception):
    def __init__(self, code: int):
        self.code = code

class AsyncTonCenterClient:
    def __init__(self, network: Union[Literal["mainnet"], Literal["testnet"]], *, custom_api_key: Optional[str]=None, custom_base_url: Optional[str]=None) -> None:
        api_key = os.getenv("TONCENTER_API_KEY", custom_api_key)
        # show warning if api_key is None
        if not api_key:
            warnings.warn("API key is not provided. TonCenter API is rate limited to 1 request per second. Suggesting providing it in environment variable `TONCENTER_API_KEY` or custom_api_key to increase the rate limit.", RuntimeWarning)        
        assert (network in ["mainnet", "testnet"]) or (custom_base_url is not None), "Network or custom_base_url must be provided"
        if custom_base_url is not None:
            self.base_url = custom_base_url
        else:
            prefix = "" if network == "mainnet" else "testnet."
            self.base_url = f"https://{prefix}toncenter.com/api/v2"
        self.api_key = api_key

    def _get_request_headers(self) -> Dict[str, Any]:
        headers =  {
            'Content-Type': 'application/json',
            'accept': 'application/json',
        }
        if self.api_key:
            headers['X-API-KEY'] = self.api_key
        return headers
    
    def _serialize(self, params: OrderedDict[str, str]) -> List[Tuple[str, Any]]:
        return [ (k, v) for k, v in params.items()]
    
    def _deserialize(self, stack: List[Tuple[str, Any]]) -> OrderedDict[str, str]:
        return OrderedDict(stack)

    async def _parse_response(self, response: aiohttp.ClientResponse):
        """
        _parse_response parses the response from TonCenter API and returns the result if the request was successful.
        If the request was unsuccessful, a TonException is raised.

        Parameters
        ----------
        response : requests.Response
            The response from TonCenter API
        
        Returns
        -------
        Any
            The result of the request
        
        Raises
        ------
        aiohttp.client_exceptions.ClientResponseError:
            If the request was unsuccessful, a ClientResponseError is raised.
        TonException
            If the request was successful, but the TonCenter API returned an error, a TonException is raised.
        """
        response.raise_for_status()
        result = await response.json()
        if not result["ok"]:
            raise TonException(result["code"])
        return result["result"]

    async def _async_get(self, handler: str, query: Optional[Dict[str, str]] = None):
        url = f"{self.base_url}/{handler}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, headers=self._get_request_headers(), params={k:v for k, v in query.items() if v is not None}) as response:
                return await self._parse_response(response)
    
    async def _async_post(self, handler: str, payload:Dict[str,str]):
        url = f"{self.base_url}/{handler}"
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, headers=self._get_request_headers(), json={k:v for k, v in payload.items() if v is not None}) as response:
                return await self._parse_response(response)

    async def get_address_information(self, address: str) -> WalletInformation:
        return await self._async_get("getAddressInformation", {"address": address})

    async def get_extended_address_information(self, address: str) -> ExtentedAddressInformation:
        return await self._async_get("getExtendedAddressInformation", {"address": address})

    async def get_transactions(self, address: str, limit: Optional[int] = None, lt: Optional[int]=None, hash: Optional[str]=None, to_lt: Optional[int]=0, archival: bool=False) -> List[Tx]:
        assert limit is None or limit <= 100, "Limit must be less than or equal to 100"
        assert (lt != 0 and hash != "") or (lt == 0 and hash == ""), "lt and hash must be specified together"
        return await self._async_get("getTransactions", {"address": address, "limit": limit, "lt": lt, "hash": hash, "to_lt": to_lt, "archival": int(archival)})

    async def get_wallet_information(self, address: str) -> WalletInformation:
        return await self._async_get("getWalletInformation", {"address": address})

    async def get_address_balance(self, address: str) -> int:
        """
        get_address_balance returns the balance of the address in nanoton.
        """
        balance =  await self._async_get("getAddressBalance", {"address": address})
        return int(balance)

    async def get_address_state(self, address: str) -> str:
        """
        get_address_state returns the state of the address as a string, e.g. "active", "uninitialized", etc.
        """
        return await self._async_get("getAddressState", {"address": address})

    async def get_token_data(self, address: str) -> Union[JettonMasterData, JettonWalletData, NFTCollectionData, NFTItemData]:
        return await self._async_get("getTokenData", {"address": address})

    async def pack_address(self, address: str) -> str:
        return await self._async_get("packAddress", {"address": address})

    async def unpack_address(self, address: str) -> str:
        return await self._async_get("unpackAddress", {"address": address})

    async def detect_address(self, address: str) -> DetectAddressResult:
        return await self._async_get("detectAddress", {"address": address})

    async def run_get_method(self, address: str, method_name: str, params: OrderedDict[str, Any]):
        # serialize params into List[List[param name, param value]]
        stack = self._serialize(params)
        result =  await self._async_post("runGetMethod", {"address": address, "method": method_name, "stack": stack})
        if result.get("@type") == "smc.runResult" and "stack" in result:
            return self._deserialize(result["stack"])
        raise ValueError(f"Invalid get method result: {result}")

    async def send_boc(self, boc: str):
        return await self._async_post("sendBoc", {"boc": boc})

    async def send_boc_return_hash(self, boc: str):
        return await self._async_post("sendBocReturnHash", {"boc": boc})

        boc = message.to_boc()
        return await self._async_post("sendBocReturnHash", {"boc": boc})

    async def estimate_fee(self, address:str, body:Union[str, Cell], init_code: str, init_data:str, ignore_chksig:bool=True) -> EstimateResult:
        if isinstance(body, Cell):
            body = body.to_boc()
        return await self._async_post("estimateFee", {"address": address, "body": body, "init_code": init_code, "init_data": init_data, "ignore_chksig": int(ignore_chksig)})

    async def execute_many(self, *coros: Union[Coroutine, List[Coroutine], Dict[str, Coroutine]]):
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
            "address1": client.get_address_balance("address1"),
            "address2": client.run_get_method("kQBqSpvo4S87mX9tjHaG4zhYZeORhVhMapBJpnMZ64jhrP-A", "get_jetton_data", {})
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

        assert isinstance(coros, Iterable) or isinstance(coros, Coroutine), "Invalid argument type"
        if not coros:
            return []
        
        if isinstance(coros[0], Dict):
            tasks = [asyncio.create_task(coro, name=name) for name, coro in coros[0].items()]
            results = await asyncio.gather(*tasks)
            return {task.get_name(): result for task, result in zip(tasks, results)}
        if isinstance(coros[0], Iterable):
            tasks = [asyncio.create_task(coro) for coro in coros[0]]
            return await asyncio.gather(*tasks)
        else:
            tasks = [asyncio.create_task(coro) for coro in coros]
            return await asyncio.gather(*tasks)
        
    async def subscribeTx(self, address: str, interval: int = 1):
        """
        subscribeTx returns a generator that yields transactions of the address

        Parameters
        ----------
        address : str
            The address to subscribe to
        interval : int, optional
            The interval to poll the TonCenter API, by default 1 second

        Yields
        ------
        Tx
            The transaction of the address
        """
        cur_lt = None
        while True:
            results = await self.get_transactions(address, limit=1 if cur_lt==None else 10, to_lt=cur_lt or 0, archival=True)
            if not results:
                await asyncio.sleep(interval)
                continue
            cur_lt = results[-1]["transaction_id"]["lt"]
            for tx in results:
                yield tx

