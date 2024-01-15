import hashlib
import hmac
from typing import List, Optional, Tuple
import math
import os
from hashlib import pbkdf2_hmac
from nacl.bindings import crypto_sign_seed_keypair
from nacl.bindings import crypto_sign_ed25519_sk_to_pk
from nacl.signing import VerifyKey, exc
from .bip39 import _english


PBKDF_ITERATIONS = 100000

def get_secure_random_number(min_v, max_v):
    range_betw = max_v - min_v
    bits_needed = math.ceil(math.log2(range_betw))
    if bits_needed > 53:
        raise Exception("Range is too large")

    bytes_needed = math.ceil(bits_needed / 8)
    mask = math.pow(2, bits_needed) - 1

    while True:
        res = os.urandom(bits_needed)
        power = (bytes_needed - 1) * 8
        number_val = 0
        for i in range(bytes_needed):
            number_val += res[i] * math.pow(2, power)
            power -= 8
        number_val = int(number_val) & int(mask)
        if number_val >= range_betw:
            continue

        return min_v + number_val
    
def is_basic_seed(entropy):
    seed = pbkdf2_hmac("sha512", entropy, 'TON seed version'.encode(
        'utf-8'), max(1, math.floor(PBKDF_ITERATIONS / 256)))
    return seed[0] == 0


def private_key_to_public_key(priv_k: bytes):
    return crypto_sign_ed25519_sk_to_pk(priv_k)


def verify_sign(public_key: bytes, signed_message: bytes, signature: bytes):
    key = VerifyKey(public_key)
    try:
        key.verify(signed_message, signature)
        return True
    except exc.BadSignatureError:
        return False

def mnemonic_is_valid(mnemo_words: List[str]) -> bool:
    return len(mnemo_words) == 24 and is_basic_seed(mnemonic_to_entropy(mnemo_words))


def mnemonic_to_entropy(mnemo_words: List[str], password: Optional[str] = None):
    sign = hmac.new((" ".join(mnemo_words)).encode(
        'utf-8'), bytes(0), hashlib.sha512).digest()
    return sign


def mnemonic_to_seed(mnemo_words: List[str], seed: str, password: Optional[str] = None):
    entropy = mnemonic_to_entropy(mnemo_words, password)
    return hashlib.pbkdf2_hmac("sha512", entropy, seed, PBKDF_ITERATIONS)


def mnemonic_to_private_key(mnemo_words: List[str], password: Optional[str] = None) -> Tuple[bytes, bytes]:
    """
    :rtype: (bytes(public_key), bytes(secret_key))
    """
    seed = mnemonic_to_seed(
        mnemo_words, 'TON default seed'.encode('utf-8'), password)
    return crypto_sign_seed_keypair(seed[:32])


def mnemonic_to_wallet_key(mnemo_words: List[str], password: Optional[str] = None) -> Tuple[bytes, bytes]:
    """
    :rtype: (bytes(public_key), bytes(secret_key))
    """
    _, priv_k = mnemonic_to_private_key(mnemo_words, password)
    return crypto_sign_seed_keypair(priv_k[:32])


def mnemonic_new(words_count: int = 24, password: Optional[str] = None) -> List[str]:
    while True:
        mnemo_arr = []

        for _ in range(words_count):
            idx = get_secure_random_number(0, len(_english))
            mnemo_arr.append(_english[idx])

        if not is_basic_seed(mnemonic_to_entropy(mnemo_arr)):
            continue

        break

    return mnemo_arr
