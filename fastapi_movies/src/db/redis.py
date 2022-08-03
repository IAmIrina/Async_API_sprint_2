"""Implement Redis Cache."""
from abc import ABC, abstractmethod
from functools import lru_cache

import orjson
import logging

from typing import Any, Optional
from aioredis import Redis
from core.config import settings

CACHE_EXPIRE_IN_SECONDS = settings.cache_expire_in_seconds

redis: Optional[Redis] = None


async def get_redis() -> Redis:
    return redis


class BaseCache(ABC):
    @abstractmethod
    async def gen_cache_key(self, **kwargs):
        pass

    @abstractmethod
    async def get(self, key):
        pass

    @abstractmethod
    async def put(self, key, value):
        pass


class RedisCache(BaseCache):
    """Implement cache storage interface."""

    def __init__(self, redis, index):
        """Generate a name for key.
        Args:
            index: Name elastic index.
            redis: Redis pool.
        """
        self.redis = redis
        self.index = index

    @lru_cache()
    def gen_cache_key(self, **kwargs) -> str:
        """Generate a name for key.

        Args:
            index: Name es index.
            kwargs: Uses key/value to generate key string.

        Returs:
            str: Redis key name.
        """
        kwargs = dict(sorted(kwargs.items()))
        key_strings = [self.index]
        for key, value in kwargs.items():
            key_strings.append(f"{key}::{value}")
        return '::'.join(key_strings)

    async def get(self, key) -> Any:
        """Get data from Redis.

        Args:
            kwargs: Key/value to calculate Redis key name.

        Returns:
            Any: Any data from redis storage gotten by key name.

        """
        try:
            data = await self.redis.get(key)
        except BaseException:
            logging.exception('REDIS GET DATA ERROR')
            data = None
        if not data:
            logging.debug('No data in cache')
            return None
        logging.debug('Get data from cache done')
        return orjson.loads(data)

    async def put(self, key, value):
        """Save data to Redis.

        Args:
            value: The value will be saved to Redis Cache.
            kwargs: Key/value to calculate Redis key name.
        """
        try:
            await self.redis.set(key, value.json(), expire=CACHE_EXPIRE_IN_SECONDS)
        except BaseException:
            logging.exception('REDIS SET DATA ERROR')
        logging.debug('Success to Put data to cache')
