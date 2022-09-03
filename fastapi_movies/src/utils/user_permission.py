import json

from core.config import settings
from core.security import get_secret_key

from utils.session import get_session


class UserPermission:

    async def check_user_permission(self, authorization: str):
        session = await get_session()
        access_token = self._split_user_token(authorization)
        session.headers['Authorization'] = get_secret_key()
        async with session.post(
                url=settings.check_role_url,
                json=json.dumps({"access_token": access_token}),
        ) as response:
            response_data = await response.json()
            return response_data, response.status

    def _split_user_token(self, authorization: str) -> str:
        return authorization.split('Bearer ')[1]
