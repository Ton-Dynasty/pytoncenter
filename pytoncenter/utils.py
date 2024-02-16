import base64
from typing import Callable, Dict, Optional

from treelib import Node, Tree

from pytoncenter.address import Address
from pytoncenter.v3.models import Transaction, TransactionTrace

__all__ = [
    "get_opcode",
    "encode_base64",
    "decode_base64",
    "AddressMapping",
    "format_tx",
    "format_trace",
    "truncate_address",
    "create_address_mapping",
]


def get_opcode(data_uint32: int) -> str:
    """
    Get opcode from uint32, the output is a string with 0x prefix, 10 characters long.
    """
    return "0x{:08x}".format(data_uint32).lower()


def encode_base64(hex_data: str) -> str:
    # Convert the hex data back into bytes
    bytes_data = bytes.fromhex(hex_data)
    # Encode these bytes into a base64 string
    base64_encoded = base64.b64encode(bytes_data)
    # Return the base64-encoded string
    return base64_encoded.decode()


def decode_base64(data: str) -> str:
    return base64.b64decode(data + "==").hex()


AddressMapping = Callable[[Address], str]


def _default_address_mapping(address: Address, **kwargs) -> str:
    """
    default_address_mapping map address to a user friendly format with middle part truncated

    Parameters
    ----------
    address : str
        Address to be formatted
    prefix : int, optional
        Prefix length
    suffix : int, optional
        Suffix length
    """
    assert isinstance(address, Address), "address should be an instance of Address"
    prefix = kwargs.get("prefix", 6)
    suffix = kwargs.get("suffix", 6)
    addr = address.to_string(True, is_test_only=False)
    return addr[:prefix] + "..." + addr[-suffix:] if len(addr) > prefix + suffix else addr


def create_address_mapping(mapping: Dict[Address, str], truncate: bool = True) -> AddressMapping:
    def _mapping_func(address: Address) -> str:
        default = truncate_address(address) if truncate else address.to_string(True, is_test_only=False)
        return mapping.get(address, default)

    return _mapping_func


def truncate_address(address: Address, prefix: int = 6, suffix: int = 6) -> str:
    """
    Truncate middle part of the address to make it more readable
    """
    addr = address.to_string(True, is_test_only=False)
    return addr[:prefix] + "..." + addr[-suffix:] if len(addr) > prefix + suffix else addr


def format_tx(tx: Transaction, address_mapping: AddressMapping = _default_address_mapping) -> str:
    tmpl = "\033[95m{src}\033[0m ➡️ \033[92m{dest}\033[0m \033[93m({msg})\033[0m \033[94m[💎 {value} TON]\033[0m"
    src = address_mapping(Address(tx.in_msg.source)) if tx.in_msg.source else "External"
    dst = address_mapping(Address(tx.in_msg.destination)) if tx.in_msg.destination else ""
    value = round((tx.in_msg.value or 0) / 1e9, 5)
    msg = tx.in_msg.opcode
    if (msg is None or msg == "0x00000000") and tx.in_msg.message_content is not None and tx.in_msg.message_content.decoded is not None:
        if tx.in_msg.message_content.decoded.type == "text_comment":
            msg = tx.in_msg.message_content.decoded.comment
        else:
            msg = "<Binary message>"

    return tmpl.format(src=src, dest=dst, msg=msg, value=value)


def format_trace(root: TransactionTrace, address_mapping: AddressMapping = _default_address_mapping) -> str:
    """
    print transaction trace in a pretty way

    Returns
    -------
    str
        The pretty printed transaction trace in tree format
    """

    def recursive_add_node(tree: Tree, trace: TransactionTrace, parent: Optional[Node] = None):
        """
        Recursively add node to the tree
        """
        node = tree.create_node(
            identifier=trace.transaction.hash,
            tag=format_tx(trace.transaction, address_mapping),
            parent=parent,
        )
        for child in trace.children:
            recursive_add_node(tree, child, node)

    tree = Tree()
    recursive_add_node(tree, root)
    return tree.show(stdout=False)  # type: ignore
