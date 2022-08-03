"""Person  API endpoint tests."""
import json
from typing import List
import pytest
import pytest_asyncio
from testdata import es_persons, es_schema, schemas, es_movies
from utils.converters import to_es_bulk_format

ENDPOINT = '/persons'
ROLES = ('directors', 'actors', 'writers')


@pytest_asyncio.fixture(scope="module")
async def indexed_persons(es_client) -> None:
    """Fixture to manage elastic person index."""

    await es_client.indices.create(
        index=es_schema.persons['index_name'],
        body=es_schema.persons['schema'],
        ignore=[400, 404]
    )

    await es_client.bulk(
        index=es_schema.persons['index_name'],
        body=await to_es_bulk_format(es_schema.persons['index_name'], es_persons.documents),
        refresh='wait_for',
    )
    yield es_persons.documents

    await es_client.indices.delete(index=es_schema.persons['index_name'], ignore=[400, 404])


@pytest_asyncio.fixture(scope="module")
async def indexed_movies(es_client) -> None:
    """Fixture to manage elastic movies index."""

    await es_client.indices.create(
        index=es_schema.movies['index_name'],
        body=es_schema.movies['schema'],
        ignore=[400, 404]
    )

    await es_client.bulk(
        index=es_schema.movies['index_name'],
        body=await to_es_bulk_format(es_schema.movies['index_name'], es_movies.documents),
        refresh='wait_for',
    )
    yield es_movies.documents

    await es_client.indices.delete(index=es_schema.movies['index_name'], ignore=[400, 404])


@pytest_asyncio.fixture(scope="module")
async def es_documents(indexed_movies, indexed_persons) -> None:
    """Fixture to manage elastic movies index."""
    async def get_movies_by_role(uuid: str, role: str) -> List[str]:
        movies = filter(
            lambda doc: any(person['uuid'] == uuid for person in doc[role]),
            indexed_movies
        )
        return list(movie['uuid'] for movie in movies)

    for person in indexed_persons:
        person['role'] = {}
        for role in schemas.ActedIn.__fields__.keys():
            person['role'][role] = await get_movies_by_role(person['uuid'], f"{role}s")
            person['role'][role].sort()
    return indexed_persons


@pytest.mark.asyncio
async def test_get_by_uuid(make_get_request, es_documents, clean_cache):
    """Get person by UUID."""
    expected = es_documents[0]
    uuid = expected['uuid']
    response = await make_get_request(ENDPOINT + '/' + uuid)
    for role in schemas.ActedIn.__fields__.keys():
        response.body['role'][role].sort()
    assert response.status == 200
    assert response.body['uuid'] == expected['uuid']
    assert response.body['name'] == expected['name']
    assert response.body['role']['writer'] == expected['role']['writer']
    assert response.body['role']['director'] == expected['role']['director']
    assert response.body['role']['actor'] == expected['role']['actor']


@ pytest.mark.asyncio
async def test_uuid_doesnt_exists(make_get_request, es_documents, clean_cache):
    """GET person by UUID, if it doen't exist."""
    uuid = "Does_not_exist"
    response = await make_get_request(ENDPOINT + '/' + uuid)
    assert response.status == 404


@pytest.mark.asyncio
@pytest.mark.parametrize("page_num, page_size",
                         [
                             (-1, 3),
                             (4, -2),
                             (-4, -2),
                         ]
                         )
async def test_page_validation(page_num, page_size, make_get_request, es_documents, clean_cache):
    """Failed validation."""

    params = {
        'page[number]': page_num,
        'page[size]': page_size,
    }
    response_es = await make_get_request(ENDPOINT, params=params)

    assert response_es.status == 422


@ pytest.mark.asyncio
async def test_get_all(make_get_request, es_documents, clean_cache):
    """Get ALL."""
    response = await make_get_request(ENDPOINT)
    assert response.status == 200
    assert response.body['total_pages'] == 1
    assert response.body['page_num'] == 1
    assert response.body['page_size'] == 50
    assert len(response.body['data']) == len(es_documents)


@pytest.mark.asyncio
async def test_pagination(make_get_request, es_documents, clean_cache):
    """Pagination. Get page number N."""

    total_pages = 4
    page_num = 2
    page_size = 2

    response = await make_get_request(
        ENDPOINT,
        params={
            'page[number]': page_num,
            'page[size]': page_size,
        }
    )

    assert response.status == 200
    assert response.body['total_pages'] == total_pages
    assert response.body['page_num'] == page_num
    assert response.body['page_size'] == page_size
    assert len(response.body['data']) == page_size


@pytest.mark.asyncio
@pytest.mark.parametrize("page_num, page_size",
                         [
                             (2, 3),
                             (4, 100),
                         ]
                         )
async def test_cache(page_num, page_size, make_get_request, es_documents, clean_cache):
    """Cache. Get page number N twice."""

    params = {
        'page[number]': page_num,
        'page[size]': page_size,
    }
    response_es = await make_get_request(ENDPOINT, params=params)
    response_cache = await make_get_request(ENDPOINT, params=params)

    assert response_es.status == response_cache.status
    assert response_es == response_cache


@pytest.mark.asyncio
@pytest.mark.parametrize("query, code, count",
                         [
                             ('Luc', 200, 5),
                             ('NotEXIST', 404, 0),
                         ]
                         )
async def test_full_search(query, code, count, make_get_request, es_documents, clean_cache):
    """Full Text search."""
    params = {
        'query': query
    }
    response = await make_get_request(ENDPOINT + '/search', params=params)

    assert response.status == code
    if code == 200:
        assert len(response.body['data']) == count


@pytest.mark.asyncio
async def test_person_film(make_get_request, es_documents, clean_cache):
    """List of movies where the person acted."""
    uuid = 'a5a8f573-3cee-4ccc-8a2b-91cb9f55250a'
    response = await make_get_request(ENDPOINT + '/' + uuid + '/film')

    assert response.status == 200
    assert len(response.body['data']) == 4
    movie = response.body['data'][0]
    assert movie['uuid'] == 'b503ced6-fff1-493a-ad41-73449b55ffee'
    assert movie['title'] == 'Star Wars: The Clone Wars'
    assert movie['imdb_rating'] == 8.2


@pytest.mark.asyncio
async def test_person_no_film(make_get_request, es_documents, clean_cache):
    """List of movies of person if person have no movies."""
    uuid = 'ae0113af-2b40-4578-a530-060be491d567a'
    response = await make_get_request(ENDPOINT + '/' + uuid + '/film')
    assert response.status == 404


@pytest.mark.asyncio
async def test_get_from_redis(make_get_request, es_documents, clean_cache):
    """Cache. Compare with cached Redis Data."""

    expected = schemas.Person(**es_documents[1]).dict()
    uuid = expected['uuid']
    response = await make_get_request(ENDPOINT + '/' + uuid)

    from_cache = await clean_cache.get(f'persons::uuid::{uuid}')

    cache = json.loads(from_cache)
    if cache:
        cache = schemas.Person(**cache)

    assert response.status == 200
    assert cache == expected
