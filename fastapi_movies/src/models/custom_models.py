"""Mixins pydantic models."""

import orjson
from typing import Generic, List, TypeVar, Literal, Optional
from pydantic import BaseModel
from pydantic.generics import GenericModel
from fastapi import Query

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


class PaginateParams:
    def __init__(
        self,
        page_size: Optional[int] = Query(
            50, alias='page[size]', description='Items amount on page', ge=1
        ),
        page_number: Optional[int] = Query(
            1, alias='page[number]', description='Page number for pagination', ge=1
        ),
    ):
        self.page_num = page_number
        self.page_size = page_size


class SortModel(BaseModel):
    field: str
    order: Literal['asc', 'desc']
