from typing import Union

import pytest

from pytoncenter.address import Address
from pytoncenter.v2.api import AsyncTonCenterClientV2

pytest_plugins = ("pytest_asyncio",)


class TestAddress:
    client: AsyncTonCenterClientV2

    def setup_method(self):
        self.client = AsyncTonCenterClientV2(network="testnet")

    @pytest.mark.parametrize(
        ("addr1", "addr2", "match"),
        [
            ("0:2b790db779a6e344ee6094b09b859e0ac50f523888edc3678cd8fb845d784865", "kQAreQ23eabjRO5glLCbhZ4KxQ9SOIjtw2eM2PuEXXhIZeh3", True),
            ("kQAreQ23eabjRO5glLCbhZ4KxQ9SOIjtw2eM2PuEXXhIZeh3", "0QAreQ23eabjRO5glLCbhZ4KxQ9SOIjtw2eM2PuEXXhIZbWy", True),
            ("kQAreQ23eabjRO5glLCbhZ4KxQ9SOIjtw2eM2PuEXXhIZeh3", "EQCpk40ub48fvx89vSUjOTRy0vOEEZ4crOPPfLEvg88q1PwN", False),
        ],
    )
    def test_address_conversion(self, addr1: str, addr2: str, match: bool):
        assert (Address(addr1) == Address(addr2)) == match

    @pytest.mark.parametrize(
        ("addr1", "addr2", "match"),
        [
            (Address("0:2b790db779a6e344ee6094b09b859e0ac50f523888edc3678cd8fb845d784865"), "kQAreQ23eabjRO5glLCbhZ4KxQ9SOIjtw2eM2PuEXXhIZeh3", True),
            ("kQAreQ23eabjRO5glLCbhZ4KxQ9SOIjtw2eM2PuEXXhIZeh3", Address("0QAreQ23eabjRO5glLCbhZ4KxQ9SOIjtw2eM2PuEXXhIZbWy"), True),
            (Address("kQAreQ23eabjRO5glLCbhZ4KxQ9SOIjtw2eM2PuEXXhIZeh3"), "EQCpk40ub48fvx89vSUjOTRy0vOEEZ4crOPPfLEvg88q1PwN", False),
        ],
    )
    def test_address_compare_eq(self, addr1: Union[str, Address], addr2: Union[str, Address], match: bool):
        assert (addr1 == addr2) == match

    @pytest.mark.parametrize(
        ("addr", "form"),
        [
            ("0:2b790db779a6e344ee6094b09b859e0ac50f523888edc3678cd8fb845d784865", "raw_form"),
            ("EQCpk40ub48fvx89vSUjOTRy0vOEEZ4crOPPfLEvg88q1PwN", "bounceable"),
        ],
    )
    @pytest.mark.asyncio
    async def test_address_match_api(self, addr: str, form: str):
        result = await self.client.detect_address(addr)
        if form == "raw_form":
            assert result["raw_form"] == Address(addr).to_string(is_user_friendly=False)
        else:
            assert result[form]["b64"] == Address(addr).to_string(is_user_friendly=True, is_test_only=False, is_bounceable=True)
