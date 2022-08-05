"""Persons views"""
import logging

from functools import lru_cache
from typing import Optional

from fastapi import Depends

from db.search import AsyncSearchEngine, BaseSearchAdapter, get_search_engine
from db.elastic import get_search_adapter

from db.cache import get_cache, Cache, AsyncCacheStorage
from core.pagination import Paginator

from models.custom_models import SortModel
from models.person import Person, Persons, ActedIn, Movies
from core.config import settings


class PersonService:
    """Handle source person data."""

    def __init__(self,
                 cache_storage: AsyncCacheStorage,
                 search_engine: AsyncSearchEngine,
                 search_adapter: BaseSearchAdapter,
                 index: str,
                 movies_idx: str
                 ):
        self.cache = Cache(cache_storage, index)

        self.person_paginator = Paginator(Persons)
        self.movie_paginator = Paginator(Movies)

        self.searcher = search_adapter(search_engine, index)
        self.movie_searcher = search_adapter(search_engine, movies_idx)

    async def get_document(self, uuid: str) -> Optional[Person]:
        """Return person by uuid from source. """
        key = self.cache.gen_cache_key(uuid=uuid)
        person = await self.cache.get(key)
        if not person:
            person = await self.searcher.fetch_one(uuid=uuid)
            logging.debug("PERSON_BY_ID: %s", person)
            if not person:
                return None
            person['role'] = await self._get_roles(uuid)
            person = Person(**person)
            await self.cache.set(key, person)
        return person

    async def get_page(
            self,
            page_num: int = 1,
            page_size: int = 50,
    ) -> Optional[Person]:
        """Return one page of all persons from source."""
        key = self.cache.gen_cache_key(
            page_num=page_num,
            page_size=page_size,
        )
        persons = await self.cache.get(key)

        if not persons:
            persons, total_count = await self.searcher.fetch_all(
                from_=page_size * (page_num - 1),
                size=page_size,
            )

            if not persons:
                return None
            for person in persons:
                person['role'] = await self._get_roles(person['uuid'])
            persons = await self.person_paginator.paginate(persons, page_num, page_size, total_count)
            await self.cache.set(
                key,
                value=persons,
            )
        return persons

    async def full_text_search(
            self,
            query: str,
            page_num: int = 1,
            page_size: int = 50,
    ) -> Optional[Person]:
        """Search for a persons by query. """
        logging.debug('Get doc from elastic')

        key = self.cache.gen_cache_key(
            query=query,
            page_num=page_num,
            page_size=page_size,
        )
        persons = await self.cache.get(key)
        if not persons:
            fields = ['name']
            persons, total_count = await self.searcher.full_text_search(
                query=query,
                fields=fields,
                from_=page_size * (page_num - 1),
                size=page_size,
            )
            if not persons:
                return None
            for person in persons:
                person['role'] = await self._get_roles(person['uuid'])

            persons = await self.person_paginator.paginate(persons, page_num, page_size, total_count)

            await self.cache.set(key, persons)
        return persons

    async def _get_roles(self, person_id):
        roles = {}
        for role in ActedIn.__fields__.keys():
            roles[role] = await self._get_movies_by_role(role=f"{role}s", person_id=person_id)
        return roles

    async def get_movies(
            self,
            person_id: str,
            page_num: int = 1,
            page_size: int = 50,
    ) -> Movies:
        """Return person movies by person_id from source."""
        logging.debug('Get doc from elastic')

        key = self.cache.gen_cache_key(
            uuid=person_id,
            page_num=page_num,
            page_size=page_size,
        )

        movies = await self.cache.get(key)
        if not movies:
            fields = [f"{role}s.uuid" for role in ActedIn.__fields__.keys()]
            movies, total_count = await self.movie_searcher.exact_search_in_many_fields(
                fields=fields,
                value=person_id,
                from_=page_size * (page_num - 1),
                size=page_size,
                sort=SortModel(field='imdb_rating', order='desc')
            )
            if not movies:
                return None

            movies = await self.movie_paginator.paginate(movies, page_num, page_size, total_count)

            await self.cache.set(key, movies)

        return movies

    async def _get_movies_by_role(self, role: str, person_id: str):
        films, _ = await self.movie_searcher.exact_search_in_one_field(
            _source=False,
            value=person_id,
            field=f'{role}.uuid',
            from_=0,
            size=50,
            sort=SortModel(field='imdb_rating', order='desc')
        )
        return films


@ lru_cache()
def get_person_service(
    cache: AsyncCacheStorage = Depends(get_cache),
    search_engine: AsyncSearchEngine = Depends(get_search_engine),
    search_adapter: AsyncSearchEngine = Depends(get_search_adapter),
) -> PersonService:

    return PersonService(
        cache,
        search_engine,
        search_adapter,
        settings.persons.index_name,
        settings.movies.index_name
    )
