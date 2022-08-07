"""Settings."""
import os
from logging import config as logging_config

from pydantic import BaseModel, BaseSettings, Field

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)


class RedisSettings(BaseSettings):
    """Redis connection settings."""
    host: str = Field('127.0.0.1', env='REDIS_HOST')
    port: int = Field(6379, env='REDIS_PORT')
    password: str = Field('f73rt6r3etfr3rtw5r35t', env='REDIS_PASSWORD')


class ESIndex(BaseModel):
    index_name: str


class ElasticSettings(BaseSettings):
    """Redis connection settings."""
    host: str = Field('127.0.0.1', env='ELASTIC_HOST')
    port: int = Field(9200, env='ELASTIC_PORT')


class Settings(BaseSettings):
    """Project settings."""
    project_name = 'Read-only Async Online Cinema API'
    version = '1.0.0'
    description = 'Information about movies and also genres and persons who took apart in the movies.'
    redis: RedisSettings = RedisSettings()
    elastic: ElasticSettings = ElasticSettings()

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cache_expire_in_seconds = 15

    persons: ESIndex = ESIndex(index_name='persons')
    movies: ESIndex = ESIndex(index_name='movies')
    genres: ESIndex = ESIndex(index_name='genres')


settings = Settings()
