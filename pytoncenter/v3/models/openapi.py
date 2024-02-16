from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, model_serializer

from .types import AddressLike


class AccountBalance(BaseModel):
    account: AddressLike = Field(..., title="Account")
    balance: str = Field(..., title="Balance")


class BinaryComment(BaseModel):
    type: Literal["binary_comment"] = Field(default="binary_comment", title="Type")
    hex_comment: str = Field(..., title="Hex Comment")


class BlockReference(BaseModel):
    workchain: int = Field(..., title="Workchain")
    shard: str = Field(..., title="Shard")
    seqno: int = Field(..., title="Seqno")


class EstimateFeeRequest(BaseModel):
    address: AddressLike = Field(..., title="Address")
    body: str = Field(..., title="Body")
    init_code: Optional[str] = Field(default=None, title="Init Code")
    init_data: Optional[str] = Field(default=None, title="Init Data")
    ignore_chksig: Optional[bool] = Field(default=True, title="Ignore Chksig")


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
    owner: AddressLike = Field(..., title="Owner")
    jetton_master: AddressLike = Field(..., title="Jetton Master")
    transaction_hash: str = Field(..., title="Transaction Hash")
    transaction_lt: str = Field(..., title="Transaction Lt")
    transaction_now: int = Field(..., title="Transaction Now")
    response_destination: Optional[str] = Field(..., title="Response Destination")
    custom_payload: Optional[str] = Field(..., title="Custom Payload")


class JettonContent(BaseModel):
    uri: Optional[str] = Field(None, description="A URI pointing to JSON document with metadata. Used by 'Semi-chain content layout'. ASCII string.")
    name: Optional[str] = Field(None, description="The name of the token - e.g. 'Example Coin'. UTF8 string.")
    description: Optional[str] = Field(None, description="Describes the token - e.g. 'This is an example jetton for the TON network'. UTF8 string.")
    image: Optional[str] = Field(None, description="A URI pointing to a jetton icon with mime type image. ASCII string.")
    image_data: Optional[str] = Field(None, description="Either binary representation of the image for onchain layout or base64 for offchain layout.")
    symbol: Optional[str] = Field(None, description="The symbol of the token - e.g. 'XMPL'. Used in the form 'You received 99 XMPL'. UTF8 string.")
    decimals: Optional[int] = Field(
        9,
        description="The number of decimals the token uses - e.g. 8, means to divide the token amount by 100000000 to get its user representation, while 0 means that tokens are indivisible. If not specified, 9 is used by default. UTF8 encoded string with number from 0 to 255.",
        ge=0,
        le=255,
    )
    amount_style: Optional[Literal["n", "n-of-total", "%"]] = Field(
        "n",
        description="Needed by external applications to understand which format for displaying the number of jettons. 'n' - number of jettons (default value). 'n-of-total' - the number of jettons out of the total number of issued jettons. '%' - percentage of jettons from the total number of issued jettons.",
    )
    render_type: Optional[Literal["currency", "game"]] = Field(
        "currency",
        description="Needed by external applications to understand which group the jetton belongs to and how to display it. 'currency' - display as currency (default value). 'game' - display for games as NFT, considering the amount_style.",
    )


class JettonMaster(BaseModel):
    address: AddressLike = Field(..., title="Address")
    total_supply: int = Field(..., title="Total Supply")
    mintable: bool = Field(..., title="Mintable")
    admin_address: Optional[AddressLike] = Field(..., title="Admin Address")
    last_transaction_lt: int = Field(..., title="Last Transaction Lt")
    jetton_wallet_code_hash: str = Field(..., title="Jetton Wallet Code Hash")
    jetton_content: Optional[JettonContent] = Field(None, title="Jetton Content")
    code_hash: str = Field(..., title="Code Hash")
    data_hash: str = Field(..., title="Data Hash")


class JettonTransfer(BaseModel):
    query_id: int = Field(..., title="Query Id")
    source: AddressLike = Field(..., title="Source")
    destination: AddressLike = Field(..., title="Destination")
    amount: int = Field(..., title="Amount")
    source_wallet: AddressLike = Field(..., title="Source Wallet")
    jetton_master: AddressLike = Field(..., title="Jetton Master")
    transaction_hash: str = Field(..., title="Transaction Hash")
    transaction_lt: int = Field(..., title="Transaction Lt")
    transaction_now: int = Field(..., title="Transaction Now")
    response_destination: Optional[AddressLike] = Field(..., title="Response Destination")
    custom_payload: Optional[str] = Field(..., title="Custom Payload")
    forward_ton_amount: Optional[int] = Field(..., title="Forward Ton Amount")
    forward_payload: Optional[str] = Field(..., title="Forward Payload")


class JettonWallet(BaseModel):
    address: AddressLike = Field(..., title="Address")
    balance: int = Field(..., title="Balance")
    owner: AddressLike = Field(..., title="Owner")
    jetton: AddressLike = Field(..., title="Jetton")
    last_transaction_lt: int = Field(..., title="Last Transaction Lt")
    code_hash: str = Field(..., title="Code Hash")
    data_hash: str = Field(..., title="Data Hash")


class MessageInitState(BaseModel):
    hash: str = Field(..., title="Hash")
    body: str = Field(..., title="Body")


class NFTMetadata(BaseModel):
    uri: Optional[str] = Field(default=None, description="Used by `Semi-chain content layout`. ASCII string. A URI pointing to JSON document with metadata.")
    name: Optional[str] = Field(default=None, description="UTF8 string. Identifies the asset.")
    description: Optional[str] = Field(default=None, description="UTF8 string. Describes the asset.")
    image: Optional[str] = Field(default=None, description="ASCII string. A URI pointing to a image with mime type image.")
    image_data: Optional[str] = Field(default=None, description="Either binary representation of the image for onchain layout or base64 for offchain layout.")


class NFTCollection(BaseModel):
    address: AddressLike = Field(..., title="Address")
    owner_address: Optional[AddressLike] = Field(..., title="Owner Address")
    last_transaction_lt: int = Field(..., title="Last Transaction Lt")
    next_item_index: int = Field(..., title="Next Item Index")
    collection_content: Optional[NFTMetadata] = Field(default=None, title="Collection Content")
    code_hash: str = Field(..., title="Code Hash")
    data_hash: str = Field(..., title="Data Hash")


class NFTItem(BaseModel):
    address: AddressLike = Field(..., title="Address")
    collection_address: Optional[AddressLike] = Field(..., title="Collection Address")
    owner_address: Optional[AddressLike] = Field(..., title="Owner Address")
    init: bool = Field(..., title="Init")
    index: int = Field(..., title="Index")
    last_transaction_lt: int = Field(..., title="Last Transaction Lt")
    code_hash: str = Field(..., title="Code Hash")
    data_hash: str = Field(..., title="Data Hash")
    content: Optional[NFTMetadata] = Field(default=None, title="Content")
    collection: Optional[NFTCollection]


class NFTTransfer(BaseModel):
    query_id: int = Field(..., title="Query Id")
    nft_address: AddressLike = Field(..., title="Nft Address")
    transaction_hash: str = Field(..., title="Transaction Hash")
    transaction_lt: int = Field(..., title="Transaction Lt")
    transaction_now: int = Field(..., title="Transaction Now")
    old_owner: AddressLike = Field(..., title="Old Owner")
    new_owner: AddressLike = Field(..., title="New Owner")
    response_destination: Optional[AddressLike] = Field(..., title="Response Destination")
    custom_payload: Optional[str] = Field(..., title="Custom Payload")
    forward_amount: int = Field(..., title="Forward Amount")
    forward_payload: Optional[str] = Field(..., title="Forward Payload")


class SentMessage(BaseModel):
    message_hash: str = Field(
        ...,
        description="Hash of sent message in hex format",
        examples=["383E348617141E35BC25ED9CD0EDEC2A4EAF6413948BF1FB7F865CEFE8C2CD44"],
        title="Message Hash",
    )


class TextComment(BaseModel):
    type: Literal["text_comment"] = Field(default="text_comment", title="Type")
    comment: str = Field(..., title="Comment")


class ValidationError(BaseModel):
    loc: List[Union[str, int]] = Field(..., title="Location")
    msg: str = Field(..., title="Message")
    type: str = Field(..., title="Error Type")


class WalletInfo(BaseModel):
    balance: int = Field(..., title="Balance")
    wallet_type: Optional[str] = Field(..., title="Wallet Type")
    seqno: Optional[int] = Field(..., title="Seqno")
    wallet_id: Optional[int] = Field(..., title="Wallet Id")
    last_transaction_lt: Optional[int] = Field(..., title="Last Transaction Lt")
    last_transaction_hash: Optional[str] = Field(..., title="Last Transaction Hash")
    status: Literal["uninit", "frozen", "active", "nonexist"] = Field(..., title="Status")


class Account(BaseModel):
    balance: int = Field(..., title="Balance")
    code: Optional[str] = Field(..., title="Code")
    data: Optional[str] = Field(..., title="Data")
    last_transaction_lt: Optional[int] = Field(..., title="Last Transaction Lt")
    last_transaction_hash: Optional[str] = Field(..., title="Last Transaction Hash")
    frozen_hash: Optional[str] = Field(..., title="Frozen Hash")
    status: Literal["uninit", "frozen", "active", "nonexist"] = Field(..., title="Status")


class AccountState(BaseModel):
    hash: str = Field(..., title="Hash")
    account: AddressLike = Field(..., title="Account")
    balance: int = Field(..., title="Balance")
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
    start_lt: int = Field(..., title="Start Lt")
    end_lt: int = Field(..., title="End Lt")
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
    value: Optional[Union[List[GetMethodParameterInput], str, int, bool, AddressLike]] = Field(..., title="Value")

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
    address: AddressLike = Field(..., title="Address")
    method: str = Field(..., title="Method")
    stack: List[Union[GetMethodParameterInput, Dict[str, Any]]] = Field([], title="Stack")


class RunGetMethodResponse(BaseModel):
    gas_used: int = Field(..., title="Gas Used")
    exit_code: int = Field(..., title="Exit Code")
    stack: List[GetMethodParameterOutput] = Field(..., title="Stack")


class Message(BaseModel):
    hash: str = Field(..., title="Hash")
    source: Optional[str] = Field(..., title="Source")
    source_friendly: Optional[AddressLike] = Field(..., title="Source Friendly")
    destination: Optional[str] = Field(..., title="Destination")
    destination_friendly: Optional[AddressLike] = Field(..., title="Destination Friendly")
    value: Optional[int] = Field(..., title="Value")
    fwd_fee: Optional[int] = Field(..., title="Fwd Fee")
    ihr_fee: Optional[int] = Field(..., title="Ihr Fee")
    created_lt: Optional[int] = Field(..., title="Created Lt")
    created_at: Optional[int] = Field(..., title="Created At")
    opcode: Optional[str] = Field(..., title="Opcode")
    ihr_disabled: Optional[bool] = Field(..., title="Ihr Disabled")
    bounce: Optional[bool] = Field(..., title="Bounce")
    bounced: Optional[bool] = Field(..., title="Bounced")
    import_fee: Optional[int] = Field(..., title="Import Fee")
    message_content: Optional[MessageContent]
    init_state: Optional[MessageInitState]


class Transaction(BaseModel):
    account: AddressLike = Field(..., title="Account")
    account_friendly: AddressLike = Field(..., title="Account Friendly")
    hash: str = Field(..., title="Hash")
    lt: int = Field(..., title="Lt")
    now: int = Field(..., title="Now")
    orig_status: Literal["uninit", "frozen", "active", "nonexist"] = Field(..., title="Orig Status")
    end_status: Literal["uninit", "frozen", "active", "nonexist"] = Field(..., title="End Status")
    total_fees: int = Field(..., title="Total Fees")
    account_state_hash_before: str = Field(..., title="Account State Hash Before")
    account_state_hash_after: str = Field(..., title="Account State Hash After")
    prev_trans_hash: str = Field(..., title="Prev Trans Hash")
    prev_trans_lt: int = Field(..., title="Prev Trans Lt")
    description: Any = Field(..., title="Description")
    block_ref: Optional[BlockReference]
    in_msg: Message = Field(..., title="In Msg")
    out_msgs: List[Message] = Field(..., title="Out Msgs")
    account_state_before: Optional[AccountState]
    account_state_after: Optional[AccountState]
    trace_id: Optional[str] = Field(..., title="Trace Id")


class TransactionTrace(BaseModel):
    id: str = Field(..., title="Id")
    transaction: Transaction
    children: List[TransactionTrace] = Field(default=[], title="Children")


GetMethodParameterInput.model_rebuild()
GetMethodParameterOutput.model_rebuild()
TransactionTrace.model_rebuild()
