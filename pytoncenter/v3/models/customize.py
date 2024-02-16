from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field, model_validator

from .types import AddressLike, PyDatetime

__all__ = [
    "GetBlockRequest",
    "GetMasterchainBlockShardsRequest",
    "GetTransactionsRequest",
    "GetTransactionByMasterchainBlockRequest",
    "GetTransactionByMessageRequest",
    "GetAdjacentTransactionsRequest",
    "GetTracesRequest",
    "GetTransactionTraceRequest",
    "GetMessagesRequest",
    "GetNFTCollectionsRequest",
    "GetNFTItemsRequest",
    "GetNFTTransfersRequest",
    "GetJettonMastersRequest",
    "GetJettonWalletsRequest",
    "GetJettonTransfersRequest",
    "GetJettonBurnsRequest",
    "GetTopAccountsByBalanceRequest",
    "GetAccountRequest",
    "GetWalletRequest",
    "GetSpecifiedJettonWalletRequest",
    "GetSpecifiedNFTItemRequest",
    "GetMessageByHashRequest",
    "GetTransactionByHashRequest",
    "GetSourceTransactionRequest",
]


class GetBlockRequest(BaseModel):
    workchain: Optional[int] = Field(default=None, description="Block workchain")
    shard: Optional[str] = Field(default=None, description="Block shard id. Must be sent with workchain")
    seqno: Optional[int] = Field(default=None, description="Block block seqno. Must be sent with workchain and shard")
    start_utime: Optional[PyDatetime] = Field(default=None, description="Query blocks with generation UTC timestamp after given timestamp")
    end_utime: Optional[PyDatetime] = Field(default=None, description="Query blocks with generation UTC timestamp before given timestamp")
    start_lt: Optional[int] = Field(default=None, description="Query blocks with lt >= start_lt")
    end_lt: Optional[int] = Field(default=None, description="Query blocks with lt <= end_lt")
    limit: int = Field(default=128, ge=1, le=256, description="Limit number of queried rows. Use with offset to batch read.")
    offset: int = Field(default=0, ge=0, description="Skip first N rows. Use with limit to batch read.")
    sort: Literal["asc", "desc"] = Field(default="desc", description="Sort results by UTC timestamp")

    @model_validator(mode="after")
    def check_times(cls, values: GetBlockRequest):
        start_utime, end_utime = values.start_utime, values.end_utime
        if start_utime and end_utime and start_utime > end_utime:
            raise ValueError("\033[93mstart_utime must be earlier than end_utime\033[0m")
        return values

    @model_validator(mode="after")
    def checl_lts(cls, values: GetBlockRequest):
        start_lt, end_lt = values.start_lt, values.end_lt
        if start_lt and end_lt and start_lt > end_lt:
            raise ValueError("\033[93mstart_lt must be earlier than end_lt\033[0m")
        return values

    @model_validator(mode="after")
    def check_shard_and_seqno(cls, values: GetBlockRequest):
        shard, workchain, seqno = values.shard, values.workchain, values.seqno
        if shard and not workchain:
            raise ValueError("\033[93mworkchain is required if shard is specified\033[0m")
        if seqno and not (workchain and shard):
            raise ValueError("\033[93mworkchain and shard are required if seqno is specified\033[0m")
        return values


class GetMasterchainBlockShardsRequest(BaseModel):
    seqno: int = Field(description="Masterchain block seqno")
    include_mc_block: bool = Field(False, description="Include masterchain block")


class GetTransactionByHashRequest(BaseModel):
    hash: str = Field(description="Transaction hash. Acceptable in hex, base64 and base64url forms")


class GetTransactionsRequest(BaseModel):
    workchain: Optional[int] = Field(default=None, description="Block workchain")
    shard: Optional[str] = Field(default=None, description="Block shard id. Must be sent with workchain")
    seqno: Optional[int] = Field(default=None, description="Block block seqno. Must be sent with workchain and shard")
    account: Optional[AddressLike] = Field(default=None, description="The account address to get transactions. Can be sent in hex, base64 or base64url form")
    exclude_account: Optional[AddressLike] = Field(default=None, description="Exclude transactions on specified account addresses")
    hash: Optional[str] = Field(default=None, description="Transaction hash. Acceptable in hex, base64 and base64url forms")
    lt: Optional[int] = Field(default=None, description="Transaction logical time")
    start_utime: Optional[PyDatetime] = Field(default=None, description="Query blocks with generation UTC timestamp after given timestamp")
    end_utime: Optional[PyDatetime] = Field(default=None, description="Query blocks with generation UTC timestamp before given timestamp")
    start_lt: Optional[int] = Field(default=None, description="Query blocks with lt >= start_lt")
    end_lt: Optional[int] = Field(default=None, description="Query blocks with lt <= end_lt")
    limit: int = Field(default=128, ge=1, le=256, description="Limit number of queried rows. Use with offset to batch read.")
    offset: int = Field(default=0, ge=0, description="Skip first N rows. Use with limit to batch read.")
    sort: Literal["asc", "desc"] = Field(default="desc", description="Sort results by UTC timestamp")

    @model_validator(mode="after")
    def check_times(cls, values: GetBlockRequest):
        start_utime, end_utime = values.start_utime, values.end_utime
        if start_utime and end_utime and start_utime > end_utime:
            raise ValueError("\033[93start_utime must be earlier than end_utime\033[0m")
        return values

    @model_validator(mode="after")
    def checl_lts(cls, values: GetBlockRequest):
        start_lt, end_lt = values.start_lt, values.end_lt
        if start_lt and end_lt and start_lt > end_lt:
            raise ValueError("\033[93mstart_lt must be earlier than end_lt\033[0m")
        return values

    @model_validator(mode="after")
    def check_shard_and_seqno(cls, values: GetBlockRequest):
        shard, workchain, seqno = values.shard, values.workchain, values.seqno
        if shard and not workchain:
            raise ValueError("\033[93mworkchain is required if shard is specified\033[0m")
        if seqno and not (workchain and shard):
            raise ValueError("\033[93mworkchain and shard are required if seqno is specified\033[0m")
        return values


class GetTransactionByMasterchainBlockRequest(BaseModel):
    seqno: int = Field(description="Masterchain block seqno")
    limit: int = Field(default=128, ge=1, le=256, description="Limit number of queried rows. Use with offset to batch read.")
    offset: int = Field(default=0, ge=0, description="Skip first N rows. Use with limit to batch read.")
    sort: Literal["asc", "desc"] = Field(default="desc", description="Sort results by UTC timestamp")


class GetTransactionByMessageRequest(BaseModel):
    direction: Literal["in", "out"] = Field(description="Message direction")
    msg_hash: str = Field(description="Message hash. Acceptable in hex, base64 and base64url forms")
    limit: int = Field(default=128, ge=1, le=256, description="Limit number of queried rows. Use with offset to batch read.")
    offset: int = Field(default=0, ge=0, description="Skip first N rows. Use with limit to batch read.")


class GetSourceTransactionRequest(BaseModel):
    hash: str = Field(description="Transaction hash. Acceptable in hex, base64 and base64url forms")


class GetAdjacentTransactionsRequest(BaseModel):
    hash: str = Field(description="Transaction hash. Acceptable in hex, base64 and base64url forms")
    direction: Literal["in", "out", "both"] = Field(default="both", description="Message direction")
    limit: int = Field(default=128, ge=1, le=256, description="Limit number of queried rows. Use with offset to batch read.")
    offset: int = Field(default=0, ge=0, description="Skip first N rows. Use with limit to batch read.")
    sort: Literal["asc", "desc", "none"] = Field(default="desc", description="Sort results by UTC timestamp")


class GetTracesRequest(BaseModel):
    tx_hash: List[str] = Field(default=[], description="List of transaction hashes")
    trace_id: List[str] = Field(default=[], description="Trace id")

    @model_validator(mode="after")
    def check_txhash_traceid(cls, values: GetTracesRequest):
        tx_hash, trace_id = values.tx_hash, values.trace_id
        if (not tx_hash and not trace_id) or (tx_hash and trace_id):
            raise ValueError("\033[93mExact one parameter should be used\033[0m")
        return values


class GetTransactionTraceRequest(BaseModel):
    hash: str = Field(description="Transaction hash. Acceptable in hex, base64 and base64url forms")
    sort: Literal["none", "asc", "desc"] = Field(default="asc", description="Sort transactions by lt")


class GetMessageByHashRequest(BaseModel):
    hash: str = Field(description="Message hash. Acceptable in hex, base64 and base64url forms")


class GetMessagesRequest(BaseModel):
    hash: Optional[str] = Field(default=None, description="Message hash. Acceptable in hex, base64 and base64url forms")
    source: Optional[AddressLike] = Field(default=None, description="The source account address. Can be sent in hex, base64 or base64url form")
    destination: Optional[AddressLike] = Field(default=None, description="The destination account address. Can be sent in hex, base64 or base64url form")
    body_hash: Optional[str] = Field(default=None, description="Message body hash. Acceptable in hex, base64 and base64url forms")
    limit: int = Field(default=128, ge=1, le=256, description="Limit number of queried rows. Use with offset to batch read")
    offset: int = Field(default=0, ge=0, description="Skip first N rows. Use with limit to batch read")


class GetNFTCollectionsRequest(BaseModel):
    collection_address: Optional[AddressLike] = Field(default=None, description="NFT collection address. Must be sent in hex, base64 and base64url forms")
    owner_address: Optional[AddressLike] = Field(default=None, description="NFT owner address. Must be sent in hex, base64 and base64url forms")
    limit: int = Field(default=128, ge=1, le=256, description="Limit number of queried rows. Use with offset to batch read")
    offset: int = Field(default=0, ge=0, description="Skip first N rows. Use with limit to batch read")


class GetNFTItemsRequest(BaseModel):
    address: Optional[AddressLike] = Field(default=None, description="NFT address. Must be sent in hex, base64 and base64url forms.")
    owner_address: Optional[AddressLike] = Field(default=None, description="Address of NFT owner. Must be sent in hex, base64 and base64url forms")
    collection_address: Optional[AddressLike] = Field(default=None, description="NFT collection address. Must be sent in hex, base64 and base64url forms")
    limit: int = Field(default=128, ge=1, le=256, description="Limit number of queried rows. Use with offset to batch read")
    offset: int = Field(default=0, ge=0, description="Skip first N rows. Use with limit to batch read")


class GetSpecifiedNFTItemRequest(BaseModel):
    owner_address: AddressLike = Field(..., description="Address of NFT owner. Must be sent in hex, base64 and base64url forms")
    collection_address: AddressLike = Field(..., description="NFT collection address. Must be sent in hex, base64 and base64url forms")


class GetNFTTransfersRequest(BaseModel):
    address: Optional[AddressLike] = Field(default=None, description="Address of NFT owner. Must be sent in hex, base64 and base64url forms")
    item_address: Optional[AddressLike] = Field(default=None, description="NFT item address. Must be sent in hex, base64 and base64url forms")
    collection_address: Optional[AddressLike] = Field(default=None, description="NFT collection address. Must be sent in hex, base64 and base64url forms")
    direction: Literal["in", "out", "both"] = Field(default="both", description="Direction transactions by lt")
    start_utime: Optional[PyDatetime] = Field(default=None, description="Query transactions with generation UTC timestamp after given timestamp")
    end_utime: Optional[PyDatetime] = Field(default=None, description="Query transactions with generation UTC timestamp before given timestamp")
    start_lt: Optional[int] = Field(default=None, description="Query transactions with lt >= start_lt")
    end_lt: Optional[int] = Field(default=None, description="Query transactions with lt <= end_lt")
    limit: int = Field(default=128, ge=1, le=256, description="Limit number of queried rows. Use with offset to batch read")
    offset: int = Field(default=0, ge=0, description="Skip first N rows. Use with limit to batch read")
    sort: Literal["asc", "desc"] = Field(default="desc", description="Sort results by UTC timestamp")

    @model_validator(mode="after")
    def check_times(cls, values: GetNFTTransfersRequest):
        start_utime, end_utime = values.start_utime, values.end_utime
        if start_utime and end_utime and start_utime > end_utime:
            raise ValueError("\033[93mstart_utime must be earlier than end_utime\033[0m")
        return values

    @model_validator(mode="after")
    def checl_lts(cls, values: GetBlockRequest):
        start_lt, end_lt = values.start_lt, values.end_lt
        if start_lt and end_lt and start_lt > end_lt:
            raise ValueError("\033[93mstart_lt must be earlier than end_lt\033[0m")
        return values


class GetJettonMastersRequest(BaseModel):
    address: Optional[AddressLike] = Field(default=None, description="Jetton Master address. Must be sent in hex, base64 and base64url forms")
    admin_address: Optional[AddressLike] = Field(default=None, description="Address of Jetton Master's admin. Must be sent in hex, base64 and base64url forms")
    limit: int = Field(default=128, ge=1, le=256, description="Limit number of queried rows. Use with offset to batch read")
    offset: int = Field(default=0, ge=0, description="Skip first N rows. Use with limit to batch read")


class GetJettonWalletsRequest(BaseModel):
    address: Optional[AddressLike] = Field(default=None, description="Jetton wallet address. Must be sent in hex, base64 and base64url forms")
    owner_address: Optional[AddressLike] = Field(default=None, description="Address of Jetton wallet's owner. Must be sent in hex, base64 and base64url forms")
    jetton_address: Optional[AddressLike] = Field(default=None, description="Jetton Master. Must be sent in hex, base64 and base64url forms")
    limit: int = Field(default=128, ge=1, le=256, description="Limit number of queried rows. Use with offset to batch read")
    offset: int = Field(default=0, ge=0, description="Skip first N rows. Use with limit to batch read")


class GetSpecifiedJettonWalletRequest(BaseModel):
    owner_address: AddressLike = Field(..., description="Address of Jetton wallet's owner. Must be sent in hex, base64 and base64url forms")
    jetton_address: AddressLike = Field(..., description="Jetton Master. Must be sent in hex, base64 and base64url forms")


class JettonFilter(BaseModel):
    address: Optional[AddressLike] = Field(default=None, description="Account address. Must be sent in hex, base64 and base64url forms")
    jetton_wallet: Optional[AddressLike] = Field(default=None, description="Jetton wallet address. Must be sent in hex, base64 and base64url forms")
    jetton_master: Optional[AddressLike] = Field(default=None, description="Jetton master address. Must be sent in hex, base64 and base64url forms")
    direction: Literal["in", "out", "both"] = Field(default="both", description="Direction transactions by lt")
    start_utime: Optional[PyDatetime] = Field(default=None, description="Query transactions with generation UTC timestamp after given timestamp")
    end_utime: Optional[PyDatetime] = Field(default=None, description="Query transactions with generation UTC timestamp before given timestamp")
    start_lt: Optional[int] = Field(default=None, description="Query transactions with lt >= start_lt")
    end_lt: Optional[int] = Field(default=None, description="Query transactions with lt <= end_lt")
    limit: int = Field(default=128, ge=1, le=256, description="Limit number of queried rows. Use with offset to batch read")
    offset: int = Field(default=0, ge=0, description="Skip first N rows. Use with limit to batch read")
    sort: Literal["asc", "desc"] = Field(default="desc", description="Sort results by UTC timestamp")

    @model_validator(mode="after")
    def check_times(cls, values: GetNFTTransfersRequest):
        start_utime, end_utime = values.start_utime, values.end_utime
        if start_utime and end_utime and start_utime > end_utime:
            raise ValueError("\033[93mstart_utime must be earlier than end_utime\033[0m")
        return values

    @model_validator(mode="after")
    def checl_lts(cls, values: GetBlockRequest):
        start_lt, end_lt = values.start_lt, values.end_lt
        if start_lt and end_lt and start_lt > end_lt:
            raise ValueError("\033[93mstart_lt must be earlier than end_lt\033[0m")
        return values


class GetJettonTransfersRequest(JettonFilter): ...


class GetJettonBurnsRequest(JettonFilter): ...


class GetTopAccountsByBalanceRequest(BaseModel):
    limit: int = Field(default=128, ge=1, le=256, description="Limit number of queried rows. Use with offset to batch read")
    offset: int = Field(default=0, ge=0, description="Skip first N rows. Use with limit to batch read")


class GetAccountRequest(BaseModel):
    address: AddressLike = Field(description="Account address. Account address. Can be sent in raw or user-friendly form")


class GetWalletRequest(BaseModel):
    address: AddressLike = Field(description="Account address. Account address. Can be sent in raw or user-friendly form")
