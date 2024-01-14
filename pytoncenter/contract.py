from enum import Enum
from tonpy import begin_cell, Cell
from abc import ABC
from typing import Optional, Dict, TypedDict, Union
from .address import Address


class StateInit(TypedDict):
    code: Cell
    data: Cell
    address: Address
    state_init: Cell


class ExternalMessage(TypedDict):
    address: Address
    message: Cell
    state_init: Cell
    code: Cell
    data: Cell


class ExternalMessageWithSignature(TypedDict):
    address: Address
    message: Cell
    body: Cell
    signature: bytes
    signing_message: Cell
    state_init: Cell
    code: Cell
    data: Cell


class SendMode(Enum):
    OrdinalMessage = 0
    SendPayGasSeparately = 1
    SendIgnoreErrors = 2
    SendDestroyIfZero = 32
    SendRemainingValue = 64
    SendRemainingBalance = 128


class Contract(ABC):
    def __init__(
        self, address: Optional[str] = None, workchain: Optional[int] = None, **options
    ):
        self._address = address
        self._wc = workchain
        self.options = options

    @property
    def address(self):
        if self._address is None:
            self._address = self.create_state_init()["address"]

    def get_code_cell(self):
        code = self.options.get("code")
        assert isinstance(code, Cell), "Contract: code must be Cell"
        if not self.options.get("code"):
            raise Exception("Contract: code is not set in options")
        return code

    def get_data_cell(self) -> Cell:
        return Cell()

    def create_init_external_message(self) -> ExternalMessage:
        init = self.create_state_init()
        header = Contract.create_external_message_header(init["address"])
        external_msg = Contract.create_common_msg_info(
            header=header, state_init=init["state_init"]
        )
        return {
            "address": init["address"],
            "message": external_msg,
            "state_init": init["state_init"],
            "code": init["code"],
            "data": init["data"],
        }

    @classmethod
    def create_external_message_header(
        cls: "Contract", dest: str, src: Optional[str] = None, import_fee: int = 0
    ) -> Cell:
        cell = begin_cell()
        cell.store_uint(2, 2)
        if src is None:
            cell.store_uint(0, 2)
        else:
            cell.store_address(src)
        cell.store_address(dest)
        cell.store_grams(import_fee)
        return cell

    @classmethod
    def create_internal_message_header(
        cls: "Contract",
        dest: str,
        coins: int = 0,
        ihr_disabled: bool = True,
        bounce: Optional[bool] = None,
        bounced: bool = False,
        src: Optional[str] = None,
        currency_collection: Optional[bool] = None,
        ihr_fees: int = 0,
        fwd_fees: int = 0,
        created_lt: int = 0,
        created_at: int = 0,
    ):
        message = begin_cell()
        message.store_bool(False)
        message.store_bool(ihr_disabled)
        if bounce is not None:
            message.store_bool(bounce)
        else:
            message.store_bool(Address(dest)._is_bounceable)
        message.store_bool(bounced)
        if src is None:
            message.store_uint(0, 2)
        else:
            message.store_address(src)
        message.store_address(dest)
        message.store_grams(coins)
        if currency_collection:
            raise Exception("Contract: currency collection is not implemented")
        message.store_bool(bool(currency_collection))
        message.store_grams(ihr_fees)
        message.store_grams(fwd_fees)
        message.store_uint(created_lt, 64)
        message.store_uint(created_at, 32)
        return message

    @classmethod
    def create_common_msg_info(
        cls: "Contract",
        header: Cell,
        state_init: Optional[Cell] = None,
        body: Optional[Cell] = None,
    ) -> Cell:
        common_msg_info = begin_cell()
        common_msg_info.store_builder(header)
        if state_init:
            common_msg_info.store_bool(True)
            # TODO: get free bits
        else:
            common_msg_info.store_bool(False)

        # Body part
        if body:
            pass
        else:
            common_msg_info.store_bool(False)

        return common_msg_info

    def create_state_init(self) -> StateInit:
        code_cell = self.get_code_cell()
        data_cell = self.get_data_cell()
        state_init = begin_cell()
        split_depth = None
        tick_tock = None
        library = None
        state_init.store_bitstring(
            "".join(
                [
                    int(bool(split_depth)),
                    int(bool(tick_tock)),
                    int(code_cell),
                    int(data_cell),
                    int(bool(library)),
                ]
            )
        )
        return {
            "code": code_cell,
            "data": data_cell,
            "address": Address(f"{self._wc}:{state_init.get_hash()}"),
            "state_init": state_init.end_cell(),
        }


class WalletContract(Contract):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def from_keypair(public_key: str, private_key: str, **kwargs):
        kwargs["public_key"] = public_key
        kwargs["private_key"] = private_key
        return WalletContract(**kwargs)

    @staticmethod
    def from_address(address: str, **kwargs):
        kwargs["address"] = address
        return WalletContract(**kwargs)

    def get_data_cell(self) -> Cell:
        cell = begin_cell()
        cell.store_uint(0, 32)

    def create_signing_message(self, seqno: Optional[int] = None):
        pass

    def create_transfer_message(
        self,
        to_addr: str,
        amount: int,
        seqno: int,
        payload: Union[Cell, str, bytes, None] = None,
        send_mode: SendMode = SendMode.SendIgnoreErrors | SendMode.SendPayGasSeparately,
        dummy_signature: bool = False,
        state_init: Optional[Cell] = None,
    ):
        return

    def create_external_message(
        self, signing_message: Cell, seqno: int, dummy_signature: bool = False
    ) -> ExternalMessageWithSignature:
        pass

    def create_init_external_message(self) -> ExternalMessage:
        return super().create_init_external_message()


class WalletContractV4(WalletContract):
    pass
