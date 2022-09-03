import json
from http import HTTPStatus

from aiohttp.client_exceptions import ClientConnectorError
from core.config import settings
from core.constants import anonymous, retry

from utils.session import get_session


class UserPermission:

    async def check_user_permission(self, authorization: str):
        session = await get_session()
        access_token = self._split_user_token(authorization)
        session.headers['Authorization'] = settings.secret_key
        for _ in range(retry):
            try:
                async with session.post(
                        url=settings.check_role_url,
                        json=json.dumps({"access_token": access_token}),
                ) as response:
                    response_data = await response.json()
                    return response_data, response.status
            except ClientConnectorError:
                continue
        return anonymous, HTTPStatus.BAD_GATEWAY

    def _split_user_token(self, authorization: str) -> str:
        return authorization.split(' ')[1]
