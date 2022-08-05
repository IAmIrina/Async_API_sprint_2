"""Route persons."""
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from core.messages import PERSON_NOT_FOUND
from models.custom_models import PaginateParams
from models.person import Movies, Person, Persons
from services.person import PersonService, get_person_service

router = APIRouter()


@router.get('/',
            response_model=Persons,
            summary='Get persons.',
            description='Return list of persons.')
async def all_persons(
        paginated_params: PaginateParams = Depends(),
        person_service: PersonService = Depends(get_person_service),
) -> Persons:
    persons = await person_service.get_page(paginated_params.page_num, paginated_params.page_size)
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=PERSON_NOT_FOUND)

    return persons


@router.get('/search',
            response_model=Persons,
            summary='Full text search of persons.',
            description='Return list of persons.')
async def search_persons(
        query: str,
        paginated_params: PaginateParams = Depends(),
        person_service: PersonService = Depends(get_person_service),
) -> Persons:
    persons = await person_service.full_text_search(query, paginated_params.page_num, paginated_params.page_size)
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=PERSON_NOT_FOUND)

    return persons


@router.get('/{person_id}/film/',
            response_model=Movies,
            summary='Movies by person',
            description='Return list of movies where the person acted.')
async def person_film(
        person_id: str,
        paginated_params: PaginateParams = Depends(),
        person_service: PersonService = Depends(get_person_service)
) -> Movies:
    person = await person_service.get_movies(person_id, paginated_params.page_num, paginated_params.page_size)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=PERSON_NOT_FOUND)

    return person


@router.get('/{person_id}', response_model=Person)
async def person_by_id(person_id: str, person_service: PersonService = Depends(get_person_service)) -> Person:
    person = await person_service.get_document(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=PERSON_NOT_FOUND)
    return person
