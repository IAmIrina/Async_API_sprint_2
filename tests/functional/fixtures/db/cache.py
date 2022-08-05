
"""Cache fixtures."""
import aioredis
import pytest_asyncio
from settings import test_settings


@pytest_asyncio.fixture()
async def clean_cache():
    """Flush Redis DB."""
    redis = aioredis.from_url(
        f"redis://{test_settings.redis.host}:{test_settings.redis.port}",
        password=test_settings.redis.password
    )
    await redis.flushdb()
    yield redis
    await redis.close()
