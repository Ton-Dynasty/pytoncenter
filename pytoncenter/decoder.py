from __future__ import annotations
from pytoncenter.v2.types import GetMethodResult
from pytoncenter.v3.models import GetMethodParameterOutput, GetMethodParameterType, RunGetMethodResponse
from typing import Dict, Any, OrderedDict, TypedDict, List, Union, Optional, Tuple
from abc import abstractmethod, ABC
from .address import Address
from tonpy import CellSlice
from .utils import decode_base64
import warnings

__all__ = ["BaseType", "Types", "BaseDecoder", "Decoder", "JettonDataDecoder"]


GetMethodResultType = Union[GetMethodResult | RunGetMethodResponse]


class BaseType:
    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    @abstractmethod
    def type(self) -> Optional[GetMethodParameterType]:
        return None

    def decode(self, data: Any):
        raise NotImplementedError


class Types:
    class Raw(BaseType):
        type = None

        def decode(self, data: Any):
            return data

    class Number(BaseType):
        type = GetMethodParameterType.num

        def decode(self, hex_str: str) -> int:
            return int(hex_str, 16)

    class Address(BaseType):
        type = GetMethodParameterType.cell

        def decode(self, cell: str) -> Address:
            return Address(CellSlice(cell).load_address())

    class Bool(BaseType):
        type = GetMethodParameterType.num

        def decode(self, hex_str: str) -> bool:
            return bool(int(hex_str, 16))

    class Cell(BaseType):
        type = GetMethodParameterType.cell

        def decode(self, cell: str) -> CellSlice:
            return decode_base64(cell)

    class List(BaseType):
        type = GetMethodParameterType.list

        def __init__(self, name: str, *typs: BaseType) -> None:
            super().__init__(name)
            self.typs = typs

        def decode(self, data: Any):
            warnings.warn("List type is not supported yet, return raw data", RuntimeWarning)
            return data

    class Tuple(BaseType):
        type = GetMethodParameterType.tuple

        def __init__(self, name: str, *typs: BaseType) -> None:
            super().__init__(name)
            self.typs = typs

        def decode(self, data: Any):
            warnings.warn("Tuple type is not supported yet, return raw data", RuntimeWarning)
            return data

    class Slice(BaseType):
        type = GetMethodParameterType.slice

        def decode(self, data: Any):
            warnings.warn("Slice type is not supported yet, return raw data", RuntimeWarning)
            return data


class BaseDecoder(ABC):
    """
    BaseDecoderDecoder decodes the result of the return of the TON smart contract get method
    """

    @abstractmethod
    def decode(self, data: GetMethodResultType):
        raise NotImplementedError


class Decoder(BaseDecoder):
    def __init__(self, *typ: BaseType) -> None:
        self.types = typ
        assert len(self.types) == len(set(field.name for field in self.types)), "Field names must be unique"

    def _validate(self, data: GetMethodResultType) -> List[GetMethodParameterOutput]:
        if isinstance(data, RunGetMethodResponse):
            assert len(self.types) == len(data.stack), "Fields count must be equal to data count"
            return data.stack

        assert len(self.types) == len(data), "Fields count must be equal to data count"
        assert isinstance(data, list), "Data must be a list"
        if all(isinstance(data[i], dict) for i in range(len(data))):
            new_data = []
            for i in range(len(data)):
                assert self.types[i] is None or self.types[i].type.value == data[i]["type"], f"Field {i} type must be {self.types[i].type}, but got {data[i]['type']}"
                type = data[i].get("type")
                value = data[i].get("value")
                if type == GetMethodParameterType.cell.value:
                    new_data.append(GetMethodParameterOutput(type=type, value=value.get("bytes", "")))
                else:
                    new_data.append(GetMethodParameterOutput(type=type, value=value))
            return new_data
        raise ValueError("Data must be a RunGetMethodResponse(v3) or a list of GetMethodResult(v2)")

    def decode(self, data: GetMethodResultType) -> Dict[str, Any]:
        _data = self._validate(data)
        return OrderedDict((field.name, field.decode(_data[i].value)) for i, field in enumerate(self.types))


class AutoDecoder(BaseDecoder):
    def _transform(self, data: GetMethodResultType) -> List[GetMethodParameterOutput]:
        if isinstance(data, RunGetMethodResponse):
            return data.stack
        assert isinstance(data, list), "Data must be a list"
        if all(isinstance(data[i], dict) for i in range(len(data))):
            new_data = []
            for i in range(len(data)):
                type = data[i].get("type")
                value = data[i].get("value")
                if type == GetMethodParameterType.cell.value:
                    new_data.append(GetMethodParameterOutput(type=type, value=value.get("bytes", "")))
                else:
                    new_data.append(GetMethodParameterOutput(type=type, value=value))
            return new_data
        raise ValueError("Data must be a RunGetMethodResponse(v3) or a list of GetMethodResult(v2)")

    def decode(self, data: GetMethodResultType) -> Dict[str, Any]:
        _data = self._transform(data)
        output = {}

        def _recursive_decode(data: GetMethodParameterOutput, prefix: str = "idx_", idx: int = 0, depth: int = 0):
            field_name = f"{prefix}{idx}"

            if data.type == GetMethodParameterType.cell:
                # try to decode as address
                try:
                    t = Types.Address(field_name)
                    return t.name, t.decode(data.value)
                except:
                    t = Types.Cell(field_name)
                    return t.name, t.decode(data.value)
            if data.type == GetMethodParameterType.slice:
                t = Types.Slice(field_name)
                return t.name, t.decode(data.value)
            if data.type == GetMethodParameterType.list or data.type == GetMethodParameterType.tuple:
                results = []
                for i, t in enumerate(data.value):
                    result, _ = _recursive_decode(t, f"{field_name}_", i, depth + 1)
                    results.append(result)
                return field_name, results
            elif data.type == GetMethodParameterType.num:
                t = Types.Number(field_name)
                return t.name, t.decode(data.value)
            else:
                t = Types.Raw(field_name)
                return t.name, t.decode(data.value)

        for idx, field in enumerate(_data):
            name, value = _recursive_decode(field, idx=idx)
            output[name] = value

        return output


JettonDataDict = TypedDict(
    "JettonDataDict",
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
        Types.Number("total_supply"),
        Types.Bool("mintable"),
        Types.Address("admin_address"),
        Types.Cell("jetton_content"),
        Types.Cell("jetton_wallet_code"),
    )
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JettonDataDecoder, cls).__new__(cls)
        return cls._instance

    def decode(self, data: GetMethodResultType) -> JettonDataDict:
        return self.decoder.decode(data)
