from typing import Optional

from aiohttp import ClientSession

session: Optional[ClientSession] = None


async def get_search_engine() -> ClientSession:
    return session
