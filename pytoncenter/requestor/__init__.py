from abc import abstractmethod
from typing import Any, Dict, Literal, Optional

import aiohttp
from aiolimiter import AsyncLimiter

__all__ = ["AsyncRequestor"]


class AsyncRequestor:
    def __init__(self, qps: float):
        self.limiter = AsyncLimiter(qps, 1)

    @abstractmethod
    def _get_request_headers(self) -> Dict[str, str]:
        raise NotImplementedError

    @abstractmethod
    async def _parse_response(self, response: aiohttp.ClientResponse):
        raise NotImplementedError

    async def _underlying_call(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE"],
        url: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        payload: Optional[Dict[str, Any]] = None,
    ):
        async with self.limiter:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url=url, headers=self._get_request_headers(), params=params, json=payload) as response:
                    return await self._parse_response(response)
