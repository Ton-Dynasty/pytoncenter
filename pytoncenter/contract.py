from enum import Enum
from tonpy import begin_cell, Cell
from abc import ABC
from typing import Optional, Dict, TypedDict

class StateInit(TypedDict):
    code: Cell
    data: Cell
    address: str
    state_init: str

class SendMode(Enum):
    OrdinalMessage = 0
    SendPayGasSeparately = 1
    SendIgnoreErrors = 2
    SendDestroyIfZero = 32
    SendRemainingValue = 64
    SendRemainingBalance = 128
    
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
    
    def get_data_cell(self) -> Cell:
        return begin_cell().end_cell()
    
    def create_init_external_message(self):
        pass
    
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
            # TODO: store address is bounceable
            message.store_bool()
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
            
    def create_state_init(self) -> StateInit:
        state_init = begin_cell()
        split_depth = None
        tick_tock = None
        state_init.store_bitstring("".join([
            str(int(bool()))
        ]))