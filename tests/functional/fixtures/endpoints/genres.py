"""Genres  API endpoint fixtures."""
import pytest_asyncio
from testdata import es_genres, es_schema
from utils.converters import to_es_bulk_format
from http import HTTPStatus

ENDPOINT = '/genres'


@pytest_asyncio.fixture(scope="module")
async def test_genres(es_client):
    """Fixture to manage elastic index."""

    await es_client.indices.create(
        index=es_schema.genres['index_name'],
        body=es_schema.genres['schema'],
        ignore=[HTTPStatus.BAD_REQUEST, HTTPStatus.NOT_FOUND]
    )

    await es_client.bulk(
        index=es_schema.genres['index_name'],
        body=await to_es_bulk_format(es_schema.genres['index_name'], es_genres.documents),
        refresh='wait_for',
    )
    yield es_genres.documents

    await es_client.indices.delete(
        index=es_schema.genres['index_name'],
        ignore=[HTTPStatus.BAD_REQUEST, HTTPStatus.NOT_FOUND]
    )
