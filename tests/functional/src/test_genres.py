"""Genre  API endpoint tests."""
import json
from http import HTTPStatus

import pytest
from testdata import schemas

ENDPOINT = '/genres'


@pytest.mark.asyncio
async def test_get_by_uuid(make_get_request, test_genres, clean_cache):
    """Get genre by UUID."""
    uuid = test_genres[1]['uuid']
    expected = schemas.Genre(**test_genres[1]).dict()
    response = await make_get_request(ENDPOINT + '/' + uuid)
    assert response.status == HTTPStatus.OK
    assert response.body == expected


@pytest.mark.asyncio
async def test_uuid_doesnt_exists(make_get_request, test_genres, clean_cache):
    """GET genre by UUID, if it doen't exist."""
    uuid = "Does_not_exist"
    response = await make_get_request(ENDPOINT + '/' + uuid)
    assert response.status == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_get_all_sort(make_get_request, test_genres, clean_cache):
    """Get ALL."""
    expected = schemas.Genres(
        total_pages=1,
        page_num=1,
        page_size=50,
        data=sorted(test_genres, key=lambda d: d['name'])
    ).dict()
    response = await make_get_request(ENDPOINT,)
    assert response.status == HTTPStatus.OK
    assert response.body['total_pages'] == expected['total_pages']
    assert response.body['page_num'] == expected['page_num']
    assert response.body['page_size'] == expected['page_size']
    assert len(response.body['data']) == len(expected['data'])
    assert response.body['data'] == expected['data']


@ pytest.mark.asyncio
async def test_pagination(make_get_request, test_genres, clean_cache):
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

    assert response.status == HTTPStatus.OK
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
async def test_cache(page_num, page_size, make_get_request, test_genres, clean_cache):
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
async def test_get_from_redis(make_get_request, test_genres, clean_cache):
    """Cache. Compare with cached Redis Data."""

    expected = schemas.Genre(**test_genres[1]).dict()
    uuid = expected['uuid']
    response = await make_get_request(ENDPOINT + '/' + uuid)

    from_cache = await clean_cache.get(f'genres::uuid::{uuid}')

    cache = json.loads(from_cache)
    cache = schemas.Genre(**cache)

    assert response.status == HTTPStatus.OK
    assert cache == expected
