import asyncio

from pytoncenter.address import Address
from pytoncenter.v2.api import AsyncTonCenterClientV2


async def main():
    raw_address_str = "0:2e56d1faf0f46433caac31487aef479c3593edaace5b00d177303e1dbfe7816f"
    friendly_address_str = "EQAuVtH68PRkM8qsMUh670ecNZPtqs5bANF3MD4dv-eBb2vD"
    bounceable_address_str = "EQAuVtH68PRkM8qsMUh670ecNZPtqs5bANF3MD4dv+eBb2vD"
    bounceable_address_str_url = "EQAuVtH68PRkM8qsMUh670ecNZPtqs5bANF3MD4dv-eBb2vD"
    non_bounceable_address_str = "UQAuVtH68PRkM8qsMUh670ecNZPtqs5bANF3MD4dv+eBbzYG"
    non_bounceable_address_str_url = "UQAuVtH68PRkM8qsMUh670ecNZPtqs5bANF3MD4dv-eBbzYG"

    test_address_str = bounceable_address_str_url
    addr = Address(test_address_str)

    client = AsyncTonCenterClientV2(network="testnet")
    result = await client.detect_address(test_address_str)
    print("From detect_address:")
    print(f"Raw Form: {result['raw_form']}")
    print(f"Bounceable B64: {result['bounceable']['b64']}")
    print(f"Bounceable B64 URL: {result['bounceable']['b64url']}")
    print(f"Non-Bounceable B64: {result['non_bounceable']['b64']}")
    print(f"Non-Bounceable B64 URL: {result['non_bounceable']['b64url']}")
    print(f"Given Type: {result['given_type']}")
    print(f"Test Only: {result['test_only']}")

    print("\nFrom API:")
    print(f"Workchain: {addr.workchain}")
    print(f"Hash Part: {addr.hash_part.hex()}")
    print(f"Is Test Only: {addr.is_test_only}")
    print(f"Is User Friendly: {addr.is_user_friendly}")
    print(f"Is Bounceable: {addr.is_bounceable}")
    print(f"Is URL Safe: {addr.is_url_safe}")
    address_string = addr.to_string()
    print(f"Address String: {address_string}")

    assert result["test_only"] == addr.is_test_only, "Test only mismatch!"

    assert result["raw_form"][2:] == addr.hash_part.hex(), "User friendly mismatch!"

    if result["given_type"] == "friendly_bounceable":
        assert addr.is_user_friendly == True, "User friendly mismatch!"
        assert addr.is_bounceable == True, "Bounceable mismatch!"

    if result["given_type"] == "friendly_non_bounceable":
        assert addr.is_user_friendly == True, "User friendly mismatch!"
        assert addr.is_bounceable == False, "Bounceable mismatch!"

    if result["given_type"] == "raw_form":
        assert addr.is_user_friendly == False, "User friendly mismatch!"
        assert addr.is_bounceable == False, "Bounceable mismatch!"

    if test_address_str == result["non_bounceable"]["b64url"] or test_address_str == result["bounceable"]["b64url"]:
        assert addr.is_url_safe == True, "URL safe mismatch!"
    else:
        assert addr.is_url_safe == False, "URL safe mismatch!"

    assert (
        address_string == result["bounceable"]["b64"]
        or address_string == result["bounceable"]["b64url"]
        or address_string == result["non_bounceable"]["b64"]
        or address_string == result["non_bounceable"]["b64url"]
        or address_string == result["raw_form"]
    ), "Address string mismatch!"


if __name__ == "__main__":
    asyncio.run(main())
