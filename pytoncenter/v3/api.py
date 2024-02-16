import asyncio
import os
import warnings
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Tuple, Union, overload

import aiohttp

from pytoncenter.address import Address
from pytoncenter.exception import TonCenterException, TonCenterValidationException
from pytoncenter.multicall import Multicallable
from pytoncenter.requestor import AsyncRequestor
from pytoncenter.v3.models import *


class AsyncTonCenterClientV3(Multicallable, AsyncRequestor):
    def __init__(
        self,
        network: Union[Literal["mainnet"], Literal["testnet"]],
        *,
        api_key: Optional[str] = None,
        custom_endpoint: Optional[str] = None,
        qps: Optional[float] = None,
        **kwargs,
    ) -> None:
        api_key = os.getenv("TONCENTER_API_KEY", api_key)
        # show warning if api_key is None
        if not api_key:
            warnings.warn(
                "API key is not provided. TonCenter API is rate limited to 1 request per second. Suggesting providing it in environment variable `TONCENTER_API_KEY` or api_key to increase the rate limit.",
                RuntimeWarning,
            )
        assert (network in ["mainnet", "testnet"]) or (custom_endpoint is not None), "Network or custom_endpoint must be provided"
        if custom_endpoint is not None:
            self.base_url = custom_endpoint
        else:
            prefix = "" if network == "mainnet" else "testnet."
            self.base_url = f"https://{prefix}toncenter.com/api/v3"
        self.api_key = api_key

        if qps is not None:
            assert qps > 0, "QPS must be greater than 0"
        else:
            qps = 9.5 if self.api_key else 1
        super().__init__(qps)

    def _get_request_headers(self) -> Dict[str, Any]:
        headers = {
            "Content-Type": "application/json",
            "accept": "application/json",
        }
        if self.api_key:
            headers["X-API-KEY"] = self.api_key
        return headers

    async def _parse_response(self, response: aiohttp.ClientResponse):
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
        return await self._async_get("masterchainInfo")

    async def get_blocks(self, req: Optional[GetBlockRequest] = None) -> List[Block]:
        req = req if req is not None else GetBlockRequest()
        resp = await self._async_get("blocks", req.model_dump(exclude_none=True))
        return [Block(**r) for r in resp]

    async def get_masterchain_block_shards(self, req: GetMasterchainBlockShardsRequest) -> List[Block]:
        resp = await self._async_get("masterchainBlockShards", req.model_dump(exclude_none=True))
        return [Block(**r) for r in resp]

    @overload
    async def get_transactions(self, req: Optional[GetTransactionByHashRequest]) -> Optional[Transaction]: ...

    @overload
    async def get_transactions(self, req: Optional[GetTransactionsRequest]) -> List[Transaction]: ...

    async def get_transactions(self, req: Union[Optional[GetTransactionsRequest], GetTransactionByHashRequest] = None) -> Union[List[Transaction], Optional[Transaction]]:
        req = req or GetTransactionsRequest()
        resp = await self._async_get("transactions", req.model_dump(exclude_none=True))
        if isinstance(req, GetTransactionByHashRequest):
            if len(resp) == 0:
                return None
            assert len(resp) == 1, "The response should contain only one transaction"
            return Transaction(**resp[0])
        return [Transaction(**r) for r in resp]

    async def get_transactions_by_masterchain_block(self, req: GetTransactionByMasterchainBlockRequest) -> List[Transaction]:
        resp = await self._async_get("transactionsByMasterchainBlock", req.model_dump(exclude_none=True))
        return [Transaction(**r) for r in resp]

    async def get_transaction_by_message(self, req: GetTransactionByMessageRequest) -> List[Transaction]:
        resp = await self._async_get("transactionsByMessage", req.model_dump(exclude_none=True))
        return [Transaction(**r) for r in resp]

    @overload
    async def get_adjacent_transactions(self, req: GetAdjacentTransactionsRequest) -> List[Transaction]: ...

    @overload
    async def get_adjacent_transactions(self, req: GetSourceTransactionRequest) -> Optional[Transaction]: ...

    async def get_adjacent_transactions(self, req: Union[GetAdjacentTransactionsRequest, GetSourceTransactionRequest]) -> Union[List[Transaction], Optional[Transaction]]:
        is_single_source = isinstance(req, GetSourceTransactionRequest)
        req = GetAdjacentTransactionsRequest(hash=req.hash, direction="in", limit=1) if is_single_source else req
        try:
            resp = await self._async_get("adjacentTransactions", req.model_dump(exclude_none=True))
            if is_single_source:
                assert len(resp) == 1, "The response should contain one transaction"
                return Transaction(**resp[0])
            else:
                return [Transaction(**r) for r in resp]
        except TonCenterException as e:
            if e.code == 404:
                return None if is_single_source else []
            raise e

    async def get_transaction_trace(self, req: GetTransactionTraceRequest) -> List[TransactionTrace]:
        resp = await self._async_get("traces", req.model_dump(exclude_none=True))
        return [TransactionTrace(**r) for r in resp]

    @overload
    async def get_messages(self, req: GetMessageByHashRequest) -> Optional[Message]: ...

    @overload
    async def get_messages(self, req: Optional[GetMessagesRequest] = None) -> List[Message]: ...

    async def get_messages(self, req: Union[Optional[GetMessagesRequest], GetMessageByHashRequest] = None) -> Union[List[Message], Optional[Message]]:
        req = req if req is not None else GetMessagesRequest()
        resp = await self._async_get("messages", req.model_dump(exclude_none=True))
        if isinstance(req, GetMessageByHashRequest):
            if len(resp) == 0:
                return None
            assert len(resp) == 1, "The response should contain only one message"
            return Message(**resp[0])
        return [Message(**r) for r in resp]

    async def get_nft_collections(self, req: Optional[GetNFTCollectionsRequest] = None) -> List[NFTCollection]:
        req = req if req is not None else GetNFTCollectionsRequest()
        resp = await self._async_get("nft/collections", req.model_dump(exclude_none=True))
        return [NFTCollection(**r) for r in resp]

    @overload
    async def get_nft_items(self, req: Optional[GetNFTItemsRequest] = None) -> List[NFTItem]: ...

    @overload
    async def get_nft_items(self, req: GetSpecifiedNFTItemRequest) -> Optional[NFTItem]: ...

    async def get_nft_items(self, req: Optional[Union[GetNFTItemsRequest, GetSpecifiedNFTItemRequest]] = None) -> Union[List[NFTItem], Optional[NFTItem]]:
        req = req if req is not None else GetNFTItemsRequest()
        resp = await self._async_get("nft/items", req.model_dump(exclude_none=True))
        if isinstance(req, GetSpecifiedNFTItemRequest):
            if len(resp) == 0:
                return None
            assert len(resp) == 1, "The response should contain only one item"
            return NFTItem(**resp[0])
        return [NFTItem(**r) for r in resp]

    async def get_nft_transfers(self, req: Optional[GetNFTTransfersRequest] = None) -> List[NFTTransfer]:
        req = req if req is not None else GetNFTTransfersRequest()
        resp = await self._async_get("nft/transfers", req.model_dump(exclude_none=True))
        return [NFTTransfer(**r) for r in resp]

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
        if is_address:
            if len(resp) == 0:
                return None
            assert len(resp) == 1, "The response should contain only one master"
            return JettonMaster(**resp[0])
        return [JettonMaster(**r) for r in resp]

    @overload
    async def get_jetton_wallets(self, req: Optional[GetJettonWalletsRequest] = None) -> List[JettonWallet]: ...

    @overload
    async def get_jetton_wallets(self, req: GetSpecifiedJettonWalletRequest) -> Optional[JettonWallet]: ...

    async def get_jetton_wallets(self, req: Optional[Union[GetJettonWalletsRequest, GetSpecifiedJettonWalletRequest]] = None) -> Union[List[JettonWallet], Optional[JettonWallet]]:
        req = req if req is not None else GetJettonWalletsRequest()
        resp = await self._async_get("jetton/wallets", req.model_dump(exclude_none=True))
        if isinstance(req, GetSpecifiedJettonWalletRequest):
            if len(resp) == 0:
                return None
            assert len(resp) == 1, "The response should contain only one wallet"
            return JettonWallet(**resp[0])
        return [JettonWallet(**r) for r in resp]

    async def get_jetton_transfers(self, req: Optional[GetJettonTransfersRequest] = None) -> List[JettonTransfer]:
        req = req if req is not None else GetJettonTransfersRequest()
        resp = await self._async_get("jetton/transfers", req.model_dump(exclude_none=True))
        return [JettonTransfer(**r) for r in resp]

    async def get_jetton_burns(self, req: Optional[GetJettonBurnsRequest] = None) -> List[JettonBurn]:
        req = req if req is not None else GetJettonBurnsRequest()
        resp = await self._async_get("jetton/burns", req.model_dump(exclude_none=True))
        return [JettonBurn(**r) for r in resp]

    async def get_top_accounts_by_balance(self, req: Optional[GetTopAccountsByBalanceRequest] = None) -> List[AccountBalance]:
        req = req if req is not None else GetTopAccountsByBalanceRequest()
        resp = await self._async_get("topAccountsByBalance", req.model_dump(exclude_none=True))
        return [AccountBalance(**r) for r in resp]

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

    async def subscribe_tx(self, account: str, start_time: Optional[datetime] = None, interval_in_second: float = 2):
        """
        subscribe_tx subscribes to transactions of a wallet and yields the transactions as they come.

        Parameters
        ----------
        account: str
            The account (address) to subscribe, the account can be any_from of address
        start_time: datetime.datetime
            The start time to crawl data.
        interval_in_second: float
            Interval between every batch of requests, in second.
        """
        warnings.warn("\033[93mThe `subscribe_tx` function is currently under development; please use it with caution.\033[0m", UserWarning)
        cur_time = start_time

        while True:
            req = GetTransactionsRequest(account=account, start_utime=cur_time, sort="asc", limit=20)
            txs = await self.get_transactions(req)
            if len(txs) > 0:
                for tx in txs:
                    yield tx
                cur_time = txs[-1].now + 1
            await asyncio.sleep(interval_in_second)

    async def get_trace_alternative(self, req: GetTransactionTraceRequest) -> TransactionTrace:
        """
        get_trace_alternatives takes a transaction hash as input and returns the transaction trace.

        # Note
        This is an alternative method to get the transaction trace. It is not recommended to use this method unless the
        original method does not work. It is compatible with the original method, but it may not be as efficient as it.
        """

        # Trace source of the transaction
        async def _trace_source(orig_tx: Transaction) -> Tuple[Transaction, Dict[str, Transaction]]:
            """
            Find the source of the transaction, and return all the transaction that we found.

            Returns
            -------
            Tuple[Transaction, Dict[str, Transaction]]
                The first element is the source transaction, and the second element is a dictionary of all the transactions
                that we found.
            """
            current_tx = orig_tx
            visited: Dict[str, Transaction] = {}
            while current_tx.in_msg.source is not None:
                visited[current_tx.in_msg.hash] = current_tx
                candidates = await self.get_transaction_by_message(GetTransactionByMessageRequest(direction="out", msg_hash=current_tx.in_msg.hash))
                assert len(candidates) == 1, f"Expecting to find one transaction by message hash {current_tx.in_msg.hash}, but found {len(candidates)}"
                current_tx = candidates[0]
                if current_tx.in_msg.source is None:
                    break
            return current_tx, visited

        async def _dfs_trace(root: Transaction, visited: Dict[str, Transaction], trace_id: str) -> List[TransactionTrace]:
            children = []
            for out_msg in root.out_msgs:
                exist = visited.get(out_msg.hash, None)
                if exist is None:
                    adj_txs = await self.get_transaction_by_message(GetTransactionByMessageRequest(msg_hash=out_msg.hash, direction="in"))
                    assert len(adj_txs) == 1, f"Expecting to find one transaction by message hash {out_msg.hash}, but found {len(adj_txs)}"
                    results = await _dfs_trace(adj_txs[0], visited, trace_id)
                    child = TransactionTrace(id=trace_id, transaction=adj_txs[0], children=results)
                    children.append(child)
                else:
                    results = await _dfs_trace(exist, visited, trace_id)
                    child = TransactionTrace(id=trace_id, transaction=exist, children=results)
                    children.append(child)
            return children

        orig_tx = await self.get_transactions(GetTransactionByHashRequest(hash=req.hash))
        assert orig_tx is not None, f"The original transaction {req.hash} does not exist"
        source_tx, visited = await _trace_source(orig_tx=orig_tx)
        children = await _dfs_trace(source_tx, visited, source_tx.hash)
        return TransactionTrace(id=source_tx.hash, transaction=source_tx, children=children)
