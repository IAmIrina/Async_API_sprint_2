"""Endpoint films pydantic models."""
from typing import List, Optional

from models.custom_models import OrjsonModel, PaginationModel


class Person(OrjsonModel):
    uuid: str
    name: str


class Genre(OrjsonModel):
    uuid: str
    name: str


class FilmShort(OrjsonModel):
    uuid: str
    title: str
    imdb_rating: Optional[float] = None


class Film(FilmShort):
    description: Optional[str] = None
    genre: Optional[List[Genre]] = None
    directors: Optional[List[Person]] = None
    actors: Optional[List[Person]] = None
    writers: Optional[List[Person]] = None


class Films(PaginationModel):
    data: List[FilmShort]
