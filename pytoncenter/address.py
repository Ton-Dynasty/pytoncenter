from __future__ import annotations

import base64
import ctypes
import math
from typing import Optional, TypedDict, Union

_AddressInfo = TypedDict(
    "_AddressInfo",
    {
        "is_test_only": bool,
        "is_bounceable": bool,
        "workchain": int,
        "hash_part": bytearray,
    },
)


def string_to_bytes(string, size=1):  # ?
    if size == 1:
        buf = (ctypes.c_uint8 * len(string))()
    elif size == 2:
        buf = (ctypes.c_uint16 * len(string) * 2)()
    elif size == 4:
        buf = (ctypes.c_uint32 * len(string) * 4)()

    for i, c in enumerate(string):
        # buf[i] = ord(c)
        buf[i] = c  # ?

    return bytes(buf)


def crc16(data):
    POLY = 0x1021
    reg = 0
    message = bytes(data) + bytes(2)

    for byte in message:
        mask = 0x80
        while mask > 0:
            reg <<= 1
            if byte & mask:
                reg += 1
            mask >>= 1
            if reg > 0xFFFF:
                reg &= 0xFFFF
                reg ^= POLY

    return bytearray([math.floor(reg / 256), reg % 256])


def parse_friendly_address(addr_str: str) -> _AddressInfo:
    if len(addr_str) != 48:
        raise Exception("User-friendly address should contain strictly 48 characters")

    # avoid padding error (https://gist.github.com/perrygeo/ee7c65bb1541ff6ac770)
    data = string_to_bytes(base64.b64decode(addr_str + "=="))

    if len(data) != 36:
        raise Exception("Unknown address type: byte length is not equal to 36")

    addr = data[:34]
    crc = data[34:36]
    calced_crc = crc16(addr)
    if not (calced_crc[0] == crc[0] and calced_crc[1] == crc[1]):
        raise Exception("Wrong crc16 hashsum")

    tag = addr[0]
    is_test_only = False
    is_bounceable = False
    if tag & Address.TEST_FLAG:
        is_test_only = True
        tag ^= Address.TEST_FLAG
    if (tag != Address.BOUNCEABLE_TAG) and (tag != Address.NON_BOUNCEABLE_TAG):
        raise Exception("Unknown address tag")

    is_bounceable = tag == Address.BOUNCEABLE_TAG

    if addr[1] == 0xFF:
        workchain = -1
    else:
        workchain = addr[1]
    if workchain != 0 and workchain != -1:
        raise Exception(f"Invalid address wc {workchain}")

    hash_part = bytearray(addr[2:34])
    return {
        "is_test_only": is_test_only,
        "is_bounceable": is_bounceable,
        "workchain": workchain,
        "hash_part": hash_part,
    }


class Address:
    BOUNCEABLE_TAG = 0x11
    NON_BOUNCEABLE_TAG = 0x51
    TEST_FLAG = 0x80

    def __init__(self, any_form: Union[str, Address]):
        if any_form is None:
            raise Exception("Invalid address")

        if isinstance(any_form, Address):
            self._wc = any_form._wc
            self._hash_part = any_form._hash_part
            self._is_test_only = any_form._is_test_only
            self._is_user_friendly = any_form._is_user_friendly
            self._is_bounceable = any_form._is_bounceable
            self._is_url_safe = any_form._is_url_safe
            return

        # base64 with digits, upper and lowercase Latin letters, '/' and '+'
        # base64url with '_' and '-' instead of '/' and '+')
        if any_form.find("-") > 0 or any_form.find("_") > 0:
            any_form = any_form.replace("-", "+").replace("_", "/")
            self._is_url_safe = True
        else:
            self._is_url_safe = False

        # Check this address is raw address or not
        try:
            colon_index = any_form.index(":")
        except ValueError:
            colon_index = -1  # raw address

        if colon_index > -1:
            # Example of Raw Address, -1:fcb91a3a3816d0f7b8c2c76108b8a9bc5a6b7a55bd79f8ab101c52db29232260
            arr = any_form.split(":")
            if len(arr) != 2:
                raise Exception(f"Invalid address {any_form}")

            wc = int(arr[0])
            if wc != 0 and wc != -1:
                raise Exception(f"Invalid address wc {wc}")

            address_hex = arr[1]
            if len(address_hex) != 64:
                raise Exception(f"Invalid address hex {any_form}")

            self._is_user_friendly = False
            self._wc = wc
            self._hash_part = bytearray.fromhex(address_hex)
            self._is_test_only = False
            self._is_bounceable = False
        else:
            self._is_user_friendly = True
            parse_result = parse_friendly_address(any_form)
            self._wc = parse_result["workchain"]
            self._hash_part = parse_result["hash_part"]
            self._is_test_only = parse_result["is_test_only"]
            self._is_bounceable = parse_result["is_bounceable"]

    @property
    def wc(self) -> int:
        """
        Alias for workchain, compatible with tonsdk
        """
        return self._wc

    @property
    def workchain(self) -> int:
        return self._wc

    @property
    def hash_part(self) -> bytearray:
        return self._hash_part

    @property
    def is_test_only(self) -> bool:
        return self._is_test_only

    @property
    def is_user_friendly(self) -> bool:
        return self._is_user_friendly

    @property
    def is_bounceable(self) -> bool:
        return self._is_bounceable

    @property
    def is_url_safe(self) -> bool:
        return self._is_url_safe

    def to_string(
        self,
        is_user_friendly: Optional[bool] = None,
        is_url_safe: Optional[bool] = None,
        is_bounceable: Optional[bool] = None,
        is_test_only: Optional[bool] = None,
    ) -> str:
        if is_user_friendly is None:
            is_user_friendly = self._is_user_friendly
        if is_url_safe is None:
            is_url_safe = self._is_url_safe
        if is_bounceable is None:
            is_bounceable = self._is_bounceable
        if is_test_only is None:
            is_test_only = self._is_test_only

        if not is_user_friendly:
            return f"{self._wc}:{self._hash_part.hex()}"
        else:
            tag = Address.BOUNCEABLE_TAG if is_bounceable else Address.NON_BOUNCEABLE_TAG

            if is_test_only:
                tag |= Address.TEST_FLAG

            addr = (ctypes.c_int8 * 34)()
            addr[0] = tag
            addr[1] = self._wc
            addr[2:] = self._hash_part
            address_with_checksum = (ctypes.c_uint8 * 36)()
            address_with_checksum[:34] = addr
            address_with_checksum[34:] = crc16(addr)

            address_base_64 = base64.b64encode(address_with_checksum).decode("utf-8")
            if is_url_safe:
                address_base_64 = address_base_64.replace("+", "-").replace("/", "_")

            return str(address_base_64)

    def __hash__(self) -> int:
        return hash(self.to_string(True, True, True, is_test_only=False))

    def __key__(self) -> str:
        return self.to_string(True, True, True, is_test_only=False)

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Address):
            return False
        return self.to_string(True, True, True, is_test_only=False) == __value.to_string(True, True, True, is_test_only=False)

    def __repr__(self) -> str:
        return self.to_string(True, True, True, is_test_only=False)
