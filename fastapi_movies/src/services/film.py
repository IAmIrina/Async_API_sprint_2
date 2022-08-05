"""Film views."""

from functools import lru_cache
from typing import Optional

from fastapi import Depends


from db.search import AsyncSearchEngine, BaseSearchAdapter, get_search_engine
from db.elastic import get_search_adapter
from db.cache import get_cache, Cache, AsyncCacheStorage
from core.pagination import Paginator

from models.film import Film, Films
from models.custom_models import SortModel
from core.config import settings


class FilmService:

    def __init__(self,
                 cache_storage: AsyncCacheStorage,
                 search_engine: AsyncSearchEngine,
                 search_adapter: BaseSearchAdapter,
                 index: str):
        self.cache = Cache(cache_storage, index)

        self.paginator = Paginator(Films)

        self.searcher = search_adapter(search_engine, index)

    async def get_document(self, uuid: str) -> Optional[Film]:
        key = self.cache.gen_cache_key(uuid=uuid)
        film = await self.cache.get(key)
        if not film:
            film = await self.searcher.fetch_one(uuid=uuid)
            if not film:
                return None
            film = Film(**film)
            await self.cache.set(key, film)
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

            await self.cache.set(key, films)

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
            await self.cache.set(key, films)

        return films


@lru_cache()
def get_film_service(
        cache: AsyncCacheStorage = Depends(get_cache),
        search_engine: AsyncSearchEngine = Depends(get_search_engine),
        search_adapter: AsyncSearchEngine = Depends(get_search_adapter),
) -> FilmService:
    return FilmService(cache, search_engine, search_adapter, settings.movies.index_name)
