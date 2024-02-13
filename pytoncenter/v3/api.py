import asyncio
import os
import warnings
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, OrderedDict, Tuple, Union

import aiohttp

from pytoncenter.exception import TonCenterNotWalletException
from pytoncenter.multicall import Multicallable
from pytoncenter.v3.models import *


class AsyncTonCenterClientV3(Multicallable):
    def __init__(self, network: Union[Literal["mainnet"], Literal["testnet"]], *, custom_api_key: Optional[str] = None, custom_base_url: Optional[str] = None) -> None:
        api_key = os.getenv("TONCENTER_API_KEY", custom_api_key)
        # show warning if api_key is None
        if not api_key:
            warnings.warn(
                "API key is not provided. TonCenter API is rate limited to 1 request per second. Suggesting providing it in environment variable `TONCENTER_API_KEY` or custom_api_key to increase the rate limit.",
                RuntimeWarning,
            )
        assert (network in ["mainnet", "testnet"]) or (custom_base_url is not None), "Network or custom_base_url must be provided"
        if custom_base_url is not None:
            self.base_url = custom_base_url
        else:
            prefix = "" if network == "mainnet" else "testnet."
            self.base_url = f"https://{prefix}toncenter.com/api/v3"
        self.api_key = api_key

    def _get_request_headers(self) -> Dict[str, Any]:
        headers = {
            "Content-Type": "application/json",
            "accept": "application/json",
        }
        if self.api_key:
            headers["X-API-KEY"] = self.api_key
        return headers

    def _serialize(self, params: OrderedDict[str, str]) -> List[Tuple[str, Any]]:
        return [(k, v) for k, v in params.items()]

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
            if response.status == 409:
                raise TonCenterNotWalletException(409, result.get("error"))
            response.raise_for_status()
        return result

    async def _async_get(self, handler: str, query: Optional[Dict[str, Any]] = None):
        url = f"{self.base_url}/{handler}"
        async with aiohttp.ClientSession() as session:
            params = {k: v for k, v in query.items() if v is not None} if query is not None else None
            async with session.get(url=url, headers=self._get_request_headers(), params=params) as response:
                return await self._parse_response(response)

    async def _async_post(self, handler: str, payload: Dict[str, Any]):
        url = f"{self.base_url}/{handler}"
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, headers=self._get_request_headers(), json={k: v for k, v in payload.items() if v is not None}) as response:
                return await self._parse_response(response)

    async def get_masterchain_info(self) -> MasterchainInfo:
        return await self._async_get("masterchainInfo")

    async def get_blocks(self, req: GetBlockRequest) -> List[Block]:
        resp = await self._async_get("blocks", req.model_dump(exclude_none=True))
        return [Block(**r) for r in resp]

    async def get_masterchain_block_shards(self, req: GetMasterchainBlockShardsRequest) -> List[Block]:
        resp = await self._async_get("masterchainBlockShards", req.model_dump(exclude_none=True))
        return [Block(**r) for r in resp]

    async def get_transactions(self, req: GetTransactionRequest) -> List[Transaction]:
        resp = await self._async_get("transactions", req.model_dump(exclude_none=True))
        return [Transaction(**r) for r in resp]

    async def get_transactions_by_masterchain_block(self, req: GetTransactionByMasterchainBlockRequest) -> List[Transaction]:
        resp = await self._async_get("transactionsByMasterchainBlock", req.model_dump(exclude_none=True))
        return [Transaction(**r) for r in resp]

    async def get_transaction_by_message(self, req: GetTransactionByMessageRequest) -> List[Transaction]:
        resp = await self._async_get("transactionsByMessage", req.model_dump(exclude_none=True))
        return [Transaction(**r) for r in resp]

    async def get_adjacent_transactions(self, req: GetAdjacentTransactionsRequest) -> List[Transaction]:
        resp = await self._async_get("adjacentTransactions", req.model_dump(exclude_none=True))
        return [Transaction(**r) for r in resp]

    async def get_transaction_trace(self, req: GetTransactionTraceRequest) -> List[TransactionTrace]:
        resp = await self._async_get("traces", req.model_dump(exclude_none=True))
        return [TransactionTrace(**r) for r in resp]

    async def get_messages(self, req: GetMessagesRequest) -> List[Message]:
        resp = await self._async_get("messages", req.model_dump(exclude_none=True))
        return [Message(**r) for r in resp]

    async def get_nft_collections(self, req: GetNFTCollectionsRequest) -> List[NFTCollection]:
        resp = await self._async_get("nft/collections", req.model_dump(exclude_none=True))
        return [NFTCollection(**r) for r in resp]

    async def get_nft_items(self, req: GetNFTItemsRequest) -> List[NFTItem]:
        resp = await self._async_get("nft/items", req.model_dump(exclude_none=True))
        return [NFTItem(**r) for r in resp]

    async def get_nft_transfers(self, req: GetNFTTransfersRequest) -> List[NFTTransfer]:
        resp = await self._async_get("nft/transfers", req.model_dump(exclude_none=True))
        return [NFTTransfer(**r) for r in resp]

    async def get_jetton_masters(self, req: GetJettonMastersRequest) -> List[JettonMaster]:
        resp = await self._async_get("jetton/masters", req.model_dump(exclude_none=True))
        return [JettonMaster(**r) for r in resp]

    async def get_jetton_wallets(self, req: GetJettonWalletsRequest) -> List[JettonWallet]:
        resp = await self._async_get("jetton/wallets", req.model_dump(exclude_none=True))
        return [JettonWallet(**r) for r in resp]

    async def get_jetton_transfers(self, req: GetJettonTransfersRequest) -> List[JettonTransfer]:
        resp = await self._async_get("jetton/transfers", req.model_dump(exclude_none=True))
        return [JettonTransfer(**r) for r in resp]

    async def get_jetton_burns(self, req: GetJettonBurnsRequest) -> List[JettonBurn]:
        resp = await self._async_get("jetton/burns", req.model_dump(exclude_none=True))
        return [JettonBurn(**r) for r in resp]

    async def get_top_accounts_by_balance(self, req: GetTopAccountsByBalanceRequest) -> List[AccountBalance]:
        resp = await self._async_get("topAccountsByBalance", req.model_dump(exclude_none=True))
        return [AccountBalance(**r) for r in resp]

    async def get_account(self, req: GetAccountRequest) -> Account:
        resp = await self._async_get("account", req.model_dump(exclude_none=True))
        return Account(**resp)

    async def get_wallet(self, req: GetWalletRequest) -> WalletInfo:
        resp = await self._async_get("wallet", req.model_dump(exclude_none=True))
        return WalletInfo(**resp)

    async def send_message(self, req: ExternalMessage) -> SentMessage:
        resp = await self._async_post("sendMessage", req.model_dump(exclude_none=True))
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
            req = GetTransactionRequest(account=account, start_utime=cur_time, sort="asc", limit=20)
            txs = await self.get_transactions(req)
            if len(txs) > 0:
                for tx in txs:
                    yield tx
                cur_time = txs[-1].now + 1
            await asyncio.sleep(interval_in_second)
