import asyncio
import os
import uuid
import warnings
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

import aiohttp
from tonpy import Cell

from pytoncenter.exception import TonException
from pytoncenter.multicall import Multicallable
from pytoncenter.requestor import AsyncRequestor

from .types import *


class AsyncTonCenterClientV2(Multicallable, AsyncRequestor):
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
            self.base_url = f"https://{prefix}toncenter.com/api/v2"
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
        response.raise_for_status()
        result = await response.json()
        if not result["ok"]:
            raise TonException(result["code"])
        return result["result"]

    async def _async_get(self, handler: str, query: Optional[Dict[str, Any]] = None):
        url = f"{self.base_url}/{handler}"
        params = {k: v for k, v in query.items() if v is not None} if query is not None else None
        return await self._underlying_call("GET", url, params=params)

    async def _async_post(self, handler: str, payload: Optional[Dict[str, Any]] = None):
        url = f"{self.base_url}/{handler}"
        payload = {k: v for k, v in payload.items() if v is not None} if payload is not None else None
        return await self._underlying_call("POST", url, payload=payload)

    async def get_address_information(self, address: str) -> WalletInformation:
        return await self._async_get("getAddressInformation", {"address": address})

    async def get_extended_address_information(self, address: str) -> ExtentedAddressInformation:
        return await self._async_get("getExtendedAddressInformation", {"address": address})

    async def get_wallet_information(self, address: str) -> WalletInformation:
        return await self._async_get("getWalletInformation", {"address": address})

    async def get_address_balance(self, address: str) -> int:
        """
        get_address_balance returns the balance of the address in nanoton.
        """
        balance = await self._async_get("getAddressBalance", {"address": address})
        return int(balance)

    async def get_address_state(self, address: str) -> str:
        """
        get_address_state returns the state of the address as a string, e.g. "active", "uninitialized", etc.
        """
        return await self._async_get("getAddressState", {"address": address})

    async def get_token_data(self, address: str) -> Union[JettonMasterData, JettonWalletData, NFTCollectionData, NFTItemData]:
        return await self._async_get("getTokenData", {"address": address})

    async def pack_address(self, address: str) -> str:
        return await self._async_get("packAddress", {"address": address})

    async def unpack_address(self, address: str) -> str:
        return await self._async_get("unpackAddress", {"address": address})

    async def detect_address(self, address: str) -> DetectAddressResult:
        return await self._async_get("detectAddress", {"address": address})

    async def get_masterchain_info(self) -> MasterChainInfo:
        return await self._async_get("getMasterchainInfo")

    async def get_masterchain_block_signatures(self, seq_no: int) -> BlockSignatures:
        return await self._async_get("getMasterchainBlockSignatures", {"seq_no": seq_no})

    async def get_shards(self, seqno: int) -> Shards:
        return await self._async_get("shards", {"seqno": seqno})

    async def get_shard_block_proof(self, workchain: int, shard: int, seqno: int, from_seqno: Optional[int] = None):
        query = {"workchain": workchain, "shard": shard, "seqno": seqno}
        if from_seqno is not None:
            query["from_seqno"] = from_seqno
        return await self._async_get("getShardBlockProof", query=query)

    async def get_consensus_block(self) -> ConsensusBlock:
        return await self._async_get("getConsensusBlock")

    async def lookup_block(
        self,
        workchain: int,
        shard: int,
        seqno: Optional[int] = None,
        lt: Optional[int] = None,
        unixtime: Optional[int] = None,
    ):
        query = {"workchain": workchain, "shard": shard}
        if seqno is not None:
            query["seqno"] = seqno
        if lt is not None:
            query["lt"] = lt
        if unixtime is not None:
            query["unixtime"] = unixtime
        return await self._async_get("lookupBlock", query=query)

    async def shards(self, seqno: int):
        return await self._async_get("shards", {"seqno": seqno})

    async def get_block_transactions(
        self,
        workchain: int,
        shard: int,
        seqno: int,
        root_hash: Optional[str] = None,
        file_hash: Optional[str] = None,
        after_lt: Optional[int] = None,
        after_hash: Optional[str] = None,
        count: Optional[int] = None,
    ):
        query = {"workchain": workchain, "shard": shard, "seqno": seqno}
        if root_hash is not None:
            query["root_hash"] = root_hash
        if file_hash is not None:
            query["file_hash"] = file_hash
        if after_lt is not None:
            query["after_lt"] = after_lt
        if after_hash is not None:
            query["after_hash"] = after_hash
        if count is not None:
            query["count"] = count
        return await self._async_get("getBlockTransactions", query=query)

    async def get_block_header(
        self,
        workchain: int,
        shard: int,
        seqno: int,
        root_hash: Optional[str] = None,
        file_hash: Optional[str] = None,
    ):
        query = {"workchain": workchain, "shard": shard, "seqno": seqno}
        if root_hash is not None:
            query["root_hash"] = root_hash
        if file_hash is not None:
            query["file_hash"] = file_hash
        return await self._async_get("getBlockHeader", query=query)

    async def get_transactions(
        self,
        address: str,
        latest_lt: Optional[int] = None,
        limit: Optional[int] = None,
        begin_lt: Optional[int] = None,
        hash: Optional[str] = None,
        archival: bool = False,
    ) -> List[Tx]:
        """
        get_transactions returns the transactions of the address in descending order of logical time

        Parameters
        ----------
        address : str
            The address to get transactions
        limit : Optional[int], optional
            The limit of transactions to get, default maximum 100
        latest_lt : int, optional
            The latest logical time to get transactions, default None means always find the latest transactions
        lt : Optional[int], optional
            The logical time of the transaction to start getting transactions
        hash : Optional[str], optional
            The hash of the transaction to start getting transactions
        """
        assert limit is None or limit <= 100, "Limit must be less than or equal to 100"
        assert (begin_lt != 0 and hash != "") or (begin_lt == 0 and hash == ""), "begin_lt and hash must be specified together"
        return await self._async_get(
            "getTransactions",
            {
                "address": address,
                "limit": limit,
                "lt": begin_lt,
                "hash": hash,
                "to_lt": latest_lt,
                "archival": int(archival),
            },
        )

    async def try_locate_tx(self, source: str, destination: str, created_lt: int) -> Tx:
        return await self._async_get(
            "tryLocateTx",
            {"source": source, "destination": destination, "created_lt": created_lt},
        )

    async def try_locate_result_tx(self, source: str, destination: str, created_lt: int) -> Tx:
        return await self._async_get(
            "tryLocateResultTx",
            {"source": source, "destination": destination, "created_lt": created_lt},
        )

    async def try_locate_source_tx(self, source: str, destination: str, created_lt: int) -> Tx:
        return await self._async_get(
            "tryLocateSourceTx",
            {"source": source, "destination": destination, "created_lt": created_lt},
        )

    async def get_config_param(self, config_id: int, seqno: Optional[int] = None):
        return await self._async_get("getConfigParam", {"config_id": config_id, "seqno": seqno})

    async def run_get_method(self, address: str, method_name: str, stack: List[Tuple[str, Any]] = []) -> GetMethodResult:
        result = await self._async_post("runGetMethod", {"address": address, "method": method_name, "stack": stack})
        if result.get("@type") == "smc.runResult" and "stack" in result:
            r: Dict[str, Any] = result["stack"]
            return [{"type": r[i][0], "value": r[i][1]} for i in range(len(r))]
        raise ValueError(f"Invalid get method result: {result}")

    async def send_boc(self, boc: str):
        return await self._async_post("sendBoc", {"boc": boc})

    async def send_boc_return_hash(self, boc: str):
        return await self._async_post("sendBocReturnHash", {"boc": boc})

    async def send_query(self, address: str, body: str, init_code: str, init_data: str):
        return await self._async_post(
            "sendQuery",
            {
                "address": address,
                "body": body,
                "init_code": init_code,
                "init_data": init_data,
            },
        )

    async def estimate_fee(
        self,
        address: str,
        body: Union[str, Cell],
        init_code: str,
        init_data: str,
        ignore_chksig: bool = True,
    ) -> EstimateResult:
        if isinstance(body, Cell):
            body = body.to_boc()
        return await self._async_post(
            "estimateFee",
            {
                "address": address,
                "body": body,
                "init_code": init_code,
                "init_data": init_data,
                "ignore_chksig": int(ignore_chksig),
            },
        )

    async def json_rpc(
        self,
        method: str,
        params: Dict[str, Any],
        id: Optional[int] = None,
        jsonrpc: Optional[str] = "2.0",
    ):
        id = uuid.uuid4().int if id is None else id
        return await self._async_post(
            "jsonRpc",
            {"method": method, "params": params, "id": id, "jsonrpc": jsonrpc},
        )

    async def subscribe_tx(self, address: str, interval_in_second: float = 1.0, limit: int = 20):
        """
        subscribeTx returns a generator that yields transactions of the address

        Parameters
        ----------
        address : str
            The address to subscribe to
        interval_in_second : float
            The interval_in_second to poll the TonCenter API, by default 1 second
        limit : int
            The limit of transactions to get, by default 20. Means the maximum number of transactions to get in one request.
            And the oldest transaction you can get in default is 20 transactions from the latest transaction.

        Yields
        ------
        Tx
            The transaction of the address
        """
        cur_lt = None
        while True:
            try:
                if cur_lt is not None:
                    await asyncio.sleep(interval_in_second)
                results = await self.get_transactions(address, limit=limit, latest_lt=cur_lt, archival=False)
                if not results:
                    continue

                # The results will be sorted by lt in descending order by default, so we need to reverse it
                results.reverse()

                # Now the last transaction is the latest transaction, it will be the next begin_lt and begin_txhash
                cur_lt = results[-1]["transaction_id"]["lt"]

                for tx in results:
                    yield tx

            except asyncio.CancelledError:
                break
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(e)

    async def trace_tx(self, root_tx: Tx) -> TraceTx:
        """
        trace_tx traces the transaction and its children transactions

        Example
        -------
        ```
        client = AsyncTonCenterClient(network="testnet")
        txs = await client.get_transactions("kQAreQ23eabjRO5glLCbhZ4KxQ9SOIjtw2eM2PuEXXhIZeh3", limit=1)
        trace = await client.trace_tx(txs[0])
        pprint(trace)
        """

        async def get_children_tx(source: str, destination: str, created_lt: int) -> Optional[TraceTx]:
            try:
                _tx = await self.try_locate_tx(source=source, destination=destination, created_lt=created_lt)
                _trace: TraceTx = {
                    "@type": _tx["@type"],
                    "address": _tx["address"],
                    "data": _tx["data"],
                    "fee": _tx["fee"],
                    "other_fee": _tx["other_fee"],
                    "storage_fee": _tx["storage_fee"],
                    "transaction_id": _tx["transaction_id"],
                    "utime": _tx["utime"],
                    "in_msg": _tx["in_msg"],
                    "children": [],
                }
                tasks = [
                    get_children_tx(
                        source=msg["source"],
                        destination=msg["destination"],
                        created_lt=int(msg["created_lt"]),
                    )
                    for msg in _tx["out_msgs"]
                ]
                _trace["children"] = [child_tx for child_tx in await asyncio.gather(*tasks) if child_tx is not None]
                return _trace
            except TonException:
                return None

        output: TraceTx = {
            "@type": root_tx["@type"],
            "address": root_tx["address"],
            "data": root_tx["data"],
            "fee": root_tx["fee"],
            "other_fee": root_tx["other_fee"],
            "storage_fee": root_tx["storage_fee"],
            "transaction_id": root_tx["transaction_id"],
            "utime": root_tx["utime"],
            "in_msg": root_tx["in_msg"],
            "children": [],
        }

        tasks = [
            get_children_tx(
                source=msg["source"],
                destination=msg["destination"],
                created_lt=int(msg["created_lt"]),
            )
            for msg in root_tx["out_msgs"]
        ]
        output["children"] = [child_tx for child_tx in await asyncio.gather(*tasks) if child_tx is not None]

        return output
