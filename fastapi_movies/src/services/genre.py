"""Genre views."""

from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from db.elastic import ESSearcher, get_elastic
from db.redis import get_redis, RedisCache
from core.pagination import Paginator
from models.custom_models import SortModel

from models.genre import Genre, Genres
from core.config import settings


class GenreService:
    """Handle source genre data."""

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch, index: str):
        self.cache = RedisCache(redis, index)

        self.paginator = Paginator(Genres)

        self.searcher = ESSearcher(elastic, index)

    async def get_document(self, uuid: str) -> Optional[Genre]:
        """Return genre by id from source."""
        key = self.cache.gen_cache_key(uuid=uuid)
        genre = await self.cache.get(key)

        if not genre:
            genre = await self.searcher.fetch_one(uuid=uuid)
            if not genre:
                return None
            genre = Genre(**genre)

            await self.cache.put(key, genre)
        return genre

    async def get_page(self, page_num: int, page_size: int) -> Optional[Genres]:
        """Return all genres from source."""
        key = self.cache.gen_cache_key(
            page_num=page_num,
            page_size=page_size,
        )
        genres = await self.cache.get(key)

        if not genres:
            genres, total_count = await self.searcher.fetch_all(
                from_=page_size * (page_num - 1),
                size=page_size,
                sort=SortModel(field='name', order='asc'),
            )
            if not genres:
                return None

            genres = await self.paginator.paginate(genres, page_num, page_size, total_count)

            await self.cache.put(key, genres)
        return genres


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:

    return GenreService(redis, elastic, settings.genres.index_name)
