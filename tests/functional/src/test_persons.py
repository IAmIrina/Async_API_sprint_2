"""Persons API endpoint tests."""
import json
from http import HTTPStatus

import pytest
from testdata import schemas

ENDPOINT = '/persons'
ROLES = ('directors', 'actors', 'writers')


@pytest.mark.asyncio
async def test_get_by_uuid(make_get_request, test_persons, clean_cache):
    """Get person by UUID."""
    expected = test_persons[0]
    uuid = expected['uuid']
    response = await make_get_request(ENDPOINT + '/' + uuid)
    for role in schemas.ActedIn.__fields__.keys():
        response.body['role'][role].sort()
    assert response.status == HTTPStatus.OK
    assert response.body['uuid'] == expected['uuid']
    assert response.body['name'] == expected['name']
    assert response.body['role']['writer'] == expected['role']['writer']
    assert response.body['role']['director'] == expected['role']['director']
    assert response.body['role']['actor'] == expected['role']['actor']


@ pytest.mark.asyncio
async def test_uuid_doesnt_exists(make_get_request, test_persons, clean_cache):
    """GET person by UUID, if it doen't exist."""
    uuid = "Does_not_exist"
    response = await make_get_request(f"{ENDPOINT}/{uuid}")
    assert response.status == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
@pytest.mark.parametrize("page_num, page_size",
                         [
                             (-1, 3),
                             (4, -2),
                             (-4, -2),
                         ]
                         )
async def test_page_validation(page_num, page_size, make_get_request, test_persons, clean_cache):
    """Failed validation."""

    params = {
        'page[number]': page_num,
        'page[size]': page_size,
    }
    response_es = await make_get_request(ENDPOINT, params=params)

    assert response_es.status == HTTPStatus.UNPROCESSABLE_ENTITY


@ pytest.mark.asyncio
async def test_get_all(make_get_request, test_persons, clean_cache):
    """Get ALL."""
    response = await make_get_request(ENDPOINT)
    assert response.status == HTTPStatus.OK
    assert response.body['total_pages'] == 1
    assert response.body['page_num'] == 1
    assert response.body['page_size'] == 50
    assert len(response.body['data']) == len(test_persons)


@pytest.mark.asyncio
async def test_pagination(make_get_request, test_persons, clean_cache):
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

    assert response.status == HTTPStatus.OK
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
async def test_cache(page_num, page_size, make_get_request, test_persons, clean_cache):
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
                             ('Luc', HTTPStatus.OK, 5),
                             ('NotEXIST', HTTPStatus.NOT_FOUND, 0),
                         ]
                         )
async def test_full_search(query, code, count, make_get_request, test_persons, clean_cache):
    """Full Text search."""
    params = {
        'query': query
    }
    response = await make_get_request(ENDPOINT + '/search', params=params)

    assert response.status == code
    if code == HTTPStatus.OK:
        assert len(response.body['data']) == count


@pytest.mark.asyncio
async def test_person_film(make_get_request, test_persons, clean_cache):
    """List of movies where the person acted."""
    uuid = 'a5a8f573-3cee-4ccc-8a2b-91cb9f55250a'
    response = await make_get_request(ENDPOINT + '/' + uuid + '/film')

    assert response.status == HTTPStatus.OK
    assert len(response.body['data']) == 4
    movie = response.body['data'][0]
    assert movie['uuid'] == 'b503ced6-fff1-493a-ad41-73449b55ffee'
    assert movie['title'] == 'Star Wars: The Clone Wars'
    assert movie['imdb_rating'] == 8.2


@pytest.mark.asyncio
async def test_person_no_film(make_get_request, test_persons, clean_cache):
    """List of movies of person if person have no movies."""
    uuid = 'ae0113af-2b40-4578-a530-060be491d567a'
    response = await make_get_request(ENDPOINT + '/' + uuid + '/film')
    assert response.status == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_get_from_redis(make_get_request, test_persons, clean_cache):
    """Cache. Compare with cached Redis Data."""

    expected = schemas.Person(**test_persons[1]).dict()
    uuid = expected['uuid']
    response = await make_get_request(ENDPOINT + '/' + uuid)

    from_cache = await clean_cache.get(f'persons::uuid::{uuid}')

    cache = json.loads(from_cache)
    if cache:
        cache = schemas.Person(**cache)

    assert response.status == HTTPStatus.OK
    assert cache == expected
