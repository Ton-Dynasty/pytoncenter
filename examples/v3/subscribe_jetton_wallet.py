import asyncio
import logging
import traceback
from datetime import datetime
from typing import Callable, Coroutine, Dict

from tonpy import CellSlice

from pytoncenter import get_client
from pytoncenter.address import Address
from pytoncenter.extension.message import JettonMessage
from pytoncenter.utils import get_opcode
from pytoncenter.v2.tools import NamedFunction, create_named_mapping_func
from pytoncenter.v3.models import *

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


async def handle_jetton_internal_transfer(body: CellSlice, tx: Transaction, labeler: NamedFunction):
    msg = JettonMessage.InternalTransfer.parse(body)
    src = labeler(Address(tx.in_msg.source))
    dst = labeler(Address(tx.in_msg.destination))
    forward_ton = round(float(msg.forward_ton_amount) / 1e9, 4)
    if tx.in_msg.init_state is not None:
        return
    else:
        LOGGER.info(f"[{msg.OPCODE}] Jetton Internal Transfer | {src} -> {dst}, forward {forward_ton} TON")


async def handle_jetton_transfer(body: CellSlice, tx: Transaction, labeler: NamedFunction):
    msg = JettonMessage.Transfer.parse(body)
    jetton_amount = round(float(msg.amount) / 1e6, 4)
    value = round(float(tx.in_msg.value) / 1e9, 4)
    src = labeler(Address(tx.in_msg.source))
    dst = labeler(msg.destination)
    LOGGER.info(f"[{msg.OPCODE}] Jetton Transfer | {src} -> {dst} | {jetton_amount} USDT, {value} TON")


async def handle_jetton_burn(body: CellSlice, tx: Transaction, labeler: NamedFunction):
    msg = JettonMessage.Burn.parse(body)
    burn_amount = round(float(msg.amount) / 1e6, 4)
    src = labeler(Address(tx.in_msg.source))
    LOGGER.info(f"[{msg.OPCODE}] Jetton Burn | 🔥 {src} burn {burn_amount} USDT 🔥")


async def default_handler(*args, **kwargs): ...


async def main():
    client = get_client(version="v3", network="testnet")

    callbacks: Dict[str, Callable[[CellSlice, Transaction, NamedFunction], Coroutine]] = {
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
    async for tx in client.subscribe_tx("kQB8L_gn_thGqHLcn8ext98l6efykyB6z4yLCe9vtlrFrX-9", interval_in_second=1):
        if tx.in_msg is None:
            continue

        LOGGER.info(f"Transaction: {tx.hash} { datetime.fromtimestamp(tx.now)}")
        try:
            # get sender and receiver, sender is from external if it's an empty string
            sender = Address(tx.in_msg.source) if tx.in_msg.source is not None else "External"
            receiver = Address(tx.in_msg.destination) if tx.in_msg.destination is not None else "Unkwnon"

            # get TON amount
            value = float(tx.in_msg.value or 0) / 1e9

            if tx.in_msg.message_content is None:
                LOGGER.warn(f"No message content in tx {tx.hash}")
                continue

            if tx.in_msg.message_content.decoded is not None:
                # comment message
                if isinstance(tx.in_msg.message_content.decoded, TextComment):
                    comment = tx.in_msg.message_content.decoded.comment
                else:
                    comment = tx.in_msg.message_content.decoded.hex_comment
                src = labeler(sender)
                dst = labeler(receiver)
                LOGGER.info(f"{src} sends {dst} {value} TON to {receiver} with comment {comment}")
                continue

            # normal message with cell data
            cs = CellSlice(tx.in_msg.message_content.body)

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
