"""Flows for ETL process data."""
from database.pg_database import PGConnection
from processors.enricher import Enricher
from processors.extractor import Extractor
from processors.loader import ESLoader
from processors.transformer import Transformer, MovieTransformer
from lib import schemas
from config import settings
from lib import sql_templates

pg = PGConnection(settings.postgres.dict())


def get_movie_enricher() -> Enricher:
    """Return set up Enricher for movies index"""
    loader = ESLoader(
        redis_settings=settings.cache.loader,
        transport_options=settings.es_movies.connection.dict(),
        index=settings.es_movies.index,
        index_schema=settings.es_movies.index_schema,
    )

    transformer = MovieTransformer(
        schema=schemas.Movie,
        redis_settings=settings.cache.transformer,
        result_handler=loader.proccess,
    )

    return Enricher(
        pg=pg,
        redis_settings=settings.cache.enricher,
        sql_template=sql_templates.get_movie_info_by_id,
        result_handler=transformer.proccess,
    )


def etl_movies_by_person() -> Extractor:
    """Flow ETL Modified Persons to movie index."""

    return Extractor(
        pg=pg,
        redis_settings=settings.cache.extractor,
        sql_template=sql_templates.get_modified_movies_by_person,
        page_size=settings.page_size,
        result_handler=get_movie_enricher().proccess,
    )


def etl_movies_by_genre() -> Extractor:
    """Flow to ETL Modified Genres to movie index."""

    return Extractor(
        pg=pg,
        redis_settings=settings.cache.extractor,
        sql_template=sql_templates.get_modified_movies_by_genre,
        page_size=settings.page_size,
        result_handler=get_movie_enricher().proccess,
    )


def etl_modified_movies() -> Extractor:
    """Flow ETL Modified Movies to movie index."""

    return Extractor(
        pg=pg,
        redis_settings=settings.cache.extractor,
        sql_template=sql_templates.get_modified_movies,
        page_size=settings.page_size,
        result_handler=get_movie_enricher().proccess,
    )


def etl_genres() -> Extractor:
    """Flow ETL Genres to genres index. """

    loader = ESLoader(
        redis_settings=settings.cache.loader,
        transport_options=settings.es_genres.connection.dict(),
        index=settings.es_genres.index,
        index_schema=settings.es_genres.index_schema,
    )

    transformer = Transformer(
        schema=schemas.Genre,
        redis_settings=settings.cache.transformer,
        result_handler=loader.proccess,
    )

    return Extractor(
        pg=pg,
        redis_settings=settings.cache.extractor,
        sql_template=sql_templates.get_modified_genres,
        page_size=settings.page_size,
        result_handler=transformer.proccess,
    )


def etl_persons() -> Extractor:
    """Flow ETL Person to persons index. """

    loader = ESLoader(
        redis_settings=settings.cache.loader,
        transport_options=settings.es_persons.connection.dict(),
        index=settings.es_persons.index,
        index_schema=settings.es_persons.index_schema,
    )

    transformer = Transformer(
        schema=schemas.FilmPerson,
        redis_settings=settings.cache.transformer,
        result_handler=loader.proccess,
    )

    return Extractor(
        pg=pg,
        redis_settings=settings.cache.extractor,
        sql_template=sql_templates.get_modified_persons,
        page_size=settings.page_size,
        result_handler=transformer.proccess,
    )
