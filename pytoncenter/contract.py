from enum import Enum
from tonpy import begin_cell, Cell, CellBuilder
from abc import ABC, abstractmethod
from typing import Optional, Dict, TypedDict, Union
from .address import Address
import time

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

def to_bitstring(value: Union[bytes, bytearray]) -> str:
    """
    convert bytes or bytearray to bitstring
    
    Parameters
    ----------
    value: bytes or bytearray
        bytes or bytearray to convert
        
    Returns
    -------
    str
        bitstring
    """
    assert isinstance(value, (bytes, bytearray)), "value must be bytes or bytearray"
    return "".join([bin(i)[2:].zfill(8) for i in value])
    
class Contract(ABC):
    def __init__(self, address:Optional[str]=None, workchain: Optional[int]=None, **options):
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
    
    @abstractmethod
    def get_data_cell(self) -> Cell:
        return Cell()
    
    def create_init_external_message(self) -> ExternalMessage:
        init = self.create_state_init()
        header = Contract.create_external_message_header(init["address"])
        external_msg = Contract.create_common_msg_info(header=header, state_init=init["state_init"])
        return {
            "address": init["address"],
            "message": external_msg,
            "state_init": init["state_init"],
            "code": init["code"],
            "data": init["data"],
        }
        
    @classmethod
    def create_external_message_header(cls: "Contract", dest: str, src:Optional[str]=None, import_fee:int = 0) -> Cell:
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
    def create_internal_message_header(cls: "Contract", dest: str, coins: int = 0, ihr_disabled:bool=True, bounce: Optional[bool]=None, bounced: bool=False, src:Optional[str]=None, currency_collection: Optional[bool]=None, ihr_fees: int = 0, fwd_fees:int=0, created_lt:int = 0, created_at: int = 0):
        message = begin_cell()
        message.store_bool(False)
        message.store_bool(ihr_disabled)
        if bounce is not None:
            message.store_bool(bounce)
        else:
            message.store_bool(Address(dest).is_bounceable)
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
    def create_common_msg_info(cls: "Contract", header: Cell, state_init: Optional[Cell]=None, body: Optional[Cell]=None) -> Cell:
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
        state_init.store_bitstring("".join([
            int(bool(split_depth)),
            int(bool(tick_tock)),
            int(code_cell),
            int(data_cell),
            int(bool(library))
        ]))
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
        cell.store_bitstring(self.options["public_key"])
        return cell.end_cell()
    
    @abstractmethod
    def create_signing_message(self, seqno: Optional[int] = None) -> CellBuilder:
        raise NotImplementedError
    
    def create_transfer_message(self, to_addr: str, amount: int, seqno: int, payload: Union[Cell, str, bytes, None] = None, send_mode: SendMode = SendMode.SendIgnoreErrors | SendMode.SendPayGasSeparately, dummy_signature:bool = False, state_init: Optional[Cell] = None):
        payload_cell = begin_cell()
        if payload:
            if isinstance(payload, str):
                payload_cell.store_uint(0, 32)
                payload_cell.store_string(payload)
            elif isinstance(payload, Cell):
                payload_cell = payload
            else:
                payload_cell.store_bitstring(to_bitstring(payload))
        order_header = Contract.create_internal_message_header(to_addr, amount)  
        order = Contract.create_common_msg_info(order_header, state_init, payload_cell)
        signing_message = self.create_signing_message(seqno)
        signing_message.store_uint(send_mode.value, 8)
        signing_message.store_builder(order)
        return self.create_external_message(signing_message, seqno, dummy_signature)
        
    def create_external_message(self, signing_message: Cell, seqno: int, dummy_signature: bool = False) -> ExternalMessageWithSignature:
        raise NotImplementedError
    
    def create_init_external_message(self) -> ExternalMessage:
        raise NotImplementedError



class WalletContractV4(WalletContract):
    def get_data_cell(self) -> Cell:
        cell = begin_cell()
        cell.store_uint(0, 32)
        cell.store_uint(self.options["wallet_id"], 32)
        # store public key
        cell.store_bitstring(self.options["public_key"])
        cell.store_uint(0, 1) # empty plugin dict
        return cell.end_cell()
    
    def create_signing_message(self, seqno: Optional[int]= None, without_op: bool=False) -> CellBuilder:
        seqno = seqno or 0
        message = begin_cell()
        message.store_uint(self.options["wallet_id"], 32)
        if seqno == 0:
            message.store_ones(32)
        else:
            timestamp = int(time.time())
            message.store_uint(timestamp + 60, 32)
        message.store_uint(seqno, 32)
        if not without_op:
            message.store_uint(0, 8)
        return message
            
    

class WalletContractV4R2(WalletContractV4):
    def __init__(self, **kwargs):
        self._code = "B5EE9C72410214010002D4000114FF00F4A413F4BCF2C80B010201200203020148040504F8F28308D71820D31FD31FD31F02F823BBF264ED44D0D31FD31FD3FFF404D15143BAF2A15151BAF2A205F901541064F910F2A3F80024A4C8CB1F5240CB1F5230CBFF5210F400C9ED54F80F01D30721C0009F6C519320D74A96D307D402FB00E830E021C001E30021C002E30001C0039130E30D03A4C8CB1F12CB1FCBFF1011121302E6D001D0D3032171B0925F04E022D749C120925F04E002D31F218210706C7567BD22821064737472BDB0925F05E003FA403020FA4401C8CA07CBFFC9D0ED44D0810140D721F404305C810108F40A6FA131B3925F07E005D33FC8258210706C7567BA923830E30D03821064737472BA925F06E30D06070201200809007801FA00F40430F8276F2230500AA121BEF2E0508210706C7567831EB17080185004CB0526CF1658FA0219F400CB6917CB1F5260CB3F20C98040FB0006008A5004810108F45930ED44D0810140D720C801CF16F400C9ED540172B08E23821064737472831EB17080185005CB055003CF1623FA0213CB6ACB1FCB3FC98040FB00925F03E20201200A0B0059BD242B6F6A2684080A06B90FA0218470D4080847A4937D29910CE6903E9FF9837812801B7810148987159F31840201580C0D0011B8C97ED44D0D70B1F8003DB29DFB513420405035C87D010C00B23281F2FFF274006040423D029BE84C600201200E0F0019ADCE76A26840206B90EB85FFC00019AF1DF6A26840106B90EB858FC0006ED207FA00D4D422F90005C8CA0715CBFFC9D077748018C8CB05CB0222CF165005FA0214CB6B12CCCCC973FB00C84014810108F451F2A7020070810108D718FA00D33FC8542047810108F451F2A782106E6F746570748018C8CB05CB025006CF165004FA0214CB6A12CB1FCB3FC973FB0002006C810108D718FA00D33F305224810108F459F2A782106473747270748018C8CB05CB025005CF165003FA0213CB6ACB1F12CB3FC973FB00000AF400C9ED54696225E5"
        kwargs["code"] = Cell(self._code)
        super().__init__(**kwargs)
        if "wallet_id" not in kwargs:
            self.options["wallet_id"] = 698983191 + self.options["wc"]