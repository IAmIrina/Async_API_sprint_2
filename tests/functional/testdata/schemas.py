from typing import List, Optional

from pydantic import BaseModel, validator


class Genre(BaseModel):
    uuid: str
    name: str


class Person(BaseModel):
    uuid: str
    name: str


ROLES = ('directors', 'actors', 'writers')


class ActedIn(BaseModel):
    director: Optional[List[str]]
    actor: Optional[List[str]]
    writer: Optional[List[str]]

    class Config:

        validate_assignment = True

    @validator('director', 'actor', 'writer')
    def set_name(cls, role):
        return role or []


class PersonRole(Person):
    role: ActedIn


class FilmShort(BaseModel):
    uuid: str
    title: str
    imdb_rating: Optional[float] = None


class Film(FilmShort):
    description: Optional[str] = None
    genre: Optional[List[Genre]] = None
    directors: Optional[List[Person]] = None
    actors: Optional[List[Person]] = None
    writers: Optional[List[Person]] = None


class PaginationMixin(BaseModel):
    total_pages: int
    page_num: int
    page_size: int


class Films(PaginationMixin):
    data: List[FilmShort]


class Genres(PaginationMixin):
    data: List[Genre]


class Persons(PaginationMixin):
    data: List[PersonRole]
