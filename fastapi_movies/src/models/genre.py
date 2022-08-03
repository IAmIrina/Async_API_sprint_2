"""Endpoint genres pydantic models."""

from typing import List

from models.custom_models import OrjsonModel, PaginationModel


class Genre(OrjsonModel):
    uuid: str
    name: str


class Genres(PaginationModel):
    data: List[Genre]
