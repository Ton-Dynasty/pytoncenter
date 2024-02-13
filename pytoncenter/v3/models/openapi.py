from __future__ import annotations

from typing import Any, List, Literal, Optional, Union

from pydantic import BaseModel, Field, model_serializer

from .types import PyAddress


class AccountBalance(BaseModel):
    account: PyAddress = Field(..., title="Account")
    balance: str = Field(..., title="Balance")


class BinaryComment(BaseModel):
    type: Literal["binary_comment"] = Field("binary_comment", title="Type")
    hex_comment: str = Field(..., title="Hex Comment")


class BlockReference(BaseModel):
    workchain: int = Field(..., title="Workchain")
    shard: str = Field(..., title="Shard")
    seqno: int = Field(..., title="Seqno")


class EstimateFeeRequest(BaseModel):
    address: PyAddress = Field(..., title="Address")
    body: str = Field(..., title="Body")
    init_code: Optional[str] = Field(None, title="Init Code")
    init_data: Optional[str] = Field(None, title="Init Data")
    ignore_chksig: Optional[bool] = Field(True, title="Ignore Chksig")


class ExternalMessage(BaseModel):
    boc: str = Field(
        ...,
        examples=["te6ccgECBQEAARUAAkWIAWTtae+KgtbrX26Bep8JSq8lFLfGOoyGR/xwdjfvpvEaHg"],
        title="Boc",
    )


class Fee(BaseModel):
    in_fwd_fee: int = Field(..., title="In Fwd Fee")
    storage_fee: int = Field(..., title="Storage Fee")
    gas_fee: int = Field(..., title="Gas Fee")
    fwd_fee: int = Field(..., title="Fwd Fee")


GetMethodParameterType = Literal["cell", "slice", "num", "list", "tuple", "unsupported_type"]


class JettonBurn(BaseModel):
    query_id: str = Field(..., title="Query Id")
    owner: PyAddress = Field(..., title="Owner")
    jetton_master: PyAddress = Field(..., title="Jetton Master")
    transaction_hash: str = Field(..., title="Transaction Hash")
    transaction_lt: str = Field(..., title="Transaction Lt")
    transaction_now: int = Field(..., title="Transaction Now")
    response_destination: Optional[str] = Field(..., title="Response Destination")
    custom_payload: Optional[str] = Field(..., title="Custom Payload")


class JettonMaster(BaseModel):
    address: PyAddress = Field(..., title="Address")
    total_supply: str = Field(..., title="Total Supply")
    mintable: bool = Field(..., title="Mintable")
    admin_address: Optional[PyAddress] = Field(..., title="Admin Address")
    last_transaction_lt: str = Field(..., title="Last Transaction Lt")
    jetton_wallet_code_hash: str = Field(..., title="Jetton Wallet Code Hash")
    jetton_content: Any = Field(..., title="Jetton Content")
    code_hash: str = Field(..., title="Code Hash")
    data_hash: str = Field(..., title="Data Hash")


class JettonTransfer(BaseModel):
    query_id: str = Field(..., title="Query Id")
    source: PyAddress = Field(..., title="Source")
    destination: PyAddress = Field(..., title="Destination")
    amount: str = Field(..., title="Amount")
    source_wallet: PyAddress = Field(..., title="Source Wallet")
    jetton_master: PyAddress = Field(..., title="Jetton Master")
    transaction_hash: str = Field(..., title="Transaction Hash")
    transaction_lt: str = Field(..., title="Transaction Lt")
    transaction_now: int = Field(..., title="Transaction Now")
    response_destination: Optional[PyAddress] = Field(..., title="Response Destination")
    custom_payload: Optional[str] = Field(..., title="Custom Payload")
    forward_ton_amount: Optional[str] = Field(..., title="Forward Ton Amount")
    forward_payload: Optional[str] = Field(..., title="Forward Payload")


class JettonWallet(BaseModel):
    address: PyAddress = Field(..., title="Address")
    balance: str = Field(..., title="Balance")
    owner: PyAddress = Field(..., title="Owner")
    jetton: PyAddress = Field(..., title="Jetton")
    last_transaction_lt: str = Field(..., title="Last Transaction Lt")
    code_hash: str = Field(..., title="Code Hash")
    data_hash: str = Field(..., title="Data Hash")


class MessageInitState(BaseModel):
    hash: str = Field(..., title="Hash")
    body: str = Field(..., title="Body")


class NFTCollection(BaseModel):
    address: PyAddress = Field(..., title="Address")
    owner_address: Optional[PyAddress] = Field(..., title="Owner Address")
    last_transaction_lt: str = Field(..., title="Last Transaction Lt")
    next_item_index: str = Field(..., title="Next Item Index")
    collection_content: Any = Field(..., title="Collection Content")
    code_hash: str = Field(..., title="Code Hash")
    data_hash: str = Field(..., title="Data Hash")


class NFTItem(BaseModel):
    address: PyAddress = Field(..., title="Address")
    collection_address: Optional[PyAddress] = Field(..., title="Collection Address")
    owner_address: Optional[PyAddress] = Field(..., title="Owner Address")
    init: bool = Field(..., title="Init")
    index: str = Field(..., title="Index")
    last_transaction_lt: str = Field(..., title="Last Transaction Lt")
    code_hash: str = Field(..., title="Code Hash")
    data_hash: str = Field(..., title="Data Hash")
    content: Any = Field(..., title="Content")
    collection: Optional[NFTCollection]


class NFTTransfer(BaseModel):
    query_id: str = Field(..., title="Query Id")
    nft_address: PyAddress = Field(..., title="Nft Address")
    transaction_hash: str = Field(..., title="Transaction Hash")
    transaction_lt: str = Field(..., title="Transaction Lt")
    transaction_now: int = Field(..., title="Transaction Now")
    old_owner: PyAddress = Field(..., title="Old Owner")
    new_owner: PyAddress = Field(..., title="New Owner")
    response_destination: Optional[str] = Field(..., title="Response Destination")
    custom_payload: Optional[str] = Field(..., title="Custom Payload")
    forward_amount: str = Field(..., title="Forward Amount")
    forward_payload: Optional[str] = Field(..., title="Forward Payload")


class SentMessage(BaseModel):
    message_hash: str = Field(
        ...,
        description="Hash of sent message in hex format",
        examples=["383E348617141E35BC25ED9CD0EDEC2A4EAF6413948BF1FB7F865CEFE8C2CD44"],
        title="Message Hash",
    )


class TextComment(BaseModel):
    type: Literal["text_comment"] = Field("text_comment", title="Type")
    comment: str = Field(..., title="Comment")


class ValidationError(BaseModel):
    loc: List[Union[str, int]] = Field(..., title="Location")
    msg: str = Field(..., title="Message")
    type: str = Field(..., title="Error Type")


class WalletInfo(BaseModel):
    balance: str = Field(..., title="Balance")
    wallet_type: Optional[str] = Field(..., title="Wallet Type")
    seqno: Optional[int] = Field(..., title="Seqno")
    wallet_id: Optional[int] = Field(..., title="Wallet Id")
    last_transaction_lt: Optional[str] = Field(..., title="Last Transaction Lt")
    last_transaction_hash: Optional[str] = Field(..., title="Last Transaction Hash")
    status: Literal["uninit", "frozen", "active", "nonexist"] = Field(..., title="Status")


class Account(BaseModel):
    balance: str = Field(..., title="Balance")
    code: Optional[str] = Field(..., title="Code")
    data: Optional[str] = Field(..., title="Data")
    last_transaction_lt: Optional[str] = Field(..., title="Last Transaction Lt")
    last_transaction_hash: Optional[str] = Field(..., title="Last Transaction Hash")
    frozen_hash: Optional[str] = Field(..., title="Frozen Hash")
    status: Literal["uninit", "frozen", "active", "nonexist"] = Field(..., title="Status")


class AccountState(BaseModel):
    hash: str = Field(..., title="Hash")
    account: PyAddress = Field(..., title="Account")
    balance: str = Field(..., title="Balance")
    account_status: Literal["uninit", "frozen", "active", "nonexist"] = Field(..., title="Account Status")
    frozen_hash: Optional[str] = Field(..., title="Frozen Hash")
    code_hash: Optional[str] = Field(..., title="Code Hash")
    data_hash: Optional[str] = Field(..., title="Data Hash")


class Block(BaseModel):
    workchain: int = Field(..., title="Workchain")
    shard: str = Field(..., title="Shard")
    seqno: int = Field(..., title="Seqno")
    root_hash: str = Field(..., title="Root Hash")
    file_hash: str = Field(..., title="File Hash")
    global_id: int = Field(..., title="Global Id")
    version: int = Field(..., title="Version")
    after_merge: bool = Field(..., title="After Merge")
    before_split: bool = Field(..., title="Before Split")
    after_split: bool = Field(..., title="After Split")
    want_split: bool = Field(..., title="Want Split")
    key_block: bool = Field(..., title="Key Block")
    vert_seqno_incr: bool = Field(..., title="Vert Seqno Incr")
    flags: int = Field(..., title="Flags")
    gen_utime: str = Field(..., title="Gen Utime")
    start_lt: str = Field(..., title="Start Lt")
    end_lt: str = Field(..., title="End Lt")
    validator_list_hash_short: int = Field(..., title="Validator List Hash Short")
    gen_catchain_seqno: int = Field(..., title="Gen Catchain Seqno")
    min_ref_mc_seqno: int = Field(..., title="Min Ref Mc Seqno")
    prev_key_block_seqno: int = Field(..., title="Prev Key Block Seqno")
    vert_seqno: int = Field(..., title="Vert Seqno")
    master_ref_seqno: Optional[int] = Field(..., title="Master Ref Seqno")
    rand_seed: str = Field(..., title="Rand Seed")
    created_by: str = Field(..., title="Created By")
    tx_count: Optional[int] = Field(..., title="Tx Count")
    masterchain_block_ref: Optional[BlockReference]


class EstimateFeeResponse(BaseModel):
    source_fees: Fee
    destination_fees: List[Fee] = Field(..., title="Destination Fees")


class GetMethodParameterInput(BaseModel):
    type: GetMethodParameterType = Field(..., title="Type")
    value: Optional[Union[List[GetMethodParameterInput], str, int, bool, PyAddress]] = Field(..., title="Value")

    @model_serializer
    def serialize_value(self):
        if isinstance(self.value, int) and self.type == "num":
            v = hex(self.value)
            return {"type": self.type, "value": v}
        if isinstance(self.value, bool) and self.type == "num":
            v = "-0x1" if self.value else "0x0"
            return {"type": self.type, "value": v}
        return {"type": self.type, "value": self.value}


class GetMethodParameterOutput(BaseModel):
    type: GetMethodParameterType
    value: Optional[Union[List[GetMethodParameterOutput], str]] = Field(..., title="Value")


class HTTPValidationError(BaseModel):
    detail: Optional[List[ValidationError]] = Field(None, title="Detail")


class MasterchainInfo(BaseModel):
    first: Block
    last: Block


class MessageContent(BaseModel):
    hash: str = Field(..., title="Hash")
    body: str = Field(..., title="Body")
    decoded: Optional[Union[TextComment, BinaryComment]] = Field(..., title="Decoded")


class RunGetMethodRequest(BaseModel):
    address: PyAddress = Field(..., title="Address")
    method: str = Field(..., title="Method")
    stack: List[GetMethodParameterInput] = Field(..., title="Stack")


class RunGetMethodResponse(BaseModel):
    gas_used: int = Field(..., title="Gas Used")
    exit_code: int = Field(..., title="Exit Code")
    stack: List[GetMethodParameterOutput] = Field(..., title="Stack")


class Message(BaseModel):
    hash: str = Field(..., title="Hash")
    source: Optional[str] = Field(..., title="Source")
    source_friendly: Optional[str] = Field(..., title="Source Friendly")
    destination: Optional[str] = Field(..., title="Destination")
    destination_friendly: Optional[str] = Field(..., title="Destination Friendly")
    value: Optional[str] = Field(..., title="Value")
    fwd_fee: Optional[str] = Field(..., title="Fwd Fee")
    ihr_fee: Optional[str] = Field(..., title="Ihr Fee")
    created_lt: Optional[str] = Field(..., title="Created Lt")
    created_at: Optional[str] = Field(..., title="Created At")
    opcode: Optional[str] = Field(..., title="Opcode")
    ihr_disabled: Optional[bool] = Field(..., title="Ihr Disabled")
    bounce: Optional[bool] = Field(..., title="Bounce")
    bounced: Optional[bool] = Field(..., title="Bounced")
    import_fee: Optional[str] = Field(..., title="Import Fee")
    message_content: Optional[MessageContent]
    init_state: Optional[MessageInitState]


class Transaction(BaseModel):
    account: PyAddress = Field(..., title="Account")
    account_friendly: str = Field(..., title="Account Friendly")
    hash: str = Field(..., title="Hash")
    lt: str = Field(..., title="Lt")
    now: int = Field(..., title="Now")
    orig_status: Literal["uninit", "frozen", "active", "nonexist"] = Field(..., title="Orig Status")
    end_status: Literal["uninit", "frozen", "active", "nonexist"] = Field(..., title="End Status")
    total_fees: str = Field(..., title="Total Fees")
    account_state_hash_before: str = Field(..., title="Account State Hash Before")
    account_state_hash_after: str = Field(..., title="Account State Hash After")
    prev_trans_hash: str = Field(..., title="Prev Trans Hash")
    prev_trans_lt: str = Field(..., title="Prev Trans Lt")
    description: Any = Field(..., title="Description")
    block_ref: Optional[BlockReference]
    in_msg: Optional[Message]
    out_msgs: List[Message] = Field(..., title="Out Msgs")
    account_state_before: Optional[AccountState]
    account_state_after: Optional[AccountState]
    trace_id: Optional[str] = Field(..., title="Trace Id")


class TransactionTrace(BaseModel):
    id: str = Field(..., title="Id")
    transaction: Transaction
    children: List[TransactionTrace] = Field(..., title="Children")


GetMethodParameterInput.model_rebuild()
GetMethodParameterOutput.model_rebuild()
TransactionTrace.model_rebuild()
