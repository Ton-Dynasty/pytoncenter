from pytoncenter.api import AsyncTonCenterClient
from pytoncenter.types import Tx
from pytoncenter.utils import get_opcode, decode_base64
from tonpy import CellSlice
import asyncio
from typing import Dict, Callable, Any


async def handle_jetton_internal_transfer(body: CellSlice):
    return "jetton_internal_transfer"


async def handle_jetton_transfer(body: CellSlice):
    return "jetton_transfer"


async def default_handler(*args, **kwargs): ...


HandleFuncs: Dict[str, Callable[[CellSlice], Any]] = {
    "0x178d4519": handle_jetton_internal_transfer,
    "0x0f8a7ea5": handle_jetton_transfer,
}


async def process_tx(tx: Tx):
    txhash = decode_base64(tx["transaction_id"]["hash"])
    lt = tx["transaction_id"]["lt"]

    in_msg = tx.get("in_msg", {})
    msg_data = in_msg.get("msg_data", {})

    if msg_data.get("@type") == "msg.dataText":
        print(in_msg.get("messsage"))
        return

    cs = CellSlice(msg_data.get("body"))
    opcode = get_opcode(cs.load_uint(32))
    func = HandleFuncs.get(opcode, default_handler)
    output = await func(cs)
    print(f"Processing tx: {txhash}", lt, opcode, output)


async def main():
    client = AsyncTonCenterClient(network="testnet")
    async for tx in client.subscribeTx("kQCFEtu7e-su_IvERBf4FwEXvHISf99lnYuujdo0xYabZQgW", interval_in_second=1, limit=100):
        await process_tx(tx)


if __name__ == "__main__":
    asyncio.run(main())
