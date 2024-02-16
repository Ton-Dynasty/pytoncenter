import asyncio
from functools import wraps

import click
import pyfiglet

from pytoncenter import get_client
from pytoncenter.utils import format_trace
from pytoncenter.v3.models import *


def asyncmd(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


def common_options(f):
    f = click.option("--network", "-n", default="testnet", help="Network", type=click.Choice(["testnet", "mainnet"]))(f)
    f = click.option("--api-key", "-k", envvar="TONCENTER_API_KEY", default=None, help="API Key")(f)
    return f


CONTEXT_SETTINGS = dict(
    help_option_names=["-h", "--help"],
)

WELCOME_MESSAGE = f"\033[93m{pyfiglet.figlet_format('welcome to pytoncenter')}\033[0m"
VERSION_INFO = f"\nversion  |  %(version)s \n"

# fmt: off
@click.group(context_settings=CONTEXT_SETTINGS, invoke_without_command=True, no_args_is_help=True,)
@click.version_option(package_name="pytoncenter", message=f"\033[93m{pyfiglet.figlet_format('welcome to pytoncenter')}\033[0m {VERSION_INFO}")
def cli():
    pass


@cli.command(help="Get transaction trace which contains the specified transaction")
@click.option("--txhash", required=True)
@common_options
@asyncmd
async def trace(txhash: str,network:Literal["mainnet","testnet"], api_key: str):
    client = get_client(version="v3", network=network) # type: ignore
    trace = await client.get_trace_alternative(GetTransactionTraceRequest(hash=txhash))
    fmt = format_trace(trace)
    click.echo(fmt)

@cli.command(help="Get account balance")
@click.option("--address", required=True, help="Address")
@common_options
@asyncmd
async def balance(address: str, network: Literal["mainnet","testnet"], api_key: str):
    client = get_client(version="v3", network=network) # type: ignore
    balance = await client.get_account(GetAccountRequest(address=address))
    click.echo(f"Address: {address}\nBalance: {balance.balance / 1e9} TON")


if __name__ == "__main__":
    cli()
