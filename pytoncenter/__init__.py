from typing import Literal, Optional, overload

from pytoncenter.v2.api import AsyncTonCenterClientV2
from pytoncenter.v3.api import AsyncTonCenterClientV3


@overload
def get_client(version: Literal["v2"], network: Literal["mainnet", "testnet"], qps: Optional[float] = None, *args, **kwargs) -> AsyncTonCenterClientV2: ...


@overload
def get_client(version: Literal["v3"], network: Literal["mainnet", "testnet"], qps: Optional[float] = None, *args, **kwargs) -> AsyncTonCenterClientV3:
    """
    Parameters
    ----------
    network : Union[Literal["mainnet"], Literal["testnet"]]
        The network to use. Only mainnet and testnet are supported.

    api_key : Optional[str], optional
        The API key to use, by default None. If api_key is an empty string, then it will override the environment variable `TONCENTER_API_KEY`.
    custom_endpoint : Optional[str], optional
        The custom endpoint to use. If provided, it will override the network parameter.
    qps: Optional[float], optional
        The maximum queries per second to use. If not provided, it will use 9.5 if api_key is provided, otherwise 1.
    """


def get_client(version: Literal["v2", "v3"], network: Literal["mainnet", "testnet"], *args, **kwargs):
    if version == "v2":
        return AsyncTonCenterClientV2(network=network, *args, **kwargs)
    if version == "v3":
        return AsyncTonCenterClientV3(network=network, *args, **kwargs)
    raise ValueError(f"Invalid version {version}")


__version__ = "0.0.14"
