from pytoncenter.address import Address
import asyncio
from pytoncenter import AsyncTonCenterClient


async def main():
    test_address_str = "EQAuVtH68PRkM8qsMUh670ecNZPtqs5bANF3MD4dv-eBb2vD"
    addr = Address(test_address_str)

    client = AsyncTonCenterClient(network="mainnet")
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

    if (
        test_address_str == result["bounceable"]["b64"]
        or test_address_str == result["bounceable"]["b64url"]
        or test_address_str == result["bounceable"]["b64"]
        or test_address_str == result["bounceable"]["b64url"]
    ):
        assert addr.is_url_safe == True, "URL safe mismatch!"


if __name__ == "__main__":
    asyncio.run(main())
