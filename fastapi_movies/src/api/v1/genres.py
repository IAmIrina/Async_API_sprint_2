"""Route genres."""
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query

from services.genre import GenreService, get_genre_service
from models.genre import Genres, Genre
from core.messages import GENRE_NOT_FOUND

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
        page_num: int = Query(default=1, ge=1, alias='page[number]', description='Page number.'),
        page_size: int = Query(default=50, ge=1, le=100, alias='page[size]', description='Page size.'),
        genre_service: GenreService = Depends(get_genre_service),
) -> Genres:
    genres = await genre_service.get_page(page_num, page_size)
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=GENRE_NOT_FOUND)
    return genres
