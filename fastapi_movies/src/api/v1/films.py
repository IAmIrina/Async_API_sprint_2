"""Route films."""
from enum import Enum
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query

from core.messages import FILM_NOT_FOUND
from models.custom_models import PaginateParams, SortModel
from models.film import Film, Films
from services.film import FilmService, get_film_service

router = APIRouter()


class SortingImdbRating(str, Enum):
    desc = "-imdb_rating"
    asc = "imdb_rating"


@router.get('/',
            response_model=Films,
            summary="Get movies.",
            description="Return list of films, filter by genre can be used.")
async def films(
    film_service: FilmService = Depends(get_film_service),
    sort: SortingImdbRating = Query(default=SortingImdbRating.desc,
                                    description='IMDB rating sort.'),
    paginated_params: PaginateParams = Depends(),
    filter: str = Query(
        default=None,
        alias='filter[genre]',
        description='Use genre uuid.'),

) -> Films:
    if sort.__dict__['_name_']:
        sort = SortModel(field='imdb_rating', order=sort.__dict__['_name_'])
    else:
        sort = None
    films = await film_service.get_page(paginated_params.page_num, paginated_params.page_size, sort, filter)

    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=FILM_NOT_FOUND)
    return films


@router.get('/search', response_model=Films, summary='Full text search.', description='Use query for full text search.')
async def films_search(
    query: str,
    paginated_params: PaginateParams = Depends(),
    film_service: FilmService = Depends(get_film_service),
) -> Films:
    films = await film_service.full_text_search(paginated_params.page_num, paginated_params.page_size, query)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=FILM_NOT_FOUND)

    return films


@router.get('/{film_id}', response_model=Film, summary='Get movie by uuid', description='Return movie details.')
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> Film:
    film = await film_service.get_document(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=FILM_NOT_FOUND)
    return film
