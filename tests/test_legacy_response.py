import json

import httpx
import pytest
import pydantic

from anthropic import Anthropic, BaseModel
from anthropic._streaming import Stream
from anthropic._base_client import FinalRequestOptions
from anthropic._legacy_response import LegacyAPIResponse


class PydanticModel(pydantic.BaseModel):
    ...


def test_response_parse_mismatched_basemodel(client: Anthropic) -> None:
    response = LegacyAPIResponse(
        raw=httpx.Response(200, content=b"foo"),
        client=client,
        stream=False,
        stream_cls=None,
        cast_to=str,
        options=FinalRequestOptions.construct(method="get", url="/foo"),
    )

    with pytest.raises(
        TypeError,
        match="Pydantic models must subclass our base model type, e.g. `from anthropic import BaseModel`",
    ):
        response.parse(to=PydanticModel)


def test_response_parse_custom_stream(client: Anthropic) -> None:
    response = LegacyAPIResponse(
        raw=httpx.Response(200, content=b"foo"),
        client=client,
        stream=True,
        stream_cls=None,
        cast_to=str,
        options=FinalRequestOptions.construct(method="get", url="/foo"),
    )

    stream = response.parse(to=Stream[int])
    assert stream._cast_to == int


class CustomModel(BaseModel):
    foo: str
    bar: int


def test_response_parse_custom_model(client: Anthropic) -> None:
    response = LegacyAPIResponse(
        raw=httpx.Response(200, content=json.dumps({"foo": "hello!", "bar": 2})),
        client=client,
        stream=False,
        stream_cls=None,
        cast_to=str,
        options=FinalRequestOptions.construct(method="get", url="/foo"),
    )

    obj = response.parse(to=CustomModel)
    assert obj.foo == "hello!"
    assert obj.bar == 2
