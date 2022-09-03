from functools import wraps
from http import HTTPStatus

from fastapi import HTTPException

from core.config import settings
from core.constants import anonymous
from core.messages import API_NOT_ALLOWED


def get_secret_key() -> str:
    return 'Token' + ' ' + settings.secret_key


def check_permission(func):
    @wraps(func)
    async def wrapper(request, *args, **kwargs):
        permission = request.state.permission
        if not permission or permission == anonymous:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=API_NOT_ALLOWED)
        result = await func(request, *args, **kwargs)
        return result
    return wrapper
