from typing import Optional
import aiohttp
import asyncio
from dataclasses import dataclass
from multidict import CIMultiDictProxy
import pytest_asyncio

from settings import test_settings

pytest_plugins = [
    "fixtures.db.es",
    "fixtures.db.cache",
    "fixtures.endpoints.films",
    "fixtures.endpoints.genres",
    "fixtures.endpoints.persons"
]


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Override Event_loop for Session scope."""
    return asyncio.get_event_loop()


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
