"""Film views."""

from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic, ESSearcher
from db.redis import get_redis, RedisCache
from core.pagination import Paginator

from models.film import Film, Films
from models.custom_models import SortModel
from core.config import settings


class FilmService:

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch, index: str):
        self.cache = RedisCache(redis, index)

        self.paginator = Paginator(Films)

        self.searcher = ESSearcher(elastic, index)

    async def get_document(self, uuid: str) -> Optional[Film]:
        key = self.cache.gen_cache_key(uuid=uuid)
        film = await self.cache.get(key)
        if not film:
            film = await self.searcher.fetch_one(uuid=uuid)
            if not film:
                return None
            film = Film(**film)
            await self.cache.put(key, film)
        return film

    async def get_page(
            self,
            page_num: int,
            page_size: int,
            sort: SortModel = None,
            filter: str = None,
    ) -> Optional[Films]:
        """Return all films from source."""
        key = self.cache.gen_cache_key(
            page_num=page_num,
            page_size=page_size,
            sort=sort.field if sort else None,
            sort_order=sort.order if sort else None,
            filter=filter,
        )
        films = await self.cache.get(key)

        if not films:
            if filter:
                films, total_count = await self.searcher.exact_search_in_one_field(
                    value=filter,
                    field='genre.uuid',
                    from_=page_size * (page_num - 1),
                    size=page_size,
                    sort=sort,
                )
            else:
                films, total_count = await self.searcher.fetch_all(
                    from_=page_size * (page_num - 1),
                    size=page_size,
                    sort=sort,
                )
            if not films:
                return None
            films = await self.paginator.paginate(films, page_num, page_size, total_count)

            await self.cache.put(key, films)

        return films

    async def full_text_search(self, page_num: int, page_size: int, query: str) -> Optional[Film]:
        """Search films by fields."""

        key = self.cache.gen_cache_key(
            query=query,
            page_num=page_num,
            page_size=page_size,
        )
        films = await self.cache.get(key)

        if not films:
            fields = [
                "actors_names",
                "writers_names",
                "director",
                "title",
                "description",
                "genre"
            ]

            films, total_count = await self.searcher.full_text_search(
                query=query,
                fields=fields,
                from_=page_size * (page_num - 1),
                size=page_size,
            )

            if not films:
                return None
            films = await self.paginator.paginate(films, page_num, page_size, total_count)
            await self.cache.put(key, films)

        return films


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic, settings.movies.index_name)
