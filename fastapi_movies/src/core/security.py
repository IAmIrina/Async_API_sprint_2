from functools import wraps
from http import HTTPStatus

from fastapi import HTTPException

from core.constants import anonymous
from core.messages import API_NOT_ALLOWED


def check_permission(func):
    @wraps(func)
    async def wrapper(request, *args, **kwargs):
        permission = request.state.permission
        if permission == anonymous:
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=API_NOT_ALLOWED)
        result = await func(request, *args, **kwargs)
        return result
    return wrapper
