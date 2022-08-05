"""Genre views."""

from functools import lru_cache
from typing import Optional

from fastapi import Depends

from core.config import settings
from core.pagination import Paginator
from db.cache import AsyncCacheStorage, Cache, get_cache
from db.elastic import get_search_adapter
from db.search import AsyncSearchEngine, BaseSearchAdapter, get_search_engine
from models.custom_models import SortModel
from models.genre import Genre, Genres


class GenreService:
    """Handle source genre data."""

    def __init__(self,
                 cache_storage: AsyncCacheStorage,
                 search_engine: AsyncSearchEngine,
                 search_adapter: BaseSearchAdapter,
                 index: str):
        self.cache = Cache(cache_storage, index)

        self.paginator = Paginator(Genres)

        self.searcher = search_adapter(search_engine, index)

    async def get_document(self, uuid: str) -> Optional[Genre]:
        """Return genre by id from source."""
        key = self.cache.gen_cache_key(uuid=uuid)
        genre = await self.cache.get(key)

        if not genre:
            genre = await self.searcher.fetch_one(uuid=uuid)
            if not genre:
                return None
            genre = Genre(**genre)

            await self.cache.set(key, genre)
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

            await self.cache.set(key, genres)
        return genres


@lru_cache()
def get_genre_service(
    cache: AsyncCacheStorage = Depends(get_cache),
    search_engine: AsyncSearchEngine = Depends(get_search_engine),
    search_adapter: AsyncSearchEngine = Depends(get_search_adapter),
) -> GenreService:
    return GenreService(cache, search_engine, search_adapter, settings.genres.index_name)
