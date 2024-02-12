import os
from tonpy import Cell
from typing import Dict, List, Optional, Union, Literal, Tuple, Coroutine, Iterable, OrderedDict, Any, overload
import aiohttp
import asyncio
import warnings
import uuid


class TonException(Exception):
    def __init__(self, code: int):
        self.code = code


class Requestor:
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
