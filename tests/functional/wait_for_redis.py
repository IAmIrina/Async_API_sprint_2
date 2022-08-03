"""Wait for Redis is ready to accept connection."""
from utils.backoff import backoff
import aioredis
import asyncio

from settings import test_settings


@backoff()
async def check_connection(redis: aioredis.Redis) -> None:
    """Check Redis connection with Reconnect."""
    await redis.ping()


async def redis_connect() -> None:
    """Wait for Redis."""
    redis = await aioredis.from_url(
        f"redis://{test_settings.redis.host}:{test_settings.redis.port}",
        password=test_settings.redis.password,
    )
    await check_connection(redis)
    await redis.close()


if __name__ == '__main__':
    asyncio.run(redis_connect())
