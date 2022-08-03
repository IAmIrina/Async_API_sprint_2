"""Mixins pydantic models."""

import orjson
from typing import Generic, List, TypeVar, Literal
from pydantic import BaseModel
from pydantic.generics import GenericModel

Model = TypeVar("Model", bound=BaseModel)


def orjson_dumps(v, *, default) -> str:
    """Fast json dumps."""
    return orjson.dumps(v, default=default).decode()


class OrjsonModel(BaseModel):
    """Fast json serializer."""

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class PaginationModel(GenericModel, Generic[Model]):
    total_pages: int
    page_num: int
    page_size: int
    data: List[Model]


class SortModel(BaseModel):
    field: str
    order: Literal['asc', 'desc']
