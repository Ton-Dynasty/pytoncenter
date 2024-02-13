import asyncio
import logging
import traceback
from typing import Callable, Coroutine, Dict

from tonpy import CellSlice

from pytoncenter.address import Address
from pytoncenter.extension.message import JettonMessage
from pytoncenter.utils import get_opcode
from pytoncenter.v2.api import AsyncTonCenterClientV2
from pytoncenter.v2.tools import NamedFunction, create_named_mapping_func
from pytoncenter.v2.types import Tx

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


async def handle_jetton_internal_transfer(body: CellSlice, tx: Tx, labeler: NamedFunction):
    msg = JettonMessage.InternalTransfer.parse(body)
    src = labeler(Address(tx.get("in_msg", {}).get("source")))
    dst = labeler(Address(tx.get("in_msg", {}).get("destination")))
    jetton_amount = round(float(msg.amount) / 1e9, 4)
    forward_ton = round(float(msg.forward_ton_amount) / 1e9, 4)
    if tx.get("in_msg", {}).get("init_state", None) is not None:
        LOGGER.info(f"[{msg.OPCODE}] {src} deployed {dst} and mint {jetton_amount} USDT")
    else:
        LOGGER.info(f"[{msg.OPCODE}] Jetton Internal Transfer | {src} -> {dst}, forward {forward_ton} TON")


async def handle_jetton_transfer(body: CellSlice, tx: Tx, labeler: NamedFunction):
    msg = JettonMessage.Transfer.parse(body)
    jetton_amount = round(float(msg.amount) / 1e6, 4)
    value = round(float(tx.get("in_msg", {}).get("value")) / 1e9, 4)
    src = labeler(Address(tx.get("in_msg", {}).get("source")))
    dst = labeler(msg.destination)
    LOGGER.info(f"[{msg.OPCODE}] Jetton Transfer | {src} -> {dst} | {jetton_amount} USDT, {value} TON")


async def handle_jetton_burn(body: CellSlice, tx: Tx, labeler: NamedFunction):
    msg = JettonMessage.Burn.parse(body)
    burn_amount = round(float(msg.amount) / 1e6, 4)
    src = labeler(Address(tx.get("in_msg", {}).get("source")))
    LOGGER.info(f"[{msg.OPCODE}] Jetton Burn | 🔥 {src} burn {burn_amount} USDT 🔥")


async def default_handler(*args, **kwargs): ...


async def main():
    client = AsyncTonCenterClientV2(network="testnet")

    callbacks: Dict[str, Callable[[CellSlice, Tx, NamedFunction], Coroutine]] = {
        JettonMessage.InternalTransfer.OPCODE: handle_jetton_internal_transfer,
        JettonMessage.Transfer.OPCODE: handle_jetton_transfer,
        JettonMessage.Burn.OPCODE: handle_jetton_burn,
    }

    labeler = create_named_mapping_func(
        {
            Address("kQB8L_gn_thGqHLcn8ext98l6efykyB6z4yLCe9vtlrFrX-9"): "Oracle's USDT Wallet",
            Address("0QApdUMEOUuHnBo-RSdbikkZZ3qWItZLdXjyff9lN_eS5Zib"): "Maxey's Wallet V4R2",
            Address("kQCQ1B7B7-CrvxjsqgYT90s7weLV-IJB2w08DBslDdrIXucv"): "Maxey's USDT Wallet",
            Address("kQC94UIEeDaf4BhonCwmz-WjvBzCUWRM_FZFF-0bPFBC_pDZ"): "Oracle Contract",
            Address("kQBqSpvo4S87mX9tjHaG4zhYZeORhVhMapBJpnMZ64jhrP-A"): "USDT Contract",
        }
    )

    # Subscribe to transactions of a jetton wallet
    async for tx in client.subscribe_tx("kQB8L_gn_thGqHLcn8ext98l6efykyB6z4yLCe9vtlrFrX-9", interval_in_second=1, limit=100):
        try:
            in_msg = tx.get("in_msg", {})
            msg_data = in_msg.get("msg_data", {})

            # get message type. msg.dataText is comment message, msg.dataRaw is message with cell body
            data_type = msg_data.get("@type", None)

            # get sender and receiver, sender is from external if it's an empty string
            sender = Address(in_msg.get("source")) or "external"
            receiver = Address(in_msg.get("destination"))

            # get TON amount
            value = float(in_msg.get("value")) / 1e9

            if data_type == "msg.dataText":
                # comment message
                comment = in_msg.get("messsage")
                src = labeler(sender)
                dst = labeler(receiver)
                LOGGER.info(f"{src} sends {dst} {value} TON to {receiver} with comment {comment}")

            elif data_type == "msg.dataRaw":
                # normal message with cell data
                cs = CellSlice(msg_data.get("body"))

                # preload 32 bits to get opcode
                opcode = get_opcode(cs.preload_uint(32))

                # get handler for opcode
                handler = callbacks.get(opcode, default_handler)

                # call handler and get output string
                await handler(cs, tx, labeler)
        except Exception as e:
            LOGGER.error("Error: %s on tx %s\n* Reason\n============\n%s", e, tx, traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(main())
