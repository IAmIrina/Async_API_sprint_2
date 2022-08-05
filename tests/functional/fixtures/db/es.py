
"""Elastic fixtures."""

from elasticsearch import AsyncElasticsearch
import pytest_asyncio

from settings import test_settings


@pytest_asyncio.fixture(scope="session")
async def es_client():
    """ES connection."""
    client = AsyncElasticsearch(hosts=[f'http://{test_settings.elastic.host}:{test_settings.elastic.port}'])
    yield client
    await client.close()
