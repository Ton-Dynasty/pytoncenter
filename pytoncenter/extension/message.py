from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

from tonpy import CellSlice

from pytoncenter.address import Address
from pytoncenter.utils import get_opcode

T = TypeVar("T", bound="BaseMessage")


class BaseMessage(ABC, Generic[T]):
    OPCODE = ""

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @classmethod
    def _preparse(cls, cs: CellSlice) -> CellSlice:
        opcode = get_opcode(cs.load_uint(32))
        assert opcode == cls.OPCODE, f"opcode {opcode} is not {cls.OPCODE}"
        return cs

    @classmethod
    @abstractmethod
    def _parse(cls, body: CellSlice) -> T:
        """
        the cellslice with opcode and body
        """
        raise NotImplementedError

    @classmethod
    def parse(cls, cs: CellSlice) -> T:
        body = cls._preparse(cs)
        return cls._parse(body)

    def to_boc(self) -> str:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{self.name}({self.OPCODE})"


class JettonMessage:
    class InternalTransfer(BaseMessage["InternalTransfer"]):
        OPCODE = "0x178d4519"

        def __init__(
            self,
            query_id: int,
            amount: int,
            sender: Address,
            response_address: Address,
            forward_ton_amount: int,
            forward_payload: Optional[CellSlice],
        ):
            self.query_id = query_id
            self.amount = amount
            self.sender = sender
            self.response_address = response_address
            self.forward_ton_amount = forward_ton_amount
            self.forward_payload = forward_payload

        @classmethod
        def _parse(cls, body: CellSlice):
            """
            internal_transfer  query_id:uint64 amount:(VarUInteger 16) from:MsgAddress
                        response_address:MsgAddress
                        forward_ton_amount:(VarUInteger 16)
                        forward_payload:(Either Cell ^Cell)
            """
            query_id = body.load_uint(64)
            amount = body.load_var_int(16)
            sender = Address(body.load_address())
            response_address = Address(body.load_address())
            forward_ton_amount = body.load_var_uint(16)
            forward_payload = None if body.empty_ext() else body.load_ref(as_cs=True)
            return cls(
                query_id=query_id,
                amount=amount,
                sender=sender,
                response_address=response_address,
                forward_ton_amount=forward_ton_amount,
                forward_payload=forward_payload,
            )

    class Transfer(BaseMessage["Transfer"]):
        OPCODE = "0x0f8a7ea5"

        def __init__(
            self,
            query_id: int,
            amount: int,
            destination: Address,
            response_destination: Address,
            custom_payload: Optional[CellSlice],
            forward_ton_amount: int,
            forward_payload: Optional[CellSlice],
        ):
            self.query_id = query_id
            self.amount = amount
            self.destination = destination
            self.response_destination = response_destination
            self.custom_payload = custom_payload
            self.forward_ton_amount = forward_ton_amount
            self.forward_payload = forward_payload

        @classmethod
        def _parse(cls, body: CellSlice):
            """
            transfer query_id:uint64 amount:(VarUInteger 16) destination:MsgAddress
            response_destination:MsgAddress custom_payload:(Maybe ^Cell)
            forward_ton_amount:(VarUInteger 16) forward_payload:(Either Cell ^Cell)
            """
            query_id = body.load_uint(64)
            amount = body.load_var_uint(16)
            destination = Address(body.load_address())
            response_destination = Address(body.load_address())

            custom_payload = None
            custom_payload_exists = body.load_bool()
            if custom_payload_exists:
                custom_payload = body.load_ref(as_cs=True)

            forward_ton_amount = body.load_var_uint(16)

            forward_payload = None
            if not body.empty_ext():
                forward_payload = body.load_ref(as_cs=True)

            return cls(query_id, amount, destination, response_destination, custom_payload, forward_ton_amount, forward_payload)

    class Excess(BaseMessage["Excess"]):
        OPCODE = "0xd53276db"

        def __init__(self, query_id: int):
            self.query_id = query_id

        @staticmethod
        def _parse(cs: CellSlice) -> JettonMessage.Excess:
            """
            excess query_id:uint64 amount:(VarUInteger 16)
            """
            query_id = cs.load_uint(64)
            return JettonMessage.Excess(query_id)

    class TransferNotification(BaseMessage["TransferNotification"]):
        OPCODE = "0x7362d09c"

        def __init__(self, query_id: int, amount: int, sender: Address, forward_payload: Optional[CellSlice]):
            self.query_id = query_id
            self.amount = amount
            self.sender = sender
            self.forward_payload = forward_payload

        @classmethod
        def _parse(cls, body: CellSlice) -> JettonMessage.TransferNotification:
            """
            transfer_notification query_id:uint64 amount:(VarUInteger 16)
            sender:MsgAddress forward_payload:(Either Cell ^Cell)
            """
            query_id = body.load_uint(64)
            amount = body.load_var_uint(16)
            sender = Address(body.load_address())
            forward_payload = None
            if not body.empty_ext():
                forward_payload = body.load_ref(as_cs=True)
            return cls(query_id, amount, sender, forward_payload)

    class Burn(BaseMessage["Burn"]):
        OPCODE = "0x595f07bc"

        def __init__(
            self,
            query_id: int,
            amount: int,
            response_destination: Address,
            custom_payload: Optional[CellSlice],
        ):
            self.query_id = query_id
            self.amount = amount
            self.response_destination = response_destination
            self.custom_payload = custom_payload

        @classmethod
        def _parse(cls, body: CellSlice) -> JettonMessage.Burn:
            """
            burn query_id:uint64 amount:(VarUInteger 16)
                response_destination:MsgAddress custom_payload:(Maybe ^Cell)
            """
            query_id = body.load_uint(64)
            amount = body.load_var_uint(16)
            response_destination = Address(body.load_address())
            custom_payload = None
            custom_payload_exists = body.load_bool()
            if custom_payload_exists:
                custom_payload = body.load_ref(as_cs=True)
            return cls(query_id, amount, response_destination, custom_payload)

    class BurnNotification(BaseMessage["BurnNotification"]):
        OPCODE = "0x7bdd97de"

        def __init__(self, query_id: int, amount: int, sender: Address, response_destination: Address):
            self.query_id = query_id
            self.amount = amount
            self.sender = sender
            self.response_destination = response_destination

        @classmethod
        def _parse(cls, body: CellSlice) -> JettonMessage.BurnNotification:
            """
            burn_notification query_id:uint64 amount:(VarUInteger 16)
                sender:MsgAddress response_destination:MsgAddress
            """
            query_id = body.load_uint(64)
            amount = body.load_var_uint(16)
            sender = Address(body.load_address())
            response_destination = Address(body.load_address())
            return cls(query_id, amount, sender, response_destination)


class NFTMessage:
    pass
