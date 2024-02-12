from pytoncenter import get_client
from pytoncenter.v3.models import *
import asyncio


async def main():
    client = get_client(version="v3", network="testnet")
    req = GetAccountRequest(address="kQCpk40ub48fvx89vSUjOTRy0vOEEZ4crOPPfLEvg88q1EeH")
    account_info = await client.get_account(req)

    # Check account status is active
    if account_info.status == AccountStatus.active:
        print("Account is active")
    else:
        raise Exception("Account is not active")
    
    print("=====================================")

    # Get oracle metadata (run get method)
    metadata = await client.run_get_method(RunGetMethodRequest(address="kQCpk40ub48fvx89vSUjOTRy0vOEEZ4crOPPfLEvg88q1EeH", method="getOracleData", stack=[]))
    print(metadata)

    print("=====================================")
    
    try:
        # Oracle contract is not a wallet, so it will raise an exception
        req = GetWalletRequest(address="kQCpk40ub48fvx89vSUjOTRy0vOEEZ4crOPPfLEvg88q1EeH")
        await client.get_wallet(req)
    except Exception as e:
        print(e)
        
    print("=====================================")

    # Get transactions
    req = GetTransactionRequest(account="kQCpk40ub48fvx89vSUjOTRy0vOEEZ4crOPPfLEvg88q1EeH")
    transactions = await client.get_transactions(req)
    print(transactions[0].hash)
    
    print("=====================================")

    # Get transaction traces
    req = GetAdjacentTransactionsRequest(hash=transactions[0].hash)
    traces = await client.get_adjacent_transactions(req)
    print(traces)
    
    print("=====================================")


if __name__ == "__main__":
    asyncio.run(main())
