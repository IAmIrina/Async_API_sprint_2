"""Endpoint persons pydantic models."""

from typing import List, Optional
from pydantic import validator

from models.custom_models import OrjsonModel, PaginationModel


class ActedIn(OrjsonModel):
    director: Optional[List[str]]
    actor: Optional[List[str]]
    writer: Optional[List[str]]

    class Config:
        validate_assignment = True

    @validator('director', 'actor', 'writer')
    def set_name(cls, role):
        return role or []


class MoviePerson(OrjsonModel):
    uuid: str
    name: str


class Person(OrjsonModel):
    uuid: str
    name: str
    role: ActedIn


class Persons(PaginationModel):
    data: List[Person]


class Movie(OrjsonModel):
    uuid: str
    title: str
    imdb_rating: Optional[float] = None


class Movies(PaginationModel):
    data: List[Movie]
