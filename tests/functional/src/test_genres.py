"""Genre  API endpoint tests."""
import json
import pytest
import pytest_asyncio
from testdata import es_genres, es_schema, schemas
from utils.converters import to_es_bulk_format

ENDPOINT = '/genres'


@pytest_asyncio.fixture(scope="module")
async def es_documents(es_client):
    """Fixture to manage elastic index."""

    await es_client.indices.create(
        index=es_schema.genres['index_name'],
        body=es_schema.genres['schema'],
        ignore=[400, 404]
    )

    await es_client.bulk(
        index=es_schema.genres['index_name'],
        body=await to_es_bulk_format(es_schema.genres['index_name'], es_genres.documents),
        refresh='wait_for',
    )
    yield es_genres.documents

    await es_client.indices.delete(index=es_schema.genres['index_name'], ignore=[400, 404])


@pytest.mark.asyncio
async def test_get_by_uuid(make_get_request, es_documents, clean_cache):
    """Get genre by UUID."""
    uuid = es_documents[1]['uuid']
    expected = schemas.Genre(**es_documents[1]).dict()
    response = await make_get_request(ENDPOINT + '/' + uuid)
    assert response.status == 200
    assert response.body == expected


@pytest.mark.asyncio
async def test_uuid_doesnt_exists(make_get_request, es_documents, clean_cache):
    """GET genre by UUID, if it doen't exist."""
    uuid = "Does_not_exist"
    response = await make_get_request(ENDPOINT + '/' + uuid)
    assert response.status == 404


@pytest.mark.asyncio
async def test_get_all_sort(make_get_request, es_documents, clean_cache):
    """Get ALL."""
    expected = schemas.Genres(
        total_pages=1,
        page_num=1,
        page_size=50,
        data=sorted(es_documents, key=lambda d: d['name'])
    ).dict()
    response = await make_get_request(ENDPOINT,)
    assert response.status == 200
    assert response.body['total_pages'] == expected['total_pages']
    assert response.body['page_num'] == expected['page_num']
    assert response.body['page_size'] == expected['page_size']
    assert len(response.body['data']) == len(expected['data'])
    assert response.body['data'] == expected['data']


@ pytest.mark.asyncio
async def test_pagination(make_get_request, es_documents, clean_cache):
    """Pagination. Get page number N."""
    total_pages = 3
    page_num = 2
    page_size = 1
    count = 1
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
    assert len(response.body['data']) == count


@ pytest.mark.asyncio
@ pytest.mark.parametrize("page_num, page_size",
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
async def test_get_from_redis(make_get_request, es_documents, clean_cache):
    """Cache. Compare with cached Redis Data."""

    expected = schemas.Genre(**es_documents[1]).dict()
    uuid = expected['uuid']
    response = await make_get_request(ENDPOINT + '/' + uuid)

    from_cache = await clean_cache.get(f'genres::uuid::{uuid}')

    cache = json.loads(from_cache)
    cache = schemas.Genre(**cache)

    assert response.status == 200
    assert cache == expected
