"""Abstract AsyncSearchEngine and BaseSearchAdapter classes"""
from typing import Optional, List, Tuple
from abc import ABC, abstractmethod
from models.custom_models import SortModel


class AsyncSearchEngine(ABC):
    @abstractmethod
    async def get(self, index=str, id=str):
        pass

    @abstractmethod
    async def search(self, index=str, **kwargs):
        pass

    @abstractmethod
    async def close(self):
        pass


class BaseSearchAdapter(ABC):
    @abstractmethod
    async def fetch_one(self, uuid: str) -> dict:
        pass

    @abstractmethod
    async def fetch_all(
        self,
        from_: int = 0,
        size: int = 20,
        sort: SortModel = None,
    ) -> Tuple[List[dict], int]:
        pass

    @abstractmethod
    async def full_text_search(
        self,
        query: dict,
        fields: List[str],
        from_: int = 0,
        size: int = 20,
    ) -> Tuple[List[dict], int]:
        pass

    @abstractmethod
    async def exact_search_in_one_field(
        self,
        value: dict,
        field: List[str],
        from_: int = 0,
        size: int = 20,
        sort: SortModel = None,
        _source: bool = True,
    ) -> Tuple[List[dict], int]:
        pass

    @abstractmethod
    async def exact_search_in_many_fields(
        self,
        value: dict,
        fields: List[str],
        from_: int = 0,
        size: int = 20,
        sort: SortModel = None,
        _source: bool = True,
    ) -> Tuple[List[dict], int]:
        pass


searcher: Optional[AsyncSearchEngine] = None


async def get_search_engine() -> AsyncSearchEngine:
    """Return AsyncSearchEngine client."""
    return searcher
