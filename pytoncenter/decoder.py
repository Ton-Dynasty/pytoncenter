from .types import GetMethodResult
from typing import Dict, Any, OrderedDict, TypedDict
from abc import abstractmethod
from .address import Address
from tonpy import CellSlice
from .utils import decode_base64

__all__ = ["BaseField", "Field", "BaseDecoder", "Decoder", "JettonDataDecoder"]


class BaseField:
    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def decode(self, data: Any):
        raise NotImplementedError


class Field:
    class RawField(BaseField):
        def decode(self, data: Any):
            return data

    class Number(BaseField):
        def decode(self, hex_str: str) -> int:
            return int(hex_str, 16)

    class Address(BaseField):
        def decode(self, cell: Dict[str, Any]) -> Address:
            return Address(CellSlice(cell["bytes"]).load_address())

    class Bool(BaseField):
        def decode(self, hex_str: str) -> bool:
            return bool(int(hex_str, 16))

    class Cell(BaseField):
        def decode(self, cell: Dict[str, Any]) -> CellSlice:
            return decode_base64(cell["bytes"])


class BaseDecoder:
    """
    BaseDecoderDecoder decodes the result of the return of the TON smart contract get method
    """

    @abstractmethod
    def decode(self, data: GetMethodResult) -> Any:
        raise NotImplementedError


class Decoder(BaseDecoder):
    def __init__(self, *fields: BaseField) -> None:
        self._fields = fields

    def decode(self, data: GetMethodResult) -> Dict[str, Any]:
        assert len(self._fields) == len(data), "Fields count must be equal to data count"
        return OrderedDict((field.name, field.decode(data[i]["value"])) for i, field in enumerate(self._fields))


JettonDataDict = TypedDict(
    "JettonData",
    {
        "total_supply": int,
        "mintable": bool,
        "admin_address": Address,
        "jetton_content": str,
        "jetton_wallet_code": str,
    },
)


class JettonDataDecoder(BaseDecoder):
    """
    JettonDataDecoder is a singleton class that decodes the result of the get_jetton_data method
    """

    decoder = Decoder(
        Field.Number("total_supply"),
        Field.Bool("mintable"),
        Field.Address("admin_address"),
        Field.Cell("jetton_content"),
        Field.Cell("jetton_wallet_code"),
    )
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JettonDataDecoder, cls).__new__(cls)
        return cls._instance

    def decode(self, data: GetMethodResult) -> JettonDataDict:
        return self.decoder.decode(data)
