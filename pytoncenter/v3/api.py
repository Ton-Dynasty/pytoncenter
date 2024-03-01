import asyncio
import hashlib
import os
import time
import warnings
from typing import Any, Dict, List, Literal, Optional, Tuple, Union, overload

import aiohttp
from tonpy import CellSlice, begin_cell

from pytoncenter.address import Address
from pytoncenter.dispatcher import RoundRobinKeyRotator
from pytoncenter.exception import TonCenterException, TonCenterValidationException
from pytoncenter.multicall import Multicallable
from pytoncenter.requestor import AsyncRequestor
from pytoncenter.v3.models import *


class AsyncTonCenterClientV3(Multicallable, AsyncRequestor):
    def __init__(
        self,
        network: Union[Literal["mainnet"], Literal["testnet"]],
        *,
        api_key: Union[None, str, List[str]] = None,
        strategy: Union[Literal["round_robin"], None] = None,
        custom_endpoint: Optional[str] = None,
        qps: Optional[float] = None,
        **kwargs,
    ) -> None:
        """
        Parameters
        ----------
        network : Union[Literal["mainnet"], Literal["testnet"]]
            The network to use. Only mainnet and testnet are supported.

        api_key : Optional[str], optional
            The API key to use, by default None. If api_key is an empty string, then it will override the environment variable `TONCENTER_API_KEY`.
            - If api key is None, it will use the environment variable `TONCENTER_API_KEY`. You can provide in a comma separated string to use multiple keys.
            - If api key is an empty string, it will not use any API key
            - If api key is a string, it will use the provided API key
            - If api key is a list of strings, it will use the round robin strategy to rotate the keys
        strategy : Union[Literal["round_robin"], None], optional
            The strategy to use for rotating the API keys. if len(api_key) > 1. round_robin will be used by default.
        custom_endpoint : Optional[str], optional
            The custom endpoint to use. If provided, it will override the network parameter.
        qps: Optional[float], optional
            The maximum queries per second to use. If not provided, it will use 9.5 * len(api keys) if api_key is provided, otherwise 1.
        """
        self._network = network
        # API KEY
        self.api_keys = None
        if isinstance(api_key, str):
            if api_key != "":
                self.api_keys = api_key.split(",")
        elif isinstance(api_key, list) and len(api_key) > 0:
            self.api_keys = api_key
        else:
            _api_key = os.getenv("TONCENTER_API_KEY", None)
            if _api_key is not None:
                self.api_keys = _api_key.split(",")
        # show warning if api_key is None
        if not self.api_keys:
            warnings.warn(
                "API key is not provided. TonCenter API is rate limited to 1 request per second. Suggesting providing it in environment variable `TONCENTER_API_KEY` or api_key to increase the rate limit.",
                RuntimeWarning,
            )

        # Key rotation
        self.rotator = None
        if strategy is None:
            if self.api_keys is not None and len(self.api_keys) > 1:
                self.rotator = RoundRobinKeyRotator(keys=self.api_keys)
        elif strategy == "round_robin":
            self.rotator = RoundRobinKeyRotator(keys=self.api_keys)  # type: ignore
        else:
            raise ValueError(f"Strategy {strategy} is not supported")

        # Network and custom endpoint
        assert (network in ["mainnet", "testnet"]) or (custom_endpoint is not None), "Network or custom_endpoint must be provided"
        if custom_endpoint is not None:
            self.base_url = custom_endpoint
        else:
            prefix = "" if network == "mainnet" else "testnet."
            self.base_url = f"https://{prefix}toncenter.com/api/v3"

        # QPS
        if qps is not None:
            assert qps > 0, "QPS must be greater than 0"
        else:
            qps = 9.5 * len(self.api_keys) if self.api_keys else 1
        super().__init__(qps)

    def _get_request_headers(self) -> Dict[str, Any]:
        headers = {
            "Content-Type": "application/json",
            "accept": "application/json",
        }
        _api_key = None
        if self.rotator is not None:
            _api_key = self.rotator.get_key()
        else:
            if self.api_keys is not None:
                _api_key = self.api_keys[0]
        if _api_key:
            headers["X-API-KEY"] = _api_key
        return headers

    async def _parse_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """
        _parse_response parses the response from TonCenter API and returns the result if the request was successful.
        If the request was unsuccessful, a TonException is raised.

        Parameters
        ----------
        response : requests.Response
            The response from TonCenter API

        Returns
        -------
        Any
            The result of the request

        Raises
        ------
        aiohttp.client_exceptions.ClientResponseError:
            If the request was unsuccessful, a ClientResponseError is raised.
        TonException
            If the request was successful, but the TonCenter API returned an error, a TonException is raised.
        """

        result = await response.json()
        if not response.ok:
            if response.status == 422:
                raise TonCenterValidationException(response.status, HTTPValidationError(detail=result.get("detail")))
            else:
                raise TonCenterException(response.status, result.get("error"))
        return result

    async def _async_get(self, handler: str, query: Optional[Dict[str, Any]] = None):
        url = f"{self.base_url}/{handler}"
        params = {k: v for k, v in query.items() if v is not None} if query is not None else None
        return await self._underlying_call("GET", url, params=params)

    async def _async_post(self, handler: str, payload: Dict[str, Any]):
        url = f"{self.base_url}/{handler}"
        payload = {k: v for k, v in payload.items() if v is not None}
        return await self._underlying_call("POST", url, payload=payload)

    async def get_masterchain_info(self) -> MasterchainInfo:
        resp = await self._async_get("masterchainInfo")
        return MasterchainInfo(**resp)

    async def get_blocks(self, req: Optional[GetBlockRequest] = None) -> List[Block]:
        req = req if req is not None else GetBlockRequest()
        resp = await self._async_get("blocks", req.model_dump(exclude_none=True))
        blk_list = BlockList(**resp)
        return blk_list.blocks

    async def get_masterchain_block_shards(self, req: GetMasterchainBlockShardsRequest) -> List[Block]:
        resp = await self._async_get("masterchainBlockShards", req.model_dump(exclude_none=True))
        blk_list = BlockList(**resp)
        return blk_list.blocks

    async def get_masterchain_block_shard_state(self, req: GetMasterchainBlockShardStateRequest) -> List[Block]:
        resp = await self._async_get("masterchainBlockShardState", req.model_dump(exclude_none=True))
        b = BlockList(**resp)
        return b.blocks

    async def get_address_book(self, req: GetAddressBookRequest) -> Dict[str, AddressBookEntry]:
        """
        get_address_book returns the mapping for original address to user friendly format
        """
        resp = await self._async_get("addressBook", req.model_dump(exclude_none=True))
        addr_book = AddressBook(data=resp)
        return addr_book.data

    @overload
    async def get_transactions(self, req: Optional[GetTransactionByHashRequest]) -> Union[Tuple[None, None], Tuple[Transaction, Dict[str, AddressBookEntry]]]: ...

    @overload
    async def get_transactions(self, req: Optional[GetTransactionsRequest]) -> Tuple[List[Transaction], Dict[str, AddressBookEntry]]: ...

    async def get_transactions(
        self, req: Union[Optional[GetTransactionsRequest], GetTransactionByHashRequest] = None
    ) -> Union[Tuple[None, None], Tuple[Transaction, Dict[str, AddressBookEntry]], Tuple[List[Transaction], Dict[str, AddressBookEntry]]]:
        req = req or GetTransactionsRequest()
        resp = await self._async_get("transactions", req.model_dump(exclude_none=True))
        tx_list = TransactionList(**resp)
        if isinstance(req, GetTransactionByHashRequest):
            if len(tx_list.transactions) == 0:
                return None, None
            assert len(tx_list.transactions) == 1, "The response should contain only one transaction"
            return tx_list.transactions[0], tx_list.address_book
        return tx_list.transactions, tx_list.address_book

    async def get_transactions_by_masterchain_block(self, req: GetTransactionByMasterchainBlockRequest) -> Tuple[List[Transaction], Dict[str, AddressBookEntry]]:
        resp = await self._async_get("transactionsByMasterchainBlock", req.model_dump(exclude_none=True))
        tx_list = TransactionList(**resp)
        return tx_list.transactions, tx_list.address_book

    async def get_transaction_by_message(self, req: GetTransactionByMessageRequest) -> Tuple[List[Transaction], Dict[str, AddressBookEntry]]:
        resp = await self._async_get("transactionsByMessage", req.model_dump(exclude_none=True))
        tx_list = TransactionList(**resp)
        return tx_list.transactions, tx_list.address_book

    async def get_adjacent_transactions(self, req: GetAdjacentTransactionsRequest) -> Tuple[List[Transaction], Dict[str, AddressBookEntry]]:
        try:
            if req.full is False:
                resp = await self._async_get("adjacentTransactions", req.model_dump(exclude_none=True))
                tx_list = TransactionList(**resp)
                return tx_list.transactions, tx_list.address_book
            else:
                address_book = dict()
                transactions = []
                while True:
                    resp = await self._async_get("adjacentTransactions", req.model_dump(exclude_none=True))
                    txs = TransactionList(**resp)
                    transactions.extend(txs.transactions)
                    address_book.update(txs.address_book)
                    if len(txs.transactions) < req.limit:
                        break
                    req.offset += req.limit
                return transactions, address_book
        except TonCenterException as e:
            if e.code == 404:
                return [], {}
            raise e

    @overload
    async def get_messages(self, req: GetMessageByHashRequest) -> Optional[Message]: ...

    @overload
    async def get_messages(self, req: Optional[GetMessagesRequest] = None) -> List[Message]: ...

    async def get_messages(self, req: Union[Optional[GetMessagesRequest], GetMessageByHashRequest] = None) -> Union[List[Message], Optional[Message]]:
        req = req if req is not None else GetMessagesRequest()
        resp = await self._async_get("messages", req.model_dump(exclude_none=True))
        msg_list = MessageList(**resp)
        if isinstance(req, GetMessageByHashRequest):
            if len(msg_list.messages) == 0:
                return None
            assert len(msg_list.messages) == 1, "The response should contain only one message"
            return msg_list.messages[0]
        return msg_list.messages

    async def get_nft_collections(self, req: Optional[GetNFTCollectionsRequest] = None) -> List[NFTCollection]:
        req = req if req is not None else GetNFTCollectionsRequest()
        resp = await self._async_get("nft/collections", req.model_dump(exclude_none=True))
        collections = NFTCollectionList(**resp)
        return collections.nft_collections

    @overload
    async def get_nft_items(self, req: Optional[GetNFTItemsRequest] = None) -> List[NFTItem]: ...

    @overload
    async def get_nft_items(self, req: GetSpecifiedNFTItemRequest) -> Optional[NFTItem]: ...

    async def get_nft_items(self, req: Optional[Union[GetNFTItemsRequest, GetSpecifiedNFTItemRequest]] = None) -> Union[List[NFTItem], Optional[NFTItem]]:
        req = req if req is not None else GetNFTItemsRequest()
        resp = await self._async_get("nft/items", req.model_dump(exclude_none=True))
        items = NFTItemList(**resp)
        if isinstance(req, GetSpecifiedNFTItemRequest):
            if len(items.nft_items) == 0:
                return None
            assert len(items.nft_items) == 1, "The response should contain only one item"
            return items.nft_items[0]
        return items.nft_items

    async def get_nft_transfers(self, req: Optional[GetNFTTransfersRequest] = None) -> List[NFTTransfer]:
        req = req if req is not None else GetNFTTransfersRequest()
        resp = await self._async_get("nft/transfers", req.model_dump(exclude_none=True))
        transfers = NFTTransferList(**resp)
        return transfers.nft_transfers

    @overload
    async def get_jetton_masters(self, req: Optional[GetJettonMastersRequest] = None) -> List[JettonMaster]:
        """
        get_jetton_masters returns the jetton masters.
        """

    @overload
    async def get_jetton_masters(self, req: AddressLike) -> Optional[JettonMaster]:
        """
        get_jetton_masters returns the specified jetton master with its address as the parameter
        """

    async def get_jetton_masters(self, req: Union[Optional[GetJettonMastersRequest], AddressLike] = None) -> Union[List[JettonMaster], Optional[JettonMaster]]:
        req = req if req is not None else GetJettonMastersRequest()
        is_address = isinstance(req, (str, Address))
        if is_address:
            req = GetJettonMastersRequest(address=req)
        resp = await self._async_get("jetton/masters", req.model_dump(exclude_none=True))
        masters = JettonMasterList(**resp)
        if is_address:
            if len(masters.jetton_masters) == 0:
                return None
            assert len(masters.jetton_masters) == 1, "The response should contain only one master"
            return masters.jetton_masters[0]
        return masters.jetton_masters

    @overload
    async def get_jetton_wallets(self, req: Optional[GetJettonWalletsRequest] = None) -> List[JettonWallet]: ...

    @overload
    async def get_jetton_wallets(self, req: GetSpecifiedJettonWalletRequest) -> Optional[JettonWallet]: ...

    async def get_jetton_wallets(self, req: Optional[Union[GetJettonWalletsRequest, GetSpecifiedJettonWalletRequest]] = None) -> Union[List[JettonWallet], Optional[JettonWallet]]:
        req = req if req is not None else GetJettonWalletsRequest()
        resp = await self._async_get("jetton/wallets", req.model_dump(exclude_none=True))
        wallets = JettonWalletList(**resp)
        if isinstance(req, GetSpecifiedJettonWalletRequest):
            if len(wallets.jetton_wallets) == 0:
                return None
            assert len(wallets.jetton_wallets) == 1, "The response should contain only one wallet"
            return wallets.jetton_wallets[0]
        return wallets.jetton_wallets

    async def get_jetton_transfers(self, req: Optional[GetJettonTransfersRequest] = None) -> List[JettonTransfer]:
        req = req if req is not None else GetJettonTransfersRequest()
        resp = await self._async_get("jetton/transfers", req.model_dump(exclude_none=True))
        txfer = JettonTransferList(**resp)
        return txfer.jetton_transfers

    async def get_jetton_burns(self, req: Optional[GetJettonBurnsRequest] = None) -> List[JettonBurn]:
        req = req if req is not None else GetJettonBurnsRequest()
        resp = await self._async_get("jetton/burns", req.model_dump(exclude_none=True))
        burns = JettonBurnList(**resp)
        return burns.jetton_burns

    async def get_account(self, req: GetAccountRequest) -> Account:
        resp = await self._async_get("account", req.model_dump(exclude_none=True))
        return Account(**resp)

    async def get_wallet(self, req: GetWalletRequest) -> WalletInfo:
        resp = await self._async_get("wallet", req.model_dump(exclude_none=True))
        return WalletInfo(**resp)

    async def send_message(self, req: ExternalMessage) -> SentMessage:
        resp = await self._async_post("message", req.model_dump(exclude_none=True))
        return SentMessage(**resp)

    async def run_get_method(self, req: RunGetMethodRequest) -> RunGetMethodResponse:
        resp = await self._async_post("runGetMethod", req.model_dump(exclude_none=True))
        return RunGetMethodResponse(**resp)

    async def estimate_fee(self, req: EstimateFeeRequest) -> EstimateFeeResponse:
        resp = await self._async_post("estimateFee", req.model_dump(exclude_none=True))
        return EstimateFeeResponse(**resp)

    async def get_dns_record(self, req: GetDNSRecordRequest) -> DNSRecord:
        """
        get_dns_record returns the DNS record for the given domain name and category.
        Only mainnet is supported.
        Only the wallet category is supported at the moment.
        """
        assert self._network == "mainnet", "Only mainnet is supported"
        dns_name = req.dns_name.replace(".", "\0")
        dns_slice = begin_cell().store_string(dns_name).end_cell().to_boc()
        category_hash = 0
        if req.category is not None:
            category_hash = int(hashlib.sha256(req.category.encode()).hexdigest(), 16)
        resp = await self.run_get_method(
            RunGetMethodRequest(
                address="EQC3dNlesgVD8YbAazcauIrXBPfiVhMMr5YYk2in0Mtsz0Bz",
                method="dnsresolve",
                stack=[
                    GetMethodParameterInput(type="slice", value=dns_slice),
                    GetMethodParameterInput(type="num", value=category_hash),
                ],
            )
        )
        # We cannot import decoder here because it will cause circular import
        # Thus we need to handle the decoding here
        # It might be dirty, will find a better way to handle this
        assert len(resp.stack) == 2, "Expecting to find two items in the stack"
        assert resp.stack[0].type == "num", "Expecting the first item to be a number"
        assert resp.stack[1].type == "cell", "Expecting the second item to be a cell"
        subdomain_bits = int(resp.stack[0].value, 16)  # type: ignore
        cs = CellSlice(resp.stack[1].value)  # type: ignore
        if req.category == "wallet":
            _ = cs.load_uint(16)  # opcode
            try:
                address = cs.load_address()
            except:
                address = None
            return DNSRecord(
                subdomain_bits=subdomain_bits,
                address=address,
            )
        raise NotImplementedError(f"Decoding {req.category} category is not implemented yet")

    async def wait_message_exists(self, req: WaitMessageExistsRequest):
        """
        wait_message_exists wait until the whole transaction trace is complete and yields the transaction.
        This is useful after the external message is sent, and we want to use the message hash to get the transaction trace.
        """
        retry = req.max_retry
        while retry is None or retry > 0:
            retry = retry - 1 if retry is not None else None
            _timer_start = time.monotonic()
            try:
                msgs, _ = await self.get_transaction_by_message(
                    GetTransactionByMessageRequest(
                        direction="in",
                        msg_hash=req.msg_hash,
                        limit=1,
                    )
                )
            except TonCenterException as e:
                if e.code == 503:
                    msgs = []
                else:
                    raise e
            _timer_end = time.monotonic()
            elapse = _timer_end - _timer_start
            sleep_time = max(0, req.interval - elapse)
            if len(msgs) == 0:
                await asyncio.sleep(sleep_time)
                continue
            assert len(msgs) == 1, f"Expecting to find one transaction by message hash {req.msg_hash}, but found {len(msgs)}"
            yield msgs[0]
            return
        raise TonCenterException(429, "Reached the maximum retry limit")

    async def subscribe_tx(self, req: SubscribeTransactionRequest):
        """
        subscribe_tx subscribes to transactions of a wallet and yields the transactions as they come.
        """
        warnings.warn("\033[93mThe `subscribe_tx` function is currently under development; please use it with caution.\033[0m", UserWarning)

        while True:
            _timer_start = time.monotonic()
            txs, _ = await self.get_transactions(
                GetTransactionsRequest(
                    account=req.account,
                    start_utime=req.start_time,
                    sort="asc",
                    limit=req.limit,
                    offset=req.offset,
                )
            )
            req.offset += len(txs)
            if len(txs) > 0:
                for tx in txs:
                    yield tx
            _timer_end = time.monotonic()
            elapse = _timer_end - _timer_start
            sleep_time = max(0, req.interval - elapse)
            await asyncio.sleep(sleep_time)

    async def get_trace_alternative(self, req: GetTransactionTraceRequest) -> TransactionTrace:
        """
        get_trace_alternatives takes a transaction hash as input and returns the transaction trace.

        # Note
        This is an alternative method to get the transaction trace. It is not recommended to use this method in production unless the
        original method does not work. It is compatible with the original method, but it may not be as efficient as it.
        """

        # Trace source of the transaction
        async def _trace_source(orig_tx: Transaction) -> Transaction:
            """
            Find the source of the transaction, and return all the transaction that we found.
            External message are always the source of the transaction.

            Returns
            -------
            Transaction
                The source transaction
            """
            current_tx = orig_tx
            while current_tx.in_msg.source is not None:
                candidates, _ = await self.get_adjacent_transactions(
                    GetAdjacentTransactionsRequest(
                        hash=current_tx.hash,
                        direction="in",
                        limit=1,
                    )
                )
                assert len(candidates) == 1, f"Expecting to find one transaction by message hash {current_tx.in_msg.hash}, but found {len(candidates)}"
                prev_tx = candidates[0]
                current_tx = prev_tx
            return current_tx

        async def _dfs_trace(root: Transaction, trace_id: str) -> List[TransactionTrace]:
            next_txs, _ = await self.get_adjacent_transactions(GetAdjacentTransactionsRequest(hash=root.hash, direction="out", limit=256, sort=req.sort, full=True))
            results = await self.multicall([_dfs_trace(tx, trace_id) for tx in next_txs])
            return [TransactionTrace(id=tx.hash, transaction=tx, children=results[i]) for i, tx in enumerate(next_txs)]

        orig_tx, _ = await self.get_transactions(GetTransactionByHashRequest(hash=req.hash))
        assert orig_tx is not None, f"The original transaction {req.hash} does not exist"
        source_tx = await _trace_source(orig_tx=orig_tx)
        children = await _dfs_trace(source_tx, source_tx.hash)
        return TransactionTrace(id=source_tx.hash, transaction=source_tx, children=children)
