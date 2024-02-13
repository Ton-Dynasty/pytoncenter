from datetime import datetime
from typing import Any, Callable

from pydantic import GetJsonSchemaHandler, PlainSerializer, WithJsonSchema
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from typing_extensions import Annotated

from pytoncenter.address import Address

PyDatetime = Annotated[
    datetime,
    PlainSerializer(lambda x: int(x.timestamp()), return_type=int),
    WithJsonSchema({"type": "number"}, mode="serialization"),
]


class _AddressTypeAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Callable[[Any], core_schema.CoreSchema],
    ) -> core_schema.CoreSchema:
        """
        - str will be parsed as Address
        - Address type will be parsed as Address without any changes
        - Nothing else will pass validation
        - Serialization will always return just an str
        """

        def validate_from_str(value: str) -> Address:
            return Address(value)

        from_str_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(validate_from_str),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(Address),
                    from_str_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: x.to_string(
                    is_user_friendly=True,
                    is_url_safe=True,
                    is_test_only=False,
                )
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        return handler(core_schema.str_schema())


AddressLike = Annotated[str, Address, _AddressTypeAnnotation]
