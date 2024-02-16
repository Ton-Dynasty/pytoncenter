from typing import Callable, Dict, Optional, Union

from deprecated import deprecated
from tonpy import CellSlice
from treelib import Node, Tree

from pytoncenter.address import Address
from pytoncenter.utils import get_opcode

from .types import TraceTx

__all__ = [
    "NamedFunction",
    "truncate_middle",
    "create_named_mapping_func",
    "default_named_func",
    "format_trace_tx",
    "pretty_print_trace_tx",
]

NamedFunction = Callable[[Address], Optional[str]]


@deprecated(version="0.1.0", reason="truncate_middle is deprecated, use `pytoncenter.utils.truncate_address` instead")
def truncate_middle(address: Address, prefix: int = 6, suffix: int = 6) -> str:
    """
    Truncate middle part of the address to make it more readable
    """
    addr = address.to_string(True, is_test_only=False)
    return addr[:prefix] + "..." + addr[-suffix:] if len(addr) > prefix + suffix else addr


@deprecated(version="0.1.0", reason="default_named_func is deprecated, use `pytoncenter.utils.default_address_mapping` instead")
def default_named_func(address: Address, **kwargs) -> Optional[str]:
    """
    Truncate middle part of the address to make it more readable

    Parameters
    ----------
    address : str
        Address to be formatted
    prefix : int, optional
        Prefix length
    suffix : int, optional
        Suffix length
    """
    prefix = kwargs.get("prefix", 6)
    suffix = kwargs.get("suffix", 6)
    return truncate_middle(address, prefix, suffix)


@deprecated(version="0.1.0", reason="format_trace_tx is deprecated, use `pytoncenter.utils.format_tx` instead")
def format_trace_tx(trace_tx: TraceTx, named_func: NamedFunction = default_named_func) -> str:
    """
    Format transaction trace in a pretty way
    A -> B (Value, Opcode)
    """
    raw_src = trace_tx.get("in_msg", {}).get("source", "")
    raw_dst = trace_tx.get("in_msg", {}).get("destination", "")
    value = int(trace_tx.get("in_msg", {}).get("value", "0")) / 1e9
    opcode = "invalid opcode"
    in_msg_data = trace_tx.get("in_msg", {}).get("msg_data", {})
    if in_msg_data.get("@type") == "msg.dataText":
        opcode = trace_tx.get("in_msg", {}).get("message")
    elif in_msg_data.get("@type") == "msg.dataRaw":
        cs = CellSlice(in_msg_data.get("body"))
        opcode = get_opcode(cs.load_uint(32))
    return "{src} -> {dest} ({opcode}) [{value} TON]".format(
        src=named_func(Address(raw_src)) if raw_src else "<external>",
        dest=named_func(Address(raw_dst)),
        value=value,
        opcode=opcode,
    )


@deprecated(version="0.1.0", reason="create_named_mapping_func is deprecated, use `pytoncenter.utils.create_address_mapping` instead")
def create_named_mapping_func(mapping: Dict[Address, str], truncate_address: bool = True) -> NamedFunction:
    """
    create a named function to map address to a more readable format
    For example, you can map address EQAuVtH68PRkM8qsMUh670ecNZPtqs5bANF3MD4dv-eBb2vD to "Alice" using this function
    if the address is not in the mapping, it will return the original address by default
    the original address can be truncated if truncate_address is True
    """

    def namedFunction(address: Union[str, Address]) -> Optional[str]:
        """
        Truncate middle part of the address to make it more readable
        """
        _addr = Address(address)
        default = truncate_middle(_addr, 6, 6) if truncate_address else _addr.to_string(True, is_test_only=False)
        return mapping.get(_addr, default)

    return namedFunction


@deprecated(version="0.1.0", reason="pretty_print_trace_tx with client v2 is deprecated, use `pytoncenter.utils.format_trace` and client v3 instead")
def pretty_print_trace_tx(trace_tx: TraceTx, named_func: NamedFunction = default_named_func):
    """
    print transaction trace in a pretty way
    """

    def recursive_add_tx(tree: Tree, tx: TraceTx, parent: Optional[Node] = None):
        """
        Recursively add node to the tree
        """
        txhash = tx["transaction_id"]["hash"]
        tree.create_node(
            identifier=txhash,
            tag=format_trace_tx(tx, named_func),
            parent=parent,
        )
        for child in tx["children"]:
            recursive_add_tx(tree, child, txhash)

    tree = Tree()
    recursive_add_tx(tree, trace_tx)
    output = tree.show(stdout=False)
    print(output)
