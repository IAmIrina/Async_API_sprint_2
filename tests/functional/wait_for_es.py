"""Wait for Elastic Search is ready to accept connection."""
import asyncio

from elasticsearch import AsyncElasticsearch
from settings import test_settings
from utils.backoff import backoff


@backoff()
async def check_connection(es_client: AsyncElasticsearch) -> None:
    """Check ES connection with Reconnect."""
    if not await es_client.ping():
        raise ValueError("Connection failed")


async def es_connect() -> None:
    """Wait for ES."""
    client = AsyncElasticsearch(hosts=[f'http://{test_settings.elastic.host}:{test_settings.elastic.port}'])
    await check_connection(client)
    await client.close()


if __name__ == '__main__':
    asyncio.run(es_connect())
