from __future__ import annotations

import warnings
from abc import ABC, abstractmethod
from typing import Any, Dict, List, OrderedDict, TypedDict, Union

from tonpy import CellSlice

from pytoncenter.v2.types import GetMethodResult
from pytoncenter.v3.models import (
    GetMethodParameterOutput,
    GetMethodParameterType,
    RunGetMethodResponse,
)

from .address import Address
from .utils import decode_base64

__all__ = ["BaseType", "Types", "BaseDecoder", "Decoder", "JettonDataDecoder"]


GetMethodResultType = Union[GetMethodResult, RunGetMethodResponse]


class BaseType:
    type: GetMethodParameterType

    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def decode(self, data: Any):
        raise NotImplementedError


class Types:
    class Raw(BaseType):
        type = "unsupported_type"

        def decode(self, data: Any):
            return data

    class Number(BaseType):
        type = "num"

        def decode(self, hex_str: str) -> int:
            return int(hex_str, 16)

    class Address(BaseType):
        type = "cell"

        def decode(self, cell: str) -> Address:
            return Address(CellSlice(cell).load_address())

    class Bool(BaseType):
        type = "num"

        def decode(self, hex_str: str) -> bool:
            return bool(int(hex_str, 16))

    class Cell(BaseType):
        type = "cell"

        def decode(self, cell: str) -> CellSlice:
            return CellSlice(cell)

    class B64String(BaseType):
        type = "cell"

        def decode(self, cell: str) -> str:
            return decode_base64(cell)

    class List(BaseType):
        type = "list"

        def __init__(self, name: str, *typs: BaseType) -> None:
            super().__init__(name)
            self.typs = typs

        def decode(self, data: Any):
            warnings.warn("List type is not supported yet, return raw data", RuntimeWarning)
            return data

    class Tuple(BaseType):
        type = "tuple"

        def __init__(self, name: str, *typs: BaseType) -> None:
            super().__init__(name)
            self.typs = typs

        def decode(self, data: Any):
            warnings.warn("Tuple type is not supported yet, return raw data", RuntimeWarning)
            return data

    class Slice(BaseType):
        type = "slice"

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
                assert self.types[i] is None or self.types[i].type == data[i]["type"], f"Field {i} type must be {self.types[i].type}, but got {data[i]['type']}"
                _type = data[i].get("type")
                _value = data[i].get("value")
                if _type == "cell":
                    new_data.append(GetMethodParameterOutput(type=_type, value=_value.get("bytes", "")))
                else:
                    new_data.append(GetMethodParameterOutput(type=_type, value=_value))
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
                if type == "cell":
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

            if data.type == "cell":
                assert isinstance(data.value, str), "Cell value must be a string"
                try:
                    t = Types.Address(field_name)
                    return t.name, t.decode(data.value)
                except:
                    t = Types.B64String(field_name)
                    return t.name, t.decode(data.value)
            if data.type == "slice":
                assert isinstance(data.value, list), "Slice value must be a list"
                t = Types.Slice(field_name)
                return t.name, t.decode(data.value)
            if data.type == "list" or data.type == "tuple":
                assert isinstance(data.value, list), "List value must be a list"
                results = []
                for i, t in enumerate(data.value):
                    result, _ = _recursive_decode(t, f"{field_name}_", i, depth + 1)
                    results.append(result)
                return field_name, results
            elif data.type == "num":
                assert isinstance(data.value, str), "Number value must be a string"
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
        Types.B64String("jetton_wallet_code"),
    )
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JettonDataDecoder, cls).__new__(cls)
        return cls._instance

    def decode(self, data: GetMethodResultType) -> JettonDataDict:
        return self.decoder.decode(data)
