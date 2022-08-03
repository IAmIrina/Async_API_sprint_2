from pydantic import BaseSettings, Field


class RedisSettings(BaseSettings):
    """Redis connection settings."""
    host: str = Field('127.0.0.1', env='REDIS_HOST')
    port: int = Field(6379, env='REDIS_PORT')
    password: str = Field('f73rt6r3etfr3rtw5r35t', env='REDIS_PASSWORD')


class ElasticSettings(BaseSettings):
    """Redis connection settings."""
    host: str = Field('127.0.0.1', env='ELASTIC_HOST')
    port: int = Field(9200, env='ELASTIC_PORT')


class TestSettings(BaseSettings):
    """Project settings."""
    api_url = Field('http://127.0.0.1:9000/api/v1', env='FAST_API_URL')
    redis: RedisSettings = RedisSettings()
    elastic: ElasticSettings = ElasticSettings()


test_settings = TestSettings()
