from typing import Literal, Optional, overload

from pytoncenter.v2.api import AsyncTonCenterClientV2
from pytoncenter.v3.api import AsyncTonCenterClientV3


@overload
def get_client(version: Literal["v2"], network: Literal["mainnet", "testnet"], qps: Optional[float] = None, *args, **kwargs) -> AsyncTonCenterClientV2: ...


@overload
def get_client(version: Literal["v3"], network: Literal["mainnet", "testnet"], qps: Optional[float] = None, *args, **kwargs) -> AsyncTonCenterClientV3: ...


def get_client(version: Literal["v2", "v3"], network: Literal["mainnet", "testnet"], *args, **kwargs):
    if version == "v2":
        return AsyncTonCenterClientV2(network=network, *args, **kwargs)
    if version == "v3":
        return AsyncTonCenterClientV3(network=network, *args, **kwargs)
    raise ValueError(f"Invalid version {version}")


__version__ = "0.0.11"
