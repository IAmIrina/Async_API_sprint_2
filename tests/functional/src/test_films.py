"""Film  API endpoint tests."""
import json
import pytest
from testdata import schemas
from http import HTTPStatus

ENDPOINT = '/films'


@pytest.mark.asyncio
async def test_get_by_uuid(make_get_request, test_films, clean_cache):
    """Get film by UUID."""
    uuid = test_films[3]['uuid']
    expected = schemas.Film(**test_films[3]).dict()
    response = await make_get_request(ENDPOINT + '/' + uuid)
    assert response.status == HTTPStatus.OK
    assert response.body == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("page_num, page_size",
                         [
                             (-1, 3),
                             (4, -2),
                             (-4, -2),
                         ]
                         )
async def test_page_validation(page_num, page_size, make_get_request, test_films, clean_cache):
    """Failed validation."""

    params = {
        'page[number]': page_num,
        'page[size]': page_size,
    }
    response_es = await make_get_request(ENDPOINT, params=params)

    assert response_es.status == 422


@pytest.mark.asyncio
async def test_sort_validation(make_get_request, test_films, clean_cache):
    """Failed validation."""

    params = {
        'sort': 'does_not_exist',
    }
    response_es = await make_get_request(ENDPOINT, params=params)

    assert response_es.status == 422


@pytest.mark.asyncio
async def test_uuid_doesnt_exists(make_get_request, test_films, clean_cache):
    """GET film by UUID, if it doen't exist."""
    uuid = "Does_not_exist"
    response = await make_get_request(ENDPOINT + '/' + uuid)
    assert response.status == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
@pytest.mark.parametrize("sort,asc",
                         [
                             ('-imdb_rating', True),
                             ('imdb_rating', False),
                         ]
                         )
async def test_get_all_sort(sort, asc, make_get_request, test_films, clean_cache):
    """Get ALL. Sort."""
    expected = schemas.Films(
        total_pages=1,
        page_num=1,
        page_size=50,
        data=sorted(test_films, key=lambda d: d['imdb_rating'], reverse=asc)
    ).dict()
    response = await make_get_request(
        ENDPOINT,
        params={
            'sort': sort,
        }
    )
    assert response.status == HTTPStatus.OK
    assert response.body['total_pages'] == expected['total_pages']
    assert response.body['page_num'] == expected['page_num']
    assert response.body['page_size'] == expected['page_size']
    assert len(response.body['data']) == len(expected['data'])
    assert response.body['data'] == expected['data']


@pytest.mark.asyncio
async def test_pagination(make_get_request, test_films, clean_cache):
    """Pagination. Get page number N."""

    expected = schemas.Films(
        total_pages=5,
        page_num=3,
        page_size=2,
        data=sorted(test_films, key=lambda d: d['imdb_rating'], reverse=True)[4:6]
    ).dict()

    response = await make_get_request(
        ENDPOINT,
        params={
            'page[number]': expected['page_num'],
            'page[size]': expected['page_size'],
        }
    )

    assert response.status == HTTPStatus.OK
    assert response.body['total_pages'] == expected['total_pages']
    assert response.body['page_num'] == expected['page_num']
    assert response.body['page_size'] == expected['page_size']
    assert len(response.body['data']) == len(expected['data'])
    assert response.body['data'] == expected['data']


@pytest.mark.asyncio
async def test_filter_genre(make_get_request, test_films, clean_cache):
    """Filter by genre."""
    genre_uuid = '6a0a479b-cfec-41ac-b520-41b2b007b611'
    expected = list(
        filter(lambda item: any(genre['uuid'] == genre_uuid for genre in item['genre']), test_films)
    )
    expected = sorted(expected, key=lambda d: d['imdb_rating'], reverse=True)

    response = await make_get_request(
        ENDPOINT,
        params={
            'filter[genre]': genre_uuid
        }
    )
    assert response.status == HTTPStatus.OK
    assert len(response.body['data']) == len(expected)


@pytest.mark.asyncio
async def test_filter_genre_doesnt_exist(make_get_request, test_films, clean_cache):
    """Filter by genre."""
    genre_uuid = 'does_not_exist'

    response = await make_get_request(
        ENDPOINT,
        params={
            'filter[genre]': genre_uuid
        }
    )
    assert response.status == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
@pytest.mark.parametrize("page_num, page_size",
                         [
                             (2, 3),
                             (4, 100),
                         ]
                         )
async def test_cache(page_num, page_size, make_get_request, test_films, clean_cache):
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
                             ('Empire', HTTPStatus.OK, 1),
                             ('Obi', HTTPStatus.OK, 4),
                             ('Sttar', HTTPStatus.OK, 10),
                             ('NotEXIST', HTTPStatus.NOT_FOUND, 0),
                         ]
                         )
async def test_full_search(query, code, count, make_get_request, test_films, clean_cache):
    """Full Text search."""
    params = {
        'query': query
    }
    response = await make_get_request(ENDPOINT + '/search', params=params)

    assert response.status == code
    if code == HTTPStatus.OK:
        assert len(response.body['data']) == count


@pytest.mark.asyncio
async def test_get_from_redis(make_get_request, test_films, clean_cache):
    """Cache. Compare with cached Redis Data."""

    expected = schemas.Film(**test_films[1]).dict()
    uuid = expected['uuid']
    response = await make_get_request(ENDPOINT + '/' + uuid)

    from_cache = await clean_cache.get(f'movies::uuid::{uuid}')

    cache = json.loads(from_cache)
    if cache:
        cache = schemas.Film(**cache)

    assert response.status == HTTPStatus.OK
    assert cache == expected
