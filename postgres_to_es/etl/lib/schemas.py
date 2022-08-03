"""Schemas to transform and validate data."""

from typing import List, Optional

from pydantic import BaseModel


class Person(BaseModel):
    """Person data schema."""

    uuid: str
    name: str


class Genre(BaseModel):
    """Genre data schema."""

    uuid: str
    name: str


class Movie(BaseModel):
    """Movie data schema."""

    uuid: str
    imdb_rating: Optional[float]
    genre: Optional[List[Genre]]
    title: str
    description: Optional[str]
    director: List[str]
    actors_names: List[str]
    writers_names: List[str]
    directors: Optional[List[Person]]
    actors: Optional[List[Person]]
    writers: Optional[List[Person]]


class FilmPerson(BaseModel):
    """Genre data schema."""

    uuid: str
    name: str
