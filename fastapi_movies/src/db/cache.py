"""Implement Cache."""
from abc import ABC, abstractmethod
from functools import lru_cache

import orjson
import logging

from typing import Any, Optional
from core.config import settings

CACHE_EXPIRE_IN_SECONDS = settings.cache_expire_in_seconds


class AsyncCacheStorage(ABC):
    @abstractmethod
    async def get(self, key: str, **kwargs):
        pass

    @abstractmethod
    async def set(self, key: str, value: str, expire: int, **kwargs):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    async def wait_closed(self):
        pass


cache: Optional[AsyncCacheStorage] = None


async def get_cache() -> AsyncCacheStorage:
    return cache


class BaseCache(ABC):
    @abstractmethod
    async def gen_cache_key(self, **kwargs):
        pass

    @abstractmethod
    async def get(self, key):
        pass

    @abstractmethod
    async def set(self, key, value):
        pass


class Cache(BaseCache):
    """Implement cache storage interface."""

    def __init__(self, cache: AsyncCacheStorage, index: str):
        """Generate a name for key.
        Args:
            index: Name index.
            Cache: AsyncCacheStorage.
        """
        self.cache = cache
        self.index = index

    @lru_cache()
    def gen_cache_key(self, **kwargs) -> str:
        """Generate a name for key.

        Args:
            index: Name es index.
            kwargs: Uses key/value to generate key string.

        Returs:
            str: Cache key name.
        """
        kwargs = dict(sorted(kwargs.items()))
        key_strings = [self.index]
        for key, value in kwargs.items():
            key_strings.append(f"{key}::{value}")
        return '::'.join(key_strings)

    async def get(self, key) -> Any:
        """Get data from Cache.

        Args:
            kwargs: Key/value to calculate Cache key name.

        Returns:
            Any: Any data from cache gotten by key name.

        """
        try:
            data = await self.cache.get(key)
        except BaseException:
            logging.exception('Cache GET DATA ERROR')
            data = None
        if not data:
            logging.debug('No data in cache')
            return None
        logging.debug('Get data from cache done')
        return orjson.loads(data)

    async def set(self, key, value):
        """Save data to Cache.

        Args:
            value: The value will be saved to Cache.
            kwargs: Key/value to calculate Cache key name.
        """
        try:
            await self.cache.set(key, value.json(), expire=CACHE_EXPIRE_IN_SECONDS)
        except BaseException:
            logging.exception('CACHE SET DATA ERROR')
        logging.debug('Success to Put data to cache')
