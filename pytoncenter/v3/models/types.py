from datetime import datetime

from pydantic import PlainSerializer, WithJsonSchema
from typing_extensions import Annotated

from pytoncenter.address import Address

PyDatetime = Annotated[
    datetime,
    PlainSerializer(lambda x: int(x.timestamp()), return_type=int),
    WithJsonSchema({"type": "number"}, mode="serialization"),
]


PyAddress = Annotated[
    str,
    Address,
    PlainSerializer(lambda x: x.to_string(True, True, is_test_only=False), return_type=str),
    WithJsonSchema({"type": "string"}, mode="serialization"),
]
