"""Persons API endpoint fictures."""
from http import HTTPStatus
from typing import List

import pytest_asyncio
from testdata import es_persons, es_schema, schemas
from utils.converters import to_es_bulk_format


@pytest_asyncio.fixture(scope="module")
async def indexed_persons(es_client) -> None:
    """Fixture to manage elastic person index."""

    await es_client.indices.create(
        index=es_schema.persons['index_name'],
        body=es_schema.persons['schema'],
        ignore=[HTTPStatus.BAD_REQUEST, HTTPStatus.NOT_FOUND]
    )

    await es_client.bulk(
        index=es_schema.persons['index_name'],
        body=await to_es_bulk_format(es_schema.persons['index_name'], es_persons.documents),
        refresh='wait_for',
    )
    yield es_persons.documents

    await es_client.indices.delete(
        index=es_schema.persons['index_name'],
        ignore=[HTTPStatus.BAD_REQUEST, HTTPStatus.NOT_FOUND]
    )


@pytest_asyncio.fixture(scope="module")
async def test_persons(test_films, indexed_persons) -> None:
    """Fixture to manage elastic movies index."""
    async def get_movies_by_role(uuid: str, role: str) -> List[str]:
        movies = filter(
            lambda doc: any(person['uuid'] == uuid for person in doc[role]),
            test_films
        )
        return list(movie['uuid'] for movie in movies)

    for person in indexed_persons:
        person['role'] = {}
        for role in schemas.ActedIn.__fields__.keys():
            person['role'][role] = await get_movies_by_role(person['uuid'], f"{role}s")
            person['role'][role].sort()
    return indexed_persons
