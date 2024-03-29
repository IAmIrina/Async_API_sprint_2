import aiohttp
import aioredis
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import films, genres, persons
from core.config import settings
from db import cache, search
from middleware.permission_midlleware import PermissionMiddleware
from utils import session

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description=settings.description,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup():
    cache.cache = await aioredis.create_redis_pool(
        (settings.redis.host, settings.redis.port),
        password=settings.redis.password,
        minsize=10,
        maxsize=20,
    )
    search.searcher = AsyncElasticsearch(hosts=[f'http://{settings.elastic.host}:{settings.elastic.port}'])
    session.session = aiohttp.ClientSession()


@app.on_event('shutdown')
async def shutdown():
    cache.cache.close()
    await cache.cache.wait_closed()
    await search.searcher.close()
    await session.session.close()

app.add_middleware(PermissionMiddleware)

app.include_router(films.router, prefix='/api/v1/films', tags=['films'])
app.include_router(genres.router, prefix='/api/v1/genres', tags=['genres'])
app.include_router(persons.router, prefix='/api/v1/persons', tags=['persons'])
