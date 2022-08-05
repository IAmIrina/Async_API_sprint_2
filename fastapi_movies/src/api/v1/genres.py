"""Route genres."""
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from core.messages import GENRE_NOT_FOUND
from models.custom_models import PaginateParams
from models.genre import Genre, Genres
from services.genre import GenreService, get_genre_service

router = APIRouter()


@router.get('/{genre_id}',
            response_model=Genre,
            summary="Get genre.",
            description="Return genre by uuid.")
async def genre(genre_id: str, genre_service: GenreService = Depends(get_genre_service)) -> Genre:
    genre = await genre_service.get_document(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=GENRE_NOT_FOUND)
    return genre


@router.get('/',
            response_model=Genres,
            summary="Get genres.",
            description="Return list of genres.")
async def genres(
        paginated_params: PaginateParams = Depends(),
        genre_service: GenreService = Depends(get_genre_service),
) -> Genres:
    genres = await genre_service.get_page(paginated_params.page_num, paginated_params.page_size)
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=GENRE_NOT_FOUND)
    return genres
