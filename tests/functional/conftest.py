from typing import Optional
import aiohttp
import aioredis
import asyncio
from dataclasses import dataclass
from elasticsearch import AsyncElasticsearch
from multidict import CIMultiDictProxy
import pytest_asyncio

from settings import test_settings


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Override Event_loop for Session scope."""
    return asyncio.get_event_loop()


@pytest_asyncio.fixture()
async def clean_cache():
    """Flush Redis DB."""
    redis = aioredis.from_url(
        f"redis://{test_settings.redis.host}:{test_settings.redis.port}",
        password=test_settings.redis.password
    )
    await redis.flushdb()
    yield redis
    await redis.close()


@pytest_asyncio.fixture(scope="session")
async def es_client():
    """ES connection."""
    client = AsyncElasticsearch(hosts=[f'http://{test_settings.elastic.host}:{test_settings.elastic.port}'])
    yield client
    await client.close()


@pytest_asyncio.fixture(scope="session")
async def session():
    """AIOHTTP session."""
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture(scope="session")
def make_get_request(session):
    """Make HTTP request with AIOHTTP session."""
    async def inner(method: str, params: Optional[dict] = {}) -> HTTPResponse:
        url = test_settings.api_url + method
        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )
    return inner
