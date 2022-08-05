"""Films  API endpoint fixtures."""
from http import HTTPStatus

import pytest_asyncio
from testdata import es_movies, es_schema
from utils.converters import to_es_bulk_format


@pytest_asyncio.fixture(scope="module")
async def test_films(es_client):
    """Fixture to manage elastic index."""

    await es_client.indices.create(
        index=es_schema.movies['index_name'],
        body=es_schema.movies['schema'],
        ignore=[HTTPStatus.BAD_REQUEST, HTTPStatus.NOT_FOUND]
    )

    await es_client.bulk(
        index=es_schema.movies['index_name'],
        body=await to_es_bulk_format(es_schema.movies['index_name'], es_movies.documents),
        refresh='wait_for',
    )
    yield es_movies.documents

    await es_client.indices.delete(
        index=es_schema.movies['index_name'],
        ignore=[HTTPStatus.BAD_REQUEST, HTTPStatus.NOT_FOUND])
