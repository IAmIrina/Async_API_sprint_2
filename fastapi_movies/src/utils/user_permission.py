import json

from core.config import settings

from utils.session import get_search_engine


class UserPermission:

    async def check_user_permission(self, access_token: str):
        session = await get_search_engine()
        session.headers['Authorize'] = settings.secret_key
        async with session.post(
                url=settings.check_role_url,
                json=json.dumps({"access_token": access_token}),
        ) as response:
            response_data = await response.json()
            return response_data


