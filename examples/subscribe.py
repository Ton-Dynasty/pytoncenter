from pytoncenter.api import AsyncTonCenterClient
from pytoncenter.types import Tx
from pytoncenter.utils import get_opcode, decode_base64
from tonpy import CellSlice
import asyncio
from typing import Dict, Callable, Any
from pytoncenter.extension.message import JettonInternalTransfer, JettonTransfer
from pytoncenter.debug import truncate_middle


async def handle_jetton_internal_transfer(body: CellSlice):
    msg = JettonInternalTransfer.parse(body)
    return f"{truncate_middle(msg.sender)} -> [{msg.amount}]"


async def handle_jetton_transfer(body: CellSlice):
    msg = JettonTransfer.parse(body)
    return f"[{msg.amount}] -> {truncate_middle(msg.destination)}"


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
    opcode = get_opcode(cs.preload_uint(32))
    func = HandleFuncs.get(opcode, default_handler)
    output = await func(cs)
    print(f"Processing tx: {txhash}", lt, opcode, output)


async def main():
    client = AsyncTonCenterClient(network="testnet")
    async for tx in client.subscribeTx("kQB8L_gn_thGqHLcn8ext98l6efykyB6z4yLCe9vtlrFrX-9", interval_in_second=1, limit=10):
        await process_tx(tx)


if __name__ == "__main__":
    asyncio.run(main())
