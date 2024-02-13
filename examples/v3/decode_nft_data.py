import asyncio

from pytoncenter import get_client
from pytoncenter.v3.models import *


async def main():
    client = get_client(version="v3", network="testnet")

    print("=====================================")

    collections = await client.get_nft_collections()
    sorted_collections = sorted(collections, key=lambda x: int(x.next_item_index))
    largest_collection = sorted_collections[-1]
    print("collection", largest_collection.address, "has", int(largest_collection.next_item_index), "items.")

    print("=====================================")

    nft_items = await client.get_nft_items(GetNFTItemsRequest(collection_address=largest_collection.address))
    first_item = nft_items[0]
    print("item index", int(first_item.index), "address", first_item.address)

    print("=====================================")

    transfers = await client.get_nft_transfers(GetNFTTransfersRequest(collection_address=largest_collection.address))
    print("transfers", transfers)


if __name__ == "__main__":
    asyncio.run(main())
