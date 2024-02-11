import ctypes
import math
from nacl.bindings import crypto_sign, crypto_sign_BYTES
from nacl.signing import SignedMessage
from nacl.encoding import Encoder, RawEncoder
import base64

__all__ = [
    "get_opcode",
    "decode_base64",
]


def get_opcode(data_uint32: int) -> str:
    """
    Get opcode from uint32, the output is a string with 0x prefix, 10 characters long.
    """
    return "0x{:08x}".format(data_uint32).lower()


def decode_base64(data: str) -> str:
    return base64.b64decode(data + "==").hex()


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


def sign_message(
    message: bytes,
    signing_key: bytes,
    encoder: Encoder = RawEncoder,
) -> SignedMessage:
    raw_signed = crypto_sign(message, signing_key)

    signature = encoder.encode(raw_signed[:crypto_sign_BYTES])
    message = encoder.encode(raw_signed[crypto_sign_BYTES:])
    signed = encoder.encode(raw_signed)

    return SignedMessage._from_parts(signature, message, signed)
