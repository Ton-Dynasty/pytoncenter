from typing import List, Literal, TypedDict, Union, Dict, Any

AccountAddress = TypedDict("AccountAddress", {"@type": Literal["accountAddress"], "account_address": str})
AccountState = TypedDict("AccountState", {"@type": Literal["raw.accountState"], "code": str, "data": str, "frozen_hash": str})
BlockID = TypedDict("BlockID", {"@type": Literal["ton.blockIdExt"], "workchain": int, "shard": str, "seqno": int, "root_hash": str, "file_hash": str})
TransactionID = TypedDict("TransactionID", {"@type": Literal["'internal.transactionId'"], "lt": int, "hash": str})
WalletInformation = TypedDict("WalletInformation", {"wallet": bool, "balance": int, "account_state": str, "last_transaction_id": TransactionID})
AddressInformation = TypedDict(
    "AddressInformation",
    {
        "@type": Literal["raw.fullAccountState"],
        "balance": int,
        "code": str,
        "data": str,
        "last_transaction_id": TransactionID,
        "block_id": BlockID,
        "frozen_hash": str,
        "sync_utime": int,
        "@extra": str,
        "state": str,
    },
)
ExtentedAddressInformation = TypedDict(
    "ExtentedAddressInformation",
    {
        "@type": Literal["fullAccountState"],
        "address": AccountAddress,
        "balance": str,
        "last_transaction_id": TransactionID,
        "block_id": BlockID,
        "sync_utime": int,
        "account_state": AccountState,
        "revision": int,
        "@extra": str,
    },
)
MsgRawDataWithBody = TypedDict("MsgRawDataWithBody", {"@type": Literal["msg.dataRaw"], "body": str, "init_state": str})
MsgRawDataWithComment = TypedDict("MsgRawDataWithComment", {"@type": Literal["msg.dataText"], "text": str})
Message = TypedDict(
    "Message",
    {
        "@type": Literal["raw.message"],
        "source": str,
        "destination": str,
        "value": str,
        "foward_fee": str,
        "ihr_fee": str,
        "created_lt": str,
        "body_hash": str,
        "msg_data": Union[MsgRawDataWithBody, MsgRawDataWithComment],
        "messsage": str,
        "init_state": str,
    },
)
Tx = TypedDict(
    "Tx",
    {
        "@type": Literal["raw.transaction"],
        "address": AccountAddress,
        "utime": int,
        "data": str,
        "transaction_id": TransactionID,
        "fee": str,
        "storage_fee": str,
        "other_fee": str,
        "in_msg": Message,
        "out_msgs": List[Message],
    },
)
MasterChainInfo = TypedDict("MasterChainInfo", {"last": BlockID, "state_root_hash": str, "init": BlockID, "@extra": str})
ConsensusBlock = TypedDict("ConsensusBlock", {"consensus_block": int, "timestamp": float})
Signature = TypedDict("Signature", {"@type": Literal["blocks.signature"], "node_id_short": str, "signature": str})
BlockSignatures = TypedDict("BlockSignatures", {"@type": Literal["blocks.blockSignatures"], "id": BlockID, "signatures": List[Signature], "@extra": str})
Shards = TypedDict("Shards", {"@type": Literal["blocks.shard"], "shards": List[BlockID], "@extra": str})
BlockTxs = TypedDict("BlockTxs", {"@extra": str, "@type": Literal["blocks.transactions"], "id": BlockID, "incomplete": bool, "req_count": int, "transactions": List[Tx]})
JettonContentPayload = TypedDict("JettonContentPayload", {"image": str, "name": str, "symbol": str, "decimals": int, "description": str})
JettonContent = TypedDict("JettonContent", {"type": str, "data": JettonContentPayload})
JettonMasterData = TypedDict(
    "JettonMasterData", {"total_supply": int, "mintable": bool, "admin_address": str, "jetton_content": JettonContent, "jetton_wallet_code": str, "contract_type": Literal["jetton_master"]}
)
JettonWalletData = TypedDict("JettonWalletData", {"balance": int, "owner": str, "jetton": str, "jetton_wallet_code": str, "contract_type": Literal["jetton_wallet"]})
NFTCollectionContent = TypedDict("NFTCollectionContent", {"type": str, "data": str})
NFTCollectionData = TypedDict("NFTCollectionData", {"next_item_index": int, "owner_address": str, "contract_type": Literal["nft_collection"], "collection_content": NFTCollectionContent})
NFTItemData = TypedDict("NFTItemData", {"init": bool, "index": int, "owner_address": str, "collection_address": str, "contract_type": Literal["nft_item"], "content": NFTCollectionContent})
BounceableAddress = TypedDict("BounceableAddress", {"b64": str, "b64url": str})
DetectAddressResult = TypedDict("DetectAddressResult", {"raw_form": str, "bounceable": BounceableAddress, "non_bounceable": BounceableAddress, "given_type": str, "test_only": bool})
Fees = TypedDict("Fees", {"@type": Literal["fees"], "in_fws_fee": str, "storage_fee": str, "gas_fee": str, "fwd_fee": str})
EstimateResult = TypedDict("EstimateResult", {"@type": Literal["query.fees"], "source_fees": Fees, "destination_fees": List[Fees], "@extra": str})
TraceTx = TypedDict(
    "TraceTx",
    {
        "@type": Literal["raw.transaction"],
        "address": AccountAddress,
        "utime": int,
        "data": str,
        "transaction_id": TransactionID,
        "fee": str,
        "storage_fee": str,
        "other_fee": str,
        "in_msg": Message,
        "children": List["TraceTx"],
    },
)
GetMethodResult = List[Dict[Literal["type", "value"], Union[str, Dict[str, Any]]]]
