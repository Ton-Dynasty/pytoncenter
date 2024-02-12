import os
from tonpy import Cell
from typing import Dict, List, Optional, Union, Literal, Tuple, Coroutine, Iterable, OrderedDict, Any, overload
import aiohttp
import asyncio
import warnings
import uuid
from pytoncenter.v3.models import MasterchainInfo
from datetime import datetime


class TonException(Exception):
    def __init__(self, code: int):
        self.code = code


class AsyncTonCenterClientV3:
    def __init__(self, network: Union[Literal["mainnet"], Literal["testnet"]], *, custom_api_key: Optional[str] = None, custom_base_url: Optional[str] = None) -> None:
        api_key = os.getenv("TONCENTER_API_KEY", custom_api_key)
        # show warning if api_key is None
        if not api_key:
            warnings.warn(
                "API key is not provided. TonCenter API is rate limited to 1 request per second. Suggesting providing it in environment variable `TONCENTER_API_KEY` or custom_api_key to increase the rate limit.",
                RuntimeWarning,
            )
        assert (network in ["mainnet", "testnet"]) or (custom_base_url is not None), "Network or custom_base_url must be provided"
        if custom_base_url is not None:
            self.base_url = custom_base_url
        else:
            prefix = "" if network == "mainnet" else "testnet."
            self.base_url = f"https://{prefix}toncenter.com/api/v2"
        self.api_key = api_key

    def _get_request_headers(self) -> Dict[str, Any]:
        headers = {
            "Content-Type": "application/json",
            "accept": "application/json",
        }
        if self.api_key:
            headers["X-API-KEY"] = self.api_key
        return headers

    def _serialize(self, params: OrderedDict[str, str]) -> List[Tuple[str, Any]]:
        return [(k, v) for k, v in params.items()]

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
            params = {k: v for k, v in query.items() if v is not None} if query is not None else None
            async with session.get(url=url, headers=self._get_request_headers(), params=params) as response:
                return await self._parse_response(response)

    async def _async_post(self, handler: str, payload: Dict[str, str]):
        url = f"{self.base_url}/{handler}"
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, headers=self._get_request_headers(), json={k: v for k, v in payload.items() if v is not None}) as response:
                return await self._parse_response(response)

    async def get_masterchain_info(self) -> MasterchainInfo:
        return await self._async_get("masterchainInfo")

    async def get_blocks(
        self,
        workchain: Optional[int] = None,
        shard: Optional[str] = None,
        seqno: Optional[int] = None,
        start_utime: Optional[datetime] = None,
        end_utime: Optional[datetime] = None,
        start_lt: Optional[int] = None,
        end_lt: Optional[int] = None,
        limit: Optional[int] = None,
        offest: Optional[int] = None,
        sort: Literal["asc", "desc"] = "desc",
    ):
        if shard is not None:
            assert workchain
        if seqno is not None:
            assert workchain and shard
